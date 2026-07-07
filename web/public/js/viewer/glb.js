// GLB-format module. Loads a glTF-binary assembly (the board's 3D model,
// board body + placed component meshes — see hardware/pcb/pcba/board-3d.py)
// into the shared Three.js scene via GLTFLoader, lays the green-soldermask
// face textures (board-texture.ts) over the board slab, and renders offscreen
// thumbnails (reusing step.js's thumbScene). Materials + colors are baked in
// the GLB; no occt parse.

import * as THREE from "three";
import { GLTFLoader } from "three/addons/loaders/GLTFLoader.js";
import { state } from "./state.js";
import { scene, resetCamera } from "./scene.js";
import { thumbRenderer, thumbScene, thumbCam } from "./step.js";

const loader = new GLTFLoader();
const texLoader = new THREE.TextureLoader();

function parseGlb(buffer) {
  return new Promise((resolve, reject) => loader.parse(buffer, "", resolve, reject));
}

// RWGltf writes the board Z-up (board plane in X-Y, faces at ±z) — the scene's
// convention already, so no reorientation. The group is just a handle scene.add
// and teardown operate on.
function toZupGroup(gltf) {
  const group = new THREE.Group();
  group.add(gltf.scene);
  return group;
}

// The board is the largest flat mesh (its 95×76 face dwarfs every part). Float a
// copper+silk plane just off each ±z face — top3d over the top, bottom3d under
// (mirrored, since it's drawn as seen down through the board).
function addBoardFaces(group, file) {
  group.updateMatrixWorld(true);
  const bb = new THREE.Box3();
  let best = 0, foot = null;
  group.traverse((o) => {
    if (!o.isMesh) return;
    bb.setFromObject(o);
    const dx = bb.max.x - bb.min.x, dy = bb.max.y - bb.min.y, dz = bb.max.z - bb.min.z;
    if (dz < Math.min(dx, dy) * 0.2 && dx * dy > best) {
      best = dx * dy;
      foot = { w: dx, h: dy, cx: (bb.min.x + bb.max.x) / 2, cy: (bb.min.y + bb.max.y) / 2, z: (bb.min.z + bb.max.z) / 2 };
    }
  });
  if (!foot) return;

  const half = Math.max(Math.abs(foot.z), 1e-4); // board is centred on z=0; faces at ±half
  const lift = half * 0.25;
  const base = `/thumbs/${file.replace(/\.glb$/, "")}`;
  const face = (url, z, mirror) => {
    const mesh = new THREE.Mesh(
      new THREE.PlaneGeometry(foot.w, foot.h),
      new THREE.MeshStandardMaterial({ roughness: 0.85, metalness: 0.0 }),
    );
    mesh.position.set(foot.cx, foot.cy, z);
    if (mirror) mesh.rotation.y = Math.PI; // turn the plane to face -Z (down)
    texLoader.load(
      url,
      (tex) => {
        tex.colorSpace = THREE.SRGBColorSpace;
        // Facing -Z flips the texture's U; undo it so the bottom maps board→(x,y)
        // like the top and so its (already glyph-mirrored) silk reads forward from below.
        if (mirror) { tex.wrapS = THREE.RepeatWrapping; tex.repeat.x = -1; tex.offset.x = 1; }
        mesh.material.map = tex;
        mesh.material.needsUpdate = true;
      },
      undefined,
      () => group.remove(mesh), // no texture rendered yet — drop the blank plane
    );
    group.add(mesh);
  };
  face(`${base}.top3d.png`, half + lift, false);
  face(`${base}.bottom3d.png`, -half - lift, true);
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
    addBoardFaces(state.currentGroup, file);
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
