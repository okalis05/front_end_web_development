// playground/static/playground/js/map-page.js

import { loadBorderData } from "./border-data.js";

// Initialize Leaflet map
const map = L.map("border-map", {
  scrollWheelZoom: false,
}).setView([39.8283, -98.5795], 4); // approx center of US

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: "&copy; OpenStreetMap contributors",
}).addTo(map);

async function initMap() {
  try {
    const { ports } = await loadBorderData();

    if (!ports || !ports.length) {
      console.warn("No ports found in dataset.");
      return;
    }

    const maxTotal = Math.max(...ports.map((p) => p.totalValue || 0)) || 1;

    ports.forEach((p) => {
      if (!Number.isFinite(p.lat) || !Number.isFinite(p.lon)) return;

      const radius = 4 + 20 * (p.totalValue / maxTotal);

      const circle = L.circleMarker([p.lat, p.lon], {
        radius,
        fillColor: "#f97316",
        color: "#ea580c",
        weight: 1,
        fillOpacity: 0.8,
      }).addTo(map);

      const measures = Array.from(p.measures || []).join(", ") || "N/A";

      circle.bindPopup(
        `
        <b>${p.portName}</b><br/>
        State: ${p.state || "N/A"}<br/>
        Border: ${p.border || "N/A"}<br/>
        Number of Encounters (2020–2025): <strong>${p.totalValue.toLocaleString()}</strong>
        `
      );
    });
  } catch (err) {
    console.error("Error initializing map:", err);
  }
}

initMap();
