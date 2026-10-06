"""Verify native square-calibration toolpaths and draw the plate layout."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-ironing-squares"
WORDS = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
sha = lambda data: hashlib.sha256(data).hexdigest()


def arc_geometry(start, end, words, clockwise):
    """Exact length and XY cardinal extrema for a native I/J arc."""
    if "R" in words or not ("I" in words or "J" in words):
        raise ValueError("Unsupported arc encoding in the native slice")
    center = np.array(start)+[words.get("I", 0), words.get("J", 0)]
    radius = np.linalg.norm(np.array(start)-center)
    first = np.arctan2(start[1]-center[1], start[0]-center[0])
    last = np.arctan2(end[1]-center[1], end[0]-center[0])
    sweep = ((first-last) if clockwise else (last-first)) % (2*np.pi)
    if np.linalg.norm(np.array(end)-start) < 1e-7:
        sweep = 2*np.pi
    points = [start, end]
    for angle in (0, np.pi/2, np.pi, 3*np.pi/2):
        offset = ((first-angle) if clockwise else (angle-first)) % (2*np.pi)
        if offset <= sweep+1e-8:
            points.append(center+radius*np.array([np.cos(angle), np.sin(angle)]))
    return float(radius*sweep), np.array(points)


def main():
    study = json.loads((HERE / "study.json").read_text())
    source = HERE / study["project"]
    if sha(source.read_bytes()) != study["project_sha256"]:
        raise ValueError("Project differs from the generated calibration")
    directory = CACHE / "slice"
    result = json.loads((directory / "result.json").read_text())
    if result["return_code"] != 0 or len(result["sliced_plates"]) != 1:
        raise ValueError("Native slicing did not complete on one plate")
    plate = result["sliced_plates"][0]
    if plate["warning_message"] or len(plate["objects"]) != 10:
        raise ValueError("Unexpected native plate warning/object count")
    with zipfile.ZipFile(source) as archive:
        original = json.loads(archive.read("Metadata/project_settings.config"))
    with zipfile.ZipFile(directory / "ironing-squares-review.3mf") as archive:
        sliced = json.loads(archive.read("Metadata/project_settings.config"))
        added = {k: v for k, v in sliced.items() if k not in original}
        if added not in ({}, {"filament_map_2": ["1"]}) or any(sliced.get(k) != v for k, v in original.items()):
            raise ValueError("Native slicer changed the saved process")
        data = archive.read("Metadata/plate_1.gcode")
        if hashlib.md5(data).hexdigest() != archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Embedded G-code checksum")
        (directory / "plate_1.gcode").write_bytes(data)
        (directory / "plate_1.png").write_bytes(archive.read("Metadata/plate_1.png"))
    text = data.decode()
    layers_match = re.search(r"^; total layer number: (\d+)$", text, re.MULTILINE)
    total_layers = int(layers_match[1]) if layers_match else None
    if total_layers != 6:
        raise ValueError(f"Unexpected native layer count: {total_layers}")
    assignment = {}
    for key, expected in (("filament_map", "1"), ("filament_nozzle_map", "0"), ("nozzle_diameter", "0.8,0.8")):
        match = re.search(r"^; "+key+r" = (.+)$", text, re.MULTILINE)
        actual = match[1].strip() if match else None
        if actual != expected:
            raise ValueError(f"Native {key} is {actual!r}; expected {expected!r}")
        assignment[key] = actual
    trims = [line.strip() for line in text.splitlines() if line.strip().startswith("G29.1 Z")]
    if trims != ["G29.1 Z0 ; clear z-trim value first", "G29.1 Z0.02"]:
        raise ValueError(f"Native Mark2 Z trim differs: {trims}")
    by_id = {p["identify_id"]: p for p in study["parts"]}
    records = {p["label"]: dict(label=p["label"], ironing_extrusion_moves=0,
                                ironing_length_mm=0.0, deposited_filament_mm=0.0,
                                speed_mm_s=set(), heights_mm=set(), outside_square_moves=0)
               for p in study["parts"]}
    iron_paths = {p["label"]: [] for p in study["parts"]}
    boxes = {p["label"]: [np.full(2, np.inf), np.full(2, -np.inf)] for p in study["parts"]}
    bead_low, bead_high = np.full(2, np.inf), np.full(2, -np.inf)
    x = y = e = feed = width = 0.0
    z, obj = None, None
    relative_e, ironing, feature = True, False, ""
    support_moves = deposited_moves = 0
    layer_heights = []
    for line in text.splitlines():
        match = re.match(r"; start printing object, unique label id: (\d+)", line)
        if match:
            obj = by_id[int(match[1])]
        if line.startswith("; stop printing object"):
            obj = None
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        if line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":", 1)[1])
        if line.startswith("; LAYER_HEIGHT:") and not ironing:
            h = float(line.split(":")[1])
            if h >= 0.20:
                layer_heights.append(round(h, 4))
        code = line.split(";")[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {k: float(v) for k, v in WORDS.findall(code)}
        if command == "M1031":
            ironing = words.get("S") == 1
        if command == "M82":
            relative_e = False
        if command == "M83":
            relative_e = True
        if command == "G92":
            x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
        if command not in ("G0", "G1", "G2", "G3"):
            continue
        nx, ny = words.get("X", x), words.get("Y", y)
        ne = words.get("E", 0 if relative_e else e)
        extrusion = ne if relative_e else ne-e
        feed = words.get("F", feed)
        start, end = np.array([x, y]), np.array([nx, ny])
        length, extrema = (arc_geometry(start, end, words, command == "G2")
                           if command in ("G2", "G3") else (float(np.linalg.norm(end-start)), np.array([start, end])))
        if z is not None and feature and feature != "Custom" and extrusion > 0 and length > 0.001:
            if width <= 0:
                raise ValueError("Deposited path has no native bead width")
            low, high = extrema.min(axis=0)-width/2, extrema.max(axis=0)+width/2
            bead_low, bead_high = np.minimum(bead_low, low), np.maximum(bead_high, high)
            deposited_moves += 1
            support_moves += int(feature.startswith("Support"))
            if obj is not None:
                box = boxes[obj["label"]]
                box[0], box[1] = np.minimum(box[0], low), np.maximum(box[1], high)
        if ironing and extrusion > 0 and length > 0.001:
            if obj is None:
                raise ValueError("Unassigned native ironing path")
            r = records[obj["label"]]
            r["ironing_extrusion_moves"] += 1
            r["ironing_length_mm"] += length
            r["deposited_filament_mm"] += extrusion
            r["speed_mm_s"].add(round(feed/60, 3))
            r["heights_mm"].add(round(z, 3))
            local = extrema-np.array(obj["center"][:2])
            if np.any(np.abs(local) > study["square_side_mm"]/2+0.001):
                r["outside_square_moves"] += 1
            iron_paths[obj["label"]].append([start, end])
        x, y, e = nx, ny, ne
    if support_moves:
        raise ValueError("Flat calibration squares require no supports")
    if layer_heights[0] != 0.30 or set(layer_heights[1:]) != {0.24}:
        raise ValueError("Unexpected layer heights")
    filament_area = np.pi*(float(original["filament_diameter"][0])/2)**2
    ratio = float(original["filament_flow_ratio"][0])
    for part in study["parts"]:
        r = records[part["label"]]
        r["speed_mm_s"], r["heights_mm"] = sorted(r["speed_mm_s"]), sorted(r["heights_mm"])
        if not part["ironed"]:
            if r["ironing_extrusion_moves"]:
                raise ValueError("OFF reference contains ironing")
            continue
        if r["ironing_extrusion_moves"] < 100 or r["outside_square_moves"]:
            raise ValueError(f"{part['label']}: missing ironing or ironing outside the top square")
        if r["speed_mm_s"] != [part["speed_mm_s"]] or r["heights_mm"] != [study["square_height_mm"]]:
            raise ValueError(f"{part['label']}: incorrect speed or ironing height; label tabs must stay un-ironed")
        emitted = r["deposited_filament_mm"]/r["ironing_length_mm"]
        expected = study["spacing_mm"]*study["layer_height_mm"]*part["flow_percent"]/100*ratio/filament_area
        if not np.isclose(emitted, expected, rtol=0.01):
            raise ValueError(f"{part['label']}: emitted ironing flow differs")
        paths = np.array(iron_paths[part["label"]])
        vectors = paths[:, 1]-paths[:, 0]
        lengths = np.linalg.norm(vectors, axis=1)
        direction = vectors[lengths.argmax()]/lengths.max()
        normal = np.array([-direction[1], direction[0]])
        parallel = (lengths > 20) & (np.abs(vectors@direction) > lengths*0.9999)
        offsets = np.unique(np.round(paths[parallel].mean(axis=1)@normal, 4))
        spacing = float(np.median(np.diff(offsets)))
        if not np.isclose(spacing, study["spacing_mm"], atol=0.002):
            raise ValueError(f"{part['label']}: emitted ironing spacing differs")
        r["measured_spacing_mm"] = round(spacing, 4)
        r["emitted_flow_percent"] = round(emitted*filament_area/(study["spacing_mm"]*study["layer_height_mm"]*ratio)*100, 3)
        r["ironing_length_mm"] = round(r["ironing_length_mm"], 5)
        r["deposited_filament_mm"] = round(r["deposited_filament_mm"], 5)
    bed = np.array(study["layout"]["left_nozzle_usable_bed_bounds_mm"])
    margins = np.concatenate((bead_low-bed[0], bed[1]-bead_high))
    if not deposited_moves or min(margins) < study["layout"]["minimum_emitted_bead_edge_margin_mm"]:
        raise ValueError(f"Native beads approach the bed edges: {margins}")
    separations = []
    labels = list(boxes)
    for i, first in enumerate(labels):
        a = np.array(boxes[first])
        if not np.isfinite(a).all():
            raise ValueError(f"{first}: no deposited model paths")
        for second in labels[:i]:
            b = np.array(boxes[second])
            gaps = np.maximum(np.maximum(a[0]-b[1], b[0]-a[1]), 0)
            separations.append(float(np.linalg.norm(gaps)))
    if min(separations) < 4.0:
        raise ValueError("Calibration squares do not retain separation")
    placement = dict(left_nozzle_usable_bed_bounds_mm=bed.tolist(),
                     model_support_brim_xy_bounds_mm=[bead_low.tolist(), bead_high.tolist()],
                     edge_margins_left_front_right_back_mm=margins.tolist(),
                     minimum_full_bead_edge_margin_mm=float(min(margins)),
                     minimum_specimen_full_bead_box_gap_mm=min(separations),
                     deposited_move_count=deposited_moves, support_move_count=support_moves,
                     scope="Native deposited model/brim beads, including arc extrema and half-width. Vendor startup purge/calibration paths are excluded. Placement does not establish adhesion.")
    report = dict(project=source.name, project_sha256=sha(source.read_bytes()),
                  slicer_version="02.08.02.61", return_code=0, plate_count=1, specimen_count=10,
                  estimated_seconds=round(plate["total_predication"], 3),
                  estimated_mass_g=round(sum(f["total_used_g"] for f in plate["filaments"]), 3),
                  ironing_estimated_seconds=round(plate["feature_type_times"]["Ironing"], 3),
                  warning_message=plate["warning_message"], embedded_gcode_md5_verified=True,
                  gcode_sha256=sha(data), physical_settings_match_saved_project=True,
                  emitted_nozzle_assignment=assignment, emitted_z_trim_commands=trims,
                  slicer_added_metadata=added, first_layer_height_mm=layer_heights[0],
                  normal_layer_heights_mm=sorted(set(layer_heights[1:])), total_layers=total_layers,
                  support_summary=dict(support_bodies=0), placement=placement, parts=list(records.values()),
                  scope="Native flat-square path verification. Surface finish selection and sealing performance remain unassessed.")
    (HERE / "slice-review.json").write_text(json.dumps(report, indent=2)+"\n")
    fig, ax = plt.subplots(figsize=(8.8, 8.4))
    side = study["square_side_mm"]
    for p in study["parts"]:
        cx, cy = p["center"][:2]
        ax.add_patch(Rectangle((cx-side/2, cy-side/2), side, side, fill=False, edgecolor="#315a71", linewidth=1))
        ax.add_patch(Rectangle((cx-16.5, cy-25.5), 33, 9, facecolor="#eef3f5", edgecolor="#315a71", linewidth=0.6))
        ax.text(cx, cy-21, p["label"], ha="center", va="center", fontsize=9, fontweight="bold")
        if iron_paths[p["label"]]:
            ax.add_collection(LineCollection(iron_paths[p["label"]], colors="#cd7a24", linewidths=0.25, alpha=0.5))
        else:
            ax.text(cx, cy, "No ironing", ha="center", va="center", fontsize=9)
    inset = study["layout"]["minimum_emitted_bead_edge_margin_mm"]
    ax.add_patch(Rectangle((inset, inset), bed[1, 0]-2*inset, bed[1, 1]-2*inset,
                           fill=False, edgecolor="#39856b", linestyle="--", linewidth=1))
    ax.text(162.5, 270, f"Label = speed (mm/s) / flow (%) · spacing 0.15 mm\n"
            f"35 × 35 mm clear faces · minimum bead inset {min(margins):.2f} mm", ha="center", fontsize=10)
    ax.text(162.5, 47, "Three speed rows × three flow columns + one OFF reference", ha="center", fontsize=10)
    ax.set(xlim=(0, 325), ylim=(0, 320), aspect="equal", xlabel="Plate X (mm)", ylabel="Plate Y (mm)")
    ax.set_title("PETG ironing calibration — flat squares and native ironing paths", pad=14)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", dpi=150)
    plt.close(fig)
    print(json.dumps({k: report[k] for k in ("estimated_seconds", "estimated_mass_g", "ironing_estimated_seconds", "placement")}, indent=2))


if __name__ == "__main__":
    main()
