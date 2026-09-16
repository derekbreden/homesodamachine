// WHERE THE CAMERA HAS TO STAND TO SEE A SET OF BODIES. Every pose the tour
// takes is computed here, from the geometry that is actually loaded, so a step
// keeps framing its subject after the subject moves and never carries a
// coordinate of its own.
//
// A step says WHICH BODIES and FROM WHICH DIRECTION; this says how far back.
// The distance is the one that puts the subject's bounding sphere inside the
// narrower of the camera's two half-angles, so a wide viewport and a phone
// held upright both get the whole subject rather than a crop.

import * as THREE from "three";

// A body of a few millimetres would otherwise put the camera inside itself.
const MIN_RADIUS_MM = 9;

const _box = new THREE.Box3();
const _sphere = new THREE.Sphere();

/** World-space box of the named bodies in `group`. Empty when none are found. */
export function boxOfParts(group, names) {
  const out = new THREE.Box3();
  out.makeEmpty();
  for (const box of boxesOfParts(group, names)) out.union(box);
  return out;
}

/** Individual bounds avoid fitting empty corners between separated bodies. */
export function boxesOfParts(group, names) {
  const boxes = [];
  if (!group || !names || !names.length) return boxes;
  const want = names instanceof Set ? names : new Set(names);
  group.updateMatrixWorld(true);
  for (const child of group.children) {
    // The x-ray feature edges answer to isMesh and carry their solid's name in
    // userData rather than in `name` — a box taken off those would be the same
    // box twice. Bodies only.
    if (!child.isMesh || child.userData.isXrayEdge) continue;
    if (!child.name || !want.has(child.name)) continue;
    boxes.push(new THREE.Box3().setFromObject(child));
  }
  return boxes;
}

/** The union of several boxes, skipping the empty ones. */
export function unionBoxes(...boxes) {
  const out = new THREE.Box3();
  out.makeEmpty();
  for (const b of boxes) if (b && !b.isEmpty()) out.union(b);
  return out;
}

/**
 * The pose that frames `box` seen from `dir`, with `pad` times the room the
 * subject strictly needs.
 *
 * `dir` points FROM the subject TOWARD the camera, in the machine's own axes.
 * `up` is +Z unless the shot is looking very nearly straight down or up, where
 * +Z is the view direction and cannot also be up.
 */
export function poseFor(box, dir, pad, camera) {
  const target = box.isEmpty() ? new THREE.Vector3() : box.getCenter(new THREE.Vector3());
  box.getBoundingSphere(_sphere);
  const radius = Math.max(_sphere.radius, MIN_RADIUS_MM);

  const halfV = THREE.MathUtils.degToRad(camera.fov) / 2;
  const aspect = camera.aspect > 0 ? camera.aspect : 1;
  const halfH = Math.atan(Math.tan(halfV) * aspect);
  const half = Math.max(Math.min(halfV, halfH), 0.05);
  const distance = (radius * (pad || 1.5)) / Math.sin(half);

  const d = new THREE.Vector3().fromArray(dir).normalize();
  if (!isFinite(d.lengthSq()) || d.lengthSq() < 1e-6) d.set(1, -1, 0.6).normalize();
  const up = Math.abs(d.z) > 0.985 ? new THREE.Vector3(0, -1, 0) : new THREE.Vector3(0, 0, 1);

  return {
    target,
    position: target.clone().addScaledVector(d, distance),
    up,
    radius,
  };
}

/** Fit every context corner while favouring the subject in the composition. */
export function contextPose(subject, context, dir, pad, camera, weight = 0.75, fitBoxes = []) {
  if (!context || context.isEmpty()) return poseFor(subject, dir, pad, camera);
  const bounds = unionBoxes(subject, context);
  const target = subject.getCenter(new THREE.Vector3())
    .lerp(context.getCenter(new THREE.Vector3()), weight);
  const direction = new THREE.Vector3(...dir).normalize();
  const up = Math.abs(direction.z) > 0.985 ? new THREE.Vector3(0, -1, 0) : new THREE.Vector3(0, 0, 1);
  const right = new THREE.Vector3().crossVectors(up, direction).normalize();
  const vertical = new THREE.Vector3().crossVectors(direction, right).normalize();
  const tanV = Math.tan(THREE.MathUtils.degToRad(camera.fov) / 2);
  const tanH = tanV * camera.aspect;
  let distance = 30;
  for (const box of fitBoxes.length ? fitBoxes : [bounds]) {
    for (const x of [box.min.x, box.max.x]) {
      for (const y of [box.min.y, box.max.y]) {
        for (const z of [box.min.z, box.max.z]) {
          const v = new THREE.Vector3(x, y, z).sub(target);
          distance = Math.max(distance, v.dot(direction) + pad * Math.max(
            Math.abs(v.dot(right)) / tanH, Math.abs(v.dot(vertical)) / tanV));
        }
      }
    }
  }
  return { target, position: target.clone().addScaledVector(direction, distance), up };
}

/** The whole model's box, for the establishing frames and the depth fit. */
export function boxOfGroup(group) {
  _box.makeEmpty();
  if (group) _box.setFromObject(group);
  return _box.clone();
}
