export function initReveal() {
  // Static: reveal all sections immediately, no scroll-in animation.
  const reveals = [...document.querySelectorAll(".reveal")];
  reveals.forEach((el) => {
    el.classList.add("is-visible");
    el.style.opacity = "1";
    el.style.transform = "none";
  });
}
