(() => {
  function ms() {
    return window.MS || {};
  }

  async function getJSON(url) {
    const r = await fetch(url, { headers: { "X-Requested-With": "fetch" } });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    return r.json();
  }

  function theme() {
    return document.documentElement.getAttribute("data-theme") || "dark";
  }

  function colors() {
    const t = theme();
    return {
      grid: t === "light" ? "rgba(0,0,0,.10)" : "rgba(255,255,255,.10)",
      tick: t === "light" ? "rgba(0,0,0,.60)" : "rgba(255,255,255,.65)",
    };
  }

  function destroyChart(ref) {
    try { ref?.destroy?.(); } catch (_) {}
    return null;
  }

  // ✅ KEEP LINE CHARTS AS-IS (no structural changes)
  function lineChart(canvas, labels, datasets) {
    const { grid, tick } = colors();
    return new Chart(canvas, {
      type: "line",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
          tooltip: { intersect: false, mode: "index" },
        },
        scales: {
          x: { ticks: { color: tick }, grid: { display: false } },
          y: { ticks: { color: tick }, grid: { color: grid } },
        },
      },
    });
  }

  function barChart(canvas, labels, datasets) {
    const { grid, tick } = colors();
    return new Chart(canvas, {
      type: "bar",
      data: { labels, datasets },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: true },
          tooltip: { intersect: false, mode: "index" },
        },
        scales: {
          x: { ticks: { color: tick }, grid: { display: false } },
          y: { ticks: { color: tick }, grid: { color: grid } },
        },
      },
    });
  }

  function avg(arr) {
    const nums = (arr || []).filter((v) => typeof v === "number");
    if (!nums.length) return 0;
    return nums.reduce((a, b) => a + b, 0) / nums.length;
  }

  function variance(arr, mean) {
    const nums = (arr || []).filter((v) => typeof v === "number");
    if (!nums.length) return 0;
    return nums.reduce((a, b) => a + Math.pow(b - mean, 2), 0) / nums.length;
  }

  function hexOrFallback(hex, fallback) {
    const h = String(hex || "").trim();
    return /^#[0-9A-Fa-f]{3,8}$/.test(h) ? h : fallback;
  }

  function quarterUrl(teamId, season) {
    const tmpl = ms().teamQuarterUrlTemplate;
    if (!tmpl) return null;
    const url = tmpl.replace("/0/", `/${encodeURIComponent(teamId)}/`);
    return `${url}?season=${encodeURIComponent(season)}`;
  }

  let mysticsLine = null;
  let mysticsQuarterBar = null;
  let compareLine = null;
  let compareQuarterBar = null;

  async function initMysticsLine() {
    const canvas = document.getElementById("mysticsPpgLine");
    if (!canvas || !ms().mysticsPpgUrl) return;

    const data = await getJSON(ms().mysticsPpgUrl);
    const labels = data.labels || [];
    const pts = data.pts || [];

    if (!labels.length) return;

    mysticsLine = destroyChart(mysticsLine);
    mysticsLine = lineChart(canvas, labels, [
      {
        label: `${data.team || "Mystics"} PTS`,
        data: pts,
        fill: true,
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 0,
      },
    ]);
  }

  // ✅ Mystics bar: avg points per quarter, colors per YEAR
  async function initMysticsQuarterBar() {
    const canvas = document.getElementById("mysticsSeasonBar");
    if (!canvas) return;

    // Use Mystics team id from the DB indirectly:
    // If the user selects Mystics later, this still works because we hit the endpoint with the Mystics team_id
    // We can infer Mystics by calling teams compare? Better: just find Mystics id from the page by using Team B default selection
    // But we can do the reliable approach: ask the server for Mystics quarters by using the select with Mystics preselected if present.
    // If not present, just skip.
    const teamB = document.getElementById("teamB");
    const mysticsId = teamB?.value; // teamB defaults to Mystics in your template
    if (!mysticsId) return;

    const url2024 = quarterUrl(mysticsId, 2024);
    const url2025 = quarterUrl(mysticsId, 2025);
    if (!url2024 || !url2025) return;

    const [d24, d25] = await Promise.all([getJSON(url2024), getJSON(url2025)]);
    const labels = d25.quarters || d24.quarters || ["Q1", "Q2", "Q3", "Q4"];

    const y24 = Array.isArray(d24.values) ? d24.values : [0, 0, 0, 0];
    const y25 = Array.isArray(d25.values) ? d25.values : [0, 0, 0, 0];

    const year2024Color = hexOrFallback(d24.secondary_hex, "rgba(255,255,255,.35)");
    const year2025Color = hexOrFallback(d25.primary_hex, "rgba(255,255,255,.55)");

    mysticsQuarterBar = destroyChart(mysticsQuarterBar);
    mysticsQuarterBar = barChart(canvas, labels, [
      {
        label: "2024",
        data: y24,
        backgroundColor: year2024Color,
        borderRadius: 10,
      },
      {
        label: "2025",
        data: y25,
        backgroundColor: year2025Color,
        borderRadius: 10,
      },
    ]);
  }

  function renderAISummary(teamA, teamB, aQ, bQ, season, note) {
    const card = document.getElementById("aiSummaryCard");
    const text = document.getElementById("aiSummaryText");
    if (!card || !text) return;

    const aAvg = avg(aQ);
    const bAvg = avg(bQ);
    const aVar = variance(aQ, aAvg);
    const bVar = variance(bQ, bAvg);

    const advantage = aAvg > bAvg ? teamA : teamB;
    const margin = Math.abs(aAvg - bAvg).toFixed(2);

    const moreConsistent = aVar < bVar ? teamA : teamB;

    const aQ4 = (aQ?.[3] ?? 0);
    const bQ4 = (bQ?.[3] ?? 0);
    const lateGame = aQ4 > bQ4 ? teamA : teamB;

    card.style.display = "block";
    text.innerHTML = `
      <p>
        <strong>${advantage}</strong> shows a
        <span class="ms-ai-good">${margin}-point</span> quarter-average edge in <strong>${season}</strong>.
      </p>
      <p>
        <strong>${moreConsistent}</strong> presents a more stable scoring profile across quarters, suggesting better predictability.
      </p>
      <p>
        Late-game signal: <strong>${lateGame}</strong> holds the stronger <strong>Q4</strong> quarter-average.
      </p>
      <p class="ms-ai-dim">
        ${note || ""}
      </p>
    `;
  }

  async function runCompare() {
    const hint = document.getElementById("compareHint");
    const a = document.getElementById("teamA")?.value;
    const b = document.getElementById("teamB")?.value;
    const season = document.getElementById("compareSeason")?.value || "2025";

    if (!a || !b) return;
    if (a === b) {
      if (hint) hint.textContent = "Choose two different teams.";
      return;
    }

    // ---- Line chart (UNCHANGED) ----
    const url = `${ms().compareTeamsUrl}?team_a=${encodeURIComponent(a)}&team_b=${encodeURIComponent(b)}&season=${encodeURIComponent(season)}`;
    if (hint) hint.textContent = "Loading comparison…";

    const data = await getJSON(url);
    const labels = data.labels || [];

    const aPts = data.a_pts || [];
    const bPts = data.b_pts || [];

    compareLine = destroyChart(compareLine);
    compareLine = lineChart(document.getElementById("compareLine"), labels, [
      {
        label: data.team_a?.abbr || data.team_a?.name || "Team A",
        data: aPts,
        spanGaps: true,
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
      },
      {
        label: data.team_b?.abbr || data.team_b?.name || "Team B",
        data: bPts,
        spanGaps: true,
        tension: 0.35,
        borderWidth: 2,
        pointRadius: 0,
        fill: false,
      },
    ]);

    // ---- Quarter bar chart (NEW) ----
    const qaUrl = quarterUrl(a, season);
    const qbUrl = quarterUrl(b, season);

    const [qa, qb] = await Promise.all([getJSON(qaUrl), getJSON(qbUrl)]);
    const qLabels = qa.quarters || qb.quarters || ["Q1", "Q2", "Q3", "Q4"];
    const aQ = Array.isArray(qa.values) ? qa.values : [0, 0, 0, 0];
    const bQ = Array.isArray(qb.values) ? qb.values : [0, 0, 0, 0];

    const aColor = hexOrFallback(qa.primary_hex, "rgba(255,255,255,.55)");
    const bColor = hexOrFallback(qb.primary_hex, "rgba(255,255,255,.35)");

    compareQuarterBar = destroyChart(compareQuarterBar);
    compareQuarterBar = barChart(document.getElementById("compareBar"), qLabels, [
      {
        label: qa.abbr || qa.team || "Team A",
        data: aQ,
        backgroundColor: aColor,
        borderRadius: 10,
      },
      {
        label: qb.abbr || qb.team || "Team B",
        data: bQ,
        backgroundColor: bColor,
        borderRadius: 10,
      },
    ]);

    // ---- AI summary (NEW) ----
    renderAISummary(
      data.team_a?.name || qa.team || "Team A",
      data.team_b?.name || qb.team || "Team B",
      aQ,
      bQ,
      season,
      qa.note || qb.note || ""
    );

    if (hint) hint.textContent = `Season ${data.season}: ${data.team_a?.name} vs ${data.team_b?.name}`;
  }

  document.addEventListener("DOMContentLoaded", async () => {
    try {
      await initMysticsLine();
      await initMysticsQuarterBar();

      const btn = document.getElementById("runCompare");
      if (btn) btn.addEventListener("click", runCompare);
    } catch (e) {
      console.warn("Executive dashboard init error:", e);
    }
  });
})();
