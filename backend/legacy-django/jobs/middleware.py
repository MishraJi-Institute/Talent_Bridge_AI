"""Remove obsolete developer-only Google OAuth setup notices from public pages.

This is presentation-only: it never enables OAuth or changes authentication checks.
It removes the smallest HTML element containing the legacy setup paragraph, even
when the paragraph is nested inside wrappers.
"""
from html.parser import HTMLParser


_NOTICE_TEXT = (
    "google sign-in is not configured",
    "google signup is not configured",
    "set google_oauth_client_id",
    "client secret prompt is hidden",
)
_VOID = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
}


class _NoticeRangeParser(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=False)
        self.html = html
        self.line_offsets = [0]
        for index, char in enumerate(html):
            if char == "\n":
                self.line_offsets.append(index + 1)
        self.stack = []
        self.nodes = []
        self.text_parts = []

    def _offset(self):
        line, column = self.getpos()
        return self.line_offsets[line - 1] + column

    def handle_starttag(self, tag, attrs):
        start = self._offset()
        node = {"tag": tag.lower(), "start": start, "end": None, "text": [], "attrs": dict(attrs)}
        self.nodes.append(node)
        if self.stack:
            self.stack[-1]["text"].append(node)
        if tag.lower() not in _VOID:
            self.stack.append(node)
        else:
            node["end"] = self._offset_after_start_tag()

    def _offset_after_start_tag(self):
        raw = self.get_starttag_text() or ""
        return self._offset() + len(raw)

    def handle_startendtag(self, tag, attrs):
        start = self._offset()
        raw = self.get_starttag_text() or ""
        self.nodes.append({
            "tag": tag.lower(), "start": start,
            "end": start + len(raw), "text": [], "attrs": dict(attrs),
        })
        if self.stack:
            self.stack[-1]["text"].append("")

    def handle_endtag(self, tag):
        tag = tag.lower()
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                node = self.stack[index]
                end_start = self._offset()
                close_end = self.html.find(">", end_start)
                node["end"] = close_end + 1 if close_end >= 0 else end_start
                del self.stack[index:]
                break

    def handle_data(self, data):
        if self.stack:
            self.stack[-1]["text"].append(data)

    def handle_entityref(self, name):
        if self.stack:
            self.stack[-1]["text"].append("&" + name + ";")

    def handle_charref(self, name):
        if self.stack:
            self.stack[-1]["text"].append("&#" + name + ";")

    def handle_comment(self, data):
        pass

    @staticmethod
    def _plain_text(parts):
        return "".join(
            _NoticeRangeParser._plain_text(part["text"])
            if isinstance(part, dict) else str(part)
            for part in parts
        ).lower()

    def _node_has_protected_marker(self, node):
        attrs = node.get("attrs", {}) or {}
        attr_text = " ".join(
            str(value or "")
            for value in (attrs.get("id"), attrs.get("class"), attrs.get("data-google-oauth-notice"))
        ).lower()
        if any(marker in attr_text for marker in ("google-oauth-notice", "login-message", "tb-alert", "message", "social-buttons", "social-section")):
            return True
        for child in node.get("text", []):
            if isinstance(child, dict) and self._node_has_protected_marker(child):
                return True
        return False

    def removal_ranges(self):
        candidates = []
        for node in self.nodes:
            if node["tag"] not in {"div", "section", "aside", "p"} or node["end"] is None:
                continue
            if self._node_has_protected_marker(node):
                continue
            text = self._plain_text(node["text"])
            if any(marker in text for marker in _NOTICE_TEXT):
                candidates.append((node["start"], node["end"], node["tag"]))
        # Prefer the smallest block wrapper (for example the notice div), while
        # falling back to a paragraph if no wrapper exists.
        candidates.sort(key=lambda item: (item[2] == "p", item[1] - item[0], item[0]))
        selected = []
        for start, end, _tag in candidates:
            if not any((a <= start and end <= b) or (start <= a and b <= end) for a, b in selected):
                selected.append((start, end))
        return sorted(selected)


def remove_legacy_google_notice(content):
    try:
        html = content.decode("utf-8")
        parser = _NoticeRangeParser(html)
        parser.feed(html)
        parser.close()
        ranges = parser.removal_ranges()
        for start, end in reversed(ranges):
            html = html[:start] + html[end:]
        return html.encode("utf-8")
    except (UnicodeDecodeError, ValueError):
        return content


class RemoveObsoleteGoogleOAuthNoticeMiddleware:
    """Strip only the stale setup notice from login and signup HTML responses."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.path.startswith(("/pages/login", "/login", "/signup/"))
            and response.get("Content-Type", "").startswith("text/html")
            and hasattr(response, "content")
        ):
            response.content = remove_legacy_google_notice(response.content)
        return response
