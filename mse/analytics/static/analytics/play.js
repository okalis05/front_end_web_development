// ========= Keep your old button action if you still want it =========
function moveElem(){
  const c = document.getElementById('canfun');
  if (!c) return;
  c.innerHTML = 'Hello!';
  c.style.color = 'red';
  c.style.fontSize = '100px';
}

// ========= Main scene controller =========
(() => {
  const root = document.documentElement;
  const body = document.body;

  const statusEl = document.getElementById("status");
  const btnNight = document.getElementById("btnNight");
  const btnAudio = document.getElementById("btnAudio");
  const btnDemo  = document.getElementById("btnDemo");

  const setStatus = (msg) => { if (statusEl) statusEl.textContent = msg; };

  // ---- Night toggle
  function setNight(on) {
    body.classList.toggle("night", !!on);
    if (btnNight) {
      btnNight.setAttribute("aria-pressed", String(!!on));
      btnNight.textContent = on ? "☀️ Day" : "🌙 Night";
    }
  }
  btnNight?.addEventListener("click", () => setNight(!body.classList.contains("night")));
  setNight(false);

  // ---- Mouse parallax + tide influence
  let mx = 0.5, my = 0.5;
  let tide = 0.62;
  let tideMouseTarget = 0.62;

  window.addEventListener("mousemove", (e) => {
    mx = e.clientX / Math.max(1, window.innerWidth);
    my = e.clientY / Math.max(1, window.innerHeight);

    root.style.setProperty("--mx", mx.toFixed(4));
    root.style.setProperty("--my", my.toFixed(4));

    // Up = more water
    tideMouseTarget = 0.34 + (1 - my) * 0.42; // ~0.34..0.76
  });

  // ---- Sound (mic) + demo
  let audioCtx = null;
  let analyser = null;
  let micStream = null;
  let amp = 0;
  let demo = false;

  const timeData = new Uint8Array(2048);

  function autoTidePhase(nowMs) {
    const t = (nowMs / 1000) / 9; // 9s cycle
    const s = (Math.sin(t * 2 * Math.PI) + 1) / 2; // 0..1
    return s < 0.5 ? 2 * s * s : 1 - Math.pow(-2 * s + 2, 2) / 2;
  }

  function demoAmp(nowMs) {
    const t = nowMs / 1000;
    const a = (Math.sin(t * 3.2) + 1) / 2;
    const b = (Math.sin(t * 1.7 + 1.1) + 1) / 2;
    return Math.min(1, (a * 0.55 + b * 0.45));
  }

  async function enableMic() {
    demo = false;

    if (!window.isSecureContext) {
      setStatus("Sound blocked: use http://localhost:8000 (NOT 127.0.0.1) or HTTPS.");
      return;
    }
    if (!navigator.mediaDevices?.getUserMedia) {
      setStatus("Sound blocked: getUserMedia not supported in this browser.");
      return;
    }

    try {
      setStatus("Requesting microphone permission…");

      micStream = await navigator.mediaDevices.getUserMedia({
        audio: { echoCancellation: true, noiseSuppression: true, autoGainControl: true }
      });

      audioCtx = new (window.AudioContext || window.webkitAudioContext)();
      await audioCtx.resume();

      analyser = audioCtx.createAnalyser();
      analyser.fftSize = 2048;

      const src = audioCtx.createMediaStreamSource(micStream);
      src.connect(analyser);

      if (btnAudio) {
        btnAudio.textContent = "🎧 Sound ON";
        btnAudio.disabled = true;
      }
      setStatus("Microphone enabled. Speak/clap to push the tide.");
    } catch (err) {
      console.error(err);
      setStatus(`Mic error: ${err?.name || "Unknown"} — ${err?.message || ""}`.trim());
    }
  }

  function enableDemo() {
    demo = true;
    analyser = null;
    if (btnAudio) {
      btnAudio.textContent = "🎤 Enable Sound";
      btnAudio.disabled = false;
    }
    setStatus("Demo mode ON: simulated sound drives the wave.");
  }

  btnAudio?.addEventListener("click", enableMic);
  btnDemo?.addEventListener("click", enableDemo);

  // ---- Loop
  function tick(nowMs) {
    const phase = autoTidePhase(nowMs);
    const autoTide = 0.40 + phase * 0.30; // 0.40..0.70

    if (analyser) {
      analyser.getByteTimeDomainData(timeData);

      let sum = 0;
      for (let i = 0; i < timeData.length; i++) {
        const v = (timeData[i] - 128) / 128;
        sum += v * v;
      }
      const rms = Math.sqrt(sum / timeData.length);
      amp = Math.min(1, Math.max(0, (rms - 0.02) * 7.5));
    } else if (demo) {
      amp = demoAmp(nowMs) * 0.92;
    } else {
      amp *= 0.92;
    }

    const target = (autoTide * 0.55) + (tideMouseTarget * 0.45) + (amp * 0.08);
    tide += (target - tide) * 0.06;

    root.style.setProperty("--tide", tide.toFixed(4));
    root.style.setProperty("--amp", amp.toFixed(4));

    requestAnimationFrame(tick);
  }

  setStatus(
    window.isSecureContext
      ? "Mouse up/down controls tide. Use 🔁 Demo Sound (always works) or 🎤 Enable Sound (mic)."
      : "Use 🔁 Demo Sound. Mic requires http://localhost:8000 or HTTPS (secure context)."
  );

  requestAnimationFrame(tick);

  window.addEventListener("beforeunload", () => {
    try {
      micStream?.getTracks()?.forEach(t => t.stop());
      audioCtx?.close();
    } catch {}
  });
})();
