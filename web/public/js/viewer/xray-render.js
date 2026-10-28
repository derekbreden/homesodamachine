// Rendering only: each viewer owns its mode, material caches and line resolution.
// No scene, DOM, storage or application state is imported here.
import * as THREE from "three";
import { LineSegments2 } from "three/addons/lines/LineSegments2.js";
import { LineSegmentsGeometry } from "three/addons/lines/LineSegmentsGeometry.js";
import { LineMaterial } from "three/addons/lines/LineMaterial.js";

export function createXrayRenderer({
  enabled = false,
  surfaceOpacity = 0.14,
  // A body faded behind a focused selection: fainter than an x-ray ghost, and drawn without
  // its feature edges, so the selection is the only structure that reads.
  fadedOpacity = 0.07,
  edgeThreshold = 30,
  edgeWidth = 1.4,
  isMeshVisible = () => true,
} = {}) {
  let active = !!enabled;
  // The root whose bodies fade unless `holds` keeps them; null when nothing is in focus.
  let focus = null;
  const variants = new WeakMap();
  const fadedVariants = new WeakMap();
  const records = new WeakMap();
  const roots = new WeakMap();
  const edgeMaterials = new Set();
  const edgeColors = new Map();
  const bufferSize = new THREE.Vector2();

  function makeEdgeMaterial(params = {}) {
    const material = new LineMaterial({ linewidth: edgeWidth, alphaToCoverage: true, ...params });
    material.resolution.copy(bufferSize);
    edgeMaterials.add(material);
    return material;
  }
  function syncEdgeResolution(renderer) {
    renderer.getDrawingBufferSize(bufferSize);
    for (const material of edgeMaterials) material.resolution.copy(bufferSize);
  }
  function edgeMaterial(base) {
    // A multi-material mesh keeps every surface material. Its feature outline
    // uses the first material with a color, as one continuous structural edge.
    const list = Array.isArray(base) ? base : [base];
    const color = list.find(material => material?.color)?.color || new THREE.Color(0x8899aa);
    const key = color.getHex();
    let material = edgeColors.get(key);
    if (!material) {
      material = makeEdgeMaterial({ color: color.clone() });
      edgeColors.set(key, material);
    }
    return material;
  }
  function variant(cache, base, opacity) {
    let entry = cache.get(base);
    if (!entry) {
      entry = { material: base.clone(), version: base.version };
      cache.set(base, entry);
      // Opened procedural views dispose their base materials when closed. The
      // ghost owns a separate GPU program reference and follows that lifetime.
      const disposeVariant = () => {
        entry.material.dispose();
        cache.delete(base);
        base.removeEventListener("dispose", disposeVariant);
      };
      base.addEventListener("dispose", disposeVariant);
    } else {
      // Selection can change the base color/emission in place between restore
      // and apply. Refresh that clone while retaining its material identity.
      entry.material.copy(base);
      if (entry.version !== base.version) entry.material.needsUpdate = true;
      entry.version = base.version;
    }
    const material = entry.material;
    material.onBeforeCompile = base.onBeforeCompile;
    material.customProgramCacheKey = base.customProgramCacheKey;
    material.transparent = true;
    material.opacity = opacity;
    material.depthWrite = false;
    material.forceSinglePass = true;
    return material;
  }
  const variantsOf = (cache, opacity) => base =>
    Array.isArray(base) ? base.map(material => material ? variant(cache, material, opacity) : material) : variant(cache, base, opacity);
  const ghostMaterial = variantsOf(variants, surfaceOpacity);
  const fadedMaterial = variantsOf(fadedVariants, fadedOpacity);
  const eligible = object => object.isMesh && !object.userData?.isXrayEdge && !object.userData?.hitOnly && object.geometry && object.material;
  function meshesIn(root) {
    const meshes = new Set();
    if (root) root.traverse(object => { if (eligible(object)) meshes.add(object); });
    return meshes;
  }
  function removeEdge(record) {
    if (!record?.line) return;
    record.line.removeFromParent();
    record.line.geometry.dispose();
    record.line = null;
  }
  function release(mesh) {
    const record = records.get(mesh);
    if (!record) return;
    if (record.applied && mesh.material === record.ghost) mesh.material = record.base;
    removeEdge(record);
    records.delete(mesh);
  }
  function meshRecord(mesh) {
    let record = records.get(mesh);
    if (!record) {
      record = { base: mesh.material, ghost: null, line: null, geometry: null, applied: false };
      records.set(mesh, record);
    } else if (!record.applied || mesh.material !== record.ghost) {
      record.base = mesh.material;
    }
    return record;
  }
  function updateEdge(mesh, record) {
    const geometry = mesh.geometry;
    const positionVersion = geometry.getAttribute("position")?.version;
    const indexVersion = geometry.index?.version;
    if (record.geometry !== geometry || record.positionVersion !== positionVersion || record.indexVersion !== indexVersion) {
      removeEdge(record);
      const edges = new THREE.EdgesGeometry(geometry, edgeThreshold);
      const positions = edges.getAttribute("position");
      if (positions?.count) {
        const lineGeometry = new LineSegmentsGeometry().setPositions(positions.array);
        record.line = new LineSegments2(lineGeometry, edgeMaterial(record.base));
        record.line.userData.isXrayEdge = true;
        record.line.userData.sourceMesh = mesh;
      }
      edges.dispose();
      record.geometry = geometry;
      record.positionVersion = positionVersion;
      record.indexVersion = indexVersion;
    }
    const line = record.line;
    if (!line) return;
    // Siblings retain the flat CAD viewer's component editing/picking contract,
    // and nested Groups retain their existing transforms and visibility.
    if (line.parent !== mesh.parent) mesh.parent?.add(line);
    if (mesh.matrixAutoUpdate) mesh.updateMatrix();
    line.position.copy(mesh.position);
    line.quaternion.copy(mesh.quaternion);
    line.scale.copy(mesh.scale);
    line.matrix.copy(mesh.matrix);
    line.matrixAutoUpdate = mesh.matrixAutoUpdate;
    line.layers.mask = mesh.layers.mask;
    line.userData.xrayComponent = mesh.name || "";
    line.material = edgeMaterial(record.base);
    line.visible = mesh.visible !== false && isMeshVisible(mesh);
  }

  function detachEdge(record) {
    if (record.line) { record.line.visible = false; record.line.removeFromParent(); }
  }
  // A body outside the focus fades in either mode. The rest draw solid, or as
  // ghosts with their feature edges while x-ray is on.
  function present(root, mesh, record, on) {
    const faded = focus?.root === root && !focus.holds(mesh);
    record.ghost = faded ? fadedMaterial(record.base) : on ? ghostMaterial(record.base) : null;
    mesh.material = record.ghost || record.base;
    record.applied = !!record.ghost;
    if (on && !faded) updateEdge(mesh, record);
    else detachEdge(record);
  }

  // Restore before a caller changes its materials. Detach cached feature edges
  // so its own mesh traversal sees only its parts; apply reattaches the same
  // edge objects without rebuilding their geometry.
  function restore(root) {
    if (!root) return;
    for (const mesh of meshesIn(root)) {
      const record = records.get(mesh);
      if (!record) continue;
      if (record.applied && mesh.material === record.ghost) mesh.material = record.base;
      record.applied = false;
      detachEdge(record);
    }
  }
  function apply(root, on = active) {
    if (!root) return;
    const meshes = meshesIn(root);
    const previous = roots.get(root);
    // A conductor's opened view can replace procedural children under the same
    // content root. Drop only those departed objects, retaining all other edges.
    if (previous) for (const mesh of previous) if (!meshes.has(mesh)) release(mesh);
    roots.set(root, meshes);
    if (!on && focus?.root !== root) { restore(root); return; }
    for (const mesh of meshes) {
      const record = meshRecord(mesh);
      mesh.userData.baseMaterial = record.base;
      present(root, mesh, record, on);
    }
  }
  function setMeshMaterial(root, mesh, material, on = active) {
    if (!mesh || !eligible(mesh)) return;
    const record = meshRecord(mesh);
    record.base = material;
    mesh.userData.baseMaterial = material;
    present(root, mesh, record, on);
  }
  // Fade every body under `root` that `holds(mesh)` does not keep; no root ends the focus.
  // A root that has left the scene is not redrawn on the way out.
  function setFocus(root = null, holds = null) {
    const previous = focus?.root;
    focus = root && holds ? { root, holds } : null;
    if (previous && previous !== root && previous.parent) apply(previous);
    if (root) apply(root);
  }
  function dispose(root) {
    if (!root) return;
    const meshes = roots.get(root) || meshesIn(root);
    for (const mesh of meshes) release(mesh);
    roots.delete(root);
    if (focus?.root === root) focus = null;
  }
  function forgetEdgeMaterials() { edgeColors.clear(); }
  function setEnabled(on) { active = !!on; }
  function isEnabled() { return active; }

  return { apply, restore, setEnabled, isEnabled, syncEdgeResolution, makeEdgeMaterial, setMeshMaterial, setFocus, forgetEdgeMaterials, dispose };
}
