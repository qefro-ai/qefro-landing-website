import { initArchitecture } from "./architecture.js";
import { initButtons } from "./buttons.js";
import { initCompare } from "./compare.js";
import { initDemo } from "./demo.js";
import { initFaq } from "./faq.js";
import { initHero } from "./hero.js";
import { initMicro } from "./micro.js";
import { initMobileMenu } from "./mobile-menu.js";
import { initNav } from "./nav.js";
import { initPricingInteractions } from "./pricing.js";
import { initReveal } from "./reveal.js";
import { initStats } from "./stats.js";
import { prefersReducedMotion } from "./reduced-motion.js";

function boot() {
  document.documentElement.classList.add("js");
  document.documentElement.dataset.motion = "1";
  if (prefersReducedMotion()) {
    document.documentElement.dataset.reducedMotion = "1";
  }

  initNav();
  initMobileMenu();
  initHero();
  initDemo();
  initArchitecture();
  initReveal();
  initPricingInteractions();
  initFaq();
  initCompare();
  initButtons();
  initMicro();
  initStats();

  document.dispatchEvent(new CustomEvent("qefro:motion-ready"));
}

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", boot);
} else {
  boot();
}
