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
import { state } from "./state.js";
import { syncEdgeResolution } from "./xray.js";

// --- Detail view: Three.js setup ---
export const canvasHost = document.getElementById("cad-canvas-host");

// Exposure the filmic curve is driven at, shared with step.js's thumbnail renderer.
export const TONE_EXPOSURE = 1.25;
// What every 3D surface in the app clears to, and what distance fades toward.
export const BG_COLOR = 0x1a1a2e;

export const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(BG_COLOR);
// The scene renders through a filmic tone curve. step.js's offscreen thumbnail
// renderer carries the same curve and exposure, so a grid thumbnail and the
// detail view of a part are shaded alike.
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = TONE_EXPOSURE;
renderer.domElement.id = "viewport";
renderer.domElement.classList.add("cad-viewport");
canvasHost.appendChild(renderer.domElement);

export const scene = new THREE.Scene();
// near/far are seeded here and fitted to the mounted model every frame by
// updateDepthRange().
export const camera = new THREE.PerspectiveCamera(45, 1, 1, 1000);
export const controls = new TrackballControls(camera, renderer.domElement);
controls.rotateSpeed = 3;
controls.panSpeed = 0.2;
controls.staticMoving = false;
controls.dynamicDampingFactor = 0.12;

// --- Surface-aware zoom --------------------------------------------------
//
// TrackballControls dollies toward `target`, and only toward `target`. The
// default target is the model's bounding-box centre, so a surface beyond that
// centre is literally unreachable from the near side: every wheel tick moves a
// fraction of the remaining distance and asymptotically stops at the centre.
// It also leaves the next orbit centred there, which throws the feature the
// user just approached out of frame as soon as they rotate.
//
// A zoom gesture therefore starts by ray-picking the mounted model under the
// pointer. We move the target to that surface's DEPTH along the existing view
// direction (so the picture does not jump), then make TrackballControls' scale
// happen about the picked point rather than about the old target. Scaling both
// camera and target about that point keeps it under the pointer; moving the
// target toward it makes the same point the natural pivot for the next orbit.
//
// This wraps the one TrackballControls internal that actually scales `_eye`.
// The importmap pins three@0.170.0, the same exact build whose gesture internals
// dropStalledGesture() uses below.
const _surfaceRaycaster = new THREE.Raycaster();
const _surfacePointer = new THREE.Vector2();
const _surfaceAnchor = new THREE.Vector3();
const _surfaceForward = new THREE.Vector3();
const _surfaceOffset = new THREE.Vector3();
const _surfaceTargetBeforeZoom = new THREE.Vector3();
const TRACKBALL_ZOOM_STATE = 1;
let surfaceZoomActive = false;

function visibleInGroup(object, group) {
  for (let node = object; node; node = node.parent) {
    if (!node.visible) return false;
    if (node === group) return true;
  }
  return false;
}

function surfaceUnderPointer(clientX, clientY) {
  const group = state.currentGroup;
  if (!group) return null;
  const rect = renderer.domElement.getBoundingClientRect();
  if (!(rect.width > 0) || !(rect.height > 0)) return null;

  _surfacePointer.set(
    ((clientX - rect.left) / rect.width) * 2 - 1,
    -((clientY - rect.top) / rect.height) * 2 + 1,
  );
  _surfaceRaycaster.setFromCamera(_surfacePointer, camera);
  const hits = _surfaceRaycaster.intersectObject(group, true);
  const hit = hits.find(({ object, face }) =>
    face && object.isMesh && visibleInGroup(object, group));
  return hit ? hit.point : null;
}

function beginSurfaceZoom(clientX, clientY) {
  surfaceZoomActive = false;
  if (!controls.enabled || controls.noZoom || !camera.isPerspectiveCamera) return;
  const point = surfaceUnderPointer(clientX, clientY);
  if (!point) return;

  camera.getWorldDirection(_surfaceForward);
  const depth = _surfaceOffset.copy(point).sub(camera.position).dot(_surfaceForward);
  if (!(depth > 1e-6)) return;

  // This point lies on the camera's existing forward ray, so changing the
  // target's depth cannot pan or turn the current picture.
  controls.target.copy(camera.position).addScaledVector(_surfaceForward, depth);
  _surfaceAnchor.copy(point);
  surfaceZoomActive = true;
}

const trackballZoomCamera = controls._zoomCamera.bind(controls);
controls._zoomCamera = function surfaceAwareZoomCamera() {
  const distanceBefore = this._eye.length();
  _surfaceTargetBeforeZoom.copy(this.target);
  trackballZoomCamera();
  if (!surfaceZoomActive || !this.object.isPerspectiveCamera || !(distanceBefore > 0)) return;

  const scale = this._eye.length() / distanceBefore;
  if (!Number.isFinite(scale) || Math.abs(scale - 1) < 1e-12) return;

  // Trackball has already scaled `_eye` about target. Translating target by
  // this amount makes the resulting camera + target identical to scaling both
  // about the picked surface point. update() applies target + `_eye` to the
  // camera immediately after this method returns.
  _surfaceOffset.copy(_surfaceAnchor)
    .sub(_surfaceTargetBeforeZoom)
    .multiplyScalar(1 - scale);
  this.target.add(_surfaceOffset);
};

// Capture runs before TrackballControls' own target-phase handlers, so the new
// depth is in place when it records and consumes the gesture.
renderer.domElement.addEventListener("wheel", (e) => {
  if (e.deltaY) beginSurfaceZoom(e.clientX, e.clientY);
}, { capture: true, passive: true });

const surfaceTouches = new Map();
renderer.domElement.addEventListener("pointerdown", (e) => {
  if (e.pointerType === "touch") {
    surfaceTouches.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (surfaceTouches.size >= 2) {
      const pair = [...surfaceTouches.values()].slice(0, 2);
      beginSurfaceZoom((pair[0].x + pair[1].x) / 2, (pair[0].y + pair[1].y) / 2);
    }
  } else if (e.button === 1 || controls.keyState === TRACKBALL_ZOOM_STATE) {
    // Middle-drag, or TrackballControls' S-key + drag zoom mode.
    beginSurfaceZoom(e.clientX, e.clientY);
  }
}, true);
renderer.domElement.addEventListener("pointermove", (e) => {
  if (e.pointerType === "touch" && surfaceTouches.has(e.pointerId)) {
    surfaceTouches.set(e.pointerId, { x: e.clientX, y: e.clientY });
    if (surfaceTouches.size >= 2) {
      const pair = [...surfaceTouches.values()].slice(0, 2);
      beginSurfaceZoom((pair[0].x + pair[1].x) / 2, (pair[0].y + pair[1].y) / 2);
    }
  } else if (e.pointerType !== "touch" && (e.buttons & 4)) {
    beginSurfaceZoom(e.clientX, e.clientY);
  }
}, true);
function forgetSurfaceTouch(e) { surfaceTouches.delete(e.pointerId); }
renderer.domElement.addEventListener("pointerup", forgetSurfaceTouch, true);
renderer.domElement.addEventListener("pointercancel", forgetSurfaceTouch, true);

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

// THE ENVIRONMENT IS WHAT A SPECULAR SURFACE HAS TO LOOK AT, and on this machine that is most
// of what a surface is. A metal has no diffuse term at all — every photon it sends back is the
// environment reflected — so a metal under a uniform grey box IS a uniform grey box, whatever
// finishes.json says it is made of. The large flat panels are the other half of it: a panel
// under uniform light is one flat value across its whole face, which is the shape a render has
// and a photograph does not.
//
// So this is a lit room rather than a neutral one: ONE BRIGHT SOFTBOX overhead and toward the
// front-right, bounce cards off the left and low front, a narrow rim behind and above, and dark
// everywhere else. The softbox is the highlight that travels across a surface as it turns, the
// bounce keeps the shadow side from going flat, the rim separates the back edge from the
// background, and the dark surround is what makes the highlight read as a highlight.
//
// IT IS BUILT IN THE SCENE'S OWN +Z-UP FRAME. three.js samples an environment in world space,
// and this repo's CAD is +Z up with -Y the user's side, so "overhead" is +Z and "in front" is
// -Y. A room laid out on three.js's own Y-up convention lights the machine from the back.
//
// A FLOOR, dim and broad. A metal facing down has only this to reflect, and a metal with
// nothing to reflect is not dark, it is BLACK — the failure a uniform environment cannot have
// and the one this rig has to be tuned against.
const ROOM_PANELS = [
  { size: [9, 7, 0.2],   at: [ 2, -3,  7], power: 7 },     // key softbox, overhead and forward
  { size: [0.2, 8, 6],   at: [-7,  1,  0], power: 3 },     // bounce, left wall
  { size: [7, 0.2, 5],   at: [ 1, -7, -1], power: 2 },     // bounce, low and in front
  { size: [4, 0.2, 3],   at: [-2,  6,  4], power: 4 },     // rim, behind and above
  { size: [10, 10, 0.2], at: [ 0,  0, -7], power: 0.84 },  // floor
];

//: How dark the room is between the lights — the ground every surface sees before it sees a
//: lamp. Not zero, for the same reason the floor is there.
const SURROUND = 0.14;

function studioRoom() {
  const room = new THREE.Scene();
  room.background = new THREE.Color(SURROUND, SURROUND, SURROUND);
  for (const { size, at, power } of ROOM_PANELS) {
    // A basic material takes no lighting, so its colour IS its emission — and past 1.0 it is a
    // light source rather than a white card, which is what the float PMREM target is for.
    const face = new THREE.MeshBasicMaterial({ color: 0xffffff });
    face.color.multiplyScalar(power);
    const panel = new THREE.Mesh(new THREE.BoxGeometry(...size), face);
    panel.position.set(...at);
    room.add(panel);
  }
  return room;
}

// Blurred at 0.03 rather than convolved to nothing: the softbox has to keep an edge, because a
// highlight with no edge is the uniform grey this replaces. Roughness does the rest of the
// blurring per material, off the mip chain PMREM builds.
//
// THE WHOLE COST IS HERE, AT MODULE LOAD, AND IT IS 16 ms — measured cold, on a renderer whose
// program cache is empty, which is the state this one runs in. Five plain boxes bake faster
// than the thirteen meshes, seven of them area lights, that three's own RoomEnvironment is
// made of: that reads 39 ms on the same machine. What the frame pays is one prefiltered cube
// sampled per fragment, and that is what a uniform environment costs too.
const pmrem = new THREE.PMREMGenerator(renderer);
export const studioEnvironment = pmrem.fromScene(studioRoom(), 0.03).texture;

// Where the key stands, as a direction from the model. The contact shadow below is thrown off
// this same vector, so the dark on the floor and the bright on the panels cannot disagree.
export const KEY_DIR = new THREE.Vector3(1, -1.2, 2);

// The rig every 3D surface in the app is lit by, ON THE SCENE'S OWN AXIS. step.js's offscreen
// thumbnail scene takes the same one, so a part's grid thumbnail and its detail view are lit
// from the same directions.
//
// The key stands where a photographer stands a key: high, and off the camera axis toward the
// front-right, so the face the default framing looks at is the lit one. The flat terms stay
// small: an ambient floor and a hemisphere are a value added to every fragment alike, and a
// surface shaded mostly by them has no shape in it. The environment above is what carries the
// omnidirectional half of the light, and it carries a direction with it.
export function addStudioLighting(target) {
  target.add(new THREE.AmbientLight(0xffffff, 0.12));
  const key = new THREE.DirectionalLight(0xffffff, 1.1);
  key.position.copy(KEY_DIR);
  target.add(key);
  const fill = new THREE.DirectionalLight(0xffffff, 0.3);
  fill.position.set(-1.2, 0.8, 0.3);
  target.add(fill);
  // Sky overhead, ground below, so no face reads as black when it faces away from the two
  // directionals (the GLB assemblies have parts pointing every direction).
  const hemi = new THREE.HemisphereLight(0xffffff, 0x333340, 0.35);
  hemi.position.set(0, 0, 1);
  target.add(hemi);
  target.environment = studioEnvironment;
  // Distance fades a surface and an edge toward the background. The x-ray ghost
  // carries every solid's feature edges at once — 48,000 segments on the
  // enclosure assembly, the near ones and the far ones at one brightness — and a
  // wireframe with no depth in it is read one edge at a time. `fitFog` gives this
  // its range off the framing, the way `fitCameraDepth` gives the camera its planes.
  target.fog = new THREE.Fog(BG_COLOR, 1, 1000);
}

// How far past the model's own back the fade completes, as a multiple of its
// radius: the back of the model reaches 2/(1 + FOG_BACK) of the way, so a body
// standing there is faded about half rather than gone.
const FOG_BACK = 3.0;

export function fitFog(target, distance, radius) {
  if (!target.fog || !(radius > 0)) return;
  target.fog.near = Math.max(distance - radius, 0);
  target.fog.far = distance + radius * FOG_BACK;
}

addStudioLighting(scene);

// --- Contact shadow ---
// A MACHINE WITH NOTHING UNDER IT IS FLOATING, and floating is the loudest thing left in the
// picture that says "render". Every photograph of an appliance has the appliance standing on
// something, and what the eye reads as standing is not the surface — it is the dark that
// gathers where the object meets it.
//
// So: one quad under the model, carrying a falloff drawn once into a canvas. NO SHADOW MAP.
// A 2048² map off the key light over this assembly's 354 bodies costs 2.0 ms of a 5.1 ms
// frame — 40% — for a shadow the default framing barely sees. This costs the frame nothing
// measurable: one more draw call among 354, priced at +0.02 ms against a ±0.12 ms floor.
//
// The falloff is drawn at the model's own footprint aspect rather than as a circle, so a
// machine that is twice as wide as it is deep sits on a shadow that is too. TWO PASSES, and
// they are two different things. The tight dark one stays under the object: that is the light
// the object blocks from the floor it is touching, and it does not move, whatever the lamps do.
// The wide soft one is the cast shadow and it LEANS AWAY FROM THE KEY, by the offset a body of
// this height throws at the key's elevation. A shadow standing symmetrically under a machine lit
// from one side is the one thing about it the eye reads as wrong.
//
// FrontSide, facing +Z. Orbiting under the model is an ordinary thing to do in a CAD viewer,
// and from under it a shadow is a black disc floating in the way. Back-face culling is what
// makes it disappear there and cost nothing to hide.
const SHADOW_PX = 256;          // texture edge on the long axis
const SHADOW_PAD = 0.34;        // fraction of the texture the falloff runs out over
const SHADOW_SPREAD = 0.06;     // how far past the footprint the soft pass reaches
//: How much of the throw a real point light of this elevation would give the cast pass gets
//: kept. The whole of it puts the blob outside the quad; this is the fraction that reads as
//: "the light is over there" while the shadow stays a shadow of this object.
const SHADOW_LEAN = 0.14;

function shadowTexture(aspect) {
  const w = SHADOW_PX;
  const h = Math.max(64, Math.round(SHADOW_PX * aspect));
  const cv = document.createElement("canvas");
  cv.width = w; cv.height = h;
  const ctx = cv.getContext("2d");
  const box = [w * SHADOW_PAD, h * SHADOW_PAD, w * (1 - 2 * SHADOW_PAD), h * (1 - 2 * SHADOW_PAD)];
  // The quad lies in world XY with its texture unflipped in u and flipped in v, so canvas +x is
  // world +X and canvas +y is world -Y. The throw runs opposite the key on both axes.
  const throwX = -(KEY_DIR.x / KEY_DIR.z) * SHADOW_LEAN * w;
  const throwY =  (KEY_DIR.y / KEY_DIR.z) * SHADOW_LEAN * h;
  const grow = [
    box[0] - w * SHADOW_SPREAD + throwX, box[1] - h * SHADOW_SPREAD + throwY,
    box[2] + w * SHADOW_SPREAD * 2, box[3] + h * SHADOW_SPREAD * 2,
  ];
  ctx.filter = `blur(${Math.round(w * 0.10)}px)`;
  ctx.fillStyle = "rgba(0,0,0,0.42)";
  ctx.beginPath(); ctx.roundRect(...grow, w * 0.06); ctx.fill();
  ctx.filter = `blur(${Math.round(w * 0.05)}px)`;
  ctx.fillStyle = "rgba(0,0,0,0.82)";
  ctx.beginPath(); ctx.roundRect(...box, w * 0.03); ctx.fill();
  const tex = new THREE.CanvasTexture(cv);
  tex.colorSpace = THREE.SRGBColorSpace;
  return tex;
}

let _shadow = null;

function dropGroundShadow() {
  if (!_shadow) return;
  scene.remove(_shadow);
  _shadow.geometry.dispose();
  _shadow.material.map.dispose();
  _shadow.material.dispose();
  _shadow = null;
}

// Sized and placed off the model's box, once per mounted group — updateDepthRange calls this
// from the branch that already fires only when the group changes.
//
// `fog: false`: the fade this quad wants is its own falloff, not the distance fade, and a
// shadow lifted toward the background colour is a grey patch rather than a shadow.
export function fitGroundShadow(box) {
  dropGroundShadow();
  if (!box || box.isEmpty()) return;
  const size = box.getSize(new THREE.Vector3());
  const centre = box.getCenter(new THREE.Vector3());
  if (!(size.x > 0) || !(size.y > 0)) return;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({
      map: shadowTexture(size.y / size.x),
      transparent: true, depthWrite: false, fog: false,
      side: THREE.FrontSide, color: 0x000000,
    }),
  );
  mesh.scale.set(size.x / (1 - 2 * SHADOW_PAD), size.y / (1 - 2 * SHADOW_PAD), 1);
  // A hair under the model's own floor, so the two never fight for the same depth and the
  // part of the quad the model stands on is hidden by the model.
  mesh.position.set(centre.x, centre.y, box.min.z - Math.max(size.z, 1) * 0.001);
  mesh.renderOrder = -1;
  scene.add(mesh);
  _shadow = mesh;
}

// --- ViewCube ---
// Each cube face's projected hit area is roughly gizmoSize/2 — Apple HIG
// asks for 44pt minimum touch targets, so we size to comfortably exceed
// that on every face. The pointer-events:none on the canvas passes empty
// corners through to OrbitControls; the visible cube IS the touch
// target, so growing the canvas grows the touch area too.
function gizmoEdge() {
  return window.matchMedia("(max-width: 600px)").matches ? 140 : 180;
}
let gizmoSize = gizmoEdge();
const gizmoRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
gizmoRenderer.setPixelRatio(window.devicePixelRatio);
gizmoRenderer.setSize(gizmoSize, gizmoSize);
gizmoRenderer.setClearColor(0x000000, 0);
// The panels that stand clear of the cube lay themselves out against
// --cube-size, which is the edge the canvas is actually drawn at — so the
// window can cross the breakpoint and the two stay in agreement.
// resizeRenderer calls this on every observed box change.
export function syncGizmoSize() {
  const next = gizmoEdge();
  if (next !== gizmoSize) {
    gizmoSize = next;
    gizmoRenderer.setSize(gizmoSize, gizmoSize);
  }
  document.documentElement.style.setProperty("--cube-size", gizmoSize + "px");
}
syncGizmoSize();
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

// The cube's six faces in BoxGeometry's own material order — +X, -X, +Y, -Y,
// +Z, -Z. That order is the mapping: a face's place in this array is the slot
// its label is painted on, and the raycast reads the same places back out of
// `hit.face.materialIndex`. Repo convention is +Z-up CAD: +Z height, -Y front
// (user side), +X right. `normal` is where the camera stands to see the face.
const cubeFaces = [
  { label: "Right",  normal: new THREE.Vector3( 1, 0, 0) },
  { label: "Left",   normal: new THREE.Vector3(-1, 0, 0) },
  { label: "Back",   normal: new THREE.Vector3( 0, 1, 0) },
  { label: "Front",  normal: new THREE.Vector3( 0,-1, 0) },
  { label: "Top",    normal: new THREE.Vector3( 0, 0, 1) },
  { label: "Bottom", normal: new THREE.Vector3( 0, 0,-1) },
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

// The cube canvas is pointer-events:none, so a pointer over the cube reaches
// the viewport canvas underneath it and the raycast above places it. A pointer
// over one of the viewer's own panels reaches that panel instead — and the find
// box overlaps the cube's corner, so a click there is a click in the box.
function overCanvas(e) {
  return e.target === renderer.domElement || e.target === gizmoCanvas;
}

// One texture per face per state, made once. Swapping in a fresh CanvasTexture
// on every hover crossing left the old one on the GPU.
const _faceTextures = new Map();
function faceTexture(label, hot) {
  const key = `${label}:${hot ? 1 : 0}`;
  let tex = _faceTextures.get(key);
  if (!tex) { tex = makeFaceTexture(label, hot); _faceTextures.set(key, tex); }
  return tex;
}

function paintFace(index, hot) {
  cubeMaterials[index].map = faceTexture(cubeFaces[index].label, hot);
  cubeMaterials[index].needsUpdate = true;
}

document.addEventListener("mousemove", (e) => {
  const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
  const newIndex = hit ? hit.face.materialIndex : -1;
  if (newIndex !== hoveredFaceIndex) {
    if (hoveredFaceIndex >= 0) paintFace(hoveredFaceIndex, false);
    if (newIndex >= 0) paintFace(newIndex, true);
    hoveredFaceIndex = newIndex;
  }
});

// Capture-phase pointerdown: if the tap raycast-hits the cube, claim the
// gesture and keep OrbitControls from seeing it. Otherwise the event flows
// through normally to OrbitControls / drag-to-orbit.
document.addEventListener("pointerdown", (e) => {
  const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
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
  const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
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
  syncGizmoSize();
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

// --- Depth range ---
// The camera's near and far planes are fitted to the model in front of them —
// near at the model's leading edge, far past its trailing one — and refitted
// as the camera moves. These assemblies mate bodies face to face with nothing
// between them ([enclosure_assembly.py](/hardware/manifold-layout/enclosure_assembly.py)),
// so two solids sharing one plane is the ordinary case here.
//
// The bounding sphere is measured once per mounted group and reused until the
// group changes.
const NEAR_RATIO = 0.002;   // floor on near, as a fraction of the view distance
const NEAR_REACH = 1.25;    // how much of the model's radius sits ahead of the near plane
const FAR_REACH = 2.0;      // and how much past the far one, leaving room for rulers and markers

// A camera `distance` from the centre of a model of `radius`, given the planes
// to see it between. The offscreen thumbnail cameras in step.js and dxf.js take
// their range from here too, off the framing each shot is composed at.
export function depthRangeFor(distance, radius) {
  const near = Math.max(distance - radius * NEAR_REACH, distance * NEAR_RATIO, 1e-4);
  return { near, far: Math.max(distance + radius * FAR_REACH, near * 1.01) };
}

export function fitCameraDepth(cam, center, radius) {
  if (!(radius > 0)) return;
  const { near, far } = depthRangeFor(cam.position.distanceTo(center), radius);
  if (near === cam.near && far === cam.far) return;
  cam.near = near;
  cam.far = far;
  cam.updateProjectionMatrix();
}

let _depthGroup = null;
const _depthSphere = new THREE.Sphere();

export function updateDepthRange() {
  const group = state.currentGroup;
  if (!group) return;
  if (group !== _depthGroup) {
    const box = new THREE.Box3().setFromObject(group);
    box.getBoundingSphere(_depthSphere);
    // THE GROUP IS MARKED SEEN BEFORE THE SHADOW IS BUILT. The planes below are what makes the
    // model visible at all, and this branch is the only place they are fitted; a shadow that
    // threw with the mark still unset would re-enter here on every frame and take them with it
    // every time. Marked first, the worst a failure costs is the shadow.
    _depthGroup = group;
    // Fitted from the same box, in the same branch: this runs when a model is mounted and never
    // on a frame that only moved the camera. A DXF plate lies flat and has no floor to stand
    // on, so only a solid gets one.
    fitGroundShadow(state.mountedDetail?.type === "dxf" ? null : box);
  }
  fitFog(scene, camera.position.distanceTo(_depthSphere.center), _depthSphere.radius);
  fitCameraDepth(camera, _depthSphere.center, _depthSphere.radius);
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
  updateDepthRange();
  syncEdgeResolution(renderer);
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
  updateDepthRange();
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
