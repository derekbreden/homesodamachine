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
// group, writing each moved component back in turn. Holding a modifier as the
// drag begins instead locks it to one axis (the dominant one, latched on the
// first travel); Escape mid-drag cancels and snaps every handle back home.
// A selection also raises a bounding box and a small toolbar: rotate (90° — a
// lone part spins in place; a group rotates rigidly about its centre) and the
// six box-edge alignments (left / centre / right, top / middle / bottom).
// Inspect and Edit are mutually exclusive — arming one disarms the other (via
// the shared "hsm:pcb-tool" event) so their overlays never fight for a click.

import { state } from "./state.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

const SVGNS = "http://www.w3.org/2000/svg";
const LS_KEY = "pcb-edit";
const SNAP_MM = 0.05;          // drag snap grid (matches the prototype editor)
const PAD_MM = 0.6;            // grow the pad bbox so the handle clears the copper
const MIN_BOX_MM = 1.6;        // floor for tiny / colinear footprints, so they stay grabbable
const AXIS_LOCK_PX = 4;        // pointer travel (screen px) before a modifier-drag latches its axis

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let ctx = null;         // { svgEl, layer, status, toolbar, boundsG, boundsRect, boardName, components, compByRef, boxByRef, source, wrapper }
let dragging = null;    // { items:[{g,ref,ox,oy,newX,newY}], startMm, startClient, pointerId, moved, axisLock, lockAxis, primaryRef, pending, captureEl }
const selected = new Set(); // refs in the current multi-selection (re-applied on rebuild)
let toggleRefresh = null; // the current Edit toggle button's label refresher
let opBusy = false;     // a rotate / align write-back is in flight — ignore re-clicks until it settles

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
  // A view-swap re-installs on the same wrapper; drop the prior run's HTML chrome
  // (status chip + toolbar) so they don't accumulate.
  const cleanWrap = (info && info.wrapper) || (ctx && ctx.wrapper);
  if (cleanWrap) cleanWrap.querySelectorAll(".pcb-edit-status, .pcb-edit-toolbar").forEach((n) => n.remove());
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
  const boxByRef = new Map();   // ref → footprint box as an offset from the anchor (constant under a move)
  const compByRef = new Map();  // ref → the live component record (x/y/rot updated on write-back)
  for (const comp of info.components) {
    const box = boxFor(comp, padsByRef);
    boxByRef.set(comp.ref, { dx: box.cx - comp.x, dy: box.cy - comp.y, w: box.w, h: box.h });
    compByRef.set(comp.ref, comp);
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
  // Selection bounding box — drawn in the same flipped Gerber frame as the
  // component boxes, and inert so it never eats a drag.
  const boundsG = el("g", { class: "pcb-edit-bounds-g" });
  const boundsRect = el("rect", { class: "pcb-edit-bounds", x: 0, y: 0, width: 0, height: 0 });
  boundsG.appendChild(boundsRect);
  boundsG.style.display = "none";
  layer.appendChild(boundsG);
  svgEl.appendChild(layer);

  const status = el2("div", "pcb-edit-status");
  info.wrapper.appendChild(status);
  const toolbar = buildToolbar();
  info.wrapper.appendChild(toolbar);

  ctx = {
    svgEl, layer, status, toolbar, boundsG, boundsRect,
    boardName: info.name, components: info.components, compByRef, boxByRef,
    source: info.source, wrapper: info.wrapper,
  };
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
    try { ctx.toolbar.remove(); } catch {}
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
  refreshSelectionUI();
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
  //   • modifier      → a release toggles this part (multi-select); a move is an
  //                     axis-locked drag of the grabbed set (the whole selection
  //                     if this part is in it, else just this part)
  //   • already-sel'd → grab the whole selection; a click collapses to this one
  //   • unselected    → select only this, and grab just it
  let moveRefs, pending;
  if (additive) {
    moveRefs = selected.has(ref) ? new Set(selected) : new Set([ref]);
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

  dragging = {
    items, startMm, startClient: { x: e.clientX, y: e.clientY }, pointerId: e.pointerId,
    moved: false, axisLock: additive, lockAxis: null, primaryRef: ref, pending, captureEl: g,
  };
  try { g.setPointerCapture(e.pointerId); } catch {}
  hideSelectionUI(); // bounds + toolbar reappear on release, re-anchored to the moved selection
}

function onPointerMove(e) {
  if (!dragging) return;
  const now = clientToMm(e.clientX, e.clientY);
  if (!now) return;
  let dx = now.x - dragging.startMm.x;
  let dy = now.y - dragging.startMm.y;

  // Modifier held at press → lock to one axis. Latch the dominant screen axis on
  // the first decisive travel, then hold it for the rest of the drag; until then
  // sit in a small dead zone so the choice isn't made on jitter.
  if (dragging.axisLock) {
    if (!dragging.lockAxis) {
      const pdx = e.clientX - dragging.startClient.x;
      const pdy = e.clientY - dragging.startClient.y;
      if (Math.max(Math.abs(pdx), Math.abs(pdy)) < AXIS_LOCK_PX) return;
      dragging.lockAxis = Math.abs(pdx) >= Math.abs(pdy) ? "x" : "y";
    }
    if (dragging.lockAxis === "x") dy = 0; else dx = 0;
  }

  // Snap the shared delta (not each absolute position) so the group translates
  // rigidly — relative spacing is preserved no matter how many are grabbed.
  if (SNAP_MM > 0) {
    dx = Math.round(dx / SNAP_MM) * SNAP_MM;
    dy = Math.round(dy / SNAP_MM) * SNAP_MM;
  }
  for (const it of dragging.items) {
    it.newX = it.ox + dx;
    it.newY = it.oy + dy;
    it.g.setAttribute("transform", `translate(${dx * 1000},${dy * 1000})`);
  }
  if (!dragging.moved && (dx !== 0 || dy !== 0)) dragging.moved = true;

  const axisTag = dragging.lockAxis === "x" ? "↔ " : dragging.lockAxis === "y" ? "↕ " : "";
  if (dragging.items.length > 1) {
    setStatus(`${axisTag}${dragging.items.length} comps  Δx=${fmt(dx)}  Δy=${fmt(dy)}`);
  } else {
    const it = dragging.items[0];
    setStatus(`${axisTag}${it.ref}  x=${fmt(it.newX)}  y=${fmt(it.newY)}`);
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
    else refreshSelectionUI(); // plain press on an unselected part: restore the UI hidden at press
    hideStatus();
    return;
  }
  writePositions(d.items).finally(refreshSelectionUI);
}

document.addEventListener("pointermove", onPointerMove);
document.addEventListener("pointerup", onPointerUp);

// Escape mid-drag aborts it: snap every grabbed handle home and write nothing.
// Capture-phase + stopPropagation so the same keypress doesn't also close the
// viewer; when no drag is in flight we leave Escape alone for exactly that.
function cancelDrag() {
  if (!dragging) return;
  const d = dragging;
  dragging = null;
  for (const it of d.items) {
    it.g.classList.remove("dragging");
    it.g.setAttribute("transform", "translate(0,0)");
  }
  try { d.captureEl.releasePointerCapture(d.pointerId); } catch {}
  setStatus("drag cancelled");
  refreshSelectionUI();
}
document.addEventListener("keydown", (e) => {
  if (dragging && (e.key === "Escape" || e.key === "Esc")) {
    e.preventDefault();
    e.stopPropagation();
    cancelDrag();
  }
}, true);

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

// --- selection bounds + the rotate / align operations -----------------------

// Live records for the current selection (skipping any ref no longer on board).
function selectedItems() {
  if (!ctx) return [];
  const out = [];
  for (const ref of selected) {
    const comp = ctx.compByRef.get(ref);
    if (comp) out.push({ ref, comp });
  }
  return out;
}

// A component's footprint box in absolute board mm, rebuilt from the live anchor
// plus the stored offset — so it stays correct right after a move, without
// waiting for the copper to re-render.
function boxOf(it) {
  const o = (ctx && ctx.boxByRef.get(it.ref)) || { dx: 0, dy: 0, w: MIN_BOX_MM, h: MIN_BOX_MM };
  const cx = it.comp.x + o.dx, cy = it.comp.y + o.dy;
  return { it, cx, cy, left: cx - o.w / 2, right: cx + o.w / 2, bottom: cy - o.h / 2, top: cy + o.h / 2 };
}

// Union extent of a set of items, in board mm (y up).
function boundsOf(items) {
  let left = Infinity, right = -Infinity, bottom = Infinity, top = -Infinity;
  for (const it of items) {
    const b = boxOf(it);
    if (b.left < left) left = b.left;
    if (b.right > right) right = b.right;
    if (b.bottom < bottom) bottom = b.bottom;
    if (b.top > top) top = b.top;
  }
  return { left, right, bottom, top };
}

function gFor(ref) {
  return ctx ? ctx.layer.querySelector(`.pcb-edit-comp[data-ref="${CSS.escape(ref)}"]`) : null;
}
function normRot(deg) { return ((Math.round(deg) % 360) + 360) % 360; }
function snap(v) { return SNAP_MM > 0 ? Math.round(v / SNAP_MM) * SNAP_MM : v; }

// Redraw the bounds box and (re)anchor the toolbar over the live selection.
// Hidden while dragging — both reappear on release, re-anchored to the moved set.
function refreshSelectionUI() {
  if (!ctx) return;
  if (dragging) { hideSelectionUI(); return; }
  const items = selectedItems();
  if (!items.length) { hideSelectionUI(); return; }
  const b = boundsOf(items);
  ctx.boundsRect.setAttribute("x", b.left * 1000);
  ctx.boundsRect.setAttribute("y", b.bottom * 1000);
  ctx.boundsRect.setAttribute("width", (b.right - b.left) * 1000);
  ctx.boundsRect.setAttribute("height", (b.top - b.bottom) * 1000);
  ctx.boundsG.style.display = "";
  ctx.toolbar.classList.toggle("multi", items.length >= 2); // reveal the align row only for ≥ 2
  ctx.toolbar.classList.add("show");
  positionToolbar(b);
}
function hideSelectionUI() {
  if (!ctx) return;
  if (ctx.boundsG) ctx.boundsG.style.display = "none";
  if (ctx.toolbar) ctx.toolbar.classList.remove("show");
}

// Board mm → wrapper-local px — the inverse of clientToMm's view math — so an
// HTML toolbar can sit over a point on the board.
function mmToWrapper(xMm, yMm) {
  const pz = state.currentPcbPz;
  if (!pz || !ctx) return null;
  const ctm = ctx.layer.getCTM();
  if (!ctm) return null;
  const t = pz.getTransform();
  const p = new DOMPoint(xMm * 1000, yMm * 1000).matrixTransform(ctm);
  return { x: p.x * t.scale + t.panX, y: p.y * t.scale + t.panY };
}

// Pin the toolbar centred over the selection's top edge, flipping below when it
// would otherwise ride up into the top chrome.
function positionToolbar(b) {
  if (!ctx || !ctx.toolbar) return;
  if (!b) { const items = selectedItems(); if (!items.length) return; b = boundsOf(items); }
  const midX = (b.left + b.right) / 2;
  const top = mmToWrapper(midX, b.top);
  const bottom = mmToWrapper(midX, b.bottom);
  if (!top) return;
  const tb = ctx.toolbar;
  const h = tb.offsetHeight || 38;
  const below = (top.y - 12 - h) < 4 && !!bottom;
  const anchor = below ? bottom : top;
  tb.style.left = anchor.x + "px";
  tb.style.top = anchor.y + "px";
  tb.classList.toggle("below", below);
}

// Keep the toolbar glued to the board as the view changes. Driven by the events
// that actually pan / zoom (pointer drag, wheel, resize) rather than a standing
// rAF, so the page stays idle — and cheap — when nothing is moving.
function repositionToolbarIfShown() {
  if (ctx && ctx.toolbar && ctx.toolbar.classList.contains("show") && !dragging) positionToolbar();
}
document.addEventListener("pointermove", repositionToolbarIfShown, { passive: true });
document.addEventListener("pointerup", repositionToolbarIfShown, { passive: true });
window.addEventListener("wheel", repositionToolbarIfShown, { passive: true });
window.addEventListener("resize", repositionToolbarIfShown);

// Rotate the selection 90°. A lone part just bumps its rotation (spins in place);
// a group rotates rigidly about its bounding-box centre — each anchor swings 90°
// about the centre AND each part re-orients, which is two write-backs apiece.
async function rotateSelection() {
  if (opBusy || !ctx) return;
  const items = selectedItems();
  if (!items.length) return;
  opBusy = true;
  try {
    if (items.length === 1) {
      const it = items[0];
      const nr = normRot(it.comp.rot + 90);
      setStatus(`${it.ref}: rotate → ${nr}°`);
      const r = await writeRotation(it.ref, nr);
      setStatus(r.ok ? `${it.ref}: ${nr}° ✓` : `rotate failed: ${r.error}`, !r.ok);
    } else {
      const b = boundsOf(items);
      const cx = (b.left + b.right) / 2, cy = (b.bottom + b.top) / 2;
      setStatus(`rotating ${items.length}…`);
      let ok = 0; const failed = [];
      for (const it of items) {
        const dx = it.comp.x - cx, dy = it.comp.y - cy;
        const nx = snap(cx - dy), ny = snap(cy + dx); // +90° (CCW), matching the rotation bump
        const nr = normRot(it.comp.rot + 90);
        const g = gFor(it.ref);
        if (g) g.setAttribute("transform", `translate(${(nx - it.comp.x) * 1000},${(ny - it.comp.y) * 1000})`);
        const moved = nx !== it.comp.x || ny !== it.comp.y;
        const pr = moved ? await writeOne({ ref: it.ref, ox: it.comp.x, oy: it.comp.y, newX: nx, newY: ny, g }) : { ok: true };
        const rr = await writeRotation(it.ref, nr);
        if (pr.ok && rr.ok) ok++; else failed.push(it.ref);
      }
      setStatus(failed.length ? `rotated ${ok}/${items.length} — failed: ${failed.join(", ")}` : `rotated ${items.length} ✓`, !!failed.length);
    }
  } finally {
    opBusy = false;
    refreshSelectionUI();
  }
}

// Align the selected footprints by a shared box edge (or centre) on one axis.
// axis "x": mode left | center | right. axis "y": mode top | middle | bottom.
async function alignSelection(axis, mode) {
  if (opBusy || !ctx) return;
  const items = selectedItems();
  if (items.length < 2) return;
  opBusy = true;
  try {
    const boxes = items.map(boxOf);
    let target;
    if (axis === "x") {
      const minL = Math.min(...boxes.map((b) => b.left));
      const maxR = Math.max(...boxes.map((b) => b.right));
      target = mode === "left" ? minL : mode === "right" ? maxR : (minL + maxR) / 2;
    } else {
      const maxT = Math.max(...boxes.map((b) => b.top));
      const minB = Math.min(...boxes.map((b) => b.bottom));
      target = mode === "top" ? maxT : mode === "bottom" ? minB : (minB + maxT) / 2;
    }
    const writes = [];
    for (const b of boxes) {
      const it = b.it;
      let nx = it.comp.x, ny = it.comp.y;
      if (axis === "x") {
        const cur = mode === "left" ? b.left : mode === "right" ? b.right : b.cx;
        nx = snap(it.comp.x + (target - cur));
      } else {
        const cur = mode === "top" ? b.top : mode === "bottom" ? b.bottom : b.cy;
        ny = snap(it.comp.y + (target - cur));
      }
      const g = gFor(it.ref);
      if (g) g.setAttribute("transform", `translate(${(nx - it.comp.x) * 1000},${(ny - it.comp.y) * 1000})`);
      writes.push({ ref: it.ref, ox: it.comp.x, oy: it.comp.y, newX: nx, newY: ny, g });
    }
    await writePositions(writes);
  } finally {
    opBusy = false;
    refreshSelectionUI();
  }
}

// POST a rotation change for one component; mirrors writeOne's contract.
async function writeRotation(ref, newRot) {
  try {
    const resp = await fetch(`/api/pcb-editor/board/${encodeURIComponent(ctx.boardName)}/update-rotation`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref, rot: newRot }),
    });
    if (resp.ok) {
      const c = ctx.compByRef.get(ref);
      if (c) c.rot = newRot;
      return { ok: true };
    }
    const err = await resp.json().catch(() => ({}));
    return { ok: false, error: err.error || resp.status };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// --- selection toolbar (rotate + the six alignments) ------------------------

// 24×24 icons in currentColor, matching the conventional arrangement-tool glyphs:
// a circular rotate arrow, and bar-against-a-guide marks for each alignment.
const ICONS = {
  rotate:     `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.5 12a8.5 8.5 0 1 1-2.6-6.1"/><polyline points="20.5 3.5 20.5 9 15 9"/></svg>`,
  "x:left":   `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2.4" y="3.5" width="1.7" height="17" rx="0.6" opacity="0.65"/><rect x="6" y="6.4" width="13" height="3.6" rx="1.2"/><rect x="6" y="14" width="8.5" height="3.6" rx="1.2"/></svg>`,
  "x:center": `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="11.15" y="2.6" width="1.7" height="18.8" rx="0.6" opacity="0.65"/><rect x="5.5" y="6.4" width="13" height="3.6" rx="1.2"/><rect x="7.75" y="14" width="8.5" height="3.6" rx="1.2"/></svg>`,
  "x:right":  `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="19.9" y="3.5" width="1.7" height="17" rx="0.6" opacity="0.65"/><rect x="5" y="6.4" width="13" height="3.6" rx="1.2"/><rect x="9.5" y="14" width="8.5" height="3.6" rx="1.2"/></svg>`,
  "y:top":    `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3.5" y="2.4" width="17" height="1.7" rx="0.6" opacity="0.65"/><rect x="6.4" y="6" width="3.6" height="13" rx="1.2"/><rect x="14" y="6" width="3.6" height="8.5" rx="1.2"/></svg>`,
  "y:middle": `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="2.6" y="11.15" width="18.8" height="1.7" rx="0.6" opacity="0.65"/><rect x="6.4" y="5.5" width="3.6" height="13" rx="1.2"/><rect x="14" y="7.75" width="3.6" height="8.5" rx="1.2"/></svg>`,
  "y:bottom": `<svg viewBox="0 0 24 24" fill="currentColor"><rect x="3.5" y="19.9" width="17" height="1.7" rx="0.6" opacity="0.65"/><rect x="6.4" y="5" width="3.6" height="13" rx="1.2"/><rect x="14" y="9.5" width="3.6" height="8.5" rx="1.2"/></svg>`,
};

function toolBtn(action, title, run) {
  const b = el2("button", "pcb-edit-tool-btn");
  b.type = "button";
  b.title = title;
  b.setAttribute("aria-label", title);
  b.innerHTML = ICONS[action];
  b.addEventListener("click", (e) => { e.stopPropagation(); run(); });
  return b;
}

function buildToolbar() {
  const tb = el2("div", "pcb-edit-toolbar");
  // Keep presses off the board so PanZoom doesn't pan beneath the buttons.
  tb.addEventListener("pointerdown", (e) => e.stopPropagation());
  tb.appendChild(toolBtn("rotate", "Rotate 90°", rotateSelection));
  tb.appendChild(el2("span", "pcb-edit-tool-sep align-only"));
  tb.appendChild(toolBtn("x:left", "Align left edges", () => alignSelection("x", "left")));
  tb.appendChild(toolBtn("x:center", "Align horizontal centres", () => alignSelection("x", "center")));
  tb.appendChild(toolBtn("x:right", "Align right edges", () => alignSelection("x", "right")));
  tb.appendChild(el2("span", "pcb-edit-tool-sep align-only"));
  tb.appendChild(toolBtn("y:top", "Align top edges", () => alignSelection("y", "top")));
  tb.appendChild(toolBtn("y:middle", "Align vertical centres", () => alignSelection("y", "middle")));
  tb.appendChild(toolBtn("y:bottom", "Align bottom edges", () => alignSelection("y", "bottom")));
  // Mark the alignment controls so CSS can hide them unless ≥ 2 parts are selected.
  for (const n of tb.querySelectorAll('[title^="Align"]')) n.classList.add("align-only");
  return tb;
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
  if (enabled) window.dispatchEvent(new CustomEvent(HSM_EVENTS.PCB_TOOL, { detail: "edit" }));
}
export function isEditEnabled() { return enabled; }

// Another tool armed itself — stand down if it wasn't us.
window.addEventListener(HSM_EVENTS.PCB_TOOL, (e) => {
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
