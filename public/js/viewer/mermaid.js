// Mermaid module. Owns the lazy mermaid lib import + initialize, the
// SVG renderer, the per-file PanZoom transform persistence, the modal
// open/close flow (separate from cad-detail.js because mmd uses
// PanZoom and not the Three.js scene), the offscreen thumbnail
// renderer, and the SSE-driven open-modal swap.

import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";
import { state } from "./state.js";

mermaid.initialize({
  startOnLoad: false,
  theme: "dark",
  themeVariables: {
    darkMode: true,
    background: "#1a1a2e",
    primaryColor: "#2a2a4a",
    primaryTextColor: "#ffffff",
    primaryBorderColor: "#3a3a5a",
    lineColor: "#999999",
    secondaryColor: "#232342",
    tertiaryColor: "#1a1a2e",
    fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif",
    fontSize: "14px",
  },
  flowchart: { htmlLabels: true, curve: "basis", padding: 12 },
});

// --- Mermaid detail view ---
// The detail opens inside ContentViewer; PanZoom drives pan/zoom; we persist
// {scale,panX,panY} per-file in localStorage and restore on reopen. The
// wrapper / SVG host stays mounted so SSE re-renders can swap the SVG
// without recreating PanZoom (preserves the user's pan/zoom).
let mmdRenderCounter = 0;

function mmdTransformKey(file) { return `mmd-transform:${file}`; }

export function mmdSaveTransform(file, t) {
  try { localStorage.setItem(mmdTransformKey(file), JSON.stringify(t)); } catch {}
}
export function mmdLoadTransform(file) {
  try {
    const raw = localStorage.getItem(mmdTransformKey(file));
    if (!raw) return null;
    const s = JSON.parse(raw);
    if (typeof s.scale !== "number") return null;
    return s;
  } catch { return null; }
}

// Render `content` to an SVG element with explicit width/height (so PanZoom
// can measure natural size). Returns the SVGSVGElement, or throws.
export async function mmdRenderSvg(content) {
  const id = `mmd-detail-${++mmdRenderCounter}`;
  const { svg } = await mermaid.render(id, content);
  const tmp = document.createElement("div");
  tmp.innerHTML = svg;
  const svgEl = tmp.querySelector("svg");
  if (!svgEl) throw new Error("mermaid produced no <svg>");
  // Mermaid sets width="100%"; lock to natural viewBox dims so PanZoom can
  // fit-to-container correctly.
  const vb = svgEl.viewBox?.baseVal;
  if (vb && vb.width && vb.height) {
    svgEl.setAttribute("width", vb.width);
    svgEl.setAttribute("height", vb.height);
  }
  svgEl.style.display = "block";
  svgEl.style.maxWidth = "none";
  svgEl.style.maxHeight = "none";
  return svgEl;
}

// Replace the SVG inside the open modal's wrapper without touching PanZoom.
// Used by the SSE re-render path so the user's pan/zoom is preserved.
async function reRenderOpenMmd(content) {
  if (!state.currentMmdWrapper || !state.currentMmdPz) return;
  let svgEl;
  try {
    svgEl = await mmdRenderSvg(content);
  } catch (err) {
    state.currentMmdWrapper.innerHTML = `<pre style="color:#c44;padding:20px;font-size:13px;">${err.message || err}</pre>`;
    return;
  }
  // Clear the wrapper but keep PanZoom listeners (they're on the wrapper, not
  // the SVG). Re-wrap the new SVG against the same wrapper, then restore the
  // previous transform so the swap is invisible.
  const prev = state.currentMmdPz.getTransform();
  state.currentMmdPz.destroy();
  state.currentMmdWrapper.innerHTML = "";
  state.currentMmdWrapper.appendChild(svgEl);
  state.currentMmdPz = PanZoom.wrap(svgEl, {
    container: state.currentMmdWrapper,
    initialFit: false,
    onTransformChange: (t) => mmdSaveTransform(file, t),
  });
  state.currentMmdPz.setTransform(prev);
}

// --- Mermaid thumbnail rendering ---
export async function renderMmdThumbnail(file) {
  if (state.mmdThumbCache.has(file)) return state.mmdThumbCache.get(file);
  try {
    const resp = await fetch(`/api/mermaid-content/${file}`);
    if (!resp.ok) return null;
    const content = await resp.text();
    const id = `mmd-thumb-${file.replace(/[^a-zA-Z0-9]/g, "-")}`;
    const { svg } = await mermaid.render(id, content);
    state.mmdThumbCache.set(file, svg);
    return svg;
  } catch { return null; }
}

function shortName(file, ext = ".mmd") {
  const parts = file.split("/");
  const name = parts.pop().replace(ext, "");
  return { name };
}

export async function openMmdDetail(file, pushHistory = true) {
  // Set currentDetail BEFORE touching location.hash. In some browser
  // configurations (notably Puppeteer) setting location.hash fires a
  // popstate that runs synchronously before this function returns; the
  // popstate handler dispatches on currentDetail, so it must already
  // reflect this open or it re-enters openMmdDetail and we end up with
  // a duplicate ContentViewer (whose singleton-replacement strips the
  // hash).
  state.currentDetail = { type: "mmd", file };
  if (pushHistory) location.hash = "mmd:" + encodeURIComponent(file);

  const resp = await fetch(`/api/mermaid-content/${file}`);
  if (!resp.ok) return;
  const content = await resp.text();

  let svgEl;
  try {
    svgEl = await mmdRenderSvg(content);
  } catch (err) {
    // Render the error inside the modal too so the user sees something.
    const errWrapper = document.createElement("div");
    errWrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
    errWrapper.innerHTML = `<pre style="color:#c44;padding:20px;font-size:13px;white-space:pre-wrap;">${err.message || err}</pre>`;
    ContentViewer.open({
      content: errWrapper,
      filename: shortName(file, ".mmd").name,
      onClose: () => {
        state.currentDetail = null;
        state.currentMmdContent = null;
        state.currentMmdWrapper = null;
        state.currentMmdPz = null;
        if (location.hash) history.back();
      },
    });
    state.currentDetail = { type: "mmd", file };
    state.currentMmdContent = content;
    return;
  }

  const wrapper = document.createElement("div");
  wrapper.style.cssText = "overflow:hidden;position:relative;width:100%;height:100%;";
  wrapper.appendChild(svgEl);

  const pz = PanZoom.wrap(svgEl, {
    container: wrapper,
    initialFit: true,
    onTransformChange: (t) => mmdSaveTransform(file, t),
  });

  state.currentDetail = { type: "mmd", file };
  state.currentMmdContent = content;
  state.currentMmdWrapper = wrapper;
  state.currentMmdPz = pz;

  ContentViewer.open({
    content: wrapper,
    filename: shortName(file, ".mmd").name,
    onOpen: () => {
      // Container's real layout box is only known after the dialog has been
      // shown. Re-fit now (PanZoom's initialFit ran before showModal made the
      // wrapper measurable) and then apply any saved transform on top.
      pz.fit();
      const saved = mmdLoadTransform(file);
      if (saved) pz.setTransform(saved);
    },
    onClose: () => {
      try { pz.destroy(); } catch {}
      state.currentDetail = null;
      state.currentMmdContent = null;
      state.currentMmdWrapper = null;
      state.currentMmdPz = null;
      if (location.hash) history.back();
    },
  });
}

export function closeMmdDetail(pushHistory = true) {
  // Closing is driven by ContentViewer (backdrop tap / Escape / X / swipe).
  // The onClose handler above clears state and pops history. This wrapper
  // exists for the popstate path, which calls us with pushHistory=false to
  // dismiss the modal without re-popping (the URL already changed).
  if (!ContentViewer.isOpen()) {
    // Already closed by the user — just normalize state.
    state.currentDetail = null;
    state.currentMmdContent = null;
    state.currentMmdWrapper = null;
    state.currentMmdPz = null;
    return;
  }
  // Suppress the onClose-driven history.back() so popstate-driven closes
  // don't double-pop the history stack.
  if (!pushHistory) {
    const wrapper = state.currentMmdWrapper;
    const pz = state.currentMmdPz;
    state.currentDetail = null;
    state.currentMmdContent = null;
    state.currentMmdWrapper = null;
    state.currentMmdPz = null;
    try { pz?.destroy(); } catch {}
    ContentViewer.close();
    return;
  }
  ContentViewer.close();
}

// SSE-driven re-fetch of the open mmd modal. If content changed, swap
// the SVG without disturbing the user's pan/zoom (reRenderOpenMmd
// preserves it via getTransform/setTransform).
export async function refetchOpenMmd(file) {
  const resp = await fetch(`/api/mermaid-content/${file}`);
  if (!resp.ok) return;
  const content = await resp.text();
  if (content === state.currentMmdContent) return;
  state.currentMmdContent = content;
  await reRenderOpenMmd(content);
}
