console.log("✅ dashboards/static/dashboards/js/javascript_viz.js LOADED");

(function () {
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
  // Count-up KPI animation
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

        const formatted =
          (Math.abs(target) < 10 && txt.includes("."))
            ? val.toFixed(2)
            : Math.round(val).toString();

        el.textContent = `${prefix}${formatted}${suffix}`;
        if (p < 1) requestAnimationFrame(tick);
      }

      requestAnimationFrame(tick);
    });
  }

  // ----------------------------
  // Plotly base styling
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

  // ----------------------------
  // ✅ SINGLE SOURCE OF TRUTH: payload parser
  // Supports BOTH:
  // 1) data-payload-id="payload-0" (preferred)
  // 2) data-chart-payload='{"rows":[...]}' (fallback)
  // ----------------------------
  function parsePayload(el) {
    // 1) Preferred: script payload
    const payloadId = el.getAttribute("data-payload-id");
    if (payloadId) {
      const node = document.getElementById(payloadId);
      if (!node) {
        console.error("❌ Payload node not found for id:", payloadId);
        return {};
      }
      try {
        let parsed = JSON.parse((node.textContent || "").trim() || "{}");
        // If node contains a JSON string, decode again
        if (typeof parsed === "string") parsed = JSON.parse(parsed);
        return parsed || {};
      } catch (e) {
        console.error("❌ payload-id JSON parse failed", { payloadId, error: e, preview: (node.textContent || "").slice(0, 200) });
        return {};
      }
    }

    // 2) Fallback: inline payload attribute
    const raw = el.getAttribute("data-chart-payload");
    if (raw) {
      try {
        let parsed = JSON.parse(raw);
        if (typeof parsed === "string") parsed = JSON.parse(parsed);
        return parsed || {};
      } catch (e) {
        console.error("❌ data-chart-payload JSON parse failed", { error: e, preview: raw.slice(0, 200) });
        return {};
      }
    }

    return {};
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
          size: rr.map(r => Math.max(10, Math.sqrt(r[sizeKey] || 0) * 1.2)),
          opacity: 0.78,
          line: { width: 1, color: "rgba(30,60,90,.18)" }
        }
      };
    });

    const layout = baseLayout("Volume vs Risk — Hotspots");
    layout.xaxis.title = "Discharges (volume)";
    layout.yaxis.title = "Excess Readmission Ratio";
    layout.yaxis.range = [0.85, 1.28];

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
        "Impact Score: %{x:.1f}<br><extra></extra>",
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
      by[m] = by[m] || { sumRatio: 0, sumDis: 0, n: 0, sumImpact: 0 };
      by[m].sumRatio += (r.excess_ratio || 0);
      by[m].sumDis += (r.discharges || 0);
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

  // Synthetic demo charts
  function rand(seed) {
    let t = seed >>> 0;
    return function () {
      t += 0x6D2B79F5;
      let x = t;
      x = Math.imul(x ^ (x >>> 15), x | 1);
      x ^= x + Math.imul(x ^ (x >>> 7), x | 61);
      return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
    };
  }

  function syntheticRiskScatter(el, payload) {
    const seed = payload.seed || 7;
    const n = payload.n || 240;
    const r = rand(seed);

    const prob = [];
    const amt = [];
    const tier = [];

    for (let i = 0; i < n; i++) {
      const p = Math.min(0.98, Math.max(0.02, (Math.pow(r(), 1.7))));
      const a = 2000 + Math.round(Math.pow(r(), 0.35) * 48000);
      prob.push(p);
      amt.push(a);

      let t = "Prime";
      if (p > 0.55 && a > 24000) t = "Caution";
      else if (p > 0.40) t = "Balanced";
      else if (p > 0.25) t = "Growth";
      tier.push(t);
    }

    const tiers = ["Prime", "Growth", "Balanced", "Caution"];
    const traces = tiers.map(name => {
      const idxs = tier.map((t, i) => t === name ? i : -1).filter(i => i >= 0);
      return {
        type: "scatter",
        mode: "markers",
        name,
        x: idxs.map(i => prob[i]),
        y: idxs.map(i => amt[i]),
        marker: { size: 10, opacity: 0.75, line: { width: 1, color: "rgba(30,60,90,.18)" } },
        hovertemplate: "<b>" + name + "</b><br>Default prob: %{x:.2f}<br>Amount: $%{y}<br><extra></extra>"
      };
    });

    const layout = baseLayout("Risk Tier Map — Probability vs Amount");
    layout.xaxis.title = "Default Probability";
    layout.yaxis.title = "Loan Amount ($)";

    Plotly.newPlot(el, traces, layout, plotConfig());
  }

  function syntheticDriverWaterfall(el, payload) {
    const seed = payload.seed || 11;
    const r = rand(seed);

    const drivers = ["DTI", "FICO", "Income", "Utilization", "Delinquencies", "Employment Length", "Loan Term"];
    const deltas = drivers.map(() => (r() - 0.5) * 0.22);
    deltas[1] = -Math.abs(deltas[1]) - 0.05;

    const trace = {
      type: "waterfall",
      orientation: "v",
      x: drivers,
      y: deltas,
      measure: drivers.map(() => "relative"),
      connector: { line: { color: "rgba(30,60,90,.18)" } },
      hovertemplate: "<b>%{x}</b><br>Δ Risk: %{y:.3f}<br><extra></extra>"
    };

    const layout = baseLayout("Driver Waterfall — Portfolio Risk Contributions");
    layout.yaxis.title = "Δ Risk Contribution";

    Plotly.newPlot(el, [trace], layout, plotConfig());
  }

  function syntheticTierBars(el, payload) {
    const seed = payload.seed || 19;
    const r = rand(seed);

    const tiers = ["Prime", "Growth", "Balanced", "Caution"];
    const values = tiers.map(() => 10 + Math.round(r() * 30));
    const sum = values.reduce((a, b) => a + b, 0);
    const pct = values.map(v => Math.round((v / sum) * 100));

    const trace = {
      type: "bar",
      x: tiers,
      y: pct,
      hovertemplate: "<b>%{x}</b><br>%{y}% of portfolio<br><extra></extra>",
      opacity: 0.82,
      marker: { line: { width: 1, color: "rgba(30,60,90,.16)" } }
    };

    const layout = baseLayout("Tier Mix — Portfolio Composition");
    layout.yaxis.title = "% of portfolio";
    layout.yaxis.range = [0, 70];

    Plotly.newPlot(el, [trace], layout, plotConfig());
  }

  // ----------------------------
  // Render a single chart
  // ----------------------------
  function renderOne(el) {
    const type = el.getAttribute("data-chart-type");
    const payload = parsePayload(el);

    // clear loading
    const loading = qs(".viz__loading", el);
    if (loading) loading.remove();

    // Ensure chart has height
    if (!el.style.minHeight) el.style.minHeight = "360px";

    if (!window.Plotly) {
      el.innerHTML = "<div style='padding:14px;font-weight:850;color:crimson'>Plotly not loaded.</div>";
      console.error("❌ Plotly missing. Check CSP / script loading.");
      return;
    }

    switch (type) {
      case "bubble_volume_risk": return bubbleVolumeRisk(el, payload);
      case "leaderboard_impact": return leaderboardImpact(el, payload);
      case "measure_risk_bars": return measureRiskBars(el, payload);
      case "state_heatmap": return stateHeatmap(el, payload);

      case "synthetic_risk_scatter": return syntheticRiskScatter(el, payload);
      case "synthetic_driver_waterfall": return syntheticDriverWaterfall(el, payload);
      case "synthetic_tier_bars": return syntheticTierBars(el, payload);

      default:
        el.innerHTML = "<div style='padding:14px;font-weight:850;color:rgba(18,28,38,.72)'>Unknown chart type: " + type + "</div>";
        console.warn("Unknown chart type:", type, el);
    }
  }

  function initCharts() {
    const charts = qsa(".viz__chart[data-chart-type]");
    console.log("📊 Charts found:", charts.length);

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
          try { Plotly.Plots.resize(el); } catch (_) { }
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
