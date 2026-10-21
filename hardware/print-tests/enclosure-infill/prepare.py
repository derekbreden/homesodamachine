#!/usr/bin/env python3
"""Prepare the manual four-way gyroid comparison for Mark2; never sends a print.

    tools/cad-venv/bin/python hardware/print-tests/enclosure-infill/prepare.py --slice
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

import numpy as np
from shapely.geometry import Polygon
from shapely.ops import triangulate
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/trial-preparation"))
import _native

PROFILE = ROOT / "hardware/printed-parts/petgf.3mf"
CASES = ((1, 2, 15), (2, 4, 15), (3, 2, 25), (4, 4, 25))
STEM = "2026-10-21-enclosure-gyroid-comparison-left04-z004-mark2-v1"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def strip(thickness, notches, standing):
    """150 x 25 mm test strip; identification occupies only the first millimetre.

    The central 120 mm and both support positions are identical in every case.
    The end's one to four shallow V notches survive brim removal without text.
    """
    outline = [(0., 0.), (150., 0.), (150., 25.), (0., 25.)]
    for y in reversed([4. + 5. * i for i in range(notches)]):
        outline += [(0., y + 1.5), (1., y), (0., y - 1.5)]
    poly = Polygon(outline)
    triangles = [p for p in triangulate(poly) if poly.covers(p)]
    if abs(sum(p.area for p in triangles) - poly.area) > 1e-8:
        raise ValueError("The strip's triangulation does not cover its outline")
    points = list(poly.exterior.coords)[:-1]
    index = {p: i for i, p in enumerate(points)}
    count = len(points)
    faces = []
    for triangle in triangles:
        xyz = list(triangle.exterior.coords)[:3]
        if not triangle.exterior.is_ccw:
            xyz.reverse()
        a, b, c = [index[p] for p in xyz]
        faces += [(c, b, a), (a + count, b + count, c + count)]
    for a in range(count):
        b = (a + 1) % count
        faces += [(a, b, b + count), (a, b + count, a + count)]
    vertices = np.array([(x, y, z) for z in (0., thickness) for x, y in points])
    if standing:
        vertices = vertices[:, [0, 2, 1]]
        # Swapping axes reverses handedness.
        faces = [(a, c, b) for a, b, c in faces]
    mesh = trimesh.Trimesh(vertices=vertices, faces=faces, process=True)
    if not (mesh.is_watertight and mesh.is_winding_consistent
            and mesh.body_count == 1 and mesh.volume > 0):
        raise ValueError("The strip must be one closed, oriented volume")
    return mesh


def prepare(output, slice_now):
    output = output.resolve()
    if output.exists():
        raise FileExistsError("Keep the printed comparison immutable; use a new --output")
    output.mkdir(parents=True)
    (output / "parts").mkdir()
    profile = _native.profile_settings(PROFILE, .04)
    plate = _native.Plate(STEM, profile)
    if (plate.settings["wall_loops"], plate.settings["sparse_infill_density"],
            plate.settings["sparse_infill_pattern"]) != ("2", "15%", "gyroid"):
        raise ValueError("The production baseline must remain two walls and 15% gyroid")
    edits = {"filament_colour": ["#161616"],
             "extruder_ams_count": ["1#0|4#0", "1#0|4#0"],
             "support_filament": "1", "support_interface_filament": "1",
             "flush_into_support": "0"}
    plate.settings.update(edits)
    lo, hi = np.array(profile["usable_low"]), np.array(profile["usable_high"])
    bed_center = (lo + hi) / 2
    rows = []
    cursor = -73.5  # All eight models occupy 150 x 147 mm, centered together.
    for case, walls, density in CASES:
        for kind, thickness, standing in (("wall", 3., True), ("floor", 6., False)):
            name = f"{case}-{kind}-{walls}walls-{density}gyroid"
            mesh = strip(thickness, case, standing)
            path = output / "parts" / f"{name}.stl"
            mesh.export(path)
            # Use the serialized mesh, just as the production preparer does.
            mesh = trimesh.load(path, force="mesh", process=True)
            center = mesh.bounds.mean(axis=0)
            width = float(mesh.extents[1])
            translation = [float(bed_center[0]), float(bed_center[1] + cursor + width / 2),
                           float(mesh.extents[2] / 2)]
            settings = {"wall_loops": str(walls), "sparse_infill_density": f"{density}%",
                        "sparse_infill_pattern": "gyroid"}
            obj = plate.add_object(name, mesh.vertices - center, mesh.faces,
                                   source_file=path.name, source_center=center,
                                   build_rotation=np.eye(3), translation=translation,
                                   settings=settings)
            placed = mesh.vertices - center + translation
            rows.append({"case": case, "kind": kind, "notches": case, "name": name,
                         "object_id": obj["object_id"], "identify_id": obj["identify_id"],
                         "member": obj["member"], "source": str(path.relative_to(ROOT)),
                         "source_sha256": sha(path), "dimensions_print_mm": mesh.extents.tolist(),
                         "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
                         "settings": settings, "watertight": bool(mesh.is_watertight),
                         "body_count": int(mesh.body_count)})
            cursor += width + 5.
    project = output / "input.3mf"
    plate.write(project)
    record = {"purpose": "Manual comparison of perceived stiffness and equal-load deflection; no automatic production-setting change.",
              "printer": "Mark2", "name": STEM, "prepared_utc": datetime.now(timezone.utc).isoformat(),
              "source_profile": str(PROFILE.relative_to(ROOT)), "source_profile_sha256": sha(PROFILE),
              "generator_sha256": sha(__file__), "project": str(project.relative_to(ROOT)),
              "project_sha256": sha(project), "requested_z_trim_mm": .04,
              "emitted_textured_z_trim_mm": .02, "global_setting_edits": edits,
              "profile_changes": profile["changes"], "usable_plate_mm": [lo.tolist(), hi.tolist()],
              "test_span_mm": 120., "support_positions_from_plain_end_mm": [15., 135.],
              "objects": rows, "submitted": False}
    save(output / "preparation.json", record)
    print(str(project.relative_to(ROOT)), flush=True)
    if slice_now:
        native = ROOT / ".cache/prints" / STEM
        native.mkdir(parents=True, exist_ok=False)
        command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0",
                   "--arrange", "0", "--orient", "0", "--outputdir", str(native),
                   "--export-3mf", "native.gcode.3mf", str(project)]
        save(output / "slice-command.json", command)
        with (native / "slice.log").open("w") as log:
            subprocess.run(command, cwd=native, stdout=log, stderr=subprocess.STDOUT, check=True,
                           env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
        result = json.loads((native / "result.json").read_text())
        if result.get("return_code") != 0:
            raise RuntimeError(result.get("error_string"))
        shutil.copy2(native / "native.gcode.3mf", output / "native.gcode.3mf")
        save(output / "slice-result.json", result)
        print("Sliced; review the emitted archive before sending.", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=HERE / "mark2-v1")
    parser.add_argument("--slice", action="store_true")
    args = parser.parse_args()
    prepare(args.output, args.slice)
