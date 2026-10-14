"""Prepare one full-base elbow for Mark1 without connecting to a printer.

Run from the repository root:
    HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python \
        future/pump-elbow-exploration/prints/2026-10-13-full-base-single-tpu85a-mark1/prepare_mark1.py

The editable project, native sliced archive and readback JSON are saved beside
this script. The printed part's adhesion, socket fit and sealing are unqualified.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
STUDY = ROOT / "future/pump-elbow-exploration"
RECIPE_HELPER = STUDY / "prints/2026-10-13-continuous-body-tpu85a-mark1/prepare_mark1.py"
GEOMETRY = STUDY / "bed_supported_elbow.py"
STEM = "2026-10-13-full-base-single-elbow-tpu85a-right06-z018-mark1"
PROJECT, ARCHIVE = HERE / (STEM + ".3mf"), HERE / (STEM + ".gcode.3mf")
MODEL = HERE / "full-base-single-elbow-print.stl"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(STUDY))


def load(path, name):
    specification = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(specification)
    sys.modules[name] = module
    specification.loader.exec_module(module)
    return module


# These helpers only read the established machine/filament recipe and serialize
# files. Importing the manual preparation module does not run its main().
recipe_helpers = load(RECIPE_HELPER, "full_base_mark1_recipe_helpers")
sha, qn, xml = recipe_helpers.sha, recipe_helpers.qn, recipe_helpers.xml
metadata, uid = recipe_helpers.metadata, recipe_helpers.uid
CORE, PROD, REL = recipe_helpers.CORE, recipe_helpers.PROD, recipe_helpers.REL
SETTINGS, IDENTITY, WORD = recipe_helpers.SETTINGS, recipe_helpers.IDENTITY, recipe_helpers.WORD


def make_project(recipe, low, high, shape):
    cq.exporters.export(shape, str(MODEL), tolerance=.01, angularTolerance=.05)
    mesh = trimesh.load(MODEL, force="mesh", process=True)
    raw_hash, raw_faces, raw_volume = sha(MODEL.read_bytes()), len(mesh.faces), float(mesh.volume)
    mesh.process(validate=True)
    if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or mesh.body_count != 1:
        raise ValueError("The single specimen is not one closed, oriented mesh")
    # The analytic plane is Z0; eliminate only floating-point noise at that plane.
    near_zero = np.abs(mesh.vertices[:, 2]) < 1e-9
    mesh.vertices[near_zero, 2] = 0.0
    if mesh.bounds[0, 2] < 0 or abs(mesh.bounds[0, 2]) > 1e-7:
        raise ValueError("The full-base specimen is not grounded at Z0")
    xy_centre = mesh.bounds.mean(axis=0)[:2]
    mesh.apply_translation([-xy_centre[0], -xy_centre[1], 0])
    MODEL.write_bytes(mesh.export(file_type="stl"))
    bed_centre = (low + high) / 2
    placed = mesh.bounds + np.array([*bed_centre, 0.0])
    if np.any(placed[0, :2] < low + 20) or np.any(placed[1, :2] > high - 20):
        raise ValueError("The specimen enters the 20 mm usable-bed inset")
    flat_faces = np.all(np.abs(mesh.triangles[:, :, 2]) <= 1e-7, axis=1)
    bed_contact_area = float(mesh.area_faces[flat_faces].sum())
    if bed_contact_area <= 0:
        raise ValueError("The specimen has no planar bed contact")

    members = {SETTINGS: (json.dumps(recipe, indent=2) + "\n").encode()}
    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p")
    ET.SubElement(model, qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
    ET.SubElement(model, qn("metadata"), name="Title").text = "One full-base TPU elbow - Mark1"
    resources = ET.SubElement(model, qn("resources"))
    owner = ET.SubElement(resources, qn("object"), id="2", type="model",
                          **{f"{{{PROD}}}UUID": uid("full-base-single/object")})
    components = ET.SubElement(owner, qn("components"))
    member = "3D/Objects/full_base_single_elbow.model"
    ET.SubElement(components, qn("component"), objectid="1", transform=IDENTITY,
                  **{f"{{{PROD}}}path": "/" + member,
                     f"{{{PROD}}}UUID": uid("full-base-single/component")})
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": uid("full-base-single/build")})
    transform = f"1 0 0 0 1 0 0 0 1 {bed_centre[0]:.9f} {bed_centre[1]:.9f} 0"
    ET.SubElement(build, qn("item"), objectid="2", transform=transform, printable="1",
                  **{f"{{{PROD}}}UUID": uid("full-base-single/item")})
    child = ET.Element(qn("model"), unit="millimeter")
    child_resources = ET.SubElement(child, qn("resources"))
    volume = ET.SubElement(child_resources, qn("object"), id="1", type="model",
                           **{f"{{{PROD}}}UUID": uid("full-base-single/mesh")})
    geometry = ET.SubElement(volume, qn("mesh"))
    vertices, triangles = ET.SubElement(geometry, qn("vertices")), ET.SubElement(geometry, qn("triangles"))
    for vertex in mesh.vertices:
        ET.SubElement(vertices, qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
    for triangle in mesh.faces:
        ET.SubElement(triangles, qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))
    members[member] = xml(child)

    config = ET.Element("config")
    object_config = ET.SubElement(config, "object", id="2")
    metadata(object_config, "name", "Single full-base 15 mm tube-socket elbow")
    metadata(object_config, "extruder", 1)
    ET.SubElement(object_config, "metadata", face_count=str(len(mesh.faces)))
    part = ET.SubElement(object_config, "part", id="1", subtype="normal_part", uuid=uid("full-base-single/part"))
    for key, value in {"name": "full-base-single-elbow", "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                       "extruder": 1, "source_file": MODEL.name, "source_object_id": 0,
                       "source_volume_id": 0, "source_offset_x": 0,
                       "source_offset_y": 0, "source_offset_z": 0}.items():
        metadata(part, key, value)
    ET.SubElement(part, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                  degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
    plate = ET.SubElement(config, "plate")
    for key, value in {"plater_id": 1, "plater_name": "One full-base TPU elbow - Mark1", "locked": "false",
                       "filament_map_mode": "Auto For Flush", "filament_maps": "2", "filament_volume_maps": "0",
                       "bed_type": recipe["curr_bed_type"]}.items():
        metadata(plate, key, value)
    instance = ET.SubElement(plate, "model_instance")
    for key, value in {"object_id": 2, "instance_id": 0, "identify_id": 1901}.items():
        metadata(instance, key, value)
    assembled = ET.SubElement(config, "assemble")
    ET.SubElement(assembled, "assemble_item", object_id="2", instance_id="0", transform=transform, offset="0 0 0")
    members["3D/3dmodel.model"], members["Metadata/model_settings.config"] = xml(model), xml(config)
    model_rels = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(model_rels, f"{{{REL}}}Relationship", Target="/" + member, Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    members["3D/_rels/3dmodel.model.rels"] = xml(model_rels).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    rels = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(rels, f"{{{REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    members["_rels/.rels"] = xml(rels).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    members["[Content_Types].xml"] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="config" ContentType="application/octet-stream"/>
</Types>'''
    recipe_helpers.archive_write(PROJECT, members)
    return {"mesh": MODEL.name, "mesh_sha256": sha(MODEL.read_bytes()),
            "raw_occ_stl_sha256": raw_hash, "triangles": len(mesh.faces),
            "export_cleanup_removed_faces": raw_faces - len(mesh.faces),
            "raw_volume_mm3": raw_volume, "cleaned_volume_mm3": float(mesh.volume),
            "watertight": True, "winding_consistent": True,
            "body_count": 1, "native_object_count": 1, "native_volume_count": 1, "native_instance_count": 1,
            "bed_contact_area_mm2": bed_contact_area, "plate_bounds_mm": placed.tolist(),
            "xy_recentering_mm": (-xy_centre).tolist()}


def beads(gcode):
    xyz, e, relative_e, absolute_xy = dict(X=0., Y=0., Z=0.), 0., True, True
    feature, width, layer_z, first_z = "Custom", .62, None, None
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    first_low, first_high = np.full(2, np.inf), np.full(2, -np.inf)
    features, paths, volumes = Counter(), Counter(), Counter()
    first_paths = Counter()
    for raw in gcode.decode().splitlines():
        if raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
            features[feature] += 1
        elif raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
        elif raw.startswith("; Z_HEIGHT:"):
            layer_z = float(raw.split(":", 1)[1])
            if first_z is None:
                first_z = layer_z
        code = raw.split(";", 1)[0].strip()
        if not code:
            continue
        cmd = code.split()[0]
        words = {k: float(v) for k, v in WORD.findall(code)}
        if cmd == "M83":
            relative_e = True
        elif cmd == "M82":
            relative_e = False
        elif cmd in ("G90", "G91"):
            absolute_xy = cmd == "G90"
        elif cmd == "G92":
            e = words.get("E", e)
            xyz.update({k: words.get(k, xyz[k]) for k in xyz})
        if cmd not in ("G0", "G1", "G2", "G3"):
            continue
        start = xyz["X"], xyz["Y"]
        next_xyz = {k: words.get(k, xyz[k]) if absolute_xy else xyz[k] + words.get(k, 0) for k in xyz}
        end = next_xyz["X"], next_xyz["Y"]
        delta_e = words.get("E", 0) if relative_e else words.get("E", e) - e
        if delta_e > 0 and feature != "Custom" and (math.dist(start, end) > 1e-9 or cmd in ("G2", "G3")):
            points = recipe_helpers.arc_points(start, end, words, cmd == "G2") if cmd in ("G2", "G3") else [start, end]
            path_low, path_high = np.min(points, axis=0) - width / 2, np.max(points, axis=0) + width / 2
            low, high = np.minimum(low, path_low), np.maximum(high, path_high)
            paths[feature] += 1
            volumes[feature] += delta_e * math.pi * (1.75 / 2) ** 2
            if layer_z == first_z and "brim" not in feature.lower() and "skirt" not in feature.lower():
                first_low, first_high = np.minimum(first_low, path_low), np.maximum(first_high, path_high)
                first_paths[feature] += 1
        xyz = next_xyz
        if "E" in words:
            e = e + words["E"] if relative_e else words["E"]
    if not np.all(np.isfinite(low)) or not np.all(np.isfinite(first_low)):
        raise ValueError("Native full and first-layer model deposition envelopes are unavailable")
    if any("support" in name.lower() for name in paths):
        raise ValueError("The support-disabled slice contains deposited support")
    return {"native_full_bead_bounds_xy_mm": [low.tolist(), high.tolist()],
            "native_feature_counts": dict(features), "native_deposited_path_counts": dict(paths),
            "native_deposited_filament_volume_by_feature_mm3": dict(volumes),
            "native_first_layer_z_mm": first_z,
            "native_first_layer_model_bead_bounds_xy_mm": [first_low.tolist(), first_high.tolist()],
            "native_first_layer_model_deposited_path_counts": dict(first_paths),
            "scope": "XY bead widths and arc extrema; physical adhesion is unmeasured"}


def main():
    cache = ROOT / ".cache/printer-control/full-base-single-elbow-mark1-20261013"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    source_hash = sha(GEOMETRY.read_bytes())
    source_dependencies = {str(path.relative_to(ROOT)): sha(path.read_bytes()) for path in
                           (GEOMETRY, STUDY / "tpu_elbow.py", RECIPE_HELPER)}
    module = load(GEOMETRY, "full_base_single_elbow_geometry")
    shape = module.build()
    recipe, original, profile_sources, low, high = recipe_helpers.settings()
    recipe["print_settings_id"] = "One full-base TPU elbow 0.12 mm right 0.6 Mark1"
    specimen = make_project(recipe, low, high, shape)
    preparation = {
        "scope": "Single full-base specimen and offline native slice for Mark1; physical result pending",
        "printer": "Mark1 (H2C)", "material": "TPU 85A",
        "nozzle_mapping": "Right fixed 0.6 mm; external spool 255; TPU / 161616",
        "source_geometry": str(GEOMETRY.relative_to(ROOT)), "source_geometry_sha256": source_hash,
        "source_dependencies_sha256": source_dependencies,
        "recipe_helpers": str(RECIPE_HELPER.relative_to(ROOT)), "recipe_helpers_sha256": sha(RECIPE_HELPER.read_bytes()),
        "machine_profile_donor": str(recipe_helpers.DONOR.relative_to(ROOT)),
        "machine_profile_donor_sha256": sha(recipe_helpers.DONOR.read_bytes()),
        "machine_start_gcode_sha256": sha(recipe["machine_start_gcode"].encode()),
        "native_filament_profile_sources_sha256": profile_sources,
        "project": PROJECT.name, "project_sha256": sha(PROJECT.read_bytes()), "specimen": specimen,
        "usable_bed_bounds_xy_mm": [low.tolist(), high.tolist()],
        "settings_changes": {k: {"from": original.get(k), "to": v} for k, v in recipe.items() if original.get(k) != v},
    }
    PROJECT.with_suffix(".print.json").write_text(json.dumps(preparation, indent=2) + "\n")
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0", "--export-3mf",
               ARCHIVE.name, "--outputdir", str(run), str(PROJECT)]
    with (run / "slice.log").open("w") as log:
        subprocess.run(command, cwd=run, stdout=log, stderr=subprocess.STDOUT, check=True,
                       env=dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1"))
    result = json.loads((run / "result.json").read_text())
    if result.get("return_code") != 0:
        raise ValueError(result.get("error_string"))
    native = run / ARCHIVE.name
    with zipfile.ZipFile(native) as z:
        if z.testzip() is not None:
            raise ValueError("Native archive checksum error")
        gcode = z.read("Metadata/plate_1.gcode")
        if recipe_helpers.hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
        emitted = json.loads(z.read(SETTINGS))
        slice_info = ET.fromstring(z.read("Metadata/slice_info.config"))
        model = ET.fromstring(z.read("3D/3dmodel.model"))
        object_config = ET.fromstring(z.read("Metadata/model_settings.config"))
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0, 0.16]:
        raise ValueError(f"Unexpected Mark1 trim: {trims}")
    if emitted["filament_map"] != ["2"] or emitted["filament_colour"] != ["#161616"]:
        raise ValueError("The right-external filament mapping changed")
    for key in ("wall_loops", "sparse_infill_density", "spiral_mode", "enable_support"):
        if emitted.get(key) != recipe[key]:
            raise ValueError(f"Native process differs from requested {key}: {emitted.get(key)}")
    plate, = slice_info.findall("plate")
    used, = plate.findall("filament")
    if used.get("type") != "TPU" or used.get("color").lstrip("#").upper()[:6] != "161616":
        raise ValueError("The active sliced filament is not black TPU")
    counts = {"build_instances": len(model.findall(f"{qn('build')}/{qn('item')}")),
              "model_objects": len(object_config.findall("object")),
              "normal_volumes": len(object_config.findall("object/part[@subtype='normal_part']")),
              "slice_objects": len([o for o in plate.findall("object") if o.get("skipped") != "true"])}
    if set(counts.values()) != {1}:
        raise ValueError(f"The native plate must contain exactly one specimen: {counts}")
    deposition = beads(gcode)
    bead_low, bead_high = map(np.array, deposition["native_full_bead_bounds_xy_mm"])
    margins = [*(bead_low - low), *(high - bead_high)]
    if min(margins) < 20:
        raise ValueError("Native beads enter the 20 mm usable-bed inset")
    if any(sha((ROOT / path).read_bytes()) != digest for path, digest in source_dependencies.items()):
        raise ValueError("A geometry or recipe source changed during preparation")
    (run / "plate_1.gcode").write_bytes(gcode)
    ARCHIVE.write_bytes(native.read_bytes())
    sliced_plate, = result["sliced_plates"]
    keys = ("printer_settings_id", "filament_settings_id", "filament_map", "filament_nozzle_map", "filament_colour",
            "nozzle_diameter", "curr_bed_type", "nozzle_temperature", "nozzle_temperature_initial_layer",
            "textured_plate_temp", "filament_max_volumetric_speed", "layer_height", "initial_layer_print_height",
            "wall_loops", "wall_generator", "sparse_infill_density", "spiral_mode", "top_shell_layers",
            "bottom_shell_layers", "seam_gap", "enable_support", "brim_width", "brim_type")
    readiness = {
        "status": "Single-specimen native slice read back; no printer submission; physical result pending",
        "observed_at": datetime.now(timezone.utc).isoformat(), "cache_run": str(run.relative_to(ROOT)),
        "project": PROJECT.name, "project_sha256": preparation["project_sha256"], "archive": ARCHIVE.name,
        "archive_sha256": sha(ARCHIVE.read_bytes()), "gcode_sha256": sha(gcode),
        "source_geometry_sha256": source_hash, "specimen": specimen, "native_single_specimen_counts": counts,
        "source_dependencies_sha256": source_dependencies,
        "plate_trim_commands_mm": trims, "emitted_settings": {k: emitted.get(k) for k in keys},
        "native_active_filament": used.attrib, "usable_bed_bounds_xy_mm": [low.tolist(), high.tolist()],
        "full_bead_edge_margins_xy_mm": margins, "minimum_full_bead_edge_margin_mm": min(margins),
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": sliced_plate["total_predication"],
        "estimated_filament_g": sum(f["total_used_g"] for f in sliced_plate["filaments"]),
        "estimate_density_g_cm3": emitted["filament_density"], "slicer_warning": sliced_plate["warning_message"],
        **deposition,
    }
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
    print(json.dumps(readiness, indent=2))


if __name__ == "__main__":
    main()
