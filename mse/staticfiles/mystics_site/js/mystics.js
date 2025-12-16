(function () {
  const root = document.documentElement;

  // Theme
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    const label = document.querySelector(".ms-toggle-label");
    if (label) label.textContent = t === "light" ? "Light" : "Dark";
  }
  const saved = localStorage.getItem("ms-theme");
  applyTheme(saved || "dark");

  const toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const cur = root.getAttribute("data-theme") || "dark";
      const next = cur === "dark" ? "light" : "dark";
      localStorage.setItem("ms-theme", next);
      applyTheme(next);
      // micro animation
      if (window.anime) anime({ targets: ".ms-brand-badge", scale: [1, 1.25, 1], duration: 420, easing: "easeOutQuad" });
    });
  }

  // Reveal animations
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) e.target.classList.add("ms-revealed");
    }
  }, { threshold: 0.08 });
  document.querySelectorAll(".ms-reveal").forEach(el => io.observe(el));

  // Charts
  async function json(url) {
    const r = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
    return await r.json();
  }

  async function initTeamTrend() {
    const canvas = document.getElementById("teamTrend");
    if (!canvas || !window.MS?.teamTrendUrl) return;

    const data = await json(window.MS.teamTrendUrl);
    new Chart(canvas, {
      type: "line",
      data: {
        labels: data.labels,
        datasets: [{ label: "PTS", data: data.pts, tension: 0.35 }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: true } }
        }
      }
    });
  }

  async function initPlayerSplits() {
    const canvas = document.getElementById("playerSplits");
    if (!canvas || !window.MS?.playerSplitsUrl) return;

    const data = await json(window.MS.playerSplitsUrl);
    new Chart(canvas, {
      type: "bar",
      data: {
        labels: data.labels,
        datasets: [{ label: "PPG", data: data.ppg }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: {
          x: { grid: { display: false } },
          y: { grid: { display: true } }
        }
      }
    });
  }

  initTeamTrend();
  initPlayerSplits();
})();
document.querySelectorAll("img[data-fallback]").forEach((img) => {
  img.addEventListener("error", () => {
    img.onerror = null;
    img.src = img.dataset.fallback;
  }, { once: true });
});

