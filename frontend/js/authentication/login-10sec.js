(() => {
  function startCinema() {
    if (document.getElementById("tb-cinema")) return;

    const layer = document.createElement("div");
    layer.id = "tb-cinema";
    layer.innerHTML = `
      <span class="beam"></span>
      <span class="beam two"></span>
      <span class="particle"></span>
      <span class="particle"></span>
      <span class="particle"></span>
      <span class="particle"></span>
      <span class="particle"></span>
      <span class="ring one"></span>
      <span class="ring two"></span>
    `;

    document.body.appendChild(layer);
    window.setTimeout(() => layer.remove(), 10200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", startCinema, { once: true });
  } else {
    startCinema();
  }
})();
