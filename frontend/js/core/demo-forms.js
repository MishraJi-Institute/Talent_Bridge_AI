/* TalentBridge AI auth bridge — dual mode
   - Local folder Django (:8000 / :8001): real Google OAuth (script exits).
   - GitHub Pages: Google / email / signup work in-browser demo — no Django needed. */
(() => {
  const DEMO_SESSION_KEY = "talentbridge.demo.auth.v1";
  const localHosts = new Set(["localhost", "127.0.0.1", "[::1]", "::1"]);
  const host = (window.location.hostname || "").toLowerCase();
  const port = window.location.port || "";
  const isDjangoLocal = localHosts.has(host) && (port === "8000" || port === "8001");

  if (isDjangoLocal) return;

  const markedStatic =
    document.documentElement.getAttribute("data-static-preview") === "1" ||
    document.body?.hasAttribute("data-static-preview");
  const isStaticHost =
    window.location.protocol === "file:" ||
    markedStatic ||
    !localHosts.has(host);

  if (!isStaticHost) return;

  function dashboardHref(role) {
    return (
      (role === "employer"
        ? "/pages/dashboard/cdashboard.html"
        : "/pages/dashboard/jdashboard.html") + "?demo=1"
    );
  }

  function loginHref() {
    return "/pages/login.html?demo=1";
  }

  function makeDemoSession({ email, name, role, provider }) {
    const normalizedRole = role === "employer" ? "employer" : "job_seeker";
    const normalizedEmail = String(
      email || "demo.user@talentbridge.local"
    )
      .trim()
      .toLowerCase();
    const normalizedName =
      String(name || "").trim() ||
      normalizedEmail
        .split("@")[0]
        .replace(/[._-]+/g, " ")
        .replace(/\b\w/g, (letter) => letter.toUpperCase());
    const user = {
      id: `demo-${Date.now().toString(36)}-${Math.random()
        .toString(36)
        .slice(2, 8)}`,
      email: normalizedEmail,
      name: normalizedName,
      role: normalizedRole,
      provider: provider || "email-demo",
      isDemo: true,
    };
    try {
      window.sessionStorage.setItem(DEMO_SESSION_KEY, JSON.stringify(user));
      return user;
    } catch (_) {
      return null;
    }
  }

  function openDashboard(role) {
    window.location.assign(dashboardHref(role));
  }

  function ensureDemoBadge() {
    if (document.getElementById("tb-static-demo-badge")) return;
    const badge = document.createElement("div");
    badge.id = "tb-static-demo-badge";
    badge.setAttribute("role", "status");
    badge.textContent =
      "GitHub demo sign-in — continues in this browser (no server required)";
    badge.style.cssText =
      "position:fixed;z-index:9999;left:12px;bottom:12px;max-width:min(360px,calc(100vw - 24px));" +
      "padding:8px 12px;border-radius:999px;background:#102a56;color:#fff;" +
      "font:600 12px/1.35 system-ui,sans-serif;box-shadow:0 8px 24px rgba(16,42,86,.25);";
    document.body.appendChild(badge);
  }

  function wireGoogleButtons() {
    document.querySelectorAll('form[data-oauth-provider="google"]').forEach((form) => {
      form.setAttribute("action", "#");
      const btn = form.querySelector('button[type="submit"], .social-btn');
      if (btn) {
        btn.disabled = false;
        btn.removeAttribute("aria-describedby");
      }
      const notice = form.parentElement?.querySelector("#google-oauth-notice");
      if (notice) notice.remove();
    });
  }

  function boot() {
    ensureDemoBadge();
    wireGoogleButtons();
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }

  document.addEventListener(
    "submit",
    (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;

      if (form.matches("[data-logout-form]")) {
        event.preventDefault();
        event.stopPropagation();
        window.sessionStorage.removeItem(DEMO_SESSION_KEY);
        window.location.assign(loginHref());
        return;
      }

      if (form.matches("[data-auth-login]")) {
        event.preventDefault();
        event.stopPropagation();
        const email = String(new FormData(form).get("email") || "").trim();
        const user = makeDemoSession({ email, role: "job_seeker" });
        if (user) openDashboard(user.role);
        return;
      }

      if (form.dataset.oauthProvider === "google") {
        event.preventDefault();
        event.stopPropagation();
        const roleValue =
          form.querySelector('input[name="role"]')?.value || "job_seeker";
        const role = roleValue === "employer" ? "employer" : "job_seeker";
        const user = makeDemoSession({
          email:
            role === "employer"
              ? "demo.employer@talentbridge.local"
              : "demo.google@talentbridge.local",
          name: role === "employer" ? "Demo Employer" : "Google Demo User",
          role,
          provider: "google-demo",
        });
        if (user) openDashboard(user.role);
        return;
      }

      if (form.id === "jobSeekerForm" || form.id === "employerForm") {
        event.preventDefault();
        event.stopPropagation();
        const data = new FormData(form);
        const role = form.id === "employerForm" ? "employer" : "job_seeker";
        const user = makeDemoSession({
          email: String(data.get("email") || "").trim(),
          name: `${data.get("firstName") || ""} ${data.get("lastName") || ""}`,
          role,
          provider: "signup-demo",
        });
        if (user) openDashboard(user.role);
      }
    },
    true
  );
})();
