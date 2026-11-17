// Load the shared model workspace when Parts opens a model or Guides opens its library.

import * as THREE from "three";
import { state } from "./state.js";
import { buildGrid } from "./grid.js";
import { startViewerRoutes } from "./route.js";
import { loadStepFile } from "./step.js";
import { loadDxfFile } from "./dxf.js";
import { renderer, scene, camera, controls } from "./scene.js";
import "./live.js";

export { openViewerHash } from "./route.js";

state.gridEl = document.getElementById("grid");

// Exposed for tools/render/render-dxf.js. Tiny escape hatch so
// Puppeteer can pose the camera and trigger a render without needing
// to drive OrbitControls via synthetic events. Shape defined in
// web/contracts/hsm-globals.js and load-bearing for those tools —
// keep this object in sync with that typedef.
window.__hsm = {
  THREE, renderer, scene, camera, controls,
  loadStepFile, loadDxfFile,
  get currentGroup() { return state.currentGroup; },
  get mountedStepFile() { return state.mountedDetail?.type === "step" ? state.mountedDetail.file : null; },
  get mountedDxfFile()  { return state.mountedDetail?.type === "dxf"  ? state.mountedDetail.file : null; },
};

export async function fetchFiles() {
  const [stepResp, dxfResp, docResp, objResp, catalog] = await Promise.all([
    fetch("/api/steps"),
    fetch("/api/dxf"),
    state.gridEl ? fetch("/api/documents") : null,
    fetch("/api/objects"),
    fetch("/api/materials").catch(() => null),
  ]);
  // Where each model's bytes are on the store, when the store has a public address; empty
  // otherwise, and every loader reads this site's own routes.
  state.memberUrls.clear();
  try {
    const { objects } = await objResp.json();
    for (const [file, url] of Object.entries(objects ?? {})) state.memberUrls.set(file, url);
  } catch { /* the site's own routes answer for every model */ }
  state.allFiles = (await stepResp.json()).sort();
  state.materialCatalog = catalog?.ok ? await catalog.json() : null;
  state.materialCatalogTag = catalog?.ok ? catalog.headers.get("ETag") : null;
  // /api/dxf returns objects with thickness_mm + material from each
  // part's sidecar (hardware/README.md). Cache the metadata so the
  // viewer can extrude on open without a second round-trip.
  const dxfData = await dxfResp.json();
  state.dxfMeta.clear();
  for (const d of dxfData) state.dxfMeta.set(d.path, d);
  if (docResp) {
    state.documents = await docResp.json();
    buildGrid();
  }
  state.materialPanel?.sync();
}

export const viewerReady = fetchFiles().then(startViewerRoutes);
