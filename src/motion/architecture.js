export function initArchitecture() {
  const diagram = document.querySelector(".arch-diagram");
  if (!diagram) return;

  // Static: show the diagram immediately, no scroll-in or infinite pulse.
  const hub = diagram.querySelector(".arch-hub");
  const label = diagram.querySelector(".arch-flow-label");
  const channels = [...diagram.querySelectorAll(".arch-channel")];
  const svg = diagram.querySelector("[data-motion='arch-lines']");

  [hub, label, ...channels].filter(Boolean).forEach((el) => {
    el.style.opacity = "1";
    el.style.transform = "none";
  });

  if (svg) {
    svg.querySelectorAll("path").forEach((path) => {
      path.style.strokeDashoffset = "0";
    });
  }
}
