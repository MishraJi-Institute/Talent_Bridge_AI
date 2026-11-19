(() => {
  const form = document.querySelector(".resume-builder-form");
  const preview = document.querySelector("#resume-preview");
  if (!form || !preview) return;
  const updateText = (field) => {
    const input = form.elements.namedItem(field);
    const output = preview.querySelector(`[data-preview-field="${field}"]`);
    if (!input || !output) return "";
    const value = input.value.trim();
    output.textContent = value || output.dataset.empty || "";
    const section = output.closest("[data-preview-section]");
    if (section) section.hidden = !value;
    return value;
  };

  const updateSkills = () => {
    const input = form.elements.namedItem("skills");
    const container = preview.querySelector("[data-preview-skills]");
    const section = preview.querySelector('[data-preview-section="skills"]');
    const skills = input.value.split(",").map((skill) => skill.trim()).filter(Boolean);
    container.replaceChildren(...skills.map((skill) => {
      const chip = document.createElement("span");
      chip.textContent = skill;
      return chip;
    }));
    section.hidden = skills.length === 0;
  };

  const updateContact = () => {
    const values = ["email", "phone", "location"].map(updateText);
    preview.querySelector("[data-preview-contact]").hidden = values.every((value) => !value);
  };

  ["full_name", "headline", "summary", "experience", "education", "links"].forEach((field) => {
    const input = form.elements.namedItem(field);
    input.addEventListener("input", () => updateText(field));
  });
  ["email", "phone", "location"].forEach((field) => {
    form.elements.namedItem(field).addEventListener("input", updateContact);
  });
  form.elements.namedItem("skills").addEventListener("input", updateSkills);
  document.querySelector("#print-resume").addEventListener("click", () => window.print());
})();
