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

export function initDemo() {
  const section = document.getElementById("demo");
  const body = section?.querySelector(".chat-mock-body");
  const mock = section?.querySelector(".chat-mock");
  if (!section || !body || !mock) return;

  // Static: render the scripted conversation immediately, no typing animation.
  body.innerHTML = "";
  mock.style.opacity = "1";

  SCRIPT.forEach((step) => {
    const bubble = document.createElement("div");
    bubble.className = `chat-bubble ${step.role}`;
    bubble.textContent = step.text;
    body.appendChild(bubble);

    if (step.source) {
      const meta = document.createElement("div");
      meta.className = "chat-source";
      meta.innerHTML = `<span class="chat-source-dot" aria-hidden="true"></span><span>Source: ${step.source}</span><span class="chat-source-check" aria-hidden="true">✓</span>`;
      body.appendChild(meta);
    }
  });
}
