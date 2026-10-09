// Shared maths for the travel explorer's calc scripts.
// Ported from kit/weldkit.js (which ports web/public/js/weld-position/pose.js).
// EVERYTHING here about the gun is the kit's ILLUSTRATIVE proxy (manual envelope 253 x 143 x 34 mm; grip, pitch 60 deg,
// nozzle clearance 16 mm are illustrative). Tube/cap numbers come from the fabrication sources ([repo]).
// Units: mm, degrees at the interface, +Z up, tube axis = Z, weld station on +X.

export const DEG = Math.PI / 180;
export const IN = 25.4;
export const DIM = {
  tubeOd: 5 * IN, tubeWall: 0.065 * IN, tubeHeight: 6 * IN,
  capDiameter: 4.860 * IN, capThickness: 0.250 * IN, capRecess: 0.250 * IN,
};
export const INNER_RADIUS = DIM.tubeOd / 2 - DIM.tubeWall;         // 61.85 [repo]
export const CAP_TOP = DIM.tubeHeight - DIM.capRecess;              // 146.05 [repo]
export const RIM_Z = DIM.tubeHeight;                                 // 152.4
export const JOINT = [INNER_RADIUS, 0, CAP_TOP];
export const PITCH = 60 * DEG;            // illustrative
export const CLEARANCE = 16;              // illustrative (nozzle tip to dot)
export const GRIP_BASE = [0, -118, 237];  // illustrative proxy
const AX_LEN = Math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE);
export const ROLL_AXIS = [0, GRIP_BASE[1] / AX_LEN, (GRIP_BASE[2] + CLEARANCE) / AX_LEN];
export const HOLE_AXIS_OFFSET = 35;

// local anchors of the proxy gun (origin = nozzle tip, +Z toward the back, -Y grip side, dot at (0,0,-16))
export const ANCHORS = {
  nozzleTip: [0, 0, 0], dot: [0, 0, -CLEARANCE], barrelMid: [0, 0, 77], collar: [0, 0, 109],
  housingTop: [0, 17, 185.5], housingBack: [0, 0, 253],
  gripTop: [0, -25, 172], gripMid: [0, -68, 202], gripBase: GRIP_BASE.slice(),
};

export function posePoint(p, rollDeg, holeRollDeg, verticalDeg) {
  const [x, y, z] = p;
  const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEARANCE;
  const py = -c * along + s * y;
  const pz = s * along + c * y;
  const roll = (rollDeg || 0) * DEG;
  const ay = -c * ROLL_AXIS[2] + s * ROLL_AXIS[1];
  const az = s * ROLL_AXIS[2] + c * ROLL_AXIS[1];
  const dot = ay * py + az * pz;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  const rx = x * cr + (ay * pz - az * py) * sr;
  const ry = py * cr + az * x * sr + ay * dot * (1 - cr);
  const rz = pz * cr - ay * x * sr + az * dot * (1 - cr);
  const holeRoll = (holeRollDeg || 0) * DEG;
  const ch = Math.cos(holeRoll), sh = Math.sin(holeRoll);
  const hy = ry * ch + rz * sh;
  const hz = -ry * sh + rz * ch;
  const vertical = (verticalDeg || 0) * DEG;
  const cv = Math.cos(vertical), sv = Math.sin(vertical);
  return [JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz];
}

// world position of a local gun point at dial settings (dial hole = as shown on the slider; posePoint uses dial - 35)
export function world(local, roll, holeDial, vertical) {
  return posePoint(local, roll, holeDial - HOLE_AXIS_OFFSET, vertical);
}
export const OPENING = { roll: 45, holeDial: 30, vertical: -15 };   // the reference scene's opening pose (illustrative)

export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
export const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const norm = a => Math.hypot(a[0], a[1], a[2]);
export const unit = a => mul(a, 1 / norm(a));
export const fmt = (v, d = 2) => (Math.abs(v) < 0.5 * Math.pow(10, -d) ? 0 : v).toFixed(d);

// rotate point p about the axis through point c with unit direction u by angle a (rad): Rodrigues
export function rotAbout(p, c, u, a) {
  const v = sub(p, c), k = u;
  const cs = Math.cos(a), sn = Math.sin(a);
  const kxv = cross(k, v), kdv = dot3(k, v);
  return add(c, add(add(mul(v, cs), mul(kxv, sn)), mul(k, kdv * (1 - cs))));
}

// seam offset of a world point for a nominal circular seam (radial + into wall, along = arc, vertical above plate)
export function seamOffset(p, seam) {
  const s = seam || { cx: 0, cy: 0 };
  const dx = p[0] - s.cx, dy = p[1] - s.cy, psi = Math.atan2(dy, dx);
  return { radial: Math.hypot(dx, dy) - INNER_RADIUS, along: INNER_RADIUS * psi, vertical: p[2] - CAP_TOP, psiDeg: psi / DEG };
}
