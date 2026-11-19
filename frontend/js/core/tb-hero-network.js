/**
 * Subtle career-technology network animation for the homepage hero.
 * Soft nodes + links drifting over a light canvas. Honors reduced motion.
 */
(function () {
  const canvas = document.getElementById("tb-hero-network");
  if (!canvas || !canvas.getContext) return;

  const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const ctx = canvas.getContext("2d");
  const nodes = [];
  const NODE_COUNT = reduceMotion ? 18 : 36;
  let width = 0;
  let height = 0;
  let raf = 0;
  let last = 0;

  function resize() {
    const parent = canvas.parentElement || document.body;
    const rect = parent.getBoundingClientRect();
    width = Math.max(320, Math.floor(rect.width));
    height = Math.max(320, Math.floor(rect.height));
    const dpr = Math.min(window.devicePixelRatio || 1, 2);
    canvas.width = Math.floor(width * dpr);
    canvas.height = Math.floor(height * dpr);
    canvas.style.width = width + "px";
    canvas.style.height = height + "px";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function seed() {
    nodes.length = 0;
    for (let i = 0; i < NODE_COUNT; i += 1) {
      nodes.push({
        x: Math.random() * width,
        y: Math.random() * height,
        r: 1.2 + Math.random() * 2.4,
        vx: (Math.random() - 0.5) * (reduceMotion ? 0.08 : 0.28),
        vy: (Math.random() - 0.5) * (reduceMotion ? 0.08 : 0.28),
        pulse: Math.random() * Math.PI * 2,
      });
    }
  }

  function step(ts) {
    if (!last) last = ts;
    const dt = Math.min(32, ts - last) / 16.67;
    last = ts;

    ctx.clearRect(0, 0, width, height);

    for (const n of nodes) {
      n.x += n.vx * dt;
      n.y += n.vy * dt;
      n.pulse += 0.02 * dt;
      if (n.x < -20) n.x = width + 20;
      if (n.x > width + 20) n.x = -20;
      if (n.y < -20) n.y = height + 20;
      if (n.y > height + 20) n.y = -20;
    }

    for (let i = 0; i < nodes.length; i += 1) {
      for (let j = i + 1; j < nodes.length; j += 1) {
        const a = nodes[i];
        const b = nodes[j];
        const dx = a.x - b.x;
        const dy = a.y - b.y;
        const dist = Math.hypot(dx, dy);
        if (dist < 140) {
          const alpha = (1 - dist / 140) * 0.28;
          ctx.beginPath();
          ctx.strokeStyle = `rgba(37, 99, 235, ${alpha})`;
          ctx.lineWidth = 1;
          ctx.moveTo(a.x, a.y);
          ctx.lineTo(b.x, b.y);
          ctx.stroke();
        }
      }
    }

    for (const n of nodes) {
      const glow = 0.45 + Math.sin(n.pulse) * 0.2;
      ctx.beginPath();
      ctx.fillStyle = `rgba(14, 165, 233, ${0.35 + glow * 0.25})`;
      ctx.arc(n.x, n.y, n.r + 2.5, 0, Math.PI * 2);
      ctx.fill();
      ctx.beginPath();
      ctx.fillStyle = `rgba(16, 42, 86, ${0.45 + glow * 0.35})`;
      ctx.arc(n.x, n.y, n.r, 0, Math.PI * 2);
      ctx.fill();
    }

    if (!reduceMotion) {
      raf = window.requestAnimationFrame(step);
    }
  }

  function start() {
    resize();
    seed();
    if (reduceMotion) {
      step(performance.now());
      return;
    }
    cancelAnimationFrame(raf);
    last = 0;
    raf = window.requestAnimationFrame(step);
  }

  start();
  window.addEventListener("resize", () => {
    resize();
    seed();
  }, { passive: true });
})();
