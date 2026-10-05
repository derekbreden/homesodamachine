"""Independently read the magnet and valve fit objects in a combined native plate."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET
import zipfile

from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/publish_now.py").is_file())
RC62 = ROOT / "hardware/printed-parts/enclosure/enclosure/magnet-retention/fit-coupons"
sys.path[:0] = [str(ROOT / "hardware/printed-parts/enclosure/nameplate"),
               str(ROOT / "hardware/scripts")]
from verify_mark2_print import segments


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def intervals(geometry, axis):
    if geometry.is_empty:
        return []
    if geometry.geom_type == "LineString":
        return [(geometry.bounds[axis], geometry.bounds[axis + 2])]
    if hasattr(geometry, "geoms"):
        return sorted(span for child in geometry.geoms for span in intervals(child, axis))
    return []


def local_paths(paths, shift, layer):
    return [(r, tuple(r["a"][i] - shift[i] for i in range(2)),
             tuple(r["b"][i] - shift[i] for i in range(2)))
            for r in paths if abs(r["layer"] - layer) < 1e-6]


def rc62_reading(sample, paths, shift):
    rows = []
    for level in (3.32, 6.92, 14.12, 19.88, 20.12):
        mid = level - 0.12
        radius, arc = sample["lower_arc_radius_mm"], sample["lower_arc_center_z_mm"]
        width = (sample["pocket_width_x_mm"] if mid >= arc else
                 2 * math.sqrt(radius ** 2 - (mid - arc) ** 2))
        depth = sample["pocket_depth_y_mm"]
        horizontal, vertical = [], []
        for r, a, b in local_paths(paths, shift, level):
            if r["feature"] != "Outer wall":
                continue
            if abs(a[1] - b[1]) < 1e-6 and min(a[0], b[0]) < 0 < max(a[0], b[0]):
                horizontal.append((a[1], r["width"]))
            if abs(a[0] - b[0]) < 1e-6 and min(a[1], b[1]) < depth / 2 < max(a[1], b[1]):
                vertical.append((a[0], r["width"]))
        front = min(horizontal, key=lambda q: abs(q[0] + q[1] / 2))
        back = min(horizontal, key=lambda q: abs(q[0] - depth - q[1] / 2))
        left = min(vertical, key=lambda q: abs(q[0] + width / 2 + q[1] / 2))
        right = min(vertical, key=lambda q: abs(q[0] - width / 2 - q[1] / 2))
        printed_x = right[0] - right[1] / 2 - left[0] - left[1] / 2
        printed_y = back[0] - back[1] / 2 - front[0] - front[1] / 2
        assert abs(printed_x - width) < 0.015, (sample["label"], level, printed_x, width)
        assert abs(printed_y - depth) < 0.002, (sample["label"], level, printed_y, depth)
        rows.append(dict(layer_z_mm=level, contour_midplane_z_mm=round(mid, 2),
                         expected_gap_x_mm=round(width, 6), emitted_bead_gap_x_mm=round(printed_x, 6),
                         expected_gap_y_mm=depth, emitted_bead_gap_y_mm=round(printed_y, 6)))
    return rows


def valve_reading(sample, paths, shift):
    layers = sorted({r["layer"] for r in paths})
    rows = []
    for center_x, center_z in sample["socket_centers_source_xz_mm"]:
        level = min(layers, key=lambda z: abs(z - center_z))
        section = local_paths(paths, shift, level)
        roads = unary_union([LineString((a, b)).buffer(r["width"] / 2)
                             for r, a, b in section])
        spans = intervals(roads.intersection(LineString(((-25, 2), (25, 2)))), 0)
        left = max(hi for lo, hi in spans if hi < center_x)
        right = min(lo for lo, hi in spans if lo > center_x)
        opening = right - left
        delta_z = level - 0.12 - center_z
        expected = 2 * math.sqrt((sample["socket_diameter_mm"] / 2) ** 2 - delta_z ** 2)
        assert abs(opening - expected) < 0.02, (sample["label"], center_x, level, opening, expected)
        axial = intervals(roads.intersection(LineString(((center_x, -5), (center_x, 6)))), 1)
        floor = max(hi for lo, hi in axial if hi < 0)
        assert abs(floor - sample["socket_floor_y_mm"]) < 0.02
        rows.append(dict(socket_center_xz_mm=[center_x, center_z], layer_z_mm=level,
                         contour_midplane_z_mm=round(level - 0.12, 6), axial_probe_y_mm=2,
                         expected_section_opening_x_mm=round(expected, 6),
                         emitted_bead_opening_x_mm=[round(left, 6), round(right, 6)],
                         emitted_bead_opening_width_mm=round(opening, 6),
                         equivalent_round_diameter_mm=round(2 * math.sqrt((opening / 2) ** 2 + delta_z ** 2), 6),
                         emitted_blind_floor_y_mm=round(floor, 6),
                         nominal_bearing_to_emitted_floor_mm=round(sample["bearing_face_y_mm"] - floor, 6)))
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--preparation", type=Path, required=True)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert not args.output.exists(), "Preserve reviewed output; choose a new review filename"
    prep = json.loads(args.preparation.read_text())
    magnet = json.loads((RC62 / "geometry.json").read_text())
    valve = json.loads((HERE / "geometry.json").read_text())
    samples = {s["name"]: (s, RC62, "rc62") for s in magnet["samples"]}
    samples.update({s["name"]: (s, HERE, "valve") for s in valve["samples"]})
    with zipfile.ZipFile(args.archive) as z:
        assert z.testzip() is None
        payload = z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(payload).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        settings = json.loads(z.read("Metadata/project_settings.config"))
        plate, = ET.fromstring(z.read("Metadata/slice_info.config")).findall("plate")
    metadata = {n.get("key"): n.get("value") for n in plate.findall("metadata")}
    assert metadata["pause_count"] == "0"
    text = payload.decode()
    assert not re.findall(r"^\s*(?:M400\s+U|M0(?:\s|$)|M1(?:\s|$))", text, re.M)
    trims = [float(v) for v in re.findall(r"^\s*G29\.1 Z([-+.\d]+)", text, re.M)]
    assert trims == [0.0, 0.02]
    for key, expected in {"initial_layer_print_height": "0.2", "layer_height": "0.24",
                          "filament_map": ["1"], "filament_nozzle_map": ["0"],
                          "xy_contour_compensation": "0", "xy_hole_compensation": "0",
                          "wall_loops": "2", "sparse_infill_density": "15%",
                          "enable_arc_fitting": "0", "filament_colour": ["#161616"]}.items():
        assert settings[key] == expected, (key, settings[key])
    assert settings["filament_flow_ratio"][0] == "0.9555"
    class TextSource:
        def read_text(self):
            return text
    roads = list(segments(TextSource()))
    result = []
    for part in prep["parts"]:
        if part["name"] not in samples:
            continue
        sample, folder, kind = samples[part["name"]]
        assert sha(folder / sample["stl"]) == sample["stl_sha256"] == part["stl_sha256"]
        assert part["rotation_x_degrees"] == 0 and abs(part["plate_bounds_mm"][0][2]) < 1e-6
        paths = [r for r in roads if r["object"] == part["identify_id"]]
        assert paths and {r["tool"] for r in paths} == {0}
        assert not [r for r in paths if r["feature"].startswith("Support")]
        layers = sorted({r["layer"] for r in paths})
        assert layers[:2] == [0.2, 0.44]
        assert all(abs(b - a - 0.24) < 1e-6 for a, b in zip(layers, layers[1:]))
        first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                             for r in paths if r["layer"] == 0.2])
        overlaps = []
        for r in paths:
            if r["layer"] == 0.44:
                bead = LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                overlaps.append(bead.intersection(first).area / bead.area)
        assert min(overlaps) > 0.5
        shift = [part["plate_translation_mm"][i] - part["source_center_mm"][i] for i in range(3)]
        measurements = (rc62_reading(sample, paths, shift) if kind == "rc62" else
                        valve_reading(sample, paths, shift))
        result.append(dict(label=sample["label"], name=part["name"], kind=kind,
                           identify_id=part["identify_id"], stl_sha256=sample["stl_sha256"],
                           source_to_plate_translation_mm=shift, model_layer_count=len(layers),
                           first_two_layers_z_mm=layers[:2], last_model_layer_z_mm=layers[-1],
                           minimum_second_layer_bead_area_overlap_fraction=min(overlaps),
                           model_tools=[0], support_road_count=0, measured_sections=measurements))
    assert len(result) == 22 and {r["name"] for r in result} == set(samples)
    output = dict(schema_version=1, checked_utc=datetime.now(timezone.utc).isoformat(),
                  status="native_coupon_toolpaths_pass", checks_pass=True,
                  preparation=str(args.preparation.resolve().relative_to(ROOT)),
                  preparation_sha256=sha(args.preparation),
                  archive=str(args.archive.resolve().relative_to(ROOT)), archive_sha256=sha(args.archive),
                  gcode_sha256=hashlib.sha256(payload).hexdigest(), checksum_verified=True,
                  reviewer_source_sha256=sha(Path(__file__)),
                  source_geometry_sha256={str((folder / "geometry.json").relative_to(ROOT)): sha(folder / "geometry.json")
                                           for folder in (RC62, HERE)},
                  emitted_z_trim_commands_mm=trims, fit_object_count=22, samples=result,
                  shared_fit_settings={key: settings[key] for key in (
                      "wall_loops", "sparse_infill_density", "filament_flow_ratio",
                      "xy_contour_compensation", "xy_hole_compensation")},
                  physical_fit_qualified=False,
                  scope="Nominal bead envelopes, object identity, fit dimensions and production print orientation. Frame toolpaths and support contacts are reviewed separately; physical cooled fit, forces and endurance remain unqualified.")
    args.output.write_text(json.dumps(output, indent=2) + "\n")
    print(json.dumps({"checks_pass": True, "fit_object_count": 22,
                      "review": str(args.output),
                      "valve_openings": {r["label"]: [s["equivalent_round_diameter_mm"]
                                                      for s in r["measured_sections"]]
                                         for r in result if r["kind"] == "valve"}}, indent=2))


if __name__ == "__main__":
    main()
