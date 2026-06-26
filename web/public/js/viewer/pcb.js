// PCB board module. A board carries three rendered copper views — Top (front),
// Bottom (back, seen through the board), and Overlay (both, warm front / cool
// back) — produced by hardware/pcb/carrier/render-board.ts straight from the
// fabrication Gerbers, so the lines have the real widths the board is made with.
//
// Modeled on drawings.js: a 2D SVG opened in ContentViewer with PanZoom, with
// per-board transform persistence and a swap-in-place on re-render. What it adds is the
// Top / Bottom / Overlay toggle. The three views share one identical viewBox, so
// switching swaps the SVG while keeping the user's exact pan/zoom — the board
// holds still under the toggle.

import { state } from "./state.js";
import { makeResetButton, makeMinimap } from "./pan-zoom-extras.js";
import { installPadPicker, clearPadPicker, clearPadSelection, makePadPickToggle } from "./pcb-pick.js";

const VIEWS = ["top", "bottom", "overlay"];
const VIEW_LABEL = { top: "Top", bottom: "Bottom", overlay: "Overlay" };

// Fit insets (px) for the board PanZoom: reserve the bands occupied by the
// overlaid chrome (view toggle / minimap / filename / close on top; readout /
// pad-pick / reset on bottom) so the default fit — and the zoom-out floor,
// which equals the fit scale — keeps the whole board clear of them. One shared
// object: PanZoom and the minimap read it live, and onOpen measures the real
// chrome into it once the modal is laid out. Singleton modal ⇒ one is enough.
const pcbFitInset = { top: 0, right: 0, bottom: 0, left: 0 };

// Measure the chrome overlaying the board and return the band heights to keep
// clear, top and bottom. Queried live (positions shift with safe-area insets
// and the minimap's aspect-driven height), capped so a tiny window still
// leaves the board most of the height.
function measureChromeInset(wrapper) {
  const wr = wrapper.getBoundingClientRect();
  if (!wr.width || !wr.height) return null;
  const gap = 12;
  const topSel = [".pcb-view-toggle", ".pan-zoom-minimap", ".cv-filename", ".cv-close"];
  const botSel = [".pcb-dims", ".pcb-wrapper > .pad-pick-toggle", ".reset-view"];
  let top = 0, bottom = 0;
  for (const sel of topSel)
    for (const el of document.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect();
      if (r.height) top = Math.max(top, r.bottom - wr.top);
    }
  for (const sel of botSel)
    for (const el of document.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect();
      if (r.height) bottom = Math.max(bottom, wr.bottom - r.top);
    }
  const cap = wr.height * 0.45;
  return {
    top: Math.min(top > 0 ? top + gap : 0, cap),
    right: 0,
    bottom: Math.min(bottom > 0 ? bottom + gap : 0, cap),
    left: 0,
  };
}

function pcbTransformKey(source) { return `pcb-transform:${source}`; }
function pcbViewKey(source) { return `pcb-view:${source}`; }

export function pcbSaveTransform(source, t) {
  try { localStorage.setItem(pcbTransformKey(source), JSON.stringify(t)); } catch {}
}
export function pcbLoadTransform(source) {
  try {
    const raw = localStorage.getItem(pcbTransformKey(source));
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (typeof s.scale !== "number") return null;
    return s;
  } catch { return null; }
}
function pcbSaveView(source, view) {
  try { localStorage.setItem(pcbViewKey(source), view); } catch {}
}
function pcbLoadView(source) {
  try {
    const v = localStorage.getItem(pcbViewKey(source));
    return VIEWS.includes(v) ? v : null;
  } catch { return null; }
}

function boardForSource(source) {
  return (state.pcbBoards || []).find((b) => b.source === source) || null;
}

// Parse an SVG string into a live SVGSVGElement. PanZoom reads an SVG's natural
// size from its viewBox (here in Gerber units, e.g. 150050), and fits/zooms by
// CSS-transforming the element — so the element's rendered px size must MATCH
// the viewBox units, or fit math (natural ÷ rendered) is off by the unit ratio.
// We therefore set width/height to the viewBox numbers. That makes the element
// nominally ~150000px, so .pcb-svg is positioned absolutely (viewer.css) and
// clipped by the overflow-hidden wrapper until PanZoom's fit scales it down —
// otherwise the unscaled element would blow out the page on first paint.
function parseSvgString(svgText) {
  const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
  const svgEl = doc.querySelector("svg");
  if (!svgEl) throw new Error("Board view has no <svg> element");
  const adopted = document.importNode(svgEl, true);
  const vb = adopted.viewBox?.baseVal;
  if (vb && vb.width && vb.height) {
    adopted.setAttribute("width", vb.width);
    adopted.setAttribute("height", vb.height);
  }
  adopted.style.display = "block";
  adopted.style.maxWidth = "none";
  adopted.style.maxHeight = "none";
  adopted.classList.add("pcb-svg");
  return adopted;
}

function contentUrl(path) { return `/api/pcb-content/${path}`; }
function picksUrl(path) { return `/api/pcb-picks/${path}`; }

// Fetch a board's pad-picker data (pads + identity), or null when the board
// has no picks sidecar / the fetch fails — the picker then just doesn't arm.
async function fetchPicks(board) {
  if (!board || !board.picks) return null;
  try {
    const r = await fetch(picksUrl(board.picks));
    return r.ok ? await r.json() : null;
  } catch { return null; }
}

// Fetch all three view SVGs for a board. Returns { top, bottom, overlay } of
// SVG text, or null if any fail.
async function fetchViews(board) {
  try {
    const [top, bottom, overlay] = await Promise.all(
      VIEWS.map((v) => fetch(contentUrl(board[v])).then((r) => (r.ok ? r.text() : null))),
    );
    if (!top || !bottom || !overlay) return null;
    return { top, bottom, overlay };
  } catch { return null; }
}

function shortName(source) {
  const parts = source.split("/");
  return parts.pop().replace(/\.tsx$/, "");
}

// Board outer dimensions readout. Authoritative source is the board element's
// width/height, carried in picks.json (pick-data.ts); when a board has no picks
// sidecar we fall back to the mounted SVG's viewBox (Gerber units ÷ unitsPerMm),
// which is the rendered extent (a hair larger than the cut outline). Returns a
// "134 × 100 mm" string, or null if neither source is available.
function fmtMm(n) {
  return (Math.round(n * 10) / 10).toString();
}
function boardDimsText(picks, wrapper) {
  const s = picks && picks.size;
  if (s && s.width && s.height) return `${fmtMm(s.width)} × ${fmtMm(s.height)} mm`;
  const svg = wrapper && wrapper.querySelector("svg.pcb-svg");
  const vb = svg && svg.viewBox && svg.viewBox.baseVal;
  const per = (picks && picks.unitsPerMm) || 1000;
  if (vb && vb.width && vb.height) return `${fmtMm(vb.width / per)} × ${fmtMm(vb.height / per)} mm`;
  return null;
}
// Create or update the bottom-centre dimensions chip in `wrapper`.
function updateDimsChip(wrapper, picks) {
  if (!wrapper) return;
  const text = boardDimsText(picks, wrapper);
  let el = wrapper.querySelector(".pcb-dims");
  if (!text) { if (el) el.remove(); return; }
  if (!el) {
    el = document.createElement("div");
    el.className = "pcb-dims";
    wrapper.appendChild(el);
  }
  el.textContent = text;
}

// --- Thumbnail ---
// The card thumbnail is the Overlay view SVG, scaled by its container. Cached as
// a string (matches drawings/mermaid; keeps the grid cache shape uniform).
export async function renderPcbThumbnail(source) {
  if (state.pcbThumbCache.has(source)) return state.pcbThumbCache.get(source);
  const board = boardForSource(source);
  if (!board) return null;
  try {
    const resp = await fetch(contentUrl(board.overlay));
    if (!resp.ok) return null;
    const svgText = await resp.text();
    state.pcbThumbCache.set(source, svgText);
    return svgText;
  } catch { return null; }
}

// Build the Top / Bottom / Overlay segmented control. onSelect(view) swaps the
// shown SVG; the buttons reflect state.currentPcbView.
function makeViewToggle(onSelect) {
  const wrap = document.createElement("div");
  wrap.className = "pcb-view-toggle";
  for (const v of VIEWS) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pcb-view-btn";
    btn.dataset.view = v;
    btn.textContent = VIEW_LABEL[v];
    btn.addEventListener("click", (e) => { e.stopPropagation(); onSelect(v); });
    wrap.appendChild(btn);
  }
  return wrap;
}
function syncToggle(toggleEl, view) {
  for (const btn of toggleEl.querySelectorAll(".pcb-view-btn")) {
    btn.classList.toggle("active", btn.dataset.view === view);
  }
}

// Mount `view` into the open board's wrapper, re-wrapping PanZoom while keeping
// the current transform (the three views share a viewBox, so the board doesn't
// move). `preserve` carries the transform across a swap; on first mount we fit.
function mountView(view, preserve) {
  const wrapper = state.currentPcbWrapper;
  if (!wrapper) return;
  const svgText = state.currentPcbViews?.[view];
  if (!svgText) return;

  let svgEl;
  try {
    svgEl = parseSvgString(svgText);
  } catch (err) {
    wrapper.querySelector(".pcb-svg")?.remove();
    return;
  }

  const prev = preserve && state.currentPcbPz ? state.currentPcbPz.getTransform() : null;
  try { state.currentPcbPz?.destroy(); } catch {}
  try { state.currentPcbMinimap?.destroy(); } catch {}
  wrapper.querySelector(".pcb-svg")?.remove();
  // Insert the SVG as the first child so the toggle / minimap / reset overlay it.
  wrapper.insertBefore(svgEl, wrapper.firstChild);

  const source = state.currentPcbSource;
  const minimap = makeMinimap(svgEl, wrapper, pcbFitInset);
  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: !prev,
    // The board's natural size is in Gerber units (~150000), so the fit scale is
    // tiny (~0.006). Drop PanZoom's default minScale floor (0.1) well below it
    // or the fit clamps and the board renders far too zoomed-in.
    minScale: 0.0001,
    // Reserve the chrome bands so the fit (and the zoom-out floor) show the
    // whole board between them. Measured into pcbFitInset in onOpen; shared by
    // reference so swaps + the minimap stay consistent.
    fitInset: pcbFitInset,
    onTransformChange: (t) => { if (source) pcbSaveTransform(source, t); },
    onTransformLive: (t) => minimap.update(t),
  });
  wrapper.appendChild(minimap.el);
  wrapper.appendChild(makeResetButton(pz, { transformKey: source ? pcbTransformKey(source) : null }));

  state.currentPcbPz = pz;
  state.currentPcbMinimap = minimap;
  state.currentPcbView = view;
  if (prev) pz.setTransform(prev);
  if (source) pcbSaveView(source, view);
  if (state.currentPcbToggle) syncToggle(state.currentPcbToggle, view);

  // Re-arm the board inspector on the freshly mounted SVG (the three views share
  // a frame, so a live selection carries across the swap).
  const picks = state.currentPcbPicks;
  installPadPicker(svgEl, picks ? { pads: picks.pads, vias: picks.vias, traces: picks.traces, source, wrapper } : null);
}

export async function openPcbDetail(source, pushHistory = true) {
  // Set currentDetail BEFORE touching location.hash (popstate may fire
  // synchronously under Puppeteer; its handler dispatches on currentDetail).
  state.currentDetail = { type: "pcb", file: source };
  // Start from no inset; onOpen measures the real chrome once it's laid out.
  pcbFitInset.top = pcbFitInset.bottom = pcbFitInset.left = pcbFitInset.right = 0;
  if (pushHistory) location.hash = "pcb:" + encodeURIComponent(source);

  let board = boardForSource(source);
  if (!board) {
    // Deep-link (or any call) before the board list loaded: fetch it and retry,
    // so we open the real board rather than the unavailable-fallback.
    try {
      const list = await fetch("/api/pcb").then((r) => (r.ok ? r.json() : null));
      if (list) { state.pcbBoards = list; board = boardForSource(source); }
    } catch {}
  }
  const [views, picks] = board
    ? await Promise.all([fetchViews(board), fetchPicks(board)])
    : [null, null];

  const wrapper = document.createElement("div");
  wrapper.className = "pcb-wrapper";

  if (!views) {
    wrapper.innerHTML = `<pre style="color:#c44;padding:20px;font-size:13px;">Board views unavailable: ${shortName(source)}</pre>`;
    ContentViewer.open({
      content: wrapper,
      filename: shortName(source),
      onClose: () => { clearPcbState(); if (location.hash) history.back(); },
    });
    return;
  }

  const view = pcbLoadView(source) || "overlay";
  const toggle = makeViewToggle((v) => { if (v !== state.currentPcbView) mountView(v, true); });
  wrapper.appendChild(toggle);
  if (picks && picks.pads && picks.pads.length) wrapper.appendChild(makePadPickToggle());

  // Publish the open-modal context, then build the first view synchronously —
  // before ContentViewer.open (the proven mermaid/drawings order). Mounting
  // here rather than in onOpen keeps the SVG + PanZoom out of reach of the
  // singleton-close path, which fires the prior modal's onClose during open.
  state.currentPcbSource = source;
  state.currentPcbViews = views;
  state.currentPcbPicks = picks;
  state.currentPcbWrapper = wrapper;
  state.currentPcbToggle = toggle;
  state.currentPcbView = view;
  mountView(view, false);
  updateDimsChip(wrapper, picks);
  // Local handles for onOpen/onClose so a later modal reassigning the shared
  // state can't strand this modal's fit or teardown.
  const pz = state.currentPcbPz;
  const minimap = state.currentPcbMinimap;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(source),
    onOpen: () => {
      // The wrapper has a real layout box only after showModal. Size the
      // minimap first (its box is aspect-driven and otherwise still at its
      // pre-layout max height), then measure the settled chrome bands into the
      // shared inset and fit so the whole board lands clear of them. A saved
      // transform, if any, overrides the fit.
      try {
        minimap?.update();
        const m = measureChromeInset(wrapper);
        if (m) Object.assign(pcbFitInset, m);
        pz?.fit();
      } catch {}
      const saved = pcbLoadTransform(source);
      if (saved && pz) pz.setTransform(saved);
      minimap?.update();
    },
    onClose: () => {
      // Only tear down shared state if it still belongs to this modal; a newer
      // board opened over this one already owns it. Always destroy this modal's
      // own PanZoom either way.
      if (state.currentPcbWrapper === wrapper) {
        clearPcbState();
      } else {
        try { pz?.destroy(); } catch {}
        try { minimap?.destroy(); } catch {}
      }
      if (location.hash) history.back();
    },
  });
}

function clearPcbState() {
  try { state.currentPcbPz?.destroy(); } catch {}
  try { state.currentPcbMinimap?.destroy(); } catch {}
  try { clearPadPicker(); } catch {}
  state.currentDetail = null;
  state.currentPcbSource = null;
  state.currentPcbViews = null;
  state.currentPcbPicks = null;
  state.currentPcbWrapper = null;
  state.currentPcbToggle = null;
  state.currentPcbPz = null;
  state.currentPcbMinimap = null;
  state.currentPcbView = null;
}

export function closePcbDetail(pushHistory = true) {
  if (!ContentViewer.isOpen()) { clearPcbState(); return; }
  if (!pushHistory) {
    const pz = state.currentPcbPz;
    clearPcbState();
    try { pz?.destroy(); } catch {}
    ContentViewer.close();
    return;
  }
  ContentViewer.close();
}

export async function refetchOpenPcb(source) {
  const board = boardForSource(source);
  if (!board) return;
  const [views, picks] = await Promise.all([fetchViews(board), fetchPicks(board)]);
  if (!views) return;
  const prevActive = state.currentPcbViews?.[state.currentPcbView];
  state.currentPcbViews = views;
  state.currentPcbPicks = picks;
  updateDimsChip(state.currentPcbWrapper, picks);
  // The board re-rendered underneath us: drop any stale selection (its geometry
  // may be gone) so the inspector doesn't keep a dead highlight, then rebuild
  // the hit targets from the fresh picks so they line up with the new copper.
  clearPadSelection();
  if (views[state.currentPcbView] !== prevActive) {
    mountView(state.currentPcbView, true);
  } else {
    const svgEl = state.currentPcbWrapper?.querySelector(".pcb-svg");
    if (svgEl) installPadPicker(svgEl, picks ? { pads: picks.pads, vias: picks.vias, traces: picks.traces, source, wrapper: state.currentPcbWrapper } : null);
  }
}
