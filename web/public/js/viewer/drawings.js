// Drawings module. Owns the SVG fetcher, the per-file PanZoom transform
// persistence, the modal open/close flow, the offscreen thumbnail
// renderer, and the open-modal swap on re-render.
//
// Modeled on mermaid.js. The two viewer surfaces look the same from the
// outside — a 2D SVG opened in ContentViewer with PanZoom — so the
// open/close + transform-persistence + re-render-swap logic mirrors mermaid's.
// What differs: the SVG is generated upstream (tools/line-art/line_art.py)
// and served whole by the server, so there's no per-page render step;
// fetch -> parse to <svg> element -> wrap.

import { state } from "./state.js";
import { makeResetButton, makeMinimap, makeChromeFit } from "./pan-zoom-extras.js";

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
  // Tag the SVG so viewer.css can recolor strokes for the dark modal
  // surface (same treatment the thumbnails get via .card .drawing-thumb).
  adopted.classList.add("drawing-svg");
  return adopted;
}

// CadQuery's SVG exporter emits `width`/`height` attributes but no
// `viewBox`. Without a viewBox the SVG's internal coordinate system
// doesn't scale to fit a smaller rendered size — `max-width: 100%` on
// the thumbnail just clips the top-left corner of the original-size
// canvas. Inject a viewBox derived from the width/height so the
// content scales with the container.
function ensureViewBox(svgText) {
  if (/<svg\b[^>]*\sviewBox\s*=/i.test(svgText)) return svgText;
  const w = /<svg\b[^>]*\swidth\s*=\s*"([^"]+)"/i.exec(svgText)?.[1];
  const h = /<svg\b[^>]*\sheight\s*=\s*"([^"]+)"/i.exec(svgText)?.[1];
  if (!w || !h) return svgText;
  return svgText.replace(/<svg\b/, `<svg viewBox="0 0 ${w} ${h}"`);
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
    const svgText = ensureViewBox(await resp.text());
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
// state — used by the re-render path so the user's pan/zoom is
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
  const chrome = makeChromeFit(state.currentDrawingWrapper);
  const minimap = makeMinimap(svgEl, state.currentDrawingWrapper, chrome.obstacles);
  state.currentDrawingPz = PanZoom.wrap(svgEl, {
    container: state.currentDrawingWrapper,
    initialFit: false,
    fitObstacles: chrome.obstacles,
    onTransformChange: (t) => { if (file) drawingSaveTransform(file, t); },
    onTransformLive: (t) => minimap.update(t),
  });
  state.currentDrawingWrapper.appendChild(minimap.el);
  state.currentDrawingWrapper.appendChild(makeResetButton(state.currentDrawingPz, {
    transformKey: file ? drawingTransformKey(file) : null,
    refit: chrome.refit,
  }));
  chrome.attach(state.currentDrawingPz, minimap);
  chrome.measure();
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

  const chrome = makeChromeFit(wrapper);
  const minimap = makeMinimap(svgEl, wrapper, chrome.obstacles);
  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: true,
    fitObstacles: chrome.obstacles,
    onTransformChange: (t) => drawingSaveTransform(file, t),
    onTransformLive: (t) => minimap.update(t),
  });
  wrapper.appendChild(minimap.el);
  wrapper.appendChild(makeResetButton(pz, {
    transformKey: drawingTransformKey(file),
    refit: chrome.refit,
  }));
  chrome.attach(pz, minimap);

  state.currentDrawingContent = svgText;
  state.currentDrawingWrapper = wrapper;
  state.currentDrawingPz = pz;
  state.currentDrawingMinimap = minimap;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(file).name,
    onOpen: () => chrome.open(drawingLoadTransform(file)),
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

export async function refetchOpenDrawing(file) {
  const resp = await fetch(`/api/drawing-content/${file}`);
  if (!resp.ok) return;
  const svgText = await resp.text();
  if (svgText === state.currentDrawingContent) return;
  state.currentDrawingContent = svgText;
  await reRenderOpenDrawing(svgText);
}
