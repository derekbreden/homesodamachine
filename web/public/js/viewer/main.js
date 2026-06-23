// Viewer entry point. Loaded as <script type="module"> from
// lib/templates/viewer-body.html. Wires the modules together:
//
//   1. Read #grid into state, set the active nav class and document.title.
//   2. Expose window.__hsm for the headless render tools (Puppeteer
//      drives loadStepFile / loadDxfFile and reads scene/camera).
//   3. fetchFiles() → buildGrid() → applyInitialRoute(occtPromise).
//   4. Side-effect import ./live.js to register the SSE listeners.

import * as THREE from "three";
import { state } from "./state.js";
import { buildGrid, currentSection } from "./grid.js";
import { applyInitialRoute } from "./route.js";
import { occtPromise, loadStepFile } from "./step.js";
import { loadDxfFile } from "./dxf.js";
import { renderer, scene, camera, controls } from "./scene.js";
import "./live.js";

state.gridEl = document.getElementById("grid");

// Exposed for headless render tooling (tools/render/render-step.js,
// render-dxf.js, render-step-side-by-side.js). Tiny escape hatch so
// Puppeteer can pose the camera and trigger a render without needing
// to drive OrbitControls via synthetic events. Shape is load-bearing
// for those tools — keep it stable.
window.__hsm = {
  THREE, renderer, scene, camera, controls,
  loadStepFile, loadDxfFile,
  get currentGroup() { return state.currentGroup; },
  get mountedStepFile() { return state.mountedDetail?.type === "step" ? state.mountedDetail.file : null; },
  get mountedDxfFile()  { return state.mountedDetail?.type === "dxf"  ? state.mountedDetail.file : null; },
};

function setupNav() {
  // The shell already renders the nav with absolute hrefs (/3d, /charts,
  // /drawings); this just sets the active class for client-side
  // navigation cases.
  const section = currentSection();
  for (const a of document.querySelectorAll("#site-nav a[data-nav]")) {
    a.classList.toggle("active", a.dataset.nav === section);
  }

  const titleMap = {
    parts: "Parts · Home Soda Machine",
    charts: "Charts · Home Soda Machine",
    drawings: "Drawings · Home Soda Machine",
    pcb: "Boards · Home Soda Machine",
  };
  document.title = titleMap[section] || document.title;
}

export async function fetchFiles() {
  const [stepResp, mmdResp, dxfResp, drawingResp, pcbResp] = await Promise.all([
    fetch("/api/steps"),
    fetch("/api/mermaid"),
    fetch("/api/dxf"),
    fetch("/api/drawings"),
    fetch("/api/pcb"),
  ]);
  state.allFiles = (await stepResp.json()).sort();
  state.mmdFiles = (await mmdResp.json()).sort();
  // PCB boards arrive pre-sorted from the server (by source path).
  state.pcbBoards = await pcbResp.json();
  // /api/dxf returns objects with thickness_mm + material from each
  // part's sidecar (hardware/README.md). Cache the metadata so the
  // viewer can extrude on open without a second round-trip.
  const dxfData = await dxfResp.json();
  state.dxfMeta.clear();
  for (const d of dxfData) state.dxfMeta.set(d.path, d);
  state.dxfFiles = dxfData.map((d) => d.path).sort();
  state.drawingFiles = (await drawingResp.json()).sort();
  buildGrid();
}

setupNav();
fetchFiles().then(() => applyInitialRoute(occtPromise));
