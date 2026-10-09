"""Check emitted dense material through every layer of the faucet insert hosts.

Actual native model beads are compared with mid-slab STL sections, clipped to
the source-frame host/root regions. The radial check begins at the installed
brass envelope, rather than at the smaller printed pilot. These nominal bead
envelopes do not establish measured density, strength or insert retention.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from shapely.geometry import LineString, MultiPoint, Point, Polygon
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_vent_prints as preparation
from prepare_display_print import extrusion_segments
from review_vent_prints import components, draw_polygon, filled_section


def box_section(corners, height):
    points = []
    # Caller provides the binary-order source box transformed into print space.
    for index, first in enumerate(corners):
        for bit in (1, 2, 4):
            other = index ^ bit
            if other <= index:
                continue
            second = corners[other]
            low, high = sorted((first[2], second[2]))
            if not low - 1e-7 <= height <= high + 1e-7:
                continue
            if abs(second[2] - first[2]) < 1e-7:
                points.extend([first[:2], second[:2]])
            else:
                points.append((first + (height - first[2]) / (second[2] - first[2]) * (second - first))[:2])
    return MultiPoint(points).convex_hull


def review(project: Path) -> dict:
    report = json.loads(project.with_suffix(".print.json").read_text())
    ready = json.loads(project.with_suffix(".readiness.json").read_text())
    preparation.verify_sources(report)
    row = next(row for row in report["parts"] if row["name"].endswith("shell-base"))
    regions = report.get("insert_review_regions", report["local_solid_regions"])
    directory = (preparation.ROOT / ready["native"]["archive"]).parent
    gcode = directory / "plate_1.gcode"
    if preparation.sha(gcode) != ready["native"]["gcode_sha256"]:
        raise ValueError("Insert review must read the validated native G-code")
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3)
    center = np.array(row["source_center_mm"])
    translation = np.array(row["plate_translation_mm"])

    def placed(points):
        return (np.array(points) - center) @ rotation + translation

    mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
    mesh.vertices = placed(mesh.vertices)
    triangles = mesh.triangles
    z_min, z_max = triangles[:, :, 2].min(axis=1), triangles[:, :, 2].max(axis=1)
    staged = []
    for index, region in enumerate(regions):
        bounds = np.array(region["applied_source_bounds_mm"])
        source_corners = np.array([[x, y, z] for x in bounds[:, 0]
                                   for y in bounds[:, 1] for z in bounds[:, 2]])
        corners = placed(source_corners)
        staged.append({"name": region["name"], "source_bounds_mm": bounds.tolist(),
                       "corners": corners, "print_low": corners[:, 2].min(),
                       "print_high": corners[:, 2].max(),
                       "axis_xy": np.array(preparation.writer.shell.base_pod_centers[index]),
                       "readings": []})
    low = min(region["print_low"] for region in staged)
    high = max(region["print_high"] for region in staged)
    roads, slabs = {}, {}
    for segment in extrusion_segments(gcode):
        if segment["layer"] > high + 1:
            break
        if (segment["object"] != row["identify_id"] or segment["feature"].startswith("Support")
                or not low <= segment["a"][2] <= high + 1):
            continue
        z = round(segment["a"][2], 4)
        slabs[z] = segment["height"]
        roads.setdefault(z, []).append(LineString([segment["a"][:2], segment["b"][:2]])
                                      .buffer(segment["width"] / 2, cap_style=1, join_style=1))
    worst = {}
    shell = preparation.writer.shell
    brass_radius = shell.base_insert_outer_dia / 2
    body_low = shell.base_insert_bottom_z
    body_high = body_low + shell.base_insert_length
    for height in sorted(roads):
        slab = slabs[height]
        section_z = height - slab / 2
        faces = np.flatnonzero((z_min < section_z) & (z_max > section_z))
        stock = filled_section(mesh, section_z, faces)
        beads = unary_union(roads[height])
        # Keep each connected model component's actual outer contour, while
        # retaining the exact STL's intentional voids. Enclosed inter-road
        # pores remain quantified by coverage and the raw radial-ray result;
        # they do not move the supporting wall's external boundary.
        envelope = unary_union([Polygon(piece.exterior) for piece in components(beads)
                                if piece.geom_type == "Polygon"]).intersection(stock)
        for index, region in enumerate(staged):
            if not region["print_low"] + slab / 2 <= section_z <= region["print_high"] - slab / 2:
                continue
            target = stock.intersection(box_section(region["corners"], section_z))
            if target.area < .1:
                continue
            fraction = target.intersection(beads).area / target.area
            x, y = region["axis_xy"]
            # Solve the tilted native plane at the original vertical insert axis.
            axis_z = ((section_z - translation[2] - (x-center[0])*rotation[0, 2]
                       - (y-center[1])*rotation[1, 2]) / rotation[2, 2] + center[2])
            backing = []
            if body_low <= axis_z <= body_high:
                for theta in np.linspace(0, 2*np.pi, 360, endpoint=False):
                    direction = np.array([np.cos(theta), np.sin(theta)])
                    dz = -np.dot(direction, rotation[:2, 2]) / rotation[2, 2]
                    radial = np.array([direction[0], direction[1], dz])
                    a = np.array([x, y, axis_z]) + brass_radius * radial
                    b = np.array([x, y, axis_z]) + (brass_radius + 2.1) * radial
                    if min(a[2], b[2]) < body_low or max(a[2], b[2]) > body_high:
                        continue
                    ray = LineString(placed([a, b])[:, :2])
                    scale = np.linalg.norm(radial @ rotation[:, :2])
                    source_lines = [piece for piece in components(ray.intersection(stock))
                                    if piece.geom_type == "LineString"]
                    printed_lines = [piece for piece in components(ray.intersection(beads))
                                     if piece.geom_type == "LineString"]
                    envelope_lines = [piece for piece in components(ray.intersection(envelope))
                                      if piece.geom_type == "LineString"]
                    connected = next((piece for piece in printed_lines
                                      if piece.distance(Point(ray.coords[0])) < .05), None)
                    printed_mm = connected.length / scale if connected is not None else 0
                    outer = next((piece for piece in envelope_lines
                                  if piece.distance(Point(ray.coords[0])) < .05), None)
                    envelope_mm = outer.length / scale if outer is not None else 0
                    source_mm = sum(piece.length for piece in source_lines) / scale
                    backing.append({"azimuth_degrees": float(np.degrees(theta)),
                                    "source_stock_mm": float(source_mm),
                                    "uninterrupted_ray_bead_interval_mm": float(printed_mm),
                                    "connected_component_outer_backing_mm": float(envelope_mm)})
            minimum = min((item["connected_component_outer_backing_mm"] for item in backing), default=None)
            dense_required = shell.base_pod_z_bottom <= axis_z <= shell.base_pod_z_top
            reading = {"native_layer_top_z_mm": height, "native_layer_height_mm": slab,
                       "native_section_z_mm": section_z,
                       "source_stock_area_mm2": float(target.area),
                       "own_width_bead_coverage_fraction": float(fraction),
                       "unfilled_stock_area_mm2": float(target.difference(beads).area),
                       "dense_coverage_required_in_host_body_and_cap": bool(dense_required),
                       "axis_source_z_mm": float(axis_z), "radial_samples": len(backing),
                       "minimum_connected_component_outer_backing_mm": minimum,
                       "minimum_uninterrupted_ray_bead_interval_mm": min((item["uninterrupted_ray_bead_interval_mm"] for item in backing), default=None),
                       "worst_radial_outer_backing": min(backing, key=lambda item: item["connected_component_outer_backing_mm"]) if backing else None,
                       "worst_radial_ray_interval": min(backing, key=lambda item: item["uninterrupted_ray_bead_interval_mm"]) if backing else None,
                       "pass": (not dense_required or fraction >= .98) and (minimum is None or minimum >= 2)}
            region["readings"].append(reading)
            if dense_required and (index not in worst or fraction < worst[index][0]):
                worst[index] = (fraction, height, target, beads)
        print(f"Insert stock Z{height:.2f}", flush=True)
    fig, axes = plt.subplots(1, len(staged), figsize=(12, 4.4), constrained_layout=True)
    for index, (region, axis) in enumerate(zip(staged, np.atleast_1d(axes))):
        fraction, height, target, beads = worst[index]
        draw_polygon(axis, target, facecolor="#dce0e5", edgecolor="#343b43", linewidth=.5)
        draw_polygon(axis, target.intersection(beads), facecolor="#2f8196", edgecolor="none", alpha=.8)
        draw_polygon(axis, target.difference(beads), facecolor="#ca423e", edgecolor="none")
        axis.set_aspect("equal")
        axis.set_title(f"Host {index+1} · Z{height:.2f} · {fraction:.1%}")
        axis.set_xlabel("native X / mm")
        axis.set_ylabel("native Y / mm")
    image = directory / "insert-host-commanded-beads.png"
    fig.savefig(image, dpi=180)
    plt.close(fig)
    records = [{"name": region["name"], "source_bounds_mm": region["source_bounds_mm"],
                "native_layers_reviewed": len(region["readings"]),
                "minimum_coverage_fraction": min(item["own_width_bead_coverage_fraction"] for item in region["readings"]),
                "minimum_host_body_and_cap_coverage_fraction": min(item["own_width_bead_coverage_fraction"] for item in region["readings"] if item["dense_coverage_required_in_host_body_and_cap"]),
                "minimum_connected_component_outer_backing_mm": min((item["minimum_connected_component_outer_backing_mm"] for item in region["readings"] if item["minimum_connected_component_outer_backing_mm"] is not None), default=None),
                "minimum_uninterrupted_ray_bead_interval_mm": min((item["minimum_uninterrupted_ray_bead_interval_mm"] for item in region["readings"] if item["minimum_uninterrupted_ray_bead_interval_mm"] is not None), default=None),
                "readings": region["readings"], "pass": bool(region["readings"]) and all(item["pass"] for item in region["readings"])}
               for region in staged]
    result = {"schema": 1, "native_archive_sha256": ready["native"]["archive_sha256"],
              "gcode_sha256": ready["native"]["gcode_sha256"], "source_stl_sha256": row["stl_sha256"],
              "print_report_sha256": preparation.sha(project.with_suffix(".print.json")),
              "analysis_script_sha256": preparation.sha(Path(__file__)),
              "gcode_reader_sha256": preparation.sha(HERE / "prepare_display_print.py"),
              "method": "Every complete native slab intersecting the source host/root boxes uses its mid-height exact STL section and emitted bead widths. Dense98% coverage is required where the insert axis falls inside the CAD host body/cap interval; all other edge-slab coverage remains recorded. Installed brass OD4.6 is sampled at1 degree radial intervals within its4 mm body. A connected model component's actual outer envelope, clipped by intentional STL voids, must start within0.05 mm of the brass and extend2 mm in CAD XY radius. Enclosed inter-road pores remain measured by coverage, missing area and uninterrupted-ray intervals; they are not treated as external wall boundaries.",
              "diagnostic_dense_coverage_threshold": .98, "minimum_backing_mm": 2,
              "parts": records, "pass": all(region["pass"] for region in records),
              "scope": "Commanded deposition and nominal radial backing. Deposited density, bonds, insert retention, load capacity and lifetime are unmeasured.",
              "image": preparation.relative(image)}
    preparation.save(project.with_suffix(".insert-beads.json"), result)
    print(json.dumps({"pass": result["pass"], "parts": [{key: region[key] for key in ("name", "native_layers_reviewed", "minimum_coverage_fraction", "minimum_host_body_and_cap_coverage_fraction", "minimum_connected_component_outer_backing_mm", "pass")} for region in records]}, indent=2))
    if not result["pass"]:
        raise SystemExit("Faucet insert deposition review failed")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("styles", nargs="*", choices=("sculpted", "industrial"))
    args = parser.parse_args()
    for style in args.styles or ("sculpted", "industrial"):
        review(HERE / ("faucet-petgf.3mf" if style == "sculpted" else "industrial/faucet-industrial-petgf.3mf"))
