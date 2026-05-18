// World-axis rulers for the CAD viewer. Three labeled axes (X red,
// Y green, Z blue) that pass through the OrbitControls target — i.e. the
// point the camera is orbiting around — so wherever you pan or zoom to,
// the three rulers stay anchored at the focus of the view. Tick *labels*
// still show absolute world coordinates (in mm), so a tick labeled "120"
// is at world X=120 regardless of where you've panned to. That way you
// can read off real coordinates to feed an agent.
//
// Tick spacing auto-scales with camera distance using a 1/2/5 × 10^n nice
// number so ~10 ticks span the visible extent. The tick range recenters
// on the current target whenever it wanders past half the covered range.
//
// Rendering: lines are rendered with Three's LineSegments2 / LineMaterial
// pair (the "fat lines" example shader) because the native WebGL line
// primitive ignores linewidth on most platforms. That requires the
// material's `resolution` to be set to the drawing buffer size in pixels
// and kept in sync as the canvas resizes — we observe the canvas and
// re-sync. Label sprites use the default depth test so they hide behind
// model geometry like the axis lines do.
//
// Defaults to off; persisted per-browser in localStorage under "step-rulers".
// The toggle button is created by makeRulerToggle() and appended into the
// cad-wrapper by cad-detail.js.

import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { scene, camera, controls, renderer } from "./scene.js";

const LS_KEY = "step-rulers";

// Match the existing ViewCube axis colors so the rulers and gizmo read
// as the same coordinate system.
const COLOR = { x: 0xe74c3c, y: 0x2ecc71, z: 0x3498db };
const CSS_COLOR = { x: "#e74c3c", y: "#2ecc71", z: "#3498db" };

const AXIS_DIR = {
  x: new THREE.Vector3(1, 0, 0),
  y: new THREE.Vector3(0, 1, 0),
  z: new THREE.Vector3(0, 0, 1),
};
// One distinct perpendicular per axis. At the crosshair point (where all
// three axes meet at the orbit target), the three nearby tick labels
// offset in three different directions so they don't all stack on the
// same screen pixel.
const AXIS_PERP = {
  x: new THREE.Vector3(0, 1, 0),
  y: new THREE.Vector3(0, 0, 1),
  z: new THREE.Vector3(1, 0, 0),
};

// Axis lines extend this far in each direction in local space. Stays
// well inside the perspective camera's far plane (10000).
const AXIS_HALF_LEN = 5000;

// Hard cap on ticks per side. With step=20mm this covers ±1200mm from
// the current center, more than any part in this project.
const MAX_TICKS_PER_SIDE = 60;

// Line widths in screen pixels — the LineMaterial shader gives us true
// pixel widths regardless of camera distance.
const AXIS_LINE_WIDTH = 5;
const TICK_LINE_WIDTH = 5;

// One LineMaterial per axis per role (axis line vs tick). All
// LineSegments2 meshes share these so the resolution sync below only
// has to update six objects when the canvas resizes.
const axisLineMaterials = {
  x: new LineMaterial({ color: COLOR.x, linewidth: AXIS_LINE_WIDTH, transparent: true, opacity: 0.55 }),
  y: new LineMaterial({ color: COLOR.y, linewidth: AXIS_LINE_WIDTH, transparent: true, opacity: 0.55 }),
  z: new LineMaterial({ color: COLOR.z, linewidth: AXIS_LINE_WIDTH, transparent: true, opacity: 0.55 }),
};
const tickLineMaterials = {
  x: new LineMaterial({ color: COLOR.x, linewidth: TICK_LINE_WIDTH, transparent: true, opacity: 0.9 }),
  y: new LineMaterial({ color: COLOR.y, linewidth: TICK_LINE_WIDTH, transparent: true, opacity: 0.9 }),
  z: new LineMaterial({ color: COLOR.z, linewidth: TICK_LINE_WIDTH, transparent: true, opacity: 0.9 }),
};
const allLineMaterials = [
  ...Object.values(axisLineMaterials),
  ...Object.values(tickLineMaterials),
];

function syncLineResolution() {
  // renderer.domElement.width / .height are the drawing buffer size in
  // device pixels — exactly what LineMaterial.resolution wants.
  const w = renderer.domElement.width;
  const h = renderer.domElement.height;
  if (!w || !h) return;
  for (const mat of allLineMaterials) mat.resolution.set(w, h);
}

const canvasResizeObserver = new ResizeObserver(syncLineResolution);
canvasResizeObserver.observe(renderer.domElement);
syncLineResolution();

const rulerGroup = new THREE.Group();
rulerGroup.name = "rulers";

// One sub-group per axis. Each holds: the axis line (LineSegments2 with
// a single segment) and the per-tick marks (one LineSegments2 with N
// segments) and the per-tick sprite labels. All in *local* space.
//
// The group's *position* translates that local content so the axis line
// passes through controls.target along its own world direction. For
// example, the X axis group's position is (0, target.y, target.z): its
// local-X axis line then sits at world Y=target.y, Z=target.z, varying
// in world X. A tick placed at local position (120, 0, 0) lands at world
// (120, target.y, target.z) — i.e. it correctly represents world X=120
// at the height/depth of the current focus. That's why tick *labels*
// stay as absolute world coordinates while the rulers visually follow
// the target.
const axisGroups = {
  x: new THREE.Group(),
  y: new THREE.Group(),
  z: new THREE.Group(),
};
rulerGroup.add(axisGroups.x);
rulerGroup.add(axisGroups.y);
rulerGroup.add(axisGroups.z);

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

// Disposes geometries and per-instance materials (sprite materials and
// their textures). Shared LineMaterials live for the module lifetime —
// don't dispose those here.
function disposeGroup(group) {
  for (let i = group.children.length - 1; i >= 0; i--) {
    const obj = group.children[i];
    group.remove(obj);
    if (obj.geometry) obj.geometry.dispose();
    if (obj.material && obj.material.isSpriteMaterial) {
      if (obj.material.map) obj.material.map.dispose();
      obj.material.dispose();
    }
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

function buildAxisContent(axis, step, center) {
  const group = axisGroups[axis];
  disposeGroup(group);

  const dir = AXIS_DIR[axis];
  const perp = AXIS_PERP[axis];
  const cssColor = CSS_COLOR[axis];

  // Axis line — single segment from -AXIS_HALF_LEN to +AXIS_HALF_LEN
  // along the axis direction in local space.
  const axisGeo = new LineSegmentsGeometry();
  axisGeo.setPositions([
    -dir.x * AXIS_HALF_LEN, -dir.y * AXIS_HALF_LEN, -dir.z * AXIS_HALF_LEN,
     dir.x * AXIS_HALF_LEN,  dir.y * AXIS_HALF_LEN,  dir.z * AXIS_HALF_LEN,
  ]);
  group.add(new LineSegments2(axisGeo, axisLineMaterials[axis]));

  const tickHalf = step * 0.08;
  const labelOffset = step * 0.45;
  const labelW = step * 0.7;
  const labelH = step * 0.35;
  const maxIndex = Math.min(MAX_TICKS_PER_SIDE, Math.floor(AXIS_HALF_LEN / step));

  // All ticks for this axis go into one LineSegmentsGeometry (one draw
  // call), and each tick gets its own labeled sprite.
  const tickPositions = [];
  for (let i = -maxIndex; i <= maxIndex; i++) {
    // value is the absolute world coordinate this tick represents on
    // its axis. Local placement at dir*value is correct because the
    // group's position only translates the *other two* world axes — see
    // comment on axisGroups above.
    const value = center + i * step;
    const pos = dir.clone().multiplyScalar(value);
    const a = pos.clone().addScaledVector(perp, -tickHalf);
    const b = pos.clone().addScaledVector(perp,  tickHalf);
    tickPositions.push(a.x, a.y, a.z, b.x, b.y, b.z);

    const tex = makeLabelTexture(formatTick(value, step), cssColor);
    const mat = new THREE.SpriteMaterial({ map: tex, transparent: true });
    const sprite = new THREE.Sprite(mat);
    sprite.position.copy(pos).addScaledVector(perp, labelOffset);
    sprite.scale.set(labelW, labelH, 1);
    group.add(sprite);
  }
  const tickGeo = new LineSegmentsGeometry();
  tickGeo.setPositions(tickPositions);
  group.add(new LineSegments2(tickGeo, tickLineMaterials[axis]));
}

let currentStep = null;
const currentCenter = { x: 0, y: 0, z: 0 };

function syncAxisGroupPositions() {
  const t = controls.target;
  axisGroups.x.position.set(0,   t.y, t.z);
  axisGroups.y.position.set(t.x, 0,   t.z);
  axisGroups.z.position.set(t.x, t.y, 0  );
}

export function updateRulers() {
  if (!rulerGroup.visible) return;
  const t = controls.target;
  const dist = camera.position.distanceTo(t);
  const fovRad = camera.fov * Math.PI / 180;
  const extent = 2 * dist * Math.tan(fovRad / 2);
  const step = pickStep(extent);

  // Cheap path: just translate the groups so they keep tracking target.
  // Per-frame geometry rebuilds aren't needed.
  syncAxisGroupPositions();

  // Geometry rebuild only when step changes (a meaningful zoom event)
  // or when the user has panned past half the tick range we built.
  const halfRange = MAX_TICKS_PER_SIDE * step * 0.5;
  const xOut = Math.abs(t.x - currentCenter.x) > halfRange;
  const yOut = Math.abs(t.y - currentCenter.y) > halfRange;
  const zOut = Math.abs(t.z - currentCenter.z) > halfRange;
  if (step === currentStep && !xOut && !yOut && !zOut) return;

  currentStep = step;
  currentCenter.x = Math.round(t.x / step) * step;
  currentCenter.y = Math.round(t.y / step) * step;
  currentCenter.z = Math.round(t.z / step) * step;
  buildAxisContent("x", step, currentCenter.x);
  buildAxisContent("y", step, currentCenter.y);
  buildAxisContent("z", step, currentCenter.z);
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

// Rebuild ticks + reposition groups whenever the camera moves. The hot
// path is just three Vector3.set calls (group translations); geometry
// only rebuilds when the chosen "nice step" changes or the user has
// panned past half the tick range.
controls.addEventListener("change", updateRulers);

const stored = (() => { try { return localStorage.getItem(LS_KEY); } catch { return null; } })();
setRulersEnabled(stored === null ? false : stored === "1");
