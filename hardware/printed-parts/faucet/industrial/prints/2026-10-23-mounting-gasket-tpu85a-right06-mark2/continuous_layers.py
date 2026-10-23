"""Reorder native gasket beads into deposited tours; manual, without sending."""
from collections import defaultdict
from functools import cache
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile

from prepare_mark2 import STEM

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
sys.path.insert(0, str(ROOT / "future/pump-elbow-exploration"))
from deposited_links import layer_graph, connect, tour, visible
from departure_lap import movements, MEMBER
from wall_travel import model_layer_outlines


def sha(data):
    return hashlib.sha256(data).hexdigest()


def pair_visible_ends(graph, shape):
    """Minimum-weight perfect visible pairing avoids long deposited returns."""
    odd = [p for p, keys in graph.adj.items() if len(keys) % 2]
    choices = {}
    for index, a in enumerate(odd):
        for b in odd[index + 1:]:
            if visible(shape, graph.points[a], graph.points[b]):
                choices[(a, b)] = math.dist(graph.points[a], graph.points[b])

    @cache
    def matching(remaining):
        if not remaining:
            return 0.0, ()
        a, *others = remaining
        best = math.inf, ()
        for b in others:
            key = (a, b) if (a, b) in choices else (b, a)
            if key not in choices:
                continue
            distance, pairs = matching(tuple(p for p in others if p != b))
            candidate = distance + choices[key], ((a, b),) + pairs
            if candidate[0] < best[0]:
                best = candidate
        return best

    distance, pairs = matching(tuple(odd))
    if not math.isfinite(distance):
        raise ValueError("No perfect contained pairing without added deposition")
    for a, b in sorted(tuple(sorted(pair)) for pair in pairs):
        graph.edge(a, b, kind="travel", reason="minimum_weight_open_path_pair")
    return len(odd)


def main():
    source = HERE / (STEM + ".gcode.3mf")
    output = HERE / (STEM + "-continuous-layers.gcode.3mf")
    with zipfile.ZipFile(source) as z:
        members = {n: z.read(n) for n in z.namelist()}
    raw = members[MEMBER]
    assert hashlib.md5(raw).hexdigest() == members[MEMBER + ".md5"].decode().strip().lower()
    lines = raw.decode().splitlines(keepends=True)
    ms = list(movements(lines))
    acceleration, accelerations = None, {}
    for i, line in enumerate(lines):
        if line.startswith("M204 S"):
            acceleration = float(line.split("S", 1)[1].split()[0])
        accelerations[i] = acceleration
    for m in ms:
        m["acceleration"] = accelerations[m["index"]]
    native = [m for m in ms if m["layer"] > 0 and m["words"].get("E", -1) > 0
              and math.dist(m["start"][:2], m["end"][:2]) > 1e-8]
    assert all(m["absolute"] and m["relative_e"] and
               abs(m["start"][2] - m["layer_z"]) < 1e-7 and
               abs(m["end"][2] - m["layer_z"]) < 1e-7 for m in native)
    stock, outline = model_layer_outlines(source, native)
    grouped = defaultdict(list)
    for m in native:
        grouped[m["layer"]].append(m)
    body, rows = [], []
    last_xy, last_z = native[0]["start"][:2], 0.0
    for layer, moves in sorted(grouped.items()):
        shape = stock[(layer, 0)].buffer(1e-6)
        graph = layer_graph(moves)
        components = connect(graph, shape)
        odd = pair_visible_ends(graph, shape)
        target = native[-1]["end"][:2] if layer == max(grouped) else last_xy
        start = next((p for p in sorted(range(len(graph.points)),
                                       key=lambda p: math.dist(graph.points[p], target))
                      if visible(shape, last_xy, graph.points[p])), None)
        if start is None:
            raise ValueError(f"No contained layer transfer on layer {layer}")
        start_xy = graph.points[start]
        if layer == max(grouped) and math.dist(start_xy, target) > 1e-6:
            raise ValueError("Final tour must retain the native shutdown position")
        z = moves[0]["layer_z"]
        if layer > 1:
            body += [f"; CHANGE_LAYER\n; Z_HEIGHT: {z}\n; LAYER_HEIGHT: {z-last_z:.6f}\n",
                     f"; layer num/total_layer_count: {layer}/{len(grouped)}\n",
                     f"M73 L{layer}\nM991 S0 P{layer-1}\n"]
            marker = next(i for i, line in enumerate(lines)
                          if line.startswith(f"; layer num/total_layer_count: {layer}/"))
            previous = max(i for i in range(marker) if lines[i].startswith("; CHANGE_LAYER"))
            body += [line for line in lines[previous:moves[0]["index"]]
                     if line.split(" ", 1)[0] in ("M104", "M106", "M1003")]
        body += [f"; CONTINUOUS_GASKET_LAYER {layer}\n",
                 f"G1 Z{z:.6f} F600\n",
                 f"G1 X{start_xy[0]:.6f} Y{start_xy[1]:.6f} F6000\n"]
        pending, free_chords, nominal_seconds = [], 0, 0.0

        def flush():
            nonlocal free_chords, nominal_seconds
            if not pending:
                return
            a, b = pending[0][0], pending[-1][1]
            if not visible(shape, a, b):
                raise ValueError(f"Free attachment chord leaves gasket stock on layer {layer}: {a}, {b}")
            if math.dist(a, b) > 1e-8:
                body.append(f"G1 X{b[0]:.6f} Y{b[1]:.6f} F6000\n")
                free_chords += 1
                nominal_seconds += math.dist(a, b) / 100
            pending.clear()

        current_feature, current_width, current_acceleration, current_tag = None, None, None, None
        for key, p, q in tour(graph, start):
            edge = graph.edges[key]
            a, b = graph.points[p], graph.points[q]
            if edge["kind"] == "travel":
                pending.append((a, b))
                continue
            flush()
            assert edge["kind"] == "native"
            if edge["feature"] != current_feature:
                body.append(f"; FEATURE: {edge['feature']}\n")
                current_feature = edge["feature"]
            if edge["width"] != current_width:
                body.append(f"; LINE_WIDTH: {edge['width']:.6f}\n")
                current_width = edge["width"]
            if edge["acceleration"] != current_acceleration:
                body.append(f"M204 S{edge['acceleration']:.0f}\n")
                current_acceleration = edge["acceleration"]
            if edge["source_line"] != current_tag:
                body.append(f"; GASKET_DEPOSITION_SOURCE: native {edge['source_line']}\n")
                current_tag = edge["source_line"]
            body.append(f"G1 X{b[0]:.6f} Y{b[1]:.6f} E{edge['e']:.9f} F{edge['feed']:.3f}\n")
            nominal_seconds += math.dist(a, b) / (edge["feed"] / 60)
        flush()
        rows.append(dict(layer=layer, native_components=components, native_odd_endpoints=odd,
                         native_deposition_e_mm=sum(m["words"]["E"] for m in moves),
                         added_deposition_e_mm=0, free_chords=free_chords,
                         native_deposition_commands=len(moves), start_end_xy_mm=start_xy,
                         nominal_motion_seconds=nominal_seconds))
        last_xy, last_z = start_xy, z
        print(json.dumps(rows[-1]), flush=True)
    prefix = "".join(lines[:native[0]["index"]]).encode()
    suffix = "".join(lines[native[-1]["index"] + 1:]).encode()
    restore = (f"M204 S{native[-1]['acceleration']:.0f}\n"
               f"G1 F{native[-1]['feed']:.3f}\n").encode()
    rewritten = prefix + "".join(body).encode() + restore + suffix
    total_seconds = sum(row["nominal_motion_seconds"] for row in rows)
    completed = 0.0
    for row in rows:
        marker = f"; CONTINUOUS_GASKET_LAYER {row['layer']}\n".encode()
        progress = f"M73 P{min(99,int(100*completed/total_seconds))} R{math.ceil((total_seconds-completed)/60)}\n".encode()
        rewritten = rewritten.replace(marker, marker + progress, 1)
        completed += row["nominal_motion_seconds"]
    members[MEMBER] = rewritten
    members[MEMBER + ".md5"] = hashlib.md5(rewritten).hexdigest().encode()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    report = dict(source=source.name, source_archive_sha256=sha(source.read_bytes()),
                  archive=output.name, archive_sha256=sha(output.read_bytes()),
                  gcode_sha256=sha(rewritten), layers=rows,
                  startup_bytes_sha256=sha(prefix), shutdown_bytes_sha256=sha(suffix),
                  native_start_and_end_positions_preserved=True,
                  nominal_part_motion_seconds=total_seconds, added_deposition_e_mm=0,
                  outline=outline, processing_script_sha256=sha(Path(__file__).read_bytes()),
                  scope="Native beads reordered/reversed into deposited tours with contained straight transfers. No added plastic, geometry edits or sending. Native startup/shutdown bytes retained.")
    (HERE / "layer-processing.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
