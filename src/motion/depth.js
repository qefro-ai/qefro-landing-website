import { prefersReducedMotion } from "./reduced-motion.js";

/**
 * Mouse-reactive 3D tilt for cards and product mockups.
 * Adds subtle rotateX/Y based on cursor position relative to the element.
 */
export function initDepth() {
  if (prefersReducedMotion()) return;
  if (window.matchMedia("(pointer: coarse)").matches) return;

  const targets = document.querySelectorAll(".tilt-3d");
  if (!targets.length) return;

  const state = new Map();

  function setTransform(el, rotateX, rotateY) {
    const current = state.get(el);
    const targetX = current ? current.x + (rotateX - current.x) * 0.12 : rotateX;
    const targetY = current ? current.y + (rotateY - current.y) * 0.12 : rotateY;
    state.set(el, { x: targetX, y: targetY });

    const intensity = parseFloat(el.dataset.tiltIntensity) || 6;
    el.style.transform = `perspective(1000px) rotateX(${-targetX * intensity}deg) rotateY(${targetY * intensity}deg) translateZ(12px)`;

    if (Math.abs(targetX) > 0.001 || Math.abs(targetY) > 0.001) {
      requestAnimationFrame(() => setTransform(el, rotateX, rotateY));
    } else {
      el.style.transform = "";
      state.delete(el);
    }
  }

  targets.forEach((el) => {
    let active = false;
    let pending = false;

    el.addEventListener("mouseenter", () => {
      active = true;
    });

    el.addEventListener("mousemove", (event) => {
      if (!active) return;
      const rect = el.getBoundingClientRect();
      const x = (event.clientY - rect.top) / rect.height - 0.5;
      const y = (event.clientX - rect.left) / rect.width - 0.5;
      if (!pending) {
        pending = true;
        requestAnimationFrame(() => {
          pending = false;
          setTransform(el, x, y);
        });
      }
    });

    el.addEventListener("mouseleave", () => {
      active = false;
      setTransform(el, 0, 0);
    });

    el.addEventListener("focus", () => {
      // No keyboard tilt; just ensure transform is cleared
      el.style.transform = "";
    });
  });

  // Gentle floating animation for the demo chat mockup
  const chatMock = document.querySelector(".chat-mock");
  if (chatMock) {
    chatMock.classList.add("is-floating");
  }
}
