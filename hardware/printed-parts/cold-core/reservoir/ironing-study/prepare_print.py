"""Build one labelled ironing comparison plate from the current reservoir STEP.

Run with tools/cad-venv/bin/python. The appliance geometry and official reservoir
recipe remain inputs. This produces finish coupons, not water-hold articles.
"""

from __future__ import annotations

import copy
import importlib.util
import json
import math
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
RESERVOIR = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
CACHE = ROOT / ".cache/reservoir-ironing-study"
spec = importlib.util.spec_from_file_location("reservoir_project_writer", RESERVOIR / "prepare_print.py")
writer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(writer)

VARIANTS = (
    ("1", "September", 10, 30, 0.15),
    ("2", "Half flow", 5, 30, 0.15),
    ("3", "Twice speed", 10, 60, 0.15),
    ("4", "Twice spacing", 10, 30, 0.30),
)
IDENTITY = "1 0 0 0 1 0 0 0 1 0 0 0"
MATRIX = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"


def box(low, high):
    low, high = np.array(low), np.array(high)
    return cq.Workplane("XY").box(*(high-low)).translate(tuple((high+low)/2))


def solid_mesh(shape, name):
    target = CACHE / (name + ".stl")
    cq.exporters.export(shape, str(target), tolerance=0.025, angularTolerance=0.08)
    mesh = trimesh.load(target, force="mesh", process=True)
    if not (mesh.is_watertight and mesh.is_winding_consistent and mesh.volume > 0 and mesh.body_count == 1):
        raise ValueError(f"{name}: expected one closed, consistently oriented solid")
    if abs(mesh.volume-shape.val().Volume()) > max(0.5, shape.val().Volume()*0.003):
        raise ValueError(f"{name}: excessive tessellation volume error")
    return mesh


def horizontal_area(shape, z):
    return sum(face.Area() for face in shape.faces().vals()
               if face.geomType() == "PLANE" and abs(face.BoundingBox().zmin-z) < 1e-5
               and abs(face.BoundingBox().zmax-z) < 1e-5)


def add_mesh(resources, mesh, ident):
    obj = ET.SubElement(resources, writer.qn("object"), id=str(ident), type="model")
    geometry = ET.SubElement(obj, writer.qn("mesh"))
    vertices = ET.SubElement(geometry, writer.qn("vertices"))
    triangles = ET.SubElement(geometry, writer.qn("triangles"))
    for vertex in mesh.vertices:
        ET.SubElement(vertices, writer.qn("vertex"), **dict(zip("xyz", (f"{v:.9f}" for v in vertex))))
    for triangle in mesh.faces:
        ET.SubElement(triangles, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, triangle))))


def labelled(shape, feature, label):
    # These low tabs never overlap a sealing face or the ironing height masks.
    y = -20.5 if feature == "G" else -23.5
    tab = cq.Workplane("XY").box(24, 10, 1.26, centered=(True, True, False)).translate((0, y, 0))
    text = cq.Workplane("XY").text(label, 6.5, 0.48, font="Arial", kind="bold", combine=False)
    text = text.translate((0, y, 1.26))
    return shape.union(tab).union(text).clean()


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    source = RESERVOIR / "reservoir-left.step"
    source_hash = writer.sha(source.read_bytes())
    integration = json.loads((RESERVOIR.parent / "magnetic-float/all-aero/integration-check.json").read_text())
    if integration["files_sha256"][str(source.relative_to(ROOT))] != source_hash:
        raise ValueError("Current reservoir STEP differs from the integration record")
    recipe = json.loads((RESERVOIR / "print-settings.json").read_text())
    baseline = recipe["project_settings"]
    settings = copy.deepcopy(baseline)
    settings.update(ironing_type="no ironing", print_settings_id="Reservoir ironing comparison - 0.24mm")
    overrides = {k: {"from": baseline[k], "to": v} for k, v in settings.items() if baseline[k] != v}
    body = cq.importers.importStep(str(source))
    top = body.val().BoundingBox().zmax
    bottom = body.val().BoundingBox().zmin
    # Removing 698 complete 0.24 mm layers retains the production layer phase.
    gasket_bottom = bottom + 698*0.24
    gasket_crop = [[-131, -16, gasket_bottom], [-116, 16, top+1]]
    bulkhead_crop = [[-120, -19, bottom], [-90, 19, bottom+12]]
    gasket_origin = [-123.75, 0, gasket_bottom]
    bulkhead_origin = [-105, 0, bottom]
    gasket = body.intersect(box(*gasket_crop)).translate(tuple(-np.array(gasket_origin)))
    bulkhead = body.intersect(box(*bulkhead_crop)).translate(tuple(-np.array(bulkhead_origin)))
    if len(gasket.solids().vals()) != 1 or len(bulkhead.solids().vals()) != 1:
        raise ValueError("Each cropped sealing feature must be connected")
    seat_area = horizontal_area(bulkhead, 4.65)
    if not math.isclose(seat_area, math.pi*(12.15**2-7.9**2), abs_tol=1e-4):
        raise ValueError("The crop does not retain the complete wet washer annulus")
    gasket_area = horizontal_area(gasket, top-gasket_bottom)
    if not math.isclose(gasket_area, 150.79106527534532, abs_tol=1e-4):
        raise ValueError("The gasket rim or blind-pocket opening differs from the reviewed feature")
    gasket_mask = box([-5.6, -16.1, top-gasket_bottom-0.6], [5.6, 16.1, top-gasket_bottom+1])
    seat_mask = cq.Workplane("XY").circle(12.15).extrude(0.9).translate((0, 0, 4.15))
    slope_mask = box([-15.1, -19.1, 2.0], [15.1, 19.1, 8.0])
    masks = {"G": solid_mesh(gasket_mask, "gasket-mask"),
             "B": solid_mesh(seat_mask, "seat-mask"),
             "S": solid_mesh(slope_mask, "slope-mask")}
    entries = []
    for row, (number, title, flow, speed, spacing) in enumerate(VARIANTS):
        for feature, centers in (("G", (35, 76)), ("B", (180, 225))):
            for test, x in enumerate(centers):
                entries.append(dict(label=f"{feature}{number}{'I' if test else 'C'}", feature=feature,
                                    condition=number, condition_title=title, ironed=bool(test),
                                    flow_percent=flow, speed_mm_s=speed, spacing_mm=spacing,
                                    center=[x, 46+row*58, 0]))
    for test, x in enumerate((150, 195)):
        entries.append(dict(label=f"S1{'I' if test else 'C'}", feature="S", condition="1",
                            condition_title="September; includes sloped floor", ironed=bool(test),
                            flow_percent=10, speed_mm_s=30, spacing_mm=0.15, center=[x, 282, 0]))

    model = ET.Element(writer.qn("model"), unit="millimeter", requiredextensions="p",
                       **{"xmlns:BambuStudio": "http://schemas.bambulab.com/package/2021"})
    for name, value in (("Application", "BambuStudio-02.08.02.61"), ("BambuStudio:3mfVersion", "1"),
                        ("Title", "Reservoir sealing faces and sloped floor - ironing comparison")):
        ET.SubElement(model, writer.qn("metadata"), name=name).text = value
    resources = ET.SubElement(model, writer.qn("resources"))
    build = ET.SubElement(model, writer.qn("build"), **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-study/build")})
    config = ET.Element("config")
    plate = ET.SubElement(config, "plate")
    for key, value in dict(plater_id=1, plater_name="Sealing faces and slope comparison", locked="false",
                           bed_type=settings["curr_bed_type"], filament_map_mode="Auto For Flush",
                           filament_maps="1", filament_volume_maps="0").items():
        writer.metadata(plate, key, value)
    assembled = ET.Element("assemble")
    relations = ET.Element(f"{{{writer.REL}}}Relationships")
    members = {"Metadata/project_settings.config": (json.dumps(settings, indent=2)+"\n").encode()}
    report = dict(project="ironing-study.3mf", source=str(source.relative_to(ROOT)), source_sha256=source_hash,
                  recipe="../print-settings.json", recipe_settings_sha256=writer.sha(writer.canonical(baseline)),
                  project_overrides=overrides, plate_count=1, layer_height_mm=0.24, first_layer_mm=0.30,
                  layer_phase_removed_from_gasket_mm=698*0.24,
                  crops_in_source_frame_mm={"G": gasket_crop, "B": bulkhead_crop},
                  source_origins_mm={"G": gasket_origin, "B": bulkhead_origin},
                  retained_sealing_face_area_mm2={"G": gasket_area, "B": seat_area},
                  bulkhead_seat=dict(outer_diameter_mm=24.3, inner_diameter_mm=15.8, print_z_mm=4.65),
                  floor_slope_degrees=math.degrees(math.atan(6/(67.25-14))),
                  scope="Cropped surface-finish comparison; physical results pending. Cropping changes layer time and thermal history.",
                  parts=[])
    for index, item in enumerate(entries, 1):
        label, feature = item["label"], item["feature"]
        shape = labelled(gasket if feature == "G" else bulkhead, feature, label)
        mesh = solid_mesh(shape, label)
        part_id, mask_id, object_id = index*100+1, index*100+2, 10000+index
        member = f"3D/Objects/object_{index}.model"
        child = ET.Element(writer.qn("model"), unit="millimeter")
        child_resources = ET.SubElement(child, writer.qn("resources"))
        add_mesh(child_resources, mesh, part_id)
        if item["ironed"]:
            add_mesh(child_resources, masks[feature], mask_id)
        members[member] = writer.xml(child)
        parent = ET.SubElement(resources, writer.qn("object"), id=str(object_id), type="model",
                               **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-study/"+label)})
        components = ET.SubElement(parent, writer.qn("components"))
        for ident in ([part_id, mask_id] if item["ironed"] else [part_id]):
            ET.SubElement(components, writer.qn("component"), objectid=str(ident), transform=IDENTITY,
                          **{f"{{{writer.PROD}}}path": "/"+member,
                             f"{{{writer.PROD}}}UUID": writer.uid(f"ironing-study/{label}/{ident}")})
        transform = " ".join(map(str, [1, 0, 0, 0, 1, 0, 0, 0, 1, *item["center"]]))
        ET.SubElement(build, writer.qn("item"), objectid=str(object_id), transform=transform, printable="1",
                      **{f"{{{writer.PROD}}}UUID": writer.uid("ironing-study/"+label+"/item")})
        obj = ET.SubElement(config, "object", id=str(object_id))
        for key, value in dict(name=label, extruder=1, ironing_speed=item["speed_mm_s"]).items():
            writer.metadata(obj, key, value)
        ET.SubElement(obj, "metadata", face_count=str(len(mesh.faces)))
        for ident, kind in [(part_id, "normal_part")] + ([(mask_id, "modifier_part")] if item["ironed"] else []):
            part = ET.SubElement(obj, "part", id=str(ident), subtype=kind,
                                 uuid=writer.uid(f"ironing-study/{label}/{ident}"))
            writer.metadata(part, "name", label if kind == "normal_part" else label+" ironing region")
            writer.metadata(part, "matrix", MATRIX)
            if kind == "normal_part":
                writer.metadata(part, "source_file", label+".stl")
            else:
                for key, value in dict(ironing_type="top", ironing_flow=f"{item['flow_percent']}%",
                                       ironing_speed=item["speed_mm_s"], ironing_spacing=item["spacing_mm"]).items():
                    writer.metadata(part, key, value)
            count = len(mesh.faces) if kind == "normal_part" else len(masks[feature].faces)
            ET.SubElement(part, "mesh_stat", face_count=str(count), edges_fixed="0", degenerate_facets="0",
                          facets_removed="0", facets_reversed="0", backwards_edges="0")
        instance = ET.SubElement(plate, "model_instance")
        for key, value in dict(object_id=object_id, instance_id=0, identify_id=5000+index).items():
            writer.metadata(instance, key, value)
        ET.SubElement(assembled, "assemble_item", object_id=str(object_id), instance_id="0", transform=transform, offset="0 0 0")
        ET.SubElement(relations, f"{{{writer.REL}}}Relationship", Target="/"+member, Id=f"rel-{index}",
                      Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        placed = mesh.bounds + np.array(item["center"])
        if np.any(placed[0, :2] < [15, 15]) or np.any(placed[1, :2] > [310, 305]):
            raise ValueError(f"{label}: plate clearance")
        item.update(object_id=object_id, identify_id=5000+index, bounds_mm=placed.tolist(),
                    cad_volume_mm3=shape.val().Volume(), mesh_volume_mm3=float(mesh.volume),
                    triangles=len(mesh.faces), mesh_sha256=writer.sha((CACHE / (label+".stl")).read_bytes()),
                    closed_mesh=True, connected_solids=1)
        report["parts"].append(item)
        print(f"Prepared {label}", flush=True)
    config.append(assembled)
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
    (HERE / "study.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(dict(project=str(project), specimens=len(entries)), indent=2))


if __name__ == "__main__":
    main()
