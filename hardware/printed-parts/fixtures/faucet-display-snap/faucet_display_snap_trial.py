"""Complete faucet-display fit trial, cut directly from the production geometry.

The two print parts are the complete cover and the complete display end of
its shell, with a short gooseneck stub behind it. Both retain their production
print orientation. No display, latch, support or tube feature is rescaled.
"""
from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import sys

import cadquery as cq
import trimesh

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HW.parent
for path in (HW / "scripts", HW / "faucet-layout", HW / "printed-parts/faucet",
             HW / "printed-parts/faucet/faucet-shell",
             HW / "printed-parts/faucet/faucet-display-cover"):
    sys.path.insert(0, str(path))
import _display_snap as snap
import faucet_shell as shell
import faucet_display_cover as cover
import faucet_assembly as assembly
import refresh_print_project as production_print
from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, C_FAUCET_DISPLAY, C_FAUCET_DISPLAY_GLASS, one_body

NECK_STUB = 20.0


def trial_bounds():
    origin, _, normal = shell._tip_frame()
    frame = cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))
    features = (shell.build_display_outer_envelope(), shell.build_display_snap_arms(),
                shell.build_display_feet_pads())
    head_end = max(part.val().moved(frame.inverse).BoundingBox().ymax for part in features)
    # The wire entry and all display features remain on the test piece.
    neck_end = max(head_end, shell.display_ribbon_reference_start_s) + NECK_STUB
    return head_end, neck_end


def trial_region(s_end):
    return shell._cradle_prism(100.0, -5.0, s_end, -150.0, 100.0)


def build_trial():
    head_end, neck_end = trial_bounds()
    full = shell.build_shell()
    tip = shell.build_shell_tip(full)
    clip = trial_region(neck_end)
    housing = tip.intersect(clip)
    lid = cover.build_display_cover()
    witness = tip.intersect(trial_region(head_end + 1.0))
    missing = witness.cut(housing).val().Volume()
    if missing > 1e-5:
        raise ValueError(f"trial removes {missing} mm³ from the complete display housing")
    return housing, lid, clip, {"complete_head_end_s_mm": head_end,
                                "neck_cut_s_mm": neck_end,
                                "minimum_neck_stub_mm": NECK_STUB,
                                "missing_head_material_mm3": missing}


def print_pose(body, angle):
    rotated = body.rotate((0, 0, 0), (1, 0, 0), angle)
    bounds = rotated.val().BoundingBox()
    return rotated.translate((-(bounds.xmin + bounds.xmax) / 2.0,
                               -(bounds.ymin + bounds.ymax) / 2.0,
                               -bounds.zmin))


def export_part(body, name, rotation):
    solid = body.val()
    if not solid.isValid() or len(solid.Solids()) != 1:
        raise ValueError(f"{name}: expected one valid solid")
    mesh = shell.piece_mesh(body)
    payload = mesh.export(file_type="stl")
    printed = trimesh.load_mesh(io.BytesIO(payload), file_type="stl")
    if (not printed.is_watertight or not printed.is_winding_consistent
            or printed.body_count != 1 or printed.volume <= 0.0):
        raise ValueError(f"{name}: serialized STL is not one closed volume")
    path = HERE / f"{name}.stl"
    path.write_bytes(payload)
    export_assembly(one_body(body, name, C_FAUCET_BLACK), str(path.with_suffix(".step")))
    print(f"{name}: {len(printed.faces)} triangles", flush=True)
    return {"stl": path.name, "sha256": hashlib.sha256(payload).hexdigest(),
            "source_rotation_x_degrees": rotation,
            "source_stl_already_in_print_pose": True,
            "volume_mm3": solid.Volume(), "triangles": len(printed.faces),
            "watertight": True, "body_count": 1,
            "bounds_mm": printed.bounds.tolist()}


def main():
    sources = [Path(shell.__file__), Path(cover.__file__), Path(snap.__file__),
               Path(assembly.__file__), Path(production_print.__file__), Path(__file__),
               HW / "printed-parts/faucet/_faucet_interface.py",
               HW / "reference/touch-flo-faucet/display-reference/component-envelopes.json"]
    before = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sources}
    housing, lid, clip, retained = build_trial()
    poses = {name: angle for name, _, angle in production_print.PARTS}
    report = {"schema_version": 2, "physical_trial_completed": False,
              "trial": "complete faucet display housing and cover with short gooseneck stub",
              "retained_geometry": retained,
              "sources": before,
              "parts": []}
    for body, name, angle in ((housing, "display-trial-housing", poses["faucet-shell-tip"]),
                              (lid, "display-trial-cover", poses["faucet-display-cover"])):
        report["parts"].append(export_part(print_pose(body, angle), name, angle))
    assy = cq.Assembly(name="faucet-display-fit-trial")
    assy.add(housing, name="trial_housing", color=C_FAUCET_BLACK)
    assy.add(lid, name="trial_cover", color=C_FAUCET_BLACK)
    assy.add(assembly.build_display_body(), name="faucet_display", color=C_FAUCET_DISPLAY)
    assy.add(assembly.build_display_screen(), name="faucet_display_screen", color=C_FAUCET_DISPLAY_GLASS)
    for name, body, color in (
        ("soda_tube", assembly.build_soda_faucet_tube(), cq.Color(0.2, 0.5, 0.9)),
        ("flavor_left", assembly.build_flavor_tube(-1), cq.Color(0.9, 0.5, 0.1)),
        ("flavor_right", assembly.build_flavor_tube(1), cq.Color(0.9, 0.5, 0.1)),
        ("ribbon", assembly.build_display_ribbon(), cq.Color(0.2, 0.7, 0.4)),
    ):
        assy.add(body.intersect(clip), name=name, color=color)
    export_assembly(assy, str(HERE / "faucet-display-fit-trial.step"))
    after = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sources}
    if before != after:
        raise ValueError("faucet sources changed during the trial build; regenerate from stable geometry")
    (HERE / "trial-geometry.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
