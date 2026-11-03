import { state } from "./state.js";
import { searchCatalog, materialIndex, bomCounts, bomCountText } from "/contracts/materials.js";
import { COST_KINDS } from "/contracts/part-costs.js";
import { openMaterial, materialHash } from "./material-nav.js";

const searchView = { panel: "materials" };
const costView = { panel: "materials", tab: "cost" };

// The same description lookup serves the grid and the model companion. It finds
// what has a part number and nothing else. Stock and supplies open on the Cost
// tab of a part that uses them.
export function makeMaterialSearch({ compact = false } = {}) {
  const host = document.createElement("div");
  host.className = "material-search" + (compact ? " compact" : "");
  const label = document.createElement("label");
  label.textContent = compact ? "Find material" : "Find a material";
  const input = document.createElement("input");
  input.type = "search";
  input.placeholder = compact ? "Name or part number…" : "Description, part number or alias…";
  input.setAttribute("aria-label", "Find a material");
  input.autocomplete = "off";
  const results = document.createElement("div");
  results.className = "material-search-results";
  results.hidden = true;
  const status = document.createElement("p");
  status.className = "material-search-status";
  status.setAttribute("role", "status");
  label.append(input); host.append(label, status, results);
  function result(href, titleText, metaText, open) {
    const link = document.createElement("a");
    link.href = href;
    const title = document.createElement("strong"); title.textContent = titleText;
    const meta = document.createElement("span"); meta.textContent = metaText;
    link.append(title, meta);
    link.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); input.value = ""; update(); open();
    });
    results.append(link);
  }
  function update() {
    results.replaceChildren();
    const query = input.value.trim();
    results.hidden = !query;
    if (!query) { status.textContent = ""; return; }
    const hits = searchCatalog(state.materialCatalog, query);
    const count = hits.length;
    status.textContent = count ? `${count} result${count === 1 ? "" : "s"}${count > 40 ? " · showing the first 40" : ""}` : "No matches. Try another description or part number.";
    const index = materialIndex(state.materialCatalog);
    for (const { material: m, line } of hits.slice(0, 40)) {
      if (m) {
        let meta = `${m.id} · ${m.kind}`;
        const counts = bomCounts(state.materialCatalog, m.id, { finish: state.faucetFinish });
        if (counts.total) meta += " · " + bomCountText(counts);
        result("/3d#" + materialHash(m.id, searchView), m.description, meta, () => openMaterial(m.id, true, searchView));
        continue;
      }
      const holder = line.holders[0].id;
      const users = line.holders.map((h) => index.get(h.id)?.description).filter(Boolean);
      const kinds = COST_KINDS.filter((kind) => line.kinds.has(kind.id)).map((kind, i) => i ? kind.label.toLowerCase() : kind.label).join(" and ");
      result("/3d#" + materialHash(holder, costView), line.label,
        `${kinds} for ${users[0]}${users.length > 1 ? ` +${users.length - 1} more` : ""}`, () => openMaterial(holder, true, costView));
    }
  }
  input.addEventListener("input", update);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { input.value = ""; update(); event.preventDefault(); event.stopPropagation(); }
    if (event.key === "ArrowDown") { results.querySelector("a")?.focus(); event.preventDefault(); }
    if (event.key === "Enter" && results.querySelectorAll("a").length === 1) results.querySelector("a").click();
  });
  host.refresh = update;
  return host;
}
