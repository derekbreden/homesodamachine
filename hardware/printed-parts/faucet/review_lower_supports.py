"""Locate native support stock around the faucet base's lower cable route.

The section views support a cleanup-access review. They are not a simulation
of support release or a measurement of deposited internal surface finish.
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
import trimesh

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import prepare_vent_prints as preparation
from prepare_display_print import extrusion_segments
from review_vent_prints import draw_polygon, filled_section


def review(project: Path) -> dict:
    report = json.loads(project.with_suffix(".print.json").read_text())
    ready = json.loads(project.with_suffix(".readiness.json").read_text())
    preparation.verify_sources(report)
    assert preparation.sha(project) == ready["project_sha256"]
    assert preparation.sha(project.with_suffix(".print.json")) == ready["print_report_sha256"]
    rows = [row for row in report["parts"] if row["name"].endswith("shell-base")]
    if len(rows) != 1:
        raise ValueError("Expected exactly one rigid shell base")
    row = rows[0]
    native = ready["native"]
    archive = preparation.ROOT / native["archive"]
    assert preparation.sha(archive) == native["archive_sha256"]
    directory = archive.parent
    gcode = directory / "plate_1.gcode"
    assert preparation.sha(gcode) == native["gcode_sha256"]
    rotation = np.array(row["build_transform"][:9]).reshape(3, 3).T
    samples = []
    all_support_count = 0
    lower_ceiling = 46.0
    for segment in extrusion_segments(gcode):
        if segment["object"] != row["identify_id"] or not segment["feature"].startswith("Support"):
            continue
        all_support_count += 1
        midpoint = (np.array(segment["a"]) + segment["b"]) / 2
        source = (midpoint - row["plate_translation_mm"]) @ rotation + row["source_center_mm"]
        if source[2] <= lower_ceiling:
            samples.append(source)
    points = np.array(samples).reshape((-1, 3))
    mesh = trimesh.load(preparation.ROOT / row["source"], force="mesh", process=True)
    lower_vertices = mesh.vertices[mesh.vertices[:, 2] <= lower_ceiling]
    vertices = lower_vertices[np.unique(np.linspace(
        0, len(lower_vertices) - 1, min(20000, len(lower_vertices)), dtype=int))]
    indices = np.unique(np.linspace(0, len(points) - 1, min(20000, len(points)), dtype=int)) if len(points) else []
    selected = points[indices] if len(points) else points
    fig, axes = plt.subplots(1, 3, figsize=(13.5, 5.0), constrained_layout=True)
    for axis, dimensions, title in zip(axes, ((0, 2), (1, 2), (0, 1)),
                                       ("Lower base, X/Z", "Lower base, Y/Z", "Mounting region, X/Y")):
        axis.scatter(vertices[:, dimensions[0]], vertices[:, dimensions[1]],
                     s=.13, color="#bcc3cb", alpha=.6, rasterized=True)
        cloud = selected[selected[:, 2] <= 14] if dimensions == (0, 1) else selected
        if len(cloud):
            axis.scatter(cloud[:, dimensions[0]], cloud[:, dimensions[1]],
                         s=.3, color="#278c99", alpha=.6, rasterized=True)
        axis.set_title(title, fontsize=11)
        axis.set_xlabel("XYZ"[dimensions[0]] + " / mm")
        axis.set_ylabel("XYZ"[dimensions[1]] + " / mm")
        axis.set_aspect("equal")
    fig.suptitle("Source mesh (grey) and native support centers (blue)", fontsize=12)
    projection_path = directory / "native-lower-supports.png"
    fig.savefig(projection_path, dpi=180)
    plt.close(fig)

    levels = (.2, 3.4, 12.0, 18.0, 26.0, 38.0)
    tolerance = .6
    sections = []
    fig, axes = plt.subplots(2, 3, figsize=(12.8, 8.7), constrained_layout=True)
    for axis, z in zip(axes.flat, levels):
        stock = filled_section(mesh, z)
        near = points[np.abs(points[:, 2] - z) <= tolerance] if len(points) else points
        draw_polygon(axis, stock, facecolor="#dce0e5", edgecolor="#343b43", linewidth=.5)
        if len(near):
            axis.scatter(near[:, 0], near[:, 1], s=1, color="#278c99", alpha=.7, rasterized=True)
        axis.set_title(f"Source section Z{z:.1f} mm · supports within ±{tolerance:.1f} mm", fontsize=10)
        axis.set_xlabel("X / mm", fontsize=9)
        axis.set_ylabel("Y / mm", fontsize=9)
        axis.set_aspect("equal")
        axis.tick_params(labelsize=8)
        representatives = near[np.unique(np.linspace(0, len(near) - 1, min(20, len(near)), dtype=int))] if len(near) else near
        sections.append({"source_z_mm": z, "support_center_z_half_band_mm": tolerance,
                         "support_segment_midpoint_count": len(near),
                         "representative_source_midpoints_mm": representatives.tolist()})
    fig.suptitle("Lower cable route: source sections and nearby native support stock", fontsize=12)
    section_path = directory / "native-lower-support-sections.png"
    fig.savefig(section_path, dpi=180)
    plt.close(fig)
    result = {
        "schema": 1, "part": row["name"], "stl_sha256": row["stl_sha256"],
        "project_sha256": ready["project_sha256"],
        "native_archive": native["archive"], "native_archive_sha256": native["archive_sha256"],
        "gcode_sha256": native["gcode_sha256"], "source_sha256": report["source_sha256"],
        "analysis_script_sha256": preparation.sha(Path(__file__)),
        "section_reader_sha256": preparation.sha(HERE / "review_vent_prints.py"),
        "gcode_reader_sha256": preparation.sha(HERE / "prepare_display_print.py"),
        "all_base_support_segment_midpoints": all_support_count,
        "lower_region_source_z_ceiling_mm": lower_ceiling,
        "lower_support_segment_midpoints": len(points),
        "lower_support_source_bounds_mm": [points.min(axis=0).tolist(), points.max(axis=0).tolist()] if len(points) else None,
        "sections": sections,
        "images": [preparation.relative(projection_path), preparation.relative(section_path)],
        "method": "Every native Support feature, including bodies lacking interface labels, is transformed to the source frame. Lower support midpoints are located in orthogonal projections and six source STL sections. Section overlays use a stated Z band and are location views, not exact bead cross sections.",
        "review_status": "prepared for manual geometry and cleanup-access review",
        "scope": "Locates support stock around the lower cable route, mount sockets and donor/lever openings. It does not prove support release, required cleanup force or final guide finish.",
    }
    preparation.verify_sources(report)
    assert preparation.sha(gcode) == native["gcode_sha256"]
    output = project.with_suffix(".lower-supports.json")
    preparation.save(output, result)
    print(json.dumps({"lower_support_review": preparation.relative(output),
                      "lower_support_segment_midpoints": len(points)}, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("styles", nargs="*", choices=("sculpted", "industrial"))
    args = parser.parse_args()
    for style in args.styles or ("sculpted", "industrial"):
        project = HERE / "industrial/faucet-industrial-petgf.3mf" if style == "industrial" else HERE / "faucet-petgf.3mf"
        review(project)
