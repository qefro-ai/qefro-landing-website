import { hover, press } from "motion";
import { prefersReducedMotion } from "./reduced-motion.js";

export function initButtons() {
  if (prefersReducedMotion()) return;

  document.querySelectorAll(".btn").forEach((btn) => {
    hover(btn, (el) => {
      el.style.transform = "translateY(-1px) scale(1.02)";
      return () => {
        el.style.transform = "";
      };
    });
    press(btn, (el) => {
      el.style.transform = "translateY(0) scale(0.98)";
      return () => {
        el.style.transform = "translateY(-1px) scale(1.02)";
      };
    });
  });
}
