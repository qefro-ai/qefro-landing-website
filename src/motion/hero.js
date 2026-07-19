export function initHero() {
  const hero = document.querySelector(".hero");
  if (!hero) return;

  // Static: show hero content immediately, no intro animation.
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
    el.style.opacity = "1";
    el.style.transform = "none";
  });
}
