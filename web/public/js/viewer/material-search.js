// Material search presents canonical records with contextual model actions and construction features.
import { state } from "./state.js";
import { searchCatalog, materialIndex, bomCounts, bomCountText, materialForFile } from "/contracts/materials.js";
import { instanceLabel, matchFeatures } from "/contracts/features.js";
import { instancesInScene } from "/contracts/material-instances.js";
import { featureUrl } from "/contracts/step-locations.js";
import { COST_KINDS } from "/contracts/part-costs.js";
import { materialHash } from "/contracts/material-tabs.js";

const searchView = { panel: "materials" };
const costView = { panel: "materials", tab: "cost" };
const openMaterial = (...args) => import("./material-nav.js").then(module => module.openMaterial(...args));

// Shared description and construction lookup serves the grid and model companion.
// Stock and supplies open on the Cost tab of a part that uses them.
export function makeMaterialSearch({
  compact = false, featuresInView = () => [], catalogPending = () => false, navigate = open => open(),
} = {}) {
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
      event.preventDefault(); input.value = ""; update(); navigate(open);
    });
    destination.append(link);
    return link;
  }
  function installedAction(assembly, instance, label, destination) {
    const view = { instance: instance.name };
    return result(`/3d#${materialHash(assembly, view)}`, label, null,
      () => openMaterial(assembly, true, view), destination);
  }
  function update() {
    const expanded = new Set([...results.querySelectorAll('.material-search-locations[open]')]
      .map(node => node.closest('.material-search-entry').dataset.material));
    results.replaceChildren();
    const query = input.value.trim();
    results.hidden = !query;
    if (!query) { status.textContent = ""; return; }
    if (catalogPending()) { status.textContent = "Loading materials…"; return; }
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
          const instances = instancesInScene(state.materialCatalog, owner.id, m.id, names, options);
          if (instances.length) {
            if (instances.length > 1) {
              const locations = document.createElement("details"); locations.className = "material-search-locations";
              locations.open = expanded.has(m.id);
              const summary = document.createElement("summary"); summary.textContent = `Show installed locations in ${owner.description}`;
              locations.append(summary);
              for (const instance of instances) {
                installedAction(owner.id, instance, instance.label, locations).classList.add("material-search-location");
              }
              entry.append(locations);
            } else {
              installedAction(owner.id, instances[0], `Show in ${owner.description}`, entry).classList.add("material-search-installed");
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
    for (const feature of featuresInView()) availableFeatures.set(feature.key, feature);
    const features = matchFeatures(query, [...availableFeatures.values()]);
    for (const feature of features) result(featureUrl(feature.key, feature.file || state.mountedDetail?.file || featureFile), feature.label,
      `Feature of ${instanceLabel(feature.body)}`, async () => {
        const file = feature.file || state.mountedDetail?.file || featureFile;
        if (state.mountedDetail?.file !== file) {
          location.hash = new URL(featureUrl(feature.key, file), location.origin).hash; return;
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
