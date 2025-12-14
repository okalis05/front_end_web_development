// playground/static/playground/js/insights-page.js
import { loadBorderData } from "./border-data.js";

let ports = [];
let years = [];

// Elements
const portASelect = document.getElementById("port-a-select");
const portBSelect = document.getElementById("port-b-select");
const aiSummaryEl = document.getElementById("ai-summary");

const compareBarDiv = document.getElementById("compare-bar");
const portALineDiv = document.getElementById("port-a-line");
const portBLineDiv = document.getElementById("port-b-line");

const playButton = document.getElementById("year-play-toggle");
const yearLabel = document.getElementById("current-year-label");
const mapContainerId = "time-map";

// Map animation globals
let map;
let portMarkers = [];
let maxByYear = {};
let currentYearIndex = 0;
let animationTimer = null;

/* ---------- Helpers ---------- */

function formatNumber(n) {
  return Number(n || 0).toLocaleString("en-US");
}

function getSeries(port) {
  return years.map((y) => ({
    year: y,
    value: port.totalsByYear[y] || 0,
  }));
}

function findPortByKey(key) {
  if (!key) return null;
  return ports.find((p) => p.key === key) || null;
}

/* ---------- AI-style narrative ---------- */

function buildPortNarrative(port) {
  if (!port) return null;
  const series = getSeries(port);
  const nonZero = series.filter((d) => d.value > 0);

  if (!nonZero.length) {
    return `For port ${port.portName}, there is no recorded Value between ${years[0]} and ${
      years[years.length - 1]
    }.`;
  }

  const total = nonZero.reduce((sum, d) => sum + d.value, 0);
  const peak = nonZero.reduce(
    (best, d) => (d.value > best.value ? d : best),
    nonZero[0]
  );
  const firstYear = years[0];
  const lastYear = years[years.length - 1];
  const firstVal = port.totalsByYear[firstYear] || 0;
  const lastVal = port.totalsByYear[lastYear] || 0;
  const delta = lastVal - firstVal;
  const trend =
    delta > 0
      ? "an overall upward trend"
      : delta < 0
      ? "a slight decline over time"
      : "a relatively stable pattern";

  return [
    `Between ${firstYear} and ${lastYear}, port ${port.portName}${
      port.state ? " (" + port.state + ")" : ""
    } recorded a total Value of ${formatNumber(total)}.`,
    `Traffic peaked in ${peak.year} with ${formatNumber(
      peak.value
    )} units of Value, indicating a local maximum in border activity.`,
    `Comparing the start and end of the period, ${firstYear} logged ${formatNumber(
      firstVal
    )}, while ${lastYear} reached ${formatNumber(lastVal)}, suggesting ${trend}.`,
  ].join(" ");
}

function updateAiSummary(portA, portB) {
  const parts = [];

  const aText = buildPortNarrative(portA);
  const bText = buildPortNarrative(portB);

  if (aText) {
    parts.push("🔹 Port A — " + aText);
  }
  if (bText) {
    parts.push("🔸 Port B — " + bText);
  }

  if (portA && portB) {
    const totalA = years.reduce(
      (sum, y) => sum + (portA.totalsByYear[y] || 0),
      0
    );
    const totalB = years.reduce(
      (sum, y) => sum + (portB.totalsByYear[y] || 0),
      0
    );
    const winner =
      totalA > totalB
        ? `${portA.portName} has a higher cumulative Value than ${portB.portName}.`
        : totalB > totalA
        ? `${portB.portName} has a higher cumulative Value than ${portA.portName}.`
        : `Both ports show very similar cumulative Value over the observed period.`;

    parts.push(
      `📊 In direct comparison, Port A totals ${formatNumber(
        totalA
      )} while Port B totals ${formatNumber(totalB)}. ${winner}`
    );
  }

  aiSummaryEl.textContent = parts.length
    ? parts.join("\n\n")
    : "Select Port A and/or Port B to generate an AI-style narrative summary based on historical Value (2020–2025).";
}

/* ---------- Plotly charts ---------- */

function renderComparisonBar(portA, portB) {
  const traces = [];

  if (portA) {
    const seriesA = getSeries(portA);
    traces.push({
      x: seriesA.map((d) => d.year),
      y: seriesA.map((d) => d.value),
      name: portA.portName,
      type: "bar",
      marker: {
        color: "#0d6efd",
      },
    });
  }

  if (portB) {
    const seriesB = getSeries(portB);
    traces.push({
      x: seriesB.map((d) => d.year),
      y: seriesB.map((d) => d.value),
      name: portB.portName,
      type: "bar",
      marker: {
        color: "#e63946",
      },
    });
  }

  const layout = {
    margin: { t: 20, r: 10, l: 50, b: 40 },
    barmode: "group",
    xaxis: {
      title: "Year",
      tickmode: "linear",
      dtick: 1,
    },
    yaxis: {
      title: "Total Value",
      rangemode: "tozero",
    },
    legend: { orientation: "h", y: -0.2 },
  };

  Plotly.newPlot(compareBarDiv, traces, layout, { responsive: true });
}

function renderPortLineChart(port, targetDiv, color) {
  if (!port || !targetDiv) {
    Plotly.purge(targetDiv);
    return;
  }

  const series = getSeries(port);

  const trace = {
    x: series.map((d) => d.year),
    y: series.map((d) => d.value),
    mode: "lines+markers",
    line: {
      color: color,
      width: 3,
    },
    marker: {
      size: 8,
    },
    type: "scatter",
  };

  const layout = {
    margin: { t: 20, r: 10, l: 50, b: 40 },
    xaxis: {
      title: "Year",
      tickmode: "linear",
      dtick: 1,
    },
    yaxis: {
      title: "Value",
      rangemode: "tozero",
    },
  };

  Plotly.newPlot(targetDiv, [trace], layout, { responsive: true });
}

/* ---------- Leaflet time-animated bubble map ---------- */

function computeMaxByYear() {
  maxByYear = {};
  years.forEach((y) => {
    let maxVal = 0;
    ports.forEach((p) => {
      const v = p.totalsByYear[y] || 0;
      if (v > maxVal) maxVal = v;
    });
    maxByYear[y] = maxVal || 1;
  });
}

function initMap() {
  map = L.map(mapContainerId, {
    scrollWheelZoom: false,
  }).setView([39.8283, -98.5795], 4);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 18,
  }).addTo(map);

  // Create markers for each port with lat/lon
  portMarkers = [];
  ports.forEach((p) => {
    if (p.lat == null || p.lon == null) return;

    const circle = L.circleMarker([p.lat, p.lon], {
      radius: 4,
      fillColor: "#f97316",
      color: "#ea580c",
      weight: 1,
      fillOpacity: 0.75,
    }).addTo(map);

    circle.bindPopup(
      `<strong>${p.portName}${
        p.state ? " (" + p.state + ")" : ""
      }</strong><br>Year: <span class="map-year">—</span><br>Value: <span class="map-value">—</span>`
    );

    portMarkers.push({ port: p, circle });
  });
}

function updateMapForYear(year) {
  if (!map || !portMarkers.length) return;

  const maxVal = maxByYear[year] || 1;

  portMarkers.forEach(({ port, circle }) => {
    const value = port.totalsByYear[year] || 0;
    const scale = value / maxVal;
    const radius = value > 0 ? 4 + 20 * scale : 0;

    circle.setRadius(radius);

    // Update popup content
    const popupHtml = `
      <strong>${port.portName}${port.state ? " (" + port.state + ")" : ""}</strong><br>
      Year: ${year}<br>
      Value: ${formatNumber(value)}
    `;
    circle.bindPopup(popupHtml);
  });

  if (yearLabel) {
    yearLabel.textContent = year;
  }
}

function stepYear() {
  if (!years.length) return;
  currentYearIndex = (currentYearIndex + 1) % years.length;
  updateMapForYear(years[currentYearIndex]);
}

function toggleAnimation() {
  if (!years.length) return;

  if (animationTimer) {
    clearInterval(animationTimer);
    animationTimer = null;
    playButton.textContent = "▶ Play";
  } else {
    animationTimer = setInterval(stepYear, 1800);
    playButton.textContent = "⏸ Pause";
  }
}

/* ---------- Wiring everything together ---------- */

function handleSelectionChange() {
  const portA = findPortByKey(portASelect.value);
  const portB = findPortByKey(portBSelect.value);

  updateAiSummary(portA, portB);
  renderComparisonBar(portA, portB);
  renderPortLineChart(portA, portALineDiv, "#0d6efd");
  renderPortLineChart(portB, portBLineDiv, "#e63946");
}

async function init() {
  try {
    const data = await loadBorderData();
    ports = data.ports || [];
    years = data.years || [];

    // Populate selectors
    const optionsHtml = ports
      .map(
        (p) =>
          `<option value="${p.key}">${p.portName}${
            p.state ? " (" + p.state + ")" : ""
          }</option>`
      )
      .join("");

    portASelect.innerHTML += optionsHtml;
    portBSelect.innerHTML += optionsHtml;

    portASelect.addEventListener("change", handleSelectionChange);
    portBSelect.addEventListener("change", handleSelectionChange);

    // Default: auto-select top two ports if available
    if (ports.length > 0) {
      portASelect.value = ports[0].key;
    }
    if (ports.length > 1) {
      portBSelect.value = ports[1].key;
    }
    handleSelectionChange();

    // Map + animation
    computeMaxByYear();
    initMap();
    if (years.length) {
      currentYearIndex = 0;
      updateMapForYear(years[currentYearIndex]);
    }

    if (playButton) {
      playButton.addEventListener("click", toggleAnimation);
    }
  } catch (err) {
    console.error("Failed to initialize AI Insights page:", err);
    if (aiSummaryEl) {
      aiSummaryEl.textContent =
        "Unable to load data for AI Insights. Please try refreshing the page.";
    }
  }
}

document.addEventListener("DOMContentLoaded", init);
