// Board editor for the PCB viewer — the dev-only counterpart to the pad
// inspector (pcb-pick.js). A toggle (persisted per-browser) turns the board
// into a drag surface: when armed, every component shows a draggable handle
// over its real footprint; dragging it writes the component's new position
// back to the board .tsx source, the dev watcher re-renders the copper, and
// the viewer hot-reloads onto the moved board.
//
// Two data sources, joined by component ref:
//   • /api/pcb-editor/board/<name> — the dev-only source parser (and the
//     write-back endpoint). Gives each component's anchor (the pcbX/pcbY /
//     at() literal in the .tsx) so a drag can name what to rewrite. This
//     route exists ONLY on the dev server; in production it 404s, the fetch
//     returns null, the toggle never appears, and the board stays read-only.
//   • picks.json — pads grouped by ref, so the draggable box is the real
//     footprint extent and the handle sits exactly on the copper.
//
// The overlay lives in the same `translate(…) scale(1,-1)` Gerber-unit frame
// the pad picker uses (1 mm = 1000 SVG units), so component-mm geometry lands
// on its rendered copper. A drag moves the handle by translating its group in
// that frame; on release we POST anchor+delta to the write-back endpoint.
// Hold ⌘/Ctrl/Shift to build a multi-selection — each modifier-click toggles a
// component, and dragging any selected one then moves the whole set as a rigid
// group, writing each moved component back in turn.
// Inspect and Edit are mutually exclusive — arming one disarms the other (via
// the shared "hsm:pcb-tool" event) so their overlays never fight for a click.

import { state } from "./state.js";

const SVGNS = "http://www.w3.org/2000/svg";
const LS_KEY = "pcb-edit";
const SNAP_MM = 0.05;          // drag snap grid (matches the prototype editor)
const PAD_MM = 0.6;            // grow the pad bbox so the handle clears the copper
const MIN_BOX_MM = 1.6;        // floor for tiny / colinear footprints, so they stay grabbable

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let ctx = null;         // { svgEl, layer, status, boardName, components, source, wrapper }
let dragging = null;    // { items:[{g,ref,ox,oy,newX,newY}], startMm, moved, additive, primaryRef, pending, captureEl }
const selected = new Set(); // refs in the current multi-selection (re-applied on rebuild)
let toggleRefresh = null; // the current Edit toggle button's label refresher

// --- dev availability + component fetch (called by pcb.js) ------------------

// Fetch the source-parsed components for a board from the dev-only editor API.
// Returns { name, components } on the dev server, or null in production (route
// 404s) / on any failure — the caller treats null as "no editor", so the Edit
// toggle and overlay simply don't appear.
export async function fetchEditComponents(boardName) {
  if (!boardName) return null;
  try {
    const r = await fetch(`/api/pcb-editor/board/${encodeURIComponent(boardName)}`);
    if (!r.ok) return null;
    const data = await r.json();
    const components = (data.components || []).filter((c) => c && c.ref && c.x != null && c.y != null);
    return components.length ? { name: boardName, components } : null;
  } catch { return null; }
}

// --- install / teardown (called by pcb.js around mountView) -----------------

// Build the draggable overlay on a freshly mounted board SVG. `info` is the
// { name, components } from fetchEditComponents plus the board's picks (for
// footprint geometry), source, and wrapper. Null/absent info tears down.
export function installEditOverlay(svgEl, info) {
  const prevBoard = ctx && ctx.boardName;
  if (svgEl) svgEl.querySelectorAll(".pcb-edit-layer").forEach((n) => n.remove());
  if (!svgEl || !info || !info.components || !info.components.length) { ctx = null; return; }

  // Reuse the SVG's own Gerber-unit transform so component-mm geometry maps
  // onto the rendered copper exactly as the pad-pick layer does.
  const geomG = svgEl.querySelector("g[transform]");
  const transform = (geomG && geomG.getAttribute("transform")) || "scale(1,-1)";

  const padsByRef = new Map();
  for (const p of (info.picks && info.picks.pads) || []) {
    if (!p.ref) continue;
    if (!padsByRef.has(p.ref)) padsByRef.set(p.ref, []);
    padsByRef.get(p.ref).push(p);
  }

  const layer = el("g", { class: "pcb-edit-layer", transform });
  for (const comp of info.components) {
    const box = boxFor(comp, padsByRef);
    const g = el("g", {
      class: "pcb-edit-comp",
      "data-ref": comp.ref,
      "data-x": String(comp.x),
      "data-y": String(comp.y),
      transform: "translate(0,0)",
    });
    g.appendChild(el("rect", {
      class: "pcb-edit-box",
      x: (box.cx - box.w / 2) * 1000,
      y: (box.cy - box.h / 2) * 1000,
      width: box.w * 1000,
      height: box.h * 1000,
      rx: 200,
    }));
    // Counter-flip the label so text rides upright inside the scale(1,-1) frame.
    const lbl = el("g", { class: "pcb-edit-label", transform: `translate(${box.cx * 1000},${box.cy * 1000}) scale(1,-1)` });
    const text = el("text", { x: 0, y: 0, "text-anchor": "middle", "dominant-baseline": "central", "font-size": 1300 });
    text.textContent = comp.ref;
    lbl.appendChild(text);
    g.appendChild(lbl);
    layer.appendChild(g);
  }
  svgEl.appendChild(layer);

  const status = el2("div", "pcb-edit-status");
  info.wrapper.appendChild(status);

  ctx = { svgEl, layer, status, boardName: info.name, components: info.components, source: info.source, wrapper: info.wrapper };
  // A new board starts clean; a same-board rebuild (after a write-back re-render)
  // keeps the selection so a multi-move stays grouped across the reload.
  if (info.name !== prevBoard) selected.clear();
  applyEnabled();
  applySelectionClasses();
  layer.addEventListener("pointerdown", onPointerDown, true);
  // Suppress the browser context menu while armed so Ctrl-click multi-select is
  // clean on macOS, where a Ctrl+click would otherwise pop the menu.
  layer.addEventListener("contextmenu", (e) => { if (enabled) e.preventDefault(); });
}

export function clearEditOverlay() {
  dragging = null;
  selected.clear();
  if (ctx) {
    try { ctx.layer.remove(); } catch {}
    try { ctx.status.remove(); } catch {}
  }
  ctx = null;
}

// The component's draggable box: the bounding extent of its pads (the real
// footprint), grown a hair and floored so even a one-pad or colinear part stays
// grabbable. Each pad contributes its own size (the `pad` field, a diameter/
// edge in mm), not just its centre — otherwise a footprint whose pads are
// colinear (e.g. BT1's coin-cell holder, all five pads on one row) collapses to
// zero in that axis and the handle becomes an unhittable sliver. Falls back to
// the source-parsed nominal size when a component has no pads in picks (e.g. a
// mounting-only part).
function boxFor(comp, padsByRef) {
  const ps = padsByRef.get(comp.ref);
  let cx, cy, w, h;
  if (ps && ps.length) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const p of ps) {
      const r = (Number(p.pad) || 0) / 2; // pad half-extent so colinear pads don't collapse
      minX = Math.min(minX, p.x - r); maxX = Math.max(maxX, p.x + r);
      minY = Math.min(minY, p.y - r); maxY = Math.max(maxY, p.y + r);
    }
    cx = (minX + maxX) / 2; cy = (minY + maxY) / 2;
    w = (maxX - minX) + PAD_MM * 2; h = (maxY - minY) + PAD_MM * 2;
  } else {
    const s = comp.size || {};
    cx = comp.x; cy = comp.y;
    w = s.w || (s.r ? s.r * 2 : 4); h = s.h || (s.r ? s.r * 2 : 4);
  }
  return { cx, cy, w: Math.max(w, MIN_BOX_MM), h: Math.max(h, MIN_BOX_MM) };
}

function applyEnabled() {
  if (ctx) ctx.layer.classList.toggle("active", enabled);
  if (!enabled) { dragging = null; hideStatus(); clearSelection(); }
}

// --- selection (refs; classes re-applied whenever the overlay rebuilds) ------

function applySelectionClasses() {
  if (!ctx) return;
  for (const node of ctx.layer.querySelectorAll(".pcb-edit-comp")) {
    node.classList.toggle("selected", selected.has(node.getAttribute("data-ref")));
  }
}
function setSelection(refs) {
  selected.clear();
  for (const r of refs) selected.add(r);
  applySelectionClasses();
}
function toggleSelected(ref) {
  if (selected.has(ref)) selected.delete(ref); else selected.add(ref);
  applySelectionClasses();
}
function clearSelection() {
  if (!selected.size) return;
  selected.clear();
  applySelectionClasses();
}

// --- drag (pointer capture keeps the move/up on the grabbed component) ------

// Map a viewport point to board mm — undo PanZoom's CSS transform by hand to
// reach SVG viewport coords, then invert the layer's CTM into component space
// (1 mm = 1000 units). Same method, and same getScreenCTM caveat, as pcb-pick.
function clientToMm(clientX, clientY) {
  if (!ctx || !ctx.layer) return null;
  const pz = state.currentPcbPz;
  if (!pz) return null;
  const wr = ctx.wrapper.getBoundingClientRect();
  const t = pz.getTransform();
  const vx = (clientX - wr.left - t.panX) / t.scale;
  const vy = (clientY - wr.top - t.panY) / t.scale;
  const ctm = ctx.layer.getCTM();
  if (!ctm) return null;
  const local = new DOMPoint(vx, vy).matrixTransform(ctm.inverse());
  return { x: local.x / 1000, y: local.y / 1000 };
}

function onPointerDown(e) {
  if (!enabled || !ctx) return;
  const additive = e.metaKey || e.ctrlKey || e.shiftKey;
  const g = e.target.closest(".pcb-edit-comp");
  if (!g) {
    // Empty space: a plain press clears the selection; a modifier press keeps it,
    // so panning around never costs the user their multi-select. Either way we
    // don't stopPropagation, so PanZoom still gets the press and pans the board.
    if (!additive) clearSelection();
    return;
  }
  if (e.button !== undefined && e.button !== 0) return;
  e.stopPropagation();
  e.preventDefault();

  const startMm = clientToMm(e.clientX, e.clientY);
  if (!startMm) return;
  const ref = g.getAttribute("data-ref");

  // Decide what this press grabs, and what a release-without-move does to the
  // selection (standard editor semantics):
  //   • modifier      → grab selection+this; a click toggles this one
  //   • already-sel'd → grab the whole selection; a click collapses to this one
  //   • unselected    → select only this, and grab just it
  let moveRefs, pending;
  if (additive) {
    moveRefs = new Set(selected); moveRefs.add(ref);
    pending = "toggle";
  } else if (selected.has(ref)) {
    moveRefs = new Set(selected);
    pending = "reduce";
  } else {
    setSelection([ref]);
    moveRefs = new Set([ref]);
    pending = null;
  }

  const items = [];
  for (const node of ctx.layer.querySelectorAll(".pcb-edit-comp")) {
    if (!moveRefs.has(node.getAttribute("data-ref"))) continue;
    const ox = parseFloat(node.getAttribute("data-x"));
    const oy = parseFloat(node.getAttribute("data-y"));
    items.push({ g: node, ref: node.getAttribute("data-ref"), ox, oy, newX: ox, newY: oy });
    node.classList.add("dragging");
  }

  dragging = { items, startMm, moved: false, additive, primaryRef: ref, pending, captureEl: g };
  try { g.setPointerCapture(e.pointerId); } catch {}
}

function onPointerMove(e) {
  if (!dragging) return;
  const now = clientToMm(e.clientX, e.clientY);
  if (!now) return;
  // Snap the shared delta (not each absolute position) so the group translates
  // rigidly — relative spacing is preserved no matter how many are grabbed.
  let dx = now.x - dragging.startMm.x;
  let dy = now.y - dragging.startMm.y;
  if (SNAP_MM > 0) {
    dx = Math.round(dx / SNAP_MM) * SNAP_MM;
    dy = Math.round(dy / SNAP_MM) * SNAP_MM;
  }
  for (const it of dragging.items) {
    it.newX = it.ox + dx;
    it.newY = it.oy + dy;
    it.g.setAttribute("transform", `translate(${dx * 1000},${dy * 1000})`);
  }
  if (!dragging.moved && (dx !== 0 || dy !== 0)) {
    dragging.moved = true;
    // First real motion promotes a modifier-press from "toggle on release" into a
    // group drag, so the pressed component reads as selected with the rest.
    if (dragging.additive && !selected.has(dragging.primaryRef)) {
      selected.add(dragging.primaryRef);
      applySelectionClasses();
    }
  }
  if (dragging.items.length > 1) {
    setStatus(`${dragging.items.length} comps  Δx=${fmt(dx)}  Δy=${fmt(dy)}`);
  } else {
    const it = dragging.items[0];
    setStatus(`${it.ref}  x=${fmt(it.newX)}  y=${fmt(it.newY)}`);
  }
}

function onPointerUp(e) {
  if (!dragging) return;
  const d = dragging;
  dragging = null;
  d.items.forEach((it) => it.g.classList.remove("dragging"));
  try { d.captureEl.releasePointerCapture(e.pointerId); } catch {}
  if (!d.moved) {
    // A press that never moved is a selection click, not a drag.
    if (d.pending === "toggle") toggleSelected(d.primaryRef);
    else if (d.pending === "reduce") setSelection([d.primaryRef]);
    hideStatus();
    return;
  }
  writePositions(d.items);
}

document.addEventListener("pointermove", onPointerMove);
document.addEventListener("pointerup", onPointerUp);

// --- write-back -------------------------------------------------------------

// POST one component's move. On success the live overlay/comp adopt the new
// anchor (the dev watcher rebuilds the copper shortly after); on failure the
// handle snaps back. Returns { ok, error } so a batch can be summarised.
async function writeOne({ ref, ox, oy, newX, newY, g }) {
  try {
    const resp = await fetch(`/api/pcb-editor/board/${encodeURIComponent(ctx.boardName)}/update-position`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref, oldX: ox, oldY: oy, newX, newY }),
    });
    if (resp.ok) {
      // Anchor the next drag at the new value; the live re-render + refetch will
      // rebuild the whole overlay from the moved copper shortly after.
      g.setAttribute("data-x", String(newX));
      g.setAttribute("data-y", String(newY));
      const comp = ctx.components.find((c) => c.ref === ref);
      if (comp) { comp.x = newX; comp.y = newY; }
      return { ok: true };
    }
    const err = await resp.json().catch(() => ({}));
    g.setAttribute("transform", "translate(0,0)"); // snap the handle back
    return { ok: false, error: err.error || resp.status };
  } catch (e) {
    g.setAttribute("transform", "translate(0,0)");
    return { ok: false, error: e.message };
  }
}

async function writePosition(d) {
  if (!ctx) return;
  setStatus(`${d.ref}: saving…`);
  const r = await writeOne(d);
  if (r.ok) setStatus(`${d.ref}: ${fmt(d.ox)},${fmt(d.oy)} → ${fmt(d.newX)},${fmt(d.newY)} ✓`);
  else setStatus(`save failed: ${r.error}`, true);
}

// Write every component that actually moved. Sequential, not parallel: each
// write is a read-modify-write of the one board .tsx, so overlapping them risks
// dropping edits. A lone mover reads nicer via the single-component status.
async function writePositions(items) {
  if (!ctx) return;
  const moved = items.filter((it) => it.newX !== it.ox || it.newY !== it.oy);
  if (!moved.length) { hideStatus(); return; }
  if (moved.length === 1) return writePosition(moved[0]);
  setStatus(`saving ${moved.length}…`);
  let ok = 0; const failed = [];
  for (const it of moved) {
    const r = await writeOne(it);
    if (r.ok) ok++; else failed.push(it.ref);
  }
  if (failed.length) setStatus(`saved ${ok}/${moved.length} — failed: ${failed.join(", ")}`, true);
  else setStatus(`moved ${moved.length} components ✓`);
}

// --- status chip ------------------------------------------------------------

function fmt(n) { return Number(n).toFixed(2); }
function setStatus(msg, isError) {
  if (!ctx || !ctx.status) return;
  ctx.status.textContent = msg;
  ctx.status.classList.toggle("error", !!isError);
  ctx.status.classList.add("show");
}
function hideStatus() {
  if (ctx && ctx.status) ctx.status.classList.remove("show");
}

// --- small element helpers --------------------------------------------------

function el(tag, attrs) {
  const n = document.createElementNS(SVGNS, tag);
  for (const k in attrs) n.setAttribute(k, String(attrs[k]));
  return n;
}
function el2(tag, className) {
  const n = document.createElement(tag);
  if (className) n.className = className;
  return n;
}

// --- toggle API + mutual exclusion with the inspector -----------------------

export function setEditEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  applyEnabled();
  // Arming Edit disarms Inspect (and vice versa) so their overlays don't both
  // claim a click. Only announce on arm, so disarming can't ping-pong.
  if (enabled) window.dispatchEvent(new CustomEvent("hsm:pcb-tool", { detail: "edit" }));
}
export function isEditEnabled() { return enabled; }

// Another tool armed itself — stand down if it wasn't us.
window.addEventListener("hsm:pcb-tool", (e) => {
  if (e.detail !== "edit" && enabled) {
    enabled = false;
    try { localStorage.setItem(LS_KEY, "0"); } catch {}
    applyEnabled();
    if (toggleRefresh) toggleRefresh();
  }
});

export function makeEditToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "pcb-edit-toggle";
  function refresh() {
    btn.textContent = enabled ? "Edit: on" : "Edit: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", (ev) => {
    ev.stopPropagation();
    setEditEnabled(!enabled);
    refresh();
  });
  toggleRefresh = refresh;
  refresh();
  return btn;
}
