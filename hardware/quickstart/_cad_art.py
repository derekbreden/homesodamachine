"""Render the quick start's focused, customer-facing CAD pictures.

The production models carry more geometry than an instruction frame needs. This module keeps the
exact touched parts and makes three deliberate presentation cuts:

- the faucet's source lever is a union of rest + pressed states for collision checking, so the
  customer views reconstruct one physical state at a time from the same dimensions;
- invisible tube tails are clipped at the countertop for the user-side faucet views;
- the washer and nut are plain stand-ins because the donor hardware has no source CAD.

All generated STEP intermediates live in a temporary directory under ``hardware/`` so the browser
renderer can serve them. Only the final PNGs land in ``art/``.
"""

from __future__ import annotations

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import cadquery as cq
from PIL import Image


HERE = Path(__file__).resolve().parent
HARDWARE = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HARDWARE.parent
ART = HERE / "art"
OUT = HERE / "out"
RENDERER = ROOT / "tools" / "render" / "render-step-posed.js"
FAUCET_SOURCE = HARDWARE / "faucet-layout" / "faucet_assembly.py"
MACHINE_STEP = HARDWARE / "manifold-layout" / "enclosure-assembly.step"
MACHINE_MESH = HARDWARE / "manifold-layout" / "enclosure-assembly.step.mesh"

sys.path.insert(0, str(HARDWARE / "scripts"))
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
from _cadq_export import _per_solid_color, note_read, note_write  # noqa: E402


def _load_faucet_module():
    note_read(FAUCET_SOURCE)
    spec = importlib.util.spec_from_file_location("quickstart_faucet", FAUCET_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {FAUCET_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _export_colored(assembly: cq.Assembly, target: Path) -> Path:
    _per_solid_color(assembly).export(str(target))
    return target


def _clip_z(obj, z_min: float, z_max: float):
    clip = (
        cq.Workplane("XY")
        .workplane(offset=z_min)
        .box(600.0, 600.0, z_max - z_min, centered=(True, True, False))
    )
    if not hasattr(obj, "intersect"):
        obj = cq.Workplane("XY").newObject([obj])
    return obj.intersect(clip)


def _moved(obj, xyz):
    if hasattr(obj, "translate"):
        return obj.translate(xyz)
    return obj.moved(cq.Location(cq.Vector(*xyz)))


def _children_by_name(assembly: cq.Assembly):
    return {child.name: child for child in assembly.children}


def _add_child(out: cq.Assembly, child, *, name=None, obj=None, color=None):
    out.add(
        child.obj if obj is None else obj,
        name=name or child.name,
        color=child.color if color is None else color,
    )


def _physical_levers(fa):
    """Return the source-dimensioned physical rest and pressed levers separately."""
    cut_cylinder = (
        fa.WorldWorkplane(fa.xy_plane_z_up)
        .workplane(offset=fa.plateau_z + 1)
        .moveTo((0, +(fa.port_center_depth + 0.125)))
        .circle(fa.water_tube_r + 1)
        .extrude(50)
        .unwrap()
    )
    taper_plane = cq.Plane(origin=(0, 0, 0), xDir=(1, 0, 0), normal=(0, -1, 0))
    taper = (
        cq.Workplane(taper_plane)
        .workplane(offset=6)
        .moveTo(0, fa.plateau_z + 4.5)
        .rect(13, 8.5, centered=(True, False))
        .workplane(offset=36)
        .moveTo(0, fa.plateau_z + 10)
        .rect(13, 3, centered=(True, False))
        .loft(combine=True)
    )
    rest = (
        fa.WorldWorkplane(fa.xy_plane_z_up)
        .workplane(offset=fa.plateau_z + 1)
        .moveTo((0, +1.5))
        .rect(13, 15)
        .extrude(12)
        .unwrap()
        .union(taper)
        .cut(cut_cylinder)
    )
    pivot_a = (0, fa.lever_pivot_y, fa.lever_pivot_z)
    pivot_b = (1, fa.lever_pivot_y, fa.lever_pivot_z)
    pressed = rest.rotate(pivot_a, pivot_b, +fa.lever_press_angle_deg).cut(cut_cylinder)
    return rest, pressed


def _build_steps(work: Path) -> dict[str, Path]:
    fa = _load_faucet_module()
    faucet = fa.build_assembly()
    parts = _children_by_name(faucet)
    lever_rest, lever_pressed = _physical_levers(fa)

    head_names = (
        "valve_body",
        "water_dispense_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "lever",
        "mounting_plate",
        "mounting_gasket",
        "shell_bottom",
        "shell_middle",
        "shell_top",
        "faucet_display",
        "faucet_display_screen",
    )

    def head_with(lever, name):
        head = cq.Assembly(name=name)
        for part_name in head_names:
            child = parts[part_name]
            obj = lever if part_name == "lever" else child.obj
            if part_name in {"valve_body", "flavor_tube_pos_x", "flavor_tube_neg_x"}:
                obj = _clip_z(obj, fa.countertop_top_z, 260.0)
            _add_child(head, child, obj=obj)
        return head

    head_step = _export_colored(head_with(lever_rest, "faucet-user"), work / "faucet-user.step")
    pressed_step = _export_colored(
        head_with(lever_pressed, "faucet-user-pressed"), work / "faucet-user-pressed.step"
    )

    drop = cq.Assembly(name="faucet-mount-drop")
    lift = (0.0, 0.0, 64.0)
    drop_names = (
        "valve_body",
        "water_dispense_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "carb_supply_tube",
        "lever",
        "mounting_plate",
        "mounting_gasket",
        "shell_bottom",
        "shell_middle",
        "shell_top",
        "faucet_display",
        "faucet_display_screen",
    )
    for part_name in drop_names:
        child = parts[part_name]
        obj = lever_rest if part_name == "lever" else child.obj
        if part_name in {"flavor_tube_pos_x", "flavor_tube_neg_x", "carb_supply_tube"}:
            obj = _clip_z(obj, -125.0, 260.0)
        _add_child(drop, child, obj=_moved(obj, lift))
    _add_child(drop, parts["countertop"])
    drop_step = _export_colored(drop, work / "mount-drop.step")

    underside_names = (
        "valve_body",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "carb_supply_tube",
        "mounting_plate",
        "mounting_gasket",
        "countertop",
    )

    def add_underside(out: cq.Assembly):
        for part_name in underside_names:
            child = parts[part_name]
            obj = child.obj
            if part_name in {
                "valve_body",
                "flavor_tube_pos_x",
                "flavor_tube_neg_x",
                "carb_supply_tube",
            }:
                obj = _clip_z(obj, -92.0, fa.countertop_top_z)
            _add_child(out, child, obj=obj)

    # Sampling the exported solid confirms both plate channels open on +X. The loose plate starts
    # on -X so the mouths face the hanging shank/tubes and it installs by moving +X.
    plate_magenta = cq.Color(0.90, 0.08, 0.36, 1.0)
    slide = cq.Assembly(name="faucet-mount-slide-plate")
    add_underside(slide)
    _add_child(
        slide,
        parts["under_counter_plate"],
        obj=_moved(parts["under_counter_plate"].obj, (-38.0, 0.0, 0.0)),
        color=plate_magenta,
    )
    slide_step = _export_colored(slide, work / "mount-slide.step")

    tight = cq.Assembly(name="faucet-mount-tighten")
    add_underside(tight)
    _add_child(tight, parts["under_counter_plate"])
    washer = (
        cq.Workplane("XY")
        .workplane(offset=-39.024)
        .circle(12.0)
        .circle(6.1)
        .extrude(1.5)
    )
    nut = (
        cq.Workplane("XY")
        .workplane(offset=-47.024)
        .polygon(6, 22.0)
        .circle(6.1)
        .extrude(8.0)
    )
    tight.add(washer, name="washer-stand-in", color=cq.Color(0.72, 0.74, 0.76, 1.0))
    tight.add(nut, name="nut-stand-in", color=plate_magenta)
    tight_step = _export_colored(tight, work / "mount-tighten.step")

    return {
        "faucet-head": head_step,
        "faucet-head-pressed": pressed_step,
        "mount-drop": drop_step,
        "mount-slide": slide_step,
        "mount-tighten": tight_step,
    }


def _job(step: Path, out: str | Path, cam: tuple[float, float, float]) -> dict:
    target = Path(out)
    if not target.is_absolute():
        target = ART / target
    return {
        "step": str(step.relative_to(HARDWARE)),
        "out": str(target),
        "cam": cam,
        "up": (0, 0, 1),
        "size": "2400x2400",
        "bg": "#ffffff",
        "trim": True,
        "solid": True,
        "ortho": True,
    }


def _canonicalize_png(path: Path) -> None:
    """Write one byte-stable PNG, without host or wall-clock metadata."""
    with Image.open(path) as image:
        pixels = image.convert("RGBA")
        pixels.save(path, format="PNG", compress_level=9, optimize=False)


def _crop(source: str | Path, geometry: str, target: str | Path) -> None:
    magick = shutil.which("magick")
    if not magick:
        return
    source_path = Path(source)
    target_path = Path(target)
    if not source_path.is_absolute():
        source_path = ART / source_path
    if not target_path.is_absolute():
        target_path = ART / target_path
    subprocess.run(
        [
            magick,
            str(source_path),
            "-crop",
            geometry,
            "+repage",
            "-strip",
            str(target_path),
        ],
        check=True,
    )
    _canonicalize_png(target_path)
    note_write(target_path)


def _clear_connected_background(path: Path) -> None:
    """Remove only the white field connected to the picture edge.

    The posed renderer deliberately emits an opaque page.  Instruction layouts need the CAD
    object, not that rectangular page, but a global ``-transparent white`` would also erase real
    white parts such as the TAP collar.  Flood-filling alpha from a one-pixel white border clears
    only the connected background and leaves enclosed highlights and labels intact.
    """
    magick = shutil.which("magick")
    if not magick:
        raise RuntimeError("ImageMagick is required to clear CAD picture backgrounds")
    subprocess.run(
        [
            magick,
            str(path),
            "-bordercolor",
            "white",
            "-border",
            "1",
            "-alpha",
            "set",
            "-channel",
            "RGBA",
            "-fuzz",
            "3%",
            "-fill",
            "none",
            "-draw",
            "alpha 0,0 floodfill",
            "-shave",
            "1x1",
            "-strip",
            str(path),
        ],
        check=True,
    )
    _canonicalize_png(path)
    note_write(path)


def main() -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    note_read(RENDERER)
    note_read(MACHINE_STEP)
    note_read(MACHINE_MESH)
    with tempfile.TemporaryDirectory(prefix="quickstart-cad-", dir=OUT) as directory:
        work = Path(directory)
        steps = _build_steps(work)
        jobs = [
            _job(steps["faucet-head"], "faucet-head.png", (0.18, -1.0, 0.18)),
            _job(steps["faucet-head"], "faucet-side.png", (1.0, -1.4, 0.75)),
            _job(steps["faucet-head-pressed"], "faucet-side-pressed.png", (1.0, -1.4, 0.75)),
            _job(steps["mount-drop"], "mount-drop.png", (1.0, -1.35, 0.72)),
            _job(steps["mount-slide"], "mount-slide.png", (1.0, -1.3, -0.8)),
            _job(steps["mount-tighten"], "mount-tighten.png", (1.0, -1.3, -0.8)),
            _job(MACHINE_STEP, "machine-front.png", (1.0, -1.25, 0.72)),
            _job(MACHINE_STEP, work / "machine-back.png", (0.12, 1.0, 0.32)),
            _job(MACHINE_STEP, "machine-back-iso.png", (1.0, 1.0, 1.0)),
        ]
        subprocess.run(
            ["node", str(RENDERER), "--jobs", "-"],
            cwd=ROOT,
            input=json.dumps(jobs),
            text=True,
            check=True,
        )
        for job in jobs:
            output = Path(job["out"])
            _clear_connected_background(output)
            note_write(output)

        _crop("machine-front.png", "960x660+0+100", "machine-hopper-close.png")
        _crop(work / "machine-back.png", "720x560+180+300", "machine-back-close.png")


if __name__ == "__main__":
    main()
