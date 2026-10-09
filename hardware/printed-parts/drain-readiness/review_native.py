"""Bind the delivered drain print archives to geometry and actual native paths.

Run after prepare.py. This reads the native archives without submitting a job.
Back-top support contacts are read separately by review_show_support.py.
"""
from pathlib import Path
import hashlib
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import defaultdict

import numpy as np
from shapely.geometry import LineString
from shapely.ops import unary_union

from review_roads import layers, MODEL, WALL

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools/docgen").is_dir())
JOB = ROOT / ".cache/prints/2026-10-07-drain"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "hardware/printed-parts/faucet")]
import refresh_print_project as writer
from verify_round_layer_band import wall_layers, check_span


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    Path(path).write_text(json.dumps(value, indent=2) + "\n")


def integrity(path):
    with zipfile.ZipFile(path) as z:
        assert z.testzip() is None
        raw = z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(raw).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        settings = json.loads(z.read(writer.SETTINGS_MEMBER))
        (path.parent / "plate_1.gcode").write_bytes(raw)
        (path.parent.parent / "preview.png").write_bytes(z.read("Metadata/plate_1.png"))
    return raw, settings


def back_top():
    project = JOB / "back-top-mark2/back-top-black-z004-mark2.3mf"
    prep = project.with_suffix(".preparation.json")
    report = json.loads(prep.read_text())
    part = report["parts"][0]
    assert sha(ROOT / part["source"]) == part["stl_sha256"]
    assert sha(project) == report["project_sha256"]
    with zipfile.ZipFile(project) as z:
        settings_bytes = z.read(writer.SETTINGS_MEMBER)
        source_settings = json.loads(settings_bytes)
        config = ET.fromstring(z.read("Metadata/model_settings.config"))
        modifiers = config.findall("./object/part[@subtype='modifier_part']")
        assert len(modifiers) == len(report["solid_host_regions"]) == 23
        for modifier in modifiers:
            assert modifier.find("metadata[@key='sparse_infill_density']").get("value") == "100%"
            assert [m.get("value") for m in modifier.findall("metadata[@key='wall_loops']")] == ["10"]
    report["settings_sha256"] = hashlib.sha256(settings_bytes).hexdigest()
    save(prep, report)
    archive = project.parent / "ready" / (project.stem + ".gcode.3mf")
    raw, settings = integrity(archive)
    essentials = ("initial_layer_print_height", "layer_height", "wall_loops", "support_type",
                  "support_style", "support_top_z_distance", "support_bottom_z_distance",
                  "support_object_xy_distance", "filament_colour", "filament_nozzle_map",
                  "nozzle_diameter", "infill_wall_overlap", "wall_sequence", "is_infill_first",
                  "minimum_sparse_infill_area", "detect_narrow_internal_solid_infill",
                  "top_one_wall_type")
    assert all(settings[k] == source_settings[k] for k in essentials)
    assert float(settings["initial_layer_print_height"]) == .20
    assert float(settings["layer_height"]) == .24
    assert int(settings["wall_loops"]) == 2
    assert settings["detect_narrow_internal_solid_infill"] == "0"
    assert settings["top_one_wall_type"] == "not apply"
    assert float(settings["minimum_sparse_infill_area"]) == 15
    assert settings["support_type"] == "tree(auto)"
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", raw, re.M)]
    assert trims == [0., .02], trims
    fine = check_span(wall_layers(archive, part["identify_id"]), "additive exterior roof band",
                      .2, 9.3, .24, .001)
    assert fine["pass"], fine
    early = {}
    with zipfile.ZipFile(archive) as z:
        for height, slab, roads, _ in layers(z.open("Metadata/plate_1.gcode")):
            model = [r for r in roads if r[6] == part["identify_id"] and r[7] in MODEL]
            if model:
                early[round(height, 5)] = model
            if height > .7:
                break
    assert .2 in early and .44 in early and .68 in early
    rot = np.array(part["build_transform"][:9]).reshape(3, 3)
    trans = np.array(part["build_transform"][9:])
    center = np.array(part["source_center_mm"])
    overlap = []
    for lower_z, upper_z in ((.2, .44), (.44, .68)):
        lower = unary_union([LineString((r[:2], r[2:4])).buffer(r[4] / 2) for r in early[lower_z]])
        outer = []
        for r in early[upper_z]:
            if r[7] not in {"Outer wall", "Overhang wall"}:
                continue
            cad = (np.array([[r[0], r[1], upper_z], [r[2], r[3], upper_z]]) - trans) @ rot.T + center
            if np.all(cad[:, 0] >= 98.5) or np.all(cad[:, 0] <= -98.5):
                outer.append(LineString((r[:2], r[2:4])).buffer(r[4] / 2))
        region = unary_union(outer)
        fraction = region.intersection(lower).area / region.area
        assert fraction >= .5, (upper_z, fraction)
        overlap.append({"from_z_mm": lower_z, "to_z_mm": upper_z,
                        "upper_outer_bead_area_supported_fraction": fraction,
                        "minimum_fraction": .5})
    audit = writer.slice_review(project, report, archive.parent)
    save(project.parent / "native-review.json", audit)
    topology = audit["parts"][0]
    removal = []
    for body in topology["trees"]:
        removal.append({"body": body["id"],
                        "route": "Release its contacts from the empty forebay, exposed flank or rear opening; cut connected sacrificial stock into fragments and remove it before any fittings, boards, loom or insulation enter.",
                        "physical_removal_effort_verified": False})
    result = {"native_archive": str(archive.relative_to(ROOT)), "native_archive_sha256": sha(archive),
              "gcode_sha256": hashlib.sha256(raw).hexdigest(), "zip_crc_and_gcode_md5_pass": True,
              "source_stl_sha256": part["stl_sha256"], "source_step_sha256": sha((ROOT / part["source"]).with_suffix(".step")),
              "essential_native_settings_retained": True, "settings": {k: settings[k] for k in essentials},
              "requested_z_trim_mm": .04, "emitted_z_trim_mm": trims,
              "complete_additive_layer_band": fine, "first_layer_overlap": overlap,
              "solid_host_modifier_count": len(modifiers), "support_removal": removal,
              "full_native_bead_footprint": audit["fit"], "submitted": False,
              "scope": "Native mesh/archive/settings, complete footprint, additive roof layers and first-layer overlap. Dense region deposition and protected exterior contacts have separate readings. Physical cleanup, appearance, fit, load capacity and lifetime remain separate.",
              "passed": True}
    save(project.parent / "archive-review.json", result)
    print("Back-top archive review passed", flush=True)


def labels(colours=("white", "blue", "red", "black")):
    records = []
    for colour in colours:
        directory = JOB / ("labels-" + colour + "-mark2")
        project = directory / ("labels-" + colour + "-z004-mark2.3mf")
        prep = json.loads((directory / "preparation.json").read_text())
        assert sha(project) == prep["project_sha256"]
        with zipfile.ZipFile(project) as z:
            layer_ranges = ET.fromstring(z.read("Metadata/layer_config_ranges.xml"))
        expected = ([(1.40, 1.68, .14), (1.92, 2.48, .08)]
                    if colour == "black" else [(1.88, 2.0, .12)])
        schedules = [[(float(r.get("min_z")), float(r.get("max_z")),
                       float(r.find("option[@opt_key='layer_height']").text))
                      for r in obj.findall("range")] for obj in layer_ranges.findall("object")]
        assert len(schedules) == len(prep["parts"]) and all(row == expected for row in schedules)
        archive = directory / "ready" / (project.stem + ".gcode.3mf")
        raw, settings = integrity(archive)
        assert settings["extruder_offset"] == ["0x0", "0.5x-0.7"]
        assert float(settings["initial_layer_print_height"]) == .20
        assert float(settings["layer_height"]) == .24
        assert settings["enable_support"] == "0"
        native = json.loads((directory / "native-review.json").read_text())
        assert sha(archive) == native["native_archive_sha256"]
        assert native["minimum_shared_bed_margin_mm"] >= 80
        object_layers, object_tools = defaultdict(set), defaultdict(set)
        object_roads = defaultdict(int)
        with zipfile.ZipFile(archive) as z:
            for height, _, roads, _ in layers(z.open("Metadata/plate_1.gcode")):
                for road in roads:
                    if road[7] in MODEL:
                        object_layers[road[6]].add(height)
                        object_tools[road[6]].add(road[5])
                        object_roads[road[6]] += 1
        objects = []
        for index, item in enumerate(prep["parts"]):
            ident = 2901 + index
            assert object_layers[ident] and object_tools[ident] == {0, 1}
            assert min(object_layers[ident]) == .2
            objects.append({"identify_id": ident, "station": item["station"],
                            "kind": item["kind"], "model_road_count": object_roads[ident],
                            "model_layer_count": len(object_layers[ident]),
                            "last_model_z_mm": max(object_layers[ident]),
                            "both_body_and_letter_tools_present": True})
        snap_layers = None
        if colour == "black":
            data_index = next(i for i, part in enumerate(prep["parts"]) if part["station"] == "data")
            data_layers = sorted(object_layers[2901 + data_index])
            for height in (1.40, 1.54, 1.68, 1.92, 2.00, 2.08, 2.16):
                assert any(abs(z - height) < 1e-5 for z in data_layers), ("DATA layer", height, data_layers)
            assert abs(max(data_layers) - 2.16) < 1e-5, data_layers
            snap_layers = {"wing_top_mm": 1.68, "face_top_mm": 1.68,
                           "word_top_mm": 2.16, "model_layer_heights_mm": data_layers,
                           "passed": True}
        records.append({"colour": colour, "parts": prep["parts"],
                        "emitted_objects": objects, "shared_variable_layer_bands_mm": expected,
                        "prime_tower_layer_schedules_match": True, "data_closing_layers": snap_layers,
                        "native_archive": str(archive.relative_to(ROOT)), "native_archive_sha256": sha(archive),
                        "gcode_sha256": hashlib.sha256(raw).hexdigest(), "zip_crc_and_gcode_md5_pass": True,
                        "full_native_bead_margin_mm": native["minimum_shared_bed_margin_mm"],
                        "extruder_offset": settings["extruder_offset"], "submitted": False})
    save(JOB / "label-archive-review.json", {"plates": records, "passed": True})
    print(f"{len(records)} label archive review(s) passed", flush=True)


if __name__ == "__main__":
    labels()
    back_top()
