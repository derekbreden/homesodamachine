"""Reproduce the robot-arm concept's arithmetic; this is not qualification.

Run: python3 future/robot-arm-study/calculate.py > future/robot-arm-study/calculations.json
Requires NumPy. Dimensions inside the model are SI. No dynamics, creep,
bearing-seat compliance, fatigue, motor torque curves or camera accuracy are
inferred. Stewart-platform checks sample vertices; they do not prove a
continuous workspace or include actuator, gun, cable or fixture envelopes.
"""

from itertools import product
import json
import math
from pathlib import Path

import numpy as np


G = 9.81
GUN_CABLE_MASS = 1.3118  # Reported measurement recovered from the Rebot session.
SHELL_MASS = 0.250  # Unmeasured shell/flange/coupler allowance.
PAYLOAD = GUN_CABLE_MASS + SHELL_MASS
L1, L2, WRIST_LENGTH = 0.180, 0.180, 0.040
TOOL_CG_OFFSET = 0.100  # Unknown; provisional distance beyond the flange.
UPPER_MASS, FOREARM_MASS, WRIST_MASS = 1.800, 1.650, 0.600
# Upper mass allows an elbow motor/structure; forearm allows the three wrist
# motors routed proximally. These remain assumed masses and midpoint CGs.
CABLE_MOMENT = 3.0  # Engineering disturbance scenario, NOT a measurement.
CARRIED_STAGE_CG_OFFSET = 0.040
FINE_MOVING_PLATE_MASS = 0.350  # Unmeasured; fixed motors are not on this plate.


def arm_torques(carried_stage_mass):
    reach = L1 + L2 + WRIST_LENGTH
    shoulder = G * (
        PAYLOAD * (reach + TOOL_CG_OFFSET)
        + carried_stage_mass * (reach + CARRIED_STAGE_CG_OFFSET)
        + UPPER_MASS * L1 / 2
        + FOREARM_MASS * (L1 + L2 / 2)
        + WRIST_MASS * reach
    ) + CABLE_MOMENT
    elbow = G * (
        PAYLOAD * (L2 + WRIST_LENGTH + TOOL_CG_OFFSET)
        + carried_stage_mass * (L2 + WRIST_LENGTH + CARRIED_STAGE_CG_OFFSET)
        + FOREARM_MASS * L2 / 2
        + WRIST_MASS * (L2 + WRIST_LENGTH)
    ) + CABLE_MOMENT
    wrist = G * (
        PAYLOAD * TOOL_CG_OFFSET
        + carried_stage_mass * CARRIED_STAGE_CG_OFFSET
    ) + CABLE_MOMENT
    return {
        "carried_stage_mass_kg": carried_stage_mass,
        "shoulder_Nm": shoulder,
        "elbow_Nm": elbow,
        "wrist_pitch_Nm": wrist,
    }


BASE_RADIUS, TOP_RADIUS, HEIGHT = 0.080, 0.055, 0.070
BASE_ANGLES = [-10, 10, 110, 130, 230, 250]
TOP_ANGLES = [310, 50, 70, 170, 190, 290]
ba, pa = np.deg2rad(BASE_ANGLES), np.deg2rad(TOP_ANGLES)
B = np.column_stack([
    BASE_RADIUS * np.cos(ba), BASE_RADIUS * np.sin(ba), np.zeros(6)
])
P = np.column_stack([
    TOP_RADIUS * np.cos(pa), TOP_RADIUS * np.sin(pa), np.zeros(6)
])
NEUTRAL_LEGS = P - B + np.array([0, 0, HEIGHT])
NEUTRAL_LENGTHS = np.linalg.norm(NEUTRAL_LEGS, axis=1)
NEUTRAL_U = NEUTRAL_LEGS / NEUTRAL_LENGTHS[:, None]
J = np.column_stack([NEUTRAL_U, np.cross(P, NEUTRAL_U)])
LEAD, MOTOR_STEPS, BELT_RATIO = 0.0005, 200, 4
STRUT_STEP = LEAD / MOTOR_STEPS / BELT_RATIO
SIGN_COMBINATIONS = np.array(list(product([-1, 1], repeat=6)))


def segment_distance(a, b, c, d):
    """Minimum distance between finite straight centerline segments."""
    u, v, w = b - a, d - c, a - c
    aa, bb, cc = float(u @ u), float(u @ v), float(v @ v)
    dd, ee = float(u @ w), float(v @ w)
    denom = aa * cc - bb * bb
    candidates = []
    if denom > 1e-18:
        s, t = (bb * ee - cc * dd) / denom, (aa * ee - bb * dd) / denom
        if 0 <= s <= 1 and 0 <= t <= 1:
            candidates.append(float(np.linalg.norm(w + s * u - t * v)))
    for s in [0.0, 1.0]:
        t = float(np.clip((ee + bb * s) / cc, 0, 1))
        candidates.append(float(np.linalg.norm(w + s * u - t * v)))
    for t in [0.0, 1.0]:
        s = float(np.clip((bb * t - dd) / aa, 0, 1))
        candidates.append(float(np.linalg.norm(w + s * u - t * v)))
    return min(candidates)


def rotation_xyz(a, b, c):
    ca, sa, cb, sb, cc, sc = (
        math.cos(a), math.sin(a), math.cos(b), math.sin(b), math.cos(c), math.sin(c)
    )
    rx = np.array([[1, 0, 0], [0, ca, -sa], [0, sa, ca]])
    ry = np.array([[cb, 0, sb], [0, 1, 0], [-sb, 0, cb]])
    rz = np.array([[cc, -sc, 0], [sc, cc, 0], [0, 0, 1]])
    return rz @ ry @ rx


def rounding_error(jacobian, tool_offset):
    """First-order error for all 64 correlated half-step rounding signs."""
    dq = np.linalg.solve(jacobian, SIGN_COMBINATIONS.T * STRUT_STEP / 2).T
    endpoints = dq[:, :3] + np.cross(dq[:, 3:], tool_offset)
    return float(np.max(np.linalg.norm(endpoints, axis=1)))


def assess_pose(translation, rotation, tool_offset):
    # Rotate about the tool point, rather than silently rotating about the plate.
    r = rotation_xyz(*rotation)
    center = np.array([0, 0, HEIGHT]) + translation + (np.eye(3) - r) @ tool_offset
    pr = P @ r.T
    top = pr + center
    legs = top - B
    lengths = np.linalg.norm(legs, axis=1)
    u = legs / lengths[:, None]
    jp = np.column_stack([u, np.cross(pr, u)])
    separation = min(
        segment_distance(B[i], top[i], B[j], top[j])
        for i in range(6) for j in range(i + 1, 6)
    )
    angle_base = np.arccos(np.clip(np.sum(u * NEUTRAL_U, axis=1), -1, 1))
    angle_top = np.arccos(np.clip(np.sum((u @ r) * NEUTRAL_U, axis=1), -1, 1))
    # Hypothetical 6 Nm resultant moment: gun gravity moment plus cable scenario.
    # Includes the moving plate's weight at its center, not arm or fixed motors.
    wrench_to_force = np.linalg.inv(jp.T)
    gravity = wrench_to_force @ np.array([
        0, 0, -(PAYLOAD + FINE_MOVING_PLATE_MASS) * G, 0, 0, 0
    ])
    any_moment_bound = np.max(
        np.abs(gravity) + 6 * np.linalg.norm(wrench_to_force[:, 3:], axis=1)
    )
    return {
        "centerline_separation_mm": separation * 1e3,
        "scaled_jacobian_condition": float(np.linalg.cond(
            np.column_stack([u, np.cross(pr, u) / 0.1])
        )),
        "one_sided_leg_stroke_mm": float(np.max(np.abs(lengths - NEUTRAL_LENGTHS))) * 1e3,
        "end_joint_direction_change_deg": float(np.rad2deg(
            max(np.max(angle_base), np.max(angle_top))
        )),
        "half_step_endpoint_rounding_um": rounding_error(jp, r @ tool_offset) * 1e6,
        "any_6Nm_moment_plus_gravity_leg_bound_N": float(any_moment_bound),
    }


def sampled_envelope(translation_mm, tool_offset):
    poses = [assess_pose(np.zeros(3), np.zeros(3), tool_offset)]
    for signs in SIGN_COMBINATIONS:
        poses.append(assess_pose(
            signs[:3] * translation_mm / 1e3,
            signs[3:] * math.radians(0.5), tool_offset
        ))
    return {
        "translation_about_tool_each_axis_plus_minus_mm": translation_mm,
        "rotation_about_tool_each_axis_plus_minus_deg": 0.5,
        "tool_offset_m": tool_offset.tolist(),
        "sampled_poses": len(poses),
        "min_centerline_separation_mm": min(p["centerline_separation_mm"] for p in poses),
        "max_scaled_jacobian_condition": max(p["scaled_jacobian_condition"] for p in poses),
        "max_one_sided_leg_stroke_mm": max(p["one_sided_leg_stroke_mm"] for p in poses),
        "max_end_joint_direction_change_deg": max(p["end_joint_direction_change_deg"] for p in poses),
        "max_half_step_endpoint_rounding_um": max(p["half_step_endpoint_rounding_um"] for p in poses),
        "max_any_6Nm_moment_plus_gravity_leg_bound_N": max(p["any_6Nm_moment_plus_gravity_leg_bound_N"] for p in poses),
    }


def budget_totals():
    materials = json.loads(Path(__file__).with_name("materials.json").read_text())
    result = {}
    for group in ["arm", "supported_fine_stage_increment", "observation"]:
        result[group] = {
            bound: round(sum(row["quantity"] * row["unit_" + bound]
                             for row in materials[group]), 2)
            for bound in ["low", "high"]
        }
    for name, groups in [
        ("arm_and_observation", ["arm", "observation"]),
        ("arm_supported_stage_and_observation", ["arm", "supported_fine_stage_increment", "observation"]),
    ]:
        result[name] = {
            bound: round(sum(result[group][bound] for group in groups), 2)
            for bound in ["low", "high"]
        }
    return result


def main():
    constraints = []
    for lever in [0.4, 0.5]:
        for tolerance in [10e-6, 5e-6]:
            constraints.append({
                "single_joint_lever_m": lever,
                "endpoint_tolerance_um": tolerance * 1e6,
                "angle_deg": math.degrees(tolerance / lever),
                "angle_arcsec": math.degrees(tolerance / lever) * 3600,
                "stiffness_Nm_per_rad_for_assumed_3Nm_change": CABLE_MOMENT * lever / tolerance,
            })
    compliance = []
    for stiffness in [1e6, 3e6, 1e7]:
        for torque in [3, 0.1]:
            dq = np.linalg.solve(J.T @ J * stiffness, np.array([0, 0, 0, torque, 0, 0]))
            error = dq[:3] + np.cross(dq[3:], np.array([0, 0, -0.2]))
            compliance.append({
                "assumed_assembled_leg_stiffness_N_per_um": stiffness / 1e6,
                "changed_pitch_moment_Nm": torque,
                "endpoint_deflection_um_at_200mm_tool": float(np.linalg.norm(error)) * 1e6,
            })
    neutral_forces = []
    for moment in [0, 3, 6]:
        f = np.linalg.solve(J.T, np.array([
            0, 0, -(PAYLOAD + FINE_MOVING_PLATE_MASS) * G, moment, 0, 0
        ]))
        neutral_forces.append({
            "pitch_moment_Nm": moment, "leg_forces_N": f.tolist(),
            "max_absolute_leg_force_before_preload_N": float(np.max(np.abs(f))),
        })
    result = {
        "status": "Illustrative concept arithmetic and finite geometry samples; not physical performance evidence.",
        "inputs": {
            "reported_gun_feed_4ft_umbilical_mass_kg": GUN_CABLE_MASS,
            "assumed_shell_flange_coupler_mass_kg": SHELL_MASS,
            "planned_payload_kg": PAYLOAD,
            "assumed_tool_cg_beyond_flange_m": TOOL_CG_OFFSET,
            "assumed_upper_forearm_wrist_mass_kg": [UPPER_MASS, FOREARM_MASS, WRIST_MASS],
            "assumed_link_link_wrist_lengths_m": [L1, L2, WRIST_LENGTH],
            "assumed_cable_moment_Nm": CABLE_MOMENT,
            "assumed_carried_trim_cg_beyond_flange_m": CARRIED_STAGE_CG_OFFSET,
            "assumed_fine_moving_plate_mass_kg": FINE_MOVING_PLATE_MASS,
        },
        "horizontal_static_arm_torques": [arm_torques(m) for m in [0, 1.5, 2.5, 3.5]],
        "single_joint_constraints": constraints,
        "direct_output_one_count_at_400mm_um": {
            str(bits): 0.4 * 2 * math.pi / 2**bits * 1e6 for bits in [14, 16, 18, 20]
        },
        "25_to_1_motor_command_scale_at_400mm_um": {
            "1_8_degree_full_step": 0.4 * math.radians(1.8 / 25) * 1e6,
            "one_sixteenth_microstep_nominal": 0.4 * math.radians(1.8 / 25 / 16) * 1e6,
        },
        "unqualified_drive_sizing_screen": {
            "assumed_belt_efficiency": 0.85, "assumed_motor_derating_factor": 0.5,
            "NEMA23_2_4Nm_times_25_times_factors_Nm": 2.4 * 25 * 0.85 * 0.5,
            "NEMA17_0_59Nm_times_25_times_factors_Nm": 0.59 * 25 * 0.85 * 0.5,
        },
        "fine_stage": {
            "base_top_radii_height_mm": [BASE_RADIUS * 1e3, TOP_RADIUS * 1e3, HEIGHT * 1e3],
            "base_angles_deg": BASE_ANGLES, "top_angles_deg": TOP_ANGLES,
            "neutral_leg_lengths_mm": (NEUTRAL_LENGTHS * 1e3).tolist(),
            "neutral_scaled_jacobian_condition_100mm": float(np.linalg.cond(
                np.column_stack([NEUTRAL_U, np.cross(P, NEUTRAL_U) / 0.1])
            )),
            "screw_lead_mm": LEAD * 1e3, "motor_steps_per_rev": MOTOR_STEPS,
            "motor_to_screw_belt_ratio": BELT_RATIO,
            "nominal_full_step_strut_travel_um": STRUT_STEP * 1e6,
            "neutral_half_step_rounding_at_200mm_um": rounding_error(J, np.array([0, 0, -0.2])) * 1e6,
            "neutral_forces_before_preload": neutral_forces,
            "nominal_motor_Nm_for_150N_leg_30pct_screw_90pct_belt_efficiency": 150 * LEAD / (2 * math.pi * 0.3) / BELT_RATIO / 0.9,
            "sampled_tool_pose_envelopes": [
                sampled_envelope(tr, offset)
                for tr in [1, 2]
                for offset in [np.array([0, 0, -0.2]), np.array([0.2, 0, 0])]
            ],
            "assumed_stiffness_compliance": compliance,
            "scope_limit": "First-order Jacobian rounding/compliance; finite centerline samples exclude physical packages and continuous pose clearance. Thread error, friction, flexure stress/fatigue, bearing/support compliance and uncertainty are unqualified.",
        },
        "thermal_scale_for_1C_um": {
            "400mm_aluminum_assumed_23ppm_per_C": 0.4 * 23e-6 * 1e6,
            "100mm_steel_assumed_12ppm_per_C": 0.1 * 12e-6 * 1e6,
        },
        "materials_USD": budget_totals(),
    }
    print(json.dumps(result, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
