export function initCompare() {
  const table = document.querySelector(".compare-table");
  if (!table) return;

  // Highlight Qefro advantage cells — no scroll animation, just mark them.
  table.querySelectorAll("tbody tr").forEach((row) => {
    const tds = row.querySelectorAll("td");
    if (tds.length < 3) return;
    const trad = tds[1].textContent?.trim();
    const qefro = tds[2];
    if (trad === "✗" || trad === "Limited" || trad === "Rare") {
      qefro.classList.add("compare-advantage");
    }
  });
}
