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
import { routeToStep, parseStepHash, stepFind } from "./step-nav.js";
import { findWhenMounted } from "./pick-find.js";
import { openMaterial } from "./material-nav.js";
import { modelForMaterial } from "/contracts/materials.js";

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
  if (raw.startsWith("material:")) {
    const [identity, query = ""] = raw.slice("material:".length).split("?");
    const id = decodeHash(identity);
    const tab = new URLSearchParams(query).get("tab") === "bom" ? "bom" : null;
    const file = modelForMaterial(state.materialCatalog, id)?.file;
    const remembered = history.state?.materialPath;
    const path = file && Array.isArray(remembered) && remembered.at(-1) === file ? remembered : [file];
    return { type: file ? "step" : "material", file: file || id, path: file ? path : null, material: id, tab };
  }
  for (const [prefix, type] of Object.entries(HASH_PREFIXES)) {
    if (!raw.startsWith(prefix)) continue;
    if (type === "step") {
      const path = parseStepHash(raw);
      return { type, file: path[path.length - 1], path, find: stepFind(raw) };
    }
    return { type, file: decodeHash(raw).slice(prefix.length), path: null };
  }
  return { type: null, file: null, path: null };
}

window.addEventListener("popstate", () => {
  if (state.dismissViewerRoute) {
    state.dismissViewerRoute = false;
    history.replaceState(null, "", location.pathname + location.search);
    return;
  }
  const want = wantFromHash(location.hash ? location.hash.slice(1) : "");
  if (want.find) findWhenMounted(want.file, want.find);
  // Already showing the right thing? Nothing to do.
  if (want.type && state.currentDetail
      && state.currentDetail.type === want.type && state.currentDetail.file === want.file) {
    if (want.material) state.materialPanel?.setRoot(want.material);
    if (want.tab === "bom") state.materialPanel?.showBom();
    return;
  }
  // STEP to STEP with the modal already up — the drill-down's own move, and the
  // way back out of it. Swapping the model keeps the modal, the canvas and the
  // render loop; closing and reopening would tear down the surface being
  // navigated, and ContentViewer.close defers its teardown past the reopen.
  if (want.type === "step" && state.currentDetail && state.currentDetail.type === "step"
      && ContentViewer.isOpen()) {
    routeToStep(want.path).then(() => {
      if (want.material) state.materialPanel?.setRoot(want.material);
      if (want.tab === "bom") state.materialPanel?.showBom();
    });
    return;
  }
  if (want.material && (want.type === "material" || state.currentDetail?.type === "material")) {
    openMaterial(want.material, false, { tab: want.tab });
    return;
  }
  // Close whatever is currently open (cad / mmd / pcb close paths differ
  // because mmd and pcb use PanZoom while step/dxf use the Three.js scene).
  if (state.currentDetail) {
    if (state.currentDetail.type === "mmd") closeMmdDetail(false);
    else if (state.currentDetail.type === "pcb") closePcbDetail(false);
    else if (state.currentDetail.type === "material") { state.currentDetail = null; ContentViewer.close(); }
    else closeCadDetail(false);
  }
  if (want.material) openMaterial(want.material, false, { tab: want.tab });
  else if (want.type === "step") openDetail(want.file, false, want.path);
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
  if (want.find) findWhenMounted(want.file, want.find);
  if (want.material) { occtPromise.then(() => openMaterial(want.material, false, { tab: want.tab })); }
  else if (want.type) open(want.type, want.file, false, want.path);
  else open("step", decodeHash(raw), false);
}
