// WebSocket-driven live updates for the viewer. Side-effect import only —
// registers the listeners below on import:
//
//   hsm:files-changed (detail.files = [...]) — fired by both dev chokidar
//     saves and the prod boot-diff. Same wire format both sides. We refresh
//     the per-file card thumbnail and, if that file is the one currently
//     open in the modal, refetch the file into the open viewer too.
//
//   hsm:deploy — fired when a new build is detected, via either the WS
//     `hello` commit changing across a reconnect or boot.js's /api/version
//     activation check. We can't know which files differ, so on a real
//     build we refresh everything: drop the thumbnail + etag caches,
//     refetch the lists (rebuilding the grid re-renders every visible
//     thumbnail fresh), and reload whatever the modal is showing,
//     preserving the camera. A same-commit reconnect blip
//     (commitChanged === false) only re-lists — no cache wipe, no re-mesh.
//
// We set window.__hsmDeploySoft so boot.js leaves the deploy refresh to
// us (it reloads other pages outright). The socket itself is owned by
// boot.js (one WebSocket per page); per-file work is split by extension
// so the same handler covers .step, .dxf, .mmd, and drawing .svg.

import { state } from "./state.js";
import { getLoader } from "./loaders.js";
import { paintStepThumb } from "./grid.js";
import { renderDxfThumbnail } from "./dxf.js";
import { renderGlbThumbnail } from "./glb.js";
// Open-modal refresh resolves through detail-shims.js (hot); thumbnail renderers
// stay static — a code edit rarely touches the tiny card render and re-importing
// for it isn't worth it (matches the CAD kinds keeping renderGlbThumbnail static).
import { refetchOpenMmd, refetchOpenDrawing, refetchOpenPcb } from "./detail-shims.js";
import { renderMmdThumbnail } from "./mermaid.js";
import { renderDrawingThumbnail } from "./drawings.js";
import { renderPcbThumbnail } from "./pcb.js";
import { fetchFiles } from "./main.js";
import { HSM_EVENTS } from "/contracts/client-events.js";

function refreshStepCard(file) {
  // Re-fetch the committed PNG past the browser cache. On a real deploy the
  // thumbnail ships committed alongside the STEP, so it's fresh immediately. On
  // the dev watcher the STEP broadcast races ahead of its background thumbnail
  // render (dev-server/server.js flushThumbnails), so the card may briefly show
  // the prior PNG, then repaints when the render re-broadcasts this same file.
  // Drop the client-render cache too, in case this card is on the missing-
  // thumbnail fallback path.
  state.thumbnailCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="step"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  paintStepThumb(card, { bust: true });
}

function refreshDxfCard(file) {
  state.dxfThumbCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="dxf"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const img = card.querySelector("img");
  if (img) {
    const ph = document.createElement("div");
    ph.className = "placeholder";
    ph.dataset.file = file;
    ph.textContent = "updating...";
    img.replaceWith(ph);
  }
  renderDxfThumbnail(file).then((url) => {
    if (!url) return;
    const target = card.querySelector(".placeholder");
    if (target) {
      const newImg = document.createElement("img");
      newImg.src = url;
      target.replaceWith(newImg);
    } else {
      const existing = card.querySelector("img");
      if (existing) existing.src = url;
    }
  });
}

function refreshGlbCard(file) {
  state.glbThumbCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="glb"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const img = card.querySelector("img");
  if (img) {
    const ph = document.createElement("div");
    ph.className = "placeholder";
    ph.dataset.file = file;
    ph.textContent = "updating...";
    img.replaceWith(ph);
  }
  renderGlbThumbnail(file).then((url) => {
    if (!url) return;
    const target = card.querySelector(".placeholder");
    if (target) {
      const newImg = document.createElement("img");
      newImg.src = url;
      target.replaceWith(newImg);
    } else {
      const existing = card.querySelector("img");
      if (existing) existing.src = url;
    }
  });
}

function refreshMmdCard(file) {
  state.mmdThumbCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="mmd"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const thumbEl = card.querySelector(".mmd-thumb");
  if (thumbEl) thumbEl.innerHTML = `<div class="placeholder">updating...</div>`;
  renderMmdThumbnail(file).then((svg) => {
    if (!thumbEl) return;
    thumbEl.innerHTML = svg ? svg : `<div class="placeholder">error</div>`;
  });
}

function refreshDrawingCard(file) {
  state.drawingThumbCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="drawing"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const thumbEl = card.querySelector(".drawing-thumb");
  if (thumbEl) thumbEl.innerHTML = `<div class="placeholder">updating...</div>`;
  renderDrawingThumbnail(file).then((svg) => {
    if (!thumbEl) return;
    thumbEl.innerHTML = svg ? svg : `<div class="placeholder">error</div>`;
  });
}

function refreshPcbCard(file) {
  state.pcbThumbCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="pcb"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const thumbEl = card.querySelector(".pcb-thumb");
  if (thumbEl) thumbEl.innerHTML = `<div class="placeholder">updating...</div>`;
  renderPcbThumbnail(file).then((svg) => {
    if (!thumbEl) return;
    thumbEl.innerHTML = svg ? svg : `<div class="placeholder">error</div>`;
  });
}

function isOpenAs(type, file) {
  return state.currentDetail && state.currentDetail.type === type && state.currentDetail.file === file;
}

// Re-load a CAD part into the open modal, in place, camera preserved. Resolves
// the loader through getLoader so a code edit / deploy is reflected — the fresh
// leaf talks to the same live scene + state, so nothing is torn down.
async function reloadCad(type, file) {
  const load = await getLoader(type);
  return load(file, { preserveCamera: true });
}

window.addEventListener(HSM_EVENTS.FILES_CHANGED, (e) => {
  for (const file of (e.detail && e.detail.files) || []) {
    if (file.endsWith(".step")) {
      refreshStepCard(file);
      if (isOpenAs("step", file)) reloadCad("step", file);
    } else if (file.endsWith(".dxf")) {
      refreshDxfCard(file);
      if (isOpenAs("dxf", file)) reloadCad("dxf", file);
    } else if (file.endsWith(".glb")) {
      refreshGlbCard(file);
      if (isOpenAs("glb", file)) reloadCad("glb", file);
    } else if (file.endsWith(".mmd")) {
      refreshMmdCard(file);
      if (isOpenAs("mmd", file)) refetchOpenMmd(file);
    } else if (file.endsWith(".svg")) {
      refreshDrawingCard(file);
      if (isOpenAs("drawing", file)) refetchOpenDrawing(file);
    } else if (file.endsWith(".tsx")) {
      // PCB board: the watcher broadcasts the board source after re-rendering
      // its three views, so refresh the card and the open modal (if it's this
      // board) against the new SVGs.
      refreshPcbCard(file);
      if (isOpenAs("pcb", file)) refetchOpenPcb(file);
    }
  }
});

// Claim the deploy refresh: boot.js reloads pages that don't set this,
// but the viewer refreshes in place so the open modal + camera survive.
window.__hsmDeploySoft = true;

function reloadOpenDetail() {
  const d = state.currentDetail;
  if (!d) return;
  if (d.type === "step" || d.type === "dxf" || d.type === "glb") reloadCad(d.type, d.file);
  else if (d.type === "mmd") refetchOpenMmd(d.file);
  else if (d.type === "drawing") refetchOpenDrawing(d.file);
  else if (d.type === "pcb") refetchOpenPcb(d.file);
}

// Force the open detail to fully re-render on the next reloadOpenDetail rather
// than short-circuit on unchanged content — used when the render CODE moved even
// though the artifact bytes didn't (a deploy or a dev code edit). Each kind gates
// re-render on a "same as last time" check: CAD loaders on the ETag, the PanZoom
// kinds on the last content string / view set. Dropping those makes the freshly
// imported module actually re-parse and re-mount.
function forceDetailRerender() {
  state.stepEtags.clear();
  state.dxfEtags.clear();
  state.glbEtags.clear();
  state.currentMmdContent = null;
  state.currentDrawingContent = null;
  state.currentPcbViews = null;
}

window.addEventListener(HSM_EVENTS.DEPLOY, (e) => {
  // commitChanged === false means a same-commit reconnect blip (nothing
  // actually shipped): just re-list to catch any add/remove, cheaply.
  // Anything else is a real new build — wipe the caches so every
  // thumbnail and the open modal re-render against the new bytes.
  const newBuild = !e.detail || e.detail.commitChanged !== false;
  if (newBuild) {
    // Adopt the new build's commit as the code-bust token so the open modal and
    // any subsequent open re-import the leaf loaders as the new deploy's code,
    // not the code this tab loaded at boot.
    if (e.detail && e.detail.commit) state.codeVersion = String(e.detail.commit);
    state.thumbnailCache.clear();
    state.dxfThumbCache.clear();
    state.glbThumbCache.clear();
    state.mmdThumbCache.clear();
    state.drawingThumbCache.clear();
    state.pcbThumbCache.clear();
    // New build may carry new render code too, so force a full re-render (this
    // drops the ETags the pre-code-version deploy path already cleared).
    forceDetailRerender();
  }
  fetchFiles();
  if (newBuild) reloadOpenDetail();
});

// Dev viewer-source hot-reload: a render module (glb/step/dxf leaf, or a
// mermaid/drawing/pcb detail module) was edited. The artifact bytes are
// unchanged — only the code moved — so adopt the change nonce as the code-bust
// token, force a full re-render past the unchanged-content guards, and re-render
// the open modal in place. No card refresh or list re-fetch: nothing on disk that
// the grid reads changed. A modal opened after this naturally re-imports fresh
// (getLoader / detail-shims). No-op if nothing is open.
window.addEventListener(HSM_EVENTS.CODE_CHANGED, (e) => {
  const version = e.detail && e.detail.version;
  if (version) state.codeVersion = String(version);
  forceDetailRerender();
  reloadOpenDetail();
});
