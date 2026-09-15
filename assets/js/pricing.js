/** Fixed-plan pricing: catalog amounts only. User count is a plan cap, not a price input. */

function money(amount, currency) {
  const code = (currency || "INR").toUpperCase();
  try {
    return new Intl.NumberFormat(code === "INR" ? "en-IN" : "en-US", {
      style: "currency",
      currency: code,
      maximumFractionDigits: 0,
    }).format(amount);
  } catch {
    return `${code} ${amount}`;
  }
}

function paidPlans(plans) {
  return (plans || []).filter((p) => !["trial", "free", "enterprise"].includes(String(p.slug || "").toLowerCase()));
}

function catalogAmount(plan, currency, period) {
  const inr = currency === "INR";
  if (period === "annual") {
    return inr ? Number(plan.price_annual_inr || 0) : Number(plan.price_usd_annual || 0);
  }
  return inr ? Number(plan.price_inr || 0) : Number(plan.price_usd || 0);
}

export function initPricingCalculator() {
  const root = document.querySelector("[data-pricing-root]");
  if (!root) return;

  const api = root.getAttribute("data-pricing-api") || "https://api.qefro.com";
  let catalog = [];
  let currency = "INR";
  let period = document.querySelector(".billing-toggle .is-active")?.dataset.billing || "annual";

  const render = () => {
    document.querySelectorAll(".price-card[data-plan-slug]").forEach((card) => {
      const slug = card.getAttribute("data-plan-slug");
      const p = catalog.find((x) => String(x.slug).toLowerCase() === slug);
      const amountEl = card.querySelector("[data-quote-amount]");
      if (!p || !amountEl) return;
      const base = catalogAmount(p, currency, period);
      const shown = period === "annual" && base > 0 ? Math.round(base / 12) : base;
      const span = amountEl.querySelector("span");
      amountEl.childNodes.forEach((node) => {
        if (node.nodeType === Node.TEXT_NODE) node.textContent = `${money(shown, currency)} `;
      });
      if (!span) amountEl.insertAdjacentHTML("beforeend", "<span>/month</span>");
    });
  };

  root.querySelectorAll("[data-currency]").forEach((btn) => {
    btn.addEventListener("click", () => {
      currency = btn.getAttribute("data-currency") || "INR";
      root.querySelectorAll("[data-currency]").forEach((b) => {
        const on = b === btn;
        b.classList.toggle("is-active", on);
        b.setAttribute("aria-pressed", String(on));
      });
      render();
    });
  });

  document.addEventListener("qefro:billing-period", (ev) => {
    period = ev.detail?.period || period;
    render();
  });

  fetch(`${api}/api/v1/public/pricing`)
    .then((r) => (r.ok ? r.json() : null))
    .then((data) => {
      if (data?.plans) catalog = paidPlans(data.plans).length ? data.plans : data.plans;
      render();
    })
    .catch(() => render());
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", initPricingCalculator);
} else {
  initPricingCalculator();
}
