// /scene viewer — line-art renderer for technical drawings.
//
// Loads a glTF (built from CadQuery) and renders it as line art with
// proper z-buffer occlusion. Parts whose assembly color is white (or
// near-grayscale) render as INVISIBLE surfaces with black feature
// edges on top — the surfaces contribute to the depth buffer so edges
// behind them get hidden, but no white fill is drawn. Parts whose
// color is saturated (e.g. the red CO2-port ring) render their
// surfaces directly in that color, without an edge overlay.
//
// Camera: orthographic, posed at iso-front (+x +y -z) or iso-back
// (+x +y +z) directions and framed to the model's bounding sphere.
//
// The headless render tool (tools/render/render-scene.js) drives this
// via window.__hsm_scene.

import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

const host = document.getElementById("scene-host");

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xffffff);

// Orthographic camera — technical drawings don't want perspective
// foreshortening. Extents are set by poseIso() once a model is loaded.
const camera = new THREE.OrthographicCamera(-1, 1, 1, -1, -10000, 10000);

const renderer = new THREE.WebGLRenderer({ antialias: true });
renderer.setPixelRatio(window.devicePixelRatio);
renderer.setClearColor(0xffffff);
host.appendChild(renderer.domElement);

// Line width in CSS pixels — matches the SVG line-art's stroke-width of
// 1.5 closely enough. Line2 (vs. LineSegments) is used because GL_LINES
// only ever draws 1-pixel lines on most platforms regardless of
// linewidth; Line2 renders lines as camera-facing triangle strips, so
// width is honoured.
const LINE_WIDTH_PX = 1.5;

// EdgesGeometry threshold (degrees). Edges are drawn where adjacent
// face normals differ by at least this angle. 15° captures sharp
// feature edges while not over-decorating smooth tessellated cylinders
// with sliver edges between adjacent triangles.
const EDGE_ANGLE_THRESHOLD_DEG = 15;

function resize() {
  const w = host.clientWidth;
  const h = host.clientHeight;
  renderer.setSize(w, h, false);
  // Keep camera ortho frustum centered; the actual extents are set by
  // poseIso() once we know the model bounds.
  refreshOrthoExtents();
  for (const m of _lineMaterials) m.resolution.set(w, h);
}
window.addEventListener("resize", resize);

const _lineMaterials = new Set();
// Camera-space framing: ortho extents are derived from the loaded model's
// bounding-box corners projected into camera space (poseIso fills these).
// Stored so a window resize can re-fit without recomputing the projection.
let _frameHalfW = 1;
let _frameHalfH = 1;
let _frameCx = 0;
let _frameCy = 0;
const FRAME_MARGIN = 1.05;

function refreshOrthoExtents() {
  const w = host.clientWidth || 1;
  const h = host.clientHeight || 1;
  const viewAspect = w / h;
  const modelAspect = _frameHalfW / _frameHalfH;
  let halfW, halfH;
  if (viewAspect >= modelAspect) {
    // Viewport wider than model — limit by model height, expand width.
    halfH = _frameHalfH;
    halfW = halfH * viewAspect;
  } else {
    // Viewport taller than model — limit by model width, expand height.
    halfW = _frameHalfW;
    halfH = halfW / viewAspect;
  }
  camera.left = _frameCx - halfW;
  camera.right = _frameCx + halfW;
  camera.top = _frameCy + halfH;
  camera.bottom = _frameCy - halfH;
  camera.updateProjectionMatrix();
}

function isMonochrome(color) {
  // r ≈ g ≈ b ⇒ default white/gray → render as line art (invisible fill,
  // black feature edges). Saturated colors → render as colored fill.
  const max = Math.max(color.r, color.g, color.b);
  const min = Math.min(color.r, color.g, color.b);
  return max - min < 0.05;
}

function applyLineArtMaterials(root) {
  // Collect meshes BEFORE mutating: Line2 (the thick-line primitive used
  // for edge overlays below) inherits isMesh=true from Mesh, so a live
  // traverse would re-visit each freshly-added Line2 and try to make a
  // line-art outline of its own outline — infinite recursion.
  const meshes = [];
  root.traverse((n) => { if (n.isMesh && !n.userData?.lineArtOverlay) meshes.push(n); });
  for (const node of meshes) {
    const origColor = node.material.color.clone();
    if (isMonochrome(origColor)) {
      // Invisible-but-occluding surface: writes depth, skips color. Three.js'
      // default depthFunc=LessEqualDepth lets the EdgesGeometry overlay
      // win the depth test at the same depth as the surface — no polygon
      // offset needed. AVOID polygon offset here: it would push the
      // body's surface depth BEHIND nearby colored parts (like the red
      // ring on the wall just behind the CO2 coupling), breaking the
      // occlusion that's the whole point of running this through a
      // z-buffer renderer.
      node.material = new THREE.MeshBasicMaterial({
        colorWrite: false,
        depthWrite: true,
      });

      // Feature-edge overlay: Line2 (triangle-strip lines) for honored
      // line width. EdgesGeometry gives a non-indexed array of vertex
      // pairs; LineSegmentsGeometry wants flat [x1,y1,z1,x2,y2,z2,...].
      const edges = new THREE.EdgesGeometry(
        node.geometry, EDGE_ANGLE_THRESHOLD_DEG,
      );
      const positions = edges.attributes.position.array;
      const geo = new LineSegmentsGeometry();
      geo.setPositions(positions);
      const mat = new LineMaterial({
        color: 0x000000,
        linewidth: LINE_WIDTH_PX,
        worldUnits: false,
        resolution: new THREE.Vector2(host.clientWidth || 1, host.clientHeight || 1),
        polygonOffset: false,
      });
      _lineMaterials.add(mat);
      const lines = new Line2(geo, mat);
      lines.computeLineDistances();
      lines.userData.lineArtOverlay = true;
      node.add(lines);
    } else {
      // Colored part — flat color, no shading, no edge overlay. Surface
      // is rendered normally so it can be occluded by other meshes via
      // z-buffer (and itself occlude monochrome edges behind it).
      node.material = new THREE.MeshBasicMaterial({ color: origColor });
    }
  }
}

async function loadScene(glbUrl) {
  // Clear any previously-loaded scene roots, keep lights/camera siblings.
  for (let i = scene.children.length - 1; i >= 0; i--) {
    const c = scene.children[i];
    if (c.userData?.loaded) scene.remove(c);
  }
  const loader = new GLTFLoader();
  const gltf = await loader.loadAsync(glbUrl);
  // CadQuery's glTF export (via OCCT) bakes a Z-up → Y-up rotation into
  // the vertex positions. Our model is Z-up (+Z is height, +Y is depth),
  // so the rotation is correct as-is: after load the model sits Y-up in
  // three.js with the original +Z height now pointing along three.js +Y.
  gltf.scene.updateMatrixWorld(true);
  gltf.scene.userData.loaded = true;
  applyLineArtMaterials(gltf.scene);
  scene.add(gltf.scene);
  return gltf.scene;
}

// Camera direction (from scene center toward the camera) for each named
// view. Source convention (CadQuery): +X width, +Y depth, +Z height.
// After OCCT's Z-up→Y-up glTF rotation, in three.js the model sits with
// three.js +X = cad +X, three.js +Y = cad +Z (height), three.js -Z = cad
// +Y (depth into the back of the model).
//
// iso-front: camera at +X (right) + Y (top) + Z (front side, looking
// toward back) → (1, 1, 1)
// iso-back:  camera at +X + Y - Z (behind the back face) → (1, 1, -1)
const VIEW_DIRECTIONS = {
  "iso-front": [1, 1,  1],
  "iso-back":  [1, 1, -1],
};

function poseIso(dir) {
  const box = new THREE.Box3().setFromObject(scene);
  const center = box.getCenter(new THREE.Vector3());
  const sphere = box.getBoundingSphere(new THREE.Sphere());

  const v = new THREE.Vector3(...dir).normalize();
  camera.up.set(0, 1, 0);
  // Distance only affects clip planes (ortho doesn't use it for scale).
  // 3× sphere radius keeps near/far clipping well away from the model.
  camera.position.copy(center).add(v.multiplyScalar(sphere.radius * 3));
  camera.lookAt(center);
  camera.updateMatrixWorld(true);

  // Tight-fit ortho extents by projecting all 8 bbox corners into camera
  // space and using their actual screen-aligned extents. A bounding-sphere
  // fit (used previously) over-pads because a box's projection is much
  // smaller than its enclosing sphere.
  const corners = [
    new THREE.Vector3(box.min.x, box.min.y, box.min.z),
    new THREE.Vector3(box.min.x, box.min.y, box.max.z),
    new THREE.Vector3(box.min.x, box.max.y, box.min.z),
    new THREE.Vector3(box.min.x, box.max.y, box.max.z),
    new THREE.Vector3(box.max.x, box.min.y, box.min.z),
    new THREE.Vector3(box.max.x, box.min.y, box.max.z),
    new THREE.Vector3(box.max.x, box.max.y, box.min.z),
    new THREE.Vector3(box.max.x, box.max.y, box.max.z),
  ];
  let minX = Infinity, maxX = -Infinity, minY = Infinity, maxY = -Infinity;
  for (const c of corners) {
    c.applyMatrix4(camera.matrixWorldInverse);
    if (c.x < minX) minX = c.x;
    if (c.x > maxX) maxX = c.x;
    if (c.y < minY) minY = c.y;
    if (c.y > maxY) maxY = c.y;
  }
  _frameHalfW = (maxX - minX) / 2 * FRAME_MARGIN;
  _frameHalfH = (maxY - minY) / 2 * FRAME_MARGIN;
  _frameCx = (maxX + minX) / 2;
  _frameCy = (maxY + minY) / 2;
  refreshOrthoExtents();
}

window.__hsm_scene = {
  THREE, scene, camera, renderer,
  loadScene,
  poseIso,
  poseFor: (viewName) => {
    const d = VIEW_DIRECTIONS[viewName];
    if (!d) throw new Error(`unknown view: ${viewName}`);
    poseIso(d);
  },
  render: () => renderer.render(scene, camera),
  ready: false,
};

// Initial size — must run AFTER the canvas is attached to host.
resize();

// Auto-load if file param present (puppeteer drives this via the URL).
const params = new URLSearchParams(window.location.search);
const fileParam = params.get("file");
const viewParam = params.get("view") || "iso-front";

if (fileParam) {
  const glbUrl = fileParam.startsWith("/") ? fileParam : `/glb/${fileParam}`;
  loadScene(glbUrl).then(() => {
    window.__hsm_scene.poseFor(viewParam);
    window.__hsm_scene.render();
    window.__hsm_scene.ready = true;
  }).catch((e) => {
    console.error("scene load failed:", e);
    window.__hsm_scene.error = e.message || String(e);
  });
}
