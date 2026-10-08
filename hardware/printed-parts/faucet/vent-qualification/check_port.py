"""Native port, seal-wall and installed bowl-position witnesses.

Read the saved production tip STEP, not a rebuilt shell. Analytic witnesses use
the current source's native gland transforms and outlet cutter. This is a CAD
check, not an as-printed seal, discharge or installation measurement.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
FAUCET = HERE.parent
REPO = next(p for p in HERE.parents if (p / "hardware").is_dir() and (p / "tools").is_dir())
sys.path.insert(0, str(FAUCET))
sys.path.insert(0, str(FAUCET / "faucet-shell"))
sys.path.insert(0, str(REPO / "hardware" / "faucet-layout"))
import faucet_paths as paths
import vent_seals as seals
import faucet_shell as shell
import faucet_assembly as assembly

VOLUME_TOLERANCE_MM3 = 1e-5
AREA_TOLERANCE_MM2 = 1e-5


def _shape(value):
    return value.val() if hasattr(value, "val") else value


def _volume(shape) -> float:
    shape = _shape(shape)
    if not shape.isValid():
        raise ValueError("A native solid Boolean witness is invalid")
    volumes = [s.Volume() for s in shape.Solids()]
    if any(v < -VOLUME_TOLERANCE_MM3 for v in volumes):
        raise ValueError("A native solid Boolean witness has negative oriented volume")
    return sum(max(v, 0.0) for v in volumes)


def _area(shape) -> float:
    shape = _shape(shape)
    if not shape.isValid():
        raise ValueError("A native face Boolean witness is invalid")
    return sum(face.Area() for face in shape.Faces())


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _annulus(inner_radius: float, outer_radius: float, z: float, length: float):
    return cq.Workplane("XY", origin=(0, 0, z)).circle(outer_radius).circle(inner_radius).extrude(length)


def _floor_escape_strip():
    """Continuous independent 0.1 mm-wide downhill floor-to-outside corridor.

    A 0.002 mm station inset avoids tangency at the exact upstream cut edge.
    Travel follows the upstream gland plane's downward radial direction, so
    its clipping plane provides a sloped exit without removing seal stock.
    """
    p = paths
    sections = []
    _, xdir, tangent = p.station_plane(p.UPSTREAM_GLAND_S + p.GLAND_MID_SHIFT_S)
    for i in range(81):
        s = p.WET_START_S + 0.002 + (p.WET_END_S - p.WET_START_S - 0.004) * i / 80
        origin = p.station_point(s, n=p.SHELL_CENTER_N - p.CAVITY_RADIUS)
        plane = cq.Plane(origin=origin, xDir=xdir, normal=tangent)
        sections.append(cq.Workplane(plane).center(0, -1.2).rect(0.1, 2.4).val())
    return cq.Solid.makeLoft(sections, ruled=False)


def _conservative_wet_mouth():
    """Native constant-width chord mouth that the fluid model credits.

    The production flare must contain this face. Curved-face surface area is
    larger than the fluid model's center-floor projection and is not credited.
    """
    p = paths
    midpoint = p.PORT_START_S + p.PORT_LENGTH_S / 2
    angle = p.JOINT_ANGLE + midpoint / p.WATER_RADIUS
    origin = p.station_point(midpoint, n=p.SHELL_CENTER_N)
    normal = (0, -math.cos(angle), -math.sin(angle))
    plane = cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal)
    floor_radius = p.WATER_RADIUS + p.SHELL_CENTER_N - p.CAVITY_RADIUS
    length = 2 * floor_radius * math.sin(p.PORT_LENGTH_S / (2 * p.WATER_RADIUS))
    wire = shell._display_outline_wire(p.PORT_WIDTH, length, p.PORT_CORNER_R, 6, center_s=0)
    wire = wire.transformShape(plane.rG)
    prism = cq.Solid.extrudeLinear(wire, [], cq.Vector(*normal).multiply(24))
    mouth = _neck_surface(p.CAVITY_RADIUS).intersect(prism)
    return (mouth.intersect(_shape(shell._gland_halfspace(p.UPSTREAM_GLAND_S, seals.GLAND_LENGTH, 1)))
                 .intersect(_shape(shell._gland_halfspace(p.DOWNSTREAM_GLAND_S, 0, -1))))


def _neck_surface(radius: float):
    p = paths
    s0, s1 = p.PORT_START_S - 1.0, p.PORT_START_S + p.PORT_LENGTH_S + 1.0
    sweep = _shape(shell._round_cavity_segment(s0, s1, radius))
    torus = [face for face in sweep.Faces() if face.geomType() == "TORUS"]
    if len(torus) != 1:
        raise ValueError("The circular production neck must yield one analytic torus face")
    return torus[0]


def _bowl_forbidden(setback: float, hole_y: float, yaw_deg: float):
    """Rear of the bowl edge, after yaw about the accessory hole's center."""
    angle = math.radians(yaw_deg)
    rear = (math.sin(angle), math.cos(angle), 0.0)
    edge = (-setback * rear[0], hole_y - setback * rear[1], 0.0)
    plane = cq.Plane(origin=edge, xDir=(math.cos(angle), -math.sin(angle), 0), normal=rear)
    return cq.Workplane(plane).rect(1000, 1000).extrude(1000).val()


def assess(tip_step: Path, *, maximum_setback_mm: float = 50.8,
           maximum_yaw_deg: float = 10.0, credited_port_area_mm2: float | None = None):
    tip = _shape(cq.importers.importStep(str(tip_step)))
    if not tip.isValid() or len(tip.Solids()) != 1:
        raise ValueError("The saved tip STEP must contain one valid production solid")
    outlet = _shape(shell.build_vent_outlet())
    checks = {}
    walls = []
    seats = []
    epsilon = 0.0001
    for name, station in (("upstream", paths.UPSTREAM_GLAND_S),
                          ("downstream", paths.DOWNSTREAM_GLAND_S)):
        for region, inner, z, length in (
            ("flange_groove", seals.GROOVE_ID / 2, seals.KEEPER_LENGTH, seals.GROOVE_LENGTH),
            ("body_seat", seals.BODY_SEAT_ID / 2,
             seals.KEEPER_LENGTH + seals.GROOVE_LENGTH, seals.BODY_LENGTH),
        ):
            # Cover the full circumference and seat length with a nominal 2 mm
            # ring. Boundary insets avoid classifying coincident surfaces.
            witness = _shape(shell._gland_world(_annulus(
                inner + epsilon, inner + 2.0, z + epsilon, length - 2 * epsilon), station))
            missing = _volume(witness.cut(tip))
            walls.append({"gland": name, "region": region,
                          "required_radial_wall_mm": 2.0,
                          "witness_volume_mm3": _volume(witness),
                          "missing_from_saved_tip_mm3": missing})
            checks[f"{name}_{region}_full_2mm_wall"] = missing <= VOLUME_TOLERANCE_MM3
            seat = _shape(shell._gland_world(cq.Workplane("XY", origin=(0, 0, z))
                          .circle(inner).extrude(length), station))
            overlap = _volume(outlet.intersect(seat))
            seats.append({"gland": name, "region": region,
                          "outlet_cutter_intersection_mm3": overlap})
            checks[f"port_clear_of_{name}_{region}"] = overlap <= VOLUME_TOLERANCE_MM3

    strip = _floor_escape_strip()
    floor_blockage = _volume(strip.intersect(tip))
    checks["continuous_wet_floor_escape_corridor"] = floor_blockage <= VOLUME_TOLERANCE_MM3
    floor_radius = paths.WATER_RADIUS + paths.SHELL_CENTER_N - paths.CAVITY_RADIUS
    midpoint = paths.PORT_START_S + paths.PORT_LENGTH_S / 2
    chord = 2 * floor_radius * math.sin(paths.PORT_LENGTH_S / (2 * paths.WATER_RADIUS))
    floor_end_coords = [floor_radius * math.sin((s - midpoint) / paths.WATER_RADIUS)
                        for s in (paths.WET_START_S, paths.WET_END_S)]
    checks["exact_wet_floor_centres_within_chord_window"] = max(abs(v) for v in floor_end_coords) <= chord / 2 + 1e-7
    checks["minimum_port_profile_has_finite_flat_ends"] = paths.PORT_WIDTH > 2 * paths.PORT_CORNER_R
    conservative_mouth = _conservative_wet_mouth()
    unsupported_mouth = _area(conservative_mouth.cut(outlet))
    checks["outlet_contains_complete_conservative_wet_mouth"] = unsupported_mouth <= AREA_TOLERANCE_MM2

    # Full native curved opening faces, including rounded station ends and
    # actual side flare. The analytic torus faces avoid thin-solid subtraction.
    throats = []
    exterior = None
    for radius in (paths.CAVITY_RADIUS, 12.0, 12.5, 13.0, paths.SHELL_RADIUS):
        opening = _neck_surface(radius).intersect(outlet)
        native_area = _area(opening)
        throats.append({"neck_section_radius_mm": radius,
                        "native_open_face_area_mm2": native_area})
        if abs(radius - paths.SHELL_RADIUS) < 1e-9:
            exterior = opening
        if credited_port_area_mm2 is not None:
            checks[f"native_throat_R{radius:g}_above_credited_wet_area"] = native_area >= credited_port_area_mm2
    if exterior is None or _area(exterior) <= 0:
        raise ValueError("No exterior opening found in the native outlet cutter")
    saved_lip_blockage = _area(exterior.intersect(tip))
    checks["saved_tip_exterior_opening_is_cut"] = saved_lip_blockage <= AREA_TOLERANCE_MM2

    hole_y = assembly.countertop_hole_center_y
    bowl = []
    for yaw in (-maximum_yaw_deg, 0.0, maximum_yaw_deg):
        forbidden = _bowl_forbidden(maximum_setback_mm, hole_y, yaw)
        overlap = _area(exterior.intersect(forbidden))
        rotated = exterior.rotate((0, hole_y, 0), (0, hole_y, 1), yaw)
        bounds = rotated.BoundingBox()
        minimum_reach = hole_y - bounds.ymax
        bowl.append({"yaw_deg": yaw, "native_opening_in_counter_region_mm2": overlap,
                     "conservative_minimum_opening_reach_from_hole_mm": minimum_reach,
                     "margin_beyond_stated_bowl_edge_mm": minimum_reach - maximum_setback_mm})
        checks[f"entire_native_opening_over_bowl_yaw_{yaw:g}"] = (
            overlap <= AREA_TOLERANCE_MM2 and minimum_reach >= maximum_setback_mm - 0.0001)
    # For positive forward reach, forward projection is concave over ±10°;
    # each point's minimum on that interval is at an endpoint.
    checks["yaw_interval_has_positive_forward_reach"] = maximum_yaw_deg < 90 and min(
        row["conservative_minimum_opening_reach_from_hole_mm"] for row in bowl) > 0

    source_paths = [Path(__file__), FAUCET / "faucet_paths.py", FAUCET / "vent_seals.py",
                    FAUCET / "faucet-shell" / "faucet_shell.py",
                    REPO / "hardware" / "faucet-layout" / "faucet_assembly.py", tip_step]
    return {
        "schema": 1,
        "scope": "Saved production tip STEP with native full-circumference seal-wall witnesses, continuous bottom escape corridor, analytic torus opening faces and bowl halfspaces. Nominal CAD only; no physical seal, splash, clogging or hydraulic qualification.",
        "saved_tip_step": str(tip_step.relative_to(REPO)),
        "source_sha256": {str(p.relative_to(REPO)): _sha(p) for p in source_paths},
        "volume_tolerance_mm3": VOLUME_TOLERANCE_MM3,
        "area_tolerance_mm2": AREA_TOLERANCE_MM2,
        "checks": checks,
        "passed": all(checks.values()),
        "seal_wall_witnesses": walls,
        "outlet_seat_clearance": seats,
        "continuous_floor_escape": {
            "corridor_width_mm": 0.1, "station_inset_at_each_end_mm": 0.002,
            "corridor_downhill_travel_mm": 2.4,
            "travel_direction": "Downward radial direction of the upstream gland plane; constant negative Z without an uphill step",
            "saved_tip_blockage_mm3": floor_blockage,
            "exact_floor_endpoint_tangent_coordinates_mm": floor_end_coords,
            "minimum_port_profile_flat_end_width_mm": paths.PORT_WIDTH - 2 * paths.PORT_CORNER_R,
            "rule": "Open the complete lowest wet floor across the crown; the cavity needs no closed monotonic longitudinal floor.",
        },
        "native_throat_samples": throats,
        "native_conservative_wet_mouth_area_mm2": _area(conservative_mouth),
        "conservative_wet_mouth_outside_native_outlet_mm2": unsupported_mouth,
        "native_throat_scope": "Exact native torus-face intersections at the stated section radii. The entire port window includes keeper undercut reserve. These are not a measured discharge coefficient or a global minimum between sampled radii.",
        "credited_hydraulic_area_mm2": credited_port_area_mm2,
        "exterior_opening_saved_tip_blockage_mm2": saved_lip_blockage,
        "bowl_installation": {
            "maximum_hole_center_setback_behind_bowl_edge_mm": maximum_setback_mm,
            "maximum_yaw_deg": maximum_yaw_deg,
            "counter_hole_center_behind_shank_mm": hole_y,
            "rotation_rule": "Rotate the faucet relative to the accessory hole center; the bowl is the forward halfplane. No lateral bowl-width or curved corner envelope is inferred.",
            "native_continuous_opening_projections": bowl,
        },
        "physical_results": "Not recorded by this nominal CAD assessment",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--tip-step", type=Path, default=FAUCET / "faucet-shell" / "faucet-shell-tip.step")
    parser.add_argument("--hydraulic-report", type=Path)
    parser.add_argument("--output", type=Path, default=HERE / "port-native-check.json")
    args = parser.parse_args()
    credited = None
    if args.hydraulic_report:
        report = json.loads(args.hydraulic_report.read_text())
        credited = report["geometry"]["port_conservative_projected_wet_area_mm2"]
    result = assess(args.tip_step.resolve(), credited_port_area_mm2=credited)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "passed": result["passed"],
                      "failed_checks": [k for k, ok in result["checks"].items() if not ok]}))
    if not result["passed"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
