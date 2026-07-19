/** Set count-to text immediately (no scroll animation). */
export function initStats() {
  const nodes = [...document.querySelectorAll("[data-count-to]")];
  if (!nodes.length) return;

  nodes.forEach((el) => {
    const target = Number(el.dataset.countTo);
    if (!Number.isFinite(target)) return;
    const suffix = el.dataset.countSuffix || "";
    const prefix = el.dataset.countPrefix || "";
    el.textContent = `${prefix}${target}${suffix}`;
  });
}
