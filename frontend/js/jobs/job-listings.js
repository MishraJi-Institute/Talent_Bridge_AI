(() => {
  const form = document.querySelector(".tb-jobs-search");
  const keywordInput = form?.querySelector('[name="keyword"]');
  const locationInput = form?.querySelector('[name="location"]');
  const cards = [...document.querySelectorAll("[data-job-card]")];
  const filters = [...document.querySelectorAll("[data-job-filter]")];
  const emptyState = document.querySelector("[data-job-empty]");
  const resultCount = document.querySelector(".tb-jobs-result-count");

  if (!form || !keywordInput || !locationInput || cards.length === 0 || !emptyState || !resultCount) return;

  const params = new URLSearchParams(window.location.search);
  keywordInput.value = params.get("keyword") || "";
  locationInput.value = params.get("location") || "";
  let activeFilter = "all";

  const updateResults = () => {
    const keyword = keywordInput.value.trim().toLowerCase();
    const location = locationInput.value.trim().toLowerCase();
    let visibleCount = 0;

    cards.forEach(card => {
      const matchesFilter = activeFilter === "all" ||
        card.dataset.type === activeFilter ||
        (activeFilter === "Remote" && card.dataset.location.toLowerCase().includes("remote"));
      const matchesKeyword = !keyword || card.dataset.search.includes(keyword);
      const matchesLocation = !location || card.dataset.location.toLowerCase().includes(location);
      const visible = matchesFilter && matchesKeyword && matchesLocation;
      card.hidden = !visible;
      if (visible) visibleCount += 1;
    });

    emptyState.hidden = visibleCount > 0;
    resultCount.textContent = `${visibleCount} ${visibleCount === 1 ? "opportunity" : "opportunities"}`;
  };

  form.addEventListener("submit", event => {
    event.preventDefault();
    const query = new URLSearchParams();
    if (keywordInput.value.trim()) query.set("keyword", keywordInput.value.trim());
    if (locationInput.value.trim()) query.set("location", locationInput.value.trim());
    const suffix = query.toString();
    window.history.replaceState(null, "", `${window.location.pathname}${suffix ? `?${suffix}` : ""}`);
    updateResults();
  });

  filters.forEach(button => {
    button.addEventListener("click", () => {
      activeFilter = button.dataset.jobFilter;
      filters.forEach(filter => {
        const selected = filter === button;
        filter.classList.toggle("is-active", selected);
        filter.setAttribute("aria-pressed", String(selected));
      });
      updateResults();
    });
  });

  keywordInput.addEventListener("input", updateResults);
  locationInput.addEventListener("input", updateResults);
  updateResults();
})();
