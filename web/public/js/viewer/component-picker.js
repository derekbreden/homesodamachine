// Component picking selects installed parts in assemblies and named construction
// surfaces inside an opened part. The standard Component toggle is persisted
// per-browser in localStorage under "step-component-pick".
//
// This is the whole-solid sibling of edge-picker.js (which picks edges + faces).
// The two are mutually exclusive — arming one disarms the other over the shared
// STEP_TOOL event so a single click doesn't feed both. An installed component takes
// every body belonging to its physical placement in the catalog. Opening that part
// makes its internal bodies available to the same picker.
//
// Hiding is LOCAL and view-only: it never touches the STEP or the source. The
// hidden set lives in state.hiddenComponents and is persisted per file in
// localStorage ("step-hidden:<file>"), so a dev hot-reload (which rebuilds the
// mesh group) re-applies what you had hidden. Reset by picking a different part
// or clearing the list — never written back to the model.

import * as THREE from "three";
import { HSM_EVENTS } from "/contracts/client-events.js";
import { heldBy, leafOf, standsIn } from "/contracts/body-path.js";
import { iconSvg } from "/contracts/icons.js";
import * as viewScene from "./scene.js";
import { state } from "./state.js";
import { setEdgePickEnabled, syncEdgeToggle, invalidateAllEdgesLayer } from "./edge-picker.js";
import { sourceFileFor } from "/contracts/component-sources.js";
import { componentLocation, featureUrl, stepLabel, stepLocation } from "/contracts/step-locations.js";
import { materialForComponent, materialForView } from "/contracts/materials.js";
import { mountedFile, installedUnits, unitForKey, componentUnit } from "./component-units.js";
export { componentOwner } from "./component-units.js";
import { relatedStepsForComponent } from "/contracts/related-steps.js";
import { showsInFaucetFinish } from "/contracts/faucet-options.js";
import { drillTo, drillToComponent } from "./step-nav.js";
import { refreshHighlight } from "./part-highlight.js";
import { containsTriangle, instanceLabel, splitFeatureKey } from "/contracts/features.js";
import { sceneFeature, featureGeometry } from "./features.js";
import { requestFeatureEdges } from "./feature-edges.js";
import { nearestSurface } from "./surface-query.js";
import * as xray from "./xray.js";
import { captureHiddenThumbnail } from "./hidden-thumbnail.js";

const LS_KEY = "step-component-pick";
const SEL = 0xffa733;   // selection highlight — warm amber (distinct from edge yellow, part-highlight cyan, find magenta)
const HOVER = 0x9fd8ff; // hover tint — pale blue
const { scene, camera, renderer } = viewScene;
const requestCadRender = () => viewScene.requestCadRender?.();

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let selection = null;   // selected component name, or null
let selectionGroup = null;
let explicitMembers = null; // a Materials location can select one installation inside Wiring
const selectedBodies = () => explicitMembers || (selection && unitForKey(selection)?.bodies);
let hoverName = null;   // hovered component name, or null

// The model on screen, and the bare name of a file the drill-down could reach.
const namingOptions = () => ({ finish: state.faucetFinish });
const componentBody = name => splitFeatureKey(name)?.body || name;
const materialOf = (name) => materialForComponent(state.materialCatalog, mountedFile(), componentBody(name), namingOptions());
const componentName = (name) => sceneFeature(name)?.label || materialOf(name)?.description || leafOf(name);
const modelName = (file) => materialForView(state.materialCatalog, file, namingOptions())?.description || stepLabel(file);

const visibilityName = name => unitForKey(name)?.name || name;

// The opened view defines the selection depth; hiding surrounding parts changes no hierarchy.
function insideOpenedPart(body) {
  const file = mountedFile();
  if (!file) return false;
  const material = materialForView(state.materialCatalog, file, namingOptions());
  if (material) return material.kind !== "assembly";
  const { component } = stepLocation(file);
  if (component) return body === component;
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
  const file = mountedFile();
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
  state.hiddenComponents = new Set([...state.hiddenComponents].map(visibilityName));
  state.autoHiddenComponents = new Set([...state.autoHiddenComponents].map(visibilityName));
  let repaintSelection = false;
  const selectedNames = selectedBodies() || (selection ? [componentBody(selection)] : []);
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
        const visible = !(m.name && standsHidden(m.name)) && inFinish(m.name);
        if (m.visible !== visible && selectedNames.some(name => standsIn(m.name, name))) repaintSelection = true;
        m.visible = visible;
      }
    }
  }
  invalidateAllEdgesLayer(); // the edge picker's faint all-edges layer must drop hidden solids
  refreshHighlight(); // a selection picks out only what is still drawn
  if (repaintSelection) drawOverlay(selGroup, selection);
  syncOverlayVisibility();
  refreshPanel();
  xray.invalidateBlueprintVisibility?.();
  requestCadRender();
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
function shellMaterial(color, opacity) {
  return new THREE.MeshBasicMaterial({ color, opacity, transparent: true, side: THREE.DoubleSide,
    depthWrite: false, depthTest: false, forceSinglePass: true });
}
const selShellMat = shellMaterial(SEL, 0.18), hoverShellMat = shellMaterial(HOVER, 0.1);

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
  const component = installedUnits()?.groupByName.get(group);
  if (component) return component.bodies;
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
      if (!nm || hiddenContainsBody(name, nm)) continue;
      // The outermost node that is not the one being isolated, so 62 bodies go out as one name.
      tops.add(heldBy(nm)[0] || nm);
    }
    state.hiddenComponents = tops;
  }
  if (persist) persistHidden();
  applyHiddenComponents();
}

/** Whether `name` is hidden outright or stands inside something that is. */
export function hiddenContainsBody(hidden, name) {
  if (standsIn(name, hidden)) return true;
  const units = installedUnits();
  return units?.groupByBody.get(name)?.name === hidden || units?.byBody.get(name)?.name === hidden;
}

export function standsHidden(name) {
  if (!state.hiddenComponents.size && !state.autoHiddenComponents.size) return false;
  const units = installedUnits();
  const keys = [name, units?.groupByBody.get(name)?.name, units?.byBody.get(name)?.name, ...heldBy(name)];
  const view = state.currentGroup?.userData.instanceView;
  return keys.some(key => state.hiddenComponents.has(key)) ||
    (!(view?.material && view.names.has(name)) && keys.some(key => state.autoHiddenComponents.has(key)));
}

// Each role reuses its marks while other solids arrive in the assembly.
const selGroup = new THREE.Group(); selGroup.renderOrder = 994; overlay.add(selGroup);
const hoverGroup = new THREE.Group(); hoverGroup.renderOrder = 993; overlay.add(hoverGroup);
selGroup.userData.marks = new Map();
hoverGroup.userData.marks = new Map();

function syncMarkVisibility(mesh, mark) {
  mark.shell.layers.mask = mesh.layers.mask;
  mark.shell.visible = mesh.visible;
  if (mark.line) {
    mark.line.layers.mask = mesh.layers.mask;
    mark.line.visible = mesh.visible;
  }
}
function syncOverlayVisibility() {
  for (const group of [selGroup, hoverGroup]) {
    for (const [mesh, mark] of group.userData.marks) syncMarkVisibility(mesh, mark);
  }
}
window.addEventListener(HSM_EVENTS.BLUEPRINT_VISIBILITY, syncOverlayVisibility);

function removeMark(group, mesh, mark) {
  mesh.removeEventListener("removed", mark.onRemove);
  mark.cancelEdges?.();
  mark.shell.removeFromParent();
  mark.line?.removeFromParent();
  if (mark.feature) mark.shell.geometry.dispose();
  group.userData.marks.delete(mesh);
}
function disposeGroup(group) {
  for (const [mesh, mark] of group.userData.marks) removeMark(group, mesh, mark);
  requestCadRender();
}

function addMark(group, mesh, feature) {
  const selected = group === selGroup;
  const geometry = feature ? featureGeometry(mesh, feature) : mesh.geometry;
  const shell = new THREE.Mesh(geometry, selected ? selShellMat : hoverShellMat);
  shell.matrixAutoUpdate = false;
  shell.renderOrder = group.renderOrder;
  group.add(shell);
  const mark = { shell, feature, source: mesh.geometry, line: null, cancelEdges: null };
  mark.onRemove = () => removeMark(group, mesh, mark);
  mesh.addEventListener("removed", mark.onRemove);
  syncMarkVisibility(mesh, mark);
  group.userData.marks.set(mesh, mark);
  return mark;
}

// The fill borrows the solid already on the GPU. Feature edges join it when they are ready.
function drawOverlay(group, name, showEdges = true) {
  const marks = group.userData.marks;
  if (!name || !state.currentGroup) { disposeGroup(group); return; }
  const feature = splitFeatureKey(name);
  const members = new Set((group === selGroup && selectedBodies()) || componentUnit(name)?.bodies || [componentBody(name)]);
  const keep = new Set();
  for (const mesh of state.currentGroup.children) {
    if (mesh.userData?.side !== "front" || !mesh.visible ||
        !(members.has(mesh.name) || heldBy(mesh.name).some(body => members.has(body)))) continue;
    const record = feature && mesh.userData.features?.find(f => f.id === feature.id);
    if (feature && !record) continue;
    mesh.updateWorldMatrix(true, false);
    keep.add(mesh);
    let mark = marks.get(mesh);
    if (mark && (mark.source !== mesh.geometry || mark.feature !== record ||
        (record && !mark.pose.equals(mesh.matrixWorld)))) {
      removeMark(group, mesh, mark);
      mark = null;
    }
    if (!mark) {
      mark = addMark(group, mesh, record);
      if (record) mark.pose = mesh.matrixWorld.clone();
    }
    if (!record) {
      mark.shell.matrix.copy(mesh.matrixWorld);
      mark.shell.matrixWorldNeedsUpdate = true;
    }
    if (mark.line) {
      mark.line.matrix.copy(mark.shell.matrix);
      mark.line.matrixWorldNeedsUpdate = true;
    } else if (showEdges && !mark.cancelEdges) {
      mark.cancelEdges = requestFeatureEdges(mark.shell.geometry, edges => {
        if (marks.get(mesh) !== mark) return;
        mark.line = new THREE.LineSegments(edges, group === selGroup ? selEdgeMat : hoverEdgeMat);
        mark.line.matrix.copy(mark.shell.matrix);
        mark.line.matrixAutoUpdate = false;
        mark.line.renderOrder = group.renderOrder;
        syncMarkVisibility(mesh, mark);
        group.add(mark.line);
        requestCadRender();
      }, { priority: group === selGroup });
    }
  }
  for (const [mesh, mark] of marks) if (!keep.has(mesh)) removeMark(group, mesh, mark);
  requestCadRender();
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
  _raycaster.layers.mask = camera.layers.mask;
  const hit = nearestSurface(_raycaster, targets);
  if (!hit) return null;
  if (insideOpenedPart(hit.object.name)) {
    const feature = hit.object.userData.features?.find(f => containsTriangle(f, hit.faceIndex));
    if (feature) return `${hit.object.name}::${feature.id}`;
  }
  return hit.object.name;
}

// --- selection + hover ---
export function selectComponent(name, { members = null } = {}) {
  const unit = componentUnit(name, !members);
  name = unit?.name || name;
  const feature = sceneFeature(name);
  selection = name;
  selectionGroup = state.currentGroup;
  explicitMembers = members?.length ? [...members] : null;
  setHover(null);
  showPanel();
  drawOverlay(selGroup, name);
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED, {
    detail: { file: mountedFile(), name: componentBody(name), ...(feature ? { feature: feature.id } : {}) },
  }));
}

function clearSelectionOverlay() {
  selection = null;
  selectionGroup = null;
  explicitMembers = null;
  disposeGroup(selGroup);
}

// Let go of the selection here and in the Materials panel, whose selection is the model's.
function deselect() {
  clearSelectionOverlay();
  refreshPanel();
  window.dispatchEvent(new CustomEvent(HSM_EVENTS.MATERIAL_PICKED, {
    detail: { file: mountedFile(), name: null },
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
  if (preserve && selection && selectionGroup && selectionGroup === state.currentGroup) {
    const units = installedUnits();
    const contains = name => units?.paths ? units.paths.has(name)
      : selectionGroup.children.some(mesh => mesh.userData.side === "front" && standsIn(mesh.name, name));
    const present = splitFeatureKey(selection) ? sceneFeature(selection) : contains(selection)
      || units?.groupByName.has(selection) || explicitMembers?.some(contains);
    if (present) {
      drawOverlay(selGroup, selection);
      setHover(null); refreshPanel(); return;
    }
    setHover(null);
    deselect();
    return;
  }
  clearSelectionOverlay();
  setHover(null);
  hidePanel();
}

let hoverOutlineTimer = 0;
function setHover(name) {
  name = componentUnit(name)?.name || name;
  if (name === selection) name = null; // don't double-paint the selected one
  if (name === hoverName) return;
  hoverName = name;
  clearTimeout(hoverOutlineTimer);
  drawOverlay(hoverGroup, name, false);
  if (name) hoverOutlineTimer = setTimeout(() => drawOverlay(hoverGroup, hoverName), 100);
}

// Component commands overlay the canvas below the workspace toolbar.
let panel = null;
let hiddenObserver = null;
let thumbnailQueued = false;
const hiddenRows = new Map();

function buildPanel() {
  panel = document.createElement("aside");
  panel.className = "component-panel";
  panel.setAttribute("aria-label", "Components in view");

  const model = document.createElement("span");
  model.className = "component-model-name";
  panel._model = model;

  const selected = document.createElement("div");
  selected.className = "component-selection";
  panel.appendChild(selected);
  panel._selected = selected;

  const selectionBar = document.createElement("div");
  selectionBar.className = "component-selection-bar";
  selected.appendChild(selectionBar);
  const nameEl = document.createElement("span");
  nameEl.className = "edge-panel-file";
  selectionBar.appendChild(nameEl);
  panel._nameEl = nameEl;

  const actions = document.createElement("div");
  actions.className = "component-actions";

  // Open its canonical part model, or the selected geometry in its owning assembly.
  const openBtn = document.createElement("button");
  openBtn.type = "button";
  openBtn.className = "component-command component-open";
  openBtn.textContent = "Open";
  openBtn.addEventListener("click", () => {
    if (!selection) return;
    const body = componentBody(selection);
    const file = sourceFileFor(body, state.allFiles, mountedFile(), state.materialCatalog, { finish: state.faucetFinish });
    drillToComponent(file && file !== mountedFile() ? file : componentLocation(mountedFile(), body), selectedBodies() || body);
  });
  actions.appendChild(openBtn);
  panel._openBtn = openBtn;

  const hideBtn = document.createElement("button");
  hideBtn.type = "button";
  hideBtn.className = "component-command component-hide";
  hideBtn.textContent = "Hide";
  hideBtn.addEventListener("click", () => {
    if (!selection) return;
    const focused = document.activeElement === hideBtn;
    const group = installedUnits()?.groupByName.get(selection);
    if (group) {
      for (const body of group.bodies) state.hiddenComponents.delete(visibilityName(body));
      state.hiddenComponents.add(group.name);
    } else {
      for (const name of selectedBodies() || [selection]) state.hiddenComponents.add(visibilityName(name));
    }
    persistHidden();
    clearSelectionOverlay();
    applyHiddenComponents();
    if (focused) focusComponentControls();
  });
  actions.appendChild(hideBtn);
  panel._hideBtn = hideBtn;

  const copy = document.createElement("button");
  copy.type = "button"; copy.className = "component-command component-copy";
  copy.textContent = "Copy link";
  copy.title = "Copy feature link";
  copy.addEventListener("click", async () => {
    await navigator.clipboard.writeText(new URL(featureUrl(selection, mountedFile()), location.origin).href);
    copy.textContent = "Link copied";
  });
  const more = document.createElement("button");
  more.type = "button";
  more.className = "component-command component-details-toggle";
  more.title = "Selection details";
  more.setAttribute("aria-label", more.title);
  more.setAttribute("aria-controls", "component-selection-details");
  more.setAttribute("aria-expanded", "false");
  more.textContent = "⋯";
  more.addEventListener("click", () => setComponentDetails(panel._details.hidden));
  actions.appendChild(more);
  selectionBar.appendChild(actions);
  panel._copy = copy;
  panel._more = more;

  const details = document.createElement("div");
  details.className = "component-details";
  details.id = "component-selection-details";
  details.hidden = true;
  panel._details = details;

  const identity = document.createElement("div");
  identity.className = "component-identity";
  const description = document.createElement("div");
  description.className = "component-catalog-name";
  identity.appendChild(description);
  const featurePath = document.createElement("div");
  featurePath.className = "component-feature-path";
  identity.appendChild(featurePath);
  const metadata = document.createElement("div");
  metadata.className = "component-meta";
  identity.appendChild(metadata);
  details.appendChild(identity);
  panel._description = description;
  panel._featurePath = featurePath;
  panel._metadata = metadata;

  // Related models offered by the selected float, manifold body or tube.
  const relatedBtn = document.createElement("button");
  relatedBtn.type = "button";
  relatedBtn.className = "component-command component-related";
  relatedBtn.addEventListener("click", () => {
    const related = selection && relatedStepsForComponent(selection, state.allFiles)[0];
    if (related) drillTo(related.file);
  });
  const clear = document.createElement("button");
  clear.type = "button";
  clear.className = "component-command component-clear";
  clear.textContent = "Clear selection";
  clear.addEventListener("click", () => {
    const focused = document.activeElement === clear;
    deselect();
    if (focused) focusComponentControls();
  });
  const detailActions = document.createElement("div");
  detailActions.className = "component-detail-actions";
  detailActions.append(copy, relatedBtn, clear);
  details.appendChild(detailActions);
  panel._relatedBtn = relatedBtn;

  const hidden = document.createElement("div");
  hidden.className = "component-hidden";
  const count = document.createElement("span");
  count.className = "component-hidden-count";
  const items = document.createElement("div");
  items.className = "component-hidden-items";
  items.setAttribute("role", "group");
  items.setAttribute("aria-label", "Show hidden components");
  const showAll = document.createElement("button");
  showAll.type = "button";
  showAll.className = "component-command component-show-all";
  showAll.textContent = "Show all";
  showAll.addEventListener("click", () => {
    const focused = document.activeElement === showAll;
    state.hiddenComponents.clear();
    state.autoHiddenComponents.clear();
    const view = state.currentGroup?.userData.instanceView;
    if (view) view.rays = [];
    persistHidden();
    applyHiddenComponents();
    if (focused) focusComponentControls();
  });
  hidden.append(count, items, showAll);
  selected.appendChild(details);
  panel.appendChild(hidden);
  panel._hidden = hidden;
  panel._hiddenCount = count;
  panel._hiddenItems = items;

  hiddenObserver = new IntersectionObserver(entries => {
    for (const entry of entries) {
      const row = hiddenRows.get(entry.target.dataset.body);
      if (row?.element === entry.target) row.inView = entry.isIntersecting;
    }
    queueHiddenThumbnails();
  }, { root: items });
}

function setComponentDetails(open) {
  panel._details.hidden = !open;
  panel._more.setAttribute("aria-expanded", String(open));
}

export function closeComponentDetails() {
  if (!panel || panel._details.hidden || !panel.getClientRects().length) return false;
  setComponentDetails(false);
  panel._more.focus();
  return true;
}

function focusComponentControls(preferred = null) {
  const target = preferred?.isConnected ? preferred : panel._hiddenItems.querySelector(".component-show")
    || (selection ? panel._more : panel.closest(".cad-workspace")?.querySelector(".materials-toggle"));
  target?.focus();
}

function hiddenNames() {
  const names = new Set(state.hiddenComponents);
  if (!state.currentGroup?.userData.instanceView?.preview) {
    const units = installedUnits();
    for (const name of state.autoHiddenComponents) {
      if (!state.hiddenComponents.has(units?.groupByBody.get(name)?.name)) names.add(name);
    }
  }
  return [...names].sort();
}

function updateHiddenRows(names) {
  panel._hidden.hidden = !names.length;
  panel._hiddenCount.textContent = `Hidden ${names.length}`;
  const keep = new Set(names);
  for (const [name, row] of hiddenRows) {
    if (keep.has(name)) continue;
    hiddenObserver.unobserve(row.element);
    row.element.remove();
    hiddenRows.delete(name);
  }
  let next = panel._hiddenItems.firstElementChild;
  for (const name of names) {
    const row = hiddenRows.get(name) || makeHiddenRow(name);
    const label = `Show ${unitForKey(name)?.label || instanceLabel(name)}`;
    if (row.button.title !== label) {
      row.button.title = label;
      row.button.setAttribute("aria-label", label);
    }
    if (row.element !== next) panel._hiddenItems.insertBefore(row.element, next);
    next = row.element.nextElementSibling;
  }
}

function makeHiddenRow(name) {
  const element = document.createElement("div");
  element.className = "component-hidden-row";
  element.dataset.body = name;
  const button = document.createElement("button");
  button.type = "button";
  button.className = "component-show";
  const thumb = document.createElement("span");
  thumb.className = "component-hidden-thumb";
  thumb.setAttribute("aria-hidden", "true");
  thumb.innerHTML = iconSvg("cube", "tool-icon");
  const image = document.createElement("canvas");
  image.hidden = true;
  thumb.appendChild(image);
  button.appendChild(thumb);
  button.addEventListener("click", () => {
    const focused = document.activeElement === button;
    const next = focused && (element.nextElementSibling || element.previousElementSibling)?.querySelector("button");
    const view = state.currentGroup?.userData.instanceView;
    const shown = view?.rays.length ? (view.shown ??= new Set()) : null;
    state.hiddenComponents.delete(name);
    state.autoHiddenComponents.delete(name);
    for (const body of unitForKey(name)?.bodies || [name]) {
      shown?.add(body);
      state.hiddenComponents.delete(body);
      state.autoHiddenComponents.delete(body);
    }
    persistHidden();
    applyHiddenComponents();
    if (focused) focusComponentControls(next);
  });
  element.appendChild(button);
  const row = { element, button, image, inView: false, version: "" };
  hiddenRows.set(name, row);
  hiddenObserver.observe(element);
  return row;
}

function thumbnailSource(group, name) {
  const bodies = new Set(unitForKey(name)?.bodies || [name]);
  const meshes = group.children.filter(mesh => mesh.userData.side === "front" && inFinish(mesh.name)
    && (bodies.has(mesh.name) || heldBy(mesh.name).some(body => bodies.has(body))));
  const version = meshes.map(mesh => {
    mesh.updateWorldMatrix(true, false);
    return [mesh.geometry.id, (mesh.userData.baseMaterial || mesh.material).id, ...mesh.matrixWorld.elements].join(",");
  }).join(";");
  return { meshes, version };
}

// Capture one visible tile at a time from the mounted solids, after the viewer can paint.
function queueHiddenThumbnails() {
  if (thumbnailQueued || !hiddenRows.size) return;
  thumbnailQueued = true;
  const paint = async () => {
    const group = state.currentGroup;
    if (!group || !panel.classList.contains("show") || !panel.getClientRects().length) return;
    const tiles = group.userData.hiddenThumbnails ??= new Map();
    for (const [name, row] of hiddenRows) {
      if (!row.inView) continue;
      const { meshes, version } = thumbnailSource(group, name);
      if (version === row.version) continue;
      row.version = version;
      row.image.hidden = true;
      if (!meshes.length) continue;
      const current = () => state.currentGroup === group && hiddenRows.get(name) === row && row.version === version;
      const cached = tiles.get(name);
      try {
        const alreadyDrawn = cached?.version === version;
        const image = alreadyDrawn ? cached.image : await captureHiddenThumbnail(meshes, current);
        if (image && current() && (alreadyDrawn || thumbnailSource(group, name).version === version)) {
          tiles.delete(name);
          tiles.set(name, { version, image });
          if (tiles.size > 32) tiles.delete(tiles.keys().next().value);
          row.image.width = image.width;
          row.image.height = image.height;
          row.image.getContext("2d").putImageData(image, 0, 0);
          row.image.hidden = false;
        }
      } catch (error) {
        console.warn("Hidden part thumbnail:", error);
      }
      return true;
    }
    return false;
  };
  const next = async () => {
    let more;
    try {
      more = await paint();
    } finally {
      thumbnailQueued = false;
    }
    if (more) queueHiddenThumbnails();
  };
  if (window.requestIdleCallback) requestIdleCallback(next);
  else requestAnimationFrame(() => setTimeout(next, 0));
}

function refreshPanel() {
  const names = hiddenNames();
  if (selection || names.length) showPanel(names);
  else {
    if (panel) updateHiddenRows(names);
    hidePanel();
  }
}

function showPanel(names = hiddenNames()) {
  const wrapper = state.currentCadWrapper;
  const header = wrapper?.closest(".cad-workspace")?.querySelector(".cad-workspace-header");
  if (!header) return;
  if (!panel) buildPanel();
  if (panel.parentElement !== wrapper) {
    wrapper.prepend(panel);
    header.querySelector(".cad-context")?.appendChild(panel._model);
  }
  const file = mountedFile();
  const model = file ? modelName(file) : "";
  if (panel._model.textContent !== model) panel._model.textContent = model;
  panel._selected.hidden = !selection;
  if (panel._nameEl.title !== (selection || "")) setComponentDetails(false);
  // Material descriptions name the walkable path; CAD keys identify the selected geometry.
  panel._nameEl.textContent = "";
  panel._featurePath.replaceChildren();
  panel._nameEl.title = selection || "";
  const feature = sceneFeature(selection);
  const bodyName = componentBody(selection);
  const inside = feature || !selection ? [] : membersOf(selection);
  const description = selection ? componentName(selection) : "";
  const unit = unitForKey(selection);
  const instance = state.currentGroup?.userData.instanceView;
  const installed = instance && !instance.preview && !instance.found && instance.names.has(bodyName);
  const nameInTrail = !feature && description && [...header.querySelectorAll(".cad-crumb.show :is(.cad-crumb-step, .cad-crumb-here)")]
    .some(crumb => crumb.textContent === description);
  if (selection) {
    const parents = [...heldBy(bodyName), ...(feature ? [bodyName] : [])];
    const path = feature ? panel._featurePath : panel._nameEl;
    parents.forEach((held, i) => {
      const step = document.createElement("button");
      step.type = "button";
      step.className = "component-held-step";
      step.textContent = componentName(held);
      step.title = `Take the whole of ${held}`;
      step.addEventListener("click", () => selectComponent(held));
      path.appendChild(step);
      if (!feature || i + 1 < parents.length) {
        const sep = document.createElement("span");
        sep.className = "component-held-sep";
        sep.textContent = "/";
        path.appendChild(sep);
      }
    });
    const here = document.createElement("span");
    here.className = "component-held-here";
    here.textContent = unit?.label || (installed || nameInTrail ? instanceLabel(bodyName) : description);
    here.title = description;
    panel._nameEl.appendChild(here);
  }
  panel._description.textContent = description;
  panel._metadata.replaceChildren();
  if (selection) {
    const material = materialOf(selection);
    if (material) {
      const number = document.createElement("span");
      number.className = "component-material-number";
      number.textContent = material.id;
      panel._metadata.appendChild(number);
    }
    const body = document.createElement("span");
    body.className = "component-body-name";
    body.textContent = `CAD body: ${bodyName}`;
    panel._metadata.appendChild(body);
    if (inside.length) {
      const count = document.createElement("span");
      count.className = "component-body-name";
      count.textContent = `${inside.length} inside`;
      panel._metadata.appendChild(count);
    }
  }
  const already = selection && standsHidden(selection);
  panel._hideBtn.hidden = !selection || !!feature;
  panel._hideBtn.disabled = !!already;
  panel._hideBtn.textContent = already ? "Hidden" : "Hide";
  panel._hideBtn.title = selection ? `Hide ${description}` : "";

  panel._copy.hidden = !feature;
  panel._copy.textContent = "Copy link";
  const source = selection ? sourceFileFor(bodyName, state.allFiles, file, state.materialCatalog, { finish: state.faucetFinish }) : null;
  const goes = source && source !== file ? source : null;
  const destination = goes && materialForView(state.materialCatalog, goes, namingOptions());
  const selectedMaterial = selection && materialOf(selection);
  const openLabel = feature ? "Open containing part" : goes && destination?.id !== selectedMaterial?.id
    ? `Open ${modelName(goes)}` : "Open component";
  panel._openBtn.title = goes ? `Open ${goes}` : openLabel;
  panel._openBtn.setAttribute("aria-label", openLabel);

  // The destination is named beside the selected component, unless Open part already goes there.
  const offered = selection ? relatedStepsForComponent(selection, state.allFiles)[0] : null;
  const related = offered && offered.file !== goes ? offered : null;
  panel._relatedBtn.hidden = !related;
  panel._relatedBtn.textContent = related ? `Open ${modelName(related.file)}` : "";
  panel._relatedBtn.title = related ? `Open ${related.file}` : "";

  updateHiddenRows(names);
  panel.classList.add("show");
  queueHiddenThumbnails();
}

function hidePanel() {
  if (!panel) return;
  panel.classList.remove("show");
  setComponentDetails(false);
  if (!state.currentGroup) updateHiddenRows([]);
}

// --- pointer wiring (attached once; act only when enabled + STEP open) ---
let downX = 0, downY = 0;
let hoverFrame = 0, hoverX = 0, hoverY = 0;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }
function cancelHover() {
  if (hoverFrame) cancelAnimationFrame(hoverFrame);
  hoverFrame = 0;
  setHover(null);
}

renderer.domElement.addEventListener("pointerdown", (e) => {
  downX = e.clientX; downY = e.clientY;
  cancelHover();
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
  if (!active() || e.buttons !== 0 || e.pointerType === "touch") return;
  hoverX = e.clientX; hoverY = e.clientY;
  if (!hoverFrame) hoverFrame = requestAnimationFrame(() => {
    hoverFrame = 0;
    if (active()) setHover(pickComponent(hoverX, hoverY));
  });
});
renderer.domElement.addEventListener("pointerleave", cancelHover);
renderer.domElement.addEventListener("wheel", cancelHover, { passive: true });

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
