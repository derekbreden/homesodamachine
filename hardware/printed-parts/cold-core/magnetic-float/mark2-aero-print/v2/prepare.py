"""Review the frozen core and insert together, with zero trim and no adhesion rings."""

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import cKDTree
from shapely.geometry import LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
BASE_PATH = HERE.parent / "v1/prepare.py"
spec = importlib.util.spec_from_file_location("float_first_trial", BASE_PATH)
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
ROOT, FLOAT, SOURCE = base.ROOT, base.FLOAT, base.SOURCE
JOB = ROOT / ".cache/prints/magnetic-float-pair-mark2-aero-v3"
CENTERS = {"body-aero": (125.0, 145.0), "insert-aero": (175.0, 145.0)}


def analysis_frame(gcode, center):
    """Translate only the read-only analysis copy to the verifier's 150,145 origin."""
    delta = {"X": 150 - center[0], "Y": 145 - center[1]}
    lines = []
    for line in gcode.splitlines():
        if re.match(r"^G(?:0|1) ", line):
            line = re.sub(r"\b([XY])([-+\d.]+)",
                          lambda m: f"{m[1]}{float(m[2]) + delta[m[1]]:.6f}", line)
        lines.append(line)
    return "\n".join(lines)


def main():
    assert not JOB.exists(), "Use a new immutable native revision directory."
    JOB.mkdir(parents=True)
    with zipfile.ZipFile(SOURCE) as z:
        assert z.testzip() is None
        data = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(data["Metadata/project_settings.config"])
    original = copy.deepcopy(settings)
    config = ET.fromstring(data["Metadata/model_settings.config"])
    plates = config.findall("plate")
    assert len(plates) == 2 and len(config.findall("object")) == 2
    plate = plates[0]
    plate.append(copy.deepcopy(plates[1].find("model_instance")))
    config.remove(plates[1])
    for e in plate.findall("metadata"):
        if e.get("key") == "bed_type":
            e.set("value", "Textured PEI Plate")
        if e.get("key") == "plater_name":
            e.set("value", "ASA Aero core and insert")

    model = ET.fromstring(data["3D/3dmodel.model"])
    model.set("xmlns:BambuStudio", "http://schemas.bambulab.com/package/2021")
    resources = model.find(f"{{{base.CORE}}}resources")
    build = model.find(f"{{{base.CORE}}}build")
    geometry = {}
    object_ids = {}
    for obj in config.findall("object"):
        part = base.metadata(obj.find("part"))["name"]
        assert part in base.PARTS
        assert base.metadata(obj)["xy_contour_compensation"] == "0.05"
        assert base.metadata(obj)["xy_hole_compensation"] == "-0.05"
        oid = obj.get("id")
        item = next(i for i in build if i.get("objectid") == oid)
        transform = item.get("transform").split()
        transform[9:11] = [str(v) for v in CENTERS[part]]
        item.set("transform", " ".join(transform))
        resource = next(o for o in resources if o.get("id") == oid)
        member = resource.find(f".//{{{base.CORE}}}component").get(f"{{{base.PROD}}}path").lstrip("/")
        mesh_xml = ET.fromstring(data[member])
        vertices = np.array([[float(v.get(a)) for a in ("x", "y", "z")]
                             for v in mesh_xml.findall(f".//{{{base.CORE}}}vertex")])
        mesh = trimesh.load(FLOAT / f"{part}.stl", force="mesh", process=True)
        errors = cKDTree(mesh.vertices).query(vertices + [0, 0, float(transform[11])])[0]
        assert errors.max() < 1e-6
        assert abs(float(vertices[:, 2].min()) + float(transform[11])) < 1e-6
        assert base.sha(FLOAT / f"{part}.stl") == base.PARTS[part]
        instance = next(i for i in plate.findall("model_instance")
                        if base.metadata(i)["object_id"] == oid)
        object_ids[part] = int(base.metadata(instance)["identify_id"])
        geometry[part] = {"center_xy_mm": CENTERS[part], "identify_id": object_ids[part],
                          "embedded_vertex_error_mm": float(errors.max()),
                          "embedded_mesh_sha256": hashlib.sha256(data[member]).hexdigest(),
                          "stl_sha256": base.PARTS[part], "orientation_retained": True, "bed_z_mm": 0.0}
    assert len(geometry) == 2
    settings.update({"curr_bed_type": "Textured PEI Plate", "nozzle_diameter": ["0.4", "0.4"],
                     "min_layer_height": ["0.08", "0.08"], "max_layer_height": ["0.28", "0.28"],
                     "elefant_foot_compensation": "0", "skirt_loops": "0", "brim_type": "no_brim",
                     "brim_width": "0", "print_sequence": "by layer",
                     "machine_start_gcode": base.trimmed_start_gcode(original["machine_start_gcode"], 0.0)})
    changes = {k: {"source": original.get(k), "selected": v}
               for k, v in settings.items() if original.get(k) != v}
    changes["machine_start_gcode"] = {
        "source_sha256": hashlib.sha256(original["machine_start_gcode"].encode()).hexdigest(),
        "selected_sha256": hashlib.sha256(settings["machine_start_gcode"].encode()).hexdigest(),
        "change": "User requested 0.00 mm trim; retain stock Textured PEI correction."}
    data["Metadata/project_settings.config"] = json.dumps(settings).encode()
    data["Metadata/model_settings.config"] = ET.tostring(config, encoding="UTF-8", xml_declaration=True)
    data["3D/3dmodel.model"] = ET.tostring(model, encoding="UTF-8", xml_declaration=True)
    native_input = JOB / "magnetic-float-pair-mark2-aero-v3-input.3mf"
    with zipfile.ZipFile(native_input, "x", zipfile.ZIP_DEFLATED) as z:
        for name, body in data.items():
            z.writestr(name, body)
    ready = JOB / "ready"
    ready.mkdir()
    archive = ready / "magnetic-float-pair-mark2-aero-v3.gcode.3mf"
    with (JOB / "slice.log").open("w") as log:
        subprocess.run([str(base.STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
                        "--export-3mf", archive.name, "--outputdir", str(ready), str(native_input)],
                       cwd=ready, stdout=log, stderr=subprocess.STDOUT, check=True)
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        assert len([n for n in z.namelist() if n.endswith(".gcode")]) == 1
        gcode = z.read("Metadata/plate_1.gcode")
        assert hashlib.md5(gcode).hexdigest() == z.read("Metadata/plate_1.gcode.md5").decode().strip().lower()
        selected = json.loads(z.read("Metadata/project_settings.config"))
        (HERE / "pair-preview.png").write_bytes(z.read("Metadata/plate_1.png"))
        slice_info = ET.fromstring(z.read("Metadata/slice_info.config"))
        native_plate, = slice_info.findall("plate")
        assert len(native_plate.findall("object")) == 2
        native_metadata = base.metadata(native_plate)
        assert native_metadata["support_used"] == "false"
        nozzle = native_plate.find("nozzle")
        assert nozzle.get("extruder_id") == "2" and nozzle.get("nozzle_diameter") == "0.4"
        warnings = [w.attrib for w in native_plate.findall("warning")]
        assert not warnings
    for key in ("filament_type", "filament_flow_ratio", "filament_ids", "nozzle_temperature",
                "nozzle_temperature_initial_layer", "chamber_temperatures", "filament_max_volumetric_speed",
                "line_width", "layer_height", "initial_layer_print_height", "sparse_infill_density"):
        assert selected[key] == original[key], (key, selected[key], original[key])
    assert selected["filament_nozzle_map"] == ["1"]
    assert selected["brim_type"] == "no_brim" and float(selected["skirt_loops"]) == 0
    assert selected["print_sequence"] == "by layer"
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    assert trims == [0.0, -0.02]
    assert not re.findall(rb"^; FEATURE: (?:Skirt|Brim|Support|Prime tower)", gcode, re.M)
    path = ready / "plate_1.gcode"
    path.write_bytes(gcode)
    roads = list(base.segments(path))
    assert {r["object"] for r in roads} == set(object_ids.values())
    assert {r["tool"] for r in roads} == {0}
    reviews = {}
    for part, ident in object_ids.items():
        paths = base.read_paths(analysis_frame(gcode.decode(), CENTERS[part]), part, 0.2, 0.2, 0.99, 2)
        assert "M104 S270 T0" in paths["thermal_commands"] and "M140 S90" in paths["thermal_commands"]
        rr = [r for r in roads if r["object"] == ident]
        first = unary_union([LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                             for r in rr if r["layer"] == 0.2])
        overlaps = []
        for r in rr:
            if r["layer"] == 0.4:
                bead = LineString((r["a"], r["b"])).buffer(r["width"] / 2)
                overlaps.append(bead.intersection(first).area / bead.area)
        assert overlaps and min(overlaps) > 0.5
        paths["minimum_second_layer_bead_area_overlap_fraction"] = min(overlaps)
        reviews[part] = paths
    baseline = json.loads((HERE.parent / "v1/core-preflight.json").read_text())
    result = {"printer": "Mark2", "physical_trial_revision": 2, "native_archive_revision": 3,
              "parts": geometry, "quantity_per_part": 1, "print_sequence": "by layer",
              "source_commit": baseline["source_commit"], "source_snapshot": baseline["source_snapshot"],
              "source_project": str(SOURCE.relative_to(ROOT)), "source_project_sha256": base.sha(SOURCE),
              "preparation_dependency_sha256": {str(BASE_PATH.relative_to(ROOT)): base.sha(BASE_PATH)},
              "project": str(native_input.relative_to(ROOT)), "project_sha256": base.sha(native_input),
              "archive": str(archive.relative_to(ROOT)), "archive_sha256": base.sha(archive),
              "gcode_sha256": hashlib.sha256(gcode).hexdigest(), "requested_z_trim_mm": 0.0,
              "emitted_z_trim_commands_mm": trims, "bed": "Textured PEI Plate", "profile_changes": changes,
              "material_mapping": baseline["material_mapping"], "per_part_native_path_review": reviews,
              "native_slice_summary": {"estimated_time_s": float(native_metadata["prediction"]),
                                       "filament_mass_g": float(native_metadata["weight"]),
                                       "object_count": 2, "warnings": warnings},
              "support_paths": 0, "skirt_paths": 0, "brim_paths": 0, "submitted": False,
              "preview_inspected": False, "physical_fit_verified": False}
    (HERE / "pair-preflight.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("archive", "archive_sha256", "gcode_sha256", "native_slice_summary")}), flush=True)


if __name__ == "__main__":
    main()
