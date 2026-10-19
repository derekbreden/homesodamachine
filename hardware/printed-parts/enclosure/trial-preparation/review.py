#!/usr/bin/env python3
"""Read a trial preparation's project and sliced archive against its preparation record.

    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/review.py <preparation directory>
    tools/cad-venv/bin/python hardware/printed-parts/enclosure/trial-preparation/review.py <directory> --project-only

`check_project` reads the written project back: embedded meshes against their STLs,
part and modifier counts, painted facets and layer ranges. `review` reads the emitted
G-code: archive integrity and Z trim, fine-layer coverage of each measured round span
(`hardware/scripts/verify_round_layer_band.py`), layer heights through each transition
band, the complete bead envelope against the bed border, support beads near the painted
show faces, support inside tie-channel windows and groove ribbons, ribbon deposition,
sampled deposition in the solid-host modifiers, unbacked roads in the fine bands, the
first-to-second layer bead stack, and each object's support topology
(`hardware/scripts/enclosure_support_audit.py`). Removal lanes for the reported support
bodies remain a reading of their positions against the part.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(HERE), str(ROOT / "hardware/scripts")]
import _mesh  # noqa: E402
import _native  # noqa: E402

WORD = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
SUPPORT = {"Support", "Support interface", "Support transition"}
MODEL = {"Outer wall", "Inner wall", "Overhang wall", "Bottom surface", "Top surface",
         "Internal solid infill", "Sparse infill", "Bridge", "Gap infill", "Internal Bridge",
         "Floating vertical shell"}
WALLS = {"Outer wall", "Inner wall", "Overhang wall"}


def save(path: Path, value) -> None:
    path.write_text(json.dumps(value, indent=2, default=lambda v: v.tolist() if hasattr(v, "tolist") else str(v)) + "\n")


def _arc(x0, y0, x1, y1, words, clockwise, chord=0.25):
    cx, cy = x0 + words.get("I", 0.0), y0 + words.get("J", 0.0)
    r = math.hypot(x0 - cx, y0 - cy)
    a0 = math.atan2(y0 - cy, x0 - cx)
    sweep = math.atan2(y1 - cy, x1 - cx) - a0
    if clockwise:
        sweep = sweep if sweep < -1e-9 else sweep - 2 * math.pi
    else:
        sweep = sweep if sweep > 1e-9 else sweep + 2 * math.pi
    n = max(1, math.ceil(abs(sweep) * r / chord))
    points = [(cx + r * math.cos(a0 + sweep * i / n), cy + r * math.sin(a0 + sweep * i / n)) for i in range(n + 1)]
    points[-1] = (x1, y1)
    return points


def layers(lines):
    """Per layer: (z, height, roads); a road is (x0, y0, x1, y1, width, feature, object)."""
    x = y = e = 0.0
    width, height, feature, obj = 0.42, 0.24, "", None
    z, roads = None, []
    absolute, relative_e = True, True
    for raw in lines:
        line = raw.decode("utf-8", "replace").strip() if isinstance(raw, bytes) else raw.strip()
        if line.startswith(";"):
            text = line[1:].strip()
            if text.startswith("Z_HEIGHT:"):
                if z is not None:
                    yield z, height, roads
                z, roads = float(text.split(":", 1)[1]), []
            elif text.startswith("LAYER_HEIGHT:"):
                height = float(text.split(":", 1)[1])
            elif text.startswith("FEATURE:"):
                feature = text.split(":", 1)[1].strip()
            elif text.startswith("LINE_WIDTH:"):
                width = float(text.split(":", 1)[1])
            elif text.startswith("OBJECT_ID:"):
                obj = int(text.split(":", 1)[1])
            elif text.startswith("start printing object, unique label id:"):
                obj = int(text.rsplit(":", 1)[1])
            elif text.startswith("stop printing object"):
                obj = None
            continue
        code = line.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split(None, 1)[0]
        if command in ("G90", "G91"):
            absolute = command == "G90"
            continue
        if command in ("M82", "M83"):
            relative_e = command == "M83"
            continue
        if command not in ("G0", "G1", "G2", "G3", "G92"):
            continue
        words = {k: float(v) for k, v in WORD.findall(code[len(command):])}
        if command == "G92":
            x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
            continue
        nx = words.get("X", x) if absolute else x + words.get("X", 0.0)
        ny = words.get("Y", y) if absolute else y + words.get("Y", 0.0)
        de = (words.get("E", 0.0) if relative_e else words.get("E", e) - e) if "E" in words else 0.0
        if "E" in words:
            e = e + words["E"] if relative_e else words["E"]
        if z is not None and de > 1e-9 and (nx != x or ny != y):
            if command in ("G2", "G3"):
                points = _arc(x, y, nx, ny, words, command == "G2")
                roads.extend((a[0], a[1], b[0], b[1], width, feature, obj) for a, b in zip(points, points[1:]))
            else:
                roads.append((x, y, nx, ny, width, feature, obj))
        x, y = nx, ny
    if z is not None:
        yield z, height, roads


def gcode_lines(archive: Path):
    handle = zipfile.ZipFile(archive)
    return handle, handle.open("Metadata/plate_1.gcode")


def _point_triangle_distance(points, a, b, c):
    """Distances (P, T) from points to triangles."""
    p = points[:, None, :]
    ab, ac, ap = b - a, c - a, p - a
    d1, d2 = (ab * ap).sum(-1), (ac * ap).sum(-1)
    bp = p - b
    d3, d4 = (ab * bp).sum(-1), (ac * bp).sum(-1)
    cp = p - c
    d5, d6 = (ab * cp).sum(-1), (ac * cp).sum(-1)
    va = d3 * d6 - d5 * d4
    vb = d5 * d2 - d1 * d6
    vc = d1 * d4 - d3 * d2
    denom = np.where(np.abs(va + vb + vc) > 1e-18, va + vb + vc, 1e-18)
    v, w = vb / denom, vc / denom
    closest = a + v[..., None] * ab + w[..., None] * ac
    # Region tests, falling back to the nearest point on each edge.
    def segment(s, t):
        d = t - s
        u = np.clip(((p - s) * d).sum(-1) / np.maximum((d * d).sum(-1), 1e-18), 0, 1)
        return s + u[..., None] * d
    inside = (va >= 0) & (vb >= 0) & (vc >= 0)
    candidates = [segment(a, b), segment(b, c), segment(c, a)]
    edge = np.min(np.stack([np.linalg.norm(p - q, axis=-1) for q in candidates]), axis=0)
    face = np.linalg.norm(p - closest, axis=-1)
    return np.where(inside, face, edge)


def check_project(directory: Path) -> dict:
    """Read the written project back against its preparation record and source STLs."""
    preparation = json.loads((directory / "preparation.json").read_text())
    project = ROOT / preparation["project"]
    result = {"project_sha256_matches": _mesh.sha256(project) == preparation["project_sha256"], "objects": []}
    with zipfile.ZipFile(project) as archive:
        if archive.testzip() is not None:
            raise ValueError("the project has a damaged member")
        model = ET.fromstring(archive.read("3D/3dmodel.model"))
        config = ET.fromstring(archive.read("Metadata/model_settings.config"))
        ranges = ET.fromstring(archive.read("Metadata/layer_config_ranges.xml")
                               if "Metadata/layer_config_ranges.xml" in archive.namelist() else b"<objects/>")
        settings = json.loads(archive.read(_native.SETTINGS_MEMBER))
        ns = f"{{{_native.CORE}}}"
        items = {item.get("objectid"): item for item in model.find(f"{ns}build")}
        for order, record in enumerate(preparation["objects"], 1):
            owner = model.find(f"{ns}resources/{ns}object[@id='{record['object_id']}']")
            components = owner.find(f"{ns}components")
            main = components[0]
            member = main.get(f"{{{_native.PROD}}}path").lstrip("/")
            text = archive.read(member).decode()
            vertices = np.array(re.findall(r'<vertex x="([^"]+)" y="([^"]+)" z="([^"]+)"', text), dtype=float)
            painted = len(re.findall(r'paint_supports="8"', text))
            coded = len(re.findall(r'paint_supports="[0-9A-F]{2,}"', text))
            transform = np.array([float(v) for v in items[str(record["object_id"])].get("transform").split()])
            placed = vertices @ transform[:9].reshape(3, 3) + transform[9:]
            source = _mesh.read_stl(ROOT / record["stl"])
            source_vertices, _ = _mesh.merge(source)
            expected = (source_vertices - record["source_center_mm"]) @ np.array(record["build_rotation"]).T + record["translation_mm"]
            obj_config = config.find(f"object[@id='{record['object_id']}']")
            subtypes = defaultdict(int)
            for part in obj_config.findall("part"):
                subtypes[part.get("subtype")] += 1
            band_element = ranges.find(f"object[@id='{order}']")
            written = [(float(r.get("min_z")), float(r.get("max_z")), {o.get("opt_key"): o.text for o in r})
                       for r in (band_element.findall("range") if band_element is not None else [])]
            result["objects"].append({
                "name": record["name"], "vertices": len(vertices),
                "source_sha256_matches": _mesh.sha256(ROOT / record["stl"]) == record["stl_sha256"],
                "embedded_vertex_error_mm": float(np.abs(placed - expected).max()) if placed.shape == expected.shape else float("inf"),
                "placed_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
                "bed_contact_z_mm": float(placed[:, 2].min()),
                "blocked_facets": painted, "partially_painted_facets": coded, "parts": dict(subtypes),
                "layer_ranges": written,
                "ribbon_and_fin_parts": subtypes.get("normal_part", 1) - 1,
                "modifiers_expected": len(record["modifiers"]),
            })
    result["z_trim_block"] = re.findall(r"G29\.1 Z\{([^}]+)\}", settings["machine_start_gcode"])
    result["cooling"] = {k: settings.get(k) for k in ("fan_min_speed", "fan_max_speed", "overhang_fan_speed",
                                                      "overhang_fan_threshold", "additional_cooling_fan_speed")}
    result["support"] = {k: settings.get(k) for k in ("support_type", "support_style", "support_object_xy_distance",
                                                      "max_bridge_length", "tree_support_branch_diameter",
                                                      "tree_support_branch_diameter_angle", "brim_type")}
    problems = []
    for row in result["objects"]:
        if not row["source_sha256_matches"]:
            problems.append(f"{row['name']}: the STL changed after preparation")
        if row["embedded_vertex_error_mm"] > 1e-4:
            problems.append(f"{row['name']}: embedded vertices differ from the STL by {row['embedded_vertex_error_mm']:.2e} mm")
        if abs(row["bed_contact_z_mm"]) > 1e-4:
            problems.append(f"{row['name']}: the lowest vertex is at Z{row['bed_contact_z_mm']:.4f}")
        if row["parts"].get("modifier_part", 0) != row["modifiers_expected"]:
            problems.append(f"{row['name']}: {row['parts'].get('modifier_part', 0)} modifiers for {row['modifiers_expected']} declared")
    result["problems"] = problems
    result["pass"] = result["project_sha256_matches"] and not problems
    save(directory / "project-check.json", result)
    return result


def _filtered_gcode(archive: Path, identify_id: int, output: Path) -> Path:
    """The plate G-code with other objects' feature labels masked, for one object's support audit."""
    handle, stream = gcode_lines(archive)
    current = None
    with stream, output.open("w") as target:
        for raw in stream:
            line = raw.decode("utf-8", "replace")
            text = line.strip()
            if text.startswith("; OBJECT_ID:"):
                current = int(text.split(":", 1)[1])
            elif text.startswith("; start printing object, unique label id:"):
                current = int(text.rsplit(":", 1)[1])
            elif text.startswith("; stop printing object"):
                current = None
            if text.startswith("; FEATURE:") and current != identify_id:
                target.write("; FEATURE: Other object\n")
            else:
                target.write(line)
    handle.close()
    return output


def review(directory: Path, audit: bool = True) -> dict:
    directory = Path(directory)
    preparation = json.loads((directory / "preparation.json").read_text())
    archive = ROOT / preparation["archive"]
    if _mesh.sha256(archive) != preparation["archive_sha256"]:
        raise ValueError("the sliced archive changed after slicing")
    project_check = check_project(directory)
    with zipfile.ZipFile(archive) as z:
        gcode = z.read("Metadata/plate_1.gcode")
        integrity = hashlib.md5(gcode).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        text_head = gcode[:400000].decode("utf-8", "replace")
        del gcode
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text_head, re.M)]
    objects = {r["identify_id"]: r for r in preparation["objects"]}
    border = preparation["plate_border_mm"]
    low_area, high_area = (np.array(v) for v in preparation["usable_plate_mm"])
    show = np.load(ROOT / preparation["show_faces"])
    show_faces = {int(k): show[k] for k in show.files}
    # Grid index of painted faces, 4 mm cells in plate XY.
    grid = {}
    for oid, triangles in show_faces.items():
        for index, t in enumerate(triangles):
            lo, hi = np.floor(t[:, :2].min(axis=0) / 4).astype(int), np.floor(t[:, :2].max(axis=0) / 4).astype(int)
            for gx in range(lo[0], hi[0] + 1):
                for gy in range(lo[1], hi[1] + 1):
                    grid.setdefault((gx, gy), []).append((oid, index))
    windows = [(oid, w) for oid, r in objects.items() for w in r["tie_windows"]]
    ribbons = [(oid, rb) for oid, r in objects.items() for rb in r["ribbons"]]
    fine = [(oid, s) for oid, r in objects.items() for s in r["verify_spans"]]
    stats = {"layers": 0, "bead_low": np.full(2, np.inf), "bead_high": np.full(2, -np.inf),
             "support_roads": 0, "show_min_clearance": None, "show_contacts": [],
             "window_crossings": [], "ribbon_support": [], "ribbon_layers": defaultdict(set),
             "unbacked": defaultdict(lambda: {"roads": 0, "unbacked_mm": 0.0, "longest_mm": 0.0, "bridge_mm": 0.0, "layers": 0}),
             "stack": {}}
    previous = None
    first_two = {}
    from shapely import buffer, union_all
    from shapely.geometry import LineString, box as shapely_box

    def needs_beads(z, height, count):
        mid = z - height / 2
        return count <= 2 or any(s["print_z_mm"][0] - 0.5 <= mid <= s["print_z_mm"][1] + 0.08 for _, s in fine)

    handle, stream = gcode_lines(archive)
    with stream:
        for z, height, roads in layers(stream):
            stats["layers"] += 1
            if not roads:
                previous = None
                continue
            r = np.array([road[:5] for road in roads])
            features = [road[5] for road in roads]
            owners = [road[6] for road in roads]
            ends = np.concatenate([r[:, [0, 1]], r[:, [2, 3]]])
            reach = float(r[:, 4].max()) / 2
            stats["bead_low"] = np.minimum(stats["bead_low"], ends.min(axis=0) - reach)
            stats["bead_high"] = np.maximum(stats["bead_high"], ends.max(axis=0) + reach)
            support = np.array([f in SUPPORT for f in features])
            model = np.array([f in MODEL for f in features])
            stats["support_roads"] += int(support.sum())
            for index in np.flatnonzero(support):
                x0, y0, x1, y1, width = r[index]
                radius = math.hypot(width, height) / 2
                cells = set()
                for gx in range(int(math.floor(min(x0, x1) / 4)), int(math.floor(max(x0, x1) / 4)) + 1):
                    for gy in range(int(math.floor(min(y0, y1) / 4)), int(math.floor(max(y0, y1) / 4)) + 1):
                        cells.update(grid.get((gx, gy), ()))
                if cells:
                    tri = np.array([show_faces[o][i] for o, i in sorted(cells)])
                    near = (tri[:, :, 2].min(axis=1) <= z + radius) & (tri[:, :, 2].max(axis=1) >= z - height - radius)
                    if near.any():
                        length = math.hypot(x1 - x0, y1 - y0)
                        t = np.linspace(0, 1, max(2, int(length / 0.2) + 1))
                        points = np.stack([x0 + (x1 - x0) * t, y0 + (y1 - y0) * t, np.full(len(t), z - height / 2)], axis=1)
                        tri = tri[near]
                        clearance = float(_point_triangle_distance(points, tri[:, 0], tri[:, 1], tri[:, 2]).min() - radius)
                        if stats["show_min_clearance"] is None or clearance < stats["show_min_clearance"]:
                            stats["show_min_clearance"] = clearance
                        if clearance <= 0 and len(stats["show_contacts"]) < 200:
                            stats["show_contacts"].append({"z_mm": z, "road": r[index].tolist(),
                                                           "feature": features[index], "bead_clearance_mm": clearance})
                if windows or ribbons:
                    bead = LineString([(x0, y0), (x1, y1)]).buffer(width / 2, quad_segs=2)
                for oid, window in windows:
                    (bx0, by0, bz0), (bx1, by1, bz1) = window["box_plate_mm"]
                    if z - height < bz1 - 0.02 and z > bz0 + 0.02 and bead.intersects(
                            shapely_box(bx0 + 0.02, by0 + 0.02, bx1 - 0.02, by1 - 0.02)):
                        stats["window_crossings"].append({"object": oid, "z_mm": z, "window": window["box_plate_mm"],
                                                          "road": r[index].tolist(), "feature": features[index]})
                for oid, ribbon in ribbons:
                    (bx0, by0, bz0), (bx1, by1, bz1) = ribbon["box_plate_mm"]
                    if z - height < bz1 + 0.5 and z > bz0 - 0.3 and bead.intersects(shapely_box(bx0, by0, bx1, by1)):
                        stats["ribbon_support"].append({"object": oid, "ribbon": ribbon["number"], "z_mm": z,
                                                        "road": r[index].tolist(), "feature": features[index]})
            if ribbons:
                mids = (r[:, [0, 1]] + r[:, [2, 3]]) / 2
                for oid, ribbon in ribbons:
                    (bx0, by0, bz0), (bx1, by1, bz1) = ribbon["box_plate_mm"]
                    if bz0 <= z - height / 2 <= bz1:
                        inside = (model & (mids[:, 0] > bx0) & (mids[:, 0] < bx1) & (mids[:, 1] > by0) & (mids[:, 1] < by1))
                        if inside.any():
                            stats["ribbon_layers"][(oid, ribbon["number"])].add(round(z, 3))
            if not needs_beads(z, height, stats["layers"]):
                previous = None
                continue
            lines = np.array([LineString([(a, b), (c, d)]) for a, b, c, d, _ in r], dtype=object)
            beads = buffer(lines, r[:, 4] / 2, quad_segs=4)
            if stats["layers"] <= 2:
                for oid in objects:
                    own = np.array([o == oid for o in owners])
                    first_two.setdefault(oid, []).append((union_all(beads[own]) if own.any() else None,
                                                          lines[own & model], r[own & model, 4]))
            for oid, span in fine:
                if previous is None or not (span["print_z_mm"][0] <= z - height / 2 <= span["print_z_mm"][1] + 0.08):
                    continue
                own = np.array([o == oid for o in owners]) & model
                if not own.any():
                    continue
                entry = stats["unbacked"][(oid, span["name"])]
                entry["layers"] += 1
                for line, feature in zip(lines[own], [f for f, keep in zip(features, own) if keep]):
                    free = line.difference(previous)
                    entry["roads"] += 1
                    if free.length > 1e-6:
                        if feature == "Bridge":
                            entry["bridge_mm"] += free.length
                        else:
                            entry["unbacked_mm"] += free.length
                            entry["longest_mm"] = max(entry["longest_mm"], max(g.length for g in getattr(free, "geoms", [free])))
            previous = union_all(beads)
    handle.close()
    margins = {"left": float(stats["bead_low"][0] - low_area[0]), "front": float(stats["bead_low"][1] - low_area[1]),
               "right": float(high_area[0] - stats["bead_high"][0]), "back": float(high_area[1] - stats["bead_high"][1])}
    stack = {}
    for oid, rows in first_two.items():
        if len(rows) < 2 or rows[0][0] is None or not len(rows[1][1]):
            continue
        first_union = rows[0][0]
        second = buffer(rows[1][1], rows[1][2] / 2, quad_segs=4)
        second_union = union_all(second)
        stack[oid] = {"second_layer_model_bead_area_mm2": second_union.area,
                      "fraction_over_first_layer": second_union.intersection(first_union).area / second_union.area,
                      "second_layer_centerline_outside_first_mm": sum(l.difference(first_union).length for l in rows[1][1])}
    band_results = []
    import verify_round_layer_band as bands
    for oid, record in objects.items():
        walls = bands.wall_layers(archive, oid)
        for span in record["verify_spans"]:
            band_results.append({"object": oid, **bands.check_span(walls, span["name"], span["print_z_mm"][0], span["print_z_mm"][1],
                                                                   span["layer_height_mm"], 0.001)})
        for rng in record["ranges"]:
            if "wall_loops" in rng["options"]:
                heights = sorted({h for zz, h in walls if rng["min_z"] < zz <= rng["max_z"]})
                band_results.append({"object": oid, "name": rng["feature"], "transition_band_mm": [rng["min_z"], rng["max_z"]],
                                     "emitted_wall_layer_heights_mm": heights,
                                     "pass": all(abs(h - 0.24) < 0.001 or abs(zz - 0.2) < 0.001 for zz, h in walls if rng["min_z"] < zz <= rng["max_z"])})
    dense = dense_regions(directory, preparation, archive)
    audits = {}
    if audit:
        import enclosure_support_audit
        for oid, record in objects.items():
            filtered = _filtered_gcode(archive, oid, directory / f"support-labels-{oid}.gcode")
            coordinates = _native.coordinates_project(ROOT / preparation["project"], record["object_id"], directory / f"coordinates-{oid}.3mf")
            reading = enclosure_support_audit.audit(filtered, record["name"], ROOT / record["stl"], ROOT / preparation["project"],
                                                    coordinates, profile_label=preparation["project"], include_unlabelled_support=True)
            save(directory / f"support-audit-{oid}.json", reading)
            audits[oid] = reading["summary"]
            filtered.unlink()
    ribbon_rows = []
    for oid, rb in ribbons:
        seen = sorted(stats["ribbon_layers"][(oid, rb["number"])])
        ribbon_rows.append({"object": oid, "ribbon": rb["number"], "layers_with_ribbon_roads": len(seen),
                            "declared_layers": rb["layers"][1] - rb["layers"][0] + 1,
                            "first_z_mm": seen[0] if seen else None, "last_z_mm": seen[-1] if seen else None})
    result = {
        "archive": preparation["archive"], "archive_sha256": preparation["archive_sha256"],
        "gcode_md5_matches": integrity, "emitted_z_trim_mm": trims,
        "expected_emitted_textured_trim_mm": preparation["emitted_textured_trim_mm"],
        "layers": stats["layers"], "project_check": project_check["pass"],
        "bead_envelope_plate_mm": [stats["bead_low"].tolist(), stats["bead_high"].tolist()],
        "bed_margins_mm": margins, "minimum_bed_margin_mm": min(margins.values()), "bed_border_mm": border,
        "fine_and_transition_bands": band_results,
        "support_roads": stats["support_roads"],
        "show_face_minimum_bead_clearance_mm": stats["show_min_clearance"],
        "show_face_contacts": stats["show_contacts"],
        "tie_window_support_crossings": stats["window_crossings"][:200],
        "ribbon_support_crossings": stats["ribbon_support"][:200],
        "ribbons": ribbon_rows,
        "fine_band_unbacked_roads": [{"object": k[0], "band": k[1], **v} for k, v in stats["unbacked"].items()],
        "first_second_layer_stack": stack,
        "solid_host_deposition": dense,
        "support_topology": audits,
        "scope": "Commanded paths and bead envelopes from this archive. Support removal, surface finish, fit and strength are physical observations.",
    }
    checks = {
        "archive": integrity and project_check["pass"],
        "z_trim": len(trims) >= 1 and abs(trims[-1] - preparation["emitted_textured_trim_mm"]) < 0.005,
        "bed_border": result["minimum_bed_margin_mm"] >= border,
        "fine_and_transition_bands": all(row["pass"] for row in band_results),
        "show_faces_support_free": not stats["show_contacts"],
        "tie_windows_support_free": not stats["window_crossings"],
        "ribbons_support_free_and_printed": not stats["ribbon_support"] and all(
            row["layers_with_ribbon_roads"] >= row["declared_layers"] - 1 for row in ribbon_rows),
        "solid_hosts_sampled": all(row["minimum_coverage"] is None or row["minimum_coverage"] >= 0.9 for row in dense),
    }
    result["checks"] = checks
    result["pass"] = all(checks.values())
    save(directory / "review.json", result)
    print(json.dumps({"checks": checks, "minimum_bed_margin_mm": result["minimum_bed_margin_mm"],
                      "support_topology": audits}, indent=2), flush=True)
    return result


def dense_regions(directory: Path, preparation: dict, archive: Path) -> list[dict]:
    """Sampled bead coverage of the model's own section inside each solid-host modifier."""
    from shapely import STRtree, buffer, union_all
    from shapely.geometry import LineString, box as shapely_box
    wanted = defaultdict(list)
    rows = []
    meshes = {}
    for record in preparation["objects"]:
        if not record["modifiers"]:
            continue
        source = _mesh.read_stl(ROOT / record["stl"]).astype(np.float64)
        placed = (source.reshape(-1, 3) - record["source_center_mm"]) @ np.array(record["build_rotation"]).T + record["translation_mm"]
        meshes[record["identify_id"]] = placed.reshape(-1, 3, 3)
        for modifier in record["modifiers"]:
            (x0, y0, z0), (x1, y1, z1) = modifier["plate_bounds_mm"]
            samples = sorted({round(z0 + 0.36, 3), round((z0 + z1) / 2, 3), round(z1 - 0.36, 3)})
            row = {"object": record["identify_id"], "name": modifier["name"], "plate_bounds_mm": modifier["plate_bounds_mm"],
                   "samples": [], "minimum_coverage": None}
            rows.append(row)
            for z in samples:
                if z0 < z < z1:
                    wanted[round(z, 3)].append(row)
    if not rows:
        return []
    handle, stream = gcode_lines(archive)
    with stream:
        for z, height, roads in layers(stream):
            mid = z - height / 2
            hits = [t for t in list(wanted) if mid - height / 2 < t <= mid + height / 2]
            if not hits:
                continue
            # Tree supports print on their own layer heights between the objects' layers; a sample
            # waits for a layer on which its object prints.
            printed = {o for *_, f, o in roads if f in MODEL}
            sections = {}
            for target in hits:
                waiting = []
                for row in wanted.pop(target):
                    oid = row["object"]
                    if oid not in printed:
                        waiting.append(row)
                        continue
                    (x0, y0, _), (x1, y1, _) = row["plate_bounds_mm"]
                    if oid not in sections:
                        sections[oid] = _mesh.section_polygons(meshes[oid], mid)
                    stock = sections[oid].intersection(shapely_box(x0, y0, x1, y1))
                    if stock.area <= 0.05:
                        continue
                    own = [(a, b, c, d, w) for a, b, c, d, w, f, o in roads if o == oid and f in MODEL]
                    lines = np.array([LineString([(a, b), (c, d)]) for a, b, c, d, _ in own], dtype=object)
                    widths = np.array([w for *_, w in own])
                    tree = STRtree(lines)
                    index = tree.query(stock, predicate="dwithin", distance=float(widths.max() / 2))
                    beads = union_all(buffer(lines[index], widths[index] / 2, quad_segs=4)) if len(index) else None
                    coverage = stock.intersection(beads).area / stock.area if beads is not None else 0.0
                    row["samples"].append({"print_z_mm": z, "coverage": coverage, "stock_mm2": stock.area})
                if waiting:
                    wanted[target] = waiting
            if not wanted:
                break
    handle.close()
    for row in rows:
        if row["samples"]:
            row["minimum_coverage"] = min(s["coverage"] for s in row["samples"])
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("directory", type=Path)
    parser.add_argument("--project-only", action="store_true", help="read the written project back; no archive needed")
    parser.add_argument("--no-audit", action="store_true", help="skip the support topology reading")
    args = parser.parse_args()
    if args.project_only:
        result = check_project(args.directory)
        print(json.dumps(result, indent=2, default=str), flush=True)
        raise SystemExit(0 if result["pass"] else 1)
    result = review(args.directory, audit=not args.no_audit)
    raise SystemExit(0 if result["pass"] else 1)


if __name__ == "__main__":
    main()
