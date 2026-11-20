/* GitHub Pages: Google Identity Services (client ID only — no Render/Django). */
(() => {
  const rt = window.TalentBridge && window.TalentBridge.runtime;
  if (!rt || rt.mode() !== "static-live") return;

  const meta = document.querySelector('meta[name="google-oauth-client-id"]');
  const clientId = (meta && meta.getAttribute("content") || "").trim();
  if (!clientId) return;

  const LIVE_HOSTS = new Set(["talentbridge.qd.je", "www.talentbridge.qd.je"]);
  const onLiveHttp =
    window.location.protocol === "http:" &&
    LIVE_HOSTS.has((window.location.hostname || "").toLowerCase());
  const SECURE_PAGES =
    "https://mishraji-institute.github.io/Talent_Bridge_AI";

  function secureMirrorUrl() {
    const path = window.location.pathname || "/pages/login.html";
    if (path.startsWith("/pages/")) return `${SECURE_PAGES}${path}`;
    const slug = path.replace(/^\//, "").replace(/\/$/, "");
    if (!slug) return `${SECURE_PAGES}/pages/login.html`;
    return `${SECURE_PAGES}/pages/${slug}.html`;
  }

  function loadGsi(done) {
    if (window.google && window.google.accounts) {
      done();
      return;
    }
    const tag = document.createElement("script");
    tag.src = "https://accounts.google.com/gsi/client";
    tag.async = true;
    tag.defer = true;
    tag.onload = done;
    tag.onerror = () => showErr("Could not load Google sign-in script.");
    document.head.appendChild(tag);
  }

  function showErr(msg) {
    let note = document.getElementById("tb-pages-google-notice");
    if (!note) {
      note = document.createElement("div");
      note.id = "tb-pages-google-notice";
      note.setAttribute("role", "alert");
      note.style.cssText =
        "margin:12px 0;padding:12px 14px;border-radius:12px;background:#fff7ed;border:1px solid #fdba74;color:#9a3412;font:500 14px/1.45 system-ui,sans-serif;";
      const anchor =
        document.querySelector("form[data-oauth-provider='google']") || document.body;
      anchor.parentNode.insertBefore(note, anchor);
    }
    note.textContent = msg;
  }

  function handleCredential(response) {
    if (!response || !response.credential) {
      showErr("Google sign-in was cancelled.");
      return;
    }
    try {
      sessionStorage.setItem("tb_pages_google_credential", response.credential);
      const payload = JSON.parse(atob(response.credential.split(".")[1]));
      sessionStorage.setItem(
        "tb_pages_google_profile",
        JSON.stringify({
          email: payload.email,
          name: payload.name,
          picture: payload.picture,
        })
      );
    } catch (_) {
      /* still store credential */
    }
    const qsNext = new URLSearchParams(window.location.search).get("next") || "";
    const safeDefault = "/pages/application-success.html?signed_in=google";
    const blocked = /profile\.html/i.test(qsNext);
    const next =
      qsNext.startsWith("/") && !blocked ? qsNext : safeDefault;
    window.location.assign(next);
  }

  function startGoogleSignIn() {
    if (onLiveHttp) {
      window.location.assign(
        secureMirrorUrl() + window.location.search + window.location.hash
      );
      return;
    }
    loadGsi(() => {
      try {
        window.google.accounts.id.initialize({
          client_id: clientId,
          callback: handleCredential,
          auto_select: false,
          cancel_on_tap_outside: true,
        });
        window.google.accounts.id.prompt((notification) => {
          if (notification.isNotDisplayed() || notification.isSkippedMoment()) {
            window.google.accounts.id.renderButton(
              document.querySelector("form[data-oauth-provider='google'] button") ||
                document.body,
              { theme: "outline", size: "large", width: 320 }
            );
          }
        });
      } catch (err) {
        showErr("Google sign-in failed to start. Check OAuth client origins for talentbridge.qd.je.");
      }
    });
  }

  document.addEventListener(
    "submit",
    (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;
      if (form.dataset.oauthProvider !== "google") return;
      event.preventDefault();
      event.stopPropagation();
      startGoogleSignIn();
    },
    true
  );
})();