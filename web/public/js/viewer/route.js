// URL → state translation. Two surfaces:
//
//   - popstate: handles browser back/forward + the sentinel pop pushed
//     by ContentViewer when the user dismisses the modal directly.
//     Decides what's open now, what should be open per the URL, closes
//     the wrong thing and opens the right one.
//
//   - applyInitialRoute(occtPromise): on first load, deep-link via
//     ?file=<step|dxf|mmd> (notification) or location.hash (bookmark).
//     Extension drives which detail surface opens. STEP needs to wait
//     on the occt-import-js loader; DXF and MMD don't.

import { state } from "./state.js";
import {
  openDetail,
  openDxfDetail,
  openGlbDetail,
  closeCadDetail,
} from "./cad-detail.js";
// Non-CAD detail kinds resolve their open/close through detail-shims.js so a
// viewer-code edit is picked up (open re-imports fresh; close is the static,
// synchronous teardown — see detail-shims.js).
import {
  openMmdDetail, closeMmdDetail,
  openPcbDetail, closePcbDetail,
} from "./detail-shims.js";
import { routeToStep } from "./step-nav.js";

// Browser/OS back button: navigate to whatever the new hash represents.
// ContentViewer handles Escape / X / backdrop / swipe-down on its own.
const HASH_PREFIXES = { "step:": "step", "dxf:": "dxf", "glb:": "glb", "mmd:": "mmd", "pcb:": "pcb" };
const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail, mmd: openMmdDetail, pcb: openPcbDetail };

window.addEventListener("popstate", () => {
  // A `step:` hash carries the whole walk and is split before it is decoded —
  // every other kind is one file and decodes whole (step-nav.js's parseStepHash).
  const raw = location.hash ? location.hash.slice(1) : "";
  const hash = decodeHash(raw);
  let want = { type: null, file: null, path: null };
  for (const [prefix, type] of Object.entries(HASH_PREFIXES)) {
    if (!raw.startsWith(prefix)) continue;
    if (type === "step") {
      const path = parseStepHash(raw);
      want = { type, file: path[path.length - 1], path };
    } else {
      want = { type, file: hash.slice(prefix.length), path: null };
    }
    break;
  }
  // Already showing the right thing? Nothing to do.
  if (want.type && state.currentDetail
      && state.currentDetail.type === want.type && state.currentDetail.file === want.file) {
    return;
  }
  // STEP to STEP with the modal already up — the drill-down's own move, and the
  // way back out of it. Swapping the model keeps the modal, the canvas and the
  // render loop; closing and reopening would tear down the surface being
  // navigated, and ContentViewer.close defers its teardown past the reopen.
  if (want.type === "step" && state.currentDetail && state.currentDetail.type === "step"
      && ContentViewer.isOpen()) {
    routeToStep(want.path);
    return;
  }
  // Close whatever is currently open (cad / mmd / pcb close paths differ
  // because mmd and pcb use PanZoom while step/dxf use the Three.js scene).
  if (state.currentDetail) {
    if (state.currentDetail.type === "mmd") closeMmdDetail(false);
    else if (state.currentDetail.type === "pcb") closePcbDetail(false);
    else closeCadDetail(false);
  }
  if (want.type === "step") openDetail(want.file, false, want.path);
  else if (want.type) OPENERS[want.type](want.file, false);
});

// --- Initial route ---
// Prefer ?file=<step|dxf|mmd> (notification deep link), fall back to hash.
// The file's extension drives which detail surface opens; occtPromise is needed
// for STEP only, and every other kind can open immediately.
export function applyInitialRoute(occtPromise) {
  const initialParams = new URLSearchParams(location.search);
  const initialFile = initialParams.get("file");
  if (initialFile) {
    if (initialFile.endsWith(".mmd")) {
      setTimeout(() => openMmdDetail(initialFile, true), 100);
    } else if (initialFile.endsWith(".dxf")) {
      setTimeout(() => openDxfDetail(initialFile, true), 100);
    } else if (initialFile.endsWith(".glb")) {
      setTimeout(() => openGlbDetail(initialFile, true), 100);
    } else if (initialFile.endsWith(".tsx")) {
      setTimeout(() => openPcbDetail(initialFile, true), 100);
    } else {
      occtPromise.then(() => setTimeout(() => openDetail(initialFile, true), 100));
    }
  } else if (location.hash) {
    const hash = decodeURIComponent(location.hash.slice(1));
    if (hash.startsWith("step:")) {
      const file = hash.slice(5);
      occtPromise.then(() => setTimeout(() => openDetail(file, false), 100));
    } else if (hash.startsWith("dxf:")) {
      const file = hash.slice(4);
      setTimeout(() => openDxfDetail(file, false), 100);
    } else if (hash.startsWith("glb:")) {
      const file = hash.slice(4);
      setTimeout(() => openGlbDetail(file, false), 100);
    } else if (hash.startsWith("mmd:")) {
      const file = hash.slice(4);
      setTimeout(() => openMmdDetail(file, false), 100);
    } else if (hash.startsWith("pcb:")) {
      const file = hash.slice(4);
      setTimeout(() => openPcbDetail(file, false), 100);
    } else {
      // Legacy hash format (just a step file path)
      occtPromise.then(() => setTimeout(() => openDetail(hash, false), 100));
    }
  }
}
