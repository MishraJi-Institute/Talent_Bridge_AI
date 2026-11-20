/* GitHub Pages: reflect Google GIS session in nav (sessionStorage). */
(() => {
  const rt = window.TalentBridge && window.TalentBridge.runtime;
  if (!rt || rt.mode() !== "static-live") return;

  function readProfile() {
    try {
      return JSON.parse(sessionStorage.getItem("tb_pages_google_profile") || "null");
    } catch (_) {
      return null;
    }
  }

  function pagesRoot() {
    return window.location.pathname.includes("/pages/") ? "" : "/pages/";
  }

  function profileHref() {
    return `${pagesRoot()}profile.html`;
  }

  function loginHref() {
    return `${pagesRoot()}login.html`;
  }

  function signOut() {
    sessionStorage.removeItem("tb_pages_google_profile");
    sessionStorage.removeItem("tb_pages_google_credential");
    window.location.assign(loginHref());
  }

  function ensureStyles() {
    if (document.getElementById("tb-pages-auth-chrome-style")) return;
    const tag = document.createElement("style");
    tag.id = "tb-pages-auth-chrome-style";
    tag.textContent = `
      .auth-user-chip { font:600 14px/1.2 system-ui,sans-serif; color:#1e3a5f; margin-right:8px; max-width:140px; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .auth-btn.tb-sign-out { background:#f8fafc; color:#334155; border:1px solid #e2e8f0; cursor:pointer; font:inherit; }
      a.auth-signed-in { font-weight:600; color:#1d4ed8 !important; }
    `;
    document.head.appendChild(tag);
  }

  function apply(profile) {
    if (!profile || !profile.email) return;
    ensureStyles();
    const label = (profile.name || profile.email || "Account").trim();
    const short =
      label.length > 22 ? label.slice(0, 20) + "…" : label;

    document.querySelectorAll(".auth-actions").forEach((el) => {
      const signIn = el.querySelector(".auth-signin, a[href*='login']");
      const signUp = el.querySelector(".auth-signup, a[href*='signup']");
      if (signIn) {
        signIn.textContent = short;
        signIn.href = profileHref();
        signIn.classList.add("auth-signed-in");
        signIn.removeAttribute("aria-current");
      }
      if (signUp) {
        signUp.textContent = "Sign out";
        signUp.href = "#";
        signUp.classList.add("tb-sign-out");
        signUp.setAttribute("role", "button");
        signUp.addEventListener("click", (e) => {
          e.preventDefault();
          signOut();
        });
      }
      if (!signIn && !signUp) {
        el.innerHTML = "";
        const nameSpan = document.createElement("span");
        nameSpan.className = "auth-user-chip";
        nameSpan.textContent = short;
        const prof = document.createElement("a");
        prof.className = "auth-btn auth-signin auth-signed-in";
        prof.href = profileHref();
        prof.textContent = "Profile";
        const out = document.createElement("button");
        out.type = "button";
        out.className = "auth-btn auth-signup tb-sign-out";
        out.textContent = "Sign out";
        out.addEventListener("click", signOut);
        el.append(nameSpan, prof, out);
      }
    });

    document.querySelectorAll(".tb-links a, .tb-nav a, .nav-links a").forEach((a) => {
      const text = (a.textContent || "").trim();
      const href = (a.getAttribute("href") || "").toLowerCase();
      if (/sign\s*in/i.test(text) || href.includes("login")) {
        if (/sign\s*in/i.test(text)) {
          a.textContent = short;
          a.href = profileHref();
          a.classList.add("auth-signed-in");
        }
      }
      if (/get\s*started/i.test(text) && profile.email) {
        a.textContent = "Sign out";
        a.href = "#";
        a.classList.remove("tb-button");
        a.classList.add("tb-sign-out");
        a.addEventListener("click", (e) => {
          e.preventDefault();
          signOut();
        });
      }
    });
  }

  apply(readProfile());
  window.addEventListener("storage", () => apply(readProfile()));
})();