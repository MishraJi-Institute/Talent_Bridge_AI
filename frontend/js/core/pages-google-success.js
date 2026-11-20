/* After GIS sign-in on GitHub Pages, show name/email from sessionStorage. */
(() => {
  const rt = window.TalentBridge && window.TalentBridge.runtime;
  if (!rt || rt.mode() !== "static-live") return;
  const params = new URLSearchParams(window.location.search);
  if (params.get("signed_in") !== "google") return;

  let profile = null;
  try {
    profile = JSON.parse(sessionStorage.getItem("tb_pages_google_profile") || "null");
  } catch (_) {
  }
  if (!profile || !profile.email) return;

  const hero = document.querySelector(".tb-hero h1");
  if (hero) {
    hero.textContent = `Signed in with Google as ${profile.name || profile.email}`;
  }
  const sub = document.querySelector(".tb-hero p");
  if (sub) {
    sub.textContent =
      "Live preview only — to save this account in the database, use http://127.0.0.1:8000 and sign in with Google there.";
  }
})();