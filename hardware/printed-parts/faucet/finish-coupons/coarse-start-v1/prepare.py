"""Prepare full-scale faucet-lip coarse-start comparisons; no printer connection."""
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
WORK = ROOT / ".cache/printer-control/faucet-coarse-start-v1"
sys.path[:0] = [str(FAUCET), str(ROOT / "hardware/scripts")]
import refresh_print_project as writer
from _cadq_export import export_assembly
from _materials import one_body, C_FAUCET_BLACK
import flute_payload

PARENT = FAUCET / "industrial/physical-acceptance.json"
PARENT_PROJECT_SHA = "2561bcdaa520e94f4b0a5989fcbb9e941f707b50c46af97655ceacf312748302"
SOURCE_STUDY = HERE.parent / "2026-10-10"
PARENT_STL_SHA = "534a765c7573a99a2bcb4e81d31057f218026e613adb31c86c7bb68238595374"
PARENT_STEP_SHA = "7a2283681513fcb62692e71efff37b45c788a6ae35e3d1e3c3cd465ea0f9ad56"
STEM = "2026-10-11-faucet-lip-coarse-start-v1-petgf-left04-z004-mark2"
COMBINED_STEM = "2026-10-11-faucet-lip-and-scarf-v1-petgf-left04-z004-mark2"
SCARF_HERE = HERE.parent / "seam-gap-swatches-v1"
LIP_VARIANTS = (
    ("A", "current 0.12 band", None, 13.40, (0, -39)),
    ("B", "1 coarse layer", 1, 15.32, (-42, -39)),
    ("C", "2 coarse layers", 2, 15.56, (42, -39)),
    ("D", "4 coarse layers", 4, 16.04, (-21, 39)),
    ("E", "8 coarse layers", 8, 17.00, (21, 39)),
)
QUOTE = ('0.24 separates every time I think, it just recovers better as more heavy layers are added. '
         'Which is precisely why I expect our "1 layer" variable choice to fail. '
         'That is my hypothesis at least, which we shall test.')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def guard(folder):
    for filename in ("study-plan.json", "launch-plan.json", "launch.json"):
        path = folder / filename
        if path.exists():
            receipt = json.loads(path.read_text())
            assert not any(receipt.get(k) for k in ("import_attempted", "send_attempted", "accepted"))


def add_foot_modifier(members, model, config, relationships, part, mesh, index):
    pid = str(1000 + index)
    member = f"3D/Objects/foot-region-{pid}.model"
    sub = ET.Element(writer.qn("model"), unit="millimeter")
    resources = ET.SubElement(sub, writer.qn("resources"))
    mod = ET.SubElement(resources, writer.qn("object"), id=pid, type="model")
    geo = ET.SubElement(mod, writer.qn("mesh"))
    vertices = ET.SubElement(geo, writer.qn("vertices"))
    triangles = ET.SubElement(geo, writer.qn("triangles"))
    for v in mesh.vertices - part["source_center_mm"]:
        ET.SubElement(vertices, writer.qn("vertex"), **dict(zip("xyz", (f"{x:.9f}" for x in v))))
    for tri in mesh.faces:
        ET.SubElement(triangles, writer.qn("triangle"), **dict(zip(("v1", "v2", "v3"), map(str, tri))))
    members[member] = writer.xml(sub)
    owner = model.find(f"{writer.qn('resources')}/{writer.qn('object')}[@id='{part['object_id']}']")
    ET.SubElement(owner.find(writer.qn("components")), writer.qn("component"), objectid=pid,
                  transform="1 0 0 0 1 0 0 0 1 0 0 0",
                  **{f"{{{writer.PROD}}}path": "/" + member,
                     f"{{{writer.PROD}}}UUID": writer.identifier(part["name"] + "/foot")})
    cfg = config.find(f"object[@id='{part['object_id']}']")
    mod_config = ET.SubElement(cfg, "part", id=pid, subtype="modifier_part",
                               uuid=writer.identifier(part["name"] + "/modifier"))
    for key, value in dict(name="Parent solid-infill foot",
                           matrix="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1",
                           sparse_infill_density="100%",
                           sparse_infill_pattern="zig-zag").items():
        writer.metadata(mod_config, key, value)
    ET.SubElement(relationships, f"{{{writer.REL}}}Relationship", Target="/" + member,
                  Id="foot-" + pid, Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel")


def make_project(folder, stem, source_project, definitions, modifier_mesh, source_info, work_folder=None):
    folder.mkdir(parents=True, exist_ok=True)
    guard(folder)
    project = folder / (stem + ".3mf")
    report = writer.refresh(source_project, project,
                            parts=tuple((d["name"], d["source"], 0.) for d in definitions),
                            offsets=tuple(d["offset"] for d in definitions), plate_border=40.,
                            title="Full-scale faucet underside recovery and finish coupons")
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    model = ET.fromstring(members["3D/3dmodel.model"])
    config = ET.fromstring(members["Metadata/model_settings.config"])
    relationships = ET.fromstring(members["3D/_rels/3dmodel.model.rels"])
    ranges = ET.Element("objects")
    specimens = []
    for index, (part, definition) in enumerate(zip(report["parts"], definitions, strict=True)):
        cfg = config.find(f"object[@id='{part['object_id']}']")
        for key, value in definition["overrides"].items():
            writer.metadata(cfg, key, value)
        band = definition["fine_band"]
        group = ET.SubElement(ranges, "object", id=str(index + 1))
        entry = ET.SubElement(group, "range", min_z=f"{band[0]:.4f}", max_z=f"{band[1]:.4f}")
        ET.SubElement(entry, "option", opt_key="layer_height").text = str(definition["fine_height"])
        if definition["kind"] == "lip":
            add_foot_modifier(members, model, config, relationships, part, modifier_mesh, index)
        specimens.append({k: v for k, v in definition.items() if k not in ("source", "offset")}
                         | dict(identify_id=part["identify_id"], object_id=part["object_id"],
                                plate_bounds_mm=part["plate_bounds_mm"],
                                layer_band_print_z_mm=list(band), fine_layer_height_mm=definition["fine_height"],
                                object_overrides=definition["overrides"]))
    members["3D/3dmodel.model"] = writer.xml(model)
    members["Metadata/model_settings.config"] = writer.xml(config)
    members["3D/_rels/3dmodel.model.rels"] = writer.xml(relationships).replace(b"ns0:", b"").replace(b"xmlns:ns0=", b"xmlns=")
    members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges)
    writer.archive_write(project, members)
    report.update(source_info, project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  reinforcement_wall_loops=None,
                  specimens=specimens, native_settings_sha256=writer.digest(members[writer.SETTINGS_MEMBER]),
                  preparation_only=True, launch_authorized=False, start_now=False,
                  submitted=False, import_attempted=False, send_attempted=False, accepted=False)
    save(folder / "preparation.json", report)
    save(project.with_suffix(".print.json"), report)
    work = work_folder or WORK / ("combined" if folder != HERE else "lift")
    work.mkdir(parents=True, exist_ok=True)
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(work), "--export-3mf", stem + ".gcode.3mf", str(project)]
    save(work / "slice-command.json", dict(argv=command, printer_connection=False))
    return report


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    guard(HERE)
    parent = json.loads(PARENT.read_text())
    source_project = ROOT / parent["prepared_project"]
    study = json.loads((SOURCE_STUDY / "preparation.json").read_text())
    source_stl = SOURCE_STUDY / "faucet-foot-section.stl"
    source_step = source_stl.with_suffix(".step")
    assert sha(source_project) == PARENT_PROJECT_SHA
    assert sha(source_stl) == PARENT_STL_SHA == study["parts"][0]["stl_sha256"]
    assert sha(source_step) == PARENT_STEP_SHA
    assert study["source_stl_sha256"] == parent["parts"][0]["stl_sha256"]
    angle, lift = study["parent_pose"]["rotation_x_degrees"], study["parent_pose"]["lift_mm"]
    assert abs(angle + 15.) < 1e-10
    # The exact A/B/C foot is already frozen in the accepted print frame.
    # Read that section rather than mutable regenerated full-faucet outputs.
    posed = cq.importers.importStep(str(source_step)).val()
    # A narrow full-depth strip retains the original bed contact and front lip.
    # No support pedestal, rescaling or underside reshaping is introduced.
    crop = posed.intersect(cq.Solid.makeBox(18., 100., 25.001, cq.Vector(0, -40, -.001)), tol=1e-6)
    assert crop.isValid() and len(crop.Solids()) == 1
    step = HERE / "faucet-lip-section.step"
    export_assembly(one_body(cq.Workplane(obj=crop), "faucet-lip-section", C_FAUCET_BLACK), str(step))
    cq.exporters.export(crop, str(step.with_suffix(".stl")), tolerance=.012, angularTolerance=.07)
    mesh = trimesh.load(step.with_suffix(".stl"), force="mesh", process=True)
    assert mesh.is_watertight and mesh.body_count == 1 and mesh.volume > 0
    assert abs(mesh.bounds[0, 2]) < 1e-6
    flute_payload.cut(step, step.with_suffix(".stl"), preserve_print_triangles=True)
    full_foot = posed
    foot_box = cq.Solid.makeBox(61., 61., 14.02, cq.Vector(-30.5, -30.5, -.01))
    foot_box = foot_box.rotate((0, 0, 0), (1, 0, 0), angle).translate((0, 0, lift))
    cq.exporters.export(foot_box, str(WORK / "foot-modifier.stl"))
    modifier_mesh = trimesh.load(WORK / "foot-modifier.stl", force="mesh", process=True)
    source_info = dict(source_step=str(source_step.relative_to(ROOT)), source_step_sha256=PARENT_STEP_SHA,
                       source_stl=str(source_stl.relative_to(ROOT)), source_stl_sha256=PARENT_STL_SHA,
                       source_study=str((SOURCE_STUDY / "preparation.json").relative_to(ROOT)),
                       source_geometry_pointer_commit="5a9863696",
                       full_faucet_geometry_tag="faucet-industrial-shipping-2026-10-10",
                       full_faucet_stl_sha256=study["source_stl_sha256"],
                       full_faucet_step_sha256=study["source_step_sha256"],
                       source_acceptance=str(PARENT.relative_to(ROOT)), shipping_reference=parent["native_archive"],
                       shipping_reference_sha256=parent["native_archive_sha256"],
                       parent_pose=dict(rotation_x_degrees=angle, lift_mm=lift),
                       section_cuts=dict(parent_print_frame_box_mm=[[0, -40, -.001], [18, 60, 25]],
                                         original_front_ABC_volume_fraction=crop.Volume() / full_foot.Volume(),
                                         unchanged_bed_contact=True, scaled=False, added_stock=False),
                       supports="Tree(auto), Default; inherited automatic support decisions, gaps, interfaces and speeds")
    definitions = [dict(id=letter, name=f"{letter} lip {label}", kind="lip", source=step.with_suffix(".stl"),
                        offset=offset, requested_coarse_layers=count, fine_band=(fine_start, 25.),
                        fine_height=.12, overrides=dict(wall_generator="arachne"))
                   for letter, label, count, fine_start, offset in LIP_VARIANTS]
    prep = make_project(HERE, STEM, source_project, definitions, modifier_mesh, source_info)
    plan = dict(schema=1, status="Prepared coarse-start hypothesis comparison; unprinted",
                preparation_only=True, launch_authorized=False, start_now=False,
                import_attempted=False, send_attempted=False, accepted=False,
                authorization_quote="Please prepare a plate for this, thanks.", hypothesis_quote=QUOTE,
                customer_outcome="A stable faucet underside and clean fine-layer face above removable supports",
                hypothesis="The first supported model layer separates even at 0.24 mm; additional coarse model layers restore a stable underside before the fine band. One coarse layer is expected to fail.",
                variable=dict(coarse_model_layer_count=[1, 2, 4, 8], coarse_height_mm=.24, subsequent_height_mm=.12),
                control="A: current 0.12 mm band starting at parent print Z13.40 mm",
                counting_rule="Count from the last portion of the retained outer underside to begin: first coarse nozzle Z15.32 mm. Each treatment supplies at least N coarse layers across that test lip before the fine band; earlier-starting portions receive more.",
                scoring=["Record whether the first model layer falls away with the supports, separately from later recovery.",
                         "Compare remaining underside continuity, retained dimensions, edge gaps and fine-wall disturbance at the same full-scale front lip.",
                         "Prefer the shortest coarse start with a stable remaining underside and an undisturbed fine face; first-layer loss alone does not rank the treatments."],
                fixed_settings="Shipping faucet global profile, original -15 degree pose and bed contact, six-wall solid foot region, Tree(auto)/Default, 0.45 mm requested top support gap, temperatures, cooling, trim and normal seam. No blockers or fan/temperature treatments.",
                transfer_limit="Cropping changes perimeter length and layer return time. A recovered coupon does not establish the complete faucet's final underside dimensions, strength or finish.",
                physical_result="Unprinted; no recovery or adhesion result", specimens=prep["specimens"],
                project=prep["project"], project_sha256=prep["project_sha256"],
                automatic_next_print=False, auto_resume_authorized=False, scheduled_monitor_requested=False)
    save(HERE / "study-plan.json", plan)

    # Combine the same five lips and all fourteen prepared scarf swatches for
    # a real time/footprint comparison, without changing either treatment set.
    scarf = json.loads((SCARF_HERE / "preparation.json").read_text())
    assert scarf["settings_source_sha256"] == PARENT_PROJECT_SHA
    combined_lip_offsets = [(-87.5, 0), (-87.5, -72), (-87.5, 72), (-45.5, -36), (-45.5, 36)]
    combined_definitions = [dict(d, offset=xy) for d, xy in zip(definitions, combined_lip_offsets, strict=True)]
    for specimen, part in zip(scarf["specimens"], scarf["parts"], strict=True):
        source = ROOT / part["source"]
        assert sha(source) == part["stl_sha256"]
        combined_definitions.append(dict(id="S" + specimen["id"], name="S" + specimen["name"], kind="scarf",
                                          source=source, offset=(-4.5 + 34 * (specimen["column_from_left"] - 1),
                                                                 -57 + 38 * (specimen["row_from_front"] - 1)),
                                          fine_band=tuple(specimen["layer_band_print_z_mm"]),
                                          fine_height=specimen["fine_layer_height_mm"], overrides=specimen["object_overrides"],
                                          regular_seam_control=specimen["regular_seam_control"],
                                          seam_method=specimen["seam_method"],
                                          tested_gap_percent_of_nozzle=specimen["tested_gap_percent_of_nozzle"],
                                          tested_gap_mm=specimen["tested_gap_mm"],
                                          repeated_control=specimen["repeated_control"],
                                          row_from_front=specimen["row_from_front"],
                                          column_from_left=specimen["column_from_left"],
                                          scarf_length_mm=specimen["scarf_length_mm"],
                                          scarf_start_height_percent=specimen["scarf_start_height_percent"],
                                          fine_start_height_mm=specimen["fine_start_height_mm"]))
    folder = HERE / "combined"
    combined = make_project(folder, COMBINED_STEM, source_project, combined_definitions, modifier_mesh, source_info)
    save(folder / "study-plan.json", dict(plan, status="Prepared combined coarse-start and seam-gap comparison; unprinted",
                                           specimens=combined["specimens"], project=combined["project"],
                                           project_sha256=combined["project_sha256"],
                                           scarf_source=str((SCARF_HERE / "study-plan.json").relative_to(ROOT)),
                                           transfer_limit="Nineteen simultaneous objects change layer return time and heat exposure relative to either separate plate. Scarf settings and coarse-start counts are otherwise identical."))
    print(json.dumps(dict(lift_project=prep["project"], combined_project=combined["project"],
                          crop_bounds_mm=mesh.bounds.tolist(), crop_volume_fraction=crop.Volume() / full_foot.Volume(),
                          preparation_only=True), indent=2))


if __name__ == "__main__":
    main()
