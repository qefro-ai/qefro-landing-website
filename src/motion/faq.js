import { animate } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

/**
 * @param {HTMLElement} item
 * @param {boolean} open
 */
async function setFaqOpen(item, open) {
  const btn = item.querySelector("button");
  const panel = item.querySelector(".faq-a");
  const chevron = item.querySelector(".faq-chevron");
  if (!btn || !panel) return;

  btn.setAttribute("aria-expanded", String(open));
  item.classList.toggle("is-open", open);

  if (prefersReducedMotion()) {
    panel.style.height = open ? "auto" : "0px";
    panel.style.opacity = open ? "1" : "0";
    panel.style.overflow = "hidden";
    if (chevron) chevron.style.transform = open ? "rotate(180deg)" : "rotate(0deg)";
    return;
  }

  if (open) {
    panel.style.display = "block";
    panel.style.overflow = "hidden";
    panel.style.height = "0px";
    panel.style.opacity = "0";
    const target = panel.scrollHeight;
    await animate(
      panel,
      { height: `${target}px`, opacity: 1 },
      motionOpts({ duration: 0.32, ease: "easeOut" })
    );
    panel.style.height = "auto";
  } else {
    panel.style.overflow = "hidden";
    panel.style.height = `${panel.scrollHeight}px`;
    await animate(
      panel,
      { height: "0px", opacity: 0 },
      motionOpts({ duration: 0.28, ease: "easeIn" })
    );
  }

  if (chevron) {
    animate(
      chevron,
      { rotate: open ? 180 : 0 },
      motionOpts({ duration: 0.28, type: "spring", stiffness: 320, damping: 22 })
    );
  }
}

export function initFaq() {
  const items = [...document.querySelectorAll(".faq-item")];
  if (!items.length) return;

  items.forEach((item) => {
    const panel = item.querySelector(".faq-a");
    if (!panel) return;
    panel.style.overflow = "hidden";
    panel.style.height = "0px";
    panel.style.opacity = "0";
    panel.style.display = "block";
    panel.style.paddingBottom = "0";
  });

  items.forEach((item) => {
    const btn = item.querySelector("button");
    if (!btn) return;
    btn.addEventListener("click", async () => {
      const willOpen = !item.classList.contains("is-open");
      // Close others
      await Promise.all(
        items
          .filter((other) => other !== item && other.classList.contains("is-open"))
          .map((other) => setFaqOpen(other, false))
      );
      await setFaqOpen(item, willOpen);
    });
  });
}
