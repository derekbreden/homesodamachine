#!/usr/bin/env python3
"""Prepare fresh native Bambu projects for the enclosure trial from the current meshes.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py list
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py front-top
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py front-top --printer Mark2 --slice --review
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py all --slice --review
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/prepare.py factory-tools \
        --part hardware/printed-parts/enclosure/enclosure/enclosure-pump-tube-setting-jig.stl,quantity=1,turns=x:0

`pieces.json` declares every piece: its meshes, pose, printer, recipe changes with
their reasons, and the named features read from each mesh. Preparation writes the
project and its `preparation.json` record; `--slice` runs the installed Bambu Studio
command line on it, and `--review` reads the emitted archive (`review.py`). No
printer is contacted.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
import shutil
import subprocess
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path.insert(0, str(HERE))
import _derive  # noqa: E402
import _mesh  # noqa: E402
import _native  # noqa: E402

SPEC_PATH = HERE / "pieces.json"
STEP_MESHES = HERE / "step-meshes.json"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
OUTPUT = ROOT / ".cache/prints/trial"
#: Bambu's two-hotend arrays list the left hotend first; a filament maps to hotend 1 or 2.
SIDES = {"left": 0, "right": 1}


def relative(path: Path) -> str:
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, default=_plain) + "\n")


def _plain(value):
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    raise TypeError(type(value))


class Mesh:
    """One STL, read once, posed into its print frame."""

    def __init__(self, path: Path, pose: dict | None):
        self.path = path
        self.sha256 = _mesh.sha256(path)
        step = path.with_suffix(".step")
        self.step_sha256 = _mesh.sha256(step) if step.is_file() else None
        bound = (json.loads(STEP_MESHES.read_text())["meshes"].get(relative(path))
                 if STEP_MESHES.is_file() else None)
        if bound and (bound["stl_sha256"] != self.sha256 or bound["step_sha256"] != self.step_sha256):
            raise ValueError(f"{relative(path)} was cut by step_meshes.py from STEP {bound['step_sha256'][:12]}; "
                             f"the STEP is now {(self.step_sha256 or '-')[:12]} and the STL {self.sha256[:12]}. "
                             "Cut it again with step_meshes.py.")
        triangles = _mesh.read_stl(path)
        self.vertices, self.faces = _mesh.merge(triangles)
        del triangles
        self.closed = _mesh.closed_check(self.faces)
        if not self.closed["closed_oriented_single_body"]:
            raise ValueError(f"{relative(path)} is not one closed, oriented body: {self.closed}")
        self.center = (self.vertices.min(axis=0) + self.vertices.max(axis=0)) / 2.0
        self.rotation = _mesh.rotation(pose)
        placed = (self.vertices - self.center) @ self.rotation.T
        self.lift = -float(placed[:, 2].min())
        placed[:, 2] += self.lift
        self.print_vertices = placed
        self.geometry = _derive.Geometry(placed[self.faces], self.faces)

    def print_to_local(self, points) -> np.ndarray:
        """Print-frame points into the stored local frame (source frame less its center)."""
        points = np.asarray(points, float).copy()
        points[..., 2] -= self.lift
        return points @ self.rotation


def regions_for(spec: dict, key: str, mesh: Mesh) -> dict:
    path = ROOT / spec["regions"]
    record = json.loads(path.read_text())
    bound = record["native_artifact_sha256"].get(key)
    if bound is None:
        raise ValueError(f"{relative(path)} has no regions for {key}")
    if bound[".stl"] != mesh.sha256 or (mesh.step_sha256 and bound[".step"] != mesh.step_sha256):
        raise ValueError(f"{relative(path)} binds {key} to STL {bound['.stl'][:12]} / STEP {bound['.step'][:12]}; "
                         f"the current exports are {mesh.sha256[:12]} / {(mesh.step_sha256 or '-')[:12]}. "
                         "Regenerate it with heat-set-review/print_regions.py from the current geometry.")
    return {"record": relative(path), "record_sha256": _mesh.sha256(path), "rows": record["pieces"][key],
            "part_process_overrides": record.get("part_process_overrides", {}).get(key)}


def derive(mesh: Mesh, declared: list[dict]) -> list[dict]:
    found, transitions = [], []
    for feature in declared:
        kind = feature["kind"]
        if feature.get("enabled", True) is False:
            found.append({"name": feature["name"], "kind": kind, "enabled": False, "reason": feature["reason"]})
            continue
        if kind == "fine_band":
            found.append(_derive.fine_band(mesh.geometry, feature))
        elif kind == "transition_band":
            result = _derive.transition_band(mesh.geometry, feature)
            transitions.append(result)
            found.append(result)
        elif kind == "ceiling_inset":
            if not transitions:
                raise _derive.FeatureMissing(f"{feature['name']}: declare its transition band first")
            found.append(_derive.ceiling_inset(mesh.geometry, feature, transitions[-1]["foot_print_z_mm"]))
        elif kind == "groove_ribbons":
            found.append(_derive.groove_ribbons(mesh.geometry, feature))
        elif kind == "tie_windows":
            found.append(_derive.tie_windows(mesh.geometry, feature))
        elif kind == "edge_fins":
            ceiling = next((f for f in found if f["kind"] == "ceiling_inset"), None)
            if ceiling is None:
                raise _derive.FeatureMissing(f"{feature['name']}: declare its ceiling first")
            found.append(_derive.edge_fins(mesh.geometry, feature, ceiling))
        else:
            raise ValueError(f"unknown feature kind {kind}")
    return found


def layer_ranges(features: list[dict]) -> list[dict]:
    bands = []
    for f in features:
        if f["kind"] == "fine_band":
            low, high = f["span_print_z_mm"]
            # One fine layer past the span's top: the slicer ends a range on the last whole layer
            # inside it, and the span's top must sit inside a fine layer, not under the next 0.24.
            bands.append({"min_z": max(0.0, low - _derive.LAYER), "max_z": high + f["layer_height_mm"],
                          "options": {"layer_height": f"{f['layer_height_mm']:g}"}, "feature": f["name"]})
        elif f["kind"] == "transition_band":
            low, high = f["span_print_z_mm"]
            bands.append({"min_z": max(0.0, low - _derive.LAYER), "max_z": high + 0.1,
                          "options": {"layer_height": "0.24", "wall_loops": str(f["wall_loops"])}, "feature": f["name"]})
    bands.sort(key=lambda b: b["min_z"])
    merged = []
    for band in bands:
        if merged and band["min_z"] <= merged[-1]["max_z"]:
            last = merged[-1]
            last["max_z"] = max(last["max_z"], band["max_z"])
            heights = [float(o["layer_height"]) for o in (last["options"], band["options"])]
            walls = [int(o.get("wall_loops", 0)) for o in (last["options"], band["options"])]
            last["options"] = {"layer_height": f"{min(heights):g}", **({"wall_loops": str(max(walls))} if max(walls) else {})}
            last["feature"] += " + " + band["feature"]
        else:
            merged.append(dict(band))
    return merged


def parse_part(text: str) -> dict:
    path, *options = text.split(",")
    part = {"stl": path, "quantity": 1}
    for option in options:
        key, value = option.split("=", 1)
        if key == "quantity":
            part["quantity"] = int(value)
        elif key == "turns":
            part["pose"] = {"turns": [[t.split(":")[0], float(t.split(":")[1])] for t in value.split("+")]}
        elif key == "walls":
            part.setdefault("object_settings", {})["wall_loops"] = {"value": value, "reason": "Command-line part declaration."}
        elif key == "infill":
            part.setdefault("object_settings", {})["sparse_infill_density"] = {"value": f"{value}%", "reason": "Command-line part declaration."}
            part["object_settings"]["sparse_infill_pattern"] = {"value": "zig-zag", "reason": "Command-line part declaration."}
        elif key == "name":
            part["name"] = value
        else:
            raise ValueError(f"unknown part option {key}")
    return part


def layout(footprints: list[tuple[float, float]], usable_low, usable_high, spacing: float,
           yaw_choice) -> list[tuple[int, float, float]]:
    """Yaw and plate-center XY for each footprint (width x, depth y), packed in rows and centered."""
    width = usable_high[0] - usable_low[0]
    depth = usable_high[1] - usable_low[1]
    if len(footprints) == 1:
        dx, dy = footprints[0]
        options = [0, 90] if yaw_choice == "auto" else [int(yaw_choice)]
        margin = lambda yaw: min(width - (dx if yaw == 0 else dy), depth - (dy if yaw == 0 else dx)) / 2
        yaw = max(options, key=lambda y: (round(margin(y), 6), -y))
        return [(yaw, (usable_low[0] + usable_high[0]) / 2, (usable_low[1] + usable_high[1]) / 2)]
    order = sorted(range(len(footprints)), key=lambda i: -footprints[i][1])
    rows, row, x = [], [], 0.0
    for i in order:
        dx, dy = footprints[i]
        if row and x + dx > width - 40:
            rows.append(row)
            row, x = [], 0.0
        row.append((i, x, dx, dy))
        x += dx + spacing
    rows.append(row)
    placed, y = {}, 0.0
    for row in rows:
        row_depth = max(dy for _, _, _, dy in row)
        row_width = row[-1][1] + row[-1][2]
        for i, x0, dx, dy in row:
            placed[i] = (x0 + dx / 2 - row_width / 2, y + row_depth / 2)
        y += row_depth + spacing
    total = y - spacing
    cx, cy = (usable_low[0] + usable_high[0]) / 2, (usable_low[1] + usable_high[1]) / 2
    return [(0, cx + placed[i][0], cy + placed[i][1] - total / 2) for i in range(len(footprints))]


def yaw_matrix(degrees: float) -> np.ndarray:
    return _mesh.rotation({"turns": [["z", degrees]]})


def check_nozzle(name: str, piece: dict, settings: dict, profile_path: Path) -> dict:
    """The declared hotend against the one the recipe slices for and the side its filament maps to."""
    nozzle = piece["nozzle"]
    side = SIDES[nozzle["side"]]
    diameter = float(settings["nozzle_diameter"][side])
    if abs(diameter - nozzle["diameter_mm"]) > 1e-6:
        raise ValueError(f"{name} declares a {nozzle['diameter_mm']:g} mm {nozzle['side']} nozzle; "
                         f"{relative(profile_path)} slices {diameter:g} mm there")
    volume = settings.get("nozzle_volume_type", [])
    if nozzle.get("flow") and len(volume) > side and volume[side] != nozzle["flow"]:
        raise ValueError(f"{name} declares a {nozzle['flow']} {nozzle['side']} nozzle; "
                         f"{relative(profile_path)} slices {volume[side]}")
    mapped = {int(v) for v in settings.get("filament_map", ["1"])}
    if mapped != {side + 1}:
        raise ValueError(f"{name} prints on the {nozzle['side']} nozzle; the recipe maps its filament to {sorted(mapped)}")
    return {**nozzle, "sliced_diameter_mm": diameter, "sliced_volume_type": volume[side] if len(volume) > side else None}


def prepare(name: str, printer: str | None = None, parts: list[dict] | None = None,
            output: Path | None = None, border: float | None = None) -> Path:
    spec = json.loads(SPEC_PATH.read_text())
    piece = spec["pieces"][name]
    if "external" in piece:
        raise ValueError(f"{name} is prepared by {piece['external']['command']}")
    printer = printer or piece["printer"]
    machine = spec["printers"][printer]
    profile_path = ROOT / piece.get("profile", spec["profile"])
    z_trim = piece["z_trim_mm"]["value"] if "z_trim_mm" in piece else machine["z_trim_mm"]
    filament_from = ROOT / piece["filament_from"] if piece.get("filament_from") else None
    profile = _native.profile_settings(profile_path, z_trim, filament_from)
    title = f"{name}; {printer}"
    plate = _native.Plate(title, profile)
    settings = plate.settings
    changes = {}

    def put(key, value, reason):
        changes[key] = {"from": profile["settings"].get(key), "to": value, "reason": reason}
        settings[key] = value

    mapping = piece.get("filament_mapping", {"value": spec["filament_mapping"], "reason":
                        "Single external black PET-GF spool on the fixed left nozzle for model, support and interface."})
    for key, value in mapping["value"].items():
        put(key, value, mapping["reason"])
    colour = piece.get("filament_colour", {"value": machine["filament_colour"],
                                           "reason": f"{printer}'s loaded black PET-GF colour reading."})
    put("filament_colour", [colour["value"]], colour["reason"])
    if "z_trim_mm" in piece:
        changes["requested_z_trim_mm"] = {"from": machine["z_trim_mm"], "to": z_trim, "reason": piece["z_trim_mm"]["reason"]}
    for key, declared in piece.get("settings", {}).items():
        put(key, declared["value"], declared["reason"])
    nozzle = check_nozzle(name, piece, settings, profile_path)

    declared_parts = parts if parts is not None else piece["parts"]
    meshes, derived, instances = {}, {}, []
    for part in declared_parts:
        path = ROOT / part["stl"]
        if not path.is_file():
            raise FileNotFoundError(f"{part['stl']} is not exported")
        key = (part["stl"], json.dumps(part.get("pose")))
        if key not in meshes:
            meshes[key] = Mesh(path, part.get("pose"))
        mesh = meshes[key]
        declared = json.dumps(part.get("features", []), sort_keys=True)
        if (key, declared) not in derived:
            derived[(key, declared)] = derive(mesh, part.get("features", []))
        features = derived[(key, declared)]
        regions = regions_for(spec, part["regions"], mesh) if part.get("regions") else None
        for copy in range(part.get("quantity", 1)):
            instances.append({"part": part, "mesh": mesh, "features": features, "regions": regions,
                              "name": part.get("name", Path(part["stl"]).stem) + (f"-{copy + 1}" if part.get("quantity", 1) > 1 else "")})

    for mesh in meshes.values():
        mesh.geometry = None
    usable_low, usable_high = np.array(profile["usable_low"]), np.array(profile["usable_high"])
    footprints = []
    for inst in instances:
        p = inst["mesh"].print_vertices
        footprints.append(tuple((p[:, :2].max(axis=0) - p[:, :2].min(axis=0)).tolist()))
    placements = layout(footprints, usable_low, usable_high, piece.get("spacing_mm", 12.0), piece.get("yaw_degrees", "auto"))
    offset = piece.get("plate_offset_mm", {}).get("value", [0.0, 0.0])
    placements = [(yaw, cx + offset[0], cy + offset[1]) for yaw, cx, cy in placements]
    border = piece.get("plate_border_mm", 20.0) if border is None else border
    # auto_brim sizes each volume group's brim while slicing; review.py reads the emitted envelope.
    brim = float(settings.get("brim_width", 5)) + 0.5 if settings.get("brim_type") in ("outer_only", "outer_and_inner") else 0.0

    records = []
    for inst, (yaw, cx, cy) in zip(instances, placements):
        mesh, part = inst["mesh"], inst["part"]
        r_yaw = yaw_matrix(yaw)
        p = mesh.print_vertices @ r_yaw.T
        mid = (p[:, :2].min(axis=0) + p[:, :2].max(axis=0)) / 2
        translation = np.array([cx - mid[0], cy - mid[1], mesh.lift])
        plate_points = p + [translation[0], translation[1], 0.0]
        low, high = plate_points.min(axis=0), plate_points.max(axis=0)
        margin = float(min(np.min(low[:2] - usable_low), np.min(usable_high - high[:2])))
        if margin - brim < border:
            raise ValueError(f"{inst['name']}: the model footprint leaves {margin:.2f} mm to the usable plate; "
                             f"with {brim:g} mm of brim that is inside the {border:g} mm bed border")
        to_plate = lambda q: np.asarray(q, float) @ r_yaw.T + [translation[0], translation[1], 0.0]
        paint = [None] * len(mesh.faces)
        for f in inst["features"]:
            for index in f.get("paint_faces", []):
                paint[int(index)] = "8"
            for index, code in f.get("paint_codes", {}).items():
                if paint[index] is None:
                    paint[index] = code
        object_settings = {k: v["value"] for k, v in part.get("object_settings", {}).items()}
        obj = plate.add_object(inst["name"], mesh.vertices - mesh.center, mesh.faces,
                               source_file=Path(part["stl"]).name, source_center=mesh.center,
                               build_rotation=r_yaw @ mesh.rotation, translation=translation,
                               paint=paint, settings=object_settings)
        record = {"name": inst["name"], "identify_id": obj["identify_id"], "object_id": obj["object_id"],
                  "stl": part["stl"], "stl_sha256": mesh.sha256, "step_sha256": mesh.step_sha256,
                  "facets": int(len(mesh.faces)), "closed": mesh.closed, "pose": part.get("pose"),
                  "pose_rotation": mesh.rotation.tolist(), "yaw_degrees": yaw,
                  "source_center_mm": mesh.center.tolist(), "build_rotation": obj["build_rotation"],
                  "translation_mm": translation.tolist(),
                  "plate_bounds_mm": [low.tolist(), high.tolist()], "model_bed_margin_mm": margin,
                  "object_settings": part.get("object_settings", {}), "features": [], "ranges": [],
                  "verify_spans": [], "ribbons": [], "tie_windows": [], "modifiers": [], "fins": []}
        ribbon_source_boxes = []
        for f in inst["features"]:
            entry = {k: v for k, v in f.items() if k not in ("paint_faces", "paint_codes", "region", "ribbons", "windows", "fins")}
            record["features"].append(entry)
            if f.get("enabled", True) is False:
                continue
            if f["kind"] == "fine_band":
                record["verify_spans"].append({"name": f["name"], "print_z_mm": f["span_print_z_mm"],
                                               "layer_height_mm": f["layer_height_mm"]})
            if f["kind"] == "groove_ribbons":
                for ribbon in f["ribbons"]:
                    low_b, high_b = ribbon["box_print_mm"]
                    corners = np.array([[x, y, z] for x in (low_b[0], high_b[0]) for y in (low_b[1], high_b[1]) for z in (low_b[2], high_b[2])])
                    local = mesh.print_to_local(corners)
                    vertices, faces = _mesh.box_mesh(local.min(axis=0), local.max(axis=0))
                    plate.add_part(obj, f"Removable groove ribbon {ribbon['number']}", vertices, faces,
                                   subtype="normal_part", settings=f["ribbon_settings"], paint_all="8")
                    ribbon_source_boxes.append((local.min(axis=0) + mesh.center, local.max(axis=0) + mesh.center))
                    placed = to_plate(corners)
                    record["ribbons"].append({**ribbon, "box_plate_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]})
            if f["kind"] == "tie_windows":
                for window in f["windows"]:
                    low_b, high_b = window["box_print_mm"]
                    corners = np.array([[x, y, z] for x in (low_b[0], high_b[0]) for y in (low_b[1], high_b[1]) for z in (low_b[2], high_b[2])])
                    placed = to_plate(corners)
                    record["tie_windows"].append({**window, "box_plate_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]})
                    if f["blockers"]:
                        local = mesh.print_to_local(corners)
                        vertices, faces = _mesh.box_mesh(local.min(axis=0), local.max(axis=0))
                        plate.add_part(obj, "Tie channel support exclusion", vertices, faces, subtype="support_blocker")
            if f["kind"] == "edge_fins":
                for fin in f["fins"]:
                    boxes = [("normal_part", "box_print_mm"), ("support_blocker", "blocker_print_mm")]
                    if "foot_print_mm" in fin:
                        boxes.append(("normal_part", "foot_print_mm"))
                    for kind, box_key in boxes:
                        low_b, high_b = fin[box_key]
                        corners = np.array([[x, y, z] for x in (low_b[0], high_b[0]) for y in (low_b[1], high_b[1]) for z in (low_b[2], high_b[2])])
                        local = mesh.print_to_local(corners)
                        vertices, faces = _mesh.box_mesh(local.min(axis=0), local.max(axis=0))
                        plate.add_part(obj, "Removable edge fin" if kind == "normal_part" else "Edge fin contact strip",
                                       vertices, faces, subtype=kind,
                                       settings={"wall_loops": "2", "sparse_infill_density": "0%"} if kind == "normal_part" else {},
                                       paint_all="8" if kind == "normal_part" else None)
                    placed = to_plate(np.array(fin["box_print_mm"]))
                    record["fins"].append({**fin, "box_plate_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]})
        if part.get("pause"):
            # One print pause loads parts into closed slots: support stays out of each slot, and
            # the source Z the pause waits under is carried into this part's print frame.
            pause = part["pause"]
            if abs(abs(mesh.rotation[2][2]) - 1.0) > 1e-9:
                raise ValueError(f"{inst['name']}: a pause plane needs a pose that keeps Z vertical")

            def print_z(source_z):
                local = np.array([0.0, 0.0, source_z]) - mesh.center
                return float((local @ mesh.rotation.T)[2] + mesh.lift)
            slots = []
            for x0, x1, y0, y1, z0, z1 in pause["slots_source_mm"]:
                low_s, high_s = np.array([x0, y0, z0]), np.array([x1, y1, z1])
                # A blocker has to intersect the roof that would request support. Ending
                # just under that face leaves the slicer free to grow a tree into the slot.
                blocker_high = high_s + [0.0, 0.0, pause.get("blocker_roof_overlap_mm", 0.0)]
                vertices, faces = _mesh.box_mesh(low_s - mesh.center, blocker_high - mesh.center)
                plate.add_part(obj, "Magnet slot support exclusion", vertices, faces, subtype="support_blocker")
                corners = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)])
                placed = (corners - mesh.center) @ (r_yaw @ mesh.rotation).T + translation
                slots.append([placed.min(axis=0).tolist(), placed.max(axis=0).tolist()])
            record["pause"] = {"source_z_mm": pause["source_z_mm"], "threshold_print_z_mm": print_z(pause["source_z_mm"]),
                               "stack_top_print_z_mm": print_z(pause["stack_top_source_z_mm"]),
                               "slots_plate_mm": slots, "gcode": pause.get("gcode", "M400 U1"),
                               "message": pause["message"], "reason": pause["reason"]}
        if inst["regions"]:
            overrides = inst["regions"]["part_process_overrides"]
            record["regions"] = {k: v for k, v in inst["regions"].items() if k != "rows"}
            if overrides:
                record["regions"]["whole_part_settings_apply"] = True
            else:
                source_low, source_high = mesh.vertices.min(axis=0), mesh.vertices.max(axis=0)
                for row in inst["regions"]["rows"]:
                    bounds = np.array(row.get("applied_source_bounds_mm", row["machine_bounds_mm"])).reshape(3, 2)
                    low_r = np.maximum(bounds[:, 0], source_low + 0.001)
                    high_r = np.minimum(bounds[:, 1], source_high - 0.001)
                    if np.any(high_r <= low_r):
                        raise ValueError(f"{inst['name']}: region {row['name']} lies outside the mesh")
                    pieces = _mesh.subtract_boxes(low_r, high_r, ribbon_source_boxes)
                    for box_low, box_high in pieces:
                        vertices, faces = _mesh.box_mesh(np.array(box_low) - mesh.center, np.array(box_high) - mesh.center)
                        plate.add_part(obj, row["name"], vertices, faces, subtype="modifier_part",
                                       settings={"sparse_infill_density": row.get("sparse_infill_density", "100%"),
                                                 "sparse_infill_pattern": row.get("sparse_infill_pattern", "zig-zag")})
                        corners = np.array([[x, y, z] for x in (box_low[0], box_high[0]) for y in (box_low[1], box_high[1]) for z in (box_low[2], box_high[2])])
                        placed = (corners - mesh.center) @ (r_yaw @ mesh.rotation).T + translation
                        record["modifiers"].append({"name": row["name"], "source_bounds_mm": [box_low, box_high],
                                                    "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
                                                    "sparse_infill_density": row.get("sparse_infill_density", "100%")})
        obj["ranges"] = layer_ranges(inst["features"])
        record["ranges"] = obj["ranges"]
        records.append(record)

    pauses = [dict(r["pause"], object=r["name"], identify_id=r["identify_id"]) for r in records if "pause" in r]
    if len({round(p["threshold_print_z_mm"], 4) for p in pauses}) > 1:
        raise ValueError(f"{name}: a plate pauses once; its parts ask for {[p['threshold_print_z_mm'] for p in pauses]}")
    sources = sorted({r["stl_sha256"] for r in records})
    stamp = datetime.datetime.now().strftime("%Y-%m-%d")
    stem = f"{stamp}-{name}-{printer.lower()}-{hashlib.sha256(''.join(sources).encode()).hexdigest()[:8]}"
    # Absolute, because the slicer runs inside the preparation directory.
    directory = Path(output or OUTPUT).resolve() / stem
    if directory.exists():
        raise FileExistsError(f"{relative(directory)} exists; a preparation directory is written once")
    directory.mkdir(parents=True)
    project = directory / f"{stem}.3mf"
    plate.write(project)
    painted = []
    for inst, record in zip(instances, records):
        index = sorted({int(i) for f in inst["features"] for i in f.get("paint_faces", [])})
        rotation = np.array(record["build_rotation"])
        triangles = (inst["mesh"].vertices[inst["mesh"].faces[index]] - inst["mesh"].center) @ rotation.T + record["translation_mm"]
        painted.append(triangles)
    np.savez_compressed(directory / "show-faces.npz", **{str(r["identify_id"]): t for r, t in zip(records, painted)})
    preparation = {
        "piece": name, "printer": printer, "connection_key": machine.get("connection_key", printer),
        "nozzle": nozzle, "material": piece["material"], "bed_type": settings["curr_bed_type"],
        "requested_z_trim_mm": z_trim,
        # Bambu's Textured PEI compensation emits 0.02 mm under the request; other plates emit it.
        "emitted_textured_trim_mm": round(z_trim - (0.02 if settings["curr_bed_type"] == "Textured PEI Plate" else 0.0), 3),
        "project": relative(project), "project_sha256": _mesh.sha256(project),
        "profile": relative(profile_path), "profile_sha256": _mesh.sha256(profile_path),
        "settings_sha256": hashlib.sha256((json.dumps(settings, indent=2) + "\n").encode()).hexdigest(),
        "settings_changes": changes, "profile_changes": profile["changes"],
        "usable_plate_mm": [usable_low.tolist(), usable_high.tolist()], "plate_border_mm": border,
        "brim_allowance_mm": brim, "plate_offset_mm": piece.get("plate_offset_mm"), "objects": records,
        "pause": pauses[0] if pauses else None,
        "show_faces": relative(directory / "show-faces.npz"),
        "spec": relative(SPEC_PATH), "spec_sha256": _mesh.sha256(SPEC_PATH),
        "tool_sha256": {relative(p): _mesh.sha256(p) for p in sorted(HERE.glob("*.py"))},
        "prepared_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "sliced": False, "submitted": False}
    save(directory / "preparation.json", preparation)
    print(relative(project), flush=True)
    for record in records:
        print(f"  {record['name']}: yaw {record['yaw_degrees']}, model margin {record['model_bed_margin_mm']:.1f} mm, "
              f"ranges {[(round(r['min_z'], 2), round(r['max_z'], 2), r['options']) for r in record['ranges']]}, "
              f"ribbons {len(record['ribbons'])}, tie windows {len(record['tie_windows'])}, modifiers {len(record['modifiers'])}",
              flush=True)
    return directory


def _studio(project: Path, native: Path, archive_name: str) -> tuple[list, dict]:
    native.mkdir()
    command = [str(STUDIO), "--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir", str(native),
               "--export-3mf", archive_name, str(project)]
    with (native / "slice.log").open("w") as log:
        result = subprocess.run(command, cwd=native, stdout=log, stderr=subprocess.STDOUT,
                                env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    if result.returncode:
        raise RuntimeError(f"Bambu Studio exited {result.returncode}; see {relative(native / 'slice.log')}")
    sliced = json.loads((native / "result.json").read_text())
    if sliced.get("return_code") != 0:
        raise RuntimeError(f"Bambu Studio reported {sliced.get('error_string')}")
    return command, sliced


def gcode_layers(archive: Path) -> list[tuple[float, float]]:
    """Each emitted layer's top Z and height, in order."""
    with zipfile.ZipFile(archive) as z:
        text = z.read("Metadata/plate_1.gcode").decode("utf-8", "replace")
    out = []
    for line in text.splitlines():
        if line.startswith("; Z_HEIGHT:"):
            out.append([float(line.split(":", 1)[1]), None])
        elif line.startswith("; LAYER_HEIGHT:") and out and out[-1][1] is None:
            out[-1][1] = float(line.split(":", 1)[1])
    return [(z, h) for z, h in out]


def pause_layer(layers: list[tuple[float, float]], pause: dict) -> dict:
    """The first layer sliced above the slots' roof opens with the pause; its bottom clears the stack."""
    threshold = pause["threshold_print_z_mm"]
    for index, (z, h) in enumerate(layers):
        if z - h / 2.0 > threshold + 1e-6:
            bottom = z - h
            if bottom < pause["stack_top_print_z_mm"] - 1e-6:
                raise ValueError(f"the layer that closes the slots starts at print Z{bottom:.3f}, under the "
                                 f"loaded stack's top at Z{pause['stack_top_print_z_mm']:.4f}")
            return {"top_z_mm": z, "height_mm": h, "bottom_z_mm": round(bottom, 6), "index": index,
                    "previous_top_z_mm": layers[index - 1][0] if index else None,
                    "air_over_stack_mm": round(bottom - pause["stack_top_print_z_mm"], 4)}
    raise ValueError(f"no layer is sliced above print Z{threshold:.4f}")


def write_pause(project: Path, top_z: float, pause: dict) -> None:
    root = ET.Element("custom_gcodes_per_layer")
    plate = ET.SubElement(root, "plate")
    ET.SubElement(plate, "plate_info", id="1")
    ET.SubElement(plate, "layer", top_z=f"{top_z:.3f}", type="1", extruder="1", color="",
                  extra=pause["message"], gcode=pause["gcode"])
    ET.SubElement(plate, "mode", value="SingleExtruder")
    member = "Metadata/custom_gcode_per_layer.xml"
    temporary = project.with_suffix(".pause.tmp")
    with zipfile.ZipFile(project) as source, zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as target:
        for item in source.infolist():
            if item.filename != member:
                target.writestr(item, source.read(item.filename))
        target.writestr(member, ET.tostring(root, xml_declaration=True, encoding="UTF-8"))
    os.replace(temporary, project)


def slice_project(directory: Path) -> Path:
    preparation = json.loads((directory / "preparation.json").read_text())
    project = ROOT / preparation["project"]
    if _mesh.sha256(project) != preparation["project_sha256"]:
        raise ValueError("the project changed after preparation")
    archive_name = project.name.replace(".3mf", ".gcode.3mf")
    pause = preparation.get("pause")
    if pause:
        # Slice once to read the layers the slicer emits, put the pause on the layer that closes
        # the slots, then slice the paused project.
        probe = directory / "native-probe"
        _studio(project, probe, archive_name)
        pause["layer"] = pause_layer(gcode_layers(probe / archive_name), pause)
        write_pause(project, pause["layer"]["top_z_mm"], pause)
        preparation.update(project_sha256=_mesh.sha256(project), pause=pause)
        save(directory / "preparation.json", preparation)
    native = directory / "native"
    command, sliced = _studio(project, native, archive_name)
    save(directory / "slice-command.json", command)
    archive = directory / archive_name
    shutil.copyfile(native / archive_name, archive)
    with zipfile.ZipFile(archive) as z:
        if z.testzip() is not None:
            raise ValueError("the sliced archive has a damaged member")
        gcode = z.read("Metadata/plate_1.gcode")
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("the embedded G-code does not match its MD5")
    save(directory / "slice-result.json", sliced)
    preparation.update(sliced=True, archive=relative(archive), archive_sha256=_mesh.sha256(archive),
                       gcode_sha256=hashlib.sha256(gcode).hexdigest(),
                       estimated_seconds=sum(p.get("total_predication", 0) for p in sliced.get("sliced_plates", [])),
                       slicer_warnings=[p.get("warning_message") for p in sliced.get("sliced_plates", []) if p.get("warning_message")])
    save(directory / "preparation.json", preparation)
    print(relative(archive), flush=True)
    return archive


def check_archive(piece: dict) -> str:
    """A piece that prints from a retained processed archive: its bytes against the recorded digest."""
    path = ROOT / piece["archive"]["path"]
    if not path.is_file():
        return "missing"
    return "bound" if _mesh.sha256(path) == piece["archive"]["sha256"] else "CHANGED"


def run_external(name: str, piece: dict) -> None:
    command = [str(ROOT / "tools/cad-venv/bin/python"), *[str(ROOT / c) if c.endswith(".py") else c
                                                          for c in piece["external"]["command"]]]
    print(" ".join(command), flush=True)
    subprocess.run(command, cwd=ROOT, check=True)


def listing() -> None:
    spec = json.loads(SPEC_PATH.read_text())
    regions = json.loads((ROOT / spec["regions"]).read_text())["native_artifact_sha256"]
    for name, piece in spec["pieces"].items():
        nozzle = piece.get("nozzle", {})
        head = (f"{name:22s} {piece['printer']:6s} {nozzle.get('side', '-'):5s} {nozzle.get('diameter_mm', 0):g} mm "
                f"{nozzle.get('flow', '')}, {piece.get('material', '-')}")
        if "external" in piece:
            print(f"{head}\n    external: {' '.join(piece['external']['command'])}")
            continue
        if "archive" in piece:
            print(f"{head}\n    archive: {piece['archive']['path']}  {check_archive(piece)}")
            continue
        print(head)
        for part in piece["parts"]:
            path = ROOT / part["stl"]
            state = "missing" if not path.is_file() else _mesh.sha256(path)[:12]
            binding = ""
            if part.get("regions") and path.is_file():
                bound = regions.get(part["regions"], {}).get(".stl")
                binding = "regions bound" if bound == _mesh.sha256(path) else "regions stale"
            print(f"    {part.get('quantity', 1)} x {part['stl']}  {state}  {binding}")


def main() -> None:
    spec = json.loads(SPEC_PATH.read_text())
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("piece", choices=["list", "all", *spec["pieces"]])
    parser.add_argument("--printer", choices=sorted(spec["printers"]))
    parser.add_argument("--part", action="append", help="STL[,quantity=N][,turns=x:90][,walls=N][,infill=N][,name=...]; replaces the piece's declared parts")
    parser.add_argument("--slice", action="store_true", help="slice with the installed Bambu Studio command line")
    parser.add_argument("--review", action="store_true", help="read the sliced archive (review.py)")
    parser.add_argument("--output", type=Path, help=f"directory for preparations (default {relative(OUTPUT)})")
    parser.add_argument("--border", type=float, help="bed border in mm for the footprint precheck")
    args = parser.parse_args()
    if args.piece == "list":
        listing()
        return
    names = list(spec["pieces"]) if args.piece == "all" else [args.piece]
    if args.part and len(names) > 1:
        parser.error("--part names one plate's parts")
    failed = {}
    for name in names:
        piece = spec["pieces"][name]
        try:
            if "archive" in piece:
                state = check_archive(piece)
                print(f"{name}: prints from {piece['archive']['path']} ({state}); nothing to prepare", flush=True)
                if state != "bound":
                    raise ValueError(f"the archive is {state}")
                continue
            if "external" in piece:
                # The label preparer slices each plate it writes.
                if args.slice or args.piece == name:
                    run_external(name, piece)
                else:
                    print(f"{name}: prepared and sliced by {' '.join(piece['external']['command'])} (--slice runs it)", flush=True)
                continue
            parts = [parse_part(p) for p in args.part] if args.part else None
            directory = prepare(name, args.printer, parts, args.output, args.border)
            import review
            if args.slice:
                slice_project(directory)
                if args.review:
                    review.review(directory)
            elif args.review:
                result = review.check_project(directory)
                print(f"  project read back: {'pass' if result['pass'] else result['problems']}", flush=True)
        except Exception as error:  # one piece's failure does not stop the others
            if len(names) == 1:
                raise
            failed[name] = f"{type(error).__name__}: {error}"
            print(f"{name}: {failed[name]}", flush=True)
    if "cadquery" in sys.modules:
        raise RuntimeError("a CAD kernel was imported during print preparation")
    if failed:
        raise SystemExit(f"{len(failed)} piece(s) not prepared: {', '.join(failed)}")


if __name__ == "__main__":
    main()
