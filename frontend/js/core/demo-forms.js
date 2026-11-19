/* TalentBridge AI authentication bridge.
   Real authentication always belongs to Django on port 8000.
   Browser-only demo mode is available only with ?demo=1 on a static preview. */
(() => {
  const DEMO_SESSION_KEY = "talentbridge.demo.auth.v1";
  const localHosts = ["localhost", "127.0.0.1", "[::1]", "::1"];
  const isLocalHost = localHosts.includes(window.location.hostname);
  const isStaticPreview = window.location.protocol === "file:" ||
    (isLocalHost && window.location.port !== "8000");
  const demoExplicitlyEnabled = new URLSearchParams(window.location.search).get("demo") === "1";

  if (!isStaticPreview) return;

  function backendPage() {
    const path = window.location.pathname.toLowerCase();
    if (path.includes("company-signup") || path.includes("employer-signup")) {
      return "http://127.0.0.1:8000/pages/company-signup.html";
    }
    if (path.includes("jobseeker-signup")) {
      return "http://127.0.0.1:8000/pages/jobseeker-signup.html";
    }
    if (path.includes("dashboard/cdashboard")) {
      return "http://127.0.0.1:8000/pages/dashboard/cdashboard.html";
    }
    if (path.includes("dashboard/jdashboard")) {
      return "http://127.0.0.1:8000/pages/dashboard/jdashboard.html";
    }
    return "http://127.0.0.1:8000/pages/login.html";
  }

  // The static-preview warning banner was intentionally removed.
  // Authentication submissions still forward to the real Django backend below.

  if (!demoExplicitlyEnabled) {
    document.addEventListener("submit", event => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (form.matches("[data-auth-login], [data-oauth-provider], #jobSeekerForm, #employerForm")) {
        event.preventDefault();
        window.location.assign(backendPage());
      }
    }, true);
    document.addEventListener("click", event => {
      const link = event.target.closest('a[href*="login.html"], a[href*="signup"]');
      if (link && isStaticPreview) {
        const href = link.getAttribute("href") || "";
        if (/login|signup/i.test(href)) {
          event.preventDefault();
          window.location.assign(backendPage());
        }
      }
    }, true);
    return;
  }

  // Explicit static-preview demo only. It never runs on Django port 8000.
  function makeDemoSession({ email, name, role, provider }) {
    const normalizedRole = role === "employer" ? "employer" : "job_seeker";
    const normalizedEmail = String(email || "demo.user@talentbridge.local").trim().toLowerCase();
    const normalizedName = String(name || "").trim() ||
      normalizedEmail.split("@")[0].replace(/[._-]+/g, " ").replace(/\b\w/g, letter => letter.toUpperCase());
    const user = {
      id: `demo-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`,
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
    window.location.assign(role === "employer"
      ? "dashboard/cdashboard.html?demo=1"
      : "dashboard/jdashboard.html?demo=1");
  }

  document.addEventListener("submit", event => {
    const form = event.target;
    if (!(form instanceof HTMLFormElement)) return;
    if (form.matches("[data-logout-form]")) {
      event.preventDefault();
      window.sessionStorage.removeItem(DEMO_SESSION_KEY);
      window.location.assign("../login.html?demo=1");
      return;
    }
    if (form.matches("[data-auth-login]")) {
      event.preventDefault();
      const email = String(new FormData(form).get("email") || "").trim();
      const user = makeDemoSession({ email, role: "job_seeker" });
      if (user) openDashboard(user.role);
      return;
    }
    if (form.dataset.oauthProvider === "google") {
      event.preventDefault();
      const roleValue = form.querySelector('input[name="role"]')?.value || "job_seeker";
      const role = roleValue === "employer" ? "employer" : "job_seeker";
      const user = makeDemoSession({
        email: role === "employer" ? "demo.employer@talentbridge.local" : "demo.google@talentbridge.local",
        name: role === "employer" ? "Demo Employer" : "Google Demo User",
        role,
        provider: "google-demo",
      });
      if (user) openDashboard(user.role);
      return;
    }
    if (form.id === "jobSeekerForm" || form.id === "employerForm") {
      event.preventDefault();
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
  });
})();
