(function(){
  const key = "store_theme";
  const btn = document.querySelector("[data-theme-toggle]");
  const root = document.documentElement;

  function setTheme(next){
    root.dataset.theme = next;
    localStorage.setItem(key, next);
    if(btn){
      btn.setAttribute("aria-label", next === "dark" ? "Switch to light theme" : "Switch to dark theme");
      btn.innerHTML = next === "dark" ? "<span aria-hidden='true'>☾</span>" : "<span aria-hidden='true'>☀︎</span>";
    }
  }

  if(btn){
    btn.addEventListener("click", () => {
      const cur = root.dataset.theme || "dark";
      setTheme(cur === "dark" ? "light" : "dark");
    });
  }

  // tiny sparkle effect on gold buttons (respect reduced motion)
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(!reduce){
    document.addEventListener("pointerdown", (e) => {
      const t = e.target.closest(".st-btn--gold");
      if(!t) return;
      const s = document.createElement("span");
      s.style.position="absolute";
      s.style.width="10px";
      s.style.height="10px";
      s.style.borderRadius="999px";
      s.style.pointerEvents="none";
      s.style.left = (e.clientX - 5) + "px";
      s.style.top  = (e.clientY - 5) + "px";
      s.style.background="rgba(255,222,122,.9)";
      s.style.boxShadow="0 0 18px rgba(255,222,122,.9)";
      s.style.transform="translate(-50%,-50%)";
      s.style.zIndex="9999";
      document.body.appendChild(s);
      s.animate([{transform:"translate(-50%,-50%) scale(1)",opacity:1},{transform:"translate(-50%,-50%) scale(7)",opacity:0}],{duration:520,easing:"ease-out"});
      setTimeout(()=>s.remove(), 560);
    }, {passive:true});
  }
})();
