"""Verify the current reservoir's native slice, nozzle, trim and full bead inset.

Run with tools/cad-venv/bin/python after slicing both plates into
.cache/reservoir-no-ironing/slice and auditing their supports there.
"""

from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import zipfile

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
FOLDER = ROOT / ".cache/reservoir-no-ironing/slice"
WORDS = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")


def sha(data):
    return hashlib.sha256(data).hexdigest()


def arc_geometry(start, end, words, clockwise):
    """Exact length and XY cardinal extrema for a native I/J arc."""
    if "R" in words or not ("I" in words or "J" in words):
        raise ValueError("Unsupported native arc encoding")
    center = np.array(start) + [words.get("I", 0), words.get("J", 0)]
    radius = np.linalg.norm(np.array(start) - center)
    first = np.arctan2(start[1] - center[1], start[0] - center[0])
    last = np.arctan2(end[1] - center[1], end[0] - center[0])
    sweep = ((first - last) if clockwise else (last - first)) % (2 * np.pi)
    if np.linalg.norm(np.array(end) - start) < 1e-7:
        sweep = 2 * np.pi
    points = [start, end]
    for angle in (0, np.pi / 2, np.pi, 3 * np.pi / 2):
        offset = ((first - angle) if clockwise else (angle - first)) % (2 * np.pi)
        if offset <= sweep + 1e-8:
            points.append(center + radius * np.array([np.cos(angle), np.sin(angle)]))
    return float(radius * sweep), np.array(points)


def toolpaths(text, expected_ids, bed, minimum_margin):
    if re.search(r"^; FEATURE: Ironing\s*$", text, re.MULTILINE):
        raise ValueError("Native slice contains an ironing feature")
    x = y = e = width = fan = 0.0
    z, obj = None, None
    absolute, relative_e = True, True
    feature = ""
    deposited_moves = support_moves = 0
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    boxes = {i: [np.full(2, np.inf), np.full(2, -np.inf)] for i in expected_ids}
    cooling = Counter()
    for raw in text.splitlines():
        match = re.match(r"; start printing object, unique label id: (\d+)", raw)
        if match:
            obj = int(match[1])
            if obj not in boxes:
                raise ValueError(f"Unexpected native object: {obj}")
        if raw.startswith("; stop printing object"):
            obj = None
        if raw.startswith("; Z_HEIGHT:"):
            z = float(raw.split(":", 1)[1])
        if raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
        if raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {k: float(v) for k, v in WORDS.findall(code)}
        if command == "M1031" and words.get("S") == 1:
            raise ValueError("Native slice enables ironing")
        if command == "M106" and words.get("P", 1) == 1:
            fan = words.get("S", 255)
        if command in ("G90", "G91"):
            absolute = command == "G90"
        if command in ("M82", "M83"):
            relative_e = command == "M83"
        if command == "G92":
            x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
        if command not in ("G0", "G1", "G2", "G3"):
            continue
        nx = words.get("X", x) if absolute else x + words.get("X", 0)
        ny = words.get("Y", y) if absolute else y + words.get("Y", 0)
        ne = words.get("E", 0 if relative_e else e)
        extrusion = ne if relative_e else ne - e
        start, end = np.array([x, y]), np.array([nx, ny])
        length, extrema = (arc_geometry(start, end, words, command == "G2")
                           if command in ("G2", "G3") else
                           (float(np.linalg.norm(end - start)), np.array([start, end])))
        if z is not None and feature and feature != "Custom" and extrusion > 0 and length > 0.001:
            if width <= 0:
                raise ValueError("Deposited path has no native bead width")
            a, b = extrema.min(axis=0) - width / 2, extrema.max(axis=0) + width / 2
            low, high = np.minimum(low, a), np.maximum(high, b)
            deposited_moves += 1
            support_moves += int(feature.startswith("Support"))
            if obj is not None:
                box = boxes[obj]
                box[0], box[1] = np.minimum(box[0], a), np.maximum(box[1], b)
            if feature in ("Outer wall", "Inner wall") and z > 12:
                cooling[fan] += 1
        x, y, e = nx, ny, (e + ne if relative_e else ne)
    margins = np.concatenate((low - bed[0], bed[1] - high))
    if not deposited_moves or min(margins) < minimum_margin:
        raise ValueError(f"Native full beads exceed the required inset: {margins}")
    if not all(np.isfinite(box).all() for box in boxes.values()):
        raise ValueError("A body or cap has no deposited paths")
    first, second = map(np.array, boxes.values())
    gap = float(np.linalg.norm(np.maximum(np.maximum(first[0] - second[1], second[0] - first[1]), 0)))
    if gap < 5 or 51.0 not in cooling:
        raise ValueError("Body/cap separation or ordinary wall cooling differs")
    return {
        "left_nozzle_usable_bed_bounds_mm": bed.tolist(),
        "model_support_brim_xy_bounds_mm": [low.tolist(), high.tolist()],
        "edge_margins_left_front_right_back_mm": margins.tolist(),
        "minimum_full_bead_edge_margin_mm": float(min(margins)),
        "minimum_body_cap_full_bead_box_gap_mm": gap,
        "deposited_move_count": deposited_moves,
        "support_move_count": support_moves,
        "scope": "Native deposited model, support and brim beads, including arc extrema and half-width. Vendor startup purge/calibration paths are excluded. Placement does not establish adhesion.",
    }, sorted(cooling)


def main():
    project = HERE / "reservoir.3mf"
    generated = json.loads((HERE / "reservoir.print.json").read_text())
    if sha(project.read_bytes()) != generated["project_sha256"]:
        raise ValueError("Project differs from the geometry verification")
    source = json.loads((HERE / "print-settings.json").read_text())["project_settings"]
    result = json.loads((FOLDER / "result.json").read_text())
    if result["return_code"] != 0 or [p["id"] for p in result["sliced_plates"]] != [1, 2]:
        raise ValueError("Native slicing did not complete on both plates")
    if source["ironing_type"] != "no ironing" or source["enable_support_ironing"] != "0":
        raise ValueError("Current model and support ironing must be off")
    area = np.array([[float(v) for v in point.split("x")]
                     for point in source["extruder_printable_area"][0].split(",")])
    bed = np.array([area.min(axis=0), area.max(axis=0)])
    review = dict(project="reservoir.3mf", project_sha256=sha(project.read_bytes()),
                  recipe="print-settings.json", slicer_version="02.08.02.61", return_code=0,
                  physical_settings_match_saved_project=True, plates=[],
                  scope="Native slice of current body/cap geometry with ironing off. Coupon finish selection and the historical water-hold acceptance apply to their tested articles; this slice supplies no new physical sealing result.")
    with zipfile.ZipFile(FOLDER / "reservoir-review.3mf") as archive:
        sliced = json.loads(archive.read("Metadata/project_settings.config"))
        added = {k: v for k, v in sliced.items() if k not in source}
        if added not in ({}, {"filament_map_2": ["1"]}) or any(sliced.get(k) != v for k, v in source.items()):
            raise ValueError("Native slicer changed the saved process")
        review["slicer_added_metadata"] = added
        for row in result["sliced_plates"]:
            i = row["id"]
            parts = [p for p in generated["parts"] if p["plate"] == i]
            if row["warning_message"] or [v["name"] for v in row["objects"]] != [p["name"] for p in parts]:
                raise ValueError("Unexpected native plate warning or object composition")
            name = f"Metadata/plate_{i}.gcode"
            data = archive.read(name)
            if hashlib.md5(data).hexdigest() != archive.read(name + ".md5").decode().strip().lower():
                raise ValueError("Embedded G-code checksum failed")
            text = data.decode()
            assignment = {}
            for key, expected in (("filament_map", "1"), ("filament_nozzle_map", "0"), ("nozzle_diameter", "0.8,0.8")):
                match = re.search(r"^; " + key + r" = (.+)$", text, re.MULTILINE)
                if not match or match[1].strip() != expected:
                    raise ValueError(f"Native {key} differs from the left 0.8 mm assignment")
                assignment[key] = match[1].strip()
            trims = re.findall(r"^\s*(G29\.1 Z[^\r\n]*)", text, re.MULTILINE)
            if trims != ["G29.1 Z0 ; clear z-trim value first", "G29.1 Z0.02"]:
                raise ValueError(f"Native Mark2 Z trim differs: {trims}")
            layers = re.findall(r"^; CHANGE_LAYER\n; Z_HEIGHT: ([0-9.]+)\n; LAYER_HEIGHT: ([0-9.]+)", text, re.MULTILINE)
            if len(layers) != 740 or float(layers[0][1]) != 0.30 or any(abs(float(v[1]) - 0.24) > 2e-5 for v in layers[1:]):
                raise ValueError("Native layer count or heights differ")
            if row["feature_type_times"].get("Ironing", 0) != 0:
                raise ValueError("Native estimate includes ironing")
            placement, cooling = toolpaths(text, [2400 + 2 * i - 1, 2400 + 2 * i], bed,
                                           generated["minimum_emitted_bead_edge_margin_mm"])
            support = json.loads((FOLDER / f"plate_{i}-supports.json").read_text())["summary"]
            if support["bed_rooted_bodies"] != support["support_bodies"] or support["model_rooted_bodies"]:
                raise ValueError("Native supports require roots on the model")
            review["plates"].append(dict(
                plate=i, parts=[p["name"] for p in parts],
                estimated_seconds=round(row["total_predication"], 3),
                estimated_mass_g=round(sum(v["total_used_g"] for v in row["filaments"]), 3),
                ironing_estimated_seconds=0, ironing_enable_commands=0, ironing_feature_paths=0,
                layer_count=len(layers), first_layer_height_mm=0.30, normal_layer_height_mm=0.24,
                warning_message=row["warning_message"], gcode_sha256=sha(data), embedded_gcode_md5_verified=True,
                emitted_nozzle_assignment=assignment, z_trim_commands=trims, placement=placement,
                wall_cooling_above_cap_pwm_values=cooling, support_summary=support,
                support_scope="All detected support bodies start at the bed. Bodies without explicit interface labels have no inferred contact build-up."))
    (HERE / "slice-review.json").write_text(json.dumps(review, indent=2) + "\n")
    print(json.dumps({"project_sha256": review["project_sha256"], "plates": review["plates"]}, indent=2))


if __name__ == "__main__":
    main()
