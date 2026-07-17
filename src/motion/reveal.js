import { animate, inView, stagger } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

const GRID_SELECTORS = [
  ".exp-grid",
  ".outcome-grid",
  ".workspace-grid",
  ".channel-grid",
  ".trust-grid",
  ".scenario-grid",
  ".facts-grid",
  ".price-grid",
  ".cap-grid",
];

export function initReveal() {
  const reduced = prefersReducedMotion();
  const reveals = [...document.querySelectorAll(".reveal")];

  if (reduced) {
    reveals.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  reveals.forEach((el) => {
    // Motion owns visibility — keep CSS initial state until inView
    inView(
      el,
      () => {
        el.classList.add("is-visible");
        animate(el, { opacity: 1, y: 0, scale: 1 }, motionOpts({ duration: 0.38, ease: "easeOut" }));

        const isGrid = GRID_SELECTORS.some((sel) => el.matches(sel));
        if (isGrid) {
          const kids = [...el.children];
          kids.forEach((k) => {
            k.style.opacity = "0";
            k.style.transform = "translateY(14px)";
            k.style.filter = "blur(4px)";
          });
          animate(
            kids,
            { opacity: 1, y: 0, filter: "blur(0px)" },
            motionOpts({ duration: 0.36, delay: stagger(0.08), ease: "easeOut" })
          );
        }
      },
      { amount: 0.15 }
    );
  });
}
