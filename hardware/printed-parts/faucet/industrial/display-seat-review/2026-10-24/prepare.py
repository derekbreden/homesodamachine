"""Build the requested 4.5 mm lower display-head candidate for visual review.

This manual study exports its own geometry. Production files and print projects
are inputs, and no printer connection is made.
"""
from __future__ import annotations

import base64
from contextlib import ExitStack
from datetime import datetime, timezone
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from unittest.mock import patch

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/bambu_print.py").is_file())
sys.path[:0] = [str(ROOT / "hardware/faucet-layout"),
               str(ROOT / "hardware/printed-parts/faucet/industrial")]
import faucet_assembly as assembly
import faucet_shell as shell
import industrial_display_cover as cover

DROP = 4.5
RECESS = 1.0
RECESS_DIAMETER = 4.0
SOURCE = ROOT / "hardware/printed-parts/faucet/faucet-shell/faucet-shell-tip.step"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def main():
    origin, along, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))
    baseline_feet = shell.display_feet_n
    baseline_pad_depth = shell.display_foot_pad_depth
    pad_base = baseline_feet - baseline_pad_depth
    feet = pad_base - RECESS
    assert abs(baseline_feet - feet - DROP) < 1e-8
    source_hashes = {str(p.relative_to(ROOT)): sha(p) for p in (
        SOURCE, SOURCE.with_suffix('.stl'), Path(shell.__file__), Path(cover.__file__),
        ROOT / "hardware/reference/touch-flo-faucet/display-reference/component-envelopes.json")}

    before = cq.importers.importStep(str(SOURCE)).val()
    # Clear the complete support stock to its common former base, then cut
    # four 1 mm deep pockets on the original foot centers.
    opening = shell._cradle_prism(
        shell.display_neck_outer_r + shell.wall_thickness_min,
        shell.dispense_face_thickness, shell.display_s_top,
        pad_base, shell.display_cover_top_n + 1).val()
    native_pockets = (cq.Workplane("XY").workplane(offset=feet)
                      .pushPoints(list(shell.display_foot_centers))
                      .circle(RECESS_DIAMETER / 2).extrude(RECESS + .1))
    pockets = shell._display_world(native_pockets).val()
    after = before.cut(opening, pockets, tol=1e-6)
    if not after.isValid() or len(after.Solids()) != 1:
        raise ValueError("Review tip must be one valid solid")
    before_seated = cover.build_seated_display_cover().val()
    before_relaxed = cover.build_display_cover().val()
    before_top = cover.DIMENSIONS.n_top
    before_bezel_bottom = cover.DIMENSIONS.bezel_n_bottom
    before_display = assembly.build_display_body().val()
    before_screen = assembly.build_display_screen().val()

    changed_constants = {
        "display_feet_n": feet,
        "display_floor_n": feet,
        "display_face_n": shell.display_face_n - DROP,
        "display_cover_top_n": shell.display_cover_top_n - DROP,
    }
    with ExitStack() as stack:
        for key, value in changed_constants.items():
            stack.enter_context(patch.object(shell, key, value))
        after_seated = cover.build_seated_display_cover().val()
        after_relaxed = cover.build_display_cover().val()
        after_top = cover.DIMENSIONS.n_top
        after_bezel_bottom = cover.DIMENSIONS.bezel_n_bottom
    for name, solid in (("before-cover", before_relaxed), ("after-cover", after_relaxed)):
        if not solid.isValid() or len(solid.Solids()) != 1:
            raise ValueError(name + " must be one valid solid")

    displacement = normal.multiply(-DROP)
    after_display = before_display.translate(displacement)
    after_screen = before_screen.translate(displacement)
    flavors = [assembly.build_flavor_faucet_run(side).val() for side in (-1, 1)]
    water = assembly.build_soda_faucet_tube().val()
    readings = []
    overlaps = []
    for side, tube in zip((-1, 1), flavors):
        overlap = after_display.intersect(tube)
        overlaps.append(overlap)
        readings.append({"flavor_side": side,
                         "before_hardware_gap_mm": before_display.distance(tube),
                         "after_intersection_mm3": overlap.Volume(),
                         "scope": "Conservative vendor-derived component envelope against modeled tube wall"})

    floors = [f for f in after.Faces() if f.geomType() == "PLANE"
              and abs((f.Center() - origin).dot(normal) - feet) < 1e-5
              and f.normalAt().dot(normal) > .999]
    if len(floors) != 4:
        raise ValueError(f"Expected four recess bearing floors, found {len(floors)}")
    retained_snap = {
        "bottom_n_mm": shell.display_clip_bottom_n,
        "top_n_mm": shell.display_clip_top_n,
        "radial_engagement_mm": shell.display_neck_outer_r - shell.display_clip_lip_radius,
        "industrial_wing_extension_mm": cover.DIMENSIONS.wing_extension_mm,
    }
    record = {
        "status": "Visual review candidate; no print submitted; production geometry remains the reference",
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "source_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "source_sha256": source_hashes,
        "history": {
            "clearance_lift_commit": "5271aa710fdb3ddb7bb735a7114d80cbc4ad324b",
            "clearance_lift_mm": 1.5,
            "original_support_height_mm": 2.0,
            "four_mm_tubes_commit": "8742c66249d4e96f56e3635657f041b573e6ab25",
        },
        "drop_breakdown_mm": {"added_clearance_lift": 1.5, "original_supports": 2.0, "new_recess": RECESS},
        "total_display_and_bezel_drop_mm": DROP,
        "display_normal_world": normal.toTuple(),
        "inward_displacement_world_mm": displacement.toTuple(),
        "foot_centers_x_s_mm": shell.display_foot_centers,
        "before_foot_bearing_n_mm": baseline_feet,
        "pre_lift_foot_bearing_n_mm": baseline_feet - 1.5,
        "former_support_base_and_new_surrounding_seat_n_mm": pad_base,
        "new_recess_floor_n_mm": feet,
        "recess_diameter_mm": RECESS_DIAMETER,
        "recess_depth_below_former_support_base_mm": RECESS,
        "recess_floor_count": len(floors),
        "recess_floor_areas_mm2": [f.Area() for f in floors],
        "before_cover_top_n_mm": before_top,
        "after_cover_top_n_mm": after_top,
        "cover_bezel_thickness_before_after_mm": [before_top - before_bezel_bottom, after_top - after_bezel_bottom],
        "glass_to_bezel_gap_before_after_mm": [before_bezel_bottom - shell.display_face_n,
                                                 after_bezel_bottom - (shell.display_face_n - DROP)],
        "uncut_round_neck_crown_n_mm": shell.tube_shell_center_y + shell.tube_shell_outer_r,
        "cover_proudness_above_uncut_round_neck_before_after_mm": [
            top - shell.tube_shell_center_y - shell.tube_shell_outer_r for top in (before_top, after_top)],
        "retained_snap_datums": retained_snap,
        "conservative_hardware_to_flavor_tubes": readings,
        "normal_drop_beyond_first_modeled_tube_contact_mm": DROP - min(r["before_hardware_gap_mm"] for r in readings),
        "after_hardware_to_tip_intersection_mm3": after_display.intersect(after).Volume(),
        "after_cover_to_tip_intersection_mm3": after_seated.intersect(after).Volume(),
        "after_hardware_to_cover_intersection_mm3": after_display.intersect(after_seated).Volume(),
        "native_tip_volume_before_after_mm3": [before.Volume(), after.Volume()],
        "removed_tip_stock_mm3": before.cut(after).Volume(),
        "interpretation": "The surrounding seating area is lowered to the former support bases at N8.10, and each foot drops another 1.00 mm into its pocket. This is the complete 4.50 mm reduction, rather than removing only material above the existing N10.10 pocket floor.",
        "physical_scope": "Photos report excess display-cover gap and substantial tube clearance. Vendor component envelopes are conservative, and their modeled overlap is not a physical interference measurement. Fit and retention of this candidate are untested.",
    }
    save(HERE / "geometry-review.json", record)

    for name, part in (("candidate-tip", after), ("candidate-cover", after_relaxed)):
        cq.exporters.export(part, str(HERE / (name + ".step")))
        cq.exporters.export(part, str(HERE / (name + ".stl")), tolerance=.005, angularTolerance=.1)

    crop = shell._cradle_prism(25, -1, 53, -7, 28).val()
    raised = before.intersect(shell._cradle_prism(20, 2, shell.display_s_top, 10.1, 12).val())
    removed = before.cut(after)
    mesh_parts = {
        "beforeTip": before, "afterTip": after,
        "beforeCover": before_seated, "afterCover": after_seated,
        "beforeDisplay": before_display, "afterDisplay": after_display,
        "beforeScreen": before_screen, "afterScreen": after_screen,
        "oldNubs": raised, "removedStock": removed,
        "newFloors": cq.Compound.makeCompound(floors),
        "flavorLeft": flavors[0], "flavorRight": flavors[1], "water": water,
        "overlaps": cq.Compound.makeCompound([s for o in overlaps for s in o.Solids()]),
    }
    half = shell._display_world(cq.Workplane("XY").box(30, 100, 100)
                                .translate((-15, 25, 15))).val()
    for name in ("beforeTip", "afterTip", "beforeCover", "afterCover",
                 "beforeDisplay", "afterDisplay", "beforeScreen", "afterScreen",
                 "flavorLeft", "flavorRight", "water", "overlaps"):
        mesh_parts[name + "Section"] = mesh_parts[name].intersect(half)
    mesh_data = {}
    for name, part in mesh_parts.items():
        if part.Faces():
            local = part.intersect(crop).moved(frame.inverse) if name != "newFloors" else part.moved(frame.inverse)
            vertices, faces = local.tessellate(.045, .16)
        else:
            vertices, faces = [], []
        positions = np.round(np.array([v.toTuple() for v in vertices], dtype='<f4'), 4)
        indices = np.array(faces, dtype='<u4')
        mesh_data[name] = {
            "positions": base64.b64encode(gzip.compress(positions.tobytes(), mtime=0)).decode(),
            "indices": base64.b64encode(gzip.compress(indices.tobytes(), mtime=0)).decode(),
            "triangles": len(faces),
        }
    (HERE / "viewer-data.json").write_text(json.dumps({"meshes": mesh_data, "measurements": record}, separators=(',', ':')))
    print(json.dumps(record, indent=2), flush=True)
    print('viewer-data bytes:', (HERE / 'viewer-data.json').stat().st_size, flush=True)


if __name__ == "__main__":
    main()
