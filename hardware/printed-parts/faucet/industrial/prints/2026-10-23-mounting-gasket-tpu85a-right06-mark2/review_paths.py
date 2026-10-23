"""Manually review emitted gasket deposition and attachment chords."""
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
from travel_survey import arc_xy
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


def chords(ms, outlines, minimum_run_mm=0):
    groups = []
    for i, m in deposition(ms):
        if not groups or any(math.dist(p["start"], p["end"]) > 1e-8 or
                             p["words"].get("E", 0) < 0
                             for p in ms[groups[-1][-1][0] + 1:i]):
            groups.append([])
        groups[-1].append((i, m))
    groups = [g for g in groups if sum(math.dist(m["start"], m["end"]) for _, m in g) >= minimum_run_mm]
    rows = []
    for a, b in zip(groups, groups[1:]):
        first, last = a[-1][1], b[0][1]
        if math.dist(first["end"][:2], last["start"][:2]) < 1e-8:
            continue
        line = LineString([first["end"][:2], last["start"][:2]])
        stock = outlines[(last["layer"], 0)].buffer(1e-5)
        rows.append(dict(from_layer=first["layer"], to_layer=last["layer"],
                         outside_stock_mm=line.difference(stock).length,
                         start_xy_mm=first["end"][:2], end_xy_mm=last["start"][:2]))
    return rows


def main():
    source_path = HERE / (STEM + ".gcode.3mf")
    path = HERE / (STEM + "-continuous-layers.gcode.3mf")
    native_raw, native_ms = load(source_path)
    raw, ms = load(path)
    originals = [m for _, m in deposition(native_ms)]
    stock, _ = model_layer_outlines(source_path, originals)
    source = {m["index"] + 1: m for m in originals}
    tagged, tag, tags = defaultdict(list), None, {}
    for index, line in enumerate(raw.decode().splitlines()):
        if line.startswith("; GASKET_DEPOSITION_SOURCE:"):
            kind, original_line = line.split(":", 1)[1].split()
            assert kind == "native"
            tag = int(original_line)
        tags[index] = tag
    for _, m in deposition(ms):
        assert tags[m["index"]] in source
        tagged[tags[m["index"]]].append(m)
    assert set(tagged) == set(source)
    e_difference, path_difference, length_difference, flow = 0.0, 0.0, 0.0, 0.0
    for index, parts in tagged.items():
        original = source[index]
        e_difference = max(e_difference, abs(sum(m["words"]["E"] for m in parts) - original["words"]["E"]))
        pts = [original["start"][:2]]
        if original["command"] in ("G2", "G3"):
            w = original["words"]
            pts += arc_xy(original["start"], original["end"], w.get("I", 0), w.get("J", 0),
                          original["command"] == "G2", chord=.025)
        else:
            pts += [original["end"][:2]]
        reference = LineString(pts)
        length = 0.0
        for m in parts:
            length += math.dist(m["start"][:2], m["end"][:2])
            path_difference = max(path_difference, reference.distance(Point(m["start"][:2])),
                                  reference.distance(Point(m["end"][:2])))
            flow = max(flow, m["words"]["E"] * math.pi * (1.75 / 2)**2 * m["feed"] / 60 /
                       math.dist(m["start"][:2], m["end"][:2]))
            assert m["width"] == original["width"] and m["feature"] == original["feature"]
            assert m["layer"] == original["layer"]
            assert abs(m["start"][2] - original["end"][2]) < 1e-7
            assert abs(m["end"][2] - original["end"][2]) < 1e-7
        length_difference = max(length_difference, abs(reference.length - length))
    prefix = b"".join(native_raw.splitlines(keepends=True)[:originals[0]["index"]])
    suffix = b"".join(native_raw.splitlines(keepends=True)[originals[-1]["index"] + 1:])
    assert raw.startswith(prefix) and raw.endswith(suffix)
    assert math.dist(deposition(ms)[0][1]["start"], originals[0]["start"]) < 1e-6
    suffix_start = len(raw.splitlines()) - len(suffix.splitlines())
    final_state = next(m for m in reversed(ms) if m["index"] < suffix_start)
    assert math.dist(final_state["end"], originals[-1]["end"]) < 1e-6
    assert final_state["feed"] == originals[-1]["feed"]
    basic, conservative, baseline = chords(ms, stock), chords(ms, stock, 1.0), chords(native_ms, stock)
    dep = deposition(ms)
    body = ms[dep[0][0]:dep[-1][0] + 1]
    retractions = sum(m["words"].get("E", 0) < 0 for m in body)
    hops = sum(m["words"].get("E", 0) <= 0 and abs(m["end"][2] - m["start"][2]) > .181 for m in body)
    camera = len(re.findall(rb"^\s*M971(?:1)?\b", raw, re.M))
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", raw, re.M)]
    holes = {str(layer): sum(len(p.interiors) for p in getattr(shape, "geoms", [shape]))
             for (layer, _), shape in stock.items()}
    passed = (e_difference < 1e-6 and path_difference < .001 and length_difference < .005
              and flow <= 2.201 and all(r["outside_stock_mm"] < 1e-6 for r in basic + conservative)
              and retractions == hops == camera == 0 and trims == [0.0] and set(holes.values()) == {2})
    report = dict(archive=path.name, archive_sha256=sha(path.read_bytes()), gcode_sha256=sha(raw),
                  native_deposition_commands=len(source), all_source_commands_accounted_once=True,
                  maximum_source_e_difference_mm=e_difference, maximum_path_deviation_mm=path_difference,
                  maximum_command_length_difference_mm=length_difference, added_filament_mm=0,
                  maximum_emitted_volumetric_flow_mm3_s=flow,
                  startup_and_shutdown_bytes_preserved=True, start_and_end_positions_preserved=True,
                  source_startup_sha256=sha(prefix), source_shutdown_sha256=sha(suffix),
                  functional_holes_per_layer=holes, native_potential_opening_chords=sum(r["outside_stock_mm"] > 1e-6 for r in baseline),
                  emitted_free_chords=basic, conservative_minimum_attachment_run_mm=1.0,
                  conservative_free_chords=conservative, in_part_retractions=retractions,
                  in_part_z_hops=hops, camera_commands=camera, trim_commands_mm=trims,
                  pass_review=passed, review_script_sha256=sha(Path(__file__).read_bytes()),
                  scope="Commanded deposition and free-span geometry only; physical stringing, counter seating and spill sealing are unmeasured.")
    (HERE / "emitted-path-review.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({k: v for k, v in report.items() if k not in ("emitted_free_chords", "conservative_free_chords")}, indent=2))
    assert passed


if __name__ == "__main__":
    main()
