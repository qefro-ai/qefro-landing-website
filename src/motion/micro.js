import { animate, hover, press } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initMicro() {
  const reduced = prefersReducedMotion();

  // Billing toggle press spring
  document.querySelectorAll(".billing-toggle [data-billing]").forEach((btn) => {
    if (reduced) return;
    press(btn, (el) => {
      animate(el, { scale: 0.96 }, motionOpts({ type: "spring", stiffness: 400, damping: 22, duration: 0.2 }));
      return () =>
        animate(el, { scale: 1 }, motionOpts({ type: "spring", stiffness: 400, damping: 20, duration: 0.25 }));
    });
  });

  // Demo chips
  document.querySelectorAll(".demo-chip").forEach((chip) => {
    if (reduced) return;
    hover(chip, (el) => {
      el.style.transform = "scale(1.04)";
      return () => {
        el.style.transform = "";
      };
    });
    press(chip, (el) => {
      el.style.transform = "scale(0.97)";
      return () => {
        el.style.transform = "scale(1.04)";
      };
    });
  });

  // Use-case tabs — fade panel content
  document.querySelectorAll("[data-uc-tabs]").forEach((root) => {
    const tabs = root.querySelectorAll("[data-uc-tab]");
    const panels = root.querySelectorAll("[data-uc-panel]");
    tabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        const id = tab.dataset.ucTab;
        const panel = [...panels].find((p) => p.dataset.ucPanel === id);
        if (!panel || reduced) return;
        panel.style.opacity = "0";
        requestAnimationFrame(() => {
          animate(panel, { opacity: 1 }, motionOpts({ duration: 0.25 }));
        });
      });
    });
  });
}
