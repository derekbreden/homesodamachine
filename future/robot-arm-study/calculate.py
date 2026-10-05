"""Reproduce the single gun-positioner concept arithmetic, using the stdlib.

Run: python3 future/robot-arm-study/calculate.py > future/robot-arm-study/calculations.json
Nominal command spacing, static load scenarios and ideal geometry are not
measurements of loaded motion or optical accuracy. Axis centers are assumed
to intersect; physical gun/camera/cable/actuator envelopes are not modeled.
"""

from itertools import product
import json
import math
from pathlib import Path


G = 9.81
GUN_CABLE_MASS = 1.3118  # Reported measurement from the Rebot conversation.
SHELL_MOUNT_MASS = 0.250  # Unmeasured fabrication allowance.
ANGULAR_MOMENT_SCENARIO = 15.0  # Shaft/hub screening scenario, not a measured load.
VERTICAL_MOVING_MASS = 300.0 / G  # Screening mass equivalent; not a measured assembly mass.
LEAD = 0.002
MOTOR_STEPS = 200  # Full-step equivalents; driver pulse mode is separate.
BELT_RATIO = 4
LEVER = 0.150
NEUTRAL_ACTUATOR_LENGTH = 0.180
ANGLE_LIMIT_DEG = 20
SLIDE_HALF_TRAVEL = 0.085
TOOL_OFFSET = (0.200, 0.0, 0.04735)
NORMAL_FORCE_SCENARIO = 300.0
SCREW_EFFICIENCY = 0.20  # Assumed only, not a manufacturer rating.
BELT_EFFICIENCY = 0.90  # Assumed only, not a manufacturer rating.


def rotation_xyz(a, b, c):
    """Ideal intersecting-axis orientation Rz(c) Ry(b) Rx(a)."""
    ca, sa = math.cos(a), math.sin(a)
    cb, sb = math.cos(b), math.sin(b)
    cc, sc = math.cos(c), math.sin(c)
    return (
        (cc * cb, cc * sb * sa - sc * ca, cc * sb * ca + sc * sa),
        (sc * cb, sc * sb * sa + cc * ca, sc * sb * ca - cc * sa),
        (-sb, cb * sa, cb * ca),
    )


def rotate(rotation, vector):
    return tuple(sum(row[j] * vector[j] for j in range(3)) for row in rotation)


def dot_centered_translation(rotation, offset):
    rotated = rotate(rotation, offset)
    return tuple(offset[i] - rotated[i] for i in range(3))


def angular_actuator(angle):
    """Pivoted planar actuator A=(r,-L0), P=(r cos(theta),r sin(theta))."""
    r, l0 = LEVER, NEUTRAL_ACTUATOR_LENGTH
    dx, dy = r * (math.cos(angle) - 1), l0 + r * math.sin(angle)
    length = math.hypot(dx, dy)
    derivative = (l0 * r * math.cos(angle) + r * r * math.sin(angle)) / length
    base_articulation = math.atan2(dy, dx) - math.pi / 2
    lever_articulation = base_articulation - angle
    return length, derivative, base_articulation, lever_articulation


def sample_geometry():
    minimum = [math.inf] * 3
    maximum = [-math.inf] * 3
    worst_norm = 0.0
    count = 0
    angles = (range(-20, 21), range(-20, 11), range(-20, 21))
    for degrees in product(*angles):
        rotation = rotation_xyz(*(math.radians(value) for value in degrees))
        delta = dot_centered_translation(rotation, TOOL_OFFSET)
        for axis in range(3):
            minimum[axis] = min(minimum[axis], delta[axis])
            maximum[axis] = max(maximum[axis], delta[axis])
        worst_norm = max(worst_norm, math.sqrt(sum(x * x for x in delta)))
        count += 1
    return {
        "orientation_model": "Rz Ry Rx, ideal intersecting axes",
        "tool_vector_at_neutral_mm": [x * 1e3 for x in TOOL_OFFSET],
        "angular_limits_deg": {"yaw": [-20, 20], "pitch": [-20, 10], "roll": [-20, 20]},
        "sampling_spacing_deg": 1,
        "sampled_poses": count,
        "minimum_compensating_XYZ_mm": [x * 1e3 for x in minimum],
        "maximum_compensating_XYZ_mm": [x * 1e3 for x in maximum],
        "maximum_compensation_vector_norm_mm": worst_norm * 1e3,
        "symmetric_additional_dot_translation_each_axis_mm": [
            (SLIDE_HALF_TRAVEL - max(abs(minimum[i]), abs(maximum[i]))) * 1e3
            for i in range(3)
        ],
        "scope_limit": "Illustrative pose arithmetic with zero neutral orientation. The fabrication geometry owns its actual mounting transform and correlated reach. Does not establish physical clearance, actual tool transform, reachability under load or a 170 mm dot-translation range at every angle.",
    }


def budget_totals():
    materials = json.loads(Path(__file__).with_name("materials.json").read_text())
    totals = {}
    for group in ["positioner", "observation", "independent_reference", "optional_diagnostics"]:
        totals[group] = {
            bound: round(sum(row["quantity"] * row["unit_" + bound]
                             for row in materials[group]), 2)
            for bound in ["low", "high"]
        }
    for name, groups in [
        ("positioner_and_observation", ["positioner", "observation"]),
        ("positioner_observation_and_reference", ["positioner", "observation", "independent_reference"]),
    ]:
        totals[name] = {
            bound: round(sum(totals[group][bound] for group in groups), 2)
            for bound in ["low", "high"]
        }
    return totals


def main():
    nominal_step = LEAD / MOTOR_STEPS / BELT_RATIO
    payload = GUN_CABLE_MASS + SHELL_MOUNT_MASS
    angular_moment = ANGULAR_MOMENT_SCENARIO
    samples = [angular_actuator(math.radians(i / 10))
               for i in range(-ANGLE_LIMIT_DEG * 10, ANGLE_LIMIT_DEG * 10 + 1)]
    lengths = [p[0] for p in samples]
    derivatives = [p[1] for p in samples]
    smallest_derivative = min(derivatives)
    neutral = angular_actuator(0)
    max_angle_increment = nominal_step / smallest_derivative
    result = {
        "status": "Concept arithmetic, assumed static loads and ideal pose samples. Not physical-performance evidence.",
        "inputs": {
            "reported_gun_feed_4ft_umbilical_mass_kg": GUN_CABLE_MASS,
            "assumed_shell_mount_mass_kg": SHELL_MOUNT_MASS,
            "planned_gun_package_mass_kg": payload,
            "angular_shaft_hub_screening_moment_Nm": ANGULAR_MOMENT_SCENARIO,
            "assumed_vertical_moving_stack_mass_kg": VERTICAL_MOVING_MASS,
            "normal_axial_force_sizing_scenario_N": NORMAL_FORCE_SCENARIO,
            "assumed_screw_efficiency": SCREW_EFFICIENCY,
            "assumed_belt_efficiency": BELT_EFFICIENCY,
        },
        "nominal_commands": {
            "screw_lead_mm": LEAD * 1e3,
            "motor_full_steps_per_revolution": MOTOR_STEPS,
            "motor_to_screw_belt_ratio": BELT_RATIO,
            "linear_travel_um_per_full_step_equivalent": nominal_step * 1e6,
            "full_step_equivalents_for_nominal_0_5mm_move": 0.0005 / nominal_step,
            "angular_increment_at_neutral_arcsec": math.degrees(nominal_step / neutral[1]) * 3600,
            "maximum_angular_increment_arcsec_in_sampled_range": math.degrees(max_angle_increment) * 3600,
            "endpoint_increment_at_perpendicular_200mm_lever_neutral_um": 0.2 * nominal_step / neutral[1] * 1e6,
            "maximum_endpoint_increment_at_perpendicular_200mm_lever_um": 0.2 * max_angle_increment * 1e6,
            "scope_limit": "Nominal command spacing. Actual increments, friction, preload, reversal, settling and current effects must be observed; microstep settings do not establish attained resolution.",
        },
        "pivoted_angular_actuator": {
            "lever_radius_mm": LEVER * 1e3,
            "neutral_pivot_to_pivot_length_mm": NEUTRAL_ACTUATOR_LENGTH * 1e3,
            "angle_plus_minus_deg": ANGLE_LIMIT_DEG,
            "sample_spacing_deg": 0.1,
            "minimum_length_mm": min(lengths) * 1e3,
            "maximum_length_mm": max(lengths) * 1e3,
            "required_total_length_change_mm": (max(lengths) - min(lengths)) * 1e3,
            "stroke_below_neutral_mm": (min(lengths) - NEUTRAL_ACTUATOR_LENGTH) * 1e3,
            "stroke_above_neutral_mm": (max(lengths) - NEUTRAL_ACTUATOR_LENGTH) * 1e3,
            "minimum_dlength_dangle_mm_per_rad": smallest_derivative * 1e3,
            "max_base_hinge_articulation_deg": math.degrees(max(abs(p[2]) for p in samples)),
            "max_lever_hinge_articulation_deg": math.degrees(max(abs(p[3]) for p in samples)),
            "scope_limit": "Planar ideal geometry; excludes motor/belt/bearing/nut packages, hinge preload, interference and screw extension clearance.",
        },
        "load_scenarios": {
            "angular_output_moment_Nm": angular_moment,
            "angular_actuator_force_before_preload_friction_at_neutral_N": angular_moment / neutral[1],
            "max_angular_actuator_force_before_preload_friction_in_sampled_range_N": angular_moment / smallest_derivative,
            "vertical_gravity_force_N": VERTICAL_MOVING_MASS * G,
            "nominal_motor_torque_Nm_for_normal_force_scenario": NORMAL_FORCE_SCENARIO * LEAD / (2 * math.pi * SCREW_EFFICIENCY * BELT_RATIO * BELT_EFFICIENCY),
            "scope_limit": "Separate screening scenarios and assumed efficiencies. The governing fabrication requirements and measured actual loads accept the build. These calculations do not qualify motor duty, guide/bearing moments, screw buckling, jam forces, stiffness, retention or lifetime.",
        },
        "dot_centered_rotation": sample_geometry(),
        "materials_USD": budget_totals(),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
