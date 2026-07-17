import { prefersReducedMotion } from "./reduced-motion.js";

export function initNav() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  let ticking = false;
  const apply = () => {
    header.classList.toggle("is-scrolled", window.scrollY > 8);
    ticking = false;
  };

  apply();

  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(apply);
    },
    { passive: true }
  );

  // Prefer reduced motion still gets the scrolled state — just no animation on CSS side
  if (prefersReducedMotion()) {
    header.style.transition = "none";
  }
}
