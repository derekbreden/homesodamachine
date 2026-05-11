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
  closeCadDetail,
} from "./cad-detail.js";
import { openMmdDetail, closeMmdDetail } from "./mermaid.js";

// Browser/OS back button: navigate to whatever the new hash represents.
// ContentViewer handles Escape / X / backdrop / swipe-down on its own.
const HASH_PREFIXES = { "step:": "step", "dxf:": "dxf", "mmd:": "mmd" };
const OPENERS = { step: openDetail, dxf: openDxfDetail, mmd: openMmdDetail };

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
  // Close whatever is currently open (cad and mmd close paths differ
  // because mmd uses PanZoom and not the Three.js scene).
  if (state.currentDetail) {
    if (state.currentDetail.type === "mmd") closeMmdDetail(false);
    else closeCadDetail(false);
  }
  if (want.type) OPENERS[want.type](want.file, false);
});

// --- Initial route ---
// Prefer ?file=<step|dxf|mmd> (notification deep link), fall back to hash.
// Extension drives which detail surface opens. occtPromise is needed for
// STEP only — DXF and MMD can open immediately.
export function applyInitialRoute(occtPromise) {
  const initialParams = new URLSearchParams(location.search);
  const initialFile = initialParams.get("file");
  if (initialFile) {
    if (initialFile.endsWith(".mmd")) {
      setTimeout(() => openMmdDetail(initialFile, true), 100);
    } else if (initialFile.endsWith(".dxf")) {
      setTimeout(() => openDxfDetail(initialFile, true), 100);
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
    } else if (hash.startsWith("mmd:")) {
      const file = hash.slice(4);
      setTimeout(() => openMmdDetail(file, false), 100);
    } else {
      // Legacy hash format (just a step file path)
      occtPromise.then(() => setTimeout(() => openDetail(hash, false), 100));
    }
  }
}
