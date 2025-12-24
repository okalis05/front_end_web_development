function qs(sel, root=document){ return root.querySelector(sel); }
function qsa(sel, root=document){ return Array.from(root.querySelectorAll(sel)); }

function initParticles(){
  const c = qs("#pl-particles");
  if(!c) return;
  const ctx = c.getContext("2d");
  let w=0,h=0;

  function resize(){
    w = c.width = window.innerWidth * devicePixelRatio;
    h = c.height = window.innerHeight * devicePixelRatio;
    c.style.width = window.innerWidth + "px";
    c.style.height = window.innerHeight + "px";
  }
  window.addEventListener("resize", resize);
  resize();

  const N = 75;
  const pts = new Array(N).fill(0).map(() => ({
    x: Math.random()*w,
    y: Math.random()*h,
    vx: (Math.random()-.5)*0.35*devicePixelRatio,
    vy: (Math.random()-.5)*0.35*devicePixelRatio,
    r: (2 + Math.random()*3)*devicePixelRatio,
    k: Math.random()
  }));

  function step(){
    ctx.clearRect(0,0,w,h);
    for(const p of pts){
      p.x += p.vx; p.y += p.vy;
      if(p.x<0||p.x>w) p.vx*=-1;
      if(p.y<0||p.y>h) p.vy*=-1;

      const g = ctx.createRadialGradient(p.x,p.y,0,p.x,p.y,p.r*6);
      g.addColorStop(0, `rgba(255,255,255,${0.12 + 0.10*p.k})`);
      g.addColorStop(1, "rgba(255,255,255,0)");
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(p.x,p.y,p.r*6,0,Math.PI*2);
      ctx.fill();
    }
    requestAnimationFrame(step);
  }
  step();
}

function initCharts(){
  if(!window.Chart) return;
  const c1 = qs("#chartSuccess");
  const c2 = qs("#chartRuntime");
  if(!c1 || !c2) return;

  // Demo fallback (you can replace later with real API-based data)
  const labels = ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"];
  const success = [6,7,6,8,7,8,9];
  const runtime = [120, 98, 140, 105, 115, 90, 110];

  new Chart(c1, { type: "line",
    data: { labels, datasets: [{ label:"Success", data: success, tension: .35 }] },
    options: { responsive:true, plugins:{ legend:{ display:false } }, scales:{ x:{ grid:{ display:false } }, y:{ grid:{ display:false } } } }
  });

  new Chart(c2, { type: "bar",
    data: { labels, datasets: [{ label:"Runtime", data: runtime }] },
    options: { responsive:true, plugins:{ legend:{ display:false } }, scales:{ x:{ grid:{ display:false } }, y:{ grid:{ display:false } } } }
  });
}

function initThemeToggle(){
  const btn = document.getElementById("themeToggle");
  if(!btn) return;

  const key = "pipeline-theme";
  const apply = (mode) => {
    document.body.classList.toggle("pl-light", mode === "light");
    btn.textContent = mode === "light" ? "🌙 Dark" : "☀️ Light";
  };

  const saved = localStorage.getItem(key) || "dark";
  apply(saved);

  btn.addEventListener("click", () => {
    const next = document.body.classList.contains("pl-light") ? "dark" : "light";
    localStorage.setItem(key, next);
    apply(next);
  });
}

function initToggles(){
  const btn = qs(".pl-toggle[data-toggle='docs']");
  const hidden = qs("#generate_docs");
  if(!btn || !hidden) return;

  function sync(){
    const on = hidden.value === "true";
    btn.textContent = on ? "Docs: ON" : "Docs: OFF";
    btn.style.opacity = on ? "1" : ".72";
  }
  btn.addEventListener("click", () => {
    hidden.value = (hidden.value === "true") ? "false" : "true";
    sync();
  });
  sync();
}

async function refreshRun(runId){
  const res = await fetch(`/pipeline/api/runs/${runId}/refresh/`, {headers: {"X-Requested-With":"fetch"}});
  const data = await res.json();
  if(!data.ok) throw new Error(data.error || "refresh failed");
  return data.run;
}

function initRunRefresh(){
  const btn = qs("#refreshRunBtn");
  if(!btn) return;
  const runId = btn.getAttribute("data-run");

  const statusEl = qs("#runStatus");
  const prefectEl = qs("#prefectState");
  const durEl = qs("#runDuration");

  btn.addEventListener("click", async () => {
    btn.disabled = true;
    btn.textContent = "Refreshing…";
    try{
      const r = await refreshRun(runId);
      if(statusEl){
        statusEl.textContent = r.status;
        statusEl.className = `pl-status pl-status-${(r.status||"unknown").toLowerCase()}`;
      }
      if(prefectEl) prefectEl.textContent = r.prefect_state;
      if(durEl) durEl.textContent = (r.duration_seconds ?? "—");
    }catch(e){
      alert(e.message);
    }finally{
      btn.disabled = false;
      btn.textContent = "Refresh Status";
    }
  });

  // Auto-poll if running/pending
  setInterval(async () => {
    const current = (statusEl?.textContent || "").toUpperCase();
    if(!["RUNNING","PENDING"].includes(current)) return;
    try{
      const r = await refreshRun(runId);
      if(statusEl){
        statusEl.textContent = r.status;
        statusEl.className = `pl-status pl-status-${(r.status||"unknown").toLowerCase()}`;
      }
      if(prefectEl) prefectEl.textContent = r.prefect_state;
      if(durEl) durEl.textContent = (r.duration_seconds ?? "—");
    }catch(_e){}
  }, 8000);
}

async function refreshPipelineRuns(slug){
  const res = await fetch(`/pipeline/api/pipelines/${slug}/latest-runs/`, {headers: {"X-Requested-With":"fetch"}});
  return await res.json();
}

function initPipelineRunsAutoRefresh(){
  const table = qs("#runsTable");
  if(!table) return;
  const slug = table.getAttribute("data-pipeline");
  if(!slug) return;

  setInterval(async () => {
    try{
      const data = await refreshPipelineRuns(slug);
      const rows = qsa(".pl-tr", table).slice(1);
      rows.forEach(row => {
        const idCell = row.querySelector(".pl-mono");
        if(!idCell) return;
        const id = parseInt(idCell.textContent.replace("#",""), 10);
        const match = (data.runs || []).find(r => r.id === id);
        if(!match) return;

        const pill = row.querySelector(".pl-status");
        if(pill){
          pill.textContent = match.status;
          pill.className = `pl-status pl-status-${(match.status||"unknown").toLowerCase()}`;
        }
        const monos = row.querySelectorAll(".pl-mono");
        if(monos.length > 1) monos[1].textContent = match.prefect_state;
      });
    }catch(_e){}
  }, 9000);
}

function initPipelineWebSocket(){
  const table = document.getElementById("runsTable");
  if(!table) return;
  const slug = table.getAttribute("data-pipeline");
  if(!slug) return;

  const proto = window.location.protocol === "https:" ? "wss" : "ws";
  const ws = new WebSocket(`${proto}://${window.location.host}/ws/pipeline/${slug}/`);

  ws.onmessage = (msg) => {
    let data = null;
    try { data = JSON.parse(msg.data); } catch { return; }
    if(!data || !data.run_id) return;

    const rows = Array.from(table.querySelectorAll(".pl-tr")).slice(1);
    for(const row of rows){
      const idCell = row.querySelector(".pl-mono");
      if(!idCell) continue;
      const id = parseInt(idCell.textContent.replace("#",""), 10);
      if(id !== data.run_id) continue;

      const pill = row.querySelector(".pl-status");
      if(pill){
        pill.textContent = data.status;
        pill.className = `pl-status pl-status-${(data.status||"unknown").toLowerCase()}`;
      }
      const monos = row.querySelectorAll(".pl-mono");
      if(monos.length > 1) monos[1].textContent = data.prefect_state || "UNKNOWN";
      break;
    }
  };

  ws.onclose = () => {
    // polling fallback already running
  };
}

document.addEventListener("DOMContentLoaded", () => {
  initParticles();
  initCharts();
  initThemeToggle();
  initToggles();
  initRunRefresh();
  initPipelineRunsAutoRefresh();
  initPipelineWebSocket();
});
