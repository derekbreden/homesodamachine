#!/usr/bin/env python3
"""Insert a retracted wall lap at elbow object departures. Run by hand.

    tools/cad-venv/bin/python future/pump-elbow-exploration/departure_lap.py \
        native.gcode.3mf trial.gcode.3mf --report lap-review.json

This trial requires standing retractions, absolute XYZ and relative E in the
object blocks. It preserves every source line. No slicer preset is modified.
"""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile

from shapely.geometry import LineString, Point, Polygon
from shapely.ops import nearest_points, substring, unary_union

from travel_survey import arc_xy

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools/gcode"))
from toolpaths import read_runs

WORD = re.compile(r"([A-Z])([-+]?(?:\d*\.\d+|\d+\.?\d*))")
MEMBER = "Metadata/plate_1.gcode"
BEGIN = "; DEPARTURE_LAP_BEGIN"
END = "; DEPARTURE_LAP_END"


def digest(data):
    return hashlib.sha256(data).hexdigest()


def movements(lines):
    """Replay modal XYZ/E/feed, including the enabled H2C photo detour."""
    pos, feed, absolute, relative_e = (0., 0., 0.), 0., True, False
    layer, obj, layer_z, feature, width = 0, None, None, "", .62
    for index, raw in enumerate(lines):
        line = raw.strip()
        if line.startswith("; Z_HEIGHT:"):
            layer_z = float(line.split(":")[1])
        if line.startswith("; FEATURE:"):
            feature = line.split(":", 1)[1].strip()
        if line.startswith("; LINE_WIDTH:"):
            width = float(line.split(":")[1])
        if line.startswith("; layer num/total_layer_count:"):
            layer = int(line.split(":")[1].split("/")[0])
        if line.startswith("; start printing object, unique label id:"):
            obj = int(line.rsplit(":", 1)[1])
        if line.startswith("; stop printing object, unique label id:"):
            obj = None
        code = line.split(";")[0].strip()
        if not code:
            continue
        command = code.split()[0]
        words = {k: float(v) for k, v in WORD.findall(code[len(command):])}
        if command in ("G90", "G91"):
            absolute = command == "G90"
        elif command in ("M82", "M83"):
            relative_e = command == "M83"
        elif command == "G92":
            pos = tuple(words.get(k, v) for k, v in zip("XYZ", pos))
        elif command == "M9711" and "U" in words and "V" in words:
            pos = (words["U"], words["V"], pos[2])
        elif command in ("G0", "G1", "G2", "G3"):
            before = pos
            pos = tuple(words.get(k, v) if absolute else v + words.get(k, 0.)
                        for k, v in zip("XYZ", pos))
            feed = words.get("F", feed)
            yield dict(index=index, raw=raw, command=command, words=words,
                       start=before, end=pos, feed=feed, layer=layer, obj=obj,
                       layer_z=layer_z, absolute=absolute, relative_e=relative_e,
                       feature=feature, width=width)


def wall_lap(paths, origin, native_inner, native_outer):
    """Follow a printed inner wall; thin terminal rims use an outer wall.

    The four final layers lack closed native wall runs. Their fallback is a
    closed contour 0.15 mm inside the deposited terminal bead. Connections to
    and from the selected wall use the full 0.4 mm hop.
    """
    stock = unary_union([LineString(p).buffer(w / 2, quad_segs=12)
                         for p, w in paths if len(p) >= 2])
    if stock.distance(Point(origin)) > .005:
        raise ValueError("Departure is not on deposited stock")
    for label, runs in (("native_inner_wall", native_inner), ("native_outer_wall", native_outer),
                        ("terminal_bead_contour", [])):
        candidates = []
        if label == "terminal_bead_contour":
            islands = list(getattr(stock, "geoms", [stock]))
            island = min(islands, key=lambda g: g.distance(Point(origin)))
            interior = island.buffer(-.15, quad_segs=12)
            rings = [LineString(p.exterior.coords).simplify(.002)
                     for p in getattr(interior, "geoms", [interior])
                     if not p.is_empty and p.geom_type == "Polygon"]
        else:
            rings = []
            for run in runs:
                pts = [tuple(p[:2]) for p in run["pts"]]
                if math.dist(pts[0], pts[-1]) <= .02:
                    pts[-1] = pts[0]
                    rings.append(LineString(pts))
        for ring in rings:
            if stock.buffer(.005).covers(ring):
                candidates.append((ring.distance(Point(origin)), abs(Polygon(ring).area), ring))
        if candidates:
            nearest = min(c[0] for c in candidates)
            # Select the exterior-facing inner wall of the nearby leg/body,
            # rather than a tiny closed infill remnant or the distant leg.
            _, _, ring = max((c for c in candidates if c[0] <= nearest + 3.), key=lambda c: c[1])
            entry = nearest_points(Point(origin), ring)[1]
            connector = LineString([origin, entry.coords[0]])
            offset = ring.project(entry)
            first, second = substring(ring, offset, ring.length), substring(ring, 0, offset)
            coords = lambda g: list(g.coords)
            lap = coords(first) + coords(second)[1:]
            route = [origin, entry.coords[0]] + lap[1:] + [origin]
            route = [(round(x, 6), round(y, 6)) for x, y in route]
            line = LineString(route[1:-1])
            if not stock.buffer(.005).covers(line):
                raise ValueError("Rounded lap leaves deposited stock")
            return route, dict(loop_source=label, loop_mm=ring.length,
                               connector_each_way_mm=connector.length,
                               connector_hop_mm=.4, low_travel_mm=line.length,
                               total_added_xy_mm=LineString(route).length,
                               loop_clearance_to_stock_edge_mm=ring.distance(stock.boundary),
                               route_outside_stock_mm=line.difference(stock.buffer(.005)).length)
    raise ValueError("No reachable closed wall loop at this departure")


def insert(source, output, report_path, height=.2, speed=10.):
    if source.resolve() == output.resolve():
        raise ValueError("Keep the native source archive separate")
    if not .1 <= height <= .4 or not 1 <= speed <= 10:
        raise ValueError("This trial supports 0.1–0.4 mm height and 1–10 mm/s")
    with zipfile.ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    original = members[MEMBER]
    if hashlib.md5(original).hexdigest() != members[MEMBER + ".md5"].decode().strip().lower():
        raise ValueError("Source G-code checksum differs")
    if BEGIN.encode() in original:
        raise ValueError("Source already has departure laps")
    lines = original.decode().splitlines(keepends=True)
    moves = list(movements(lines))
    by_index = {m["index"]: m for m in moves}
    inner = read_runs(original.decode(), features=("Inner wall",))
    outer = read_runs(original.decode(), features=("Outer wall", "Overhang wall"))
    additions, rows = {}, []
    current_moves, current_obj = [], None
    for index, raw in enumerate(lines):
        if raw.startswith("; start printing object, unique label id:"):
            current_moves, current_obj = [], int(raw.rsplit(":", 1)[1])
        if index in by_index and current_obj is not None:
            current_moves.append(by_index[index])
        if not raw.startswith("; stop printing object, unique label id:"):
            continue
        extrusions = [m for m in current_moves if "E" in m["words"] and m["words"]["E"] >= 0
                      and ("X" in m["words"] or "Y" in m["words"])]
        last = extrusions[-1]
        tail = [m for m in current_moves if m["index"] > last["index"]]
        departure = tail[0]
        words = departure["words"]
        if not (set(words) <= {"E", "F"} and words.get("E", 0) < 0):
            raise ValueError(f"Object {current_obj}: departure needs a standing retraction")
        if not departure["absolute"] or not departure["relative_e"]:
            raise ValueError("Object requires G90/M83")
        if abs(departure["end"][2] - departure["layer_z"]) > .00001:
            raise ValueError("Departure is not at nominal layer height")
        if any("E" in m["words"] or m["end"][:2] != departure["end"][:2]
               for m in tail[1:]):
            raise ValueError("Unexpected XY or extrusion after the final retraction")
        layer, obj, z = departure["layer"], current_obj, departure["layer_z"]
        paths = []
        for move in extrusions:
            if move["feature"] in ("Brim", "Skirt", "Wipe tower"):
                continue
            a, b, w = move["start"], move["end"], move["words"]
            points = (arc_xy(a, b, w.get("I", 0.), w.get("J", 0.),
                             move["command"] == "G2", chord=.1)
                      if move["command"] in ("G2", "G3") else [b[:2]])
            paths.append(([a[:2]] + points, move["width"]))
        local = lambda runs: [r for r in runs if r["layer"] + 1 == layer and r["object"] == obj]
        route, measure = wall_lap(paths, departure["end"][:2], local(inner), local(outer))
        block = [f"{BEGIN} layer={layer} object={obj}\n",
                 f"G1 Z{z + .4:.6f} F600\n",
                 f"G1 X{route[1][0]:.6f} Y{route[1][1]:.6f} F{speed * 60:.3f}\n",
                 f"G1 Z{z + height:.6f} F600\n"]
        block += [f"G1 X{x:.6f} Y{y:.6f} F{speed * 60:.3f}\n" for x, y in route[2:-1]]
        # Restore XY and modal feed. Leave Z at the full hop before native
        # lift or inter-object travel; no low crossing is introduced.
        block += [f"G1 Z{z + .4:.6f} F600\n",
                  f"G1 X{route[0][0]:.6f} Y{route[0][1]:.6f} F{speed * 60:.3f}\n",
                  f"G1 F{departure['feed']:.3f}\n", END + "\n"]
        additions[departure["index"]] = block
        rows.append(dict(layer=layer, object=obj, after_source_line=departure["index"] + 1,
                         print_z_mm=z, lap_z_mm=z + height, crossing_z_mm=z + .4,
                         route_xy_mm=route, **measure))
        current_obj = None
    if not rows:
        raise ValueError("No departures found")
    rewritten = "".join(raw + "".join(additions.get(i, [])) for i, raw in enumerate(lines)).encode()
    # Removing exactly our blocks must reproduce every native line byte for byte.
    stripped, in_lap = [], False
    for raw in rewritten.decode().splitlines(keepends=True):
        if raw.startswith(BEGIN):
            in_lap = True
        elif raw.startswith(END):
            in_lap = False
        elif not in_lap:
            stripped.append(raw)
    if "".join(stripped).encode() != original:
        raise ValueError("A native line changed")
    original_e = [(m["raw"], m["start"], m["end"], m["feed"])
                  for m in moves if "E" in m["words"]]
    rewritten_e = [(m["raw"], m["start"], m["end"], m["feed"])
                   for m in movements(rewritten.decode().splitlines(keepends=True)) if "E" in m["words"]]
    if original_e != rewritten_e:
        raise ValueError("An extrusion/retraction start, endpoint or modal feed changed")
    members[MEMBER] = rewritten
    members[MEMBER + ".md5"] = hashlib.md5(rewritten).hexdigest().encode()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zfile:
        for name, data in members.items():
            zfile.writestr(name, data)
    with zipfile.ZipFile(output) as zfile:
        if zfile.testzip() is not None:
            raise ValueError("Output ZIP checksum differs")
    report = dict(source=source.name, source_sha256=digest(source.read_bytes()),
                  archive=output.name, archive_sha256=digest(output.read_bytes()),
                  native_gcode_sha256=digest(original), gcode_sha256=digest(rewritten),
                  embedded_md5=hashlib.md5(rewritten).hexdigest(),
                  laps=len(rows), lap_height_mm=height, lap_speed_mm_s=speed,
                  normal_hop_mm=.4, native_lines_unchanged=True,
                  native_e_commands_and_motion_states_unchanged=True,
                  e_command_count=len(original_e),
                  modified_zip_members=[MEMBER, MEMBER + ".md5"],
                  loop_sources=dict(Counter(r["loop_source"] for r in rows)),
                  added_xy_mm=sum(r["total_added_xy_mm"] for r in rows),
                  nominal_added_motion_seconds=sum(r["total_added_xy_mm"] / speed
                                                   + 2 * (.4 - height) / 10 for r in rows),
                  scope="Object-end departures, including before timelapse. Intra-object leg transfers are native.",
                  native_preview_scope="Native thumbnails and time estimates do not depict the inserted moves.",
                  departures=rows)
    report_path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "departures"}, indent=2))
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--height", type=float, default=.2)
    parser.add_argument("--speed", type=float, default=10.)
    args = parser.parse_args()
    insert(args.source, args.output, args.report, args.height, args.speed)
