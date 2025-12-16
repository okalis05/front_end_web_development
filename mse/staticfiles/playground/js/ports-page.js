// playground/static/playground/js/ports-page.js

import { loadBorderData, YEARS } from "./border-data.js";

// DOM references
const portSelect = document.getElementById("port-select");
const yearSelect = document.getElementById("year-select");
const portInfo = document.getElementById("port-info");

const barChartEl = document.getElementById("bar-chart");
const lineChartEl = document.getElementById("line-chart");
const bubbleChartEl = document.getElementById("bubble-chart");

let ports = [];
let years = [];
let totalsByYear = {};

function formatNumber(n) {
  return Number(n || 0).toLocaleString("en-US");
}

function getPortSeries(port) {
  return years.map((y) => ({
    year: y,
    value: port.totalsByYear[y] || 0,
  }));
}

function renderPortNarrative(port) {
  if (!port) {
    portInfo.value = "Select a port to see its details and Value trends.";
    return;
  }

  const coords =
    Number.isFinite(port.lat) && Number.isFinite(port.lon)
      ? `${port.lat.toFixed(3)}, ${port.lon.toFixed(3)}`
      : "N/A";

  const measures = port.measures && port.measures.size
    ? Array.from(port.measures).join(", ")
    : "N/A";

  portInfo.value = `
Port: ${port.portName}
State: ${port.state || "N/A"}
Border: ${port.border || "N/A"}
Coordinates: ${coords}
Measures: ${measures}
Number of Encounters (2020–2025): ${formatNumber(port.totalValue)}
  `.trim();
}

/* ---------- Plotly charts ---------- */

function renderBarChart(port, series) {
  const x = series.map((d) => d.year);
  const y = series.map((d) => d.value);

  const data = [
    {
      x,
      y,
      type: "bar",
      marker: {
        color: "rgba(13,110,253,0.85)",
      },
      hovertemplate: "Year %{x}<br>Value %{y:,}<extra></extra>",
    },
  ];

  const layout = {
    title: port
      ? `Annual Value for ${port.portName}`
      : "Annual Value (select a port)",
    margin: { t: 40, r: 10, l: 50, b: 40 },
    height: 260,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    xaxis: {
      title: "Year",
      tickmode: "array",
      tickvals: YEARS,
    },
    yaxis: {
      title: "Value",
      rangemode: "tozero",
    },
  };

  Plotly.newPlot(barChartEl, data, layout, { responsive: true });
}

function renderLineChart(port, series) {
  const x = series.map((d) => d.year);
  const y = series.map((d) => d.value);

  const data = [
    {
      x,
      y,
      type: "scatter",
      mode: "lines+markers",
      line: {
        shape: "spline",
        color: "rgba(230,57,70,0.95)",
        width: 3,
      },
      marker: {
        size: 8,
        color: "rgba(230,57,70,1)",
      },
      hovertemplate: "Year %{x}<br>Value %{y:,}<extra></extra>",
    },
  ];

  const layout = {
    title: port
      ? `Value Trend for ${port.portName}`
      : "Value Trend (select a port)",
    margin: { t: 40, r: 10, l: 50, b: 40 },
    height: 260,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    xaxis: {
      title: "Year",
      tickmode: "array",
      tickvals: YEARS,
    },
    yaxis: {
      title: "Value",
      rangemode: "tozero",
    },
  };

  Plotly.newPlot(lineChartEl, data, layout, { responsive: true });
}

function renderBubbleChart(year) {
  if (!year) {
    Plotly.newPlot(
      bubbleChartEl,
      [],
      {
        title: "Value by Port (select a year)",
        margin: { t: 40, r: 10, l: 50, b: 80 },
        height: 260,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
      },
      { responsive: true }
    );
    return;
  }

  const yearInt = Number(year);

  const filtered = ports
    .map((p) => ({
      name: p.portName,
      state: p.state,
      border: p.border,
      value: p.totalsByYear[yearInt] || 0,
    }))
    .filter((p) => p.value > 0);

  if (!filtered.length) {
    Plotly.newPlot(
      bubbleChartEl,
      [],
      {
        title: `Value by Port (${yearInt}) — no data`,
        margin: { t: 40, r: 10, l: 50, b: 80 },
        height: 260,
        paper_bgcolor: "rgba(0,0,0,0)",
        plot_bgcolor: "rgba(0,0,0,0)",
      },
      { responsive: true }
    );
    return;
  }

  const x = filtered.map((p) => p.name);
  const y = filtered.map((p) => p.value);
  const text = filtered.map(
    (p) =>
      `${p.name} (${p.state || "N/A"})<br>Border: ${p.border || "N/A"}<br>Value: ${formatNumber(
        p.value
      )}`
  );

  const maxVal = Math.max(...y) || 1;

  const data = [
    {
      x,
      y,
      text,
      mode: "markers",
      marker: {
        size: y.map((v) => 10 + 40 * (v / maxVal)),
        sizemode: "area",
        color: y,
        colorscale: "Blues",
        opacity: 0.8,
      },
      hovertemplate: "%{text}<extra></extra>",
    },
  ];

  const layout = {
    title: `Value by Port (${yearInt})`,
    margin: { t: 40, r: 10, l: 50, b: 80 },
    height: 260,
    paper_bgcolor: "rgba(0,0,0,0)",
    plot_bgcolor: "rgba(0,0,0,0)",
    xaxis: {
      title: "Port",
      tickangle: -40,
    },
    yaxis: {
      title: "Value",
      rangemode: "tozero",
    },
  };

  Plotly.newPlot(bubbleChartEl, data, layout, { responsive: true });
}

/* ---------- Event handlers ---------- */

function handlePortChange() {
  const key = portSelect.value;
  const port = ports.find((p) => p.key === key);
  if (!port) {
    renderPortNarrative(null);
    renderBarChart(null, YEARS.map((y) => ({ year: y, value: 0 })));
    renderLineChart(null, YEARS.map((y) => ({ year: y, value: 0 })));
    return;
  }

  const series = getPortSeries(port);
  renderPortNarrative(port);
  renderBarChart(port, series);
  renderLineChart(port, series);
}

function handleYearChange() {
  const yearVal = yearSelect.value;
  renderBubbleChart(yearVal);
}

/* ---------- Init ---------- */

async function init() {
  try {
    const data = await loadBorderData();
    ports = data.ports || [];
    years = data.years || YEARS;
    totalsByYear = data.totalsByYear || {};

    // Populate port dropdown
    portSelect.innerHTML =
      `<option value="">Select a port...</option>` +
      ports
        .map((p) => {
          const label = `${p.portName}${
            p.state ? " (" + p.state + ")" : ""
          }${p.border ? " • " + p.border : ""}`;
          return `<option value="${p.key}">${label}</option>`;
        })
        .join("");

    // Populate year dropdown (for bubble chart)
    yearSelect.innerHTML =
      `<option value="">Year...</option>` +
      years.map((y) => `<option value="${y}">${y}</option>`).join("");

    // Default selections: first port + latest year (if available)
    if (ports.length) {
      portSelect.value = ports[0].key;
      handlePortChange();
    } else {
      renderPortNarrative(null);
      renderBarChart(null, YEARS.map((y) => ({ year: y, value: 0 })));
      renderLineChart(null, YEARS.map((y) => ({ year: y, value: 0 })));
    }

    if (years.length) {
      const latestYear = Math.max(...years);
      yearSelect.value = String(latestYear);
      renderBubbleChart(latestYear);
    } else {
      renderBubbleChart(null);
    }

    portSelect.addEventListener("change", handlePortChange);
    yearSelect.addEventListener("change", handleYearChange);
  } catch (err) {
    console.error("Error initializing Port Analytics:", err);
    portInfo.value = "Error loading data. Please try again later.";
  }
}

document.addEventListener("DOMContentLoaded", init);

