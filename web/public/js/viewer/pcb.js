// PCB board module. A board carries its rendered copper views — Top (front),
// Bottom (back, seen from above through the board), any inner copper planes of a
// multi-layer board, and Overlay (the whole stack at once, warm front / cool
// back) — produced by hardware/pcb/pcba/render-board.ts straight from the
// fabrication Gerbers, so the lines have the real widths the board is made with.
//
// Modeled on drawings.js: a 2D SVG opened in ContentViewer with PanZoom, with
// per-board transform persistence and a swap-in-place on re-render. What it adds
// is the view toggle — Top / Inner 1…N / Bottom / Overlay, in physical stack
// order. All views share one identical viewBox, so switching swaps the SVG while
// keeping the user's exact pan/zoom — the board holds still under the toggle.

import { state } from "./state.js";
import { makeResetButton, makeMinimap } from "./pan-zoom-extras.js";
import { installPadPicker, clearPadPicker, clearPadSelection, makePadPickToggle } from "./pcb-pick.js";
import { installEditOverlay, clearEditOverlay, makeEditToggle, fetchEditComponents } from "./pcb-edit.js";

// Every board has these three; inner planes (inner1, inner2, …) are per-board,
// discovered by the server (walk.js) and slotted between Top and Bottom.
const FIXED_LABEL = { top: "Top", bottom: "Bottom", overlay: "Overlay" };

// The view key for an inner-plane path (".../mini.inner2.svg" -> "inner2"), or
// null if the path isn't an inner view.
function innerKey(path) {
  const m = /\.inner(\d+)\.svg$/.exec(path || "");
  return m ? "inner" + m[1] : null;
}
// Human label for a view key: the fixed ones verbatim, "inner2" -> "Inner 2".
function viewLabel(view) {
  if (FIXED_LABEL[view]) return FIXED_LABEL[view];
  const m = /^inner(\d+)$/.exec(view);
  return m ? "Inner " + m[1] : view;
}
// The ordered {view, path} list a board offers, in physical stack order:
// Top (front) → inner planes front-to-back → Bottom (back) → Overlay (composite,
// last). board.inners is already stack-ordered by the server.
function orderedViews(board) {
  const list = [{ view: "top", path: board.top }];
  for (const p of board.inners || []) {
    const key = innerKey(p);
    if (key) list.push({ view: key, path: p });
  }
  list.push({ view: "bottom", path: board.bottom });
  list.push({ view: "overlay", path: board.overlay });
  return list;
}

// Fit obstacles for the board PanZoom: the on-screen rectangles of the overlaid
// chrome (toggle / minimap / filename / close on top; readout / pad-pick / reset
// on the bottom), so the fit — and the zoom-out floor, which equals the fit
// scale — grow the board as large as possible while clearing them. Treating
// them as rects (not a uniform band) means a corner widget like the minimap
// only limits the fit when the board actually grows under it. One shared array:
// PanZoom and the minimap read it live; onOpen measures the laid-out chrome in.
const pcbFitObstacles = [];

// Each chrome pill, as a wrapper-local rect padded by `gap`, so the board keeps
// a small margin from it. Measured live (positions shift with safe-area insets
// and the minimap's aspect-driven height).
const CHROME_SELECTORS = [
  ".pcb-view-toggle", ".pan-zoom-minimap", ".cv-filename", ".cv-close",
  ".pcb-dims", ".pcb-wrapper > .pad-pick-toggle", ".pcb-wrapper > .pcb-edit-toggle",
  ".reset-view",
];
function measureChromeObstacles(wrapper) {
  const wr = wrapper.getBoundingClientRect();
  const cw = wrapper.clientWidth, ch = wrapper.clientHeight;
  if (!wr.width || !wr.height || !cw || !ch) return [];
  // getBoundingClientRect is scaled by the modal card's open animation; divide
  // the wrapper-relative offsets by that live scale to land in layout px — the
  // same coordinate space PanZoom fits in (clientWidth/Height). This makes the
  // fit correct mid-animation without waiting for the card to settle.
  const sx = wr.width / cw, sy = wr.height / ch;
  const gap = 12;
  const rects = [];
  for (const sel of CHROME_SELECTORS)
    for (const el of document.querySelectorAll(sel)) {
      const r = el.getBoundingClientRect();
      if (!r.width || !r.height) continue;
      rects.push({
        left: (r.left - wr.left) / sx - gap,
        top: (r.top - wr.top) / sy - gap,
        right: (r.right - wr.left) / sx + gap,
        bottom: (r.bottom - wr.top) / sy + gap,
      });
    }
  return rects;
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
function pcbLoadView(source, validViews) {
  try {
    const v = localStorage.getItem(pcbViewKey(source));
    return validViews.includes(v) ? v : null;
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
// Inlining several board SVGs into one document collides their shared element ids:
// pcb-stackup emits the SAME `fcu_clear-1`, `bcu_clear-1`, `in*_clear-1`, and
// `*_pad-*` ids in every file and view, so a `mask="url(#fcu_clear-1)"` binds to
// whichever copy is FIRST in the document — a grid thumbnail — and the modal's
// copper gets masked by the wrong board's clearance (the "big hole" that only
// appeared from the /pcb grid, not a direct deep-link). Rewrite every id and its
// references to a per-instance token so each inlined SVG is self-contained.
let _svgIdSeq = 0;
function uniquifySvgIds(svgText) {
  const ids = new Set();
  for (const m of svgText.matchAll(/\bid="([^"]+)"/g)) ids.add(m[1]);
  if (!ids.size) return svgText;
  const tok = "__b" + ++_svgIdSeq;
  let out = svgText;
  for (const id of ids) {
    const esc = id.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
    out = out
      .replace(new RegExp(`id="${esc}"`, "g"), `id="${id}${tok}"`)
      .replace(new RegExp(`url\\(#${esc}\\)`, "g"), `url(#${id}${tok})`)
      .replace(new RegExp(`((?:xlink:)?href)="#${esc}"`, "g"), `$1="#${id}${tok}"`);
  }
  return out;
}

function parseSvgString(svgText) {
  svgText = uniquifySvgIds(svgText);
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

// Fetch a board's view SVGs — Top/Bottom/Overlay plus any inner planes — keyed
// by view name ({ top, bottom, overlay, inner1, … }). Returns null if any of the
// three fixed views fail; an inner plane that fails to load is simply omitted,
// so its toggle button never appears rather than blocking the whole board.
async function fetchViews(board) {
  try {
    const entries = orderedViews(board);
    const texts = await Promise.all(
      entries.map((e) => fetch(contentUrl(e.path)).then((r) => (r.ok ? r.text() : null))),
    );
    const views = {};
    entries.forEach((e, i) => { if (texts[i] != null) views[e.view] = texts[i]; });
    if (!views.top || !views.bottom || !views.overlay) return null;
    return views;
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
// Via tally for the dimensions chip. Vias live in picks.json (pick-data.ts);
// without a picks sidecar there is no via data, so this returns null and the
// chip shows dimensions alone. Returns a "42 vias" string (singular "1 via").
function viaCountText(picks) {
  const vias = picks && picks.vias;
  if (!Array.isArray(vias)) return null;
  return `${vias.length} via${vias.length === 1 ? "" : "s"}`;
}
// Create or update the bottom-centre dimensions chip in `wrapper`.
function updateDimsChip(wrapper, picks) {
  if (!wrapper) return;
  const text = [boardDimsText(picks, wrapper), viaCountText(picks)].filter(Boolean).join(" · ");
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
    // Uniquify here too — the grid inlines every board's thumbnail at once, so
    // without this they collide with each other (and seed the modal collision).
    const svgText = uniquifySvgIds(await resp.text());
    state.pcbThumbCache.set(source, svgText);
    return svgText;
  } catch { return null; }
}

// Build the segmented control from `views` (ordered view keys). onSelect(view)
// swaps the shown SVG; the buttons reflect state.currentPcbView.
function makeViewToggle(views, onSelect) {
  const wrap = document.createElement("div");
  wrap.className = "pcb-view-toggle";
  for (const v of views) {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "pcb-view-btn";
    btn.dataset.view = v;
    btn.textContent = viewLabel(v);
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
// The toggle's per-button action — swap to `v` unless it's already showing.
// Shared by the initial build and the live-reload rebuild.
function onViewSelect(v) { if (v !== state.currentPcbView) mountView(v, true); }

// Mount `view` into the open board's wrapper, re-wrapping PanZoom while keeping
// the current transform (all views share a viewBox, so the board doesn't move).
// `preserve` carries the transform across a swap; on first mount we fit.
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
  const minimap = makeMinimap(svgEl, wrapper, pcbFitObstacles);
  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: !prev,
    // The board's natural size is in Gerber units (~150000), so the fit scale is
    // tiny (~0.006). Drop PanZoom's default minScale floor (0.1) well below it
    // or the fit clamps and the board renders far too zoomed-in.
    minScale: 0.0001,
    // Grow the fit (and the zoom-out floor) as large as clears the chrome rects.
    // Measured into pcbFitObstacles in onOpen; shared by reference so swaps + the
    // minimap stay consistent.
    fitObstacles: pcbFitObstacles,
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

  // Re-arm the (dev-only) component editor on the freshly mounted SVG. Present
  // only when the editor API returned components for this board (state set in
  // openPcbDetail / refetchOpenPcb); null elsewhere, so production is read-only.
  const edit = state.currentPcbEdit;
  installEditOverlay(svgEl, edit ? { name: edit.name, components: edit.components, picks, source, wrapper } : null);
}

export async function openPcbDetail(source, pushHistory = true) {
  // Set currentDetail BEFORE touching location.hash (popstate may fire
  // synchronously under Puppeteer; its handler dispatches on currentDetail).
  state.currentDetail = { type: "pcb", file: source };
  // Start from no obstacles; onOpen measures the real chrome once it's laid out.
  pcbFitObstacles.length = 0;
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
  const [views, picks, edit] = board
    ? await Promise.all([fetchViews(board), fetchPicks(board), fetchEditComponents(shortName(source))])
    : [null, null, null];

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

  // The toggle and its order follow the views that actually loaded, in stack
  // order; a saved view only sticks if it's one of them.
  const present = orderedViews(board).map((e) => e.view).filter((v) => views[v]);
  const view = pcbLoadView(source, present) || "overlay";
  const toggle = makeViewToggle(present, onViewSelect);
  wrapper.appendChild(toggle);
  if (picks && picks.pads && picks.pads.length) wrapper.appendChild(makePadPickToggle());
  // The Edit toggle only mounts when the dev-only editor API returned
  // components (null in production) — so the move-components affordance is
  // dev-server-only without any host/commit sniffing.
  if (edit) wrapper.appendChild(makeEditToggle());

  // Publish the open-modal context, then build the first view synchronously —
  // before ContentViewer.open (the proven mermaid/drawings order). Mounting
  // here rather than in onOpen keeps the SVG + PanZoom out of reach of the
  // singleton-close path, which fires the prior modal's onClose during open.
  state.currentPcbSource = source;
  state.currentPcbViews = views;
  state.currentPcbPicks = picks;
  state.currentPcbEdit = edit;
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
      // Size the minimap (its box is aspect-driven, otherwise still at its
      // pre-layout max height), measure the laid-out chrome rects into the
      // shared obstacle list, and fit so the board grows as large as clears
      // them.
      const refit = () => {
        try {
          minimap?.update();
          const obs = measureChromeObstacles(wrapper);
          pcbFitObstacles.length = 0;
          pcbFitObstacles.push(...obs);
          pz?.fit();
        } catch {}
        minimap?.update();
      };
      refit();
      // measureChromeObstacles works in layout px, so the fit is correct even
      // mid-open-animation — no settle-timing needed. One more on the next frame
      // covers the minimap sizing itself (its box is aspect-driven on first
      // paint). A saved transform, if any, overrides the fit.
      const saved = pcbLoadTransform(source);
      if (saved && pz) { pz.setTransform(saved); minimap?.update(); return; }
      requestAnimationFrame(refit);
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
  try { clearEditOverlay(); } catch {}
  state.currentDetail = null;
  state.currentPcbSource = null;
  state.currentPcbViews = null;
  state.currentPcbPicks = null;
  state.currentPcbEdit = null;
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
  // Live-reload path: the open-board branch of refreshPcbCard (live.js) never
  // re-fetches the board list, so board.inners would otherwise be frozen at
  // page-load. Refresh it (like openPcbDetail) so a re-render that added or
  // dropped an inner plane is reflected in the views we fetch and the toggle.
  try {
    const list = await fetch("/api/pcb").then((r) => (r.ok ? r.json() : null));
    if (list) state.pcbBoards = list;
  } catch {}
  const board = boardForSource(source);
  if (!board) return;
  const [views, picks, edit] = await Promise.all([
    fetchViews(board), fetchPicks(board), fetchEditComponents(shortName(source)),
  ]);
  if (!views) return;
  const prevView = state.currentPcbView;
  const prevActive = state.currentPcbViews?.[prevView];
  state.currentPcbViews = views;
  state.currentPcbPicks = picks;
  state.currentPcbEdit = edit;
  updateDimsChip(state.currentPcbWrapper, picks);

  // If the showing plane is gone, fall back to the overlay (always present).
  const present = orderedViews(board).map((e) => e.view).filter((v) => views[v]);
  const view = views[prevView] ? prevView : "overlay";

  // Rebuild the toggle when the available planes changed (a layer added or
  // removed), so new buttons appear and dead ones go away; leave it untouched
  // when the set is identical (the common case — a geometry-only re-render).
  // Either way re-sync the active button: a remount below would, but the
  // unchanged-view path skips it, and a freshly built toggle starts blank.
  if (state.currentPcbToggle) {
    const shown = [...state.currentPcbToggle.querySelectorAll(".pcb-view-btn")].map((b) => b.dataset.view);
    if (shown.join() !== present.join()) {
      const fresh = makeViewToggle(present, onViewSelect);
      state.currentPcbToggle.replaceWith(fresh);
      state.currentPcbToggle = fresh;
    }
    syncToggle(state.currentPcbToggle, view);
  }

  // The board re-rendered underneath us: drop any stale selection (its geometry
  // may be gone) so the inspector doesn't keep a dead highlight, then rebuild
  // the hit targets from the fresh picks so they line up with the new copper.
  clearPadSelection();
  if (view !== prevView || views[view] !== prevActive) {
    mountView(view, true);
  } else {
    const svgEl = state.currentPcbWrapper?.querySelector(".pcb-svg");
    if (svgEl) {
      installPadPicker(svgEl, picks ? { pads: picks.pads, vias: picks.vias, traces: picks.traces, source, wrapper: state.currentPcbWrapper } : null);
      installEditOverlay(svgEl, edit ? { name: edit.name, components: edit.components, picks, source, wrapper: state.currentPcbWrapper } : null);
    }
  }
}
