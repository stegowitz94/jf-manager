(function () {
  const page = document.querySelector("[data-attendance-page]");
  if (!page) return;
  const indicator = page.querySelector("[data-save-indicator]");
  const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]")?.value;

  function setIndicator(text, state) {
    indicator.textContent = text;
    indicator.dataset.state = state || "";
  }

  page.addEventListener("click", async (event) => {
    const button = event.target.closest("[data-status]");
    if (!button) return;
    const row = button.closest("[data-row]");
    const previous = row.querySelector(".status-button.is-active");
    if (previous === button) return;

    row.querySelectorAll(".status-button").forEach((item) => {
      item.classList.toggle("is-active", item === button);
      item.setAttribute("aria-pressed", item === button ? "true" : "false");
    });
    setIndicator("Wird gespeichert …", "saving");

    const body = new URLSearchParams({ status: button.dataset.status });
    try {
      const response = await fetch(row.dataset.updateUrl, {
        method: "POST",
        headers: { "X-CSRFToken": csrfToken, "X-Requested-With": "XMLHttpRequest", "Content-Type": "application/x-www-form-urlencoded" },
        body,
      });
      if (!response.ok) throw new Error("Speichern fehlgeschlagen");
      const data = await response.json();
      Object.entries(data.counts).forEach(([key, value]) => {
        const scope = data.scope || row.dataset.scope || "member";
        const target = page.querySelector(`[data-count-scope="${scope}"][data-count="${key}"]`);
        if (target) target.textContent = value;
      });
      row.classList.remove("is-leave");
      setIndicator("✓ Automatisch gespeichert", "saved");
    } catch (error) {
      row.querySelectorAll(".status-button").forEach((item) => {
        item.classList.toggle("is-active", item === previous);
        item.setAttribute("aria-pressed", item === previous ? "true" : "false");
      });
      setIndicator("⚠ Änderung konnte nicht gespeichert werden", "error");
    }
  });
})();
