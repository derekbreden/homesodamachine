// Component (assembly-solid) picker for the STEP viewer. A toggle (persisted
// per-browser in localStorage under "step-component-pick") that turns the loaded
// STEP into a click-to-select surface at the whole-component level: click a solid
// to select the named component it belongs to, then hide it from your own view.
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
import { scene, camera, renderer } from "./scene.js";
import { state } from "./state.js";
import { setEdgePickEnabled, syncEdgeToggle, invalidateAllEdgesLayer } from "./edge-picker.js";

const LS_KEY = "step-component-pick";
const SEL = 0xffa733;   // selection highlight — warm amber (distinct from edge yellow, part-highlight cyan, find magenta)
const HOVER = 0x9fd8ff; // hover tint — pale blue
const EDGE_THRESHOLD_DEG = 30;

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let selection = null;   // selected component name, or null
let hoverName = null;   // hovered component name, or null

// --- hidden-set persistence (per open file, view-only) ---
function hiddenKey(file) { return `step-hidden:${file}`; }

export function loadHiddenForFile(file) {
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

// Set mesh.visible from state.hiddenComponents. Called after each STEP load
// (step.js) and after every hide/show. Unnamed meshes stay visible.
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
        m.visible = !(nm && state.hiddenComponents.has(nm));
      } else if (m.isMesh) {
        m.visible = !(m.name && state.hiddenComponents.has(m.name));
      }
    }
  }
  invalidateAllEdgesLayer(); // the edge picker's faint all-edges layer must drop hidden solids
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
  for (const mesh of state.currentGroup.children) {
    if (!mesh.isMesh || mesh.name !== name || mesh.visible === false || seen.has(mesh.geometry)) continue;
    seen.add(mesh.geometry);
    g.add(new THREE.LineSegments(new THREE.EdgesGeometry(mesh.geometry, EDGE_THRESHOLD_DEG), edgeMat));
    const shell = new THREE.Mesh(mesh.geometry.clone(), new THREE.MeshBasicMaterial({
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
  return hits.length ? hits[0].object.name || null : null;
}

// --- selection + hover ---
function selectComponent(name) {
  selection = name;
  drawOverlay(selGroup, name, SEL, selEdgeMat, 0.18);
  setHover(null);
  showPanel();
}

function clearSelectionOverlay() {
  selection = null;
  disposeGroup(selGroup);
}

export function clearComponentPicker() {
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
  close.addEventListener("click", () => { clearSelectionOverlay(); refreshPanel(); });
  head.appendChild(title);
  head.appendChild(nameEl);
  head.appendChild(close);
  panel.appendChild(head);
  panel._nameEl = nameEl;

  const hideBtn = document.createElement("button");
  hideBtn.type = "button";
  hideBtn.className = "edge-panel-all component-hide";
  hideBtn.textContent = "Hide component";
  hideBtn.addEventListener("click", () => {
    if (!selection) return;
    state.hiddenComponents.add(selection);
    persistHidden();
    clearSelectionOverlay();
    applyHiddenComponents();
  });
  panel.appendChild(hideBtn);
  panel._hideBtn = hideBtn;

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
  // Selected component row.
  panel._nameEl.textContent = selection || "—";
  panel._nameEl.title = selection || "";
  const already = selection && state.hiddenComponents.has(selection);
  panel._hideBtn.style.display = selection ? "block" : "none";
  panel._hideBtn.disabled = !!already;
  panel._hideBtn.textContent = already ? "Already hidden" : "Hide component";

  // Hidden list.
  const hidden = panel._hidden;
  hidden.textContent = "";
  const names = [...state.hiddenComponents].sort();
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
      n.textContent = name;
      n.title = name;
      const show = document.createElement("button");
      show.type = "button";
      show.className = "component-show";
      show.textContent = "Show";
      show.addEventListener("click", () => {
        state.hiddenComponents.delete(name);
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

function hidePanel() { if (panel) panel.classList.remove("show"); }

// --- pointer wiring (attached once; act only when enabled + STEP open) ---
let downX = 0, downY = 0;
function active() { return enabled && state.mountedDetail && state.mountedDetail.type === "step"; }

renderer.domElement.addEventListener("pointerdown", (e) => {
  downX = e.clientX; downY = e.clientY;
});
renderer.domElement.addEventListener("pointerup", (e) => {
  if (!active()) return;
  if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return; // a drag, not a click
  const name = pickComponent(e.clientX, e.clientY);
  if (name) selectComponent(name);
  else { clearSelectionOverlay(); refreshPanel(); } // click on empty space clears the selection
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

let toggleRefresh = null;
export function syncComponentToggle() { if (toggleRefresh) toggleRefresh(); }

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

export function makeComponentPickToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "component-pick-toggle";
  function refresh() {
    btn.textContent = enabled ? "Select component: on" : "Select component: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", () => { setComponentPickEnabled(!enabled); refresh(); });
  toggleRefresh = refresh;
  refresh();
  return btn;
}
