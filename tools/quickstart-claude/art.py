"""The quick start with words' own scenes: the four first-glass panels, as registered pairs.

RUN BY HAND. NOT A STEP OF THE BUILD — `hardware/quickstart-claude/README.md` names what holds
that. This module lives under `tools/`, which `tools/bazel/trace_inputs.py` names in `ELSEWHERE`,
and it keeps no `note_read` / `note_write` bookkeeping. Its pictures are committed to git beside
the sheet.

The install scenes (steps 1-6) are the wordless sheet's own renders, copied. These four are
composed here off the same solids — the Wellbom regulator, the enclosure's rear children with
their fluted skin, the whole appliance, the faucet — and the same presentation cuts
`_install_art.py` makes: the cylinder, the bottle, the customer's cord and the glass have no
source CAD and are drawn to catalogue size, and none is a dimensional authority.

Each pair is one camera, one span, and no trim, so the two states register: the cue on the
sheet rides the part that moves, and the state after it stays clean.

    tools/cad-venv/bin/python tools/quickstart-claude/art.py            # every scene
    tools/cad-venv/bin/python tools/quickstart-claude/art.py --list
    tools/cad-venv/bin/python tools/quickstart-claude/art.py pour-ready pour-pressed
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
SHEET = HARDWARE / "quickstart-claude"
ART = SHEET / "art"
OUT = SHEET / "out"

sys.path.insert(0, str(HARDWARE / "scripts"))
sys.path.insert(0, str(HARDWARE / "quickstart"))
sys.path.insert(0, str(HARDWARE / "install-guide"))

import cadquery as cq  # noqa: E402

import _cad_art as ca  # noqa: E402
import _install_art as ia  # noqa: E402

RENDERER = ia.RENDERER
MACHINE_STEP = ia.MACHINE_STEP

#: One frame for every scene here: the sheet's first-glass picture column is 678 x 444 px, and
#: a render at this size lands in it without a crop, so a cue placed in fractions of the box
#: lands on the same part in both states.
FRAME = "1526x1000"

SODA = cq.Color(0.50, 0.27, 0.11, 1.0)
GLASS = cq.Color(0.90, 0.91, 0.94, 1.0)
HANDWHEEL = cq.Color(0.10, 0.10, 0.12, 1.0)
VALVE_BRASS = ia.BRASS


# --- the cylinder and its regulator ------------------------------------------------------

#: The regulator's own frame: +Y toward the customer, -X out along the inlet to the cylinder,
#: -Z down the outlet. The cylinder valve is drawn as the CGA-320 valve every USA beverage
#: cylinder carries: a body on the neck, its outlet sideways on the inlet axis, a handwheel on
#: top. Catalogue proportions, not a dimensional authority.
VALVE_AXIS_X = -112.0
VALVE_BODY_D, VALVE_BODY_Z0, VALVE_BODY_Z1 = 34.0, -46.0, 34.0
VALVE_STEM_D, VALVE_STEM_Z1 = 14.0, 48.0
HANDWHEEL_D, HANDWHEEL_T = 50.0, 9.0
HANDWHEEL_HUB_D, HANDWHEEL_HUB_Z1 = 18.0, 62.0
NECK_D, NECK_Z0 = 32.0, -60.0
SHOULDER_Z0 = -100.0
CYLINDER_Z0 = -330.0
NUT_LEN = 14.0


def _regulator_module():
    return ia._load(ia.REGULATOR_DIR, "wellbom_regulator")


def _cylinder_and_regulator(gap: float) -> cq.Assembly:
    """The regulator on its cylinder, the tether's nut `gap` mm short of the outlet's flare."""
    reg = _regulator_module()
    a = reg.build_assembly()
    tip, _ = reg.outlet()
    x, y, z = tip
    inlet_face_x = reg.inlet()[0][0]

    # The valve: outlet stub on the inlet axis, body on the neck, handwheel on top.
    ia._add(a, ia._cyl(inlet_face_x, 0.0, 0.0, 14.0, VALVE_AXIS_X - inlet_face_x, axis="X")
            if VALVE_AXIS_X > inlet_face_x else
            ia._cyl(VALVE_AXIS_X, 0.0, 0.0, 14.0, inlet_face_x - VALVE_AXIS_X, axis="X"),
            "valve-outlet-stub", VALVE_BRASS)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, VALVE_BODY_Z0, VALVE_BODY_D, VALVE_BODY_Z1 - VALVE_BODY_Z0),
            "valve-body", VALVE_BRASS)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, VALVE_BODY_Z1, VALVE_STEM_D, VALVE_STEM_Z1 - VALVE_BODY_Z1),
            "valve-stem", ia.STEEL)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, VALVE_STEM_Z1, HANDWHEEL_D, HANDWHEEL_T),
            "handwheel", HANDWHEEL)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, VALVE_STEM_Z1 + HANDWHEEL_T, HANDWHEEL_HUB_D,
                       HANDWHEEL_HUB_Z1 - VALVE_STEM_Z1 - HANDWHEEL_T),
            "handwheel-hub", HANDWHEEL)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, NECK_Z0, NECK_D, VALVE_BODY_Z0 - NECK_Z0),
            "cylinder-neck", ia.CYLINDER)
    ia._add(a, (cq.Workplane("XY", origin=(VALVE_AXIS_X, 0.0, SHOULDER_Z0))
                .circle(ia.CYLINDER_D / 2.0).workplane(offset=NECK_Z0 - SHOULDER_Z0)
                .circle(NECK_D / 2.0).loft()),
            "cylinder-shoulder", ia.CYLINDER)
    ia._add(a, ia._cyl(VALVE_AXIS_X, 0.0, CYLINDER_Z0, ia.CYLINDER_D, SHOULDER_Z0 - CYLINDER_Z0),
            "cylinder", ia.CYLINDER)

    # The MI4508F4SLF's swivel nut and the red tether leaving it, `gap` short of home.
    nut_top = z - gap
    ia._add(a, ia._hex(x, y, nut_top - NUT_LEN, reg.OUTLET_HEX_FLATS, NUT_LEN),
            "tether-swivel-nut", ia.BRASS)
    top = nut_top - NUT_LEN
    ia._add(a, ia._bend([(x, y, top), (x, y, top - 46.0), (x + 130.0, y, top - 46.0)],
                        radius=22.0),
            "red-tether", ia.RED_TUBE)
    return a


def s_cylinder_nut_ready():
    return _cylinder_and_regulator(gap=26.0)


def s_cylinder_nut_seated():
    return _cylinder_and_regulator(gap=0.0)


def s_gas_on():
    """The same rig, closer: the handwheel that opens the gas and the knob that sets it."""
    return _cylinder_and_regulator(gap=0.0)


# --- the cord ------------------------------------------------------------------------------

def _cord(gap: float) -> cq.Assembly:
    a = ia._rear_face(cq.Assembly(name="power-cord-scene"))
    a.add(ia._c13_cordset(gap), name="c13-cordset", color=ia.CORDSET)
    return a


def s_power_cord_ready():
    return _cord(gap=42.0)


def s_power_cord_home():
    return _cord(gap=0.5)


# --- the bottle in the funnel --------------------------------------------------------------

def _bottle(lift: float) -> cq.Assembly:
    """`_install_art.s_bottle_in_funnel`, with the bottle `lift` mm above its seat."""
    a = cq.Assembly(name="fill-scene")
    ia._machine(a)
    mouth_x, mouth_y = ia.HOPPER_MID
    top = 355.0
    neck_z = top - 16.0 + lift
    ia._add(a, ia._cyl(mouth_x, mouth_y, neck_z, ia.BOTTLE_NECK_D, ia.BOTTLE_NECK_H),
            "bottle-neck", ia.BOTTLE_PET)
    shoulder = neck_z + ia.BOTTLE_NECK_H
    ia._add(a, cq.Workplane("XY", origin=(mouth_x, mouth_y, shoulder))
            .circle(ia.BOTTLE_NECK_D / 2.0).workplane(offset=26.0)
            .circle(ia.BOTTLE_D / 2.0).loft(),
            "bottle-shoulder", ia.BOTTLE_PET)
    ia._add(a, ia._cyl(mouth_x, mouth_y, shoulder + 26.0, ia.BOTTLE_D, ia.BOTTLE_H),
            "bottle-body", ia.CONCENTRATE)
    ia._add(a, ia._cyl(mouth_x, mouth_y, shoulder + 26.0 + ia.BOTTLE_H, ia.BOTTLE_D * 0.62, 4.0),
            "bottle-base", ia.BOTTLE_PET)
    return a


def s_fill_ready():
    return _bottle(lift=55.0)


def s_fill_seated():
    return _bottle(lift=0.0)


# --- the pour ------------------------------------------------------------------------------

ABOVE_COUNTER = (
    "westbrass", "soda_faucet_tube", "tpu_o_ring", "flavor_tube_pos_x", "flavor_tube_neg_x",
    "lever", "above_counter_plate", "above_counter_gasket", "shell_base", "shell_tip",
    "faucet-display-cover", "faucet_display", "faucet_display_screen",
)
GLASS_D, GLASS_WALL, GLASS_H = 74.0, 3.0, 112.0
SODA_H = 96.0
STREAM_D = 4.0
SLAB_X, SLAB_Y = 300.0, 330.0


def _faucet(pressed: bool) -> cq.Assembly:
    fa = ca._load_faucet_module()
    faucet = fa.build_assembly()
    parts = ca._children_by_name(faucet)
    lever_rest, lever_pressed = ca._physical_levers(fa)
    a = cq.Assembly(name="pour-scene")
    for name in ABOVE_COUNTER:
        child = parts[name]
        obj = (lever_pressed if pressed else lever_rest) if name == "lever" else child.obj
        if name in {"westbrass", "flavor_tube_pos_x", "flavor_tube_neg_x"}:
            obj = ca._clip_z(obj, fa.countertop_top_z, 260.0)
        ca._add_child(a, child, obj=obj)

    # The counter under it, forward far enough to stand a glass under the spout.
    slab = (cq.Workplane("XY").workplane(offset=fa.countertop_bottom_z)
            .center(0.0, -SLAB_Y / 2.0 + 60.0)
            .box(SLAB_X, SLAB_Y, fa.countertop_thickness, centered=(True, True, False)))
    ia._add(a, slab, "countertop", ia.STONE)

    # The spout is under the display on the tip; the glass stands under the spout.
    bb = parts["faucet_display"].obj.val().BoundingBox() \
        if hasattr(parts["faucet_display"].obj, "val") else parts["faucet_display"].obj.BoundingBox()
    gx, gy = bb.center.x, bb.center.y
    exit_z = bb.zmin - 6.0
    glass = (cq.Workplane("XY", origin=(gx, gy, fa.countertop_top_z))
             .circle(GLASS_D / 2.0).extrude(GLASS_H)
             .faces(">Z").workplane().circle(GLASS_D / 2.0 - GLASS_WALL).cutBlind(-(GLASS_H - 5.0)))
    ia._add(a, glass, "glass", GLASS)
    if pressed:
        ia._add(a, ia._cyl(gx, gy, fa.countertop_top_z + 5.0, GLASS_D - 2.0 * GLASS_WALL - 0.5, SODA_H),
                "soda", SODA)
        stream_z0 = fa.countertop_top_z + 5.0 + SODA_H
        ia._add(a, ia._cyl(gx, gy, stream_z0, STREAM_D, exit_z - stream_z0), "stream", SODA)
    return a


def s_pour_ready():
    return _faucet(pressed=False)


def s_pour_pressed():
    return _faucet(pressed=True)


# --- the scenes ----------------------------------------------------------------------------

_RIG_CAM = dict(cam=(0.42, 1.0, 0.30), target=(-30.0, 0.0, -36.0), span=126.0)
# Well off the wall's own column, so the plug's stand-off from the face reads as a gap on the
# page rather than folding into the socket behind it.
_CORD_CAM = dict(cam=(-0.85, 1.0, 0.22),
                 target=(ia.C14_STATION[0] + 16.0, ia.REAR_FACE_Y + 12.0, ia.C14_STATION[1] + 2.0),
                 span=46.0)
_FILL_CAM = dict(cam=(0.55, -1.0, 1.05), target=(0.0, ia.HOPPER_MID[1], 418.0), span=152.0)
# High enough to see the soda's surface over the glass's near rim.
_POUR_CAM = dict(cam=(1.0, -1.15, 0.55), target=(0.0, -70.0, 116.0), span=150.0)

SCENES = {
    "cylinder-nut-ready": (s_cylinder_nut_ready, _RIG_CAM),
    "cylinder-nut-seated": (s_cylinder_nut_seated, _RIG_CAM),
    "gas-on": (s_gas_on, dict(cam=(0.42, 1.0, 0.30), target=(-58.0, 10.0, 16.0), span=70.0)),
    "power-cord-ready": (s_power_cord_ready, _CORD_CAM),
    "power-cord-home": (s_power_cord_home, _CORD_CAM),
    "fill-ready": (s_fill_ready, _FILL_CAM),
    "fill-seated": (s_fill_seated, _FILL_CAM),
    "pour-ready": (s_pour_ready, _POUR_CAM),
    "pour-pressed": (s_pour_pressed, _POUR_CAM),
}

#: Scenes standing on the machine's printed bodies: the flutes live in the payload beside the
#: STEP, so these carry that skin across.
FLUTED = frozenset({"power-cord-ready", "power-cord-home", "fill-ready", "fill-seated"})


def render(names: list[str]) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="qs-claude-art-", dir=OUT) as directory:
        work = Path(directory)
        jobs = []
        for name in names:
            build, pose = SCENES[name]
            step = work / f"{name}.step"
            fluted = name in FLUTED
            ca._export_colored(build(), step, mesh=fluted)
            if fluted:
                ia._graft_flutes(step)
            jobs.append({
                "step": str(step.relative_to(HARDWARE)),
                "out": str(ART / f"{name}.png"),
                "up": (0, 0, 1),
                "size": FRAME,
                "bg": "#ffffff",
                "trim": False,
                "solid": True,
                "ortho": True,
                "ground": False,
                "fog": False,
                "transparent": True,
                **pose,
            })
            print(f"  staged {name}")
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
        for job in jobs:
            out = Path(job["out"])
            ca._canonicalize_png(out)
            print(f"  -> art/{out.name} ({out.stat().st_size // 1024} KB)")


def main(argv: list[str]) -> int:
    if "--list" in argv:
        for name in SCENES:
            print(name)
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
