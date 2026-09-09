"""Staged scenes for the funnel guides — one picture per step, bodies moved into the action.

A camera on the closed mold shows an object. These show a step: only the bodies the step
touches, standing in the mold's own frame, with the thing that step moves lifted off its seat
along the axis it travels and painted coral. The offset is the arrow, so a page that says
"lower the core onto the poured cavity" has a picture of exactly that and no annotation.

    tools/cad-venv/bin/python tools/funnel-mold-guide/mold_scenes.py           # all
    tools/cad-venv/bin/python tools/funnel-mold-guide/mold_scenes.py core-down # one
    tools/cad-venv/bin/python tools/funnel-mold-guide/mold_scenes.py --list

Bodies come from the shipped assembly rather than from `funnel_mold.py`, so a scene is the
geometry that was exported and costs an import instead of a rebuild. Staged STEPs are written
under the guide's own `out/`, which is gitignored and named in `pack.py`'s NOT_BUNDLED_DIRS —
`render-step-posed.js` resolves a job's `step` relative to `hardware/`, so they cannot live
outside it.

This file sits under `tools/` so no build reading reaches it: `trace_inputs.py`'s ELSEWHERE,
`affected.py`'s two artifact scopes, and the dev server's content roots all stop here.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

# Set before `_cadq_export` is imported: it takes the build lock at import time, and staging a
# picture out of an already-exported assembly is not a CAD build.
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
GUIDE = HARDWARE / "funnel-mold-guide"
ART, OUT = GUIDE / "art", GUIDE / "out"
ASSEMBLY = "printed-parts/zone-c/funnel-mold/funnel-mold-assembly.step"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"

sys.path.insert(0, str(HARDWARE / "scripts"))
from _material_base import M_STAINLESS, step_safe  # noqa: E402
from _cadq_export import _per_solid_color, import_assembly  # noqa: E402

# The guide's own inks, so a body in a picture wears the colour the page calls it by.
M_CAVITY = cq.Color(0.169, 0.486, 0.580)
M_CORE = cq.Color(0.827, 0.573, 0.180)
M_SILICONE = cq.Color(0.184, 0.184, 0.208)
# Coral is the cue colour everywhere else in this guide, and in a picture it means the same
# thing: this is what the step moves.
M_MOVES = cq.Color(0.839, 0.251, 0.314)
# A thing that is on the bench for the step and is not part of the mold.
M_BENCH = cq.Color(0.42, 0.55, 0.62)

NAVY = "#1a1a2e"
#: How far an arriving part stands off its seat, everywhere. One distance, so the gap reads as
#: a direction of assembly rather than as an accident of framing.
POISE = 62.0
#: The core's own working stroke. Where a step is about that stroke, the picture uses it.
STROKE = 32.0

TOP_Z = 88.649           # the core plate's upper face, closed
CHAMBER_ID = 11.8 * 25.4  # the owned chamber's listed interior

_BODIES: dict | None = None


def body(name: str):
    global _BODIES
    if _BODIES is None:
        _BODIES = import_assembly(HARDWARE / ASSEMBLY)
    return cq.Workplane(obj=_BODIES[name][0])


def group(prefix: str):
    return [body(f"{prefix}-{i}") for i in (1, 2, 3, 4)]


def _add(assembly: cq.Assembly, shape, name: str, color) -> None:
    if shape is not None:
        assembly.add(shape, name=name, color=step_safe(color))


def _scene(name: str) -> cq.Assembly:
    return cq.Assembly(name=f"{name}-scene")


def up(shape, dz: float = POISE):
    return shape.translate((0, 0, dz))


def on_bed(shape):
    """A part dropped so its lowest point sits on Z=0 — the plate, as it is sliced."""
    return shape.translate((0, 0, -shape.val().BoundingBox().zmin))


def flip(shape):
    """Turned over the way a hand turns it."""
    return shape.rotate((0, 0, 0), (1, 0, 0), 180.0)


def _cavity_at_rest(a: cq.Assembly, silicone: bool = True) -> None:
    """The half that stays put, with its washers seated."""
    _add(a, body("cavity"), "cavity", M_CAVITY)
    if silicone:
        _add(a, body("funnel"), "silicone", M_SILICONE)
    for i, washer in enumerate(group("washer"), 1):
        _add(a, washer, f"washer-{i}", M_STAINLESS)


def _core_at(a: cq.Assembly, dz: float, color, rod: bool = True) -> None:
    """The core and everything that travels with it, standing `dz` off its seat."""
    _add(a, up(body("core"), dz), "core", color)
    if rod:
        _add(a, up(body("rod"), dz), "rod", M_STAINLESS)
    for i, (screw, nut) in enumerate(zip(group("jack-screw"), group("square-nut")), 1):
        _add(a, up(screw, dz), f"jack-screw-{i}", M_STAINLESS)
        _add(a, up(nut, dz), f"square-nut-{i}", M_STAINLESS)


# --- the scenes -------------------------------------------------------------------------

def s_core_down() -> cq.Assembly:
    """Lower the core onto the poured cavity: silicone at rest, blades still clear."""
    a = _scene("core-down")
    _cavity_at_rest(a)
    _core_at(a, POISE, M_MOVES)
    return a


def s_core_lifted() -> cq.Assembly:
    """The working lift: the core off the cured part, the rod clear of its socket."""
    a = _scene("core-lifted")
    _cavity_at_rest(a)
    _add(a, body("rod"), "rod", M_STAINLESS)          # the rod stays with the silicone
    _core_at(a, STROKE, M_MOVES, rod=False)
    return a


def s_dry_assemble() -> cq.Assembly:
    """The dry run before any coating: no silicone, the rod in the core, blades approaching."""
    a = _scene("dry-assemble")
    _cavity_at_rest(a, silicone=False)
    _core_at(a, POISE, M_MOVES)
    return a


def s_hold_cure() -> cq.Assembly:
    """What holds the core seated through the cure — the guide's own arrangement."""
    a = _scene("hold-cure")
    _cavity_at_rest(a)
    _core_at(a, 0.0, M_CORE)
    board = cq.Workplane("XY").box(292, 292, 12).translate((0, 0, TOP_Z + 6))
    # A window over the pour dish, so the dish can still be seen and topped up.
    board = board.cut(cq.Workplane("XY").box(56, 56, 20).translate((-80, -80, TOP_Z + 6)))
    weight = cq.Workplane("XY").box(110, 110, 56).translate((0, 0, TOP_Z + 12 + 28))
    _add(a, board, "clamp-board", M_MOVES)
    _add(a, weight, "weight", M_MOVES)
    return a


def s_in_chamber() -> cq.Assembly:
    """The filled mold as it stands for its cycle: a flat shelf under it, a tray around it."""
    a = _scene("in-chamber")
    _cavity_at_rest(a)
    _core_at(a, 0.0, M_CORE)
    # A flat shelf leaves the cavity's backing-air exits open; a tray catches the overflow.
    shelf = cq.Workplane("XY").box(300, 300, 8).translate((0, 0, -4))
    tray = (cq.Workplane("XY").box(330, 330, 30)
            .cut(cq.Workplane("XY").box(312, 312, 26).translate((0, 0, 4)))
            .translate((0, 0, -23)))
    _add(a, shelf, "shelf", M_BENCH)
    _add(a, tray, "catch-tray", M_BENCH)
    return a


def s_chamber_fit() -> cq.Assembly:
    """The assembled mold inside the chamber's own bore, seen down the axis."""
    a = _scene("chamber-fit")
    _cavity_at_rest(a, silicone=False)
    _core_at(a, 0.0, M_CORE)
    wall = (cq.Workplane("XY").circle(CHAMBER_ID / 2 + 3).circle(CHAMBER_ID / 2)
            .extrude(120).translate((0, 0, -10)))
    _add(a, wall, "chamber-wall", M_BENCH)
    return a


def s_print_plates() -> cq.Assembly:
    """How each half meets the bed: the cavity opening up, the core inverted."""
    a = _scene("print-plates")
    _add(a, on_bed(body("cavity")).translate((-150, 0, 0)), "cavity", M_CAVITY)
    _add(a, on_bed(flip(body("core"))).translate((150, 0, 0)), "core", M_CORE)
    bed = cq.Workplane("XY").box(640, 300, 6).translate((0, 0, -3))
    _add(a, bed, "bed", M_BENCH)
    return a


def lay(shape, x: float, y: float, *, about=None, angle: float = 0.0):
    """A part laid on the bench at (x, y): turned about `about`, dropped to Z=0, then moved by
    its own centre so the grid is a grid rather than the assembly's own scatter."""
    if about is not None:
        shape = shape.rotate((0, 0, 0), about, angle)
    shape = on_bed(shape)
    centre = shape.val().Center()
    return shape.translate((x - centre.x, y - centre.y, 0))


def s_hardware() -> cq.Assembly:
    """The steel for one mold, off the parts and laid out: four of each, and the rod."""
    a = _scene("hardware")
    # The screws lie along Y so four of them read as four rather than as one long bar.
    for i, screw in enumerate(group("jack-screw")):
        _add(a, lay(screw, -72 + i * 34, 56, about=(1, 0, 0), angle=90),
             f"jack-screw-{i + 1}", M_STAINLESS)
    for i, nut in enumerate(group("square-nut")):
        _add(a, lay(nut, -60 + i * 40, -6), f"square-nut-{i + 1}", M_STAINLESS)
    for i, washer in enumerate(group("washer")):
        _add(a, lay(washer, -66 + i * 44, -50), f"washer-{i + 1}", M_STAINLESS)
    # The rod is the one piece of this steel that ends up inside the part.
    _add(a, lay(body("rod"), 0, -96, about=(0, 1, 0), angle=90), "rod", M_MOVES)
    return a


class Scene:
    def __init__(self, build, *, cam, target=None, span=None, size="1800x1350",
                 up=(0, 0, 1), ortho=True):
        self.build, self.cam, self.target = build, cam, target
        self.span, self.size, self.up, self.ortho = span, size, up, ortho


SCENES = {
    "core-down": Scene(s_core_down, cam=(0.85, -1.0, 0.50), size="1800x1450"),
    "core-lifted": Scene(s_core_lifted, cam=(0.85, -1.0, 0.42), size="1800x1350"),
    "dry-assemble": Scene(s_dry_assemble, cam=(0.85, -1.0, 0.50), size="1800x1450"),
    "hold-cure": Scene(s_hold_cure, cam=(0.85, -1.0, 0.46), size="1800x1350"),
    "in-chamber": Scene(s_in_chamber, cam=(0.85, -1.0, 0.40), size="1800x1400"),
    "chamber-fit": Scene(s_chamber_fit, cam=(0.2, -0.28, 1.0), size="1700x1700"),
    "print-plates": Scene(s_print_plates, cam=(0.6, -1.0, 0.55), size="2000x1150"),
    "hardware": Scene(s_hardware, cam=(0.30, -0.75, 0.95), size="1900x1250"),
}


def render(names: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="mold-scene-", dir=OUT) as directory:
        work, jobs = Path(directory), []
        for name in names:
            scene = SCENES[name]
            step = work / f"{name}.step"
            _per_solid_color(scene.build()).export(str(step))
            job = {
                "step": str(step.relative_to(HARDWARE)),
                "out": str(ART / f"{name}.png"),
                "cam": list(scene.cam), "up": list(scene.up), "size": scene.size,
                "bg": NAVY, "trim": True, "solid": True, "ortho": scene.ortho,
                "ground": False, "fog": False,
            }
            if scene.target is not None:
                job["target"] = list(scene.target)
            if scene.span is not None:
                job["span"] = scene.span
            jobs.append(job)
            print(f"  staged {name}")
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)


def main(argv: list[str]) -> int:
    if "--list" in argv:
        print("\n".join(SCENES))
        return 0
    wanted = [a for a in argv if not a.startswith("-")] or list(SCENES)
    unknown = [n for n in wanted if n not in SCENES]
    if unknown:
        print(f"unknown scene(s): {', '.join(unknown)}", file=sys.stderr)
        return 1
    render(wanted)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
