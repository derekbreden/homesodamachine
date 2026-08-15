// Moving between STEP models without leaving the modal.
//
// Selecting a component and taking the part it offers loads that part into the
// open modal and pushes a history entry. The trail of what you came through is
// drawn at the top-left as a breadcrumb, each step a button back to that model;
// the browser's own Back walks the same steps, because each step IS a history
// entry. Going back swaps the model in place — the modal, the canvas, the
// renderer and the render loop all stay up, so a drill down and back up costs
// one mesh fetch each way and never a teardown.
//
// route.js hands popstate here whenever both sides of a move are STEP.

import { state } from "./state.js";
import { saveCameraState, applyCameraState } from "./scene.js";
import { loadStepFile } from "./step.js";
import { mountScorecard } from "./scorecard-3d.js";
import { probeEditor } from "./component-edit.js";

// The models above the one on screen, outermost first. Reset whenever a move
// lands somewhere the trail doesn't explain — a fresh open, a Find that jumped
// sideways to another assembly.
let trail = [];

function label(file) {
  return file.slice(file.lastIndexOf("/") + 1).replace(/\.step$/i, "");
}

export function resetTrail(file) {
  trail = [];
  syncCrumb(file);
}

// ── Breadcrumb ──────────────────────────────────────────────────────────────
// Stands where ContentViewer's filename pill stands, and takes its place while
// there is a trail to show; with no trail the pill says it on its own.
function filenamePill(wrapper) {
  const card = wrapper && wrapper.closest(".cv-card");
  return card ? card.querySelector(".cv-filename") : null;
}

export function setFilename(file) {
  const pill = filenamePill(state.currentCadWrapper);
  if (pill) pill.textContent = label(file);
}

function syncCrumb(file) {
  const wrapper = state.currentCadWrapper;
  if (!wrapper) return;
  let crumb = wrapper.querySelector(".cad-crumb");
  const pill = filenamePill(wrapper);

  if (!trail.length) {
    if (crumb) crumb.classList.remove("show");
    if (pill) pill.style.display = "";
    return;
  }
  if (!crumb) {
    crumb = document.createElement("div");
    crumb.className = "cad-crumb";
    crumb.setAttribute("aria-label", "Breadcrumb");
    wrapper.appendChild(crumb);
  }
  crumb.textContent = "";
  trail.forEach((ancestor, i) => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "cad-crumb-step";
    btn.textContent = label(ancestor);
    btn.title = `Back to ${ancestor}`;
    // Walking history rather than loading directly, so the entries this drill
    // pushed come off the stack with it.
    btn.addEventListener("click", () => history.go(-(trail.length - i)));
    crumb.appendChild(btn);
    const sep = document.createElement("span");
    sep.className = "cad-crumb-sep";
    sep.textContent = "/";
    crumb.appendChild(sep);
  });
  const here = document.createElement("span");
  here.className = "cad-crumb-here";
  here.textContent = label(file);
  crumb.appendChild(here);
  crumb.classList.add("show");
  crumb.scrollLeft = crumb.scrollWidth;
  if (pill) pill.style.display = "none";
}

// ── The move ────────────────────────────────────────────────────────────────
// Everything the open modal shows that belongs to a particular file, brought
// over to `file`: the camera it was last left at, its name, its scorecard bar
// and the port/box chips that bar mounts, and which file the editor writes to.
async function showStep(file, push) {
  const from = state.mountedDetail && state.mountedDetail.file;
  if (!from || file === from) return false;
  saveCameraState(from);
  state.currentDetail = { type: "step", file };
  if (push) location.hash = "step:" + encodeURIComponent(file);

  await loadStepFile(file);
  if (!state.mountedDetail || state.mountedDetail.file !== file) return false;

  applyCameraState(file);
  setFilename(file);
  syncCrumb(file);
  if (state.currentCadWrapper) mountScorecard(state.currentCadWrapper, file);
  probeEditor(file);
  return true;
}

// The component picker's offer, taken.
export async function drillTo(file) {
  const from = state.mountedDetail && state.mountedDetail.file;
  if (!from || file === from) return;
  trail.push(from);
  if (!(await showStep(file, true))) trail.pop();
}

// popstate landed on another STEP with this modal already open. Same move, no
// new history entry — and the trail follows the URL rather than leading it, so
// forward/back and a hand-edited hash all leave it describing what is shown.
export async function routeToStep(file) {
  const at = trail.lastIndexOf(file);
  if (at >= 0) trail = trail.slice(0, at);
  else if (trail.length && file !== (state.mountedDetail && state.mountedDetail.file)) trail = [];
  await showStep(file, false);
}

// A file swap that isn't a drill — the Find box jumping to where a pick lives.
// The trail can't describe it, so it says nothing rather than something wrong.
export async function jumpToStep(file) {
  trail = [];
  const moved = await showStep(file, false);
  if (moved) history.replaceState(null, "", "#step:" + encodeURIComponent(file));
  return moved;
}
