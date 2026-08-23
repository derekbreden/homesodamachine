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

// ── The path in the URL ─────────────────────────────────────────────────────
// THE HASH CARRIES THE WHOLE WALK, outermost first, so a reload or a pasted link
// lands where it says and with the way back out of it:
//
//   #step:manifold-layout%2Fenclosure-assembly.step/cold-core-layout%2Fcold-core-assembly.step
//
// Each step is percent-encoded, which takes the `/` out of a path and leaves the
// separator as the only bare one. A one-step path is a file on its own, which is
// what every link written before there were paths says and what the Find box and
// a card still write.
const STEP_PREFIX = "step:";

export function stepHash(files) {
  return STEP_PREFIX + files.map(encodeURIComponent).join("/");
}

const decode = (s) => { try { return decodeURIComponent(s); } catch { return s; } };

/** The models a `step:` hash names, outermost first. `raw` is undecoded. */
export function parseStepHash(raw) {
  const body = raw.slice(STEP_PREFIX.length);
  const parts = body.split("/").map(decode);
  // A hand-typed path that never went through `stepHash` carries bare `/` and
  // splits into pieces that are not models — it is one file, and it says so by
  // having a piece that does not end in `.step`.
  return parts.length > 1 && parts.every((p) => /\.step$/i.test(p)) ? parts : [decode(body)];
}

// HOW MANY HISTORY ENTRIES STAND BETWEEN THE PAGE AND THIS MODEL. Dismissing the
// modal pops exactly these, so a walk three models deep closes in one go rather
// than stepping back up through the models it was reached by, and a model opened
// from a pasted link — which pushed nothing — closes without leaving the page.
//
// A drill adds one, and going back takes one off, so this counts where the walk
// stands rather than how far it has been: back twice and then close pops two,
// not four.
let pushed = 0;

export const walkDepth = () => pushed;

// The walk this file is the end of. `files` is outermost first and includes the
// model being shown, so a one-step walk is a model opened on its own.
export function setTrail(files, pushedHistory = false) {
  trail = files.slice(0, -1);
  pushed = pushedHistory ? 1 : 0;
  syncCrumb(files[files.length - 1]);
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

  // Nothing above this model: the pill says its name on its own, and the crumb
  // stands empty rather than hidden-but-still-reading as the last walk taken.
  if (!trail.length) {
    if (crumb) { crumb.classList.remove("show"); crumb.textContent = ""; }
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
  if (push) {
    location.hash = stepHash([...trail, file]);
    pushed += 1;
  }

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
// new history entry — and the trail is taken from the URL rather than guessed
// against it, so forward, back and a pasted path all leave it describing what
// is shown. `files` is the whole walk, outermost first.
export async function routeToStep(files) {
  const file = files[files.length - 1];
  // The move is one history entry per level, so the levels it crosses are the
  // entries it crosses — forwards or back.
  pushed = Math.max(0, pushed + (files.length - 1) - trail.length);
  trail = files.slice(0, -1);
  await showStep(file, false);
  syncCrumb(file);
}

// A file swap that isn't a drill — the Find box jumping to where a pick lives.
// The trail can't describe it, so it says nothing rather than something wrong.
export async function jumpToStep(file) {
  trail = [];
  const moved = await showStep(file, false);
  if (moved) history.replaceState(null, "", "#" + stepHash([file]));
  return moved;
}
