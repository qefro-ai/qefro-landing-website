/**
 * Advanced Depth Parallax Module
 * Creates multi-layer parallax with depth-based motion for immersive scrolling
 */
(function () {
  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion()) return;

  class DepthLayer {
    constructor(element, depth = 1) {
      this.element = element;
      this.depth = parseFloat(element.dataset.depthLayer || depth);
      this.offsetY = 0;
      this.targetOffsetY = 0;
      this.rotZ = 0;
      this.targetRotZ = 0;
      this.scale = 1;
      this.targetScale = 1;
    }

    update(scrollY, mouseX, mouseY) {
      // Vertical parallax based on depth
      this.targetOffsetY = scrollY * this.depth * 0.5;

      // Subtle mouse-based rotation
      const rotInfluence = this.depth * 0.02;
      this.targetRotZ = (mouseX / window.innerWidth - 0.5) * rotInfluence;
      this.targetScale = 1 + (this.depth - 1) * 0.05;

      // Smooth transitions
      this.offsetY += (this.targetOffsetY - this.offsetY) * 0.15;
      this.rotZ += (this.targetRotZ - this.rotZ) * 0.12;
      this.scale += (this.targetScale - this.scale) * 0.1;

      const transform = `
        translate3d(0, ${this.offsetY}px, 0)
        scale(${this.scale})
        rotateZ(${this.rotZ}deg)
      `;

      this.element.style.transform = transform;
    }
  }

  // Initialize depth layers
  const depthLayers = [];
  const layerElements = document.querySelectorAll("[data-depth-layer]");

  if (layerElements.length === 0) return;

  layerElements.forEach((el, index) => {
    const layer = new DepthLayer(el, index + 1);
    depthLayers.push(layer);
    el.style.willChange = "transform";
  });

  let scrollY = 0;
  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;

  function onScroll() {
    scrollY = window.scrollY;
  }

  function onMouseMove(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
  }

  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("mousemove", onMouseMove, { passive: true });

  let animationId;

  function animate() {
    animationId = requestAnimationFrame(animate);

    if (!document.hidden) {
      depthLayers.forEach((layer) => {
        layer.update(scrollY, mouseX, mouseY);
      });
    }
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(animationId);
    } else {
      animate();
    }
  });

  animate();

  // Cleanup
  window.addEventListener("pagehide", () => {
    cancelAnimationFrame(animationId);
    window.removeEventListener("scroll", onScroll);
    window.removeEventListener("mousemove", onMouseMove);
  });
})();
