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
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-ironing-study"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
import enclosure_support_audit as support_reader

WORDS = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
sha = lambda data: hashlib.sha256(data).hexdigest()


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
    layers = []
    for line in data.decode().splitlines():
        match = re.match(r"; start printing object, unique label id: (\d+)", line)
        if match:
            obj = by_id[int(match[1])]
        if line.startswith("; stop printing object"):
            obj = None
        if line.startswith("; Z_HEIGHT:"):
            z = float(line.split(":")[1])
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
    report = dict(project=source.name, project_sha256=sha(source.read_bytes()),
                  slicer_version="02.08.02.61", return_code=0, plate_count=1, specimen_count=18,
                  estimated_seconds=round(plate["total_predication"], 3),
                  estimated_mass_g=round(sum(f["total_used_g"] for f in plate["filaments"]), 3),
                  ironing_estimated_seconds=round(plate["feature_type_times"]["Ironing"], 3),
                  warning_message=plate["warning_message"], embedded_gcode_md5_verified=True,
                  gcode_sha256=sha(data), physical_settings_match_saved_project=True,
                  slicer_added_metadata=added_metadata,
                  first_layer_height_mm=layers[0], normal_layer_heights_mm=sorted(set(layers[1:])),
                  support_summary=support["summary"], support_bodies=support["trees"],
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
        ax.text(part["center"][0], part["center"][1]-33, part["label"], ha="center", va="center", fontsize=9,
                color=color if part["ironed"] else "#234e70", fontweight="bold")
    for row, (number, title, flow, speed, spacing) in enumerate((("1", "September", 10, 30, .15),
                                                               ("2", "Half flow", 5, 30, .15),
                                                               ("3", "Twice speed", 10, 60, .15),
                                                               ("4", "Twice spacing", 10, 30, .30))):
        ax.text(275, 46+row*58, f"{number}. {title}\n{flow}% / {speed} mm/s\n{spacing:.2f} mm spacing", ha="center", va="center", fontsize=9)
    ax.text(55.5, 315, "G: gasket rim", ha="center", fontsize=11, fontweight="bold")
    ax.text(202.5, 315, "B: washer seat", ha="center", fontsize=11, fontweight="bold")
    ax.text(278, 283, "S: slope diagnostic\nSeptember ironing\non the adjacent floor", ha="center", va="center", fontsize=9, color="#b63b37")
    ax.set(xlim=(0, 325), ylim=(0, 325), aspect="equal", xlabel="Plate X (mm)", ylabel="Plate Y (mm)")
    ax.set_title("Reservoir ironing comparison — actual native paths\nC = un-ironed control     I = ironed     orange/red = ironing", pad=16)
    ax.grid(alpha=0.15)
    fig.tight_layout()
    fig.savefig(HERE / "plate-layout.png", dpi=150)
    plt.close(fig)
    print(json.dumps({k: report[k] for k in ("estimated_seconds", "estimated_mass_g", "support_summary")}, indent=2))


if __name__ == "__main__":
    main()
