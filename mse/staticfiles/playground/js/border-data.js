

const DATA_URL =
  "https://data.transportation.gov/api/views/keg4-3bc2/rows.json?accessType=DOWNLOAD";

export const YEARS = [2020, 2021, 2022, 2023, 2024, 2025];

let cache = null;

function toNumber(x) {
  if (x === null || x === undefined || x === "") return 0;
  const n = Number(x);
  return Number.isFinite(n) ? n : 0;
}

function yearFromDate(d) {
  if (!d) return null;
  const y = new Date(d).getFullYear();
  return Number.isFinite(y) ? y : null;
}

function parseLatLon(row) {
  const latRaw = row[15];
  const lonRaw = row[16];

  const lat = Number.parseFloat(latRaw);
  const lon = Number.parseFloat(lonRaw);

  return {
    lat: Number.isFinite(lat) ? lat : null,
    lon: Number.isFinite(lon) ? lon : null,
  };
}

async function fetchRows() {
  const res = await fetch(DATA_URL);
  if (!res.ok) {
    throw new Error(`Failed to fetch dataset: ${res.status} ${res.statusText}`);
  }
  const json = await res.json();
  return json.data || [];
}

// Build aggregates from rows.json
function buildAggregates(rows) {
  const portsMap = new Map();
  const totalsByYear = {};
  const yearsSeen = new Set();

  for (const row of rows) {
    const portName = row[8];
    if (!portName) continue;

    const state = row[9] || null;
    const border = row[11] || null;
    const dateStr = row[12];
    const measure = row[13] || null; // currently not used for filtering
    const value = toNumber(row[14]);

    const year = yearFromDate(dateStr);
    if (!year || year < 2020 || year > 2025) continue;

    const key = `${portName}||${state || ""}||${border || ""}`;

    if (!portsMap.has(key)) {
      const { lat, lon } = parseLatLon(row);
      portsMap.set(key, {
        key,
        portName,
        state,
        border,
        lat,
        lon,
        totalsByYear: {},
        totalValue: 0,
        measures: new Set(), // informational
      });
    }

    const port = portsMap.get(key);
    port.totalsByYear[year] = (port.totalsByYear[year] || 0) + value;
    port.totalValue += value;
    if (measure) port.measures.add(measure);

    totalsByYear[year] = (totalsByYear[year] || 0) + value;
    yearsSeen.add(year);
  }

  const ports = Array.from(portsMap.values())
    .filter((p) => p.totalValue > 0)
    .sort((a, b) => b.totalValue - a.totalValue);

  const years = YEARS.filter((y) => yearsSeen.has(y));

  return {
    ports,
    years,
    totalsByYear,
  };
}

export async function loadBorderData() {
  if (cache) return cache;
  const rows = await fetchRows();
  const agg = buildAggregates(rows);
  cache = agg;
  return agg;
}

