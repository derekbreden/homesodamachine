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
// The final guide lies on the dot-to-base line; rolling the gun keeps its
// straight wire approach on that line. Bracket placement is schematic.
export const WIRE_GUIDE_END = Object.freeze([0, GRIP_BASE[1] * (28 + CLEARANCE) / (GRIP_BASE[2] + CLEARANCE), 28]);

export function posePoint(point, rollDegrees = 0, holeRollDegrees = 0) {
  const [x, y, z] = point;
  const s = Math.sin(PITCH), c = Math.cos(PITCH);
  const along = z + CLEARANCE;
  const py = -c * along + s * y;
  const pz = s * along + c * y;
  const roll = rollDegrees * Math.PI / 180;
  // The axis passes through the dot AND the grip's cable exit. Its plan
  // projection follows the tangent; its elevation follows those two points.
  // Rodrigues rotation preserves both endpoints and the final wire approach.
  const ay = -c * LOCAL_ROLL_AXIS[2] + s * LOCAL_ROLL_AXIS[1];
  const az = s * LOCAL_ROLL_AXIS[2] + c * LOCAL_ROLL_AXIS[1];
  const dot = ay * py + az * pz;
  const cr = Math.cos(roll), sr = Math.sin(roll);
  const rx = x * cr + (ay * pz - az * py) * sr;
  const ry = py * cr + az * x * sr + ay * dot * (1 - cr);
  const rz = pz * cr - ay * x * sr + az * dot * (1 - cr);

  // The second axis runs through the dot and both port centers: the cap's
  // X diameter at CAP_TOP. Positive rotation about -X raises the grip.
  // Apply it to the whole pose, carrying the dot-to-grip axis with the gun.
  const holeRoll = holeRollDegrees * Math.PI / 180;
  const ch = Math.cos(holeRoll), sh = Math.sin(holeRoll);
  return [JOINT[0] + rx, ry * ch + rz * sh, JOINT[2] - ry * sh + rz * ch];
}
