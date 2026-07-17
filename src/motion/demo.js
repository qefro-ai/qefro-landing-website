import { animate, inView } from "motion";
import { motionOpts, prefersReducedMotion } from "./reduced-motion.js";

const SCRIPT = [
  {
    role: "ai",
    text: "Hi! I can explain how Qefro deploys AI for customers and employees from one platform.",
  },
  { role: "user", text: "What makes Qefro different?" },
  {
    role: "ai",
    text: "Most AI platforms answer questions. Qefro also performs business actions using your knowledge, APIs, and permissions — configure once, deploy everywhere.",
    source: "Qefro product knowledge",
  },
];

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function typeText(el, text, reduced) {
  if (reduced) {
    el.textContent = text;
    return;
  }
  el.textContent = "";
  const chunk = Math.max(1, Math.ceil(text.length / 28));
  for (let i = 0; i < text.length; i += chunk) {
    el.textContent = text.slice(0, i + chunk);
    await sleep(28);
  }
  el.textContent = text;
}

export function initDemo() {
  const section = document.getElementById("demo");
  const body = section?.querySelector(".chat-mock-body");
  const mock = section?.querySelector(".chat-mock");
  if (!section || !body || !mock) return;

  const reduced = prefersReducedMotion();
  let played = false;

  const play = async () => {
    if (played) return;
    played = true;

    body.innerHTML = "";
    animate(mock, { opacity: [0.85, 1], scale: [0.98, 1] }, motionOpts({ duration: 0.35 }));

    for (const step of SCRIPT) {
      if (step.role === "user") {
        await sleep(reduced ? 80 : 450);
        const bubble = document.createElement("div");
        bubble.className = "chat-bubble user";
        bubble.style.opacity = "0";
        bubble.textContent = step.text;
        body.appendChild(bubble);
        await animate(bubble, { opacity: 1, y: [8, 0] }, motionOpts({ duration: 0.28 }));
        continue;
      }

      await sleep(reduced ? 60 : 320);
      const typing = document.createElement("div");
      typing.className = "chat-bubble ai chat-typing";
      typing.setAttribute("aria-hidden", "true");
      typing.innerHTML = "<span></span><span></span><span></span>";
      body.appendChild(typing);
      await animate(typing, { opacity: [0, 1] }, motionOpts({ duration: 0.2 }));
      await sleep(reduced ? 100 : 700);
      typing.remove();

      const bubble = document.createElement("div");
      bubble.className = "chat-bubble ai";
      bubble.style.opacity = "0";
      body.appendChild(bubble);
      await animate(bubble, { opacity: 1, y: [6, 0] }, motionOpts({ duration: 0.25 }));
      await typeText(bubble, step.text, reduced);

      if (step.source) {
        const meta = document.createElement("div");
        meta.className = "chat-source";
        meta.innerHTML = `<span class="chat-source-dot" aria-hidden="true"></span><span>Source: ${step.source}</span><span class="chat-source-check" aria-hidden="true">✓</span>`;
        meta.style.opacity = "0";
        body.appendChild(meta);
        await animate(meta, { opacity: 1, y: [4, 0] }, motionOpts({ duration: 0.3 }));
        const check = meta.querySelector(".chat-source-check");
        if (check) {
          await animate(
            check,
            { scale: [0.6, 1.15, 1], opacity: [0, 1] },
            motionOpts({ duration: 0.35, type: "spring", stiffness: 380, damping: 18 })
          );
        }
      }
    }
  };

  inView(
    section,
    () => {
      play();
    },
    { amount: 0.35 }
  );
}
