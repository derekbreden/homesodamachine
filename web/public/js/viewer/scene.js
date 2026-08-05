// Three.js scene singletons: renderer, camera, TrackballControls, lighting,
// the ViewCube gizmo, the animate loop, and per-file camera persistence.
//
// renderer/scene/camera/controls/gizmo* are created ONCE at module load
// and reused across opens. The two canvases (renderer.domElement and
// gizmoCanvas) live in #cad-canvas-host when no detail is open, and get
// appendChild'd into the modal wrapper inside cad-detail.js. This keeps
// controls listeners (bound to renderer.domElement) alive across
// open/close cycles and avoids reparsing GL state.
//
// TrackballControls (not OrbitControls) so rotation has no up-vector
// clamp — you can keep dragging through the poles like Fusion 360
// instead of hitting a wall at "straight overhead". camera.up is a
// free variable the trackball maintains as you rotate; the ViewCube
// snap and resetCamera still set it explicitly to land on a known
// orientation.
//
// This module does NOT know about modals — cad-detail.js owns wrapper
// creation and the canvas reparenting. Here we only own the scene
// objects + helpers (resize, animate start/stop, isometric framing,
// localStorage save/apply).

import * as THREE from "three";
import { TrackballControls } from "three/addons/controls/TrackballControls.js";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { state } from "./state.js";

// --- Detail view: Three.js setup ---
export const canvasHost = document.getElementById("cad-canvas-host");

export const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0x1a1a2e);
renderer.domElement.id = "viewport";
renderer.domElement.classList.add("cad-viewport");
canvasHost.appendChild(renderer.domElement);

export const scene = new THREE.Scene();
export const camera = new THREE.PerspectiveCamera(45, 1, 0.01, 10000);
export const controls = new TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 3;
controls.panSpeed = 0.2;
controls.staticMoving = false;
controls.dynamicDampingFactor = 0.12;

// --- Gesture gate ---
// occt's wasm STEP reader holds the main thread for the length of a parse — ~10 s
// on the 20 MB enclosure assembly. Work that heavy waits for the pointer to come
// up: afterGesture() resolves immediately when nothing is being dragged, and on
// the controls' `end` event when something is. TrackballControls brackets every
// rotate/pan/zoom gesture with start/end; a wheel zoom fires both in one tick.
let gesturing = false;
const gestureWaiters = [];

function endGesture() {
  if (!gesturing) return;
  gesturing = false;
  for (const resolve of gestureWaiters.splice(0)) resolve();
}

controls.addEventListener("start", () => { gesturing = true; });
controls.addEventListener("end", endGesture);
// Safety net for a pointerup that never reaches the controls (capture lost,
// gesture cancelled). Capture phase on document, alongside the gizmo handlers
// below — their stopPropagation doesn't reach listeners on the same node in the
// same phase.
document.addEventListener("pointerup", endGesture, true);
document.addEventListener("pointercancel", endGesture, true);

export function afterGesture() {
  if (!gesturing) return Promise.resolve();
  return new Promise((resolve) => gestureWaiters.push(resolve));
}

scene.add(new THREE.AmbientLight(0xffffff, 0.5));
const dirLight = new THREE.DirectionalLight(0xffffff, 0.8);
dirLight.position.set(1, 2, 1.5);
scene.add(dirLight);
const dirLight2 = new THREE.DirectionalLight(0xffffff, 0.3);
dirLight2.position.set(-1, -0.5, -1);
scene.add(dirLight2);
// Omnidirectional fill so no face reads as black when it faces away from the
// two directionals (the GLB assemblies have parts pointing every direction).
scene.add(new THREE.HemisphereLight(0xffffff, 0x333340, 0.5));
// A neutral studio environment gives metallic PBR materials (the GLB
// component models — connectors, cans, ICs) something to reflect; without it
// they render black. STEP parts (near-non-metallic) pick up only a faint sheen.
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;

// --- ViewCube ---
// Each cube face's projected hit area is roughly gizmoSize/2 — Apple HIG
// asks for 44pt minimum touch targets, so we size to comfortably exceed
// that on every face. The pointer-events:none on the canvas passes empty
// corners through to OrbitControls; the visible cube IS the touch
// target, so growing the canvas grows the touch area too.
const gizmoSize = window.innerWidth < 600 ? 140 : 180;
const gizmoRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
gizmoRenderer.setPixelRatio(window.devicePixelRatio);
gizmoRenderer.setSize(gizmoSize, gizmoSize);
gizmoRenderer.setClearColor(0x000000, 0);
export const gizmoCanvas = gizmoRenderer.domElement;
gizmoCanvas.id = "gizmoCanvas";
// .cad-gizmo: position:absolute inside the wrapper (top-right, safe-area
// padded), pointer-events:none so empty corners pass touches through to
// OrbitControls. Hits on the rendered cube are picked up via document-level
// raycast handlers below.
gizmoCanvas.classList.add("cad-gizmo");
canvasHost.appendChild(gizmoCanvas);

const gizmoScene = new THREE.Scene();
const gizmoCam = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
const gizmoRaycaster = new THREE.Raycaster();

// Face definitions: label, normal (camera direction to see that face), material index.
// Repo convention is +Z-up CAD: +Z height, -Y front (user side), +X right.
const cubeFaces = [
  { label: "Right",  normal: new THREE.Vector3( 1, 0, 0), index: 0 },
  { label: "Left",   normal: new THREE.Vector3(-1, 0, 0), index: 1 },
  { label: "Top",    normal: new THREE.Vector3( 0, 0, 1), index: 2 },
  { label: "Bottom", normal: new THREE.Vector3( 0, 0,-1), index: 3 },
  { label: "Front",  normal: new THREE.Vector3( 0,-1, 0), index: 4 },
  { label: "Back",   normal: new THREE.Vector3( 0, 1, 0), index: 5 },
];

function makeFaceTexture(label, isHovered) {
  const canvas = document.createElement("canvas");
  canvas.width = 256; canvas.height = 256;
  const ctx = canvas.getContext("2d");
  const bg = isHovered ? "#3a3a5a" : "#232342";
  const border = "#3a3a5a";
  const radius = 16;

  // Rounded rect fill
  ctx.beginPath();
  ctx.roundRect(2, 2, 252, 252, radius);
  ctx.fillStyle = bg;
  ctx.fill();
  ctx.strokeStyle = border;
  ctx.lineWidth = 3;
  ctx.stroke();

  ctx.font = "52px -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = isHovered ? "#ffffff" : "#999999";
  ctx.fillText(label, 128, 128);
  const tex = new THREE.CanvasTexture(canvas);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

const cubeMaterials = cubeFaces.map((f) =>
  new THREE.MeshBasicMaterial({ map: makeFaceTexture(f.label, false) })
);
const cubeGeo = new THREE.BoxGeometry(0.55, 0.55, 0.55);
const cubeMesh = new THREE.Mesh(cubeGeo, cubeMaterials);
// No offset — cube centered at origin, axes start from its corner
gizmoScene.add(cubeMesh);

// Axis lines + labels from bottom-left-back corner of cube. All three
// axes emerge from this corner and travel in their POSITIVE directions
// across the cube to land their labels past the opposite (+X / +Y / +Z)
// faces — keeps the "Z" label on the +Z side of the cube to match the
// "X" and "Y" labels on the +X and +Y sides.
const axisOrigin = new THREE.Vector3(-0.275, -0.275, -0.275);
const axisLen = 0.7;

function makeAxisLine(origin, dir, color) {
  const end = origin.clone().add(new THREE.Vector3().copy(dir).multiplyScalar(axisLen));
  const geo = new THREE.BufferGeometry().setFromPoints([origin, end]);
  return new THREE.Line(geo, new THREE.LineBasicMaterial({ color }));
}

function makeAxisLabel(text, position, color) {
  const canvas = document.createElement("canvas");
  canvas.width = 64; canvas.height = 64;
  const ctx = canvas.getContext("2d");
  ctx.font = "bold 48px -apple-system, BlinkMacSystemFont, sans-serif";
  ctx.textAlign = "center";
  ctx.textBaseline = "middle";
  ctx.fillStyle = color;
  ctx.fillText(text, 32, 32);
  const tex = new THREE.CanvasTexture(canvas);
  const sprite = new THREE.Sprite(new THREE.SpriteMaterial({ map: tex, depthTest: false }));
  sprite.position.copy(position);
  sprite.scale.set(0.3, 0.3, 1);
  return sprite;
}

gizmoScene.add(makeAxisLine(axisOrigin, new THREE.Vector3(1, 0, 0), 0xe74c3c));
gizmoScene.add(makeAxisLine(axisOrigin, new THREE.Vector3(0, 1, 0), 0x2ecc71));
gizmoScene.add(makeAxisLine(axisOrigin, new THREE.Vector3(0, 0, 1), 0x3498db));
const labelOffset = axisLen + 0.15;
gizmoScene.add(makeAxisLabel("X", axisOrigin.clone().add(new THREE.Vector3(labelOffset, 0, 0)), "#e74c3c"));
gizmoScene.add(makeAxisLabel("Y", axisOrigin.clone().add(new THREE.Vector3(0, labelOffset, 0)), "#2ecc71"));
gizmoScene.add(makeAxisLabel("Z", axisOrigin.clone().add(new THREE.Vector3(0, 0, labelOffset)), "#3498db"));

// Hover + click tracking. Listeners are document-level (capture phase) so we
// can decide whether the gesture belongs to the gizmo *before* OrbitControls
// sees it. The canvas itself is pointer-events:none, so any tap that doesn't
// raycast-hit the cube falls straight through to the 3D viewport underneath.
let hoveredFaceIndex = -1;
let armedAtPointerDown = false;          // true when pointerdown landed on the cube

function gizmoRaycastFromEvent(e) {
  const rect = gizmoCanvas.getBoundingClientRect();
  if (
    e.clientX < rect.left || e.clientX > rect.right ||
    e.clientY < rect.top  || e.clientY > rect.bottom
  ) return null;
  const mouse = new THREE.Vector2(
    ((e.clientX - rect.left) / rect.width) * 2 - 1,
    -((e.clientY - rect.top) / rect.height) * 2 + 1,
  );
  gizmoRaycaster.setFromCamera(mouse, gizmoCam);
  const hits = gizmoRaycaster.intersectObject(cubeMesh);
  return hits.length > 0 ? hits[0] : null;
}

document.addEventListener("mousemove", (e) => {
  const hit = gizmoRaycastFromEvent(e);
  const newIndex = hit ? hit.face.materialIndex : -1;
  if (newIndex !== hoveredFaceIndex) {
    if (hoveredFaceIndex >= 0) {
      cubeMaterials[hoveredFaceIndex].map = makeFaceTexture(cubeFaces[hoveredFaceIndex].label, false);
      cubeMaterials[hoveredFaceIndex].needsUpdate = true;
    }
    if (newIndex >= 0) {
      cubeMaterials[newIndex].map = makeFaceTexture(cubeFaces[newIndex].label, true);
      cubeMaterials[newIndex].needsUpdate = true;
    }
    hoveredFaceIndex = newIndex;
  }
});

// Capture-phase pointerdown: if the tap raycast-hits the cube, claim the
// gesture and keep OrbitControls from seeing it. Otherwise the event flows
// through normally to OrbitControls / drag-to-orbit.
document.addEventListener("pointerdown", (e) => {
  const hit = gizmoRaycastFromEvent(e);
  if (!hit) { armedAtPointerDown = false; return; }
  armedAtPointerDown = true;
  e.stopPropagation();
  e.preventDefault();
}, true);

// Capture-phase pointerup: complete the snap if our pointerdown landed on
// the cube AND this pointerup also lands on the cube (so a drag off the
// cube cancels rather than snaps).
document.addEventListener("pointerup", (e) => {
  if (!armedAtPointerDown) return;
  armedAtPointerDown = false;
  const hit = gizmoRaycastFromEvent(e);
  e.stopPropagation();
  e.preventDefault();
  if (!hit) return;
  const face = cubeFaces[hit.face.materialIndex];
  snapCameraToFace(face.normal);
}, true);

function snapCameraToFace(normal) {
  const target = controls.target.clone();
  const dist = camera.position.distanceTo(target);
  const dest = target.clone().add(normal.clone().multiplyScalar(dist));

  // Up vector: use Z-up unless looking along Z axis (Top / Bottom view),
  // then fall back to Y-up so the camera doesn't collapse onto its own
  // up vector (which would produce an undefined "right" direction).
  const up = Math.abs(normal.z) > 0.9
    ? new THREE.Vector3(0, normal.z > 0 ? -1 : 1, 0)
    : new THREE.Vector3(0, 0, 1);

  const startPos = camera.position.clone();
  const startUp = camera.up.clone();
  const duration = 300;
  const startTime = performance.now();

  function animateSnap() {
    const t = Math.min((performance.now() - startTime) / duration, 1);
    const ease = t * (2 - t); // ease-out quad
    camera.position.lerpVectors(startPos, dest, ease);
    camera.up.lerpVectors(startUp, up, ease).normalize();
    camera.lookAt(target);
    controls.update();
    if (t < 1) requestAnimationFrame(animateSnap);
  }
  animateSnap();
}

function renderGizmo() {
  // Mirror main camera orientation
  const dir = new THREE.Vector3();
  camera.getWorldDirection(dir);
  gizmoCam.position.copy(dir).multiplyScalar(-3);
  gizmoCam.up.copy(camera.up);
  gizmoCam.lookAt(0, 0, 0);
  gizmoRenderer.render(gizmoScene, gizmoCam);
}

// Size the renderer to the canvas's parent (the modal wrapper when open,
// the hidden host when not — but the host has display:none, so we only
// expect this to do useful work when the modal is open). Falls back to
// window size if the parent has no measured rect (e.g. headless tools that
// drove openDetail and may inspect the canvas before layout settles).
export function resizeRenderer() {
  const parent = renderer.domElement.parentElement;
  let w = 0, h = 0;
  if (parent && parent !== canvasHost) {
    const r = parent.getBoundingClientRect();
    w = Math.floor(r.width);
    h = Math.floor(r.height);
  }
  if (w === 0 || h === 0) {
    w = window.innerWidth;
    h = window.innerHeight;
  }
  renderer.setSize(w, h, false);
  // Also re-apply CSS size — setSize(...,false) doesn't touch style, and we
  // want the canvas to actually fill the wrapper's content box.
  renderer.domElement.style.width = w + "px";
  renderer.domElement.style.height = h + "px";
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
  // TrackballControls samples canvas screen geometry once in its constructor
  // and again here; without this, mouse coords normalize against stale
  // dimensions after a resize and rotation feels off-axis.
  controls.handleResize();
  // TrackballControls' _getMouseOnCircle divides BOTH x and y by screen.width
  // (intentional upstream; see "screen.width intentional" comment in three.js).
  // That ties a full rotation to canvas width, so mobile portrait feels much
  // faster than desktop landscape on the same finger travel. Overriding width
  // to equal height after handleResize() makes rotation feel height-driven
  // and keeps pan symmetric across axes as a side effect.
  controls.screen.width = controls.screen.height;
}

// A frame gap this long is the main thread having been blocked, or the tab
// hidden — rAF didn't run. The gesture deltas TrackballControls accumulated
// across the gap describe seconds of hand travel, and the next update() spends
// them as one frame of motion: _rotateCamera applies the whole delta at once and
// seeds _lastAngle with it, which dynamic damping re-applies every frame after,
// decayed by only sqrt(1 - dynamicDampingFactor) ≈ 0.94 — tens of radians of
// spin over the two seconds that follow. Pan and zoom damp the same way off
// _panStart / _zoomStart.
const STALL_MS = 400;

function dropStalledGesture() {
  // three@0.170.0 internals; the importmap pins that exact build.
  controls._movePrev?.copy(controls._moveCurr);  // rotate: the stale delta
  controls._panStart?.copy(controls._panEnd);    // pan: same shape
  controls._zoomStart?.copy(controls._zoomEnd);  // zoom: same shape
  controls._lastAngle = 0;                       // and the rotation flywheel
}

let animating = false;
let animateRafId = 0;
let lastFrameAt = 0;
function animate() {
  if (!animating) { animateRafId = 0; return; }
  animateRafId = requestAnimationFrame(animate);
  const now = performance.now();
  if (lastFrameAt && now - lastFrameAt > STALL_MS) dropStalledGesture();
  lastFrameAt = now;
  controls.update();
  renderer.render(scene, camera);
  renderGizmo();
}
export function startAnimate() {
  if (animating) return;
  animating = true;
  lastFrameAt = 0; // a closed modal is not a stall
  animate();
}
export function stopAnimate() {
  animating = false;
  if (animateRafId) {
    cancelAnimationFrame(animateRafId);
    animateRafId = 0;
  }
}

// Default isometric framing for STEP groups. DXF has its own framing in
// dxf.js (resetDxfCamera) because flat plates need aspect-aware sizing.
// camera.up is restored to +Z-up so a prior Top/Bottom ViewCube snap
// (which temporarily lays up onto ±Y) doesn't carry over and leave the
// reset view rolled.
export function resetCamera(group) {
  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = maxDim * 2.5;

  // Isometric angles. +Z-up CAD-standard front-iso: camera at +X, -Y, +Z
  // — the user's "front-right-above" view. Elevation lifts the camera by
  // sin(35.26°) along +Z; the horizontal projection lays it at az = -45°
  // so the X contribution is positive (right) and the Y contribution is
  // negative (front, user's side of the appliance).
  const el = Math.atan(1 / Math.sqrt(2)); // ~35.26 deg
  const az = -Math.PI / 4;
  camera.up.set(0, 0, 1);
  camera.position.set(
    center.x + dist * Math.cos(el) * Math.cos(az),
    center.y + dist * Math.cos(el) * Math.sin(az),
    center.z + dist * Math.sin(el)
  );
  camera.lookAt(center);
  controls.target.copy(center);
  controls.update();
}

// --- Per-file camera persistence ---
// Saves position/up/target to localStorage on every settled change so
// reopening the file (or following a push notification) restores the same
// view. Keys are namespaced by file path.
export function saveCameraState(file) {
  if (!file) return;
  try {
    localStorage.setItem(`step-camera:${file}`, JSON.stringify({
      p: camera.position.toArray(),
      u: camera.up.toArray(),
      t: controls.target.toArray(),
    }));
  } catch {}
}

export function applyCameraState(file) {
  try {
    const raw = localStorage.getItem(`step-camera:${file}`);
    if (!raw) return false;
    const s = JSON.parse(raw);
    camera.position.fromArray(s.p);
    camera.up.fromArray(s.u);
    controls.target.fromArray(s.t);
    controls.update();
    return true;
  } catch {
    return false;
  }
}

let cameraSaveTimer = null;
controls.addEventListener("change", () => {
  // Save the camera for whichever file is open. Both STEP and DXF use
  // the same camera, scoped per-file in localStorage.
  // Both STEP and DXF use the same camera; saving is keyed by file path.
  const openFile = state.mountedDetail ? state.mountedDetail.file : null;
  if (!openFile) return;
  clearTimeout(cameraSaveTimer);
  cameraSaveTimer = setTimeout(() => saveCameraState(openFile), 250);
});
