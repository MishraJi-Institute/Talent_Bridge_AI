(() => {
  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const reveals = document.querySelectorAll(".reveal");
  if (reveals.length) {
    if (reduce || !("IntersectionObserver" in window)) {
      reveals.forEach((el) => el.classList.add("is-in"));
    } else {
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) return;
            entry.target.classList.add("is-in");
            io.unobserve(entry.target);
          });
        },
        { rootMargin: "0px 0px -8% 0px", threshold: 0.12 }
      );
      reveals.forEach((el) => io.observe(el));
    }
  }

  const scoreEl = document.querySelector("[data-fit-score]");
  if (scoreEl) {
    const target = Number(scoreEl.getAttribute("data-fit-score") || 86);
    if (reduce) {
      scoreEl.textContent = String(target);
    } else {
      const start = performance.now();
      const duration = 700;
      const delay = 400;
      const tick = (now) => {
        const t = Math.max(0, Math.min(1, (now - start - delay) / duration));
        const eased = 1 - Math.pow(1 - t, 3);
        scoreEl.textContent = String(Math.round(target * eased));
        if (t < 1) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    }
  }
})();
