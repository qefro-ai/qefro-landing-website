function setFaqOpen(item, open) {
  const btn = item.querySelector("button");
  const panel = item.querySelector(".faq-a");
  if (!btn || !panel) return;

  btn.setAttribute("aria-expanded", String(open));
  item.classList.toggle("is-open", open);

  panel.style.height = open ? "auto" : "0px";
  panel.style.opacity = open ? "1" : "0";
  panel.style.overflow = "hidden";
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
  });

  items.forEach((item) => {
    const btn = item.querySelector("button");
    if (!btn) return;
    btn.addEventListener("click", () => {
      const willOpen = !item.classList.contains("is-open");
      items.forEach((other) => {
        if (other !== item && other.classList.contains("is-open")) {
          setFaqOpen(other, false);
        }
      });
      setFaqOpen(item, willOpen);
    });
  });
}
