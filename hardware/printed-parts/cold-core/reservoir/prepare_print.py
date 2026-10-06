"""Build the current body/cap pairs with the accepted September PETG settings.

Run with tools/cad-venv/bin/python. STEP geometry must match the float integration
record. Slicing belongs in an ignored review directory, not a second repo 3MF.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import uuid
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in HERE.parents if (path / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-current-print"
CORE = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
PROD = "http://schemas.microsoft.com/3dmanufacturing/production/2015/06"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
ET.register_namespace("", CORE)
ET.register_namespace("p", PROD)


def sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def canonical(settings: dict) -> bytes:
    return json.dumps(settings, sort_keys=True, separators=(",", ":")).encode()


def qn(name: str) -> str:
    return f"{{{CORE}}}{name}"


def uid(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, "homesodamachine/reservoir/" + name))


def metadata(parent, name, value):
    ET.SubElement(parent, "metadata", key=name, value=str(value))


def xml(element) -> bytes:
    return ET.tostring(element, encoding="UTF-8", xml_declaration=True)


def write_archive(path: Path, members: dict[str, bytes]):
    temporary = path.with_suffix(".3mf.tmp")
    with zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as archive:
        for name, data in sorted(members.items()):
            entry = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
            entry.compress_type = zipfile.ZIP_DEFLATED
            entry.external_attr = 0o644 << 16
            archive.writestr(entry, data, compresslevel=6)
    temporary.replace(path)


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    recipe = json.loads((HERE / "print-settings.json").read_text())
    settings = recipe["project_settings"]
    restored = settings.copy()
    for key, change in recipe["identity_changes"].items():
        if settings[key] != change["to"]:
            raise ValueError(f"Unexpected profile identity: {key}")
        restored[key] = change["from"]
    if sha(canonical(restored)) != recipe["historical_source"]["project_settings_sha256"]:
        raise ValueError("Settings differ from the accepted September recipe")
    integration = json.loads((HERE.parent / "magnetic-float/all-aero/integration-check.json").read_text())
    area = np.array([[float(v) for v in point.split("x")]
                     for point in settings["extruder_printable_area"][0].split(",")])
    usable_low, usable_high = area.min(axis=0), area.max(axis=0)
    model = ET.Element(qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    ET.SubElement(model, qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
    ET.SubElement(model, qn("metadata"), name="Title").text = "Flavor reservoirs - PETG 0.24 mm"
    resources = ET.SubElement(model, qn("resources"))
    build = ET.SubElement(model, qn("build"), **{f"{{{PROD}}}UUID": uid("build")})
    config = ET.Element("config")
    assembled = ET.Element("assemble")
    relationships = ET.Element(f"{{{REL}}}Relationships")
    members = {"Metadata/project_settings.config": (json.dumps(settings, indent=2) + "\n").encode()}
    report = {
        "project": "reservoir.3mf", "recipe": "print-settings.json",
        "accepted_result_id": recipe["accepted_result_id"],
        "settings_sha256": sha(canonical(settings)),
        "physical_settings_match_accepted_recipe": True,
        "identity_changes": recipe["identity_changes"],
        "plate_count": 2, "mesh_tolerance_mm": 0.025,
        "mesh_angular_tolerance_rad": 0.08, "parts": [],
        "scope": "Current CAD and saved settings; the physical water hold belongs to the September article.",
    }
    number = 0
    for plate_id, side in enumerate(("left", "right"), 1):
        plate = ET.SubElement(config, "plate")
        for key, value in {"plater_id": plate_id, "plater_name": f"{side.title()} body and cap",
                           "locked": "false", "bed_type": settings["curr_bed_type"],
                           "filament_map_mode": "Auto For Flush", "filament_maps": "1",
                           "filament_volume_maps": "0"}.items():
            metadata(plate, key, value)
        # Bambu Studio's horizontal plate spacing is 1.2 times the 330 mm bed.
        origin = np.array([(plate_id - 1) * 396.0, 0.0, 0.0])
        for cap in (False, True):
            number += 1
            name = f"reservoir-{'cap-' if cap else ''}{side}"
            source = HERE / f"{name}.step"
            source_hash = sha(source.read_bytes())
            if integration["files_sha256"].get(str(source.relative_to(ROOT))) != source_hash:
                raise ValueError(f"{source.name} differs from the float integration record")
            shape = cq.importers.importStep(str(source))
            stl = CACHE / f"{name}.stl"
            cq.exporters.export(shape, str(stl), tolerance=0.025, angularTolerance=0.08)
            mesh = trimesh.load(stl, force="mesh", process=True)
            if not mesh.is_watertight or not mesh.is_winding_consistent or mesh.volume <= 0 or mesh.body_count != 1:
                raise ValueError(f"{name} is not one closed, consistently oriented volume")
            center = mesh.bounds.mean(axis=0)
            local_vertices = mesh.vertices - center
            # Body mouth up. Cap exterior face down and gasket rim up.
            rotation = np.diag([1.0, -1.0, -1.0]) if cap else np.eye(3)
            rotated = local_vertices @ rotation.T
            low, high = rotated.min(axis=0), rotated.max(axis=0)
            translation = np.array([70.0 if cap else 175.0, 160.0, -low[2]])
            placed = rotated + translation
            if (np.any(placed[:, :2].min(axis=0) < usable_low + 15) or
                    np.any(placed[:, :2].max(axis=0) > usable_high - 15) or
                    placed[:, 2].max() > float(settings["printable_height"])):
                raise ValueError(f"{name} exceeds the left nozzle's usable bed/height")
            part_id, object_id = str(number * 2 - 1), str(number * 2)
            member = f"3D/Objects/object_{number}.model"
            child = ET.Element(qn("model"), unit="millimeter")
            child_resources = ET.SubElement(child, qn("resources"))
            child_object = ET.SubElement(child_resources, qn("object"), id=part_id, type="model")
            geometry = ET.SubElement(child_object, qn("mesh"))
            vertices = ET.SubElement(geometry, qn("vertices"))
            triangles = ET.SubElement(geometry, qn("triangles"))
            for vertex in local_vertices:
                ET.SubElement(vertices, qn("vertex"), **dict(zip(("x", "y", "z"), (f"{v:.9f}" for v in vertex))))
            for triangle in mesh.faces:
                ET.SubElement(triangles, qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))
            members[member] = xml(child)
            parent = ET.SubElement(resources, qn("object"), id=object_id, type="model",
                                   **{f"{{{PROD}}}UUID": uid(name)})
            components = ET.SubElement(parent, qn("components"))
            ET.SubElement(components, qn("component"), objectid=part_id,
                          transform="1 0 0 0 1 0 0 0 1 0 0 0",
                          **{f"{{{PROD}}}path": "/" + member, f"{{{PROD}}}UUID": uid(name + "/part")})
            transform = " ".join(f"{v:.9f}" for v in [*rotation.T.reshape(-1), *(translation + origin)])
            ET.SubElement(build, qn("item"), objectid=object_id, transform=transform, printable="1",
                          **{f"{{{PROD}}}UUID": uid(name + "/item")})
            obj_config = ET.SubElement(config, "object", id=object_id)
            metadata(obj_config, "name", name)
            metadata(obj_config, "extruder", 1)
            ET.SubElement(obj_config, "metadata", face_count=str(len(mesh.faces)))
            part_config = ET.SubElement(obj_config, "part", id=part_id, subtype="normal_part", uuid=uid(name + "/part"))
            for key, value in {"name": name, "source_file": source.name,
                               "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                               "source_object_id": 0, "source_volume_id": 0,
                               "source_offset_x": center[0], "source_offset_y": center[1],
                               "source_offset_z": center[2]}.items():
                metadata(part_config, key, value)
            ET.SubElement(part_config, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                          degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
            instance = ET.SubElement(plate, "model_instance")
            for key, value in {"object_id": object_id, "instance_id": 0, "identify_id": 2400 + number}.items():
                metadata(instance, key, value)
            ET.SubElement(assembled, "assemble_item", object_id=object_id, instance_id="0", transform=transform, offset="0 0 0")
            ET.SubElement(assembled, "assemble_item", object_id=object_id, volume_id="0", transform="1 0 0 0 1 0 0 0 1 0 0 0")
            ET.SubElement(relationships, f"{{{REL}}}Relationship", Target="/" + member, Id=f"rel-{number}",
                          Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
            report["parts"].append({"name": name, "plate": plate_id,
                "source": str(source.relative_to(ROOT)), "step_sha256": source_hash,
                "triangles": len(mesh.faces), "watertight": True, "body_count": 1,
                "print_orientation": "exterior face down" if cap else "mouth up",
                "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()]})
    config.append(assembled)
    package = ET.Element(f"{{{REL}}}Relationships")
    ET.SubElement(package, f"{{{REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    for name, element in (("3D/3dmodel.model", model), ("Metadata/model_settings.config", config),
                          ("3D/_rels/3dmodel.model.rels", relationships), ("_rels/.rels", package)):
        payload = xml(element)
        if name.endswith(".rels"):
            payload = payload.replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
        members[name] = payload
    members["[Content_Types].xml"] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="config" ContentType="application/octet-stream"/></Types>'''
    project = HERE / "reservoir.3mf"
    write_archive(project, members)
    with zipfile.ZipFile(project) as archive:
        if archive.testzip() is not None or json.loads(archive.read("Metadata/project_settings.config")) != settings:
            raise ValueError("Saved project did not preserve the recipe")
    report["project_sha256"] = sha(project.read_bytes())
    (HERE / "reservoir.print.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"project": str(project), "plates": 2, "parts": report["parts"]}, indent=2))


if __name__ == "__main__":
    main()
