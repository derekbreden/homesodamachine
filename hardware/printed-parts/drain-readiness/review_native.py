"""Bind the identification plate archives to their preparations and actual native paths.

Run after `prepare.py labels`. This reads the native archives without submitting a job.
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


def labels(colours=("white", "blue", "red", "black")):
    records = []
    for colour in colours:
        directory = JOB / ("labels-" + colour + "-mark2")
        project = directory / ("labels-" + colour + "-z004-mark2.3mf")
        prep = json.loads((directory / "preparation.json").read_text())
        assert sha(project) == prep["project_sha256"]
        with zipfile.ZipFile(project) as z:
            layer_ranges = ET.fromstring(z.read("Metadata/layer_config_ranges.xml"))
        expected = [tuple(band) for band in prep["closing_layer_ranges_mm"]]
        schedules = [[(float(r.get("min_z")), float(r.get("max_z")),
                       float(r.find("option[@opt_key='layer_height']").text))
                      for r in obj.findall("range")] for obj in layer_ranges.findall("object")]
        assert len(schedules) == len(prep["parts"])
        assert all(np.allclose(row, expected, atol=1e-6) if expected else not row for row in schedules), schedules
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
        closing = []
        for index, part in enumerate(prep["parts"]):
            if not part.get("face_up_tops_mm"):
                continue
            emitted = sorted(object_layers[2901 + index])
            for height in part["face_up_tops_mm"]:
                assert any(abs(z - height) < 1e-5 for z in emitted), (part["station"], "face top", height, emitted)
            assert abs(max(emitted) - max(part["face_up_tops_mm"])) < 1e-5, (part["station"], emitted)
            closing.append({"station": part["station"], "face_up_tops_mm": part["face_up_tops_mm"],
                            "model_layer_heights_mm": emitted, "passed": True})
        records.append({"colour": colour, "parts": prep["parts"],
                        "emitted_objects": objects, "shared_variable_layer_bands_mm": expected,
                        "prime_tower_layer_schedules_match": True, "face_closing_layers": closing,
                        "native_archive": str(archive.relative_to(ROOT)), "native_archive_sha256": sha(archive),
                        "gcode_sha256": hashlib.sha256(raw).hexdigest(), "zip_crc_and_gcode_md5_pass": True,
                        "full_native_bead_margin_mm": native["minimum_shared_bed_margin_mm"],
                        "extruder_offset": settings["extruder_offset"], "submitted": False})
    save(JOB / "label-archive-review.json", {"plates": records, "passed": True})
    print(f"{len(records)} label archive review(s) passed", flush=True)


if __name__ == "__main__":
    labels()
