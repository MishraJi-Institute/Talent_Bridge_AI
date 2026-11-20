/* GitHub Pages: block POST to .html (nginx returns 405). Django forms use real URLs locally. */
(() => {
  const rt = window.TalentBridge && window.TalentBridge.runtime;
  if (!rt || rt.mode() !== "static-live") return;

  function notice() {
    let el = document.getElementById("tb-static-post-blocked");
    if (!el) {
      el = document.createElement("div");
      el.id = "tb-static-post-blocked";
      el.setAttribute("role", "alert");
      el.style.cssText =
        "margin:12px 0;padding:12px 14px;border-radius:12px;background:#fff7ed;border:1px solid #fdba74;color:#9a3412;font:500 14px/1.45 system-ui,sans-serif;";
      el.textContent =
        "Saving accounts and profiles needs the full app on your PC: START_TALENTBRIDGEAI.bat → http://127.0.0.1:8000. This live site is preview only.";
      (document.querySelector("main") || document.body).prepend(el);
    }
    el.scrollIntoView({ block: "nearest" });
  }

  document.addEventListener(
    "submit",
    (event) => {
      const form = event.target;
      if (!(form instanceof HTMLFormElement)) return;
      if ((form.method || "get").toLowerCase() !== "post") return;
      if (form.dataset.oauthProvider === "google") return;
      const action = (form.getAttribute("action") || "").trim();
      if (!action || /^https?:\/\//i.test(action)) return;
      if (action.endsWith(".html") || !action.startsWith("/")) {
        event.preventDefault();
        event.stopPropagation();
        notice();
      }
    },
    true
  );
})();