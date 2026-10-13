"""Manual CAD pictures for the tube insertion jig guide.

Printed shapes come from the fixture's own CadQuery module. The thimble and
faucet-lever identification views use the existing accepted source models.
The complete factory clamps are nominal catalogue-form illustrations, not
measured manufacturer profiles. Stock fasteners are size proxies.

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
                              include_hardware=hardware, include_clamps=False)


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


def _add_clamps(assembly, stroke=0.0, *, accents=(), pad_backoff=0.0,
                contact_color=None):
    """Keep both complete factory schematics, including their steel returns."""
    for side, label in ((-1, "C1"), (1, "C2")):
        source = jig.build_clamp_reference(side, stroke)
        for item in source.children:
            name = f"{label}-{item.name}"
            shape = item.obj
            if pad_backoff and item.name in ("moving-pad-envelope",
                                             "spindle-schematic", "wood-handle-envelope"):
                shape = shape.translate((pad_backoff, 0, 0))
            color = M_ACCENT if item.name in accents else item.color
            if contact_color and item.name in ("fixed-pad-envelope", "moving-pad-envelope"):
                color = contact_color
            _add(assembly, shape, name, color, loc=item.loc)


GRIP_NAMES = ("carrier", "lower-jaw", "upper-jaw", "lower-liner", "upper-liner",
              "clamp-front-m5x50", "clamp-rear-m5x50", "clamp-front-washer",
              "clamp-rear-washer", "clamp-front-nut", "clamp-rear-nut",
              "carrier-front-m5x20", "carrier-rear-m5x20",
              "carrier-front-nut", "carrier-rear-nut")


def _whole(stroke=0.0, accents=(), *, workpiece=True, clamps=True,
           tube_length=330.0, clamp_accents=(), pad_backoff=0.0):
    source = _placed(stroke, workpiece, True)
    names = [name for name, item in source.objects.items() if item.obj is not None]
    a = _parts_scene(names, accents, stroke=stroke, workpiece=workpiece, hardware=True)
    if workpiece:
        a.objects["lldpe-tube"].obj = jig.tube_shape(stroke=stroke, length=tube_length)
    if clamps:
        _add_clamps(a, stroke, accents=clamp_accents, pad_backoff=pad_backoff)
    return a


def _arrow_left(x, y, z, length=24.0):
    """A blue direction annotation; arrow length does not encode force."""
    return (cq.Workplane("XY", origin=(x, y, z))
            .polyline(((0, 0), (8, 5), (8, 2), (length, 2),
                       (length, -2), (8, -2), (8, -5))).close().extrude(0.4))


def _label(assembly, value, x, y, z, size=10):
    letters = cq.Workplane("XY", origin=(x, y, z)).text(
        value, size, 0.3, font="Helvetica", halign="center", valign="center",
        combine=False)
    _add(assembly, letters, f"label-{value}", M_GAUGE)


def s_hero():
    return _whole(stroke=jig.PRESS_TRAVEL)


def s_load_path():
    a = _whole(stroke=10, clamps=False, accents=("lower-jaw", "upper-jaw"))
    _add_clamps(a, 10, contact_color=M_GAUGE)
    tube_bb = a.objects["lldpe-tube"].obj.val().BoundingBox()
    _add(a, jig.block(jig.DONOR_PORT_X, tube_bb.xmax, jig.TUBE_Y - 0.22,
                       jig.TUBE_Y + 0.22, 59, 59.25), "tube-axis-reference", M_GAUGE)
    for station in jig.clamp_stations(10):
        x, y, _ = station["moving_center_mm"]
        _add(a, _arrow_left(x + 15, y, 58), f"{station['name']}-advance", M_GAUGE)
        side = station["side"]
        _label(a, station["name"], 30, y + side * (jig.FACTORY_CLAMP_THROAT + 12), 42)
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
    for n, x in enumerate((-5, 5)):
        shift = (x - (bb.xmin + bb.xmax) / 2,
                 -(bb.ymin + bb.ymax) / 2, -bb.zmin)
        _add(a, shape.translate(shift), f"F-liner-{n+1}", M_ACCENT)
    return a


def s_hardware():
    a = _scene("hardware")
    _add_clamps(a)
    for i in range(2):
        _add(a, jig.bolt_shape(-3 + i * 23, -4, 5, 50), f"M5x50-{i+1}", M_STAINLESS)
        _add(a, jig.countersunk_bolt_shape(48 + i * 20, -4, 0, 20),
             f"M5x20-countersunk-{i+1}", M_STAINLESS)
        _add(a, jig.washer_shape(12 + i * 33, 28, 0), f"washer-{i+1}", M_STAINLESS)
    for i in range(4):
        _add(a, jig.square_nut_shape(-4 + i * 18, 52, 0), f"square-nut-{i+1}", M_BRASS)
    return a


def s_clean_base():
    a = s_plate_base()
    for station in jig.clamp_stations():
        x, y, z = station["fixed_center_mm"]
        dot = jig.cylinder_x(x - 0.25, x - 0.02, y, z, 1.8)
        _add(a, dot, f"{station['name']}-fixed-centre-ink", M_GAUGE)
    return a


def s_carrier_joint():
    return _parts_scene(("carrier", "lower-jaw", "lower-liner",
                         "carrier-front-m5x20", "carrier-rear-m5x20",
                         "carrier-front-nut", "carrier-rear-nut"),
                        ("carrier-front-m5x20", "carrier-rear-m5x20"), hardware=True,
                        offsets={"lower-jaw": (0, 0, 28), "lower-liner": (0, 0, 28),
                                 "carrier-front-m5x20": (0, 0, -16),
                                 "carrier-rear-m5x20": (0, 0, -16),
                                 "carrier-front-nut": (0, -16, 28),
                                 "carrier-rear-nut": (0, 16, 28)})


def s_carrier():
    offsets = {name: (0, 0, 34) for name in GRIP_NAMES}
    return _parts_scene(("base",) + GRIP_NAMES, ("carrier",), hardware=True,
                        offsets=offsets)


def s_liners():
    a = _scene("liners")
    _add(a, _parts(True)["lower-jaw"].translate((0, -62, 0)), "D-lower-jaw")
    _add(a, _parts(True)["upper-jaw"].translate((0, 62, 0)), "E-upper-jaw")
    x = jig.LINER_START_X
    for n, y in enumerate((-62, 62)):
        _add(a, jig.build_liner().translate((x, y, jig.JAW_HALF_H - jig.LINER_H + 18)),
             f"F-liner-{n+1}", M_ACCENT)
    return a


def s_jaws():
    return _parts_scene(GRIP_NAMES,
                        ("upper-jaw", "clamp-front-m5x50", "clamp-rear-m5x50"),
                        hardware=True,
                        offsets={"upper-jaw": (0, 0, 28), "upper-liner": (0, 0, 28),
                                 "clamp-front-m5x50": (0, 0, -18),
                                 "clamp-rear-m5x50": (0, 0, -18),
                                 "clamp-front-washer": (0, 0, 40),
                                 "clamp-rear-washer": (0, 0, 40),
                                 "clamp-front-nut": (0, 0, 49),
                                 "clamp-rear-nut": (0, 0, 49)})


def s_puck():
    a = _scene("puck")
    _add(a, jig.build_cap_support_puck(), "G-cap-support-puck", M_ACCENT)
    _add(a, tpu_o_ring.build_o_ring().translate((0, 0, jig.PUCK_H + 12)),
         "thimble", M_TPU_BLACK)
    return a


def s_preset_travel():
    a = _whole(stroke=jig.PRESS_TRAVEL, workpiece=False,
               clamp_accents=("spindle-schematic", "wood-handle-envelope"))
    for station in jig.clamp_stations(jig.PRESS_TRAVEL):
        x, y, _ = station["moving_center_mm"]
        _add(a, _arrow_left(x - jig.PRESS_TRAVEL, y, 57, jig.PRESS_TRAVEL),
             f"{station['name']}-travel-direction", M_GAUGE)
    return a


def s_handles_clear():
    a = _whole(stroke=jig.PRESS_TRAVEL,
               clamp_accents=("wood-handle-envelope",))
    for n, (x, y) in enumerate(((12.0, 112.0), (170.0, 112.0))):
        ring = (cq.Workplane("XY", origin=(x, y, jig.BASE_H + 0.05))
                .circle(7).circle(3).extrude(0.3))
        _add(a, ring, f"mounting-location-{n+1}", M_GAUGE)
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
    witness = jig.DONOR_PORT_DEPTH_MIN - jig.SLEEVE_CAP_H
    grip_mark = witness + jig.CLAMP_FINAL_X - jig.DONOR_PORT_X
    for n, z in enumerate((witness, grip_mark)):
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
    # The grip and its bolted carrier stay together during sleeve fitting.
    clamp = _placed(0.0, False, True)
    for name in GRIP_NAMES:
        obj = clamp.objects[name].obj.translate((-jig.CLAMP_FINAL_X, -jig.TUBE_Y, -jig.TUBE_Z))
        obj = obj.rotate((0, 0, 0), (0, 1, 0), -90).translate((0, 0, 65))
        _add(a, obj, name, M_BRASS if "nut" in name else clamp.objects[name].color)
    return a


def s_grip_mark():
    names = GRIP_NAMES + ("lldpe-tube", "tpu-sealing-thimble")
    a = _parts_scene(names, workpiece=True, hardware=True)
    # Picture a short tube so the datum joint stays large and readable.
    a.objects["lldpe-tube"].obj = jig.tube_shape(length=220)
    for n, x in enumerate((jig.DONOR_PORT_X, jig.CLAMP_FINAL_X)):
        mark = jig.cylinder_x(x, x + 0.7, jig.TUBE_Y, jig.TUBE_Z, jig.TUBE_OD / 2 + 0.15).cut(
            jig.cylinder_x(x - 1, x + 2, jig.TUBE_Y, jig.TUBE_Z, jig.TUBE_OD / 2))
        _add(a, mark, f"tube-mark-{n+1}", M_GAUGE)
    for station in jig.clamp_stations():
        x, y, z = station["moving_center_mm"]
        _add(a, jig.cylinder_x(x + 0.02, x + 0.25, y, z, 1.8),
             f"{station['name']}-moving-centre-ink", M_GAUGE)
    return a


def s_donor_in():
    a = _parts_scene(("base",))
    _add(a, jig.donor_shape().translate((0, 0, 24)), "donor", M_ACCENT)
    return a


def s_engage():
    return _whole(stroke=jig.PRESS_TRAVEL, accents=("lower-jaw", "upper-jaw"))


def s_press():
    return _whole(stroke=8,
                   clamp_accents=("spindle-schematic", "wood-handle-envelope",
                                  "moving-pad-envelope"))


def s_release():
    a = _whole(stroke=0, accents=("upper-jaw",), pad_backoff=6)
    a.objects["upper-jaw"].obj = a.objects["upper-jaw"].obj.translate((0, 0, 28))
    a.objects["upper-liner"].obj = a.objects["upper-liner"].obj.translate((0, 0, 28))
    for name in ("clamp-front-nut", "clamp-rear-nut", "clamp-front-washer", "clamp-rear-washer"):
        a.objects[name].obj = a.objects[name].obj.translate((0, 0, 49))
    # Both complete clamps have been unloaded and lifted away before E opens.
    for name, item in a.objects.items():
        if name.startswith(("C1-", "C2-")):
            side = -1 if name.startswith("C1-") else 1
            item.obj = item.obj.translate((0, side * 12, 40))
    return a


def s_workpiece():
    a = _parts_scene(("touch-flo-donor", "lldpe-tube", "tpu-sealing-thimble"),
                     workpiece=True)
    a.objects["lldpe-tube"].obj = jig.tube_shape(length=100)
    return a


SCENES = {
    "hero": Scene(s_hero, cam=(0.25, -0.85, 1.15), size="2400x1700"),
    "load-path": Scene(s_load_path, cam=(0, 0, 1), up=(0, 1, 0), size="2400x1650"),
    "faucet-lever": Scene(s_faucet_lever, cam=(0.65, -0.9, 0.7), size="1900x1300"),
    "plate-rigid": Scene(s_plate_rigid, cam=(0.4, -0.75, 1.2), size="2200x1800"),
    "plate-liners": Scene(s_plate_liners, cam=(-0.9, -1, 0.6), size="1900x1500"),
    "hardware": Scene(s_hardware, cam=(0.3, -0.8, 1.2), size="2200x1700"),
    "clean-base": Scene(s_clean_base, cam=(-0.7, -0.85, 0.9), size="2200x1700"),
    "carrier-joint": Scene(s_carrier_joint, cam=(0.6, -0.9, 0.7), size="2200x1800"),
    "carrier": Scene(s_carrier, cam=(0.45, -0.85, 0.9), size="2200x1700"),
    "liners": Scene(s_liners, cam=(0.55, -0.8, 0.8), size="1900x1600"),
    "jaws": Scene(s_jaws, cam=(0.65, -0.9, 0.7), size="2200x1800"),
    "puck": Scene(s_puck, cam=(0.6, -0.8, 0.9), span=42, size="1800x1600"),
    "preset-travel": Scene(s_preset_travel, cam=(0.25, -0.85, 1.2), size="2200x1700"),
    "handles-clear": Scene(s_handles_clear, cam=(0.15, -0.8, 1.35), size="2200x1700"),
    "depth": Scene(s_depth, cam=(-1, 0.2, 0.35), target=(0, 8.75, 32),
                    span=24, size="1800x1400"),
    "marks": Scene(s_marks, cam=(0.5, -0.9, 0.3), size="1600x1900"),
    "sleeve-fit": Scene(s_sleeve_fit, cam=(-0.65, -0.85, 0.45), size="1900x1900"),
    "grip-mark": Scene(s_grip_mark, cam=(0.55, -0.9, 0.55), size="2200x1500"),
    "donor-in": Scene(s_donor_in, cam=(0.4, -0.95, 0.85), size="2200x1700"),
    "engage": Scene(s_engage, cam=(0.3, -0.9, 1), size="2200x1600"),
    "press": Scene(s_press, cam=(0.2, -0.8, 1.15), size="2200x1700"),
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
    if set(names) == set(SCENES):
        for stale in ART.glob("*.png"):
            if stale.stem not in SCENES:
                stale.unlink()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
