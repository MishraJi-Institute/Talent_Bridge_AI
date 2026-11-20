/* Local static → Django; GitHub Pages → Google client ID (google-pages-signin.js). */
(() => {
  const rt = window.TalentBridge && window.TalentBridge.runtime;
  if (!rt) return;
  if (rt.mode() === "django") return;
  if (!rt.isStaticPreview()) return;

  const pagesGoogle =
    rt.mode() === "static-live" &&
    !!document.querySelector('meta[name="google-oauth-client-id"]')?.getAttribute("content");

  if (pagesGoogle) return;

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
    if (rt.mode() === "static-local") {
      note.textContent =
        "Start Django first: double-click START_TALENTBRIDGEAI.bat, then use http://127.0.0.1:8000/login/";
    } else {
      note.textContent =
        "Set GOOGLE_OAUTH_CLIENT_ID in GitHub repo Variables (Settings → Secrets and variables → Actions), then push main to rebuild Pages.";
    }
    note.focus();
  }

  function resolveOrigin() {
    const origin = rt.backendOrigin();
    if (!origin) {
      showConfigError();
      return "";
    }
    return origin;
  }

  function startRealGoogle(form) {
    const origin = resolveOrigin();
    if (!origin) return;
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
    const origin = resolveOrigin();
    if (!origin) return;
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