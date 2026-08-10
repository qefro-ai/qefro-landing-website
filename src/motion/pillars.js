/** Interactive Connect / Build / Automate pillar tabs on the homepage hero. */
export function initPillars() {
  const root = document.querySelector("[data-pillars]");
  if (!root) return;

  const tabs = [...root.querySelectorAll("[data-pillar]")];
  const panels = [...root.querySelectorAll("[data-pillar-panel]")];
  if (!tabs.length || !panels.length) return;

  function activate(id, moveFocus = false) {
    tabs.forEach((tab) => {
      const on = tab.getAttribute("data-pillar") === id;
      tab.classList.toggle("is-active", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
      // Roving tabindex: a tablist is one tab stop, arrows move between tabs.
      tab.tabIndex = on ? 0 : -1;
      if (on && moveFocus) tab.focus();
    });
    panels.forEach((panel) => {
      const on = panel.getAttribute("data-pillar-panel") === id;
      panel.classList.toggle("is-active", on);
      if (on) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
    });
  }

  tabs.forEach((tab, index) => {
    tab.addEventListener("click", () => {
      const id = tab.getAttribute("data-pillar");
      if (id) activate(id);
    });

    tab.addEventListener("keydown", (event) => {
      let next = -1;
      if (event.key === "ArrowRight") next = (index + 1) % tabs.length;
      else if (event.key === "ArrowLeft") next = (index - 1 + tabs.length) % tabs.length;
      else if (event.key === "Home") next = 0;
      else if (event.key === "End") next = tabs.length - 1;
      if (next < 0) return;
      event.preventDefault();
      const id = tabs[next].getAttribute("data-pillar");
      if (id) activate(id, true);
    });
  });
}
