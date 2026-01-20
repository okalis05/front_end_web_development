(() => {
  const root = document.querySelector(".world");
  if (!root) return;

  const industry = root.getAttribute("data-industry");
  const kpiGrid = document.getElementById("kpiGrid");
  const alertStream = document.getElementById("alertStream");

  const liveDot = document.getElementById("liveDot");
  const liveLabel = document.getElementById("liveLabel");
  const liveTime = document.getElementById("liveTime");
  const siren = document.getElementById("siren");

  if (!industry || !kpiGrid || !alertStream) return;

  // -------------------------
  // Visual severity + siren
  // -------------------------
  let maxSeveritySeen = 1;

  function sevColor(sev) {
    if (sev >= 5) return "rgba(255,80,110,.90)";
    if (sev === 4) return "rgba(255,160,80,.82)";
    if (sev === 3) return "rgba(120,190,255,.85)";
    return "rgba(255,255,255,.55)";
  }

  function setSiren(sev) {
    maxSeveritySeen = Math.max(maxSeveritySeen, sev || 1);
    const s = Math.max(1, Math.min(5, maxSeveritySeen));

    // speed + glow scale with severity
    document.documentElement.style.setProperty("--siren-speed", `${Math.max(0.55, 1.35 - (s * 0.16))}s`);
    document.documentElement.style.setProperty("--siren-glow", s >= 5 ? "1" : s === 4 ? "0.7" : "0.35");
    document.documentElement.style.setProperty("--accent-red", s >= 5 ? "rgba(255,80,110,.9)" : "rgba(255,80,110,.55)");
  }

  function setLiveState(state) {
    // state: "live" | "reconnecting" | "offline"
    const now = new Date();
    const stamp = now.toLocaleTimeString();

    if (liveTime) liveTime.textContent = `last ${stamp}`;

    if (!liveDot || !liveLabel) return;

    liveDot.classList.remove("live", "reconnecting", "offline");
    liveLabel.classList.remove("live", "reconnecting", "offline");

    liveDot.classList.add(state);
    liveLabel.classList.add(state);

    if (state === "live") liveLabel.textContent = "LIVE";
    else if (state === "reconnecting") liveLabel.textContent = "RECONNECT";
    else liveLabel.textContent = "OFFLINE";
  }

  // -------------------------
  // Rendering with animation
  // -------------------------
  const metricCache = new Map(); // kpi_key -> {value, ts}

  function animateTick(el, cls) {
    el.classList.remove(cls);
    // force reflow
    void el.offsetWidth;
    el.classList.add(cls);
  }

  function renderKpis(metrics) {
    // keep existing tiles when possible for smooth animations
    const byKey = new Map(metrics.map(m => [m.kpi_key, m]));

    // If first time: build all
    if (kpiGrid.children.length === 0) {
      metrics.forEach(m => {
        const tile = document.createElement("div");
        tile.className = "kpi-tile";
        tile.dataset.kpi = m.kpi_key;

        tile.innerHTML = `
          <div class="kpi-label">${m.label}</div>
          <div class="kpi-value">
            <span class="kpi-num">${Number(m.value).toFixed(2)}</span>
            <span class="kpi-unit">${m.unit}</span>
          </div>
          <div class="kpi-ts">${m.ts ? new Date(m.ts).toLocaleTimeString() : ""}</div>
        `;
        kpiGrid.appendChild(tile);
        metricCache.set(m.kpi_key, { value: m.value, ts: m.ts });
      });
      return;
    }

    // Update existing tiles
    [...kpiGrid.children].forEach(tile => {
      const key = tile.dataset.kpi;
      const m = byKey.get(key);
      if (!m) return;

      const prev = metricCache.get(key);
      const numEl = tile.querySelector(".kpi-num");
      const tsEl = tile.querySelector(".kpi-ts");

      const changed = !prev || Number(prev.value) !== Number(m.value);
      if (numEl) numEl.textContent = Number(m.value).toFixed(2);
      if (tsEl) tsEl.textContent = m.ts ? new Date(m.ts).toLocaleTimeString() : "";

      metricCache.set(key, { value: m.value, ts: m.ts });

      if (changed) animateTick(tile, "tick");
    });
  }

  function prependEvent(e) {
    // empty-state removal
    const empty = alertStream.querySelector("[data-empty='1']");
    if (empty) empty.remove();

    const card = document.createElement("div");
    card.className = "alert";
    card.dataset.eventId = e.id || "";

    const color = sevColor(e.severity);
    card.innerHTML = `
      <div class="alert-top">
        <div class="alert-title">${e.title}</div>
        <div class="alert-pill" style="color:${color}">sev ${e.severity}</div>
      </div>
      <div class="alert-body">${e.body}</div>
      <div class="alert-ts">${e.ts ? new Date(e.ts).toLocaleString() : ""}</div>
    `;
    alertStream.prepend(card);

    animateTick(card, e.severity >= 5 ? "impact" : "arrive");

    // cap stream
    while (alertStream.children.length > 60) {
      alertStream.lastElementChild?.remove();
    }

    setSiren(e.severity);
  }

  function renderEvents(events) {
    alertStream.innerHTML = "";
    if (!events.length) {
      const empty = document.createElement("div");
      empty.dataset.empty = "1";
      empty.style.opacity = "0.6";
      empty.style.fontSize = "14px";
      empty.textContent = "No events yet. The world is quiet…";
      alertStream.appendChild(empty);
      return;
    }

    events.forEach(e => {
      const card = document.createElement("div");
      card.className = "alert";
      card.dataset.eventId = e.id || "";
      card.innerHTML = `
        <div class="alert-top">
          <div class="alert-title">${e.title}</div>
          <div class="alert-pill" style="color:${sevColor(e.severity)}">sev ${e.severity}</div>
        </div>
        <div class="alert-body">${e.body}</div>
        <div class="alert-ts">${new Date(e.ts).toLocaleString()}</div>
      `;
      alertStream.appendChild(card);
      setSiren(e.severity);
    });
  }

  async function fetchJson(url) {
    const res = await fetch(url, { cache: "no-store" });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return res.json();
  }

  // -------------------------
  // Fallback polling
  // -------------------------
  let pollTimer = null;
  async function pollOnce() {
    try {
      const m = await fetchJson(`/sentinel/api/${industry}/metrics/`);
      renderKpis(m.metrics);

      const e = await fetchJson(`/sentinel/api/${industry}/events/?limit=50`);
      renderEvents(e.events);

      setLiveState("reconnecting"); // polling implies "not push-live"
    } catch (err) {
      setLiveState("offline");
    }
  }

  function startPollingFallback() {
    if (pollTimer) return;
    pollOnce();
    pollTimer = setInterval(pollOnce, 2500);
  }

  function stopPollingFallback() {
    if (!pollTimer) return;
    clearInterval(pollTimer);
    pollTimer = null;
  }

  // -------------------------
  // SSE live stream
  // -------------------------
  let es = null;
  let reconnectTimer = null;

  function connectSSE() {
    if (es) return;

    setLiveState("reconnecting");
    try {
      es = new EventSource(`/sentinel/stream/${industry}/`);

      es.addEventListener("open", () => {
        stopPollingFallback();
        setLiveState("live");
      });

      es.addEventListener("error", () => {
        // stream failed; fallback polling + schedule reconnect
        try { es.close(); } catch (_) {}
        es = null;

        setLiveState("offline");
        startPollingFallback();

        if (!reconnectTimer) {
          reconnectTimer = setTimeout(() => {
            reconnectTimer = null;
            connectSSE();
          }, 1800);
        }
      });

      es.addEventListener("metric", (evt) => {
        setLiveState("live");
        try {
          const m = JSON.parse(evt.data);
          // update only one KPI tile (fast)
          const tile = kpiGrid.querySelector(`[data-kpi="${m.kpi_key}"]`);
          if (tile) {
            const numEl = tile.querySelector(".kpi-num");
            const tsEl = tile.querySelector(".kpi-ts");
            const prev = metricCache.get(m.kpi_key);

            if (numEl) numEl.textContent = Number(m.value).toFixed(2);
            if (tsEl) tsEl.textContent = m.ts ? new Date(m.ts).toLocaleTimeString() : "";

            const changed = !prev || Number(prev.value) !== Number(m.value);
            metricCache.set(m.kpi_key, { value: m.value, ts: m.ts });

            if (changed) animateTick(tile, "tick");
          } else {
            // if tile not built yet (first load)
            pollOnce();
          }
        } catch (_) {}
      });

      es.addEventListener("event", (evt) => {
        setLiveState("live");
        try {
          const e = JSON.parse(evt.data);
          prependEvent(e);
        } catch (_) {}
      });

      es.addEventListener("hello", () => {
        setLiveState("live");
      });

    } catch (_) {
      es = null;
      startPollingFallback();
      setLiveState("offline");
    }
  }

  // Initial render (fast) then live stream
  pollOnce().finally(() => connectSSE());
})();
