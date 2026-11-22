// Hidden-part tiles draw the placed CAD geometry in a worker while the viewer handles input.
import * as THREE from "three";
import { fitCameraDepth } from "./navigation.js";
import { KEY_DIR } from "./scene.js";

const direction = new THREE.Vector3(1, -1, 1).normalize();
export function frameThumbnail(bounds, camera, shelf) {
  const center = bounds.getCenter(new THREE.Vector3());
  const size = bounds.getSize(new THREE.Vector3());
  const distance = Math.max(size.x, size.y, size.z) * (shelf ? 2.25 : 2.5);
  const radius = size.length() / 2;
  camera.up.set(0, 0, 1);
  camera.position.copy(center).addScaledVector(direction, distance);
  camera.lookAt(center);
  fitCameraDepth(camera, center, radius);
  camera.updateMatrixWorld();
  return { distance, radius };
}

let worker;
function send(message, transfer = []) {
  worker ??= new Worker(new URL("./hidden-thumbnail-worker.js", import.meta.url));
  return new Promise((resolve, reject) => {
    worker.onmessage = event => resolve(event.data);
    worker.onerror = event => {
      worker.terminate();
      worker = null;
      reject(new Error(event.message));
    };
    worker.postMessage(message, transfer);
  });
}

// Each reply lets another input run before the next solid's arrays are copied for transfer.
export async function captureHiddenThumbnail(meshes, current) {
  const bounds = new THREE.Box3();
  for (const mesh of meshes) bounds.expandByObject(mesh);
  if (bounds.isEmpty()) return null;
  const camera = new THREE.PerspectiveCamera(45, 1, 1, 1000);
  frameThumbnail(bounds, camera, true);
  const cameraMatrix = new THREE.Matrix4().multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse);
  const side = 128;
  await send({ begin: side, light: KEY_DIR.clone().normalize().toArray() });
  for (const mesh of meshes) {
    if (!current()) return null;
    const geometry = mesh.geometry;
    const positions = geometry.getAttribute("position").array.slice();
    const indices = geometry.index?.array.slice();
    const transform = new THREE.Matrix4().multiplyMatrices(cameraMatrix, mesh.matrixWorld);
    const normal = new THREE.Matrix3().getNormalMatrix(mesh.matrixWorld);
    const material = mesh.userData.baseMaterial || mesh.material;
    const transfer = [positions.buffer];
    if (indices) transfer.push(indices.buffer);
    await send({ positions, indices, transform: transform.elements, normal: normal.elements, mirrored: mesh.matrixWorld.determinant() < 0,
      color: material.color.getHex(THREE.SRGBColorSpace), metalness: material.metalness || 0 }, transfer);
  }
  if (!current()) return null;
  const pixels = await send({ finish: true });
  return new ImageData(pixels, side, side);
}
