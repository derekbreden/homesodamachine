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
import { openMmdDetail, closeMmdDetail } from "./mermaid.js";
import { openDrawingDetail, closeDrawingDetail } from "./drawings.js";
import { openPcbDetail, closePcbDetail } from "./pcb.js";

// Browser/OS back button: navigate to whatever the new hash represents.
// ContentViewer handles Escape / X / backdrop / swipe-down on its own.
const HASH_PREFIXES = { "step:": "step", "dxf:": "dxf", "glb:": "glb", "mmd:": "mmd", "svg:": "drawing", "pcb:": "pcb" };
const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail, mmd: openMmdDetail, drawing: openDrawingDetail, pcb: openPcbDetail };

window.addEventListener("popstate", () => {
  const hash = location.hash ? decodeURIComponent(location.hash.slice(1)) : "";
  let want = { type: null, file: null };
  for (const [prefix, type] of Object.entries(HASH_PREFIXES)) {
    if (hash.startsWith(prefix)) { want = { type, file: hash.slice(prefix.length) }; break; }
  }
  // Already showing the right thing? Nothing to do.
  if (want.type && state.currentDetail
      && state.currentDetail.type === want.type && state.currentDetail.file === want.file) {
    return;
  }
  // Close whatever is currently open (cad / mmd / drawing close paths
  // differ because mmd and drawing use PanZoom while step/dxf use the
  // Three.js scene).
  if (state.currentDetail) {
    if (state.currentDetail.type === "mmd") closeMmdDetail(false);
    else if (state.currentDetail.type === "drawing") closeDrawingDetail(false);
    else if (state.currentDetail.type === "pcb") closePcbDetail(false);
    else closeCadDetail(false);
  }
  if (want.type) OPENERS[want.type](want.file, false);
});

// --- Initial route ---
// Prefer ?file=<step|dxf|mmd|svg> (notification deep link), fall back to
// hash. Extension drives which detail surface opens. occtPromise is needed
// for STEP only — DXF / MMD / SVG can open immediately.
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
    } else if (initialFile.endsWith(".svg")) {
      setTimeout(() => openDrawingDetail(initialFile, true), 100);
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
    } else if (hash.startsWith("svg:")) {
      const file = hash.slice(4);
      setTimeout(() => openDrawingDetail(file, false), 100);
    } else if (hash.startsWith("pcb:")) {
      const file = hash.slice(4);
      setTimeout(() => openPcbDetail(file, false), 100);
    } else {
      // Legacy hash format (just a step file path)
      occtPromise.then(() => setTimeout(() => openDetail(hash, false), 100));
    }
  }
}
