// =====================
// Cinematic motion (restrained)
// - Reveal on scroll
// - Cursor glow
// - Subtle tilt on cards
// =====================

(() => {
  // Footer year
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();

  // Reveal on intersection
  const items = document.querySelectorAll(".reveal");
  const io = new IntersectionObserver(
    (entries) => {
      entries.forEach((e) => {
        if (e.isIntersecting) e.target.classList.add("is-visible");
      });
    },
    { threshold: 0.12 }
  );
  items.forEach((el) => io.observe(el));

  // Cursor glow
  const glow = document.querySelector(".cursor-glow");
  if (glow) {
    let raf = null;
    let targetX = -9999, targetY = -9999;
    let currentX = -9999, currentY = -9999;

    const animate = () => {
      const dx = (targetX - currentX) * 0.12;
      const dy = (targetY - currentY) * 0.12;
      currentX += dx;
      currentY += dy;
      glow.style.left = `${currentX}px`;
      glow.style.top = `${currentY}px`;
      raf = requestAnimationFrame(animate);
    };

    window.addEventListener("mousemove", (e) => {
      targetX = e.clientX;
      targetY = e.clientY;
      if (!raf) raf = requestAnimationFrame(animate);
    }, { passive: true });

    window.addEventListener("mouseleave", () => {
      glow.style.opacity = "0";
    });
    window.addEventListener("mouseenter", () => {
      glow.style.opacity = ".85";
    });
  }

  // Subtle tilt (desktop only)
  const tiltCards = document.querySelectorAll("[data-tilt]");
  const isCoarse = window.matchMedia("(pointer: coarse)").matches;
  if (!isCoarse) {
    tiltCards.forEach((card) => {
      let rect = null;

      const onMove = (e) => {
        if (!rect) rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width;  // 0..1
        const y = (e.clientY - rect.top) / rect.height;  // 0..1
        const rx = (y - 0.5) * -6; // rotateX
        const ry = (x - 0.5) * 8;  // rotateY

        card.style.transform = `translateY(-2px) rotateX(${rx}deg) rotateY(${ry}deg)`;
        card.style.setProperty("--mx", `${x * 100}%`);
        card.style.setProperty("--my", `${y * 100}%`);
      };

      const onLeave = () => {
        rect = null;
        card.style.transform = "";
        card.style.setProperty("--mx", `20%`);
        card.style.setProperty("--my", `20%`);
      };

      card.addEventListener("mousemove", onMove);
      card.addEventListener("mouseleave", onLeave);
    });
  }
})();
