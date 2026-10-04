"""Check the emitted RC62 pauses, pocket exclusion and closing bridge paths.

Read native archives without printer communication. Coordinates in the report
are translated back into the assembled machine frame.
"""
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from shapely.geometry import LineString, box
from shapely import polygons, union_all

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
ENC = HERE.parent
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from verify_round_layer_band import check_span
NUMBER = re.compile(r"([XYZEFIJ])([-+]?\d*\.?\d+(?:[eE][-+]?\d+)?)")


def clipped_projection(triangles, low, high):
    shapes = []
    for triangle in triangles:
        poly = triangle
        for z, above in ((low, True), (high, False)):
            out = []
            for a, b in zip(poly, np.roll(poly, -1, axis=0)):
                ia = a[2] >= z if above else a[2] <= z
                ib = b[2] >= z if above else b[2] <= z
                if ia: out.append(a)
                if ia != ib: out.append(a+(b-a)*((z-a[2])/(b[2]-a[2])))
            poly = np.array(out)
            if len(poly) < 3: break
        if len(poly) >= 3:
            shape = polygons(poly[:, :2])
            if shape.area > 1e-10: shapes.append(shape)
    return union_all(shapes)


def show_contact_check(name, rows):
    """Read support-bead contact against the current printed show rounds."""
    import trimesh
    mesh = trimesh.load_mesh(ENC / f"enclosure-{name}.stl", process=True)
    tri, normals = mesh.triangles, mesh.face_normals
    if name == "front-top":
        picked = (np.min(tri[:, :, 2], axis=1) >= 345.69) & (
            (np.max(tri[:, :, 0], axis=1) <= -100) | (np.min(tri[:, :, 0], axis=1) >= 100))
    else:
        center = tri.mean(axis=1)
        picked = (np.abs(center[:, 0]) >= 91.7) & (center[:, 1] >= 22.19) & (center[:, 1] <= 61.42) & \
                 (center[:, 2] >= 266.18) & (center[:, 2] <= 278.21) & (normals[:, 2] < -0.001) & \
                 (np.max(np.abs(tri[:, :, 2] - 272.1940001), axis=1) > 0.001)
    tri = tri[picked]
    lows, highs = tri[:, :, 2].min(axis=1), tri[:, :, 2].max(axis=1)
    hits = []
    groups = {}
    for row in rows:
        groups.setdefault(row["machine_z_mm"], []).append(row)
    for z, roads in groups.items():
        near = tri[(highs >= z-1e-5) & (lows <= z+0.60)]
        region = clipped_projection(near, z-1e-5, z+0.60)
        for road in roads:
            bead = LineString(road["xy_mm"]).buffer(road["width_mm"]/2+0.05)
            if region.intersection(bead).area > 1e-8:
                hits.append(road)
    return {"check": "no support-bead contacts on visible show rounds", "pass": not hits,
            "show_round_triangles": len(tri), "support_roads_checked": len(rows),
            "vertical_contact_band_mm": 0.60, "xy_allowance_mm": 0.05, "contact_roads": hits[:10]}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_job(job, geom):
    archive = ROOT / job["native_archive"]
    assert sha(archive) == job["native_archive_sha256"]
    assert sha(ROOT / job["project"]) == job["project_sha256"]
    assert sha(ENC / f"enclosure-{job['part']}.stl") == job["source_stl_sha256"]
    tx, ty, tz = job["machine_to_bed_translation_mm"]
    xcenter, zcenter = geom["axis_xz_mm"]
    ymin, ymax = geom["pocket_y_mm"]
    radius, arc_z, roof_z = geom["pocket_radius_mm"], geom["arc_center_z_mm"], geom["roof_z_mm"]
    feature = ""
    width, height = 0.45, 0.24
    layer_z = 0.0
    actual = {"X": 0., "Y": 0., "Z": 0., "E": 0.}
    relative_e = False
    object_active = False
    pause = []
    support_inside = []
    prior_closure = []
    roofs = []
    last_model_z = None
    model_before = Counter()
    model_after = Counter()
    deposited_support = Counter()
    first_model_layer = []
    second_model_layer = []
    wall_layers = set()
    show_support = []
    settings = {}
    with zipfile.ZipFile(archive) as z:
        settings = json.loads(z.read("Metadata/project_settings.config"))
        data = z.read("Metadata/plate_1.gcode")
        assert hashlib.sha256(data).hexdigest() == job["gcode_sha256"]
        assert hashlib.md5(data).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        plate = ET.fromstring(z.read("Metadata/slice_info.config")).find("plate")
        metadata = {v.get("key"): v.get("value") for v in plate.findall("metadata")}
        nozzle_ids = [n.get("id") for n in plate.findall("nozzle")]
        trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+\d.]+)", data, re.M)]
        for lineno, raw in enumerate(data.splitlines(), 1):
            line = raw.decode()
            if line.startswith("; FEATURE: "):
                feature = line.split(": ", 1)[1]
                continue
            if line.startswith("; LINE_WIDTH: "):
                width = float(line.split(": ", 1)[1]); continue
            if line.startswith("; LAYER_HEIGHT: "):
                height = float(line.split(": ", 1)[1]); continue
            if line.startswith("; Z_HEIGHT: "):
                layer_z = float(line.split(": ", 1)[1]); continue
            if line.startswith("; OBJECT_ID:"):
                object_active = True
            if line.startswith("M83"):
                relative_e = True; continue
            if line.startswith("M82"):
                relative_e = False; continue
            if re.match(r"^M400 U1\s*(;.*)?$", line):
                pause.append({"gcode_line": lineno, "requested_layer_height_mm": layer_z,
                              "last_deposited_model_height_mm": last_model_z})
                continue
            cmd = line.split(";", 1)[0].strip()
            if not cmd or cmd.startswith(";"):
                continue
            words = cmd.split()
            if words[0] not in ("G0", "G1", "G2", "G3", "G92"):
                continue
            values = {k: float(v) for k, v in NUMBER.findall(cmd)}
            if words[0] == "G92":
                actual.update({k: v for k, v in values.items() if k in actual}); continue
            start = actual.copy()
            actual.update({k: values[k] for k in "XYZ" if k in values})
            extrusion = values.get("E", 0.) if relative_e else values.get("E", actual["E"]) - actual["E"]
            if "E" in values:
                actual["E"] = actual["E"] + values["E"] if relative_e else values["E"]
            if not object_active or extrusion <= 0 or not ("X" in values or "Y" in values):
                continue
            is_support = feature.startswith("Support")
            cad_z = layer_z - tz
            if not is_support:
                last_model_z = layer_z
                (model_after if pause else model_before)[round(layer_z, 6)] += 1
                if feature in ("Inner wall", "Outer wall", "Overhang wall"):
                    wall_layers.add((round(layer_z, 6), round(height, 6)))
                if feature in ("Inner wall", "Outer wall", "Overhang wall") and layer_z < 0.21:
                    first_model_layer.append([start["X"], start["Y"], actual["X"], actual["Y"], width])
                elif feature in ("Inner wall", "Outer wall", "Overhang wall") and abs(layer_z-0.44) < 0.002:
                    second_model_layer.append([start["X"], start["Y"], actual["X"], actual["Y"], width])
            else:
                deposited_support[round(layer_z, 6)] += 1
                if (job["part"] == "pump-cartridge" and 265.5 <= cad_z <= 278.3) or \
                   (job["part"] == "front-top" and cad_z >= 345.0):
                    show_support.append({"gcode_line": lineno, "machine_z_mm": cad_z,
                        "width_mm": width, "feature": feature,
                        "xy_mm": [[start["X"]-tx, start["Y"]-ty], [actual["X"]-tx, actual["Y"]-ty]]})
            # The roof slab is local. Only roads near this cavity are retained;
            # full part/support paths would needlessly enlarge the record.
            if not geom["seat_floor_z_mm"] - 0.6 <= cad_z <= roof_z + 0.8:
                continue
            pts = [(start["X"]-tx, start["Y"]-ty), (actual["X"]-tx, actual["Y"]-ty)]
            if max(p[0] for p in pts) < xcenter-radius-1 or min(p[0] for p in pts) > xcenter+radius+1:
                continue
            if max(p[1] for p in pts) < ymin-1 or min(p[1] for p in pts) > ymax+1:
                continue
            # Native object roads in this region must be straight, allowing an
            # exact line/slab intersection rather than chord approximation.
            assert words[0] not in ("G2", "G3"), (job["part"], lineno, cmd)
            road = LineString(pts)
            sample_z = min(cad_z - height/2, roof_z-1e-4)
            half = radius if sample_z >= arc_z else math.sqrt(max(0., radius**2-(sample_z-arc_z)**2))
            cavity = box(xcenter-half+0.05, ymin+0.05,
                         xcenter+half-0.05, ymax-0.05)
            inside = cavity.buffer(-width/2)
            overlap = road.intersection(inside)
            if is_support and cad_z-height/2 < roof_z:
                # Include the entire deposited bead and a small XY allowance;
                # a centreline outside the cavity can still foul insertion.
                bead_overlap = road.buffer(width/2+0.05).intersection(cavity).area
                if bead_overlap > 0.005:
                    support_inside.append({"gcode_line": lineno, "feature": feature,
                                           "machine_z_mm": cad_z, "bead_overlap_mm2": bead_overlap})
            if overlap.length <= 0.005:
                continue
            row = {"gcode_line": lineno, "feature": feature,
                   "print_z_mm": layer_z, "machine_z_mm": cad_z,
                   "layer_height_mm": height, "width_mm": width,
                   "from_machine_xy_mm": pts[0], "to_machine_xy_mm": pts[1],
                   "length_inside_pocket_mm": overlap.length}
            if not is_support and cad_z >= roof_z - 0.002:
                roofs.append(row)
                if not pause:
                    prior_closure.append(row)
    first_close_z = min((r["print_z_mm"] for r in roofs), default=None)
    first_roads = [r for r in roofs if r["print_z_mm"] == first_close_z]
    y_bridges = [r for r in first_roads if "Bridge" in r["feature"] and
                 abs(r["to_machine_xy_mm"][0]-r["from_machine_xy_mm"][0]) < 0.02]
    paused_rim = pause[0]["last_deposited_model_height_mm"] if len(pause) == 1 else None
    max_ring_top = geom["magnet_maximum_top_above_bed_mm"]
    first = union_all([LineString(((x1,y1),(x2,y2))).buffer(w/2) for x1,y1,x2,y2,w in first_model_layer])
    overlap_area = sum(LineString(((x1,y1),(x2,y2))).buffer(w/2).intersection(first).area
                       for x1,y1,x2,y2,w in second_model_layer)
    second_area = sum(LineString(((x1,y1),(x2,y2))).buffer(w/2).area for x1,y1,x2,y2,w in second_model_layer)
    unsupported_second = sum(not LineString(((x1,y1),(x2,y2))).buffer(w/2).intersects(first)
                             for x1,y1,x2,y2,w in second_model_layer)
    fine_spans = [("grip-floor-rounds", 6.23, 18.23), ("grip-ceiling-rounds", 100.999, 112.999)] \
                 if job["part"] == "pump-cartridge" else [("roof-corner-rounds", 187.392, 195.)]
    fine_checks = [check_span(sorted(wall_layers), *span, 0.08, 0.001) for span in fine_spans]
    checks = [
        {"check": "one emitted insertion pause", "pass": len(pause) == 1},
        {"check": "no roof closure before pause", "pass": not prior_closure},
        {"check": "ring below completed open rim", "pass": paused_rim is not None and paused_rim > max_ring_top,
         "completed_rim_height_mm": paused_rim, "largest_ring_top_height_mm": max_ring_top},
        {"check": "no support deposited inside closed pocket", "pass": not support_inside,
         "roads": len(support_inside)},
        {"check": "closing roof exists", "pass": bool(first_roads)},
        {"check": "first closing bead clears maximum ring", "pass": bool(first_roads) and
         min(r["print_z_mm"]-r["layer_height_mm"] for r in first_roads) > max_ring_top,
         "minimum_bead_underside_air_mm": min((r["print_z_mm"]-r["layer_height_mm"]-max_ring_top
                                                for r in first_roads), default=None)},
        {"check": "closing bridges span the short pocket depth", "pass": bool(y_bridges),
         "y_bridge_roads": len(y_bridges)},
        {"check": "native plate inside printable area and uses left nozzle", "pass":
         metadata.get("outside") == "false" and nozzle_ids == ["0"], "nozzle_ids": nozzle_ids},
        {"check": "each printer retains its emitted Textured PEI trim", "pass":
         trims == [0., 0.02 if job["part"] == "pump-cartridge" else 0.16], "emitted_trim_mm": trims},
        {"check": "first-to-second wall beads overlap", "pass": bool(second_model_layer) and unsupported_second == 0,
         "second_layer_roads": len(second_model_layer), "roads_without_overlap": unsupported_second,
         "area_overlap_fraction": overlap_area/second_area if second_area else 0.},
        {"check": "emitted fine show-round layer bands", "pass": all(c["pass"] for c in fine_checks), "bands": fine_checks},
        show_contact_check(job["part"], show_support),
    ]
    return {"part": job["part"], "native_checks_pass": all(c["pass"] for c in checks),
            "checks": checks, "pause": pause,
            "first_closing_layer_height_mm": first_close_z,
            "first_closing_roads": first_roads,
            "support_inside_pocket": support_inside[:12], "closure_before_pause": prior_closure[:12],
            "process": {k: settings.get(k) for k in (
                "printer_settings_id", "filament_nozzle_map", "curr_bed_type", "layer_height",
                "initial_layer_print_height", "wall_loops", "nozzle_temperature",
                "nozzle_temperature_initial_layer", "chamber_temperatures", "support_type")},
            "native_archive_sha256": job["native_archive_sha256"], "gcode_sha256": job["gcode_sha256"],
            "project_sha256": job["project_sha256"], "source_stl_sha256": job["source_stl_sha256"]}


def main():
    preparation = json.loads((HERE / "preparation.json").read_text())
    geometry = json.loads((HERE / "geometry-check.json").read_text())
    readings = [read_job(job, geometry["pieces"][job["part"]]) for job in preparation["jobs"]]
    report = {"submitted": False, "native_checks_pass": all(r["native_checks_pass"] for r in readings),
              "scope": "Native emitted pause, ring insertion clearance, pocket support exclusion and sealing paths. Physical ring retention, roof quality, heat exposure and assembled seating remain unmeasured.",
              "jobs": readings, "audit_script_sha256": sha(Path(__file__))}
    (HERE / "native-check.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"native_checks_pass": report["native_checks_pass"],
                      "jobs": [{k: r[k] for k in ("part", "native_checks_pass", "checks", "pause", "first_closing_layer_height_mm")} for r in readings]}, indent=2))
    if not report["native_checks_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
