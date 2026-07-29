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

  const setOpen = (next, { restoreFocus = false } = {}) => {
    if (open === next) return;
    open = next;
    toggle.setAttribute("aria-expanded", String(open));
    toggle.setAttribute("aria-label", open ? "Close menu" : "Open menu");
    toggle.innerHTML = open ? iconOpen : iconClosed;
    header.classList.toggle("is-open", open);
    if (!open && restoreFocus) toggle.focus();
  };

  toggle.addEventListener("click", () => setOpen(!open));

  // ESC closes and returns focus to the toggle (disclosure pattern).
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && open) setOpen(false, { restoreFocus: true });
  });

  // Clicking anywhere outside the header closes the menu.
  document.addEventListener("click", (event) => {
    if (open && !header.contains(event.target)) setOpen(false);
  });

  // Navigating from the panel closes the menu behind the new page.
  panel.addEventListener("click", (event) => {
    if (event.target.closest("a")) setOpen(false);
  });

  // Crossing into the desktop breakpoint while open would strand the open state.
  const desktop = window.matchMedia("(min-width: 901px)");
  const onBreakpoint = (event) => {
    if (event.matches && open) setOpen(false);
  };
  if (typeof desktop.addEventListener === "function") {
    desktop.addEventListener("change", onBreakpoint);
  } else if (typeof desktop.addListener === "function") {
    desktop.addListener(onBreakpoint);
  }
}
