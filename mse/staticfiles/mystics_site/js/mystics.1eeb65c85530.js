(() => {
  const root = document.documentElement;

  /* -----------------------------
   * Theme
   * ----------------------------- */
  function applyTheme(t) {
    root.setAttribute("data-theme", t);
    const label = document.querySelector(".ms-toggle-label");
    if (label) label.textContent = t === "light" ? "Light" : "Dark";
  }

  function getTheme() {
    return root.getAttribute("data-theme") || "dark";
  }

  applyTheme(localStorage.getItem("ms-theme") || "dark");

  const toggle = document.querySelector("[data-theme-toggle]");
  if (toggle) {
    toggle.addEventListener("click", () => {
      const next = getTheme() === "dark" ? "light" : "dark";
      localStorage.setItem("ms-theme", next);
      applyTheme(next);

      // Re-init charts with theme-aware colors
      initChartsSafe(true);
    });
  }

  /* -----------------------------
   * Reveal animations
   * ----------------------------- */
  const io = new IntersectionObserver(
    (entries) => entries.forEach((e) => e.isIntersecting && e.target.classList.add("ms-revealed")),
    { threshold: 0.08 }
  );
  document.querySelectorAll(".ms-reveal").forEach((el) => io.observe(el));

  /* -----------------------------
   * Helpers
   * ----------------------------- */
  function ms() {
    return window.MS || {};
  }

  function playerFallback() {
    return (ms().staticPlayerFallback || "") || (window.MS_STATIC_PLAYER_FALLBACK || "") || "";
  }

  async function getJSON(url) {
    const r = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  function escapeHTML(s) {
    return String(s).replace(/[&<>"']/g, (c) => ({
      "&": "&amp;",
      "<": "&lt;",
      ">": "&gt;",
      '"': "&quot;",
      "'": "&#39;",
    }[c]));
  }

  /* -----------------------------
   * Charts
   * ----------------------------- */
  function chartColors() {
    const theme = getTheme();
    return {
      grid: theme === "light" ? "rgba(0,0,0,.10)" : "rgba(255,255,255,.10)",
      tick: theme === "light" ? "rgba(0,0,0,.60)" : "rgba(255,255,255,.65)",
    };
  }

  function makeLineChart(canvas, labels, series, { label = "", fill = true } = {}) {
    const { grid, tick } = chartColors();
    if (!window.Chart) return null;

    return new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label,
            data: series,
            tension: 0.35,
            fill,
            borderWidth: 2,
            pointRadius: 0,
          },
        ],
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: !!label },
          tooltip: { intersect: false, mode: "index" },
        },
        scales: {
          x: { ticks: { color: tick }, grid: { display: false } },
          y: { ticks: { color: tick }, grid: { color: grid } },
        },
      },
    });
  }

  const charts = {
    teamTrend: null,
    playerSplits: null,
  };

  async function initTeamTrend(forceDestroy = false) {
    const canvas = document.getElementById("teamTrend");
    if (!canvas) return;

    const url = ms().mysticsTrendUrl || ms().teamTrendUrl;
    if (!url) return;

    try {
      const data = await getJSON(url);
      const labels = Array.isArray(data.labels) ? data.labels : [];
      const pts = Array.isArray(data.pts) ? data.pts : [];

      if (!labels.length || !pts.length) return;

      if (forceDestroy) charts.teamTrend?.destroy?.();
      charts.teamTrend?.destroy?.();
      charts.teamTrend = makeLineChart(canvas, labels, pts, { label: "", fill: true });
    } catch (e) {
      console.warn("Team trend error:", e);
    }
  }

  async function initPlayerSplits(forceDestroy = false) {
    const canvas = document.getElementById("playerSplits");
    if (!canvas) return;

    const url = ms().playerSplitsUrl;
    if (!url) return;

    try {
      const data = await getJSON(url);
      const labels = Array.isArray(data.labels) ? data.labels : [];
      const ppg = Array.isArray(data.ppg) ? data.ppg : [];

      if (!labels.length || !ppg.length) return;

      if (forceDestroy) charts.playerSplits?.destroy?.();
      charts.playerSplits?.destroy?.();
      charts.playerSplits = makeLineChart(canvas, labels, ppg, { label: "PPG", fill: true });
    } catch (e) {
      console.warn("Player splits error:", e);
    }
  }

  /* -----------------------------
   * Roster table
   * ----------------------------- */
  async function initRosterTable() {
    const table = document.getElementById("playersTable");
    const url = ms().playersApiUrl;

    if (!table || !url) return;

    const tbody = table.querySelector("tbody");
    if (!tbody) return;

    try {
      const payload = await getJSON(url);
      const results = Array.isArray(payload) ? payload : (payload.results || []);

      if (!results.length) {
        tbody.innerHTML = `<tr><td colspan="3" class="ms-dim">No players found.</td></tr>`;
        return;
      }

      tbody.innerHTML = "";

      for (const p of results) {
        const id = p.api_id ?? p.id ?? null;
        if (!id) continue;

        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>
            <a href="/mystics_site/players/${id}/"
               style="font-weight:700;text-decoration:none;color:inherit">
              ${escapeHTML(p.name || "—")}
            </a>
          </td>
          <td>${escapeHTML(p.position || "—")}</td>
          <td>${escapeHTML(p.team || "—")}</td>
        `;
        tbody.appendChild(tr);
      }
    } catch (e) {
      console.warn("Roster table error:", e);
      tbody.innerHTML = `<tr><td colspan="3" class="ms-dim">Unable to load roster.</td></tr>`;
    }
  }

  /* -----------------------------
   * Image fallback wiring
   * ----------------------------- */
  function attachFallback(img) {
    const fb = img.dataset.fallback || playerFallback();
    if (!fb) return;

    img.addEventListener(
      "error",
      () => {
        img.onerror = null;
        img.src = fb;
      },
      { once: true }
    );
  }

  function initChartsSafe(forceDestroy = false) {
    initTeamTrend(forceDestroy);
    initPlayerSplits(forceDestroy);
  }

  document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll("img[data-fallback]").forEach(attachFallback);

    initChartsSafe(false);
    initRosterTable();
  });
})();





