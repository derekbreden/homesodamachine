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


def lower_access_reading(reading, f, base):
    """Actual cheek stock and the continuous bridge above the lever opening."""
    import cadquery as cq
    base = shape(base)
    wall = f.wall_thickness_min
    cheek_rows = []
    for face in shape(f.build_zone3_inner_cut()).Faces():
        if face.geomType() != "PLANE" or abs(face.normalAt().x) < 0.999999:
            continue
        x = face.Center().x
        if abs(abs(x) - f.shell_arch_bore_outer_x) > DISTANCE_TOLERANCE:
            continue
        direction = cq.Vector(math.copysign(wall, x), 0.0, 0.0)
        witness = cq.Solid.extrudeLinear(face.outerWire(), face.innerWires(), direction)
        missing = volume(witness.cut(base))
        cheek_rows.append({"cavity_face_x_mm": clean_number(x),
                           "witness_volume_mm3": clean_number(volume(witness)),
                           "missing_witness_mm3": clean_number(missing)})
    reading.add("wall:lever-cheek",
                len(cheek_rows) == 2 and all(row["missing_witness_mm3"] <= VOLUME_TOLERANCE
                                           for row in cheek_rows),
                method="complete outward extrusion of each donor-arch cavity outer face into the finished base",
                required_outward_stock_mm=wall, samples=cheek_rows,
                scope="the two outer cheeks over the complete donor-arch footprint")

    ceiling_faces = [face for face in shape(f.build_lever_clearance()).Faces()
                     if face.geomType() == "PLANE" and face.normalAt().z > 0.999999]
    if not ceiling_faces:
        reading.add("wall:lever-roof-bridge", False, reason="the lever clearance has no horizontal ceiling")
        reading.add("section:lever-roof-continuity", False, reason="no lever ceiling datum")
        return
    ceiling = max(ceiling_faces, key=lambda face: face.Area())
    roof_z = ceiling.Center().z
    rear_y = ceiling.BoundingBox().ymax - DISTANCE_TOLERANCE
    front_y = rear_y - 2.0 * wall
    half_width = f.lever_x_half
    witness = (cq.Workplane("XY").workplane(offset=roof_z)
               .center(0.0, (front_y + rear_y) / 2.0)
               .rect(2.0 * half_width, rear_y - front_y).extrude(wall).val())
    missing = volume(witness.cut(base))
    reading.add("wall:lever-roof-bridge", missing <= VOLUME_TOLERANCE,
                method="complete vertical wall witness above the rear two wall-widths of the actual flat lever ceiling",
                bounds_mm=[-half_width, half_width, clean_number(front_y), clean_number(rear_y),
                           clean_number(roof_z), clean_number(roof_z + wall)],
                required_vertical_stock_mm=wall, missing_witness_mm3=clean_number(missing),
                scope="the bridge from the lever roof into the neck; not every exterior opening edge")
    samples = []
    for x in (-half_width, 0.0, half_width):
        for y in (front_y, rear_y - wall, rear_y):
            spans = line_intervals(base, (x, y, roof_z + DISTANCE_TOLERANCE),
                                   (0.0, 0.0, 1.0), 2.0 * wall)
            continuous = (len(spans) == 1 and spans[0][0] <= DISTANCE_TOLERANCE
                          and spans[0][1] - spans[0][0] >= wall - DISTANCE_TOLERANCE)
            samples.append({"x_mm": clean_number(x), "y_mm": clean_number(y),
                            "material_intervals_above_roof_mm":
                                [[clean_number(a), clean_number(b)] for a, b in spans],
                            "continuous": continuous})
    reading.add("section:lever-roof-continuity", all(row["continuous"] for row in samples),
                method="nine exact vertical B-rep chords from the lever ceiling through two wall-widths of roof and neck",
                roof_z_mm=clean_number(roof_z), probe_height_mm=2.0 * wall,
                minimum_continuous_stock_mm=wall, samples=samples,
                scope="no separated upper slit in the roof-to-neck bridge; exterior rays may end at the show surface")


def display_retention_reading(reading, f, parts, body, screen, ribbon, tubes):
    """Actual cover-lip capture and clearance demand, without an elastic model."""
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    from OCP.BRepBndLib import BRepBndLib
    from OCP.Bnd import Bnd_Box
    snap = f._display_snap
    full = cq.Compound.makeCompound([shape(parts["shell_base"]), shape(parts["shell_tip"])])
    tip, cover = shape(parts["shell_tip"]), shape(parts["display_cover"])
    body, ribbon = shape(body), shape(ribbon)
    origin, along, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    lips = shape(f.build_display_cover_lips())
    outside = shape(f.build_display_outer_envelope())
    outside_faces = cq.Compound.makeCompound([face for face in outside.Faces()
                                             if face.geomType() != "PLANE"])
    s0, s1 = f.display_clip_s_bottom, f.display_clip_s_top
    n0, n1 = f.display_clip_bottom_n, f.display_clip_top_n

    def band(a, b, low, high):
        return shape(f._cradle_prism(f.display_cover_skirt_width, a, b, low, high))

    def half(part, side):
        native = cq.Solid.makeBox(50.0, 200.0, 150.0,
                                 cq.Vector(0.0 if side == 1 else -50.0, -50.0, -50.0))
        return shape(part).intersect(shape(f._display_world(cq.Workplane(obj=native))))

    def local_bounds(part):
        box = Bnd_Box()
        BRepBndLib.AddOptimal_s(shape(part).moved(frame.inverse).wrapped,
                              box, False, False)
        return cq.BoundBox(box)

    def radius(face):
        surface = BRepAdaptor_Surface(face.wrapped)
        if face.geomType() == "CYLINDER":
            return surface.Cylinder().Radius()
        if face.geomType() == "TORUS":
            return surface.Torus().MinorRadius()
        return None

    def contact(first, second):
        return volume(shape(first).intersect(shape(second)))

    def outside_volume(part, allowed):
        return volume(shape(part).cut(shape(allowed))) if volume(part) > VOLUME_TOLERANCE else 0.0

    def lip_radii(part):
        return sorted({clean_number(r) for face in shape(part).Faces()
                       if (r := radius(face)) is not None})

    lower_skirts = cover.intersect(band(f.display_head_s_min, f.display_head_s_max + 1.0,
                                       n0, f.display_cover_shoulder_n))
    skirts = {side: half(lower_skirts, side) for side in (-1, 1)}
    lip_parts = {side: half(lips, side) for side in (-1, 1)}
    groove_band = band(s0-snap.END_SLIP, s1+snap.END_SLIP, n0, n1+snap.BEARING_SLIP)
    groove_core = shape(f._build_zone6_outer_shrunk(f.tube_shell_outer_r-f.display_clip_groove_radius))
    backed_core = shape(f._build_zone6_outer_shrunk(
        f.tube_shell_outer_r-f.display_clip_groove_radius+f.wall_thickness_min))
    backing = groove_core.cut(backed_core).intersect(groove_band)
    groove_faces = []
    for face in tip.Faces():
        r = radius(face)
        if r is not None and abs(r-f.display_clip_groove_radius) < DISTANCE_TOLERANCE:
            b = local_bounds(face)
            if b.ymin >= s0-snap.END_SLIP-DISTANCE_TOLERANCE and b.ymax <= s1+snap.END_SLIP+DISTANCE_TOLERANCE:
                groove_faces.append(face)
    for side in (-1, 1):
        lip = lip_parts[side]
        missing = volume(lip.cut(cover))
        native_lip = lip.moved(frame.inverse)
        lip_chords = []
        for fraction in (0.001, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 0.999):
            station = s0+(s1-s0)*fraction
            spans = line_intervals(native_lip, (0.0, station, (n0+n1)/2.0),
                                   (side, 0.0, 0.0), 30.0)
            x = side*sum(spans[0])/2.0 if spans else 0.0
            chords = line_intervals(native_lip, (x, station, n0-0.1), (0.0, 0.0, 1.0),
                                    snap.LIP_HEIGHT+0.2)
            stock = sum(b-a for a, b in chords)
            lip_chords.append({"x_mm": clean_number(x), "s_mm": clean_number(station),
                               "normal_stock_mm": clean_number(stock)})
        inner_faces = [face for face in lip.Faces() if radius(face) is not None]
        radial_stock = (cq.Compound.makeCompound(inner_faces).distance(outside_faces)
                        if inner_faces else 0.0)
        b = local_bounds(lip)
        reading.add(f"wall:cover-lip-{side:+d}", lip.isValid() and len(lip.Solids()) == 1
                    and missing <= VOLUME_TOLERANCE
                    and all(row["normal_stock_mm"] >= 1.0-DISTANCE_TOLERANCE for row in lip_chords)
                    and radial_stock >= 1.0-DISTANCE_TOLERANCE,
                    missing_lip_from_cover_mm3=clean_number(missing),
                    sampled_normal_chords=lip_chords,
                    measured_normal_height_mm=clean_number(b.zlen),
                    minimum_inner_surface_to_outer_skin_mm=clean_number(radial_stock),
                    required_mm=1.0,
                    method="complete lip containment in the cover, nine exact interior normal chords per side, and complete curved-side separation")
        witness = half(backing, side)
        missing = volume(witness.cut(tip))
        reading.add(f"wall:retention-groove-{side:+d}", volume(witness) > VOLUME_TOLERANCE
                    and missing <= VOLUME_TOLERANCE,
                    missing_complete_radial_backing_mm3=clean_number(missing),
                    required_radial_backing_mm=f.wall_thickness_min,
                    method="complete three-millimeter annular witness behind the actual swept groove, including its rear torus section")
        faces = [face for face in groove_faces if side*face.Center().x > 0.0]
        if faces:
            gb = local_bounds(cq.Compound.makeCompound(faces))
            groove_r = min(radius(face) for face in faces)
            lip_r = min(lip_radii(lip))
            bearing = gb.zmax-b.zmax
            floor_gap = b.zmin-gb.zmin
            end_gaps = [b.ymin-gb.ymin, gb.ymax-b.ymax]
        else:
            groove_r = lip_r = bearing = floor_gap = 0.0
            end_gaps = [-1.0, -1.0]
        engagement = f.tube_shell_outer_r-lip_r
        radial_slip = lip_r-groove_r
        reading.add(f"snap:engagement-{side:+d}", bool(faces)
                    and abs(engagement-snap.ENGAGEMENT) < DISTANCE_TOLERANCE
                    and abs(radial_slip-snap.RADIAL_SLIP) < DISTANCE_TOLERANCE
                    and abs(bearing-snap.BEARING_SLIP) < DISTANCE_TOLERANCE
                    and abs(floor_gap) < DISTANCE_TOLERANCE
                    and all(abs(gap-snap.END_SLIP) < DISTANCE_TOLERANCE for gap in end_gaps),
                    measured_radial_engagement_mm=clean_number(engagement),
                    measured_radial_clearance_mm=clean_number(radial_slip),
                    measured_normal_bearing_gap_mm=clean_number(bearing),
                    measured_floor_gap_mm=clean_number(floor_gap),
                    measured_end_gaps_mm=[clean_number(gap) for gap in end_gaps],
                    method="actual lip and groove cylinder/torus radii and clipped face extents in the display frame")

    seated_overlap = contact(cover, full)
    reading.add("seat:display-cover", seated_overlap <= VOLUME_TOLERANCE,
                overlap_mm3=clean_number(seated_overlap),
                method="exact common volume at the designed lip-floor contact pose")
    pushed = cover.translate(normal.multiply(-0.01))
    pushed_lips = lips.translate(normal.multiply(-0.01))
    seat_common = pushed.intersect(full)
    seat_other = volume(seat_common.cut(pushed_lips))
    seat_floor = tip.intersect(band(s0, s1, n0-0.01-DISTANCE_TOLERANCE, n0+DISTANCE_TOLERANCE)).cut(groove_core)
    outside_floor = volume(seat_common.cut(seat_floor))
    glass = shape(screen)
    reading.add("seat:display-cover-stop", volume(seat_common) > VOLUME_TOLERANCE
                and max(seat_other, outside_floor, contact(pushed, body), contact(pushed, glass)) <= VOLUME_TOLERANCE,
                fixed_body_interference_after_0_01mm_inward_motion_mm3=clean_number(volume(seat_common)),
                contact_outside_actual_lips_mm3=clean_number(seat_other),
                contact_outside_groove_floor_mm3=clean_number(outside_floor),
                device_interference_mm3=clean_number(contact(pushed, body)),
                glass_interference_mm3=clean_number(contact(pushed, glass)),
                method="actual lip bottoms contact only the shallow groove floors before the display or glass")
    lifted = cover.translate(normal.multiply(0.5))
    retention_common = lifted.intersect(full)
    shoulder = tip.intersect(band(s0, s1, n1+snap.BEARING_SLIP-DISTANCE_TOLERANCE,
                                  n1+0.5+DISTANCE_TOLERANCE)).cut(groove_core)
    outside_lips = volume(retention_common.cut(lips.translate(normal.multiply(0.5))))
    outside_shoulder = volume(retention_common.cut(shoulder))
    reading.add("retention:display-snaps", volume(retention_common) > VOLUME_TOLERANCE
                and max(outside_lips, outside_shoulder) <= VOLUME_TOLERANCE,
                interference_on_0_5mm_outward_lift_mm3=clean_number(volume(retention_common)),
                contact_outside_actual_lips_mm3=clean_number(outside_lips),
                contact_outside_retaining_shoulders_mm3=clean_number(outside_shoulder),
                scope="geometric cover-lip capture only; PET-GF force, flex distribution and cycling require the complete print trial")

    # This measures clearance demand by translating only each actual lower
    # skirt outwards. It is not a deformed-cover model or an elastic solution.
    search_limit = snap.ENGAGEMENT+snap.RADIAL_SLIP
    resolution = 0.0001
    hardware = {"display": body, "glass": glass, "ribbon": ribbon,
                **{name: shape(part) for name, part in tubes.items()}}
    hardware_bounds = {name: local_bounds(part) for name, part in hardware.items()}
    travel = {name: {"overlap": 0.0, "gap": float("inf")} for name in hardware}
    rows = []
    lifts = sorted({0.0, 0.10, snap.BEARING_SLIP, snap.BEARING_SLIP+0.001,
                    snap.BEARING_SLIP+0.01, snap.BEARING_SLIP+0.05, 0.35, 0.50, 0.75,
                    1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 8.0, 10.0, 12.0, 15.0, 20.0})
    for lift in lifts:
        moved = cover.translate(normal.multiply(lift))
        common = moved.intersect(full)
        row = {"normal_lift_mm": lift, "unflexed_body_interference_mm3": clean_number(volume(common)),
               "contact_outside_actual_lips_mm3": clean_number(outside_volume(common, lips.translate(normal.multiply(lift)))),
               "contact_outside_lower_skirts_mm3": clean_number(outside_volume(common, lower_skirts.translate(normal.multiply(lift)))),
               "sides": []}
        hardware_poses = [moved]
        for side in (-1, 1):
            skirt = skirts[side].translate(normal.multiply(lift))
            low, high = 0.0, search_limit
            first = contact(skirt, full)
            if first <= VOLUME_TOLERANCE:
                high = 0.0
            elif contact(skirt.translate((side*high, 0.0, 0.0)), full) <= VOLUME_TOLERANCE:
                while high-low > resolution:
                    mid = (low+high)/2.0
                    if contact(skirt.translate((side*mid, 0.0, 0.0)), full) <= VOLUME_TOLERANCE:
                        high = mid
                    else:
                        low = mid
            remaining = contact(skirt.translate((side*high, 0.0, 0.0)), full)
            row["sides"].append({"side": side, "required_outward_clearance_mm": clean_number(high),
                                  "remaining_body_interference_mm3": clean_number(remaining)})
            hardware_poses.extend(skirt.translate((side*high*fraction, 0.0, 0.0))
                                  for fraction in (0.5, 1.0))
        posed = [(pose, local_bounds(pose)) for pose in hardware_poses]
        for name, obstacle in hardware.items():
            ob = hardware_bounds[name]
            required = 0.1 if name == "ribbon" else 0.0
            for pose, pb in posed:
                # Disjoint conservative boxes prove separation. Overlapping
                # boxes never excuse a collision: use the exact common, or
                # exact distance when the ribbon's positive gap is required.
                gaps = [max(0.0, getattr(pb, axis+"min")-getattr(ob, axis+"max"),
                            getattr(ob, axis+"min")-getattr(pb, axis+"max")) for axis in "xyz"]
                gap = math.sqrt(sum(value*value for value in gaps))
                if gap > required+DISTANCE_TOLERANCE:
                    overlap = 0.0
                elif required == 0.0:
                    overlap = contact(pose, obstacle)
                else:
                    distance = BRepExtrema_DistShapeShape(pose.wrapped, obstacle.wrapped)
                    if not distance.IsDone():
                        raise RuntimeError("cover travel: exact hardware distance did not complete")
                    gap = distance.Value()
                    overlap = contact(pose, obstacle) if gap <= DISTANCE_TOLERANCE or distance.InnerSolution() else 0.0
                travel[name]["gap"] = min(travel[name]["gap"], gap)
                travel[name]["overlap"] = max(travel[name]["overlap"], overlap)
        rows.append(row)
        print(f"  cover normal lift {lift:g} mm: outward demands "
              + ", ".join(f"{side['required_outward_clearance_mm']:.4f}" for side in row["sides"]) + " mm", flush=True)
    peak = max(side["required_outward_clearance_mm"] for row in rows for side in row["sides"])
    reading.add("motion:display-cover-normal", all(
                    max(row["contact_outside_actual_lips_mm3"], row["contact_outside_lower_skirts_mm3"],
                        *(side["remaining_body_interference_mm3"] for side in row["sides"])) <= VOLUME_TOLERANCE
                    for row in rows),
                samples=rows, peak_required_outward_clearance_per_side_mm=clean_number(peak),
                outward_search_budget_mm=clean_number(search_limit), clearance_search_resolution_mm=resolution,
                scope="sampled normal insertion; all unflexed contact must be in actual lips on actual lower skirts; outward translation measures the skirts' geometric clearance demand, not deformation, strain or insertion force")
    for name, result in travel.items():
        required = 0.1 if name == "ribbon" else 0.0
        reading.add(f"clearance:snap-travel-{name}", result["overlap"] <= VOLUME_TOLERANCE
                    and result["gap"] >= required-DISTANCE_TOLERANCE,
                    maximum_sampled_overlap_mm3=clean_number(result["overlap"]),
                    minimum_sampled_gap_lower_bound_mm=clean_number(result["gap"]), required_gap_mm=required,
                    method="complete cover at every normal station plus both actual lower skirts at half and full measured outward travel; exact commons or distance, with conservative box separation where available")

    display_rigid_neck_reading(reading, f, tip)


def display_rigid_neck_reading(reading, f, part):
    """Verify the rigid cylinder outside the groove and the open device pocket."""
    import cadquery as cq
    tip = shape(part)
    origin, along, normal = f._tip_frame()

    def band(a, b, low, high):
        return shape(f._cradle_prism(f.display_cover_skirt_width, a, b, low, high))

    neck_outer = shape(f._build_zone6_outer_shrunk(0.0))
    # Keep the complete volume witness inside the exact show surface and away
    # from coplanar opening/groove boundaries. Independent exact chords below
    # require the real exterior endpoint and a full millimeter of material.
    surface_inset, edge_inset, depth = 0.01, 0.02, 1.0
    skin_outer = shape(f._build_zone6_outer_shrunk(surface_inset))
    skin_inner = shape(f._build_zone6_outer_shrunk(depth))
    restored = skin_outer.cut(skin_inner).intersect(
        band(f.display_s_bottom+edge_inset, f.display_s_top-edge_inset,
             f.display_clip_top_n+f._display_snap.BEARING_SLIP+edge_inset,
             f.display_feet_n-edge_inset))
    missing_skin = volume(restored.cut(tip))
    samples = []
    for station in (2.0, 6.0, 10.0, 13.573, 20.0, 26.0, 30.0, 34.0, 40.0, 44.0):
        for n in (5.0, 7.0, 9.0):
            point = (origin+along.multiply(station)+normal.multiply(n)).toTuple()
            for side in (-1, 1):
                expected = line_intervals(neck_outer, point, (side, 0.0, 0.0), 25.0)
                actual = line_intervals(tip, point, (side, 0.0, 0.0), 25.0)
                stock = actual[-1][1]-actual[-1][0] if actual else 0.0
                endpoint_error = (abs(actual[-1][1]-expected[-1][1])
                                  if actual and expected else 25.0)
                samples.append({"s_mm": station, "n_mm": n, "side": side,
                                "outer_endpoint_error_mm": clean_number(endpoint_error),
                                "continuous_stock_mm": clean_number(stock)})
    head_region = band(f.display_s_bottom, f.display_s_top,
                       f.display_clip_bottom_n, f.display_cover_top_n+1.0)
    beyond_neck = volume(tip.intersect(head_region).cut(neck_outer))
    upper = band(f.display_s_bottom, f.display_s_top, f.display_feet_n+DISTANCE_TOLERANCE,
                 f.display_cover_top_n+1.0)
    upper_fins = volume(tip.intersect(upper))
    reading.add("shape:display-rigid-neck", restored.isValid() and volume(restored) > VOLUME_TOLERANCE
                and max(missing_skin, beyond_neck, upper_fins) <= VOLUME_TOLERANCE
                and all(row["outer_endpoint_error_mm"] <= DISTANCE_TOLERANCE
                        and row["continuous_stock_mm"] >= depth-DISTANCE_TOLERANCE for row in samples),
                missing_complete_subsurface_witness_mm3=clean_number(missing_skin),
                radial_witness_range_below_exterior_mm=[surface_inset, depth],
                witness_open_boundary_inset_mm=edge_inset, exterior_sections=samples,
                required_continuous_chord_stock_mm=depth,
                material_beyond_swept_cylinder_mm3=clean_number(beyond_neck),
                upper_device_opening_material_mm3=clean_number(upper_fins),
                method="complete swept subsurface witness above the grooves, exact exterior endpoints and continuous material on 60 chords, no material beyond the original cylinder, and the complete full-width opening above the feet")


def display_rim_reading(reading, f, part):
    """Read actual post-trim corner stock, including the neck-clearance rim."""
    import cadquery as cq
    from OCP.BRepAlgoAPI import BRepAlgoAPI_Section
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    cover = shape(part).moved(frame.inverse)
    outside = shape(f.build_display_outer_envelope()).moved(frame.inverse)
    faces = outside.Faces()
    samples, sections = [], []
    # These fore/aft stations cover both ends of the skirt's rounded corners;
    # their normal probes detected the original neck-cut feathered material.
    for station in (0.5, 1.0, 2.0, 4.0, 6.0, 42.0, 44.0, 46.0, 48.0):
        plane = cq.Plane(origin=(0.0, station, 0.0), xDir=(1.0, 0.0, 0.0), normal=(0.0, 1.0, 0.0))
        section_face = cq.Face.makeFromWires(cq.Workplane(plane).rect(100.0, 100.0).val())
        section = cover.intersect(section_face)
        if not section.Edges():
            sections.append({"s_mm": station, "present": False, "probe_count": 0})
            continue
        bottom = section.BoundingBox().zmin
        before = len(samples)
        for rise in (0.25, 0.5, 1.0, 2.0, 3.0):
            n = bottom+rise
            for side in (-1, 1):
                intervals = line_intervals(cover, (0.0, station, n), (side, 0.0, 0.0), 30.0)
                if not intervals:
                    continue
                p = cq.Vector(side*intervals[-1][1], station, n)
                vertex = cq.Vertex.makeVertex(*p.toTuple())
                face = min(faces, key=lambda candidate: candidate.distance(vertex))
                outer_distance = face.distance(vertex)
                normal = face.normalAt(p)
                if side*normal.x < 0.0:
                    normal = normal.multiply(-1.0)
                start = p-normal.multiply(DISTANCE_TOLERANCE)
                chords = line_intervals(cover, start.toTuple(), normal.multiply(-1.0).toTuple(), 6.0)
                stock = chords[0][1]+DISTANCE_TOLERANCE if chords and chords[0][0] < 0.001 else 0.0
                samples.append({"point_x_s_n_mm": [clean_number(v) for v in p.toTuple()],
                                "outer_face_distance_mm": clean_number(outer_distance),
                                "section_rim_n_mm": clean_number(bottom),
                                "rise_above_section_rim_mm": rise,
                                "normal_inward": [clean_number(v) for v in normal.multiply(-1.0).toTuple()],
                                "normal_stock_mm": clean_number(stock)})
        sections.append({"s_mm": station, "present": True, "probe_count": len(samples)-before})
    least = min((row["normal_stock_mm"] for row in samples), default=0.0)
    reading.add("wall:display-finished-neck-rim", bool(samples) and least >= 1.0-DISTANCE_TOLERANCE
                and all(row["outer_face_distance_mm"] <= DISTANCE_TOLERANCE for row in samples)
                and all(row["present"] and row["probe_count"] > 0 for row in sections),
                minimum_sampled_normal_stock_mm=clean_number(least), required_mm=1.0,
                sections=sections, samples=samples,
                method="exact finished-cover sections at nine fore/aft stations; inward normal material chords on both sides at five heights above each actual lower edge",
                scope="sampled neck-rim and corner stock after all cuts, separate from untrimmed loft separation; not a global minimum-wall certificate")

    front_samples = []
    for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
        spans = line_intervals(cover, (x, DISTANCE_TOLERANCE, 0.0), (0.0, 0.0, 1.0),
                               f.display_cover_top_n+1.0)
        for bottom, top in spans:
            heights = {bottom+0.05, bottom+0.25, bottom+0.5, (bottom+top)/2.0, top-0.05}
            for n in sorted(value for value in heights if bottom < value < top):
                chords = line_intervals(cover, (x, DISTANCE_TOLERANCE, n), (0.0, 1.0, 0.0), 6.0)
                stock = chords[0][1]+DISTANCE_TOLERANCE if chords and chords[0][0] < 0.001 else 0.0
                front_samples.append({"x_mm": x, "n_mm": clean_number(n),
                                      "axial_stock_mm": clean_number(stock)})
    least_front = min((row["axial_stock_mm"] for row in front_samples), default=0.0)
    reading.add("wall:display-flush-front", bool(front_samples)
                and {row["x_mm"] for row in front_samples} == {-6.0, -3.0, 0.0, 3.0, 6.0}
                and least_front >= f.dispense_face_thickness-DISTANCE_TOLERANCE,
                minimum_sampled_axial_stock_mm=clean_number(least_front),
                required_mm=f.dispense_face_thickness, samples=front_samples,
                method="exact inward +S material chords at five X stations, from each actual lower rim through the crown of the flush front wall")

    outer_surfaces = cq.Compound.makeCompound(faces)
    retained_skin_faces = [face for face in cover.Faces()
                           if face.geomType() == "BSPLINE" and face.Vertices()
                           and all(outer_surfaces.distance(vertex) <= DISTANCE_TOLERANCE
                                   for vertex in face.Vertices())]
    retained_skin = cq.Compound.makeCompound(retained_skin_faces)
    rear_samples, rear_sections = [], []
    for x in (-6.0, -3.0, 0.0, 3.0, 6.0):
        s0, s1 = f._display_housing_center_s, f.display_head_s_max+1.0
        plane = cq.Plane(origin=(x, (s0+s1)/2.0, f.display_cover_top_n/2.0),
                         xDir=(0.0, 1.0, 0.0), normal=(1.0, 0.0, 0.0))
        face = cq.Face.makeFromWires(cq.Workplane(plane)
                                    .rect(s1-s0, f.display_cover_top_n+2.0).val())
        operation = BRepAlgoAPI_Section(retained_skin.wrapped, face.wrapped)
        if not operation.IsDone():
            raise RuntimeError("rear cover rim: exact outer-skin section failed")
        section = cq.Shape.cast(operation.Shape())
        if not section.Edges():
            rear_sections.append({"x_mm": x, "present": False, "probe_count": 0})
            continue
        box = section.BoundingBox()
        bottom, top = box.zmin, box.zmax
        heights = sorted({min(bottom+rise, top-0.01) for rise in (0.01, 0.1, 0.25, 0.5, 1.0, 2.0, 3.0)})
        before = len(rear_samples)
        for n in heights:
            spans = line_intervals(cover, (x, s0, n), (0.0, 1.0, 0.0), s1-s0)
            if not spans:
                continue
            point = cq.Vector(x, s0+spans[-1][1], n)
            vertex = cq.Vertex.makeVertex(*point.toTuple())
            outer_face = min(faces, key=lambda candidate: candidate.distance(vertex))
            outer_distance = outer_face.distance(vertex)
            outward = outer_face.normalAt(point)
            start = point-outward.multiply(DISTANCE_TOLERANCE)
            chords = line_intervals(cover, start.toTuple(), outward.multiply(-1.0).toTuple(), 6.0)
            stock = chords[0][1]+DISTANCE_TOLERANCE if chords and chords[0][0] < 0.001 else 0.0
            rear_samples.append({"point_x_s_n_mm": [clean_number(v) for v in point.toTuple()],
                                 "actual_outer_rim_n_mm": clean_number(bottom),
                                 "rise_above_outer_rim_mm": clean_number(n-bottom),
                                 "outer_face_distance_mm": clean_number(outer_distance),
                                 "normal_inward": [clean_number(v) for v in outward.multiply(-1.0).toTuple()],
                                 "normal_stock_mm": clean_number(stock)})
        rear_sections.append({"x_mm": x, "present": True, "probe_count": len(rear_samples)-before})
    least_rear = min((row["normal_stock_mm"] for row in rear_samples), default=0.0)
    reading.add("wall:display-rear-rim", bool(rear_samples) and least_rear >= 1.0-DISTANCE_TOLERANCE
                and all(row["present"] and row["probe_count"] > 0 for row in rear_sections)
                and all(row["outer_face_distance_mm"] <= DISTANCE_TOLERANCE for row in rear_samples),
                minimum_sampled_normal_stock_mm=clean_number(least_rear), required_mm=1.0,
                sections=rear_sections, samples=rear_samples,
                method="exact retained outer-skin sections at X0/±3/±6, then inward surface-normal chords 0.01 to 3 mm above the actual rear rim through the crown",
                scope="the rear central cover bridge; axial chords alone do not certify a tilted wall")


def display_reading(reading, f, assembly, parts, body):
    import cadquery as cq
    full = cq.Compound.makeCompound([shape(parts["shell_base"]), shape(parts["shell_tip"])])
    tip, cover, body = shape(parts["shell_tip"]), shape(parts["display_cover"]), shape(body)
    origin, tangent, normal = f._tip_frame()
    ribbon = shape(assembly.build_display_ribbon())
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

    display_retention_reading(reading, f, parts, body, assembly.build_display_screen(), ribbon, tubes)
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
    display_rim_reading(reading, f, cover)
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
    cap = shape(f._cradle_prism(f.signal_lane_width/2.0, 0.0, f.dispense_face_thickness,
                              f.signal_lane_center_n-f.signal_lane_depth/2.0,
                              f.signal_lane_center_n+f.signal_lane_depth/2.0))
    cap = cap.cut(shape(f.build_zone6_inner_cut()))
    missing = volume(cap.cut(tip))
    face_slab = shape(f._cradle_prism(25.0, -0.001, 0.001, -20.0, 30.0))
    signal_at_face = volume(face_slab.intersect(shape(f.build_signal_neck_inner_cut())))
    reading.add("wall:outlet-signal-closure", missing <= VOLUME_TOLERANCE and signal_at_face <= VOLUME_TOLERANCE,
                missing_full_thickness_cap_mm3=clean_number(missing),
                required_axial_thickness_mm=f.dispense_face_thickness,
                signal_void_at_outlet_mm3=clean_number(signal_at_face),
                method="full-thickness closure witness above the flavor passage and the neck signal cutter at the outlet plane")
    front_slab = shape(f._cradle_prism(30.0, 0.0, f.dispense_face_thickness, -30.0, 40.0))
    front_stock = shape(f.build_zone6_outer()).intersect(front_slab).cut(shape(f.build_zone6_inner_cut()))
    missing_front = volume(front_stock.cut(tip))
    back_faces = [face for face in tip.Faces() if face.geomType() == "PLANE"
                  and face.normalAt().dot(tangent) > 0.999999
                  and 0.0 < (face.Center()-origin).dot(tangent) < f.dispense_face_thickness+0.5]
    back_stations = [(face.Center()-origin).dot(tangent) for face in back_faces]
    reading.add("wall:dispense-face", missing_front <= VOLUME_TOLERANCE and bool(back_faces)
                and all(abs(station-f.dispense_face_thickness) < DISTANCE_TOLERANCE for station in back_stations),
                required_axial_thickness_mm=f.dispense_face_thickness,
                missing_complete_front_stock_mm3=clean_number(missing_front),
                cavity_rear_face_stations_mm=[clean_number(v) for v in back_stations],
                method="complete 2 mm cylinder-minus-tube-passages witness, with a common planar cavity face behind it")


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
    reading.add("position:signal-southwest", f.display_ribbon_side_x < 0.0
                and f.display_ribbon_terminal_s < f._display_housing_center_s,
                ribbon_end_native_display_xy_mm=[f.display_ribbon_side_x, f.display_ribbon_terminal_y],
                scope="the unrestrained ribbon ends before solder fan-out in the southwest quadrant viewed from the glass")
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
    lower_access_reading(reading, f, base)
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
                  "PET-GF cover-wall spreading, seating and pull-off force, lip strength, repeated closure and release in the complete display fit trial."],
              "passed": passed}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(f"{'PASS' if passed else 'FAIL'} faucet geometry: {len(reading.rows)} readings; {args.output}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
