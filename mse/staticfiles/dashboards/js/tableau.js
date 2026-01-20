(() => {
  const root = document.documentElement;
  const toggle = () => {
    const current = root.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    root.setAttribute("data-theme", next);
    localStorage.setItem("theme", next);
    updateIcon(next);
  };

  const updateIcon = (theme) => {
    const icon = document.getElementById("themeIcon");
    if (!icon) return;
    icon.textContent = theme === "dark" ? "🌙" : "☀️";
  };

  // Init
  const stored = localStorage.getItem("theme");
  const initial = stored || "dark";
  root.setAttribute("data-theme", initial);

  document.addEventListener("DOMContentLoaded", () => {
    updateIcon(initial);
    const btn = document.getElementById("themeToggle");
    if (btn) btn.addEventListener("click", toggle);
  });
})();


document.addEventListener("DOMContentLoaded", () => {
  const flash = document.getElementById("flash");
  if (!flash) return;

  flash.addEventListener("click", () => {
    flash.animate(
      [
        { filter: "brightness(1)" },
        { filter: "brightness(1.6)" },
        { filter: "brightness(1)" }
      ],
      { duration: 420, easing: "ease-out" }
    );
  });
});
