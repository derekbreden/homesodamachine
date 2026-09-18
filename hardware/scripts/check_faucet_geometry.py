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


def outside_material_volume(part, allowed) -> float:
    """Solid volume outside a mask, ignoring contact-only faces and edges."""
    import cadquery as cq
    solids, allowed_solids = shape(part).Solids(), shape(allowed).Solids()
    total = sum(solid.Volume() for solid in solids)
    if total <= VOLUME_TOLERANCE:
        return 0.0
    if not allowed_solids:
        return total
    material = solids[0] if len(solids) == 1 else cq.Compound.makeCompound(solids)
    mask = allowed_solids[0] if len(allowed_solids) == 1 else cq.Compound.makeCompound(allowed_solids)
    outside = total-volume(material.intersect(mask))
    if outside < -VOLUME_TOLERANCE:
        raise RuntimeError("allowed contact common exceeds the original material volume")
    return max(0.0, outside)


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


def open_lower_rim_evidence(part, f, point, inward, chord):
    """Qualify a normal ray truncated by the intentional flat lower opening."""
    import cadquery as cq
    bottom = f.display_cover_bottom_n
    exit_point = point+inward.multiply(chord)
    if (point.y < (f.display_cover_rear_rim_s0+f.display_cover_rear_rim_ds_dn*f.display_cover_bottom_n)-DISTANCE_TOLERANCE
            or abs(exit_point.z-bottom) > DISTANCE_TOLERANCE
            or abs(point.x) < DISTANCE_TOLERANCE):
        return None
    side = math.copysign(1.0, point.x)
    rim_spans = line_intervals(part, (0.0, point.y, bottom+DISTANCE_TOLERANCE),
                               (side, 0.0, 0.0), 30.0)
    rim_stock = rim_spans[-1][1]-rim_spans[-1][0] if rim_spans else 0.0
    # Move far enough above the rim that a full wall-normal chord can reach the
    # inner surface. Recompute both the actual surface point and its normal.
    high_n = max(point.z+0.5,
                 bottom+(f.display_cosmetic_wall+0.5)*abs(inward.z)+0.2)
    spans = line_intervals(part, (0.0, point.y, high_n), (side, 0.0, 0.0), 30.0)
    high_stock, high_exits_rim = 0.0, True
    if spans:
        high_point = cq.Vector(side*spans[-1][1], point.y, high_n)
        vertex = cq.Vertex.makeVertex(*high_point.toTuple())
        face = min(shape(part).Faces(), key=lambda candidate: candidate.distance(vertex))
        outward = face.normalAt(high_point)
        if side*outward.x < 0.0:
            outward = outward.multiply(-1.0)
        start = high_point-outward.multiply(DISTANCE_TOLERANCE)
        high_spans = line_intervals(part, start.toTuple(), outward.multiply(-1.0).toTuple(), 6.0)
        high_stock = (high_spans[0][1]+DISTANCE_TOLERANCE
                      if high_spans and high_spans[0][0] < 0.001 else 0.0)
        high_exit = high_point-outward.multiply(high_stock)
        high_exits_rim = abs(high_exit.z-bottom) <= DISTANCE_TOLERANCE
    return {"normal_chord_exits_flat_open_rim": True,
            "exit_x_s_n_mm": [clean_number(v) for v in exit_point.toTuple()],
            "rim_section_n_mm": clean_number(bottom+DISTANCE_TOLERANCE),
            "actual_lateral_rim_stock_mm": clean_number(rim_stock),
            "elevated_probe_n_mm": clean_number(high_n),
            "elevated_normal_stock_mm": clean_number(high_stock),
            "elevated_chord_exits_rim": high_exits_rim,
            "passed": min(rim_stock, high_stock) >= 1.0-DISTANCE_TOLERANCE
                      and not high_exits_rim}


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
                    tolerance_is_relative=False,
                    scope="live B-rep tessellated, serialized as STL and loaded again; not a slicer result")


def lower_outer_mesh_reading(reading, f, mesh_path: Path | None = None):
    """Measure the saved base mesh against analytic, uncut outer loft points."""
    import numpy as np
    import trimesh
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepTools import BRepTools

    mesh_path = Path(mesh_path) if mesh_path is not None else SHELL / "faucet-shell-base.stl"
    payload = mesh_path.read_bytes()
    mesh = trimesh.load_mesh(io.BytesIO(payload), file_type="stl")
    samples, faces = [], []
    u_count, v_count, batch_size = 41, 51, 128
    for index, face in enumerate(shape(f.build_lower_outer()).Faces()):
        if face.geomType() != "BSPLINE":
            continue
        u0, u1, v0, v1 = BRepTools.UVBounds_s(face.wrapped)
        surface = BRepAdaptor_Surface(face.wrapped)
        before = len(samples)
        for u in np.linspace(u0, u1, u_count):
            for v in np.linspace(v0, v1, v_count):
                point = surface.Value(float(u), float(v))
                xyz = (point.X(), point.Y(), point.Z())
                if abs(xyz[0]) > 10.0 and 2.0 < xyz[2] < 63.0:
                    samples.append(xyz)
        faces.append({"face_index": index,
                      "uv_bounds": [clean_number(value) for value in (u0, u1, v0, v1)],
                      "selected_points": len(samples)-before})
    points = np.asarray(samples, dtype=float).reshape((-1, 3))
    distances = []
    for start in range(0, len(points), batch_size):
        _, measured, _ = trimesh.proximity.closest_point(mesh, points[start:start+batch_size])
        distances.extend(float(value) for value in measured)
    errors = np.asarray(distances)
    finite = bool(len(errors) and np.isfinite(errors).all())
    maximum = float(errors.max()) if finite else float("inf")
    percentiles = ({f"p{percent}": clean_number(np.percentile(errors, percent))
                    for percent in (50, 90, 95, 99)} if finite else {})
    worst = int(errors.argmax()) if finite else None
    target = 0.015
    measurements = {
        "mesh": str(mesh_path),
        "stl_sha256": hashlib.sha256(payload).hexdigest(),
        "triangle_count": len(mesh.faces),
        "grid_per_bspline_face": [u_count, v_count],
        "selection": "abs(X)>10 mm and 2<Z<63 mm; outside the lever cut",
        "faces": faces, "sample_count": len(samples),
        "closest_point_batch_size": batch_size,
        "maximum_surface_to_mesh_distance_mm": clean_number(maximum) if finite else None,
        "rms_surface_to_mesh_distance_mm": clean_number(math.sqrt(float(np.mean(errors**2)))) if finite else None,
        "distance_percentiles_mm": percentiles,
        "worst_sample_xyz_mm": [clean_number(value) for value in points[worst]] if worst is not None else None,
        "required_maximum_mm": target,
        "current_export_settings": {"deflection_mm": f.piece_mesh_tol,
                                    "angle_rad": f.piece_mesh_angle,
                                    "tolerance_is_relative": False},
        "method": "analytic B-rep BSpline surface values on each exact UV rectangle, measured to triangles loaded from the actual serialized STL in bounded nearest-point batches",
        "scope": "sampled surface-to-mesh error on the broad lower outer loft; the source file is identified by SHA, and current exporter settings do not establish the provenance of an optional comparison file. Not a two-sided Hausdorff bound or a physical print-surface measurement",
    }
    reading.add("mesh:lower-outer-loft-accuracy", finite and len(samples) >= 100
                and bool(np.any(points[:, 0] < -10.0)) and bool(np.any(points[:, 0] > 10.0))
                and maximum <= target+1e-6, **measurements)
    return measurements


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
                    method=f"complete {f.wall_thickness_min:g} mm radial witness around the real brass OD over its installed length",
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

    # The geometric lever stand-in does not include a measured rear arm. Keep
    # its established overhead envelope independently of that moving model.
    opening_half_width = f.lever_clearance_x_half
    opening_rear_y = f.lever_clearance_y_back
    rest_top = f.lever_rest_top_z
    roof_circle = (cq.Workplane("YZ").center(f.fill_y_min, f.back_arch_center_z)
                   .circle(f.back_arch_r).extrude(opening_half_width, both=True).val())
    overhead_box = cq.Solid.makeBox(2.0*opening_half_width, opening_rear_y-f.shell_rect_y_min,
                                    f.zone4_z_top-rest_top,
                                    cq.Vector(-opening_half_width, f.shell_rect_y_min, rest_top))
    overhead = roof_circle.intersect(overhead_box)
    implemented = shape(f.build_lever_overhead_clearance())
    profile_delta = volume(overhead.cut(implemented))+volume(implemented.cut(overhead))
    remaining = volume(overhead.intersect(base))
    reading.add("clearance:lever-overhead-profile", volume(overhead) > VOLUME_TOLERANCE
                and max(profile_delta, remaining) <= VOLUME_TOLERANCE,
                profile_volume_mm3=clean_number(volume(overhead)),
                printed_material_inside_profile_mm3=clean_number(remaining),
                clearance_builder_symmetric_difference_mm3=clean_number(profile_delta),
                x_half_width_mm=clean_number(opening_half_width),
                rear_y_mm=clean_number(opening_rear_y),
                minimum_z_mm=clean_number(rest_top),
                circle_center_yz_mm=[clean_number(f.fill_y_min), clean_number(f.back_arch_center_z)],
                circle_radius_mm=clean_number(f.back_arch_r),
                method="independently reconstructed circular overhead volume, clipped to the lever opening and above the rest-lever top, intersected with the complete printed base",
                scope="keeps the full overhead relief for the rising rear arm; it is not a measured metal-arm shape or proof of the harvested lever's complete travel")

    rear_y = f.soda_faucet_tube_y-f.soda_faucet_hole_diameter/2.0-wall-DISTANCE_TOLERANCE
    front_y = rear_y - 2.0 * wall
    half_width = f.lever_x_half
    bridge_box = cq.Solid.makeBox(2.0*half_width, rear_y-front_y, f.zone4_z_top+wall-rest_top,
                                  cq.Vector(-half_width, front_y, rest_top))
    witness = roof_circle.translate((0.0, 0.0, wall)).cut(roof_circle).intersect(bridge_box)
    missing = volume(witness.cut(base))
    reading.add("wall:lever-roof-bridge", volume(witness) > VOLUME_TOLERANCE and missing <= VOLUME_TOLERANCE,
                method=f"complete {wall:g} mm vertical strip above two wall-widths of the independently reconstructed circular lever roof, ending one wall-width forward of the water bore",
                xy_bounds_mm=[-half_width, half_width, clean_number(front_y), clean_number(rear_y)],
                required_vertical_stock_mm=wall, missing_witness_mm3=clean_number(missing),
                scope="the bridge from the lever roof into the neck; not every exterior opening edge")
    samples = []
    for x in (-half_width, 0.0, half_width):
        for y in (front_y, rear_y - wall, rear_y):
            roof_z = f.back_arch_center_z+math.sqrt(f.back_arch_r**2-(y-f.fill_y_min)**2)
            spans = line_intervals(base, (x, y, roof_z + DISTANCE_TOLERANCE),
                                   (0.0, 0.0, 1.0), 2.0 * wall)
            continuous = (len(spans) == 1 and spans[0][0] <= DISTANCE_TOLERANCE
                          and spans[0][1] - spans[0][0] >= wall - DISTANCE_TOLERANCE)
            samples.append({"x_mm": clean_number(x), "y_mm": clean_number(y),
                            "circular_roof_z_mm": clean_number(roof_z),
                            "material_intervals_above_roof_mm":
                                [[clean_number(a), clean_number(b)] for a, b in spans],
                            "continuous": continuous})
    reading.add("section:lever-roof-continuity", all(row["continuous"] for row in samples),
                method="nine exact vertical B-rep chords from the circular roof at each Y station through two wall-widths of roof and neck",
                probe_height_mm=2.0 * wall,
                minimum_continuous_stock_mm=wall, samples=samples,
                scope="no separated upper slit in the roof-to-neck bridge; exterior rays may end at the show surface")


def lower_passage_join_reading(reading, base):
    """Check the small cable/flavor handoff where a residual fin can survive."""
    import cadquery as cq
    base = shape(base)
    probes = []
    for xyz in ((6.85, 16.299, 7.1), (6.90, 16.299, 7.1),
                (6.85, 16.5, 15.0)):
        point = cq.Vector(*xyz)
        inside = any(solid.isInside(point, DISTANCE_TOLERANCE)
                     for solid in base.Solids())
        distance = base.distance(cq.Vertex.makeVertex(*xyz))
        probes.append({"xyz_mm": list(xyz), "inside_printed_material": inside,
                       "gap_to_printed_material_mm": clean_number(distance)})
    minimum = (6.81, 16.48, 14.8)
    size = (0.13, 0.04, 0.3)
    witness = cq.Solid.makeBox(*size, cq.Vector(*minimum))
    interference = volume(witness.intersect(base))
    reading.add("clearance:lower-passage-join", interference <= VOLUME_TOLERANCE
                and all(not row["inside_printed_material"]
                        and row["gap_to_printed_material_mm"] > DISTANCE_TOLERANCE
                        for row in probes),
                probes=probes, empty_prism_minimum_xyz_mm=list(minimum),
                empty_prism_size_xyz_mm=list(size),
                printed_material_in_empty_prism_mm3=clean_number(interference),
                method="three exact point-to-solid gaps and a complete empty-volume witness through the flavor/cable opening handoff",
                scope="named lower-passage corner and loft handoff; not a global small-feature scan")


def display_retention_reading(reading, f, parts, body, screen, ribbon, tubes,
                              free_cover, cover_builder, *, include_motion=True):
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
        # Commons at the preload root also carry zero-volume contact faces.
        # Work only with solid material; a cut of the mixed-dimensional common
        # can return a null TopoDS shape when all of its solids are covered.
        return outside_material_volume(part, allowed)

    def lip_radii(part):
        return sorted({clean_number(r) for face in shape(part).Faces()
                       if (r := radius(face)) is not None})

    lower_skirts = cover.intersect(band(f.display_head_s_min, f.display_head_s_max + 1.0,
                                       n0, f.display_cover_shoulder_n))
    skirts = {side: half(lower_skirts, side) for side in (-1, 1)}
    free_cover = shape(free_cover)
    free_lower_skirts = free_cover.intersect(
        band(f.display_head_s_min, f.display_head_s_max + 1.0,
             n0, cover_builder.bezel_n_bottom))
    free_skirts = {side: half(free_lower_skirts, side) for side in (-1, 1)}
    lip_parts = {side: half(lips, side) for side in (-1, 1)}
    # Crop the obstacle once, using exact conservative bounds of both complete
    # covers and the full allowed translation range. The lower base and remote
    # neck faces cannot affect these poses; excluding them avoids repeating
    # their unrelated intersections in every clearance bisection.
    search_limit = max(3.0, snap.ENGAGEMENT+cover_builder.preload_inward_at(n0)+0.5)
    resolution = 0.005
    lifts = sorted(value for value in {0.0, 0.10, snap.BEARING_SLIP, snap.BEARING_SLIP+0.001,
                    snap.BEARING_SLIP+0.01, snap.BEARING_SLIP+0.05, 0.35, 0.50, 0.75,
                    1.0, 1.5, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, f.display_cartridge_lift_n}
                   if value <= f.display_cartridge_lift_n)
    cover_bounds = [local_bounds(part) for part in (cover, free_cover)]
    margin = 0.1
    clip_min = [min(b.xmin for b in cover_bounds)-search_limit-margin,
                min(b.ymin for b in cover_bounds)-margin,
                min(b.zmin for b in cover_bounds)-margin]
    clip_max = [max(b.xmax for b in cover_bounds)+search_limit+margin,
                max(b.ymax for b in cover_bounds)+margin,
                max(b.zmax for b in cover_bounds)+max(lifts)+margin]
    native_clip = cq.Solid.makeBox(*(b-a for a, b in zip(clip_min, clip_max)),
                                   cq.Vector(*clip_min))
    obstacle_clip = shape(f._display_world(cq.Workplane(obj=native_clip)))
    full = full.intersect(obstacle_clip)
    if not full.isValid() or volume(full) <= VOLUME_TOLERANCE:
        raise RuntimeError("display motion: invalid or empty conservative obstacle crop")
    groove_band = band(s0-snap.END_SLIP, s1+snap.END_SLIP, n0, n1+snap.BEARING_SLIP)
    groove_core = shape(f.build_display_neck_reference(f.display_neck_outer_r-f.display_clip_groove_radius))
    backed_core = shape(f.build_display_neck_reference(
        f.display_neck_outer_r-f.display_clip_groove_radius+f.wall_thickness_min))
    backing = groove_core.cut(backed_core).intersect(groove_band)
    groove_ceiling = n1+snap.BEARING_SLIP
    shoulder_witness = shape(f.build_display_neck_reference()).cut(groove_core).intersect(
        band(s0, s1, groove_ceiling, groove_ceiling+f.wall_thickness_min))
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
                    and all(row["normal_stock_mm"] >= snap.LIP_HEIGHT-DISTANCE_TOLERANCE for row in lip_chords)
                    and radial_stock >= 1.0-DISTANCE_TOLERANCE,
                    missing_lip_from_cover_mm3=clean_number(missing),
                    sampled_normal_chords=lip_chords,
                    measured_normal_height_mm=clean_number(b.zlen),
                    minimum_inner_surface_to_outer_skin_mm=clean_number(radial_stock),
                    required_normal_height_mm=snap.LIP_HEIGHT,
                    required_radial_stock_mm=1.0,
                    method="complete lip containment in the cover, nine exact interior normal chords per side, and complete curved-side separation")
        witness = half(backing, side)
        missing = volume(witness.cut(tip))
        reading.add(f"wall:retention-groove-{side:+d}", volume(witness) > VOLUME_TOLERANCE
                    and missing <= VOLUME_TOLERANCE,
                    missing_complete_radial_backing_mm3=clean_number(missing),
                    required_radial_backing_mm=f.wall_thickness_min,
                    method=f"complete {f.wall_thickness_min:g} mm annular witness behind the actual swept groove, including its rear torus section")
        shoulder = half(shoulder_witness, side)
        missing_shoulder = volume(shoulder.cut(tip))
        reading.add(f"wall:retention-shoulder-{side:+d}", volume(shoulder) > VOLUME_TOLERANCE
                    and missing_shoulder <= VOLUME_TOLERANCE,
                    missing_complete_bearing_stock_mm3=clean_number(missing_shoulder),
                    required_normal_witness_span_mm=f.wall_thickness_min,
                    bearing_start_n_mm=clean_number(groove_ceiling),
                    method=f"complete annular volume between the original cylinder and groove-root sweep over a {f.wall_thickness_min:g} mm N band above each retaining shoulder",
                    scope=f"retained stock following the curved neck; not a {f.wall_thickness_min:g} mm vertical column at every point of the outer bearing edge")
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
        engagement = f.display_neck_outer_r-lip_r
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
    early_push, whole_push = 0.01, 0.02
    early = cover.translate(normal.multiply(-early_push))
    floor_witnesses = []
    for fraction in (0.125, 0.5, 0.875):
        station = s0+(s1-s0)*fraction
        point = origin+along.multiply(station)+normal.multiply(n0-early_push/2.0)
        for side in (-1, 1):
            fixed_spans = line_intervals(tip, point.toTuple(), (side, 0.0, 0.0), 30.0)
            moving_spans = line_intervals(early, point.toTuple(), (side, 0.0, 0.0), 30.0)
            overlaps = [(max(a, c), min(b, d)) for a, b in fixed_spans for c, d in moving_spans
                        if min(b, d)-max(a, c) > 4.0*DISTANCE_TOLERANCE]
            if not overlaps:
                floor_witnesses.append({"side": side, "s_mm": clean_number(station), "present": False})
                continue
            lo, hi = max(overlaps, key=lambda span: span[1]-span[0])
            half_x = min(0.1, (hi-lo)/4.0)
            witness = shape(f._cradle_prism(half_x, station-0.1, station+0.1,
                                            n0-0.9*early_push, n0-0.1*early_push)
                            .translate((side*(lo+hi)/2.0, 0.0, 0.0)))
            missing_fixed, missing_moving = outside_volume(witness, tip), outside_volume(witness, early)
            floor_witnesses.append({"side": side, "s_mm": clean_number(station),
                                    "present": volume(witness) > VOLUME_TOLERANCE,
                                    "witness_volume_mm3": clean_number(volume(witness)),
                                    "missing_from_tip_mm3": clean_number(missing_fixed),
                                    "missing_from_pushed_lip_mm3": clean_number(missing_moving)})
    # A whole-shape common at 0.01 mm can lose these independently verified
    # slivers at coincident torus/cylinder roots. The larger probe remains well
    # short of the glass clearance and supplies the complete contact inventory.
    pushed = cover.translate(normal.multiply(-whole_push))
    pushed_lips = lips.translate(normal.multiply(-whole_push))
    seat_common = pushed.intersect(full)
    seat_other = outside_volume(seat_common, pushed_lips)
    root_contact_zone = tip.intersect(groove_band)
    # The common already lies inside the real tip. Classify it with the full
    # floor/root coordinate band instead of subtracting the coincident swept
    # root from a 0.02 mm floor sliver: that redundant Boolean can lose material
    # at the cylinder-to-torus transition. The independent witnesses above
    # establish actual floor contact, and the lip mask excludes other parts.
    seat_allowed = band(s0-DISTANCE_TOLERANCE, s1+DISTANCE_TOLERANCE,
                        n0-whole_push-DISTANCE_TOLERANCE,
                        n1+snap.BEARING_SLIP+DISTANCE_TOLERANCE)
    outside_floor_and_root = outside_volume(seat_common, seat_allowed)
    glass = shape(screen)
    reading.add("seat:display-cover-stop", volume(seat_common) > VOLUME_TOLERANCE
                and all(row["present"] and max(row["missing_from_tip_mm3"], row["missing_from_pushed_lip_mm3"]) <= VOLUME_TOLERANCE
                        for row in floor_witnesses)
                and max(seat_other, outside_floor_and_root, contact(pushed, body), contact(pushed, glass)) <= VOLUME_TOLERANCE,
                early_floor_probe_inward_motion_mm=early_push, floor_contact_witnesses=floor_witnesses,
                complete_contact_probe_inward_motion_mm=whole_push,
                fixed_body_interference_mm3=clean_number(volume(seat_common)),
                contact_outside_actual_lips_mm3=clean_number(seat_other),
                contact_outside_groove_floor_and_root_mm3=clean_number(outside_floor_and_root),
                device_interference_mm3=clean_number(contact(pushed, body)),
                glass_interference_mm3=clean_number(contact(pushed, glass)),
                method="six independent interior floor witnesses after 0.01 mm inward travel; the complete 0.02 mm contact common must remain in the actual lips against groove floors or preload roots, before the display or glass")
    lifted = cover.translate(normal.multiply(0.5))
    retention_common = lifted.intersect(full)
    shoulder = tip.intersect(band(s0, s1, n1+snap.BEARING_SLIP-DISTANCE_TOLERANCE,
                                  n1+0.5+DISTANCE_TOLERANCE)).cut(groove_core)
    outside_lips = outside_volume(retention_common, lips.translate(normal.multiply(0.5)))
    shoulder_capture = volume(retention_common)-outside_volume(retention_common, shoulder)
    root_camming = volume(retention_common)-outside_volume(retention_common, root_contact_zone)
    outside_shoulder_and_root = outside_volume(retention_common, cq.Compound.makeCompound([shoulder, root_contact_zone]))
    reading.add("retention:display-snaps", shoulder_capture > VOLUME_TOLERANCE
                and max(outside_lips, outside_shoulder_and_root) <= VOLUME_TOLERANCE,
                interference_on_0_5mm_outward_lift_mm3=clean_number(volume(retention_common)),
                actual_shoulder_capture_mm3=clean_number(shoulder_capture),
                groove_root_camming_contact_mm3=clean_number(root_camming),
                contact_outside_actual_lips_mm3=clean_number(outside_lips),
                contact_outside_shoulders_and_preload_roots_mm3=clean_number(outside_shoulder_and_root),
                scope="geometric cover-lip capture only; PET-GF force, flex distribution and cycling require the complete print trial")
    if not include_motion:
        display_rigid_neck_reading(reading, f, tip)
        return

    # Independently measure both the nominal seated and relaxed printed skirts.
    # Radial engagement is not a sufficient search budget at the cylinder crown.
    # A rigid skirt translation measures clearance demand, not its elastic path.
    def outward_clearance(skirt, side):
        low, high = 0.0, search_limit
        if contact(skirt, full) <= VOLUME_TOLERANCE:
            return 0.0, 0.0
        if contact(skirt.translate((side*high, 0.0, 0.0)), full) <= VOLUME_TOLERANCE:
            while high-low > resolution:
                mid = (low+high)/2.0
                if contact(skirt.translate((side*mid, 0.0, 0.0)), full) <= VOLUME_TOLERANCE:
                    high = mid
                else:
                    low = mid
        return high, contact(skirt.translate((side*high, 0.0, 0.0)), full)
    hardware = {"display": body, "glass": glass,
                "ribbon-neck": shape(f.build_signal_neck_ribbon()),
                **{name: shape(part) for name, part in tubes.items()}}
    hardware_bounds = {name: local_bounds(part) for name, part in hardware.items()}
    travel = {name: {"overlap": 0.0, "gap": float("inf")} for name in hardware}
    rows = []
    for lift in lifts:
        moved = cover.translate(normal.multiply(lift))
        common = moved.intersect(full)
        row = {"normal_lift_mm": lift, "unflexed_body_interference_mm3": clean_number(volume(common)),
               "contact_outside_actual_lips_mm3": clean_number(outside_volume(common, lips.translate(normal.multiply(lift)))),
               "contact_outside_lower_skirts_mm3": clean_number(outside_volume(common, lower_skirts.translate(normal.multiply(lift)))),
               "sides": []}
        hardware_poses = [
            (moved, {"state": "nominal", "part": "complete_cover", "normal_lift_mm": lift}),
            (free_cover.translate(normal.multiply(lift)),
             {"state": "relaxed", "part": "complete_cover", "normal_lift_mm": lift})]
        for side in (-1, 1):
            skirt = skirts[side].translate(normal.multiply(lift))
            high, remaining = outward_clearance(skirt, side)
            free_skirt = free_skirts[side].translate(normal.multiply(lift))
            free_high, free_remaining = outward_clearance(free_skirt, side)
            row["sides"].append({"side": side, "required_outward_clearance_mm": clean_number(high),
                                  "required_outward_clearance_from_nominal_seat_mm": clean_number(high),
                                  "total_outward_clearance_from_relaxed_print_mm": clean_number(free_high),
                                  "remaining_body_interference_mm3": clean_number(remaining),
                                  "remaining_relaxed_body_interference_mm3": clean_number(free_remaining)})
            for state, material, demand in (("nominal", skirt, high), ("relaxed", free_skirt, free_high)):
                hardware_poses.extend(
                    (material.translate((side*demand*fraction, 0.0, 0.0)),
                     {"state": state, "part": "lower_skirt", "side": side,
                      "normal_lift_mm": lift, "outward_translation_mm": clean_number(demand*fraction)})
                    for fraction in (0.5, 1.0))
        posed = [(pose, local_bounds(pose), description) for pose, description in hardware_poses]
        for name, original_obstacle in hardware.items():
            # The LCD is already inside the cover. Moving it with the cap is
            # the actual cartridge assembly sequence; the loading stroke has
            # its own complete swept-volume reading below.
            obstacle = (original_obstacle.translate(normal.multiply(lift))
                        if name in ("display", "glass") else original_obstacle)
            ob = local_bounds(obstacle) if name in ("display", "glass") else hardware_bounds[name]
            required = 0.1 if name == "ribbon-neck" else 0.0
            for pose, pb, description in posed:
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
                if overlap > travel[name]["overlap"]:
                    travel[name]["maximum_overlap_pose"] = description
                travel[name]["overlap"] = max(travel[name]["overlap"], overlap)
        rows.append(row)
        print(f"  cover normal lift {lift:g} mm: nominal / relaxed outward demands "
              + ", ".join(f"{side['required_outward_clearance_mm']:.4f} / "
                          f"{side['total_outward_clearance_from_relaxed_print_mm']:.4f}"
                          for side in row["sides"]) + " mm", flush=True)
    peak = max(side["required_outward_clearance_mm"] for row in rows for side in row["sides"])
    free_peak = max(side["total_outward_clearance_from_relaxed_print_mm"] for row in rows for side in row["sides"])
    reading.add("motion:display-cover-normal", all(
                    max(row["contact_outside_actual_lips_mm3"], row["contact_outside_lower_skirts_mm3"],
                        *(side["remaining_body_interference_mm3"] for side in row["sides"]),
                        *(side["remaining_relaxed_body_interference_mm3"] for side in row["sides"])) <= VOLUME_TOLERANCE
                    for row in rows),
                samples=rows, peak_required_outward_clearance_per_side_mm=clean_number(peak),
                peak_total_outward_clearance_from_relaxed_print_per_side_mm=clean_number(free_peak),
                outward_search_budget_mm=clean_number(search_limit), clearance_search_resolution_mm=resolution,
                obstacle_crop_display_frame_xyz_mm={"minimum": [clean_number(v) for v in clip_min],
                                                     "maximum": [clean_number(v) for v in clip_max]},
                obstacle_crop_method="exact conservative bounds of both complete covers, expanded by the full independent outward search budget in X, all normal lifts in N, and 0.1 mm on every face; also contains the inward seating probes",
                cartridge_lift_n_mm=f.display_cartridge_lift_n,
                scope="final normal seating of the preloaded cover/display cartridge after the lifted axial approach; display and glass move with the cover. Nominal contact must stay in the lips and lower skirts. Each skirt's rigid outward translation measures clearance demand, not deformation, strain, force, or the loaded equilibrium shape of the joined end bridges")
    for name, result in travel.items():
        required = 0.1 if name == "ribbon-neck" else 0.0
        reading.add(f"clearance:snap-travel-{name}", result["overlap"] <= VOLUME_TOLERANCE
                    and result["gap"] >= required-DISTANCE_TOLERANCE,
                    maximum_sampled_overlap_mm3=clean_number(result["overlap"]),
                    maximum_overlap_pose=result.get("maximum_overlap_pose"),
                    minimum_sampled_gap_lower_bound_mm=clean_number(result["gap"]), required_gap_mm=required,
                    method="complete nominal and relaxed covers at every final seating station, plus both states' actual lower skirts at half and full measured outward travel; the display/glass share the cover's normal translation, while tubes and neck ribbon remain fixed; exact commons or distance, with conservative box separation where available")

    display_rigid_neck_reading(reading, f, tip)


def display_loading_reading(reading, f, cover_builder, body, screen, free_cover):
    """Complete device-loading envelope and independent wing-opening demand."""
    import cadquery as cq
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.BRepPrimAPI import BRepPrimAPI_MakePrism
    from OCP.gp import gp_Vec
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    hardware = [shape(part).moved(frame.inverse) for part in (body, screen)]
    free = shape(free_cover).moved(frame.inverse)
    bottom = free.BoundingBox().zmin-0.1
    upper = max(part.BoundingBox().zmax for part in hardware)
    travel = f.display_loading_travel_n
    starts_below_cover = upper-travel < bottom
    # These reference solids are vertical extrusions: horizontal planes and
    # cylinders parallel to N. Extruding every upward face to a plane below
    # the cap gives their exact loading occupancy within the cap's N band,
    # once the entire device starts below that band. Reject new unsupported
    # surface types instead of assuming this projection remains complete.
    prisms, face_kinds = [], {}
    for part in hardware:
        for face in part.Faces():
            kind = face.geomType()
            face_kinds[kind] = face_kinds.get(kind, 0)+1
            if kind == "PLANE":
                nz = face.normalAt().z
                if min(abs(nz), abs(abs(nz)-1.0)) > 1e-6:
                    raise RuntimeError("display loading: unsupported tilted reference face")
                if nz > 1.0-1e-6 and face.Center().z > bottom:
                    prism = cq.Shape.cast(BRepPrimAPI_MakePrism(
                        face.wrapped, gp_Vec(0.0, 0.0, bottom-face.Center().z), True).Shape())
                    if not prism.isValid() or len(prism.Solids()) != 1:
                        raise RuntimeError("display loading: invalid upward-face sweep")
                    prisms.append(prism)
            elif kind == "CYLINDER":
                axis = BRepAdaptor_Surface(face.wrapped).Cylinder().Axis().Direction()
                if abs(abs(axis.Z())-1.0) > 1e-6:
                    raise RuntimeError("display loading: unsupported tilted reference cylinder")
            else:
                raise RuntimeError(f"display loading: unsupported reference surface {kind}")
    if not prisms:
        raise RuntimeError("display loading: missing upward device faces")
    swept = prisms[0].fuse(*prisms[1:]).clean()
    cap_band = cq.Solid.makeBox(100.0, 150.0, f.display_cover_top_n+1.0-bottom,
                                cq.Vector(-50.0, -50.0, bottom))
    containment = []
    for shift in (0.0, -travel/2.0, -travel):
        moved = cq.Compound.makeCompound([part.translate((0.0, 0.0, shift)) for part in hardware])
        containment.append(outside_material_volume(moved.intersect(cap_band), swept))
    bezel = free.intersect(cq.Solid.makeBox(100.0, 150.0, 50.0,
                                           cq.Vector(-50.0, -50.0, cover_builder.bezel_n_bottom)))
    bezel_overlap = volume(bezel.intersect(swept))
    budget, resolution, allowance = 3.0, 0.005, f.display_cradle_clearance
    rows = []
    for side in (-1, 1):
        mask = cq.Solid.makeBox(50.0, 150.0, cover_builder.bezel_n_bottom+50.0,
                                cq.Vector(0.0 if side > 0 else -50.0, -50.0, -50.0))
        wing = free.intersect(mask)
        low, high = 0.0, budget
        initial = volume(wing.intersect(swept))
        if initial <= VOLUME_TOLERANCE:
            high = 0.0
        elif volume(wing.translate((side*high, 0.0, 0.0)).intersect(swept)) <= VOLUME_TOLERANCE:
            while high-low > resolution:
                middle = (low+high)/2.0
                if volume(wing.translate((side*middle, 0.0, 0.0)).intersect(swept)) <= VOLUME_TOLERANCE:
                    high = middle
                else:
                    low = middle
        opening = high+allowance
        posed = wing.translate((side*opening, 0.0, 0.0))
        rows.append({"side": side, "unopened_interference_mm3": clean_number(initial),
                     "required_outward_clearance_from_relaxed_print_mm": clean_number(high),
                     "outward_opening_with_lateral_allowance_mm": clean_number(opening),
                     "remaining_interference_mm3": clean_number(volume(posed.intersect(swept))),
                     "minimum_complete_stroke_gap_mm": clean_number(posed.distance(swept))})
    reading.add("motion:display-loading-into-cover", starts_below_cover and swept.isValid()
                and max(containment+[bezel_overlap]) <= VOLUME_TOLERANCE
                and all(row["remaining_interference_mm3"] <= VOLUME_TOLERANCE
                        and row["minimum_complete_stroke_gap_mm"] >= 0.1-DISTANCE_TOLERANCE for row in rows),
                normal_loading_stroke_mm=travel, starts_completely_below_cover=starts_below_cover,
                complete_sweep_n_band_mm=[clean_number(bottom), clean_number(upper)],
                reference_face_kinds=face_kinds, upward_face_prism_count=len(prisms),
                independent_pose_containment_missing_mm3=[clean_number(v) for v in containment],
                unchanged_bezel_interference_mm3=clean_number(bezel_overlap),
                independent_outward_search_budget_mm=budget, search_resolution_mm=resolution,
                lateral_allowance_mm=allowance, sides=rows,
                method="exact complete downward projection of every upward device face within the cover band, after verifying all reference surfaces are parallel vertical extrusions; independent actual free-wing translation and exact common/distance",
                scope="factory loading opens the plastic before the PCB enters. Opening demand is geometric; the joined end bridges, force, spring return and display support require the complete print trial. This is not an elastic shape prediction")


def display_cartridge_axial_reading(reading, f, parts, seated, free, body, screen, tubes):
    """Bound the complete lifted slide using a translation-invariant cylinder."""
    import cadquery as cq
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    lift, slide = f.display_cartridge_lift_n, f.display_cartridge_slide_s
    movers = {name: shape(part).moved(frame.inverse).translate((0.0, 0.0, lift))
              for name, part in (("nominal_cover", seated), ("relaxed_cover", free),
                                 ("display", body), ("glass", screen))}
    boxes = [part.BoundingBox() for part in movers.values()]
    low_s = min(box.ymin for box in boxes)-slide-0.1
    high_s = max(box.ymax for box in boxes)+0.1
    low_n = min(box.zmin for box in boxes)-0.1
    high_n = max(box.zmax for box in boxes)+0.1
    half_x = max(max(abs(box.xmin), abs(box.xmax)) for box in boxes)+0.1
    crop = cq.Solid.makeBox(2.0*half_x, high_s-low_s, high_n-low_n,
                            cq.Vector(-half_x, low_s, low_n))
    cylinder = cq.Solid.makeCylinder(f.tube_shell_outer_r, high_s-low_s,
                                     cq.Vector(0.0, low_s, f.tube_shell_center_y),
                                     cq.Vector(0.0, 1.0, 0.0))
    obstacles = {"shell_base": parts["shell_base"], "shell_tip": parts["shell_tip"],
                 "neck_ribbon": f.build_signal_neck_ribbon(), **tubes}
    containment = []
    for name, part in obstacles.items():
        relevant = shape(part).moved(frame.inverse).intersect(crop)
        outside = volume(relevant.cut(cylinder)) if volume(relevant) > VOLUME_TOLERANCE else 0.0
        containment.append({"part": name, "relevant_volume_mm3": clean_number(volume(relevant)),
                            "outside_cylinder_mm3": clean_number(outside)})
    clearances = []
    for name, part in movers.items():
        clearances.append({"part": name, "overlap_mm3": clean_number(volume(part.intersect(cylinder))),
                           "minimum_cylinder_gap_mm": clean_number(part.distance(cylinder))})
    reading.add("motion:display-cartridge-axial", lift > 0.0 and slide > 0.0
                and abs(f.display_neck_outer_r-f.tube_shell_outer_r) <= DISTANCE_TOLERANCE
                and all(row["outside_cylinder_mm3"] <= VOLUME_TOLERANCE for row in containment)
                and all(row["overlap_mm3"] <= VOLUME_TOLERANCE
                        and row["minimum_cylinder_gap_mm"] >= 0.1-DISTANCE_TOLERANCE for row in clearances),
                path_local_s_n_mm=[[-slide, lift], [0.0, lift]],
                conservative_cylinder_radius_mm=f.tube_shell_outer_r,
                complete_moving_bounds_mm={"s": [clean_number(low_s), clean_number(high_s)],
                                           "n": [clean_number(low_n), clean_number(high_n)],
                                           "x": [-clean_number(half_x), clean_number(half_x)]},
                fixed_obstacle_containment=containment, complete_mover_clearances=clearances,
                method="exact containment of every relevant fixed solid inside a straight cylinder, plus exact clearance of each complete lifted mover from that S-invariant cylinder; proves the entire axial segment rather than sampled poses",
                scope="display and glass travel inside the cover from the outlet. The temporary flexible ribbon branch must be fed during factory assembly; its final route is checked separately. Normal seating and plastic opening have separate readings")


def display_rigid_neck_reading(reading, f, part):
    """Verify the rigid cylinder outside the groove and the open device pocket."""
    import cadquery as cq
    tip = shape(part)
    origin, along, normal = f._tip_frame()

    def band(a, b, low, high):
        return shape(f._cradle_prism(f.display_cover_skirt_width, a, b, low, high))

    neck_outer = shape(f.build_display_neck_reference())
    # Keep the complete volume witness inside the exact show surface and away
    # from coplanar opening/groove boundaries. Independent exact chords below
    # require the real exterior endpoint and a full millimeter of material.
    surface_inset, edge_inset, depth = 0.01, 0.02, 1.0
    skin_outer = shape(f.build_display_neck_reference(surface_inset))
    skin_inner = shape(f.build_display_neck_reference(depth))
    restored = skin_outer.cut(skin_inner).intersect(
        band(f.display_s_bottom+edge_inset, f.display_s_top-edge_inset,
             f.display_clip_top_n+f._display_snap.BEARING_SLIP+edge_inset,
             f.display_feet_n-edge_inset))
    missing_skin = volume(restored.cut(tip))
    samples = []
    groove_ceiling = f.display_clip_top_n+f._display_snap.BEARING_SLIP
    n_low, n_high = groove_ceiling+0.5, f.display_feet_n-1.0
    n_stations = (n_low, (n_low+n_high)/2.0, n_high)
    for station in (2.0, 6.0, 10.0, 13.573, 20.0, 26.0, 30.0, 34.0, 40.0, 44.0):
        for n in n_stations:
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
    beyond_neck_material = tip.intersect(head_region).cut(neck_outer)
    beyond_neck = volume(beyond_neck_material)
    beyond_named_features = outside_material_volume(beyond_neck_material, f.build_display_feet_pads())
    upper = band(f.display_s_bottom, f.display_s_top, f.display_feet_n+DISTANCE_TOLERANCE,
                 f.display_cover_top_n+1.0)
    upper_fins = volume(tip.intersect(upper))
    reading.add("shape:display-rigid-neck", n_low < n_high
                and restored.isValid() and volume(restored) > VOLUME_TOLERANCE
                and max(missing_skin, beyond_named_features, upper_fins) <= VOLUME_TOLERANCE
                and all(row["outer_endpoint_error_mm"] <= DISTANCE_TOLERANCE
                        and row["continuous_stock_mm"] >= depth-DISTANCE_TOLERANCE for row in samples),
                missing_complete_subsurface_witness_mm3=clean_number(missing_skin),
                radial_witness_range_below_exterior_mm=[surface_inset, depth],
                witness_open_boundary_inset_mm=edge_inset, exterior_sections=samples,
                groove_ceiling_n_mm=clean_number(groove_ceiling),
                local_head_radius_mm=f.display_neck_outer_r,
                sampled_n_stations_mm=[clean_number(n) for n in n_stations],
                required_continuous_chord_stock_mm=depth,
                material_beyond_swept_cylinder_mm3=clean_number(beyond_neck),
                material_beyond_cylinder_and_named_foot_pads_mm3=clean_number(beyond_named_features),
                upper_device_opening_material_mm3=clean_number(upper_fins),
                method="complete swept subsurface witness above the grooves, exact exterior endpoints and continuous material on 60 chords, no material beyond the cylinder and named foot pads, and the complete full-width opening above the feet; complete pad/backing volumes are checked separately")


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
    stations = [0.5, 1.0, 2.0, 4.0, 6.0, 42.0, 44.0, 46.0, 48.0]
    rear_start = max(stations[-1], (f.display_cover_rear_rim_s0+f.display_cover_rear_rim_ds_dn*f.display_cover_bottom_n))
    stations.extend(rear_start+(cover.BoundingBox().ymax-rear_start)*fraction
                    for fraction in (0.25, 0.5, 0.75, 0.9))
    for station in stations:
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
                rim_evidence = open_lower_rim_evidence(cover, f, p, normal.multiply(-1.0), stock)
                samples.append({"point_x_s_n_mm": [clean_number(v) for v in p.toTuple()],
                                "outer_face_distance_mm": clean_number(outer_distance),
                                "section_rim_n_mm": clean_number(bottom),
                                "rise_above_section_rim_mm": rise,
                                "normal_inward": [clean_number(v) for v in normal.multiply(-1.0).toTuple()],
                                "open_rim_evidence": rim_evidence,
                                "normal_stock_mm": clean_number(stock)})
        sections.append({"s_mm": station, "present": True, "probe_count": len(samples)-before})
    through_wall = [row["normal_stock_mm"] for row in samples if row["open_rim_evidence"] is None]
    least = min(through_wall, default=0.0)
    reading.add("wall:display-finished-neck-rim", bool(samples) and least >= 1.0-DISTANCE_TOLERANCE
                and all(row["open_rim_evidence"]["passed"] for row in samples
                        if row["open_rim_evidence"] is not None)
                and all(row["outer_face_distance_mm"] <= DISTANCE_TOLERANCE for row in samples)
                and all(row["present"] and row["probe_count"] > 0 for row in sections),
                minimum_sampled_normal_stock_mm=clean_number(least), required_mm=1.0,
                minimum_unqualified_normal_chord_mm=clean_number(min((row["normal_stock_mm"] for row in samples), default=0.0)),
                sections=sections, samples=samples,
                method=f"exact finished-cover sections at {len(stations)} fore/aft stations including the rear closure; inward normal material chords on both sides at five heights above each actual lower edge",
                scope="sampled neck-rim and corner stock after all cuts. Rays leaving the intentional flat lower rim are reported with independent lateral rim stock and an elevated through-wall normal chord; other short chords still fail. Not a global minimum-wall certificate")

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
    retained_skin_faces = []
    for face in cover.Faces():
        if face.geomType() == "PLANE":
            continue
        # Include the rear closure's analytic cylinder/torus faces as well as the
        # loft. Boundary vertices alone can also belong to an inner cut face;
        # its complete area must coincide with the source outer envelope.
        common_area = sum(piece.Area() for piece in face.intersect(outer_surfaces).Faces())
        if abs(face.Area()-common_area) <= DISTANCE_TOLERANCE:
            retained_skin_faces.append(face)
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


def display_free_cover_reading(reading, f, cover_builder, seated, free, tip):
    """Read the printable preform separately from the nominal installed cover."""
    import cadquery as cq
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    seated, free, tip = (shape(part).moved(frame.inverse) for part in (seated, free, tip))
    lips = shape(f.build_display_cover_lips()).moved(frame.inverse)
    n0, n1 = f.display_clip_bottom_n, f.display_clip_top_n
    anchor = cover_builder.bezel_n_bottom
    slope = f._display_snap.X_PRELOAD/(anchor-n1)

    def preload(n):
        return slope*max(0.0, anchor-n)

    def native_band(low, high):
        return cq.Solid.makeBox(100.0, 150.0, high-low, cq.Vector(-50.0, -50.0, low))

    upper = native_band(anchor, f.display_cover_top_n+1.0)
    installed_bezel, free_bezel = seated.intersect(upper), free.intersect(upper)
    bezel_delta = (outside_material_volume(installed_bezel, free_bezel)
                   +outside_material_volume(free_bezel, installed_bezel))
    reading.add("shape:display-cover-unchanged-bezel", volume(installed_bezel) > VOLUME_TOLERANCE
                and bezel_delta <= VOLUME_TOLERANCE,
                unchanged_from_n_mm=clean_number(anchor),
                symmetric_difference_mm3=clean_number(bezel_delta),
                method="exact symmetric difference of the complete nominal and printed solids above the bezel underside")

    shift_samples, height_samples, missing_lips = [], [], []
    s0, s1 = f.display_clip_s_bottom, f.display_clip_s_top
    for side in (-1, 1):
        halfspace = cq.Solid.makeBox(50.0, 150.0, 100.0,
                                    cq.Vector(0.0 if side == 1 else -50.0, -50.0, -30.0))
        printed_lip = lips.intersect(halfspace).transformGeometry(cover_builder.relaxed_wing_transform(side))
        missing_lips.append(outside_material_volume(printed_lip, free))
        for fraction in (0.125, 0.5, 0.875):
            station = s0+(s1-s0)*fraction
            for n in (n0+0.25, (n0+n1)/2.0, n1-0.25):
                nominal = line_intervals(seated, (0.0, station, n), (side, 0.0, 0.0), 30.0)
                printed = line_intervals(free, (0.0, station, n), (side, 0.0, 0.0), 30.0)
                errors = ([abs(a-b-preload(n)) for a, b in zip(nominal[-1], printed[-1])]
                          if nominal and printed else [30.0, 30.0])
                shift_samples.append({"side": side, "s_mm": clean_number(station), "n_mm": clean_number(n),
                                      "expected_inward_shift_mm": clean_number(preload(n)),
                                      "inner_and_outer_shift_error_mm": [clean_number(v) for v in errors],
                                      "printed_lateral_stock_mm": clean_number(printed[-1][1]-printed[-1][0]) if printed else 0.0})
            middle = line_intervals(seated, (0.0, station, (n0+n1)/2.0), (side, 0.0, 0.0), 30.0)
            if not middle:
                height_samples.append({"side": side, "s_mm": clean_number(station), "normal_height_mm": 0.0})
                continue
            x = side*sum(middle[-1])/2.0
            start = (x-side*preload(n0-0.1), station, n0-0.1)
            direction = cq.Vector(side*slope, 0.0, 1.0).normalized()
            chords = line_intervals(free, start, direction.toTuple(), (n1-n0+0.2)/direction.z)
            height = max((b-a for a, b in chords), default=0.0)*direction.z
            height_samples.append({"side": side, "s_mm": clean_number(station),
                                   "normal_height_mm": clean_number(height)})
    free_common = free.intersect(tip)
    interface_overlap = volume(free_common)
    lower = native_band(n0, anchor)
    unexpected_overlap = outside_material_volume(free_common, lower)
    parameter_error = max(abs(cover_builder.preload_inward_at(n)-preload(n)) for n in (n0, n1, anchor))
    reading.add("shape:display-cover-relaxed-preload", bool(shift_samples)
                and all(max(row["inner_and_outer_shift_error_mm"]) <= DISTANCE_TOLERANCE for row in shift_samples)
                and parameter_error <= DISTANCE_TOLERANCE
                and interface_overlap > VOLUME_TOLERANCE and unexpected_overlap <= VOLUME_TOLERANCE,
                preload_at_lip_top_mm=clean_number(preload(n1)),
                preload_at_lip_bottom_mm=clean_number(preload(n0)),
                nominal_radial_clearance_mm=f._display_snap.RADIAL_SLIP,
                shear_x_per_n=clean_number(slope),
                free_interference_with_rigid_tip_mm3=clean_number(interface_overlap),
                interference_outside_preformed_wings_mm3=clean_number(unexpected_overlap),
                samples=shift_samples,
                method="independent actual-solid X chords at three lip stations and three heights per wing, plus exact common volume against the rigid tip",
                scope="the relaxed print is intentionally narrower than the nominal seated reference; the joined end bridges are not an invertible elastic map, and installed equilibrium and preload force require the print trial")
    reading.add("wall:display-relaxed-lips", max(missing_lips) <= VOLUME_TOLERANCE
                and all(row["normal_height_mm"] >= f._display_snap.LIP_HEIGHT-DISTANCE_TOLERANCE for row in height_samples)
                and all(row["printed_lateral_stock_mm"] >= 1.0-DISTANCE_TOLERANCE for row in shift_samples),
                missing_complete_lip_witness_mm3=[clean_number(v) for v in missing_lips],
                required_normal_height_mm=f._display_snap.LIP_HEIGHT,
                required_lateral_stock_mm=1.0, height_samples=height_samples,
                method="complete affine lip witnesses inside the printable solid, with six actual material chords projected onto N and eighteen lateral lip sections")

    # Re-read the actual free solid along the mapped surface normals. The
    # centre seam is excluded here and has independent bridge readings below.
    skin_samples = []
    for name in ("wall:display-finished-neck-rim", "wall:display-rear-rim"):
        for row in reading.rows[name]["samples"]:
            x, station, n = row["point_x_s_n_mm"]
            if abs(x) < 1.0:
                continue
            side = 1 if x > 0.0 else -1
            point = cq.Vector(x-side*preload(n), station, n)
            vx, vs, vn = row["normal_inward"]
            inward = cq.Vector(vx, vs, vn-side*slope*vx if n < anchor else vn).normalized()
            start = point+inward.multiply(DISTANCE_TOLERANCE)
            chords = line_intervals(free, start.toTuple(), inward.toTuple(), 6.0)
            stock = chords[0][1]+DISTANCE_TOLERANCE if chords and chords[0][0] < 0.001 else 0.0
            rim_evidence = open_lower_rim_evidence(free, f, point, inward, stock)
            skin_samples.append({"source_section": name, "point_x_s_n_mm": [clean_number(v) for v in point.toTuple()],
                                 "normal_inward": [clean_number(v) for v in inward.toTuple()],
                                 "open_rim_evidence": rim_evidence,
                                 "normal_stock_mm": clean_number(stock)})
    minimum = min((row["normal_stock_mm"] for row in skin_samples
                   if row["open_rim_evidence"] is None), default=0.0)
    reading.add("wall:display-relaxed-cosmetic-rims", bool(skin_samples) and minimum >= 1.0-DISTANCE_TOLERANCE
                and all(row["open_rim_evidence"]["passed"] for row in skin_samples
                        if row["open_rim_evidence"] is not None),
                minimum_sampled_normal_stock_mm=clean_number(minimum), required_mm=1.0,
                minimum_unqualified_normal_chord_mm=clean_number(min((row["normal_stock_mm"] for row in skin_samples), default=0.0)),
                samples=skin_samples,
                method="actual printable-solid material chords on the affine images of the finished corner and rear-rim sections, using inverse-transpose surface normals",
                scope="sampled material after the wing union; not a global thickness or elastic-deformation certificate")

    bridge_samples = []
    faces = free.Faces()
    for x in (-3.0, 0.0, 3.0):
        for front in (True, False):
            station = DISTANCE_TOLERANCE if front else f._display_housing_center_s
            for n in (14.25, 16.0, 18.0, anchor-0.1, anchor+0.1):
                spans = line_intervals(free, (x, station, n), (0.0, 1.0, 0.0), f.display_head_s_max+1.0-station)
                if front:
                    # Below the front's neck-following rim, a forward ray may
                    # find only the distant rear wall. That is not a front
                    # bridge sample and must not be reported as one.
                    spans = [(a, b) for a, b in spans
                             if station+b < f._display_housing_center_s]
                if not spans:
                    continue
                point = cq.Vector(x, station+(spans[0][0] if front else spans[-1][1]), n)
                if front:
                    inward = cq.Vector(0.0, 1.0, 0.0)
                else:
                    vertex = cq.Vertex.makeVertex(*point.toTuple())
                    face = min(faces, key=lambda candidate: candidate.distance(vertex))
                    inward = face.normalAt(point)
                    if inward.y > 0.0:
                        inward = inward.multiply(-1.0)
                start = point+inward.multiply(DISTANCE_TOLERANCE)
                chords = line_intervals(free, start.toTuple(), inward.toTuple(), 6.0)
                stock = chords[0][1]+DISTANCE_TOLERANCE if chords and chords[0][0] < 0.001 else 0.0
                bridge_samples.append({"end": "front" if front else "rear", "x_mm": x, "n_mm": n,
                                       "normal_stock_mm": clean_number(stock)})
    minimum_bridge = min((row["normal_stock_mm"] for row in bridge_samples), default=0.0)
    reading.add("wall:display-relaxed-end-bridges", minimum_bridge >= 1.0-DISTANCE_TOLERANCE
                and {(row["end"], row["x_mm"]) for row in bridge_samples}
                == {(end, x) for end in ("front", "rear") for x in (-3.0, 0.0, 3.0)},
                minimum_sampled_normal_stock_mm=clean_number(minimum_bridge), required_mm=1.0,
                samples=bridge_samples,
                method="actual free-solid front and rear bridge chords at X0/±3, below and above the unchanged-bezel join",
                scope="named central-union sections; the bridges' installed bending and any load on the glass remain physical trial observations")


def display_opening_rim_reading(reading, f, cover_builder, seated, free):
    """Read the real planar opening band independently of show-wall normals."""
    import cadquery as cq
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    outside = shape(f.build_display_outer_envelope()).moved(frame.inverse)
    show_faces = [face for face in outside.Faces() if face.geomType() != "PLANE"]
    cut_normal = cq.Vector(0.0, 1.0, -f.display_cover_rear_rim_ds_dn).normalized()
    start_s = f.display_cover_rear_rim_s0+f.display_cover_rear_rim_ds_dn*f.display_cover_bottom_n
    for state, part in (("seated", seated), ("relaxed", free)):
        part = shape(part).moved(frame.inverse)
        cut_faces = [face for face in part.Faces() if face.geomType() == "PLANE"
                     and face.Center().y >= start_s-DISTANCE_TOLERANCE
                     and face.normalAt().dot(cut_normal) > 1.0-1e-6]
        face_rows, pairs, samples = [], [], []
        for fi, face in enumerate(cut_faces):
            outer_edges, inner_edges, bottom_edges = [], [], []
            for ei, edge in enumerate(face.Edges()):
                matches = []
                for t in (0.25, 0.5, 0.75):
                    point = edge.positionAt(t)
                    candidates = ([point] if state == "seated" else
                                  [cq.Vector(point.x+side*cover_builder.preload_inward_at(point.z),
                                             point.y, point.z) for side in (-1, 1)])
                    matches.append(min(skin.distance(cq.Vertex.makeVertex(*candidate.toTuple()))
                                       for skin in show_faces for candidate in candidates) <= DISTANCE_TOLERANCE)
                bounds = edge.BoundingBox()
                if all(matches):
                    outer_edges.append((ei, edge))
                elif max(abs(bounds.zmin-f.display_cover_bottom_n),
                         abs(bounds.zmax-f.display_cover_bottom_n)) <= DISTANCE_TOLERANCE:
                    bottom_edges.append(ei)
                else:
                    inner_edges.append((ei, edge))
            face_rows.append({"face": fi, "outer_edge_count": len(outer_edges),
                              "inner_edge_count": len(inner_edges),
                              "excluded_flat_lower_join_edge_indices": bottom_edges})
            for oi, outer_edge in outer_edges:
                for ii, inner_edge in inner_edges:
                    pairs.append({"face": fi, "outer_edge": oi, "inner_edge": ii,
                                  "minimum_complete_edge_distance_mm": clean_number(outer_edge.distance(inner_edge))})
                for t in (0.02, 0.05, 0.1, 0.2, 0.35, 0.5, 0.65, 0.8, 0.9, 0.95, 0.98):
                    point = outer_edge.positionAt(t)
                    transverse = outer_edge.tangentAt(t).cross(cut_normal).normalized()
                    inset = point-cut_normal.multiply(DISTANCE_TOLERANCE)
                    options = []
                    for direction in (transverse, transverse.multiply(-1.0)):
                        start = inset-direction.multiply(DISTANCE_TOLERANCE)
                        spans = line_intervals(part, start.toTuple(), direction.toTuple(), 20.0)
                        stock = spans[0][1]-spans[0][0] if spans and spans[0][0] < 0.001 else 0.0
                        options.append((stock, direction))
                    stock, direction = max(options, key=lambda item: item[0])
                    samples.append({"face": fi, "edge": oi, "parameter": t,
                                    "point_x_s_n_mm": [clean_number(v) for v in point.toTuple()],
                                    "in_plane_direction": [clean_number(v) for v in direction.toTuple()],
                                    "continuous_material_stock_mm": clean_number(stock)})
        least_edge = min((row["minimum_complete_edge_distance_mm"] for row in pairs), default=0.0)
        least_stock = min((row["continuous_material_stock_mm"] for row in samples), default=0.0)
        reading.add(f"wall:display-rear-opening-rim-{state}", bool(cut_faces) and bool(pairs) and bool(samples)
                    and all(row["outer_edge_count"] and row["inner_edge_count"] for row in face_rows)
                    and min(least_edge, least_stock) >= 1.0-DISTANCE_TOLERANCE,
                    minimum_complete_boundary_distance_mm=clean_number(least_edge),
                    minimum_sampled_transverse_material_mm=clean_number(least_stock), required_mm=1.0,
                    cut_face_normal=[clean_number(v) for v in cut_normal.toTuple()],
                    faces=face_rows, complete_boundary_pairs=pairs, transverse_samples=samples,
                    method="complete outer-to-inner edge distances on every actual rear opening face, with tangent-perpendicular material chords within that plane; outer edges match the source show skin at three points, using the inverse wing preform for the relaxed part",
                    scope="the physical opening band, separate from inward show-wall normals; only the connecting flat lower-edge segments are excluded from the inner-boundary set")


def display_rear_closure_reading(reading, f, tip, cover, body):
    """Look for an actual printed rear barrier behind occupied electronics."""
    import cadquery as cq
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.IntCurvesFace import IntCurvesFace_ShapeIntersector
    from OCP.TopAbs import TopAbs_IN, TopAbs_ON
    from OCP.gp import gp_Dir, gp_Lin, gp_Pnt
    origin, _, normal = f._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    cover = shape(cover).moved(frame.inverse)
    printed = cq.Compound.makeCompound([shape(tip).moved(frame.inverse), cover])
    hardware = cq.Compound.makeCompound([
        shape(body).moved(frame.inverse),
        shape(f.build_display_ribbon_transition()).moved(frame.inverse)])

    def prepare_ray(part):
        # Reuse the exact surface intersector and solid classifiers. Building
        # a new Boolean common of the component-rich display and an edge for
        # every ray is unnecessarily expensive and is poorly conditioned on
        # component boundaries. Surface crossings partition the line; exact
        # midpoint classification identifies each material interval.
        reader = IntCurvesFace_ShapeIntersector()
        reader.Load(part.wrapped, 1e-7)
        classifiers = [BRepClass3d_SolidClassifier(solid.wrapped) for solid in part.Solids()]

        def intervals(x, s, n, length):
            reader.Perform(gp_Lin(gp_Pnt(x, s, n), gp_Dir(0.0, 1.0, 0.0)), 0.0, length)
            if not reader.IsDone():
                raise RuntimeError("rear closure: exact surface intersection failed")
            crossings = sorted([0.0, length]+[max(0.0, min(length, reader.WParameter(i)))
                                              for i in range(1, reader.NbPnt()+1)])
            unique = []
            for value in crossings:
                if not unique or value-unique[-1] > 1e-7:
                    unique.append(value)
            spans = []
            for a, b in zip(unique, unique[1:]):
                if b-a <= DISTANCE_TOLERANCE:
                    continue
                inside = False
                for classifier in classifiers:
                    classifier.Perform(gp_Pnt(x, s+(a+b)/2.0, n), 1e-7)
                    inside |= classifier.State() in (TopAbs_IN, TopAbs_ON)
                if inside:
                    if spans and a-spans[-1][1] <= DISTANCE_TOLERANCE:
                        spans[-1] = (spans[-1][0], b)
                    else:
                        spans.append((a, b))
            return spans
        return intervals

    hardware_ray, printed_ray = prepare_ray(hardware), prepare_ray(printed)
    start_s = f.display_s_bottom
    end_s = max(f.display_head_s_max, cover.BoundingBox().ymax)+1.0
    crosschecks = []
    for x, n in ((-10.0, f.display_feet_n+4.1), (0.0, f.display_feet_n+4.1),
                 (8.5, f.display_feet_n+8.1), (12.0, f.display_feet_n+9.1)):
        for name, part, reader in (("hardware", hardware, hardware_ray),
                                    ("printed", printed, printed_ray)):
            ray_spans = reader(x, start_s, n, end_s-start_s)
            common_spans = line_intervals(part, (x, start_s, n), (0.0, 1.0, 0.0), end_s-start_s)
            error = (max((abs(a-b) for ray, common in zip(ray_spans, common_spans)
                          for a, b in zip(ray, common)), default=0.0)
                     if len(ray_spans) == len(common_spans) else float("inf"))
            crosschecks.append({"part": name, "x_mm": x, "n_mm": clean_number(n),
                                "interval_count_matches": len(ray_spans) == len(common_spans),
                                "maximum_endpoint_error_mm": clean_number(error) if math.isfinite(error) else None,
                                "passed": error <= DISTANCE_TOLERANCE})
    heights = sorted({f.display_feet_n+0.1+0.5*index for index in range(21)}
                     | {f.display_face_n-0.01})
    rows = []
    for x in (-12.0, -10.0, -8.5, -6.0, -3.0, 0.0, 3.0, 6.0, 8.5, 10.0, 12.0):
        for n in heights:
            occupied = hardware_ray(x, start_s, n, end_s-start_s)
            if not occupied:
                continue
            hardware_back = start_s+occupied[-1][1]
            probe_s = hardware_back+DISTANCE_TOLERANCE
            barrier = printed_ray(x, probe_s, n, end_s-probe_s)
            spans = [(a+probe_s, b+probe_s) for a, b in barrier]
            present = any(b-a > DISTANCE_TOLERANCE for a, b in spans)
            rows.append({"x_mm": x, "n_mm": clean_number(n),
                         "hardware_rear_s_mm": clean_number(hardware_back),
                         "printed_rear_barrier_s_intervals_mm":
                             [[clean_number(a), clean_number(b)] for a, b in spans],
                         "present": present})
    reading.add("coverage:display-rear-electronics", bool(rows)
                and all(row["present"] for row in rows)
                and all(row["passed"] for row in crosschecks),
                sample_count=len(rows), missing_barrier_count=sum(not row["present"] for row in rows),
                independent_edge_boolean_crosschecks=crosschecks,
                samples=rows,
                method="exact +S surface crossings and solid-classified material intervals behind occupied display/component or branch-ribbon sections, through the nominal assembled tip and cover",
                scope="sampled rear line-of-sight closure around the actual hardware; stock and rim thickness have separate readings. This is not a water-seal or all-angle visibility certificate")


def display_reading(reading, f, assembly, parts, body, free_cover):
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

    display_retention_reading(reading, f, parts, body, assembly.build_display_screen(), ribbon, tubes,
                              free_cover, assembly.faucet_display_cover)
    display_loading_reading(reading, f, assembly.faucet_display_cover, body,
                            assembly.build_display_screen(), free_cover)
    display_cartridge_axial_reading(reading, f, parts, cover, free_cover, body,
                                    assembly.build_display_screen(), tubes)
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1.0, 0.0, 0.0), normal=normal))
    carried_hardware = cq.Compound.makeCompound([
        body.moved(frame.inverse), shape(assembly.build_display_screen()).moved(frame.inverse)])
    box = carried_hardware.BoundingBox()
    device_sweep = cq.Solid.makeBox(box.xlen, box.ylen,
                                    box.zlen+f.display_cartridge_lift_n,
                                    cq.Vector(box.xmin, box.ymin, box.zmin)).moved(frame)
    overlap = volume(device_sweep.intersect(full))
    reading.add("motion:cartridge-device-complete-normal", overlap <= VOLUME_TOLERANCE,
                normal_stroke_mm=[0.0, f.display_cartridge_lift_n],
                conservative_stroke_bounds_x_s_n_mm={
                    "minimum": [clean_number(v) for v in (box.xmin, box.ymin, box.zmin)],
                    "maximum": [clean_number(v) for v in
                                (box.xmax, box.ymax, box.zmax+f.display_cartridge_lift_n)]},
                fixed_printed_overlap_mm3=clean_number(overlap),
                method="exact conservative box containing the complete carried display and glass throughout the final normal stroke, against both shell halves",
                scope="complete rigid hardware-to-printed-body seating bound; cover spreading and finished tubing/ribbon clearance have separate readings")
    pads = shape(f.build_display_feet_pads())
    missing = volume(pads.cut(tip))
    backing = pads.translate(normal.multiply(-f.display_foot_pad_depth))
    missing_backing = volume(backing.cut(tip))
    reading.add("wall:display-foot-pads", missing <= VOLUME_TOLERANCE
                and missing_backing <= VOLUME_TOLERANCE
                and f.display_foot_pad_depth >= f.wall_thickness_min-DISTANCE_TOLERANCE,
                missing_complete_pad_material_mm3=clean_number(missing),
                missing_complete_backing_material_mm3=clean_number(missing_backing),
                pad_footprint_mm=[f.display_foot_pad_width, f.display_foot_pad_width],
                pad_depth_mm=f.display_foot_pad_depth,
                continuous_vertical_depth_including_backing_mm=2.0*f.display_foot_pad_depth,
                required_functional_depth_mm=f.wall_thickness_min,
                method="complete four support-pad witnesses plus equally deep full-footprint backing blocks directly below them inside the final single-solid tip")
    outside = shape(f.build_display_outer_envelope())
    side = cq.Compound.makeCompound([face for face in outside.Faces() if face.geomType() != "PLANE"])
    side_wall = side.distance(shape(f.build_display_cover_inner_envelope()))
    reading.add("wall:display-cosmetic-shroud", side_wall >= 1.0-DISTANCE_TOLERANCE,
                minimum_loft_side_separation_mm=clean_number(side_wall), required_mm=1.0,
                method="exact separation of the complete outer loft's curved side faces and inner cover cavity")
    display_rim_reading(reading, f, cover)
    display_free_cover_reading(reading, f, assembly.faucet_display_cover, cover, free_cover, tip)
    display_opening_rim_reading(reading, f, assembly.faucet_display_cover, cover, free_cover)
    display_rear_closure_reading(reading, f, tip, cover, body)
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


def display_trial_reading(reading, f, parts, free_cover):
    sys.path.insert(0, str(ROOT / "hardware/printed-parts/fixtures/faucet-display-snap"))
    import faucet_display_snap_trial as trial
    housing, cover, clip, dimensions = trial.build_trial()
    tip = shape(parts["shell_tip"])
    boundary = max(dimensions["complete_head_end_s_mm"], f.display_ribbon_reference_start_s)+1.0
    witness = tip.intersect(shape(trial.trial_region(boundary)))
    missing = volume(witness.cut(shape(housing)))
    extra = volume(shape(housing).cut(tip))
    cover_delta = volume(shape(cover).cut(shape(free_cover))) + volume(shape(free_cover).cut(shape(cover)))
    cable_clipped = volume(shape(f.build_display_ribbon_transition()).cut(shape(clip)))
    reading.add("fixture:complete-display-fit-trial", max(missing, extra, cover_delta, cable_clipped) <= VOLUME_TOLERANCE,
                missing_head_or_anchor_material_mm3=clean_number(missing),
                added_housing_material_mm3=clean_number(extra),
                cover_symmetric_difference_mm3=clean_number(cover_delta),
                clipped_side_entry_ribbon_mm3=clean_number(cable_clipped),
                retained_geometry=dimensions,
                method="complete production head region through the cable branch, and exact complete relaxed printable cover")
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
    free_cover = assembly.faucet_display_cover.build_display_cover()
    solids_reading(reading, parts)
    mesh_reading(reading, f, parts)
    solids_reading(reading, {"display_cover_relaxed_print": free_cover})
    mesh_reading(reading, f, {"display_cover_relaxed_print": free_cover})
    lower_outer_mesh_reading(reading, f)
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
    lower_passage_join_reading(reading, base)
    display_reading(reading, f, assembly, parts, assembly.build_display_body(), free_cover)
    display_trial_reading(reading, f, parts, free_cover)
    lever_reading(reading, assembly, parts)
    ribbon_reading(reading, f, assembly, parts)
    clearance_reading(reading, "seat:plate-gasket", plate, parts["above_counter_gasket"])
    after = hashes(paths)
    if before != after:
        raise RuntimeError("a faucet source changed during the reading; rerun after its build settles")
    passed = all(row["passed"] for row in reading.rows.values())
    result = {"schema_version": 1,
              "scope": "Live B-rep builders and serialized STL surfaces, separate nominal seated and relaxed printable display covers, fixed donor, dimensional display and tube models; "
                       "named wall witnesses and sampled sections. No global minimum-wall certification.",
              "nominal_cad_only": True,
              "distance_tolerance_mm": DISTANCE_TOLERANCE,
              "overlap_tolerance_mm3": VOLUME_TOLERANCE,
              "geometry_source_sha256": before,
              "display_assembly": {
                  "sequence": "load the display into the opened cover, lift and slide the cartridge from the outlet, then seat it normally",
                  "rigid_positions_local_s_n_mm": [
                      [-f.display_cartridge_slide_s, f.display_cartridge_lift_n],
                      [0.0, f.display_cartridge_lift_n], [0.0, 0.0]],
                  "display_loading_travel_n_mm": f.display_loading_travel_n,
                  "scope": "Rigid fit references and independent wing-clearance demand; no elastic deformation or force prediction."},
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
                  "Factory plastic spreading to load the display without forcing its PCB/glass edges, and feeding the temporary flexible ribbon branch during cartridge travel.",
                  "PET-GF cover-wall spreading, installed shape and end-bridge bending, seating and pull-off force, lip strength, repeated closure and release in the complete display fit trial."],
              "passed": passed}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    temporary.replace(args.output)
    print(f"{'PASS' if passed else 'FAIL'} faucet geometry: {len(reading.rows)} readings; {args.output}", flush=True)
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
