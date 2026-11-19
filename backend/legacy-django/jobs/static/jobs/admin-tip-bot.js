(() => {
  const bot = document.getElementById("admin-tip-bot");
  const card = document.getElementById("admin-tip-card");
  const message = document.getElementById("admin-tip-message");
  const avatar = document.getElementById("admin-tip-avatar");
  const dismiss = document.getElementById("admin-tip-dismiss");
  const next = document.getElementById("admin-tip-next");

  if (!bot || !card || !message || !avatar || !dismiss || !next) {
    return;
  }

  const tips = [
    "Unclench your jaw, drop your shoulders, and take one slow breath before the next task.",
    "A sip of water is a small reset. Keep a glass nearby while you work.",
    "Give your eyes a screen break: look across the room for 20 seconds.",
    "Stand up and stretch gently for a moment. Your back will thank you.",
    "One task at a time is enough. Pick the next small step and let the rest wait.",
    "Rest your wrists and loosen your fingers after a long stretch of typing.",
    "A short walk between tasks can clear your head. Even a minute counts.",
    "Take a breath in for four counts and out for six. Let your shoulders soften."
  ];
  const showAfterStart = 9000;
  const arrivalInterval = 52000;
  const visibleDuration = 15000;
  let tipIndex = 0;
  let hideTimer;

  function hideTip() {
    window.clearTimeout(hideTimer);
    card.hidden = true;
    avatar.setAttribute("aria-expanded", "false");
  }

  function showTip() {
    message.textContent = tips[tipIndex % tips.length];
    tipIndex += 1;
    card.hidden = false;
    avatar.setAttribute("aria-expanded", "true");
    card.classList.remove("is-arriving");
    window.requestAnimationFrame(() => card.classList.add("is-arriving"));
    window.clearTimeout(hideTimer);
    hideTimer = window.setTimeout(hideTip, visibleDuration);
  }

  avatar.addEventListener("click", () => {
    if (card.hidden) {
      showTip();
    } else {
      hideTip();
    }
  });
  dismiss.addEventListener("click", hideTip);
  next.addEventListener("click", showTip);
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !card.hidden) {
      hideTip();
      avatar.focus();
    }
  });

  bot.addEventListener("pointerenter", () => window.clearTimeout(hideTimer));
  bot.addEventListener("pointerleave", () => {
    if (!card.hidden) {
      hideTimer = window.setTimeout(hideTip, visibleDuration);
    }
  });
  bot.addEventListener("focusin", () => window.clearTimeout(hideTimer));
  bot.addEventListener("focusout", (event) => {
    if (!bot.contains(event.relatedTarget) && !card.hidden) {
      hideTimer = window.setTimeout(hideTip, visibleDuration);
    }
  });

  window.setTimeout(() => {
    if (!document.hidden) {
      showTip();
    }
  }, showAfterStart);
  window.setInterval(() => {
    if (!document.hidden) {
      showTip();
    }
  }, arrivalInterval);
})();
