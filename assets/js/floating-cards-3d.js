/**
 * Floating 3D Cards Module
 * Creates animated floating cards with depth parallax and tilt effects
 * Works alongside hero-3d.js for a cohesive 3D experience
 */
(function () {
  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion()) return;

  class FloatingCard {
    constructor(element) {
      this.element = element;
      this.x = 0;
      this.y = 0;
      this.z = 0;
      this.rotX = 0;
      this.rotY = 0;
      this.targetX = 0;
      this.targetY = 0;
      this.targetRotX = 0;
      this.targetRotY = 0;
      this.offsetX = 0;
      this.offsetY = 0;
      this.floatSpeed = Math.random() * 0.5 + 0.3;
      this.floatAmount = Math.random() * 2 + 1;
      this.floatPhase = Math.random() * Math.PI * 2;
    }

    updateTargetFromMouse(mouseX, mouseY) {
      const rect = this.element.getBoundingClientRect();
      const centerX = rect.left + rect.width / 2;
      const centerY = rect.top + rect.height / 2;

      const dx = mouseX - centerX;
      const dy = mouseY - centerY;

      this.targetX = (dx / window.innerWidth) * 8;
      this.targetY = (dy / window.innerHeight) * 8;

      this.targetRotX = (dy / window.innerHeight) * 15;
      this.targetRotY = (dx / window.innerWidth) * 15;
    }

    update(time) {
      // Floating animation
      const floatOffset = Math.sin(time * this.floatSpeed + this.floatPhase) * this.floatAmount;

      // Smooth interpolation
      this.x += (this.targetX - this.x) * 0.08;
      this.y += (this.targetY - this.y) * 0.08;
      this.rotX += (this.targetRotX - this.rotX) * 0.06;
      this.rotY += (this.targetRotY - this.rotY) * 0.06;

      const transform = `
        perspective(1200px)
        translate3d(${this.x}px, ${this.y + floatOffset}px, ${this.z}px)
        rotateX(${this.rotX}deg)
        rotateY(${this.rotY}deg)
      `;

      this.element.style.transform = transform;
    }

    reset() {
      this.targetX = 0;
      this.targetY = 0;
      this.targetRotX = 0;
      this.targetRotY = 0;
    }
  }

  // Initialize floating cards
  const cards = [];
  const cardElements = document.querySelectorAll("[data-floating-card]");

  if (cardElements.length === 0) return;

  cardElements.forEach((el) => {
    const card = new FloatingCard(el);
    cards.push(card);
    el.style.willChange = "transform";
  });

  let mouseX = window.innerWidth / 2;
  let mouseY = window.innerHeight / 2;
  let isMouseInViewport = false;

  function onMouseMove(e) {
    mouseX = e.clientX;
    mouseY = e.clientY;
    isMouseInViewport = true;

    cards.forEach((card) => {
      card.updateTargetFromMouse(mouseX, mouseY);
    });
  }

  function onMouseLeave() {
    isMouseInViewport = false;
    cards.forEach((card) => card.reset());
  }

  window.addEventListener("mousemove", onMouseMove, { passive: true });
  document.addEventListener("mouseleave", onMouseLeave, { passive: true });

  let animationId;
  let startTime = Date.now();

  function animate() {
    animationId = requestAnimationFrame(animate);
    const time = (Date.now() - startTime) * 0.001;

    cards.forEach((card) => card.update(time));
  }

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      cancelAnimationFrame(animationId);
    } else {
      startTime = Date.now();
      animate();
    }
  });

  animate();

  // Cleanup
  window.addEventListener("pagehide", () => {
    cancelAnimationFrame(animationId);
    window.removeEventListener("mousemove", onMouseMove);
    document.removeEventListener("mouseleave", onMouseLeave);
  });
})();
