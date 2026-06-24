// Pad picker for the PCB viewer — the 2D counterpart to the STEP edge picker.
// A toggle (persisted per-browser) turns the board into a clickable surface:
// click a pad / through-hole to select it and copy a text blob naming it
// (component ref, pin, net, board position). The agent on the other side of
// the clipboard reads the blob to know exactly which pad the user means.
//
// The copper SVG is anonymous Gerber geometry, so identity comes from a
// sidecar: hardware/pcb/carrier/pick-data.ts distills each pad's ref/pin/net
// and millimetre position into out/<board>.picks.json. We overlay an invisible
// hit-circle per pad, inside a group that reuses the SVG's own
// `translate(…) scale(1,-1)` Gerber-unit transform — so a pad at circuit-json
// (x,y) mm lands exactly on its rendered copper (1 mm = 1000 SVG units). The
// browser does the hit-testing through PanZoom's CSS transform; we only listen
// for a click on a hit-circle (delegated) and read its pad index.

import { state } from "./state.js";

const LS_KEY = "pcb-pad-pick";
const HIT_R = 1100;       // hit-circle radius in Gerber units (1.1 mm); just
                          // under the 2.54 mm pad pitch so neighbours don't overlap
const HILITE = "#ffd400"; // selected-pad ring (matches the edge picker's warm yellow)

let enabled = (() => {
  try { return localStorage.getItem(LS_KEY) === "1"; } catch { return false; }
})();

// Live install: the freshly mounted SVG, its hit layer + highlight group, the
// board's pads, and the board source. Rebuilt on every view swap (mountView
// re-parses the SVG); the selection survives swaps so toggling Top/Bottom/Overlay
// keeps the pad highlighted.
let ctx = null;
let selection = null; // { index, pad, source }
let panel = null, panelRows = null;

// --- install / teardown (called by pcb.js around mountView) ---

// Build the hit layer + highlight group inside `svgEl` and wire the delegated
// click. `info` = { pads, source, wrapper }. Safe to call with no pads (older
// boards lacking a picks sidecar) — it simply installs nothing.
export function installPadPicker(svgEl, info) {
  if (!svgEl || !info || !Array.isArray(info.pads) || !info.pads.length) {
    ctx = null;
    return;
  }
  // Reuse the geometry group's exact transform so picks share its frame.
  const geomG = svgEl.querySelector("g[transform]");
  const transform = (geomG && geomG.getAttribute("transform")) || "scale(1,-1)";

  const layer = document.createElementNS("http://www.w3.org/2000/svg", "g");
  layer.setAttribute("class", "pcb-pick-layer");
  layer.setAttribute("transform", transform);
  for (let i = 0; i < info.pads.length; i++) {
    const p = info.pads[i];
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("class", "pcb-pad-hit");
    c.setAttribute("cx", p.x * 1000);
    c.setAttribute("cy", p.y * 1000);
    c.setAttribute("r", HIT_R);
    c.setAttribute("data-i", String(i));
    layer.appendChild(c);
  }
  const hilite = document.createElementNS("http://www.w3.org/2000/svg", "g");
  hilite.setAttribute("class", "pcb-pick-hilite");
  hilite.setAttribute("transform", transform);

  // On top of the copper so hits land and the ring reads over traces.
  svgEl.appendChild(layer);
  svgEl.appendChild(hilite);

  ctx = { svgEl, layer, hilite, pads: info.pads, source: info.source, wrapper: info.wrapper };
  applyEnabled();
  wireWrapper(info.wrapper);

  // Carry a live selection across a view swap (same board → same pad indices).
  if (selection && selection.source === info.source && selection.index < info.pads.length) {
    drawHighlight(info.pads[selection.index]);
    showPanel(info.pads[selection.index]);
  } else {
    clearSelection();
  }
}

// Full teardown when the board modal closes.
export function clearPadPicker() {
  clearSelection();
  ctx = null;
}

function applyEnabled() {
  if (!ctx) return;
  ctx.layer.classList.toggle("active", enabled);
}

// --- selection ---

// Selection runs off pointerdown/up on the wrapper — PanZoom captures the
// pointer to the wrapper on pointerdown (pan-zoom.js), so a real click never
// reaches the SVG as a `click` event. We record the down point and, on an up
// that didn't travel (a click, not a pan), hit-test the cursor: a pad's
// hit-circle selects it; empty board clears. PanZoom's own handlers don't stop
// propagation, so ours coexist. Wired once per board (the wrapper is reused
// across Top/Bottom/Overlay swaps).
function wireWrapper(wrapper) {
  if (!wrapper || wrapper._padPickWired) return;
  wrapper._padPickWired = true;
  let downX = 0, downY = 0;
  wrapper.addEventListener("pointerdown", (e) => { downX = e.clientX; downY = e.clientY; });
  wrapper.addEventListener("pointerup", (e) => {
    if (!enabled || !ctx) return;
    if (e.target && e.target.closest && e.target.closest("button")) return; // a control, not the board
    if (Math.hypot(e.clientX - downX, e.clientY - downY) > 6) return;       // a pan, not a click
    const el = document.elementFromPoint(e.clientX, e.clientY);
    if (el && el.classList && el.classList.contains("pcb-pad-hit")) {
      selectPad(+el.getAttribute("data-i"));
    } else {
      clearSelection();
    }
  });
}

function selectPad(i) {
  if (!ctx || !ctx.pads[i]) return;
  const pad = ctx.pads[i];
  selection = { index: i, pad, source: ctx.source };
  drawHighlight(pad);
  showPanel(pad);
}

function clearSelection() {
  selection = null;
  if (ctx && ctx.hilite) while (ctx.hilite.firstChild) ctx.hilite.removeChild(ctx.hilite.firstChild);
  hidePanel();
}

function drawHighlight(pad) {
  if (!ctx) return;
  const g = ctx.hilite;
  while (g.firstChild) g.removeChild(g.firstChild);
  const padR = (pad.pad ? (pad.pad * 1000) / 2 : 700);
  const ring = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  ring.setAttribute("cx", pad.x * 1000);
  ring.setAttribute("cy", pad.y * 1000);
  ring.setAttribute("r", padR + 350);
  ring.setAttribute("fill", "none");
  ring.setAttribute("stroke", HILITE);
  ring.setAttribute("stroke-width", "180");
  g.appendChild(ring);
}

// --- text formatting (the copy blob the agent reads) ---

function repoPath(source) {
  let lite = false;
  try { lite = localStorage.getItem("hsmEdition") === "lite"; } catch {}
  return (lite ? "pie-in-the-sky/lite" : "hardware") + "/" + source;
}
function fnum(n) {
  const s = Number(n).toFixed(3);
  return s === "-0.000" ? "0.000" : s;
}
function padLine(pad) {
  const pin = pad.pinNum != null ? `pin ${pad.pinNum}` : "";
  const name = pad.pin && String(pad.pin) !== String(pad.pinNum) ? pad.pin : "";
  return [pad.ref || "?", pin, name].filter(Boolean).join(" ");
}
function posLine(pad) { return `x=${fnum(pad.x)} y=${fnum(pad.y)} mm`; }

function allText(pad) {
  const lines = [];
  if (ctx && ctx.source) lines.push(`file: ${repoPath(ctx.source)}`);
  lines.push(`pad: ${padLine(pad)}`);
  lines.push(`net: ${pad.net || "(none)"}`);
  lines.push(`pos: ${posLine(pad)}`);
  return lines.join("\n");
}

// --- panel (reuses .edge-panel styles) ---

function buildPanel() {
  panel = document.createElement("div");
  panel.className = "edge-panel";

  const head = document.createElement("div");
  head.className = "edge-panel-head";
  const title = document.createElement("span");
  title.className = "edge-panel-title";
  title.textContent = "Pad";
  const fileEl = document.createElement("span");
  fileEl.className = "edge-panel-file";
  const close = document.createElement("button");
  close.type = "button";
  close.className = "edge-panel-close";
  close.textContent = "×";
  close.title = "Clear selection";
  close.addEventListener("click", () => clearSelection());
  head.appendChild(title);
  head.appendChild(fileEl);
  head.appendChild(close);
  panel.appendChild(head);
  panel._fileEl = fileEl;

  const mkRow = (label) => {
    const row = document.createElement("div");
    row.className = "edge-row";
    const lab = document.createElement("span");
    lab.className = "edge-row-label";
    lab.textContent = label;
    const val = document.createElement("span");
    val.className = "edge-row-val";
    const copy = document.createElement("button");
    copy.type = "button";
    copy.className = "edge-row-copy";
    copy.textContent = "Copy";
    row.appendChild(lab);
    row.appendChild(val);
    row.appendChild(copy);
    panel.appendChild(row);
    const doCopy = () => copyText(val.textContent, copy);
    val.addEventListener("click", doCopy);
    copy.addEventListener("click", doCopy);
    return { row, lab, val, copy };
  };

  panelRows = { pad: mkRow("Pad"), net: mkRow("Net"), pos: mkRow("Pos") };

  const all = document.createElement("button");
  all.type = "button";
  all.className = "edge-panel-all";
  all.textContent = "Copy all";
  all.addEventListener("click", () => { if (selection) copyText(allText(selection.pad), all); });
  panel.appendChild(all);
}

function showPanel(pad) {
  if (!panel) buildPanel();
  if (ctx && ctx.wrapper && panel.parentElement !== ctx.wrapper) ctx.wrapper.appendChild(panel);
  panelRows.pad.val.textContent = padLine(pad);
  panelRows.net.val.textContent = pad.net || "(none)";
  panelRows.pos.val.textContent = posLine(pad);
  panel._fileEl.textContent = ctx && ctx.source ? ctx.source.split("/").pop().replace(/\.tsx$/, "") : "";
  panel._fileEl.title = ctx && ctx.source ? repoPath(ctx.source) : "";
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

// --- public toggle API (mirrors the edge picker) ---

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
    btn.textContent = enabled ? "Select pad: on" : "Select pad: off";
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
