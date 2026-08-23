// URL → state translation. Two surfaces:
//
//   - popstate: handles browser back/forward + the sentinel pop pushed
//     by ContentViewer when the user dismisses the modal directly.
//     Decides what's open now, what should be open per the URL, closes
//     the wrong thing and opens the right one.
//
//   - applyInitialRoute(occtPromise): on first load, deep-link via
//     ?file=<path> (notification), where the extension names the surface,
//     or location.hash (bookmark), where the prefix does. STEP waits on the
//     occt-import-js loader; nothing else does.
//
// Both read the hash through `wantFromHash` and open through `OPENERS`, so the
// prefixes are stated once and the two surfaces cannot come to disagree about
// what a link means.

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
import { routeToStep, parseStepHash } from "./step-nav.js";

const decodeHash = (s) => { try { return decodeURIComponent(s); } catch { return s; } };

// Browser/OS back button: navigate to whatever the new hash represents.
// ContentViewer handles Escape / X / backdrop / swipe-down on its own.
const HASH_PREFIXES = { "step:": "step", "dxf:": "dxf", "glb:": "glb", "mmd:": "mmd", "pcb:": "pcb" };
const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail, mmd: openMmdDetail, pcb: openPcbDetail };

// WHAT A HASH NAMES, read once for both surfaces below. A `step:` hash carries
// the whole walk and is split before it is decoded; every other kind is one file
// and decodes whole (step-nav.js's parseStepHash). A hash matching no prefix
// names nothing here — popstate reads that as "close what is open", and the
// initial route reads it as the bare STEP path a link written before the
// prefixes says.
function wantFromHash(raw) {
  for (const [prefix, type] of Object.entries(HASH_PREFIXES)) {
    if (!raw.startsWith(prefix)) continue;
    if (type === "step") {
      const path = parseStepHash(raw);
      return { type, file: path[path.length - 1], path };
    }
    return { type, file: decodeHash(raw).slice(prefix.length), path: null };
  }
  return { type: null, file: null, path: null };
}

window.addEventListener("popstate", () => {
  const want = wantFromHash(location.hash ? location.hash.slice(1) : "");
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
// On first load: a `?file=` deep link (what a notification writes), else the
// hash (what a bookmark or a pasted link carries).

// Extension → the surface a `?file=` link opens. Anything the table does not
// name is a STEP, which is what a hand-written link and every render tool pass.
const FILE_KINDS = { ".mmd": "mmd", ".dxf": "dxf", ".glb": "glb", ".tsx": "pcb" };

export function applyInitialRoute(occtPromise) {
  // A STEP waits on the occt loader; every other kind can open at once. The
  // timeout lets the grid finish laying out under the modal about to cover it.
  const open = (type, file, push, path = null) => {
    const go = () => setTimeout(
      () => (type === "step" ? openDetail(file, push, path) : OPENERS[type](file, push)), 100);
    if (type === "step") occtPromise.then(go); else go();
  };

  const linked = new URLSearchParams(location.search).get("file");
  if (linked) {
    open(FILE_KINDS[linked.slice(linked.lastIndexOf("."))] || "step", linked, true);
    return;
  }
  if (!location.hash) return;
  const raw = location.hash.slice(1);
  const want = wantFromHash(raw);
  if (want.type) open(want.type, want.file, false, want.path);
  else open("step", decodeHash(raw), false);
}
