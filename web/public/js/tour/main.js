import * as THREE from "three";
import { TOUR } from "/contracts/tour-water.js";
import { timelineFor, locateTime, stageAt, motionEnd } from "/contracts/tour-timeline.js";
import { state } from "../viewer/state.js";
import { renderer, gizmoCanvas, scene, camera, controls, resizeRenderer,
  startAnimate, setExtraDepthBounds, fitGroundShadow, updateDepthRange } from "../viewer/scene.js";
import { loadStepFile } from "../viewer/step.js";
import { isXrayEnabled, setXrayEnabled } from "../viewer/xray.js";
import { applyHiddenComponents } from "../viewer/component-picker.js";
import { boxOfParts, boxesOfParts, contextPose } from "./frame.js";
import { tween, driftAt } from "./flight.js";
import * as spotlight from "./spotlight.js";
import { createReveal } from "./reveal.js";
import { mountHud } from "./hud.js";
import { mountTags } from "./tags.js";

const steps = TOUR.steps;
const timeline = timelineFor(steps);
const stage = document.getElementById("tour-stage");
const picture = document.createElement("div");
picture.className = "tour-picture";
picture.style.cssText = "position:absolute;inset:0 0 var(--tour-footer-height,230px);overflow:hidden";
picture.append(renderer.domElement, gizmoCanvas);
stage.prepend(picture);
state.currentCadWrapper = stage;
const loading = document.createElement("div");
loading.className = "cad-loading";
loading.innerHTML = "<span>Loading the machine…</span>";
stage.append(loading);

const background = 0x101923;
renderer.setClearColor(background);
if (scene.fog) scene.fog.color.setHex(background);
spotlight.setBackground(background);
const readerXray = isXrayEnabled();
setXrayEnabled(false, { persist: false });
controls.staticMoving = true;

const params = new URLSearchParams(location.search);
const reducedMotion = matchMedia("(prefers-reduced-motion: reduce)").matches;
let playing = !reducedMotion && params.get("paused") !== "1";
let grabbed = false;
let ready = false;
let time = 0;
let speed = 1;
let frameAt = 0;
let shownIndex = -1;
let reveal;
let machineBox;
let poses = [];
let missing = [];
let pictureRect = { width: 1, height: 1 };
let shadowHidden = false;
const clamp = THREE.MathUtils.clamp;
const smooth = (p) => { p = clamp(p, 0, 1); return p * p * (3 - 2 * p); };

function focusBox(step) {
  const names = step.focus || step.parts || [];
  if (!names.length || names.includes("*")) return machineBox.clone();
  const box = boxOfParts(state.currentGroup, names);
  return box.isEmpty() ? machineBox.clone() : box;
}

function shotFor(step) {
  const subject = focusBox(step);
  const context = boxOfParts(state.currentGroup, step.context || []);
  const fitBoxes = step.context ? boxesOfParts(state.currentGroup,
    [...(step.focus || step.parts), ...step.context]) : [];
  return contextPose(subject, context, step.dir || [1, -1, 0.5],
    step.pad || 1.4, camera, step.contextWeight ?? 0.75, fitBoxes);
}

function composeShots() {
  if (!ready) return;
  poses = steps.map((step) => {
    reveal.apply(step.frameReveal || step.reveal);
    return shotFor(step);
  });
}

function applyPose(pose) {
  camera.up.copy(pose.up);
  camera.position.copy(pose.position);
  controls.target.copy(pose.target);
  camera.lookAt(controls.target);
  camera.updateMatrixWorld();
}

function paint() {
  if (!ready) return;
  const at = locateTime(timeline, time);
  const step = steps[at.index];
  const previous = steps[Math.max(0, at.index - 1)];
  const staging = stageAt(steps, at.index, at.local);
  reveal.apply(staging);
  const hideShadow = staging.coreIsolation > 0.01;
  if (hideShadow !== shadowHidden) {
    shadowHidden = hideShadow;
    fitGroundShadow(hideShadow ? null : machineBox);
  }
  if (!grabbed) {
    const enter = at.index ? (step.enter ?? 1400) : 0;
    const drift = reducedMotion ? null : step.drift;
    const destination = step.frameReveal ? poses[at.index] : shotFor(step);
    if (at.local < enter && !reducedMotion) {
      const from = driftAt(poses[at.index - 1], previous.drift, 1);
      applyPose(tween(from, destination, at.local / enter));
    } else {
      applyPose(driftAt(destination, drift,
        clamp((at.local - enter) / Math.max(1, at.duration - enter), 0, 1)));
    }
  }
  if (shownIndex !== at.index) {
    shownIndex = at.index;
    hud.setStep(at.index, step, missing[at.index]);
    stage.style.setProperty("--tour-accent", `#${(spotlight.HUES[step.hue] || 0x86dfd3).toString(16).padStart(6, "0")}`);
    const hash = `#${at.index + 1}`;
    if (location.hash !== hash) history.replaceState(null, "", hash);
  }
  const mix = smooth(at.local / 700);
  const parts = step.parts || [];
  const crest = step.flow && parts.length ? [parts[Math.floor(at.local / step.flow) % parts.length]] : [];
  spotlight.paint({ active: parts, hue: step.hue || "soda", mix: mix * (step.emphasis ?? 1),
    out: [], trail: [], paths: [], crest, pulse: time / 1000,
    quiet: step.quiet || 0, haloWidth: 0.65 });
  spotlight.fitScrim(camera);
  const subjects = (step.subjects || []).map((subject) => ({
    ...subject,
    box: boxOfParts(state.currentGroup, subject.parts),
    active: subject.parts.some((name) => parts.includes(name)),
  }));
  tags.update({ camera, rect: pictureRect, box: boxOfParts(state.currentGroup, parts), subjects,
    text: step.label || "", active: !!step.label && !!parts.length,
    alpha: subjects.length ? smooth((staging.coreSpread || 0) * 2) : mix });
  hud.setProgress(at.index, at.progress);
  hud.setTime(time, timeline.duration);
  hud.setEnded(time >= timeline.duration);
  hud.showTitle(false);
}

function setPlaying(value) {
  playing = value;
  hud.setPlaying(value);
}
function seekTime(ms) {
  time = clamp(Number(ms) || 0, 0, timeline.duration);
  grabbed = false;
  hud.setGrabbed(false);
  paint();
}
function seek(index) {
  index = clamp(Math.round(Number(index) || 0), 0, steps.length - 1);
  const step = steps[index];
  const settled = !playing && index > 0
    ? Math.min(step.dwell - 1, Math.max(step.enter ?? 1400, motionEnd(step)))
    : 0;
  seekTime(timeline.beats[index].start + settled);
}
const actions = {
  prev: () => seek(locateTime(timeline, time).index - 1),
  next: () => seek(locateTime(timeline, time).index + 1),
  goto: seek,
  togglePlay() {
    if (time >= timeline.duration) seekTime(0);
    if (grabbed) { grabbed = false; hud.setGrabbed(false); paint(); }
    setPlaying(!playing);
  },
  resume() { grabbed = false; hud.setGrabbed(false); setPlaying(true); paint(); },
  cycleSpeed() {
    const speeds = [1, 1.5, 0.75];
    speed = speeds[(speeds.indexOf(speed) + 1) % speeds.length];
    hud.setSpeed(speed);
  },
  toggleGhost() {
    reveal?.restore();
    setXrayEnabled(!isXrayEnabled(), { persist: false });
    hud.setGhost(isXrayEnabled());
    spotlight.invalidate();
    paint();
  },
  copyPose() {
    const direction = camera.position.clone().sub(controls.target).normalize().toArray();
    navigator.clipboard?.writeText(`dir: [${direction.map((v) => v.toFixed(2)).join(", ")}]`);
    hud.flash("Camera direction copied");
  },
};
const host = document.getElementById("tour-hud-host");
const tags = mountTags(picture);
const hud = mountHud(host, { steps, title: TOUR.title, subtitle: TOUR.subtitle, on: actions });
hud.setPlaying(playing);
hud.setSpeed(speed);
hud.setGhost(false);

function resize() {
  resizeRenderer();
  pictureRect = { width: picture.clientWidth, height: picture.clientHeight };
  composeShots();
  paint();
}
new ResizeObserver(resize).observe(picture);
resize();
controls.addEventListener("start", () => {
  grabbed = true;
  setPlaying(false);
  hud.setGrabbed(true);
});

function advance(ms) {
  if (!ready) return;
  time = clamp(time + Math.max(0, Number(ms) || 0), 0, timeline.duration);
  if (time >= timeline.duration) setPlaying(false);
  paint();
}
function tick(now) {
  const delta = frameAt ? Math.min(now - frameAt, 100) : 0;
  frameAt = now;
  if (playing && !grabbed && !document.hidden) advance(delta * speed);
  else if (grabbed) paint();
  requestAnimationFrame(tick);
}

function initialIndex() {
  const number = Number(location.hash.replace(/^#s?/, "") || params.get("step") || 1);
  return clamp((Number.isFinite(number) ? number : 1) - 1, 0, steps.length - 1);
}
window.addEventListener("hashchange", () => seek(initialIndex()));
document.addEventListener("keydown", (event) => {
  if (event.metaKey || event.ctrlKey || event.altKey || /INPUT|TEXTAREA|SELECT/.test(event.target.tagName)) return;
  if (event.key === " " && event.target.closest("button")) return;
  const action = { " ": actions.togglePlay, ArrowRight: actions.next, ArrowLeft: actions.prev }[event.key];
  if (action) { event.preventDefault(); action(); }
});
window.addEventListener("pagehide", (event) => {
  if (event.persisted) return;
  reveal?.restore();
  setXrayEnabled(readerXray, { persist: false });
});
window.addEventListener("pageshow", (event) => {
  if (event.persisted) { frameAt = 0; resize(); }
});

window.__tour = {
  TOUR, THREE, scene, camera, controls, renderer, timeline, actions,
  assetVersion: new URL(import.meta.url).pathname.match(/^\/tour-assets\/([^/]+)\//)?.[1] || null,
  get group() { return state.currentGroup; },
  get state() {
    const at = locateTime(timeline, time);
    return { idx: at.index, clock: at.local, span: at.duration, time,
      duration: timeline.duration, playing, grabbed, speed,
      staging: ready ? reveal.state : null,
      phase: ready ? "dwell" : "loading", loadedModel: ready ? TOUR.model : null };
  },
  seek, seekTime, advance,
};

async function boot() {
  await loadStepFile(TOUR.model, { preserveCamera: true });
  if (!state.currentGroup) throw new Error("The machine model could not be loaded.");
  state.mountedDetail = null;
  state.hiddenComponents.clear();
  applyHiddenComponents();
  setXrayEnabled(false, { persist: false });
  machineBox = boxOfParts(state.currentGroup, ["enclosure-front-top", "enclosure-front-bottom",
    "enclosure-back-top", "enclosure-back-bottom"]);
  if (machineBox.isEmpty()) machineBox = new THREE.Box3().setFromObject(state.currentGroup);
  const have = new Set(state.currentGroup.children.filter((m) => m.isMesh).map((m) => m.name));
  missing = steps.map((s) => (s.parts || []).filter((name) => !have.has(name)));
  if (missing.some((names) => names.length)) console.warn("[tour] Missing bodies", missing);
  reveal = createReveal(state.currentGroup, TOUR.model);
  spotlight.attach(state.currentGroup);
  // Floating panels and fasteners remain inside the camera's depth range.
  setExtraDepthBounds("tour", machineBox.clone().expandByScalar(2200));
  updateDepthRange();
  ready = true;
  composeShots();
  loading.remove();
  seek(initialIndex());
  startAnimate();
  requestAnimationFrame(tick);
}
boot().catch((error) => {
  loading.querySelector("span").textContent = "The machine could not load. Reload to try again.";
  setPlaying(false);
  console.error("[tour]", error);
});
