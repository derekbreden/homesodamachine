import * as THREE from "three";
import { ENCLOSURE_FASTENERS, ease, fastenerMotion, revealMotion } from "./reveal-plan.js";
export { REVEAL_STATES } from "./reveal-plan.js";

function fasteners(group) {
  if (!group.children.some((c) => c.name === "enclosure-front-top")) return null;
  const root = new THREE.Group();
  root.name = "tour-fasteners";
  root.userData.tourOnly = true;
  const spec = ENCLOSURE_FASTENERS;
  const steel = new THREE.MeshStandardMaterial({ color: 0xd9dce2, metalness: 0.75, roughness: 0.28 });
  const dark = new THREE.MeshStandardMaterial({ color: 0x242b35, metalness: 0.4, roughness: 0.5 });
  const markerMaterial = new THREE.MeshBasicMaterial({
    color: 0x5de3ce, transparent: true, opacity: 0, depthWrite: false,
  });
  const axisMaterial = new THREE.LineDashedMaterial({
    color: 0x87cec7, transparent: true, opacity: 0,
    dashSize: 4, gapSize: 3, depthWrite: false,
  });
  const head = new THREE.CylinderGeometry(spec.headDiameter / 2, spec.headDiameter / 2, spec.headHeight, 24);
  const shank = new THREE.CylinderGeometry(spec.shankDiameter / 2, spec.shankDiameter / 2, spec.shankLength, 12);
  const socket = new THREE.CircleGeometry(1.3, 6);
  const shoulder = new THREE.TorusGeometry(spec.shankDiameter / 2, 0.12, 4, 12);
  const markerGeometry = new THREE.TorusGeometry(7.5, 0.45, 6, 40);
  const geometries = [head, shank, socket, shoulder, markerGeometry];
  const screws = [];
  const markers = [];
  for (const sign of [-1, 1]) {
    for (const z of spec.levels) {
      const screw = new THREE.Group();
      screw.name = `tour-seam-screw-${sign < 0 ? "left" : "right"}-${z}`;
      screw.userData.tourOnly = true;
      // The screw's +Z points out through the side wall; Z=0 is its bearing face.
      const h = new THREE.Mesh(head, steel);
      h.rotation.x = Math.PI / 2;
      h.position.z = spec.headHeight / 2;
      const s = new THREE.Mesh(shank, steel);
      s.rotation.x = Math.PI / 2;
      s.position.z = -spec.shankLength / 2;
      const hex = new THREE.Mesh(socket, dark);
      hex.position.z = spec.headHeight + 0.015;
      screw.add(h, s, hex);
      const marker = new THREE.Mesh(markerGeometry, markerMaterial);
      marker.position.z = spec.headHeight + 0.2;
      marker.visible = false;
      screw.add(marker);
      markers.push(marker);
      for (let at = -0.5; at > -spec.shankLength; at -= 0.5) {
        const thread = new THREE.Mesh(shoulder, dark);
        thread.position.z = at;
        screw.add(thread);
      }
      screw.quaternion.setFromUnitVectors(new THREE.Vector3(0, 0, 1), new THREE.Vector3(sign, 0, 0));
      screw.position.set(sign * (spec.exteriorX - spec.headSeatDepth), spec.axisY, z);
      root.add(screw);
      const axisGeometry = new THREE.BufferGeometry().setFromPoints([
        screw.position.clone().add(new THREE.Vector3(sign * 5, 0, 0)),
        screw.position.clone().add(new THREE.Vector3(sign * 78, 0, 0)),
      ]);
      geometries.push(axisGeometry);
      const axis = new THREE.Line(axisGeometry, axisMaterial);
      axis.computeLineDistances();
      axis.visible = false;
      root.add(axis);
      markers.push(axis);
      screws.push({ object: screw, sign, position: screw.position.clone(), quaternion: screw.quaternion.clone() });
    }
  }
  group.add(root);
  return { root, screws, markers, markerMaterial, axisMaterial, geometries,
    materials: [steel, dark, markerMaterial, axisMaterial] };
}

/** Deterministic tour-only transforms; geometry and shared materials stay owned by the viewer. */
export function createReveal(group, modelFile = "") {
  const bodies = new Map();
  const edgeBases = new Map();
  const translation = new THREE.Vector3();
  const screwSet = group ? fasteners(group) : null;
  if (group) {
    for (const object of group.children) {
      if (!object.isMesh || object.userData.isXrayEdge) continue;
      bodies.set(object, {
        position: object.position.clone(), quaternion: object.quaternion.clone(),
        scale: object.scale.clone(),
      });
    }
  }
  let current = { enclosure: 0, coldCore: 0, carbonator: 0, park: 0 };
  let disposed = false;

  function apply(next = {}) {
    if (!group || disposed) return;
    current = { enclosure: next.enclosure || 0, coldCore: next.coldCore || 0,
      carbonator: next.carbonator || 0, park: next.park || 0 };
    for (const [object, base] of bodies) {
      const delta = revealMotion(object.name, current);
      object.position.copy(base.position).add(translation.set(...delta));
      object.quaternion.copy(base.quaternion);
      object.scale.copy(base.scale);
      object.updateMatrix();
    }
    // X-ray toggles replace their edge objects. Each fresh edge inherits the solid's pose.
    const byName = new Map();
    for (const [object, base] of bodies) if (!byName.has(object.name)) byName.set(object.name, { object, base });
    for (const edge of group.children) {
      if (!edge.userData.isXrayEdge) continue;
      const source = byName.get(edge.userData.xrayComponent);
      if (!source) continue;
      if (!edgeBases.has(edge)) {
        edgeBases.set(edge, {
          position: source.base.position.clone(), quaternion: source.base.quaternion.clone(),
          scale: source.base.scale.clone(),
        });
      }
      edge.position.copy(source.object.position);
      edge.quaternion.copy(source.object.quaternion);
      edge.scale.copy(source.object.scale);
      edge.updateMatrix();
    }
    if (screwSet) {
      const emphasis = ease((current.enclosure - 0.005) / 0.025)
        * (1 - ease((current.enclosure - 0.36) / 0.02));
      screwSet.markerMaterial.opacity = 0.86 * emphasis;
      screwSet.axisMaterial.opacity = 0.40 * emphasis;
      for (const marker of screwSet.markers) marker.visible = emphasis > 0.001;
      for (const [index, screw] of screwSet.screws.entries()) {
        const motion = fastenerMotion(current.enclosure, index);
        screw.object.position.copy(screw.position);
        screw.object.position.x += screw.sign * (motion.distance + 800 * ease(current.park));
        screw.object.quaternion.copy(screw.quaternion);
        screw.object.rotateZ(motion.turns * Math.PI * 2);
      }
    }
    group.updateMatrixWorld(true);
  }

  function restore() {
    if (!group || disposed) return;
    apply({});
    for (const [object, base] of [...bodies, ...edgeBases]) {
      object.position.copy(base.position);
      object.quaternion.copy(base.quaternion);
      object.scale.copy(base.scale);
      object.updateMatrix();
    }
    group.updateMatrixWorld(true);
  }

  function dispose() {
    if (disposed) return;
    restore();
    if (screwSet) {
      group.remove(screwSet.root);
      for (const geometry of screwSet.geometries) geometry.dispose();
      for (const material of screwSet.materials) material.dispose();
    }
    bodies.clear();
    edgeBases.clear();
    disposed = true;
  }

  return { apply, restore, dispose, modelFile, get state() { return { ...current }; } };
}
