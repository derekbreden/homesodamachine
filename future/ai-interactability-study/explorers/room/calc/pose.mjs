// pose.mjs - port of the kit's posePointArr / dialsToPose (kit/weldkit.js, itself a port of
// web/public/js/weld-position/pose.js). Plain node, no dependencies. Millimetres, +Z up, tube axis = Z,
// weld station on +X, tube bottom at z = 0.  [repo] tube/cap numbers; the gun proxy is ILLUSTRATIVE.
const DEG = Math.PI / 180, IN = 25.4;
export const DIM = { tubeOd: 5 * IN, tubeWall: 0.065 * IN, tubeHeight: 6 * IN, capRecess: 0.25 * IN };
export const RI = DIM.tubeOd / 2 - DIM.tubeWall;          // 61.85 weld-circle radius [repo]
export const RO = DIM.tubeOd / 2;                          // 63.5
export const RIM_Z = DIM.tubeHeight;                       // 152.4
export const JOINT_Z = DIM.tubeHeight - DIM.capRecess;     // 146.05
export const JOINT = [RI, 0, JOINT_Z];
export const PITCH = 60 * DEG, CLEARANCE = 16;             // illustrative (reference scene)
export const GRIP_BASE = [0, -118, 237];
const axl = Math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE);
export const ROLL_AXIS = [0, GRIP_BASE[1] / axl, (GRIP_BASE[2] + CLEARANCE) / axl];
export const HOLE_OFFSET = 35;

export function posePoint(p, rollDeg = 0, holeRollDeg = 0, vertDeg = 0) {
  const [x, y, z] = p;
  const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEARANCE;
  const py = -c * along + s * y, pz = s * along + c * y;
  const roll = rollDeg * DEG;
  const ay = -c * ROLL_AXIS[2] + s * ROLL_AXIS[1], az = s * ROLL_AXIS[2] + c * ROLL_AXIS[1];
  const dot = ay * py + az * pz;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  const rx = x * cr + (ay * pz - az * py) * sr;
  const ry = py * cr + az * x * sr + ay * dot * (1 - cr);
  const rz = pz * cr - ay * x * sr + az * dot * (1 - cr);
  const hr = holeRollDeg * DEG, ch = Math.cos(hr), sh = Math.sin(hr);
  const hy = ry * ch + rz * sh, hz = -ry * sh + rz * ch;
  const v = vertDeg * DEG, cv = Math.cos(v), sv = Math.sin(v);
  return [JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz];
}
// dials as the sliders show them (holeDial = posePoint hole angle + 35)
export function world(p, roll = 45, holeDial = 30, vert = -15) { return posePoint(p, roll, holeDial - HOLE_OFFSET, vert); }
export function worldDir(d, roll = 45, holeDial = 30, vert = -15) {
  const a = world([0, 0, 0], roll, holeDial, vert), b = world(d, roll, holeDial, vert);
  return [b[0] - a[0], b[1] - a[1], b[2] - a[2]];
}
// local anchor points of the proxy gun (kit gun.anchors)
const gripStart = [0, -25, 172], gripEnd = [0, -111, 232];
export const ANCHORS = {
  nozzleTip: [0, 0, 0], dot: [0, 0, -CLEARANCE], barrelMid: [0, 0, 77], collar: [0, 0, 109],
  housingTop: [0, 17, 185.5], housingBack: [0, 0, 253], gripTop: gripStart, gripBase: GRIP_BASE,
  gripMid: gripStart.map((v, i) => (v + gripEnd[i]) / 2), wireBracket: [0, -12, 110],
};
export const add = (a, b) => a.map((v, i) => v + b[i]);
export const sub = (a, b) => a.map((v, i) => v - b[i]);
export const scl = (a, k) => a.map(v => v * k);
export const dot3 = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
export const len = a => Math.hypot(...a);
export const unit = a => scl(a, 1 / len(a));
export const cross = (a, b) => [a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0]];
export const fmt = (a, d = 1) => '[' + a.map(v => v.toFixed(d)).join(', ') + ']';
