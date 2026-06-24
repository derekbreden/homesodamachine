// Board inspector for the PCB viewer — the 2D counterpart to the STEP edge
// picker. A toggle (persisted per-browser) turns the board into a clickable
// surface: click a pad / through-hole, a via, or a trace to select it and copy
// a text blob naming it. The agent on the other side of the clipboard reads the
// blob to know exactly what the user means; there is no paste-back-to-highlight
// round-trip (it has never earned its keep).
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
// they overlap the most specific wins.

import { state } from "./state.js";

const SVGNS = "http://www.w3.org/2000/svg";
const LS_KEY = "pcb-pad-pick";
const PAD_HIT_R = 1100;   // pad hit radius, Gerber units (1.1 mm) — under the 2.54 mm pitch
const VIA_HIT_R = 650;    // via hit radius (0.65 mm)
const TRACE_HIT_W = 700;  // trace hit-band width (0.7 mm)
const HILITE = "#ffd400"; // selection colour (the edge picker's warm yellow)

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

let ctx = null;       // { svgEl, layer, hilite, pads, vias, traces, source, wrapper }
let selection = null; // { kind:"pad"|"via"|"trace", index, data, source }
let panel = null;

// --- install / teardown (called by pcb.js around mountView) ---

export function installPadPicker(svgEl, info) {
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

  // Carry a live selection across a view swap (same board → same indices).
  if (selection && selection.source === info.source) {
    const data = pick(selection.kind, selection.index);
    if (data) { selection.data = data; drawHighlight(selection); showPanel(selection); }
    else clearSelection();
  } else {
    clearSelection();
  }
}

export function clearPadPicker() {
  clearSelection();
  ctx = null;
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
    const cl = t && t.classList;
    if (cl && cl.contains("pcb-pad-hit")) select("pad", +t.getAttribute("data-i"));
    else if (cl && cl.contains("pcb-via-hit")) select("via", +t.getAttribute("data-i"));
    else if (cl && cl.contains("pcb-trace-hit")) select("trace", +t.getAttribute("data-i"));
    else clearSelection();
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

// One source of truth for what a selection says, in the panel and the copy blob.
function describe(sel) {
  const d = sel.data;
  const fileLine = ctx && ctx.source ? `file: ${repoPath(ctx.source)}` : null;
  if (sel.kind === "pad") {
    return {
      title: "Pad",
      rows: [["Pad", padLine(d)], ["Net", d.net || "(none)"], ["Pos", posLine(d)]],
      blob: [fileLine, `pad: ${padLine(d)}`, `net: ${d.net || "(none)"}`, `pos: ${posLine(d)}`].filter(Boolean).join("\n"),
    };
  }
  if (sel.kind === "via") {
    const layers = d.fromLayer && d.toLayer ? `${d.fromLayer} ↔ ${d.toLayer}` : "";
    return {
      title: "Via",
      rows: [["Net", d.net || "(none)"], ["Layers", layers], ["Pos", posLine(d)]],
      blob: [fileLine, `via: net ${d.net || "(none)"}${layers ? " · " + layers : ""}`, `pos: ${posLine(d)}`].filter(Boolean).join("\n"),
    };
  }
  const route = d.from && d.to ? `${d.from} → ${d.to}` : (d.from || d.to || "");
  return {
    title: "Trace",
    rows: [["Net", d.net || "(none)"], ["From", d.from || "—"], ["To", d.to || "—"]],
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
  const rowsHost = el2("div", "edge-rows");
  const all = el2("button", "edge-panel-all");
  all.type = "button";
  all.textContent = "Copy all";
  panel.append(head, rowsHost, all);
  panel._title = title; panel._fileEl = fileEl; panel._rowsHost = rowsHost; panel._allBtn = all;
}

function mkRow(label, value) {
  const row = el2("div", "edge-row");
  const lab = el2("span", "edge-row-label"); lab.textContent = label;
  const val = el2("span", "edge-row-val"); val.textContent = value;
  const copy = el2("button", "edge-row-copy"); copy.type = "button"; copy.textContent = "Copy";
  row.append(lab, val, copy);
  const doCopy = () => copyText(val.textContent, copy);
  val.addEventListener("click", doCopy);
  copy.addEventListener("click", doCopy);
  return row;
}

function showPanel(sel) {
  if (!panel) buildPanel();
  if (ctx && ctx.wrapper && panel.parentElement !== ctx.wrapper) ctx.wrapper.appendChild(panel);
  const { title, rows, blob } = describe(sel);
  panel._title.textContent = title;
  panel._fileEl.textContent = ctx && ctx.source ? ctx.source.split("/").pop().replace(/\.tsx$/, "") : "";
  panel._fileEl.title = ctx && ctx.source ? repoPath(ctx.source) : "";
  panel._rowsHost.textContent = "";
  for (const [label, value] of rows) {
    if (value == null || value === "") continue;
    panel._rowsHost.appendChild(mkRow(label, value));
  }
  panel._allBtn.onclick = () => copyText(blob, panel._allBtn);
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
