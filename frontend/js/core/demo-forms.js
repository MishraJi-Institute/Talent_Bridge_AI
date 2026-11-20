/* TalentBridge AI — static frontend → real Django OAuth (no demo sessions).
   Local Django (:8000 / :8001): exit; server handles forms and Google. */
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
    if (fromMeta && !fromMeta.includes("127.0.0.1")) return fromMeta;
    const fromWindow = (window.TALENTBRIDGE_DJANGO_ORIGIN || "").trim().replace(/\/$/, "");
    if (fromWindow && !fromWindow.includes("127.0.0.1")) return fromWindow;
    return "";
  }

  function showConfigError() {
    let note = document.getElementById("tb-real-oauth-notice");
    if (!note) {
      note = document.createElement("div");
      note.id = "tb-real-oauth-notice";
      note.setAttribute("role", "alert");
      note.tabIndex = -1;
      note.style.cssText =
        "margin:12px 0;padding:12px 14px;border-radius:12px;background:#fff7ed;border:1px solid #fdba74;color:#9a3412;font:500 14px/1.45 system-ui,sans-serif;";
      const anchor =
        document.querySelector("form[data-oauth-provider='google']") ||
        document.querySelector("form[data-auth-login]") ||
        document.querySelector("main");
      if (anchor && anchor.parentNode) {
        anchor.parentNode.insertBefore(note, anchor);
      } else {
        document.body.prepend(note);
      }
    }
    note.textContent =
      "Google sign-in is not wired yet: deploy the Django backend and set config/talentbridge_django_origin.txt (or TALENTBRIDGE_DJANGO_ORIGIN in GitHub Actions) to that HTTPS URL, then redeploy Pages.";
    note.focus();
  }

  function startRealGoogle(form) {
    const origin = djangoOrigin();
    if (!origin) {
      showConfigError();
      return;
    }
    const role = form.querySelector('input[name="role"]')?.value || "choose";
    const next = form.querySelector('input[name="next"]')?.value || "";
    const params = new URLSearchParams();
    if (role) params.set("role", role);
    if (next) params.set("next", next);
    const qs = params.toString();
    window.location.assign(
      origin + "/auth/social/google/" + (qs ? "?" + qs : "")
    );
  }

  function signupPathForForm(form) {
    if (form.id === "employerForm") return "/signup/employer/";
    if (form.id === "jobSeekerForm") return "/signup/job-seeker/";
    return "/login/";
  }

  function startRealBackend(form) {
    const origin = djangoOrigin();
    if (!origin) {
      showConfigError();
      return;
    }
    window.location.assign(origin + signupPathForForm(form));
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

      if (form.matches("[data-auth-login], #jobSeekerForm, #employerForm")) {
        event.preventDefault();
        event.stopPropagation();
        startRealBackend(form);
      }
    },
    true
  );
})();