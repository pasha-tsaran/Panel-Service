(() => {
  const key = "panel-service.theme";
  let theme = "dark";
  try {
    if (localStorage.getItem(key) === "light") theme = "light";
  } catch {
    // The dark default also applies when browser storage is unavailable.
  }

  function apply(value) {
    document.documentElement.dataset.theme = value;
    document.querySelectorAll("[data-theme-picker] input").forEach((input) => {
      input.checked = input.value === value;
    });
  }

  apply(theme);
  document.addEventListener("DOMContentLoaded", () => {
    apply(theme);
    document.querySelectorAll("[data-theme-picker] input").forEach((input) => {
      input.addEventListener("change", () => {
        if (!input.checked) return;
        apply(input.value);
        try {
          localStorage.setItem(key, input.value);
        } catch {
          // The theme still works for this page.
        }
      });
    });
  }, { once: true });
})();
