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
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { GTAOPass } from "three/addons/postprocessing/GTAOPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";
import { state } from "./state.js";
import { syncEdgeResolution } from "./xray.js";

// --- Detail view: Three.js setup ---
export const canvasHost = document.getElementById("cad-canvas-host");

// Exposure the filmic curve is driven at, shared with step.js's thumbnail renderer.
export const TONE_EXPOSURE = 1.15;
// What every 3D surface in the app clears to, and what distance fades toward.
export const BG_COLOR = 0x1a1a2e;

export const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(BG_COLOR);
// AND THE SCENE OWNS IT TOO, which is the spelling that survives the composer. A clear colour is
// written straight into the render target, and the target a post chain draws into is LINEAR — so
// `OutputPass` converts it to sRGB on the way out and a colour that was already sRGB comes back
// lifted, 0x1a1a2e reading as a pale lilac. `scene.background` goes through three's own colour
// management instead and lands on the same value it names, composer or not.
// The scene renders through a filmic tone curve. step.js's offscreen thumbnail
// renderer carries the same curve and exposure, so a grid thumbnail and the
// detail view of a part are shaded alike.
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = TONE_EXPOSURE;
renderer.domElement.id = "viewport";
renderer.domElement.classList.add("cad-viewport");
canvasHost.appendChild(renderer.domElement);

export const scene = new THREE.Scene();
scene.background = new THREE.Color(BG_COLOR);
// near/far are seeded here and fitted to the mounted model every frame by
// updateDepthRange().
export const camera = new THREE.PerspectiveCamera(45, 1, 1, 1000);
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

// THE ENVIRONMENT IS WHAT A SPECULAR SURFACE HAS TO LOOK AT, and on this machine that is most
// of what a surface is. A metal has no diffuse term at all — every photon it sends back is the
// environment reflected — so a metal under a uniform grey box IS a uniform grey box, whatever
// `_materials` says it is made of. Brass, copper, the sintered stone and the mill-finish
// stainless all arrive at the viewer as their own colour and can only spend it here.
//
// So this is a lit room rather than a neutral one: ONE BRIGHT SOFTBOX overhead and forward, two
// dim bounce cards off to either side, and dark everywhere else. The softbox is the highlight
// that travels across a surface as it turns, the bounce keeps the shadow side from going flat,
// and the dark surround is what makes the highlight read as a highlight. Measured against a
// uniform environment on the cold core, that is worth a mean 22 counts of 255 across the frame
// and it DOUBLES what `finishes.json` is worth on the same bodies — a roughness that has
// nothing to sharpen or smear is a roughness nobody can see.
//
// The dielectrics gain far less and cannot gain more: a non-metal keeps about 4 % of the light
// in its specular lobe, so the whole PETG-against-PET-GF difference is a redistribution of that
// 4 % and no lamp lifts the ceiling. What it buys them is real and small; what it buys the
// metals is the difference between metal and paint.
// AN ENVIRONMENT LIGHTS DIFFUSE AS WELL AS SPECULAR. `scene.environment` is irradiance, not just
// reflection: a face pointed at a dark wall gets a dark ambient term whatever the lamps do. So a
// bright box on one side and a near-black room everywhere else does not merely fail to sparkle on
// the far side — it STARVES it, and the machine reads light grey from the back and near-black
// from the front. The room has to be lit all the way round, with one source clearly brightest.
const SOFTBOX = { size: [10, 0.2, 8], at: [0, 7, 2], power: 7 };
const BOUNCE = [
  { size: [8, 6, 0.2], at: [-7, 0, -4], power: 3.5 },
  { size: [6, 5, 0.2], at: [6, -1, 3], power: 2.2 },
  // The two walls the first pair leaves dark. Dimmer than the key by enough that the highlight
  // still travels, bright enough that no face of a closed box falls off a cliff.
  { size: [0.2, 6, 8], at: [-8, 2, 2], power: 1.6 },
  { size: [8, 6, 0.2], at: [0, 2, -8], power: 1.4 },
  // A FLOOR, dim and broad. A metal facing down has only this to reflect, and a metal with
  // nothing to reflect is not dark, it is BLACK — the failure a uniform environment cannot have
  // and the one this rig has to be tuned against. The brass hex is the part that shows it: at a
  // surround of 0.03 its underside went to nothing, and every value here was set by turning that
  // face back into a readable shadow without flattening the highlight on top of it.
  { size: [10, 0.2, 8], at: [0, -7, -1], power: 2.4 },
];
//: How dark the room is between the lights — the ground every surface sees before it sees a
//: lamp. Not zero, for the same reason the floor is there.
const SURROUND = 0.40;

function studioRoom() {
  const room = new THREE.Scene();
  room.background = new THREE.Color(SURROUND, SURROUND, SURROUND);
  for (const { size, at, power } of [SOFTBOX, ...BOUNCE]) {
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
const pmrem = new THREE.PMREMGenerator(renderer);
export const studioEnvironment = pmrem.fromScene(studioRoom(), 0.03).texture;

// The rig every 3D surface in the app is lit by. step.js's offscreen thumbnail
// scene takes the same one, so a part's grid thumbnail and its detail view are
// lit from the same directions.
// A RIG NAILED TO THE WORLD STARVES A FACE. Lamps at fixed world positions light the sides they
// happen to point at, and the machine is a closed box: orbit to the far side and the whole
// silhouette falls to ambient, which is the one term carrying no form at all. The back of this
// box read light grey and the front read near-black for exactly that reason — key and softbox
// both stood on +Y.
//
// So the three lamps travel with the eye, in the camera's own basis, the way a photographer
// carries a rig around a subject rather than nailing it to the room: KEY up and to the left of
// the lens, FILL down and right at a fifth of it, RIM behind the subject to lift its edge off
// the background. What stays fixed in the world is the ENVIRONMENT, because reflections have to
// slide across a surface as it turns — a specular that travels with you is painted on, and the
// eye reads that as fake immediately.
const KEY_DIR = [-0.55, 0.62, 0.55];   // in camera basis: left, up, toward the eye
const FILL_DIR = [0.70, -0.35, 0.35];
const RIM_DIR = [0.25, 0.55, -0.85];   // behind the subject, raking its far edge

// THE RIG BELONGS TO ITS SCENE, not to this module. `addStudioLighting` is called twice — once
// for the model and once for step.js's offscreen thumbnail scene — so a lamp held in a module
// variable is overwritten by whichever scene was lit second, and the FIRST scene's lamps are
// then never aimed at all. They sit at the origin pointing at the origin, contribute nothing,
// and every scrap of form the picture has comes from the environment alone. Hanging the rig on
// the scene that owns it is what makes two lit scenes possible.

// The lamps are placed each frame from the camera's own axes. `_aimAt` puts one at `dir` in that
// basis, a fixed distance out, and a DirectionalLight only cares about direction so the distance
// is arbitrary — it just has to be outside the model.
function _aimAt(light, dir, cam, target, reach) {
  const right = new THREE.Vector3(), up = new THREE.Vector3(), back = new THREE.Vector3();
  cam.matrixWorld.extractBasis(right, up, back);
  light.position.copy(target)
    .addScaledVector(right, dir[0] * reach)
    .addScaledVector(up, dir[1] * reach)
    .addScaledVector(back, dir[2] * reach);
  light.target.position.copy(target);
  light.target.updateMatrixWorld();
}

export function aimLights(cam, target, radius, host = scene) {
  const rig = host && host.userData && host.userData.hsmRig;
  if (!rig) return;
  const reach = Math.max(radius, 1) * 4;
  _aimAt(rig.key, KEY_DIR, cam, target, reach);
  _aimAt(rig.fill, FILL_DIR, cam, target, reach);
  _aimAt(rig.rim, RIM_DIR, cam, target, reach);
}

export function addStudioLighting(target) {
  // AMBIENT IS THE TERM THAT FLATTENS. It reaches every face at one value regardless of which way
  // that face points, so every unit of it is a unit of shape removed — and at 0.5 it was most of
  // the light in the room. What is left is a floor under the deepest shadow, not a light.
  target.add(new THREE.AmbientLight(0xffffff, 0.14));
  const key = new THREE.DirectionalLight(0xffffff, 3.4);
  const fill = new THREE.DirectionalLight(0xffffff, 0.60);
  const rim = new THREE.DirectionalLight(0xffffff, 1.25);
  for (const l of [key, fill, rim]) { target.add(l); target.add(l.target); }
  target.userData.hsmRig = { key, fill, rim };
  // Sky above, a cooler ground below — the gradient a room actually has, and the cheapest cue
  // that there is an up.
  target.add(new THREE.HemisphereLight(0xdfe6ff, 0x24242e, 0.34));
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
  resizeComposer(w, h);
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
    new THREE.Box3().setFromObject(group).getBoundingSphere(_depthSphere);
    _depthGroup = group;
  }
  fitFog(scene, camera.position.distanceTo(_depthSphere.center), _depthSphere.radius);
  aimLights(camera, _depthSphere.center, _depthSphere.radius);
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

// --- what a corner does to the light -----------------------------------------------------
//
// NOTHING IN A DIRECT RENDER KNOWS THAT A GROOVE IS A GROOVE. Ambient and hemisphere light reach
// every face at full value whatever stands in front of it, so the floor of a 1.2 mm flute is lit
// exactly as brightly as the ridge beside it and a 460 mm wall of them reads as a soft ripple
// rather than as cut material. It is the single largest reason a render of a shape-dense part
// looks like a render: real crevices are dark, and the darkness is what the eye reads depth from.
//
// GTAO puts it back — for each pixel it asks how much of the sky that point can actually see and
// dims it by the answer. On this machine that is every flute valley, every counterbore, the seam
// between two quadrants, the land under every boss, the inside of every port.
//
// SCREEN-SPACE RADIUS, not world. A viewer's zoom runs from the whole 460 mm box down to a
// nameplate a few millimetres across, and a radius fixed in millimetres is either invisible at
// one end or smeared over the whole frame at the other. Asking for it in screen terms holds the
// effect at the scale the eye is actually looking at.
const AO_RADIUS = 0.28;
const AO_SAMPLES = 16;

let composer = null;
let gtaoPass = null;

function buildComposer() {
  try {
    const c = renderer.domElement;
    const w = Math.max(c.width, 1), h = Math.max(c.height, 1);
    const made = new EffectComposer(renderer);
    made.addPass(new RenderPass(scene, camera));
    const ao = new GTAOPass(scene, camera, w, h);
    ao.output = GTAOPass.OUTPUT.Default;
    ao.updateGtaoMaterial({
      radius: AO_RADIUS, screenSpaceRadius: true,
      distanceExponent: 1.0, thickness: 1.0, scale: 1.0,
      samples: AO_SAMPLES, distanceFallOff: 1.0,
    });
    made.addPass(ao);
    made.addPass(new OutputPass());
    made.setSize(w, h);
    composer = made;
    gtaoPass = ao;
  } catch (err) {
    // A browser that cannot build the composer still gets the model, without the occlusion.
    console.warn("post-processing unavailable, drawing direct:", err);
    composer = null;
    gtaoPass = null;
  }
}

export function resizeComposer(w, h) {
  if (composer) composer.setSize(w, h);
  if (gtaoPass) gtaoPass.setSize(w, h);
}

// The one place a frame is drawn, so the composer and the direct path cannot drift.
export function renderFrame() {
  if (composer) composer.render();
  else renderer.render(scene, camera);
}

// Built here rather than beside `addStudioLighting` above: `composer` is a `let` in this block,
// and a call placed before it runs in its dead zone.
buildComposer();

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
  renderFrame();
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
