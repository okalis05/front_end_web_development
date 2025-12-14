(function () {
  // Reveal animations
  const reveal = () => {
    const els = document.querySelectorAll("[data-reveal]");
    if (!("IntersectionObserver" in window)) {
      els.forEach(e => e.classList.add("is-in"));
      return;
    }
    const io = new IntersectionObserver((entries) => {
      entries.forEach((en) => {
        if (en.isIntersecting) en.target.classList.add("is-in");
      });
    }, { threshold: 0.12 });
    els.forEach(e => io.observe(e));
  };

  // Toast dismiss + auto timeout
  const initToasts = () => {
    document.querySelectorAll("[data-toast]").forEach((toast) => {
      const close = toast.querySelector("[data-toast-close]");
      if (close) close.addEventListener("click", () => toast.remove());
      setTimeout(() => { if (toast && toast.isConnected) toast.remove(); }, 5500);
    });
  };

  // Modal system (single modal + dynamic templates)
  const modal = {
    root: null,
    title: null,
    body: null,
    open(title, node) {
      if (!this.root) return;
      this.title.textContent = title;
      this.body.innerHTML = "";
      this.body.appendChild(node);
      this.root.classList.add("is-open");
      this.root.setAttribute("aria-hidden", "false");
    },
    close() {
      if (!this.root) return;
      this.root.classList.remove("is-open");
      this.root.setAttribute("aria-hidden", "true");
      this.body.innerHTML = "";
    }
  };

  const initModal = () => {
    modal.root = document.getElementById("bkModal");
    modal.title = document.getElementById("bkModalTitle");
    modal.body = document.getElementById("bkModalBody");
    if (!modal.root) return;

    modal.root.querySelectorAll("[data-modal-close]").forEach((el) => {
      el.addEventListener("click", () => modal.close());
    });
    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape") modal.close();
    });

    // Buttons that open Deposit/Withdraw templates on pages
    document.querySelectorAll("[data-modal]").forEach((btn) => {
      btn.addEventListener("click", () => {
        const key = btn.getAttribute("data-modal");
        if (key === "deposit") {
          const tpl = document.getElementById("tplDeposit");
          if (tpl) modal.open("Deposit", tpl.content.cloneNode(true));
        }
        if (key === "withdraw") {
          const tpl = document.getElementById("tplWithdraw");
          if (tpl) modal.open("Withdraw", tpl.content.cloneNode(true));
        }
      });
    });

    // Billpay “Add Payee” modal
    document.querySelectorAll("[data-modal-open='add-payee']").forEach((btn) => {
      btn.addEventListener("click", () => {
        const tpl = document.getElementById("tplAddPayee");
        if (tpl) modal.open("Add Payee", tpl.content.cloneNode(true));
      });
    });
  };

  // Count-up animation for hero stats
  const countUp = () => {
    const els = document.querySelectorAll("[data-countup]");
    const fmt = (n) => {
      try {
        return "$" + Number(n).toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
      } catch {
        return "$0.00";
      }
    };
    els.forEach((el) => {
      const target = parseFloat(el.getAttribute("data-countup")) || 0;
      const start = 0;
      const dur = 900;
      const t0 = performance.now();
      const step = (t) => {
        const p = Math.min(1, (t - t0) / dur);
        const eased = 1 - Math.pow(1 - p, 3);
        el.textContent = fmt(start + (target - start) * eased);
        if (p < 1) requestAnimationFrame(step);
      };
      requestAnimationFrame(step);
    });
  };

  // Balance chart (demo: derived from DOM balances if present)
  const initChart = () => {
    const canvas = document.getElementById("bkChartBalance");
    if (!canvas || !window.Chart) return;

    // Create a simple pseudo trend from current balances (no backend chart endpoint needed)
    const balances = Array.from(document.querySelectorAll(".bk-acct-bal"))
      .map((x) => (x.textContent || "").replace(/[$,]/g, ""))
      .map((x) => parseFloat(x) || 0);

    const total = balances.reduce((a, b) => a + b, 0);
    const base = total || 1000;

    // Fake 10 points around base for premium look
    const labels = Array.from({ length: 10 }, (_, i) => `W${i + 1}`);
    const data = labels.map((_, i) => {
      const wave = Math.sin(i / 1.7) * base * 0.03;
      const drift = (i - 5) * base * 0.004;
      return Math.max(0, base + wave + drift);
    });

    // Respect your “no custom colors” preference? You explicitly asked red/gold,
    // so we intentionally set colors here for the banking theme.
    const ctx = canvas.getContext("2d");
    new Chart(ctx, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Total",
          data,
          borderColor: "rgba(255, 222, 122, 0.9)",
          backgroundColor: "rgba(193, 18, 31, 0.20)",
          tension: 0.35,
          fill: true,
          pointRadius: 0,
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (c) => "$" + Number(c.parsed.y).toLocaleString("en-US", { maximumFractionDigits: 0 })
            }
          }
        },
        scales: {
          x: { grid: { display: false }, ticks: { color: "rgba(255,255,255,.55)" } },
          y: { grid: { color: "rgba(255,255,255,.08)" }, ticks: { color: "rgba(255,255,255,.55)" } }
        }
      }
    });
  };

  document.addEventListener("DOMContentLoaded", () => {
    reveal();
    initToasts();
    initModal();
    countUp();
    // Chart.js loads with defer too; wait a tick
    setTimeout(initChart, 120);
  });
})();
