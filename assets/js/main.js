(() => {
  const THEME_KEY = "theme";
  const TOKEN_SESSION_KEY = "qefro-demo-widget-token";
  const FALLBACK_DEMO_TOKEN = "demo-qefro-widget-token";
  const WELCOME_MESSAGE =
    "Hi! I'm the Qefro assistant. Ask about the AI Workspace Platform, workspaces, Business Tools, pricing, or security.";
  const root = document.documentElement;
  const themeMeta = document.getElementById("theme-color-meta");
  const API_URL = root.dataset.apiUrl || "https://api.qefro.com";
  const WIDGET_CDN_URL = root.dataset.widgetCdn || "https://cdn.qefro.com/widget.js";

  // localStorage/sessionStorage throw in some privacy modes — never let that break the page.
  const store = {
    get(area, key) {
      try {
        return window[area].getItem(key);
      } catch (_) {
        return null;
      }
    },
    set(area, key, value) {
      try {
        window[area].setItem(key, value);
      } catch (_) {
        /* storage unavailable */
      }
    },
  };

  const removeWidget = () => {
    const scriptEl = document.getElementById("qefro-widget-script");
    const containerEl = document.getElementById("ai-widget-container");
    if (scriptEl) scriptEl.remove();
    if (containerEl) containerEl.remove();
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
    // Cached per tab so page navigation doesn't re-hit the API for a token.
    let token = store.get("sessionStorage", TOKEN_SESSION_KEY) || FALLBACK_DEMO_TOKEN;
    if (token === FALLBACK_DEMO_TOKEN) {
      try {
        const res = await fetch(`${API_URL}/graphql`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ query: "{ demoWidgetToken { token } }" }),
        });
        const json = await res.json();
        const fetched =
          json &&
          json.data &&
          json.data.demoWidgetToken &&
          json.data.demoWidgetToken.token;
        if (typeof fetched === "string" && fetched.length > 0) {
          token = fetched;
          store.set("sessionStorage", TOKEN_SESSION_KEY, fetched);
        }
      } catch (error) {
        console.warn("[Qefro] demoWidgetToken fetch failed, using fallback", error);
      }
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
      btn.setAttribute("aria-pressed", String(isDark));
    });
    store.set("localStorage", THEME_KEY, theme);
    if (reloadWidget) refreshWidget(theme);
  };

  const getTheme = () => (root.getAttribute("data-theme") === "dark" ? "dark" : "light");

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.setAttribute("aria-pressed", String(getTheme() === "dark"));
    btn.addEventListener("click", () => {
      applyTheme(getTheme() === "dark" ? "light" : "dark");
    });
  });

  const syncTheme = () => {
    const saved = store.get("localStorage", THEME_KEY);
    if (saved === "dark") {
      applyTheme("dark", false);
    }
    const widgetTheme = getTheme();
    const existing = document.getElementById("qefro-widget-script");
    const currentWidgetTheme =
      (existing && existing.dataset && existing.dataset.theme) || "light";
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
  // The fallback binds only if the Motion bundle failed by DOMContentLoaded
  // (module scripts run before DOMContentLoaded, so data-motion is reliable then).
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
              const openBtn = el.querySelector("button");
              if (openBtn) openBtn.setAttribute("aria-expanded", "false");
            }
          });
          item.classList.toggle("is-open", open);
          btn.setAttribute("aria-expanded", String(open));
        });
      });
    }

    document.querySelectorAll(".reveal").forEach((el) => {
      el.classList.add("is-visible");
      el.style.opacity = "1";
      el.style.transform = "none";
    });
  };

  // Deferred scripts run at readyState "interactive", *before* DOMContentLoaded —
  // and the Motion module runs after this file in that same window. Waiting for
  // DOMContentLoaded guarantees data-motion reflects whether Motion took ownership.
  if (document.readyState === "complete") {
    bindFallbackUi();
  } else {
    document.addEventListener("DOMContentLoaded", bindFallbackUi);
  }

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
        const billed =
          el.parentElement && el.parentElement.querySelector(".price-billed");
        if (billed) {
          billed.textContent =
            period === "annual"
              ? `billed annually · or ${monthly}/mo monthly`
              : `billed monthly · or ${annual}/mo annually`;
        }
      });
    };
    billingToggle.querySelectorAll("[data-billing]").forEach((btn) => {
      btn.addEventListener("click", () => {
        setPeriod(btn.dataset.billing);
        document.dispatchEvent(new CustomEvent("qefro:billing-period", { detail: { period: btn.dataset.billing } }));
      });
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
    if (demo) demo.scrollIntoView({ behavior: "auto", block: "start" });
    window.setTimeout(() => {
      const launcher =
        document.querySelector("#ai-widget-container button") ||
        document.querySelector("button[aria-label*='chat' i], button[aria-label*='Chat' i]");
      if (launcher) launcher.click();
    }, 0);
  };

  document.querySelectorAll("[data-open-demo]").forEach((el) => {
    el.addEventListener("click", (event) => {
      event.preventDefault();
      openLiveDemo();
    });
  });

  const TRY_SCENARIOS = {
    table: {
      conversation: [
        { who: "customer", text: "Book a table for 4 tomorrow at 7 PM." },
        { who: "qefro", text: "Done. Table for 4 reserved at 7:00 PM tomorrow. Confirmation sent." },
      ],
    },
    invoice: {
      conversation: [
        { who: "customer", text: "Create an invoice for \u20B945,000 for client Acme Corp." },
        { who: "qefro", text: "Invoice #2847 created for Acme Corp \u00B7 \u20B945,000. Due in 30 days. Sent to billing@acme.com." },
      ],
    },
    property: {
      conversation: [
        { who: "customer", text: "Find 3BHK apartments in Anna Nagar under \u20B980L." },
        { who: "qefro", text: "Found 4 properties. Top match: 3BHK, Anna Nagar, \u20B972L, 1,650 sq.ft." },
      ],
    },
    sales: {
      conversation: [
        { who: "customer", text: "What were our total sales this week?" },
        { who: "qefro", text: "\u20B93,28,400 this week. Up 12% from last week. Top product: Product A." },
      ],
    },
    customer: {
      conversation: [
        { who: "customer", text: "Find customer Priya Sharma." },
        { who: "qefro", text: "Priya Sharma \u00B7 Last order: 12 days ago \u00B7 \u20B918,200 total. 2 open invoices." },
      ],
    },
  };

  const tryChips = document.querySelectorAll("[data-try-scenario]");
  const tryArea = document.getElementById("try-demo-area");
  if (tryChips.length && tryArea) {
    tryChips.forEach((chip) => {
      chip.addEventListener("click", () => {
        const key = chip.dataset.tryScenario;
        const scenario = TRY_SCENARIOS[key];
        if (!scenario) return;
        tryChips.forEach((c) => c.classList.remove("active"));
        chip.classList.add("active");
        const msgs = scenario.conversation
          .map(
            (m) =>
              `<div class="demo-msg demo-${m.who === "customer" ? "customer" : "qefro"}">` +
              `<span class="demo-avatar demo-avatar-${m.who === "customer" ? "customer" : "qefro"}">${m.who === "customer" ? "Y" : "Q"}</span>` +
              `<div class="demo-bubble demo-bubble-${m.who === "customer" ? "in" : "out"}"><p>${m.text}</p></div></div>`
          )
          .join("");
        tryArea.innerHTML = `<div class="hero-demo-convo">${msgs}</div>`;
      });
    });
  }

  // Hero interactive scenario tabs
  const heroTabs = document.querySelectorAll("[data-hero-tab]");
  const heroPanels = document.querySelectorAll("[data-scenario]");
  if (heroTabs.length && heroPanels.length) {
    heroTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const scenario = tab.dataset.heroTab;
        heroTabs.forEach((t) => {
          t.classList.remove("is-active");
          t.setAttribute("aria-selected", "false");
        });
        tab.classList.add("is-active");
        tab.setAttribute("aria-selected", "true");
        heroPanels.forEach((p) => {
          if (p.dataset.scenario === scenario) {
            p.classList.add("is-active");
            // Ensure messages are immediately visible on tab switch
            p.querySelectorAll("[data-hero-msg]").forEach((m) => {
              m.style.opacity = "1";
              m.style.transform = "none";
              m.classList.add("demo-msg-visible");
            });
          } else {
            p.classList.remove("is-active");
          }
        });
      });
    });
  }

  // Plan Finder Quiz
  window.runPlanQuiz = function() {
    const teamEl = document.getElementById('quiz-team');
    const volEl = document.getElementById('quiz-volume');
    const softEl = document.getElementById('quiz-software');
    const appEl = document.getElementById('quiz-approvals');
    const outEl = document.getElementById('quiz-recommendation');
    if (!teamEl || !volEl || !softEl || !appEl || !outEl) return;

    const team = parseInt(teamEl.value, 10);
    const volume = parseInt(volEl.value, 10);
    const software = softEl.value;
    const approvals = appEl.value;

    let plan = "Starter Plan (₹699/mo)";
    let rationale = "single-operator setup and lightweight message volume";

    if (team > 15 || volume > 10000 || software === 'custom') {
      plan = "Enterprise Plan (Custom)";
      rationale = "high volume and custom ERP integration requirements";
    } else if (team > 5 || volume > 2500) {
      plan = "Growth Plan (₹2,999/mo)";
      rationale = "your larger team size and higher monthly conversation traffic";
    } else if (team > 1 || software === 'zoho' || approvals === 'yes') {
      plan = "Pro Plan (₹1,499/mo)";
      rationale = "multi-user collaboration, Tally/Zoho connectivity, and approval workflows";
    }

    outEl.innerHTML = `<span>💡 <strong>Recommendation:</strong> Based on ${rationale}, the <strong>${plan}</strong> fits your operations best.</span> <a class="btn btn-primary" href="https://app.qefro.com/login?mode=signup" style="padding:0.45rem 1rem;font-size:0.8125rem"><span>Start Free Trial</span></a>`;
  };

  // WhatsApp QR Code Generator Tool
  window.generateWhatsAppQR = function() {
    var ccEl = document.getElementById('qr-cc');
    var phoneEl = document.getElementById('qr-phone');
    var msgEl = document.getElementById('qr-message');
    var linkTextEl = document.getElementById('qr-link-text');
    var openBtnEl = document.getElementById('qr-open-btn');
    var imgEl = document.getElementById('qr-image');
    if (!ccEl || !phoneEl || !msgEl || !linkTextEl || !openBtnEl || !imgEl) return;

    var cc = ccEl.value.replace(/[^0-9]/g, '');
    var phone = phoneEl.value.replace(/[^0-9]/g, '');
    var msg = msgEl.value;
    if (!phone) { phone = '9999999999'; }
    var fullNumber = cc + phone;
    var url = 'https://wa.me/' + fullNumber;
    if (msg.trim()) {
      url += '?text=' + encodeURIComponent(msg);
    }
    linkTextEl.innerText = url;
    openBtnEl.href = url;
    imgEl.src = 'https://api.qrserver.com/v1/create-qr-code/?size=180x180&data=' + encodeURIComponent(url);
  };

  window.copyWhatsAppLink = function() {
    var linkTextEl = document.getElementById('qr-link-text');
    if (!linkTextEl) return;
    navigator.clipboard.writeText(linkTextEl.innerText).then(function() {
      alert('WhatsApp link copied to clipboard!');
    });
  };
})();
