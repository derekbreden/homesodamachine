"""Map lower base paths through a smooth shaft transition and join native upper paths."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass, replace
from io import StringIO
import json
import math
from pathlib import Path

import map_base as source

SKIN_TOP = 3.6
FADE_START = 88.0
FADE_END = 144.0
NATIVE_JOIN_Z = 143.48
SHAFT_PIVOT_Y = 12.9
SHAFT_RADIUS = 13.5
BASE_ID = 1901
FLOOR, SHAFT, UPPER = "native tilted base", "graded shaft transition", "native level upper base"
TANGENT = source.SIN / source.COS
END_DERIVATIVE = 1.0 / source.COS - 1.0


@dataclass(frozen=True)
class ShaftTransition:
    """Preserve XY in the straight CAD shaft while shearing each deposited course."""

    physical: tuple[float, float, float]
    fade_end: float = FADE_END
    native_join_z: float = NATIVE_JOIN_Z

    @property
    def phase(self):
        return (self.native_join_z - self.physical[2] + source.SIN * SHAFT_PIVOT_Y) / source.COS - self.fade_end

    def height_and_scale(self, cad_y, height):
        if height <= FADE_START:
            return height, 1.0
        target_offset = TANGENT * (cad_y - SHAFT_PIVOT_Y) + self.phase
        if height >= self.fade_end:
            return self.fade_end + target_offset + (height - self.fade_end) / source.COS, 1.0 / source.COS
        span = self.fade_end - FADE_START
        t = (height - FADE_START) / span
        blend = t * t * (3 - 2 * t)
        start_to_end_pitch = END_DERIVATIVE * span * t * t * (t - 1)
        normal = height + blend * target_offset + start_to_end_pitch
        derivative = 1.0 + (6 * t * (1 - t) / span) * target_offset + END_DERIVATIVE * t * (3 * t - 2)
        return normal, derivative

    def map_point(self, point, donor, physical, move=None, exterior_shift=False):
        x, y, u = (value - origin for value, origin in zip(point, donor))
        n, _ = self.height_and_scale(y, u)
        a, b, c = physical
        return a + x, b + source.COS * y + source.SIN * n, c - source.SIN * y + source.COS * n

    def adjust_moves(self, moves, donor):
        # The volume Jacobian is the normal derivative since CAD X and Y stay fixed.
        for move in moves:
            if not move.deposition or move.e == 0 or max(move.start[2], move.end[2]) <= FADE_START:
                yield move
                continue
            y = (move.start[1] + move.end[1]) * 0.5 - donor[1]
            u = (move.start[2] + move.end[2]) * 0.5 - donor[2]
            _, scale = self.height_and_scale(y, u)
            yield replace(move, e=move.e * scale)

    def join_plane_to_donor(self, point, donor):
        x, y, z = (value - origin for value, origin in zip(point, self.physical))
        return donor[0] + x, donor[1] + source.COS*y - source.SIN*z, donor[2] + self.fade_end


def write_stitched_join(stream, height, section, count, moves, donor, warp, stats, mesh):
    from shaft_ties import ties

    bridge_moves, report = ties(mesh, warp.native_join_z, warp.physical, height)
    walls = [move for move in moves if move.deposition and move.feature in source.WALLS]
    stock_features = {move.feature for move in moves if move.deposition}
    if stock_features - source.WALLS != {"Sparse infill"}:
        raise ValueError(f"Unexpected shaft join features: {stock_features}")
    bridge_moves = [replace(move, start=warp.join_plane_to_donor(move.start, donor),
                            end=warp.join_plane_to_donor(move.end, donor)) for move in bridge_moves]
    written = StringIO()
    source.write_group(written, height, section, count, walls + bridge_moves, donor, warp.physical, stats,
                       map_point=warp.map_point, uphill_wall_runs=True)
    lines = written.getvalue()
    marker = "; FEATURE: Bridge\n"
    if lines.count(marker) != 1:
        raise ValueError("The shaft needs one uninterrupted bridge stitch feature band")
    stream.write(lines.replace(marker, "; HSM_BRIDGE_STITCH: shaft join bridge stitch\n" + marker))
    return report


def original_point(point, *_):
    return point


def relevant_layers(path, keep):
    with path.open() as stream:
        for line in stream:
            if line.startswith("; Z_HEIGHT:"):
                height = float(line.split(":", 1)[1])
                if keep(height):
                    yield height


def audit_upper_source(path, join_z):
    height = 0.0
    object_id = None
    feature = None
    base_count = 0
    with path.open() as stream:
        for line in stream:
            if line.startswith("; MACHINE_END_GCODE_START"):
                break
            if line.startswith("; Z_HEIGHT:"):
                height = float(line.split(":", 1)[1])
            if height <= join_z:
                continue
            if line.startswith("; OBJECT_ID:"):
                object_id = int(line.split(":", 1)[1])
            elif line.startswith("; FEATURE:"):
                feature = line.split(":", 1)[1].strip()
            elif line.startswith(("G1 ", "G2 ", "G3 ")) and " E" in line and (" X" in line or " Y" in line):
                _, words = source.command(line)
                if words.get("E", 0.0) > 0:
                    if object_id != BASE_ID or (feature and feature.startswith("Support")):
                        raise ValueError(f"Upper native band has unrelated deposition at {height}, {object_id=}, {feature=}")
                    base_count += 1
    if not base_count:
        raise ValueError("No upper native model extrusion found")
    return base_count


def range_summary(warp):
    pitch = []
    slopes = []
    heights = []
    for index in range(1001):
        t = index / 1000
        u = FADE_START + (warp.fade_end - FADE_START) * t
        w = t * t * (3 - 2 * t)
        normal_slope = w * TANGENT
        physical_slope = (-source.SIN + source.COS * normal_slope) / (source.COS + source.SIN * normal_slope)
        slopes.append(math.degrees(math.atan(physical_slope)))
        for y in (SHAFT_PIVOT_Y - SHAFT_RADIUS, SHAFT_PIVOT_Y + SHAFT_RADIUS):
            n, jacobian = warp.height_and_scale(y, u)
            heights.append(warp.physical[2] - source.SIN * y + source.COS * n)
            # u→n transformed pitch, evaluated along the actual local build normal.
            pitch.append(source.BASE_NORMAL_LAYER * jacobian / math.hypot(1.0, normal_slope))
    return {
        "local_plane_slope_range_degrees": [min(slopes), max(slopes)],
        "physical_fade_z_extent_mm": [min(heights), max(heights)],
        "approx_bead_normal_pitch_range_mm": [min(pitch), max(pitch)],
        "physical_join_z_mm": warp.native_join_z,
        "cad_join_section_offset_mm": warp.phase,
        "donor_normal_fade_extent_mm": [FADE_START, warp.fade_end],
        "cad_shaft_pivot_y_mm": SHAFT_PIVOT_Y,
        "native_upper_first_z_mm": warp.native_join_z + source.BASE_NORMAL_LAYER,
    }


def new_stats():
    return {"road_mm": 0.0, "filament_mm": 0.0, "dz_roads": 0, "features": defaultdict(float),
            "min_xyz": [math.inf] * 3, "max_xyz": [-math.inf] * 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("donor_gcode", type=Path)
    parser.add_argument("donor_report", type=Path)
    parser.add_argument("physical_gcode", type=Path)
    parser.add_argument("physical_report", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--uphill-wall-runs", action="store_true")
    parser.add_argument("--stitch-mesh", type=Path)
    parser.add_argument("--fade-end", type=float, default=FADE_END)
    parser.add_argument("--native-join-z", type=float, default=NATIVE_JOIN_Z)
    args = parser.parse_args()

    donor, physical = source.tape_origin(json.loads(args.donor_report.read_text()),
                                         json.loads(args.physical_report.read_text()))
    warp = ShaftTransition(physical, args.fade_end, args.native_join_z)
    if args.fade_end <= FADE_START:
        raise ValueError("The shaft blend must end above where it begins")
    use_donor = lambda z: SKIN_TOP < z <= warp.fade_end
    use_upper = lambda z: z > warp.native_join_z
    lower_layers = list(relevant_layers(args.donor_gcode, use_donor))
    upper_layers = list(relevant_layers(args.physical_gcode, use_upper))
    if abs(lower_layers[-1] - warp.fade_end) > .0001:
        raise ValueError("The fade must end precisely on a donor course")
    if abs(upper_layers[0] - warp.native_join_z - source.BASE_NORMAL_LAYER) > .0001:
        raise ValueError("The upper source must begin one complete native course above the blend")
    count = len(lower_layers) + len(upper_layers)
    upper_verified = audit_upper_source(args.physical_gcode, warp.native_join_z)
    phase_stats = {phase: new_stats() for phase in (FLOOR, SHAFT, UPPER)}
    phase_layers = defaultdict(int)
    section = 0
    stitched = None
    with args.output.open("w") as stream:
        for height, moves in source.groups(args.donor_gcode):
            z = float(height)
            if z > warp.fade_end:
                break
            if not use_donor(z):
                continue
            laid = source.active(moves)
            if not laid:
                continue
            phase = FLOOR if z <= FADE_START else SHAFT
            section += 1
            phase_layers[phase] += 1
            stream.write(f"; HSM_DONOR_PHASE: {phase}\n")
            adjusted = list(warp.adjust_moves(laid, donor))
            if z == warp.fade_end and args.stitch_mesh is not None:
                stitched = write_stitched_join(stream, height, section, count, adjusted, donor, warp,
                                               phase_stats[phase], args.stitch_mesh)
            else:
                source.write_group(stream, height, section, count, adjusted, donor, physical, phase_stats[phase],
                                   map_point=warp.map_point, uphill_wall_runs=args.uphill_wall_runs)
        for height, moves in source.groups(args.physical_gcode):
            z = float(height)
            if not use_upper(z):
                continue
            laid = source.active(moves)
            if not laid:
                continue
            section += 1
            phase_layers[UPPER] += 1
            stream.write(f"; HSM_DONOR_PHASE: {UPPER}\n; HSM_UPPER_NATIVE_Z: {height}\n")
            progress = warp.fade_end + z - warp.native_join_z
            source.write_group(stream, f"{progress:.5f}", section, count, laid,
                               donor, physical, phase_stats[UPPER], map_point=original_point)
    summary = range_summary(warp)
    summary.update({"donor_gcode_sha256": source.file_hash(args.donor_gcode),
                    "physical_gcode_sha256": source.file_hash(args.physical_gcode),
                    "candidate_gcode_sha256": source.file_hash(args.output),
                    "early_donor_origin_mm": donor, "physical_seat_origin_mm": physical,
                    "native_upper_positive_source_roads_audited": upper_verified,
                    "emitted_events_by_phase": phase_layers,
                    "emitted_deposition_by_phase": phase_stats,
                    "shaft_bridge_stitch": stitched,
                    "uphill_wall_runs": args.uphill_wall_runs})
    if section != count:
        raise ValueError("A selected source course contains no deposition")
    args.output.with_suffix(".json").write_text(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
