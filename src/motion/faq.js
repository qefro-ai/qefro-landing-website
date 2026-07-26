function setFaqOpen(item, open) {
  const btn = item.querySelector("button");
  const panel = item.querySelector(".faq-a");
  if (!btn || !panel) return;

  btn.setAttribute("aria-expanded", String(open));
  item.classList.toggle("is-open", open);
  panel.style.overflow = "hidden";

  // Animate between measured pixel heights — CSS can't tween to/from "auto".
  // The transition curve lives in styles.css (html[data-motion] .faq-a).
  if (open) {
    panel.style.height = panel.scrollHeight + "px";
    panel.style.opacity = "1";
    panel.addEventListener("transitionend", function onEnd(e) {
      if (e.propertyName !== "height") return;
      panel.removeEventListener("transitionend", onEnd);
      if (item.classList.contains("is-open")) panel.style.height = "auto";
    });
  } else {
    // Pin the current height first so collapsing from "auto" still animates.
    panel.style.height = panel.scrollHeight + "px";
    panel.getBoundingClientRect();
    panel.style.height = "0px";
    panel.style.opacity = "0";
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
