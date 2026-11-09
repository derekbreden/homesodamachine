// Feature navigation highlights authored ranges of the model already mounted on screen.
import * as THREE from "three";
import { state } from "./state.js";
import { featureKey, instanceBody, splitFeatureKey, featureIndices } from "/contracts/features.js";

export function sceneFeatures(body = null) {
  const records = new Map();
  for (const mesh of state.currentGroup?.children || []) {
    if (mesh.userData?.side !== "front" || (body && mesh.name !== body)) continue;
    for (const feature of mesh.userData.features || []) {
      const key = featureKey(instanceBody(mesh.name), feature.id);
      const previous = records.get(key);
      if (previous) previous.meshes.push(mesh);
      else records.set(key, { ...feature, key, body: instanceBody(mesh.name), meshes: [mesh] });
    }
  }
  return [...records.values()];
}

export const sceneFeature = key => {
  const parsed = splitFeatureKey(key);
  return parsed ? sceneFeatures(parsed.body).find(f => f.id === parsed.id) || null : null;
};

export function featureGeometry(mesh, feature) {
  mesh.updateWorldMatrix(true, false);
  const indices = featureIndices(mesh.geometry.index.array, feature);
  const source = mesh.geometry.getAttribute("position");
  const positions = new Float32Array(indices.length * 3);
  const point = new THREE.Vector3();
  for (let i = 0; i < indices.length; i++) {
    point.fromBufferAttribute(source, indices[i]).applyMatrix4(mesh.matrixWorld).toArray(positions, i * 3);
  }
  return new THREE.BufferGeometry().setAttribute("position", new THREE.BufferAttribute(positions, 3));
}

export function featureUrl(key, file = state.mountedDetail?.file) {
  return `${location.origin}/3d#step:${encodeURIComponent(file)}?find=${encodeURIComponent(`feature: ${key}`)}`;
}
