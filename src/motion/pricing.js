import { animate, hover, press } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initPricingInteractions() {
  if (prefersReducedMotion()) return;

  document.querySelectorAll(".price-card").forEach((card) => {
    hover(card, (el) => {
      const cta = el.querySelector(".btn");
      animate(
        el,
        { scale: 1.02, y: -2 },
        motionOpts({ type: "spring", stiffness: 380, damping: 24, duration: 0.28 })
      );
      if (cta) {
        animate(cta, { filter: "brightness(1.08)" }, motionOpts({ duration: 0.2 }));
      }
      return () => {
        animate(el, { scale: 1, y: 0 }, motionOpts({ duration: 0.25, ease: "easeOut" }));
        if (cta) animate(cta, { filter: "brightness(1)" }, motionOpts({ duration: 0.2 }));
      };
    });

    press(card, (el) => {
      animate(el, { scale: 0.99, y: 0 }, motionOpts({ duration: 0.12 }));
      return () => {
        animate(el, { scale: 1.02, y: -2 }, motionOpts({ duration: 0.2 }));
      };
    });
  });
}
