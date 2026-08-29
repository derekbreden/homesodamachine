"""Render the modern-home, 1/4-inch inline water-tee installation states.

The two frames use one literal orthographic camera and one stationary existing
water line.  The open frame lays the kit tee below the two square-cut ends; the
connected frame seats those ends in the tee's run and seats the new white
appliance branch in its third port.  Every visible tube and fitting is a CAD
solid; the page may add instructional typography and arrows around these
transparent pictures without painting over their plumbing.

Regenerate from the repository root with::

    tools/cad-venv/bin/python \
      hardware/quickstart/plumbing/modern/render_modern_tee.py
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import cadquery as cq
from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
ROOT = HARDWARE.parent
ART = HERE / "art"
TEE_STEP = HARDWARE / "reference" / "tee-connector" / "tee-connector.step"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"

# The repository's PP0208E reference has three equal 20.07 mm reaches from its
# centre.  It is posed with its run on world X and its branch opening downward.
TEE_REACH = 20.07
TUBE_OD = 6.35
TUBE_ID = 4.20
MAIN_Z = 42.0
BEFORE_TEE_Z = 0.0
AFTER_TEE_Z = MAIN_Z
RUN_CUT_X = 27.0
RUN_SEATED_X = 16.0
SCENE_X = 400.0
BRANCH_FREE_Z = -32.0

# One camera, crop and target for both states.  Keeping the line and the canvas
# registered makes the tee's move and the three insertions directly comparable.
CAMERA = (0.65, -1.60, 0.75)
TARGET = (0.0, 0.0, 6.0)
ORTHO_SPAN = 48.0
RENDER_SIZE = "2000x1100"

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(HARDWARE / "scripts"))
from _cadq_export import _per_solid_color, _write_mesh_payload, note_read, note_write  # noqa: E402


BLACK_PP = cq.Color(0.025, 0.030, 0.035, 1.0)
EXISTING_LINE = cq.Color(0.42, 0.50, 0.58, 1.0)
NEW_WHITE_LINE = cq.Color(0.62, 0.65, 0.69, 1.0)
NEW_WHITE_TRACER = cq.Color(0.30, 0.33, 0.37, 1.0)
CUT_BORE = cq.Color(0.075, 0.085, 0.095, 1.0)


def _unit(vector: cq.Vector) -> cq.Vector:
    length = vector.Length
    if length <= 0.0:
        raise ValueError("a tube needs two different endpoints")
    return vector.multiply(1.0 / length)


def _tube(start: tuple[float, float, float], end: tuple[float, float, float]):
    """A hollow 1/4-inch LLDPE tube with true square-cut end faces."""
    first = cq.Vector(*start)
    last = cq.Vector(*end)
    vector = last - first
    direction = _unit(vector)
    outer = cq.Solid.makeCylinder(TUBE_OD / 2.0, vector.Length, first, direction)
    # Extend the subtraction through both faces so the bore is actually open.
    inner_start = first - direction.multiply(0.20)
    inner = cq.Solid.makeCylinder(
        TUBE_ID / 2.0,
        vector.Length + 0.40,
        inner_start,
        direction,
    )
    return outer.cut(inner)


def _branch_points(start_z: float, *, y: float = 0.0) -> list[cq.Vector]:
    return [
        cq.Vector(0.0, y, start_z),
        cq.Vector(0.0, y, start_z - 17.0),
        cq.Vector(4.0, y, start_z - 27.0),
        cq.Vector(18.0, y, start_z - 41.0),
        cq.Vector(46.0, y, start_z - 55.0),
        cq.Vector(110.0, y, start_z - 78.0),
        cq.Vector(300.0, y, start_z - 130.0),
    ]


def _swept_round(points: list[cq.Vector], radius: float):
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(points)])
    first = points[0]
    plane = cq.Plane(
        origin=(first.x, first.y, first.z),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
    )
    return cq.Workplane(plane).circle(radius).sweep(path, isFrenet=True).val()


def _appliance_branch(start_z: float, *, open_end: bool):
    """A seated straight lead followed by one plausible under-sink service loop.

    The generous continuation is deliberate: the fixed instruction viewport
    crops it through the lower-right edge instead of displaying an arbitrary
    remote tube end.
    """
    outer = _swept_round(_branch_points(start_z), TUBE_OD / 2.0)
    if not open_end:
        return outer
    # Only the first 8 mm needs a bore: it is the one free, square-cut face the
    # customer sees.  Leaving the invisible continuation solid avoids a sweep
    # subtraction degeneracy without changing any rendered surface.
    bore_start = cq.Vector(0.0, 0.0, start_z + 0.20)
    bore = cq.Solid.makeCylinder(
        TUBE_ID / 2.0,
        8.20,
        bore_start,
        cq.Vector(0.0, 0.0, -1.0),
    )
    return outer.cut(bore)


def _appliance_branch_tracer(start_z: float):
    """A narrow, modeled tracer on the tube's camera-facing surface."""
    return _swept_round(_branch_points(start_z, y=-TUBE_OD / 2.0), 0.34)


def _bore_witness(
    face: tuple[float, float, float],
    inward: tuple[float, float, float],
):
    """A recessed dark disk that lets a square cut read at instruction scale."""
    direction = _unit(cq.Vector(*inward))
    start = cq.Vector(*face) + direction.multiply(0.28)
    return cq.Solid.makeCylinder(TUBE_ID / 2.0, 0.22, start, direction)


def _tee(center_z: float):
    """Pose the checked-in tee with its run horizontal and branch downward."""
    note_read(TEE_STEP)
    tee = cq.importers.importStep(str(TEE_STEP)).val()
    # Source axes: run ±Z, branch +Y.  +90° about Y maps the run to +X;
    # then -90° about X keeps that run fixed and maps the branch to -Z.
    return (
        tee.rotate((0, 0, 0), (0, 1, 0), 90.0)
        .rotate((0, 0, 0), (1, 0, 0), -90.0)
        .translate((0.0, 0.0, center_z))
    )


def _existing_line(scene: cq.Assembly, *, seated: bool) -> None:
    inner_x = RUN_SEATED_X if seated else RUN_CUT_X
    scene.add(
        _tube((-SCENE_X, 0.0, MAIN_Z), (-inner_x, 0.0, MAIN_Z)),
        name="existing-water-left",
        color=EXISTING_LINE,
    )
    scene.add(
        _tube((inner_x, 0.0, MAIN_Z), (SCENE_X, 0.0, MAIN_Z)),
        name="existing-water-right",
        color=EXISTING_LINE,
    )
    if not seated:
        scene.add(
            _bore_witness((-inner_x, 0.0, MAIN_Z), (-1.0, 0.0, 0.0)),
            name="existing-left-cut-bore",
            color=CUT_BORE,
        )
        scene.add(
            _bore_witness((inner_x, 0.0, MAIN_Z), (1.0, 0.0, 0.0)),
            name="existing-right-cut-bore",
            color=CUT_BORE,
        )


def build_before() -> cq.Assembly:
    scene = cq.Assembly(name="modern-inline-tee-before")
    _existing_line(scene, seated=False)
    scene.add(_tee(BEFORE_TEE_Z), name="kit-tee", color=BLACK_PP)
    scene.add(
        _appliance_branch(BRANCH_FREE_Z, open_end=True),
        name="new-appliance-branch",
        color=NEW_WHITE_LINE,
    )
    scene.add(
        _appliance_branch_tracer(BRANCH_FREE_Z),
        name="new-appliance-branch-tracer",
        color=NEW_WHITE_TRACER,
    )
    scene.add(
        _bore_witness((0.0, 0.0, BRANCH_FREE_Z), (0.0, 0.0, -1.0)),
        name="new-branch-cut-bore",
        color=CUT_BORE,
    )
    return scene


def build_after() -> cq.Assembly:
    scene = cq.Assembly(name="modern-inline-tee-after")
    _existing_line(scene, seated=True)
    scene.add(_tee(AFTER_TEE_Z), name="kit-tee", color=BLACK_PP)
    # Penetrate four millimetres beyond the visible collet face so the tube
    # unmistakably reads as fully seated, with no light-line gap at the mouth.
    branch_inside_z = AFTER_TEE_Z - TEE_REACH + 4.0
    scene.add(
        _appliance_branch(branch_inside_z, open_end=False),
        name="new-appliance-branch",
        color=NEW_WHITE_LINE,
    )
    scene.add(
        _appliance_branch_tracer(branch_inside_z),
        name="new-appliance-branch-tracer",
        color=NEW_WHITE_TRACER,
    )
    return scene


def _export_scene(scene: cq.Assembly, target: Path) -> None:
    colored = _per_solid_color(scene)
    colored.export(str(target))
    _write_mesh_payload(target, colored)


def _canonicalize_png(path: Path) -> None:
    with Image.open(path) as image:
        image.convert("RGBA").save(path, format="PNG", compress_level=9, optimize=False)


def _job(step: Path, output: Path) -> dict:
    return {
        "step": str(step.relative_to(HARDWARE)),
        "out": str(output),
        "cam": CAMERA,
        "up": (0.0, 0.0, 1.0),
        "target": TARGET,
        "size": RENDER_SIZE,
        "span": ORTHO_SPAN,
        "bg": "#ffffff",
        "trim": False,
        "solid": True,
        "ortho": True,
        "ground": False,
        "fog": False,
    }


def main() -> None:
    if not TEE_STEP.is_file():
        raise FileNotFoundError(f"missing PP0208E reference solid: {TEE_STEP}")
    note_read(RENDERER)
    ART.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".modern-tee-", dir=HERE) as directory:
        work = Path(directory)
        before_step = work / "modern-inline-tee-before.step"
        after_step = work / "modern-inline-tee-after.step"
        _export_scene(build_before(), before_step)
        _export_scene(build_after(), after_step)

        outputs = (
            ART / "modern-inline-tee-before.png",
            ART / "modern-inline-tee-after.png",
        )
        jobs = [_job(before_step, outputs[0]), _job(after_step, outputs[1])]
        subprocess.run(
            ["node", str(RENDERER), "--jobs", "-"],
            cwd=ROOT,
            input=json.dumps(jobs),
            text=True,
            check=True,
        )
        for output in outputs:
            # White is part of this intentional instruction-art canvas.  In
            # particular, retaining it keeps the white branch visible where it
            # exits through the crop instead of treating that tube as page
            # background merely because the two meet at the frame edge.
            _canonicalize_png(output)
            note_write(output)

    print("modern inline-tee art:")
    for name in ("modern-inline-tee-before.png", "modern-inline-tee-after.png"):
        print(f"  {ART / name}")


if __name__ == "__main__":
    main()
