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

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HW.parent
for path in (HW / "scripts", HW / "faucet-layout", HW / "printed-parts/faucet",
             HW / "printed-parts/faucet/faucet-shell",
             HW / "printed-parts/faucet/faucet-display-cover"):
    sys.path.insert(0, str(path))
if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

import cadquery as cq
import trimesh

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
    features = (shell.build_display_outer_envelope(), shell.build_display_cover_lips(),
                shell.build_display_feet_pads())
    head_end = max(part.val().moved(frame.inverse).BoundingBox().ymax for part in features)
    # The open ribbon space and all display features remain on the test piece.
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


def numbers():
    """Production fine models, the head's authored loft and the fixture's clip and print poses."""
    from _cadq_export import note_read
    from _materials import linear

    def model(path):
        path = Path(str(path) + ".npz")
        note_read(path)
        return path.relative_to(ROOT).as_posix()

    poses = {name: angle for name, _, angle in production_print.PARTS}
    origin, _, normal = shell._tip_frame_data()
    return {
        "tip_model": model(HW / "printed-parts/faucet/faucet-shell/faucet-shell-tip.step"),
        "cover_model": model(HW / "printed-parts/faucet/faucet-display-cover/faucet-display-cover.step"),
        "seated_model": model(cover.SEATED_STEP),
        "assembly_model": model(HW / "faucet-layout/faucet-assembly.step"),
        "origin": origin, "normal": normal, "neck_stub": NECK_STUB,
        "head_outline_rows": [
            [shell.display_cover_skirt_width, shell.display_cover_skirt_length,
             shell.display_cover_skirt_r, height, shell._display_cover_center_s]
            for height in (shell.display_cover_bottom_n, shell.display_cover_shoulder_n)
        ] + [[shell.display_cover_face_width, shell.display_cover_face_length,
              shell.display_cover_face_r, shell.display_cover_top_n, shell._display_cover_center_s]],
        "head_clip_s": shell.display_head_s_max + 1.0,
        "pad_end_s": max(s for _, s in shell.display_foot_centers) + shell.display_foot_pad_width / 2.0,
        "lip_end_s": shell.display_clip_s_top,
        "ribbon_start_s": shell.display_ribbon_reference_start_s,
        "housing_angle": poses["faucet-shell-tip"], "cover_angle": poses["faucet-display-cover"],
        "black": list(linear(C_FAUCET_BLACK)), "display": list(linear(C_FAUCET_DISPLAY)),
        "glass": list(linear(C_FAUCET_DISPLAY_GLASS)),
        "water": list(linear(cq.Color(0.2, 0.5, 0.9))),
        "flavor": list(linear(cq.Color(0.9, 0.5, 0.1))),
        "ribbon": list(linear(cq.Color(0.2, 0.7, 0.4))),
        "context": [
            {"name": "faucet_display", "source": "faucet_display", "color": "display", "clip": False},
            {"name": "faucet_display_screen", "source": "faucet_display_screen", "color": "glass", "clip": False},
            {"name": "soda_tube", "source": "soda_faucet_tube", "color": "water", "clip": True},
            {"name": "flavor_left", "source": "flavor_tube_neg_x", "color": "flavor", "clip": True},
            {"name": "flavor_right", "source": "flavor_tube_pos_x", "color": "flavor", "clip": True},
            {"name": "ribbon", "source": "display_signal_ribbon", "color": "ribbon", "clip": True},
        ],
    }


def main():
    import _rust_part
    from _realized import code_digest

    data = numbers()
    sources = [Path(shell.__file__), Path(cover.__file__), Path(snap.__file__),
               Path(assembly.__file__), Path(production_print.__file__), Path(__file__),
               HW / "printed-parts/faucet/_faucet_interface.py",
               HW / "reference/touch-flo-faucet/display-reference/component-envelopes.json",
               Path(__file__).with_suffix(".rs"),
               *(ROOT / data[key] for key in ("tip_model", "cover_model", "seated_model", "assembly_model"))]
    before = {str(p.relative_to(ROOT)): (code_digest(p) if p.suffix == ".py"
                                        else hashlib.sha256(p.read_bytes()).hexdigest())
              for p in sources}
    said = _rust_part.cut("tooling", "faucet-display-snap", data, HERE)
    bodies = {body["name"]: body for body in said["bodies"]}
    housing = bodies["display-trial-housing"]
    retained = {key: housing[key] for key in (
        "complete_head_end_s_mm", "neck_cut_s_mm", "missing_head_material_mm3")}
    retained["minimum_neck_stub_mm"] = NECK_STUB
    report = {"schema_version": 3, "physical_trial_completed": False,
              "trial": "complete faucet display housing and cover with short gooseneck stub",
              "cover_print_shape": "relaxed inward-preloaded wings",
              "assembly_cover_shape": "nominal seated fit reference, not an elastic deformation prediction",
              "retention": {"radial_engagement_mm": snap.ENGAGEMENT,
                            "groove_depth_mm": snap.ENGAGEMENT + snap.RADIAL_SLIP,
                            "lip_height_mm": snap.LIP_HEIGHT,
                            "wing_inward_preload_at_lip_top_mm": snap.X_PRELOAD,
                            "wing_inward_preload_at_lip_bottom_mm": cover.preload_inward_at(shell.display_clip_bottom_n)},
              "retained_geometry": retained,
              "sources": {path: value for path, value in before.items() if not path.endswith(".py")},
              "source_code": {path: value for path, value in before.items() if path.endswith(".py")},
              "parts": []}
    for name, angle in (("display-trial-housing", data["housing_angle"]),
                         ("display-trial-cover", data["cover_angle"])):
        path = HERE / f"{name}.stl"
        mesh = trimesh.load(path, force="mesh")
        if (not mesh.is_watertight or not mesh.is_winding_consistent
                or mesh.body_count != 1 or mesh.volume <= 0.0):
            raise ValueError(f"{name}: serialized STL is not one closed volume")
        report["parts"].append({
            "stl": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "source_rotation_x_degrees": angle, "source_stl_already_in_print_pose": True,
            "source_translation_mm": bodies[name]["source_translation_mm"],
            "volume_mm3": bodies[name]["volume"], "triangles": len(mesh.faces),
            "watertight": True, "body_count": 1, "bounds_mm": mesh.bounds.tolist(),
        })
    after = {str(p.relative_to(ROOT)): (code_digest(p) if p.suffix == ".py"
                                       else hashlib.sha256(p.read_bytes()).hexdigest())
             for p in sources}
    if before != after:
        raise ValueError("faucet sources changed during the trial build; regenerate from stable geometry")
    (HERE / "trial-geometry.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
