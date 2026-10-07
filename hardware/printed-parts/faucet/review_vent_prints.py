"""Read bung webs and wire apertures from the retained native commanded beads.

This compares ideal bead envelopes with the source STL section. It does not
measure deposited TPU, compression, sealing or assembly force.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points, polygonize, substring, unary_union
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_vent_prints as preparation
from prepare_display_print import extrusion_segments


def section(mesh: trimesh.Trimesh, z: float) -> tuple:
    edges = trimesh.intersections.mesh_plane(mesh, [0.0, 0.0, 1.0], [0.0, 0.0, z])
    if not len(edges):
        raise ValueError(f"No bung STL section at Z{z:g}")
    planar = np.round(edges[:, :, :2], 6)
    loops = [Polygon(polygon.exterior) for polygon in polygonize(
        unary_union([LineString(edge) for edge in planar]))]
    outer = max(loops, key=lambda loop: loop.area)
    holes = [loop for loop in loops if loop is not outer and outer.covers(loop.representative_point())]
    return outer.difference(unary_union(holes)), holes


def components(geometry):
    if geometry.is_empty:
        return []
    return list(geometry.geoms) if hasattr(geometry, "geoms") else [geometry]


def filled_section(mesh: trimesh.Trimesh, z: float, local_faces=None):
    edges = np.round(trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, z],
                                                   local_faces=local_faces)[:, :, :2], 6)
    if not len(edges):
        return Polygon()
    a, b = edges[:, 0], edges[:, 1]
    filled = []
    for polygon in polygonize(unary_union([LineString(edge) for edge in edges])):
        point = polygon.representative_point()
        crossing = (a[:, 1] > point.y) != (b[:, 1] > point.y)
        start, end = a[crossing], b[crossing]
        x = start[:, 0] + (point.y - start[:, 1]) * (end[:, 0] - start[:, 0]) / (end[:, 1] - start[:, 1])
        if np.count_nonzero(x > point.x) % 2:
            filled.append(polygon)
    return unary_union(filled)


def draw_polygon(axis, geometry, **kwargs):
    for shape in components(geometry):
        if shape.geom_type != "Polygon":
            continue
        xy = np.array(shape.exterior.coords)
        axis.fill(xy[:, 0], xy[:, 1], **kwargs)
        for ring in shape.interiors:
            xy = np.array(ring.coords)
            axis.fill(xy[:, 0], xy[:, 1], facecolor="white", edgecolor="none")


def connected_web(commanded, source, span, foot, half_width):
    """Measure a local material route between the two bore-wall neighborhoods.

    The corridor is only one emitted bead wide on either side of the shortest
    inter-bore line. It cannot escape around the outside of the bung. Eroding
    that local material and testing the two transverse anchor lines measures
    the narrowest connected route, including a route around an enclosed pore.
    """
    points = np.array(span.coords)
    direction = (points[1] - points[0]) / span.length
    normal = np.array([-direction[1], direction[0]])
    inset = min(foot + .12, span.length / 3)
    anchor_points = (points[0] + inset * direction, points[1] - inset * direction)
    anchors = [LineString([point - half_width * normal, point + half_width * normal])
               for point in anchor_points]
    local = commanded.intersection(source).intersection(span.buffer(half_width))

    def joins(radius):
        return any(piece.intersects(anchors[0]) and piece.intersects(anchors[1])
                   for piece in components(local.buffer(-radius)))

    connected = joins(0)
    lower, upper = 0.0, half_width
    if connected:
        for _ in range(16):
            middle = (lower + upper) / 2
            if joins(middle):
                lower = middle
            else:
                upper = middle
    return {"local_corridor_half_width_mm": half_width,
            "anchor_inset_from_bore_boundary_mm": inset,
            "local_material_connected": connected,
            "connected_material_path_width_mm": 2 * lower}


def seal_review(project: Path | None = None) -> dict:
    project = preparation.SEALS / "vent-bungs-tpu85a.3mf" if project is None else project
    manifest = json.loads(project.with_suffix(".print.json").read_text())
    readiness = json.loads(project.with_suffix(".readiness.json").read_text())
    with zipfile.ZipFile(project) as archive:
        settings = json.loads(archive.read(preparation.writer.SETTINGS_MEMBER))
    preparation.verify_sources(manifest)
    native = readiness["native"]
    gcode = preparation.ROOT / native["archive"]
    directory = gcode.parent
    loose = directory / "plate_1.gcode"
    if preparation.sha(loose) != native["gcode_sha256"]:
        raise ValueError("Bung bead review must use the validated native G-code")
    rows = {row["identify_id"]: row for row in manifest["parts"] if row["name"].endswith("bung")}
    roads = {key: {} for key in rows}
    for segment in extrusion_segments(loose):
        row = rows.get(segment["object"])
        if row is None or segment["feature"].startswith("Support"):
            continue
        rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
        local = ((np.array([segment["a"], segment["b"]]) - row["plate_translation_mm"])
                 @ rotation + row["source_center_mm"])
        if np.max(np.abs(local[:, 2] - local[0, 2])) > .005:
            raise ValueError("Bung review requires flat planar model roads")
        layer = round(float(local[0, 2]), 4)
        roads[segment["object"]].setdefault(layer, []).append(
            LineString(local[:, :2]).buffer(segment["width"] / 2.0, cap_style=1, join_style=1))
    records = []
    fig, axes = plt.subplots(2, 3, figsize=(12.0, 8.4), constrained_layout=True)
    for index, (label, row) in enumerate(rows.items()):
        mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
        layers = sorted(roads[label])
        if not layers:
            raise ValueError(f"No native model roads for {row['name']}")
        # The first flange layer and two separated axial-body layers expose
        # elephant-foot compensation, normal-body webs and the final bore rim.
        selected = [layers[0], min(layers, key=lambda z: abs(z - 2.4)), layers[-1]]
        readings = []
        previous_z = 0.0
        for z in layers:
            section_z = z - (z - previous_z) / 2.0
            previous_z = z
            source, holes = section(mesh, max(mesh.bounds[0, 2] + .01, section_z))
            commanded = unary_union(roads[label][z])
            foot = float(settings["elefant_foot_compensation"]) if z == layers[0] else 0.0
            core = source.buffer(-max(.08, foot + .02))
            missing = core.difference(commanded)
            voids = [Polygon(ring) for polygon in components(commanded)
                     if polygon.geom_type == "Polygon" for ring in polygon.interiors]
            bore_voids = [[void for void in voids if void.covers(hole.centroid)] for hole in holes]
            bore_contours_closed = (all(len(void) == 1 for void in bore_voids)
                                    and len({void[0].wkb for void in bore_voids if len(void) == 1}) == len(holes))
            pores = [void.intersection(source) for void in voids
                     if not any(void.covers(hole.centroid) for hole in holes)]
            wires = [hole for hole in holes if .4 <= hole.area <= 2.0]
            if len(wires) != 4:
                raise ValueError(f"Expected four individual wire holes at {row['name']} Z{z:g}; got {len(wires)}")
            apertures = [{"center_xy_mm": list(hole.centroid.coords)[0],
                          "stl_diameter_from_area_mm": float(np.sqrt(4.0 * hole.area / np.pi)),
                          "commanded_centered_clear_diameter_mm": 2.0 * float(commanded.distance(hole.centroid))}
                         for hole in sorted(wires, key=lambda hole: hole.centroid.x)]
            for aperture, hole in zip(apertures, sorted(wires, key=lambda hole: hole.centroid.x)):
                wire_voids = [void for void in voids if void.covers(hole.centroid)]
                if len(wire_voids) != 1:
                    raise ValueError("A wire bore must be one enclosed commanded void")
                void = wire_voids[0]
                vertices = np.array(void.exterior.coords)
                aperture["commanded_void_area_equivalent_diameter_mm"] = float(np.sqrt(4 * void.area / np.pi))
                aperture["commanded_circumscribed_void_diameter_mm"] = 2 * float(np.max(
                    np.linalg.norm(vertices - np.array(hole.centroid.coords)[0], axis=1)))
            webs = []
            for a_index, first in enumerate(holes):
                for second in holes[:a_index]:
                    a, b = nearest_points(first, second)
                    span = LineString([a, b])
                    if span.length >= 2.0:
                        continue
                    target = substring(span, min(foot + .02, span.length / 2.0),
                                       max(span.length / 2.0, span.length - foot - .02))
                    uncovered = target.difference(commanded)
                    web = {"endpoints_xy_mm": [list(a.coords)[0], list(b.coords)[0]],
                                 "source_web_mm": float(span.length),
                                 "compensated_checked_span_mm": float(target.length),
                                 "commanded_covered_length_mm": float(span.intersection(commanded).length),
                                 "largest_uncovered_gap_mm": max((piece.length for piece in components(uncovered)), default=0.0)}
                    web.update(connected_web(commanded, source, span, foot,
                                             float(settings["line_width"])))
                    webs.append(web)
            reading = {"layer_top_z_mm": z, "wire_bores": apertures, "adjacent_webs": webs,
                       "stl_section_z_mm": section_z,
                       "first_layer_elephant_foot_compensation_mm": foot,
                       "source_core_area_mm2": float(core.area),
                       "commanded_missing_core_area_mm2": float(missing.area),
                       "bore_contours_closed_and_separate": bore_contours_closed,
                       "enclosed_internal_pore_area_mm2": float(sum(pore.area for pore in pores)),
                       "largest_enclosed_internal_pore_area_mm2": float(max((pore.area for pore in pores), default=0)),
                       "minimum_wire_clear_diameter_mm": min(item["commanded_centered_clear_diameter_mm"] for item in apertures),
                       "maximum_web_gap_mm": max((item["largest_uncovered_gap_mm"] for item in webs), default=0.0)}
            # With 2.2 mm wire pitch and the supplier's maximum 1.3 mm
            # jacket, d >= 0.915 keeps (1.3-d)/(2.2-d) at or below 30%.
            # This is the nominal web-squeeze starting guide, not measured
            # TPU compression or proof of sealing.
            reading["minimum_wire_clear_diameter_required_mm"] = .915
            reading["wire_bores_open"] = reading["minimum_wire_clear_diameter_mm"] >= .915
            reading["webs_continuous_in_commanded_envelope"] = all(web["local_material_connected"] for web in webs)
            reading["minimum_connected_web_path_width_mm"] = min((web["connected_material_path_width_mm"] for web in webs), default=0)
            readings.append(reading)
            if z not in selected:
                continue
            column = selected.index(z)
            axis = axes[index, column]
            draw_polygon(axis, source, facecolor="#dce0e5", edgecolor="#343b43", linewidth=.5)
            draw_polygon(axis, commanded.intersection(source), facecolor="#2f8196", edgecolor="none", alpha=.70)
            draw_polygon(axis, missing, facecolor="#ca423e", edgecolor="none")
            for aperture in apertures:
                x, y = aperture["center_xy_mm"]
                axis.plot(x, y, "+", color="#343b43", markersize=5)
            axis.set_aspect("equal")
            axis.set_title(f"{'Upstream' if index == 0 else 'Downstream'} · layer Z{z:.2f} mm", fontsize=11)
            axis.set_xlabel("mm", fontsize=9)
            axis.set_ylabel("mm", fontsize=9)
            axis.tick_params(labelsize=9)
        core = [item for item in readings if mesh.bounds[0, 2] + .2 <= item["stl_section_z_mm"] <= mesh.bounds[1, 2] - .2]
        core_wires = [wire for item in core for wire in item["wire_bores"]]
        records.append({"part": row["name"], "stl_sha256": row["stl_sha256"],
                        "all_native_model_layers_reviewed": len(layers),
                        "wire_contact_core": {"excluded_bore_lead_depth_mm_per_end": .2,
                                              "native_layers": len(core),
                                              "minimum_centered_clear_diameter_mm": min(w["commanded_centered_clear_diameter_mm"] for w in core_wires),
                                              "maximum_centered_clear_diameter_mm": max(w["commanded_centered_clear_diameter_mm"] for w in core_wires),
                                              "maximum_area_equivalent_void_diameter_mm": max(w["commanded_void_area_equivalent_diameter_mm"] for w in core_wires),
                                              "maximum_circumscribed_void_diameter_mm": max(w["commanded_circumscribed_void_diameter_mm"] for w in core_wires)},
                        "readings": readings, "pass": all(item["wire_bores_open"] and item["webs_continuous_in_commanded_envelope"] and item["bore_contours_closed_and_separate"] for item in readings)})
    fig.suptitle("TPU bungs: source section (grey), native commanded beads (blue), unfilled core (red)", fontsize=12)
    fig.savefig(directory / "bung-commanded-beads.png", dpi=180)
    plt.close(fig)
    result = {"schema": 1, "native_archive": native["archive"],
              "native_archive_sha256": native["archive_sha256"], "gcode_sha256": native["gcode_sha256"],
              "project_sha256": readiness["project_sha256"], "source_sha256": manifest["source_sha256"],
              "analysis_script_sha256": preparation.sha(Path(__file__)),
              "gcode_reader_sha256": preparation.sha(HERE / "prepare_display_print.py"),
              "method": "Buffered native model centerlines at emitted widths; every native bung model layer checked against its mid-height STL section. All bore contours must be closed and separate. Local inter-bore material paths are tested inside a corridor of one emitted line-width on each side of the shortest bore-to-bore span; erosion gives a connected-path width. Straight-span gaps and enclosed pore areas remain recorded. First-layer elephant-foot compensation retained; three layers drawn.",
              "parts": records, "pass": all(row["pass"] for row in records),
              "wire_aperture_guide": {"wire_pitch_mm": 2.2, "supplier_maximum_jacket_od_mm": 1.3,
                                      "maximum_nominal_web_squeeze_fraction": .30,
                                      "minimum_commanded_clear_diameter_mm": .915},
              "scope": "Commanded bead continuity and open wire holes. Deposited aperture size, compression, liquid sealing and assembly force are unmeasured.",
              "image": preparation.relative(directory / "bung-commanded-beads.png")}
    preparation.save(project.with_suffix(".bead-review.json"), result)
    print(json.dumps({"pass": result["pass"], "parts": [{"part": row["part"], "pass": row["pass"]} for row in records]}, indent=2))
    if not result["pass"]:
        raise SystemExit("Bung native bead review failed")
    return result


def tool_review() -> dict:
    project = preparation.SEALS / "vent-seal-tool-petgf.3mf"
    report = json.loads(project.with_suffix(".print.json").read_text())
    ready = json.loads(project.with_suffix(".readiness.json").read_text())
    preparation.verify_sources(report)
    row = report["parts"][0]
    directory = (preparation.ROOT / ready["native"]["archive"]).parent
    gcode = directory / "plate_1.gcode"
    if preparation.sha(gcode) != ready["native"]["gcode_sha256"]:
        raise ValueError("Tool review must use the validated native G-code")
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
    roads, support = {}, []
    for segment in extrusion_segments(gcode):
        if segment["object"] != row["identify_id"]:
            continue
        local = ((np.array([segment["a"], segment["b"]]) - row["plate_translation_mm"])
                 @ rotation + row["source_center_mm"])
        if segment["feature"].startswith("Support"):
            support.extend(local.tolist())
        else:
            roads.setdefault(round(float(local[0, 2]), 4), []).append(
                LineString(local[:, :2]).buffer(segment["width"] / 2))
    heights = sorted(roads)
    if not heights:
        raise ValueError("No native model roads for the perimeter tool")
    mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
    fig, axes = plt.subplots(1, 4, figsize=(14.5, 4.5), constrained_layout=True)
    indices = np.unique(np.linspace(0, len(mesh.vertices) - 1, min(20000, len(mesh.vertices)), dtype=int))
    vertices = mesh.vertices[indices]
    axes[0].scatter(vertices[:, 1], vertices[:, 2], s=.25, c="#aeb7c2", alpha=.5)
    if support:
        actual = np.array(support)
        indices = np.unique(np.linspace(0, len(actual) - 1, min(12000, len(actual)), dtype=int))
        axes[0].scatter(actual[indices, 1], actual[indices, 2], s=.25, c="#278c99", alpha=.6)
    axes[0].set_title("Tool and native supports")
    axes[0].set_xlabel("Y / mm")
    axes[0].set_ylabel("Z / mm")
    readings = []
    selected = [heights[-3], heights[-1], round(heights[-1] + .24, 4)]
    for axis, height in zip(axes[1:], selected):
        source = filled_section(mesh, height - .12)
        commanded = unary_union(roads.get(height, []))
        draw_polygon(axis, source, facecolor="#dce0e5", edgecolor="#343b43", linewidth=.5)
        draw_polygon(axis, commanded.intersection(source), facecolor="#2f8196", edgecolor="none", alpha=.8)
        missing = source.buffer(-.08).difference(commanded)
        draw_polygon(axis, missing, facecolor="#ca423e", edgecolor="none")
        axis.set_title(f"Tool tip · Z{height:.2f} mm")
        axis.set_xlabel("X / mm")
        axis.set_ylabel("Y / mm")
        readings.append({"layer_top_z_mm": height, "source_section_z_mm": height - .12,
                         "source_section_area_mm2": float(source.area),
                         "commanded_beads_present": height in roads,
                         "commanded_missing_inset_core_area_mm2": float(missing.area)})
    for axis in axes:
        axis.set_aspect("equal")
        axis.tick_params(labelsize=8)
    fig.savefig(directory / "tool-native-supports-and-tip.png", dpi=180)
    plt.close(fig)
    result = {"schema": 1, "native_archive": ready["native"]["archive"],
              "native_archive_sha256": ready["native"]["archive_sha256"],
              "gcode_sha256": ready["native"]["gcode_sha256"], "source_sha256": report["source_sha256"],
              "analysis_script_sha256": preparation.sha(Path(__file__)),
              "highest_native_model_layer_mm": heights[-1], "source_stl_maximum_z_mm": float(mesh.bounds[1, 2]),
              "high_tip_readings": readings, "support_centerline_endpoints": len(support),
              "cleanup_route": "Release the tree through the 19 mm open side slot. Cut sacrificial stock into small fragments; remove through the slot and both ends. Retain the main flat annular flange-bearing face and curved outside envelope.",
              "scope": "Native support locations and small upper slot-tip omission. The exact retained bearing area is measured separately from the CAD face; physical release, finish and insertion force remain unmeasured.",
              "image": preparation.relative(directory / "tool-native-supports-and-tip.png")}
    preparation.save(project.with_suffix(".tool-review.json"), result)
    print(json.dumps({"tool": row["name"], "highest_native_model_layer_mm": heights[-1], "high_tip_readings": readings}, indent=2))
    return result


def faucet_support_review(project: Path | None = None) -> dict:
    """Locate all support features, including bodies without interface labels."""
    import faucet_paths as paths
    project = HERE / "faucet-petgf.3mf" if project is None else project
    report = json.loads(project.with_suffix(".print.json").read_text())
    ready = json.loads(project.with_suffix(".readiness.json").read_text())
    preparation.verify_sources(report)
    directory = (preparation.ROOT / ready["native"]["archive"]).parent
    gcode = directory / "plate_1.gcode"
    if preparation.sha(gcode) != ready["native"]["gcode_sha256"]:
        raise ValueError("Support face review must use the validated native G-code")
    rows = {row["identify_id"]: row for row in report["parts"]}
    samples = {key: [] for key in rows}
    for segment in extrusion_segments(gcode):
        row = rows.get(segment["object"])
        if row is None or not segment["feature"].startswith("Support"):
            continue
        rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
        point = (np.array(segment["a"]) + segment["b"]) / 2.0
        world = (point - row["plate_translation_mm"]) @ rotation + row["source_center_mm"]
        samples[segment["object"]].append(world)

    def frame(points):
        dy = points[:, 1] - (paths.WATER_Y - paths.WATER_RADIUS)
        dz = points[:, 2] - paths.ARC_START_Z
        angle = np.arctan2(dz, dy)
        return np.column_stack((points[:, 0], (angle - paths.JOINT_ANGLE) * paths.WATER_RADIUS,
                                np.hypot(dy, dz) - paths.WATER_RADIUS))

    contacts, cloud = [], []
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.2), constrained_layout=True)
    for key, row in rows.items():
        if row["name"] not in {"faucet-shell-base", "industrial-shell-base", "faucet-shell-tip"} or not samples[key]:
            continue
        mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
        vertices = mesh.vertices
        indices = np.unique(np.linspace(0, len(vertices) - 1, min(25000, len(vertices)), dtype=int))
        axes[0].scatter(vertices[indices, 1], vertices[indices, 2], s=.10, c="#bcc3cb", alpha=.5, rasterized=True)
        actual = np.array(samples[key])
        indices = np.unique(np.linspace(0, len(actual) - 1, min(12000, len(actual)), dtype=int))
        axes[0].scatter(actual[indices, 1], actual[indices, 2], s=.18, c="#278c99", alpha=.65, rasterized=True)
        local = frame(actual)
        near = local[(local[:, 1] >= paths.UPSTREAM_GLAND_S - 5)
                     & (local[:, 1] <= paths.CONVERGE_START_S + 5)
                     & (np.abs(local[:, 0]) < 15)
                     & (np.abs(local[:, 2] - paths.SHELL_CENTER_N) < 16)]
        if not len(near):
            continue
        cloud.extend(near.tolist())
        axes[1].scatter(near[:, 1], near[:, 2], s=.6, c="#278c99", alpha=.5, rasterized=True)
        wet = near[(near[:, 1] >= paths.WET_START_S) & (near[:, 1] <= paths.WET_END_S)]
        axes[2].scatter(wet[:, 0], wet[:, 2], s=1.0, c="#278c99", alpha=.6, rasterized=True)
        selected = actual[np.unique(np.linspace(0, len(actual) - 1, min(2500, len(actual)), dtype=int))]
        closest, distance, triangles = trimesh.proximity.closest_point(mesh, selected)
        witnesses = []
        for point, gap, triangle in zip(closest, distance, triangles):
            if gap > .85:
                continue
            x, s, n = frame(np.array([point]))[0]
            if not paths.UPSTREAM_GLAND_S - 5 <= s <= paths.CONVERGE_START_S + 5:
                continue
            station = ("upstream gland" if s <= paths.WET_START_S
                       else "wet cavity and port" if s <= paths.WET_END_S
                       else "downstream gland" if s <= paths.CONVERGE_START_S
                       else "dry transition")
            witnesses.append({"station": station, "point_x_s_n_mm": [float(x), float(s), float(n)],
                              "distance_from_support_centerline_mm": float(gap),
                              "normal_world": mesh.face_normals[triangle].tolist()})
        retained = []
        for station in sorted({w["station"] for w in witnesses}):
            group = [w for w in witnesses if w["station"] == station]
            retained.extend(group[int(i)] for i in np.unique(np.linspace(0, len(group) - 1, min(12, len(group)), dtype=int)))
        contacts.append({"part": row["name"], "support_path_samples": len(actual),
                         "nearby_face_witness_counts": {station: sum(w["station"] == station for w in witnesses)
                                                         for station in sorted({w["station"] for w in witnesses})},
                         "representative_nearby_faces": retained})
    axes[0].set_title("Native support paths in CAD frame", fontsize=11)
    axes[0].set_xlabel("Y / mm")
    axes[0].set_ylabel("Z / mm")
    axes[0].set_aspect("equal")
    axes[1].axvspan(paths.UPSTREAM_GLAND_S, paths.WET_START_S, color="#b6b0c3", alpha=.25)
    axes[1].axvspan(paths.WET_START_S, paths.WET_END_S, color="#9dc6de", alpha=.2)
    axes[1].axvspan(paths.WET_END_S, paths.CONVERGE_START_S, color="#b6b0c3", alpha=.25)
    floor = paths.SHELL_CENTER_N - paths.CAVITY_RADIUS
    axes[1].plot([paths.PORT_START_S, paths.PORT_START_S + paths.PORT_LENGTH_S], [floor, floor], lw=4, c="#b26038")
    axes[1].set_title("Shared cavity: support paths and bottom port", fontsize=11)
    axes[1].set_xlabel("Arc distance after joint / mm")
    axes[1].set_ylabel("N outward from S / mm")
    axes[1].set_xlim(paths.UPSTREAM_GLAND_S - 5, paths.CONVERGE_START_S + 5)
    axes[1].set_ylim(-12, 20)
    axes[1].set_aspect("equal")
    for radius in (paths.SHELL_RADIUS, paths.CAVITY_RADIUS):
        axes[2].add_patch(plt.Circle((0, paths.SHELL_CENTER_N), radius, fill=False, color="#424950", lw=1))
    f_x, f_n, _, _, _ = paths.positions((paths.WET_START_S + paths.WET_END_S) / 2)
    for x, n, radius in ((0, 0, paths.WATER_OD / 2), (-f_x, f_n, paths.FLAVOR_OD / 2),
                         (f_x, f_n, paths.FLAVOR_OD / 2)):
        axes[2].add_patch(plt.Circle((x, n), radius, fill=False, color="#657585", lw=1, ls="--"))
    axes[2].set_title("Support paths within cavity; tube positions dashed", fontsize=11)
    axes[2].set_xlabel("X / mm")
    axes[2].set_ylabel("N outward from S / mm")
    axes[2].set_xlim(-15, 15)
    axes[2].set_ylim(-12, 20)
    axes[2].set_aspect("equal")
    for axis in axes:
        axis.tick_params(labelsize=9)
    fig.savefig(directory / "native-cavity-supports.png", dpi=180)
    plt.close(fig)
    result = {"schema": 1, "native_archive": ready["native"]["archive"],
              "native_archive_sha256": ready["native"]["archive_sha256"],
              "gcode_sha256": ready["native"]["gcode_sha256"],
              "source_sha256": report["source_sha256"], "analysis_script_sha256": preparation.sha(Path(__file__)),
              "method": "All Support feature centerlines, including unlabeled bodies; up to 2,500 per-part nearest-surface witnesses within 0.85 mm.",
              "parts": contacts, "image": preparation.relative(directory / "native-cavity-supports.png"),
              "scope": "Locates support paths and nearby seats/faces. It does not establish physical release, deposited finish or liquid sealing.",
              "review_status": "ready for geometry/access review"}
    preparation.save(project.with_suffix(".support-faces.json"), result)
    print(json.dumps({"support_faces": preparation.relative(project.with_suffix(".support-faces.json")),
                      "parts": [{"part": row["part"], "face_counts": row["nearby_face_witness_counts"]} for row in contacts]}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jobs", nargs="*", choices=("seals", "supports", "tool", "seals-industrial", "supports-industrial"))
    args = parser.parse_args()
    actions = {"seals": seal_review, "supports": faucet_support_review, "tool": tool_review,
               "seals-industrial": lambda: seal_review(preparation.SEALS / "vent-bungs-industrial-tpu85a.3mf"),
               "supports-industrial": lambda: faucet_support_review(HERE / "industrial/faucet-industrial-petgf.3mf")}
    for name in args.jobs or actions:
        actions[name]()
