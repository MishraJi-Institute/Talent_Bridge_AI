(() => {
  const intro = document.getElementById("welcome-intro");
  if (!intro) return;

  const skipButton = intro.querySelector(".welcome-intro-skip");
  const sessionKey = "talentbridge.welcome-intro-shown";
  let alreadyShown;
  try {
    alreadyShown = window.sessionStorage.getItem(sessionKey) === "true";
    if (!alreadyShown) window.sessionStorage.setItem(sessionKey, "true");
  } catch (error) {
    console.warn("Welcome intro skipped because session storage is unavailable.", error);
    return;
  }
  if (alreadyShown) return;

  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const heading = document.querySelector(".hero-section h1");
  const status = intro.querySelector("#welcome-intro-status");
  let dismissed = false;
  let hideTimer;
  let statusTimer;
  const statusMessages = [
    "Connecting talent to opportunity",
    "Preparing a more thoughtful way to grow",
    "Your next step starts here"
  ];
  let currentStatus = 0;

  const dismiss = () => {
    if (dismissed) return;
    dismissed = true;
    window.clearTimeout(hideTimer);
    window.clearInterval(statusTimer);
    intro.classList.remove("is-visible");
    intro.classList.add("is-leaving");
    document.body.classList.remove("welcome-intro-open");
    window.setTimeout(() => {
      intro.hidden = true;
      if (heading) {
        heading.focus({ preventScroll: true });
        heading.blur();
      }
    }, reducedMotion ? 0 : 360);
  };

  intro.hidden = false;
  document.body.classList.add("welcome-intro-open");
  window.requestAnimationFrame(() => {
    intro.classList.add("is-visible");
    skipButton?.focus();
  });

  skipButton?.addEventListener("click", dismiss);
  intro.addEventListener("keydown", event => {
    if (event.key === "Escape") {
      event.preventDefault();
      dismiss();
    } else if (event.key === "Tab") {
      event.preventDefault();
      skipButton?.focus();
    }
  });

  if (!reducedMotion && status) {
    statusTimer = window.setInterval(() => {
      currentStatus = (currentStatus + 1) % statusMessages.length;
      status.firstChild.textContent = statusMessages[currentStatus];
    }, 850);
  }

  hideTimer = window.setTimeout(dismiss, reducedMotion ? 700 : 2850);
})();
