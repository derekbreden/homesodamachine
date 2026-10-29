import { state } from "./state.js";
import { searchCatalog, searchTerms, searchWords, termsMatch, materialIndex, bomCounts, bomCountText } from "/contracts/materials.js";
import { COST_KINDS } from "/contracts/part-costs.js";
import { openMaterial, materialHash } from "./material-nav.js";
import { stepHash, parseStepHash } from "./step-nav.js";

const modelLabel = (file) => file.split("/").at(-1).replace(/\.step$/, "").replace(/[-_]/g, " ");
const searchView = { panel: "materials" };
const costView = { panel: "materials", tab: "cost" };
const fileWords = new Map();
const wordsOf = (file) => fileWords.get(file) || fileWords.set(file, searchWords(file)).get(file);

// The same description lookup serves the grid and the model companion. CAD
// representations without catalog identities remain discoverable by file name.
// Stock and supplies open on the Cost tab of a part that uses them.
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
    const terms = searchTerms(query);
    const represented = new Set((state.materialCatalog?.materials || []).flatMap((m) => (m.models || []).map((model) => model.file)));
    const files = state.allFiles.filter((file) => !represented.has(file) &&
      !file.split("/").some((part) => part === "out" || part.startsWith("_")) && termsMatch(terms, wordsOf(file)));
    const count = hits.length + files.length;
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
    for (const file of files.slice(0, Math.max(0, 40 - hits.length))) {
      result("/3d#" + stepHash([file], searchView), modelLabel(file), "CAD model · " + file, async () => {
        if (state.currentCadWrapper) {
          const { drillTo, jumpToStep } = await import("./step-nav.js");
          if (state.mountedDetail?.type === "step") await drillTo(file);
          else await jumpToStep(file);
        } else {
          const { openDetail } = await import("./cad-detail.js"); openDetail(file);
        }
        if (state.currentDetail?.file !== file) return;
        history.replaceState(history.state, "", "#" + stepHash(parseStepHash(location.hash.slice(1)), searchView));
        state.materialPanel?.applyRoute(searchView);
      });
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
