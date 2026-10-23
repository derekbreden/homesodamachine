"""Join the sleeve's planar cap paths; retain its native spiral wall verbatim.

Run manually after prepare_mark2.py. Does not send a print or run on builds.
"""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import sys
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
sys.path.insert(0, str(ROOT / "future/pump-elbow-exploration"))
from deposited_links import layer_graph, connect, pair_ends, tour, visible
from departure_lap import movements, MEMBER
from wall_travel import model_layer_outlines
from prepare_mark2 import STEM


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    source = HERE / (STEM + ".gcode.3mf")
    output = HERE / (STEM + "-continuous-cap.gcode.3mf")
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
    helix = next(m for m in native if m["end"][2] > m["start"][2] + 1e-7)
    cap = [m for m in native if m["index"] < helix["index"]]
    assert {m["layer"] for m in cap} == {1, 2, 3}
    assert all(m["absolute"] and m["relative_e"] and
               abs(m["start"][2] - m["end"][2]) < 1e-7 for m in cap)
    stock, outline = model_layer_outlines(source, cap)
    grouped = defaultdict(list)
    for m in cap:
        grouped[m["layer"]].append(m)
    graphs, counts, duplicates = {}, {}, {}
    for layer, moves in grouped.items():
        graph = layer_graph(moves)
        counts[layer] = connect(graph, stock[(layer, 0)].buffer(1e-6))
        _, duplicates[layer] = pair_ends(graph, stock[(layer, 0)].buffer(1e-6))
        graphs[layer] = graph
    start1 = cap[0]["start"][:2]
    start3 = helix["start"][:2]
    allowed = stock[(2, 0)].buffer(1e-6)
    choices = [p for p in graphs[2].points
               if visible(allowed, start1, p) and visible(allowed, p, start3)]
    if not choices:
        raise ValueError("No contained straight links between the three layer tours")
    start2 = min(choices, key=lambda p: math.dist(start1, p) + math.dist(p, start3))
    starts = {1: start1, 2: start2, 3: start3}
    body, rows = [], []
    for layer, graph in sorted(graphs.items()):
        shape = stock[(layer, 0)].buffer(1e-6)
        start = min(range(len(graph.points)), key=lambda p: math.dist(graph.points[p], starts[layer]))
        assert math.dist(graph.points[start], starts[layer]) < 1e-6
        z = grouped[layer][0]["layer_z"]
        if layer > 1:
            body += [f"; CHANGE_LAYER\n; Z_HEIGHT: {z}\n; LAYER_HEIGHT: 0.18\n",
                     f"; layer num/total_layer_count: {layer}/86\nM73 L{layer}\nM991 S0 P{layer-1}\n"]
            marker = next(i for i, line in enumerate(lines)
                          if line.startswith(f"; layer num/total_layer_count: {layer}/"))
            previous = max(i for i in range(marker) if lines[i].startswith("; CHANGE_LAYER"))
            body += [line for line in lines[previous:grouped[layer][0]["index"]]
                     if line.split(" ", 1)[0] in ("M104", "M106", "M1003")]
        body += [f"; CONTINUOUS_CAP_LAYER {layer}\n; OBJECT_ID: 1574\n",
                 f"G1 Z{z:.6f} F600\n",
                 f"G1 X{starts[layer][0]:.6f} Y{starts[layer][1]:.6f} F6000\n"]
        pending, free_chords, extra = [], 0, 0.0

        def flush():
            nonlocal free_chords
            if not pending:
                return
            a, b = pending[0][0], pending[-1][1]
            if not visible(shape, a, b):
                raise ValueError(f"Free attachment chord leaves cap stock on layer {layer}")
            if math.dist(a, b) > 1e-8:
                body.append(f"G1 X{b[0]:.6f} Y{b[1]:.6f} F6000\n")
                free_chords += 1
            pending.clear()

        for key, p, q in tour(graph, start):
            edge = graph.edges[key]
            a, b = graph.points[p], graph.points[q]
            if edge["kind"] == "travel":
                pending.append((a, b))
                continue
            flush()
            if edge["kind"] != "native":
                extra += edge["e"]
            body += [f"; FEATURE: {edge['feature']}\n; LINE_WIDTH: {edge['width']:.6f}\n",
                     f"; CAP_DEPOSITION_SOURCE: {edge['kind']} {edge['source_line']}\n",
                     f"M204 S{edge['acceleration']:.0f}\n",
                     f"G1 X{b[0]:.6f} Y{b[1]:.6f} E{edge['e']:.9f} F{edge['feed']:.3f}\n"]
        flush()
        rows.append(dict(layer=layer, native_components=counts[layer],
                         native_deposition_e_mm=sum(m["words"]["E"] for m in grouped[layer]),
                         added_deposition_e_mm=extra, free_chords=free_chords,
                         duplicated_features=[graph.edges[k].get("feature") for k in duplicates[layer]],
                         start_end_xy_mm=starts[layer]))
    marker = max(i for i in range(helix["index"]) if lines[i].startswith("; CHANGE_LAYER"))
    body += [line for line in lines[marker:helix["index"]]
             if line.startswith(("; CHANGE_LAYER", "; Z_HEIGHT:", "; LAYER_HEIGHT:",
                                 "; layer num/total_layer_count:", "M73 ", "M991 ",
                                 "M104 ", "M106 ", "M1003 "))]
    body += ["; NATIVE_SPIRAL_CONTINUES\n; FEATURE: Outer wall\n; LINE_WIDTH: 0.62\n",
             f"M204 S{helix['acceleration']:.0f}\nG1 F{helix['feed']:.3f}\n"]
    rewritten = ("".join(lines[:cap[0]["index"]]) + "".join(body) +
                 "".join(lines[helix["index"]:])).encode()
    members[MEMBER] = rewritten
    members[MEMBER + ".md5"] = hashlib.md5(rewritten).hexdigest().encode()
    with zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in members.items():
            z.writestr(name, data)
    report = dict(source=source.name, source_archive_sha256=sha(source.read_bytes()),
                  archive=output.name, archive_sha256=sha(output.read_bytes()),
                  gcode_sha256=sha(rewritten), cap_layers=rows,
                  native_spiral_from_source_line=helix["index"] + 1,
                  native_spiral_and_shutdown_sha256=sha("".join(lines[helix["index"]:]).encode()),
                  source_native_cap_height_mm=helix["start"][2], outline=outline,
                  scope="Only the three planar cap layers are spliced into deposited tours. Native spiral and shutdown bytes are retained; startup is retained. No sending or physical acceptance.")
    (HERE / "cap-processing.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k != "outline"}, indent=2))


if __name__ == "__main__":
    main()
