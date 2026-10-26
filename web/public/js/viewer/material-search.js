import { state } from "./state.js";
import { searchMaterials, bomCounts, bomCountText } from "/contracts/materials.js";
import { openMaterial, materialHash } from "./material-nav.js";
import { stepHash, parseStepHash } from "./step-nav.js";

const modelLabel = (file) => file.split("/").at(-1).replace(/\.step$/, "").replace(/[-_]/g, " ");
const searchView = { panel: "materials" };

// The same description lookup serves the grid and the model companion. CAD
// representations without catalog identities remain discoverable by file name.
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
  function update() {
    results.replaceChildren();
    const query = input.value.trim();
    results.hidden = !query;
    if (!query) { status.textContent = ""; return; }
    const materials = searchMaterials(state.materialCatalog, query);
    const represented = new Set((state.materialCatalog?.materials || []).flatMap((m) => (m.models || []).map((model) => model.file)));
    const words = query.toLowerCase().split(/\s+/);
    const files = state.allFiles.filter((file) => !represented.has(file) &&
      !file.split("/").some((part) => part === "out" || part.startsWith("_")) &&
      words.every((word) => file.replace(/[-_/]/g, " ").toLowerCase().includes(word)));
    const count = materials.length + files.length;
    status.textContent = count ? `${count} result${count === 1 ? "" : "s"}${count > 40 ? " · showing the first 40" : ""}` : "No matches. Try another description or part number.";
    for (const m of materials.slice(0, 40)) {
      const link = document.createElement("a");
      link.href = "/3d#" + materialHash(m.id, searchView);
      const title = document.createElement("strong"); title.textContent = m.description;
      const meta = document.createElement("span"); meta.textContent = `${m.id} · ${m.kind}`;
      const counts = bomCounts(state.materialCatalog, m.id, { finish: state.faucetFinish });
      if (counts.total) meta.textContent += " · " + bomCountText(counts);
      link.append(title, meta);
      link.addEventListener("click", (event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault(); input.value = ""; update(); openMaterial(m.id, true, searchView);
      });
      results.append(link);
    }
    for (const file of files.slice(0, Math.max(0, 40 - materials.length))) {
      const link = document.createElement("a");
      link.href = "/3d#" + stepHash([file], searchView);
      const title = document.createElement("strong"); title.textContent = modelLabel(file);
      const meta = document.createElement("span"); meta.textContent = "CAD model · " + file;
      link.append(title, meta);
      link.addEventListener("click", async (event) => {
        if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
        event.preventDefault(); input.value = ""; update();
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
      results.append(link);
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
