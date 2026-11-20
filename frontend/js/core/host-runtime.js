/* TalentBridge AI — one runtime for GitHub Pages, Live Server, VS Code, and local Django. */
(() => {
  const LOCAL_HOSTS = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);
  const LOCAL_DJANGO_PORTS = new Set(["8000", "8001"]);
  const LOCAL_STATIC_PORTS = new Set(["5500", "5501", "5502"]);
  const PUBLIC_MARKETING_HOSTS = new Set([
    "talentbridge.qd.je",
    "www.talentbridge.qd.je",
  ]);
  const DEFAULT_LOCAL_ORIGIN = "http://127.0.0.1:8000";

  function trimOrigin(value) {
    return (value || "").trim().replace(/\/$/, "");
  }

  function metaContent(name) {
    const el = document.querySelector(`meta[name="${name}"]`);
    return trimOrigin(el && el.getAttribute("content"));
  }

  function hostname() {
    return (window.location.hostname || "").toLowerCase();
  }

  function port() {
    return window.location.port || "";
  }

  function mode() {
    const host = hostname();
    const p = port();
    if (LOCAL_HOSTS.has(host) && LOCAL_DJANGO_PORTS.has(p)) return "django";
    if (window.location.protocol === "file:") return "static-local";
    if (LOCAL_HOSTS.has(host)) {
      if (!p || LOCAL_STATIC_PORTS.has(p)) return "static-local";
    }
    if (PUBLIC_MARKETING_HOSTS.has(host) || host.endsWith(".github.io")) {
      return "static-live";
    }
    if (LOCAL_HOSTS.has(host)) return "static-local";
    return "static-live";
  }

  function productionOrigin() {
    const fromMeta = metaContent("talentbridge-django-origin");
    if (fromMeta && !fromMeta.includes("127.0.0.1")) return fromMeta;
    const fromWin = trimOrigin(window.TALENTBRIDGE_DJANGO_ORIGIN);
    if (fromWin && !fromWin.includes("127.0.0.1")) return fromWin;
    return "";
  }

  function localOrigin() {
    const fromMeta = metaContent("talentbridge-django-origin-local");
    if (fromMeta) return fromMeta;
    return DEFAULT_LOCAL_ORIGIN;
  }

  function backendOrigin() {
    const m = mode();
    if (m === "django") return window.location.origin;
    if (m === "static-local") return localOrigin();
    return productionOrigin();
  }

  function isStaticPreview() {
    return mode() !== "django";
  }

  window.TalentBridge = window.TalentBridge || {};
  window.TalentBridge.runtime = {
    mode,
    backendOrigin,
    localOrigin,
    productionOrigin,
    isStaticPreview,
    LOCAL_DJANGO_ORIGIN: DEFAULT_LOCAL_ORIGIN,
  };
})();