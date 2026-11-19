/**
 * Pause expensive hero visualization CSS animations while off-screen.
 * No continuous DOM rewrites — IntersectionObserver only.
 */
(function () {
  "use strict";

  var SEL = "[data-tb-viz]";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  function setPaused(el, paused) {
    if (!el) return;
    el.classList.toggle("is-paused", !!paused);
  }

  function init() {
    var panels = document.querySelectorAll(SEL);
    if (!panels.length) return;

    if (reduce || !("IntersectionObserver" in window)) {
      panels.forEach(function (el) {
        setPaused(el, !!reduce);
      });
      return;
    }

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          setPaused(entry.target, !entry.isIntersecting);
        });
      },
      { root: null, rootMargin: "80px 0px", threshold: 0.12 }
    );

    panels.forEach(function (el) {
      setPaused(el, true);
      observer.observe(el);
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", init, { once: true });
  } else {
    init();
  }
})();
