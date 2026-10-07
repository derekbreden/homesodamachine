"""Check the flat countertop gaskets in their retained native TPU slices.

Closed contours and nominal bead coverage check the emitted material topology.
They do not measure compression, friction or spill containment after assembly.
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
from shapely.geometry import LineString, Polygon
from shapely.ops import unary_union
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_vent_prints as preparation
from prepare_display_print import extrusion_segments
from review_vent_prints import components, draw_polygon, filled_section


def review(project: Path) -> dict:
    report = json.loads(project.with_suffix(".print.json").read_text())
    ready = json.loads(project.with_suffix(".readiness.json").read_text())
    preparation.verify_sources(report)
    assert preparation.sha(project) == ready["project_sha256"]
    assert preparation.sha(project.with_suffix(".print.json")) == ready["print_report_sha256"]
    rows = [row for row in report["parts"] if row["name"].endswith("counter-gasket")]
    if len(rows) != 1:
        raise ValueError("Expected exactly one countertop gasket")
    row = rows[0]
    native = ready["native"]
    archive_path = preparation.ROOT / native["archive"]
    assert preparation.sha(archive_path) == native["archive_sha256"]
    directory = archive_path.parent
    gcode = directory / "plate_1.gcode"
    if preparation.sha(gcode) != native["gcode_sha256"]:
        raise ValueError("Gasket review requires the validated native G-code")
    with zipfile.ZipFile(project) as archive:
        settings = json.loads(archive.read(preparation.writer.SETTINGS_MEMBER))
    mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
    roads = {}
    for segment in extrusion_segments(gcode):
        if segment["object"] != row["identify_id"]:
            continue
        if segment["feature"].startswith("Support"):
            raise ValueError("The flat countertop gasket must print without supports")
        local = ((np.array([segment["a"], segment["b"]]) - row["plate_translation_mm"])
                 @ rotation + row["source_center_mm"])
        if np.max(np.abs(local[:, 2] - local[0, 2])) > .005:
            raise ValueError("Gasket model roads must be planar in the flat source pose")
        z = round(float(local[0, 2]), 4)
        roads.setdefault(z, []).append(LineString(local[:, :2]).buffer(
            segment["width"] / 2, cap_style=1, join_style=1))
    if not roads:
        raise ValueError("No native gasket model roads")

    readings = []
    previous = float(mesh.bounds[0, 2])
    for index, z in enumerate(sorted(roads)):
        mid = (previous + z) / 2
        previous = z
        source = filled_section(mesh, mid)
        source_parts = [piece for piece in components(source) if piece.geom_type == "Polygon"]
        if len(source_parts) != 1:
            raise ValueError(f"Source gasket must be one connected pad at Z{mid:g}")
        source_pad = source_parts[0]
        holes = [Polygon(ring) for ring in source_pad.interiors]
        commanded = unary_union(roads[z])
        foot = float(settings["elefant_foot_compensation"]) if index == 0 else 0.0
        # The source perimeter is intentionally reduced on the compensated
        # first layer. A small edge inset removes normal section/road rounding
        # from the broad dense-stock comparison; the full contours stay checked.
        core = source.buffer(-max(.08, foot + .02))
        material = commanded.intersection(source)
        pieces = [piece for piece in components(material) if piece.geom_type == "Polygon"]
        largest = max(pieces, key=lambda piece: piece.area)
        missing = core.difference(commanded)
        voids = [Polygon(ring) for piece in components(commanded)
                 if piece.geom_type == "Polygon" for ring in piece.interiors]
        # Representative points remain inside asymmetric pill/branch openings.
        bore_voids = [[void for void in voids if void.covers(hole.representative_point())]
                      for hole in holes]
        closed = (all(len(matches) == 1 for matches in bore_voids)
                  and len({matches[0].wkb for matches in bore_voids if len(matches) == 1}) == len(holes))
        pores = [void.intersection(source) for void in voids
                 if not any(void.covers(hole.representative_point()) for hole in holes)]
        coverage = 100 * core.intersection(commanded).area / core.area
        connected_coverage = 100 * core.intersection(largest).area / core.area
        reading = {
            "layer_top_source_z_mm": z, "source_section_z_mm": mid,
            "first_layer_elephant_foot_compensation_mm": foot,
            "source_core_area_mm2": float(core.area),
            "commanded_core_coverage_percent": float(coverage),
            "largest_connected_material_core_coverage_percent": float(connected_coverage),
            "commanded_missing_core_area_mm2": float(missing.area),
            "source_functional_opening_count": len(holes),
            "functional_openings_closed_and_separate": closed,
            "material_component_count": len(pieces),
            "material_outside_largest_component_mm2": float(sum(piece.area for piece in pieces) - largest.area),
            "enclosed_interroad_pore_area_mm2": float(sum(pore.area for pore in pores)),
            "largest_enclosed_interroad_pore_area_mm2": float(max((pore.area for pore in pores), default=0)),
        }
        reading["pass"] = closed and connected_coverage >= 98.0
        readings.append(reading)

    worst = min(readings, key=lambda value: value["largest_connected_material_core_coverage_percent"])
    z = worst["layer_top_source_z_mm"]
    source = filled_section(mesh, worst["source_section_z_mm"])
    commanded = unary_union(roads[z])
    core = source.buffer(-max(.08, worst["first_layer_elephant_foot_compensation_mm"] + .02))
    fig, axis = plt.subplots(figsize=(7.4, 7.0), constrained_layout=True)
    draw_polygon(axis, source, facecolor="#dce0e5", edgecolor="#343b43", linewidth=.6)
    draw_polygon(axis, commanded.intersection(source), facecolor="#2f8196", edgecolor="none", alpha=.7)
    draw_polygon(axis, core.difference(commanded), facecolor="#ca423e", edgecolor="none")
    axis.set_aspect("equal")
    axis.set_xlabel("Source X / mm")
    axis.set_ylabel("Source Y / mm")
    axis.set_title(f"{row['name']} · layer source Z{z:.2f} mm\n"
                   f"Connected core coverage {worst['largest_connected_material_core_coverage_percent']:.3f}%", fontsize=11)
    image = directory / "gasket-commanded-beads.png"
    fig.savefig(image, dpi=180)
    plt.close(fig)
    result = {
        "schema": 1, "part": row["name"], "stl_sha256": row["stl_sha256"],
        "project_sha256": ready["project_sha256"],
        "native_archive": native["archive"], "native_archive_sha256": native["archive_sha256"],
        "gcode_sha256": native["gcode_sha256"], "source_sha256": report["source_sha256"],
        "analysis_script_sha256": preparation.sha(Path(__file__)),
        "section_reader_sha256": preparation.sha(HERE / "review_vent_prints.py"),
        "gcode_reader_sha256": preparation.sha(HERE / "prepare_display_print.py"),
        "all_native_gasket_model_layers_reviewed": len(readings),
        "minimum_connected_core_coverage_required_percent": 98.0,
        "readings": readings, "pass": all(reading["pass"] for reading in readings),
        "method": "Every flat native model layer is compared at emitted bead widths with its mid-slab source STL section. All source functional openings require separate enclosed native contours, and one connected material component must cover at least 98% of the compensated broad source core. Other material islands, enclosed pores and missing area remain recorded.",
        "scope": "Native commanded material topology and dense-stock presence. Compression, deposited pores, friction and assembled spill containment are unmeasured.",
        "image": preparation.relative(image),
    }
    output = project.with_suffix(".gasket-beads.json")
    preparation.verify_sources(report)
    assert preparation.sha(gcode) == native["gcode_sha256"]
    assert preparation.sha(archive_path) == native["archive_sha256"]
    preparation.save(output, result)
    print(json.dumps({"gasket_review": preparation.relative(output), "pass": result["pass"],
                      "native_layers": len(readings), "minimum_connected_core_coverage_percent":
                      worst["largest_connected_material_core_coverage_percent"]}, indent=2))
    if not result["pass"]:
        raise SystemExit("Gasket native bead review failed")
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("styles", nargs="*", choices=("sculpted", "industrial"))
    args = parser.parse_args()
    for style in args.styles or ("sculpted", "industrial"):
        stem = "vent-bungs-industrial-tpu85a" if style == "industrial" else "vent-bungs-tpu85a"
        review(preparation.SEALS / (stem + ".3mf"))
