"""Rotate a bed-normal donor slice into the physical Sculpted base's printing frame."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, replace
import hashlib
import json
import math
from pathlib import Path
import re
from typing import Iterator

WORD = re.compile(r"([A-Z])(-?(?:\d+(?:\.\d*)?|\.\d+))")
BASE_NORMAL_LAYER = 0.24
EXTRUSION_Z_FEED = 7.5 * 60
TRAVEL_Z_FEED = 15.0 * 60
LOCAL_LIFT = 1.10
TRAVEL_FEED = 100.0 * 60
WALLS = frozenset(("Outer wall", "Overhang wall", "Inner wall", "Floating vertical shell"))
ROT = math.radians(15)
SIN, COS = math.sin(ROT), math.cos(ROT)
RETRACT_SPEED = 1800
RETRACT_AMOUNT = 0.8
ARC_SEGMENT = 0.75
SPATIAL = 1e-7


@dataclass
class Move:
    """A donor move read at its original source position, with active bead information."""
    start: tuple[float, float, float]
    end: tuple[float, float, float]
    feed: float
    e: float | None
    arc: tuple[bool, float, float] | None
    feature: str
    width: str
    bead_height: str
    fan: int
    acceleration: int
    layer: str

    @property
    def deposition(self) -> bool:
        return bool(self.e is not None and self.e >= 0
                    and (self.arc is not None or math.dist(self.start, self.end) > SPATIAL))


def command(line: str) -> tuple[str, dict[str, float]]:
    code = line.split(";", 1)[0].strip()
    op = code.split(None, 1)[0] if code else ""
    args = {key: float(value) for key, value in WORD.findall(code[len(op):])}
    return op, args


def read_moves(source: Path) -> Iterator[Move]:
    """Consume the complete motion context; yield only part moves in the print body."""
    xyz = (0.0, 0.0, 0.0)
    started = False
    absolute = True
    relative_e = True
    feed = 0.0
    feature = "Custom"
    layer = "0"
    height = width = ""
    fan = 0
    acceleration = 6000
    with source.open() as stream:
        for line in stream:
            if line.startswith("; MACHINE_START_GCODE_END"):
                started = True
            elif line.startswith("; MACHINE_END_GCODE_START"):
                break
            elif line.startswith("; Z_HEIGHT:"):
                layer = line.split(":", 1)[1].strip()
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif line.startswith("; LINE_WIDTH:"):
                width = line.split(":", 1)[1].strip()
            elif line.startswith("; LAYER_HEIGHT:"):
                height = line.split(":", 1)[1].strip()
            if line.startswith(";"):
                continue
            op, args = command(line)
            if op == "G90" or op == "G91":
                absolute = op == "G90"
            elif op == "M83" or op == "M82":
                relative_e = op == "M83"
            elif op == "M106" and args.get("P", 1) == 1:
                fan = round(args.get("S", 255))
            elif op == "M204" and "S" in args:
                acceleration = round(args["S"])
            if op not in ("G0", "G1", "G2", "G3"):
                continue
            if absolute:
                target = tuple(args.get(letter, previous) for letter, previous in zip("XYZ", xyz))
            else:
                target = tuple(previous + args.get(letter, 0.0) for letter, previous in zip("XYZ", xyz))
            feed = args.get("F", feed)
            if started and layer != "0":
                if not absolute or not relative_e or feed <= 0.0:
                    raise ValueError("The donor print body must have G90, M83 and a valid feed")
                planar_arc = None
                if op in ("G2", "G3"):
                    if "R" in args or args.get("P", 1) != 1:
                        raise ValueError(f"Unexpected donor arc: {line.strip()}")
                    planar_arc = (op == "G2", args.get("I", 0.0), args.get("J", 0.0))
                yield Move(xyz, target, feed, args.get("E"), planar_arc,
                           feature, width, height, fan, acceleration, layer)
            xyz = target


def groups(source: Path) -> Iterator[tuple[str, list[Move]]]:
    """Split at the donor slice heights, including independent support layers."""
    layer = None
    moves = []
    for move in read_moves(source):
        if layer is not None and move.layer != layer:
            yield layer, moves
            moves = []
        layer = move.layer
        moves.append(move)
    if layer is not None:
        yield layer, moves


def active(moves: list[Move]) -> list[Move]:
    first = next((n for n, move in enumerate(moves) if move.deposition), len(moves))
    last = next((n for n, move in enumerate(reversed(moves)) if move.deposition), len(moves))
    return moves[first:len(moves) - last] if first < len(moves) else []


def points(move: Move) -> Iterator[tuple[float, float, float]]:
    """Linearize XY-plane arcs before rotation so the firmware moves in the right plane."""
    if move.arc is None:
        yield move.end
        return
    cw, i, j = move.arc
    x, y, z = move.start
    u, v, w = move.end
    cx, cy = x + i, y + j
    radius = math.hypot(i, j)
    if radius < SPATIAL:
        if math.dist(move.start, move.end) > SPATIAL:
            yield move.end
        return
    angle = math.atan2(y - cy, x - cx)
    turn = math.atan2(v - cy, u - cx) - angle
    if cw and turn >= -SPATIAL:
        turn -= math.tau
    elif not cw and turn <= SPATIAL:
        turn += math.tau
    count = max(1, math.ceil(abs(turn) * radius / ARC_SEGMENT))
    for index in range(1, count):
        fraction = index / count
        at = angle + turn * fraction
        yield (cx + radius * math.cos(at), cy + radius * math.sin(at), z + (w - z) * fraction)
    yield move.end


def file_hash(path: Path) -> str:
    with path.open("rb") as file:
        return hashlib.file_digest(file, "sha256").hexdigest()


def tape_origin(donor_report, physical_report):
    base = next(part for part in donor_report["parts"] if part["identify_id"] == 1901)
    if abs(base["rotation_x_degrees"]) > 1e-9:
        raise ValueError("The donor base has to be horizontal in its CAD frame")
    donor = tuple(t - c for t, c in zip(base["plate_translation_mm"], base["source_center_mm"]))
    physical = tuple(physical_report["base_rim_supports"]["seat_print_world_center_mm"])
    return donor, physical


def transform(point, donor, physical, _move=None):
    x, y, z = (p - d for p, d in zip(point, donor))
    a, b, c = physical
    return a + x, b + COS * y + SIN * z, c - SIN * y + COS * z


def output_point(point):
    return tuple(round(value, 3) for value in point)


def output_feed(start, end, requested, cap):
    """Apply the Z speed ceiling to exactly the motion the firmware receives."""
    start, end = output_point(start), output_point(end)
    dz = abs(end[2] - start[2])
    if dz < SPATIAL:
        return math.floor(requested)
    feed = min(requested, cap * math.dist(start, end) / dz)
    return math.floor(feed + 1e-9)


def write_group(stream, height: str, section: int, total: int, moves: list[Move], donor, physical, seen,
                *, map_point=transform, uphill_wall_runs=False):
    """Write a restartable physical band. The plate scheduler owns travel to the entry."""
    if uphill_wall_runs:
        return write_ordered_group(stream, height, section, total, moves, donor, physical, seen, map_point)
    entry = map_point(moves[0].start, donor, physical, moves[0])
    exit = map_point(moves[-1].end, donor, physical, moves[-1])
    xyz = lambda p: " ".join(f"{value:.3f}" for value in p)
    stream.write(f"; whole-base course {section} of {total}\n")
    stream.write(f"; HSM_ENTRY_XYZ: {xyz(entry)}\n; HSM_ENTRY_RETRACT_MM: {RETRACT_AMOUNT}\n")
    stream.write(f"; HSM_EXIT_XYZ: {xyz(exit)}\n; HSM_EXIT_RETRACT_MM: {RETRACT_AMOUNT}\n")
    stream.write(f"; HSM_NORMAL_Z: {height}\n; OBJECT_ID: 1901\n")
    stream.write(f"G90\nM83\nG1 E{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
    flags = {}
    cursor = entry
    for move in moves:
        mapped_end = map_point(move.end, donor, physical, move)
        if move.deposition:
            expected = map_point(move.start, donor, physical, move)
            if math.dist(cursor, expected) > 0.002:
                raise ValueError(f"Support remap lost nozzle continuity at {height}: {cursor} -> {expected}")
            for key, value in (("FEATURE", move.feature), ("LINE_WIDTH", move.width), ("LAYER_HEIGHT", move.bead_height)):
                if flags.get(key) != value:
                    stream.write(f"; {key}: {value}\n")
                    flags[key] = value
        for key, value in (("M106", move.fan), ("M204", move.acceleration)):
            if flags.get(key) != value:
                stream.write(f"{key} S{value}\n")
                flags[key] = value
        prev = cursor
        arc_points = list(points(move)) if move.arc is not None else (move.end,)
        for point in arc_points:
            p = mapped_end if point == move.end else map_point(point, donor, physical, move)
            delta = math.dist(prev, p)
            e = None if move.e is None else move.e / len(arc_points)
            if delta < SPATIAL and not move.deposition:
                p = cursor
            if delta > SPATIAL:
                if output_point(prev) == output_point(p):
                    if e and round(e, 5) != 0:
                        raise ValueError(f"Positive extrusion collapsed to one coordinate at {height}: {prev} -> {p}")
                    prev = p
                    continue
                if any(not -1 < coordinate < 330 for coordinate in p):
                    raise ValueError(f"Requested nozzle coordinate outside the plate or Z travel: {p}")
                dz = abs(prev[2] - p[2])
                cap = EXTRUSION_Z_FEED if move.deposition else TRAVEL_Z_FEED
                feed = output_feed(prev, p, move.feed, cap)
                if move.deposition:
                    seen["road_mm"] += delta
                    if e is not None:
                        seen["filament_mm"] += e
                    seen["features"][move.feature] += delta
                    seen["dz_roads"] += dz > 0.0005
                    for i in range(3):
                        seen["min_xyz"][i] = min(seen["min_xyz"][i], prev[i], p[i])
                        seen["max_xyz"][i] = max(seen["max_xyz"][i], prev[i], p[i])
                line = f"G1 X{p[0]:.3f} Y{p[1]:.3f} Z{p[2]:.3f}"
            elif e is not None:
                line = "G1"
                feed = move.feed
            else:
                continue
            if e is not None:
                line += f" E{e:.5f}"
            line += f" F{math.floor(feed)}"
            stream.write(line + "\n")
            prev = p
        cursor = prev
    stream.write(f"G1 E-{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
    stream.write("; HSM_END_WHOLE_BASE_COURSE\n")


def runs_of(moves: list[Move]) -> Iterator[list[Move]]:
    """Keep consecutive features together, splitting at native travel or retraction."""
    run = []
    for move in moves:
        if move.deposition:
            previous = run[-1] if run else None
            if previous and (previous.feature != move.feature or
                             math.dist(previous.end, move.start) > SPATIAL):
                yield run
                run = []
            run.append(move)
        elif run and (math.dist(move.start, move.end) > SPATIAL or (move.e or 0) < 0):
            yield run
            run = []
    if run:
        yield run


def climbing(run, mapped):
    """Retain each original wall's bead centerline, E and ramp. Divide only at reversals in Z."""
    if any(move.arc is not None for move in run):
        raise ValueError("Split/reverse needs linear wall roads")
    slope_dz = 0.003
    pieces = []
    piece = []
    sign = 0
    for move in run:
        dz = mapped(move.end, move)[2] - mapped(move.start, move)[2]
        direction = (1 if dz > 0 else -1) if abs(dz) > slope_dz else 0
        if direction and sign and direction != sign:
            pieces.append((sign, piece))
            piece = []
        piece.append(move)
        sign = direction or sign
    if piece:
        pieces.append((sign, piece))
    for sign, piece in pieces:
        if sign < 0:
            yield [replace(move, start=move.end, end=move.start) for move in reversed(piece)]
        else:
            yield piece


def write_ordered_group(stream, height, section, total, moves, donor, physical, seen, map_point):
    """Reorder wall runs uphill and replace same-layer non-extruding moves with nozzle hops."""
    from itertools import groupby

    def mapped(point, move):
        return map_point(point, donor, physical, move)

    runs = []
    for feature, same_feature in groupby(runs_of(moves), key=lambda run: run[0].feature):
        if feature in WALLS:
            pieces = [piece for run in same_feature for piece in climbing(run, mapped)]
            runs.extend(sorted(pieces, key=lambda run: mapped(run[0].start, run[0])[2]))
        else:
            runs.extend(same_feature)

    entry = mapped(runs[0][0].start, runs[0][0])
    exit = mapped(runs[-1][-1].end, runs[-1][-1])
    xyz = lambda p: " ".join(f"{v:.3f}" for v in p)
    stream.write(f"; whole-base course {section} of {total}\n")
    stream.write(f"; HSM_ENTRY_XYZ: {xyz(entry)}\n; HSM_ENTRY_RETRACT_MM: {RETRACT_AMOUNT}\n")
    stream.write(f"; HSM_EXIT_XYZ: {xyz(exit)}\n; HSM_EXIT_RETRACT_MM: {RETRACT_AMOUNT}\n")
    stream.write(f"; HSM_NORMAL_Z: {height}\n; OBJECT_ID: 1901\n")
    stream.write(f"G90\nM83\nG1 E{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
    flags = {}
    previous = entry

    def linear(next_point, feed, e=None):
        nonlocal previous
        length = math.dist(previous, next_point)
        dz = abs(next_point[2] - previous[2])
        if output_point(previous) == output_point(next_point):
            if e and round(e, 5) != 0:
                raise ValueError(f"Positive extrusion collapsed to one coordinate at {height}: {previous} -> {next_point}")
            previous = next_point
            return
        z_limit = TRAVEL_Z_FEED if e is None else EXTRUSION_Z_FEED
        feed = output_feed(previous, next_point, feed, z_limit)
        x, y, z = next_point
        rw = f" E{e:.5f}" if e is not None else ""
        stream.write(f"G1 X{x:.3f} Y{y:.3f} Z{z:.3f}{rw} F{feed}\n")
        if e is not None:
            seen["road_mm"] += length
            seen["filament_mm"] += e
            seen["dz_roads"] += dz > .0005
            seen["features"][flags["FEATURE"]] += length
            for i in range(3):
                seen["min_xyz"][i] = min(seen["min_xyz"][i],previous[i],next_point[i])
                seen["max_xyz"][i] = max(seen["max_xyz"][i],previous[i],next_point[i])
        previous = next_point

    for run in runs:
        start = mapped(run[0].start,run[0])
        if math.dist(previous,start) > .002:
            stream.write(f"G1 E-{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
            linear((previous[0],previous[1],previous[2]+LOCAL_LIFT),TRAVEL_Z_FEED)
            linear((start[0],start[1],start[2]+LOCAL_LIFT),TRAVEL_FEED)
            linear(start,TRAVEL_Z_FEED)
            stream.write(f"G1 E{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
        for move in run:
            for key, value in (("FEATURE", move.feature), ("LINE_WIDTH", move.width), ("LAYER_HEIGHT", move.bead_height)):
                if flags.get(key) != value:
                    stream.write(f"; {key}: {value}\n")
                    flags[key] = value
            for key, value in (("M106", move.fan), ("M204", move.acceleration)):
                if flags.get(key) != value:
                    stream.write(f"{key} S{value}\n")
                    flags[key] = value
            arc_points = list(points(move)) if move.arc is not None else (move.end,)
            for point in arc_points:
                linear(mapped(point,move),move.feed,move.e/len(arc_points))
    stream.write(f"G1 E-{RETRACT_AMOUNT:g} F{RETRACT_SPEED}\n")
    stream.write("; HSM_END_WHOLE_BASE_COURSE\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("donor_gcode", type=Path)
    parser.add_argument("donor_report", type=Path)
    parser.add_argument("physical_report", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--first-event-above", type=float, default=3.6)
    parser.add_argument("--last-event-at", type=float, default=300.0)
    parser.add_argument("--uphill-wall-runs", action="store_true")
    args = parser.parse_args()
    donor, physical = tape_origin(json.loads(args.donor_report.read_text()), json.loads(args.physical_report.read_text()))
    heights = []
    for line in args.donor_gcode.open():
        if line.startswith("; Z_HEIGHT:"):
            height = line.split(":", 1)[1].strip()
            if args.first_event_above < float(height) <= args.last_event_at:
                heights.append(height)
    stats = {"road_mm": 0.0, "filament_mm": 0.0, "dz_roads": 0, "features": defaultdict(float),
             "min_xyz": [math.inf] * 3, "max_xyz": [-math.inf] * 3}
    result = {
        "purpose": "Maps the native Sculpted base deposition and travel groups into the existing inclined plate frame.",
        "donor_gcode_sha256": file_hash(args.donor_gcode),
        "donor_first_nominal_layer_mm": BASE_NORMAL_LAYER,
        "donor_origin_mm": donor,
        "approved_seat_origin_mm": physical,
        "physical_x_rotation_degrees": -15,
        "normal_deposition_event_range_mm": [float(heights[0]), float(heights[-1])],
        "donor_layer_events": len(heights),
        "normal_model_nominal_layers_in_range": sum(abs(float(h) / BASE_NORMAL_LAYER - round(float(h) / BASE_NORMAL_LAYER)) < 1e-4 for h in heights),
        "verification_scope": "Rigidly maps source coordinates and relative E. The plate scheduler and collision replay validate final timing and clearance.",
    }
    with args.output.open("w") as stream:
        stream.write("; HSM_PHASE: native tilted base\n")
        section = 0
        for height, moves in groups(args.donor_gcode):
            if args.first_event_above < float(height) <= args.last_event_at:
                laid = active(moves)
                if laid:
                    section += 1
                    write_group(stream, height, section, len(heights), laid, donor, physical, stats, uphill_wall_runs=args.uphill_wall_runs)
    result["transformed_deposition"] = stats
    result["emitted_events"] = section
    result["generated_gcode_sha256"] = file_hash(args.output)
    args.output.with_suffix(".json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
