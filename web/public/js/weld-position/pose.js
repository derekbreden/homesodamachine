// Millimetres; +Z is up. The weld station is on the +X side of the tube.
// Dimensions are checked against the tube interface and the endcap generator.
const IN = 25.4;
export const DIM = Object.freeze({
  tubeOd: 5 * IN,
  tubeWall: 0.065 * IN,
  tubeHeight: 6 * IN,
  capDiameter: 4.860 * IN,
  capThickness: 0.250 * IN,
  capRecess: 0.250 * IN,
  portDiameter: 0.438 * IN,
  portOffset: 0.750 * IN,
  gunLength: 253,
  gunWidth: 34,
  gunHeight: 143,
});

export const INNER_RADIUS = DIM.tubeOd / 2 - DIM.tubeWall;
export const CAP_TOP = DIM.tubeHeight - DIM.capRecess;
export const JOINT = Object.freeze([INNER_RADIUS, 0, CAP_TOP]);

// The unrolled reference puts the gun and its wire guide in the YZ plane:
// their plan projections follow the tangent, perpendicular to the +X radius.
// Pitch and nozzle clearance are illustrative, not measured setup values.
export const PITCH = 60 * Math.PI / 180;
export const CLEARANCE = 16;
export const WIRE_TIP = Object.freeze([0, 0, -CLEARANCE]);
// Cable exit at the bottom of the grip, in the schematic gun's local frame.
export const GRIP_BASE = Object.freeze([0, -118, 237]);
const axisLength = Math.hypot(GRIP_BASE[1], GRIP_BASE[2] + CLEARANCE);
export const LOCAL_ROLL_AXIS = Object.freeze([0, GRIP_BASE[1] / axisLength, (GRIP_BASE[2] + CLEARANCE) / axisLength]);
// A short support leg holds the straight guide close to the barrel. The guide
// aims at the dot; its approach differs from the straight run at the grip.
// Holder dimensions are schematic pending the gun scan.
export const WIRE_BRACE_MOUNT = Object.freeze([0, -12, 110]);
export const WIRE_GUIDE_BACK = Object.freeze([0, -24.7, 87.1]);
export const WIRE_GUIDE_LENGTH = 40;
const guideVector = WIRE_GUIDE_BACK.map((v, i) => v - WIRE_TIP[i]);
export const WIRE_GUIDE_DIRECTION = Object.freeze(guideVector.map(v => v / Math.hypot(...guideVector)));
export const WIRE_GUIDE_END = Object.freeze(WIRE_GUIDE_BACK.map((v, i) => v - WIRE_GUIDE_LENGTH * WIRE_GUIDE_DIRECTION[i]));

export function wireFeedPath() {
  const atGrip = GRIP_BASE.map((v, i) => v + [23, 0, 0][i]);
  const tailEnd = atGrip.map((v, i) => v + 70 * LOCAL_ROLL_AXIS[i]);
  const bendStart = atGrip.map((v, i) => v - 35 * LOCAL_ROLL_AXIS[i]);
  return {
    atGrip, tailEnd, bendStart,
    control1: bendStart.map((v, i) => v - 50 * LOCAL_ROLL_AXIS[i]),
    control2: WIRE_GUIDE_BACK.map((v, i) => v + 45 * WIRE_GUIDE_DIRECTION[i]),
    guideBack: [...WIRE_GUIDE_BACK],
  };
}

export function posePoint(point, rollDegrees = 0, holeRollDegrees = 0, verticalDegrees = 0) {
  const [x, y, z] = point;
  const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEARANCE;
  const py = -c * along + s * y;
  const pz = s * along + c * y;
  const roll = rollDegrees * Math.PI / 180;
  // The axis passes through the dot AND the grip's cable exit. Its plan
  // projection follows the tangent; its elevation follows those two points.
  // Rodrigues rotation fixes the dot and grip base. The guide rolls with the
  // gun while its straight wire continues to aim at the dot.
  const ay = -c * LOCAL_ROLL_AXIS[2] + s * LOCAL_ROLL_AXIS[1];
  const az = s * LOCAL_ROLL_AXIS[2] + c * LOCAL_ROLL_AXIS[1];
  const dot = ay * py + az * pz;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  const rx = x * cr + (ay * pz - az * py) * sr;
  const ry = py * cr + az * x * sr + ay * dot * (1 - cr);
  const rz = pz * cr - ay * x * sr + az * dot * (1 - cr);

  // At zero vertical rotation, the second axis runs through the dot and both
  // port centers. Positive rotation about -X raises the grip and carries
  // the dot-to-grip axis with the gun.
  const holeRoll = holeRollDegrees * Math.PI / 180;
  const ch = Math.cos(holeRoll), sh = Math.sin(holeRoll);
  const hy = ry * ch + rz * sh;
  const hz = -ry * sh + rz * ch;

  // The outer rotation stays vertical in the tube frame and passes through
  // the laser dot. It changes approach in plan without changing elevation.
  const vertical = verticalDegrees * Math.PI / 180;
  const cv = Math.cos(vertical), sv = Math.sin(vertical);
  return [JOINT[0] + rx * cv - hy * sv, JOINT[1] + rx * sv + hy * cv, JOINT[2] + hz];
}
