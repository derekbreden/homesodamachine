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
import { loadStepFile } from "./step.js";
import { paintStepThumb } from "./grid.js";
import { loadDxfFile, renderDxfThumbnail } from "./dxf.js";
import { renderMmdThumbnail, refetchOpenMmd } from "./mermaid.js";
import { renderDrawingThumbnail, refetchOpenDrawing } from "./drawings.js";
import { renderPcbThumbnail, refetchOpenPcb } from "./pcb.js";
import { fetchFiles } from "./main.js";

function refreshStepCard(file) {
  // The export pipeline rewrote this part's committed thumbnail before the
  // watcher broadcast the change (its atexit render finishes before the
  // python process closes), so just re-fetch the PNG past the browser cache.
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

window.addEventListener("hsm:files-changed", (e) => {
  for (const file of (e.detail && e.detail.files) || []) {
    if (file.endsWith(".step")) {
      refreshStepCard(file);
      if (isOpenAs("step", file)) loadStepFile(file, { preserveCamera: true });
    } else if (file.endsWith(".dxf")) {
      refreshDxfCard(file);
      if (isOpenAs("dxf", file)) loadDxfFile(file, { preserveCamera: true });
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
  if (d.type === "step") loadStepFile(d.file, { preserveCamera: true });
  else if (d.type === "dxf") loadDxfFile(d.file, { preserveCamera: true });
  else if (d.type === "mmd") refetchOpenMmd(d.file);
  else if (d.type === "drawing") refetchOpenDrawing(d.file);
  else if (d.type === "pcb") refetchOpenPcb(d.file);
}

window.addEventListener("hsm:deploy", (e) => {
  // commitChanged === false means a same-commit reconnect blip (nothing
  // actually shipped): just re-list to catch any add/remove, cheaply.
  // Anything else is a real new build — wipe the caches so every
  // thumbnail and the open modal re-render against the new bytes.
  const newBuild = !e.detail || e.detail.commitChanged !== false;
  if (newBuild) {
    state.thumbnailCache.clear();
    state.dxfThumbCache.clear();
    state.mmdThumbCache.clear();
    state.drawingThumbCache.clear();
    state.pcbThumbCache.clear();
    state.stepEtags.clear();
    state.dxfEtags.clear();
  }
  fetchFiles();
  if (newBuild) reloadOpenDetail();
});
