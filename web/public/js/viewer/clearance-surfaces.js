// The highlighted triangles and cropped context come from each part's published CAD mesh.
import * as THREE from "three";
import { faceIndexAtTriangle } from "./picked-face.js";

export const faceColors = { host: 0xfa64cc, mate: 0x65decf };
const vector = xyz => new THREE.Vector3().fromArray(xyz);
const box = (lo, hi) => new THREE.Box3(vector(lo), vector(hi));

function nearestFaces(meshes, points) {
  const matches = points.map(() => ({ distance: 0.5 ** 2 }));
  const triangle = new THREE.Triangle(), near = new THREE.Vector3(), bounds = new THREE.Box3();
  for (const mesh of meshes) {
    if (!mesh.brep_faces?.length) continue;
    const positions = mesh.attributes.position.array, indices = mesh.index.array;
    for (let i = 0; i < indices.length; i += 3) {
      triangle.a.fromArray(positions, indices[i] * 3);
      triangle.b.fromArray(positions, indices[i + 1] * 3);
      triangle.c.fromArray(positions, indices[i + 2] * 3);
      bounds.min.copy(triangle.a).min(triangle.b).min(triangle.c);
      bounds.max.copy(triangle.a).max(triangle.b).max(triangle.c);
      for (let j = 0; j < points.length; j++) {
        const match = matches[j], point = points[j];
        bounds.clampPoint(point, near);
        if (near.distanceToSquared(point) >= match.distance) continue;
        const distance = triangle.closestPointToPoint(point, near).distanceToSquared(point);
        if (distance >= match.distance) continue;
        const face = mesh.brep_faces[faceIndexAtTriangle(mesh.brep_faces, i / 3)];
        if (face) Object.assign(match, { mesh, face, distance });
      }
    }
  }
  return matches;
}

function meshGeometry(mesh) {
  const geometry = new THREE.BufferGeometry();
  for (const name of ["position", "normal"]) {
    const data = mesh.attributes[name]?.array;
    if (data?.length) geometry.setAttribute(name, new THREE.BufferAttribute(data instanceof Float32Array ? data : new Float32Array(data), 3));
  }
  const indices = mesh.index.array instanceof Uint32Array ? mesh.index.array : new Uint32Array(mesh.index.array);
  geometry.setIndex(new THREE.BufferAttribute(indices, 1));
  return geometry;
}

function clipPlanes(bounds) {
  return ["x", "y", "z"].flatMap(axis => {
    const normal = new THREE.Vector3(); normal[axis] = 1;
    return [new THREE.Plane(normal, -bounds.min[axis]), new THREE.Plane(normal.clone().negate(), bounds.max[axis])];
  });
}

export function fitSide(meshes, site, side, fit) {
  const group = new THREE.Group(), clips = [], marks = [];
  const positioned = new THREE.Group(); group.add(positioned);
  if (site.placement) {
    positioned.matrix.set(...site.placement.flat(), 0, 0, 0, 1);
    positioned.matrixAutoUpdate = false;
  }
  const points = (site.faces || []).map(([, ...xyz]) => vector(xyz));
  const witnesses = new THREE.Box3().setFromPoints(points);
  if (site.band) witnesses.union(box(site.band.lo, site.band.hi));
  const pocket = !!fit.hostGaps;
  const margin = Math.max(5, Math.min(14, (fit.dimensions[0].nominal || 12) * 0.6));
  const crop = site.crop ? box(...site.crop).expandByScalar(2.5)
    : site.whole || (pocket && side === "mate") ? null : witnesses.clone().expandByScalar(margin);
  const localBounds = new THREE.Box3();
  const bases = new Map();
  function addMesh(geometry, options, clippedTo) {
    const planes = clippedTo ? clipPlanes(clippedTo) : [];
    const material = new THREE.MeshPhongMaterial({ side: THREE.DoubleSide, shininess: 18, ...options,
      clippingPlanes: planes.map(plane => plane.clone()) });
    if (planes.length) clips.push({ planes, world: material.clippingPlanes });
    const solid = new THREE.Mesh(geometry, material);
    positioned.add(solid);
    return solid;
  }
  for (const mesh of meshes) {
    const geometry = meshGeometry(mesh);
    geometry.computeBoundingBox();
    const visible = geometry.boundingBox.clone();
    if (crop) visible.intersect(crop);
    if (visible.isEmpty()) { geometry.dispose(); continue; }
    bases.set(mesh, geometry);
    localBounds.union(visible);
    const color = mesh.color ? new THREE.Color(...mesh.color) : new THREE.Color(0xaab1c0);
    const ghost = !(pocket && side === "mate");
    if (ghost) color.lerp(new THREE.Color(side === "host" ? 0x747386 : 0x95b2b8), 0.46);
    addMesh(geometry, { color, transparent: ghost, opacity: ghost ? (site.whole ? 0.62 : 0.40) : 1, depthWrite: !ghost,
      polygonOffset: true, polygonOffsetFactor: 1, polygonOffsetUnits: 1 }, crop);
  }

  function mark(mesh, name, point, face, region) {
    const base = bases.get(mesh), surface = new THREE.BufferGeometry();
    surface.setAttribute("position", base.attributes.position);
    if (base.attributes.normal) surface.setAttribute("normal", base.attributes.normal);
    const indices = base.index.array;
    surface.setIndex(face ? new THREE.BufferAttribute(indices.subarray(face.first * 3, (face.last + 1) * 3), 1) : base.index);
    const solid = addMesh(surface, { color: faceColors[side], transparent: true,
      opacity: 0.58, depthTest: !pocket, depthWrite: false, polygonOffset: true, polygonOffsetFactor: -2, polygonOffsetUnits: -2 }, region);
    solid.renderOrder = 2;
    if (pocket && side === "host") {
      // Fade the outside of each wall so the pocket reads as an opening from any angle.
      solid.material.onBeforeCompile = shader => {
        shader.fragmentShader = shader.fragmentShader.replace("#include <color_fragment>",
          "#include <color_fragment>\nif (!gl_FrontFacing) diffuseColor.a *= 0.22;");
      };
      const outline = new THREE.LineSegments(new THREE.EdgesGeometry(surface, 20), new THREE.LineBasicMaterial({
        color: 0xffa8e9, transparent: true, opacity: 0.72, depthTest: false, depthWrite: false,
        clippingPlanes: solid.material.clippingPlanes,
      }));
      outline.renderOrder = 3; positioned.add(outline);
    }
    return { name, point: point.clone().applyMatrix4(positioned.matrix), material: solid.material };
  }
  if (points.length) {
    const matches = nearestFaces(bases.keys(), points);
    matches.forEach(({ mesh, face }, i) => {
      // The witness still identifies its authored location if a reduced mesh omits that face.
      const name = site.faces[i][0];
      marks.push(mesh ? mark(mesh, name, points[i], face, crop)
        : { name, point: points[i].clone().applyMatrix4(positioned.matrix) });
    });
  } else if (site.band) {
    const band = box(site.band.lo, site.band.hi);
    for (const mesh of bases.keys()) {
      const marker = mark(mesh, site.band.label, band.getCenter(new THREE.Vector3()), null, band);
      if (!marks.length) marks.push(marker);
    }
  }
  if (localBounds.isEmpty()) throw new Error("No geometry at this fit");
  const bounds = localBounds.applyMatrix4(positioned.matrix);
  function move(offset) {
    group.position.copy(offset);
    positioned.updateWorldMatrix(true, false);
    for (const { planes, world } of clips) planes.forEach((plane, i) => world[i].copy(plane).applyMatrix4(positioned.matrixWorld));
  }
  return { group, bounds, marks, move };
}

// Stock tubing without an installed model is drawn at its specified outside diameter along the collar bore.
export function nominalTube(fit) {
  const radius = fit.dimensions[0].nominal / 2;
  const mid = fit.hostSites[0].faces[0][2];
  const geometry = new THREE.CylinderGeometry(radius, radius, mid * 2, 72, 1, true);
  geometry.translate(0, mid, 0);
  const material = new THREE.MeshPhongMaterial({ color: faceColors.mate, side: THREE.DoubleSide });
  const group = new THREE.Group(); group.add(new THREE.Mesh(geometry, material));
  const bounds = new THREE.Box3().setFromObject(group);
  return { group, bounds, marks: [{ name: "Nominal tube OD", point: new THREE.Vector3(radius, mid, 0) }],
    move: offset => group.position.copy(offset) };
}
