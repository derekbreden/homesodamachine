// Material search presents canonical records with contextual model actions and construction features.
import { state } from "./state.js";
import { searchCatalog, materialIndex, bomCounts, bomCountText, materialForFile, explodeBom, occurrenceBodies } from "/contracts/materials.js";
import { instanceBody, instanceLabel, matchFeatures } from "/contracts/features.js";
import { sceneFeatures, featureUrl } from "./features.js";
import { COST_KINDS } from "/contracts/part-costs.js";
import { openMaterial, materialHash } from "./material-nav.js";

const searchView = { panel: "materials" };
const costView = { panel: "materials", tab: "cost" };

// Shared description and construction lookup serves the grid and model companion.
// Stock and supplies open on the Cost tab of a part that uses them.
export function makeMaterialSearch({ compact = false } = {}) {
  let remote = { file: null, features: [], instances: [], loaded: 0, pending: false };
  const host = document.createElement("div");
  host.className = "material-search" + (compact ? " compact" : "");
  const label = document.createElement("label");
  label.textContent = compact ? "Find" : "Find a part or feature";
  const input = document.createElement("input");
  input.type = "search";
  input.placeholder = "Part, instance or feature…";
  input.setAttribute("aria-label", "Find a part or feature");
  input.autocomplete = "off";
  const results = document.createElement("div");
  results.className = "material-search-results";
  results.hidden = true;
  const status = document.createElement("p");
  status.className = "material-search-status";
  status.setAttribute("role", "status");
  label.append(input); host.append(label, status, results);
  function result(href, titleText, metaText, open, destination = results) {
    const link = document.createElement("a");
    link.href = href;
    const title = document.createElement("strong"); title.textContent = titleText;
    link.append(title);
    if (metaText) {
      const meta = document.createElement("span"); meta.textContent = metaText;
      link.append(meta);
    }
    link.addEventListener("click", (event) => {
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
      event.preventDefault(); input.value = ""; update(); open();
    });
    destination.append(link);
    return link;
  }
  function installedAction(file, text, label, destination, selection = null) {
    const link = result(`/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent(text)}`, label, null, async () => {
      if (state.mountedDetail?.file !== file) {
        location.hash = `step:${encodeURIComponent(file)}?find=${encodeURIComponent(text)}`; return;
      }
      const { selectComponent, clearComponentSelection } = await import("./component-picker.js");
      if (selection) selectComponent(selection);
      else {
        clearComponentSelection();
        const { clearHighlight } = await import("./part-highlight.js"); clearHighlight();
      }
      const { findWhenMounted } = await import("./pick-find.js"); findWhenMounted(file, text);
    }, destination);
    return link;
  }
  function update() {
    results.replaceChildren();
    const query = input.value.trim();
    results.hidden = !query;
    if (!query) { status.textContent = ""; return; }
    const featureFile = state.mountedDetail?.sourceFile || state.mountedDetail?.file || "manifold-layout/enclosure-assembly.step";
    if (!remote.pending && (remote.file !== featureFile || Date.now() - remote.loaded > 5000)) {
      remote = { file: featureFile, features: [], instances: [], loaded: Date.now(), pending: true };
      const request = remote;
      fetch(`/api/features?file=${encodeURIComponent(featureFile)}`).then(r => r.ok ? r.json() : { features: [] }).then(data => {
        if (remote !== request) return;
        remote.features = data.features || []; remote.instances = data.instances || []; remote.pending = false;
        if (input.value.trim()) update();
      }).catch(() => { if (remote === request) remote.pending = false; });
    }
    const hits = searchCatalog(state.materialCatalog, query);
    const count = hits.length;
    const suggested = hits[0]?.match === "suggestion";
    const noun = suggested ? (count === 1 ? "possible match" : "possible matches") : (count === 1 ? "result" : "results");
    status.textContent = count ? `${suggested ? "No exact matches · " : ""}${count} ${noun}${count > 40 ? " · showing the first 40" : ""}` : "No matches. Try another description or part number.";
    const index = materialIndex(state.materialCatalog);
    for (const { material: m, line, match, corrections, unmatched } of hits.slice(0, 40)) {
      if (m) {
        let meta = `${m.id} · ${m.kind}`;
        if (match === "suggestion") meta += " · possible match" + (unmatched.length
          ? ` · unmatched: ${unmatched.join(", ")}`
          : ` · spelling: ${corrections.map(({ from, to }) => `${from} → ${to}`).join(", ")}`);
        const counts = bomCounts(state.materialCatalog, m.id, { finish: state.faucetFinish });
        if (counts.total) meta += " · " + bomCountText(counts);
        const entry = document.createElement("div");
        entry.className = "material-search-entry";
        entry.dataset.material = m.id;
        results.append(entry);
        result("/3d#" + materialHash(m.id, searchView), m.description, meta, () => openMaterial(m.id, true, searchView), entry);
        const file = state.mountedDetail?.file || featureFile;
        const owner = materialForFile(state.materialCatalog, state.mountedDetail?.sourceFile || file);
        if (owner?.kind === "assembly") {
          const names = state.currentGroup ? [...new Set(state.currentGroup.children.filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))] : remote.instances;
          const options = { finish: state.faucetFinish };
          const rows = explodeBom(state.materialCatalog, owner.id, options).filter(row => row.material.id === m.id);
          const instances = [...new Set(rows.flatMap(row => occurrenceBodies(state.materialCatalog, row.path, names, options)))];
          if (instances.length) {
            // BOM quantities distinguish repeated parts from several solids representing a part.
            const quantity = rows.every(row => row.item.unit === "ea" && Number.isSafeInteger(row.quantity))
              ? rows.reduce((sum, row) => sum + row.quantity, 0) : null;
            const groups = new Map();
            for (const name of instances) {
              const body = instanceBody(name);
              if (!groups.has(body)) groups.set(body, []);
              groups.get(body).push(name);
            }
            if (quantity > 1 && groups.size === quantity) {
              const locations = document.createElement("details"); locations.className = "material-search-locations";
              const summary = document.createElement("summary"); summary.textContent = `Show installed locations in ${owner.description}`;
              locations.append(summary);
              for (const [body, bodies] of [...groups].sort(([a], [b]) => a.localeCompare(b))) {
                installedAction(file, bodies.map(name => `solid: ${name}`).join("\n"), instanceLabel(body), locations, body).classList.add("material-search-location");
              }
              entry.append(locations);
            } else {
              installedAction(file, m.id, `Show in ${owner.description}`, entry).classList.add("material-search-installed");
            }
          }
        }
        continue;
      }
      const holder = line.holders[0].id;
      const users = line.holders.map((h) => index.get(h.id)?.description).filter(Boolean);
      const kinds = COST_KINDS.filter((kind) => line.kinds.has(kind.id)).map((kind, i) => i ? kind.label.toLowerCase() : kind.label).join(" and ");
      result("/3d#" + materialHash(holder, costView), line.label,
        `${kinds} for ${users[0]}${users.length > 1 ? ` +${users.length - 1} more` : ""}`, () => openMaterial(holder, true, costView));
    }
    const availableFeatures = new Map(remote.features.map(f => [f.key, f]));
    for (const feature of sceneFeatures()) availableFeatures.set(feature.key, feature);
    const features = matchFeatures(query, [...availableFeatures.values()]);
    for (const feature of features) result(featureUrl(feature.key, feature.file || state.mountedDetail?.file || featureFile), feature.label,
      `Feature of ${instanceLabel(feature.body)}`, async () => {
        const file = feature.file || state.mountedDetail?.file || featureFile;
        if (state.mountedDetail?.file !== file) {
          location.hash = new URL(featureUrl(feature.key, file)).hash; return;
        }
        const { selectComponent } = await import("./component-picker.js"); selectComponent(feature.key);
        const { findWhenMounted } = await import("./pick-find.js"); findWhenMounted(file, `feature: ${feature.key}`);
      });
    if (features.length) status.textContent = `${count} material result${count === 1 ? "" : "s"} · ${features.length} feature${features.length === 1 ? "" : "s"}`;
  }
  input.addEventListener("input", update);
  input.addEventListener("keydown", (event) => {
    if (event.key === "Escape") { input.value = ""; update(); event.preventDefault(); event.stopPropagation(); }
    if (event.key === "ArrowDown") { results.querySelector("a")?.focus(); event.preventDefault(); }
    if (event.key === "Enter") {
      const records = [...results.children].filter(child => child.classList.contains("material-search-entry") || child.tagName === "A");
      if (records.length === 1) results.querySelector("a")?.click();
    }
  });
  host.refresh = update;
  return host;
}
