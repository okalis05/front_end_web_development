console.log("✅ dashboards/static/dashboards/js/javascript_viz.js LOADED");

(function () {
  "use strict";

  function qs(sel, root = document) { return root.querySelector(sel); }
  function qsa(sel, root = document) { return Array.from(root.querySelectorAll(sel)); }

  // ----------------------------
  // Intersection reveal
  // ----------------------------
  function initReveal() {
    const els = qsa(".reveal");
    if (!("IntersectionObserver" in window)) {
      els.forEach(el => el.classList.add("is-in"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach(e => {
        if (e.isIntersecting) {
          e.target.classList.add("is-in");
          io.unobserve(e.target);
        }
      });
    }, { threshold: 0.12 });
    els.forEach(el => io.observe(el));
  }

  // ----------------------------
  // Count-up for KPI values
  // ----------------------------
  function initCountUp() {
    const els = qsa("[data-countup]");
    els.forEach(el => {
      const txt = (el.textContent || "").trim();
      const numMatch = txt.match(/-?\d+(\.\d+)?/);
      if (!numMatch) return;

      const target = parseFloat(numMatch[0]);
      if (!Number.isFinite(target)) return;

      const prefix = txt.slice(0, numMatch.index);
      const suffix = txt.slice((numMatch.index || 0) + numMatch[0].length);

      const dur = 650;
      const t0 = performance.now();

      function tick(t) {
        const p = Math.min(1, (t - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        const val = target * eased;
        const formatted = (Math.abs(target) < 10 && txt.includes(".")) ? val.toFixed(2) : Math.round(val).toString();
        el.textContent = `${prefix}${formatted}${suffix}`;
        if (p < 1) requestAnimationFrame(tick);
      }

      requestAnimationFrame(tick);
    });
  }

  // ----------------------------
  // Plotly helpers
  // ----------------------------
  function baseLayout(title) {
    return {
      title: { text: title, font: { size: 16 } },
      paper_bgcolor: "rgba(255,255,255,0)",
      plot_bgcolor: "rgba(255,255,255,0)",
      margin: { l: 48, r: 18, t: 56, b: 48 },
      hoverlabel: {
        bgcolor: "rgba(255,255,255,.95)",
        bordercolor: "rgba(30,60,90,.18)",
        font: { color: "rgba(18,28,38,.92)" }
      },
      font: { color: "rgba(18,28,38,.92)", family: "ui-sans-serif, system-ui, -apple-system, Segoe UI" },
      xaxis: { gridcolor: "rgba(30,60,90,.10)", zerolinecolor: "rgba(30,60,90,.12)" },
      yaxis: { gridcolor: "rgba(30,60,90,.10)", zerolinecolor: "rgba(30,60,90,.12)" },
      legend: { orientation: "h", y: -0.18 },
    };
  }

  function plotConfig() {
    return { displayModeBar: false, responsive: true };
  }

  // ✅ Robust payload parsing using json_script output
  // Each chart has: data-payload-id="payload-<index>"
  // And a sibling: <script id="payload-<index>" type="application/json">{"rows":[...]}</script>
  function parsePayload(el) {
    const id = el.getAttribute("data-payload-id");
    if (!id) return {};

    const node = document.getElementById(id);
    if (!node) {
      console.error("❌ Payload node not found for id:", id);
      return {};
    }

    try {
      return JSON.parse(node.textContent || "{}");
    } catch (e) {
      console.error("❌ json_script payload JSON.parse failed", {
        id,
        error: e,
        preview: (node.textContent || "").slice(0, 220)
      });
      return {};
    }
  }

  // ----------------------------
  // Chart renderers
  // ----------------------------
  function bubbleVolumeRisk(el, payload) {
    const rows = payload.rows || [];
    const xKey = payload.x || "discharges";
    const yKey = payload.y || "excess_ratio";
    const sizeKey = payload.size || "readmissions";
    const colorKey = payload.color || "measure";

    const groups = {};
    rows.forEach(r => {
      const g = r[colorKey] || "Unknown";
      groups[g] = groups[g] || [];
      groups[g].push(r);
    });

    const traces = Object.keys(groups).map(g => {
      const rr = groups[g];
      return {
        type: "scatter",
        mode: "markers",
        name: g,
        x: rr.map(r => r[xKey]),
        y: rr.map(r => r[yKey]),
        text: rr.map(r => `${r.facility} (${r.state})`),
        customdata: rr.map(r => [r.facility, r.state, r.measure, r.predicted_rate, r.expected_rate, r.discharges, r.readmissions]),
        hovertemplate:
          "<b>%{customdata[0]}</b><br>" +
          "State: %{customdata[1]}<br>" +
          "Measure: %{customdata[2]}<br>" +
          "Discharges: %{customdata[5]}<br>" +
          "Readmissions: %{customdata[6]}<br>" +
          "Predicted: %{customdata[3]}%<br>" +
          "Expected: %{customdata[4]}%<br>" +
          "<extra></extra>",
        marker: {
          size: rr.map(r => Math.max(10, Math.sqrt((r[sizeKey] || 0)) * 1.2)),
          opacity: 0.78,
          line: { width: 1, color: "rgba(30,60,90,.18)" }
        }
      };
    });

    const layout = baseLayout("Volume vs Risk — Hotspots");
    layout.xaxis.title = "Discharges (volume)";
    layout.yaxis.title = "Excess Readmission Ratio";
    layout.yaxis.autorange = true;

    Plotly.newPlot(el, traces, layout, plotConfig());
  }

  function leaderboardImpact(el, payload) {
    const rows = payload.rows || [];
    const topN = payload.top_n || 8;

    const ranked = rows.map(r => {
      const impact = (r.discharges || 0) * Math.max(0, (r.excess_ratio || 0) - 1);
      return { ...r, impact };
    }).sort((a, b) => b.impact - a.impact).slice(0, topN).reverse();

    const trace = {
      type: "bar",
      orientation: "h",
      x: ranked.map(r => r.impact),
      y: ranked.map(r => `${r.facility} · ${r.state}`),
      hovertemplate:
        "<b>%{y}</b><br>" +
        "Impact Score: %{x:.1f}<br>" +
        "<extra></extra>",
      marker: { opacity: 0.82, line: { width: 1, color: "rgba(30,60,90,.16)" } }
    };

    const layout = baseLayout("Impact Leaderboard — Priority Targets");
    layout.xaxis.title = "Impact Score (Discharges × Excess above 1.0)";
    layout.margin.l = 160;

    Plotly.newPlot(el, [trace], layout, plotConfig());
  }

  function measureRiskBars(el, payload) {
    const rows = payload.rows || [];
    const by = {};
    rows.forEach(r => {
      const m = r.measure || "Unknown";
      by[m] = by[m] || { sumRatio: 0, n: 0, sumImpact: 0 };
      by[m].sumRatio += (r.excess_ratio || 0);
      by[m].n += 1;
      by[m].sumImpact += (r.discharges || 0) * Math.max(0, (r.excess_ratio || 0) - 1);
    });

    const items = Object.keys(by).map(k => ({
      measure: k,
      avgRatio: by[k].sumRatio / Math.max(1, by[k].n),
      impact: by[k].sumImpact
    })).sort((a, b) => b.impact - a.impact);

    const trace1 = {
      type: "bar",
      name: "Impact (priority weight)",
      x: items.map(i => i.measure),
      y: items.map(i => i.impact),
      opacity: 0.82,
      hovertemplate: "<b>%{x}</b><br>Impact: %{y:.1f}<br><extra></extra>"
    };

    const trace2 = {
      type: "scatter",
      mode: "lines+markers",
      name: "Avg Excess Ratio",
      x: items.map(i => i.measure),
      y: items.map(i => i.avgRatio),
      yaxis: "y2",
      hovertemplate: "<b>%{x}</b><br>Avg Excess: %{y:.2f}<br><extra></extra>"
    };

    const layout = baseLayout("Measure Lens — What Drives Priority?");
    layout.yaxis.title = "Impact";
    layout.yaxis2 = {
      overlaying: "y",
      side: "right",
      title: "Avg Excess Ratio",
      gridcolor: "rgba(0,0,0,0)"
    };

    Plotly.newPlot(el, [trace1, trace2], layout, plotConfig());
  }

  function stateHeatmap(el, payload) {
    const rows = payload.rows || [];
    const by = {};
    rows.forEach(r => {
      const s = r.state || "NA";
      by[s] = by[s] || { dis: 0, impact: 0, avgRatioSum: 0, n: 0 };
      by[s].dis += (r.discharges || 0);
      by[s].impact += (r.discharges || 0) * Math.max(0, (r.excess_ratio || 0) - 1);
      by[s].avgRatioSum += (r.excess_ratio || 0);
      by[s].n += 1;
    });

    const states = Object.keys(by).sort();
    const impact = states.map(s => by[s].impact);
    const ratio = states.map(s => by[s].avgRatioSum / Math.max(1, by[s].n));
    const dis = states.map(s => by[s].dis);

    const z = states.map((s, idx) => [impact[idx], ratio[idx], dis[idx]]);
    const trace = {
      type: "heatmap",
      x: ["Impact", "Avg Excess Ratio", "Discharges"],
      y: states,
      z,
      hovertemplate: "<b>%{y}</b><br>%{x}: %{z}<br><extra></extra>"
    };

    const layout = baseLayout("Geographic Signal — State Hotspots");
    layout.margin.l = 80;

    Plotly.newPlot(el, [trace], layout, plotConfig());
  }

  // ----------------------------
  // Render dispatcher
  // ----------------------------
  function renderOne(el) {
    const type = el.getAttribute("data-chart-type");
    const payload = parsePayload(el);

    const loading = qs(".viz__loading", el);
    if (loading) loading.remove();

    if (!el.style.minHeight) el.style.minHeight = "360px";

    switch (type) {
      case "bubble_volume_risk": return bubbleVolumeRisk(el, payload);
      case "leaderboard_impact": return leaderboardImpact(el, payload);
      case "measure_risk_bars": return measureRiskBars(el, payload);
      case "state_heatmap": return stateHeatmap(el, payload);
      default:
        el.innerHTML = "<div style='padding:14px;font-weight:750;color:rgba(18,28,38,.66)'>Unknown chart type.</div>";
    }
  }

  // ----------------------------
  // Init charts
  // ----------------------------
  function initCharts() {
    const charts = qsa(".viz__chart[data-chart-type]");
    console.log("📊 Charts found:", charts.length);
    if (!charts.length) return;

    if (!window.Plotly) {
      charts.forEach(el => {
        el.innerHTML = "<div style='padding:14px;font-weight:800;color:rgba(18,28,38,.80)'>Plotly is not available.</div>";
      });
      return;
    }

    charts.forEach((el, idx) => {
      try {
        renderOne(el);
      } catch (err) {
        console.error(`🔥 Chart[${idx}] crashed`, err);
        el.innerHTML = `<div style="padding:14px;font-weight:900;color:crimson">
          Chart failed to render: ${String(err)}
        </div>`;
      }
    });

    window.addEventListener("resize", () => {
      charts.forEach(el => {
        if (window.Plotly && el && el.data) {
          try { Plotly.Plots.resize(el); } catch (_) {}
        }
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    initReveal();
    initCountUp();
    initCharts();
  });
})();
