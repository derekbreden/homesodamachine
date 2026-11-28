// Open the model or material named by a Parts link and preserve its modal history.

import { state } from "./state.js";
import {
  openDetail,
  openDxfDetail,
  openGlbDetail,
  closeCadDetail,
} from "./cad-detail.js";
import { routeToStep, parseStepHash, stepFind } from "./step-nav.js";
import { findWhenMounted } from "./pick-find.js";
import { openMaterial } from "./material-nav.js";
import { modelForMaterial } from "/contracts/materials.js";
import { materialTab } from "/contracts/material-tabs.js";
import { ASSEMBLIES } from "/contracts/parts-tree.js";
import { stepLocation } from "/contracts/step-locations.js";
import { isViewerHash } from "/contracts/viewer-links.js";

const decodeHash = (s) => { try { return decodeURIComponent(s); } catch { return s; } };

// Browser/OS back button: navigate to whatever the new hash represents.
// ContentViewer handles Escape / X / backdrop / swipe-down on its own.
const HASH_PREFIXES = { "step:": "step", "dxf:": "dxf", "glb:": "glb" };
const OPENERS = { step: openDetail, dxf: openDxfDetail, glb: openGlbDetail };

// WHAT A HASH NAMES, read once for both surfaces below. A `step:` hash carries
// the whole walk and is split before it is decoded. Older links name a STEP
// file without a prefix.
function wantFromHash(raw) {
  if (raw.startsWith("material:")) {
    const [identity, query = ""] = raw.slice("material:".length).split("?");
    const id = decodeHash(identity);
    const params = new URLSearchParams(query);
    const tab = materialTab(params.get("tab")).tab ? params.get("tab") : null;
    const panel = params.get("panel");
    const instance = params.get("instance");
    const view = params.get("view");
    const file = modelForMaterial(state.materialCatalog, id)?.file;
    const remembered = history.state?.materialPath;
    const path = file && Array.isArray(remembered) && remembered.at(-1) === file ? remembered : [file];
    return { type: file ? "step" : "material", file: file || id, path: file ? path : null, material: id, tab, panel, instance, view,
      benchCase: params.get("case"), landmark: params.get("landmark") };
  }
  for (const [prefix, type] of Object.entries(HASH_PREFIXES)) {
    if (!raw.startsWith(prefix)) continue;
    if (type === "step") {
      const path = parseStepHash(raw);
      return { type, file: path[path.length - 1], path, find: stepFind(raw), panel: new URLSearchParams(raw.split("?")[1]).get("panel") };
    }
    return { type, file: decodeHash(raw).slice(prefix.length), path: null };
  }
  const file = isViewerHash(raw) ? decodeHash(raw) : null;
  return { type: file ? "step" : null, file, path: file ? [file] : null };
}

function followViewerHistory() {
  if (state.dismissViewerRoute) {
    state.dismissViewerRoute = false;
    history.replaceState(null, "", location.pathname + location.search);
    return;
  }
  const want = wantFromHash(location.hash ? location.hash.slice(1) : "");
  const target = stepTarget(want);
  if (want.find) findWhenMounted(want.file, want.find);
  // Already showing the right thing? Nothing to do.
  if (want.type && state.currentDetail
      && state.currentDetail.type === want.type && state.currentDetail.file === want.file) {
    const apply = () => {
      if (want.material) state.materialPanel?.setRoot(want.material);
      state.materialPanel?.applyRoute(want);
    };
    if (want.type === "step" && state.mountedDetail?.file === want.file) routeToStep(want.path, target).then(apply);
    else apply();
    return;
  }
  // STEP to STEP with the modal already up — the drill-down's own move, and the
  // way back out of it. Swapping the model keeps the modal, the canvas and the
  // render loop; closing and reopening would tear down the surface being
  // navigated, and ContentViewer.close defers its teardown past the reopen.
  if (want.type === "step" && state.currentDetail && state.currentDetail.type === "step"
      && ContentViewer.isOpen()) {
    const apply = () => {
      if (want.material) state.materialPanel?.setRoot(want.material);
      state.materialPanel?.applyRoute(want);
    };
    const move = routeToStep(want.path, target);
    if (want.instance) apply();
    else move.then(apply);
    return;
  }
  if (want.material && (want.type === "material" || state.currentDetail?.type === "material")) {
    openMaterial(want.material, false, want);
    return;
  }
  // Close the open workspace with its own teardown.
  if (state.currentDetail) {
    if (state.currentDetail.type === "material") { state.currentDetail = null; ContentViewer.close(); }
    else closeCadDetail(false);
  }
  if (want.material) openMaterial(want.material, false, want);
  else if (want.type === "step") { openDetail(want.file, false, want.path, target); state.materialPanel?.applyRoute(want); }
  else if (want.type) OPENERS[want.type](want.file, false);
}

// --- Initial route ---
// On first load: a `?file=` deep link (what a notification writes), else the
// hash (what a bookmark or a pasted link carries).

// Extension → the surface a `?file=` link opens. Anything the table does not
// name is a STEP, which is what a hand-written link and every render tool pass.
const FILE_KINDS = { ".dxf": "dxf", ".glb": "glb" };
const stepTarget = ({ instance, find }) => instance ? { instance } : find ? { find } : null;

function openFile(want, pushHistory) {
  const { type, file, path, find } = want;
  if (type !== "step") return OPENERS[type](file, pushHistory);
  if (find) findWhenMounted(file, find);
  openDetail(file, pushHistory, path, stepTarget(want));
  state.materialPanel?.applyRoute(want);
}

export function openViewerHash(hash, pushHistory = false) {
  const want = wantFromHash(hash.slice(1));
  if (want.material) return openMaterial(want.material, pushHistory, want);
  // A surface link in an open model navigates its canvas and preserves the material entry for Back.
  if (want.find && pushHistory && state.currentDetail?.type === "step") {
    history.pushState(null, "", hash);
    return followViewerHistory();
  }
  if (want.type) {
    openFile(want, pushHistory);
    if (pushHistory && location.hash !== hash) history.replaceState(history.state, "", hash);
  }
}

export function startViewerRoutes() {
  window.addEventListener("popstate", followViewerHistory);
  const query = new URLSearchParams(location.search);
  const linked = query.get("file");
  const find = query.get("find");
  if (linked || (find && !isViewerHash(location.hash))) {
    const file = linked || ASSEMBLIES[0].model;
    const extension = stepLocation(file).file.match(/\.[a-z]+$/i)?.[0]?.toLowerCase();
    return openFile({ type: FILE_KINDS[extension] || "step", file, find }, true);
  }
  return openViewerHash(location.hash);
}
