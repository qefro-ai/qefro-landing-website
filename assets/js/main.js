(() => {
  const THEME_KEY = "theme";
  const FALLBACK_DEMO_TOKEN = "demo-qefro-widget-token";
  const WELCOME_MESSAGE =
    "Hi! I'm the Qefro assistant. Ask me how Qefro helps businesses, pricing, security, or how to integrate.";
  const root = document.documentElement;
  const themeMeta = document.getElementById("theme-color-meta");
  const API_URL = root.dataset.apiUrl || "https://api.qefro.com";

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
    script.src = `${API_URL}/widget.js`;
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

  if (toggle && header) {
    toggle.addEventListener("click", () => {
      const open = header.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", String(open));
      toggle.innerHTML = open
        ? '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>'
        : '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';
    });
  }

  document.querySelectorAll(".faq-item button").forEach((btn) => {
    btn.addEventListener("click", () => {
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

  const reveals = document.querySelectorAll(".reveal");
  if ("IntersectionObserver" in window) {
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
  } else {
    reveals.forEach((el) => el.classList.add("is-visible"));
  }

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
})();
