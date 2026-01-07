(() => {
  const KEY = "mse-dashboard-theme";
  const root = document.documentElement;

  function setTheme(theme) {
    root.setAttribute("data-theme", theme);
    localStorage.setItem(KEY, theme);
  }

  const saved = localStorage.getItem(KEY);
  if (saved === "light" || saved === "dark") setTheme(saved);

  window.addEventListener("DOMContentLoaded", () => {
    const btn = document.getElementById("themeToggle");
    if (!btn) return;

    btn.addEventListener("click", () => {
      const current = root.getAttribute("data-theme") || "dark";
      setTheme(current === "dark" ? "light" : "dark");
    });
  });
})();
