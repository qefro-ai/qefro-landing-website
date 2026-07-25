export function initNav() {
  const header = document.querySelector(".site-header");
  if (!header) return;

  // Hysteresis avoids class thrash when scrollY oscillates near the threshold
  // (sticky header height changes used to feedback into scrollY and flicker).
  const ENTER = 24;
  const EXIT = 8;
  let scrolled = false;
  let ticking = false;

  const apply = () => {
    const y = window.scrollY || 0;
    const next = scrolled ? y > EXIT : y > ENTER;
    if (next !== scrolled) {
      scrolled = next;
      header.classList.toggle("is-scrolled", scrolled);
    }
    ticking = false;
  };

  apply();

  window.addEventListener(
    "scroll",
    () => {
      if (ticking) return;
      ticking = true;
      requestAnimationFrame(apply);
    },
    { passive: true }
  );
}
