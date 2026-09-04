"""Render a modern-home, all-push-connect cold-water installation sequence.

The household line is 1/4-inch OD LLDPE already seated in an existing John
Guest PP0408W-style push-to-connect union.  The installation shown here never
opens a threaded or compression joint:

1. turn the household quarter-turn shutoff from ON to OFF while the LLDPE and
   its PTC union remain connected;
2. press the union's release collet and withdraw the existing LLDPE;
3. push a short supplied jumper into that union;
4. push one PP0208E tee onto the jumper;
5. push the original household line into the tee's other run port;
6. push the new appliance/filter branch into the tee, then tug-check it.

Every visible fitting, tube, valve, and handle is literal CAD geometry.
The wide shutoff pair, release trio, and cumulative tee sequence each retain a
registered orthographic camera so motion is the only visual change within a
step. Motion arrows stay out of the renders: the guide page places one fixed
flat glyph at each projected action anchor. The final PNGs have transparent
canvases so the guide page is their only background.

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
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq
from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(parent for parent in HERE.parents if parent.name == "hardware")
ROOT = HARDWARE.parent
ART = HERE / "art"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"
VIEWER_SCENE = ROOT / "web" / "public" / "js" / "viewer" / "scene.js"

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "reference" / "jg-pp0408w"))
from _cadq_export import _per_solid_color, _write_mesh_payload, note_read, note_write  # noqa: E402
import jg_pp0408w as union_ref  # noqa: E402


# John Guest's official PP0208E data sheet, Pp4608_01/23:
# https://www.johnguest.com/sites/jg/files/2023-04/
# JG%20Drinks%20Polypropylene%20Equal%20Tee%20Data%20Sheet.pdf
#
# These are the black 1/4-inch row's dimensions.  The customer-facing render
# uses them directly instead of the repo's intentionally approximate McMaster
# layout stand-in in hardware/reference/tee-connector.
PP0208_TUBE_OD = 6.35       # A, tube OD
PP0208_RUN_SPAN = 39.0      # B, face to face with collets released
PP0208_REACH = 19.5         # C, centre to each of the three port faces
PP0208_INSERTION = 15.7     # D, tube face to internal stop
PP0208_MAX_OD = 16.3        # E, widest body/collar diameter
PP0208_BORE = 4.3           # F, through bore
PP0208_BRANCH_ENVELOPE = 27.7  # G, branch face to opposite body envelope

TUBE_OD = PP0208_TUBE_OD
TUBE_ID = 4.20
AXIS_Z = 42.0
UNION_X = -98.0
TEE_X = -12.0
TEE_STAGED_X = 15.0
RELEASE_STARTED_GAP = 5.5
TEE_FREE_X = 51.0
SCENE_END = 420.0

UNION_REACH = union_ref.reach()
UNION_INSERTION = union_ref.INSERTION
UNION_RIGHT_FACE = UNION_X + UNION_REACH
UNION_LEFT_FACE = UNION_X - UNION_REACH
RELEASE_STARTED_X = UNION_RIGHT_FACE + RELEASE_STARTED_GAP
TEE_LEFT_FACE = TEE_X - PP0208_REACH
TEE_RIGHT_FACE = TEE_X + PP0208_REACH
TEE_BRANCH_FACE_Z = AXIS_Z - PP0208_REACH


# Every household/tap-water tube and the existing white push connector use one
# neutral-white instruction material.  Its midtone is held below clipped white
# so the shared studio light can shape the parts without implying multiple tube
# types; highlights still land white on the page.
C_WATER_WHITE = cq.Color(0.82, 0.84, 0.85, 1.0)
C_CUT_BORE = cq.Color(0.065, 0.075, 0.085, 1.0)
C_TEE_BODY = cq.Color(0.035, 0.040, 0.045, 1.0)
C_TEE_COLLET = cq.Color(0.085, 0.090, 0.100, 1.0)
C_VALVE_BODY = cq.Color(0.60, 0.39, 0.13, 1.0)
C_VALVE_SHOULDER = cq.Color(0.78, 0.55, 0.20, 1.0)
C_HANDLE = cq.Color(0.035, 0.27, 0.73, 1.0)
C_STEM = cq.Color(0.34, 0.36, 0.39, 1.0)
C_TOUCHED_COLLET = cq.Color(0.46, 0.50, 0.54, 1.0)
# The physical source declares 1.335 mm. This macro-only pose is enlarged so the two states
# remain distinct after the 13 x 19 sheet is printed.
ILLUSTRATED_COLLET_TRAVEL = 2.4


@dataclass(frozen=True)
class View:
    camera: tuple[float, float, float]
    target: tuple[float, float, float]
    span: float


WATER_VIEW = View((1.05, -1.72, 0.72), (-25.0, 8.0, 105.0), 104.0)
RELEASE_VIEW = View((0.58, -1.58, 0.66), (-77.8, 0.0, 42.0), 18.0)
TEE_VIEW = View((0.62, -1.58, 0.72), (-25.0, 0.0, 12.0), 52.0)
RENDER_SIZE = "2000x1100"
# Transparent rendering still carries a nominal clear color.  Matching the
# guide field keeps any browser-level edge RGB neutral, though alpha—not color
# keying—is what separates the scene from the page.
RENDER_CLEAR = "#dce7e9"


def _vector(values) -> cq.Vector:
    return values if isinstance(values, cq.Vector) else cq.Vector(*values)


def _unit(values) -> cq.Vector:
    vector = _vector(values)
    if vector.Length <= 0.0:
        raise ValueError("a direction needs non-zero length")
    return vector.multiply(1.0 / vector.Length)


def _cylinder(diameter: float, length: float, base, axis) -> cq.Solid:
    return cq.Solid.makeCylinder(diameter / 2.0, length, _vector(base), _unit(axis))


def _ring(outer_d: float, inner_d: float, length: float, base, axis) -> cq.Shape:
    direction = _unit(axis)
    outer = _cylinder(outer_d, length, base, direction)
    inner = _cylinder(
        inner_d,
        length + 0.40,
        _vector(base) - direction.multiply(0.20),
        direction,
    )
    return outer.cut(inner)


def _tube(start, end) -> cq.Shape:
    """A hollow 1/4-inch LLDPE tube with true square-cut end faces."""
    first = _vector(start)
    last = _vector(end)
    vector = last - first
    direction = _unit(vector)
    outer = cq.Solid.makeCylinder(TUBE_OD / 2.0, vector.Length, first, direction)
    inner = cq.Solid.makeCylinder(
        TUBE_ID / 2.0,
        vector.Length + 0.40,
        first - direction.multiply(0.20),
        direction,
    )
    return outer.cut(inner)


def _swept_round(points: list[cq.Vector], radius: float) -> cq.Shape:
    path = cq.Wire.assembleEdges([cq.Edge.makeSpline(points)])
    first = points[0]
    plane = cq.Plane(
        origin=(first.x, first.y, first.z),
        xDir=(1.0, 0.0, 0.0),
        normal=(0.0, 0.0, -1.0),
    )
    return cq.Workplane(plane).circle(radius).sweep(path, isFrenet=True).val()


def _branch_points(start_z: float, *, y: float = 0.0) -> list[cq.Vector]:
    return [
        cq.Vector(TEE_X, y, start_z),
        cq.Vector(TEE_X, y, start_z - 18.0),
        cq.Vector(TEE_X + 7.0, y, start_z - 31.0),
        cq.Vector(TEE_X + 28.0, y, start_z - 47.0),
        cq.Vector(TEE_X + 75.0, y, start_z - 65.0),
        cq.Vector(TEE_X + 170.0, y, start_z - 93.0),
        cq.Vector(TEE_X + 360.0, y, start_z - 132.0),
    ]


def _branch(start_z: float, *, open_end: bool = False) -> cq.Shape:
    outer = _swept_round(_branch_points(start_z), TUBE_OD / 2.0)
    if not open_end:
        return outer
    bore = _cylinder(
        TUBE_ID,
        8.2,
        (TEE_X, 0.0, start_z + 0.2),
        (0.0, 0.0, -1.0),
    )
    return outer.cut(bore)


def _bore_witness(face, inward) -> cq.Solid:
    """A recessed dark disk that makes a free square tube end legible."""
    direction = _unit(inward)
    start = _vector(face) + direction.multiply(0.28)
    return cq.Solid.makeCylinder(TUBE_ID / 2.0, 0.22, start, direction)


def _add(scene: cq.Assembly, shape: cq.Shape, name: str, color: cq.Color) -> None:
    if not shape.isValid():
        raise RuntimeError(f"invalid shape: {name}")
    scene.add(shape, name=name, color=color)


def _pp0208e_parts(center=(0.0, 0.0, 0.0)) -> tuple[cq.Shape, tuple[cq.Shape, ...]]:
    """A dimensionally held PP0208E instruction solid from the official drawing.

    The three-port topology and every published envelope/port/tube dimension
    are exact.  The official sheet does not dimension the minor cosmetic
    breakpoints along each arm, so those are a restrained symmetric profile:
    a 10.6-mm barrel, a full-16.3-mm collar body, and an annular release collet.
    """
    collar_near = 8.2
    collet_near = 16.3
    barrel_d = 10.6
    collet_d = 9.7
    collet_bore = 6.70

    arms = (
        ((1.0, 0.0, 0.0), (-1.0, 0.0, 0.0)),
        ((-1.0, 0.0, 0.0), (1.0, 0.0, 0.0)),
        ((0.0, 0.0, -1.0), (0.0, 0.0, 1.0)),
    )
    body = cq.Solid.makeSphere(barrel_d / 2.0)
    collets = []
    for axis, inward in arms:
        axis_v = _vector(axis)
        body = body.fuse(
            _cylinder(barrel_d, collar_near, (0.0, 0.0, 0.0), axis),
            _cylinder(
                PP0208_MAX_OD,
                collet_near - collar_near,
                axis_v.multiply(collar_near),
                axis,
            ),
        )
        collets.append(
            _ring(
                collet_d,
                collet_bore,
                PP0208_REACH - collet_near,
                axis_v.multiply(collet_near),
                axis,
            )
        )

        face = axis_v.multiply(PP0208_REACH)
        socket_stop = face + _vector(inward).multiply(PP0208_INSERTION)
        socket = _cylinder(
            PP0208_TUBE_OD,
            PP0208_INSERTION + 0.2,
            socket_stop - _vector(inward).multiply(0.1),
            axis,
        )
        body = body.cut(socket)

    run_bore = _cylinder(
        PP0208_BORE,
        PP0208_RUN_SPAN + 0.4,
        (-PP0208_REACH - 0.2, 0.0, 0.0),
        (1.0, 0.0, 0.0),
    )
    branch_bore = _cylinder(
        PP0208_BORE,
        PP0208_REACH + 0.2,
        (0.0, 0.0, -PP0208_REACH - 0.2),
        (0.0, 0.0, 1.0),
    )
    body = body.cut(run_bore.fuse(branch_bore))

    translation = cq.Vector(*center)
    return body.translate(translation), tuple(part.translate(translation) for part in collets)


def _pp0208e_bounds_hold() -> None:
    body, collets = _pp0208e_parts()
    compound = cq.Compound.makeCompound([body, *collets])
    bounds = compound.BoundingBox()
    claims = (
        ("run minimum", bounds.xmin, -PP0208_REACH),
        ("run maximum", bounds.xmax, PP0208_REACH),
        ("width minimum", bounds.ymin, -PP0208_MAX_OD / 2.0),
        ("width maximum", bounds.ymax, PP0208_MAX_OD / 2.0),
        ("branch face", bounds.zmin, -PP0208_REACH),
        ("opposite envelope", bounds.zmax, PP0208_MAX_OD / 2.0),
        ("branch envelope", bounds.zlen, PP0208_BRANCH_ENVELOPE),
    )
    for label, actual, expected in claims:
        if abs(actual - expected) > 0.06:
            raise RuntimeError(
                f"PP0208E {label} is {actual:.3f}, not official {expected:.3f} mm"
            )


def _add_tee(scene: cq.Assembly, *, installed: bool) -> None:
    center_x = TEE_X if installed else TEE_STAGED_X
    body, collets = _pp0208e_parts((center_x, 0.0, AXIS_Z))
    _add(scene, body, "pp0208e-body", C_TEE_BODY)
    for index, collet in enumerate(collets, start=1):
        _add(scene, collet, f"pp0208e-release-collet-{index}", C_TEE_COLLET)


def _canonical_union_parts(
    *,
    pressed_right: bool,
    separate_right: bool = False,
) -> tuple[cq.Shape, ...]:
    union = union_ref.build_jg_pp0408w().val()
    if not pressed_right and not separate_right:
        return (union,)

    sleeve_start = union_ref.ring_face_z
    sleeve_end = union_ref.port_face_z
    erase = _cylinder(
        union_ref.COLLET_D + 0.4,
        sleeve_end - sleeve_start + 0.4,
        (0.0, 0.0, sleeve_start - 0.2),
        (0.0, 0.0, 1.0),
    )
    body = union.cut(erase)
    sleeve = _ring(
        union_ref.COLLET_D,
        union_ref.COLLET_BORE,
        sleeve_end - sleeve_start,
        (
            0.0,
            0.0,
            sleeve_start - (ILLUSTRATED_COLLET_TRAVEL if pressed_right else 0.0),
        ),
        (0.0, 0.0, 1.0),
    )
    return body, sleeve


def _add_union(
    scene: cq.Assembly,
    *,
    center=(UNION_X, 0.0, AXIS_Z),
    pressed_right: bool = False,
    highlight_right: bool = False,
) -> None:
    parts = _canonical_union_parts(
        pressed_right=pressed_right,
        separate_right=highlight_right,
    )
    for index, part in enumerate(parts, start=1):
        posed = part.rotate((0, 0, 0), (0, 1, 0), 90.0).translate(center)
        color = C_TOUCHED_COLLET if highlight_right and index == 2 else C_WATER_WHITE
        _add(scene, posed, f"existing-pp0408w-{index}", color)


def _add_source_line(scene: cq.Assembly) -> None:
    stop_x = UNION_LEFT_FACE + UNION_INSERTION
    _add(
        scene,
        _tube((-SCENE_END, 0.0, AXIS_Z), (stop_x, 0.0, AXIS_Z)),
        "existing-source-lldpe",
        C_WATER_WHITE,
    )


def _add_original_line(scene: cq.Assembly, *, destination: str) -> None:
    if destination == "union":
        start_x = UNION_RIGHT_FACE - UNION_INSERTION
    elif destination == "tee":
        start_x = TEE_RIGHT_FACE - PP0208_INSERTION
    elif destination == "release-started":
        start_x = RELEASE_STARTED_X
    elif destination == "tee-free":
        start_x = TEE_FREE_X
    else:
        raise ValueError(f"unknown original-line destination: {destination}")
    _add(
        scene,
        _tube((start_x, 0.0, AXIS_Z), (SCENE_END, 0.0, AXIS_Z)),
        "existing-downstream-lldpe",
        C_WATER_WHITE,
    )
    if destination.endswith("free"):
        _add(
            scene,
            _bore_witness((start_x, 0.0, AXIS_Z), (1.0, 0.0, 0.0)),
            "existing-downstream-free-bore",
            C_CUT_BORE,
        )


def _add_jumper(scene: cq.Assembly) -> None:
    start_x = UNION_RIGHT_FACE - UNION_INSERTION
    stop_x = TEE_LEFT_FACE + PP0208_INSERTION
    _add(
        scene,
        _tube((start_x, 0.0, AXIS_Z), (stop_x, 0.0, AXIS_Z)),
        "supplied-lldpe-jumper",
        C_WATER_WHITE,
    )
    _add(
        scene,
        _bore_witness((stop_x, 0.0, AXIS_Z), (-1.0, 0.0, 0.0)),
        "jumper-free-bore",
        C_CUT_BORE,
    )


def _add_connected_branch(scene: cq.Assembly, *, tugged: bool = False) -> None:
    insertion = PP0208_INSERTION - (3.2 if tugged else 0.0)
    start_z = TEE_BRANCH_FACE_Z + insertion
    _add(scene, _branch(start_z), "filter-to-appliance-branch", C_WATER_WHITE)


def build_release_ready() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-ready")
    _add_union(scene, pressed_right=False, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="union")
    return scene


def build_release_pressed() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-pressed")
    _add_union(scene, pressed_right=True, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="union")
    return scene


def build_release_withdrawn() -> cq.Assembly:
    scene = cq.Assembly(name="modern-release-withdrawn")
    # Hold the highlighted collar depressed while the tube begins to move clear.
    _add_union(scene, pressed_right=True, highlight_right=True)
    _add_source_line(scene)
    _add_original_line(scene, destination="release-started")
    return scene


def _tee_scene(name: str) -> cq.Assembly:
    scene = cq.Assembly(name=name)
    _add_union(scene, pressed_right=False)
    _add_source_line(scene)
    return scene


def build_tee_jumper() -> cq.Assembly:
    scene = _tee_scene("modern-tee-jumper")
    _add_jumper(scene)
    _add_tee(scene, installed=False)
    _add_original_line(scene, destination="tee-free")
    return scene


def build_tee_mounted() -> cq.Assembly:
    scene = _tee_scene("modern-tee-mounted")
    _add_jumper(scene)
    _add_tee(scene, installed=True)
    _add_original_line(scene, destination="tee-free")
    return scene


def build_tee_existing() -> cq.Assembly:
    scene = _tee_scene("modern-tee-existing")
    _add_jumper(scene)
    _add_tee(scene, installed=True)
    _add_original_line(scene, destination="tee")
    return scene


def build_tee_complete() -> cq.Assembly:
    scene = _tee_scene("modern-tee-complete")
    _add_jumper(scene)
    _add_tee(scene, installed=True)
    _add_original_line(scene, destination="tee")
    _add_connected_branch(scene)
    return scene


def build_tee_tug_check() -> cq.Assembly:
    scene = _tee_scene("modern-tee-tug-check")
    _add_jumper(scene)
    _add_tee(scene, installed=True)
    _add_original_line(scene, destination="tee")
    _add_connected_branch(scene, tugged=True)
    return scene


# Product-neutral installed context: a compact quarter-turn body with integral
# PTC mouths.  It establishes the shutoff action without inventing a threaded
# or compression operation.  The exact measured PP0408W downstream is repeated
# here and in the release closeups.
WIDE_AXIS_Z = 112.0
WIDE_VALVE_X = -98.0
WIDE_UNION_X = 34.0


def _add_modern_shutoff(scene: cq.Assembly, *, on: bool) -> None:
    body_left = WIDE_VALVE_X - 28.0
    _add(
        scene,
        _cylinder(24.0, 56.0, (body_left, 0.0, WIDE_AXIS_Z), (1.0, 0.0, 0.0)),
        "quarter-turn-shutoff-body",
        C_VALVE_BODY,
    )
    for suffix, x, axis in (
        ("left", body_left, (-1.0, 0.0, 0.0)),
        ("right", body_left + 56.0, (1.0, 0.0, 0.0)),
    ):
        _add(scene, _cylinder(16.0, 7.0, (x, 0.0, WIDE_AXIS_Z), axis),
             f"shutoff-ptc-shoulder-{suffix}", C_VALVE_SHOULDER)
        _add(scene, _ring(9.7, 6.70, 3.2,
                         _vector((x, 0.0, WIDE_AXIS_Z)) + _vector(axis).multiply(7.0), axis),
             f"shutoff-release-collet-{suffix}", C_STEM)

    _add(scene, _cylinder(9.0, 13.0, (WIDE_VALVE_X, 0.0, WIDE_AXIS_Z + 8.0),
                          (0.0, 0.0, 1.0)), "shutoff-stem", C_STEM)
    hub_z = WIDE_AXIS_Z + 21.0
    handle = cq.Solid.makeBox(62.0, 9.0, 5.0,
                              cq.Vector(WIDE_VALVE_X - 31.0, -4.5, hub_z))
    handle = handle.fuse(
        _cylinder(12.0, 5.0, (WIDE_VALVE_X, 0.0, hub_z), (0.0, 0.0, 1.0))
    )
    if not on:
        handle = handle.rotate(
            (WIDE_VALVE_X, 0.0, hub_z),
            (WIDE_VALVE_X, 0.0, hub_z + 1.0),
            90.0,
        )
    _add(scene, handle, "quarter-turn-blue-handle", C_HANDLE)

    valve_left_face = body_left - 10.2
    valve_right_face = body_left + 66.2
    wide_union_left = WIDE_UNION_X - UNION_REACH
    wide_union_right = WIDE_UNION_X + UNION_REACH
    _add(scene, _tube((-SCENE_END, 0.0, WIDE_AXIS_Z),
                      (valve_left_face + 5.0, 0.0, WIDE_AXIS_Z)),
         "household-source-lldpe", C_WATER_WHITE)
    _add(scene, _tube((valve_right_face - 5.0, 0.0, WIDE_AXIS_Z),
                      (wide_union_left + UNION_INSERTION, 0.0, WIDE_AXIS_Z)),
         "household-line-before-union", C_WATER_WHITE)
    _add_union(scene, center=(WIDE_UNION_X, 0.0, WIDE_AXIS_Z), pressed_right=False)
    _add(scene, _tube((wide_union_right - UNION_INSERTION, 0.0, WIDE_AXIS_Z),
                      (SCENE_END, 0.0, WIDE_AXIS_Z)),
         "household-line-after-union", C_WATER_WHITE)


def build_water_on() -> cq.Assembly:
    scene = cq.Assembly(name="modern-water-on")
    _add_modern_shutoff(scene, on=True)
    return scene


def build_water_off() -> cq.Assembly:
    scene = cq.Assembly(name="modern-water-off")
    _add_modern_shutoff(scene, on=False)
    return scene


SCENES = (
    ("modern-water-on", build_water_on, WATER_VIEW),
    ("modern-water-off", build_water_off, WATER_VIEW),
    ("modern-release-ready", build_release_ready, RELEASE_VIEW),
    ("modern-release-pressed", build_release_pressed, RELEASE_VIEW),
    ("modern-release-withdrawn", build_release_withdrawn, RELEASE_VIEW),
    ("modern-tee-jumper", build_tee_jumper, TEE_VIEW),
    ("modern-tee-mounted", build_tee_mounted, TEE_VIEW),
    ("modern-tee-existing", build_tee_existing, TEE_VIEW),
    ("modern-tee-complete", build_tee_complete, TEE_VIEW),
    ("modern-tee-tug-check", build_tee_tug_check, TEE_VIEW),
)


def _export_scene(scene: cq.Assembly, target: Path) -> None:
    compound = scene.toCompound()
    if not compound.isValid():
        raise RuntimeError(f"invalid scene compound: {scene.name}")
    colored = _per_solid_color(scene)
    colored.export(str(target))
    _write_mesh_payload(target, colored)


def _canonicalize_png(path: Path) -> None:
    with Image.open(path) as image:
        if image.size != (2000, 1100):
            raise RuntimeError(f"unexpected render size {image.size}: {path}")
        rgba = image.convert("RGBA")
        alpha = rgba.getchannel("A")
        if alpha.getextrema() != (0, 255) or alpha.getbbox() is None:
            raise RuntimeError(f"render does not hold transparent scene art: {path}")
        rgba.save(path, format="PNG", compress_level=9, optimize=False)


def _job(step: Path, output: Path, view: View) -> dict:
    return {
        "step": str(step.relative_to(HARDWARE)),
        "out": str(output),
        "cam": view.camera,
        "up": (0.0, 0.0, 1.0),
        "target": view.target,
        "size": RENDER_SIZE,
        "span": view.span,
        "bg": RENDER_CLEAR,
        "trim": False,
        "solid": True,
        "ortho": True,
        "ground": False,
        "fog": False,
        "transparent": True,
    }


def main() -> None:
    union_ref.stations_hold()
    _pp0208e_bounds_hold()
    note_read(union_ref.STEP)
    note_read(RENDERER)
    note_read(VIEWER_SCENE)
    ART.mkdir(parents=True, exist_ok=True)

    outputs: list[Path] = []
    with tempfile.TemporaryDirectory(prefix=".modern-pushfit-", dir=HERE) as directory:
        work = Path(directory)
        jobs = []
        for name, builder, view in SCENES:
            scene = builder()
            step = work / f"{name}.step"
            output = ART / f"{name}.png"
            _export_scene(scene, step)
            jobs.append(_job(step, output, view))
            outputs.append(output)

        subprocess.run(
            ["node", str(RENDERER), "--jobs", "-"],
            cwd=ROOT,
            input=json.dumps(jobs),
            text=True,
            check=True,
        )
        for output in outputs:
            _canonicalize_png(output)
            note_write(output)

    print("modern push-connect installation art:")
    for output in outputs:
        print(f"  {output}")


if __name__ == "__main__":
    main()
