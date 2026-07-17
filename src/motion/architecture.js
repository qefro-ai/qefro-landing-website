import { animate, inView, stagger } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initArchitecture() {
  const diagram = document.querySelector(".arch-diagram");
  if (!diagram) return;

  const reduced = prefersReducedMotion();
  const hub = diagram.querySelector(".arch-hub");
  const label = diagram.querySelector(".arch-flow-label");
  const channels = [...diagram.querySelectorAll(".arch-channel")];
  const svg = diagram.querySelector("[data-motion='arch-lines']");

  [hub, label, ...channels].filter(Boolean).forEach((el) => {
    if (reduced) return;
    el.style.opacity = "0";
    el.style.transform = "translateY(12px)";
  });

  inView(
    diagram,
    () => {
      if (hub) {
        animate(hub, { opacity: 1, y: 0 }, motionOpts({ duration: 0.35 }));
      }
      if (label) {
        animate(label, { opacity: 1, y: 0 }, motionOpts({ duration: 0.3, delay: 0.1 }));
      }
      if (channels.length) {
        animate(
          channels,
          { opacity: 1, y: 0 },
          motionOpts({ duration: 0.35, delay: stagger(0.08, { start: 0.18 }) })
        );
      }

      if (svg && !reduced) {
        const paths = svg.querySelectorAll("path");
        paths.forEach((path, i) => {
          const len = path.getTotalLength?.() ?? 120;
          path.style.strokeDasharray = String(len);
          path.style.strokeDashoffset = String(len);
          animate(
            path,
            { strokeDashoffset: 0 },
            { duration: 0.55, delay: 0.2 + i * 0.08, ease: "easeOut" }
          );
        });
      }

      // Soft pulse between hub and channels
      if (!reduced && hub) {
        animate(
          hub,
          { boxShadow: ["0 0 0 0 rgba(8,145,178,0)", "0 0 0 12px rgba(8,145,178,0.18)", "0 0 0 0 rgba(8,145,178,0)"] },
          { duration: 2.4, repeat: Infinity, ease: "easeInOut", delay: 0.6 }
        );
      }
    },
    { amount: 0.3 }
  );
}
