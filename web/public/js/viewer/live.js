// SSE-driven live updates. Side-effect import only — registers two
// listeners on import:
//
//   hsm:files-changed (detail.files = [...]) — fired by both dev chokidar
//     saves and prod boot-diff. Same wire format both sides. We refresh
//     the per-file card thumbnail and, if that file is the one currently
//     open in the modal, refetch the file into the open viewer too.
//
//   hsm:deploy — fired when the SSE `hello` commit fingerprint changes,
//     meaning a fresh server build is up. Files added or removed in the
//     deploy aren't covered by hsm:files-changed (we only diff content
//     of files still on disk), so we refetch the list.
//
// SSE connection itself is owned by HEAD_TAGS (see public/boot.js) —
// one EventSource per page, used for both the toast (page-global) and
// per-file refresh (viewer-only). Per-file work is split by extension
// so the same handler covers .step, .dxf, and .mmd uniformly.

import { state } from "./state.js";
import { loadStepFile, renderThumbnail } from "./step.js";
import { loadDxfFile, renderDxfThumbnail } from "./dxf.js";
import { renderMmdThumbnail, refetchOpenMmd } from "./mermaid.js";
import { renderDrawingThumbnail, refetchOpenDrawing } from "./drawings.js";
import { fetchFiles } from "./main.js";

function refreshStepCard(file) {
  state.thumbnailCache.delete(file);
  const card = state.gridEl.querySelector(`.card[data-type="step"][data-file="${CSS.escape(file)}"]`);
  if (!card) { fetchFiles(); return; }
  const img = card.querySelector("img");
  if (img) {
    const ph = document.createElement("div");
    ph.className = "placeholder";
    ph.dataset.file = file;
    ph.textContent = "updating...";
    img.replaceWith(ph);
  }
  renderThumbnail(file).then((url) => {
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
    }
  }
});

// On a fresh deploy, the file list itself may have additions/removals
// that per-file `hsm:files-changed` events don't cover (we only diff
// content of files still on disk). Refetch the list to pick those up.
window.addEventListener("hsm:deploy", () => { fetchFiles(); });
