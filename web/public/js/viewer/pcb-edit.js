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
let dragging = null;    // { g, ref, ox, oy, startMm, newX, newY, moved }
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
  applyEnabled();
  layer.addEventListener("pointerdown", onPointerDown, true);
}

export function clearEditOverlay() {
  dragging = null;
  if (ctx) {
    try { ctx.layer.remove(); } catch {}
    try { ctx.status.remove(); } catch {}
  }
  ctx = null;
}

// The component's draggable box: the bounding extent of its pads (the real
// footprint), grown a hair and floored so even a one-pad or colinear part stays
// grabbable. Falls back to the source-parsed nominal size when a component has
// no pads in picks (e.g. a mounting-only part).
function boxFor(comp, padsByRef) {
  const ps = padsByRef.get(comp.ref);
  let cx, cy, w, h;
  if (ps && ps.length) {
    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    for (const p of ps) {
      minX = Math.min(minX, p.x); maxX = Math.max(maxX, p.x);
      minY = Math.min(minY, p.y); maxY = Math.max(maxY, p.y);
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
  if (!enabled) { dragging = null; hideStatus(); }
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
  const g = e.target.closest(".pcb-edit-comp");
  if (!g) return; // a miss falls through to PanZoom for panning
  if (e.button !== undefined && e.button !== 0) return;
  e.stopPropagation();
  e.preventDefault();

  const startMm = clientToMm(e.clientX, e.clientY);
  if (!startMm) return;
  const ox = parseFloat(g.getAttribute("data-x"));
  const oy = parseFloat(g.getAttribute("data-y"));
  dragging = { g, ref: g.getAttribute("data-ref"), ox, oy, startMm, newX: ox, newY: oy, moved: false };
  g.classList.add("dragging");
  try { g.setPointerCapture(e.pointerId); } catch {}
}

function onPointerMove(e) {
  if (!dragging) return;
  const now = clientToMm(e.clientX, e.clientY);
  if (!now) return;
  let nx = dragging.ox + (now.x - dragging.startMm.x);
  let ny = dragging.oy + (now.y - dragging.startMm.y);
  if (SNAP_MM > 0) {
    nx = Math.round(nx / SNAP_MM) * SNAP_MM;
    ny = Math.round(ny / SNAP_MM) * SNAP_MM;
  }
  dragging.newX = nx; dragging.newY = ny;
  if (nx !== dragging.ox || ny !== dragging.oy) dragging.moved = true;
  dragging.g.setAttribute("transform", `translate(${(nx - dragging.ox) * 1000},${(ny - dragging.oy) * 1000})`);
  setStatus(`${dragging.ref}  x=${fmt(nx)}  y=${fmt(ny)}`);
}

function onPointerUp(e) {
  if (!dragging) return;
  const d = dragging;
  dragging = null;
  d.g.classList.remove("dragging");
  try { d.g.releasePointerCapture(e.pointerId); } catch {}
  if (!d.moved) { hideStatus(); return; }
  writePosition(d);
}

document.addEventListener("pointermove", onPointerMove);
document.addEventListener("pointerup", onPointerUp);

// --- write-back -------------------------------------------------------------

async function writePosition(d) {
  if (!ctx) return;
  const { ref, ox, oy, newX, newY, g } = d;
  setStatus(`${ref}: saving…`);
  try {
    const resp = await fetch(`/api/pcb-editor/board/${encodeURIComponent(ctx.boardName)}/update-position`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ ref, oldX: ox, oldY: oy, newX, newY }),
    });
    if (resp.ok) {
      setStatus(`${ref}: ${fmt(ox)},${fmt(oy)} → ${fmt(newX)},${fmt(newY)} ✓`);
      // Anchor the next drag at the new value; the live re-render + refetch will
      // rebuild the whole overlay from the moved copper shortly after.
      g.setAttribute("data-x", String(newX));
      g.setAttribute("data-y", String(newY));
      const comp = ctx.components.find((c) => c.ref === ref);
      if (comp) { comp.x = newX; comp.y = newY; }
    } else {
      const err = await resp.json().catch(() => ({}));
      setStatus(`save failed: ${err.error || resp.status}`, true);
      g.setAttribute("transform", "translate(0,0)"); // snap the handle back
    }
  } catch (e) {
    setStatus(`network error: ${e.message}`, true);
    g.setAttribute("transform", "translate(0,0)");
  }
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
