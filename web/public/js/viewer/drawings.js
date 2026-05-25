// Drawings module. Owns the SVG fetcher, the per-file PanZoom transform
// persistence, the modal open/close flow, the offscreen thumbnail
// renderer, and the SSE-driven open-modal swap.
//
// Modeled on mermaid.js. The two viewer surfaces look the same from the
// outside — a 2D SVG opened in ContentViewer with PanZoom — so the
// open/close + transform-persistence + SSE-swap logic mirrors mermaid's.
// What differs: the SVG is generated upstream (tools/line-art/line_art.py)
// and served whole by the server, so there's no per-page render step;
// fetch -> parse to <svg> element -> wrap.

import { state } from "./state.js";
import { makeResetButton, makeMinimap } from "./pan-zoom-extras.js";

function drawingTransformKey(file) { return `drawing-transform:${file}`; }

export function drawingSaveTransform(file, t) {
  try { localStorage.setItem(drawingTransformKey(file), JSON.stringify(t)); } catch {}
}
export function drawingLoadTransform(file) {
  try {
    const raw = localStorage.getItem(drawingTransformKey(file));
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (typeof s.scale !== "number") return null;
    return s;
  } catch { return null; }
}

// Parse an SVG string into a live SVGSVGElement. The browser's
// DOMParser knows how to interpret xml-namespaced SVG; we just need to
// pull the root <svg> out of the resulting document.
function parseSvgString(svgText) {
  const doc = new DOMParser().parseFromString(svgText, "image/svg+xml");
  const svgEl = doc.querySelector("svg");
  if (!svgEl) throw new Error("Drawing content has no <svg> element");
  // Import the parsed node into the live document so it can be mounted.
  const adopted = document.importNode(svgEl, true);
  // The line_art generator writes width/height in mm and a matching
  // viewBox. PanZoom needs the natural size to compute its initial fit,
  // so make sure both are present.
  const vb = adopted.viewBox?.baseVal;
  if (vb && vb.width && vb.height) {
    adopted.setAttribute("width", vb.width);
    adopted.setAttribute("height", vb.height);
  }
  adopted.style.display = "block";
  adopted.style.maxWidth = "none";
  adopted.style.maxHeight = "none";
  return adopted;
}

// --- Thumbnail ---
// The thumbnail is the SVG itself, scaled by the .drawing-thumb container.
// SVG is already a vector — no separate rasterization step, no separate
// fetch path. Returned as a string so grid.js can innerHTML-set the host
// (matches the mermaid path; keeps cache shape uniform).
export async function renderDrawingThumbnail(file) {
  if (state.drawingThumbCache.has(file)) return state.drawingThumbCache.get(file);
  try {
    const resp = await fetch(`/api/drawing-content/${file}`);
    if (!resp.ok) return null;
    const svgText = await resp.text();
    state.drawingThumbCache.set(file, svgText);
    return svgText;
  } catch { return null; }
}

function shortName(file, ext = ".svg") {
  const parts = file.split("/");
  const name = parts.pop().replace(ext, "");
  return { name };
}

// Swap the SVG inside the open modal's wrapper without disturbing PanZoom's
// state — used by the SSE re-render path so the user's pan/zoom is
// preserved across an upstream regenerate. Minimap + reset button get
// rebuilt against the new SVG so natural-bounds-derived state stays current.
async function reRenderOpenDrawing(svgText) {
  if (!state.currentDrawingWrapper || !state.currentDrawingPz) return;
  let svgEl;
  try {
    svgEl = parseSvgString(svgText);
  } catch (err) {
    state.currentDrawingWrapper.innerHTML = `<pre style="color:#c44;padding:20px;font-size:13px;">${err.message || err}</pre>`;
    return;
  }
  const prev = state.currentDrawingPz.getTransform();
  const file = state.currentDetail?.file;
  state.currentDrawingPz.destroy();
  try { state.currentDrawingMinimap?.destroy(); } catch {}
  state.currentDrawingWrapper.innerHTML = "";
  state.currentDrawingWrapper.appendChild(svgEl);
  const minimap = makeMinimap(svgEl, state.currentDrawingWrapper);
  state.currentDrawingPz = PanZoom.wrap(svgEl, {
    container: state.currentDrawingWrapper,
    initialFit: false,
    onTransformChange: (t) => { if (file) drawingSaveTransform(file, t); },
    onTransformLive: (t) => minimap.update(t),
  });
  state.currentDrawingWrapper.appendChild(minimap.el);
  state.currentDrawingWrapper.appendChild(makeResetButton(state.currentDrawingPz, {
    transformKey: file ? drawingTransformKey(file) : null,
  }));
  state.currentDrawingMinimap = minimap;
  state.currentDrawingPz.setTransform(prev);
}

export async function openDrawingDetail(file, pushHistory = true) {
  // Mirror mermaid's openMmdDetail: set currentDetail BEFORE touching
  // location.hash, since some configurations (Puppeteer) fire popstate
  // synchronously and the popstate handler dispatches on currentDetail.
  state.currentDetail = { type: "drawing", file };
  if (pushHistory) location.hash = "svg:" + encodeURIComponent(file);

  const resp = await fetch(`/api/drawing-content/${file}`);
  if (!resp.ok) return;
  const svgText = await resp.text();

  let svgEl;
  try {
    svgEl = parseSvgString(svgText);
  } catch (err) {
    const errWrapper = document.createElement("div");
    errWrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
    errWrapper.innerHTML = `<pre style="color:#c44;padding:20px;font-size:13px;white-space:pre-wrap;">${err.message || err}</pre>`;
    ContentViewer.open({
      content: errWrapper,
      filename: shortName(file).name,
      onClose: () => {
        state.currentDetail = null;
        state.currentDrawingContent = null;
        state.currentDrawingWrapper = null;
        state.currentDrawingPz = null;
        if (location.hash) history.back();
      },
    });
    state.currentDrawingContent = svgText;
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
  wrapper.appendChild(svgEl);

  const minimap = makeMinimap(svgEl, wrapper);
  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: true,
    onTransformChange: (t) => drawingSaveTransform(file, t),
    onTransformLive: (t) => minimap.update(t),
  });
  wrapper.appendChild(minimap.el);
  wrapper.appendChild(makeResetButton(pz, { transformKey: drawingTransformKey(file) }));

  state.currentDrawingContent = svgText;
  state.currentDrawingWrapper = wrapper;
  state.currentDrawingPz = pz;
  state.currentDrawingMinimap = minimap;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(file).name,
    onOpen: () => {
      pz.fit();
      const saved = drawingLoadTransform(file);
      if (saved) pz.setTransform(saved);
      minimap.update();
    },
    onClose: () => {
      try { pz.destroy(); } catch {}
      try { minimap.destroy(); } catch {}
      state.currentDetail = null;
      state.currentDrawingContent = null;
      state.currentDrawingWrapper = null;
      state.currentDrawingPz = null;
      state.currentDrawingMinimap = null;
      if (location.hash) history.back();
    },
  });
}

export function closeDrawingDetail(pushHistory = true) {
  if (!ContentViewer.isOpen()) {
    state.currentDetail = null;
    state.currentDrawingContent = null;
    state.currentDrawingWrapper = null;
    state.currentDrawingPz = null;
    return;
  }
  if (!pushHistory) {
    const pz = state.currentDrawingPz;
    state.currentDetail = null;
    state.currentDrawingContent = null;
    state.currentDrawingWrapper = null;
    state.currentDrawingPz = null;
    try { pz?.destroy(); } catch {}
    ContentViewer.close();
    return;
  }
  ContentViewer.close();
}

// SSE-driven re-fetch of the currently-open drawing. If the content
// changed, swap the SVG without disturbing the user's pan/zoom.
export async function refetchOpenDrawing(file) {
  const resp = await fetch(`/api/drawing-content/${file}`);
  if (!resp.ok) return;
  const svgText = await resp.text();
  if (svgText === state.currentDrawingContent) return;
  state.currentDrawingContent = svgText;
  await reRenderOpenDrawing(svgText);
}
