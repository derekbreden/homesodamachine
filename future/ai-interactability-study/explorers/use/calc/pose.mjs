// Port of the kit's pose maths (kit/weldkit.js posePointArr / dialsToPose) for stand-alone calculations.
// Coordinates: mm, +Z up, tube axis = Z, weld station on +X, joint at (61.85, 0, 146.05).
// Gun proxy geometry is the kit's ILLUSTRATIVE proxy (manual envelope 253 x 143 x 34 mm only).
export const IN = 25.4;
export const DEG = Math.PI / 180;
export const TUBE_OD = 5 * IN, WALL = 0.065 * IN, RI = TUBE_OD / 2 - WALL, RO = TUBE_OD / 2;
export const RIM_Z = 6 * IN, CAP_TOP = RIM_Z - 0.25 * IN;
export const JOINT = [RI, 0, CAP_TOP];
export const PITCH = 60 * DEG, CLEAR = 16;
export const GRIP_BASE = [0, -118, 237];
const ax0 = Math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEAR);
export const ROLL_AXIS = [0, GRIP_BASE[1] / ax0, (GRIP_BASE[2] + CLEAR) / ax0];
const HOLE_OFFSET = 35;
export const ANCHORS = {
  nozzleTip: [0, 0, 0], dot: [0, 0, -CLEAR], barrelMid: [0, 0, 77], collar: [0, 0, 109],
  housingTop: [0, 17, 185.5], housingBack: [0, 0, 253], gripTop: [0, -25, 172], gripBase: GRIP_BASE,
};
export function posePoint(p, roll, holeRoll, vertical) {
  const [x, y, z] = p; const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEAR, py = -c * along + s * y, pz = s * along + c * y, r = roll * DEG;
  const ay = -c * ROLL_AXIS[2] + s * ROLL_AXIS[1], az = s * ROLL_AXIS[2] + c * ROLL_AXIS[1];
  const dot = ay * py + az * pz, cr = Math.cos(r), sr = Math.sin(r);
  const rx = x * cr + (ay * pz - az * py) * sr, ry = py * cr + az * x * sr + ay * dot * (1 - cr), rz = pz * cr - ay * x * sr + az * dot * (1 - cr);
  const h = holeRoll * DEG, ch = Math.cos(h), sh = Math.sin(h);
  const hy = ry * ch + rz * sh, hz = -ry * sh + rz * ch, v = vertical * DEG, cv = Math.cos(v), sv = Math.sin(v);
  return [JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz];
}
// world point of a gun-local point at the given dials (holeDial as the slider shows it)
export function world(local, roll = 45, holeDial = 30, vertical = -15) { return posePoint(local, roll, holeDial - HOLE_OFFSET, vertical); }
export const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
export const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
export const mul = (a, k) => [a[0] * k, a[1] * k, a[2] * k];
export const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const norm = a => Math.hypot(a[0], a[1], a[2]);
export const unit = a => mul(a, 1 / norm(a));
export const fmt = (a, d = 1) => '(' + a.map(v => v.toFixed(d)).join(', ') + ')';
// Rodrigues rotation of point p about the line (origin o, unit direction u) by angle a (rad)
export function rotAbout(p, o, u, a) {
  const v = sub(p, o), c = Math.cos(a), s = Math.sin(a);
  const t1 = mul(v, c), t2 = mul(cross(u, v), s), t3 = mul(u, dot(u, v) * (1 - c));
  return add(o, add(t1, add(t2, t3)));
}
if (process.argv[1] && process.argv[1].endsWith('pose.mjs')) {
  const d = [45, 30, -15];
  console.log('opening pose dials', d.join(', '));
  for (const k of Object.keys(ANCHORS)) console.log(k.padEnd(12), fmt(world(ANCHORS[k], ...d)));
  const bd = unit(sub(world(ANCHORS.dot, ...d), world(ANCHORS.nozzleTip, ...d)));
  console.log('beam dir (nozzle->dot)', fmt(bd, 3), ' angle from vertical', (Math.acos(-bd[2]) / DEG).toFixed(1));
  const bx = unit(sub(world(ANCHORS.housingBack, ...d), world(ANCHORS.nozzleTip, ...d)));
  console.log('barrel axis toward back', fmt(bx, 3), 'elev', (Math.asin(bx[2]) / DEG).toFixed(1));
}
