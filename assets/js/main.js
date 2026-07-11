(() => {
  const THEME_KEY = "theme";
  const FALLBACK_DEMO_TOKEN = "demo-qefro-widget-token";
  const WELCOME_MESSAGE =
    "Hi! I'm the Qefro assistant. Ask me how Qefro helps businesses, pricing, security, or how to integrate.";
  const root = document.documentElement;
  const themeMeta = document.getElementById("theme-color-meta");
  const API_URL = root.dataset.apiUrl || "https://api.qefro.com";
  let widgetTimer = 0;

  const removeWidget = () => {
    document.getElementById("qefro-widget-script")?.remove();
    document.getElementById("ai-widget-container")?.remove();
  };

  const fetchDemoToken = async () => {
    try {
      const res = await fetch(`${API_URL}/graphql`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: "{ demoWidgetToken { token } }" }),
      });
      const json = await res.json();
      const token = json?.data?.demoWidgetToken?.token;
      if (typeof token === "string" && token.length > 0) return token;
    } catch (error) {
      console.warn("[Qefro] demoWidgetToken fetch failed, using fallback", error);
    }
    return FALLBACK_DEMO_TOKEN;
  };

  const loadDemoWidget = async (theme) => {
    removeWidget();
    const token = await fetchDemoToken();
    const script = document.createElement("script");
    script.id = "qefro-widget-script";
    script.src = `${API_URL}/widget.js`;
    script.async = true;
    script.dataset.token = token;
    script.dataset.endpoint = API_URL;
    script.dataset.theme = theme === "dark" ? "dark" : "light";
    script.dataset.position = "bottom-right";
    script.dataset.primaryColor = "#6366f1";
    script.dataset.welcomeMessage = WELCOME_MESSAGE;
    document.body.appendChild(script);
  };

  const scheduleWidgetLoad = (theme) => {
    clearTimeout(widgetTimer);
    widgetTimer = window.setTimeout(() => {
      loadDemoWidget(theme);
    }, 500);
  };

  const applyTheme = (theme) => {
    const isDark = theme === "dark";
    if (isDark) {
      root.setAttribute("data-theme", "dark");
    } else {
      root.removeAttribute("data-theme");
    }
    if (themeMeta) {
      themeMeta.setAttribute("content", isDark ? "#080a12" : "#f8fafc");
    }
    document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
      btn.setAttribute("aria-label", isDark ? "Switch to light mode" : "Switch to dark mode");
    });
    localStorage.setItem(THEME_KEY, theme);
    scheduleWidgetLoad(theme);
  };

  const getTheme = () => (root.getAttribute("data-theme") === "dark" ? "dark" : "light");

  document.querySelectorAll("[data-theme-toggle]").forEach((btn) => {
    btn.addEventListener("click", () => {
      applyTheme(getTheme() === "dark" ? "light" : "dark");
    });
  });

  applyTheme(getTheme());

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

  const year = document.querySelector("[data-year]");
  if (year) year.textContent = String(new Date().getFullYear());
})();
