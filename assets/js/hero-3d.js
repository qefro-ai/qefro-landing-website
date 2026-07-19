/**
 * Qefro homepage hero — lightweight Three.js ambient scene.
 * Loads Three.js from CDN only when needed, respects reduced motion,
 * and falls back to the CSS hero grid if anything fails.
 */
(function () {
  const HERO_SELECTOR = ".hero";
  const CONTAINER_CLASS = "hero-3d-canvas";
  const THREE_CDN = "https://unpkg.com/three@0.160.0/build/three.module.js";
  const PARTICLE_COUNT = 48;
  const CONNECTION_DISTANCE = 2.6;
  const CONNECTION_MAX = 2;
  const THEME_INDIGO = 0x7c3aed;
  const THEME_CYAN = 0x0891b2;
  const THEME_PURPLE = 0xa78bfa;

  const prefersReducedMotion = () =>
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (prefersReducedMotion()) return;

  const hero = document.querySelector(HERO_SELECTOR);
  if (!hero) return;

  async function init() {
    let THREE;
    try {
      THREE = await import(THREE_CDN);
    } catch (error) {
      console.warn("[Qefro] Could not load Three.js for hero scene", error);
      return;
    }

    const container = document.createElement("div");
    container.className = CONTAINER_CLASS;
    container.setAttribute("aria-hidden", "true");
    hero.insertBefore(container, hero.firstChild);

    const canvas = document.createElement("canvas");
    canvas.style.display = "block";
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    container.appendChild(canvas);
    const renderer = new THREE.WebGLRenderer({
      canvas,
      alpha: true,
      antialias: false,
      powerPreference: "default",
    });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 1));
    renderer.setSize(container.clientWidth, container.clientHeight);

    const scene = new THREE.Scene();

    const camera = new THREE.PerspectiveCamera(
      60,
      container.clientWidth / container.clientHeight,
      0.1,
      100
    );
    camera.position.z = 8;

    const isDark = () => document.documentElement.getAttribute("data-theme") === "dark";

    function palette() {
      return isDark()
        ? { bg: 0x080a12, particle: THEME_CYAN, line: THEME_INDIGO, shape: THEME_PURPLE }
        : { bg: 0xffffff, particle: THEME_INDIGO, line: THEME_CYAN, shape: THEME_PURPLE };
    }

    let colors = palette();

    // Particles
    const particleGeo = new THREE.BufferGeometry();
    const positions = new Float32Array(PARTICLE_COUNT * 3);
    const velocities = [];
    for (let i = 0; i < PARTICLE_COUNT; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 14;
      positions[i * 3 + 1] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 6;
      velocities.push({
        x: (Math.random() - 0.5) * 0.003,
        y: (Math.random() - 0.5) * 0.003,
        z: (Math.random() - 0.5) * 0.0015,
      });
    }
    particleGeo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    const particleMat = new THREE.PointsMaterial({
      color: colors.particle,
      size: 0.09,
      transparent: true,
      opacity: 0.75,
      sizeAttenuation: true,
    });
    const particles = new THREE.Points(particleGeo, particleMat);
    scene.add(particles);

    // Connection lines (drawn each frame)
    const lineMat = new THREE.LineBasicMaterial({
      color: colors.line,
      transparent: true,
      opacity: 0.12,
    });
    const lineGeo = new THREE.BufferGeometry();
    const lineMesh = new THREE.LineSegments(lineGeo, lineMat);
    scene.add(lineMesh);

    // Floating shapes
    const shapesGroup = new THREE.Group();
    const shapeMat = new THREE.MeshBasicMaterial({
      color: colors.shape,
      wireframe: true,
      transparent: true,
      opacity: 0.18,
    });

    const ico = new THREE.Mesh(new THREE.IcosahedronGeometry(0.55, 0), shapeMat.clone());
    ico.position.set(-3.5, 1.2, -1.5);
    shapesGroup.add(ico);

    const torus = new THREE.Mesh(new THREE.TorusGeometry(0.45, 0.14, 12, 32), shapeMat.clone());
    torus.position.set(3.8, -1.4, -2);
    shapesGroup.add(torus);

    const octa = new THREE.Mesh(new THREE.OctahedronGeometry(0.4, 0), shapeMat.clone());
    octa.position.set(2.2, 2.2, -3);
    shapesGroup.add(octa);

    scene.add(shapesGroup);

    // Mouse parallax
    let targetRotX = 0;
    let targetRotY = 0;
    let currentRotX = 0;
    let currentRotY = 0;

    function onPointerMove(event) {
      const x = (event.clientX / window.innerWidth) * 2 - 1;
      const y = -(event.clientY / window.innerHeight) * 2 + 1;
      targetRotY = x * 0.08;
      targetRotX = y * 0.06;
    }

    window.addEventListener("pointermove", onPointerMove, { passive: true });

    // Theme updates
    const observer = new MutationObserver(() => {
      colors = palette();
      particleMat.color.setHex(colors.particle);
      lineMat.color.setHex(colors.line);
      shapesGroup.children.forEach((child) => {
        child.material.color.setHex(colors.shape);
      });
    });
    observer.observe(document.documentElement, { attributes: true, attributeFilter: ["data-theme"] });

    // Resize
    let resizePending = false;
    function onResize() {
      if (resizePending) return;
      resizePending = true;
      requestAnimationFrame(() => {
        resizePending = false;
        const width = container.clientWidth;
        const height = container.clientHeight;
        camera.aspect = width / height;
        camera.updateProjectionMatrix();
        renderer.setSize(width, height);
      });
    }
    window.addEventListener("resize", onResize, { passive: true });

    // Animation
    let rafId;
    let hidden = false;
    const linePositions = new Float32Array(PARTICLE_COUNT * CONNECTION_MAX * 6);

    function animate() {
      rafId = requestAnimationFrame(animate);

      if (document.hidden) return;

      const posAttr = particleGeo.attributes.position;
      const posArray = posAttr.array;

      for (let i = 0; i < PARTICLE_COUNT; i++) {
        const idx = i * 3;
        posArray[idx] += velocities[i].x;
        posArray[idx + 1] += velocities[i].y;
        posArray[idx + 2] += velocities[i].z;

        // Soft wrap-around bounds
        if (Math.abs(posArray[idx]) > 8) velocities[i].x *= -1;
        if (Math.abs(posArray[idx + 1]) > 6) velocities[i].y *= -1;
        if (Math.abs(posArray[idx + 2]) > 4) velocities[i].z *= -1;
      }
      posAttr.needsUpdate = true;

      // Draw connections
      let lineIdx = 0;
      for (let i = 0; i < PARTICLE_COUNT; i++) {
        let connections = 0;
        const ix = posArray[i * 3];
        const iy = posArray[i * 3 + 1];
        const iz = posArray[i * 3 + 2];
        for (let j = i + 1; j < PARTICLE_COUNT && connections < CONNECTION_MAX; j++) {
          const jx = posArray[j * 3];
          const jy = posArray[j * 3 + 1];
          const jz = posArray[j * 3 + 2];
          const dx = ix - jx;
          const dy = iy - jy;
          const dz = iz - jz;
          const distSq = dx * dx + dy * dy + dz * dz;
          if (distSq < CONNECTION_DISTANCE * CONNECTION_DISTANCE) {
            linePositions[lineIdx++] = ix;
            linePositions[lineIdx++] = iy;
            linePositions[lineIdx++] = iz;
            linePositions[lineIdx++] = jx;
            linePositions[lineIdx++] = jy;
            linePositions[lineIdx++] = jz;
            connections++;
          }
        }
      }
      lineGeo.setAttribute("position", new THREE.BufferAttribute(linePositions.slice(0, lineIdx), 3));

      // Rotate shapes
      ico.rotation.x += 0.002;
      ico.rotation.y += 0.0035;
      torus.rotation.x += 0.0015;
      torus.rotation.y += 0.0025;
      octa.rotation.y += 0.003;

      // Mouse parallax smoothing
      currentRotX += (targetRotX - currentRotX) * 0.04;
      currentRotY += (targetRotY - currentRotY) * 0.04;
      shapesGroup.rotation.x = currentRotX;
      shapesGroup.rotation.y = currentRotY;
      particles.rotation.x = currentRotX * 0.5;
      particles.rotation.y = currentRotY * 0.5;

      renderer.render(scene, camera);
    }

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        hidden = true;
        cancelAnimationFrame(rafId);
      } else {
        hidden = false;
        animate();
      }
    });

    animate();

    // Cleanup on pagehide
    window.addEventListener("pagehide", () => {
      cancelAnimationFrame(rafId);
      observer.disconnect();
      window.removeEventListener("pointermove", onPointerMove);
      window.removeEventListener("resize", onResize);
      renderer.dispose();
    });
  }

  // Defer until page is interactive and hero is visible
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", () => {
      requestAnimationFrame(init);
    });
  } else {
    requestAnimationFrame(init);
  }
})();
