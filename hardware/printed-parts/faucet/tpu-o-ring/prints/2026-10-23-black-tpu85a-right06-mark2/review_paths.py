"""Manually assess emitted deposition, free chords and the retained spiral."""
from collections import defaultdict
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import zipfile

from prepare_mark2 import STEM

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
sys.path.insert(0, str(ROOT / "future/pump-elbow-exploration"))
from departure_lap import movements, MEMBER
from wall_travel import model_layer_outlines
from shapely.geometry import LineString, Point


def sha(data):
    return hashlib.sha256(data).hexdigest()


def load(path):
    with zipfile.ZipFile(path) as z:
        raw = z.read(MEMBER)
        assert hashlib.md5(raw).hexdigest() == z.read(MEMBER + ".md5").decode().strip().lower()
    return raw, list(movements(raw.decode().splitlines(keepends=True)))


def deposition(ms):
    return [(i, m) for i, m in enumerate(ms) if m["layer"] > 0 and
            m["words"].get("E", -1) > 0 and math.dist(m["start"][:2], m["end"][:2]) > 1e-8]


def runs(ms):
    groups = []
    for i, m in deposition(ms):
        if not groups or any(math.dist(p["start"], p["end"]) > 1e-8 or
                             p["words"].get("E", 0) < 0
                             for p in ms[groups[-1][-1][0] + 1:i]):
            groups.append([])
        groups[-1].append((i, m))
    return groups


def chords(ms, outlines, minimum_run_mm=0):
    groups = [group for group in runs(ms) if
              sum(math.dist(m["start"], m["end"]) for _, m in group) >= minimum_run_mm]
    rows = []
    for a, b in zip(groups, groups[1:]):
        first, last = a[-1][1], b[0][1]
        if math.dist(first["end"][:2], last["start"][:2]) < 1e-8:
            continue
        line = LineString([first["end"][:2], last["start"][:2]])
        stock = outlines[(min(last["layer"], 3), 0)].buffer(1e-5)
        rows.append(dict(from_layer=first["layer"], to_layer=last["layer"],
                         outside_stock_mm=line.difference(stock).length,
                         minimum_radius_mm=line.distance(Point(177.5, 160)),
                         start_xy_mm=first["end"][:2], end_xy_mm=last["start"][:2]))
    return rows


def main():
    native_path = HERE / (STEM + ".gcode.3mf")
    path = HERE / (STEM + "-continuous-cap.gcode.3mf")
    native_raw, native_ms = load(native_path)
    raw, ms = load(path)
    original_cap = [m for _, m in deposition(native_ms) if m["layer"] <= 3]
    stock, _ = model_layer_outlines(native_path, original_cap)
    source = {m["index"] + 1: m for m in original_cap}
    tagged, tag, tagged_moves = defaultdict(list), None, {}
    for index, line in enumerate(raw.decode().splitlines()):
        if line.startswith("; CAP_DEPOSITION_SOURCE:"):
            kind, original_line = line.split(":", 1)[1].split()
            assert kind == "native", "No extra cap deposition is selected"
            tag = int(original_line)
        if line == "; NATIVE_SPIRAL_CONTINUES":
            tag = None
        tagged_moves[index] = tag
    for _, m in deposition(ms):
        if m["layer"] <= 3:
            assert tagged_moves[m["index"]] in source
            tagged[tagged_moves[m["index"]]].append(m)
    assert set(tagged) == set(source)
    e_difference = max(abs(sum(m["words"]["E"] for m in tagged[i]) - source[i]["words"]["E"])
                       for i in source)
    path_difference = 0.0
    for i, parts in tagged.items():
        original = LineString([source[i]["start"][:2], source[i]["end"][:2]])
        for m in parts:
            path_difference = max(path_difference,
                                  original.distance(Point(m["start"][:2])),
                                  original.distance(Point(m["end"][:2])))
            assert m["width"] == source[i]["width"]
            assert m["feature"] == source[i]["feature"]
            assert abs(m["end"][2] - source[i]["end"][2]) < 1e-7
    native_helix = next(m for _, m in deposition(native_ms)
                        if m["end"][2] > m["start"][2] + 1e-7)
    suffix = b"".join(native_raw.splitlines(keepends=True)[native_helix["index"]:])
    assert raw.endswith(suffix)
    basic = chords(ms, stock)
    conservative = chords(ms, stock, 1.0)
    baseline = chords(native_ms, stock)
    dep = deposition(ms)
    body = ms[dep[0][0]:dep[-1][0] + 1]
    camera = len(re.findall(rb"^\s*M971(?:1)?\b", raw, re.M))
    retractions = sum(m["words"].get("E", 0) < 0 for m in body)
    hops = sum(m["words"].get("E", 0) <= 0 and abs(m["end"][2] - m["start"][2]) > .181 for m in body)
    report = dict(archive=path.name, archive_sha256=sha(path.read_bytes()), gcode_sha256=sha(raw),
                  native_cap_deposition_commands=len(source), all_cap_source_commands_accounted_once=True,
                  maximum_source_e_difference_mm=e_difference, maximum_cap_path_deviation_mm=path_difference,
                  added_cap_filament_mm=0, native_spiral_and_shutdown_bytes_preserved=True,
                  source_spiral_and_shutdown_sha256=sha(suffix), native_solid_cap_height_mm=.66,
                  native_bottom_layers=3, modeled_cap_height_mm=2.1,
                  free_attachment_chords=len(basic),
                  maximum_chord_outside_stock_mm=max((r["outside_stock_mm"] for r in basic), default=0),
                  conservative_attachment_minimum_deposition_mm=1,
                  conservative_chords=len(conservative),
                  maximum_conservative_chord_outside_stock_mm=max((r["outside_stock_mm"] for r in conservative), default=0),
                  native_cap_chords_crossing_hole=sum(r["outside_stock_mm"] > 1e-5 for r in baseline),
                  native_maximum_chord_outside_stock_mm=max((r["outside_stock_mm"] for r in baseline), default=0),
                  in_part_retractions=retractions, in_part_z_hops=hops, camera_commands=camera,
                  scope="Manual emitted-command assessment. All holes retained in native cap sections. Strand adhesion, printed fit and sealing remain physical results. Startup/shutdown travel is excluded. Saved spiral recipe commands three solid cap layers (0.66 mm), while CAD has a 2.1 mm cap region.",
                  conservative_outliers=[r for r in conservative if r["outside_stock_mm"] > 1e-5])
    (HERE / "emitted-path-review.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2), flush=True)
    assert e_difference < 1e-6 and path_difference < 1e-5
    assert report["maximum_chord_outside_stock_mm"] < 1e-5
    assert report["maximum_conservative_chord_outside_stock_mm"] < 1e-5
    assert retractions == hops == camera == 0


if __name__ == "__main__":
    main()
