
(() => {
  "use strict";

  // ----------------------------
  // Helpers
  // ----------------------------
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  const clamp = (n, min, max) => Math.max(min, Math.min(max, n));

  const prefersDark = () =>
    window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;

  const getTheme = () => localStorage.getItem("mse_theme");
  const setTheme = (theme) => localStorage.setItem("mse_theme", theme);

  // ----------------------------
  // Theme (dark/light)
  // Uses <html data-theme="dark|light">
  // ----------------------------
  function applyTheme(theme) {
    const root = document.documentElement;
    const resolved = theme === "light" || theme === "dark" ? theme : "dark";
    root.setAttribute("data-theme", resolved);

    // aria state
    const btn = $("#themeToggle");
    if (btn) btn.setAttribute("aria-pressed", resolved === "dark" ? "true" : "false");
  }

  function initTheme() {
    // priority: saved theme → system preference
    const saved = getTheme();
    if (saved) {
      applyTheme(saved);
      return;
    }
    applyTheme(prefersDark() ? "dark" : "light");
  }

  function toggleTheme() {
    const current = document.documentElement.getAttribute("data-theme") || "dark";
    const next = current === "dark" ? "light" : "dark";
    applyTheme(next);
    setTheme(next);
    toast(`Theme: ${next.toUpperCase()}`);
  }

  // ----------------------------
  // Toast (executive minimal)
  // ----------------------------
  let toastTimer = null;

  function toast(message) {
    // If the UI doesn’t want toast, skip silently
    // You can enable by ensuring <body data-toast="1"> or always show.
    const allow = document.body?.dataset?.toast === "1";
    if (!allow) return;

    let el = $("#mseToast");
    if (!el) {
      el = document.createElement("div");
      el.id = "mseToast";
      el.setAttribute("role", "status");
      el.setAttribute("aria-live", "polite");
      el.style.position = "fixed";
      el.style.left = "50%";
      el.style.bottom = "18px";
      el.style.transform = "translateX(-50%)";
      el.style.padding = "10px 14px";
      el.style.borderRadius = "999px";
      el.style.border = "1px solid rgba(255,255,255,.16)";
      el.style.background = "rgba(7,12,18,.72)";
      el.style.backdropFilter = "blur(10px)";
      el.style.webkitBackdropFilter = "blur(10px)";
      el.style.color = "rgba(255,255,255,.92)";
      el.style.fontSize = "13px";
      el.style.letterSpacing = ".2px";
      el.style.boxShadow = "0 22px 70px rgba(0,0,0,.55)";
      el.style.opacity = "0";
      el.style.pointerEvents = "none";
      el.style.transition = "opacity .18s ease, transform .18s ease";
      document.body.appendChild(el);
    }

    el.textContent = message;
    el.style.opacity = "1";
    el.style.transform = "translateX(-50%) translateY(-2px)";

    if (toastTimer) clearTimeout(toastTimer);
    toastTimer = setTimeout(() => {
      el.style.opacity = "0";
      el.style.transform = "translateX(-50%) translateY(6px)";
    }, 1400);
  }

  // ----------------------------
  // Smooth anchor scrolling
  // ----------------------------
  function initSmoothAnchors() {
    // any link with href="#..."
    $$('a[href^="#"]').forEach((a) => {
      a.addEventListener("click", (e) => {
        const href = a.getAttribute("href");
        if (!href || href === "#") return;

        const target = $(href);
        if (!target) return;

        e.preventDefault();

        const topbar = $(".topbar, .nav, header");
        const offset = topbar ? topbar.getBoundingClientRect().height : 0;

        const y =
          window.scrollY + target.getBoundingClientRect().top - clamp(offset, 0, 90) - 10;

        window.scrollTo({ top: y, behavior: "smooth" });

        // Keep URL hash updated without jump
        history.pushState(null, "", href);
      });
    });
  }

  // ----------------------------
  // Active link highlighting
  // - Updates .is-active on nav links based on current path
  // - Supports exact match + prefix match
  // ----------------------------
  function initActiveLinks() {
    const current = window.location.pathname;

    const navLinks = $$(".nav__link, .toplink, nav a");
    if (!navLinks.length) return;

    navLinks.forEach((link) => {
      const href = link.getAttribute("href");
      if (!href || href.startsWith("#")) return;

      try {
        // Build absolute path
        const url = new URL(href, window.location.origin);
        const path = url.pathname;

        const isExact = current === path;
        const isPrefix = current.startsWith(path) && path !== "/";

        if (isExact || isPrefix) link.classList.add("is-active");
      } catch (_) {
        // ignore invalid href
      }
    });
  }

  // ----------------------------
  // Breadcrumb helper
  // ----------------------------
  function initBreadcrumbs() {
    const el = $("#breadcrumbs");
    if (!el) return;

    // You can override via <body data-crumb="...">
    const crumb = document.body?.dataset?.crumb;

    // Otherwise infer from URL segments
    let label = crumb;
    if (!label) {
      const segs = window.location.pathname.split("/").filter(Boolean);
      // ex: /dashboards/tableau/view/ -> ["dashboards","tableau","view"]
      label = segs[segs.length - 1] || "Executive";
      label = label.replace(/[-_]/g, " ");
      label = label.charAt(0).toUpperCase() + label.slice(1);
    }

    const active = $(".crumb.is-active", el);
    if (active) active.textContent = label;
  }

  // ----------------------------
  // Flash mark (#flash) – executive flashlight vibe
  // - adds hover glow
  // - adds click pulse
  // ----------------------------
  function initFlashMark() {
    const flash = $("#flash");
    if (!flash) return;

    // Style injection (JS only)
    const css = `
      #flash{
        position: relative;
        display: inline-grid;
        place-items: center;
        transform: translateZ(0);
        border-radius: 10px;
        transition: transform .18s ease, filter .18s ease;
      }
      #flash::after{
        content:"";
        position:absolute;
        inset:-14px -18px;
        background:
          radial-gradient(circle at 40% 40%, rgba(255,255,255,.22), transparent 55%),
          radial-gradient(circle at 65% 55%, rgba(53,211,255,.20), transparent 60%);
        opacity: .0;
        filter: blur(7px);
        transition: opacity .18s ease;
        pointer-events:none;
      }
      #flash.is-on{
        filter: drop-shadow(0 0 16px rgba(53,211,255,.34)) drop-shadow(0 0 32px rgba(53,211,255,.22));
      }
      #flash.is-on::after{ opacity:.9; }
      #flash.pulse{
        animation: flashPulse 480ms ease both;
      }
      @keyframes flashPulse{
        0%{ transform: scale(1); }
        35%{ transform: scale(1.06); }
        100%{ transform: scale(1); }
      }
    `;
    injectCSS("mseFlashCSS", css);

    // Hover glow
    flash.addEventListener("mouseenter", () => flash.classList.add("is-on"));
    flash.addEventListener("mouseleave", () => flash.classList.remove("is-on"));

    // Click pulse
    flash.addEventListener("click", () => {
      flash.classList.add("is-on", "pulse");
      setTimeout(() => flash.classList.remove("pulse"), 520);
    });
  }

  // ----------------------------
  // CSS injector
  // ----------------------------
  function injectCSS(id, cssText) {
    if (document.getElementById(id)) return;
    const style = document.createElement("style");
    style.id = id;
    style.type = "text/css";
    style.appendChild(document.createTextNode(cssText));
    document.head.appendChild(style);
  }

  // ----------------------------
  // Init
  // ----------------------------
  function boot() {
    initTheme();
    initSmoothAnchors();
    initActiveLinks();
    initBreadcrumbs();
    initFlashMark();

    const themeBtn = $("#themeToggle");
    if (themeBtn) {
      themeBtn.addEventListener("click", toggleTheme);

      // Keyboard support
      themeBtn.addEventListener("keydown", (e) => {
        if (e.key === "Enter" || e.key === " ") {
          e.preventDefault();
          toggleTheme();
        }
      });
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
