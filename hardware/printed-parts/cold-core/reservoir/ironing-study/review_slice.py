"""Verify the native comparison slice and draw its actual ironing paths."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import sys
import zipfile

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.patches import Rectangle
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-ironing-study"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
import enclosure_support_audit as support_reader

WORDS = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
sha = lambda data: hashlib.sha256(data).hexdigest()


def arc_extrema(start, end, words, clockwise):
    """Include the exact XY cardinal extrema of the emitted I/J arc."""
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
    return np.array(points)


def main():
    study = json.loads((HERE / "study.json").read_text())
    source = HERE / study["project"]
    if sha(source.read_bytes()) != study["project_sha256"]:
        raise ValueError("Project differs from the generated study")
    directory = CACHE / "slice"
    result = json.loads((directory / "result.json").read_text())
    if result["return_code"] != 0 or len(result["sliced_plates"]) != 1:
        raise ValueError("Native slicing did not complete on one plate")
    plate = result["sliced_plates"][0]
    if plate["warning_message"] or len(plate["objects"]) != 18:
        raise ValueError("Unexpected native plate warning/object count")
    with zipfile.ZipFile(source) as archive:
        original = json.loads(archive.read("Metadata/project_settings.config"))
    with zipfile.ZipFile(directory / "ironing-study-review.3mf") as archive:
        sliced = json.loads(archive.read("Metadata/project_settings.config"))
        added_metadata = {k: v for k, v in sliced.items() if k not in original}
        if added_metadata not in ({}, {"filament_map_2": ["1"]}) or any(sliced.get(k) != v for k, v in original.items()):
            raise ValueError("Native slicer changed the saved process")
        data = archive.read("Metadata/plate_1.gcode")
        expected_md5 = archive.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        if hashlib.md5(data).hexdigest() != expected_md5:
            raise ValueError("Embedded G-code checksum")
        text = data.decode()
        emitted_map = {}
        for key, expected in (("filament_map", "1"), ("filament_nozzle_map", "0"),
                              ("nozzle_diameter", "0.8,0.8")):
            match = re.search(r"^; "+key+r" = (.+)$", text, re.MULTILINE)
            actual = match[1].strip() if match else None
            if actual != expected:
                raise ValueError(f"Native {key} is {actual!r}; expected {expected!r} for the left 0.8 mm nozzle")
            emitted_map[key] = actual
        trims = [line.strip() for line in text.splitlines() if line.strip().startswith("G29.1 Z")]
        if trims != ["G29.1 Z0 ; clear z-trim value first", "G29.1 Z0.02"]:
            raise ValueError(f"Native Mark2 Z trim differs: {trims}")
        (directory / "plate_1.gcode").write_bytes(data)
        (directory / "plate_1.png").write_bytes(archive.read("Metadata/plate_1.png"))
    paths = {p["label"]: [] for p in study["parts"]}
    records = {p["label"]: dict(label=p["label"], ironing_extrusion_moves=0, ironing_length_mm=0.0,
                                deposited_filament_mm=0.0, speed_mm_s=set(), heights_mm=set(),
                                slope_ironing_length_mm=0.0, outside_target_length_mm=0.0)
               for p in study["parts"]}
    by_id = {p["identify_id"]: p for p in study["parts"]}
    x = y = e = 0.0
    feed = 0.0
    relative_e = True
    z = None
    obj = None
    ironing = False
    feature = ""
    width = 0.0
    bead_low, bead_high = np.full(2, np.inf), np.full(2, -np.inf)
    support_low, support_high = np.full(2, np.inf), np.full(2, -np.inf)
    deposited_moves = 0
    support_moves = 0
    bead_boxes = {p["label"]: [np.full(2, np.inf), np.full(2, -np.inf)] for p in study["parts"]}
    layers = []
    for line in data.decode().splitlines():
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
            # Ironing pseudo-heights are extrusion metadata, not new layers.
            height = float(line.split(":")[1])
            if height >= 0.20:
                layers.append(round(height, 4))
        text = line.split(";")[0].strip()
        if not text:
            continue
        command = text.split()[0]
        words = {k: float(v) for k, v in WORDS.findall(text)}
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
        delta_e = ne if relative_e else ne-e
        feed = words.get("F", feed)
        points = [(x, y)] + (support_reader._arc_points((x, y), (nx, ny), words, command == "G2")
                              if command in ("G2", "G3") and ("I" in words or "J" in words)
                              else [(nx, ny)])
        length = sum(np.linalg.norm(np.array(b)-a) for a, b in zip(points, points[1:]))
        if z is not None and feature and feature != "Custom" and delta_e > 0 and length > 0.001:
            if width <= 0:
                raise ValueError("Deposited path has no native bead width")
            extrema = (arc_extrema((x, y), (nx, ny), words, command == "G2")
                       if command in ("G2", "G3") and ("I" in words or "J" in words)
                       else np.array([(x, y), (nx, ny)]))
            low, high = extrema.min(axis=0)-width/2, extrema.max(axis=0)+width/2
            bead_low, bead_high = np.minimum(bead_low, low), np.maximum(bead_high, high)
            deposited_moves += 1
            if feature.startswith("Support"):
                support_low, support_high = np.minimum(support_low, low), np.maximum(support_high, high)
                support_moves += 1
            if obj is not None:
                box = bead_boxes[obj["label"]]
                box[0], box[1] = np.minimum(box[0], low), np.maximum(box[1], high)
        if ironing and obj is not None and delta_e > 0 and length > 0.001:
            row = records[obj["label"]]
            row["ironing_extrusion_moves"] += 1
            row["ironing_length_mm"] += length
            row["deposited_filament_mm"] += delta_e
            row["speed_mm_s"].add(round(feed/60, 3))
            row["heights_mm"].add(round(z, 3))
            origin = np.array(obj["center"][:2])
            for a, b in zip(points, points[1:]):
                a, b = np.array(a), np.array(b)
                span = np.linalg.norm(b-a)
                # Sample the deposited centerline at <=0.1 mm for mask checks.
                count = max(1, int(np.ceil(span/0.1)))
                mid = a + (b-a)*((np.arange(count)+0.5)/count)[:, None] - origin
                slopes = np.abs(mid[:, 1]) > 14+0.02 if obj["feature"] != "G" else np.zeros(count, bool)
                row["slope_ironing_length_mm"] += span*slopes.mean()
                if obj["feature"] == "B":
                    radii = np.linalg.norm(mid, axis=1)
                    outside = (radii < 7.9-0.03) | (radii > 12.15+0.03) | (abs(z-4.65) > 0.13)
                elif obj["feature"] == "G":
                    outside = (np.abs(mid[:, 1]) > 16.1) | (abs(z-10.03) > 0.13)
                else:
                    outside = np.zeros(count, bool)
                row["outside_target_length_mm"] += span*outside.mean()
                paths[obj["label"]].append([a.tolist(), b.tolist()])
        x, y = nx, ny
        if not relative_e:
            e = ne
    for part in study["parts"]:
        row = records[part["label"]]
        for key in ("speed_mm_s", "heights_mm"):
            row[key] = sorted(row[key])
        for key in ("ironing_length_mm", "deposited_filament_mm", "slope_ironing_length_mm", "outside_target_length_mm"):
            row[key] = round(row[key], 5)
        if part["ironed"] != bool(row["ironing_extrusion_moves"]):
            raise ValueError(f"{part['label']}: incorrect on/off behavior")
        if part["ironed"] and row["speed_mm_s"] != [part["speed_mm_s"]]:
            raise ValueError(f"{part['label']}: emitted ironing speed {row['speed_mm_s']} differs")
        if row["outside_target_length_mm"] > 0.1 or (part["feature"] == "B" and row["slope_ironing_length_mm"] > 0):
            raise ValueError(f"{part['label']}: ironing escaped the flat sealing face")
    if records["S1I"]["slope_ironing_length_mm"] < 10:
        raise ValueError("The slope diagnostic did not actually iron the slope")
    for feature in ("G", "B"):
        full, half = records[feature+"1I"], records[feature+"2I"]
        ratios = (half["deposited_filament_mm"]/half["ironing_length_mm"] /
                  (full["deposited_filament_mm"]/full["ironing_length_mm"]))
        if not 0.48 < ratios < 0.52:
            raise ValueError(f"{feature}: half-flow condition was not emitted")
        if not 0.45 < records[feature+"4I"]["ironing_length_mm"]/full["ironing_length_mm"] < 0.60:
            raise ValueError(f"{feature}: wider spacing condition was not emitted")
    support = support_reader.audit(directory / "plate_1.gcode", "reservoir-ironing-study",
                                   include_unlabelled_support=True)
    bed = np.array(study["layout"]["left_nozzle_usable_bed_bounds_mm"])
    margins = np.concatenate((bead_low-bed[0], bed[1]-bead_high))
    if not deposited_moves or min(margins) < study["layout"]["minimum_emitted_bead_edge_margin_mm"]:
        raise ValueError(f"Emitted model/support/brim paths approach the bed edges: {margins}")
    separations = []
    labels = list(bead_boxes)
    for index, first in enumerate(labels):
        a = np.array(bead_boxes[first])
        if not np.isfinite(a).all():
            raise ValueError(f"{first}: no deposited specimen paths")
        for second in labels[:index]:
            b = np.array(bead_boxes[second])
            gaps = np.maximum(np.maximum(a[0]-b[1], b[0]-a[1]), 0)
            separations.append(dict(labels=[first, second], full_bead_box_gap_mm=float(np.linalg.norm(gaps))))
    if min(p["full_bead_box_gap_mm"] for p in separations) < 1.5:
        raise ValueError("The compact layout does not retain specimen separation")
    placement = dict(left_nozzle_usable_bed_bounds_mm=bed.tolist(),
                     model_support_brim_xy_bounds_mm=[bead_low.tolist(), bead_high.tolist()],
                     edge_margins_left_front_right_back_mm=margins.tolist(),
                     minimum_full_bead_edge_margin_mm=float(min(margins)),
                     deposited_move_count=deposited_moves, support_move_count=support_moves,
                     support_xy_bounds_mm=[support_low.tolist(), support_high.tolist()] if support_moves else None,
                     per_specimen_full_bead_xy_bounds_mm={label: [v.tolist() for v in box] for label, box in bead_boxes.items()},
                     minimum_specimen_full_bead_box_gap_mm=min(p["full_bead_box_gap_mm"] for p in separations),
                     scope="All native deposited specimen, support and brim beads, including arc extrema and half-width. Vendor startup purge/calibration paths are excluded. Placement does not establish adhesion.")
    report = dict(project=source.name, project_sha256=sha(source.read_bytes()),
                  slicer_version="02.08.02.61", return_code=0, plate_count=1, specimen_count=18,
                  estimated_seconds=round(plate["total_predication"], 3),
                  estimated_mass_g=round(sum(f["total_used_g"] for f in plate["filaments"]), 3),
                  ironing_estimated_seconds=round(plate["feature_type_times"]["Ironing"], 3),
                  warning_message=plate["warning_message"], embedded_gcode_md5_verified=True,
                  gcode_sha256=sha(data), physical_settings_match_saved_project=True,
                  emitted_nozzle_assignment=emitted_map, emitted_z_trim_commands=trims,
                  slicer_added_metadata=added_metadata,
                  first_layer_height_mm=layers[0], normal_layer_heights_mm=sorted(set(layers[1:])),
                  support_summary=support["summary"], support_bodies=support["trees"],
                  placement=placement,
                  parts=list(records.values()),
                  scope="Native path verification. Surface finish and contact performance await the physical print.")
    (HERE / "slice-review.json").write_text(json.dumps(report, indent=2)+"\n")

    fig, ax = plt.subplots(figsize=(10, 10.4))
    for part in study["parts"]:
        mesh = trimesh.load(CACHE / (part["label"]+".stl"), force="mesh", process=True)
        shifted = mesh.vertices[:, :2]+np.array(part["center"][:2])
        # Show physical edges; omit triangulation diagonals on planar faces.
        neighbors = mesh.face_adjacency
        normals = mesh.face_normals[neighbors]
        edge = (np.einsum("ij,ij->i", normals[:, 0], normals[:, 1]) < 0.9999) & (normals[:, :, 2].max(axis=1) > 0.2)
        outlines = shifted[mesh.face_adjacency_edges[edge]]
        ax.add_collection(LineCollection(outlines, colors="#98a8b6", linewidths=0.6, alpha=0.8))
        color = "#b63b37" if part["feature"] == "S" else "#d57b16"
        if paths[part["label"]]:
            ax.add_collection(LineCollection(paths[part["label"]], colors=color, linewidths=0.45))
        ax.text(part["center"][0], part["center"][1]-(20.5 if part["feature"] == "G" else 23.5),
                part["label"], ha="center", va="center", fontsize=9,
                color=color if part["ironed"] else "#234e70", fontweight="bold",
                bbox=dict(facecolor="white", edgecolor="none", alpha=0.85, pad=0.8))
    inset = study["layout"]["minimum_emitted_bead_edge_margin_mm"]
    ax.add_patch(Rectangle((inset, inset), bed[1, 0]-2*inset, bed[1, 1]-2*inset,
                           fill=False, edgecolor="#39758a", linestyle="--", linewidth=1,
                           label=f"{inset:g} mm inset from usable bed edges"))
    ax.text(162.5, 278, f"Minimum full-bead edge clearance: {min(margins):.2f} mm\n"
            "G: gasket rim    B: washer seat    S: slope diagnostic", ha="center", fontsize=10)
    ax.legend(loc="lower center", frameon=False, bbox_to_anchor=(0.5, 0.02))
    ax.set(xlim=(0, 325), ylim=(0, 320), aspect="equal", xlabel="Plate X (mm)", ylabel="Plate Y (mm)")
    ax.set_title("Centered reservoir ironing comparison — actual native paths\nC = un-ironed control     I = ironed     orange/red = ironing", pad=16)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", dpi=150)
    plt.close(fig)
    print(json.dumps({k: report[k] for k in ("estimated_seconds", "estimated_mass_g", "support_summary", "placement")}, indent=2))


if __name__ == "__main__":
    main()
