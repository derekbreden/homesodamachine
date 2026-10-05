"""Nominal screw and dot-pivot geometry. Cameras determine attained pose."""
import math
import json
from pathlib import Path

GEOMETRY_PATH = Path(__file__).resolve().parents[3] / "hardware/printed-parts/fixtures/gun-positioner/geometry-check.json"
GEOMETRY = json.loads(GEOMETRY_PATH.read_text())
COUNTS_PER_MM = int(GEOMETRY["nominal_motion"]["sixteen_microstep_command_pulses_per_mm"])
AXES = ("X", "Y", "Z", "U", "V", "W")
RADIUS_MM = GEOMETRY["angular_actuator"]["r_mm"]
NEUTRAL_LENGTH_MM = GEOMETRY["angular_actuator"]["L0_mm"]
ANGULAR_SOFT = [GEOMETRY["angular_limits_deg"].get("soft_by_axis", {}).get(name, GEOMETRY["angular_limits_deg"]["soft"])
                for name in ("yaw", "pitch", "roll")]

def angle_limits(axis=None):
    if axis is None: return GEOMETRY["angular_limits_deg"]["soft"]
    index = AXES.index(axis.upper()) - 3 if isinstance(axis, str) else axis
    if not 0 <= index < 3: raise ValueError("Angular axis must be U/V/W")
    return ANGULAR_SOFT[index]

def actuator_length(angle_degrees, radius_mm=RADIUS_MM, neutral_length_mm=NEUTRAL_LENGTH_MM, axis=None):
    lo, hi = angle_limits(axis)
    if not math.isfinite(angle_degrees) or not lo <= angle_degrees <= hi:
        raise ValueError(f"Angular target must lie within {lo}..{hi}° for this axis")
    a = math.radians(angle_degrees)
    return math.sqrt(neutral_length_mm**2 + 2 * neutral_length_mm * radius_mm * math.sin(a)
                     + 2 * radius_mm**2 * (1 - math.cos(a)))

def actuator_angle(length_mm, radius_mm=RADIUS_MM, neutral_length_mm=NEUTRAL_LENGTH_MM, axis=None):
    lo, hi = angle_limits(axis)
    if not actuator_length(lo, radius_mm, neutral_length_mm, axis) <= length_mm <= actuator_length(hi, radius_mm, neutral_length_mm, axis):
        raise ValueError("Screw extension outside the angular soft envelope")
    for _ in range(70):
        mid = (lo + hi) / 2
        if actuator_length(mid, radius_mm, neutral_length_mm) < length_mm:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2

SOFT_MIN = ([math.ceil(GEOMETRY["linear_limits_mm"]["soft"][0] * COUNTS_PER_MM)] * 3 +
            [math.ceil((actuator_length(v[0], axis=i) - NEUTRAL_LENGTH_MM) * COUNTS_PER_MM) for i, v in enumerate(ANGULAR_SOFT)])
SOFT_MAX = ([math.floor(GEOMETRY["linear_limits_mm"]["soft"][1] * COUNTS_PER_MM)] * 3 +
            [math.floor((actuator_length(v[1], axis=i) - NEUTRAL_LENGTH_MM) * COUNTS_PER_MM) for i, v in enumerate(ANGULAR_SOFT)])

def mm_to_count(mm):
    if not math.isfinite(mm):
        raise ValueError("Finite displacement required")
    return round(mm * COUNTS_PER_MM)

def pose_to_counts(pose, radius_mm=RADIUS_MM, neutral_length_mm=NEUTRAL_LENGTH_MM):
    if len(pose) != 6 or not all(math.isfinite(v) for v in pose):
        raise ValueError("Six finite nominal pose coordinates required")
    count = [mm_to_count(v) for v in pose[:3]]
    count += [max(SOFT_MIN[i + 3], min(SOFT_MAX[i + 3],
                mm_to_count(actuator_length(v, radius_mm, neutral_length_mm, i) - neutral_length_mm)))
              for i, v in enumerate(pose[3:])]
    if any(not lo <= v <= hi for v, lo, hi in zip(count, SOFT_MIN, SOFT_MAX)):
        raise ValueError("Nominal target outside controller soft limits")
    return count

def matmul(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)] for i in range(3)]

def rotation(yaw_degrees, pitch_degrees, roll_degrees):
    z, y, x = map(math.radians, (yaw_degrees, pitch_degrees, roll_degrees))
    cz, sz, cy, sy, cx, sx = math.cos(z), math.sin(z), math.cos(y), math.sin(y), math.cos(x), math.sin(x)
    rz = [[cz, -sz, 0], [sz, cz, 0], [0, 0, 1]]
    ry = [[cy, 0, sy], [0, 1, 0], [-sy, 0, cy]]
    rx = [[1, 0, 0], [0, cx, -sx], [0, sx, cx]]
    return matmul(matmul(rz, ry), rx)

def dot_rotation(current_pose, new_angles, tool_vector_mm, neutral_angles=None):
    """Hold a nominal dot while changing local clevis angles, using a measured tool vector.

    tool_vector_mm is from common gimbal center to dot in the gun's local frame.
    neutral_angles are mounting orientation, distinct from each screw's zero.
    Non-coincident calibrated axes require a complete fitted transform instead.
    """
    if neutral_angles is None:
        neutral_angles = GEOMETRY["tool_proxy"]["orientation_deg"]
    if len(current_pose) != 6 or len(new_angles) != 3 or len(tool_vector_mm) != 3:
        raise ValueError("Expected pose6, angles3 and measured tool-vector3")
    if not all(math.isfinite(v) for v in (*current_pose, *new_angles, *tool_vector_mm, *neutral_angles)):
        raise ValueError("Finite geometry required")
    before = rotation(*(a + n for a, n in zip(current_pose[3:], neutral_angles)))
    after = rotation(*(a + n for a, n in zip(new_angles, neutral_angles)))
    translation = [current_pose[i] + sum((before[i][j] - after[i][j]) * tool_vector_mm[j]
                                        for j in range(3)) for i in range(3)]
    result = translation + list(new_angles)
    pose_to_counts(result) # Reject out-of-envelope compensation.
    return result

def split_target(current_counts, target_counts, max_jog_counts=640):
    """Generate bounded, coordinated actuator segments; interpolate count coordinates."""
    if len(current_counts) != 6 or len(target_counts) != 6:
        raise ValueError("Six count coordinates required")
    if any(not lo <= v <= hi for v, lo, hi in zip(target_counts, SOFT_MIN, SOFT_MAX)):
        raise ValueError("Target outside soft limits")
    delta = [b - a for a, b in zip(current_counts, target_counts)]
    pieces = max(1, math.ceil(max(map(abs, delta)) / max_jog_counts))
    prior = list(current_counts)
    for part in range(1, pieces + 1):
        point = [a + round(d * part / pieces) for a, d in zip(current_counts, delta)]
        step = [b - a for a, b in zip(prior, point)]
        if any(step):
            yield step
        prior = point
