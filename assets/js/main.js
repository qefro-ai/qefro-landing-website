(() => {
  const THEME_KEY = "theme";
  const FALLBACK_DEMO_TOKEN = "demo-qefro-widget-token";
  const WELCOME_MESSAGE =
    "Hi! I'm the Qefro assistant. Ask about the AI Workspace Platform, workspaces, Business Tools, pricing, or security.";
  const root = document.documentElement;
  const themeMeta = document.getElementById("theme-color-meta");
  const API_URL = root.dataset.apiUrl || "https://api.qefro.com";
  const WIDGET_CDN_URL = root.dataset.widgetCdn || "https://cdn.qefro.com/widget.js";

  const removeWidget = () => {
    document.getElementById("qefro-widget-script")?.remove();
    document.getElementById("ai-widget-container")?.remove();
  };

  const applyWidgetTheme = (theme) => {
    const container = document.getElementById("ai-widget-container");
    if (!container) return false;
    container.classList.toggle("dark", theme === "dark");
    container.classList.toggle("light", theme !== "dark");
    const script = document.getElementById("qefro-widget-script");
    if (script) script.dataset.theme = theme === "dark" ? "dark" : "light";
    return true;
  };

  const mountWidget = (theme, token = FALLBACK_DEMO_TOKEN) => {
    if (document.getElementById("ai-widget-container") && applyWidgetTheme(theme)) {
      return;
    }
    removeWidget();
    const script = document.createElement("script");
    script.id = "qefro-widget-script";
    script.src = WIDGET_CDN_URL;
    script.dataset.token = token;
    script.dataset.endpoint = API_URL;
    script.dataset.theme = theme === "dark" ? "dark" : "light";
    script.dataset.position = "bottom-right";
    script.dataset.primaryColor = "#7c3aed";
    script.dataset.welcomeMessage = WELCOME_MESSAGE;
    document.body.appendChild(script);
  };

  const refreshWidget = async (theme) => {
    if (document.getElementById("ai-widget-container") && applyWidgetTheme(theme)) {
      return;
    }
    let token = FALLBACK_DEMO_TOKEN;
    try {
      const res = await fetch(`${API_URL}/graphql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: "{ demoWidgetToken { token } }" }),
      });
      const json = await res.json();
      const fetched = json?.data?.demoWidgetToken?.token;
      if (typeof fetched === "string" && fetched.length > 0) token = fetched;
    } catch (error) {
      console.warn("[Qefro] demoWidgetToken fetch failed, using fallback", error);
    }
    mountWidget(theme, token);
  };

  const applyTheme = (theme, reloadWidget = true) => {
    const isDark = theme === "dark";
    if (isDark) {
      root.setAttribute("data-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
    }
    if (themeMeta) {
      themeMeta.setAttribute("content", isDark ? "#080a12" : "#ffffff");
    }
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    });
    localStorage.setItem(THEME_KEY, theme);
    if (reloadWidget) refreshWidget(theme);
  };

  const getTheme = () => (root.getAttribute("data-theme") === "dark" ? "dark" : "light");

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      applyTheme(getTheme() === "dark" ? "light" : "dark");
    });
  });

  const syncTheme = () => {
    const saved = localStorage.getItem(THEME_KEY);
    if (saved === "dark") {
      applyTheme("dark", false);
    }
    const widgetTheme = getTheme();
    const existing = document.getElementById("qefro-widget-script");
    const currentWidgetTheme = existing?.dataset.theme || "light";
    if (!existing || currentWidgetTheme !== widgetTheme) {
      refreshWidget(widgetTheme);
    }
  };

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", syncTheme);
  } else {
    syncTheme();
  }

  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const motionOwned = () => document.documentElement.dataset.motion === "1";

  // Mobile menu, FAQ, and reveals are owned by qefro-motion.js when loaded.
  // Fallback if the Motion bundle fails to load within a short window.
  const bindFallbackUi = () => {
    if (motionOwned()) return;

    if (toggle && header && !toggle.dataset.fallbackBound) {
      toggle.dataset.fallbackBound = "1";
      toggle.addEventListener("click", () => {
        const open = header.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(open));
        toggle.innerHTML = open
          ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>'
          : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
      });
    }

    if (!document.body.dataset.faqFallback) {
      document.body.dataset.faqFallback = "1";
      document.querySelectorAll(".faq-item button").forEach((btn) => {
        btn.addEventListener("click", () => {
          if (motionOwned()) return;
          const item = btn.closest(".faq-item");
          const open = !item.classList.contains("is-open");
          item.parentElement.querySelectorAll(".faq-item.is-open").forEach((el) => {
            if (el !== item) {
              el.classList.remove("is-open");
              el.querySelector("button")?.setAttribute("aria-expanded", "false");
            }
          });
          item.classList.toggle("is-open", open);
          btn.setAttribute("aria-expanded", String(open));
        });
      });
    }

    const reveals = document.querySelectorAll(".reveal");
    const prefersReducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    if (prefersReducedMotion || !("IntersectionObserver" in window)) {
      reveals.forEach((el) => el.classList.add("is-visible"));
    } else if (!document.body.dataset.revealFallback) {
      document.body.dataset.revealFallback = "1";
      const io = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (entry.isIntersecting) {
              entry.target.classList.add("is-visible");
              io.unobserve(entry.target);
            }
          });
        },
        { threshold: 0.12 }
      );
      reveals.forEach((el) => io.observe(el));
    }
  };

  document.addEventListener("qefro:motion-ready", () => {
    /* Motion owns menu / FAQ / reveal */
  });
  window.setTimeout(bindFallbackUi, 1200);

  document.querySelectorAll("[data-uc-tabs]").forEach((root) => {
    const tabs = root.querySelectorAll("[data-uc-tab]");
    const panels = root.querySelectorAll("[data-uc-panel]");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const id = tab.dataset.ucTab;
        tabs.forEach((t) => {
          const active = t === tab;
          t.classList.toggle("is-active", active);
          t.setAttribute("aria-selected", String(active));
        });
        panels.forEach((panel) => {
          const show = panel.dataset.ucPanel === id;
          panel.classList.toggle("is-active", show);
          if (show) panel.removeAttribute("hidden");
          else panel.setAttribute("hidden", "");
        });
      });
    });
  });

  const year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());

  // Pricing: monthly / yearly toggle (default yearly)
  const billingToggle = document.querySelector(".billing-toggle");
  if (billingToggle) {
    const setPeriod = (period) => {
      billingToggle.querySelectorAll("[data-billing]").forEach((btn) => {
        const active = btn.dataset.billing === period;
        btn.classList.toggle("is-active", active);
        btn.setAttribute("aria-pressed", String(active));
      });
      document.querySelectorAll(".price-amount[data-price-annual]").forEach((el) => {
        const annual = el.dataset.priceAnnual;
        const monthly = el.dataset.priceMonthly;
        const price = period === "annual" ? annual : monthly;
        const span = el.querySelector("span");
        el.childNodes.forEach((node) => {
          if (node.nodeType === Node.TEXT_NODE) node.textContent = `${price} `;
        });
        if (!span) el.insertAdjacentHTML("beforeend", "<span>/month</span>");
        const billed = el.parentElement?.querySelector(".price-billed");
        if (billed) {
          billed.textContent =
            period === "annual"
              ? `billed annually · or ${monthly}/mo monthly`
              : `billed monthly · or ${annual}/mo annually`;
        }
      });
    };
    billingToggle.querySelectorAll("[data-billing]").forEach((btn) => {
      btn.addEventListener("click", () => setPeriod(btn.dataset.billing));
    });
    setPeriod("annual");
  }

  const trackClarity = (name) => {
    if (!name) return;
    try {
      if (typeof window.clarity === "function") window.clarity("event", name);
    } catch (_) {
      /* ignore analytics failures */
    }
  };

  document.querySelectorAll("[data-clarity-event]").forEach((el) => {
    el.addEventListener("click", () => trackClarity(el.dataset.clarityEvent));
  });

  document.querySelectorAll("[data-price-cta]").forEach((card) => {
    card.addEventListener("click", (event) => {
      if (event.target.closest("a, button")) return;
      const cta = card.querySelector("a.btn");
      if (!cta) return;
      trackClarity(cta.dataset.clarityEvent || "cta_price_card");
      cta.click();
    });
  });

  const openLiveDemo = () => {
    trackClarity("open_live_demo");
    const demo = document.getElementById("demo");
    demo?.scrollIntoView({ behavior: "auto", block: "start" });
    window.setTimeout(() => {
      const launcher =
        document.querySelector("#ai-widget-container button") ||
        document.querySelector("button[aria-label*='chat' i], button[aria-label*='Chat' i]");
      launcher?.click();
    }, 0);
  };

  document.querySelectorAll("[data-open-demo]").forEach((el) => {
    el.addEventListener("click", (event) => {
      event.preventDefault();
      openLiveDemo();
    });
  });
})();
