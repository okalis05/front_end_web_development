(() => {
  const canvas = document.getElementById("waveCanvas");
  const option = document.getElementById("portalOption");
  const labelEl = document.getElementById("portalLabel");

  if (!canvas || !option || !labelEl) return;

  const ORDER = ["sports", "mortgage", "retail", "healthcare"];
  const LABEL = {
    sports: "Sports",
    mortgage: "Mortgage",
    retail: "Retail",
    healthcare: "Healthcare"
  };

  let revealedIdx = 0;
  let dir = 1;         // 1 or -1
  let hue = 205;       // base ocean hue
  let t = 0;

  const ctx = canvas.getContext("2d", { alpha: false });

  function resize() {
    const dpr = Math.min(2, window.devicePixelRatio || 1);
    canvas.width = Math.floor(window.innerWidth * dpr);
    canvas.height = Math.floor(window.innerHeight * dpr);
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }

  function ocean(a) {
    return `hsla(${hue}, 85%, 58%, ${a})`;
  }

  function draw() {
    t += 0.008;

    const w = window.innerWidth;
    const h = window.innerHeight;

    // Night base
    const bg = ctx.createLinearGradient(0, 0, 0, h);
    bg.addColorStop(0, "#05060b");
    bg.addColorStop(0.6, "#070a16");
    bg.addColorStop(1, "#070a12");
    ctx.fillStyle = bg;
    ctx.fillRect(0, 0, w, h);

    // Sand region
    const sandTop = Math.floor(h * 0.58);
    const sandGrad = ctx.createLinearGradient(0, sandTop, 0, h);
    sandGrad.addColorStop(0, "rgba(210, 184, 140, 0.10)");
    sandGrad.addColorStop(1, "rgba(210, 184, 140, 0.22)");
    ctx.fillStyle = sandGrad;
    ctx.fillRect(0, sandTop, w, h - sandTop);

    // Subtle grain shimmer
    ctx.globalAlpha = 0.22;
    const step = 6;
    for (let y = sandTop; y < h; y += step) {
      for (let x = 0; x < w; x += step) {
        const g = (Math.sin((x * 0.013 + t) * 12.9898 + (y * 0.011 + t) * 78.233) * 43758.5453) % 1;
        ctx.fillStyle = `rgba(230,210,170,${Math.max(0, g) * 0.06})`;
        ctx.fillRect(x, y, 1.2, 1.2);
      }
    }
    ctx.globalAlpha = 1;

    // Wave boundary
    const horizonY = sandTop;
    const waveAmp = 22 + 8 * Math.sin(t * 0.7);
    const waveLen = 0.011;

    ctx.globalCompositeOperation = "lighter";

    // Under-glow
    ctx.beginPath();
    for (let x = 0; x <= w; x += 2) {
      const phase = t * (dir * 1.2);
      const y = horizonY
        + Math.sin(x * waveLen + phase) * waveAmp
        + Math.sin(x * waveLen * 2.6 + phase * 1.7) * (waveAmp * 0.35);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = ocean(0.25);
    ctx.lineWidth = 18;
    ctx.shadowColor = ocean(0.25);
    ctx.shadowBlur = 28;
    ctx.stroke();
    ctx.shadowBlur = 0;

    // Crest line
    ctx.beginPath();
    for (let x = 0; x <= w; x += 2) {
      const phase = t * (dir * 1.2);
      const y = horizonY
        + Math.sin(x * waveLen + phase) * waveAmp
        + Math.sin(x * waveLen * 2.6 + phase * 1.7) * (waveAmp * 0.35);
      if (x === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    }
    ctx.strokeStyle = ocean(0.65);
    ctx.lineWidth = 3;
    ctx.stroke();

    // Foam
    for (let i = 0; i < 70; i++) {
      const x = (i / 70) * w + (Math.sin(t * 2 + i) * 12);
      const phase = t * (dir * 1.2);
      const y = horizonY
        + Math.sin(x * waveLen + phase) * waveAmp
        + Math.sin(x * waveLen * 2.6 + phase * 1.7) * (waveAmp * 0.35);
      const r = 0.6 + (Math.sin(t * 3 + i) + 1) * 0.6;
      ctx.fillStyle = "rgba(255,255,255,0.18)";
      ctx.beginPath();
      ctx.arc(x, y - 2, r, 0, Math.PI * 2);
      ctx.fill();
    }

    ctx.globalCompositeOperation = "source-over";
    requestAnimationFrame(draw);
  }

  // Direction change -> color shift -> option changes
  function flip() {
    dir = dir === 1 ? -1 : 1;
    hue = (hue + 55) % 360;
    revealedIdx = (revealedIdx + 1) % ORDER.length;

    const key = ORDER[revealedIdx];
    option.dataset.active = key;
    labelEl.textContent = LABEL[key];

    // Option styling becomes “alive” with new hue
    option.style.borderColor = `hsla(${hue}, 90%, 65%, .35)`;
    option.style.background = `linear-gradient(180deg, hsla(${hue}, 90%, 65%, .18), rgba(255,255,255,.06))`;
    option.style.boxShadow = `0 30px 90px rgba(0,0,0,.55), 0 0 0 1px rgba(255,255,255,.10) inset`;
  }

  option.addEventListener("mouseenter", () => {
    const key = option.dataset.active || "sports";
    window.location.href = `/sentinel/${key}/`;
  });

  window.addEventListener("resize", resize);

  resize();
  flip();                 // initialize with correct styling
  setInterval(flip, 4200);
  requestAnimationFrame(draw);
})();
