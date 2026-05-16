// World-axis rulers for the CAD viewer. Three labeled axes through the
// world origin (X red, Y green, Z blue) with tick marks at "nice" mm
// intervals. Tick spacing auto-scales with camera distance so zooming
// in shows finer divisions and zooming out shows coarser ones, keeping
// the rough count of visible ticks stable across zoom levels.
//
// Defaults to on; persisted per-browser in localStorage under "step-rulers".
// The toggle button is created by makeRulerToggle() and appended into the
// cad-wrapper by cad-detail.js so it sits inside the modal alongside the
// gizmo and loading pill.

import * as THREE from "three";
import { scene, camera, controls } from "./scene.js";

const LS_KEY = "step-rulers";

// Match the existing ViewCube axis colors so the rulers and gizmo read
// as the same coordinate system.
const COLOR = { x: 0xe74c3c, y: 0x2ecc71, z: 0x3498db };
const CSS_COLOR = { x: "#e74c3c", y: "#2ecc71", z: "#3498db" };

// Axis lines extend this far in each direction from origin. Stays well
// inside the perspective camera's far plane (10000) while comfortably
// passing any part in this project.
const AXIS_HALF_LEN = 5000;

// Hard cap on ticks per side. Keeps label count bounded if the user is
// extremely zoomed out (in which case the picked step is large anyway).
const MAX_TICKS_PER_SIDE = 60;

const rulerGroup = new THREE.Group();
rulerGroup.name = "rulers";

const tickGroups = {
  x: new THREE.Group(),
  y: new THREE.Group(),
  z: new THREE.Group(),
};
rulerGroup.add(tickGroups.x);
rulerGroup.add(tickGroups.y);
rulerGroup.add(tickGroups.z);

function makeAxisLine(dir, color) {
  const a = new THREE.Vector3().copy(dir).multiplyScalar(-AXIS_HALF_LEN);
  const b = new THREE.Vector3().copy(dir).multiplyScalar( AXIS_HALF_LEN);
  const geo = new THREE.BufferGeometry().setFromPoints([a, b]);
  const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.5 });
  return new THREE.Line(geo, mat);
}

rulerGroup.add(makeAxisLine(new THREE.Vector3(1, 0, 0), COLOR.x));
rulerGroup.add(makeAxisLine(new THREE.Vector3(0, 1, 0), COLOR.y));
rulerGroup.add(makeAxisLine(new THREE.Vector3(0, 0, 1), COLOR.z));

function makeLabelTexture(text, cssColor) {
  const canvas = document.createElement("canvas");
  canvas.width = 128; canvas.height = 64;
  const ctx = canvas.getContext("2d");
  ctx.font = "bold 40px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = cssColor;
  ctx.fillText(text, 64, 32);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

function formatTick(value, step) {
  if (step >= 1) return String(Math.round(value));
  const decimals = Math.max(0, -Math.floor(Math.log10(step)));
  return value.toFixed(decimals);
}

function disposeTickGroup(group) {
  for (let i = group.children.length - 1; i >= 0; i--) {
    const obj = group.children[i];
    group.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material) {
      if (obj.material.map) obj.material.map.dispose();
      obj.material.dispose();
    }
  }
}

function buildTicks(axis, step) {
  const group = tickGroups[axis];
  disposeTickGroup(group);

  // Pick a perpendicular for tick-mark direction and label offset so the
  // labels sit outboard of the axis along a sensible neighbour axis.
  const dirVec = new THREE.Vector3();
  const perpVec = new THREE.Vector3();
  if (axis === "x")      { dirVec.set(1, 0, 0); perpVec.set(0, 1, 0); }
  else if (axis === "y") { dirVec.set(0, 1, 0); perpVec.set(1, 0, 0); }
  else                   { dirVec.set(0, 0, 1); perpVec.set(1, 0, 0); }

  const tickHalf = step * 0.08;
  const labelOffset = step * 0.45;
  const labelW = step * 0.7;
  const labelH = step * 0.35;
  const color = COLOR[axis];
  const cssColor = CSS_COLOR[axis];

  const maxIndex = Math.min(MAX_TICKS_PER_SIDE, Math.floor(AXIS_HALF_LEN / step));

  for (let i = -maxIndex; i <= maxIndex; i++) {
    if (i === 0) continue; // origin is the crossing of all three axes — no label
    const value = i * step;
    const pos = dirVec.clone().multiplyScalar(value);

    const tickGeo = new THREE.BufferGeometry().setFromPoints([
      pos.clone().addScaledVector(perpVec, -tickHalf),
      pos.clone().addScaledVector(perpVec,  tickHalf),
    ]);
    const tickMat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.8 });
    group.add(new THREE.Line(tickGeo, tickMat));

    const tex = makeLabelTexture(formatTick(value, step), cssColor);
    const mat = new THREE.SpriteMaterial({ map: tex, depthTest: false, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.position.copy(pos).addScaledVector(perpVec, labelOffset);
    sprite.scale.set(labelW, labelH, 1);
    // Render after the model so labels stay legible through geometry.
    sprite.renderOrder = 999;
    group.add(sprite);
  }
}

function pickStep(targetExtent) {
  // 1/2/5 × 10^n nice number so ~10 ticks span the targetExtent.
  const raw = targetExtent / 10;
  if (!isFinite(raw) || raw <= 0) return 1;
  const exponent = Math.floor(Math.log10(raw));
  const fraction = raw / Math.pow(10, exponent);
  let niceFraction;
  if (fraction < 1.5) niceFraction = 1;
  else if (fraction < 3.5) niceFraction = 2;
  else if (fraction < 7.5) niceFraction = 5;
  else niceFraction = 10;
  return niceFraction * Math.pow(10, exponent);
}

let currentStep = null;

export function updateRulers() {
  if (!rulerGroup.visible) return;
  const dist = camera.position.distanceTo(controls.target);
  const fovRad = camera.fov * Math.PI / 180;
  const extent = 2 * dist * Math.tan(fovRad / 2);
  const step = pickStep(extent);
  if (step === currentStep) return;
  currentStep = step;
  buildTicks("x", step);
  buildTicks("y", step);
  buildTicks("z", step);
}

export function setRulersEnabled(on) {
  rulerGroup.visible = !!on;
  try { localStorage.setItem(LS_KEY, on ? "1" : "0"); } catch {}
  if (on) {
    // Force a rebuild on next update so ticks reflect current camera.
    currentStep = null;
    updateRulers();
  }
}

export function areRulersEnabled() {
  return rulerGroup.visible;
}

export function makeRulerToggle() {
  const btn = document.createElement("button");
  btn.type = "button";
  btn.className = "ruler-toggle";
  function refresh() {
    const on = areRulersEnabled();
    btn.textContent = on ? "Rulers: on" : "Rulers: off";
    btn.classList.toggle("off", !on);
  }
  btn.addEventListener("click", () => {
    setRulersEnabled(!areRulersEnabled());
    refresh();
  });
  refresh();
  return btn;
}

scene.add(rulerGroup);

// Rebuild ticks whenever the camera moves. Cheap — buildTicks only runs
// when the chosen "nice step" actually changes, so an orbit at constant
// zoom does nothing past the early-return inside updateRulers().
controls.addEventListener("change", updateRulers);

const stored = (() => { try { return localStorage.getItem(LS_KEY); } catch { return null; } })();
setRulersEnabled(stored === null ? true : stored === "1");
