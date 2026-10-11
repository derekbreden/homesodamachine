"""Prepare a provisional scarf matrix from the accepted faucet's actual neck.

Preparation only. Native slicing is local and does not connect to a printer.
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

STEM = "2026-10-10-faucet-scarf-swatches-v1-petgf-left04-z004-mark2"
WORK = ROOT / ".cache/printer-control/faucet-scarf-swatches-v1"
PARENT = FAUCET / "industrial/physical-acceptance.json"
PARENT_PROJECT_SHA = "2561bcdaa520e94f4b0a5989fcbb9e941f707b50c46af97655ceacf312748302"
PARENT_STL_SHA = "b3d9fa899ad07a075f1ba64258dc92d07a19612bf91b23439b2010185ee0125f"
PARENT_STEP_SHA = "fbeca2bc5ce5da7f5d808547c5bfd166046c8847e996227432e7c77acee6e716"
CUT_Z = (82.0, 100.2)
FINE_BAND = (4.04, 16.04)
FINE_HEIGHT = .08
# Letter, scarf length, start height %, row from front, column from left.
# Mix levels across positions rather than putting one treatment at an edge.
VARIANTS = (
    ("A", 0, 10, 1, 1), ("B", 5, 10, 1, 2),
    ("C", 20, 25, 1, 3), ("D", 10, 5, 1, 4),
    ("E", 30, 10, 2, 1), ("F", 5, 25, 2, 2),
    ("G", 20, 5, 2, 3), ("H", 10, 10, 2, 4),
    ("I", 30, 25, 3, 1), ("J", 5, 5, 3, 2),
    ("K", 20, 10, 3, 3), ("L", 10, 25, 3, 4),
    ("M", 30, 5, 4, 1), ("N", 0, 10, 4, 4),
)
COMMON = dict(wall_generator="classic", seam_position="back",
              override_filament_scarf_seam_setting="1",
              seam_slope_conditional="1", scarf_angle_threshold="155",
              seam_slope_entire_loop="0", seam_slope_steps="10",
              seam_slope_inner_walls="1", seam_slope_gap="0")
QUOTE = ("After this, depending on results of course, I'd like to consider something "
         "more swatch like, that gives a broader range of settings for one specific "
         "thing (I'm thinking the scarf). Please prepare for that.")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    HERE.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    for receipt in (HERE / "study-plan.json", HERE / "launch-plan.json", HERE / "launch.json"):
        if receipt.exists():
            state = json.loads(receipt.read_text())
            assert not any(state.get(k) for k in ("import_attempted", "send_attempted", "accepted"))
    parent = json.loads(PARENT.read_text())
    source_project = ROOT / parent["prepared_project"]
    source_stl = ROOT / parent["parts"][0]["source"]
    source_step = source_stl.with_suffix(".step")
    assert sha(source_project) == PARENT_PROJECT_SHA
    assert sha(source_stl) == PARENT_STL_SHA
    assert sha(source_step) == PARENT_STEP_SHA
    solid = cq.importers.importStep(str(source_step)).val()
    angle = parent["parts"][0]["rotation_x_degrees"]
    theta = math.radians(angle)
    rotation = np.array([[1, 0, 0], [0, math.cos(theta), -math.sin(theta)],
                         [0, math.sin(theta), math.cos(theta)]])
    source_mesh = trimesh.load(source_stl, force="mesh", process=True)
    lift = -float((source_mesh.vertices @ rotation.T)[:, 2].min())
    posed = solid.rotate((0, 0, 0), (1, 0, 0), angle).translate((0, 0, lift))
    swatch = posed.intersect(cq.Solid.makeBox(160, 180, CUT_Z[1] - CUT_Z[0],
                                           cq.Vector(-80, -80, CUT_Z[0])), tol=1e-6)
    swatch = swatch.translate((0, 0, -CUT_Z[0]))
    assert swatch.isValid() and len(swatch.Solids()) == 1
    step = HERE / "faucet-neck-swatch.step"
    export_assembly(one_body(cq.Workplane(obj=swatch), "faucet-neck-swatch", C_FAUCET_BLACK), str(step))
    stl = step.with_suffix(".stl")
    cq.exporters.export(swatch, str(stl), tolerance=.012, angularTolerance=.07)
    mesh = trimesh.load(stl, force="mesh", process=True)
    assert mesh.is_watertight and mesh.body_count == 1 and mesh.volume > 0
    flute_payload.cut(step, stl, preserve_print_triangles=True)

    names = [f"{v[0]} " + ("regular seam" if not v[1] else f"scarf {v[1]}mm start {v[2]}pct") for v in VARIANTS]
    offsets = tuple(((v[4] - 2.5) * 34., (v[3] - 2.5) * 38.5) for v in VARIANTS)
    project = HERE / (STEM + ".3mf")
    report = writer.refresh(source_project, project,
                            parts=tuple((name, stl, 0.) for name in names),
                            offsets=offsets, plate_border=40.,
                            title="Provisional faucet scarf length and start-height swatches")
    with zipfile.ZipFile(project) as z:
        members = {n: z.read(n) for n in z.namelist()}
    config = ET.fromstring(members["Metadata/model_settings.config"])
    ranges = ET.Element("objects")
    specimens = []
    for index, (part, variant) in enumerate(zip(report["parts"], VARIANTS, strict=True)):
        letter, length, percent, row, column = variant
        overrides = dict(COMMON, seam_slope_type="external" if length else "none",
                         seam_slope_min_length=str(length or 10),
                         seam_slope_start_height=f"{percent}%")
        obj = config.find(f"object[@id='{part['object_id']}']")
        for key, value in overrides.items():
            writer.metadata(obj, key, value)
        # Bambu uses 1-based build order here, not the component resource IDs.
        group = ET.SubElement(ranges, "object", id=str(index + 1))
        entry = ET.SubElement(group, "range", min_z=f"{FINE_BAND[0]:.4f}", max_z=f"{FINE_BAND[1]:.4f}")
        ET.SubElement(entry, "option", opt_key="layer_height").text = str(FINE_HEIGHT)
        specimens.append(dict(id=letter, name=part["name"], row_from_front=row,
                              column_from_left=column, identify_id=part["identify_id"],
                              object_id=part["object_id"], regular_seam_control=length == 0,
                              scarf_length_mm=length or None, scarf_start_height_percent=percent if length else None,
                              fine_start_height_mm=FINE_HEIGHT * percent / 100 if length else None,
                              object_overrides=overrides, plate_bounds_mm=part["plate_bounds_mm"],
                              layer_band_print_z_mm=list(FINE_BAND), fine_layer_height_mm=FINE_HEIGHT))
    members["Metadata/model_settings.config"] = writer.xml(config)
    members["Metadata/layer_config_ranges.xml"] = writer.xml(ranges)
    writer.archive_write(project, members)
    report.update(project=str(project.relative_to(ROOT)), project_sha256=sha(project),
                  source_step=str(source_step.relative_to(ROOT)), source_step_sha256=sha(source_step),
                  source_stl=str(source_stl.relative_to(ROOT)), source_stl_sha256=sha(source_stl),
                  source_acceptance=str(PARENT.relative_to(ROOT)),
                  shipping_reference=parent["native_archive"], shipping_reference_sha256=parent["native_archive_sha256"],
                  specimens=specimens, parent_pose=dict(rotation_x_degrees=angle, lift_mm=lift),
                  section_cuts=dict(neck_parent_print_z_mm=list(CUT_Z)),
                  preparation_only=True, launch_authorized=False, start_now=False,
                  submitted=False, import_attempted=False, send_attempted=False, accepted=False)
    save(HERE / "preparation.json", report)
    save(project.with_suffix(".print.json"), report)
    save(HERE / "study-plan.json", dict(
        schema=1, status="Provisional native-sliced scarf matrix; current physical results pending",
        authorization_quote=QUOTE, preparation_only=True, launch_authorized=False, start_now=False,
        import_attempted=False, send_attempted=False, accepted=False,
        source_study="hardware/printed-parts/faucet/finish-coupons/2026-10-10/README.md",
        source_study_task_id="1327799013", source_study_results_recorded=False,
        customer_outcome="A less visible faucet seam without a broader depression, exposed gap or rough neighboring wall",
        factors=dict(scarf_length_mm=[5, 10, 20, 30], scarf_start_height_percent=[5, 10, 25]),
        ordinary_seam_control_ids=["A", "N"], specimens=specimens,
        geometry=dict(height_mm=CUT_Z[1]-CUT_Z[0], actual_faucet_section=True, scaled=False,
                      support_blockers=False, minimum_requested_bed_inset_mm=40),
        fixed_settings=COMMON, project=report["project"], project_sha256=sha(project),
        prerequisites=["Evaluate current D, E and F for seam visibility, broader depressions and damage.",
                       "Use those results to retain or refine this proposed range and common layer height.",
                       "Require a separate instruction to start; read both printers and apply startup spacing at that time."],
        result_status="Unprinted; no physical appearance, adhesion, strength or leak result",
        selection_rule="Prefer lower seam visibility than both ordinary controls with no exposed gap, broader trough or rough surrounding wall. Similar-looking candidates favor settings closest to Bambu's 10mm/10% defaults.",
        transfer_limit="Short sections and fourteen simultaneous objects alter layer return time and heat exposure. A selected candidate requires confirmation in the complete faucet before replacing its shipping recipe.",
        automatic_next_print=False, auto_resume_authorized=False, scheduled_monitor_requested=False))
    command = ["/Applications/BambuStudio.app/Contents/MacOS/BambuStudio", "--slice", "0", "--arrange", "0", "--orient", "0",
               "--outputdir", str(WORK), "--export-3mf", STEM + ".gcode.3mf", str(project)]
    save(WORK / "slice-command.json", dict(argv=command, printer_connection=False))
    print(json.dumps(dict(project=report["project"], specimens=len(specimens), height_mm=CUT_Z[1]-CUT_Z[0],
                          swatch_bounds_mm=mesh.bounds.tolist(), preparation_only=True), indent=2))


if __name__ == "__main__":
    main()
