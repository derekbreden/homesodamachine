"""Refresh the faucet's four meshes using the shared PET-GF profile's complete settings."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
SETTINGS_MEMBER = "Metadata/project_settings.config"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(HERE / "faucet-shell"))
import faucet_shell as shell

PARTS = (
    ("faucet-shell-base", HERE / "faucet-shell/faucet-shell-base.stl", -math.degrees(shell.print_base_build_rot)),
    ("faucet-shell-tip", HERE / "faucet-shell/faucet-shell-tip.stl", -math.degrees(shell.print_tip_build_rot)),
    ("faucet-display-cover", HERE / "faucet-display-cover/faucet-display-cover.stl", -50.0),
    ("above-counter-plate", HERE / "above-counter-plate/above-counter-plate.stl", 0.0),
)
# Millimetres from the centre of the shared printable area. The base occupies
# the left column; the other three parts have separate support/brim spaces.
PART_OFFSETS = ((-80.0, 0.0), (20.0, 47.0), (89.0, 110.0), (43.0, -52.0))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def qn(name: str) -> str:
    return f"{{{CORE}}}{name}"


def metadata(parent, key, value):
    ET.SubElement(parent, "metadata", key=key, value=str(value))


def identifier(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "homesodamachine/faucet/" + name))


def xml(element) -> bytes:
    return ET.tostring(element, xml_declaration=True, encoding="UTF-8")


def archive_write(path: Path, members: dict[str, bytes]):
    temporary = path.with_suffix(path.suffix + ".tmp")
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
        for name, data in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data, compresslevel=6)
    temporary.replace(path)


def refresh(settings_from: Path, output: Path, *, parts: tuple | None = None,
            offsets: tuple | None = None, title: str = "Faucet PET-GF",
            z_trim: float | None = None, plate_border: float = 15.0) -> dict:
    parts = PARTS if parts is None else parts
    offsets = PART_OFFSETS if offsets is None else offsets
    if len(parts) != len(offsets):
        raise ValueError("Each print-project part needs one bed-position offset")
    with zipfile.ZipFile(settings_from) as source:
        if source.testzip() is not None:
            raise ValueError("source project has a damaged member")
        settings_payload = source.read(SETTINGS_MEMBER)
        original_settings_payload = settings_payload
        settings = json.loads(settings_payload)
        settings_changes = {}
        if z_trim is not None:
            if not math.isfinite(z_trim):
                raise ValueError("Z trim must be a finite millimetre value")
            original_start = settings["machine_start_gcode"]
            marker = re.search(r"(?m)^;===== (?:for Textured PEI Plate|plate compensation plus user-calibrated)", original_start)
            if marker is None:
                raise ValueError("The profile has no recognized plate-compensation block")
            end = original_start.index("\nG150.1", marker.start())
            block = f''';===== plate compensation plus user-calibrated +{z_trim:.2f} mm Z trim =====
{{if curr_bed_type=="Textured PEI Plate"}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{z_trim:.2f} - 0.01}}
    {{else}}
        G29.1 Z{{{z_trim:.2f} - 0.02}}
    {{endif}}
{{else}}
    {{if nozzle_diameter_at_nozzle_id[initial_nozzle_id] == 0.2}}
        G29.1 Z{{{z_trim:.2f} + 0.01}}
    {{else}}
        G29.1 Z{{{z_trim:.2f}}}
    {{endif}}
{{endif}}'''
            settings["machine_start_gcode"] = original_start[:marker.start()] + block + original_start[end:]
            nozzle = float(settings["nozzle_diameter"][0])
            identity = f"Bambu Lab H2C {nozzle:g} Standard +{z_trim:.2f} Z trim"
            settings_changes = {
                "machine_start_gcode": {"from_sha256": digest(original_start.encode()),
                                       "to_sha256": digest(settings["machine_start_gcode"].encode()),
                                       "requested_z_trim_mm": z_trim},
                "printer_settings_id": {"from": settings["printer_settings_id"], "to": identity},
            }
            settings["printer_settings_id"] = identity
            settings_payload = (json.dumps(settings, indent=2) + "\n").encode()
        bed_points = np.array([[float(value) for value in point.split("x")] for point in settings["printable_area"]])
        # The plate is what the nozzles this job maps its filaments to can reach: the left
        # nozzle's area alone for a one-filament job, both nozzles' intersection for two.
        all_areas = [np.array([[float(value) for value in point.split("x")] for point in area.split(",")])
                     for area in settings.get("extruder_printable_area", [])]
        used = sorted({int(n) for n in settings.get("filament_nozzle_map", [])} & set(range(len(all_areas))))
        extruder_areas = [all_areas[i] for i in used] if used else all_areas
        usable_low = np.max([area.min(axis=0) for area in extruder_areas], axis=0) if extruder_areas else bed_points.min(axis=0)
        usable_high = np.min([area.max(axis=0) for area in extruder_areas], axis=0) if extruder_areas else bed_points.max(axis=0)
        members = {SETTINGS_MEMBER: settings_payload}
        for name in source.namelist():
            if name.startswith("Metadata/filament_settings_") and name.endswith(".config"):
                members[name] = source.read(name)
    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    ET.SubElement(model, qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
    ET.SubElement(model, qn("metadata"), name="Title").text = title
    resources = ET.SubElement(model, qn("resources"))
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": identifier("build")})
    config = ET.Element("config")
    assembled = ET.Element("assemble")
    model_rels = ET.Element(f"{{{REL}}}Relationships")
    report = {
        "project": output.name,
        "settings_source": str(settings_from.relative_to(ROOT)) if settings_from.is_relative_to(ROOT) else str(settings_from),
        "settings_source_sha256": digest(settings_from.read_bytes()),
        "settings_sha256": digest(settings_payload),
        "source_settings_sha256": digest(original_settings_payload),
        "settings_changes": settings_changes,
        "printer": settings["printer_settings_id"],
        "process": settings["print_settings_id"],
        "filament": settings["filament_settings_id"],
        "layer_height_mm": float(settings["layer_height"]),
        "nozzle_diameter_mm": [float(value) for value in settings["nozzle_diameter"]],
        "line_widths_mm": {key: float(settings[key]) for key in (
            "outer_wall_line_width", "inner_wall_line_width", "sparse_infill_line_width",
            "internal_solid_infill_line_width", "top_surface_line_width", "support_line_width")},
        "wall_loops": int(settings["wall_loops"]),
        "sparse_infill_percent": float(settings["sparse_infill_density"].rstrip("%")),
        "sparse_infill_pattern": settings["sparse_infill_pattern"],
        "saved_profile_filament_density_g_cm3": [float(value) for value in settings["filament_density"]],
        "bed_type": settings["curr_bed_type"],
        "shared_printable_area_mm": [usable_low.tolist(), usable_high.tolist()],
        "printable_area_extruders": used if used else list(range(len(all_areas))),
        "plate_border_mm": plate_border,
        "plate_count": 1,
        "parts": [],
    }
    plate = ET.Element("plate")
    for key, value in {"plater_id": 1, "plater_name": title, "locked": "false",
                       "filament_map_mode": "Auto For Flush", "filament_maps": "1",
                       "filament_volume_maps": "0", "bed_type": settings["curr_bed_type"]}.items():
        metadata(plate, key, value)
    for part_index, (name, source_path, angle) in enumerate(parts, 1):
        payload = source_path.read_bytes()
        mesh = trimesh.load(source_path, force="mesh", process=True)
        if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or mesh.body_count != 1:
            raise ValueError(f"{source_path.name} is not one closed, oriented volume")
        center = mesh.bounds.mean(axis=0)
        local_vertices = mesh.vertices - center
        theta = math.radians(angle)
        rotation = np.array([[1, 0, 0], [0, math.cos(theta), -math.sin(theta)], [0, math.sin(theta), math.cos(theta)]])
        rotated = local_vertices @ rotation.T
        low, high = rotated.min(axis=0), rotated.max(axis=0)
        plate_center = np.array([*((usable_low + usable_high) / 2.0 + offsets[part_index - 1]), 0.0])
        local_translation = plate_center - (low + high) / 2.0
        local_translation[2] = -low[2]
        placed = rotated + local_translation
        margin = plate_border
        if np.any(placed[:, :2].min(axis=0) < usable_low + margin) or np.any(placed[:, :2].max(axis=0) > usable_high - margin):
            raise ValueError(f"{name} extends into the {margin:g} mm plate border")
        if placed[:, 2].max() > float(settings["printable_height"]):
            raise ValueError(f"{name} exceeds the printer height")
        plate_origin = np.zeros(3)
        global_translation = local_translation + plate_origin
        transform_values = [*rotation.T.reshape(-1), *global_translation]
        transform = " ".join(f"{value:.9f}" for value in transform_values)
        part_id, object_id = str(2 * part_index - 1), str(2 * part_index)
        member_path = f"/3D/Objects/object_{part_index}.model"
        part_model = ET.Element(qn("model"), unit="millimeter")
        part_resources = ET.SubElement(part_model, qn("resources"))
        mesh_object = ET.SubElement(part_resources, qn("object"), id=part_id, type="model")
        geometry = ET.SubElement(mesh_object, qn("mesh"))
        vertices = ET.SubElement(geometry, qn("vertices"))
        triangles = ET.SubElement(geometry, qn("triangles"))
        for vertex in local_vertices:
            ET.SubElement(vertices, qn("vertex"), **dict(zip(("x", "y", "z"), (f"{value:.9f}" for value in vertex))))
        for triangle in mesh.faces:
            ET.SubElement(triangles, qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))
        members[member_path.lstrip("/")] = xml(part_model)
        obj = ET.SubElement(resources, qn("object"), id=object_id, type="model", **{f"{{{PROD}}}UUID": identifier(name)})
        components = ET.SubElement(obj, qn("components"))
        ET.SubElement(components, qn("component"), objectid=part_id, transform="1 0 0 0 1 0 0 0 1 0 0 0",
                      **{f"{{{PROD}}}path": member_path, f"{{{PROD}}}UUID": identifier(name + "/component")})
        ET.SubElement(build, qn("item"), objectid=object_id, transform=transform, printable="1",
                      **{f"{{{PROD}}}UUID": identifier(name + "/item")})
        ET.SubElement(model_rels, f"{{{REL}}}Relationship", Target=member_path, Id=f"rel-{part_index}",
                      Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        obj_config = ET.SubElement(config, "object", id=object_id)
        metadata(obj_config, "name", name)
        metadata(obj_config, "extruder", 1)
        ET.SubElement(obj_config, "metadata", face_count=str(len(mesh.faces)))
        part_config = ET.SubElement(obj_config, "part", id=part_id, subtype="normal_part", uuid=identifier(name + "/part"))
        for key, value in {"name": name, "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1", "source_file": source_path.name,
                           "source_object_id": 0, "source_volume_id": 0,
                           "source_offset_x": center[0], "source_offset_y": center[1], "source_offset_z": center[2]}.items():
            metadata(part_config, key, value)
        ET.SubElement(part_config, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0", degenerate_facets="0",
                      facets_removed="0", facets_reversed="0", backwards_edges="0")
        instance = ET.SubElement(plate, "model_instance")
        for key, value in {"object_id": object_id, "instance_id": 0, "identify_id": 1900 + part_index}.items():
            metadata(instance, key, value)
        ET.SubElement(assembled, "assemble_item", object_id=object_id, instance_id="0", transform=transform, offset="0 0 0")
        ET.SubElement(assembled, "assemble_item", object_id=object_id, volume_id="0", transform="1 0 0 0 1 0 0 0 1 0 0 0")
        report["parts"].append({
            "name": name, "plate": 1, "object_id": object_id, "part_id": part_id,
            "member": member_path.lstrip("/"), "identify_id": 1900 + part_index,
            "source": str(source_path.relative_to(ROOT)), "stl_sha256": digest(payload),
            "triangles": len(mesh.faces), "rotation_x_degrees": angle,
            "source_center_mm": center.tolist(), "build_transform": transform_values,
            "plate_translation_mm": local_translation.tolist(),
            "plate_origin_mm": plate_origin.tolist(),
            "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
            "watertight": True, "body_count": 1,
        })
    config.append(plate)
    config.append(assembled)
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
    archive_write(output, members)
    with zipfile.ZipFile(output) as rebuilt:
        assert rebuilt.testzip() is None
        assert rebuilt.read(SETTINGS_MEMBER) == settings_payload
        assert len(ET.fromstring(rebuilt.read("Metadata/model_settings.config")).findall("plate")) == 1
        for row in report["parts"]:
            child = ET.fromstring(rebuilt.read(row["member"]))
            serialized = child.find(f"{qn('resources')}/{qn('object')}/{qn('mesh')}")
            restored = np.array([[float(vertex.get(axis)) for axis in ("x", "y", "z")] for vertex in serialized.find(qn("vertices"))])
            source = trimesh.load(ROOT / row["source"], force="mesh", process=True)
            error = float(np.max(np.abs(restored + row["source_center_mm"] - source.vertices)))
            assert error < 1e-6
            restored_faces = np.array([[int(triangle.get(key)) for key in ("v1", "v2", "v3")] for triangle in serialized.find(qn("triangles"))])
            assert np.array_equal(restored_faces, source.faces)
            row["embedded_vertex_error_mm"] = error
    report["project_sha256"] = digest(output.read_bytes())
    report["settings_preserved_byte_for_byte"] = settings_payload == original_settings_payload
    output.with_suffix(".print.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def object_toolpaths(gcode: Path, output: Path, identify_id: int) -> dict:
    """Mask other objects' feature labels for reading, retaining all coordinate moves."""
    from enclosure_support_audit import _WORD, _arc_points

    current = None
    x = y = e = 0.0
    absolute_xy, relative_e = True, True
    layer_seen, selected_seen = False, False
    width = 0.0
    low, high = np.full(2, np.inf), np.full(2, -np.inf)
    with gcode.open() as source, output.open("w") as target:
        for raw in source:
            line = raw.strip()
            start = re.match(r"; start printing object, unique label id: (\d+)", line)
            if start:
                current = int(start.group(1))
                selected_seen |= current == identify_id
                target.write("; FEATURE: Other object\n")
            elif line.startswith("; stop printing object"):
                current = None
                target.write("; FEATURE: Other object\n")
            if line.startswith("; FEATURE:") and current != identify_id:
                target.write("; FEATURE: Other object\n")
            else:
                target.write(raw)
            if line.startswith("; Z_HEIGHT:"):
                layer_seen = True
            if line.startswith("; LINE_WIDTH:") and current == identify_id:
                width = max(width, float(line.split(":", 1)[1]))
            code = line.split(";", 1)[0].strip()
            if not code:
                continue
            command = code.split(None, 1)[0]
            words = {key: float(value) for key, value in _WORD.findall(code)}
            if command in {"G90", "G91"}:
                absolute_xy = command == "G90"
            elif command in {"M82", "M83"}:
                relative_e = command == "M83"
            elif command == "G92":
                x, y, e = words.get("X", x), words.get("Y", y), words.get("E", e)
            elif command in {"G0", "G1", "G2", "G3"}:
                nx = words.get("X", x) if absolute_xy else x + words.get("X", 0.0)
                ny = words.get("Y", y) if absolute_xy else y + words.get("Y", 0.0)
                de = words.get("E", 0.0) if relative_e else words.get("E", e) - e
                if current == identify_id and layer_seen and de > 1e-9 and (nx != x or ny != y):
                    points = [(x, y)] + ([(nx, ny)] if command in {"G0", "G1"} else
                                         _arc_points((x, y), (nx, ny), words, command == "G2"))
                    low = np.minimum(low, np.min(points, axis=0))
                    high = np.maximum(high, np.max(points, axis=0))
                x, y = nx, ny
                if "E" in words:
                    e = e + words["E"] if relative_e else words["E"]
    if not selected_seen or not np.all(np.isfinite(low)):
        raise ValueError(f"no extrusion toolpaths for object label {identify_id}")
    # The arc reader samples at <=0.18 mm; this extra allowance covers the
    # sagitta as well as the actual extrusion's half width.
    padding = max(width, 0.6) / 2.0 + 0.1
    return {"extrusion_bounds_xy_mm": [(low - padding).tolist(), (high + padding).tolist()],
            "maximum_line_width_mm": width, "bounds_padding_mm": padding}


def slice_review(project: Path, report: dict, directory: Path) -> dict:
    """Read each plate's toolpaths in its own placement and retain support topology."""
    sys.path.insert(0, str(ROOT / "hardware/scripts"))
    from enclosure_support_audit import audit

    assert digest(project.read_bytes()) == report["project_sha256"]
    with zipfile.ZipFile(project) as archive:
        members = {name: archive.read(name) for name in archive.namelist()}
        assert digest(members[SETTINGS_MEMBER]) == report["settings_sha256"]
    result_path = directory / "result.json"
    sliced = json.loads(result_path.read_text())
    if sliced.get("return_code") != 0:
        raise ValueError(f"Bambu slice failed: {sliced.get('error_string')}")
    result = {
        "project": str(project.relative_to(ROOT)) if project.is_relative_to(ROOT) else project.name,
        "project_sha256": digest(project.read_bytes()),
        "settings_sha256": report["settings_sha256"],
        "slicer": None,
        "layer_height_mm": sliced["layer_height"],
        "wall_loops": sliced["wall_loops"],
        "sparse_infill_density_percent": sliced["sparse_infill_density"],
        "saved_profile_filament_density_g_cm3": report["saved_profile_filament_density_g_cm3"],
        "mass_estimate_note": "Slicer grams use the saved profile density, not a measured PET-GF part mass.",
        "plates": [],
        "parts": [],
    }
    sliced_plates = {row["id"]: row for row in sliced["sliced_plates"]}
    for plate_id, row in sliced_plates.items():
        result["plates"].append({"plate": plate_id,
                                 "estimated_total_seconds": row["total_predication"],
                                 "saved_profile_filament_estimate_g": sum(f["total_used_g"] for f in row["filaments"]),
                                 "slicer_warning": row["warning_message"]})
    for part in report["parts"]:
        if digest((ROOT / part["source"]).read_bytes()) != part["stl_sha256"]:
            raise ValueError(f"{part['name']} source changed after the project was refreshed")
        gcode = directory / f"plate_{part['plate']}.gcode"
        if not gcode.is_file():
            raise ValueError(f"missing slice: {gcode}")
        one = dict(members)
        model = ET.fromstring(one["3D/3dmodel.model"])
        resources, build = model.find(qn("resources")), model.find(qn("build"))
        for item in list(resources):
            if item.get("id") != part["object_id"]:
                resources.remove(item)
        for item in list(build):
            if item.get("objectid") != part["object_id"]:
                build.remove(item)
            else:
                values = part["build_transform"][:9] + part["plate_translation_mm"]
                item.set("transform", " ".join(f"{value:.9f}" for value in values))
        config = ET.fromstring(one["Metadata/model_settings.config"])
        for item in list(config):
            if item.tag != "object" or item.get("id") != part["object_id"]:
                config.remove(item)
        one["3D/3dmodel.model"], one["Metadata/model_settings.config"] = xml(model), xml(config)
        coordinates = directory / f"coordinates-{part['name']}.3mf"
        archive_write(coordinates, one)
        filtered = directory / f"support-labels-{part['name']}.gcode"
        bounds = object_toolpaths(gcode, filtered, part["identify_id"])
        reading = audit(filtered, part["name"], ROOT / part["source"], project, coordinates,
                        profile_label=result["project"], include_unlabelled_support=True)
        if result["slicer"] is None:
            result["slicer"] = reading["slicer"]
        elif reading["slicer"] != result["slicer"]:
            raise ValueError("plate G-code files come from different slicer versions")
        reading["plate"] = part["plate"]
        reading["rotation_x_degrees"] = part["rotation_x_degrees"]
        reading["toolpaths"] = bounds
        reading["inputs"]["plate_gcode_sha256"] = digest(gcode.read_bytes())
        reading["inputs"]["object_label"] = part["identify_id"]
        reading["inputs"]["feature_filter"] = "Other objects' feature labels are masked; coordinates and extrusion commands are retained."
        result["parts"].append(reading)
        print(f"  {part['name']}: {reading['summary']}", flush=True)
    area_low, area_high = np.array(report["shared_printable_area_mm"])
    margins, gaps = [], []
    for index, part in enumerate(result["parts"]):
        low, high = np.array(part["toolpaths"]["extrusion_bounds_xy_mm"])
        margin = float(min(np.min(low - area_low), np.min(area_high - high)))
        if margin < 15.0:
            raise ValueError(f"{part['piece']} toolpaths enter the 15 mm plate border")
        margins.append(margin)
        for other in result["parts"][:index]:
            other_low, other_high = np.array(other["toolpaths"]["extrusion_bounds_xy_mm"])
            gap = float(np.linalg.norm(np.maximum(0.0, np.maximum(low - other_high, other_low - high))))
            if gap < 10.0:
                raise ValueError(f"toolpaths of {part['piece']} and {other['piece']} are only {gap:.2f} mm apart")
            gaps.append({"parts": [other["piece"], part["piece"]], "separation_mm": gap})
    result["fit"] = {"minimum_shared_bed_margin_mm": min(margins),
                     "minimum_toolpath_separation_mm": min(row["separation_mm"] for row in gaps),
                     "pairwise_toolpath_separations": gaps}
    output = project.with_suffix(".support-audit.json")
    output.write_text(json.dumps(result, indent=2) + "\n")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=HERE / "faucet-petgf.3mf")
    parser.add_argument("--settings-from", type=Path, default=ROOT / "hardware/printed-parts/petgf.3mf")
    parser.add_argument("--z-trim", type=float, help="User Z trim in mm, added to the existing stock plate compensation.")
    parser.add_argument("--slice-output", type=Path, help="Optional local Bambu CLI slice directory; no printer connection.")
    parser.add_argument("--slicer", type=Path, default=Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"))
    args = parser.parse_args()
    report = refresh(args.settings_from.resolve(), args.project, z_trim=args.z_trim)
    print(f"{args.project}: four parts on one plate; exact settings {report['settings_sha256']}")
    for row in report["parts"]:
        size = np.subtract(row["plate_bounds_mm"][1], row["plate_bounds_mm"][0])
        print(f"  plate {row['plate']} {row['name']}: Rx {row['rotation_x_degrees']:g}°, {size.round(2).tolist()} mm")
    if args.slice_output:
        args.slice_output.mkdir(parents=True, exist_ok=True)
        command = [str(args.slicer.resolve()), "--slice", "0", "--arrange", "0", "--orient", "0", "--outputdir",
                   str(args.slice_output.resolve()), str(args.project.resolve())]
        log = args.slice_output / "bambu-cli.log"
        with log.open("w") as stream:
            result = subprocess.run(command, cwd=args.slice_output, stdout=stream, stderr=subprocess.STDOUT)
        print(f"Offline slice exited {result.returncode}; {log}")
        if result.returncode:
            raise SystemExit(result.returncode)
        slice_review(args.project.resolve(), report, args.slice_output.resolve())


if __name__ == "__main__":
    main()
