import { animate, stagger } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initMobileMenu() {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector(".mobile-panel");
  if (!header || !toggle || !panel) return;

  const iconOpen =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  const iconClosed =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';

  let open = false;

  const setOpen = async (next) => {
    open = next;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    toggle.innerHTML = open ? iconOpen : iconClosed;

    const links = [...panel.querySelectorAll("a, button")];

    if (open) {
      header.classList.add("is-open");
      if (prefersReducedMotion()) return;
      animate(panel, { opacity: [0, 1], y: [-8, 0] }, motionOpts({ duration: 0.28 }));
      links.forEach((l) => {
        l.style.opacity = "0";
        l.style.transform = "translateX(-10px)";
      });
      animate(
        links,
        { opacity: 1, x: 0 },
        motionOpts({ duration: 0.28, delay: stagger(0.04), ease: "easeOut" })
      );
      return;
    }

    if (!prefersReducedMotion()) {
      await animate(panel, { opacity: 0, y: -6 }, motionOpts({ duration: 0.2 }));
    }
    header.classList.remove("is-open");
    panel.style.opacity = "";
    panel.style.transform = "";
  };

  toggle.addEventListener("click", () => {
    setOpen(!open);
  });
}
