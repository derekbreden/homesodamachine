"""Manually review the printer-left exterior lip in an identified native slice.

Run with cad-venv; this is an offline inspection, not a build or printer step.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import zipfile

import numpy as np
from shapely.geometry import LineString, Point
from shapely.ops import substring, unary_union


def arc_points(start, end, words, clockwise):
    center = np.asarray(start) + [words.get("I", 0), words.get("J", 0)]
    radius = math.dist(start, center)
    a0 = math.atan2(start[1] - center[1], start[0] - center[0])
    a1 = math.atan2(end[1] - center[1], end[0] - center[0])
    if clockwise:
        while a1 >= a0:
            a1 -= 2 * math.pi
    else:
        while a1 <= a0:
            a1 += 2 * math.pi
    count = max(1, math.ceil(abs(a1 - a0) * radius / .025))
    points = [(center[0] + radius * math.cos(a), center[1] + radius * math.sin(a))
              for a in np.linspace(a0, a1, count + 1)]
    points[0], points[-1] = start, end
    return points


def review(archive, first=17, last=33):
    with zipfile.ZipFile(archive) as z:
        data = z.read("Metadata/plate_1.gcode")
    lines = data.decode().splitlines()
    layers = {}
    x = y = z = e = time = 0.
    feed, width = 1200., .62
    relative_e = absolute_xyz = True
    feature, layer, group = "Custom", 0, 0
    depositing = False
    fans, nozzle_target, feed_line = {}, None, None
    for line_number, raw in enumerate(lines, 1):
        if raw.startswith("; Z_HEIGHT:"):
            layer += 1
            if layer > last:
                break
            layers[layer] = dict(z=float(raw.split(":", 1)[1]), start=time, moves=[],
                                 fans=dict(fans), nozzle_target=nozzle_target)
        if raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
            depositing = False
        if raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {k: float(v) for k, v in re.findall(r"([XYZEFIJPQS])(-?(?:\d+(?:\.\d*)?|\.\d+))", code)}
        if command in {"G90", "G91"}:
            absolute_xyz = command == "G90"
        if command in {"M82", "M83"}:
            relative_e = command == "M83"
        if command == "G92":
            x, y, z, e = [words.get(k, v) for k, v in zip("XYZE", (x, y, z, e))]
        if command == "M106":
            fans[int(words.get("P", 1))] = words.get("S", 255)
        if command == "M107":
            fans[int(words.get("P", 1))] = 0
        if command in {"M104", "M109"} and "S" in words:
            nozzle_target = words["S"]
        if command not in {"G0", "G1", "G2", "G3"}:
            continue
        if "F" in words:
            feed, feed_line = words["F"], line_number
        nx, ny, nz = [words.get(k, v) if absolute_xyz else v + words.get(k, 0)
                      for k, v in zip("XYZ", (x, y, z))]
        delta_e = words.get("E", 0) if relative_e else words.get("E", e) - e
        points = (arc_points((x, y), (nx, ny), words, command == "G2")
                  if command in {"G2", "G3"} else [(x, y), (nx, ny)])
        path = LineString(points)
        distance = path.length
        duration = (math.hypot(distance, nz - z) if distance > 1e-8 or abs(nz-z) > 1e-8
                    else abs(delta_e)) / feed * 60
        drawing = layer > 0 and feature not in {"Custom", "Brim"} and delta_e > 1e-9 and distance > 1e-8
        if drawing:
            if not depositing:
                group += 1
            layers[layer]["moves"].append(dict(line=line_number, feed_line=feed_line,
                feature=feature, width=width, speed=feed/60, path=path,
                start=time, end=time+duration, group=group, start_xy=(x, y)))
        # A feed-only G1 changes speed without ending a continuous perimeter.
        if distance > 1e-8 or abs(nz-z) > 1e-8 or abs(delta_e) > 1e-9:
            depositing = drawing
        if layer > 0:
            time += duration
            layers[layer]["end"] = time
        x, y, z = nx, ny, nz
        if "E" in words:
            e = e + words["E"] if relative_e else words["E"]

    rows = []
    for number in range(first, last + 1):
        row, previous = layers[number], layers[number-1]
        groups = {}
        for move in row["moves"]:
            if move["feature"] == "Outer wall":
                groups.setdefault(move["group"], []).append(move)
        loops = []
        for paths in groups.values():
            coordinates = list(paths[0]["path"].coords)
            for move in paths[1:]:
                coordinates.extend(list(move["path"].coords)[1:])
            outline = LineString(coordinates)
            loops.append((outline.length, outline, paths))
        _, outline, paths = max(loops, key=lambda item: item[0])
        closure_gap = Point(outline.coords[0]).distance(Point(outline.coords[-1]))
        if closure_gap > .002:
            raise ValueError(f"Layer {number}: selected exterior is not closed ({closure_gap} mm)")
        coordinates = np.asarray(outline.coords)
        point = Point(coordinates[int(np.argmin(coordinates[:, 0]))])
        position = outline.project(point)
        lip = substring(outline, max(0, position-.5), min(outline.length, position+.5))
        local = [move for move in paths if move["path"].distance(lip) < .001]
        width = float(np.median([move["width"] for move in local]))
        prior = unary_union([move["path"].buffer(move["width"]/2, quad_segs=6)
                             for move in previous["moves"]])
        bead = lip.buffer(width/2, quad_segs=6)
        nearest = min(local, key=lambda move: move["path"].distance(point))
        previous_nearest = min((m for m in previous["moves"] if m["feature"] == "Outer wall"),
                               key=lambda move: move["path"].distance(point))
        rows.append(dict(layer=number, z_mm=row["z"],
            layer_nominal_motion_s=row["end"]-row["start"],
            outer_loops=len(loops), exterior_closure_gap_mm=closure_gap,
            exterior_speed_range_mm_s=[min(m["speed"] for m in paths), max(m["speed"] for m in paths)],
            left_lip_plate_xy_mm=list(point.coords)[0],
            left_lip_speeds_mm_s=sorted({round(m["speed"], 5) for m in local}),
            left_lip_width_mm=width,
            left_lip_local_1mm_bead_prior_overlap_fraction=bead.intersection(prior).area/bead.area,
            left_lip_distance_from_seam_along_outline_mm=min(position, outline.length-position),
            left_lip_nominal_return_time_s=nearest["start"]-previous_nearest["start"],
            left_lip_gcode_line=nearest["line"], left_lip_gcode_command=lines[nearest["line"]-1],
            left_lip_feed_line=nearest["feed_line"], left_lip_feed_command=lines[nearest["feed_line"]-1],
            fans_at_layer_start_pwm=row["fans"], nozzle_target_at_layer_start_c=row["nozzle_target"]))
    return dict(archive=Path(archive).name,
        archive_sha256=hashlib.sha256(Path(archive).read_bytes()).hexdigest(),
        gcode_sha256=hashlib.sha256(data).hexdigest(),
        scope=f"Layers {first}–{last}. Minimum-X point on the longest closed exterior perimeter. Feed-only G1 commands preserve continuous extrusion. Arc sampling interval at most 0.025 mm. Local speeds and overlap cover a 1 mm outline window. Timing sums commanded motion without acceleration, firmware or timelapse waits. Fans and nozzle targets are archived commands, not physical measurements. Bead overlap is geometric, not a printability result.",
        layers=rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--first", type=int, default=17)
    parser.add_argument("--last", type=int, default=33)
    args = parser.parse_args()
    result = review(args.archive, args.first, args.last)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"output": str(args.output), "gcode_sha256": result["gcode_sha256"],
        "lip_speeds_mm_s": {r["layer"]: r["left_lip_speeds_mm_s"] for r in result["layers"]}}))
