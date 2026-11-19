(() => {
  const DEMO_SESSION_KEY = "talentbridge.demo.auth.v1";
  const { authUserId, authEmail, authName } = document.body.dataset;
  const serverUser = authUserId
    ? { id: authUserId, email: authEmail || "", name: authName || "" }
    : null;
  const localHosts = ["localhost", "127.0.0.1", "[::1]", "::1"];
  const isStaticPreview = window.location.protocol === "file:" ||
    (localHosts.includes(window.location.hostname) && window.location.port !== "8000");
  const demoExplicitlyEnabled = new URLSearchParams(window.location.search).get("demo") === "1";
  let demoUser = null;

  if (!serverUser && isStaticPreview && demoExplicitlyEnabled) {
    try {
      const stored = JSON.parse(window.sessionStorage.getItem(DEMO_SESSION_KEY) || "null");
      if (stored?.isDemo && stored.id && stored.role && stored.email) demoUser = stored;
    } catch (_) {}
  }

  const user = serverUser || demoUser;
  if (demoUser) {
    document.body.dataset.authUserId = demoUser.id;
    document.body.dataset.authEmail = demoUser.email;
    document.body.dataset.authName = demoUser.name;
  }

  document.documentElement.dataset.dashboardAuth = serverUser
    ? "ready"
    : demoUser ? "demo" : "missing";
  document.body.querySelectorAll("[data-auth-email]").forEach(element => {
    element.textContent = demoUser
      ? `Demo account · ${demoUser.email}`
      : user?.email || "Signed in";
  });
  document.addEventListener("submit", event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement) || !form.matches("[data-logout-form]") || user) return;

    event.preventDefault();
    window.location.assign(form.action);
  });
  window.TALENTBRIDGE_AUTH_READY = Promise.resolve(user);
})();
