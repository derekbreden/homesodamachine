// Shared CAD navigation. Scene owners supply geometry and framing bounds;
// the same Trackball gestures, surface zoom and ViewCube serve every 3D bench.
import * as THREE from "three";
import { TrackballControls } from "three/addons/controls/TrackballControls.js";

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

export function saveCameraPose(camera, controls, key) {
  if (!key) return false;
  try {
    localStorage.setItem(key, JSON.stringify({ p: camera.position.toArray(), u: camera.up.toArray(), t: controls.target.toArray() }));
    return true;
  } catch { return false; }
}

export function applyCameraPose(camera, controls, key) {
  try {
    const raw = localStorage.getItem(key);
    if (!raw) return false;
    const pose = JSON.parse(raw);
    if (![pose.p, pose.u, pose.t].every(row => Array.isArray(row) && row.length === 3 && row.every(Number.isFinite))) return false;
    camera.position.fromArray(pose.p); camera.up.fromArray(pose.u); controls.target.fromArray(pose.t);
    controls.update();
    return true;
  } catch { return false; }
}

export function createNavigation({
  camera, renderer, canvas = renderer.domElement, getGroup = () => null, getBounds,
  defaultUp = new THREE.Vector3(0, 0, 1), invalidate = () => {}, onDepthFit,
  gizmoClassName = "cad-gizmo", gizmoSize: requestedGizmoSize, gizmoStyleTarget,
} = {}) {
  const removers = [];
  function listen(target, type, callback, options) {
    target.addEventListener(type, callback, options);
    removers.push(() => target.removeEventListener(type, callback, options));
  }
  const controls = new TrackballControls(camera, canvas);
  controls.rotateSpeed = 3;
  controls.panSpeed = .2;
  controls.staticMoving = false;
  controls.dynamicDampingFactor = .12;
  const depthSphere = new THREE.Sphere();
  let mode = "rotate", nativeGesture = null, changeSerial = 0, disposed = false;

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
  // A floor dolly rides on that scale: each zoomed frame also translates camera
  // and target together, a fixed fraction of the model's radius per unit of
  // fractional zoom. Zoom slows against a surface, holds a floor speed, crosses
  // to the far side, and the wheel tick after crossing re-picks there.
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
  // One wheel notch spent against a surface dollies the rig about an eightieth
  // of the model's radius.
  const ZOOM_FLOOR_RATIO = 0.05;
  let surfaceZoomActive = false;

  function visibleInGroup(object, group) {
    for (let node = object; node; node = node.parent) {
      if (!node.visible) return false;
      if (node === group) return true;
    }
    return false;
  }

  function surfaceUnderPointer(clientX, clientY) {
    const mounted = getGroup();
    const groups = (Array.isArray(mounted) ? mounted : [mounted]).filter(Boolean);
    if (!groups.length) return null;
    const rect = canvas.getBoundingClientRect();
    if (!(rect.width > 0) || !(rect.height > 0)) return null;
    _surfacePointer.set(((clientX - rect.left) / rect.width) * 2 - 1,
      -((clientY - rect.top) / rect.height) * 2 + 1);
    _surfaceRaycaster.layers.mask = camera.layers.mask;
    _surfaceRaycaster.setFromCamera(_surfacePointer, camera);
    const hit = _surfaceRaycaster.intersectObjects(groups, true).find(({ object, face }) =>
      face && object.isMesh && !object.userData.hitOnly && groups.some(group => visibleInGroup(object, group)));
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
    if (!this.object.isPerspectiveCamera || !(distanceBefore > 0)) return;

    const distanceAfter = this._eye.length();
    const scale = distanceAfter / distanceBefore;
    if (!Number.isFinite(scale) || Math.abs(scale - 1) < 1e-12) return;

    if (surfaceZoomActive) {
      // Trackball has already scaled `_eye` about target. Translating target by
      // this amount makes the resulting camera + target identical to scaling both
      // about the picked surface point. update() applies target + `_eye` to the
      // camera immediately after this method returns.
      _surfaceOffset.copy(_surfaceAnchor)
        .sub(_surfaceTargetBeforeZoom)
        .multiplyScalar(1 - scale);
      this.target.add(_surfaceOffset);
    }

    // Floor dolly: translating only `target` moves the camera with it — update()
    // re-derives the camera as target + `_eye`. A step along the camera-to-anchor
    // line holds the anchor's projection fixed beneath the pointer; within one
    // step of the anchor that line degenerates, and the step runs down the view
    // direction instead, through the surface.
    const radius = depthSphere.radius; // measured per mounted group by updateDepthRange()
    if (!(radius > 0) || !(distanceAfter > 0)) return;
    const floorStep = ZOOM_FLOOR_RATIO * radius * (1 - scale);
    _surfaceForward.copy(this._eye).divideScalar(-distanceAfter);
    if (surfaceZoomActive) {
      _surfaceOffset.copy(_surfaceAnchor).sub(this.target).sub(this._eye);
      if (_surfaceOffset.dot(_surfaceForward) > Math.abs(floorStep)) {
        this.target.addScaledVector(_surfaceOffset, floorStep / _surfaceOffset.length());
        return;
      }
    }
    this.target.addScaledVector(_surfaceForward, floorStep);
  };

  // Capture runs before TrackballControls' own target-phase handlers, so the new
  // depth is in place when it records and consumes the gesture.
  listen(canvas, "wheel", (e) => {
    if (e.deltaY) { fitDepth(); beginSurfaceZoom(e.clientX, e.clientY); }
  }, { capture: true, passive: true });

  const surfaceTouches = new Map();
  listen(canvas, "pointerdown", (e) => {
    if (e.pointerType === "touch") {
      if (mode === "zoom") beginSurfaceZoom(e.clientX, e.clientY);
      surfaceTouches.set(e.pointerId, { x: e.clientX, y: e.clientY });
      if (surfaceTouches.size >= 2) {
        canvas.parentElement?.classList.add("cad-gesturing");
        const pair = [...surfaceTouches.values()].slice(0, 2);
        beginSurfaceZoom((pair[0].x + pair[1].x) / 2, (pair[0].y + pair[1].y) / 2);
      }
    } else if (e.button === 1 || mode === "zoom" || controls.keyState === TRACKBALL_ZOOM_STATE) {
      // Middle-drag, or TrackballControls' S-key + drag zoom mode.
      beginSurfaceZoom(e.clientX, e.clientY);
    }
  }, true);
  listen(canvas, "pointermove", (e) => {
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
  function forgetSurfaceTouch(e) {
    if (!surfaceTouches.delete(e.pointerId)) return;
    if (surfaceTouches.size) return;
    const wrapper = canvas.parentElement;
    // Keep the gate through the final pointerup so a pinch cannot become a pick.
    requestAnimationFrame(() => {
      if (!surfaceTouches.size) wrapper?.classList.remove("cad-gesturing");
    });
  }
  listen(document, "pointerup", forgetSurfaceTouch, true);
  listen(document, "pointercancel", forgetSurfaceTouch, true);
  function clearTouches() {
    surfaceTouches.clear();
    nativeGesture = null;
    endGesture();
    dropStalledGesture();
    for (const pointer of controls._pointers) {
      if (canvas.hasPointerCapture?.(pointer.pointerId)) canvas.releasePointerCapture(pointer.pointerId);
    }
    controls._pointers.length = 0;
    controls._pointerPositions = {};
    controls.state = controls.keyState = -1;
    canvas.removeEventListener("pointermove", controls._onPointerMove);
    canvas.removeEventListener("pointerup", controls._onPointerUp);
    canvas.parentElement?.classList.remove("cad-gesturing");
  }
  listen(window, "blur", clearTouches);
  listen(document, "visibilitychange", () => { if (document.hidden) clearTouches(); });

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

  listen(controls, "start", () => { gesturing = true; });
  listen(controls, "end", endGesture);
  // Safety net for a pointerup that never reaches the controls (capture lost,
  // gesture cancelled). Capture phase on document, alongside the gizmo handlers
  // below — their stopPropagation doesn't reach listeners on the same node in the
  // same phase.
  listen(document, "pointerup", endGesture, true);
  listen(document, "pointercancel", endGesture, true);

  function afterGesture() {
    if (!gesturing) return Promise.resolve();
    return new Promise((resolve) => gestureWaiters.push(resolve));
  }

  // --- ViewCube ---
  // Each cube face's projected hit area is roughly gizmoSize/2 — Apple HIG
  // asks for 44pt minimum touch targets, so we size to comfortably exceed
  // that on every face. The pointer-events:none on the canvas passes empty
  // corners through to TrackballControls; the visible cube IS the touch
  // target, so growing the canvas grows the touch area too.
  function gizmoEdge() {
    const requested = typeof requestedGizmoSize === "function" ? requestedGizmoSize() : requestedGizmoSize;
    return requested ?? (window.matchMedia("(max-width: 600px)").matches ? 140 : 180);
  }
  let gizmoSize = gizmoEdge();
  const gizmoRenderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
  gizmoRenderer.setPixelRatio(renderer.getPixelRatio());
  gizmoRenderer.setSize(gizmoSize, gizmoSize);
  gizmoRenderer.setClearColor(0x000000, 0);
  // The panels that stand clear of the cube lay themselves out against
  // --cube-size, which is the edge the canvas is actually drawn at — so the
  // window can cross the breakpoint and the two stay in agreement.
  // resizeRenderer calls this on every observed box change.
  function syncGizmoSize() {
    const next = gizmoEdge();
    if (next !== gizmoSize) {
      gizmoSize = next;
      gizmoRenderer.setSize(gizmoSize, gizmoSize);
    }
    (gizmoStyleTarget || canvas.parentElement || document.documentElement).style.setProperty("--cube-size", gizmoSize + "px");
  }
  syncGizmoSize();
  const gizmoCanvas = gizmoRenderer.domElement;
  gizmoCanvas.style.pointerEvents = "none";
  // .cad-gizmo: position:absolute inside the wrapper (top-right, safe-area
  // padded), pointer-events:none so empty corners pass touches through to
  // TrackballControls. Hits on the rendered cube are picked up via document-level
  // raycast handlers below.
  gizmoCanvas.classList.add(gizmoClassName);

  const gizmoScene = new THREE.Scene();
  const gizmoCam = new THREE.PerspectiveCamera(45, 1, 0.1, 100);
  const gizmoRaycaster = new THREE.Raycaster();

  // The cube's six faces in BoxGeometry's own material order — +X, -X, +Y, -Y,
  // +Z, -Z. That order is the mapping: a face's place in this array is the slot
  // its label is painted on, and the raycast reads the same places back out of
  // `hit.face.materialIndex`. Repo convention is +Z-up CAD: +Z height, -Y front
  // (user side), +X right. `normal` is where the camera stands to see the face.
  const basisUp = (defaultUp.isVector3 ? defaultUp.clone() : new THREE.Vector3(...defaultUp)).normalize();
  const basisRight = new THREE.Vector3(1, 0, 0);
  const basisBack = new THREE.Vector3().crossVectors(basisUp, basisRight).normalize();
  const cubeFaces = [[1,0,0],[-1,0,0],[0,1,0],[0,-1,0],[0,0,1],[0,0,-1]].map(axis => {
    const normal = new THREE.Vector3(...axis);
    const vertical = normal.dot(basisUp), horizontal = normal.dot(basisRight), depth = normal.dot(basisBack);
    const label = Math.abs(vertical) > .9 ? vertical > 0 ? "Top" : "Bottom"
      : Math.abs(horizontal) > .9 ? horizontal > 0 ? "Right" : "Left" : depth > 0 ? "Back" : "Front";
    return { label, normal };
  });
  const ownedTextures = new Set();

  function makeFaceTexture(label, isHovered) {
    const canvas = document.createElement("canvas");
    canvas.width = 256; canvas.height = 256;
    const ctx = canvas.getContext("2d");
    const bg = isHovered ? "#1749d1" : "#10319c";
    const border = "#6b8fe9";
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
    ctx.fillStyle = isHovered ? "#ffffff" : "#dce6ff";
    ctx.fillText(label, 128, 128);
    const tex = new THREE.CanvasTexture(canvas);
    tex.colorSpace = THREE.SRGBColorSpace;
    ownedTextures.add(tex);
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
    ownedTextures.add(tex);
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
  // can decide whether the gesture belongs to the gizmo *before* TrackballControls
  // sees it. The canvas itself is pointer-events:none, so any tap that doesn't
  // raycast-hit the cube falls straight through to the 3D viewport underneath.
  let hoveredFaceIndex = -1;
  let armedAtPointerDown = false;          // true when pointerdown landed on the cube

  function gizmoRaycastFromEvent(e) {
    if (canvas.parentElement?.classList.contains("cad-gesturing")) return null;
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
    return e.target === canvas || e.target === gizmoCanvas;
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

  listen(document, "mousemove", (e) => {
    const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
    const newIndex = hit ? hit.face.materialIndex : -1;
    if (newIndex !== hoveredFaceIndex) {
      if (hoveredFaceIndex >= 0) paintFace(hoveredFaceIndex, false);
      if (newIndex >= 0) paintFace(newIndex, true);
      hoveredFaceIndex = newIndex;
      invalidate();
    }
  });

  // Capture-phase pointerdown: if the tap raycast-hits the cube, claim the
  // gesture and keep TrackballControls from seeing it. Otherwise the event flows
  // through normally to TrackballControls / drag-to-orbit.
  listen(document, "pointerdown", (e) => {
    // A second finger joins the viewport gesture, including over the cube.
    if (e.pointerType === "touch" && surfaceTouches.size) { armedAtPointerDown = false; return; }
    const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
    if (!hit) { armedAtPointerDown = false; return; }
    armedAtPointerDown = true;
    e.stopPropagation();
    e.preventDefault();
  }, true);

  // Capture-phase pointerup: complete the snap if our pointerdown landed on
  // the cube AND this pointerup also lands on the cube (so a drag off the
  // cube cancels rather than snaps).
  listen(document, "pointerup", (e) => {
    if (!armedAtPointerDown) return;
    armedAtPointerDown = false;
    const hit = overCanvas(e) ? gizmoRaycastFromEvent(e) : null;
    e.stopPropagation();
    e.preventDefault();
    if (!hit) return;
    const face = cubeFaces[hit.face.materialIndex];
    snapToFace(face.normal);
  }, true);

  let snapRafId = 0;
  function stopSnap() { if (snapRafId) cancelAnimationFrame(snapRafId); snapRafId = 0; }
  function snapToFace(normal) {
    controls.dispatchEvent({ type: "start" });
    dropStalledGesture();
    normal = normal.isVector3 ? normal.clone() : new THREE.Vector3(...normal);
    const target = controls.target.clone();
    const dist = camera.position.distanceTo(target);
    const dest = target.clone().add(normal.clone().multiplyScalar(dist));

    // Pole snaps use the back axis as up; ordinary faces keep the host's
    // default up. This preserves Z-up CAD and gives Y-up benches Top +Y.
    const vertical = normal.dot(basisUp);
    const up = Math.abs(vertical) > .9
      ? basisBack.clone().multiplyScalar(vertical > 0 ? -1 : 1) : basisUp.clone();

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
      invalidate();
      if (t < 1) snapRafId = requestAnimationFrame(animateSnap);
      else { snapRafId = 0; controls.dispatchEvent({ type: "end" }); }
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

  const STALL_MS = 400;

  function dropStalledGesture() {
    // three@0.170.0 internals; the importmap pins that exact build.
    controls._movePrev?.copy(controls._moveCurr);  // rotate: the stale delta
    controls._panStart?.copy(controls._panEnd);    // pan: same shape
    controls._zoomStart?.copy(controls._zoomEnd);  // zoom: same shape
    controls._lastAngle = 0;                       // and the rotation flywheel
  }


  // Trackball fixes one-finger touch to rotation. Reuse its native pan/zoom
  // accumulators for the host's explicit tool, retaining native two-finger
  // combined pan/pinch and its pointer bookkeeping.
  const touchStart = controls._onTouchStart;
  const touchMove = controls._onTouchMove;
  const touchEnd = controls._onTouchEnd;
  function seedSingleTouch(event) {
    controls.state = mode === "pan" ? 2 : 1;
    controls._lastAngle = 0;
    controls._movePrev.copy(controls._moveCurr);
    const point = controls._getMouseOnScreen(event.pageX, event.pageY);
    if (mode === "pan") { controls._panStart.copy(point); controls._panEnd.copy(point); }
    else { controls._zoomStart.copy(point); controls._zoomEnd.copy(point); }
  }
  controls._onTouchStart = event => {
    touchStart(event);
    if (mode !== "rotate" && controls._pointers.length === 1) seedSingleTouch(event);
  };
  controls._onTouchMove = event => {
    if (mode === "rotate" || controls._pointers.length !== 1) { touchMove(event); return; }
    controls._trackPointer(event);
    const point = controls._getMouseOnScreen(event.pageX, event.pageY);
    if (mode === "pan") controls._panEnd.copy(point);
    else controls._zoomEnd.copy(point);
  };
  controls._onTouchEnd = event => {
    touchEnd(event);
    if (mode === "rotate") return;
    const remaining = controls._pointers.filter(pointer => pointer.pointerId !== event.pointerId);
    if (remaining.length === 1) {
      const point = controls._pointerPositions[remaining[0].pointerId];
      seedSingleTouch({ pageX: point.x, pageY: point.y });
    }
  };

  // WebKit trackpads may supply native scale events instead of ctrl-wheel.
  // Feed incremental scale through the same surface-aware Trackball zoom,
  // consuming each increment once instead of starting another damping tail.
  listen(canvas, "gesturestart", event => {
    if (!controls.enabled || controls.noZoom || surfaceTouches.size > 1) return;
    event.preventDefault(); dropStalledGesture(); fitDepth();
    beginSurfaceZoom(event.clientX, event.clientY);
    nativeGesture = { scale: 1 };
    canvas.parentElement?.classList.add("cad-gesturing");
    controls.dispatchEvent({ type: "start" });
  }, { passive: false });
  listen(canvas, "gesturechange", event => {
    if (!nativeGesture || !Number.isFinite(event.scale) || event.scale <= 0) return;
    event.preventDefault();
    if (surfaceTouches.size > 1) return;
    beginSurfaceZoom(event.clientX, event.clientY);
    const factor = nativeGesture.scale / event.scale;
    nativeGesture.scale = event.scale;
    controls._zoomStart.y = 0;
    controls._zoomEnd.y = (factor - 1) / controls.zoomSpeed;
    controls.update();
    controls._zoomStart.copy(controls._zoomEnd);
    invalidate();
  }, { passive: false });
  listen(canvas, "gestureend", event => {
    if (!nativeGesture) return;
    event.preventDefault(); nativeGesture = null;
    controls.dispatchEvent({ type: "end" });
    const wrapper = canvas.parentElement;
    requestAnimationFrame(() => { if (!nativeGesture && !surfaceTouches.size) wrapper?.classList.remove("cad-gesturing"); });
  }, { passive: false });

  let lastFrameAt = 0;
  function fitDepth(bounds = getBounds?.()) {
    if (!bounds) {
      if (getBounds) return null;
      const mounted = getGroup();
      const groups = (Array.isArray(mounted) ? mounted : [mounted]).filter(Boolean);
      if (!groups.length) return null;
      bounds = new THREE.Box3();
      groups.forEach(group => bounds.expandByObject(group));
    }
    if (bounds.isSphere || bounds instanceof THREE.Sphere) depthSphere.copy(bounds);
    else {
      if (bounds.isEmpty()) return null;
      bounds.getBoundingSphere(depthSphere);
    }
    if (!(depthSphere.radius > 0)) return null;
    fitCameraDepth(camera, depthSphere.center, depthSphere.radius);
    onDepthFit?.(depthSphere);
    return depthSphere;
  }
  function resize() {
    syncGizmoSize();
    controls.handleResize();
    // Preserve the CAD viewer's height-based trackball travel and symmetric pan.
    controls.screen.width = controls.screen.height;
    invalidate();
  }
  function update(now = performance.now()) {
    if (disposed) return false;
    if (lastFrameAt && now - lastFrameAt > STALL_MS) dropStalledGesture();
    lastFrameAt = now;
    const before = changeSerial;
    controls.update(); fitDepth(); renderGizmo();
    return changeSerial !== before || !!snapRafId;
  }
  function setMode(next) {
    if (!["rotate", "pan", "zoom"].includes(next)) return;
    dropStalledGesture(); mode = next;
    controls.mouseButtons.LEFT = next === "pan" ? THREE.MOUSE.PAN : next === "zoom" ? THREE.MOUSE.DOLLY : THREE.MOUSE.ROTATE;
    invalidate();
  }
  listen(controls, "change", () => { changeSerial++; invalidate(); });
  listen(controls, "start", () => { stopSnap(); lastFrameAt = 0; invalidate(); });
  // Trackball accumulates pointer deltas until update(); unlike TrackballControls,
  // its move handler does not dispatch change. Wake on-demand scene owners.
  listen(canvas, "pointermove", event => {
    if (controls.enabled && (controls._pointers.length || event.buttons)) invalidate();
  });
  function dispose() {
    if (disposed) return;
    disposed = true; stopSnap(); clearTouches();
    removers.splice(0).forEach(remove => remove());
    controls.dispose();
    gizmoScene.traverse(object => {
      object.geometry?.dispose();
      for (const material of Array.isArray(object.material) ? object.material : object.material ? [object.material] : []) material.dispose();
    });
    ownedTextures.forEach(texture => texture.dispose());
    gizmoRenderer.dispose(); gizmoCanvas.remove();
  }
  return {
    controls, gizmoCanvas, update, resize, fitDepth, clearTouches, afterGesture,
    renderGizmo, syncGizmoSize, snapToFace, setMode, dropStalledGesture, dispose,
    resetFrameClock() { lastFrameAt = 0; },
    savePose(key) { return saveCameraPose(camera, controls, key); },
    applyPose(key) { dropStalledGesture(); const applied = applyCameraPose(camera, controls, key); if (applied) { fitDepth(); invalidate(); } return applied; },
    isTouchGesture() { return surfaceTouches.size > 1 || !!nativeGesture; },
    get mode() { return mode; },
    get depthSphere() { return depthSphere; },
  };
}
