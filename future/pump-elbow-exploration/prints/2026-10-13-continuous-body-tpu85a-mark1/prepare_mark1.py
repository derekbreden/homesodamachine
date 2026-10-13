"""Prepare two current 15 mm elbows for Mark1, without connecting to a printer.

Run from the repository root after the elbow geometry is ready:
    HSM_NO_BUILD_LOCK=1 tools/cad-venv/bin/python \
        future/pump-elbow-exploration/prints/2026-10-13-continuous-body-tpu85a-mark1/prepare_mark1.py

The editable project, native sliced archive and readback JSON live beside this
script. Native slicer logs and extracted G-code live in the reported cache run.
The two elbows are volumes of one object, with a 2 mm model gap and native
outer brims. Printed shape, socket fit and pressure sealing are unqualified.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
STUDY = ROOT / "future/pump-elbow-exploration"
DONOR = ROOT / "hardware/printed-parts/faucet/tpu-o-ring/prints/2026-10-13-tpu85a-right06-mark1/2026-10-13-tpu-o-ring-85a-right06-z018-mark1.3mf"
SLICER = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
PROFILES = Path("/Applications/BambuStudio.app/Contents/Resources/profiles/BBL/filament")
STEM = "2026-10-13-continuous-body-elbows-tpu85a-right06-z018-mark1"
PROJECT = HERE / (STEM + ".3mf")
ARCHIVE = HERE / (STEM + ".gcode.3mf")
GAP = 2.0
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SETTINGS = "Metadata/project_settings.config"
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
WORD = re.compile(r"([A-Z])([-+]?(?:\d+(?:\.\d*)?|\.\d+))")
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(STUDY))
from tpu_elbow import Elbow


def sha(payload):
    return hashlib.sha256(payload).hexdigest()


def qn(name):
    return f"{{{CORE}}}{name}"


def xml(element):
    return ET.tostring(element, encoding="UTF-8", xml_declaration=True)


def metadata(parent, key, value):
    ET.SubElement(parent, "metadata", key=key, value=str(value))


def uid(name):
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "homesodamachine/continuous-elbow/" + name))


def archive_write(path, members):
    temporary = path.with_suffix(path.suffix + ".tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as target:
        for name, payload in sorted(members.items()):
            item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            item.compress_type = zipfile.ZIP_DEFLATED
            item.external_attr = 0o644 << 16
            target.writestr(item, payload)
    temporary.replace(path)


def filament(name, sources):
    path = PROFILES / (name + ".json")
    payload = path.read_bytes()
    sources[str(path)] = sha(payload)
    own = json.loads(payload)
    combined = filament(own["inherits"], sources) if own.get("inherits") else {}
    for include in own.get("include", []):
        combined.update(filament(include, sources))
    combined.update(own)
    for key in ("inherits", "include", "name", "type", "from", "setting_id", "instantiation"):
        combined.pop(key, None)
    return combined


def settings():
    with zipfile.ZipFile(DONOR) as z:
        if z.testzip() is not None:
            raise ValueError("Damaged Mark1 machine-profile donor")
        original = json.loads(z.read(SETTINGS))
    result = dict(original)
    profiles = {}
    result.update(filament("Bambu TPU 85A @BBL H2C", profiles))
    # This is one filament feeding the right fixed nozzle. Preserve the donor's
    # full printer/start G-code while replacing its process and filament settings.
    result.update({
        "filament_settings_id": ["Bambu TPU 85A @BBL H2C"],
        "filament_colour": ["#161616"], "filament_type": ["TPU"],
        "filament_map": ["2"], "filament_nozzle_map": ["1"],
        "filament_extruder_compatibility": ["0"],
        "curr_bed_type": "Textured PEI Plate",
        "layer_height": "0.12", "initial_layer_print_height": "0.20",
        "wall_loops": "6", "wall_generator": "arachne",
        "spiral_mode": "0", "spiral_mode_smooth": "0",
        "top_shell_layers": "3", "bottom_shell_layers": "3",
        "skin_infill_density": "100%", "skeleton_infill_density": "100%",
        "enable_support": "0", "raft_layers": "0",
        "sparse_infill_density": "100%", "sparse_infill_pattern": "zig-zag",
        "seam_gap": "0%", "brim_width": "5", "brim_type": "outer_only",
        "print_settings_id": "Continuous TPU elbow 0.12 mm right 0.6 Mark1",
    })
    for key in ("line_width", "initial_layer_line_width", "outer_wall_line_width",
                "inner_wall_line_width", "sparse_infill_line_width",
                "internal_solid_infill_line_width", "top_surface_line_width",
                "support_line_width"):
        result[key] = "0.62"
    for key in ("outer_wall_speed", "inner_wall_speed", "sparse_infill_speed",
                "internal_solid_infill_speed", "top_surface_speed", "initial_layer_speed",
                "initial_layer_infill_speed", "gap_infill_speed", "bridge_speed"):
        result[key] = ["25"] * 4
    if result["machine_start_gcode"] != original["machine_start_gcode"]:
        raise ValueError("The Mark1 donor's start G-code changed")
    if list(map(float, result["nozzle_diameter"])) != [0.6, 0.6]:
        raise ValueError("The donor is not the accepted two-head 0.6 mm profile")
    area = np.array([[float(v) for v in p.split("x")]
                     for p in result["extruder_printable_area"][1].split(",")])
    return result, original, profiles, area.min(axis=0), area.max(axis=0)


def make_project(recipe, low, high):
    shapes = [Elbow(tube_depth=15).print_shape() for _ in range(2)]
    boxes = [s.BoundingBox() for s in shapes]
    shifts = [-GAP / 2 - boxes[0].xmax, GAP / 2 - boxes[1].xmin]
    centre = ((boxes[0].xmin + shifts[0]) + (boxes[1].xmax + shifts[1])) / 2
    shifts = [shift - centre for shift in shifts]
    bed_centre = (low + high) / 2
    mid_gap = -centre + bed_centre[0]
    members = {SETTINGS: (json.dumps(recipe, indent=2) + "\n").encode()}
    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p")
    ET.SubElement(model, qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
    ET.SubElement(model, qn("metadata"), name="Title").text = "Continuous TPU elbows - Mark1"
    resources = ET.SubElement(model, qn("resources"))
    owner = ET.SubElement(resources, qn("object"), id="3", type="model",
                          **{f"{{{PROD}}}UUID": uid("object")})
    components = ET.SubElement(owner, qn("components"))
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": uid("build")})
    transform = f"1 0 0 0 1 0 0 0 1 {bed_centre[0]:.9f} {bed_centre[1]:.9f} 0"
    ET.SubElement(build, qn("item"), objectid="3", transform=transform, printable="1",
                  **{f"{{{PROD}}}UUID": uid("item")})
    model_rels = ET.Element(f"{{{REL}}}Relationships")
    config = ET.Element("config")
    object_config = ET.SubElement(config, "object", id="3")
    metadata(object_config, "name", "Two 15 mm tube-socket elbows")
    metadata(object_config, "extruder", 1)
    records, face_count = [], 0
    for part_id, (shape, shift, depth) in enumerate(zip(shapes, shifts, (15, 15)), 1):
        name = f"elbow-tube-socket-{depth}mm-{part_id}"
        source = HERE / (name + ".stl")
        posed = shape.translate(cq.Vector(shift, 0, 0))
        cq.exporters.export(posed, str(source), tolerance=.01, angularTolerance=.05)
        mesh = trimesh.load(source, force="mesh", process=True)
        raw_hash, raw_faces, raw_volume = sha(source.read_bytes()), len(mesh.faces), float(mesh.volume)
        # OCC can emit collapsed triangles at the sphere's tangent poles.
        # Native mesh cleanup removes those facets without changing the surface.
        mesh.process(validate=True)
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or mesh.body_count != 1:
            raise ValueError(f"{name} is not one closed, oriented mesh")
        source.write_bytes(mesh.export(file_type="stl"))
        placed = mesh.bounds + np.array([*bed_centre, 0.0])
        if np.any(placed[0, :2] < low + 20) or np.any(placed[1, :2] > high - 20):
            raise ValueError("Elbow models enter the 20 mm usable-bed inset")
        child = ET.Element(qn("model"), unit="millimeter")
        child_resources = ET.SubElement(child, qn("resources"))
        volume = ET.SubElement(child_resources, qn("object"), id=str(part_id), type="model",
                               **{f"{{{PROD}}}UUID": uid(name + "/mesh")})
        geometry = ET.SubElement(volume, qn("mesh"))
        vertices = ET.SubElement(geometry, qn("vertices"))
        triangles = ET.SubElement(geometry, qn("triangles"))
        for vertex in mesh.vertices:
            ET.SubElement(vertices, qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
        for triangle in mesh.faces:
            ET.SubElement(triangles, qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))
        member = f"3D/Objects/elbow_{part_id}.model"
        members[member] = xml(child)
        ET.SubElement(components, qn("component"), objectid=str(part_id), transform=IDENTITY,
                      **{f"{{{PROD}}}path": "/" + member, f"{{{PROD}}}UUID": uid(name + "/component")})
        ET.SubElement(model_rels, f"{{{REL}}}Relationship", Target="/" + member, Id=f"rel-{part_id}",
                      Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        part = ET.SubElement(object_config, "part", id=str(part_id), subtype="normal_part", uuid=uid(name))
        for key, value in {"name": name, "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                           "extruder": 1, "source_file": source.name, "source_object_id": 0,
                           "source_volume_id": 0, "source_offset_x": 0,
                           "source_offset_y": 0, "source_offset_z": 0}.items():
            metadata(part, key, value)
        ET.SubElement(part, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                      degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
        face_count += len(mesh.faces)
        records.append({"name": name, "tube_socket_depth_mm": depth, "source": source.name,
                        "source_sha256": sha(source.read_bytes()), "triangles": len(mesh.faces),
                        "raw_occ_stl_sha256": raw_hash, "export_cleanup_removed_faces": raw_faces - len(mesh.faces),
                        "raw_volume_mm3": raw_volume, "cleaned_volume_mm3": float(mesh.volume),
                        "bed_relative_x_shift_mm": shift, "plate_bounds_mm": placed.tolist(),
                        "watertight": True, "winding_consistent": True})
    ET.SubElement(object_config, "metadata", face_count=str(face_count))
    plate = ET.SubElement(config, "plate")
    for key, value in {"plater_id": 1, "plater_name": "Continuous TPU elbows - Mark1",
                       "locked": "false", "filament_map_mode": "Auto For Flush",
                       "filament_maps": "2", "filament_volume_maps": "0",
                       "bed_type": recipe["curr_bed_type"]}.items():
        metadata(plate, key, value)
    instance = ET.SubElement(plate, "model_instance")
    for key, value in {"object_id": 3, "instance_id": 0, "identify_id": 1901}.items():
        metadata(instance, key, value)
    assembled = ET.SubElement(config, "assemble")
    ET.SubElement(assembled, "assemble_item", object_id="3", instance_id="0", transform=transform, offset="0 0 0")
    members["3D/3dmodel.model"] = xml(model)
    members["Metadata/model_settings.config"] = xml(config)
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
    archive_write(PROJECT, members)
    return records, mid_gap


def arc_points(start, end, words, clockwise):
    if "I" not in words and "J" not in words:
        raise ValueError("A deposited arc has no centre offsets")
    cx, cy = start[0] + words.get("I", 0), start[1] + words.get("J", 0)
    radius = math.dist(start, (cx, cy))
    a0, a1 = math.atan2(start[1] - cy, start[0] - cx), math.atan2(end[1] - cy, end[0] - cx)
    if clockwise:
        while a1 >= a0:
            a1 -= 2 * math.pi
    else:
        while a1 <= a0:
            a1 += 2 * math.pi
    points = [start, end]
    for k in range(math.floor(min(a0, a1) / (math.pi / 2)), math.ceil(max(a0, a1) / (math.pi / 2)) + 1):
        angle = k * math.pi / 2
        if min(a0, a1) <= angle <= max(a0, a1):
            points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
    return points


def beads(gcode, middle_x):
    xyz = dict(X=0., Y=0., Z=0.)
    e, relative_e, absolute_xy = 0., True, True
    feature, width = "Custom", .62
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    left_high, right_low = -math.inf, math.inf
    brim_left_high, brim_right_low = -math.inf, math.inf
    features, paths, volumes = Counter(), Counter(), Counter()
    merged_brim = False
    for raw in gcode.decode().splitlines():
        if raw.startswith("; FEATURE:"):
            feature = raw.split(":", 1)[1].strip()
            features[feature] += 1
        if raw.startswith("; LINE_WIDTH:"):
            width = float(raw.split(":", 1)[1])
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
            for key in xyz:
                xyz[key] = words.get(key, xyz[key])
        if cmd not in ("G0", "G1", "G2", "G3"):
            continue
        start = (xyz["X"], xyz["Y"])
        next_xyz = {key: words.get(key, xyz[key]) if absolute_xy else xyz[key] + words.get(key, 0)
                    for key in xyz}
        end = (next_xyz["X"], next_xyz["Y"])
        extruding = words.get("E", 0) > 0 if relative_e else words.get("E", e) > e
        if extruding and feature != "Custom" and (math.dist(start, end) > 1e-9 or cmd in ("G2", "G3")):
            points = arc_points(start, end, words, cmd == "G2") if cmd in ("G2", "G3") else [start, end]
            path_low, path_high = np.min(points, axis=0) - width / 2, np.max(points, axis=0) + width / 2
            low, high = np.minimum(low, path_low), np.maximum(high, path_high)
            paths[feature] += 1
            delta_e = words.get("E", 0) if relative_e else words.get("E", e) - e
            volumes[feature] += delta_e * math.pi * (1.75 / 2) ** 2
            is_brim = "brim" in feature.lower() or "skirt" in feature.lower()
            if is_brim:
                merged_brim |= bool(path_low[0] <= middle_x <= path_high[0])
                if path_high[0] < middle_x:
                    brim_left_high = max(brim_left_high, path_high[0])
                elif path_low[0] > middle_x:
                    brim_right_low = min(brim_right_low, path_low[0])
            elif path_high[0] < middle_x:
                left_high = max(left_high, path_high[0])
            elif path_low[0] > middle_x:
                right_low = min(right_low, path_low[0])
            else:
                raise ValueError(f"Native {feature} bead enters the inter-elbow clearance")
        xyz = next_xyz
        if "E" in words:
            e = e + words["E"] if relative_e else words["E"]
    if not np.all(np.isfinite(low)) or not math.isfinite(left_high + right_low):
        raise ValueError("Native deposition envelopes are unavailable")
    if any("support" in name.lower() for name in paths):
        raise ValueError("The support-disabled slice contains deposited support")
    return {"native_full_bead_bounds_xy_mm": [low.tolist(), high.tolist()],
            "native_feature_counts": dict(features), "native_deposited_path_counts": dict(paths),
            "native_model_bead_separation_x_mm": right_low - left_high,
            "native_brim_beads_cross_inter_elbow_gap": merged_brim,
            "native_separate_brim_bead_gap_x_mm": brim_right_low - brim_left_high if not merged_brim else None,
            "native_deposited_filament_volume_by_feature_mm3": dict(volumes),
            "scope": "XY bead widths and arc extrema; physical adhesion is unmeasured"}


def main():
    cache = ROOT / ".cache/printer-control/continuous-body-elbows-mark1-20261013"
    cache.mkdir(parents=True, exist_ok=True)
    run = Path(tempfile.mkdtemp(prefix="native-", dir=cache))
    source_hash = sha((STUDY / "tpu_elbow.py").read_bytes())
    recipe, original, profile_sources, low, high = settings()
    parts, middle_x = make_project(recipe, low, high)
    preparation = {
        "scope": "Current CAD and offline native slice for Mark1; physical result pending",
        "printer": "Mark1 (H2C)", "material": "TPU 85A",
        "nozzle_mapping": "Right fixed 0.6 mm; external spool 255; TPU / 161616",
        "source_geometry": "future/pump-elbow-exploration/tpu_elbow.py",
        "source_geometry_sha256": source_hash,
        "machine_profile_donor": str(DONOR.relative_to(ROOT)), "machine_profile_donor_sha256": sha(DONOR.read_bytes()),
        "machine_start_gcode_sha256": sha(recipe["machine_start_gcode"].encode()),
        "native_filament_profile_sources_sha256": profile_sources,
        "project": PROJECT.name, "project_sha256": sha(PROJECT.read_bytes()),
        "parts": parts, "physical_model_gap_mm": GAP,
        "native_object_structure": "One object with two named normal volumes; native outer brims",
        "usable_bed_bounds_xy_mm": [low.tolist(), high.tolist()],
        "resolved_process_settings": {key: value for key, value in recipe.items()
                                      if original.get(key) != value},
    }
    PROJECT.with_suffix(".print.json").write_text(json.dumps(preparation, indent=2) + "\n")
    command = [str(SLICER), "--slice", "0", "--arrange", "0", "--orient", "0",
               "--export-3mf", ARCHIVE.name, "--outputdir", str(run), str(PROJECT)]
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
        if hashlib.md5(gcode).hexdigest() != z.read("Metadata/plate_1.gcode.md5").decode().strip().lower():
            raise ValueError("Native G-code checksum error")
        emitted = json.loads(z.read(SETTINGS))
        slice_info = ET.fromstring(z.read("Metadata/slice_info.config"))
    trims = [float(v) for v in re.findall(rb"^\s*G29\.1 Z([-+.\d]+)", gcode, re.M)]
    if trims != [0.0, 0.16]:
        raise ValueError(f"Unexpected Mark1 trim: {trims}")
    if emitted["filament_map"] != ["2"] or emitted["filament_colour"] != ["#161616"]:
        raise ValueError("The native right-external filament mapping changed")
    for key in ("wall_loops", "sparse_infill_density", "spiral_mode", "enable_support"):
        if emitted.get(key) != recipe[key]:
            raise ValueError(f"Native process differs from requested {key}: {emitted.get(key)}")
    plate, = slice_info.findall("plate")
    used, = plate.findall("filament")
    if used.get("type") != "TPU" or used.get("color").lstrip("#").upper()[:6] != "161616":
        raise ValueError("The active sliced filament is not black TPU")
    deposited = beads(gcode, middle_x)
    bead_low, bead_high = map(np.array, deposited["native_full_bead_bounds_xy_mm"])
    margins = [*(bead_low - low), *(high - bead_high)]
    if min(margins) < 20 or deposited["native_model_bead_separation_x_mm"] <= 0:
        raise ValueError("Native beads violate the bed inset or model separation")
    if sha((STUDY / "tpu_elbow.py").read_bytes()) != source_hash:
        raise ValueError("The elbow source changed during preparation")
    (run / "plate_1.gcode").write_bytes(gcode)
    ARCHIVE.write_bytes(native.read_bytes())
    sliced_plate, = result["sliced_plates"]
    checked_keys = ("printer_settings_id", "filament_settings_id", "filament_map", "filament_nozzle_map",
                    "filament_colour", "nozzle_diameter", "curr_bed_type", "nozzle_temperature",
                    "nozzle_temperature_initial_layer", "textured_plate_temp", "filament_max_volumetric_speed",
                    "layer_height", "initial_layer_print_height", "wall_loops", "wall_generator",
                    "sparse_infill_density", "spiral_mode", "spiral_mode_smooth", "top_shell_layers",
                    "bottom_shell_layers", "seam_gap", "enable_support", "brim_width", "brim_type")
    readiness = {
        "status": "Native slice read back; no printer submission; physical result pending",
        "observed_at": datetime.now(timezone.utc).isoformat(), "cache_run": str(run.relative_to(ROOT)),
        "project": PROJECT.name, "project_sha256": preparation["project_sha256"],
        "archive": ARCHIVE.name, "archive_sha256": sha(ARCHIVE.read_bytes()), "gcode_sha256": sha(gcode),
        "plate_trim_commands_mm": trims, "emitted_settings": {k: emitted.get(k) for k in checked_keys},
        "native_active_filament": used.attrib, "physical_model_gap_mm": GAP,
        "usable_bed_bounds_xy_mm": [low.tolist(), high.tolist()],
        "full_bead_edge_margins_xy_mm": margins, "minimum_full_bead_edge_margin_mm": min(margins),
        "layers": int(re.search(rb"^; total layer number: (\d+)", gcode, re.M).group(1)),
        "estimated_seconds": sliced_plate["total_predication"],
        "estimated_filament_g": sum(f["total_used_g"] for f in sliced_plate["filaments"]),
        "estimate_density_g_cm3": emitted["filament_density"],
        "slicer_warning": sliced_plate["warning_message"], **deposited,
    }
    PROJECT.with_suffix(".readiness.json").write_text(json.dumps(readiness, indent=2) + "\n")
    print(json.dumps(readiness, indent=2))


if __name__ == "__main__":
    main()
