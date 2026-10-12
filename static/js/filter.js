document.addEventListener("DOMContentLoaded", () => {
  const searchInput = document.querySelector("#job-search");
  const skillInput = document.querySelector("#skill-filter");
  const clearButton = document.querySelector("#clear-filters");
  const cards = [...document.querySelectorAll(".job-card")];
  const count = document.querySelector("#visible-count");
  const emptyState = document.querySelector("#no-results");

  if (!searchInput || !skillInput) return;

  const filterJobs = () => {
    const query = searchInput.value.trim().toLocaleLowerCase();
    const skill = skillInput.value.trim().toLocaleLowerCase();
    let visible = 0;

    cards.forEach((card) => {
      const matchesQuery = card.dataset.search.toLocaleLowerCase().includes(query);
      const matchesSkill = card.dataset.skills.toLocaleLowerCase().includes(skill);
      const show = matchesQuery && matchesSkill;
      card.hidden = !show;
      if (show) visible += 1;
    });

    count.textContent = visible;
    emptyState.classList.toggle("d-none", visible !== 0);
  };

  searchInput.addEventListener("input", filterJobs);
  skillInput.addEventListener("input", filterJobs);
  clearButton.addEventListener("click", () => {
    searchInput.value = "";
    skillInput.value = "";
    filterJobs();
    searchInput.focus();
  });

  document.querySelectorAll("#application-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const field = form.querySelector("textarea");
      const valid = field && field.value.trim().length >= 10;
      field?.classList.toggle("is-invalid", !valid);
      if (!valid) {
        event.preventDefault();
        field?.focus();
      }
    });
  });
});