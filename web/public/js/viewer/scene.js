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
import { createNavigation, saveCameraPose } from "./navigation.js";
export { depthRangeFor, fitCameraDepth } from "./navigation.js";
import { state } from "./state.js";
import { syncEdgeResolution } from "./xray.js";

// --- Detail view: Three.js setup ---
export const canvasHost = document.getElementById("cad-canvas-host");

// Exposure shared with the owner-guide Fill artwork and step.js's thumbnails.
export const TONE_EXPOSURE = 0.6;
// What every 3D surface in the app clears to, and what distance fades toward.
export const BG_COLOR = 0x10319c;

// Headless instruction renders can request a canvas with a real alpha channel.
// The ordinary viewer keeps the browser default (opaque) context, so its
// interactive rendering path is unchanged.
const renderAlpha = new URLSearchParams(window.location.search).get("renderAlpha") === "1";
export const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: renderAlpha });
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
const navigation = createNavigation({
  camera, renderer, getGroup: () => state.currentGroup, getBounds: navigationDepthBounds,
  defaultUp: new THREE.Vector3(0, 0, 1), gizmoStyleTarget: document.documentElement,
  onDepthFit: sphere => fitFog(scene, camera.position.distanceTo(sphere.center), sphere.radius),
});
export const controls = navigation.controls;
export const gizmoCanvas = navigation.gizmoCanvas;
gizmoCanvas.id = "gizmoCanvas";
canvasHost.appendChild(gizmoCanvas);
export const clearSurfaceTouches = () => navigation.clearTouches();
export const afterGesture = () => navigation.afterGesture();
export const syncGizmoSize = () => navigation.syncGizmoSize();

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
// The prefiltered texture lives in the renderer's WebGL context. Each renderer
// bakes the same room into its own texture when its scene is initialized.
function studioEnvironmentFor(targetRenderer) {
  const room = studioRoom();
  const pmrem = new THREE.PMREMGenerator(targetRenderer);
  const texture = pmrem.fromScene(room, 0.03).texture;
  pmrem.dispose();
  room.traverse((object) => {
    object.geometry?.dispose();
    object.material?.dispose();
  });
  return texture;
}

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
export function addStudioLighting(target, targetRenderer) {
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
  target.environment = studioEnvironmentFor(targetRenderer);
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

addStudioLighting(scene, renderer);

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
export function fitGroundShadow(box, { opacity = 1 } = {}) {
  dropGroundShadow();
  if (!box || box.isEmpty()) return;
  const size = box.getSize(new THREE.Vector3());
  const centre = box.getCenter(new THREE.Vector3());
  if (!(size.x > 0) || !(size.y > 0)) return;
  const mesh = new THREE.Mesh(
    new THREE.PlaneGeometry(1, 1),
    new THREE.MeshBasicMaterial({
      map: shadowTexture(size.y / size.x),
      transparent: true, opacity, depthWrite: false, fog: false,
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
    // The layout size, not the rect on screen: the viewer opens with a scale transition, and a
    // ResizeObserver never reports the transform settling.
    w = parent.clientWidth;
    h = parent.clientHeight + viewInset;
  }
  if (w === 0 || h === viewInset) {
    w = window.innerWidth;
    h = window.innerHeight;
  }
  // Resizing clears the drawing buffer, so an unchanged size is not set again.
  const ratio = renderer.getPixelRatio();
  if (w !== drawnSize.w || h !== drawnSize.h || ratio !== drawnSize.ratio) {
    renderer.setSize(w, h, false);
    Object.assign(drawnSize, { w, h, ratio });
  }
  // Also re-apply CSS size — setSize(...,false) doesn't touch style, and we
  // want the canvas to actually fill the wrapper's content box.
  renderer.domElement.style.width = w + "px";
  renderer.domElement.style.height = h + "px";
  camera.aspect = w / h;
  if (viewInset) camera.setViewOffset(w, h, 0, viewInset / 2, w, h);
  else camera.clearViewOffset();
  camera.updateProjectionMatrix();
  navigation.resize();
}
const drawnSize = { w: 0, h: 0, ratio: 0 };

// A phone's Materials sheet covers the bottom of the model. The canvas keeps its full height
// under the sheet, so moving it never reallocates the drawing buffer or rescales a gesture
// in progress, and the view's centre sits in the part left uncovered: framing puts a part
// there. `hold` keeps the picture still while the centre moves, as a map stays put under a
// sheet; without it the picture re-centres in what is left. `goal` is the inset a moving sheet
// is settling at, which framing aims for.
let viewInset = 0;
let goalInset = 0;
export function setViewInset(px, { hold = true, goal = px } = {}) {
  px = Math.max(0, Math.round(px));
  goalInset = Math.max(0, Math.round(goal));
  if (px === viewInset) return;
  if (hold) {
    // The centre rises by half the change; the camera rises with it, so nothing on screen moves.
    const height = renderer.domElement.clientHeight || 1;
    const perPixel = 2 * camera.position.distanceTo(controls.target)
      * Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2) / height;
    const shift = new THREE.Vector3(0, 1, 0).applyQuaternion(camera.quaternion)
      .multiplyScalar((px - viewInset) / 2 * perPixel);
    camera.position.add(shift);
    controls.target.add(shift);
  }
  viewInset = px;
  resizeRenderer();
}

// The share of the canvas's height the sheet leaves uncovered, once it settles.
export function visibleShare() {
  const height = drawnSize.h || renderer.domElement.clientHeight || 1;
  return Math.max(0.2, Math.min(1, (height - goalInset) / height));
}

// Mounted geometry and scene siblings share the navigation camera depth.
let _depthGroup = null;
const _depthSphere = new THREE.Sphere();
const _modelDepthBox = new THREE.Box3();
const _extraDepthBounds = new Map();
let _depthBoundsRevision = 0, _seenDepthBoundsRevision = -1;

// Optional scene siblings can extend the camera and fog range while retaining
// the model's own ground shadow and default framing.
export function setExtraDepthBounds(key, bounds) {
  if (!bounds || bounds.isEmpty()) {
    if (_extraDepthBounds.delete(key)) _depthBoundsRevision++;
    return;
  }
  if (_extraDepthBounds.get(key)?.equals(bounds)) return;
  _extraDepthBounds.set(key, bounds.clone());
  _depthBoundsRevision++;
}

function navigationDepthBounds() {
  const group = state.currentGroup;
  if (!group) return;
  if (group !== _depthGroup) {
    const box = new THREE.Box3().setFromObject(group);
    _modelDepthBox.copy(box);
    _depthBoundsRevision++;
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
  if (_seenDepthBoundsRevision !== _depthBoundsRevision) {
    const box = _modelDepthBox.clone();
    for (const extra of _extraDepthBounds.values()) box.union(extra);
    box.getBoundingSphere(_depthSphere);
    _seenDepthBoundsRevision = _depthBoundsRevision;
  }
  return _depthSphere;
}

export function updateDepthRange() { navigation.fitDepth(); }

let animating = false;
let animateRafId = 0;
function animate() {
  if (!animating) { animateRafId = 0; return; }
  animateRafId = requestAnimationFrame(animate);
  navigation.update();
  syncEdgeResolution(renderer);
  renderer.render(scene, camera);
}
export function startAnimate() {
  if (animating) return;
  animating = true;
  navigation.resetFrameClock(); // a closed modal is not a stall
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
  const key = `step-camera:${file}`;
  if (heldPose?.file === file) saveCameraPose(heldPose, heldPose, key);
  else navigation.savePose(key);
}

// A selection's fly-to is a look at one part, not where the reader left the
// model. While a selection is up (part-highlight.js), the view kept for its file
// is the one from before it, and leaving the selection flies back there.
let heldPose = null;
export function holdCameraPose() {
  const file = state.mountedDetail?.file;
  if (!file || heldPose?.file === file) return;
  heldPose = { file, position: camera.position.clone(), up: camera.up.clone(), target: controls.target.clone() };
}

export function releaseCameraPose() {
  const pose = heldPose;
  heldPose = null;
  return pose;
}

export function applyCameraState(file) {
  return navigation.applyPose(`step-camera:${file}`);
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
