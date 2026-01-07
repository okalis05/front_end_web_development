(() => {
  // Micro-interactions: subtle hover glow on tiles/panels
  window.addEventListener("mousemove", (e) => {
    const targets = document.querySelectorAll(".tile, .panel, .frame, .card");
    for (const el of targets) {
      const r = el.getBoundingClientRect();
      const x = ((e.clientX - r.left) / r.width) * 100;
      const y = ((e.clientY - r.top) / r.height) * 100;
      el.style.setProperty("--mx", `${x}%`);
      el.style.setProperty("--my", `${y}%`);
    }
  }, { passive: true });
})();
