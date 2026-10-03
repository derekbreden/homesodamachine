"""Slice the frozen float foam pieces separately for Mark2's right 0.4 mm nozzle."""

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
FLOAT = HERE.parent.parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
SOURCE = ROOT / ".cache/magnetic-float-print/aero-input.3mf"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
NATIVE_REVISION = 2
sys.path.insert(0, str(ROOT / "tools/funnel-mold-print"))
from profiles import trimmed_start_gcode
sys.path.insert(0, str(FLOAT))
from verify import read_paths
sys.path.insert(0, str(ROOT / "hardware/printed-parts/enclosure/nameplate"))
from verify_mark2_print import segments

CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
ET.register_namespace("BambuStudio", "http://schemas.bambulab.com/package/2021")
PARTS = {
    "body-aero": "63d12cbb501b629997a2462822df42a1f4f6bf20ee2806f2f6f310c1f7e72771",
    "insert-aero": "c69cdc552c1dec84dd0bd84972ed601667df8327b0388236eec63ea7d672b8c6",
}


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def metadata(element):
    return {e.get("key"): e.get("value") for e in element.findall("metadata")}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def prepare(part, frozen):
    key = "core" if part == "body-aero" else "insert"
    job = ROOT / f".cache/prints/magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}"
    assert not job.exists(), "Use a new immutable revision directory."
    job.mkdir(parents=True)
    with zipfile.ZipFile(SOURCE) as z:
        assert z.testzip() is None
        data = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(data["Metadata/project_settings.config"])
    original_settings = dict(settings)
    config = ET.fromstring(data["Metadata/model_settings.config"])
    chosen = next(o for o in config.findall("object")
                  if metadata(o.find("part"))["name"] == part)
    object_id = chosen.get("id")
    plate = next(p for p in config.findall("plate")
                 if metadata(p.find("model_instance"))["object_id"] == object_id)
    for child in list(config):
        if child is not chosen and child is not plate:
            config.remove(child)
    assert metadata(chosen)["xy_contour_compensation"] == "0.05"
    assert metadata(chosen)["xy_hole_compensation"] == "-0.05"
    for e in plate.findall("metadata"):
        if e.get("key") == "plater_id":
            e.set("value", "1")
        if e.get("key") == "bed_type":
            e.set("value", "Textured PEI Plate")

    model = ET.fromstring(data["3D/3dmodel.model"])
    model.set("xmlns:BambuStudio", "http://schemas.bambulab.com/package/2021")
    resources = model.find(f"{{{CORE}}}resources")
    build = model.find(f"{{{CORE}}}build")
    for obj in list(resources):
        if obj.get("id") != object_id:
            resources.remove(obj)
    for item in list(build):
        if item.get("objectid") != object_id:
            build.remove(item)
    item, = list(build)
    transform = item.get("transform").split()
    transform[9:11] = ["150", "145"]
    item.set("transform", " ".join(transform))
    component = resources.find(f".//{{{CORE}}}component")
    member = component.get(f"{{{PROD}}}path").lstrip("/")
    embedded = ET.fromstring(data[member])
    vertices = np.array([[float(v.get(a)) for a in ("x", "y", "z")]
                         for v in embedded.findall(f".//{{{CORE}}}vertex")])
    source_mesh = trimesh.load(FLOAT / f"{part}.stl", force="mesh", process=True)
    local = vertices + np.array([0, 0, float(transform[11])])
    errors = cKDTree(source_mesh.vertices).query(local)[0]
    assert float(errors.max()) < 1e-6
    assert abs(float(local[:, 2].min())) < 1e-6
    assert sha(FLOAT / f"{part}.stl") == frozen
    rels = ET.fromstring(data["3D/_rels/3dmodel.model.rels"])
    for relationship in list(rels):
        if relationship.get("Target").lstrip("/") != member:
            rels.remove(relationship)
    settings.update({
        "curr_bed_type": "Textured PEI Plate",
        "nozzle_diameter": ["0.4", "0.4"],
        "min_layer_height": ["0.08", "0.08"],
        "max_layer_height": ["0.28", "0.28"],
        "elefant_foot_compensation": "0",
        "machine_start_gcode": trimmed_start_gcode(settings["machine_start_gcode"], 0.04),
    })
    assert settings["filament_nozzle_map"] == ["1"]
    assert settings["filament_type"] == ["ASA-AERO"]
    assert settings["filament_flow_ratio"] == ["0.52"]
    assert settings["nozzle_temperature"] == ["270"]
    assert settings["chamber_temperatures"] == ["60"]
    assert settings["textured_plate_temp"] == ["90"]
    changes = {k: {"source": original_settings.get(k), "selected": v}
               for k, v in settings.items() if v != original_settings.get(k)}
    data["Metadata/project_settings.config"] = json.dumps(settings).encode()
    data["Metadata/model_settings.config"] = ET.tostring(config, encoding="UTF-8", xml_declaration=True)
    data["3D/3dmodel.model"] = ET.tostring(model, encoding="UTF-8", xml_declaration=True)
    # Studio requires unprefixed relationship tags in this package member.
    data["3D/_rels/3dmodel.model.rels"] = ET.tostring(
        rels, encoding="UTF-8", xml_declaration=True).replace(
            b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    native_input = job / f"magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}-input.3mf"
    with zipfile.ZipFile(native_input, "x", zipfile.ZIP_DEFLATED) as z:
        for name, body in data.items():
            if name.startswith("3D/Objects/") and name != member:
                continue
            z.writestr(name, body)
    ready = job / "ready"
    ready.mkdir()
    archive = ready / f"magnetic-float-{key}-mark2-aero-v{NATIVE_REVISION}.gcode.3mf"
    with (job / "slice.log").open("w") as log:
        subprocess.run([str(STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
                        "--export-3mf", archive.name, "--outputdir", str(ready), str(native_input)],
                       cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        gcode = z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        selected = json.loads(z.read("Metadata/project_settings.config"))
        (HERE / f"{key}-preview.png").write_bytes(z.read("Metadata/plate_1.png"))
        assert len([n for n in z.namelist() if n.endswith(".gcode")]) == 1
    (ready / "plate_1.gcode").write_bytes(gcode)
    assert selected["curr_bed_type"] == "Textured PEI Plate"
    assert selected["filament_nozzle_map"] == ["1"]
    for k in ("filament_type", "filament_flow_ratio", "filament_ids", "nozzle_temperature",
              "chamber_temperatures", "filament_max_volumetric_speed", "line_width",
              "layer_height", "initial_layer_print_height", "sparse_infill_density"):
        assert selected[k] == original_settings[k], (k, selected[k], original_settings[k])
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, 0.02]
    paths = read_paths(gcode.decode(), part, 0.2, 0.2, 0.99, 2)
    assert "M140 S90" in paths["thermal_commands"]
    assert "M104 S270 T0" in paths["thermal_commands"]
    assert not paths["insertion_pauses"]
    roads = list(segments(ready / "plate_1.gcode"))
    support = [r for r in roads if r["feature"].startswith("Support")]
    assert not support
    model_roads = [r for r in roads if not r["feature"].startswith("Support")]
    first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                         for r in model_roads if r["layer"] == 0.2])
    overlaps = []
    for r in model_roads:
        if r["layer"] == 0.4:
            bead = LineString((r["a"], r["b"])).buffer(r["width"] / 2)
            overlaps.append((bead.intersection(first).area / bead.area, r["feature"]))
    assert overlaps and min(v for v, _ in overlaps) > 0.5
    preparation = {
        "printer": "Mark2", "part": part, "quantity": 1,
        "native_archive_revision": NATIVE_REVISION,
        "source_project": str(SOURCE.relative_to(ROOT)), "source_project_sha256": sha(SOURCE),
        "source_stl_sha256": {part: frozen}, "embedded_vertex_error_mm": float(errors.max()),
        "source_mesh_bytes_retained": True, "print_orientation_retained": True,
        "project": str(native_input.relative_to(ROOT)), "project_sha256": sha(native_input),
        "archive": str(archive.relative_to(ROOT)), "archive_sha256": sha(archive),
        "gcode_sha256": hashlib.sha256(gcode).hexdigest(),
        "requested_z_trim_mm": 0.04, "emitted_z_trim_commands_mm": trims,
        "profile_changes": changes, "native_path_review": paths,
        "support_paths": len(support),
        "minimum_second_layer_bead_area_overlap_fraction": min(v for v, _ in overlaps),
        "minimum_second_layer_outer_wall_bead_area_overlap_fraction": min(
            v for v, feature in overlaps if feature == "Outer wall"),
        "bed": "Textured PEI Plate", "physical_plate_trial": "User selected Textured PEI for the first ASA Aero print.",
        "material_mapping": {"physical_material": "Bambu ASA Aero White 46100", "filament_id": "GFB02",
                             "nozzle": "right standard-flow hardened 0.4 mm", "source": "AMS HT, unit 128 tray 0"},
        "submitted": False, "physical_fit_verified": False,
    }
    # The start template is represented by its hash rather than duplicating its full text.
    preparation["profile_changes"]["machine_start_gcode"] = {
        "source_sha256": hashlib.sha256(original_settings["machine_start_gcode"].encode()).hexdigest(),
        "selected_sha256": hashlib.sha256(settings["machine_start_gcode"].encode()).hexdigest(),
        "change": "Retain Mark2 +0.04 mm trim with stock Textured PEI compensation.",
    }
    write_json(HERE / f"{key}-preflight.json", preparation)
    assert sha(FLOAT / f"{part}.stl") == frozen
    print(f"Reviewed {archive.name}: {paths['layers']} layers, right ASA Aero, +0.04 trim", flush=True)


if __name__ == "__main__":
    for part, frozen in PARTS.items():
        prepare(part, frozen)
