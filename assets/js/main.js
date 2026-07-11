(() => {
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

  const demo = document.querySelector("[data-chat-demo]");
  if (demo) {
    const body = demo.querySelector("[data-chat-body]");
    demo.querySelectorAll(".chat-suggestions button").forEach((btn) => {
      btn.addEventListener("click", () => {
        demo.querySelectorAll(".chat-suggestions button").forEach((b) => b.classList.remove("is-active"));
        btn.classList.add("is-active");
        const q = btn.getAttribute("data-q") || "";
        const a = btn.getAttribute("data-a") || "";
        body.innerHTML = `
          <div class="bubble bubble-ai">Hi! I'm connected to Qefro's knowledge base. What can I help you with?</div>
          <div class="bubble bubble-user"></div>
          <div class="bubble bubble-ai"></div>
        `;
        const user = body.querySelector(".bubble-user");
        const ai = body.querySelectorAll(".bubble-ai")[1];
        user.textContent = q;
        ai.textContent = "";
        let i = 0;
        const tick = () => {
          if (i <= a.length) {
            ai.textContent = a.slice(0, i);
            i += 2;
            setTimeout(tick, 12);
          }
        };
        tick();
      });
    });
  }
})();
