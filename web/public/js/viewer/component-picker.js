// Component picking selects installed parts in assemblies and named construction
// surfaces inside an opened part. The standard Component toggle is persisted
// per-browser in localStorage under "step-component-pick".
//
// This is the whole-solid sibling of edge-picker.js (which picks edges + faces).
// The two are mutually exclusive — arming one disarms the other over the shared
// STEP_TOOL event so a single click doesn't feed both. A component here is the set
// of meshes sharing one occt assembly name (export_assembly names each solid;
// step.js's buildMesh stamps that name onto every THREE.Mesh, front + back). So a
// raycast hit's mesh.name IS the component identity, and hiding a component is
// setting mesh.visible = false on every mesh carrying that name.
//
// Hiding is LOCAL and view-only: it never touches the STEP or the source. The
// hidden set lives in state.hiddenComponents and is persisted per file in
// localStorage ("step-hidden:<file>"), so a dev hot-reload (which rebuilds the
// mesh group) re-applies what you had hidden. Reset by picking a different part
// or clearing the list — never written back to the model.

import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { heldBy, leafOf, standsIn } from "/contracts/body-path.js";
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";
import { setEdgePickEnabled, syncEdgeToggle, invalidateAllEdgesLayer } from "./edge-picker.js";
import { sourceFileFor } from "/contracts/component-sources.js";
import { componentLocation, stepLocation } from "/contracts/step-locations.js";
import { materialForComponent, materialForView } from "/contracts/materials.js";
import { relatedStepsForComponent } from "/contracts/related-steps.js";
import { showsInFaucetFinish } from "/contracts/faucet-options.js";
import { drillTo, drillToComponent } from "./step-nav.js";
import { makePanelCollapse } from "./tool-rail.js";
import { refreshHighlight, fadedBody } from "./part-highlight.js";
import { renderMeasure } from "./hsm.js";
import { containsTriangle, splitFeatureKey } from "/contracts/features.js";
import { sceneFeature, featureGeometry, featureUrl } from "./features.js";

const LS_KEY = "step-component-pick";
const SEL = 0xffa733;   // selection highlight — warm amber (distinct from edge yellow, part-highlight cyan, find magenta)
const HOVER = 0x9fd8ff; // hover tint — pale blue
const EDGE_THRESHOLD_DEG = 30;

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let selection = null;   // selected component name, or null
let selectionBodies = null; // the bodies of a compound installed unit
let hoverName = null;   // hovered component name, or null

// The model on screen, and the bare name of a file the drill-down could reach.
const mountedFile = () =>
  (state.mountedDetail && state.mountedDetail.type === "step" ? state.mountedDetail.file : null);
const stemOf = (file) => file.slice(file.lastIndexOf("/") + 1).replace(/\.step$/i, "");
const namingOptions = () => ({ finish: state.faucetFinish });
const componentBody = name => splitFeatureKey(name)?.body || name;
const materialOf = (name) => materialForComponent(state.materialCatalog, mountedFile(), componentBody(name), namingOptions());
const componentName = (name) => sceneFeature(name)?.label || materialOf(name)?.description || leafOf(name);
const modelName = (file) => materialForView(state.materialCatalog, file, namingOptions())?.description || stemOf(file);

// The opened view defines the selection depth; hiding surrounding parts changes no hierarchy.
function insideOpenedPart(body) {
  const file = mountedFile();
  if (!file) return false;
  const { component } = stepLocation(file);
  if (component) return body === component;
  const material = materialForView(state.materialCatalog, file, namingOptions());
  if (material) return material.kind !== "assembly";
  const head = state.currentGroup?.userData.sharedHead;
  const names = head ? head.meshes.map(node => node.name)
    : (state.currentGroup?.children || []).filter(mesh => mesh.userData?.side === "front").map(mesh => mesh.name);
  return new Set(names).size === 1;
}

// --- hidden-set persistence (per open file, view-only) ---
function hiddenKey(file) { return `step-hidden:${file}`; }

export function loadHiddenForFile(file) {
  if (state.autoHiddenFile !== file) {
    state.autoHiddenComponents.clear();
    state.autoHiddenFile = file;
  }
  let names = [];
  try {
    const raw = localStorage.getItem(hiddenKey(file));
    if (raw) names = JSON.parse(raw);
  } catch { names = []; }
  state.hiddenComponents = new Set(Array.isArray(names) ? names : []);
}

function persistHidden() {
  const file = state.mountedDetail && state.mountedDetail.file;
  if (!file) return;
  try {
    const arr = [...state.hiddenComponents];
    if (arr.length) localStorage.setItem(hiddenKey(file), JSON.stringify(arr));
    else localStorage.removeItem(hiddenKey(file));
  } catch {}
}

// A body the faucet's finish leaves out (a Black faucet has no union) is out of view whatever the
// hidden set says, and the hidden set never names it: nobody hid it.
const inFinish = (name) => showsInFaucetFinish(mountedFile(), name, state.faucetFinish);

// Set mesh.visible from state.hiddenComponents and the faucet's finish. Called after each STEP
// load (step.js), after every hide/show and after a finish change. Unnamed meshes stay visible.
export function applyHiddenComponents() {
  if (state.currentGroup) {
    for (const m of state.currentGroup.children) {
      // An x-ray edge answers to isMesh — xray.js draws it as LineSegments2,
      // which extends Mesh — and carries its solid's name in userData rather
      // than in `name`. It is asked about first, so it is never taken for a
      // body with no name of its own.
      if (m.userData && m.userData.isXrayEdge) {
        // Hide a hidden component's feature edges too, or its wireframe keeps
        // obstructing the interior.
        const nm = m.userData.xrayComponent;
        m.visible = !(nm && standsHidden(nm)) && inFinish(nm);
      } else if (m.isMesh) {
        m.visible = !(m.name && standsHidden(m.name)) && inFinish(m.name);
      }
    }
  }
  invalidateAllEdgesLayer(); // the edge picker's faint all-edges layer must drop hidden solids
  refreshHighlight(); // a selection picks out only what is still drawn
  if (selection) drawOverlay(selGroup, selection, SEL, selEdgeMat, 0.18);
  refreshPanel();
}

// --- overlay (highlight over the selected / hovered component) ---
const overlay = new THREE.Group();
overlay.name = "component-picker";
overlay.renderOrder = 994;
scene.add(overlay);

const selEdgeMat = new THREE.LineBasicMaterial({ color: SEL, transparent: true, opacity: 0.95, depthTest: false });
selEdgeMat.depthWrite = false;
const hoverEdgeMat = new THREE.LineBasicMaterial({ color: HOVER, transparent: true, opacity: 0.8, depthTest: false });
hoverEdgeMat.depthWrite = false;

// --- the tree a name spells ---------------------------------------------------
//
// A BODY IS NAMED FOR THE BRANCH IT HANGS ON. The appliance stands the cold core as a
// sub-assembly, so its bodies arrive called `cold-core/evap-coil` — the STEP carries that
// nesting, and the name carries it too because occt-import-js reports a component node as
// childless and the tree would otherwise not survive the read. Grouping on the name is
// therefore grouping on the model's own structure, not on a convention laid over it.
//
// An index is not a branch: `display/1` is the first solid of one body, which `bodyName` in
// step.js has already taken off by the time a name reaches here.

/** Every body standing inside `group`, by name. */
export { heldBy, leafOf };

export function membersOf(group) {
  const out = new Set();
  if (!state.currentGroup || !group) return [];
  for (const m of state.currentGroup.children) {
    const nm = m.isMesh ? (m.name || (m.userData && m.userData.body)) : null;
    if (nm && nm !== group && standsIn(nm, group)) out.add(nm);
  }
  return [...out].sort();
}

// ISOLATE A NODE, IN PLACE. Everything the machine holds that is not `name` or inside it goes
// out of sight; `name` and its subtree stay. No reload, no second model, no swap — the bodies
// are already loaded and this only decides which of them are drawn. `isolateComponent(null)`
// puts everything back.
//
// This is what a walkthrough wants of a sub-assembly: show me the core, alone, where it stands
// in the appliance. Hiding is by NAME and the tree is in the name, so a node's descendants come
// out of the same set every hand-hidden body does — one mechanism, not two.
// `persist` is what separates a PERSON isolating a node from a SCRIPT doing it. The hidden set
// is saved per file under `step-hidden:<file>`, and that saved set is the reader's own view of
// their own model: a walkthrough that isolates the core and is closed mid-chapter must not
// leave them opening the appliance later with 137 bodies gone and no memory of hiding them.
// So a scripted caller passes `{persist: false}` — the view changes for this session and the
// stored set is neither written nor cleared, which also makes `isolateComponent(null, …)` a
// restore to "nothing hidden" that gives them their own saved view back on the next load.
export function isolateComponent(name, { persist = true } = {}) {
  state.autoHiddenComponents.clear();
  if (!name) {
    state.hiddenComponents = new Set();
  } else {
    const tops = new Set();
    for (const m of (state.currentGroup ? state.currentGroup.children : [])) {
      const nm = m.isMesh ? (m.name || (m.userData && m.userData.body)) : null;
      if (!nm || standsIn(nm, name)) continue;
      // The outermost node that is not the one being isolated, so 62 bodies go out as one name.
      tops.add(heldBy(nm)[0] || nm);
    }
    state.hiddenComponents = tops;
  }
  if (persist) persistHidden();
  applyHiddenComponents();
}

/** Whether `name` is hidden outright or stands inside something that is. */
export function standsHidden(name) {
  return [name, ...heldBy(name)].some(held =>
    state.hiddenComponents.has(held) || state.autoHiddenComponents.has(held));
}

// One overlay Group per role so we can rebuild each independently.
const selGroup = new THREE.Group(); selGroup.renderOrder = 994; overlay.add(selGroup);
const hoverGroup = new THREE.Group(); hoverGroup.renderOrder = 993; overlay.add(hoverGroup);

function disposeGroup(g) {
  for (const c of [...g.children]) {
    g.remove(c);
    if (c.geometry) c.geometry.dispose();
    if (c.material && c.material !== selEdgeMat && c.material !== hoverEdgeMat) c.material.dispose();
  }
}

// Bright edges + a faint translucent shell over every (visible) mesh of `name`,
// depth-test off so it reads through the translucent enclosure. Mirrors
// part-highlight.js, deduped by shared front/back geometry.
function drawOverlay(g, name, color, edgeMat, shellOpacity) {
  disposeGroup(g);
  if (!name || !state.currentGroup) return;
  const seen = new Set();
  const feature = sceneFeature(name);
  const members = g === selGroup && selectionBodies ? selectionBodies : [componentBody(name)];
  // A sub-assembly lights up as the whole of what it holds.
  for (const mesh of state.currentGroup.children) {
    if (!mesh.isMesh || !members.some(body => standsIn(mesh.name, body)) || mesh.visible === false
        || seen.has(mesh.geometry)) continue;
    seen.add(mesh.geometry);
    mesh.updateWorldMatrix(true, false);
    const record = feature && mesh.userData.features?.find(f => f.id === feature.id);
    if (feature && !record) continue;
    const geometry = record ? featureGeometry(mesh, record) : mesh.geometry.clone().applyMatrix4(mesh.matrixWorld);
    g.add(new THREE.LineSegments(new THREE.EdgesGeometry(geometry, EDGE_THRESHOLD_DEG), edgeMat));
    const shell = new THREE.Mesh(geometry, new THREE.MeshBasicMaterial({
      color, transparent: true, opacity: shellOpacity, side: THREE.DoubleSide,
      depthWrite: false, depthTest: false,
    }));
    shell.renderOrder = 993;
    g.add(shell);
  }
}

// --- component raycasting (front, visible meshes only) ---
const _raycaster = new THREE.Raycaster();
const _ndc = new THREE.Vector2();

function frontMeshes() {
  if (!state.currentGroup) return [];
  return state.currentGroup.children.filter(
    (c) => c.userData && c.userData.side === "front" && c.visible !== false && c.name,
  );
}

function pickComponent(clientX, clientY) {
  const targets = frontMeshes();
  if (!targets.length) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  _ndc.set(
    ((clientX - rect.left) / rect.width) * 2 - 1,
    -((clientY - rect.top) / rect.height) * 2 + 1,
  );
  _raycaster.setFromCamera(_ndc, camera);
  const hits = _raycaster.intersectObjects(targets, false);
  // Behind a part chosen in the Materials pane the rest of the model is faded, and a click
  // goes through what is faded to what stands out.
  const hit = hits.find((h) => !fadedBody(h.object)) || hits[0];
  if (!hit) return null;
  if (insideOpenedPart(hit.object.name)) {
    const feature = hit.object.userData.features?.find(f => containsTriangle(f, hit.faceIndex));
    if (feature) return `${hit.object.name}::${feature.id}`;
  }
  return hit.object.name || null;
}

// --- selection + hover ---
export function selectComponent(name, { members = null } = {}) {
  const feature = sceneFeature(name);
  selection = name;
  selectionBodies = members?.length ? [...members] : null;
  drawOverlay(selGroup, name, SEL, selEdgeMat, 0.18);
  setHover(null);
  showPanel();
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED, {
    detail: { file: state.mountedDetail?.file, name: componentBody(name), ...(feature ? { feature: feature.id } : {}) },
  }));
}

function clearSelectionOverlay() {
  selection = null;
  selectionBodies = null;
  disposeGroup(selGroup);
}

// Let go of the selection here and in the Materials panel, whose selection is the model's.
function deselect() {
  clearSelectionOverlay();
  refreshPanel();
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED, {
    detail: { file: state.mountedDetail?.file, name: null },
  }));
}

// The Materials panel moved the selection somewhere a click here did not put it. Answers
// whether there was a selection to clear.
export function clearComponentSelection() {
  if (!selection) return false;
  clearSelectionOverlay();
  setHover(null);
  refreshPanel();
  return true;
}

export function clearComponentPicker({ preserve = false } = {}) {
  if (preserve && selection && (!splitFeatureKey(selection) || sceneFeature(selection))) {
    drawOverlay(selGroup, selection, SEL, selEdgeMat, 0.18);
    setHover(null); refreshPanel(); return;
  }
  clearSelectionOverlay();
  setHover(null);
  hidePanel();
}

function setHover(name) {
  if (name === selection) name = null; // don't double-paint the selected one
  if (name === hoverName) return;
  hoverName = name;
  drawOverlay(hoverGroup, name, HOVER, hoverEdgeMat, 0.1);
}

// --- panel (selected component + the hidden-components list) ---
let panel = null;

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "edge-panel component-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Component";
  const nameEl = document.createElement("span");
  nameEl.className = "edge-panel-file";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", deselect);
  head.appendChild(title);
  head.appendChild(nameEl);
  head.appendChild(makePanelCollapse(panel, "step-component-panel-collapsed", {
    defaultCollapsed: matchMedia("(max-width: 700px)").matches,
  }));
  head.appendChild(close);
  panel.appendChild(head);
  panel._nameEl = nameEl;
  panel._close = close;

  const identity = document.createElement("div");
  identity.className = "component-identity";
  panel.appendChild(identity);
  panel._identity = identity;

  // What hsm measures of the selection, where the server has one (hsm.js).
  const measure = document.createElement("div");
  measure.className = "component-measure";
  panel.appendChild(measure);
  panel._measure = measure;

  const actions = document.createElement("div");
  actions.className = "component-actions";

  // Open its canonical part model, or the selected geometry in its owning assembly.
  const openBtn = document.createElement("button");
  openBtn.type = "button";
  openBtn.className = "edge-panel-all component-open";
  openBtn.textContent = "Open part";
  openBtn.addEventListener("click", () => {
    if (!selection) return;
    const body = componentBody(selection);
    const file = sourceFileFor(body, state.allFiles, mountedFile(), state.materialCatalog, { finish: state.faucetFinish });
    drillToComponent(file && file !== mountedFile() ? file : componentLocation(mountedFile(), body), body);
  });
  actions.appendChild(openBtn);
  panel._openBtn = openBtn;

  const hideBtn = document.createElement("button");
  hideBtn.type = "button";
  hideBtn.className = "edge-panel-all component-hide";
  hideBtn.textContent = "Hide component";
  hideBtn.addEventListener("click", () => {
    if (!selection) return;
    for (const name of selectionBodies || [selection]) state.hiddenComponents.add(name);
    persistHidden();
    clearSelectionOverlay();
    applyHiddenComponents();
  });
  actions.appendChild(hideBtn);
  panel._hideBtn = hideBtn;

  const copy = document.createElement("button");
  copy.type = "button"; copy.className = "edge-panel-all component-copy";
  copy.textContent = "Copy feature link";
  copy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(featureUrl(selection));
    copy.textContent = "Link copied";
  });
  actions.append(copy); panel._copy = copy;

  panel.appendChild(actions);

  // Related models offered by the selected float, manifold body or tube.
  const relatedBtn = document.createElement("button");
  relatedBtn.type = "button";
  relatedBtn.className = "edge-panel-all component-open component-related";
  relatedBtn.addEventListener("click", () => {
    const related = selection && relatedStepsForComponent(selection, state.allFiles)[0];
    if (related) drillTo(related.file);
  });
  panel.appendChild(relatedBtn);
  panel._relatedBtn = relatedBtn;

  const hidden = document.createElement("div");
  hidden.className = "component-hidden";
  panel.appendChild(hidden);
  panel._hidden = hidden;
}

// The panel earns its place when there's a live selection or something hidden
// to restore; otherwise it collapses (showPanel is idempotent, so re-showing to
// refresh content is fine).
function refreshPanel() {
  if (selection || state.hiddenComponents.size) showPanel();
  else hidePanel();
}

function showPanel() {
  if (!panel) buildPanel();
  if (state.currentCadWrapper && panel.parentElement !== state.currentCadWrapper) {
    state.currentCadWrapper.appendChild(panel);
  }
  // Material descriptions name the walkable path; CAD keys identify the selected geometry.
  panel._nameEl.textContent = "";
  panel._nameEl.title = selection || "";
  const feature = sceneFeature(selection);
  panel.classList.toggle("feature-selected", !!feature);
  const bodyName = componentBody(selection);
  const inside = feature || !selection ? [] : membersOf(selection);
  if (selection) {
    [...heldBy(bodyName), ...(feature ? [bodyName] : [])].forEach((held) => {
      const step = document.createElement("button");
      step.type = "button";
      step.className = "component-held-step";
      step.textContent = componentName(held);
      step.title = `Take the whole of ${held}`;
      step.addEventListener("click", () => selectComponent(held));
      panel._nameEl.appendChild(step);
      const sep = document.createElement("span");
      sep.className = "component-held-sep";
      sep.textContent = "/";
      panel._nameEl.appendChild(sep);
    });
    const here = document.createElement("span");
    here.className = "component-held-here";
    here.textContent = componentName(selection);
    panel._nameEl.appendChild(here);
    if (inside.length) {
      const count = document.createElement("span");
      count.className = "component-held-count";
      count.textContent = `${inside.length} inside`;
      panel._nameEl.appendChild(count);
    }
  }
  panel.querySelector(".edge-panel-title").textContent = feature ? "Feature" : "Component";
  panel._identity.replaceChildren();
  if (selection) {
    const material = materialOf(selection);
    if (material) {
      const number = document.createElement("span");
      number.className = "component-material-number";
      number.textContent = material.id;
      panel._identity.appendChild(number);
    }
    const body = document.createElement("span");
    body.className = "component-body-name";
    body.textContent = feature ? `Feature of ${componentName(bodyName)}` : `CAD body: ${selection}`;
    panel._identity.appendChild(body);
  }
  renderMeasure(panel._measure, feature ? null : selection, {
    file: state.mountedDetail?.sourceFile,
    solids: selection ? frontMeshes().filter((m) => m.name === selection).length : 0,
    label: componentName,
  });
  panel._close.style.display = selection ? "" : "none";
  const already = selection && standsHidden(selection);
  panel._hideBtn.style.display = selection && !feature ? "block" : "none";
  panel._hideBtn.disabled = !!already;
  panel._hideBtn.textContent = already ? "Already hidden"
    : inside.length ? `Hide ${componentName(selection)} (${inside.length})` : "Hide component";

  panel._copy.hidden = !feature;
  panel._copy.textContent = "Copy feature link";
  const source = selection ? sourceFileFor(bodyName, state.allFiles, mountedFile(), state.materialCatalog, { finish: state.faucetFinish }) : null;
  const goes = source && source !== mountedFile() ? source : null;
  panel._openBtn.style.display = selection ? "block" : "none";
  const destination = goes && materialForView(state.materialCatalog, goes, namingOptions());
  const selectedMaterial = selection && materialOf(selection);
  panel._openBtn.textContent = goes && destination?.id !== selectedMaterial?.id
    ? `Open ${modelName(goes)}` : "Open component";
  panel._openBtn.title = goes ? `Open ${goes}` : "Open this component from the assembly";
  if (feature) panel._openBtn.textContent = "Open containing part";

  // The destination is named beside the selected component, unless Open part already goes there.
  const offered = selection ? relatedStepsForComponent(selection, state.allFiles)[0] : null;
  const related = offered && offered.file !== goes ? offered : null;
  panel._relatedBtn.style.display = related ? "block" : "none";
  panel._relatedBtn.textContent = related ? `Open ${modelName(related.file)}` : "";
  panel._relatedBtn.title = related ? `Open ${related.file}` : "";

  // Hidden list.
  const hidden = panel._hidden;
  hidden.textContent = "";
  const names = [...new Set([...state.hiddenComponents, ...state.autoHiddenComponents])].sort();
  if (names.length) {
    const head = document.createElement("div");
    head.className = "component-hidden-head";
    const label = document.createElement("span");
    label.textContent = `Hidden (${names.length})`;
    const showAll = document.createElement("button");
    showAll.type = "button";
    showAll.className = "component-show-all";
    showAll.textContent = "Show all";
    showAll.addEventListener("click", () => {
      state.hiddenComponents.clear();
      state.autoHiddenComponents.clear();
      persistHidden();
      applyHiddenComponents();
    });
    head.appendChild(label);
    head.appendChild(showAll);
    hidden.appendChild(head);

    for (const name of names) {
      const row = document.createElement("div");
      row.className = "component-hidden-row";
      const n = document.createElement("span");
      n.className = "component-hidden-name";
      n.textContent = componentName(name);
      const body = document.createElement("span");
      body.className = "component-body-name";
      body.textContent = name;
      n.appendChild(body);
      n.title = name;
      const show = document.createElement("button");
      show.type = "button";
      show.className = "component-show";
      show.textContent = "Show";
      show.addEventListener("click", () => {
        state.hiddenComponents.delete(name);
        state.autoHiddenComponents.delete(name);
        persistHidden();
        applyHiddenComponents();
      });
      row.appendChild(n);
      row.appendChild(show);
      hidden.appendChild(row);
    }
  }
  panel.classList.add("show");
}

function hidePanel() {
  if (!panel) return;
  panel.classList.remove("show");
  renderMeasure(panel._measure, null, {});
}

// --- pointer wiring (attached once; act only when enabled + STEP open) ---
let downX = 0, downY = 0;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }

renderer.domElement.addEventListener("pointerdown", (e) => {
  downX = e.clientX; downY = e.clientY;
});
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!active()) return;
  if (renderer.domElement.parentElement?.classList.contains("cad-gesturing")) return;
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return; // a drag, not a click
  const name = pickComponent(e.clientX, e.clientY);
  if (name) selectComponent(name);
  else deselect(); // click on empty space clears the selection
});
renderer.domElement.addEventListener("pointermove", (e) => {
  if (!active() || e.buttons !== 0) return;
  setHover(pickComponent(e.clientX, e.clientY));
});

// --- toggle + mutual exclusion with the edge picker ---
export function setComponentPickEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  if (enabled) {
    // Arming component-select disarms the edge picker so they don't both claim a
    // click. Announce over STEP_TOOL for any future STEP tool; sync the edge
    // toggle's label directly since it's a sibling in the same toolbar.
    setEdgePickEnabled(false);
    syncEdgeToggle();
    window.dispatchEvent(new CustomEvent(HSM_EVENTS.STEP_TOOL, { detail: "component" }));
    refreshPanel();
  } else {
    clearSelectionOverlay();
    setHover(null);
    refreshPanel();
  }
}

export function isComponentPickEnabled() { return enabled; }

// pick-mode.js registers the segmented control's sync here.
let toggleRefresh = null;
export function setComponentToggleRefresh(fn) { toggleRefresh = fn; }

// Another STEP tool armed itself — stand down if it wasn't us.
window.addEventListener(HSM_EVENTS.STEP_TOOL, (e) => {
  if (e.detail !== "component" && enabled) {
    enabled = false;
    try { localStorage.setItem(LS_KEY, "0"); } catch {}
    clearSelectionOverlay();
    setHover(null);
    refreshPanel();
    if (toggleRefresh) toggleRefresh();
  }
});
