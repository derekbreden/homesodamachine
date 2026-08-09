// STEP-format module. Owns the occt-import-js loader (no importmap
// support, so injected manually as a classic <script>), the STEP parser,
// the mesh builder that turns occt output into a Three.js Group, the
// network + parse + scene-mount loader, and the offscreen thumbnail
// renderer (with a per-file dataURL cache via state).

import * as THREE from "three";
import { state } from "./state.js";
import { scene, camera, resetCamera, addStudioLighting, fitCameraDepth, fitFog,
         BG_COLOR, TONE_EXPOSURE } from "./scene.js";
import { applyXray, syncEdgeResolution } from "./xray.js";
import { setActiveEdges } from "./edge-picker.js";
import { clearPickFind } from "./pick-find.js";
import { clearHighlight } from "./part-highlight.js";
import { clearComponentPicker, loadHiddenForFile, applyHiddenComponents } from "./component-picker.js";
import { onStepReloaded } from "./component-edit.js";
import { clearPortsExcept } from "./port-markers.js";
import { clearShapeBoxesExcept } from "./shape-boxes.js";

// --- occt-import-js loader (no importmap support, loaded manually) ---
let occtReady;
export const occtPromise = new Promise((resolve) => { occtReady = resolve; });
const occtScript = document.createElement("script");
occtScript.src = "https://cdn.jsdelivr.net/npm/occt-import-js@0.0.23/dist/occt-import-js.js";
occtScript.onload = () => {
  window.occtimportjs().then((occt) => occtReady(occt));
};
document.head.appendChild(occtScript);

// --- STEP parsing ---
async function parseStep(buffer) {
  const occt = await occtPromise;
  const result = occt.ReadStepFile(buffer, null);
  backfillMeshNames(result);
  return result;
}

// The same `{ meshes: [...] }` occt hands back, decoded from a tessellation the
// generator already had in hand rather than re-derived from the STEP text —
// reading a 24 MB assembly back through the wasm parser costs ~13 s, the
// tessellation that produced it ~1 s. Only the headless thumbnailer takes this
// path (tools/render/render-thumbnails.js); the live viewer still parses the
// STEP, because in the browser the STEP is all there is.
//
// Layout: u32 header length, that many bytes of JSON, then one blob every
// array indexes into by [byteOffset, length] — positions and normals f32,
// indices u32. See hardware/scripts/_mesh_payload.py, which writes it.
export function decodeMeshPayload(bytes) {
  const view = new DataView(bytes.buffer, bytes.byteOffset, bytes.byteLength);
  const headLen = view.getUint32(0, true);
  const head = JSON.parse(new TextDecoder().decode(bytes.subarray(4, 4 + headLen)));
  const blob = bytes.buffer.slice(bytes.byteOffset + 4 + headLen, bytes.byteOffset + bytes.byteLength);
  const meshes = head.meshes.map((m) => ({
    name: m.name,
    color: m.color || undefined,
    attributes: {
      position: { array: new Float32Array(blob, m.pos[0], m.pos[1]) },
      normal: { array: new Float32Array(blob, m.nrm[0], m.nrm[1]) },
    },
    index: { array: new Uint32Array(blob, m.idx[0], m.idx[1]) },
  }));
  return { meshes };
}

// occt-import-js copies a product's name onto its mesh only when the product is a
// single solid. A multi-solid component (our valve-manifold trays, the pump
// assemblies, the display) comes back with unnamed leaf meshes — the name lives
// on the owning hierarchy node instead. Walk the node tree and stamp each unnamed
// mesh with its component's name, so the edge picker's `solid:` blob line names
// the tray you clicked, not just the single-solid parts (reservoir, shell halves,
// funnel). Each mesh is listed by exactly one node, so the unnamed-only guard
// never clobbers a real per-mesh name.
function backfillMeshNames(result) {
  if (!result || !result.meshes || !result.root) return;
  const visit = (node) => {
    if (node.name && node.meshes) {
      for (const mi of node.meshes) {
        const mesh = result.meshes[mi];
        if (mesh && !mesh.name) mesh.name = node.name;
      }
    }
    (node.children || []).forEach(visit);
  };
  visit(result.root);
}

// Default gray for parts that carry no color (single-solid STEPs from
// export_step). Assemblies from export_assembly carry a per-solid color that
// occt-import-js surfaces as mesh.color ([r, g, b], 0..1).
const DEFAULT_FRONT = 0x8899aa;
const BACK_DARKEN = 0.75; // back faces a shade darker so thin parts read from behind

// A solid is one double-sided draw, and the darkening of its back faces happens
// inside that draw. xray.js clones these materials for its ghost variant and
// carries the injection across with them.
export function darkenBackFaces(shader) {
  shader.fragmentShader = shader.fragmentShader.replace(
    "#include <color_fragment>",
    `#include <color_fragment>
    if ( !gl_FrontFacing ) diffuseColor.rgb *= ${BACK_DARKEN.toFixed(3)};`,
  );
}

// Materials are shared across meshes (and across loads) by color, so an
// assembly with N same-colored solids makes one material, not N.
const _matCache = new Map();

function materialFor(color) {
  const key = color ? color.map((c) => Math.round(c * 255)).join(",") : "default";
  let mat = _matCache.get(key);
  if (!mat) {
    // Surfaces sit a depth-unit back, so the feature edges xray.js draws on
    // these same triangles resolve in front of them.
    mat = new THREE.MeshStandardMaterial({
      color: color ? new THREE.Color(color[0], color[1], color[2]) : new THREE.Color(DEFAULT_FRONT),
      metalness: 0.1, roughness: 0.6,
      side: THREE.DoubleSide,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1,
    });
    mat.onBeforeCompile = darkenBackFaces;
    mat.customProgramCacheKey = () => "hsm-back-darken";
    _matCache.set(key, mat);
  }
  return mat;
}

function buildMesh(result) {
  const group = new THREE.Group();

  result.meshes.forEach((mesh, occtIndex) => {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.position.array), 3));
    if (mesh.attributes.normal) {
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.normal.array), 3));
    }
    if (mesh.index) {
      geo.setIndex(new THREE.BufferAttribute(new Uint32Array(mesh.index.array), 1));
    }
    geo.computeBoundingBox();

    // One double-sided draw per solid, so a thin part still reads from behind.
    // occt-import-js hands us mesh.color per solid when the STEP carries one;
    // else gray. The occt mesh index rides along so the edge picker's face
    // raycast can map a hit triangle back to its BREP face.
    const solid = new THREE.Mesh(geo, materialFor(mesh.color));
    solid.userData.occtIndex = occtIndex;
    solid.userData.side = "front"; // the name the face raycast selects on
    // Carry the component name (backfilled from the STEP assembly node) onto the mesh so
    // the scorecard's clickable rows can find a solid by name (part-highlight.js).
    solid.name = mesh.name || "";
    group.add(solid);
  });

  return group;
}

export async function loadStepFile(file, { preserveCamera = false } = {}) {
  // Loading pill lives inside the current step wrapper (or none if the
  // headless tool drove loadStepFile directly). Tolerate either.
  const loadingEl = state.currentCadWrapper && state.currentCadWrapper.querySelector(".cad-loading");
  if (loadingEl) loadingEl.style.display = "block";

  try {
    // If we're refetching the same file that's already in the scene, send
    // If-None-Match so the server can answer 304 when bytes are unchanged
    // (avoids the visible re-render flash on a deploy that didn't touch
    // this STEP file).
    const headers = {};
    const prevEtag = state.stepEtags.get(file);
    if (state.mountedDetail?.type === "step" && state.mountedDetail.file === file && prevEtag) {
      headers["If-None-Match"] = prevEtag;
    }
    const resp = await fetch(`/steps/${file}`, { headers });
    if (resp.status === 304) return;
    if (!resp.ok) return;
    const etag = resp.headers.get("etag");
    if (etag) state.stepEtags.set(file, etag);

    const buf = new Uint8Array(await resp.arrayBuffer());
    const result = await parseStep(buf);

    if (state.currentGroup) {
      scene.remove(state.currentGroup);
      state.currentGroup.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
    }

    state.currentGroup = buildMesh(result);
    applyXray(state.currentGroup); // ghost + edges if x-ray mode is on
    setActiveEdges(result); // BREP edges for the edge picker (lazy-reconstructed)
    clearPickFind(); // stale find highlights reference the old geometry
    clearHighlight(); // and a stale scorecard part-highlight does too
    clearPortsExcept(file); // port markers for another model don't belong on this one
    clearShapeBoxesExcept(file); // nor its shape boxes
    clearComponentPicker();      // drop a stale component selection/hover overlay
    scene.add(state.currentGroup);
    state.mountedDetail = { type: "step", file };
    loadHiddenForFile(file);     // restore this file's locally-hidden components…
    applyHiddenComponents();     // …and take them out of the freshly-built view
    onStepReloaded();            // re-seat the component editor's selection on the fresh meshes
    if (!preserveCamera) resetCamera(state.currentGroup);
  } finally {
    if (loadingEl) loadingEl.style.display = "none";
  }
}

// --- Thumbnail rendering ---
const thumbRenderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
thumbRenderer.setSize(400, 400);
thumbRenderer.setPixelRatio(1);
thumbRenderer.setClearColor(BG_COLOR);
thumbRenderer.toneMapping = THREE.ACESFilmicToneMapping;
thumbRenderer.toneMappingExposure = TONE_EXPOSURE;
const thumbScene = new THREE.Scene();
const thumbCam = new THREE.PerspectiveCamera(45, 1, 1, 1000);
addStudioLighting(thumbScene);

// Frame a group front-iso in the offscreen scene, snap it, and tear it down.
// Shared with glb.js so every 3D thumbnail is composed the same way.
export function snapThumbnail(group) {
  thumbScene.add(group);

  const box = new THREE.Box3().setFromObject(group);
  const center = box.getCenter(new THREE.Vector3());
  const size = box.getSize(new THREE.Vector3());
  const maxDim = Math.max(size.x, size.y, size.z);
  const dist = maxDim * 2.5;
  // +Z-up CAD-standard front-iso — matches resetCamera in scene.js so
  // the thumbnail shows the same orientation as the detail view's
  // default. Camera at +X, -Y, +Z (front-right-above).
  const el = Math.atan(1 / Math.sqrt(2));
  const az = -Math.PI / 4;
  thumbCam.up.set(0, 0, 1);
  thumbCam.position.set(
    center.x + dist * Math.cos(el) * Math.cos(az),
    center.y + dist * Math.cos(el) * Math.sin(az),
    center.z + dist * Math.sin(el)
  );
  thumbCam.lookAt(center);
  fitCameraDepth(thumbCam, center, size.length() / 2);
  fitFog(thumbScene, dist, size.length() / 2);
  syncEdgeResolution(thumbRenderer);

  thumbRenderer.render(thumbScene, thumbCam);
  const dataURL = thumbRenderer.domElement.toDataURL();

  thumbScene.remove(group);
  group.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
  return dataURL;
}

// Build + shade + snap an occt-shaped result. Both thumbnail sources end here,
// so where the meshes came from can't change how the part looks.
export function renderMeshes(result) {
  const group = buildMesh(result);
  applyXray(group); // match the detail view's x-ray mode in the thumbnail
  return snapThumbnail(group);
}

export async function renderThumbnail(file) {
  if (state.thumbnailCache.has(file)) return state.thumbnailCache.get(file);

  try {
    const resp = await fetch(`/steps/${file}`);
    if (!resp.ok) return null;
    const buf = new Uint8Array(await resp.arrayBuffer());
    const dataURL = renderMeshes(await parseStep(buf));
    state.thumbnailCache.set(file, dataURL);
    return dataURL;
  } catch {
    return null;
  }
}

// thumbScene is also reused by dxf.js's renderDxfThumbnail — same offscreen
// renderer, just a different group producer. Re-exported so dxf.js doesn't
// need its own duplicate setup.
export { thumbRenderer, thumbScene, thumbCam };
