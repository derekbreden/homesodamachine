// /scene viewer — line-art renderer for technical drawings.
//
// Loads a glTF (built from CadQuery) and renders it as line art with
// proper z-buffer occlusion. Parts whose assembly color is white (or
// near-grayscale) render as white surfaces (invisible on the white
// page background but writing depth) with black feature edges on top
// AND black silhouette outlines from a Sobel-on-normals post-process.
// Parts whose color is saturated (e.g. the red CO2-port ring) render
// their surfaces in that color.
//
// Two complementary edge sources:
//   - Line2 overlay from EdgesGeometry — captures CREASE edges (where
//     adjacent face normals jump by > EDGE_ANGLE_THRESHOLD_DEG). Fast,
//     crisp, line-width controlled exactly.
//   - Sobel on a per-frame normal pass — captures SILHOUETTES (where a
//     smoothly tessellated surface curves away from the camera, e.g.
//     a cylinder side). EdgesGeometry can't find these because adjacent
//     tessellation triangles on a smooth surface have nearly-equal
//     normals; the silhouette only exists in screen space.
//
// Camera: orthographic, posed at iso-front (+x +y +z in three.js, which
// is the right-front-top corner after OCCT's Z-up → Y-up glTF rotation
// brings our +Z height to three.js +Y) or iso-back (+x +y -z).
//
// The headless render tool (tools/render/render-scene.js) drives this
// via window.__hsm_scene.

import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { Line2 } from "three/addons/lines/Line2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { ShaderPass } from "three/addons/postprocessing/ShaderPass.js";

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

// Line width in CSS pixels for the Line2 feature-edge overlay. Matches
// the SVG line-art's stroke-width of 1.5 closely enough. Line2 (vs.
// LineSegments) is used because GL_LINES only ever draws 1-pixel lines
// on most platforms regardless of linewidth; Line2 renders lines as
// camera-facing triangle strips so width is honoured.
const LINE_WIDTH_PX = 1.5;

// EdgesGeometry threshold (degrees). Edges are drawn where adjacent
// face normals differ by at least this angle. 15° captures sharp
// feature edges while not over-decorating smoothly-tessellated cylinders
// with sliver edges between adjacent triangles. Silhouettes that
// EdgesGeometry misses are filled in by the Sobel post-process below.
const EDGE_ANGLE_THRESHOLD_DEG = 15;

// ---------------------------------------------------------------------------
// Silhouette pass — Sobel on normals
// ---------------------------------------------------------------------------
// The normal pass renders the scene with overrideMaterial = MeshNormalMaterial
// to a separate render target. The Sobel composite shader then samples that
// normal buffer at the current pixel + its 4 neighbours; a large gradient
// in the (encoded) normal between adjacent pixels means either:
//   - A silhouette (object normal vs background's clear-color vec3) — the
//     thing we're trying to capture.
//   - A crease (object normal A vs object normal B) — Line2 already covers
//     these but Sobel reinforces them, which is fine.
// Output: black where gradient > threshold, otherwise the main scene color.

const normalsRT = new THREE.WebGLRenderTarget(1, 1, {
  format: THREE.RGBAFormat,
  type: THREE.UnsignedByteType,
});

const normalsMaterial = new THREE.MeshNormalMaterial({ side: THREE.DoubleSide });

// Sobel gradient threshold (sum of |nR-nL| + |nU-nD| of encoded normal
// vectors). 0.15 picks up silhouettes of curved surfaces (where the
// normal smoothly rotates away from the camera so the gradient grows
// gradually toward the edge) without flooding the image with edges on
// every smoothly-tessellated surface interior.
const SOBEL_THRESHOLD = 0.3;

const sobelShader = {
  uniforms: {
    tDiffuse: { value: null },
    tNormals: { value: normalsRT.texture },
    resolution: { value: new THREE.Vector2(1, 1) },
    threshold: { value: SOBEL_THRESHOLD },
  },
  vertexShader: `
    varying vec2 vUv;
    void main() {
      vUv = uv;
      gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
  `,
  fragmentShader: `
    precision highp float;
    uniform sampler2D tDiffuse;
    uniform sampler2D tNormals;
    uniform vec2 resolution;
    uniform float threshold;
    varying vec2 vUv;

    void main() {
      vec2 px = 1.0 / resolution;
      vec3 nL = texture2D(tNormals, vUv - vec2(px.x, 0.0)).rgb;
      vec3 nR = texture2D(tNormals, vUv + vec2(px.x, 0.0)).rgb;
      vec3 nU = texture2D(tNormals, vUv + vec2(0.0, px.y)).rgb;
      vec3 nD = texture2D(tNormals, vUv - vec2(0.0, px.y)).rgb;
      float gx = length(nR - nL);
      float gy = length(nU - nD);
      float g = gx + gy;

      vec3 color = texture2D(tDiffuse, vUv).rgb;
      // Hard step at threshold — smoothstep produces a fuzzy edge halo
      // at this resolution.
      float edge = step(threshold, g);
      gl_FragColor = vec4(mix(color, vec3(0.0), edge), 1.0);
    }
  `,
};

const composer = new EffectComposer(renderer);
composer.addPass(new RenderPass(scene, camera));
const sobelPass = new ShaderPass(sobelShader);
composer.addPass(sobelPass);

function resize() {
  const w = host.clientWidth;
  const h = host.clientHeight;
  const dpr = renderer.getPixelRatio();
  renderer.setSize(w, h, false);
  composer.setSize(w, h);
  normalsRT.setSize(Math.max(1, Math.floor(w * dpr)), Math.max(1, Math.floor(h * dpr)));
  // ShaderPass clones uniforms in its constructor — write to the pass's
  // *live* uniforms object, not the original shader spec.
  sobelPass.uniforms.resolution.value.set(w * dpr, h * dpr);
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
  // r ≈ g ≈ b ⇒ default white/gray → render as line art (white-on-white
  // fill, black feature edges + Sobel silhouettes). Saturated colors →
  // render as colored fill.
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
      // White surface on a white background — paints white pixels that
      // are invisible against the page bg but DO write depth (and DO
      // write color, matching the bg). All edges in the scene are drawn
      // AFTER all surfaces (via renderOrder=1 on the Line2 below), and
      // depthFunc defaults to LessEqualDepth, so an edge at the same
      // depth as the surface it outlines wins by being drawn later.
      node.material = new THREE.MeshBasicMaterial({ color: 0xffffff });

      // Feature-edge overlay: Line2 for honored line width.
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
      lines.renderOrder = 1;
      node.add(lines);
    } else {
      // Colored part — flat color, no shading, no edge overlay. Sobel
      // still draws the part's silhouette in black on top via the
      // normal-buffer post-process below.
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
  // space and using their actual screen-aligned extents.
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

function render() {
  // 1) Render normals pass to off-screen target. The Line2 overlays are
  //    excluded so they don't contribute spurious crease-like gradients
  //    in the normal buffer — Sobel runs over the surface normals only.
  const restoreVisibility = [];
  scene.traverse((n) => {
    if (n.userData?.lineArtOverlay && n.visible) {
      restoreVisibility.push(n);
      n.visible = false;
    }
  });
  scene.overrideMaterial = normalsMaterial;
  renderer.setRenderTarget(normalsRT);
  renderer.setClearColor(0xffffff, 1);
  renderer.clear(true, true, true);
  renderer.render(scene, camera);
  scene.overrideMaterial = null;
  for (const n of restoreVisibility) n.visible = true;

  // 2) Main composite: RenderPass draws the scene normally, then the
  //    Sobel ShaderPass paints black at high-gradient pixels of the
  //    normals buffer (silhouettes + creases).
  //
  // ShaderPass clones the input shader.uniforms object via
  // UniformsUtils.clone in its constructor, so we have to set tNormals
  // on the *pass's* uniforms (sobelPass.uniforms), not on the original
  // shader spec. The texture reference is the same object across frames,
  // so this is a one-time wire-up, but doing it here avoids a separate
  // initialization site that's easy to drift from the pass creation.
  sobelPass.uniforms.tNormals.value = normalsRT.texture;
  renderer.setRenderTarget(null);
  renderer.setClearColor(0xffffff, 1);
  composer.render();
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
  render,
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
