// THE PART, AND THE THING POINTED AT IT. Geometry only — no clock, no camera.
//
// Every dimension here is read off the carbonator: 5" OD × 0.065" wall × 6"
// 316L tube (OnlineMetals #12498), a 4.860" × 1/4" laser-cut 316L plate
// (endcap_circular_dxf.py) seated as an ID-fit plug recessed 1/4" below the
// tube end, and the corner fillet that closes the internal corner those two
// leave. `hardware/assembly/pressure-vessel.md` steps 3 and 5 are the joint;
// `hardware/assembly/weld-rotation-rig.md` is the rig this draws.
//
// THE TUBE AXIS IS +Y and the part turns about it, because that is the whole
// claim the page is making: the head does not move, the part does.
//
// LOCAL ANGLE IS MEASURED FROM +Z TOWARD +X — position (r·sinθ, y, r·cosθ).
// Under that convention a group rotated `rotation.y = φ` carries local θ to
// world θ + φ, with no sign flip to remember. Everything downstream (where
// the head stands, where the bead has been laid, which side the wire enters
// from) is one subtraction in that frame.

import * as THREE from "three";

const IN = 25.4;

export const DIM = {
  tubeOd:    5.000 * IN,   // 127.00 mm
  tubeWall:  0.065 * IN,   //   1.651 mm
  tubeH:     6.000 * IN,   // 152.40 mm — TANK_H
  plateOd:   4.860 * IN,   // 123.44 mm — tube ID − 0.010" slip
  plateT:    0.250 * IN,   //   6.35 mm
  recess:    0.250 * IN,   //   6.35 mm — plate outer face below the tube end
  portBore:  0.438 * IN,   //  11.13 mm — PORT_BORE
  portR:     1.500 * IN,   // port pair off-axis, ±X of the plate
};

DIM.tubeId  = DIM.tubeOd - 2 * DIM.tubeWall;   // 123.698 mm
DIM.beadR   = DIM.tubeId / 2;                  //  61.849 mm — the corner's radius
DIM.beadC   = Math.PI * DIM.tubeId;            // 388.60 mm — one lap of bead
DIM.capTopY = DIM.tubeH - DIM.recess;          // the plate's outer face

// The wire's own cross-section, which is what turns a travel speed into a
// fillet size: ER316L .030" = 0.762 mm Ø.
export const WIRE_AREA = Math.PI * Math.pow(0.030 * IN, 2) / 4;   // 0.456 mm²

// A metal with nothing around it to reflect renders black. Every value below
// assumes `scene.environment` is set (main.js builds one), because that is
// what makes 316L look like 316L instead of like charcoal.
const MAT = {
  tube:  new THREE.MeshStandardMaterial({ color: 0xb0b9c5, metalness: 0.92, roughness: 0.3 }),
  plate: new THREE.MeshStandardMaterial({ color: 0x8e99a7, metalness: 0.78, roughness: 0.44 }),
  port:  new THREE.MeshStandardMaterial({ color: 0x0e0e16, metalness: 0.2,  roughness: 0.95 }),
  index: new THREE.MeshStandardMaterial({ color: 0x4488ff, metalness: 0.2,  roughness: 0.7,
                                          emissive: 0x18406e, emissiveIntensity: 1 }),
  bead:  new THREE.MeshStandardMaterial({
    color: 0xe8a33c, metalness: 0.45, roughness: 0.5,
    emissive: 0x6b3c05, emissiveIntensity: 1,
  }),
  gun:   new THREE.MeshStandardMaterial({ color: 0x5b638a, metalness: 0.45, roughness: 0.5 }),
  gunLip:new THREE.MeshStandardMaterial({ color: 0x4488ff, metalness: 0.4, roughness: 0.35 }),
  wire:  new THREE.MeshStandardMaterial({ color: 0xd6dbe4, metalness: 0.95, roughness: 0.22 }),
};

// A profile drawn in the (radius, y) half-plane, swept through an arc about
// +Y. This is the one geometry primitive the page needs: the tube, the fillet
// bead and the plate rim are all profiles revolved through some angle.
//
// `profile` is [[r, y], …] and closes on itself. Angles follow the local-angle
// convention above, so a sweep from θ0 to θ1 lands exactly where the head says
// it should.
export function sweepProfile(profile, theta0, theta1, segments, { cap = false } = {}) {
  const n = profile.length;
  const steps = Math.max(1, segments);
  const pos = [];
  const idx = [];

  for (let s = 0; s <= steps; s++) {
    const th = theta0 + (theta1 - theta0) * (s / steps);
    const st = Math.sin(th), ct = Math.cos(th);
    for (let p = 0; p < n; p++) {
      const [r, y] = profile[p];
      pos.push(r * st, y, r * ct);
    }
  }
  for (let s = 0; s < steps; s++) {
    for (let p = 0; p < n; p++) {
      const q = (p + 1) % n;
      const a = s * n + p, b = s * n + q, c = (s + 1) * n + q, d = (s + 1) * n + p;
      idx.push(a, b, c, a, c, d);
    }
  }
  // A partial sweep is an open tube; close its two ends so a growing bead
  // reads as having a start and a leading edge rather than a hole.
  if (cap) {
    for (const [s, flip] of [[0, false], [steps, true]]) {
      const base = pos.length / 3;
      let cr = 0, cy = 0;
      for (const [r, y] of profile) { cr += r / n; cy += y / n; }
      const th = theta0 + (theta1 - theta0) * (s / steps);
      pos.push(cr * Math.sin(th), cy, cr * Math.cos(th));
      for (let p = 0; p < n; p++) {
        const q = (p + 1) % n;
        const a = s * n + p, b = s * n + q;
        idx.push(base, ...(flip ? [b, a] : [a, b]));
      }
    }
  }

  const g = new THREE.BufferGeometry();
  g.setAttribute("position", new THREE.Float32BufferAttribute(pos, 3));
  g.setIndex(idx);
  g.computeVertexNormals();
  return g;
}

// The tube: a rectangular section revolved the whole way round, so it has real
// ends and a real bore rather than two nested shells.
function buildTube() {
  const ro = DIM.tubeOd / 2, ri = DIM.tubeId / 2;
  const g = sweepProfile([[ri, 0], [ro, 0], [ro, DIM.tubeH], [ri, DIM.tubeH]], 0, Math.PI * 2, 220);
  return new THREE.Mesh(g, MAT.tube);
}

// The plate, seated. Its outer face is what the fillet washes onto, so it is
// drawn where the procedure puts it — 1/4" down the bore, not flush.
function buildPlate() {
  const g = new THREE.CylinderGeometry(DIM.plateOd / 2, DIM.plateOd / 2, DIM.plateT, 96);
  const m = new THREE.Mesh(g, MAT.plate);
  m.position.y = DIM.capTopY - DIM.plateT / 2;
  return m;
}

// Two ports and the seam. NOT DECORATION — they are the only things on a
// turned cylinder that let an eye read rotation at all. A featureless tube
// spinning at 1.2 RPM looks like a tube standing still.
function buildMarks(group, indexTheta) {
  for (const sx of [-1, 1]) {
    const g = new THREE.CylinderGeometry(DIM.portBore / 2, DIM.portBore / 2, 1.6, 32);
    const m = new THREE.Mesh(g, MAT.port);
    m.position.set(sx * DIM.portR, DIM.capTopY - 0.7, 0);
    group.add(m);
  }
  // THE INDEX STRIPE, standing at the head's own angle. When it comes back
  // under the head the lap has closed, and everything past that is overlap.
  // It runs the height of the tube and continues across the plate, so it
  // answers "how far round" from the side and from straight above alike.
  const ro = DIM.tubeOd / 2;
  const w = 0.028;
  group.add(new THREE.Mesh(
    sweepProfile([[ro, 0], [ro + 0.35, 0], [ro + 0.35, DIM.tubeH], [ro, DIM.tubeH]],
                 indexTheta - w, indexTheta + w, 1),
    MAT.index,
  ));
  const bar = new THREE.Mesh(new THREE.BoxGeometry(4, 0.8, 32), MAT.index);
  bar.position.set((DIM.beadR - 20) * Math.sin(indexTheta), DIM.capTopY + 0.45,
                   (DIM.beadR - 20) * Math.cos(indexTheta));
  bar.rotation.y = indexTheta;
  group.add(bar);
}

// Everything that turns, in one group. The caller spins `group.rotation.y`
// and nothing else in the scene moves.
export function buildPart(indexTheta = 0) {
  const group = new THREE.Group();
  group.add(buildTube());
  group.add(buildPlate());
  buildMarks(group, indexTheta);
  return group;
}

// The fillet's cross-section, in (radius, y), for a given leg length. The root
// is the corner itself — bore wall meets plate face — and the two legs run in
// off it, with a slightly convex face between them.
function filletProfile(leg) {
  const r0 = DIM.beadR, y0 = DIM.capTopY;
  const k = leg * 0.30;
  return [
    [r0,       y0],            // root, in the corner
    [r0,       y0 + leg],      // up the bore wall
    [r0 - k,   y0 + k * 1.6],  // the convex face
    [r0 - leg, y0],            // out along the plate face
  ];
}

// The bead laid so far. It lives in the PART's frame, so it turns with the
// part and stays where it was put — which is the whole point of the picture.
//
// The head stands at world angle `headTheta` and the part has turned through
// `phi`, so the metal now under the head is at local `headTheta − phi` and the
// bead occupies local [headTheta − phi, headTheta].
export class Bead {
  constructor(parent, leg = 1.2) {
    this.parent = parent;
    this.leg = leg;
    this.mesh = null;
    this.built = -1;
  }

  // `phi` is SIGNED: the part turns +φ or −φ, and the bead trails on whichever
  // side of the head the finished metal is leaving toward. One sweep covers
  // both directions because sweepProfile interpolates θ0 → θ1 either way.
  set(headTheta, phi, leg) {
    if (leg !== undefined && leg !== this.leg) { this.leg = leg; this.built = -1; }
    const mag = Math.abs(phi);
    if (mag <= 0.0005) { this.clear(); return; }
    // Rebuild only when the arc has actually grown — at 1.2 RPM a frame moves
    // it 0.12°, and a geometry per frame is a geometry per frame.
    if (Math.abs(mag - this.built) < 0.004) return;
    this.clear();
    const segs = Math.max(2, Math.ceil((mag / (Math.PI * 2)) * 260));
    const g = sweepProfile(filletProfile(this.leg), headTheta - phi, headTheta, segs, { cap: true });
    this.mesh = new THREE.Mesh(g, MAT.bead);
    this.parent.add(this.mesh);
    this.built = mag;
  }

  clear() {
    if (!this.mesh) return;
    this.parent.remove(this.mesh);
    this.mesh.geometry.dispose();
    this.mesh = null;
    this.built = -1;
  }
}

// A tack — the same fillet section, a few degrees of it, dropped at one local
// angle and left there. The rig indexes to eight of these before it runs the
// lap.
export function buildTack(parent, localTheta, leg = 1.2) {
  const half = 0.035;   // ~2° of arc, ~4 mm of bead
  const g = sweepProfile(filletProfile(leg), localTheta - half, localTheta + half, 4, { cap: true });
  const m = new THREE.Mesh(g, MAT.bead);
  parent.add(m);
  return m;
}

// THE HEAD, AND WHY IT LEANS IN. The joint is a corner 6.35 mm down a 123.7 mm
// bore. A beam angled outward is blocked by the tube wall the instant it tilts
// — the rim stands at the same radius as the corner — so the only way in is
// over the plate: the head leans INWARD, above the bore, and fires down and
// out into the corner. `tilt` is that lean, off vertical.
//
// Returns a group parked in the WORLD, not on the part.
export function buildHead({ headTheta = 0, tilt = Math.PI / 4, standoff = 22 } = {}) {
  const group = new THREE.Group();

  const target = new THREE.Vector3(
    DIM.beadR * Math.sin(headTheta),
    DIM.capTopY,
    DIM.beadR * Math.cos(headTheta),
  );
  // Down and outward, in the plane through the axis at headTheta.
  const dir = new THREE.Vector3(
    Math.sin(tilt) * Math.sin(headTheta),
    -Math.cos(tilt),
    Math.sin(tilt) * Math.cos(headTheta),
  ).normalize();

  const place = (mesh, alongFrom, alongTo) => {
    const a = target.clone().addScaledVector(dir, -alongFrom);
    const b = target.clone().addScaledVector(dir, -alongTo);
    mesh.position.copy(a.clone().add(b).multiplyScalar(0.5));
    mesh.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), dir.clone().negate());
    group.add(mesh);
  };

  // Nozzle cone, then the barrel behind it — schematic, but the standoff and
  // the lean are the two things it has to get right.
  const cone = new THREE.Mesh(new THREE.CylinderGeometry(3.2, 8, standoff - 4, 28), MAT.gunLip);
  place(cone, 4, standoff);
  const barrel = new THREE.Mesh(new THREE.CylinderGeometry(9, 9, 46, 28), MAT.gun);
  place(barrel, standoff, standoff + 46);
  const body = new THREE.Mesh(new THREE.CylinderGeometry(12, 12, 58, 28), MAT.gun);
  place(body, standoff + 46, standoff + 104);

  // The wire, entering from the side the unwelded metal arrives from. The work
  // travels +θ under a fixed head, so the torch travels −θ over the work: the
  // leading edge of the puddle faces world angles BELOW headTheta, and that is
  // where the wire has to come in. Flip the rotation and this has to move.
  const wire = new THREE.Group();
  group.add(wire);
  group.userData.wire = wire;
  group.userData.target = target;
  group.userData.dir = dir;
  group.userData.headTheta = headTheta;
  setWireSide(group, +1);

  return group;
}

// `sign` is the direction the part turns: +1 carries local angle to larger
// world angle. The wire leads, so it stands on the −sign side of the head.
export function setWireSide(head, sign) {
  const { wire, target, headTheta } = head.userData;
  while (wire.children.length) {
    const c = wire.children.pop();
    c.geometry.dispose();
  }
  const lead = headTheta - sign * 0.26;         // ~15° upstream of the puddle
  const from = new THREE.Vector3(
    (DIM.beadR - 6) * Math.sin(lead),
    DIM.capTopY + 34,
    (DIM.beadR - 6) * Math.cos(lead),
  );
  const seg = new THREE.Vector3().subVectors(target, from);
  const len = seg.length();
  const m = new THREE.Mesh(new THREE.CylinderGeometry(0.9, 0.9, len, 10), MAT.wire);
  m.position.copy(from).addScaledVector(seg, 0.5);
  m.quaternion.setFromUnitVectors(new THREE.Vector3(0, 1, 0), seg.clone().normalize());
  wire.add(m);

  const guide = new THREE.Mesh(new THREE.CylinderGeometry(2.6, 2.6, 22, 16), MAT.gun);
  guide.position.copy(from).addScaledVector(seg, -0.12);
  guide.quaternion.copy(m.quaternion);
  wire.add(guide);
}
