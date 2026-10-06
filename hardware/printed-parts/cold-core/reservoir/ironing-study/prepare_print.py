"""Build a centered plate of flat PETG squares for ironing calibration."""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
RESERVOIR = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-ironing-squares"
spec = importlib.util.spec_from_file_location("reservoir_project_writer", RESERVOIR / "prepare_print.py")
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)

SPEEDS = (15, 30, 60)
FLOWS = (10, 20, 30)
SPACING = 0.15
SIDE = 35.0
HEIGHT = 1.50  # One 0.30 mm layer and five 0.24 mm layers.
TAB_HEIGHT = 0.78
LABEL_HEIGHT = 1.02
BED = np.array([[0.0, 0.0], [325.0, 320.0]])
MIN_MARGIN = 80.0
GAP = 5.0
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
MATRIX = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"


def mesh_for(label):
    square = cq.Workplane("XY").box(SIDE, SIDE, HEIGHT, centered=(True, True, False))
    # Labels lie on a lower tab, outside the uninterrupted square test face.
    tab = cq.Workplane("XY").box(33, 9, TAB_HEIGHT, centered=(True, True, False)).translate((0, -21, 0))
    text = cq.Workplane("XY").text(label, 4.5, LABEL_HEIGHT-TAB_HEIGHT,
                                   font="Arial", kind="bold", combine=False).translate((0, -21, TAB_HEIGHT))
    shape = square.union(tab).union(text).clean()
    if len(shape.solids().vals()) != 1:
        raise ValueError(f"{label}: disconnected label or tab")
    face_area = sum(face.Area() for face in shape.faces().vals()
                    if abs(face.BoundingBox().zmin-HEIGHT) < 1e-6
                    and abs(face.BoundingBox().zmax-HEIGHT) < 1e-6)
    if abs(face_area-SIDE**2) > 1e-6:
        raise ValueError(f"{label}: interrupted square top face")
    target = CACHE / (label.replace("/", "-")+".stl")
    cq.exporters.export(shape, str(target), tolerance=0.025, angularTolerance=0.08)
    mesh = trimesh.load(target, force="mesh", process=True)
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and mesh.body_count == 1):
        raise ValueError(f"{label}: expected one closed solid")
    if abs(mesh.volume-shape.val().Volume()) > max(0.5, shape.val().Volume()*0.003):
        raise ValueError(f"{label}: tessellation volume error")
    return mesh, shape.val().Volume(), writer.sha(target.read_bytes())


def add_mesh(resources, mesh, ident):
    obj = ET.SubElement(resources, writer.qn("object"), id=str(ident), type="model")
    geometry = ET.SubElement(obj, writer.qn("mesh"))
    vertices = ET.SubElement(geometry, writer.qn("vertices"))
    triangles = ET.SubElement(geometry, writer.qn("triangles"))
    for vertex in mesh.vertices:
        ET.SubElement(vertices, writer.qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
    for triangle in mesh.faces:
        ET.SubElement(triangles, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    baseline = json.loads((RESERVOIR / "print-settings.json").read_text())["project_settings"]
    settings = copy.deepcopy(baseline)
    settings.update(ironing_type="no ironing", enable_support="0",
                    print_settings_id="PETG flat-square ironing calibration - 0.24mm",
                    filament_map_mode="Manual", filament_map=["1"], filament_nozzle_map=["0"])
    changes = {k: {"from": baseline.get(k), "to": v} for k, v in settings.items() if baseline.get(k) != v}
    entries = []
    # Three speed rows, three flow columns; a single OFF reference in column 4.
    for row, speed in enumerate(SPEEDS):
        for column, flow in enumerate(FLOWS):
            entries.append(dict(label=f"{speed}/{flow}", ironed=True, speed_mm_s=speed,
                                flow_percent=flow, spacing_mm=SPACING, row=row, column=column))
    entries.append(dict(label="OFF", ironed=False, speed_mm_s=None, flow_percent=0,
                        spacing_mm=SPACING, row=1, column=3))
    width, depth = 4*SIDE+3*GAP, 3*43+2*GAP
    low_x, low_y = (BED[1]-np.array([width, depth]))/2
    for item in entries:
        item["center"] = [float(low_x+SIDE/2+item["column"]*(SIDE+GAP)),
                          float(low_y+25.5+item["row"]*(43+GAP)), 0]

    model = ET.Element(writer.qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    for name, value in (("Application", "BambuStudio-02.08.02.61"), ("BambuStudio:3mfVersion", "1"),
                        ("Title", "PETG flat-square ironing calibration")):
        ET.SubElement(model, writer.qn("metadata"), name=name).text = value
    resources = ET.SubElement(model, writer.qn("resources"))
    build = ET.SubElement(model, writer.qn("build"), **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-squares/build")})
    config = ET.Element("config")
    plate = ET.SubElement(config, "plate")
    for key, value in dict(plater_id=1, plater_name="PETG ironing squares", locked="false",
                           bed_type=settings["curr_bed_type"], filament_map_mode="Manual",
                           filament_maps="1", filament_volume_maps="0").items():
        writer.metadata(plate, key, value)
    assembled = ET.SubElement(config, "assemble")
    relations = ET.Element(f"{{{writer.REL}}}Relationships")
    members = {"Metadata/project_settings.config": (json.dumps(settings, indent=2)+"\n").encode()}
    report = dict(project="ironing-study.3mf", geometry="flat squares", recipe="../print-settings.json",
                  recipe_settings_sha256=writer.sha(writer.canonical(baseline)), project_overrides=changes,
                  plate_count=1, square_side_mm=SIDE, square_height_mm=HEIGHT,
                  unobstructed_top_face_area_mm2=SIDE**2, label_tab_top_mm=LABEL_HEIGHT,
                  first_layer_mm=0.30, layer_height_mm=0.24,
                  speeds_mm_s=SPEEDS, flows_percent=FLOWS, spacing_mm=SPACING,
                  un_ironed_reference_count=1, label_format="speed in mm/s / flow in percent; OFF = no ironing",
                  layout=dict(left_nozzle_usable_bed_bounds_mm=BED.tolist(),
                              minimum_emitted_bead_edge_margin_mm=MIN_MARGIN,
                              model_bounding_box_gap_mm=GAP, speed_rows_front_to_back=SPEEDS,
                              flow_columns_left_to_right=FLOWS, reference_row=1, reference_column=3),
                  scope="Flat top-surface ironing calibration. Physical finish selection is pending; sealing and sloped surfaces are outside this test.",
                  parts=[])
    for index, item in enumerate(entries, 1):
        label = item["label"]
        mesh, volume, mesh_sha = mesh_for(label)
        part_id, object_id = index*100+1, 10000+index
        member = f"3D/Objects/object_{index}.model"
        child = ET.Element(writer.qn("model"), unit="millimeter")
        child_resources = ET.SubElement(child, writer.qn("resources"))
        add_mesh(child_resources, mesh, part_id)
        members[member] = writer.xml(child)
        parent = ET.SubElement(resources, writer.qn("object"), id=str(object_id), type="model",
                               **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-squares/"+label)})
        components = ET.SubElement(parent, writer.qn("components"))
        ET.SubElement(components, writer.qn("component"), objectid=str(part_id), transform=IDENTITY,
                      **{f"{{{writer.PROD}}}path": "/"+member,
                         f"{{{writer.PROD}}}UUID": writer.uid(f"ironing-squares/{label}/{part_id}")})
        transform = " ".join(map(str, [1, 0, 0, 0, 1, 0, 0, 0, 1, *item["center"]]))
        ET.SubElement(build, writer.qn("item"), objectid=str(object_id), transform=transform, printable="1",
                      **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-squares/"+label+"/item")})
        obj = ET.SubElement(config, "object", id=str(object_id))
        for key, value in dict(name=label, extruder=1,
                               ironing_type="topmost" if item["ironed"] else "no ironing").items():
            writer.metadata(obj, key, value)
        if item["ironed"]:
            for key, value in dict(ironing_speed=item["speed_mm_s"],
                                   ironing_flow=f"{item['flow_percent']}%", ironing_spacing=SPACING).items():
                writer.metadata(obj, key, value)
        ET.SubElement(obj, "metadata", face_count=str(len(mesh.faces)))
        part = ET.SubElement(obj, "part", id=str(part_id), subtype="normal_part",
                             uuid=writer.uid(f"ironing-squares/{label}/{part_id}"))
        writer.metadata(part, "name", label)
        writer.metadata(part, "matrix", MATRIX)
        writer.metadata(part, "source_file", label.replace("/", "-")+".stl")
        ET.SubElement(part, "mesh_stat", face_count=str(len(mesh.faces)), edges_fixed="0",
                      degenerate_facets="0", facets_removed="0", facets_reversed="0", backwards_edges="0")
        instance = ET.SubElement(plate, "model_instance")
        for key, value in dict(object_id=object_id, instance_id=0, identify_id=6000+index).items():
            writer.metadata(instance, key, value)
        ET.SubElement(assembled, "assemble_item", object_id=str(object_id), instance_id="0", transform=transform, offset="0 0 0")
        ET.SubElement(relations, f"{{{writer.REL}}}Relationship", Target="/"+member, Id=f"rel-{index}",
                      Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        placed = mesh.bounds+np.array(item["center"])
        if np.any(placed[0, :2] < BED[0]+MIN_MARGIN) or np.any(placed[1, :2] > BED[1]-MIN_MARGIN):
            raise ValueError(f"{label}: plate clearance")
        item.update(object_id=object_id, identify_id=6000+index, bounds_mm=placed.tolist(),
                    cad_volume_mm3=volume, mesh_volume_mm3=float(mesh.volume), triangles=len(mesh.faces),
                    mesh_sha256=mesh_sha, closed_mesh=True, connected_solids=1)
        report["parts"].append(item)
        print(f"Prepared {label}", flush=True)
    package = ET.Element(f"{{{writer.REL}}}Relationships")
    ET.SubElement(package, f"{{{writer.REL}}}Relationship", Target="/3D/3dmodel.model", Id="rel-1",
                  Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
    for name, element in (("3D/3dmodel.model", model), ("Metadata/model_settings.config", config),
                          ("3D/_rels/3dmodel.model.rels", relations), ("_rels/.rels", package)):
        payload = writer.xml(element)
        if name.endswith(".rels"):
            payload = payload.replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
        members[name] = payload
    members["[Content_Types].xml"] = b'''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>
<Default Extension="config" ContentType="application/octet-stream"/></Types>'''
    project = HERE / "ironing-study.3mf"
    writer.write_archive(project, members)
    with zipfile.ZipFile(project) as archive:
        if archive.testzip() or json.loads(archive.read("Metadata/project_settings.config")) != settings:
            raise ValueError("Saved project differs from requested settings")
    report["project_sha256"] = writer.sha(project.read_bytes())
    bounds = np.array([p["bounds_mm"] for p in report["parts"]])
    envelope = np.array([bounds[:, 0, :2].min(axis=0), bounds[:, 1, :2].max(axis=0)])
    report["layout"]["model_xy_bounds_mm"] = envelope.tolist()
    report["layout"]["model_edge_margins_left_front_right_back_mm"] = np.concatenate(
        (envelope[0]-BED[0], BED[1]-envelope[1])).tolist()
    (HERE / "study.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(project=str(project), specimens=len(entries)), indent=2))


if __name__ == "__main__":
    main()
