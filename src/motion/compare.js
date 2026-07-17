import { animate, inView, stagger } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initCompare() {
  const table = document.querySelector(".compare-table");
  if (!table) return;
  if (prefersReducedMotion()) return;

  // Highlight Qefro advantage cells (3rd column checkmarks where Traditional is ✗)
  const cells = [];
  table.querySelectorAll("tbody tr").forEach((row) => {
    const tds = row.querySelectorAll("td");
    if (tds.length < 3) return;
    const trad = tds[1].textContent?.trim();
    const qefro = tds[2];
    if (trad === "✗" || trad === "Limited" || trad === "Rare") {
      qefro.classList.add("compare-advantage");
      cells.push(qefro);
    }
  });

  if (!cells.length) return;

  cells.forEach((c) => {
    c.style.opacity = "0.35";
    c.style.transform = "scale(0.92)";
  });

  inView(
    table,
    () => {
      animate(
        cells,
        { opacity: 1, scale: 1 },
        motionOpts({ duration: 0.35, delay: stagger(0.06), type: "spring", stiffness: 280, damping: 20 })
      );
    },
    { amount: 0.25 }
  );
}
