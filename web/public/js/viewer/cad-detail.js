// Shared modal flow for STEP + DXF (the two CAD formats that use the
// same Three.js scene). Mermaid is a separate flow (PanZoom, no
// Three.js) — see mermaid.js.
//
// open/close functions take a `pushHistory` flag. UI-driven calls push;
// popstate-driven calls don't (the URL already changed).
//
// CAD detail open/close — handles both STEP and DXF, which differ only
// in extension, hash prefix, and loader. The shared Three.js scene
// (renderer, camera, controls) is reused across both: open swaps the
// canvas into the modal, the loader populates currentGroup, close
// teardown is identical.

import { state } from "./state.js";
import {
  scene,
  renderer,
  gizmoCanvas,
  canvasHost,
  resizeRenderer,
  startAnimate,
  stopAnimate,
  saveCameraState,
  applyCameraState,
} from "./scene.js";
import { loadStepFile } from "./step.js";
import { loadDxfFile } from "./dxf.js";
import { makeRulerToggle } from "./rulers.js";

function shortName(file, ext = ".step") {
  const parts = file.split("/");
  const name = parts.pop().replace(ext, "");
  const dir = parts.join("/");
  return { name, dir };
}

const CAD_KINDS = {
  step: { ext: ".step", hashPrefix: "step:", loader: loadStepFile },
  dxf:  { ext: ".dxf",  hashPrefix: "dxf:",  loader: loadDxfFile  },
};

export function openCadDetail(type, file, pushHistory = true) {
  const kind = CAD_KINDS[type];
  // Set currentDetail BEFORE touching location.hash. In Puppeteer (and
  // some browser configurations) setting location.hash can fire a
  // popstate that runs synchronously before this function returns; the
  // popstate handler dispatches on currentDetail, so it must already
  // reflect this open or we re-enter and end up with a duplicate
  // ContentViewer.
  state.currentDetail = { type, file };
  if (pushHistory) location.hash = kind.hashPrefix + encodeURIComponent(file);

  // Build the modal wrapper. Renderer canvas + gizmo canvas get moved
  // out of the hidden host into here; on close they go back. The
  // wrapper also hosts a centered loading pill that the loader toggles.
  const wrapper = document.createElement("div");
  wrapper.className = "cad-wrapper";
  wrapper.appendChild(renderer.domElement);
  wrapper.appendChild(gizmoCanvas);
  const loadingEl = document.createElement("div");
  loadingEl.className = "cad-loading";
  loadingEl.textContent = "Loading...";
  wrapper.appendChild(loadingEl);
  wrapper.appendChild(makeRulerToggle());

  state.currentCadWrapper = wrapper;

  // Re-fit the renderer whenever the wrapper's content box changes
  // (modal show, window resize, orientation change). The first
  // observation fires synchronously after observe(), giving us a
  // correct initial size as soon as the modal lays out.
  state.currentCadResizeObserver = new ResizeObserver(() => {
    if (renderer.domElement.parentElement === wrapper) resizeRenderer();
  });
  state.currentCadResizeObserver.observe(wrapper);

  ContentViewer.open({
    content: wrapper,
    filename: shortName(file, kind.ext).name,
    onOpen: () => {
      // Wrapper has its real size now — size the renderer + start the loop.
      resizeRenderer();
      startAnimate();
    },
    onClose: () => {
      // Persist camera state defensively. The debounced save (controls
      // "change" handler) usually has already fired, but if the user
      // dismissed mid-gesture the trailing save may not have. Use the
      // captured `file` rather than currentDetail — closeCadDetail(false)
      // clears currentDetail before invoking us, so we'd otherwise miss
      // the save on popstate-driven closes.
      saveCameraState(file);
      // Whether this onClose was triggered by a UI-driven dismissal
      // (Escape / X / backdrop / swipe) or by closeCadDetail(false)
      // from the popstate path. The popstate path clears currentDetail
      // before close fires; UI-driven closes leave it set.
      const wasUiDriven =
        state.currentDetail && state.currentDetail.type === type && state.currentDetail.file === file;
      stopAnimate();
      // Disconnect ResizeObserver before moving canvases (otherwise it
      // fires once more for the move into the hidden host).
      if (state.currentCadResizeObserver) {
        try { state.currentCadResizeObserver.disconnect(); } catch {}
        state.currentCadResizeObserver = null;
      }
      // Move canvases back to the hidden host so they stay mounted for
      // the next open. Don't dispose anything Three.js — renderer/
      // scene/controls are reused.
      try { canvasHost.appendChild(renderer.domElement); } catch {}
      try { canvasHost.appendChild(gizmoCanvas); } catch {}
      // Drop the loaded mesh — fresh load on next open.
      if (state.currentGroup) {
        scene.remove(state.currentGroup);
        state.currentGroup.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
        state.currentGroup = null;
      }
      state.currentCadWrapper = null;
      state.currentDetail = null;
      state.mountedDetail = null;
      // Pop the hash if the user dismissed the modal directly. popstate
      // already moved the URL, so don't double-pop.
      if (wasUiDriven && location.hash) history.back();
    },
  });

  kind.loader(file).then(() => applyCameraState(file));
}

// closeCadDetail is the entry point for the popstate path; UI-driven
// closes (Escape / X / backdrop / swipe) go through ContentViewer
// directly and run the modal's onClose. All teardown lives there.
export function closeCadDetail(pushHistory = true) {
  if (!ContentViewer.isOpen()) {
    // Already closed by the user — normalize state.
    state.currentDetail = null;
    state.mountedDetail = null;
    return;
  }
  // pushHistory=false comes from popstate (the URL already changed).
  // Clear currentDetail first so the onClose handler sees it as null
  // and skips the history.back() that would double-pop the stack.
  if (!pushHistory) {
    state.currentDetail = null;
  }
  ContentViewer.close();
}

// Backward-compatible thin wrappers — call sites in grid/sse/popstate
// still use the old per-format names.
export function openDetail(file, pushHistory = true)    { openCadDetail("step", file, pushHistory); }
export function openDxfDetail(file, pushHistory = true) { openCadDetail("dxf",  file, pushHistory); }
export function closeDetail(pushHistory = true)         { closeCadDetail(pushHistory); }
export function closeDxfDetail(pushHistory = true)      { closeCadDetail(pushHistory); }
