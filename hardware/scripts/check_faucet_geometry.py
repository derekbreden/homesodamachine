#!/usr/bin/env python3
"""Measure the faucet's production solids, assembly motion and named wall sections.

    tools/cad-venv/bin/python hardware/scripts/check_faucet_geometry.py

The scorecard reads the live CadQuery builders. Wall readings are named B-rep
sections or complete witness volumes around fasteners, not a global thickness
certification. Print finish, strength, hand access and assembly force require
the physical PET-GF parts and the harvested donor.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
FAUCET = ROOT / "hardware/printed-parts/faucet"
SHELL = FAUCET / "faucet-shell"
OUTPUT = SHELL / "geometry-check.json"
DISTANCE_TOLERANCE = 1e-4
VOLUME_TOLERANCE = 1e-5


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def source_paths() -> tuple[Path, ...]:
    return (Path(__file__).resolve(),
            ROOT / "hardware/faucet-layout/faucet_assembly.py",
            FAUCET / "_faucet_interface.py",
            FAUCET / "_display_snap.py",
            FAUCET / "refresh_print_project.py",
            ROOT / "hardware/printed-parts/fixtures/faucet-display-snap/faucet_display_snap_trial.py",
            ROOT / "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json",
            SHELL / "faucet_shell.py",
            FAUCET / "above-counter-plate/above_counter_plate.py",
            FAUCET / "above-counter-gasket/above_counter_gasket.py",
            FAUCET / "faucet-display-cover/faucet_display_cover.py",
            FAUCET / "tpu-o-ring/tpu_o_ring.py",
            ROOT / "hardware/printed-parts/cadlib/fits.py",
            ROOT / "hardware/printed-parts/cadlib/world_workplane.py",
            ROOT / "hardware/cut-parts/faucet/under-counter-plate/under-counter-plate.dxf",
            ROOT / "hardware/reference/touch-flo-faucet/westbrass-reference/westbrass-reference.step")


def hashes(paths: tuple[Path, ...]) -> dict:
    return {str(p.relative_to(ROOT)): digest(p) for p in paths}


def shape(part):
    return part.val() if hasattr(part, "val") else part


def volume(part) -> float:
    return sum(s.Volume() for s in shape(part).Solids())


def clean_number(value: float) -> float:
    return round(float(value), 7)


class Reading:
    def __init__(self):
        self.rows = {}

    def add(self, name: str, passed: bool, **measurements):
        self.rows[name] = {**measurements, "passed": bool(passed)}
        print(f"{'PASS' if passed else 'FAIL'} {name}", flush=True)


def line_intervals(solid, origin, direction, length):
    """Material intervals on an exact B-rep line, as distance from its origin."""
    import cadquery as cq
    origin, direction = cq.Vector(*origin), cq.Vector(*direction).normalized()
    edge = cq.Edge.makeLine(origin, origin + direction.multiply(length))
    intervals = []
    for hit in shape(solid).intersect(edge).Edges():
        t0 = (hit.startPoint() - origin).dot(direction)
        t1 = (hit.endPoint() - origin).dot(direction)
        if abs(t1 - t0) > DISTANCE_TOLERANCE:
            intervals.append(tuple(sorted((t0, t1))))
    merged = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1] + DISTANCE_TOLERANCE:
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def ring_witness(center, inner_radius, wall, bottom_z, height):
    import cadquery as cq
    return (cq.Workplane("XY").workplane(offset=bottom_z).center(*center)
            .circle(inner_radius + wall).circle(inner_radius).extrude(height).val())


def solids_reading(reading, parts):
    for name, part in parts.items():
        solid = shape(part)
        bounds = solid.BoundingBox()
        valid, count, size = solid.isValid(), len(solid.Solids()), volume(solid)
        reading.add(f"solid:{name}", valid and count == 1 and size > 0,
                    valid=valid, solids=count, volume_mm3=clean_number(size),
                    bounds_mm=[clean_number(v) for v in (
                        bounds.xmin, bounds.xmax, bounds.ymin, bounds.ymax,
                        bounds.zmin, bounds.zmax)])


def mesh_reading(reading, f, parts):
    """Exercise the production tessellator and the actual serialized STL surface."""
    for name, part in parts.items():
        data = f.piece_mesh(part).export(file_type="stl")
        mesh = f.trimesh.load_mesh(io.BytesIO(data), file_type="stl")
        bodies = len(mesh.split(only_watertight=False))
        valid = mesh.is_watertight and mesh.is_winding_consistent and bodies == 1 and mesh.volume > 0.0
        reading.add(f"mesh:{name}", valid, watertight=bool(mesh.is_watertight),
                    consistent_winding=bool(mesh.is_winding_consistent), bodies=bodies,
                    triangle_count=len(mesh.faces), volume_mm3=clean_number(mesh.volume),
                    tolerance_mm=f.piece_mesh_tol, angular_tolerance_rad=f.piece_mesh_angle,
                    scope="live B-rep tessellated, serialized as STL and loaded again; not a slicer result")


def tube_radius_reading(reading, f, assembly):
    from OCP.BRepAdaptor import BRepAdaptor_Curve, BRepAdaptor_Surface
    source = "https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf"
    arcs = []
    for path in (assembly._flavor_path(assembly.umbilical_z_bottom), assembly._splay_path(1)):
        for edge in path.wire().val().Edges():
            if edge.geomType() == "CIRCLE":
                arcs.append(BRepAdaptor_Curve(edge.wrapped).Circle().Radius())
    reading.add("route:flavor-tube-radius", bool(arcs) and min(arcs) >= f.flavor_bend_min_radius - DISTANCE_TOLERANCE,
                method="actual circular edges of the assembled flavor and tail-splay centerline paths",
                centerline_radii_mm=sorted({clean_number(r) for r in arcs}),
                supplier_minimum_mm=f.flavor_bend_min_radius, supplier_source=source)
    for name, body, minimum in (("flavor-passage", f.build_flavor_transition_inner_cut(), f.flavor_bend_min_radius),
                                 ("soda-tube", assembly.build_soda_faucet_tube(), 31.75)):
        radii = [BRepAdaptor_Surface(face.wrapped).Torus().MajorRadius()
                 for face in shape(body).Faces() if face.geomType() == "TORUS"]
        reading.add(f"route:{name}-radius", bool(radii) and min(radii) >= minimum - DISTANCE_TOLERANCE,
                    method="toroidal B-rep surfaces' major radii",
                    centerline_radii_mm=sorted({clean_number(r) for r in radii}),
                    supplier_minimum_mm=minimum, supplier_source=source)


def clearance_reading(reading, name, first, second, minimum_gap=0.0):
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    first, second = shape(first), shape(second)

    def single_solid(part):
        solids = part.Solids()
        if len(solids) != 1:
            return None
        solid = solids[0]
        # A compound wrapper carries the same complete solid topology.
        if any(len(getattr(part, kind)()) != len(getattr(solid, kind)())
               for kind in ("Faces", "Edges", "Vertices")):
            return None
        return solid

    left, right = single_solid(first), single_solid(second)
    distance = BRepExtrema_DistShapeShape(
        (left if left is not None else first).wrapped,
        (right if right is not None else second).wrapped)
    if not distance.IsDone():
        raise RuntimeError(f"{name}: exact distance calculation did not complete")
    gap = distance.Value()
    separated = (left is not None and right is not None and gap > DISTANCE_TOLERANCE
                 and not distance.InnerSolution())
    overlap = 0.0 if separated else volume(first.intersect(second))
    reading.add(name, overlap <= VOLUME_TOLERANCE and gap >= minimum_gap - DISTANCE_TOLERANCE,
                overlap_mm3=clean_number(overlap), gap_mm=clean_number(gap),
                required_gap_mm=minimum_gap,
                overlap_method="positive exact solid distance" if separated else "B-rep common volume")


def neck_reading(reading, f, full, base, tip):
    import cadquery as cq
    stations = (
        ("neck", full, (0.0, f.soda_faucet_tube_y + f.tube_shell_center_y,
                        (f.zone5_z_top + f.gn_bend1_z_start) / 2.0), (0.0, 1.0, 0.0),
         f.split_socket_wall + f.split_slip / 2.0 + f.split_plug_wall),
    )
    theta = f.split_junction_rot - f.split_plug_angle_rad / 2.0
    point = f._bend2_point(theta)
    profile_y = (0.0, math.cos(theta), math.sin(theta))
    center = (0.0, f.soda_faucet_tube_y - point[0] + f.tube_shell_center_y * profile_y[1],
              f.zone5_z_top + point[1] + f.tube_shell_center_y * profile_y[2])
    stations += (("socket", base, center, profile_y, f.wall_thickness_min),
                 ("plug", tip, center, profile_y, f.wall_thickness_min))
    for name, part, center, profile_y, requirement in stations:
        probes = []
        for step in range(72):
            angle = 2.0 * math.pi * step / 72
            direction = (math.cos(angle), math.sin(angle) * profile_y[1],
                         math.sin(angle) * profile_y[2])
            spans = line_intervals(part, center, direction, f.tube_shell_outer_r + 2.0)
            thickness = spans[-1][1] - spans[-1][0] if spans else 0.0
            probes.append((math.degrees(angle), thickness))
        least = min(probes, key=lambda row: row[1])
        reading.add(f"section:{name}", least[1] >= requirement - DISTANCE_TOLERANCE,
                    method="72 radial B-rep material chords in one section; last material interval",
                    center_mm=list(center), probe_count=len(probes),
                    minimum_sampled_wall_mm=clean_number(least[1]),
                    minimum_at_section_angle_deg=clean_number(least[0]),
                    required_mm=requirement)
    center = (0.0, f.soda_faucet_tube_y - f._path_center_bend2[0],
              f.zone5_z_top + f._path_center_bend2[1])
    axis_end = (1.0, center[1], center[2])
    motion = []
    for station in range(9):
        angle = math.degrees(f.split_plug_angle_rad) * station / 8.0
        overlap = volume(shape(base).intersect(shape(tip).rotate(center, axis_end, angle)))
        motion.append({"rotation_deg": clean_number(angle), "overlap_mm3": clean_number(overlap)})
    reading.add("motion:neck-joint", all(row["overlap_mm3"] <= VOLUME_TOLERANCE for row in motion),
                samples=motion, method="tip rotated about the arc axis from closed to plug-clear")
    outlet = f._tip_frame()[0].toTuple()
    desired = (0.0, f.gn_outlet_y, f.gn_outlet_z)
    reading.add("position:outlet", math.dist(outlet, desired) < DISTANCE_TOLERANCE,
                actual_mm=list(outlet), required_mm=list(desired))


def base_fastener_reading(reading, f, base, plate):
    import cadquery as cq
    for index, center in enumerate(f.base_pod_centers, 1):
        witness = ring_witness(center, f.base_insert_outer_dia / 2.0,
                               f.wall_thickness_min, f.base_insert_bottom_z, f.base_insert_length)
        missing = volume(witness.cut(shape(base)))
        reading.add(f"wall:base-insert-{index}", missing <= VOLUME_TOLERANCE,
                    method="complete 3 mm radial witness around the real brass OD over its installed length",
                    center_mm=list(center), insert_od_mm=f.base_insert_outer_dia,
                    required_wall_mm=f.wall_thickness_min, missing_witness_mm3=clean_number(missing))
        radius = (f.base_pod_shank_dia + f.base_pod_counterbore_dia) / 4.0
        seats = []
        for turn in range(8):
            angle = turn * math.pi / 4.0
            point = (center[0] + radius * math.cos(angle), center[1] + radius * math.sin(angle),
                     -f.above_counter_plate_thickness - 1.0)
            spans = line_intervals(plate, point, (0.0, 0.0, 1.0),
                                   f.above_counter_plate_thickness + f.base_pedestal_height + 2.0)
            seats.append(spans[-1][1] - spans[-1][0] if spans else 0.0)
        least = min(seats)
        reading.add(f"wall:base-screw-seat-{index}", least >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                    method="eight vertical B-rep chords through the bearing annulus",
                    minimum_sampled_wall_mm=clean_number(least), required_mm=f.wall_thickness_min)
        tip_z = f.base_screw_seat_z + f.base_screw_length
        insert_end = f.base_insert_bottom_z + f.base_insert_length
        engagement = min(tip_z, insert_end) - max(f.base_screw_seat_z, f.base_insert_bottom_z)
        tip_clearance = f.base_insert_bottom_z + f.base_pod_insert_depth - tip_z
        reading.add(f"fit:base-screw-{index}", engagement >= f.base_insert_length - DISTANCE_TOLERANCE
                    and tip_clearance >= -DISTANCE_TOLERANCE,
                    thread_engagement_mm=clean_number(engagement),
                    blind_tip_clearance_mm=clean_number(tip_clearance),
                    head_recess_mm=f.base_screw_head_recess)
    clearance_reading(reading, "seat:plate-shell", base, plate)
    for index, center in enumerate(f.base_pod_centers, 1):
        pedestal = (cq.Workplane("XY").center(*center).circle(f.base_pedestal_dia / 2.0)
                    .extrude(f.base_pedestal_height).edges(">Z").chamfer(f.base_pedestal_chamfer).val())
        clearance_reading(reading, f"fit:base-pedestal-{index}", base, pedestal, f.fits.slip)
        witness = ring_witness(center, f.base_pod_hole_dia / 2.0,
                               f.wall_thickness_min, 0.0, f.base_pod_hole_depth)
        missing = volume(witness.cut(shape(base)))
        reading.add(f"wall:base-pedestal-socket-{index}", missing <= VOLUME_TOLERANCE,
                    method="complete radial witness around the socket throughout the pedestal engagement",
                    missing_witness_mm3=clean_number(missing), required_wall_mm=f.wall_thickness_min)


def lower_section_reading(reading, f, base):
    """Closed body sections below the open lever plateau, in the XY plane."""
    sampled = []
    for z in (12.0, 16.0, 20.0, 24.0, 28.0, 32.0, 36.0, 38.0):
        chords = []
        for station in range(72):
            angle = station * 2.0 * math.pi / 72.0
            direction = (math.cos(angle), math.sin(angle), 0.0)
            spans = line_intervals(base, (0.0, 0.0, z), direction, f.foot_depth)
            chords.append(spans[-1][1] - spans[-1][0] if spans else 0.0)
        least = min(chords)
        sampled.append({"z_mm": z, "minimum_sampled_radial_wall_mm": clean_number(least)})
    reading.add("section:lower-closed-body",
                min(row["minimum_sampled_radial_wall_mm"] for row in sampled)
                >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                method="72 exact radial B-rep chords from the shank axis at each of eight heights",
                scope="closed body below the lever opening; radial chords are not global normal thickness",
                samples=sampled, required_mm=f.wall_thickness_min)
    import cadquery as cq
    outer = shape(f.build_lower_outer())
    side = cq.Compound.makeCompound([face for face in outer.Faces() if face.geomType() != "PLANE"])
    cavities = (("donor-rectangle", f.build_zone2_inner_cut()),
                ("donor-arches", f.build_zone3_inner_cut()),
                ("soda-passage", f.build_lower_soda_inner_cut()),
                ("flavor-transition", f.build_flavor_transition_inner_cut()),
                ("signal-transition", f.build_signal_transition_inner_cut()),
                ("lower-signal-lane", f.build_lower_signal_lane()),
                ("vertical-neck", f._tube_shell_inner_section(f.zone5_z_bottom, f.zone5_height)))
    for name, cavity in cavities:
        distance = side.distance(shape(cavity))
        reading.add(f"wall:loft-to-{name}", distance >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                    method="exact minimum distance from the loft's curved side faces to the complete cavity solid",
                    minimum_distance_mm=clean_number(distance), required_mm=f.wall_thickness_min,
                    scope="outer loft only; access-cut and fastener boundaries are checked separately")
    distance = shape(f.build_lever_clearance()).distance(shape(f.build_flavor_transition_inner_cut()))
    reading.add("wall:lever-to-flavor-transition", distance >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                method="exact minimum separation between the swept lever clearance and flavor-passage cutters",
                minimum_distance_mm=clean_number(distance), required_mm=f.wall_thickness_min,
                scope="the rear lever web; intersections with the donor outlet cavity are intentional")
    arch_faces = [face for face in shape(f.build_lower_access_cut()).Faces() if face.geomType() == "CYLINDER"]
    if not arch_faces:
        reading.add("wall:lever-cheek", False, reason="the access cut has no analytic arch surface")
    else:
        arch = cq.Compound.makeCompound(arch_faces)
        distance = arch.distance(shape(f.build_zone3_inner_cut()))
        reading.add("wall:lever-cheek", distance >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                    method="exact distance from the lever-access arch surface to the donor-arch cavity",
                    minimum_distance_mm=clean_number(distance), required_mm=f.wall_thickness_min)


def display_reading(reading, f, assembly, parts, body):
    import cadquery as cq
    snap = f._display_snap
    full = cq.Compound.makeCompound([shape(parts["shell_base"]), shape(parts["shell_tip"])])
    tip, cover, body = shape(parts["shell_tip"]), shape(parts["display_cover"]), shape(body)
    origin, tangent, normal = f._tip_frame()
    local_frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0,0.0,0.0), normal=normal))
    offset = f.display_snap_s_offset
    arms = shape(f.build_display_snap_arms())
    receivers = shape(f.build_display_snap_receivers())
    ribbon = shape(assembly.build_display_ribbon())
    bottom, top = snap.beam_n_range(f.display_feet_n)

    def world(native):
        return shape(f._display_world(native.translate((0.0, offset, 0.0))))

    def handed(part, side):
        return part if side == 1 else part.mirror("YZ")

    def point(x, s, n):
        return (origin + tangent.multiply(s) + normal.multiply(n) + cq.Vector(x, 0.0, 0.0)).toTuple()

    tubes = {"soda": assembly.build_soda_faucet_tube(),
             "flavor-a": assembly.build_flavor_tube(1),
             "flavor-b": assembly.build_flavor_tube(-1)}
    gaps = []
    for name, tube in tubes.items():
        gap, overlap = body.distance(shape(tube)), volume(body.intersect(shape(tube)))
        required = 0.15 if name.startswith("flavor") else 0.0
        passed = overlap <= VOLUME_TOLERANCE and gap >= required - DISTANCE_TOLERANCE
        if name.startswith("flavor"):
            passed = passed and gap <= 0.40 + DISTANCE_TOLERANCE
            gaps.append(gap)
        reading.add(f"clearance:display-{name}", passed,
                    gap_mm=clean_number(gap), overlap_mm3=clean_number(overlap),
                    required_minimum_mm=required,
                    nominal_target_mm=0.30 if name.startswith("flavor") else None,
                    scope="fixed nominal tube and corrected vendor-component envelopes; no printed central floor")
    reading.add("placement:display-tube-budget", True,
                nominal_minimum_gap_mm=clean_number(min(gaps)),
                flavor_bore_radial_allowance_mm=clean_number((f.flavor_tube_hole_dia-f.flavor_tube_od)/2.0),
                scope="nominal placement only; the tube fit trial checks actual tube motion, component tolerances and contact")

    tooth_masks, travel_regions = [], []
    for side in (-1, 1):
        free = world(snap.build_motion_clearance(f.display_feet_n, side))
        extra = volume(tip.intersect(free).cut(arms))
        missing = volume(world(snap.build_beam(f.display_feet_n, side)).cut(tip))
        reading.add(f"snap:free-arm-{side:+d}", extra <= VOLUME_TOLERANCE and missing <= VOLUME_TOLERANCE,
                    excess_body_in_free_space_mm3=clean_number(extra),
                    missing_arm_material_mm3=clean_number(missing),
                    free_length_from_tooth_end_mm=snap.BEAM_ROOT_S-snap.ROOT_FILLET-snap.TOOTH_S_END,
                    method="actual body inside the complete motion-clearance box minus the arm, and complete arm containment")
        tooth = handed(snap.box(snap.BEAM_OUTER_X, snap.BEAM_OUTER_X+1.0,
                                snap.BEAM_TIP_S, snap.TOOTH_S_END, bottom-1.0, top+1.0), side)
        tooth_mask = world(tooth)
        tooth_masks.append(tooth_mask)
        travel = handed(snap.box(snap.BEAM_INNER_X-snap.OVERTRAVEL,
                                 snap.BEAM_OUTER_X+snap.RADIAL_SLIP+snap.ENGAGEMENT,
                                 snap.BEAM_TIP_S, snap.BEAM_ROOT_S-snap.ROOT_FILLET,
                                 bottom, top), side)
        travel_regions.append(world(travel))
        receiver = world(snap.build_receiver(f.display_feet_n, side))
        missing = volume(receiver.cut(cover))
        reading.add(f"wall:snap-receiver-{side:+d}", missing <= VOLUME_TOLERANCE,
                    missing_complete_3mm_ledge_mm3=clean_number(missing),
                    method="complete three-dimensional receiver witness inside the final cover")
        tooth_bounds = tip.intersect(tooth_mask).moved(local_frame.inverse).BoundingBox()
        receiver_bounds = cover.intersect(receiver).moved(local_frame.inverse).BoundingBox()
        projection = (tooth_bounds.xmax-receiver_bounds.xmin if side == 1
                      else receiver_bounds.xmax-tooth_bounds.xmin)
        bearing_gap = tooth_bounds.zmin-receiver_bounds.zmax
        reading.add(f"snap:engagement-{side:+d}",
                    abs(projection-snap.ENGAGEMENT) < DISTANCE_TOLERANCE
                    and abs(bearing_gap-snap.BEARING_SLIP) < DISTANCE_TOLERANCE,
                    measured_radial_engagement_mm=clean_number(projection),
                    measured_normal_bearing_gap_mm=clean_number(bearing_gap),
                    method="actual tooth and actual cover-ledge extents in the head frame")
        sections, stops = [], []
        for s in (snap.BEAM_TIP_S+1.5, (snap.TOOTH_S_END+snap.BEAM_ROOT_S)/2.0,
                  snap.BEAM_ROOT_S-snap.ROOT_FILLET-0.5):
            core = world(handed(snap.box(snap.BEAM_INNER_X, snap.BEAM_OUTER_X,
                                         s-0.1, s+0.1, bottom, top), side))
            sections.append(clean_number(volume(core.cut(tip))))
            spans = line_intervals(tip, point(side*(snap.BEAM_INNER_X-0.00001), s+offset,
                                             (bottom+top)/2.0), (-side, 0.0, 0.0), 4.0)
            stops.append(spans[0][0]+0.00001 if spans else 0.0)
        reading.add(f"section:snap-arm-{side:+d}", max(sections) <= VOLUME_TOLERANCE,
                    missing_3_by_3_sections_mm3=sections,
                    method="complete 3 by 3 mm witnesses at three actual free-arm stations")
        reading.add(f"snap:travel-stop-{side:+d}", all(abs(gap-snap.OVERTRAVEL) < DISTANCE_TOLERANCE for gap in stops),
                    measured_inward_stop_gaps_mm=[clean_number(gap) for gap in stops],
                    nominal_stop_travel_mm=snap.OVERTRAVEL,
                    method="B-rep line from the inner arm face to fixed body at three stations")
    without_teeth = full.cut(cq.Compound.makeCompound(tooth_masks))
    rows = []
    for lift in [step/4.0 for step in range(33)] + [10.0, 15.0, 20.0]:
        moved = cover.translate(normal.multiply(lift))
        rows.append({"lift_mm": lift,
                     "non_tooth_shell_overlap_mm3": clean_number(volume(moved.intersect(without_teeth))),
                     "device_overlap_mm3": clean_number(volume(moved.intersect(body))),
                     "ribbon_overlap_mm3": clean_number(volume(moved.intersect(ribbon))),
                     "tooth_contact_mm3": clean_number(volume(moved.intersect(full)))})
    reading.add("motion:display-cover-normal", all(max(row["non_tooth_shell_overlap_mm3"],
                row["device_overlap_mm3"], row["ribbon_overlap_mm3"]) <= VOLUME_TOLERANCE for row in rows),
                samples=rows, scope="unflexed cover; only the actual tooth projections are exempted from fixed-body interference")
    pushed = cover.translate(normal.multiply(-0.01))
    stop_contact = volume(pushed.intersect(without_teeth))
    device_contact = volume(pushed.intersect(body))
    reading.add("seat:display-cover-stop", stop_contact > VOLUME_TOLERANCE and device_contact <= VOLUME_TOLERANCE,
                fixed_body_interference_after_0_01mm_inward_motion_mm3=clean_number(stop_contact),
                device_interference_mm3=clean_number(device_contact),
                method="the final cover's inward seating stop contacts the body before the display")
    lift_overlap = volume(cover.translate(normal.multiply(0.5)).intersect(full))
    reading.add("retention:display-snaps", lift_overlap > VOLUME_TOLERANCE,
                nominal_engagement_mm=snap.ENGAGEMENT, radial_slip_mm=snap.RADIAL_SLIP,
                normal_bearing_slip_mm=snap.BEARING_SLIP,
                interference_on_0_5mm_outward_lift_mm3=clean_number(lift_overlap),
                ideal_rectangular_beam_strain_percent=clean_number(100.0*snap.nominal_strain()),
                scope="geometric capture and ideal strain only; PET-GF force, strength and cycling are physical trial results")
    travel = cq.Compound.makeCompound(travel_regions)
    for name, hardware in (("display", body), ("ribbon", ribbon), *tubes.items()):
        clearance_reading(reading, f"clearance:snap-travel-{name}", travel, hardware,
                          0.1 if name == "ribbon" else 0.0)
    for lift in [step/4.0 for step in range(17)] + [6.0, 10.0, 20.0]:
        moved = body.translate(normal.multiply(lift))
        overlap = volume(moved.intersect(full))
        reading.add(f"motion:display-insertion-{lift:g}", overlap <= VOLUME_TOLERANCE,
                    normal_lift_mm=lift, overlap_mm3=clean_number(overlap),
                    method="actual device translated normally into the complete fixed shell")
    pads = shape(f.build_display_feet_pads())
    missing = volume(pads.cut(tip))
    reading.add("wall:display-foot-pads", missing <= VOLUME_TOLERANCE,
                missing_3_by_3_by_3_pad_material_mm3=clean_number(missing),
                method="complete four support-pad witnesses inside the final tip")
    outside = shape(f.build_display_outer_envelope())
    side = cq.Compound.makeCompound([face for face in outside.Faces() if face.geomType() != "PLANE"])
    side_wall = side.distance(shape(f.build_display_cover_inner_envelope()))
    reading.add("wall:display-cosmetic-shroud", side_wall >= 1.0-DISTANCE_TOLERANCE,
                minimum_loft_side_separation_mm=clean_number(side_wall), required_mm=1.0,
                method="exact separation of the complete outer loft's curved side faces and inner cover cavity")
    spans = line_intervals(cover, point(11.0, f._display_housing_center_s,
                                      f.display_cover_top_n+1.0), normal.multiply(-1).toTuple(), 5.0)
    bezel = spans[0][1]-spans[0][0] if spans else 0.0
    reading.add("section:display-cosmetic-bezel", bezel >= 1.0-DISTANCE_TOLERANCE,
                measured_bezel_mm=clean_number(bezel), required_mm=1.0,
                method="normal material chord through the flat bezel next to the screen opening")
    front_planes = [((face.Center()-origin).dot(tangent), face.Area())
                    for face in cover.Faces()
                    if face.geomType() == "PLANE" and face.normalAt().dot(tangent) < -0.999999]
    front = min((station for station, _ in front_planes), default=float("inf"))
    front_area = sum(area for station, area in front_planes if abs(station) < DISTANCE_TOLERANCE)
    forward_halfspace = shape(f._cradle_prism(50.0, -100.0, -DISTANCE_TOLERANCE, -100.0, 100.0))
    protrusion = volume(cover.intersect(forward_halfspace))
    reading.add("position:display-flush-front", abs(front) < DISTANCE_TOLERANCE
                and front_area > VOLUME_TOLERANCE and protrusion <= VOLUME_TOLERANCE,
                foremost_front_plane_s_mm=clean_number(front), outlet_plane_s_mm=0.0,
                flush_front_face_area_mm2=clean_number(front_area),
                material_forward_of_outlet_mm3=clean_number(protrusion),
                method="actual forward-facing planar face and exact negative-S halfspace intersection")
    cap = shape(f._cradle_prism(f.signal_lane_width/2.0, 0.0001, 1.0001,
                              f.signal_lane_center_n-f.signal_lane_depth/2.0,
                              f.signal_lane_center_n+f.signal_lane_depth/2.0))
    cap = cap.cut(shape(f.build_zone6_inner_cut()))
    missing = volume(cap.cut(tip))
    face_slab = shape(f._cradle_prism(25.0, -0.001, 0.001, -20.0, 30.0))
    signal_at_face = sum(volume(face_slab.intersect(shape(cutter))) for cutter in
                         (f.build_signal_neck_inner_cut(), f._display_wire_hole()))
    reading.add("wall:outlet-signal-closure", missing <= VOLUME_TOLERANCE and signal_at_face <= VOLUME_TOLERANCE,
                missing_1mm_cosmetic_cap_mm3=clean_number(missing),
                signal_void_at_outlet_mm3=clean_number(signal_at_face),
                method="1 mm closure witness above the unchanged flavor passage, and both signal cutters at the outlet plane")


def display_trial_reading(reading, f, parts):
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/fixtures/faucet-display-snap"))
    import faucet_display_snap_trial as trial
    housing, cover, clip, dimensions = trial.build_trial()
    tip = shape(parts["shell_tip"])
    boundary = max(dimensions["complete_head_end_s_mm"], f.display_ribbon_reference_start_s)+1.0
    witness = tip.intersect(shape(trial.trial_region(boundary)))
    missing = volume(witness.cut(shape(housing)))
    extra = volume(shape(housing).cut(tip))
    cover_delta = volume(shape(cover).cut(shape(parts["display_cover"]))) + volume(shape(parts["display_cover"]).cut(shape(cover)))
    cable_clipped = volume(shape(f.build_display_ribbon_transition()).cut(shape(clip)))
    reading.add("fixture:complete-display-fit-trial", max(missing, extra, cover_delta, cable_clipped) <= VOLUME_TOLERANCE,
                missing_head_or_anchor_material_mm3=clean_number(missing),
                added_housing_material_mm3=clean_number(extra),
                cover_symmetric_difference_mm3=clean_number(cover_delta),
                clipped_side_entry_ribbon_mm3=clean_number(cable_clipped),
                retained_geometry=dimensions,
                method="complete production head region through the cable branch, and exact complete cover")
    poses = {name: angle for name, _, angle in trial.production_print.PARTS}
    reading.add("fixture:production-print-orientations",
                abs(poses["faucet-shell-tip"]+math.degrees(f.print_tip_build_rot)) < DISTANCE_TOLERANCE,
                housing_rotation_x_deg=poses["faucet-shell-tip"],
                cover_rotation_x_deg=poses["faucet-display-cover"],
                method="trial print transforms are read from the same production-print part table")
    solids_reading(reading, {"display_trial_housing": housing})
    mesh_reading(reading, f, {"display_trial_housing": housing})


def lever_reading(reading, assembly, parts):
    rows = []
    for step in range(19):
        angle = assembly.lever_press_angle_deg * step / 18.0
        lever = shape(assembly.build_lever_at(angle))
        overlap = sum(volume(lever.intersect(shape(parts[name]))) for name in ("shell_base", "shell_tip"))
        gap = min(lever.distance(shape(parts[name])) for name in ("shell_base", "shell_tip"))
        rows.append({"angle_deg": angle, "overlap_mm3": clean_number(overlap),
                     "gap_mm": clean_number(gap)})
    reading.add("motion:lever", all(row["overlap_mm3"] <= VOLUME_TOLERANCE for row in rows),
                samples=rows, scope="the repo's dimensional lever envelope, not a measured scan of the donor lever")


def ribbon_reading(reading, f, assembly, parts):
    import cadquery as cq
    ribbon = assembly.build_display_ribbon()
    solid = shape(ribbon)
    reading.add("solid:display-ribbon-envelope", solid.isValid() and len(solid.Solids()) == 1,
                valid=solid.isValid(), solids=len(solid.Solids()),
                section_mm=[f.signal_ribbon_max_width, f.signal_ribbon_max_depth],
                scope="maximum vendor-stated ribbon section; the modeled end stops beside the PCB before factory solder fan-out")
    for name, body in parts.items():
        # The 5 × 1.8 mm capsule gives the maximum rectangular ribbon a
        # 0.1094 mm corner gap. Require positive stock-free space through the
        # lofted handoffs too, rather than accepting a zero-volume tangency.
        clearance_reading(reading, f"clearance:signal-{name}", ribbon, body, 0.1)
    hardware = (("donor", assembly.load_westbrass()),
                ("soda-tube", assembly.build_soda_faucet_tube()),
                ("flavor-a", assembly.build_flavor_tube(1)),
                ("flavor-b", assembly.build_flavor_tube(-1)),
                ("countertop", assembly.build_countertop()),
                ("under-counter-plate", assembly.build_under_counter_plate()),
                ("display-body", assembly.build_display_body()),
                ("display-usb", f.build_display_usb_keepout()))
    for name, body in hardware:
        clearance_reading(reading, f"clearance:signal-{name}", ribbon, body)
    lane = (cq.Workplane("XY").center(0.0, f.signal_lane_center_n)
            .slot2D(f.signal_lane_width, f.signal_lane_depth).extrude(1.0).val())
    section = (cq.Workplane("XY").center(0.0, f.signal_lane_center_n)
               .rect(f.signal_ribbon_max_width, f.signal_ribbon_max_depth).extrude(1.0).val())
    outside = volume(section.cut(lane))
    reading.add("fit:signal-lane-section", outside <= VOLUME_TOLERANCE,
                method="complete maximum rectangular cable section inside the actual capsule lane",
                outside_volume_mm3=clean_number(outside),
                lane_section_mm=[f.signal_lane_width, f.signal_lane_depth])
    plug = (cq.Workplane("XY").center(0.0, f.tube_shell_center_y)
            .circle(f.tube_shell_outer_r - f.split_plug_shrink).extrude(1.0).val())
    side = cq.Compound.makeCompound([face for face in plug.Faces() if face.geomType() == "CYLINDER"])
    distance = side.distance(lane)
    reading.add("wall:neck-signal-lane", distance >= f.wall_thickness_min - DISTANCE_TOLERANCE,
                method="exact separation of the plug's circular exterior and full signal-lane profile",
                minimum_distance_mm=clean_number(distance), required_mm=f.wall_thickness_min,
                scope="the uniform profile; the curved neck, lap and port have separate readings")


def print_reading(f, parts):
    rows = {}
    for name, theta in (("shell_base", f.print_base_build_rot), ("shell_tip", f.print_tip_build_rot)):
        posed = shape(parts[name]).rotate((0, 0, 0), (1, 0, 0), -math.degrees(theta))
        box = posed.BoundingBox()
        rows[name] = {"build_rotation_deg": clean_number(math.degrees(theta)),
                      "conservative_bounding_box_mm": [clean_number(box.xlen), clean_number(box.ylen),
                                                       clean_number(box.zlen)]}
    rows["visible_swept_neck_maximum_overhang_deg"] = clean_number(math.degrees(f.max_print_overhang_rad))
    rows["hidden_plug_maximum_flank_overhang_deg"] = clean_number(
        math.degrees(f.print_tip_build_rot - f._path_plug_start_rot))
    rows["scope"] = "Geometric orientations only; no slice or physical support-removal result."
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    paths = source_paths()
    before = hashes(paths)
    os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
    sys.path.insert(0, str(ROOT / "hardware/faucet-layout"))
    import faucet_assembly as assembly
    f = assembly.faucet_shell
    reading = Reading()
    print("Building the faucet's production solids", flush=True)
    full = f.build_shell()
    parts = {"shell_base": f.build_shell_base(full), "shell_tip": f.build_shell_tip(full),
             "above_counter_plate": assembly.load_above_counter_plate(),
             "above_counter_gasket": assembly.load_above_counter_gasket(),
             "display_cover": assembly.load_display_cover(), "tpu_thimble": assembly.build_o_ring()}
    solids_reading(reading, parts)
    mesh_reading(reading, f, parts)
    tube_radius_reading(reading, f, assembly)
    base, tip, plate = parts["shell_base"], parts["shell_tip"], parts["above_counter_plate"]
    for name in ("shell_base", "shell_tip", "above_counter_plate", "display_cover"):
        clearance_reading(reading, f"clearance:donor-{name}", parts[name], assembly.load_westbrass())
    for name, body in (("soda", assembly.build_soda_faucet_tube()),
                       ("flavor-a", assembly.build_flavor_tube(+1)),
                       ("flavor-b", assembly.build_flavor_tube(-1)),
                       ("display-body", assembly.build_display_body()),
                       ("display-screen", assembly.build_display_screen())):
        for piece in ("shell_base", "shell_tip", "display_cover"):
            clearance_reading(reading, f"clearance:{name}-{piece}", body, parts[piece])
    neck_reading(reading, f, full, base, tip)
    base_fastener_reading(reading, f, base, plate)
    lower_section_reading(reading, f, base)
    display_reading(reading, f, assembly, parts, assembly.build_display_body())
    display_trial_reading(reading, f, parts)
    lever_reading(reading, assembly, parts)
    ribbon_reading(reading, f, assembly, parts)
    clearance_reading(reading, "seat:plate-gasket", plate, parts["above_counter_gasket"])
    after = hashes(paths)
    if before != after:
        raise RuntimeError("a faucet source changed during the reading; rerun after its build settles")
    passed = all(row["passed"] for row in reading.rows.values())
    result = {"schema_version": 1,
              "scope": "Live production B-rep builders and serialized STL surfaces, fixed donor, dimensional display and tube models; "
                       "named wall witnesses and sampled sections. No global minimum-wall certification.",
              "nominal_cad_only": True,
              "distance_tolerance_mm": DISTANCE_TOLERANCE,
              "overlap_tolerance_mm3": VOLUME_TOLERANCE,
              "geometry_source_sha256": before,
              "display_usb_reference": {"file": f.display_usb_reference_file,
                                        "url": f.display_usb_reference_url,
                                        "sha256": f.display_usb_reference_sha256,
                                        "native_bounds_mm": f.display_usb_reference_bounds},
              "display_under_pcb_reference": {
                  "source_file": assembly._display_components["source_file"],
                  "source_sha256": assembly._display_components["source_sha256"],
                  "source_url": assembly._display_components["source_url"],
                  "component_count": assembly._display_components["component_count"],
                  "excluded_optional_header_indices": assembly._display_components["excluded_optional_header_indices"],
                  "vendor_feet_z_mm": assembly._display_components["vendor_feet_z_mm"],
                  "vendor_pcb_underside_above_feet_mm": assembly._display_components["vendor_pcb_underside_above_feet_mm"],
                  "measured_pcb_underside_above_feet_mm": assembly.display_pcb_bottom_z,
                  "scope": "Conservative component envelopes from the vendor STEP, with PCB-mounted components "
                           "lowered by the caliper PCB-height correction; feet preserve their measured datum. "
                           "Actual component and tube tolerances remain a bench check."},
              "checks": reading.rows, "printing": print_reading(f, parts),
              "physical_checks_remaining": [
                  "Actual harvested lever dimensions, hand approach and full motion in printed parts.",
                  "PET-GF print strength, curved-joint fit and retention, and heat-set insert installation.",
                  "Support access and contact finish from a production-profile slice and physical print.",
                  "Tube feeding, flow, actual tube/display separation, cable routing and splash drainage.",
                  "PET-GF snap seating and pull-off force, root strength, repeated closure and release in the complete display fit trial."],
              "passed": passed}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(f"{'PASS' if passed else 'FAIL'} faucet geometry: {len(reading.rows)} readings; {args.output}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
