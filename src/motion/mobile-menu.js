export function initMobileMenu() {
  const header = document.querySelector(".site-header");
  const toggle = document.querySelector(".nav-toggle");
  const panel = document.querySelector(".mobile-panel");
  if (!header || !toggle || !panel) return;

  const iconOpen =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 6L6 18M6 6l12 12"/></svg>';
  const iconClosed =
    '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M4 7h16M4 12h16M4 17h16"/></svg>';

  let open = false;

  const setOpen = (next) => {
    open = next;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    toggle.innerHTML = open ? iconOpen : iconClosed;

    if (open) {
      header.classList.add("is-open");
    } else {
      header.classList.remove("is-open");
    }
  };

  toggle.addEventListener("click", () => {
    setOpen(!open);
  });
}
