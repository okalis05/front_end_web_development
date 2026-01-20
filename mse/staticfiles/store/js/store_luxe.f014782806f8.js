(() => {
  const root = document.documentElement;
  const key = "store_theme";

  function apply(theme){
    root.setAttribute("data-theme", theme);
    localStorage.setItem(key, theme);
    const btn = document.querySelector("[data-theme-toggle]");
    if (btn) btn.textContent = theme === "light" ? "☼" : "☾";
  }

  const saved = localStorage.getItem(key);
  if (saved) apply(saved);

  document.addEventListener("click", (e) => {
    const t = e.target.closest("[data-theme-toggle]");
    if (!t) return;
    const cur = root.getAttribute("data-theme") || "dark";
    apply(cur === "dark" ? "light" : "dark");
  });
})();
