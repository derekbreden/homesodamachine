import { state } from "./state.js";
import * as xray from "./xray.js";

const ownedMaterials = new WeakSet();
const disposed = new WeakSet();

// STEP materials belong to its shared palette. GLB and procedural DXF groups
// own their materials and textures, including a texture that finishes late.
export function ownCadGroup(group) {
  ownedMaterials.add(group);
  return group;
}

export function cadGroupDisposed(group) { return disposed.has(group); }

export function disposeCadGroup(group) {
  if (!group || disposed.has(group)) return;
  disposed.add(group);
  xray.disposeXray?.(group);
  const own = ownedMaterials.has(group) || (group === state.currentGroup
    && (state.mountedDetail?.type === "glb" || state.mountedDetail?.type === "dxf"));
  const geometries = new Set(), materials = new Set(), textures = new Set(), images = new Set();
  group.traverse(object => {
    if (object.geometry) geometries.add(object.geometry);
    if ((own || object.userData.ownsMaterial) && object.material) {
      for (const material of Array.isArray(object.material) ? object.material : [object.material]) {
        if (material) materials.add(material);
      }
    }
  });
  for (const geometry of geometries) geometry.dispose();
  for (const material of materials) {
    for (const value of Object.values(material)) if (value?.isTexture) textures.add(value);
    material.dispose();
  }
  for (const texture of textures) {
    if (texture.image) images.add(texture.image);
    texture.dispose();
  }
  for (const image of images) image.close?.();
  group.clear();
}

// One active CAD transfer, shared by hot loader versions and all three formats.
// stepLoadSeq remains the older tabs' sequence field.
export function beginCadLoad() {
  state.cadLoadAbort?.abort();
  const controller = new AbortController();
  state.cadLoadAbort = controller;
  const seq = ++state.stepLoadSeq;
  const wrapper = state.currentCadWrapper;
  return {
    signal: controller.signal,
    current: () => !controller.signal.aborted && seq === state.stepLoadSeq
      && (!wrapper || wrapper === state.currentCadWrapper),
    finish() {
      if (state.cadLoadAbort === controller) state.cadLoadAbort = null;
    },
  };
}

export function cancelCadLoad() {
  state.cadLoadAbort?.abort();
  state.cadLoadAbort = null;
  state.stepLoadSeq++;
}
