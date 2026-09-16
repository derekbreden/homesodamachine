import * as THREE from "three";
import { ENCLOSURE_FASTENERS, REVEAL_DEFAULTS, clamp, corePartGroup, ease, fastenerMotion, revealMotion, revealOpacity } from "./reveal-plan.js";
export { REVEAL_STATES, REVEAL_DEFAULTS } from "./reveal-plan.js";

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
  const fadedMaterials = new Map();
  const translation = new THREE.Vector3();
  const screwSet = group ? fasteners(group) : null;
  const remember = (object) => ({
    position: object.position.clone(), quaternion: object.quaternion.clone(),
    scale: object.scale.clone(), matrix: object.matrix.clone(),
    matrixAutoUpdate: object.matrixAutoUpdate, visible: object.visible,
    material: object.material, fadedMaterial: null,
    tourOpacity: object.userData.tourOpacity,
  });
  if (group) {
    for (const object of group.children) {
      if (!object.isMesh || object.userData.isXrayEdge) continue;
      bodies.set(object, remember(object));
    }
  }
  let current = { ...REVEAL_DEFAULTS };
  let disposed = false;

  function faded(material, opacity, lane) {
    let lanes = fadedMaterials.get(material);
    if (!lanes) fadedMaterials.set(material, lanes = new Map());
    let clone = lanes.get(lane);
    if (!clone) {
      clone = material.clone();
      clone.transparent = true;
      clone.depthWrite = false;
      lanes.set(lane, clone);
    }
    clone.opacity = material.opacity * opacity;
    if (clone.resolution && material.resolution) clone.resolution.copy(material.resolution);
    return clone;
  }

  function opacityFor(object, base, opacity, name = object.name) {
    // The reader can toggle x-ray between frames, replacing the source material.
    if (object.material !== base.fadedMaterial) base.material = object.material;
    if (opacity < 1) {
      const part = corePartGroup(name);
      const lane = part === "caps" || part === "shell" ? "covers" : "surroundings";
      base.fadedMaterial = Array.isArray(base.material)
        ? base.material.map((material) => faded(material, opacity, lane)) : faded(base.material, opacity, lane);
      object.material = base.fadedMaterial;
    } else {
      object.material = base.material;
      base.fadedMaterial = null;
    }
    object.visible = base.visible && opacity > 0.001;
    object.userData.tourOpacity = opacity;
  }

  function apply(next = {}) {
    if (!group || disposed) return;
    current = Object.fromEntries(Object.keys(REVEAL_DEFAULTS).map((key) => [key, clamp(next[key] || 0)]));
    for (const [object, base] of bodies) {
      const delta = revealMotion(object.name, current);
      object.position.copy(base.position).add(translation.set(...delta));
      object.quaternion.copy(base.quaternion);
      object.scale.copy(base.scale);
      object.updateMatrix();
      opacityFor(object, base, revealOpacity(object.name, current));
    }
    // X-ray toggles replace their edge objects. Each fresh edge inherits the solid's pose.
    const byName = new Map();
    for (const [object, base] of bodies) if (!byName.has(object.name)) byName.set(object.name, { object, base });
    for (const edge of group.children) {
      if (!edge.userData.isXrayEdge) continue;
      const source = byName.get(edge.userData.xrayComponent);
      if (!source) continue;
      if (!edgeBases.has(edge)) {
        edgeBases.set(edge, { ...remember(edge),
          position: source.base.position.clone(), quaternion: source.base.quaternion.clone(),
          scale: source.base.scale.clone(), matrix: source.base.matrix.clone(),
        });
      }
      edge.position.copy(source.object.position);
      edge.quaternion.copy(source.object.quaternion);
      edge.scale.copy(source.object.scale);
      edge.updateMatrix();
      opacityFor(edge, edgeBases.get(edge), revealOpacity(source.object.name, current), source.object.name);
    }
    if (screwSet) {
      const opacity = 1 - ease(current.coreIsolation);
      screwSet.root.visible = opacity > 0.001;
      for (const material of screwSet.materials.slice(0, 2)) {
        material.opacity = opacity;
        material.transparent = opacity < 1;
      }
      const emphasis = ease((current.enclosure - 0.005) / 0.025)
        * (1 - ease((current.enclosure - 0.36) / 0.02));
      screwSet.markerMaterial.opacity = 0.86 * emphasis * opacity;
      screwSet.axisMaterial.opacity = 0.40 * emphasis * opacity;
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
      object.matrix.copy(base.matrix);
      object.matrixAutoUpdate = base.matrixAutoUpdate;
      object.visible = base.visible;
      if (base.tourOpacity === undefined) delete object.userData.tourOpacity;
      else object.userData.tourOpacity = base.tourOpacity;
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
    for (const lanes of fadedMaterials.values()) {
      for (const material of lanes.values()) material.dispose();
    }
    fadedMaterials.clear();
    disposed = true;
  }

  return { apply, restore, dispose, modelFile, get state() { return { ...current }; } };
}
