(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const toast = $("#toast");
  const btnMotion = $("#btnMotion");
  const btnSkip = $("#btnSkip");
  const plates = $$(".plate");
  const topLinks = $$("[data-jump]");

  let motionOn = true;
  let activeSectionId = "hero";

  function showToast(msg) {
    if (!toast) return;
    toast.textContent = msg;
    toast.classList.add("is-on");
    window.clearTimeout(showToast._t);
    showToast._t = window.setTimeout(() => toast.classList.remove("is-on"), 1400);
  }

  function smoothJump(target) {
    const el = typeof target === "string" ? $(target) : target;
    if (!el) return;

    const top = el.getBoundingClientRect().top + window.scrollY - 78;
    window.scrollTo({ top, behavior: "smooth" });
  }

  function setActivePlate(sectionId) {
    plates.forEach(p => {
      const tgt = p.getAttribute("data-target") || "";
      const isActive = tgt === `#${sectionId}`;
      p.classList.toggle("is-active", isActive);
    });
  }

  function wireJumpLinks() {
    topLinks.forEach(a => {
      a.addEventListener("click", (e) => {
        const jump = a.getAttribute("data-jump");
        if (!jump) return;
        // allow normal anchor behavior, but also smooth
        e.preventDefault();
        smoothJump(jump);
      });
    });

    plates.forEach(p => {
      p.addEventListener("click", () => {
        const tgt = p.getAttribute("data-target");
        if (!tgt) return;
        smoothJump(tgt);
        showToast("Teleported");
      });
    });
  }

  function observeSections() {
    const sections = $$("[id][data-section], #hero");
    if (!sections.length) return;

    const io = new IntersectionObserver((entries) => {
      // choose the most visible entry
      const visible = entries
        .filter(e => e.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) return;
      const id = visible.target.id || "hero";
      if (id === activeSectionId) return;

      activeSectionId = id;
      setActivePlate(activeSectionId);

      // keep URL hash in sync (shareable)
      if (id && id !== "hero") {
        history.replaceState(null, "", `#${id}`);
      } else {
        history.replaceState(null, "", location.pathname + location.search);
      }
    }, { threshold: [0.2, 0.33, 0.5, 0.66] });

    sections.forEach(s => io.observe(s));
  }

  function motionTick() {
    if (!motionOn) return;

    const y = window.scrollY;
    plates.forEach((p, i) => {
      const amp = 2.5 + (i * 0.4);
      const t = (y * 0.002) + (i * 0.65);
      const drift = Math.sin(t) * amp;
      p.style.transform = `translateY(${drift}px)`;
    });

    requestAnimationFrame(motionTick);
  }

  function wireMotionToggle() {
    if (!btnMotion) return;
    btnMotion.addEventListener("click", () => {
      motionOn = !motionOn;
      btnMotion.setAttribute("aria-pressed", motionOn ? "true" : "false");
      btnMotion.textContent = motionOn ? "Motion: ON" : "Motion: OFF";
      showToast(motionOn ? "Motion enabled" : "Motion paused");

      if (motionOn) requestAnimationFrame(motionTick);
      if (!motionOn) plates.forEach(p => (p.style.transform = ""));
    });
  }

  function wireTeleportButton() {
    if (!btnSkip) return;
    btnSkip.addEventListener("click", () => {
      const target = activeSectionId && activeSectionId !== "hero"
        ? `#${activeSectionId}`
        : "#executive_overview";
      smoothJump(target);
      showToast("Teleported");
    });
  }

  function initialRouteJump() {
    // if user hits /executive/ etc, we still show landing but jump to the section
    const path = location.pathname;
    const hash = location.hash;

    if (hash && $(hash)) {
      setTimeout(() => smoothJump(hash), 40);
      return;
    }

    // fallback: infer from last path segment
    const map = {
      "executive": "#executive_overview",
      "player": "#player_impact",
      "health": "#health_risk",
      "revenue": "#revenue_fans",
    };

    const seg = (path.split("/").filter(Boolean).slice(-1)[0] || "").toLowerCase();
    if (map[seg] && $(map[seg])) {
      setTimeout(() => smoothJump(map[seg]), 50);
    }
  }

  // Boot
  wireJumpLinks();
  observeSections();
  wireMotionToggle();
  wireTeleportButton();
  setActivePlate(activeSectionId);
  requestAnimationFrame(motionTick);
  initialRouteJump();
})();


function observeSectionEntrances(){
  const sections = document.querySelectorAll(".section");
  const io = new IntersectionObserver(entries=>{
    entries.forEach(e=>{
      if(e.isIntersecting){
        e.target.classList.add("is-visible");
        io.unobserve(e.target);
      }
    });
  }, { threshold: .18 });

  sections.forEach(s=>io.observe(s));
}


const breadcrumbMap = {
  executive_overview: "Executive",
  player_impact: "Player",
  health_risk: "Health",
  revenue_fans: "Revenue",
};

function updateBreadcrumb(sectionId){
  const el = document.getElementById("breadcrumbs");
  if (!el) return;

  const map = {
    hero: "Executive",
    executive_overview: "Executive",
    player_impact: "Player",
    health_risk: "Health",
    revenue_fans: "Revenue",
  };

  const label = map[sectionId];
  if (!label) return;

  el.innerHTML = `
    <span class="crumb">Executive</span>
    <span class="crumb is-active">${label}</span>
  `;
}
