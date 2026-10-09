"""Prepare three close ASA Aero floats and export a native slice; never Send."""

import argparse
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_printer.py").is_file())
FLOAT = HERE.parents[1]
PRIVATE = ROOT / ".cache/prints/2026-10-08-three-floats-close-mark2"
STUDIO = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")
STEM = "2026-10-08-three-floats-close-asa-aero-right04-engineering-mark2"
PROJECT = HERE / (STEM + ".3mf")
ARCHIVE_NAME = STEM + ".gcode.3mf"
SETTING = "Metadata/project_settings.config"
PITCH = 38.1
MESSAGE = (
    "Insert one RC62 ring into EACH of the three open float pockets. "
    "Seat all three rings fully on their pocket floors, below both rims. "
    "Keep the guide bores open and remove loose strings without moving the floats. "
    "Clear the toolhead and resume only after all three magnets are seated."
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def write_project(adapted, centers, snapshot, writer):
    """Package the unchanged one-solid STL, including its enclosed cavity shell."""
    import numpy as np
    import trimesh

    with zipfile.ZipFile(adapted) as archive:
        members = {name: archive.read(name) for name in archive.namelist()
                   if name == SETTING or name.startswith("Metadata/filament_settings_")}
    settings = json.loads(members[SETTING])
    source = snapshot / "float-aero.stl"
    mesh = trimesh.load(source, force="mesh", process=True)
    shells = mesh.split(only_watertight=False)
    assert mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0
    assert len(shells) == 2 and all(s.is_watertight and s.is_winding_consistent for s in shells)
    outer, = [s for s in shells if s.volume > 0]
    cavity, = [s for s in shells if s.volume < 0]
    radius = np.linalg.norm(cavity.vertices[:, :2], axis=1)
    assert radius.min() > 2.4 and radius.max() < 18
    assert 0 < cavity.bounds[0, 2] < cavity.bounds[1, 2] < 28
    source_center = mesh.bounds.mean(axis=0)
    local_vertices = mesh.vertices - source_center
    usable = np.array([[float(v) for v in point.split("x")]
                       for point in settings["extruder_printable_area"][1].split(",")])
    low, high = usable.min(axis=0), usable.max(axis=0)
    model = ET.Element(writer.qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    ET.SubElement(model, writer.qn("metadata"), name="Application").text = "BambuStudio-02.08.02.61"
    ET.SubElement(model, writer.qn("metadata"), name="BambuStudio:3mfVersion").text = "1"
    ET.SubElement(model, writer.qn("metadata"), name="Title").text = "Three close ASA Aero floats"
    resources = ET.SubElement(model, writer.qn("resources"))
    build = ET.SubElement(model, writer.qn("build"), **{f"{{{writer.PROD}}}UUID": writer.identifier("three-float-build")})
    config, assembled = ET.Element("config"), ET.Element("assemble")
    plate = ET.SubElement(config, "plate")
    for key, value in {"plater_id": 1, "plater_name": "Three close ASA Aero floats", "locked": "false",
                       "filament_map_mode": "Manual", "filament_maps": "2", "filament_volume_maps": "0",
                       "bed_type": settings["curr_bed_type"]}.items():
        writer.metadata(plate, key, value)
    relationships = ET.Element(f"{{{writer.REL}}}Relationships")
    report = {"project": str(PROJECT.relative_to(ROOT)), "parts": [],
              "shared_printable_area_mm": [low.tolist(), high.tolist()], "plate_border_mm": 80,
              "plate_count": 1, "printer": settings["printer_settings_id"],
              "process": settings["print_settings_id"], "filament": settings["filament_settings_id"],
              "layer_height_mm": float(settings["layer_height"]),
              "bed_type": settings["curr_bed_type"], "solid_count": 1,
              "surface_shells_per_float": [{"signed_volume_mm3": s.volume} for s in shells]}
    for index, center in enumerate(centers, 1):
        name, part_id, object_id = f"ASA Aero float {index}", str(2 * index - 1), str(2 * index)
        translation = [*center, source_center[2]]
        transform = [1, 0, 0, 0, 1, 0, 0, 0, 1, *translation]
        placed = local_vertices + translation
        assert np.all(placed[:, :2].min(axis=0) >= low + 80)
        assert np.all(placed[:, :2].max(axis=0) <= high - 80)
        member = f"3D/Objects/object_{index}.model"
        child = ET.Element(writer.qn("model"), unit="millimeter")
        child_resources = ET.SubElement(child, writer.qn("resources"))
        obj = ET.SubElement(child_resources, writer.qn("object"), id=part_id, type="model")
        geometry = ET.SubElement(obj, writer.qn("mesh"))
        vertices, triangles = ET.SubElement(geometry, writer.qn("vertices")), ET.SubElement(geometry, writer.qn("triangles"))
        for vertex in local_vertices:
            ET.SubElement(vertices, writer.qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
        for face in mesh.faces:
            ET.SubElement(triangles, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, face))))
        members[member] = writer.xml(child)
        top = ET.SubElement(resources, writer.qn("object"), id=object_id, type="model", **{f"{{{writer.PROD}}}UUID": writer.identifier(name)})
        components = ET.SubElement(top, writer.qn("components"))
        ET.SubElement(components, writer.qn("component"), objectid=part_id, transform="1 0 0 0 1 0 0 0 1 0 0 0",
                      **{f"{{{writer.PROD}}}path": "/" + member, f"{{{writer.PROD}}}UUID": writer.identifier(name + "/component")})
        transform_text = " ".join(f"{v:.9f}" for v in transform)
        ET.SubElement(build, writer.qn("item"), objectid=object_id, transform=transform_text, printable="1",
                      **{f"{{{writer.PROD}}}UUID": writer.identifier(name + "/item")})
        obj_config = ET.SubElement(config, "object", id=object_id)
        for key, value in {"name": name, "extruder": 1}.items(): writer.metadata(obj_config, key, value)
        ET.SubElement(obj_config, "metadata", face_count=str(len(mesh.faces)))
        part_config = ET.SubElement(obj_config, "part", id=part_id, subtype="normal_part", uuid=writer.identifier(name + "/part"))
        for key, value in {"name": name, "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1", "source_file": source.name,
                           "source_object_id": 0, "source_volume_id": 0,
                           **dict(zip(("source_offset_x", "source_offset_y", "source_offset_z"), source_center))}.items():
            writer.metadata(part_config, key, value)
        ET.SubElement(part_config, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0", degenerate_facets="0",
                      facets_removed="0", facets_reversed="0", backwards_edges="0")
        instance = ET.SubElement(plate, "model_instance")
        for key, value in {"object_id": object_id, "instance_id": 0, "identify_id": 1900 + index}.items(): writer.metadata(instance, key, value)
        ET.SubElement(assembled, "assemble_item", object_id=object_id, instance_id="0", transform=transform_text, offset="0 0 0")
        ET.SubElement(assembled, "assemble_item", object_id=object_id, volume_id="0", transform="1 0 0 0 1 0 0 0 1 0 0 0", offset="0 0 0")
        ET.SubElement(relationships, f"{{{writer.REL}}}Relationship", Target="/" + member, Id=f"rel-{index}",
                      Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        report["parts"].append({"name": name, "object_id": object_id, "part_id": part_id, "member": member,
                               "identify_id": 1900 + index, "source": str(source.relative_to(ROOT)),
                               "stl_sha256": sha(source), "triangles": len(mesh.faces), "source_center_mm": source_center.tolist(),
                               "build_transform": transform, "plate_bounds_mm": [placed.min(axis=0).tolist(), placed.max(axis=0).tolist()],
                               "watertight": True, "solid_count": 1, "surface_shell_count": 2})
    config.append(assembled)
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relationships).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    rels = ET.Element(f"{{{writer.REL}}}Relationships")
    ET.SubElement(rels, f"{{{writer.REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    members["_rels/.rels"] = writer.xml(rels).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    members["[Content_Types].xml"] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="config" ContentType="application/octet-stream"/>
</Types>'''
    writer.archive_write(PROJECT, members)
    return report


def paint_inward_seams(members, parts, centers, writer):
    """Paint a vertical seam strip toward the cluster center on each mesh."""
    records = []
    cluster = (177.5, 160.0)
    for part, center in zip(parts, centers):
        target = math.atan2(cluster[1] - center[1], cluster[0] - center[0])
        child = ET.fromstring(members[part["member"]])
        mesh = child.find(f"{writer.qn('resources')}/{writer.qn('object')}/{writer.qn('mesh')}")
        vertices = [tuple(float(v.get(axis)) for axis in "xyz") for v in mesh.find(writer.qn("vertices"))]
        enforced = blocked = 0
        for triangle in mesh.find(writer.qn("triangles")):
            points = [vertices[int(triangle.get(key))] for key in ("v1", "v2", "v3")]
            a, b, c = points
            u, v = [b[i] - a[i] for i in range(3)], [c[i] - a[i] for i in range(3)]
            normal = (u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0])
            length = math.sqrt(sum(n * n for n in normal))
            if not length or abs(normal[2]) / length > 0.1:
                continue
            x, y = (sum(p[i] for p in points) / 3 for i in (0, 1))
            delta = math.atan2(math.sin(math.atan2(y, x) - target), math.cos(math.atan2(y, x) - target))
            # Native unsplit-triangle serialization: ENFORCER=1 -> 4; BLOCKER=2 -> 8.
            inward = abs(delta) <= math.radians(4)
            triangle.set("paint_seam", "4" if inward else "8")
            enforced += inward
            blocked += not inward
        assert enforced > 0 and blocked > 0
        members[part["member"]] = writer.xml(child)
        records.append({"object_id": part["object_id"], "identify_id": part["identify_id"],
                        "target_degrees_from_positive_x": math.degrees(target) % 360,
                        "strip_half_angle_degrees": 4, "enforcer_triangles": enforced,
                        "blocker_triangles": blocked})
    root = ET.fromstring(members["3D/3dmodel.model"])
    ET.SubElement(root, writer.qn("metadata"), name="BambuStudio:SeamPaintingVersion").text = "0"
    members["3D/3dmodel.model"] = writer.xml(root)
    return records


def prepare():
    sys.path[:0] = [str(ROOT / "hardware/printed-parts/faucet"), str(ROOT / "hardware/scripts")]
    import refresh_print_project as writer

    snapshot = HERE / "source-snapshot"
    snapshot.mkdir(exist_ok=True)
    sources = {
        "float-aero.stl": FLOAT / "float-aero.stl",
        "float-aero.step": FLOAT / "float-aero.step",
        "all_aero_float.py": FLOAT / "all_aero_float.py",
        "design.json": FLOAT / "design.json",
        "_float_interface.py": FLOAT.parents[1] / "_float_interface.py",
    }
    manifest = []
    for name, source in sources.items():
        target = snapshot / name
        if target.exists():
            assert target.read_bytes() == source.read_bytes(), "Inspect changed frozen source before another preparation"
        else:
            shutil.copyfile(source, target)
        manifest.append({"source": str(source.relative_to(ROOT)), "snapshot": str(target.relative_to(ROOT)), "sha256": sha(target)})
    json_write(snapshot / "manifest.json", {"files": manifest, "scope": "Frozen geometry for this three-float plate; no production geometry is regenerated."})
    design = json.loads((snapshot / "design.json").read_text())
    assert design["dimensions_mm"]["pocket_depth"] == 3.6
    assert design["print_intent"]["pause_before_layer_z_mm"] == 16.2

    baseline = FLOAT / "all-aero-float.3mf"
    with zipfile.ZipFile(baseline) as archive:
        assert archive.testzip() is None
        members = {name: archive.read(name) for name in archive.namelist()}
    saved = json.loads(members[SETTING])
    settings = json.loads(json.dumps(saved))
    assert settings["wall_loops"] == "300"
    assert settings["filament_nozzle_map"] == ["1"]
    assert settings["curr_bed_type"] == "Engineering Plate"
    start = settings["machine_start_gcode"]
    assert start.count("X110 Y14 I181 J154") == 3
    settings.update(
        machine_start_gcode=start.replace("X110 Y14 I181 J154", "X110 Y14 I181 J196"),
        wrapping_detection_gcode="",
        filament_colour=["#FFFFFF"],
        filament_multi_colour=["#FFFFFF"],
        print_sequence="by layer",
        seam_position="aligned",
        seam_slope_type="none",
        filament_scarf_seam_type=["none"],
    )
    PRIVATE.mkdir(parents=True, exist_ok=True)
    members[SETTING] = (json.dumps(settings, indent=2) + "\n").encode()
    adapted = PRIVATE / "adapted-recipe.3mf"
    writer.archive_write(adapted, members)
    height = PITCH * math.sqrt(3) / 2
    centers = [(177.5 - PITCH / 2, 160 - height / 3),
               (177.5 + PITCH / 2, 160 - height / 3),
               (177.5, 160 + 2 * height / 3)]
    report = write_project(adapted, centers, snapshot, writer)
    with zipfile.ZipFile(PROJECT) as archive:
        output = {name: archive.read(name) for name in archive.namelist()}
    config = ET.fromstring(output["Metadata/model_settings.config"])
    for obj in config.findall("object"):
        writer.metadata(obj, "xy_contour_compensation", 0.05)
        writer.metadata(obj, "xy_hole_compensation", -0.05)
    plate = config.find("plate")
    for item in plate.findall("metadata"):
        if item.get("key") == "filament_map_mode": item.set("value", "Manual")
        if item.get("key") == "filament_maps": item.set("value", "2")
    output["Metadata/model_settings.config"] = writer.xml(config)
    pauses = ET.Element("custom_gcodes_per_layer")
    pause_plate = ET.SubElement(pauses, "plate")
    ET.SubElement(pause_plate, "plate_info", id="1")
    ET.SubElement(pause_plate, "layer", top_z="16.200000", type="1", extruder="1",
                  color="", extra=MESSAGE, gcode="M400 U1")
    ET.SubElement(pause_plate, "mode", value="SingleExtruder")
    output["Metadata/custom_gcode_per_layer.xml"] = writer.xml(pauses)
    seam_painting = paint_inward_seams(output, report["parts"], centers, writer)
    writer.archive_write(PROJECT, output)
    effective = json.loads(output[SETTING])
    report.update(
        project_sha256=sha(PROJECT), settings_sha256=hashlib.sha256(output[SETTING]).hexdigest(),
        recipe_source=str(baseline.relative_to(ROOT)), recipe_source_sha256=sha(baseline),
        recipe_changes={k: {"source": saved.get(k), "chosen": effective.get(k)}
                        for k in sorted(set(saved) | set(effective)) if saved.get(k) != effective.get(k)},
        preparation_only=True, launch_authorized=False, submitted=False, send_attempted=False,
        requested_quantity=3, arrangement="Equilateral triangle centered in the right usable bed area",
        centers_xy_mm=centers, center_pitch_mm=PITCH, nominal_cad_surface_gap_mm=PITCH - 36,
        compensated_nominal_surface_gap_mm=PITCH - 36 - 2 * 0.05,
        source_design_revision=design["cad_revision"], pocket_depth_mm=3.6,
        custom_pause={"count": 1, "before_layer": 81, "top_z_mm": 16.2, "message": MESSAGE},
        process_order="by layer", active_side="RIGHT", active_nozzle_mm=0.4,
        external_slot=255, physical_material="White Bambu ASA Aero GFB02", glue_user_report=True,
        requested_z_trim_mm=0.04, probing_clump_detection=False,
        seam_type="Regular seam", scarf_enabled=False, inward_seam_painting=seam_painting,
        seam_scope="Layer starts and stops target the central gap; verify the emitted paths after native slicing.",
        adaptive_leveling_bounds_mm={"x_min": 110, "x_max": 291, "y_min": 14, "y_max": 210},
        customer_outcome="Three floats with short inter-object transfers; evaluate whether resulting defects are small enough for local repair.",
        user_quotes=[
            "I'd like to print 3 floats at once.",
            "I've got mark2 loaded with ASA Aero in the right hotend 0.4 mm with engineering plate glued.",
            "I'd like the floats to be close together, so that the distance between objects is small. The defects we had results in catastrophe, and I'd like to see if we can get some tighter smaller controllable work-pastable defects with this approach.",
            "Do the slice and tell me the magnet pause time (how long after start), and we'll see what we have time for tonight.",
            "I'd like, if possible, that the scarf be \"in the middle\" for all 3, as in the start/stop for each layer on them should be closest to the other two floats - you follow me?",
            "I mean a regular seam - the distinction between scarf and seam is not clear to me.",
        ],
        physical_result_scope="The user reports catastrophic prior defects. This arrangement's defect size and repairability remain unobserved.",
        prepared_at_utc=datetime.now(timezone.utc).isoformat(),
    )
    json_write(HERE / "preparation.json", report)
    json_write(PROJECT.with_suffix(".print.json"), report)
    print(json.dumps({"prepared": str(PROJECT.relative_to(ROOT)), "centers": centers,
                      "nominal_compensated_gap_mm": 2.0, "pause_before_layer": 81,
                      "submitted": False}, indent=2), flush=True)


def native_slice():
    record = json.loads((HERE / "preparation.json").read_text())
    assert sha(PROJECT) == record["project_sha256"]
    native = PRIVATE / "native"
    native.mkdir(exist_ok=True)
    output = native / ARCHIVE_NAME
    assert not output.exists(), "Review the existing native export before rerunning the slice"
    command = [str(STUDIO), "--arrange", "0", "--orient", "0", "--slice", "0",
               "--export-3mf", ARCHIVE_NAME, "--outputdir", str(native), str(PROJECT)]
    json_write(PRIVATE / "slice-command.json", {"command": command, "scope": "Offline native slicing only; no sender or printer command."})
    with (PRIVATE / "slice.log").open("w") as log:
        subprocess.run(command, cwd=native, stdout=log, stderr=subprocess.STDOUT, check=True)
    summary = json.loads((native / "result.json").read_text())["sliced_plates"][0]
    print(json.dumps({"native_archive": str(output.relative_to(ROOT)),
                      "total_minutes": summary["total_predication"] / 60,
                      "object_count": len(summary["objects"]), "warnings": summary["warning_message"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "slice"))
    action = parser.parse_args().action
    prepare() if action == "prepare" else native_slice()
