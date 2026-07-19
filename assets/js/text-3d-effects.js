/**
 * 3D Text Effects Module
 * Animates text with perspective and depth for visual impact
 */
(function () {
  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion()) return;

  class Text3DEffect {
    constructor(element) {
      this.element = element;
      this.chars = [];
      this.animationPhase = 0;
      this.duration = 1;
      this.delay = 0;
      this.isAnimating = false;

      this.splitText();
    }

    splitText() {
      const text = this.element.textContent;
      this.element.innerHTML = "";

      text.split("").forEach((char, i) => {
        if (char === " ") {
          this.element.appendChild(document.createTextNode(char));
        } else {
          const span = document.createElement("span");
          span.textContent = char;
          span.style.display = "inline-block";
          span.style.willChange = "transform";
          span.style.transformStyle = "preserve-3d";
          this.chars.push({
            element: span,
            index: i,
            x: 0,
            y: 0,
            z: 0,
            rotX: 0,
            rotY: 0,
            opacity: 1,
          });
          this.element.appendChild(span);
        }
      });
    }

    animate(progress) {
      this.chars.forEach((char, i) => {
        const charDelay = i * 0.03;
        const charProgress = Math.max(0, Math.min(1, progress - charDelay));

        if (charProgress > 0 && charProgress < 1) {
          const wave = Math.sin(charProgress * Math.PI);
          const stagger = (i / this.chars.length) * 0.5;

          char.y = -10 + wave * 15;
          char.rotX = charProgress * 360;
          char.z = Math.sin((charProgress + stagger) * Math.PI * 2) * 20;
          char.opacity = charProgress;

          const transform = `
            translate3d(0, ${char.y}px, ${char.z}px)
            rotateX(${char.rotX}deg)
          `;

          char.element.style.transform = transform;
          char.element.style.opacity = char.opacity;
        }
      });
    }

    triggerAnimation() {
      if (this.isAnimating) return;
      this.isAnimating = true;

      const startTime = Date.now();
      const animationDuration = this.duration * 1000;

      const animationLoop = () => {
        const elapsed = Date.now() - startTime;
        const progress = Math.min(1, elapsed / animationDuration);

        this.animate(progress);

        if (progress < 1) {
          requestAnimationFrame(animationLoop);
        } else {
          this.isAnimating = false;
        }
      };

      animationLoop();
    }
  }

  // Initialize text effects
  const textElements = document.querySelectorAll("[data-text-3d]");

  if (textElements.length === 0) return;

  const effects = [];
  textElements.forEach((el) => {
    effects.push(new Text3DEffect(el));
  });

  // Trigger animations on scroll into view
  const observerOptions = {
    threshold: 0.5,
    rootMargin: "0px",
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        const effect = effects.find((e) => e.element === entry.target);
        if (effect) {
          effect.triggerAnimation();
          observer.unobserve(entry.target);
        }
      }
    });
  }, observerOptions);

  textElements.forEach((el) => {
    observer.observe(el);
  });

  // Cleanup
  window.addEventListener("pagehide", () => {
    observer.disconnect();
  });
})();
