// STEP-format module. Owns the occt-import-js loader (no importmap
// support, so injected manually as a classic <script>), the STEP parser,
// the mesh builder that turns occt output into a Three.js Group, the
// network + parse + scene-mount loader, and the offscreen thumbnail
// renderer (with a per-file dataURL cache via state).

import * as THREE from "three";
import { state } from "./state.js";
import { scene, camera, resetCamera } from "./scene.js";

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
  return occt.ReadStepFile(buffer, null);
}

function buildMesh(result) {
  const group = new THREE.Group();
  const mat = new THREE.MeshStandardMaterial({ color: 0x8899aa, metalness: 0.1, roughness: 0.6 });
  const matBack = new THREE.MeshStandardMaterial({ color: 0x667788, metalness: 0.1, roughness: 0.6, side: THREE.BackSide });

  for (const mesh of result.meshes) {
    const geo = new THREE.BufferGeometry();
    geo.setAttribute("position", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.position.array), 3));
    if (mesh.attributes.normal) {
      geo.setAttribute("normal", new THREE.Float32BufferAttribute(new Float32Array(mesh.attributes.normal.array), 3));
    }
    if (mesh.index) {
      geo.setIndex(new THREE.BufferAttribute(new Uint32Array(mesh.index.array), 1));
    }
    geo.computeBoundingBox();

    // Front + back face so thin parts are visible from behind
    group.add(new THREE.Mesh(geo, mat));
    group.add(new THREE.Mesh(geo, matBack));
  }

  // Edge lines for CAD look
  for (const edge of (result.brpieces || [])) {
    // Not all versions expose edges — skip if absent
  }

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
    scene.add(state.currentGroup);
    state.mountedDetail = { type: "step", file };
    if (!preserveCamera) resetCamera(state.currentGroup);
  } finally {
    if (loadingEl) loadingEl.style.display = "none";
  }
}

// --- Thumbnail rendering ---
const thumbRenderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true });
thumbRenderer.setSize(400, 400);
thumbRenderer.setPixelRatio(1);
thumbRenderer.setClearColor(0x1a1a2e);
const thumbScene = new THREE.Scene();
const thumbCam = new THREE.PerspectiveCamera(45, 1, 0.01, 10000);
thumbScene.add(new THREE.AmbientLight(0xffffff, 0.5));
const tl = new THREE.DirectionalLight(0xffffff, 0.8);
tl.position.set(1, 2, 1.5);
thumbScene.add(tl);
const tl2 = new THREE.DirectionalLight(0xffffff, 0.3);
tl2.position.set(-1, -0.5, -1);
thumbScene.add(tl2);

export async function renderThumbnail(file) {
  if (state.thumbnailCache.has(file)) return state.thumbnailCache.get(file);

  try {
    const resp = await fetch(`/steps/${file}`);
    if (!resp.ok) return null;
    const buf = new Uint8Array(await resp.arrayBuffer());
    const result = await parseStep(buf);
    const group = buildMesh(result);
    thumbScene.add(group);

    const box = new THREE.Box3().setFromObject(group);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const maxDim = Math.max(size.x, size.y, size.z);
    const dist = maxDim * 2.5;
    const el = Math.atan(1 / Math.sqrt(2));
    const az = Math.PI / 4;
    thumbCam.position.set(
      center.x + dist * Math.cos(el) * Math.cos(az),
      center.y + dist * Math.sin(el),
      center.z + dist * Math.cos(el) * Math.sin(az)
    );
    thumbCam.lookAt(center);

    thumbRenderer.render(thumbScene, thumbCam);
    const dataURL = thumbRenderer.domElement.toDataURL();

    thumbScene.remove(group);
    group.traverse((c) => { if (c.geometry) c.geometry.dispose(); });

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
