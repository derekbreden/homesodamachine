"""Six Sculpted display covers for the existing faucet tip.

STEP and STL coordinates use the assembled faucet frame. The print project
applies each trial's rotation. A–F are recessed into the planar bezel.
"""

from dataclasses import asdict, dataclass
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(path for path in HERE.parents if (path / "tools").is_dir())
FAUCET = ROOT / "hardware/printed-parts/faucet"
for directory in (ROOT / "hardware/scripts", FAUCET, FAUCET / "faucet-shell",
                  FAUCET / "faucet-display-cover"):
    sys.path.insert(0, str(directory))

from _cadq_export import export_assembly
from _materials import C_FAUCET_BLACK, one_body
import faucet_display_cover as cover
import faucet_shell as shell
import flute_payload


@dataclass(frozen=True)
class Trial:
    id: str
    preload_mm: float
    lip_height_mm: float
    rotation_x_degrees: float


TRIALS = (
    Trial("A", 1.00, 3.00, 130.0),
    Trial("B", 1.25, 3.00, 130.0),
    Trial("C", 1.00, 3.00, -50.0),
    Trial("D", 1.25, 3.00, -50.0),
    Trial("E", 1.00, 3.10, -50.0),
    Trial("F", 1.25, 3.10, -50.0),
)
LABEL_DEPTH = 0.25
LABEL_HEIGHT = 2.8
LABEL_X = 12.0
INSTALL_LIFT = 8.5
TIP = FAUCET / "faucet-shell/faucet-shell-tip.step"
TIP_STL = TIP.with_suffix(".stl")
PROTECTED = (TIP, TIP_STL, FAUCET / "faucet-display-cover/faucet-display-cover.step",
             FAUCET / "faucet-display-cover/faucet-display-cover.stl")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(path.relative_to(ROOT))


def frame():
    origin, _, normal = shell._tip_frame()
    return cq.Location(cq.Plane(origin=origin, xDir=(1, 0, 0), normal=normal))


@lru_cache(maxsize=2)
def seated_native(lip_height):
    seated = cover.build_seated_display_cover().val()
    top = shell.display_clip_bottom_n + lip_height
    if top > shell.display_clip_top_n:
        extension = shell._cradle_prism(
            shell.display_cover_skirt_width / 2.0 + 1.0,
            shell.display_clip_s_bottom, shell.display_clip_s_top,
            shell.display_clip_top_n, top)
        inner = shell.build_display_neck_reference(
            shell.display_neck_outer_r - shell.display_clip_lip_radius)
        extension = cover.build_plate_outer().intersect(extension).cut(inner)
        seated = seated.fuse(extension.val()).clean()
    return seated.moved(frame().inverse)


def wing_transform(side, preload):
    slope = side * preload / (cover.bezel_n_bottom - shell.display_clip_top_n)
    return cq.Matrix([[1.0, 0.0, slope, -slope * cover.bezel_n_bottom],
                      [0.0, 1.0, 0.0, 0.0],
                      [0.0, 0.0, 1.0, 0.0],
                      [0.0, 0.0, 0.0, 1.0]])


def relaxed_native(trial):
    seated = seated_native(trial.lip_height_mm)
    bezel = seated.intersect(cq.Solid.makeBox(
        100.0, 150.0, 50.0, cq.Vector(-50.0, -50.0, cover.bezel_n_bottom)))
    pieces = [bezel]
    for side in (-1, 1):
        half = cq.Solid.makeBox(50.0, 150.0, cover.bezel_n_bottom + 50.0,
                                cq.Vector(0.0 if side > 0 else -50.0, -50.0, -50.0))
        pieces.append(seated.intersect(half).transformGeometry(
            wing_transform(side, trial.preload_mm)))
    return pieces[0].fuse(*pieces[1:]).clean()


def label_cutter(trial):
    return (cq.Workplane("XY")
            .text(trial.id, LABEL_HEIGHT, LABEL_DEPTH + 0.05, font="Arial", kind="bold",
                  halign="center", valign="center", combine=True)
            .translate((LABEL_X, shell._display_cover_center_s,
                        shell.display_cover_top_n - LABEL_DEPTH)).val())


def build_cover(trial):
    relaxed = relaxed_native(trial)
    cutter = label_cutter(trial)
    label_slab = cq.Solid.makeBox(100.0, 100.0, LABEL_DEPTH,
                                 cq.Vector(-50.0, -25.0, shell.display_cover_top_n - LABEL_DEPTH))
    required_cut = cutter.intersect(label_slab).Volume()
    result = relaxed.cut(cutter).clean()
    if abs(relaxed.intersect(cutter).Volume() - required_cut) > 1e-5:
        raise ValueError(f"{trial.id}: the complete label must lie inside the planar bezel")
    if not result.isValid() or len(result.Solids()) != 1:
        raise ValueError(f"{trial.id}: expected one valid cover")
    return cq.Workplane(obj=result.moved(frame()))


def main():
    protected = {relative(path): digest(path) for path in PROTECTED}
    ready = json.loads((FAUCET / "faucet-petgf.readiness.json").read_text())
    printed_tip = ready["validation"]["source_stls"][relative(TIP_STL)]
    if printed_tip != digest(TIP_STL):
        raise ValueError("The current tip differs from the successfully submitted faucet tip")
    sources = (Path(__file__), Path(cover.__file__), Path(shell.__file__),
               FAUCET / "_display_snap.py", FAUCET / "_faucet_interface.py", TIP, TIP_STL,
               FAUCET / "faucet-petgf.readiness.json")
    report = {
        "style": "Sculpted",
        "scope": "Display covers only, for the unchanged printed tip; physical retention is the trial reading.",
        "sources_sha256": {relative(path): digest(path) for path in sources},
        "printed_tip_stl_sha256": printed_tip,
        "preload_reference_n_mm": shell.display_clip_top_n,
        "installation_lift_n_mm": INSTALL_LIFT,
        "label_depth_mm": LABEL_DEPTH,
        "label_remaining_bezel_mm": cover.bezel_thickness - LABEL_DEPTH,
        "parts": [],
    }
    for trial in TRIALS:
        print(f"Building cover {trial.id}: {trial.preload_mm:g} mm preload, "
              f"{trial.lip_height_mm:g} mm lip, Rx {trial.rotation_x_degrees:g}", flush=True)
        shape = build_cover(trial)
        name = f"cover-retention-{trial.id.lower()}"
        step = HERE / f"{name}.step"
        export_assembly(one_body(shape, name, C_FAUCET_BLACK), str(step))
        shell.write_bed_file(shape, step.with_suffix(".stl"))
        flute_payload.cut(step, step.with_suffix(".stl"), preserve_print_triangles=True)
        top = shell.display_clip_bottom_n + trial.lip_height_mm
        report["parts"].append({
            **asdict(trial), "step": step.name, "stl": step.with_suffix(".stl").name,
            "sha256": digest(step.with_suffix(".stl")), "step_sha256": digest(step),
            "volume_mm3": shape.val().Volume(), "valid_single_solid": True,
            "groove_roof_clearance_mm": shell.display_clip_top_n + 0.15 - top,
            "lip_radius_mm": shell.display_clip_lip_radius,
            "bottom_inset_per_wing_mm": trial.preload_mm *
                (cover.bezel_n_bottom - shell.display_clip_bottom_n) /
                (cover.bezel_n_bottom - shell.display_clip_top_n),
        })
    if protected != {relative(path): digest(path) for path in PROTECTED}:
        raise ValueError("A production faucet artifact changed during the trial build")
    report["production_artifacts_unchanged"] = protected
    (HERE / "trial-geometry.json").write_text(json.dumps(report, indent=2) + "\n")


if __name__ == "__main__":
    main()
