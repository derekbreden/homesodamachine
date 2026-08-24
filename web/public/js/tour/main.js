// THE PLAYER. Everything the tour is made of is somewhere else — the words and
// the angles in contracts/tour-water.js, the pose arithmetic in frame.js, the
// move in flight.js, the light in spotlight.js — and this runs the clock over
// them.
//
// IT IS ONE CONTINUOUS SESSION AND NOT A SLIDESHOW. There are two phases and
// neither of them is still: a FLIGHT between beats, which swings out to a wide
// shot holding both subjects and comes back in, and a DWELL on a beat, which
// keeps drifting a few degrees while the words are read. The camera stops only
// when a hand grabs it.
//
// THE MODEL CAN CHANGE UNDER THE CAMERA. The carbonator is not a body of the
// enclosure — it is inside the cold core, which the enclosure carries as one
// foam block — so the beats inside the vessel are shown on the cold core's own
// model, seated back into the machine's frame (contracts/tour-water.js
// `frames`). The camera does not move for the swap: it pulls back to a shot of
// the block, the picture dips through the background colour, and the block's
// insides are standing where the block was.
//
// WHERE THE PLAYER IS IS IN THE URL, one-based, so a reload lands on the beat
// you were looking at. That is the iteration loop: change a word or an angle,
// push, and the deploy reloads the page onto the same beat.

import * as THREE from "three";
import { TOUR } from "/contracts/tour-water.js";
import { state } from "../viewer/state.js";
import {
  renderer, gizmoCanvas, scene, camera, controls, resizeRenderer, startAnimate,
} from "../viewer/scene.js";
import { loadStepFile } from "../viewer/step.js";
import { isXrayEnabled, setXrayEnabled } from "../viewer/xray.js";
import { applyHiddenComponents, isolateComponent } from "../viewer/component-picker.js";
import { boxOfParts, unionBoxes, poseFor, boxOfGroup } from "./frame.js";
import { flight, tween, driftAt, durationFor, midHeading, toOrbit, vertigoScale } from "./flight.js";
import * as spotlight from "./spotlight.js";
import { mountHud } from "./hud.js";
import { mountTags } from "./tags.js";
import { dissolve, restoreModel, setSection } from "./ghost.js";

const STEPS = TOUR.steps;
const N = STEPS.length;

// How much bigger than both subjects together the wide shot is. Tight enough
// that the pull-back is clearly TO something rather than merely away.
const MID_PAD = 1.12;
// And the pull-back before a model swap, which only has to clear the block.
const SWAP_PAD = 1.4;
// Reading pace for a beat with no `dwell` of its own: words at a calm rate,
// plus a moment to look at what is lit before and after the sentence.
const MS_PER_WORD = 230;
const READ_BASE = 1100;
const READ_FLOOR = 2600;
// A beat that only changes what is lit does not travel. The words and the light
// cross over this long while the camera carries on with the drift it was
// already making, which is what keeps a chapter one shot rather than six.
const SWING_MS = 750;
const SWAP_OUT_MS = 1500;
const VEIL_MS = 620;

// ── stage ───────────────────────────────────────────────────────────────────
const stage = document.getElementById("tour-stage");
stage.append(renderer.domElement, gizmoCanvas);
const loadingEl = document.createElement("div");
loadingEl.className = "cad-loading";
loadingEl.append(document.createElement("span"));
stage.append(loadingEl);
const veil = document.createElement("div");
veil.className = "tour-veil";
stage.append(veil);
state.currentCadWrapper = stage;

// The stage's box, read on change rather than every frame — the pins project
// into it sixty times a second and a layout read per frame is a layout per
// frame.
let stageRect = { width: 0, height: 0 };
new ResizeObserver(() => {
  resizeRenderer();
  stageRect = stage.getBoundingClientRect();
  onResize();
}).observe(stage);
resizeRenderer();
stageRect = stage.getBoundingClientRect();
startAnimate();

// ── models and their seats ──────────────────────────────────────────────────
const seats = new Map();     // body name -> its Box3 in the machine's own frame
let loadedModel = null;

const modelOf = (i) => {
  for (let k = i; k >= 0; k--) if (STEPS[k].model) return STEPS[k].model;
  return TOUR.model;
};

// WHAT IS SHOWN ALONE AT THIS BEAT. Carried forward from the last beat that
// stated one, the way `model` is — and `isolate: null` is a statement, so a
// chapter can put the machine back.
const isolateOf = (i) => {
  for (let k = i; k >= 0; k--) if ("isolate" in STEPS[k]) return STEPS[k].isolate;
  return null;
};

// WHAT IS IN THE PIPE AT THIS BEAT. Carried forward from the last beat that
// said, the way `isolate` and `model` are — so the water becomes soda once,
// where the tour says it does, and stays soda after.
const hueOf = (i) => {
  for (let k = i; k >= 0; k--) if (STEPS[k].hue) return STEPS[k].hue;
  return "water";
};

// The sub-assembly the view currently stands isolated to.
let isolated = null;

// HOW A BEAT SHOWS SOMETHING BURIED. Two answers to the same question, and the
// tour runs one of them: `isolate` deletes the context for the cleanest
// possible subject, `section` keeps it and cuts it open so the subject is read
// where it sits. `?reveal=section` swaps which, so they can be judged on the
// same shot instead of from memory.
const REVEAL = new URLSearchParams(location.search).get("reveal") === "section"
  ? "section" : "isolate";

// A BEAT SHOWS ITS SUBJECT ALONE BY TAKING THE REST OF THE MACHINE OUT OF THE
// VIEW, not by loading a second model. The bodies are already there; this only
// decides which of them are drawn (component-picker.js isolateComponent).
//
// `persist: false` because a walkthrough must not edit the reader's own view:
// the picker's hidden set is saved per file, and a beat that isolated the core
// would otherwise leave 137 bodies missing from that model on /3d, with no
// memory of hiding them.
//
// Applied as a move BEGINS rather than as it lands. The camera is already
// travelling, so the change in what is drawn arrives under motion instead of
// popping on arrival, and the shot flies INTO a subject that is already clear.
function applyIsolate(i) {
  const want = isolateOf(i);
  if (want === isolated) return;
  isolated = want;
  // Sectioning needs no dissolve: the cut opens with the camera rather than
  // switching, so there is nothing to fade around.
  if (REVEAL === "section") { spotlight.invalidate(); return; }
  // THE MACHINE DISSOLVES AROUND THE CHANGE rather than blinking through it.
  // The fade runs over the move that is starting, the visibility flips at the
  // bottom of it, and the spotlight's own tiers never dim — so the box thins
  // away and the core is read as having stood inside it the whole time.
  ghosting = dissolve(state.currentGroup, () => {
    isolateComponent(want, { persist: false });
    spotlight.invalidate();
  });
  ghostClock = 0;
  ghostSpan = GHOST_MS; // a move starting in the same breath overrides this
}

// The dissolve in flight, if there is one, and how far into it we are.
//
// IT RUNS OVER THE MOVE, NOT ON A CLOCK OF ITS OWN. The bottom of the dissolve
// is where the machine is faintest, and the middle of a move is where the wide
// shot is and where both the beat being left and the beat being arrived at are
// lit. Landing those on each other means the picture is never dim and empty at
// the same moment; running them on separate clocks means it is.
let ghosting = null;
let ghostClock = 0;
let ghostSpan = 1100;
const GHOST_MS = 1100;   // when nothing is moving — a held beat, or a link

function seatBoxFor(file) {
  const spec = (TOUR.frames || {})[file];
  if (!spec) return null;
  const live = seats.get(spec.into);
  if (live) return live;
  if (!spec.intoBox) return null;
  const b = spec.intoBox;
  return new THREE.Box3(new THREE.Vector3(b[0], b[1], b[2]),
                        new THREE.Vector3(b[3], b[4], b[5]));
}

/** Stand a freshly loaded model where the machine puts it. The base model is
 *  already in the machine's frame and gives up the seats the others land in. */
function seatGroup(file, group) {
  if (!group) return;
  group.position.set(0, 0, 0);
  group.rotation.set(0, 0, 0);
  group.updateMatrixWorld(true);

  const spec = (TOUR.frames || {})[file];
  if (!spec) {
    for (const s of Object.values(TOUR.frames || {})) {
      if (!s.into) continue;
      const b = boxOfParts(group, [s.into]);
      if (!b.isEmpty()) seats.set(s.into, b.clone());
    }
    return;
  }
  group.rotation.z = THREE.MathUtils.degToRad(spec.yawDeg || 0);
  group.updateMatrixWorld(true);
  const seat = seatBoxFor(file);
  const anchor = boxOfParts(group, spec.anchor || []);
  if (!seat || anchor.isEmpty()) return;
  group.position.copy(seat.getCenter(new THREE.Vector3())
    .sub(anchor.getCenter(new THREE.Vector3())));
  group.updateMatrixWorld(true);
}

async function ensureModel(file) {
  if (loadedModel === file && state.currentGroup) return;
  await loadStepFile(file, { preserveCamera: true });
  // A tour is a reading of the model, not a visit to a file. It does not take
  // the components someone hid on /3d, and it does not write its own camera
  // back over the one they left there — both hang off `mountedDetail`, which
  // is what a visit is.
  state.mountedDetail = null;
  state.hiddenComponents.clear();
  try { applyHiddenComponents(); } catch {}
  isolated = null;   // the fresh mount is the whole machine
  ghosting = null;   // and nothing is mid-dissolve on a group that is gone
  loadedModel = file;
  seatGroup(file, state.currentGroup);
  spotlight.attach(state.currentGroup);
}

// ── poses ───────────────────────────────────────────────────────────────────
const focusNames = (s) => (s.focus && s.focus.length ? s.focus : s.parts) || [];

// `focus: ["*"]` is the whole model — what an establishing beat wants, where
// the subject is the appliance and the lit run is a line drawn on it.
function focusBox(i) {
  const names = focusNames(STEPS[i]);
  if (names.includes("*")) return boxOfGroup(state.currentGroup);
  const b = boxOfParts(state.currentGroup, names);
  return b.isEmpty() ? boxOfGroup(state.currentGroup) : b;
}

// THE SHOT A BEAT IS SEEN IN. A held beat states no direction because it is
// whatever the beat before it left standing — which is nothing at all when it
// is the first beat asked for. A link into the middle of a chapter is the
// ordinary way to reach one while the words are being written, so it resolves
// backwards to the nearest beat that does state a direction and takes that
// beat's whole shot: the chapter's opening frame, which is the frame the held
// beat was written to be read in.
function anchorOf(i) {
  for (let k = i; k >= 0; k--) if (STEPS[k].dir) return k;
  return 0;
}

function poseOf(i) {
  const k = STEPS[i].dir ? i : anchorOf(i);
  return poseFor(focusBox(k), STEPS[k].dir, STEPS[k].pad || 1.6, camera);
}

const livePose = () => ({
  target: controls.target.clone(),
  position: camera.position.clone(),
  up: camera.up.clone(),
});

const headingOf = (pose) => pose.position.clone().sub(pose.target).normalize().toArray();

// The lens, and what it does to the distance. The flight hands over a pose
// framed at the page's own field of view; holding the subject's size while the
// lens changes means moving the camera along its own axis by the ratio of the
// two half-angles' tangents.
function applyVertigo(pose, raw) {
  if (!vertigo) return pose;
  const { fov, scale } = vertigoScale(vertigo.from, vertigo.to,
    THREE.MathUtils.clamp(raw, 0, 1), camera.aspect);
  if (camera.fov !== fov) { camera.fov = fov; camera.updateProjectionMatrix(); }
  const o = pose.position.clone().sub(pose.target);
  const d = o.length();
  return { ...pose,
    position: pose.target.clone().addScaledVector(o.normalize(), d * scale) };
}

function applyPose(p) {
  camera.up.copy(p.up);
  camera.position.copy(p.position);
  controls.target.copy(p.target);
  camera.lookAt(controls.target);
}

// ── SOLID OR SEEN THROUGH — ONE PLACE THAT DECIDES ──────────────────────────
// Three different things want the machine drawn solid: the opening, where it is
// an object before it is a diagram; a section, which is a thicket through the
// ghost and a drawing through solid shading; and the closing beat, which shuts
// the appliance again with the line still burning inside it.
//
// They used to each write x-ray when they changed. Two edge-triggered writers
// on one piece of state race on any frame they share — one sets, the other
// restores, and neither fires again, so the mode sticks wrong permanently and
// reads as the feature simply not working. So nothing writes it on an edge.
// Every frame states what the beat needs, and the one place below moves the
// renderer if it disagrees.
//
// THE READER'S OWN CHOICE IS THEIRS. It is read once at boot, it is what every
// beat that does not care falls back to, and it is put back on pagehide — a
// walkthrough must not leave someone's parts viewer in a mode they did not pick.
const readerXray = isXrayEnabled();

function wantsGhost(shown, at) {
  const step = STEPS[shown];
  if (REVEAL === "section" && isolateOf(shown)) return false;  // a section is a drawing
  if (shown === 0 && step.solid && at < step.solid) return false; // the machine, first
  if (step.xray === false) return false;                        // and last
  return readerXray;
}

function syncGhost(shown, at) {
  const want = wantsGhost(shown, at);
  if (isXrayEnabled() === want) return;
  setXrayEnabled(want);
  spotlight.invalidate();
}

window.addEventListener("pagehide", () => {
  if (isXrayEnabled() !== readerXray) setXrayEnabled(readerXray);
  restoreModel(state.currentGroup);
});

// ── the clock ───────────────────────────────────────────────────────────────
let idx = 0;
let pendingIndex = 0;    // the beat a flight is on its way to
let phase = "loading";   // loading | flight | swap-out | swap-hold | swap-in | dwell
let clock = 0;
let span = 0;            // ms this phase runs for
let poseAt = null;       // the pose function for the phase
let dwellBase = null;    // the pose a dwell drifts from
let pending = null;      // { file, bIndex } while a swap is in the air
let playing = true;
let grabbed = false;
let speed = 1;
let lastFrame = 0;
let elapsed = 0;        // ms of tour time, for the pulse on the active leg
let modelSpan = 400;     // the loaded model's own size, for pacing
let moveTags = null;     // the two subjects of the move in the air, for the pins
let swinging = false;    // a held beat's light is still crossing over
let swingFrom = [];      // and this is what it is crossing from
let quietNow = 0;        // how far the machine behind the lights is turned down
const BASE_FOV = camera.fov;
// The lens a beat is seen through, carried forward like `hue` — so a chapter
// entered on a wide lens stays on it, and the moves inside it change nothing.
const vertigoOf = (i) => {
  for (let k = i; k >= 0; k--) if (STEPS[k].vertigo) return STEPS[k].vertigo;
  return BASE_FOV;
};
let vertigo = null;      // { from, to } while a move is changing the lens

const SPEEDS = [1, 1.5, 0.6];
let speedAt = 0;

function dwellMs(s) {
  if (s.dwell) return s.dwell;
  const words = String(s.body || "").split(/\s+/).filter(Boolean).length;
  return Math.max(READ_FLOOR, words * MS_PER_WORD + READ_BASE);
}

function setVeil(a) { veil.style.opacity = String(THREE.MathUtils.clamp(a, 0, 1)); }

// ── moving between beats ────────────────────────────────────────────────────
async function go(i, { instant = false } = {}) {
  i = ((i % N) + N) % N;
  const want = modelOf(i);

  // A HELD BEAT IS THE SAME SHOT. Its subject is already on screen and already
  // framed, so nothing flies: the highlight crosses over, the card changes its
  // words, and the camera carries on drifting from exactly where it is. A
  // chapter is one move and then a few of these.
  if (!instant && STEPS[i].hold && want === loadedModel && loadedModel !== null) {
    applyIsolate(i);
    moveTags = {
      fromBox: focusBox(idx), fromText: STEPS[idx].title,
      toBox: focusBox(i), toText: STEPS[i].title,
    };
    swingFrom = STEPS[idx].parts || [];
    swinging = true;
    commit(i);
    dwellBase = livePose();
    span = dwellMs(STEPS[i]);
    clock = 0;
    phase = "dwell";
    return;
  }

  if (instant || loadedModel === null) {
    await ensureModel(want);
    modelSpan = boxOfGroup(state.currentGroup).getSize(new THREE.Vector3()).length() || 400;
    idx = i;
    applyIsolate(i);
    // A LINK LANDS ON THE BEAT'S OWN LENS. There is no move to change it during,
    // so it is set before the pose is framed — `poseFor` takes its distance from
    // the field of view, and framing at 45 and then arriving at 68 would put the
    // subject at the wrong size in its own beat.
    const lens = vertigoOf(i);
    if (Math.abs(camera.fov - lens) > 0.01) { camera.fov = lens; camera.updateProjectionMatrix(); }
    vertigo = null;
    applyPose(poseOf(i));
    beginDwell();
    commit(i);
    setVeil(0);
    return;
  }

  if (want !== loadedModel) {
    // Step back until the region both models share is in frame, dip, and come
    // back in on the other one. The region is the seat: the block the cold
    // core is, on the enclosure, and the core itself once it is loaded.
    const from = livePose();
    const region = seatBoxFor(want) || seatBoxFor(loadedModel) || focusBox(idx);
    const wide = poseFor(unionBoxes(focusBox(idx), region), headingOf(from), SWAP_PAD, camera);
    moveTags = {
      fromBox: focusBox(idx), fromText: STEPS[idx].title,
      toBox: region, toText: STEPS[i].title,
    };
    pending = { file: want, index: i, wide };
    poseAt = tween.bind(null, from, wide);
    span = SWAP_OUT_MS;
    clock = 0;
    phase = "swap-out";
    return;
  }

  applyIsolate(i);
  startFlight(i, livePose());
}

function startFlight(i, from) {
  const to = poseOf(i);
  const mid = poseFor(
    unionBoxes(focusBox(idx), focusBox(i)),
    midHeading(from, to),
    MID_PAD,
    camera,
  );
  const authored = STEPS[i].enter;
  span = authored != null ? authored : durationFor(from, to, modelSpan);
  if (span <= 0) { applyPose(to); idx = i; beginDwell(); commit(i); return false; }
  // A beat that states `vertigo` takes the lens with it. The number is the field
  // of view it arrives at: below the page's own is a longer lens, which flattens
  // the machine and pushes the camera back; above it is wider, which swells the
  // surroundings around a subject that has not moved.
  const lens = vertigoOf(i);
  vertigo = Math.abs(camera.fov - lens) > 0.01 ? { from: camera.fov, to: lens } : null;

  // Coming out of a swap the beat being left is not in this model any more, so
  // it gets no pin — there is nothing on screen for one to point at.
  moveTags = {
    fromBox: phase === "swap-hold" ? null : focusBox(idx),
    fromText: phase === "swap-hold" ? "" : STEPS[idx].title,
    toBox: focusBox(i), toText: STEPS[i].title,
  };
  poseAt = flight(from, mid, to);
  if (ghosting) ghostSpan = span;   // the fade is this move's own length
  clock = 0;
  swinging = false;
  pendingIndex = i;
  // A swap sets its own phase after this returns; a plain move is a flight.
  if (phase !== "swap-hold") phase = "flight";
  return true;
}

function beginDwell() {
  dwellBase = livePose();
  span = dwellMs(STEPS[idx]);
  clock = 0;
  phase = "dwell";
}

// The legs already crossed. An `overview` beat lights the whole run at once —
// counting it would put every leg in the trail before the tour has been
// anywhere, which is the one thing the trail exists not to say.
const visited = () => {
  const out = new Set();
  for (let k = 0; k < idx; k++) {
    if (STEPS[k].overview) continue;
    for (const p of STEPS[k].parts || []) out.add(p);
  }
  return out;
};

// The body names this model actually carries. A tour names solids and the tree
// renames them; a beat pointing at a name nothing answers to would quietly
// frame the whole machine and light nothing, which reads as a bad angle rather
// than as a stale name. So it is said out loud, on the chip and in the console.
function presentNames() {
  const have = new Set();
  if (state.currentGroup) {
    for (const m of state.currentGroup.children) {
      if (m.isMesh && !m.userData.isXrayEdge && m.name) have.add(m.name);
    }
  }
  return have;
}

function commit(i) {
  idx = i;
  const have = presentNames();
  const missing = (STEPS[i].parts || []).filter((p) => !have.has(p));
  if (missing.length) {
    console.warn(`[tour] step ${i + 1} "${STEPS[i].title}" names ${missing.length} `
      + `body/bodies this model does not carry: ${missing.join(", ")}`);
  }
  hud.setStep(i, STEPS[i], missing);
  const h = `#${i + 1}`;
  if (location.hash !== h) history.replaceState(null, "", h);
}

// ── the frame ───────────────────────────────────────────────────────────────
// ONE FRAME, GIVEN HOW LONG SINCE THE LAST. Split from the rAF driver so the
// tour can be advanced by hand — a console taking it a beat at a time, or a
// recorder walking it at a fixed frame interval, neither of which has a real
// clock to read. `tick` is the driver; this is the tour.
function step(dt) {
  elapsed += dt;
  if (playing && !grabbed && span > 0) clock += dt * speed;

  const t = span > 0 ? Math.min(clock / span, 1) : 1;
  // What is lit, and how far through the handoff between two beats we are.
  // In a flight both beats are on screen at once: the one being left fading
  // back into the trail, the one being arrived at coming up.
  let active = STEPS[idx].parts || [];
  let out = [];
  let mix = 1;

  if (phase === "dwell" && dwellBase) {
    if (!grabbed) applyPose(driftAt(dwellBase, STEPS[idx].drift, t));
    hud.setProgress(idx, t);
    if (swinging) {
      const m = Math.min(clock / SWING_MS, 1);
      mix = m;
      out = swingFrom;
      if (m >= 1) swinging = false;
    }
    if (t >= 1 && playing && !grabbed) go(idx + 1);
  } else if (phase === "flight") {
    if (!grabbed) applyPose(applyVertigo(poseAt(t), t));
    active = STEPS[pendingIndex].parts || [];
    out = STEPS[idx].parts || [];
    mix = t;
    if (t >= 1) { commit(pendingIndex); beginDwell(); }
  } else if (phase === "swap-out") {
    if (!grabbed) applyPose(poseAt(t));
    setVeil(Math.max(0, (t - 0.55) / 0.45));
    out = STEPS[idx].parts || [];
    active = [];
    mix = 1 - t;
    if (t >= 1 && pending) {
      const p = pending;
      pending = null;
      phase = "swap-hold";
      setVeil(1);
      ensureModel(p.file).then(() => {
        modelSpan = boxOfGroup(state.currentGroup).getSize(new THREE.Vector3()).length() || 400;
        applyPose(p.wide);
        startFlight(p.index, p.wide);
        phase = "swap-in";
      });
    }
  } else if (phase === "swap-in") {
    if (!grabbed) applyPose(poseAt(t));
    setVeil(Math.max(0, 1 - clock / VEIL_MS));
    active = STEPS[pendingIndex].parts || [];
    mix = t;
    if (t >= 1) { setVeil(0); commit(pendingIndex); beginDwell(); }
  } else {
    // swap-hold: the picture is under the veil while the next model arrives.
    active = [];
    mix = 0;
  }

  // HOW FAR INTO THE BEAT'S OWN IGNITION WE ARE. A beat that states `ignite`
  // comes on one body at a time in the order it names them, which for a beat
  // about a whole run is the order the water takes.
  const shown = phase === "flight" || phase === "swap-in" ? pendingIndex : idx;
  const step0 = STEPS[shown];
  const parts0 = step0.parts || [];
  const reveal = step0.ignite
    ? THREE.MathUtils.clamp(clock / (step0.ignite * (parts0.length || 1)), 0, 1)
    : 1;

  // And how far down the rest of the machine is turned, eased over about a
  // quarter-second so it arrives with the shot rather than before it.
  quietNow += ((step0.quiet || 0) - quietNow) * Math.min(1, dt / 260);

  // THE WAVEFRONT. `flow` gives a beat a bright crest of two bodies travelling
  // its list in the order it names them, over and over — direction, on a run
  // whose tubes have no centreline to draw dashes along. It only runs once the
  // beat is fully lit, so it does not race the ignition.
  let crest = [];
  if (step0.flow && reveal >= 1 && parts0.length > 2) {
    const period = step0.flow * parts0.length;
    const head = Math.floor(((elapsed % period) / period) * parts0.length);
    crest = [parts0[head], parts0[(head + 1) % parts0.length]];
  }

  // THE HALO, NARROWED ON A WIDE SHOT. How much of the frame the subject fills
  // is what decides whether a glow reads as a glow or as a smear, so the width
  // is taken from that rather than fixed.
  const subject = focusBox(shown);
  let haloWidth = 1;
  if (!subject.isEmpty()) {
    const r = subject.getBoundingSphere(new THREE.Sphere()).radius;
    const d = Math.max(camera.position.distanceTo(subject.getCenter(new THREE.Vector3())), 1);
    haloWidth = THREE.MathUtils.clamp((r / d) * 3.2, 0.25, 1);
  }

  syncGhost(shown, clock);
  if (shown !== 0 || clock > (STEPS[0].solid || 0)) hud.showTitle(false);

  // The cut rides the camera, so it re-strikes every frame it is wanted.
  //
  // AND IT IS DRAWN SOLID. A cut-away through the x-ray ghost is not a section,
  // it is a thicket: the plane takes the near wall away and every feature edge
  // of everything behind it is still drawn, so what the cut opens onto is
  // denser than what it removed. Solid shading is what makes a section read —
  // the cut face is a face, and the first thing behind it is the thing you are
  // being shown.
  if (REVEAL === "section") {
    setSection(state.currentGroup, isolateOf(shown) ? focusBox(shown) : null,
               camera, renderer);
  }

  if (ghosting) {
    ghostClock += dt;
    ghosting(ghostClock / ghostSpan);
    if (ghostClock >= ghostSpan) ghosting = null;
  }

  // THE LAST BEAT IS THE MACHINE AND THE LINE. Its words have been read by the
  // time it is half over, and a walkthrough that ends on a paragraph ends on
  // the paragraph. This one ends on the appliance.
  hud.setCardVisible(!(STEPS[shown].bare && t > 0.45));

  spotlight.paint({
    paths: TOUR.paths,
    hue: hueOf(shown),
    trail: visited(),
    active,
    out,
    crest,
    mix,
    pulse: elapsed / 1000,
    quiet: quietNow,
    reveal,
    haloWidth,
  });
  spotlight.fitScrim(camera);

  // The pins ride the move: from at full at its start, to at full at its end,
  // and both up across the wide shot in the middle where they are the point.
  const moving = swinging
    || phase === "flight" || phase === "swap-out" || phase === "swap-in";
  const pinMix = phase === "swap-out" ? t * 0.6
               : phase === "swap-in" ? 0.4 + t * 0.6
               : swinging ? Math.min(clock / SWING_MS, 1)
               : t;
  tags.update({
    camera,
    rect: stageRect,
    mix: pinMix,
    active: moving && !!moveTags,
    ...(moveTags || {}),
  });
}

function tick(now) {
  requestAnimationFrame(tick);
  const dt = lastFrame ? Math.min(now - lastFrame, 120) : 0;
  lastFrame = now;
  step(dt);
}

// ── controls ────────────────────────────────────────────────────────────────
function onResize() {
  // A held beat states no direction — it is whatever shot the beat before it
  // left standing — so there is nothing to re-derive and re-framing it would
  // throw the camera at a default heading.
  if (phase === "dwell" && !grabbed && STEPS[idx].dir) {
    dwellBase = poseOf(idx);
    // Keep where the drift has got to rather than snapping back to the top of
    // the beat: the shot is re-framed for the new aspect, not restarted.
  }
}

const ACTIONS = {
  prev: () => { playing = true; grabbed = false; hud.setPlaying(true); go(idx - 1); },
  next: () => { playing = true; grabbed = false; hud.setPlaying(true); go(idx + 1); },
  goto: (i) => { playing = true; grabbed = false; hud.setPlaying(true); go(i); },
  togglePlay: () => {
    playing = !playing;
    if (playing && grabbed) { grabbed = false; go(idx); }
    hud.setPlaying(playing);
  },
  resume: () => { grabbed = false; playing = true; hud.setPlaying(true); go(idx); },
  cycleSpeed: () => {
    speedAt = (speedAt + 1) % SPEEDS.length;
    speed = SPEEDS[speedAt];
    hud.setSpeed(speed);
  },
  toggleGhost: () => {
    setXrayEnabled(!isXrayEnabled());
    hud.setGhost(isXrayEnabled());
  },
  copyPose: () => {
    const box = focusBox(idx);
    const target = box.getCenter(new THREE.Vector3());
    const sphere = box.getBoundingSphere(new THREE.Sphere());
    const d = camera.position.clone().sub(target);
    const halfV = THREE.MathUtils.degToRad(camera.fov) / 2;
    const half = Math.min(halfV, Math.atan(Math.tan(halfV) * camera.aspect));
    const pad = (d.length() * Math.sin(half)) / Math.max(sphere.radius, 9);
    const n = d.clone().normalize();
    const r2 = (v) => Math.round(v * 100) / 100;
    const text = `dir: [${r2(n.x)}, ${r2(n.y)}, ${r2(n.z)}],\npad: ${r2(pad)},`;
    navigator.clipboard?.writeText(text);
    hud.flash(text.replace(/\n/g, "  "));
  },
};

const tags = mountTags(document.getElementById("tour-hud-host"));

const hud = mountHud(document.getElementById("tour-hud-host"), {
  steps: STEPS,
  title: TOUR.title,
  subtitle: TOUR.subtitle,
  on: ACTIONS,
});

controls.addEventListener("start", () => {
  grabbed = true;
  playing = false;
  hud.setPlaying(false);
  hud.setGrabbed(true);
});

document.addEventListener("keydown", (e) => {
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key;
  if (k === " ") { e.preventDefault(); ACTIONS.togglePlay(); }
  else if (k === "ArrowRight") { e.preventDefault(); ACTIONS.next(); }
  else if (k === "ArrowLeft") { e.preventDefault(); ACTIONS.prev(); }
  else if (k === "g") ACTIONS.toggleGhost();
  else if (k === "p") ACTIONS.copyPose();
  else if (k === "]") ACTIONS.cycleSpeed();
  else if (k >= "1" && k <= "9") ACTIONS.goto(Number(k) - 1);
});

// ── start ───────────────────────────────────────────────────────────────────
function initialIndex() {
  const m = /^#?(\d+)$/.exec(location.hash.replace(/^#s?/, "#"));
  const q = new URLSearchParams(location.search).get("step");
  const n = m ? Number(m[1]) : q ? Number(q) : 1;
  return Number.isFinite(n) ? THREE.MathUtils.clamp(n - 1, 0, N - 1) : 0;
}

// The escape hatch, in the shape web/contracts/hsm-globals.js gives __hsm:
// something outside the module graph — a console, a headless driver taking the
// tour frame by frame — can read where the player is and move it.
window.__tour = {
  TOUR,
  THREE, scene, camera, controls, renderer,
  get group() { return state.currentGroup; },
  actions: ACTIONS,
  get state() {
    return { idx, pendingIndex, phase, clock, span, playing, grabbed, speed,
             loadedModel, reveal: REVEAL };
  },
  seek(i) { return go(i, { instant: true }); },
  // Advance the tour by hand. `advance(1000/30)` thirty times is one second of
  // tour, whatever the page's own frame rate is doing.
  advance(ms) { step(ms); },
};

hud.setGhost(isXrayEnabled());
hud.setSpeed(speed);
hud.setPlaying(true);
// Only the tour's own opening beat gets the solid machine. A link into the
// middle of it is someone coming back to a beat, not meeting the appliance.
if (STEPS[0].solid && initialIndex() === 0) hud.showTitle(true);
requestAnimationFrame(tick);
go(initialIndex(), { instant: true });

window.addEventListener("hashchange", () => {
  const i = initialIndex();
  if (i !== idx) { playing = true; grabbed = false; hud.setPlaying(true); go(i); }
});
