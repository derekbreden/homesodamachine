"""Prepare actual accepted-faucet sections for a cooling and scarf comparison.

The faucet shipping meshes and recipe are inputs only. Three identical foot
sections retain the original tilt, underside and first shoulder. Three identical
straight-neck sections retain the actual tube passages and curved outer wall.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
import zipfile

import cadquery as cq
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").exists())
FAUCET = ROOT / "hardware/printed-parts/faucet"
sys.path[:0] = [str(FAUCET), str(ROOT / "hardware/scripts")]
import refresh_print_project as writer
from _cadq_export import export_assembly
from _materials import one_body, C_FAUCET_BLACK
import flute_payload

STEM = "2026-10-10-faucet-foot-cooling-neck-scarf-petgf-left04-z004-mark2"
WORK = ROOT / ".cache/printer-control/faucet-finish-coupons-20261010"
SELECTION = FAUCET / "industrial/selected-print.json"
VARIANTS = (
    ("A foot current cooling", "foot", 0.12, "reference", 0, (-68, -23)),
    ("B foot half cooling", "foot", 0.12, "half", 0, (0, -23)),
    ("C foot stronger cooling", "foot", 0.12, "stronger", 0, (68, -23)),
    ("D neck regular seam", "neck", 0.08, "native", 0, (-36, 49)),
    ("E neck scarf 10mm", "neck", 0.08, "native", 10, (0, 49)),
    ("F neck scarf 20mm", "neck", 0.08, "native", 20, (36, 49)),
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def export_piece(name, solid):
    assert solid.isValid() and len(solid.Solids()) == 1
    step = HERE / f"{name}.step"
    assembly = one_body(cq.Workplane(obj=solid), name, C_FAUCET_BLACK)
    export_assembly(assembly, str(step))
    cq.exporters.export(solid, str(step.with_suffix(".stl")), tolerance=0.012, angularTolerance=0.07)
    mesh = trimesh.load(step.with_suffix(".stl"), force="mesh", process=True)
    assert mesh.is_watertight and mesh.body_count == 1 and mesh.volume > 0
    flute_payload.cut(step, step.with_suffix(".stl"), preserve_print_triangles=True)
    return mesh


def main():
    WORK.mkdir(parents=True, exist_ok=True)
    for receipt in (HERE / "launch-plan.json", HERE / "launch.json"):
        if receipt.exists():
            state = json.loads(receipt.read_text())
            assert not any(state.get(k) for k in ("import_attempted", "send_attempted", "accepted"))
    selected = json.loads(SELECTION.read_text())
    source_project = ROOT / selected["prepared_project"]
    assert sha(source_project) == selected["prepared_project_sha256"]
    source_stl = ROOT / selected["parts"][0]["source"]
    assert sha(source_stl) == selected["parts"][0]["stl_sha256"]
    source_step = source_stl.with_suffix(".step")
    solid = cq.importers.importStep(str(source_step)).val()
    assert len(solid.Solids()) == 1
    angle = selected["parts"][0]["rotation_x_degrees"]
    theta = math.radians(angle)
    rotation = np.array([[1, 0, 0], [0, math.cos(theta), -math.sin(theta)],
                         [0, math.sin(theta), math.cos(theta)]])
    source_mesh = trimesh.load(source_stl, force="mesh", process=True)
    rotated = source_mesh.vertices @ rotation.T
    lift = -float(rotated[:, 2].min())
    posed = solid.rotate((0, 0, 0), (1, 0, 0), angle).translate((0, 0, lift))
    foot = posed.intersect(cq.Solid.makeBox(160, 180, 33.8, cq.Vector(-80, -80, -.001)), tol=1e-6)
    # A print-horizontal cut in the straight neck supplies a seated sample,
    # while preserving the real tilted exterior and each internal passage.
    neck_start, neck_end = 82.0, 120.0
    neck = posed.intersect(cq.Solid.makeBox(160, 180, neck_end-neck_start,
                                         cq.Vector(-80, -80, neck_start)), tol=1e-6)
    neck = neck.translate((0, 0, -neck_start))
    geometry = {"foot": export_piece("faucet-foot-section", foot),
                "neck": export_piece("faucet-neck-section", neck)}
    parts = tuple((name, HERE / f"faucet-{kind}-section.stl", 0.)
                  for name, kind, height, cooling, scarf, xy in VARIANTS)
    project = HERE / (STEM + ".3mf")
    report = writer.refresh(source_project, project, parts=parts,
                            offsets=tuple(v[-1] for v in VARIANTS),
                            title="Actual faucet foot cooling and curved neck scarf comparison",
                            plate_border=40.)
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    settings = json.loads(members[writer.SETTINGS_MEMBER])
    # Parent foot's reinforcement applies only inside that CAD foot. Transform
    # the same region to the section's baked print frame and keep it as a modifier.
    model = ET.fromstring(members["3D/3dmodel.model"])
    config = ET.fromstring(members["Metadata/model_settings.config"])
    relationships = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    layer_ranges = ET.Element("objects")
    foot_box = cq.Solid.makeBox(61., 61., 14.02, cq.Vector(-30.5, -30.5, -.01))
    foot_box = foot_box.rotate((0, 0, 0), (1, 0, 0), angle).translate((0, 0, lift))
    cq.exporters.export(foot_box, str(WORK / "foot-modifier.stl"))
    modifier_mesh = trimesh.load(WORK / "foot-modifier.stl", force="mesh", process=True)
    specimens = []
    for index, (row, variant) in enumerate(zip(report["parts"], VARIANTS)):
        name, kind, height, cooling, scarf, xy = variant
        obj = config.find(f"object[@id='{row['object_id']}']")
        overrides = {"wall_generator": "arachne" if kind == "foot" else "classic"}
        if kind == "neck":
            overrides["seam_position"] = "back"
        if scarf:
            overrides.update(override_filament_scarf_seam_setting="1", seam_slope_type="external",
                             seam_slope_min_length=str(scarf))
        for key, value in overrides.items():
            writer.metadata(obj, key, value)
        band = (13.4, 29.0) if kind == "foot" else (16.04, 35.24)
        # Bambu imports this file by 1-based build-object order. Part IDs are
        # unrelated to that order once multiple components are present.
        group = ET.SubElement(layer_ranges, "object", id=str(index + 1))
        entry = ET.SubElement(group, "range", min_z=f"{band[0]:.4f}", max_z=f"{band[1]:.4f}")
        ET.SubElement(entry, "option", opt_key="layer_height").text = str(height)
        if kind == "foot":
            pid = str(100 + index)
            member = f"3D/Objects/foot-region-{pid}.model"
            sub = ET.Element(writer.qn("model"), unit="millimeter")
            resources = ET.SubElement(sub, writer.qn("resources"))
            mod = ET.SubElement(resources, writer.qn("object"), id=pid, type="model")
            geo = ET.SubElement(mod, writer.qn("mesh"))
            verts = ET.SubElement(geo, writer.qn("vertices"))
            faces = ET.SubElement(geo, writer.qn("triangles"))
            for v in modifier_mesh.vertices - row["source_center_mm"]:
                ET.SubElement(verts, writer.qn("vertex"), **dict(zip("xyz", (f"{x:.9f}" for x in v))))
            for tri in modifier_mesh.faces:
                ET.SubElement(faces, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, tri))))
            members[member] = writer.xml(sub)
            owner = model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{row['object_id']}']")
            ET.SubElement(owner.find(writer.qn("components")), writer.qn("component"), objectid=pid,
                          transform="1 0 0 0 1 0 0 0 1 0 0 0", **{f"{{{writer.PROD}}}path": "/"+member,
                          f"{{{writer.PROD}}}UUID": writer.identifier(name+"/foot")})
            part = ET.SubElement(obj, "part", id=pid, subtype="modifier_part", uuid=writer.identifier(name+"/modifier"))
            for key, value in {"name": "Parent continuous six-wall solid foot",
                               "matrix": "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                               "wall_loops": 6, "sparse_infill_density": "100%",
                               "sparse_infill_pattern": "zig-zag"}.items():
                writer.metadata(part, key, value)
            ET.SubElement(relationships, f"{{{writer.REL}}}Relationship", Target="/"+member, Id="foot-"+pid,
                          Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")
        specimens.append({"id": name[0], "name": name, "kind": kind,
                          "identify_id": row["identify_id"], "object_id": row["object_id"],
                          "layer_band_print_z_mm": band, "fine_layer_height_mm": height,
                          "cooling": cooling, "scarf_length_mm": scarf,
                          "plate_bounds_mm": row["plate_bounds_mm"], "object_overrides": overrides})
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relationships).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    members["Metadata/layer_config_ranges.xml"] = writer.xml(layer_ranges)
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  source_step=str(source_step.relative_to(ROOT)), source_step_sha256=sha(source_step),
                  source_stl=str(source_stl.relative_to(ROOT)), source_stl_sha256=sha(source_stl),
                  shipping_reference=selected["native_archive"], shipping_reference_sha256=selected["native_archive_sha256"],
                  shipping_reference_task=selected["printer_task_id"], specimens=specimens,
                  parent_pose={"rotation_x_degrees":angle,"lift_mm":lift},
                  section_cuts={"foot_max_print_z_mm":33.799,"neck_parent_print_z_mm":[neck_start,neck_end]},
                  supports="Tree(auto), Default; parent gaps, interfaces and speeds",
                  native_settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
                  submitted=False, import_attempted=False, send_attempted=False, accepted=False)
    save(HERE / "preparation.json", report)
    save(project.with_suffix(".print.json"), report)
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(WORK), "--export-3mf", STEM+".gcode.3mf", str(project)]
    save(WORK / "slice-command.json", {"argv": command, "printer_connection": False})
    print(json.dumps({"project": str(project.relative_to(ROOT)),
                      "parts": [{"id": r["id"], "bounds":r["plate_bounds_mm"]} for r in specimens]}, indent=2))


if __name__ == "__main__":
    main()
