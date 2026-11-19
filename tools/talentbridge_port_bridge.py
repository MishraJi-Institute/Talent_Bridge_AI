#!/usr/bin/env python3
"""HTTP reverse-proxy bridge so TalentBridge is reachable on both :8000 and :8001.

Keeps the browser Host header on the listen port so Google OAuth redirect URIs
registered for http://127.0.0.1:8000/... keep matching when Django is on :8001.

Usage:
  python tools/talentbridge_port_bridge.py --listen 8000 --target 8001
"""
from __future__ import annotations

import argparse
import http.client
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

HOP_BY_HOP = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailers",
    "transfer-encoding",
    "upgrade",
    "host",
    "content-length",
}


def build_handler(listen_host: str, listen_port: int, target_host: str, target_port: int):
    public_host = f"{listen_host}:{listen_port}"

    class ProxyHandler(BaseHTTPRequestHandler):
        protocol_version = "HTTP/1.1"

        def _proxy(self):
            length = int(self.headers.get("Content-Length", "0") or "0")
            body = self.rfile.read(length) if length > 0 else None

            headers = {}
            for key, value in self.headers.items():
                if key.lower() in HOP_BY_HOP:
                    continue
                headers[key] = value
            # Preserve the public alias host so Django builds OAuth callbacks for :8000.
            headers["Host"] = public_host
            headers["X-Forwarded-Host"] = public_host
            headers["X-Forwarded-Proto"] = "http"
            headers["X-Forwarded-For"] = self.client_address[0]
            headers["Connection"] = "close"

            conn = http.client.HTTPConnection(target_host, target_port, timeout=120)
            try:
                conn.request(self.command, self.path, body=body, headers=headers)
                upstream = conn.getresponse()
                payload = upstream.read()
                self.send_response(upstream.status, upstream.reason)
                for key, value in upstream.getheaders():
                    if key.lower() in HOP_BY_HOP:
                        continue
                    self.send_header(key, value)
                self.send_header("Content-Length", str(len(payload)))
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD" and payload:
                    self.wfile.write(payload)
            except Exception as exc:  # noqa: BLE001 — surface upstream outages to the browser
                message = (
                    f"TalentBridge AI backend is unavailable on "
                    f"{target_host}:{target_port} ({exc})."
                ).encode("utf-8")
                self.send_response(502)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.send_header("Content-Length", str(len(message)))
                self.send_header("Connection", "close")
                self.end_headers()
                if self.command != "HEAD":
                    self.wfile.write(message)
            finally:
                conn.close()

        def do_GET(self):  # noqa: N802
            self._proxy()

        def do_HEAD(self):  # noqa: N802
            self._proxy()

        def do_POST(self):  # noqa: N802
            self._proxy()

        def do_PUT(self):  # noqa: N802
            self._proxy()

        def do_DELETE(self):  # noqa: N802
            self._proxy()

        def do_PATCH(self):  # noqa: N802
            self._proxy()

        def do_OPTIONS(self):  # noqa: N802
            self._proxy()

        def log_message(self, format, *args):  # noqa: A003
            return

    return ProxyHandler


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="TalentBridge dual-port reverse-proxy bridge")
    parser.add_argument("--listen-host", default="127.0.0.1")
    parser.add_argument("--listen", type=int, required=True)
    parser.add_argument("--target-host", default="127.0.0.1")
    parser.add_argument("--target", type=int, required=True)
    args = parser.parse_args(argv)

    if args.listen == args.target and args.listen_host == args.target_host:
        print("Listen and target ports are identical; nothing to bridge.", file=sys.stderr)
        return 2

    handler = build_handler(args.listen_host, args.listen, args.target_host, args.target)
    server = ThreadingHTTPServer((args.listen_host, args.listen), handler)
    print(
        f"TalentBridge port bridge listening on http://{args.listen_host}:{args.listen}/ "
        f"↦ http://{args.target_host}:{args.target}/ (reverse proxy)",
        flush=True,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
