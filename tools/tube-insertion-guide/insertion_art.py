"""Manual CAD pictures for the tube insertion jig guide.

Printed shapes come from the fixture's own CadQuery module. The thimble and
faucet-lever identification views use the existing accepted source models.
Fasteners are catalogue-size proxies, poised along their insertion axes.

    tools/cad-venv/bin/python tools/tube-insertion-guide/insertion_art.py
    tools/cad-venv/bin/python tools/tube-insertion-guide/insertion_art.py --list

No build target invokes this script.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
HARDWARE = ROOT / "hardware"
FIXTURE = HARDWARE / "printed-parts" / "fixtures" / "tube-insertion"
GUIDE = HARDWARE / "tube-insertion-guide"
ART = GUIDE / "art"
OUT = GUIDE / "out"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"

for directory in (
    HARDWARE / "scripts",
    FIXTURE,
    HARDWARE / "printed-parts" / "faucet" / "tpu-o-ring",
    HARDWARE / "printed-parts" / "faucet" / "lever-replica",
    HARDWARE / "reference" / "touch-flo-faucet" / "westbrass-reference",
):
    sys.path.insert(0, str(directory))

from _cadq_export import _per_solid_color
from _material_base import M_PETGF_BLACK, M_STAINLESS, M_TPU_BLACK, step_safe
import lever_replica
import tpu_o_ring
import tube_insertion as jig
import westbrass_reference as donor

M_ACCENT = cq.Color(0.84, 0.25, 0.31)
M_BRASS = cq.Color(0.78, 0.60, 0.22)
M_GAUGE = cq.Color(0.23, 0.41, 0.68)
M_LLDPE = cq.Color(0.86, 0.88, 0.90)


class Scene:
    def __init__(self, build, *, cam=(0.9, -1.1, 0.8), target=None,
                 span=None, size="2200x1800", up=(0, 0, 1)):
        self.build, self.cam, self.target = build, cam, target
        self.span, self.size, self.up = span, size, up


def _scene(name):
    return cq.Assembly(name=f"{name}-scene")


def _add(assembly, shape, name, color=M_PETGF_BLACK, loc=None):
    assembly.add(shape, name=name, color=step_safe(color), loc=loc)


def _tube(length=70.0):
    return (cq.Workplane("XY")
            .circle(tpu_o_ring.lldpe_od / 2)
            .circle(tpu_o_ring.lldpe_id / 2)
            .extrude(length))


def _section(shape):
    """Open the front half of an axis-Z wet-path view."""
    cutter = (cq.Workplane("XY", origin=(0, -50, -10))
              .box(100, 100, 150, centered=(True, True, False)))
    return shape.cut(cutter)


def s_sleeved_tube():
    a = _scene("sleeved-tube")
    _add(a, _section(tpu_o_ring.build_o_ring()), "thimble-section", M_ACCENT)
    tube = _tube(35).translate((0, 0, tpu_o_ring.cap_thickness))
    _add(a, _section(tube), "tube-section", M_LLDPE)
    return a


def s_thimble_before():
    a = _scene("thimble-before")
    _add(a, tpu_o_ring.build_o_ring(), "thimble", M_ACCENT)
    _add(a, _tube(55).translate((0, 0, 32)), "tube", M_LLDPE)
    return a


@lru_cache(maxsize=2)
def _parts(print_frame=False):
    return jig.build_parts(print_frame=print_frame)


@lru_cache(maxsize=16)
def _placed(stroke=0.0, workpiece=False, hardware=False):
    return jig.build_assembly(stroke=stroke, include_workpiece=workpiece,
                              include_hardware=hardware)


def _parts_scene(names, accents=(), *, stroke=0.0, workpiece=False, hardware=False,
                 offsets=None):
    """Keep exactly the named source assembly components and their placements."""
    source = _placed(stroke, workpiece, hardware)
    a = _scene("assembly-detail")
    for name in names:
        item = source.objects[name]
        shape = item.obj
        if offsets and name in offsets:
            shape = shape.translate(offsets[name])
        color = M_ACCENT if name in accents else item.color
        if "nut" in name:
            color = M_BRASS
        if name == "lldpe-tube":
            color = M_LLDPE
        _add(a, shape, name, color, loc=item.loc)
    return a


def _whole(stroke=0.0, accents=(), *, workpiece=True):
    source = _placed(stroke, workpiece, True)
    names = [name for name, item in source.objects.items() if item.obj is not None]
    return _parts_scene(names, accents, stroke=stroke, workpiece=workpiece,
                        hardware=True)


def s_hero():
    return _whole(stroke=jig.PRESS_TRAVEL)


def s_levers():
    a = _scene("levers")
    _add(a, _parts(True)["press-lever"], "press-lever", M_ACCENT)
    accepted = lever_replica.build(printed=True).translate((55, 32, 12))
    _add(a, accepted, "accepted-faucet-lever", M_PETGF_BLACK)
    return a


def s_faucet_lever():
    a = _scene("faucet-lever")
    _add(a, lever_replica.build(printed=True), "accepted-faucet-lever", M_ACCENT)
    return a


def s_plate_base():
    a = _scene("plate-base")
    _add(a, _parts(True)["base"], "A-base")
    return a


def s_plate_rigid():
    a = _scene("plate-rigid")
    layout = json.loads((FIXTURE / "print-layout.json").read_text())
    plate = next(row for row in layout["plates"] if row["id"] == "rigid-parts-h2c")
    for row in plate["parts"]:
        name = row["source"].removeprefix("tube-insertion-").removesuffix("-print.stl")
        shape = _parts(True)[name]
        bb = shape.val().BoundingBox()
        x, y = row["offset_mm"]
        place = (x - (bb.xmin + bb.xmax) / 2,
                 y - (bb.ymin + bb.ymax) / 2, -bb.zmin)
        _add(a, shape.translate(place), name)
    return a


def s_plate_liners():
    a = _scene("plate-liners")
    shape = _parts(True)["liner"]
    bb = shape.val().BoundingBox()
    for n, x in enumerate((-20, 20)):
        shift = (x - (bb.xmin + bb.xmax) / 2,
                 -(bb.ymin + bb.ymax) / 2, -bb.zmin)
        _add(a, shape.translate(shift), f"F-liner-{n+1}", M_ACCENT)
    return a


def s_hardware():
    a = _scene("hardware")
    for i in range(3):
        _add(a, jig.bolt_shape(i * 16, 0, 5, 50), f"M5x50-{i+1}", M_STAINLESS)
        _add(a, jig.washer_shape(i * 30, 30, 0), f"washer-{i+1}", M_STAINLESS)
    for i in range(4):
        _add(a, jig.square_nut_shape(i * 16, 55, 0), f"square-nut-{i+1}", M_BRASS)
    return a


def s_clean_base():
    return s_plate_base()


def s_ram():
    return _parts_scene(("base", "ram"), ("ram",), offsets={"ram": (0, 0, 24)})


def s_lever():
    return _parts_scene(("base", "ram", "press-lever", "pivot-m5x50"),
                        ("press-lever", "pivot-m5x50"), hardware=True,
                        offsets={"press-lever": (0, 0, 18), "pivot-m5x50": (0, 0, -16)})


def s_pivot_nuts():
    return _parts_scene(("base", "ram", "press-lever", "pivot-m5x50", "pivot-washer",
                         "pivot-nut-1", "pivot-nut-2"),
                        ("pivot-washer",), hardware=True,
                        offsets={"pivot-washer": (0, 0, 12),
                                 "pivot-nut-1": (0, 0, 24), "pivot-nut-2": (0, 0, 30)})


def s_liners():
    a = _scene("liners")
    _add(a, jig.build_lower_jaw().translate((0, -42, 11)), "D-lower-jaw")
    _add(a, jig.build_upper_jaw().rotate((0, 0, 0), (1, 0, 0), 180)
         .translate((0, 42, 11)), "E-upper-jaw")
    x = jig.LINER_START_X
    for n, y in enumerate((-42, 42)):
        _add(a, jig.build_liner().translate((x, y, 17)), f"F-liner-{n+1}", M_ACCENT)
    return a


def s_jaws():
    return _parts_scene(("lower-jaw", "upper-jaw", "lower-liner", "upper-liner",
                         "clamp-front-m5x50", "clamp-rear-m5x50", "clamp-front-washer",
                         "clamp-rear-washer", "clamp-front-nut", "clamp-rear-nut"),
                        ("upper-jaw", "clamp-front-m5x50", "clamp-rear-m5x50"),
                        hardware=True,
                        offsets={"upper-jaw": (0, 0, 18), "upper-liner": (0, 0, 18),
                                 "clamp-front-m5x50": (0, 0, -16),
                                 "clamp-rear-m5x50": (0, 0, -16),
                                 "clamp-front-washer": (0, 0, 35),
                                 "clamp-rear-washer": (0, 0, 35),
                                 "clamp-front-nut": (0, 0, 43),
                                 "clamp-rear-nut": (0, 0, 43)})


def s_puck():
    a = _scene("puck")
    _add(a, jig.build_cap_support_puck(), "G-cap-support-puck", M_ACCENT)
    _add(a, tpu_o_ring.build_o_ring().translate((0, 0, jig.PUCK_H + 12)),
         "thimble", M_TPU_BLACK)
    return a


def s_empty_press():
    return _parts_scene(("base", "ram", "press-lever", "pivot-m5x50",
                         "pivot-washer", "pivot-nut-1", "pivot-nut-2"),
                        stroke=jig.PRESS_TRAVEL, hardware=True)


def s_secure_base():
    a = s_empty_press()
    _add(a, jig.block(0, 64, 62, 116, jig.BASE_H + 0.02, jig.BASE_H + 0.35),
         "palm-area-reference", M_GAUGE)
    return a


def s_depth():
    a = _scene("depth")
    shape = donor.build_valve_body()
    remove = (cq.Workplane("XY", origin=(-50, 0, -55))
              .box(100, 100, 150, centered=(True, True, False)))
    _add(a, shape.cut(remove), "donor-section", M_STAINLESS)
    # A slim depth-blade proxy reads from the mouth, below the raised arches.
    y = donor.port_center_x
    beam = jig.block(3, 6, y - 15, y + 15, donor.plateau_z, donor.plateau_z + 3)
    blade = jig.block(3.7, 4.4, y - 1.2, y + 1.2,
                      donor.plateau_z - donor.port_bore_depth, donor.plateau_z)
    _add(a, beam.union(blade), "depth-blade-reference", M_GAUGE)
    return a


def s_marks():
    a = _scene("marks")
    _add(a, _tube(58), "tube", M_LLDPE)
    for n, z in enumerate((17.9, 36.9)):
        mark = (cq.Workplane("XY", origin=(0, 0, z))
                .circle(tpu_o_ring.lldpe_od / 2 + 0.15)
                .circle(tpu_o_ring.lldpe_od / 2).extrude(0.6))
        _add(a, mark, f"witness-{n+1}", M_GAUGE)
    return a


def s_sleeve_fit():
    a = _scene("sleeve-fit")
    cap_z = jig.PUCK_H - jig.PUCK_CAP_RECESS_H
    _add(a, jig.build_cap_support_puck(), "puck")
    _add(a, tpu_o_ring.build_o_ring().translate((0, 0, cap_z)), "thimble", M_ACCENT)
    tube_end = cap_z + jig.SLEEVE_CAP_H + 5
    _add(a, _tube(130).translate((0, 0, tube_end)), "tube", M_LLDPE)
    # Turn the whole source clamp from X-axis to Z-axis for sleeve fitting.
    clamp = _placed(0.0, False, True)
    for name in ("lower-jaw", "upper-jaw", "lower-liner", "upper-liner",
                 "clamp-front-m5x50", "clamp-rear-m5x50", "clamp-front-washer",
                 "clamp-rear-washer", "clamp-front-nut", "clamp-rear-nut"):
        obj = clamp.objects[name].obj.translate((-jig.CLAMP_FINAL_X, -jig.TUBE_Y, -jig.TUBE_Z))
        obj = obj.rotate((0, 0, 0), (0, 1, 0), -90).translate((0, 0, 65))
        _add(a, obj, name, M_BRASS if "nut" in name else clamp.objects[name].color)
    return a


def s_grip_mark():
    names = ("lower-jaw", "upper-jaw", "lower-liner", "upper-liner",
             "clamp-front-m5x50", "clamp-rear-m5x50", "clamp-front-washer",
             "clamp-rear-washer", "clamp-front-nut", "clamp-rear-nut",
             "lldpe-tube", "tpu-sealing-thimble")
    a = _parts_scene(names, workpiece=True, hardware=True)
    # Picture a short tube so the datum joint stays large and readable.
    a.objects["lldpe-tube"].obj = jig.tube_shape(length=112)
    for n, x in enumerate((jig.DONOR_PORT_X, jig.CLAMP_FINAL_X)):
        mark = jig.cylinder_x(x, x + 0.7, jig.TUBE_Y, jig.TUBE_Z, jig.TUBE_OD / 2 + 0.15).cut(
            jig.cylinder_x(x - 1, x + 2, jig.TUBE_Y, jig.TUBE_Z, jig.TUBE_OD / 2))
        _add(a, mark, f"tube-mark-{n+1}", M_GAUGE)
    return a


def s_donor_in():
    a = s_empty_press()
    _add(a, jig.donor_shape().translate((0, 0, 24)), "donor", M_ACCENT)
    return a


def s_engage():
    return _whole(stroke=jig.PRESS_TRAVEL, accents=("lower-jaw", "upper-jaw"))


def s_press():
    return _whole(stroke=8, accents=("press-lever",))


def s_release():
    a = _whole(stroke=0, accents=("upper-jaw",))
    a.objects["upper-jaw"].obj = a.objects["upper-jaw"].obj.translate((0, 0, 18))
    a.objects["upper-liner"].obj = a.objects["upper-liner"].obj.translate((0, 0, 18))
    for name in ("clamp-front-nut", "clamp-rear-nut", "clamp-front-washer", "clamp-rear-washer"):
        a.objects[name].obj = a.objects[name].obj.translate((0, 0, 36))
    return a


def s_workpiece():
    a = _parts_scene(("touch-flo-donor", "lldpe-tube", "tpu-sealing-thimble"),
                     workpiece=True)
    a.objects["lldpe-tube"].obj = jig.tube_shape(length=100)
    return a


SCENES = {
    "hero": Scene(s_hero, cam=(0.35, -0.9, 1.15), size="2400x1700"),
    "levers": Scene(s_levers, cam=(0.3, -0.7, 1.2), size="2200x1700"),
    "faucet-lever": Scene(s_faucet_lever, cam=(0.65, -0.9, 0.7), size="1900x1300"),
    "plate-rigid": Scene(s_plate_rigid, cam=(0.4, -0.75, 1.2), size="2200x1800"),
    "plate-liners": Scene(s_plate_liners, cam=(-0.9, -1, 0.6), size="1900x1500"),
    "hardware": Scene(s_hardware, cam=(0.5, -0.8, 1), size="1900x1500"),
    "clean-base": Scene(s_clean_base, cam=(0.4, -0.8, 0.9), size="2200x1700"),
    "ram": Scene(s_ram, cam=(0.7, -0.95, 0.65), size="2200x1600"),
    "lever": Scene(s_lever, cam=(0.65, -0.9, 0.75), size="2200x1700"),
    "pivot-nuts": Scene(s_pivot_nuts, cam=(0.8, -0.9, 0.6),
                        target=(jig.PRESS_PIVOT_X, jig.PRESS_PIVOT_Y, 28), span=57,
                        size="1800x1800"),
    "liners": Scene(s_liners, cam=(0.55, -0.8, 0.8), size="1900x1600"),
    "jaws": Scene(s_jaws, cam=(0.65, -0.9, 0.7), span=75, size="1900x1800"),
    "puck": Scene(s_puck, cam=(0.6, -0.8, 0.9), span=42, size="1800x1600"),
    "secure-base": Scene(s_secure_base, cam=(0.4, -0.95, 1.1), size="2200x1700"),
    "depth": Scene(s_depth, cam=(-1, 0.2, 0.35), target=(0, 8.75, 32),
                    span=24, size="1800x1400"),
    "marks": Scene(s_marks, cam=(0.5, -0.9, 0.3), size="1600x1900"),
    "sleeve-fit": Scene(s_sleeve_fit, cam=(0.55, -0.9, 0.6), size="1900x1900"),
    "grip-mark": Scene(s_grip_mark, cam=(0.55, -0.9, 0.55), size="2200x1500"),
    "donor-in": Scene(s_donor_in, cam=(0.4, -0.95, 0.85), size="2200x1700"),
    "engage": Scene(s_engage, cam=(0.3, -0.9, 1), size="2200x1600"),
    "press": Scene(s_press, cam=(0.2, -0.95, 1), target=(94, 66, 30),
                    span=133, size="2200x1600"),
    "release": Scene(s_release, cam=(0.35, -0.9, 1), size="2200x1600"),
    "workpiece": Scene(s_workpiece, cam=(0.4, -1, 0.65), size="2100x1300"),
    "sleeved-tube": Scene(s_sleeved_tube, cam=(0.35, -1, 0.28), size="1500x1800"),
}


def render(names):
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="insertion-art-", dir=OUT) as directory:
        work = Path(directory)
        jobs = []
        for name in names:
            scene = SCENES[name]
            step = work / f"{name}.step"
            _per_solid_color(scene.build()).export(str(step))
            job = {
                "step": str(step.relative_to(HARDWARE)),
                "out": str(ART / f"{name}.png"),
                "cam": list(scene.cam), "up": list(scene.up), "size": scene.size,
                "bg": "#ffffff", "trim": True, "solid": True, "ortho": True,
                "ground": False, "fog": False, "transparent": True,
            }
            if scene.target is not None:
                job["target"] = list(scene.target)
            if scene.span is not None:
                job["span"] = scene.span
            jobs.append(job)
            print(f"staged {name}")
        subprocess.run(["node", str(RENDERER), "--jobs", "-"], cwd=ROOT,
                       input=json.dumps(jobs), text=True, check=True)
        for job in jobs:
            out = Path(job["out"])
            print(f"-> art/{out.name} ({out.stat().st_size // 1024} KB)")


def main(argv):
    if "--list" in argv:
        print("\n".join(SCENES))
        return 0
    names = [arg for arg in argv if not arg.startswith("-")] or list(SCENES)
    unknown = [name for name in names if name not in SCENES]
    if unknown:
        raise SystemExit(f"unknown scenes: {', '.join(unknown)}")
    render(names)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
