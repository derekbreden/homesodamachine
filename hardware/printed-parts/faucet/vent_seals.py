"""ASSE vent-cavity bungs, local gland geometry and factory insertion tool.

Local axes are X lateral, Y outward relative to the shell centre, and Z
downstream tangent. Tube coordinate tables use N relative to the soda tube;
CAD solids subtract SHELL_CENTER_N. Gland Z=0 is its upstream mouth;
the free bung prints flange-down at Z=0. All dimensions are millimetres.
No shell import is made: the shell places these helpers in its curved frame.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import sys
from pathlib import Path

import cadquery as cq
import faucet_paths as _paths

SODA_OD = _paths.WATER_OD
FLAVOR_OD = _paths.FLAVOR_OD
DRAIN_OD = _paths.DRAIN_OD
SEAL_WEB = _paths.SEAL_WEB
SHELL_CENTER_N = _paths.SHELL_CENTER_N
NECK_OD = 2 * _paths.SHELL_RADIUS
WATER_BEND_RADIUS = _paths.WATER_RADIUS

DRAIN_N = (SODA_OD + DRAIN_OD) / 2.0 + SEAL_WEB
_sf = (SODA_OD + FLAVOR_OD) / 2.0 + SEAL_WEB
_df = (DRAIN_OD + FLAVOR_OD) / 2.0 + SEAL_WEB
FLAVOR_N = (_sf ** 2 - _df ** 2 + DRAIN_N ** 2) / (2 * DRAIN_N)
FLAVOR_X = math.sqrt(_sf ** 2 - FLAVOR_N ** 2)
WIRE_N = DRAIN_N + DRAIN_OD / 2.0 + SEAL_WEB + 0.65
WIRE_X = (-3.3, -1.1, 1.1, 3.3)
WIRE_BORE = 1.05
TUBE_DIAMETRIC_INTERFERENCE = 0.30
BORE_LEAD_RADIAL = 0.10
BORE_LEAD_DEPTH = 0.20

BODY_OD = 22.4
BODY_LENGTH = 4.0
FLANGE_OD = 23.0
FLANGE_LENGTH = 0.8
BUNG_LENGTH = BODY_LENGTH + FLANGE_LENGTH
KEEPER_ID = 22.0
KEEPER_LENGTH = 1.2
GROOVE_ID = 22.8
GROOVE_LENGTH = 0.9
BODY_SEAT_ID = 22.0
STOP_ID = 20.0
UPSTREAM_STOP_ID = 22.0
STOP_LENGTH = 1.2
KEEPER_LEAD_RADIAL = 0.30
KEEPER_LEAD_LENGTH = 0.30
GLAND_LENGTH = KEEPER_LENGTH + GROOVE_LENGTH + BODY_LENGTH + STOP_LENGTH
BUNG_SEATED_Z = KEEPER_LENGTH + GROOVE_LENGTH - FLANGE_LENGTH
BODY_MID_Z = KEEPER_LENGTH + GROOVE_LENGTH + BODY_LENGTH / 2

TOOL_OD = 21.5
TOOL_ID = 19.7
TOOL_SLOT_WIDTH = 19.0
TOOL_ARC_LENGTH = 95.0  # measured along the soda path, including the open socket
TOOL_HANDLE_OD = 32.0
TOOL_HANDLE_LENGTH = 4.0
STL_LINEAR_TOLERANCE = 0.005
STL_ANGULAR_TOLERANCE = 0.04

_HERE = Path(__file__).resolve().parent
OUTPUT = _HERE / "asse-vent-seals"


def tube_centres(upstream: bool = True) -> tuple[tuple[str, float, float, float], ...]:
    """Name, X, N and actual nominal OD at either constant-pack seal station."""
    tubes = (("S", 0.0, 0.0, SODA_OD),
             ("F1", -FLAVOR_X, FLAVOR_N, FLAVOR_OD),
             ("F2", FLAVOR_X, FLAVOR_N, FLAVOR_OD))
    return tubes + (("D", 0.0, DRAIN_N, DRAIN_OD),) if upstream else tubes


def bore_centres(upstream: bool = True) -> tuple[tuple[str, float, float, float], ...]:
    tubes = tuple((name, x, n, od - TUBE_DIAMETRIC_INTERFERENCE)
                  for name, x, n, od in tube_centres(upstream))
    return tubes + tuple((f"wire-{i + 1}", x, WIRE_N, WIRE_BORE)
                         for i, x in enumerate(WIRE_X))


def _cylinder(diameter: float, length: float, z: float = 0.0,
              centre_n: float = 0.0) -> cq.Workplane:
    return (cq.Workplane("XY", origin=(0, 0, z))
            .center(0, centre_n).circle(diameter / 2).extrude(length))


def build_bung(upstream: bool = True) -> cq.Workplane:
    """Single unslit TPU body; the downstream version has no drain aperture."""
    bung = _cylinder(FLANGE_OD, FLANGE_LENGTH).union(
        _cylinder(BODY_OD, BODY_LENGTH, FLANGE_LENGTH))
    for _, x, n, diameter in bore_centres(upstream):
        n -= SHELL_CENTER_N
        radius = diameter / 2
        bore = (cq.Workplane("XY", origin=(x, n, -0.01))
                .circle(radius).extrude(BUNG_LENGTH + 0.02))
        lower = cq.Solid.makeCone(radius + BORE_LEAD_RADIAL, radius,
                                  BORE_LEAD_DEPTH,
                                  cq.Vector(x, n, 0), cq.Vector(0, 0, 1))
        upper = cq.Solid.makeCone(radius, radius + BORE_LEAD_RADIAL,
                                  BORE_LEAD_DEPTH,
                                  cq.Vector(x, n, BUNG_LENGTH - BORE_LEAD_DEPTH),
                                  cq.Vector(0, 0, 1))
        bung = bung.cut(bore).cut(lower).cut(upper)
    return bung.clean()


def build_seated_bung(upstream: bool = True) -> cq.Workplane:
    """Undeformed inspection shape located against the distal gland backstop."""
    return build_bung(upstream).translate((0, 0, BUNG_SEATED_Z))


def _curved_bore(x: float, n: float, diameter: float,
                 z0: float, z1: float) -> cq.Workplane:
    radius = WATER_BEND_RADIUS + n
    shell_r = WATER_BEND_RADIUS + SHELL_CENTER_N

    def point(z: float) -> tuple[float, float, float]:
        dz = z - BODY_MID_Z
        return (x, math.sqrt(radius * radius - dz * dz) - shell_r, z)

    start = point(z0)
    alpha = math.asin((z0 - BODY_MID_Z) / radius)
    plane = cq.Plane(origin=start, xDir=(1, 0, 0),
                     normal=(0, -math.sin(alpha), math.cos(alpha)))
    edge = cq.Edge.makeThreePointArc(cq.Vector(*start),
                                     cq.Vector(*point((z0 + z1) / 2)),
                                     cq.Vector(*point(z1)))
    path = cq.Workplane("XY").newObject([cq.Wire.assembleEdges([edge])])
    return cq.Workplane(plane).circle(diameter / 2).sweep(path)


def build_installed_bung(upstream: bool = True, wire_od: float = 1.3) -> cq.Workplane:
    """Seated contact envelope for assembly/clearance, not an FEA solution.

    Its OD equals the hard seat/groove. Actual tube-OD bores follow the
    curved paths through the body-midpoint plane. Use build_bung for prints.
    """
    body = _cylinder(GROOVE_ID, FLANGE_LENGTH, BUNG_SEATED_Z).union(
        _cylinder(BODY_SEAT_ID, BODY_LENGTH, BUNG_SEATED_Z + FLANGE_LENGTH))
    for _, x, n, od in tube_centres(upstream):
        body = body.cut(_curved_bore(x, n, od, BUNG_SEATED_Z - 0.10,
                                    BUNG_SEATED_Z + BUNG_LENGTH + 0.10))
    for x in WIRE_X:
        body = body.cut(_curved_bore(x, WIRE_N, wire_od, BUNG_SEATED_Z - 0.10,
                                    BUNG_SEATED_Z + BUNG_LENGTH + 0.10))
    return body.clean()


def build_gland_cutter(upstream: bool = True) -> cq.Workplane:
    """Planar-pocket cutter: keeper, captured flange groove, body seat, stop.

    Cut this from solid shell stock; do not union it with a pre-existing full
    Ø23 cavity cutter through this axial interval, which would erase the lips.
    The upstream backstop opens to Ø22 so the perimeter tool and compressed
    distal bung can pass. The captured flange locates that bung axially.
    """
    keeper = _cylinder(KEEPER_ID, KEEPER_LENGTH)
    lead = cq.Solid.makeCone(KEEPER_ID / 2 + KEEPER_LEAD_RADIAL,
                             KEEPER_ID / 2, KEEPER_LEAD_LENGTH,
                             cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))
    groove_z = KEEPER_LENGTH
    body_z = groove_z + GROOVE_LENGTH
    stop_z = body_z + BODY_LENGTH
    return (keeper.union(lead)
            .union(_cylinder(GROOVE_ID, GROOVE_LENGTH, groove_z))
            .union(_cylinder(BODY_SEAT_ID, BODY_LENGTH, body_z))
            .union(_cylinder(UPSTREAM_STOP_ID if upstream else STOP_ID,
                             STOP_LENGTH, stop_z)).clean())


def build_gland_stock(upstream: bool = True) -> cq.Workplane:
    """Complete rigid annular keeper/seat/backstop for a nominal Ø27 neck.

    Its outer envelope is deliberately planar; intersect with the real neck
    before union. The shell must verify its actual curved minimum wall.
    """
    return _cylinder(NECK_OD, GLAND_LENGTH).cut(build_gland_cutter(upstream)).clean()


def _tool_sketch(diameter: float) -> cq.Sketch:
    # The wide, open +N slot lets the entire upstream bundle leave the tool
    # once the curved sleeve has been withdrawn through the joint entrance.
    return (cq.Sketch().circle(diameter / 2)
            .circle(TOOL_ID / 2, mode="s")
            .reset().push([(0, diameter / 2)])
            .rect(TOOL_SLOT_WIDTH, diameter, mode="s").clean())


def build_perimeter_tool(radius: float = WATER_BEND_RADIUS) -> cq.Workplane:
    """Slotted curved pusher in the same local midpoint-aligned gland frame.

    Its travel corresponds to the neutral soda path from -95 to 0 mm.
    Its arc centre is (0,-(radius+SHELL_CENTER_N),BODY_MID_Z). The leading
    bearing face is clipped flat at Z=BUNG_SEATED_Z, against the flange.
    Rotate about the actual neck centre; placing its whole curve on a
    translated flange-tangent frame would displace the arc by 2.8 mm.
    """
    phi = TOOL_ARC_LENGTH / radius
    shell_radius = radius + SHELL_CENTER_N

    def point(angle: float) -> tuple[float, float, float]:
        return (0.0, shell_radius * (math.cos(angle) - 1),
                BODY_MID_Z + shell_radius * math.sin(angle))

    start_angle = -phi
    start = point(start_angle)
    plane = cq.Plane(origin=start, xDir=(1, 0, 0),
                     normal=(0, -math.sin(start_angle), math.cos(start_angle)))
    arc = cq.Edge.makeThreePointArc(cq.Vector(*start),
                                    cq.Vector(*point(-phi / 2)), cq.Vector(0, 0, BODY_MID_Z))
    path = cq.Workplane("XY").newObject([cq.Wire.assembleEdges([arc])])
    sleeve = cq.Workplane(plane).placeSketch(_tool_sketch(TOOL_OD)).sweep(path)
    handle = (cq.Workplane(plane).placeSketch(_tool_sketch(TOOL_HANDLE_OD))
              .extrude(-TOOL_HANDLE_LENGTH))
    assembled = sleeve.union(handle)
    below_face = (cq.Workplane("XY", origin=(0, 0, BUNG_SEATED_Z - 200))
                  .box(200, 200, 200, centered=(True, True, False)))
    return assembled.intersect(below_face).clean()


def build_perimeter_tool_print(radius: float = WATER_BEND_RADIUS) -> cq.Workplane:
    """Handle-flat bed pose; the long +N opening gives full support access."""
    phi = TOOL_ARC_LENGTH / radius
    tool = build_perimeter_tool(radius).rotate((0, 0, 0), (1, 0, 0), math.degrees(phi))
    return tool.translate((0, 0, -tool.val().BoundingBox().zmin))


def check_geometry() -> dict:
    """Application checks on distinct sealing interfaces and assembly access."""
    pair_webs = {}
    holes = bore_centres(True)
    for i, (a, ax, an, ad) in enumerate(holes):
        for b, bx, bn, bd in holes[i + 1:]:
            gap = math.hypot(ax - bx, an - bn) - (ad + bd) / 2
            pair_webs[f"{a}:{b}"] = gap
    minimum_web = min(pair_webs.values())
    actual_tube_reach = max(math.hypot(x, n - SHELL_CENTER_N) + od / 2
                            for _, x, n, od in tube_centres(True))
    wire_reach = max(math.hypot(x, WIRE_N - SHELL_CENTER_N) + 1.3 / 2
                    for x in WIRE_X)
    minimum_face_web = minimum_web - 2 * BORE_LEAD_RADIAL
    assert actual_tube_reach < STOP_ID / 2
    assert wire_reach < STOP_ID / 2
    bundle_width = 2 * (FLAVOR_X + FLAVOR_OD / 2)
    shell_r = WATER_BEND_RADIUS + SHELL_CENTER_N
    floor_r = shell_r - _paths.CAVITY_RADIUS
    keeper_edge_clearance = (shell_r-TOOL_OD/2)-math.hypot(
        shell_r-KEEPER_ID/2,BODY_MID_Z-KEEPER_LEAD_LENGTH)
    midpoint_offset = BODY_MID_Z * WATER_BEND_RADIUS / shell_r
    body_deviation = {
        name: WATER_BEND_RADIUS + n - math.sqrt(
            (WATER_BEND_RADIUS + n) ** 2 - (BODY_LENGTH / 2) ** 2)
        for name, n in (("S", 0.0), ("F", FLAVOR_N),
                        ("D", DRAIN_N), ("wire", WIRE_N))
    }
    groove_far_z = BODY_MID_Z - KEEPER_LENGTH
    crown_wall = shell_r + NECK_OD / 2 - math.hypot(
        shell_r + GROOVE_ID / 2, groove_far_z)
    gland_volume = math.pi / 4 * (
        KEEPER_ID ** 2 * KEEPER_LENGTH + GROOVE_ID ** 2 * GROOVE_LENGTH
        + BODY_SEAT_ID ** 2 * BODY_LENGTH + UPSTREAM_STOP_ID ** 2 * STOP_LENGTH)
    occupied_area = math.pi / 4 * (
        SODA_OD ** 2 + 2 * FLAVOR_OD ** 2 + DRAIN_OD ** 2 + 4 * 1.3 ** 2)
    displacement_space = gland_volume - occupied_area * GLAND_LENGTH
    free_volume = math.pi / 4 * (FLANGE_OD ** 2 * FLANGE_LENGTH + BODY_OD ** 2 * BODY_LENGTH)
    for _, _, _, d in holes:
        free_volume -= math.pi / 4 * d * d * BUNG_LENGTH
        free_volume -= 2 * math.pi * BORE_LEAD_DEPTH * (
            d / 2 * BORE_LEAD_RADIAL + BORE_LEAD_RADIAL ** 2 / 3)
    body_space = math.pi / 4 * (
        GROOVE_ID ** 2 * GROOVE_LENGTH + BODY_SEAT_ID ** 2 * BODY_LENGTH
        ) - occupied_area * (GROOVE_LENGTH + BODY_LENGTH)
    return {
        "minimum_uninstalled_web_mm": minimum_web,
        "minimum_web_at_bore_leads_mm": minimum_face_web,
        "minimum_nominal_installed_tube_web_mm": SEAL_WEB,
        "nominal_tube_web_compression_fraction":
            TUBE_DIAMETRIC_INTERFERENCE / (SEAL_WEB + TUBE_DIAMETRIC_INTERFERENCE),
        "tube_reach_from_shell_center_mm": actual_tube_reach,
        "wire_reach_at_maximum_stated_envelope_mm": wire_reach,
        "stop_to_nominal_tube_clearance_mm": STOP_ID / 2 - actual_tube_reach,
        "body_radial_interference_mm": (BODY_OD - BODY_SEAT_ID) / 2,
        "flange_radial_interference_mm": (FLANGE_OD - GROOVE_ID) / 2,
        "rigid_pusher_to_keeper_radial_clearance_mm": (KEEPER_ID - TOOL_OD) / 2,
        "minimum_pusher_keeper_edge_clearance_over_rotation_mm":keeper_edge_clearance,
        "pusher_inner_to_nominal_tube_clearance_mm": TOOL_ID / 2 - actual_tube_reach,
        "pusher_slot_to_nominal_bundle_width_clearance_mm": TOOL_SLOT_WIDTH - bundle_width,
        "planar_groove_wall_mm": (NECK_OD - GROOVE_ID) / 2,
        "free_bung_gland_body_axial_fit_mm": BODY_LENGTH,
        "flange_groove_axial_float_mm": GROOVE_LENGTH - FLANGE_LENGTH,
        "upstream_flange_capture_radial_overlap_mm":
            (GROOVE_ID-max(KEEPER_ID,BODY_SEAT_ID)) / 2,
        "planar_gland_alignment": {
            "local_z_at_body_midpoint_mm": BODY_MID_Z,
            "body_midpoint_arc_station_offset_mm": midpoint_offset,
            "rule": "Align local Z=4.1 to the station at nominal_gland_s+offset; set local origin4.1 mm backward along its tangent. Clip the round cavity with actual planar mouth/stop faces.",
            "maximum_tube_centre_deviation_in_body_mm": body_deviation,
            "minimum_nominal_tube_radial_interference_after_curvature_mm":
                TUBE_DIAMETRIC_INTERFERENCE / 2 - max(
                    body_deviation[name] for name in ("S", "F", "D")),
            "analytical_minimum_groove_crown_wall_mm": crown_wall,
            "upstream_backstop_plane_floor_station_mm":
                _paths.UPSTREAM_GLAND_S + midpoint_offset + WATER_BEND_RADIUS * math.asin(
                    (GLAND_LENGTH - BODY_MID_Z) / floor_r),
            "downstream_keeper_plane_floor_station_mm":
                _paths.DOWNSTREAM_GLAND_S + midpoint_offset + WATER_BEND_RADIUS * math.asin(
                    -BODY_MID_Z / floor_r),
        },
        "elastomer_displacement_budget": {
            "method": "Straight maximum-wire-envelope volume budget; conservative because it excludes the extra keeper lead-in volume. Actual curved tubes and deformation are separate checks.",
            "free_upstream_bung_volume_mm3": free_volume,
            "body_and_groove_available_after_tubes_mm3": body_space,
            "minimum_axial_bulge_volume_mm3": max(0, free_volume - body_space),
            "keeper_and_backstop_opening_displacement_space_mm3": displacement_space - body_space,
            "complete_gland_available_after_tubes_mm3": displacement_space,
            "complete_gland_nominal_fill_fraction": free_volume / displacement_space,
            "rule": "Leave keeper/backstop openings clear for axial rubber bulging. No solid clamp plate across the bung faces.",
        },
        "scope": "Nominal free CAD dimensions. Elastomer deformation, as-printed bore size, cable jackets, tube extrusion variation, shell curved-wall reserve, assembly load, water containment and aging need separate readings.",
        "passed": True,
    }


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    # This independent three-part generator must not supersede the shell build.
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    hardware = next(p for p in Path(__file__).resolve().parents if p.name == "hardware")
    sys.path.insert(0, str(hardware / "scripts"))
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, M_TPU_BLACK, one_body
    import trimesh

    generator_digest = _sha(Path(__file__))
    path_digest = _sha(Path(_paths.__file__))
    OUTPUT.mkdir(parents=True, exist_ok=True)
    parts = (
        ("asse-vent-upstream-bung", build_bung(True), "Bambu TPU 85A", M_TPU_BLACK),
        ("asse-vent-downstream-bung", build_bung(False), "Bambu TPU 85A", M_TPU_BLACK),
        ("asse-vent-perimeter-tool", build_perimeter_tool_print(), "Fiberon PET-GF15", M_PETGF_BLACK),
    )
    checks = check_geometry()
    records = []
    for name, workplane, material, colour in parts:
        solid = workplane.val()
        assert solid.isValid() and len(solid.Solids()) == 1, name
        step = OUTPUT / f"{name}.step"
        stl = OUTPUT / f"{name}.stl"
        solid.copy().exportStl(str(stl), tolerance=STL_LINEAR_TOLERANCE,
                               angularTolerance=STL_ANGULAR_TOLERANCE, relative=False)
        export_assembly(one_body(workplane, name, colour), str(step))
        mesh = trimesh.load(stl, force="mesh")
        assert mesh.is_watertight and mesh.is_winding_consistent, name
        assert len(mesh.split()) == 1 and mesh.volume > 0, name
        relative_volume_error = abs(mesh.volume - solid.Volume()) / solid.Volume()
        assert relative_volume_error < 0.01, (name, relative_volume_error)
        box = solid.BoundingBox()
        records.append({
            "name": name, "material": material, "quantity": 1,
            "step": step.name, "step_sha256": _sha(step),
            "stl": stl.name, "stl_sha256": _sha(stl),
            "bounds_mm": {"min": [box.xmin, box.ymin, box.zmin],
                           "max": [box.xmax, box.ymax, box.zmax]},
            "cad_volume_mm3": solid.Volume(),
            "solid_count": len(solid.Solids()), "cad_valid": solid.isValid(),
            "mesh_watertight": bool(mesh.is_watertight),
            "mesh_winding_consistent": bool(mesh.is_winding_consistent),
            "mesh_components": len(mesh.split()), "mesh_faces": len(mesh.faces),
            "mesh_relative_volume_error": relative_volume_error,
            "bed_pose": "flange-down" if "bung" in name else "handle-flat",
        })
    report = {
        "generator": "hardware/printed-parts/faucet/vent_seals.py",
        "generator_sha256": generator_digest,
        "path_source_sha256": path_digest,
        "stl_absolute_tolerance_mm": STL_LINEAR_TOLERANCE,
        "stl_angular_tolerance_radians": STL_ANGULAR_TOLERANCE,
        "frame": "CAD local X is lateral, Y is outward relative to shell centre, Z is downstream tangent. Tube tables use N from soda centre. Bungs print flange-down; tool is rotated handle-flat onto Z=0.",
        "parts": records, "geometry_checks": checks,
        "gland_mm": {"keeper_id": KEEPER_ID, "keeper_length": KEEPER_LENGTH,
                     "groove_id": GROOVE_ID, "groove_length": GROOVE_LENGTH,
                     "seat_id": BODY_SEAT_ID, "body_length": BODY_LENGTH,
                     "upstream_stop_id": UPSTREAM_STOP_ID,
                     "downstream_stop_id": STOP_ID, "stop_length": STOP_LENGTH,
                     "overall_length": GLAND_LENGTH,
                     "seated_bung_offset": BUNG_SEATED_Z},
        "tool_mm": {"outside_diameter": TOOL_OD, "inside_diameter": TOOL_ID,
                    "side_slot_width": TOOL_SLOT_WIDTH, "arc_length_on_soda_path": TOOL_ARC_LENGTH,
                    "handle_diameter": TOOL_HANDLE_OD, "handle_length": TOOL_HANDLE_LENGTH,
                    "bearing_face_local_z": BUNG_SEATED_Z,
                    "arc_center_local": [0, -(WATER_BEND_RADIUS + SHELL_CENTER_N), BODY_MID_Z]},
        "tube_and_wire_bores_mm": [dict(name=n, x=x, normal=y, diameter=d)
                                   for n, x, y, d in bore_centres(True)],
        "physical_qualification": "No vent-cavity bung has been printed, fitted, tested for leakage or aged. Existing 85A thimble fit is evidence for that article only.",
        "sources": [
            "https://www.parker.com/content/dam/Parker-com/Literature/O-Ring-Division-Literature/ORD-5700.pdf",
            "https://us.store.bambulab.com/products/tpu-85a-tpu-90a/",
            "https://bntechgo.com/bntechgo-28-gauge-silicone-ribbon-cable-copper-wire-4p-flat-cable-28-awg-flexible-soft-silicone-rubber-parallel-wire-stranded-tinned-copper-wire-4-pin-black-50-ft//",
        ],
    }
    assert generator_digest == _sha(Path(__file__)), "Generator changed during export; regenerate."
    assert path_digest == _sha(Path(_paths.__file__)), "Faucet paths changed during export; regenerate."
    (OUTPUT / "manifest.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"parts": [r["name"] for r in records], "checks": checks}, indent=2))


if __name__ == "__main__":
    main()
