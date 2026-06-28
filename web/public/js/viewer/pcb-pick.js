// Board inspector for the PCB viewer — the 2D counterpart to the STEP edge
// picker. A toggle (persisted per-browser) turns the board into a clickable
// surface: click a pad / through-hole, a via, or a trace to select it and copy
// a text blob naming it; click anywhere else (bare laminate, an unpicked copper
// pour, silkscreen) to drop a marker at that spot and copy its board (x, y) mm.
// The agent on the other side of the clipboard reads the blob to know exactly
// what the user means; there is no paste-back-to-highlight round-trip (it has
// never earned its keep).
//
// The copper SVG is anonymous Gerber geometry, so identity comes from a sidecar:
// hardware/pcb/carrier/pick-data.ts distills pads (ref/pin/net + mm position),
// vias (net + layer hop), and traces (net + endpoint pads + polyline) into
// out/<board>.picks.json. We overlay an invisible hit-target per entity inside a
// group that reuses the SVG's own `translate(…) scale(1,-1)` Gerber-unit
// transform — so geometry at circuit-json (x,y) mm lands on its rendered copper
// (1 mm = 1000 SVG units). The browser does the hit-testing through PanZoom's
// CSS transform; on pointerup (not `click` — PanZoom captures the pointer) we
// read what's under the cursor. Targets are layered pad > via > trace, so where
// they overlap the most specific wins. A click that hits no target instead maps
// the cursor back to board mm through the pick layer's getScreenCTM (which folds
// in PanZoom's CSS transform), so a miss still yields a coordinate.

import { state } from "./state.js";

const SVGNS = "http://www.w3.org/2000/svg";
const LS_KEY = "pcb-pad-pick";
const PAD_HIT_R = 1100;   // pad hit radius, Gerber units (1.1 mm) — under the 2.54 mm pitch
const VIA_HIT_R = 650;    // via hit radius (0.65 mm)
const TRACE_HIT_W = 700;  // trace hit-band width (0.7 mm)
const HILITE = "#ffd400"; // selection colour (the edge picker's warm yellow)
// Overlaid UI that sits over the board — a click here is chrome, not a pick.
const CHROME_SEL = ".edge-panel, .pcb-view-toggle, .pan-zoom-minimap, .pcb-dims, .cv-filename";

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let ctx = null;       // { svgEl, layer, hilite, pads, vias, traces, source, wrapper }
let selection = null; // { kind:"pad"|"via"|"trace", index, data, source }
let panel = null;

// --- install / teardown (called by pcb.js around mountView) ---

export function installPadPicker(svgEl, info) {
  // Idempotent: a live re-render can re-install on a still-mounted SVG, so drop
  // any prior overlay first rather than stacking a second one.
  if (svgEl) svgEl.querySelectorAll(".pcb-pick-layer, .pcb-pick-hilite").forEach((n) => n.remove());
  const hasData = svgEl && info && ((info.pads && info.pads.length) || (info.vias && info.vias.length) || (info.traces && info.traces.length));
  if (!hasData) { ctx = null; return; }

  const geomG = svgEl.querySelector("g[transform]");
  const transform = (geomG && geomG.getAttribute("transform")) || "scale(1,-1)";

  const layer = el("g", { class: "pcb-pick-layer", transform });
  // Order matters: traces first (bottom), then vias, then pads (top), so where
  // targets overlap, elementFromPoint returns the most specific one.
  (info.traces || []).forEach((t, i) => {
    if (!t.points || t.points.length < 2) return;
    layer.appendChild(el("polyline", {
      class: "pcb-trace-hit", "data-i": i, "stroke-width": TRACE_HIT_W,
      points: t.points.map((p) => `${p[0] * 1000},${p[1] * 1000}`).join(" "),
    }));
  });
  (info.vias || []).forEach((v, i) => {
    layer.appendChild(el("circle", { class: "pcb-via-hit", "data-i": i, cx: v.x * 1000, cy: v.y * 1000, r: VIA_HIT_R }));
  });
  (info.pads || []).forEach((p, i) => {
    layer.appendChild(el("circle", { class: "pcb-pad-hit", "data-i": i, cx: p.x * 1000, cy: p.y * 1000, r: PAD_HIT_R }));
  });

  const hilite = el("g", { class: "pcb-pick-hilite", transform });
  svgEl.appendChild(layer);
  svgEl.appendChild(hilite);

  ctx = { svgEl, layer, hilite, pads: info.pads || [], vias: info.vias || [], traces: info.traces || [], source: info.source, wrapper: info.wrapper };
  applyEnabled();
  wireWrapper(info.wrapper);

  // Carry a live selection across a view swap (same board → same frame, so a
  // point's mm and an entity's index both still hold).
  if (selection && selection.source === info.source) {
    if (selection.kind === "point") { drawHighlight(selection); showPanel(selection); }
    else {
      const data = pick(selection.kind, selection.index);
      if (data) { selection.data = data; drawHighlight(selection); showPanel(selection); }
      else clearSelection();
    }
  } else {
    clearSelection();
  }
}

export function clearPadPicker() {
  clearSelection();
  ctx = null;
}

// Drop the current selection (highlight + panel) without tearing down the
// picker — used when the board re-renders underneath an open inspector.
export function clearPadSelection() {
  clearSelection();
}

function applyEnabled() {
  if (ctx) ctx.layer.classList.toggle("active", enabled);
}

// --- pointer wiring (on the wrapper — PanZoom's capture container) ---

function wireWrapper(wrapper) {
  if (!wrapper || wrapper._padPickWired) return;
  wrapper._padPickWired = true;
  let downX = 0, downY = 0;
  wrapper.addEventListener("pointerdown", (e) => { downX = e.clientX; downY = e.clientY; });
  wrapper.addEventListener("pointerup", (e) => {
    if (!enabled || !ctx) return;
    if (e.target && e.target.closest && e.target.closest("button")) return; // a control, not the board
    if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return;       // a pan, not a click
    const t = document.elementFromPoint(e.clientX, e.clientY);
    // An overlaid chrome pill (the inspector panel, view toggle, minimap, dims,
    // filename) sits over the board; clicking one is UI, not a board pick — leave
    // the current selection alone rather than dropping a marker under it.
    if (t && t.closest && t.closest(CHROME_SEL)) return;
    const cl = t && t.classList;
    if (cl && cl.contains("pcb-pad-hit")) select("pad", +t.getAttribute("data-i"));
    else if (cl && cl.contains("pcb-via-hit")) select("via", +t.getAttribute("data-i"));
    else if (cl && cl.contains("pcb-trace-hit")) select("trace", +t.getAttribute("data-i"));
    else selectPoint(e.clientX, e.clientY);
  });
}

// --- selection ---

function pick(kind, index) {
  if (!ctx) return null;
  const arr = kind === "pad" ? ctx.pads : kind === "via" ? ctx.vias : ctx.traces;
  return arr ? arr[index] : null;
}

function select(kind, index) {
  const data = pick(kind, index);
  if (!data) return;
  selection = { kind, index, data, source: ctx.source };
  drawHighlight(selection);
  showPanel(selection);
}

// Map a viewport (client) point to board mm. The pick layer carries the SVG's
// own Gerber-unit transform, so its getScreenCTM — which folds in PanZoom's CSS
// pan/zoom and the viewBox — turns a screen click straight into layer-local
// units (1 mm = 1000), no manual unwinding of the transform stack needed.
function clientToMm(clientX, clientY) {
  if (!ctx || !ctx.layer) return null;
  const m = ctx.layer.getScreenCTM();
  if (!m) return null;
  const p = new DOMPoint(clientX, clientY).matrixTransform(m.inverse());
  return { x: p.x / 1000, y: p.y / 1000 };
}

// A click that hit no entity: select the bare spot under the cursor, so an
// empty-board click reads out its (x, y) the same way a pad click reads its pad.
function selectPoint(clientX, clientY) {
  const mm = clientToMm(clientX, clientY);
  if (!mm) return;
  selection = { kind: "point", data: mm, source: ctx.source };
  drawHighlight(selection);
  showPanel(selection);
}

function clearSelection() {
  selection = null;
  if (ctx && ctx.hilite) while (ctx.hilite.firstChild) ctx.hilite.removeChild(ctx.hilite.firstChild);
  hidePanel();
}

function drawHighlight(sel) {
  if (!ctx) return;
  const g = ctx.hilite;
  while (g.firstChild) g.removeChild(g.firstChild);
  const d = sel.data;
  if (sel.kind === "point") {
    const x = d.x * 1000, y = d.y * 1000, arm = 1500, r = 520, sw = 150;
    g.appendChild(el("circle", { cx: x, cy: y, r, fill: "none", stroke: HILITE, "stroke-width": sw, opacity: "0.95" }));
    g.appendChild(el("line", { x1: x - arm, y1: y, x2: x + arm, y2: y, stroke: HILITE, "stroke-width": sw, "stroke-linecap": "round" }));
    g.appendChild(el("line", { x1: x, y1: y - arm, x2: x, y2: y + arm, stroke: HILITE, "stroke-width": sw, "stroke-linecap": "round" }));
    return;
  }
  if (sel.kind === "trace") {
    g.appendChild(el("polyline", {
      points: d.points.map((p) => `${p[0] * 1000},${p[1] * 1000}`).join(" "),
      fill: "none", stroke: HILITE, "stroke-width": (d.width ? d.width * 1000 : 200) + 260,
      "stroke-linecap": "round", "stroke-linejoin": "round", opacity: "0.85",
    }));
  } else {
    const size = sel.kind === "pad" ? (d.pad ? (d.pad * 1000) / 2 : 700) : (d.outer ? (d.outer * 1000) / 2 : 300);
    g.appendChild(el("circle", {
      cx: d.x * 1000, cy: d.y * 1000, r: size + 320,
      fill: "none", stroke: HILITE, "stroke-width": 180,
    }));
  }
}

// --- text (panel rows + copy blob) ---

function repoPath(source) {
  let lite = false;
  try { lite = localStorage.getItem("hsmEdition") === "lite"; } catch {}
  return (lite ? "pie-in-the-sky/lite" : "hardware") + "/" + source;
}
function fnum(n) {
  const s = Number(n).toFixed(3);
  return s === "-0.000" ? "0.000" : s;
}
function padLine(p) {
  const pin = p.pinNum != null ? `pin ${p.pinNum}` : "";
  const name = p.pin && String(p.pin) !== String(p.pinNum) ? p.pin : "";
  return [p.ref || "?", pin, name].filter(Boolean).join(" ");
}
function posLine(p) { return `x=${fnum(p.x)} y=${fnum(p.y)} mm`; }

// What a selection says — a title for the panel header and the copy blob shown
// verbatim in the panel's text box.
function describe(sel) {
  const d = sel.data;
  const fileLine = ctx && ctx.source ? `file: ${repoPath(ctx.source)}` : null;
  if (sel.kind === "point") {
    return {
      title: "Point",
      blob: [fileLine, `pos: ${posLine(d)}`].filter(Boolean).join("\n"),
    };
  }
  if (sel.kind === "pad") {
    return {
      title: "Pad",
      blob: [fileLine, `pad: ${padLine(d)}`, `net: ${d.net || "(none)"}`, `pos: ${posLine(d)}`].filter(Boolean).join("\n"),
    };
  }
  if (sel.kind === "via") {
    const layers = d.fromLayer && d.toLayer ? `${d.fromLayer} ↔ ${d.toLayer}` : "";
    return {
      title: "Via",
      blob: [fileLine, `via: net ${d.net || "(none)"}${layers ? " · " + layers : ""}`, `pos: ${posLine(d)}`].filter(Boolean).join("\n"),
    };
  }
  const route = d.from && d.to ? `${d.from} → ${d.to}` : (d.from || d.to || "");
  return {
    title: "Trace",
    blob: [fileLine, `trace: net ${d.net || "(none)"}`, route ? `route: ${route}` : null].filter(Boolean).join("\n"),
  };
}

// --- panel (reuses .edge-panel styles; rows are rebuilt per selection) ---

function buildPanel() {
  panel = el2("div", "edge-panel");
  const head = el2("div", "edge-panel-head");
  const title = el2("span", "edge-panel-title");
  const fileEl = el2("span", "edge-panel-file");
  const close = el2("button", "edge-panel-close");
  close.type = "button";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", () => clearSelection());
  head.append(title, fileEl, close);
  const text = el2("textarea", "edge-panel-text");
  text.readOnly = true;
  text.spellcheck = false;
  const copy = el2("button", "edge-panel-all");
  copy.type = "button";
  copy.textContent = "Copy";
  copy.addEventListener("click", () => copyText(panel._text.value, copy));
  panel.append(head, text, copy);
  panel._title = title; panel._fileEl = fileEl; panel._text = text;
}

function showPanel(sel) {
  if (!panel) buildPanel();
  if (ctx && ctx.wrapper && panel.parentElement !== ctx.wrapper) ctx.wrapper.appendChild(panel);
  const { title, blob } = describe(sel);
  panel._title.textContent = title;
  panel._fileEl.textContent = ctx && ctx.source ? ctx.source.split("/").pop().replace(/\.tsx$/, "") : "";
  panel._fileEl.title = ctx && ctx.source ? repoPath(ctx.source) : "";
  panel._text.value = blob;
  panel._text.rows = Math.min(12, Math.max(2, blob.split("\n").length));
  panel.classList.add("show");
}
function hidePanel() { if (panel) panel.classList.remove("show"); }

function copyText(text, btn) {
  const done = () => {
    const prev = btn.textContent;
    btn.textContent = "✓";
    btn.classList.add("edge-copied");
    setTimeout(() => { btn.textContent = prev; btn.classList.remove("edge-copied"); }, 1100);
  };
  try {
    navigator.clipboard.writeText(text).then(done, () => fallbackCopy(text, done));
  } catch { fallbackCopy(text, done); }
}
function fallbackCopy(text, done) {
  const ta = document.createElement("textarea");
  ta.value = text;
  ta.style.position = "fixed";
  ta.style.opacity = "0";
  document.body.appendChild(ta);
  ta.select();
  try { document.execCommand("copy"); done(); } catch {}
  document.body.removeChild(ta);
}

// --- small element helpers ---

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

// --- public toggle API ---

export function setPadPickEnabled(on) {
  enabled = !!on;
  try { localStorage.setItem(LS_KEY, enabled ? "1" : "0"); } catch {}
  applyEnabled();
  if (!enabled) clearSelection();
}
export function isPadPickEnabled() { return enabled; }

export function makePadPickToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "pad-pick-toggle";
  function refresh() {
    btn.textContent = enabled ? "Inspect: on" : "Inspect: off";
    btn.classList.toggle("off", !enabled);
  }
  btn.addEventListener("click", (e) => {
    e.stopPropagation();
    setPadPickEnabled(!enabled);
    refresh();
  });
  refresh();
  return btn;
}
