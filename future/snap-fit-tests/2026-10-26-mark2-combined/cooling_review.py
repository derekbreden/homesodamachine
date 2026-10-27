"""Manual fan/time and cable-pocket reading of one retained native archive.

Usage: tools/cad-venv/bin/python cooling_review.py <native-directory-or-archive>
Optional --geometry names the cable variant report; --output names the receipt.
No slicer, printer, shared preset or production source is changed.
"""
from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import math
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

import numpy as np
from shapely.geometry import LineString, box

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
SHARED = ROOT / "hardware/printed-parts/enclosure/trial-preparation"
sys.path.insert(0, str(SHARED))
spec = importlib.util.spec_from_file_location("combined_native_reader", SHARED / "review.py")
reader = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reader)
WORDS = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
COOLING = ("fan_min_speed", "fan_max_speed", "close_fan_the_first_x_layers",
           "full_fan_speed_layer", "reduce_fan_stop_start_freq", "overhang_fan_speed",
           "additional_cooling_fan_speed", "slow_down_for_layer_cooling",
           "slow_down_layer_time", "slow_down_min_speed", "no_slow_down_for_cooling_on_outwalls")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    path = Path(path).resolve()
    return str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path)


def motion_length(command, start, end, words):
    delta = end-start
    if command in {"G2", "G3"} and ("I" in words or "J" in words):
        centre = start[:2]+[words.get("I",0),words.get("J",0)]
        radius = float(np.linalg.norm(start[:2]-centre))
        a0 = math.atan2(start[1]-centre[1],start[0]-centre[0])
        a1 = math.atan2(end[1]-centre[1],end[0]-centre[0])
        sweep = a1-a0
        if command == "G2":
            sweep = sweep if sweep < -1e-9 else sweep-2*math.pi
        else:
            sweep = sweep if sweep > 1e-9 else sweep+2*math.pi
        return math.hypot(radius*sweep,delta[2])
    return float(np.linalg.norm(delta))


def timing(lines, objects):
    position = np.zeros(3)
    extrusion, feed, multiplier, elapsed = 0., 1200., 1., 0.
    absolute, relative_e, skipped = True, True, False
    fan, owner, feature = None, None, ""
    rows, fan_commands, current = [], [], None

    def finish(final=False):
        if current is None:
            return
        end = current["last_model_end_s"] if final else elapsed
        current["nominal_motion_and_dwell_s"] = end-current["start_s"]
        current["objects"] = dict(current["objects"])
        rows.append(current)

    for number, raw in enumerate(lines,1):
        line = raw.strip()
        if line.startswith(";"):
            comment = line[1:].strip()
            if comment == "SKIPPABLE_START":
                skipped = True
            elif comment == "SKIPPABLE_END":
                skipped = False
            elif re.match(r"=+\s*machine:.*\bend\b",comment,re.I):
                finish(final=True)
                current = None
                break
            elif comment.startswith("Z_HEIGHT:"):
                finish()
                current = {"layer":len(rows)+1,"z_mm":float(comment.split(":",1)[1]),
                           "start_s":elapsed,"last_model_end_s":elapsed,"explicit_dwell_s":0.,
                           "objects":defaultdict(lambda:{"first_model_s":None,"last_model_s":None,
                               "model_cruise_s":0.,"model_length_mm":0.,"part_fan_states_s255":set(),
                               "model_length_at_full_part_fan_mm":0.})}
            elif comment.startswith("OBJECT_ID:"):
                owner = int(comment.split(":",1)[1])
            elif comment.startswith("FEATURE:"):
                feature = comment.split(":",1)[1].strip()
            continue
        if skipped:
            continue
        code = line.split(";",1)[0].strip()
        if not code:
            continue
        command = code.split(None,1)[0]
        words = {k:float(v) for k,v in WORDS.findall(code[len(command):])}
        if command in {"G90","G91"}:
            absolute = command == "G90"
        elif command in {"M82","M83"}:
            relative_e = command == "M83"
        elif command == "M220" and "S" in words:
            multiplier = words["S"]/100
        elif command in {"M106","M107"} and int(words.get("P",1)) == 1:
            fan = words.get("S",255.) if command == "M106" else 0.
            if current is not None:
                fan_commands.append({"source_line":number,"layer":current["layer"],
                                     "z_mm":current["z_mm"],"command":code,"value_s255":fan,
                                     "channel":1,"explicit_P1":words.get("P")==1})
        elif command in {"G4","M400"}:
            seconds = words.get("S",0.)+words.get("P",0.)/1000
            elapsed += seconds
            if current is not None:
                current["explicit_dwell_s"] += seconds
        elif command == "G92":
            for axis,index in zip("XYZ",range(3)):
                position[index] = words.get(axis,position[index])
            extrusion = words.get("E",extrusion)
        elif command in {"G0","G1","G2","G3"}:
            start = position.copy()
            for axis,index in zip("XYZ",range(3)):
                if axis in words:
                    position[index] = words[axis] if absolute else position[index]+words[axis]
            de = (words.get("E",0.) if relative_e else words.get("E",extrusion)-extrusion) if "E" in words else 0.
            extrusion = extrusion+de if relative_e else words.get("E",extrusion)
            feed = words.get("F",feed)
            length = motion_length(command,start,position,words)
            distance = length if length > 1e-9 else abs(de)
            seconds = distance/(feed*multiplier/60) if feed*multiplier > 0 else 0.
            before = elapsed
            elapsed += seconds
            if current is not None and de > 1e-9 and length > 1e-9 and feature in reader.MODEL and owner in objects:
                entry = current["objects"][owner]
                if entry["first_model_s"] is None:
                    entry["first_model_s"] = before
                entry["last_model_s"] = elapsed
                entry["model_cruise_s"] += seconds
                entry["model_length_mm"] += length
                entry["part_fan_states_s255"].add(fan)
                if fan is not None and fan >= 254.5:
                    entry["model_length_at_full_part_fan_mm"] += length
                current["last_model_end_s"] = elapsed
    if current is not None:
        finish(final=True)
    previous = {}
    for row in rows:
        for oid,entry in row["objects"].items():
            entry["part_fan_states_s255"] = sorted(entry["part_fan_states_s255"],key=lambda x:-1 if x is None else x)
            entry["full_part_fan_model_length_fraction"] = entry["model_length_at_full_part_fan_mm"]/entry["model_length_mm"]
            if oid in previous:
                entry["nominal_start_to_start_s"] = entry["first_model_s"]-previous[oid]["first_model_s"]
                entry["nominal_off_object_interval_s"] = entry["first_model_s"]-previous[oid]["last_model_s"]
            previous[oid] = entry
    return rows,fan_commands


def pocket_reading(archive, preparation, geometry):
    if not geometry:
        return []
    variants = {v["stl"]:v for v in geometry["variants"]}
    windows = []
    for record in preparation["objects"]:
        variant = variants.get(record["stl"])
        if variant is None:
            continue
        for label,key in (("seat","print_pocket_bounds_mm"),("entry","print_entry_core_bounds_mm")):
            bounds = np.array(variant[key]).reshape(2,3)
            corners = np.array([[x,y,z] for x in bounds[:,0] for y in bounds[:,1] for z in bounds[:,2]])
            placed = (corners-record["source_center_mm"]) @ np.array(record["build_rotation"]).T+record["translation_mm"]
            windows.append({"object":record["name"],"identify_id":record["identify_id"],"void":label,
                            "source_bounds_mm":variant[key],"plate_bounds_mm":[placed.min(0).tolist(),placed.max(0).tolist()],
                            "support_crossings":[],"brim_or_other_nonmodel_crossings":[]})
    handle,stream = reader.gcode_lines(archive)
    with stream:
        for z,height,roads in reader.layers(stream):
            for window in windows:
                lo,hi = window["plate_bounds_mm"]
                if z-height >= hi[2]-1e-3 or z <= lo[2]+1e-3:
                    continue
                region = box(lo[0]+1e-3,lo[1]+1e-3,hi[0]-1e-3,hi[1]-1e-3)
                for a,b,c,d,width,feature,owner in roads:
                    if feature in reader.MODEL:
                        continue
                    overlap = LineString([(a,b),(c,d)]).buffer(width/2,quad_segs=4).intersection(region)
                    if overlap.area > 1e-6:
                        key = "support_crossings" if feature in reader.SUPPORT else "brim_or_other_nonmodel_crossings"
                        window[key].append({"z_mm":z,"feature":feature,"road_mm":[a,b,c,d,width],"area_in_void_mm2":overlap.area})
    handle.close()
    return windows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input",type=Path)
    parser.add_argument("--geometry",type=Path)
    parser.add_argument("--output",type=Path,default=HERE/"cooling-review.json")
    args = parser.parse_args()
    directory = args.input if args.input.is_dir() else args.input.parent
    preparation = json.loads((directory/"preparation.json").read_text())
    archive = ROOT/preparation["archive"] if args.input.is_dir() else args.input
    geometry = json.loads(args.geometry.read_text()) if args.geometry else None
    with zipfile.ZipFile(archive) as zipped:
        raw = zipped.read("Metadata/plate_1.gcode")
        gcode = raw.decode("utf-8","replace").splitlines()
        settings = json.loads(zipped.read("Metadata/project_settings.config"))
        embedded_filament = json.loads(zipped.read("Metadata/filament_settings_1.config"))
        md5_ok = hashlib.md5(raw).hexdigest() == zipped.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
    objects = {r["identify_id"]:r for r in preparation["objects"]}
    rows,fan_commands = timing(gcode,objects)
    cable_ids = {oid for oid,r in objects.items() if re.search(r"ribbon|cable",r["name"]+r["stl"],re.I)}
    upper_z = min(v["print_pocket_bounds_mm"][2] for v in geometry["variants"]) if geometry else 14.2
    upper = [r for r in rows if r["z_mm"] >= upper_z and any(oid in cable_ids for oid in r["objects"])]
    cable_entries = [entry for r in upper for oid,entry in r["objects"].items() if oid in cable_ids]
    times = [r["nominal_motion_and_dwell_s"] for r in upper]
    windows = pocket_reading(archive,preparation,geometry)
    result = {
        "scope":"Manual experimental plate audit. Fan commands are requests, not measured airflow. Feed-command cruise times plus explicit dwell are lower bounds, not firmware wall-clock timing; acceleration, synchronization and optional timelapse are not credited.",
        "archive":relative(archive),"archive_sha256":sha(archive),
        "preparation":relative(directory/"preparation.json"),"preparation_sha256":sha(directory/"preparation.json"),
        "recorded_archive_sha256":preparation["archive_sha256"],"archive_digest_matches":sha(archive)==preparation["archive_sha256"],
        "gcode_md5_matches":md5_ok,"reviewer_sha256":sha(Path(__file__)),
        "cooling_settings":{key:settings.get(key) for key in COOLING},
        "embedded_filament_cooling_settings":{key:embedded_filament.get(key) for key in COOLING},
        "fan_command_interpretation":"M106 without P selects the default part-fan channel P1; explicit P2/P3/P9 commands are excluded. S255 is a100% request. This is commanded state, not measured airflow.",
        "geometry":relative(args.geometry) if args.geometry else None,
        "geometry_sha256":sha(args.geometry) if args.geometry else None,
        "cable_upper_from_z_mm":upper_z,"cable_upper_layers":len(upper),
        "cable_upper_minimum_full_part_fan_model_length_fraction":min((r["full_part_fan_model_length_fraction"] for r in cable_entries),default=None),
        "cable_upper_part_fan_states_s255":sorted({s for r in cable_entries for s in r["part_fan_states_s255"]},key=lambda x:-1 if x is None else x),
        "explicit_P1_fan_commands_in_model_layers":[r for r in fan_commands if re.match(r"M106\s+P1\b",r["command"])],
        "part_fan_commands_after_first_three_layers":[r for r in fan_commands if r["layer"]>=4],
        "first_three_layer_model_part_fan_states_s255":sorted({s for row in rows[:3] for entry in row["objects"].values() for s in entry["part_fan_states_s255"]},key=lambda x:-1 if x is None else x),
        "upper_layer_nominal_motion_and_dwell_s":{"minimum":min(times) if times else None,"maximum":max(times) if times else None,"last_ten":[{"z_mm":r["z_mm"],"seconds":r["nominal_motion_and_dwell_s"]} for r in upper[-10:]]},
        "upper_layers_with_nominal_lower_bound_below_20s":sum(t < 20 for t in times),
        "cable_upper_minimum_nominal_start_to_start_s":min((r["nominal_start_to_start_s"] for r in cable_entries if "nominal_start_to_start_s" in r),default=None),
        "cable_upper_minimum_nominal_off_object_interval_s":min((r["nominal_off_object_interval_s"] for r in cable_entries if "nominal_off_object_interval_s" in r),default=None),
        "voids":windows,"support_and_brim_excluded_from_declared_voids":bool(windows) and all(not r["support_crossings"] and not r["brim_or_other_nonmodel_crossings"] for r in windows),
        "layers":rows,"part_fan_commands":fan_commands,
    }
    if geometry:
        checks = {
            "archive_and_gcode_bound":result["archive_digest_matches"] and md5_ok,
            "upper_cable_model_part_fan_commanded_100_percent":bool(cable_entries) and result["cable_upper_minimum_full_part_fan_model_length_fraction"]==1.,
            "first_three_model_layers_part_fan_off":result["first_three_layer_model_part_fan_states_s255"]==[0.],
            "local_layer_cooling_target_20_seconds":settings.get("slow_down_for_layer_cooling")==["1"] and settings.get("slow_down_layer_time")==["20"],
            "cable_seat_and_entry_support_and_brim_free":result["support_and_brim_excluded_from_declared_voids"],
            "conservative_timing_and_off_object_interval_recorded":bool(times) and result["cable_upper_minimum_nominal_off_object_interval_s"] is not None,
        }
        result.update(status="Pass: requested experimental fan/time settings and emitted commands recorded; no physical20-second timing claim.",
                      checks=checks,pass_requested_command_audit=all(checks.values()))
    else:
        result["status"] = "Historical command/timing comparison only; no current-policy acceptance claim."
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in {"layers","part_fan_commands","voids"}},indent=2))
    print(json.dumps({"void_crossing_counts":[{"object":r["object"],"void":r["void"],"support":len(r["support_crossings"]),"brim_or_other":len(r["brim_or_other_nonmodel_crossings"])} for r in windows]},indent=2))


if __name__ == "__main__":
    main()
