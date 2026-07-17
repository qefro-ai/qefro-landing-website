import { animate, inView } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

export function initHero() {
  const hero = document.querySelector(".hero");
  if (!hero) return;

  const reduced = prefersReducedMotion();
  const parts = [
    hero.querySelector("[data-motion='hero-badge']"),
    hero.querySelector("[data-motion='hero-title']"),
    hero.querySelector("[data-motion='hero-sub']"),
    hero.querySelector("[data-motion='hero-actions']"),
    hero.querySelector("[data-motion='hero-checks']"),
    hero.querySelector("[data-motion='hero-diff']"),
    hero.querySelector("[data-motion='hero-cue']"),
  ].filter(Boolean);

  parts.forEach((el) => {
    el.style.opacity = reduced ? "1" : "0";
    if (!reduced) el.style.transform = "translateY(16px)";
  });

  const run = () => {
    parts.forEach((el, i) => {
      animate(
        el,
        { opacity: 1, y: 0 },
        motionOpts({ duration: 0.35, delay: reduced ? 0 : i * 0.07, ease: "easeOut" })
      );
    });
  };

  if (reduced) {
    run();
  } else {
    // Hero is above the fold — animate on load
    requestAnimationFrame(run);
  }

  // Product mock / dashboard float (homepage may use product-mock later; hero has no mock —
  // float the first product mock in platform if present, or demo chat mock as visual anchor)
  const floatTarget =
    document.querySelector("[data-motion='hero-float']") ||
    document.querySelector(".demo-chat .chat-mock");

  if (floatTarget && !reduced) {
    const startFloat = () => {
      animate(
        floatTarget,
        { y: [0, -4, 0] },
        { duration: 4, repeat: Infinity, ease: "easeInOut" }
      );
    };
    inView(
      floatTarget,
      () => {
        startFloat();
        return () => {};
      },
      { amount: 0.2 }
    );
  }

  // Slow ambient gradient shift on hero glow / ambient blobs
  if (!reduced) {
    const blobs = document.querySelectorAll(".ambient-blob");
    blobs.forEach((blob, i) => {
      animate(
        blob,
        { opacity: [0.45, 0.7, 0.45], scale: [1, 1.06, 1] },
        {
          duration: 12 + i * 2,
          repeat: Infinity,
          ease: "easeInOut",
          delay: i * 1.5,
        }
      );
    });
  }
}
