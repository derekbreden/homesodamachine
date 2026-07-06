// GLB-format module. Loads a glTF-binary assembly (the board's 3D model,
// board body + placed component meshes — see hardware/pcb/pcba/board-3d.py)
// into the shared Three.js scene via GLTFLoader, plus an offscreen thumbnail
// renderer (reusing step.js's thumbScene). Materials + colors come baked in
// the GLB; no occt parse.

import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { state } from "./state.js";
import { scene, resetCamera } from "./scene.js";
import { thumbRenderer, thumbScene, thumbCam } from "./step.js";

const loader = new GLTFLoader();

function parseGlb(buffer) {
  return new Promise((resolve, reject) => loader.parse(buffer, "", resolve, reject));
}

// glTF is Y-up; the scene (resetCamera, the thumbnail camera) is +Z-up like the
// STEP parts. Wrap the loaded content in a group tipped +90° about X so the
// board's normal points up in this scene the way a Z-up STEP would.
function toZupGroup(gltf) {
  const group = new THREE.Group();
  group.add(gltf.scene);
  group.rotation.x = Math.PI / 2;
  return group;
}

export async function loadGlbFile(file, { preserveCamera = false } = {}) {
  const loadingEl = state.currentCadWrapper && state.currentCadWrapper.querySelector(".cad-loading");
  if (loadingEl) loadingEl.style.display = "block";
  try {
    const headers = {};
    const prevEtag = state.glbEtags.get(file);
    if (state.mountedDetail?.type === "glb" && state.mountedDetail.file === file && prevEtag) {
      headers["If-None-Match"] = prevEtag;
    }
    const resp = await fetch(`/models/${file}`, { headers });
    if (resp.status === 304) return;
    if (!resp.ok) return;
    const etag = resp.headers.get("etag");
    if (etag) state.glbEtags.set(file, etag);

    const gltf = await parseGlb(await resp.arrayBuffer());

    if (state.currentGroup) {
      scene.remove(state.currentGroup);
      state.currentGroup.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
    }
    state.currentGroup = toZupGroup(gltf);
    scene.add(state.currentGroup);
    state.mountedDetail = { type: "glb", file };
    if (!preserveCamera) resetCamera(state.currentGroup);
  } finally {
    if (loadingEl) loadingEl.style.display = "none";
  }
}

export async function renderGlbThumbnail(file) {
  if (state.glbThumbCache.has(file)) return state.glbThumbCache.get(file);
  try {
    const resp = await fetch(`/models/${file}`);
    if (!resp.ok) return null;
    const gltf = await parseGlb(await resp.arrayBuffer());
    const group = toZupGroup(gltf);
    thumbScene.add(group);

    const box = new THREE.Box3().setFromObject(group);
    const center = box.getCenter(new THREE.Vector3());
    const size = box.getSize(new THREE.Vector3());
    const dist = Math.max(size.x, size.y, size.z) * 2.5;
    const el = Math.atan(1 / Math.sqrt(2));
    const az = -Math.PI / 4;
    thumbCam.up.set(0, 0, 1);
    thumbCam.position.set(
      center.x + dist * Math.cos(el) * Math.cos(az),
      center.y + dist * Math.cos(el) * Math.sin(az),
      center.z + dist * Math.sin(el),
    );
    thumbCam.lookAt(center);
    thumbRenderer.render(thumbScene, thumbCam);
    const dataURL = thumbRenderer.domElement.toDataURL();

    thumbScene.remove(group);
    group.traverse((c) => { if (c.geometry) c.geometry.dispose(); });
    state.glbThumbCache.set(file, dataURL);
    return dataURL;
  } catch {
    return null;
  }
}
