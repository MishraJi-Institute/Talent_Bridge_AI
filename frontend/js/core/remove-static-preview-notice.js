/* Remove the obsolete static-preview top notice from stale/static browser renders.
   This does not alter backend routing or enable database features on port 5500. */
(() => {
  const matchesNotice = (el) => {
    if (!el || el.nodeType !== 1) return false;
    const text = (el.innerText || el.textContent || "").replace(/\s+/g, " ").trim();
    return text.startsWith("Static preview:") &&
      text.includes("pages and demo interactions") &&
      text.includes("Open the live Django page");
  };

  const removeNotice = () => {
    document.querySelectorAll("body *").forEach((el) => {
      if (!matchesNotice(el)) return;
      // Remove the smallest wrapper that contains the complete notice.
      let target = el;
      while (target.parentElement && target.parentElement !== document.body &&
             matchesNotice(target.parentElement)) {
        target = target.parentElement;
      }
      target.remove();
    });
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", removeNotice, { once: true });
  } else {
    removeNotice();
  }

  // Covers a stale preview script that injects the notice after page load.
  const observer = new MutationObserver(removeNotice);
  const startObserver = () => {
    if (document.body) observer.observe(document.body, { childList: true, subtree: true });
  };
  startObserver();
})();
