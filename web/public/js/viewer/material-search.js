import { state } from "./state.js";
import { searchCatalog, materialIndex, bomCounts, bomCountText, materialForFile, explodeBom, occurrenceBodies } from "/contracts/materials.js";
import { instanceLabel, matchFeatures } from "/contracts/features.js";
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
        result("/3d#" + materialHash(m.id, searchView), m.description, meta, () => openMaterial(m.id, true, searchView));
        const file = state.mountedDetail?.file || featureFile;
        const owner = materialForFile(state.materialCatalog, state.mountedDetail?.sourceFile || file);
        if (owner?.kind === "assembly") {
          const names = state.currentGroup ? [...new Set(state.currentGroup.children.filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name))] : remote.instances;
          const instances = [...new Set(explodeBom(state.materialCatalog, owner.id).filter(row => row.material.id === m.id)
            .flatMap(row => occurrenceBodies(state.materialCatalog, row.path, names)))];
          for (const name of instances) result(`/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent(`solid: ${name}`)}`,
            instanceLabel(name), `Installed in ${owner.description}`, async () => {
              if (state.mountedDetail?.file !== file) {
                location.hash = `step:${encodeURIComponent(file)}?find=${encodeURIComponent(`solid: ${name}`)}`; return;
              }
              const { selectComponent } = await import("./component-picker.js"); selectComponent(name);
              const { findWhenMounted } = await import("./pick-find.js"); findWhenMounted(file, `solid: ${name}`);
            });
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
    if (event.key === "Enter" && results.querySelectorAll("a").length === 1) results.querySelector("a").click();
  });
  host.refresh = update;
  return host;
}
