"""Verify the native three-float archive and publish its preparation receipts."""

import hashlib
import json
import math
import re
import shutil
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter, defaultdict, namedtuple
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import trimesh
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union

from prepare import ARCHIVE_NAME, FLOAT, HERE, PRIVATE, PROJECT, ROOT, SETTING, json_write, sha

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
GCODE = "Metadata/plate_1.gcode"
Road = namedtuple("Road", "index obj layer z feature width ax ay bx by extrusion speed")
Move = namedtuple("Move", "index layer ax ay bx by distance")
WORDS = re.compile(r"([XYZEF])([-+\d.]+)")


def members(path):
    with zipfile.ZipFile(path) as archive:
        assert archive.testzip() is None
        return {name: archive.read(name) for name in archive.namelist()}


def parse(program):
    x = y = z = e = feed = width = 0.0
    obj = layer = None
    absolute_xyz = relative_e = True
    feature = ""
    roads, moves, runs = [], [], []
    run = None
    for index, raw in enumerate(program.splitlines()):
        if raw.startswith("; OBJECT_ID:") or raw.startswith("; start printing object, unique label id:"):
            obj = int(raw.rsplit(":", 1)[1])
        elif raw.startswith("; stop printing object"):
            obj = None
        elif raw.startswith("; Z_HEIGHT:"):
            layer = float(raw.split(":", 1)[1]); obj = None
        elif raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
        elif raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        values = {key: float(value) for key, value in WORDS.findall(code)}
        if command in ("G90", "G91"):
            absolute_xyz = command == "G90"
        elif command in ("M82", "M83"):
            relative_e = command == "M83"
        elif command == "G92":
            x, y, z, e = (values.get(key, old) for key, old in zip("XYZE", (x, y, z, e)))
        elif command in ("G0", "G1", "G2", "G3"):
            tx, ty, tz = (values.get(key, old) if absolute_xyz else old + values.get(key, 0)
                          for key, old in zip("XYZ", (x, y, z)))
            delta = values.get("E", 0) if relative_e else values.get("E", e) - e
            distance = math.hypot(tx - x, ty - y)
            feed = values.get("F", feed)
            if obj in (1901, 1902, 1903) and layer is not None and delta > 1e-9 and distance > 1e-6:
                assert command in ("G0", "G1"), "Explicit straight deposition required for this review"
                road = Road(index, obj, layer, tz, feature, width, x, y, tx, ty, delta, feed / 60)
                roads.append(road)
                if feature == "Outer wall":
                    if run is None or run["object"] != obj or run["layer_z_mm"] != layer:
                        run = {"object": obj, "layer_z_mm": layer, "start_xy_mm": [x, y],
                               "end_xy_mm": [tx, ty], "first_line_1_based": index + 1,
                               "last_line_1_based": index + 1, "segment_count": 0}
                        runs.append(run)
                    run.update(end_xy_mm=[tx, ty], last_line_1_based=index + 1,
                               segment_count=run["segment_count"] + 1)
                else:
                    run = None
            elif distance > 1e-6 and layer is not None and delta <= 1e-9:
                moves.append(Move(index, layer, x, y, tx, ty, distance)); run = None
            elif delta < -1e-9:
                run = None
            x, y, z = tx, ty, tz
            if "E" in values:
                e = e + values["E"] if relative_e else values["E"]
    return roads, moves, runs


def bead_shape(roads):
    return unary_union([LineString(((r.ax, r.ay), (r.bx, r.by))).buffer(r.width / 2, quad_segs=4) for r in roads])


def geometry_binding(preparation, native):
    model = ET.fromstring(native["3D/3dmodel.model"])
    qn = lambda tag: f"{{{CORE}}}{tag}"
    resources = {o.get("id"): o for o in model.find(qn("resources"))}
    items = {i.get("objectid"): i for i in model.find(qn("build"))}
    assert len(items) == len(resources) == 3
    mesh = trimesh.load(HERE / "source-snapshot/float-aero.stl", force="mesh", process=True)
    records = []
    for part in preparation["parts"]:
        component, = resources[part["object_id"]].find(qn("components"))
        assert component.get("transform") == "1 0 0 0 1 0 0 0 1 0 0 0"
        child = ET.fromstring(native[component.get(f"{{{PROD}}}path").lstrip("/")])
        embedded = child.find(f"{qn('resources')}/{qn('object')}/{qn('mesh')}")
        vertices = np.array([[float(v.get(axis)) for axis in "xyz"] for v in embedded.find(qn("vertices"))])
        faces = np.array([[int(f.get(key)) for key in ("v1", "v2", "v3")] for f in embedded.find(qn("triangles"))])
        assert np.array_equal(faces, mesh.faces)
        error = float(np.max(np.abs(vertices + part["source_center_mm"] - mesh.vertices)))
        assert error < 1e-6
        transform = np.array(list(map(float, items[part["object_id"]].get("transform").split())))
        assert np.max(np.abs(transform - part["build_transform"])) < 1e-6
        paint = Counter(f.get("paint_seam", "") for f in embedded.find(qn("triangles")))
        assert paint["4"] > 0 and paint["8"] > 0
        records.append({"identify_id": part["identify_id"], "source_stl_sha256": part["stl_sha256"],
                        "embedded_vertex_error_mm": error, "build_transform_verified": True,
                        "seam_paint_triangle_counts": dict(paint)})
    return records


def seam_review(runs, centers, targets):
    rows = []
    for obj, center in centers.items():
        target = targets[obj]
        exterior = [run for run in runs if run["object"] == obj and math.dist(run["start_xy_mm"], center) > 17]
        assert len(exterior) == 140, (obj, len(exterior))
        assert len({run["layer_z_mm"] for run in exterior}) == 140
        for run in exterior:
            angles = []
            for point in (run["start_xy_mm"], run["end_xy_mm"]):
                angle = math.degrees(math.atan2(point[1] - center[1], point[0] - center[0])) % 360
                difference = (angle - target + 180) % 360 - 180
                assert abs(difference) < 7, (obj, run["layer_z_mm"], angle, target)
                angles.append(difference)
            run["angular_error_degrees"] = angles
        rows.append({"identify_id": obj, "target_degrees_from_positive_x": target,
                     "external_seam_layers_verified": len(exterior),
                     "maximum_start_error_degrees": max(abs(r["angular_error_degrees"][0]) for r in exterior),
                     "maximum_end_error_degrees": max(abs(r["angular_error_degrees"][1]) for r in exterior),
                     "all_external_starts_and_stops_face_cluster_center": True,
                     "sample_seams": [exterior[i] for i in (0, 61, 79, 80, 139)]})
    return {"seam_type": "Regular seam", "scarf_enabled": False, "objects": rows,
            "scope": "All 140 emitted exterior contour starts and stops per float; inner nested-wall transfers are also present."}


def pocket_review(grouped, centers, pause_index):
    records, shapes = [], {}
    for obj, center in centers.items():
        angles = np.linspace(0, 2 * math.pi, 720, endpoint=False)
        ring = Polygon([(center[0] + 9.525 * math.cos(a), center[1] + 9.525 * math.sin(a)) for a in angles],
                       [[(center[0] + 4.7625 * math.cos(a), center[1] + 4.7625 * math.sin(a)) for a in angles]])
        fractions = {}
        for z in (12.4, 12.6, 16.0, 16.2, 16.4):
            shape = bead_shape(grouped[obj, z]); shapes[obj, z] = shape
            fractions[z] = shape.intersection(ring).area / ring.area
        assert fractions[12.4] > .95 and fractions[12.6] < .05 and fractions[16.0] < .05, (obj, fractions)
        assert fractions[16.2] > .95 and fractions[16.4] > .95, (obj, fractions)
        cover = grouped[obj, 16.2]
        assert all(r.index > pause_index and r.z == 16.2 for r in cover)
        assert shapes[obj, 16.2].intersection(Point(center).buffer(2.3)).area < .01
        maximum_top = 12.4 + 3.175 + .1
        records.append({"identify_id": obj, "printed_seat_top_z_mm": 12.4,
                        "last_open_pocket_layer_z_mm": 16.0, "first_covering_layer_z_mm": 16.2,
                        "ring_footprint_coverage_by_layer": {str(k): v for k, v in fractions.items()},
                        "maximum_seated_magnet_top_z_mm": maximum_top,
                        "minimum_magnet_recess_below_printed_rims_mm": 16.0 - maximum_top,
                        "minimum_first_cover_nozzle_clearance_mm": 16.2 - maximum_top,
                        "cover_emitted_after_pause": True, "guide_bore_remains_open": True})
    return records, shapes


def travel_review(roads, moves):
    boundaries = [(a, b) for a, b in zip(roads, roads[1:]) if a.obj != b.obj and a.layer == b.layer]
    move_index = 0
    transfers = []
    for a, b in boundaries:
        while move_index < len(moves) and moves[move_index].index <= a.index:
            move_index += 1
        i = move_index
        distance = 0
        while i < len(moves) and moves[i].index < b.index:
            distance += moves[i].distance; i += 1
        transfers.append({"from": a.obj, "to": b.obj, "layer_z_mm": a.layer,
                          "xy_path_mm": distance, "deposition_end_to_next_start_mm": math.hypot(b.ax - a.bx, b.ay - a.by)})
    assert len(transfers) == 280
    return {"same_layer_inter_object_transfer_count": len(transfers),
            "shortest_xy_transfer_path_mm": min(t["xy_path_mm"] for t in transfers),
            "median_xy_transfer_path_mm": float(np.median([t["xy_path_mm"] for t in transfers])),
            "longest_xy_transfer_path_mm": max(t["xy_path_mm"] for t in transfers),
            "samples": [transfers[i] for i in (0, 1, 158, 159, 160, 161, 278, 279)],
            "scope": "Explicit non-depositing XY between the last bead on one object and first bead on its peer on the same layer; includes wipes and positioning. Startup-strip, layer-change and firmware-generated moves are excluded."}


def render(grouped, seams, centers, shapes, transfers):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Circle
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.6))
    colors = {1901: "#2875a1", 1902: "#39836f", 1903: "#8261aa"}
    for axis, z, title in zip(axes, (16.0, 16.2), ("Pocket open at the shared pause", "First layer over all three magnets")):
        for obj, center in centers.items():
            axis.add_collection(LineCollection([[(r.ax, r.ay), (r.bx, r.by)] for r in grouped[obj, z]],
                                                colors=colors[obj], linewidths=.45))
            axis.text(center[0], center[1] + 7, f"Float {obj - 1900}", ha="center", fontsize=9,
                      bbox={"facecolor": "white", "edgecolor": "none", "alpha": .8, "pad": 2})
            seam = next(s for s in seams["objects"] if s["identify_id"] == obj)
            sample = next(s for s in seam["sample_seams"] if s["layer_z_mm"] == z)
            sx, sy = sample["start_xy_mm"]
            axis.plot(sx, sy, "o", color="#da4b32", markersize=6)
            axis.add_patch(Circle(center, 9.525, fill=False, edgecolor="#7b8791", linewidth=.8, linestyle="--"))
            axis.add_patch(Circle(center, 4.7625, fill=False, edgecolor="#7b8791", linewidth=.8, linestyle="--"))
        axis.set(xlim=(137, 218), ylim=(127, 204), aspect="equal", xlabel="X (mm)", ylabel="Y (mm)",
                 title=f"{title}\nZ {z:g} mm")
        axis.grid(alpha=.12)
    fig.suptitle("Three close floats · regular seams face the central gap", fontsize=14)
    fig.text(.5, .035, "Red dots: emitted exterior seams. Dashed rings: nominal RC62 footprints. Approximate wall gap: 2 mm.", ha="center", fontsize=10)
    fig.tight_layout(rect=(0, .06, 1, .93))
    fig.savefig(HERE / "path-preview.png", dpi=170)
    plt.close(fig)


def main():
    prep = json.loads((HERE / "preparation.json").read_text())
    assert sha(PROJECT) == prep["project_sha256"]
    for row in json.loads((HERE / "source-snapshot/manifest.json").read_text())["files"]:
        assert sha(ROOT / row["snapshot"]) == row["sha256"]
    source = PRIVATE / "native" / ARCHIVE_NAME
    native = members(source)
    assert hashlib.md5(native[GCODE]).hexdigest() == native[GCODE + ".md5"].decode().strip().lower()
    program = native[GCODE].decode()
    lines = program.splitlines()
    summary = json.loads((PRIVATE / "native/result.json").read_text())["sliced_plates"][0]
    assert len(summary["objects"]) == 3 and not summary["warning_message"]
    chosen, effective = json.loads(members(PROJECT)[SETTING]), json.loads(native[SETTING])
    core_keys = ["machine_start_gcode", "machine_pause_gcode", "curr_bed_type", "wall_loops", "top_shell_layers", "bottom_shell_layers",
                 "layer_height", "initial_layer_print_height", "filament_flow_ratio", "filament_max_volumetric_speed",
                 "nozzle_temperature", "nozzle_temperature_initial_layer", "eng_plate_temp", "eng_plate_temp_initial_layer",
                 "chamber_temperatures", "filament_nozzle_map", "nozzle_diameter", "nozzle_volume_type",
                 "print_sequence", "seam_position", "seam_slope_type", "filament_scarf_seam_type", "wrapping_detection_gcode"]
    assert all(chosen.get(k) == effective.get(k) for k in core_keys)
    assert effective["filament_nozzle_map"] == ["1"] and effective["seam_slope_type"] == "none"
    bare_probe = [line for line in lines if re.match(r"^\s*G39(?:\s|$)", line)]
    trims = [line.split(";", 1)[0].strip() for line in lines if re.match(r"^\s*G29\.1\s", line)]
    assert not bare_probe and trims == ["G29.1 Z0", "G29.1 Z0.04"]
    binding = geometry_binding(prep, native)
    pauses = [i for i, line in enumerate(lines) if line.split(";", 1)[0].strip() == "M400 U1"]
    assert len(pauses) == 1
    pause_index = pauses[0]
    roads, moves, runs = parse(program)
    print(json.dumps({"phase": "paths parsed", "deposition_segments": len(roads), "explicit_travel_moves": len(moves)}), flush=True)
    assert max(r.layer for r in roads if r.index < pause_index) == 16.0
    assert min(r.layer for r in roads if r.index > pause_index) == 16.2
    grouped = defaultdict(list)
    for r in roads: grouped[r.obj, r.layer].append(r)
    assert len(grouped) == 420 and set(r.obj for r in roads) == {1901, 1902, 1903}
    assert set(r.feature for r in roads) <= {"Inner wall", "Outer wall", "Overhang wall", "Gap infill"}
    centers = {p["identify_id"]: tuple(c) for p, c in zip(prep["parts"], prep["centers_xy_mm"])}
    targets = {p["identify_id"]: p["target_degrees_from_positive_x"] for p in prep["inward_seam_painting"]}
    seams = seam_review(runs, centers, targets)
    print(json.dumps({"phase": "external seams verified", "layers_per_float": 140}), flush=True)
    pockets, shapes = pocket_review(grouped, centers, pause_index)
    envelope, radii = {}, {}
    for obj, center in centers.items():
        selected = [r for r in roads if r.obj == obj]
        low = [min(min(getattr(r, a), getattr(r, b)) - r.width / 2 for r in selected) for a, b in (("ax", "bx"), ("ay", "by"))]
        high = [max(max(getattr(r, a), getattr(r, b)) + r.width / 2 for r in selected) for a, b in (("ax", "bx"), ("ay", "by"))]
        inset = min(*(np.array(low) - [25, 0]), *([330, 320] - np.array(high)))
        assert inset >= 80
        radius = max(max(math.hypot(r.ax - center[0], r.ay - center[1]), math.hypot(r.bx - center[0], r.by - center[1])) + r.width / 2 for r in selected)
        radii[obj] = radius
        envelope[obj] = {"xy_min_mm": low, "xy_max_mm": high, "minimum_usable_bed_inset_mm": inset,
                         "maximum_radial_bead_envelope_mm": radius}
    pairs = [(1901, 1902), (1901, 1903), (1902, 1903)]
    conservative_gap = min(math.dist(centers[a], centers[b]) - radii[a] - radii[b] for a, b in pairs)
    assert conservative_gap > 1.8
    sampled_gap = min(shapes[a, z].distance(shapes[b, z]) for a, b in pairs for z in (16.0, 16.2))
    transfers = travel_review(roads, moves)
    slice_config = ET.fromstring(native["Metadata/slice_info.config"])
    pause, = slice_config.findall("plate/pause_list/pause")
    assert pause.get("layer") == "81"
    initial_countdown = int(next(re.search(r"^M73 C(\d+)", line).group(1) for line in lines if re.match(r"^M73 C\d+", line)))
    total_seconds = summary["total_predication"]
    elapsed = round(total_seconds / 60 - int(pause.get("remaining_time")))
    assert abs(elapsed - initial_countdown) <= 1
    archive = HERE / ARCHIVE_NAME
    if archive.exists():
        assert sha(archive) == sha(source)
    else:
        shutil.copyfile(source, archive)
    json_write(HERE / "native-result.json", summary)
    forecast = {"status": "native_pause_forecast_verified", "checked_utc": datetime.now(timezone.utc).isoformat(),
                "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
                "gcode_sha256": hashlib.sha256(native[GCODE]).hexdigest(), "project_sha256": sha(PROJECT),
                "quantity": 3, "printer": "Mark2", "active_side": "RIGHT", "nozzle_mm": .4,
                "programmed_pause": {"count": 1, "command": "M400 U1", "gcode_line_1_based": pause_index + 1,
                                     "before_layer": 81, "total_layers": 140, "top_z_mm": 16.2,
                                     "completed_open_layer_z_mm": 16.0, "remaining_minutes": int(pause.get("remaining_time"))},
                "native_forecast": {"approximate_elapsed_from_start_minutes": elapsed,
                                    "initial_emitted_countdown_minutes": initial_countdown,
                                    "total_prediction_seconds": total_seconds, "total_prediction_minutes": total_seconds / 60,
                                    "remaining_after_pause_minutes": int(pause.get("remaining_time")),
                                    "method": "Native total estimate minus minute-rounded pause-list remainder, compared with initial emitted M73 C countdown.",
                                    "scope": "Approximate start-to-pause forecast; startup and physical print timing can shift it. Manual magnet-insertion time is additional."},
                "submitted": False, "launch_authorized": False, "send_attempted": False}
    json_write(HERE / "pause-forecast.json", forecast)
    record = {"status": "preparation_verified", "checked_utc": forecast["checked_utc"],
              "archive": forecast["archive"], "archive_sha256": forecast["archive_sha256"], "gcode_sha256": forecast["gcode_sha256"],
              "project": str(PROJECT.relative_to(ROOT)), "project_sha256": sha(PROJECT),
              "review_script_sha256": sha(Path(__file__)), "prepare_script_sha256": sha(HERE / "prepare.py"),
              "native_crc_and_gcode_md5_verified": True, "geometry_binding": binding,
              "core_settings_verified": {k: effective.get(k) for k in core_keys},
              "native_settings_normalizations": {k: {"input": v, "native": effective.get(k)} for k, v in chosen.items() if v != effective.get(k)},
              "seam_review": seams, "magnet_pockets": pockets, "full_bead_envelopes": envelope,
              "conservative_all_layer_surface_gap_mm": conservative_gap,
              "sampled_exact_bead_gap_mm": sampled_gap, "travel_review": transfers,
              "layer_count_per_float": 140, "deposition_feature_counts": dict(Counter(r.feature for r in roads)),
              "supports": 0, "brim": 0, "bare_G39_probe_commands": 0, "emitted_z_trim_commands": trims,
              "filament_mass_estimate_g": summary["filaments"][0]["total_used_g"],
              "submitted": False, "launch_authorized": False, "send_attempted": False,
              "physical_scope": "Native geometry, timing and idealized bead footprints. Actual adhesion, foaming, defect size, repairability, magnet stability, roof strength and finished buoyancy are not established by this slice."}
    json_write(HERE / "native-review.json", record)
    render(grouped, seams, centers, shapes, transfers)
    print(json.dumps({"pause_minutes_after_start": elapsed, "total_minutes": total_seconds / 60,
                      "scarf": False, "external_seams_verified": 420, "minimum_surface_gap_mm": conservative_gap,
                      "inter_object_transfer_median_mm": transfers["median_xy_transfer_path_mm"], "submitted": False}), flush=True)


if __name__ == "__main__":
    main()
