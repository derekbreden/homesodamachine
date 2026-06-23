// PCB board module. A board carries three rendered copper views — Top (front),
// Bottom (back, seen through the board), and Overlay (both, warm front / cool
// back) — produced by hardware/pcb/carrier/render-board.ts straight from the
// fabrication Gerbers, so the lines have the real widths the board is made with.
//
// Modeled on drawings.js: a 2D SVG opened in ContentViewer with PanZoom, with
// per-board transform persistence and an SSE-driven swap. What it adds is the
// Top / Bottom / Overlay toggle. The three views share one identical viewBox, so
// switching swaps the SVG while keeping the user's exact pan/zoom — the board
// holds still under the toggle.

import { state } from "./state.js";
import { makeResetButton, makeMinimap } from "./pan-zoom-extras.js";

const VIEWS = ["top", "bottom", "overlay"];
const VIEW_LABEL = { top: "Top", bottom: "Bottom", overlay: "Overlay" };

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

// Parse an SVG string into a live SVGSVGElement. The render carries width/height
// in mm and a matching viewBox; we re-assert width/height from the viewBox so
// PanZoom can measure the natural size for its initial fit.
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

// --- Thumbnail ---
// The card thumbnail is the Top view SVG, scaled by its container. Cached as a
// string (matches drawings/mermaid; keeps the grid cache shape uniform).
export async function renderPcbThumbnail(source) {
  if (state.pcbThumbCache.has(source)) return state.pcbThumbCache.get(source);
  const board = boardForSource(source);
  if (!board) return null;
  try {
    const resp = await fetch(contentUrl(board.top));
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
  const minimap = makeMinimap(svgEl, wrapper);
  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: !prev,
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
}

export async function openPcbDetail(source, pushHistory = true) {
  // Set currentDetail BEFORE touching location.hash (popstate may fire
  // synchronously under Puppeteer; its handler dispatches on currentDetail).
  state.currentDetail = { type: "pcb", file: source };
  if (pushHistory) location.hash = "pcb:" + encodeURIComponent(source);

  const board = boardForSource(source);
  const views = board ? await fetchViews(board) : null;

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

  const view = pcbLoadView(source) || "top";
  const toggle = makeViewToggle((v) => { if (v !== state.currentPcbView) mountView(v, true); });
  wrapper.appendChild(toggle);

  state.currentPcbSource = source;
  state.currentPcbViews = views;
  state.currentPcbWrapper = wrapper;
  state.currentPcbToggle = toggle;
  state.currentPcbView = view;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(source),
    onOpen: () => {
      // The wrapper has a real layout box only after showModal; mount now so
      // PanZoom's fit measures correctly, then apply any saved transform.
      mountView(view, false);
      const saved = pcbLoadTransform(source);
      if (saved && state.currentPcbPz) state.currentPcbPz.setTransform(saved);
      state.currentPcbMinimap?.update();
    },
    onClose: () => { clearPcbState(); if (location.hash) history.back(); },
  });
}

function clearPcbState() {
  try { state.currentPcbPz?.destroy(); } catch {}
  try { state.currentPcbMinimap?.destroy(); } catch {}
  state.currentDetail = null;
  state.currentPcbSource = null;
  state.currentPcbViews = null;
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

// SSE-driven re-fetch of the open board. If any view changed, swap the active
// view in place (preserving pan/zoom and the selected view).
export async function refetchOpenPcb(source) {
  const board = boardForSource(source);
  if (!board) return;
  const views = await fetchViews(board);
  if (!views) return;
  const prevActive = state.currentPcbViews?.[state.currentPcbView];
  state.currentPcbViews = views;
  if (views[state.currentPcbView] !== prevActive) {
    mountView(state.currentPcbView, true);
  }
}
