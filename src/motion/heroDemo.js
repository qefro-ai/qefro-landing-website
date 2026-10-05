const DELAY_FIRST = 600;
const DELAY_MSG = 1800;
const DELAY_TYPING = 700;
const DELAY_LOOP = 4000;

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

function getMessages(root) {
  const activePanel = root.querySelector(".hero-scenario-panel.is-active") || root;
  return Array.from(activePanel.querySelectorAll("[data-hero-msg]"));
}

function showTyping(root) {
  const existing = root.querySelector(".demo-typing");
  if (existing) existing.remove();

  const typing = document.createElement("div");
  typing.className = "demo-typing";
  typing.setAttribute("aria-label", "Qefro is typing");
  typing.innerHTML =
    '<span class="demo-avatar demo-avatar-qefro" aria-hidden="true">Q</span>' +
    '<div class="demo-bubble demo-bubble-out demo-typing-bubble">' +
    '<span class="demo-typing-dot"></span>' +
    '<span class="demo-typing-dot"></span>' +
    '<span class="demo-typing-dot"></span>' +
    "</div>";
  root.appendChild(typing);
  return typing;
}

function hideTyping(typing) {
  if (typing && typing.parentNode) typing.parentNode.removeChild(typing);
}

async function runSequence(root) {
  const msgs = getMessages(root);
  if (!msgs.length) return;

  // Reset all messages to hidden
  msgs.forEach((m) => {
    m.classList.remove("demo-msg-visible");
    m.style.opacity = "0";
    m.style.transform = "translateY(8px)";
  });

  await sleep(DELAY_FIRST);

  for (let i = 0; i < msgs.length; i++) {
    const msg = msgs[i];
    const isQefro = msg.classList.contains("demo-qefro");

    // Show typing indicator before Qefro messages (skip first user message)
    if (isQefro && i > 0) {
      const typing = showTyping(root);
      await sleep(DELAY_TYPING);
      hideTyping(typing);
    }

    // Reveal message
    msg.style.transition = "opacity 0.35s ease, transform 0.35s ease";
    msg.style.opacity = "1";
    msg.style.transform = "translateY(0)";
    msg.classList.add("demo-msg-visible");

    // Scroll the conversation container to keep latest message visible
    const convo = root.closest(".hero-demo-body");
    if (convo) {
      convo.scrollTop = convo.scrollHeight;
    }

    if (i < msgs.length - 1) {
      await sleep(DELAY_MSG);
    }
  }
}

export function initHeroDemo() {
  const root = document.querySelector("[data-motion='hero-visual']");
  if (!root) return;

  const reducedMotion =
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  if (reducedMotion) {
    // Show all messages immediately
    getMessages(root).forEach((m) => {
      m.style.opacity = "1";
      m.style.transform = "none";
      m.classList.add("demo-msg-visible");
    });
    return;
  }

  // Start hidden
  getMessages(root).forEach((m) => {
    m.style.opacity = "0";
    m.style.transform = "translateY(8px)";
  });

  async function loop() {
    await runSequence(root);
    await sleep(DELAY_LOOP);
    loop();
  }

  loop();
}
