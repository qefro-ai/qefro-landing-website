import { animate, inView } from "motion";
import { prefersReducedMotion } from "./reduced-motion.js";

/** Count-up for elements with data-count-to="123" */
export function initStats() {
  const nodes = [...document.querySelectorAll("[data-count-to]")];
  if (!nodes.length) return;

  nodes.forEach((el) => {
    const target = Number(el.dataset.countTo);
    if (!Number.isFinite(target)) return;
    const suffix = el.dataset.countSuffix || "";
    const prefix = el.dataset.countPrefix || "";

    inView(
      el,
      () => {
        if (prefersReducedMotion()) {
          el.textContent = `${prefix}${target}${suffix}`;
          return;
        }
        const from = { v: 0 };
        animate(from, { v: target }, {
          duration: 0.9,
          ease: "easeOut",
          onUpdate: () => {
            el.textContent = `${prefix}${Math.round(from.v)}${suffix}`;
          },
        });
      },
      { amount: 0.5 }
    );
  });
}
