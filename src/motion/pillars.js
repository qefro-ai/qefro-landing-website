/** Interactive Connect / Build / Automate pillar tabs on the homepage hero. */
export function initPillars() {
  const root = document.querySelector("[data-pillars]");
  if (!root) return;

  const tabs = [...root.querySelectorAll("[data-pillar]")];
  const panels = [...root.querySelectorAll("[data-pillar-panel]")];
  if (!tabs.length || !panels.length) return;

  function activate(id) {
    tabs.forEach((tab) => {
      const on = tab.getAttribute("data-pillar") === id;
      tab.classList.toggle("is-active", on);
      tab.setAttribute("aria-selected", on ? "true" : "false");
    });
    panels.forEach((panel) => {
      const on = panel.getAttribute("data-pillar-panel") === id;
      panel.classList.toggle("is-active", on);
      if (on) panel.removeAttribute("hidden");
      else panel.setAttribute("hidden", "");
    });
  }

  tabs.forEach((tab) => {
    tab.addEventListener("click", () => {
      const id = tab.getAttribute("data-pillar");
      if (id) activate(id);
    });
  });
}
