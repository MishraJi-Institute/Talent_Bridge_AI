(() => {
  document.querySelectorAll('form[data-oauth-provider="google"]').forEach(form => {
    form.addEventListener("submit", () => {
      const button = form.querySelector('button[type="submit"]');
      if (!button || button.disabled) return;

      button.disabled = true;
      button.setAttribute("aria-busy", "true");
      button.setAttribute("aria-label", "Connecting to Google");

      const label = button.querySelector(".google-signup-label") ||
        button.querySelector(".social-name");
      if (label) label.textContent = "Connecting to Google...";
    });
  });
})();
