/* TalentBridge AI auth bridge — REAL Google OAuth only (no demo login).
   - Local Django (:8000 / :8001): do nothing; allauth handles Google.
   - GitHub Pages / static: send the browser to the real Django app origin
     for /accounts/google/login/ (server-side OAuth). Never invent a session. */
(() => {
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

  function djangoOrigin() {
    const meta = document.querySelector('meta[name="talentbridge-django-origin"]');
    const fromMeta = (meta && meta.getAttribute("content") || "").trim().replace(/\/$/, "");
    if (fromMeta) return fromMeta;
    // Optional runtime override for deploys that inject window config.
    const fromWindow = (window.TALENTBRIDGE_DJANGO_ORIGIN || "").trim().replace(/\/$/, "");
    return fromWindow;
  }

  function showRealOauthNotice() {
    let note = document.getElementById("tb-real-oauth-notice");
    if (!note) {
      note = document.createElement("div");
      note.id = "tb-real-oauth-notice";
      note.setAttribute("role", "status");
      note.tabIndex = -1;
      note.style.cssText =
        "margin:12px 0;padding:12px 14px;border-radius:12px;background:#fff7ed;border:1px solid #fdba74;color:#9a3412;font:500 14px/1.45 system-ui,sans-serif;";
      const anchor =
        document.querySelector("form[data-oauth-provider='google']") ||
        document.querySelector("form[data-auth-login]") ||
        document.querySelector(".login-content") ||
        document.querySelector("main");
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(note, anchor);
      } else {
        document.body.prepend(note);
      }
    }
    note.innerHTML =
      "<strong>Real Google sign-in needs the Django app server.</strong> " +
      "This GitHub Pages site is static and cannot finish OAuth. " +
      'Use <a href="http://127.0.0.1:8000/login/">http://127.0.0.1:8000/login/</a> from this project folder, ' +
      "or set <code>TALENTBRIDGE_DJANGO_ORIGIN</code> to your deployed Django HTTPS URL.";
    note.focus();
  }

  function startRealGoogle(form) {
    const origin = djangoOrigin();
    if (!origin) {
      showRealOauthNotice();
      return;
    }
    const role = form.querySelector('input[name="role"]')?.value || "choose";
    const next = form.querySelector('input[name="next"]')?.value || "";
    const params = new URLSearchParams();
    if (role) params.set("role", role);
    if (next) params.set("next", next);
    const qs = params.toString();
    // allauth Google login (GET) starts the real authorization-code flow.
    window.location.assign(
      origin + "/accounts/google/login/" + (qs ? "?" + qs : "")
    );
  }

  function startRealLoginPage() {
    const origin = djangoOrigin();
    if (!origin) {
      showRealOauthNotice();
      return;
    }
    window.location.assign(origin + "/login/");
  }

  document.addEventListener(
    "submit",
    (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;

      if (form.dataset.oauthProvider === "google") {
        event.preventDefault();
        event.stopPropagation();
        startRealGoogle(form);
        return;
      }

      // Email/password on static cannot authenticate against Django without CORS+API.
      // Send the user to the real login page instead of inventing a demo session.
      if (form.matches("[data-auth-login], #jobSeekerForm, #employerForm")) {
        event.preventDefault();
        event.stopPropagation();
        startRealLoginPage();
      }
    },
    true
  );
})();
