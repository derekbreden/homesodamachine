"""Render the quick start's focused, customer-facing CAD pictures.

The production models carry more geometry than an instruction frame needs. This module keeps the
exact touched parts and makes four deliberate presentation cuts:

- the faucet's source lever is a union of rest + pressed states for collision checking, so the
  customer views reconstruct one physical state at a time from the same dimensions;
- invisible tube tails are clipped at the countertop for the user-side faucet views;
- the mount sequence keeps the recognizable full faucet for the lowering event, then changes once
  to a fixed, literal below-counter camera for the plate and retained-nut actions;
- the retained donor washer and nut are plain visual stand-ins because the purchased hardware has
  no source CAD. Their family installation geometry is shown without using them as dimensional
  authority.

All generated STEP intermediates live in a temporary directory under ``hardware/`` so the browser
renderer can serve them. Only the final PNGs land in ``art/``.

``--mount-studies`` renders only the registered mount frames into ``out/mount-studies/`` for fast
visual review without touching the checked-in artwork.
"""

from __future__ import annotations

import importlib.util
import json
import math
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
MOUNT_CAM = (1.0, -1.45, -0.38)
MOUNT_TARGET = (0.0, 0.0, 110.0)
MOUNT_FRAME_SHAVE = 18
MOUNT_FRAME_TRIM_TOP = 200
MOUNT_FRAME_TRIM_BOTTOM = 40
UNDER_MOUNT_CAM = (0.58, -1.60, -0.72)
UNDER_MOUNT_TARGET = (0.0, 5.0, -45.0)
UNDER_MOUNT_FRAME_SHAVE = 18

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

    # This full, direct-front assembly is an intermediate for the exact rear-wall tail crop. The
    # lever is outside that crop; every pictured tube, sleeve and word collar comes from source CAD.
    faucet_full_step = _export_colored(faucet, work / "faucet-full.step")

    # The lowering event needs one cutaway view that keeps the recognizable faucet, countertop,
    # shank and tails together. The two securing frames below deliberately use the intact source
    # countertop from the installer’s below-counter viewpoint instead.
    section_cutter = (
        cq.Workplane("XY")
        .workplane(offset=-130.0)
        .box(180.0, 180.0, 260.0, centered=(True, True, False))
        .translate((0.0, fa.countertop_hole_center_y - 90.0, 0.0))
    )
    countertop_section = parts["countertop"].obj.cut(section_cutter)

    mount_names = (
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
    mount_tails = {"flavor_tube_pos_x", "flavor_tube_neg_x", "carb_supply_tube"}
    mount_clip = (-88.0, 380.0)
    washer_thickness = 1.5
    nut_height = 5.0
    # Until the plate is in, the pair hangs on the shank's last thread. A 50 mm shank through a
    # 30 mm slab leaves 14 mm of shank below the counter, and everything above the washer there
    # is the gap the open plate slides through — so the pair is drawn at the bottom of it.
    captive_washer_top_z = -fa.shank_length + nut_height + washer_thickness
    final_washer_top_z = fa.countertop_bottom_z - fa.under_counter_plate_thickness
    plate_steel = cq.Color(0.72, 0.74, 0.76, 1.0)
    washer_steel = cq.Color(0.82, 0.83, 0.84, 1.0)
    nut_steel = cq.Color(0.43, 0.45, 0.48, 1.0)
    countertop_stone = cq.Color(0.55, 0.55, 0.58, 1.0)
    # Both flavor lines are physically black. Instruction-lighting tones keep their tangent round
    # bodies countable at print size; the much lighter flat SIG-6 remains a different silhouette.
    flavor_black_a = cq.Color(0.025, 0.027, 0.031, 1.0)
    flavor_black_b = cq.Color(0.20, 0.205, 0.215, 1.0)
    signal_gray = cq.Color(0.55, 0.56, 0.59, 1.0)
    signal_stripe_gray = cq.Color(0.30, 0.31, 0.34, 1.0)
    motion_red = cq.Color(0.83, 0.19, 0.16, 1.0)
    frame_anchor_color = cq.Color(0.95, 0.04, 0.82, 1.0)

    def donor_hardware(washer_top_z: float):
        """Approximate the retained donor washer + nut as one always-present pair.

        The broad washer over a low hex nut follows the Westbrass Touch-Flo family installation
        drawing. The purchased pair remains the fit authority; these solids carry only identity,
        ordering and motion into the instruction frame.
        """
        washer_bottom_z = washer_top_z - washer_thickness
        washer = (
            cq.Workplane("XY")
            .workplane(offset=washer_bottom_z)
            .circle(12.0)
            .circle(6.1)
            .extrude(washer_thickness)
        )
        nut = (
            cq.Workplane("XY")
            .workplane(offset=washer_bottom_z - nut_height)
            .polygon(6, 22.0)
            .circle(6.1)
            .extrude(nut_height)
        )
        return washer, nut

    def signal_ribbon(lift_z: float):
        """A short, flat identity segment of the fitted SIG-6 harness below the slab.

        Its installed physical assembly is the route authority. The picture stops the segment at
        the underside stack instead of manufacturing a hidden path through the faucet shell. Three
        quiet face stripes survive grayscale reduction and distinguish this flat harness from the
        adjacent round flavor lines; they are an illustration texture, not conductor geometry.
        """
        ribbon_bottom_z = -123.0 + lift_z
        ribbon_length = 84.8
        ribbon_turn = -144.5
        ribbon_move = (9.0, 10.5, 0.0)
        ribbon = (
            cq.Workplane("XY")
            .workplane(offset=ribbon_bottom_z)
            .rect(4.8, 1.2)
            .extrude(ribbon_length)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), ribbon_turn)
            .translate(ribbon_move)
        )
        stripes = (
            cq.Workplane("XY")
            .workplane(offset=ribbon_bottom_z)
            .pushPoints([(-1.25, 0.635), (0.0, 0.635), (1.25, 0.635)])
            .rect(0.24, 0.08)
            .extrude(ribbon_length)
            .rotate((0.0, 0.0, 0.0), (0.0, 0.0, 1.0), ribbon_turn)
            .translate(ribbon_move)
        )
        return _clip_z(ribbon, *mount_clip), _clip_z(stripes, *mount_clip)

    def motion_arrow(start, direction, shaft_length: float, head_length: float):
        """One solid instruction arrow, outside the product geometry."""
        start_v = cq.Vector(*start)
        direction_v = cq.Vector(*direction)
        direction_v = direction_v.multiply(1.0 / direction_v.Length)
        head_start = start_v.add(direction_v.multiply(shaft_length))
        shaft = cq.Solid.makeCylinder(1.7, shaft_length, start_v, direction_v)
        head = cq.Solid.makeCone(4.5, 0.25, head_length, head_start, direction_v)
        return cq.Compound.makeCompound([shaft, head])

    def rotation_arrow(center, radius: float, start_angle: float, end_angle: float):
        """A circular hand-motion cue around the nut's Z axis."""
        center_v = cq.Vector(*center)
        path = cq.Edge.makeCircle(
            radius,
            center_v,
            (0.0, 0.0, 1.0),
            start_angle,
            end_angle,
        )
        start = path.startPoint()
        end = path.endPoint()
        tangent = cq.Vector(
            -math.sin(math.radians(end_angle)),
            math.cos(math.radians(end_angle)),
            0.0,
        )
        profile = cq.Wire.makeCircle(1.7, start, tangent)
        shaft = cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=True)
        head = cq.Solid.makeCone(4.5, 0.25, 7.0, end, tangent)
        return cq.Compound.makeCompound([shaft, head])

    def add_render_frame(out: cq.Assembly):
        """Give every mount state one identical orthographic frame.

        ``render-step-posed`` fits an orthographic camera from each subject's bounding box. Four
        small anchors at the corners of the camera plane make that box, target, scale and horizon
        identical across the sequence. They are shaved off the rendered PNG before it is used.
        """
        view = cq.Vector(*MOUNT_CAM)
        view = view.multiply(1.0 / view.Length)
        world_up = cq.Vector(0.0, 0.0, 1.0)
        right = view.cross(world_up)
        right = right.multiply(1.0 / right.Length)
        screen_up = right.cross(view)
        screen_up = screen_up.multiply(1.0 / screen_up.Length)
        target = cq.Vector(*MOUNT_TARGET)
        for index, (across, rise) in enumerate(
            ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)),
            start=1,
        ):
            point = target.add(right.multiply(across * 118.0)).add(
                screen_up.multiply(rise * 235.0)
            )
            anchor = (
                cq.Workplane("XY")
                .workplane(offset=point.z - 0.75)
                .center(point.x, point.y)
                .box(1.5, 1.5, 1.5, centered=(True, True, False))
            )
            out.add(anchor, name=f"render-frame-anchor-{index}", color=frame_anchor_color)

    def add_under_render_frame(out: cq.Assembly):
        """Lock both below-counter actions to one deliberately wide installer camera."""
        view = cq.Vector(*UNDER_MOUNT_CAM)
        view = view.multiply(1.0 / view.Length)
        world_up = cq.Vector(0.0, 0.0, 1.0)
        right = view.cross(world_up)
        right = right.multiply(1.0 / right.Length)
        screen_up = right.cross(view)
        screen_up = screen_up.multiply(1.0 / screen_up.Length)
        target = cq.Vector(*UNDER_MOUNT_TARGET)
        for index, (across, rise) in enumerate(
            ((-1.0, -1.0), (-1.0, 1.0), (1.0, -1.0), (1.0, 1.0)),
            start=1,
        ):
            point = target.add(right.multiply(across * 190.0)).add(
                screen_up.multiply(rise * 76.0)
            )
            anchor = (
                cq.Workplane("XY")
                .workplane(offset=point.z - 0.75)
                .center(point.x, point.y)
                .box(1.5, 1.5, 1.5, centered=(True, True, False))
            )
            out.add(
                anchor,
                name=f"under-render-frame-anchor-{index}",
                color=frame_anchor_color,
            )

    def add_mount_product(
        out: cq.Assembly,
        lift_z: float,
        *,
        washer_top_z: float | None = None,
    ):
        move = (0.0, 0.0, lift_z)
        for part_name in mount_names:
            child = parts[part_name]
            obj = lever_rest if part_name == "lever" else child.obj
            obj = _moved(obj, move)
            if part_name in mount_tails:
                obj = _clip_z(obj, *mount_clip)
            color = {
                "flavor_tube_pos_x": flavor_black_a,
                "flavor_tube_neg_x": flavor_black_b,
            }.get(part_name)
            _add_child(out, child, obj=obj, color=color)
        ribbon, ribbon_stripes = signal_ribbon(lift_z)
        out.add(ribbon, name="sig6-flat-ribbon", color=signal_gray)
        out.add(ribbon_stripes, name="sig6-ribbon-face-stripes", color=signal_stripe_gray)
        if washer_top_z is None:
            washer_top_z = captive_washer_top_z + lift_z
        washer, nut = donor_hardware(washer_top_z)
        out.add(washer, name="retained-donor-washer", color=washer_steel)
        out.add(nut, name="retained-donor-nut", color=nut_steel)

    def add_countertop_section(out: cq.Assembly):
        _add_child(out, parts["countertop"], obj=countertop_section)

    def add_under_countertop(out: cq.Assembly):
        """Keep the complete source slab intact for the view the installer actually sees."""
        _add_child(out, parts["countertop"], color=countertop_stone)

    def add_under_mount_product(out: cq.Assembly, *, washer_top_z: float):
        """Show only the real shank, three attached tubes and captive donor pair below the slab."""
        under_clip = (-112.0, -2.0)
        for part_name in (
            "valve_body",
            "flavor_tube_pos_x",
            "flavor_tube_neg_x",
            "carb_supply_tube",
        ):
            child = parts[part_name]
            color = {
                "flavor_tube_pos_x": flavor_black_a,
                "flavor_tube_neg_x": flavor_black_b,
            }.get(part_name)
            _add_child(
                out,
                child,
                name=f"under-{part_name}",
                obj=_clip_z(child.obj, *under_clip),
                color=color,
            )
        washer, nut = donor_hardware(washer_top_z)
        out.add(washer, name="under-retained-donor-washer", color=washer_steel)
        out.add(nut, name="under-retained-donor-nut", color=nut_steel)

    # 1 — received factory state. The donor pair was loaded onto the bare shank before the blue
    # connection was made; this connected assembly makes that captive ordering visible above the
    # prepared opening. None of the field frames ever presents either item loose.
    factory = cq.Assembly(name="faucet-mount-factory-captive")
    add_countertop_section(factory)
    add_mount_product(factory, 35.0)
    add_render_frame(factory)
    drop_step = _export_colored(factory, work / "mount-drop.step")

    # 2 — the same complete assembly is down and seated. Camera, countertop section, hardware and
    # tail ordering are unchanged; only the product's vertical position changes.
    lowered = cq.Assembly(name="faucet-mount-lowered")
    add_countertop_section(lowered)
    add_mount_product(lowered, 0.0)
    add_render_frame(lowered)
    lowered_clean_step = _export_colored(lowered, work / "mount-lowered-clean.step")
    lowered.add(
        motion_arrow((-31.0, -23.0, 38.0), (0.0, 0.0, -1.0), 19.0, 8.0),
        name="lower-motion",
        color=motion_red,
    )
    seated_step = _export_colored(lowered, work / "mount-seated.step")

    # 3 — the exact source plate approaches from -X. Sampling the exported solid confirms both
    # channel mouths open on +X, toward the fixed shank and tube pair. Its Z is already above the
    # captive washer: the installer moves the plate only laterally.
    slide = cq.Assembly(name="faucet-mount-slide-plate")
    add_countertop_section(slide)
    add_mount_product(slide, 0.0)
    _add_child(
        slide,
        parts["under_counter_plate"],
        obj=_moved(parts["under_counter_plate"].obj, (-36.0, 0.0, 0.0)),
        color=plate_steel,
    )
    add_render_frame(slide)
    slide_clean_step = _export_colored(slide, work / "mount-slide-clean.step")
    slide.add(
        motion_arrow((-61.0, -23.0, -29.0), (1.0, 0.0, 0.0), 28.0, 8.0),
        name="slide-motion",
        color=motion_red,
    )
    slide_step = _export_colored(slide, work / "mount-slide.step")

    # 4 — plate seated, same pair closed against it. The circular cue asks for hand rotation without
    # hiding the zero-gap result behind an approximate CAD hand or implying upward force.
    tight = cq.Assembly(name="faucet-mount-tighten")
    add_countertop_section(tight)
    add_mount_product(tight, 0.0, washer_top_z=final_washer_top_z)
    _add_child(tight, parts["under_counter_plate"], color=plate_steel)
    add_render_frame(tight)
    final_clean_step = _export_colored(tight, work / "mount-final-clean.step")
    tight.add(
        rotation_arrow((0.0, 0.0, -51.0), 18.0, 70.0, 280.0),
        name="tighten-rotation",
        color=motion_red,
    )
    tight_step = _export_colored(tight, work / "mount-tighten.step")

    # 3A — once the faucet is seated, the installer is below the intact counter. The light steel
    # plate is the actual source DXF solid, still displaced at -X; its two open channels face the
    # attached shank/tube stack. The only red is its literal lateral movement.
    under_slide = cq.Assembly(name="faucet-mount-under-slide")
    add_under_countertop(under_slide)
    add_under_mount_product(under_slide, washer_top_z=captive_washer_top_z)
    _add_child(
        under_slide,
        parts["under_counter_plate"],
        name="under-open-plate",
        obj=_moved(parts["under_counter_plate"].obj, (-36.0, 0.0, 0.0)),
        color=plate_steel,
    )
    under_slide.add(
        motion_arrow((-62.0, -20.0, -51.0), (1.0, 0.0, 0.0), 40.0, 9.0),
        name="under-slide-motion",
        color=motion_red,
    )
    add_under_render_frame(under_slide)
    under_slide_step = _export_colored(under_slide, work / "mount-under-slide-clean.step")

    # 3B — identical counter, camera and hanging assembly. Only the source plate is seated and
    # the captive donor washer/nut pair has closed into the real stack, so the rotation cue is
    # unmistakably about that one hex nut.
    under_tight = cq.Assembly(name="faucet-mount-under-tighten")
    add_under_countertop(under_tight)
    add_under_mount_product(under_tight, washer_top_z=final_washer_top_z)
    _add_child(
        under_tight,
        parts["under_counter_plate"],
        name="under-seated-plate",
        color=plate_steel,
    )
    under_tight.add(
        rotation_arrow((0.0, 0.0, -51.0), 18.0, 70.0, 280.0),
        name="under-tighten-rotation",
        color=motion_red,
    )
    add_under_render_frame(under_tight)
    under_tight_step = _export_colored(under_tight, work / "mount-under-tighten-clean.step")

    return {
        "faucet-head": head_step,
        "faucet-head-pressed": pressed_step,
        "faucet-full": faucet_full_step,
        "mount-drop": drop_step,
        "mount-seated": seated_step,
        "mount-slide": slide_step,
        "mount-tighten": tight_step,
        "mount-lowered-clean": lowered_clean_step,
        "mount-slide-clean": slide_clean_step,
        "mount-final-clean": final_clean_step,
        "mount-under-slide-clean": under_slide_step,
        "mount-under-tighten-clean": under_tight_step,
    }


def _job(
    step: Path,
    out: str | Path,
    cam: tuple[float, float, float],
    *,
    target: tuple[float, float, float] | None = None,
) -> dict:
    output = Path(out)
    if not output.is_absolute():
        output = ART / output
    job = {
        "step": str(step.relative_to(HARDWARE)),
        "out": str(output),
        "cam": cam,
        "up": (0, 0, 1),
        "size": "2400x2400",
        "bg": "#ffffff",
        "trim": True,
        "solid": True,
        "ortho": True,
    }
    if target is not None:
        job["target"] = target
    return job


def _canonicalize_png(path: Path) -> None:
    """Write one byte-stable PNG, without host or wall-clock metadata."""
    with Image.open(path) as image:
        pixels = image.convert("RGBA")
        pixels.save(path, format="PNG", compress_level=9, optimize=False)


def _crop(source: str | Path, geometry: str, target: str | Path) -> None:
    magick = shutil.which("magick") or shutil.which("convert")
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
    magick = shutil.which("magick") or shutil.which("convert")
    if not magick:
        raise RuntimeError("ImageMagick is required to clear CAD picture backgrounds")
    # ImageMagick 7 renamed the IM6 ``matte`` drawing primitive to ``alpha``. macOS carries
    # the v7 ``magick`` entry point; Ubuntu 24.04 carries the v6 ``convert`` entry point.
    primitive = "alpha" if Path(magick).name == "magick" else "matte"
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
            f"{primitive} 0,0 floodfill",
            "-shave",
            "1x1",
            "-strip",
            str(path),
        ],
        check=True,
    )
    _canonicalize_png(path)
    note_write(path)


def _shave_render_frame(path: Path, margin: int) -> None:
    """Remove the frame anchors and their deliberately generous vertical review margin."""
    with Image.open(path) as image:
        top = margin + MOUNT_FRAME_TRIM_TOP
        bottom = image.height - margin - MOUNT_FRAME_TRIM_BOTTOM
        if image.width <= 2 * margin or bottom <= top:
            raise ValueError(f"cannot shave {margin}px from {image.width}x{image.height}: {path}")
        cropped = image.crop((margin, top, image.width - margin, bottom))
        cropped.save(path, format="PNG", compress_level=9, optimize=False)
    _canonicalize_png(path)
    note_write(path)


def _shave_under_render_frame(path: Path, margin: int) -> None:
    """Remove only the four wide-frame anchors, preserving the installer-scale slab."""
    with Image.open(path) as image:
        if image.width <= 2 * margin or image.height <= 2 * margin:
            raise ValueError(f"cannot shave {margin}px from {image.width}x{image.height}: {path}")
        cropped = image.crop((margin, margin, image.width - margin, image.height - margin))
        cropped.save(path, format="PNG", compress_level=9, optimize=False)
    _canonicalize_png(path)
    note_write(path)


def main(*, mount_studies: bool = False) -> None:
    ART.mkdir(parents=True, exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    note_read(RENDERER)
    if not mount_studies:
        note_read(MACHINE_STEP)
        note_read(MACHINE_MESH)
    with tempfile.TemporaryDirectory(prefix="quickstart-cad-", dir=OUT) as directory:
        work = Path(directory)
        steps = _build_steps(work)
        mount_jobs = [
            _job(steps["mount-drop"], "mount-drop.png", MOUNT_CAM, target=MOUNT_TARGET),
            _job(steps["mount-seated"], "mount-seated.png", MOUNT_CAM, target=MOUNT_TARGET),
            _job(steps["mount-slide"], "mount-slide.png", MOUNT_CAM, target=MOUNT_TARGET),
            _job(steps["mount-tighten"], "mount-tighten.png", MOUNT_CAM, target=MOUNT_TARGET),
        ]
        mount_clean_jobs = [
            _job(
                steps["mount-lowered-clean"],
                "mount-lowered-clean.png",
                MOUNT_CAM,
                target=MOUNT_TARGET,
            ),
            _job(
                steps["mount-slide-clean"],
                "mount-slide-clean.png",
                MOUNT_CAM,
                target=MOUNT_TARGET,
            ),
            _job(
                steps["mount-final-clean"],
                "mount-final-clean.png",
                MOUNT_CAM,
                target=MOUNT_TARGET,
            ),
        ]
        under_mount_jobs = [
            _job(
                steps["mount-under-slide-clean"],
                "mount-under-slide-clean.png",
                UNDER_MOUNT_CAM,
                target=UNDER_MOUNT_TARGET,
            ),
            _job(
                steps["mount-under-tighten-clean"],
                "mount-under-tighten-clean.png",
                UNDER_MOUNT_CAM,
                target=UNDER_MOUNT_TARGET,
            ),
        ]
        mount_frame_jobs = [
            *mount_jobs,
            *mount_clean_jobs,
        ]
        mount_render_jobs = [
            *mount_frame_jobs,
            *under_mount_jobs,
        ]
        if mount_studies:
            study_dir = OUT / "mount-studies"
            study_dir.mkdir(parents=True, exist_ok=True)
            for job in mount_render_jobs:
                job["out"] = str(study_dir / Path(job["out"]).name)
            jobs = mount_render_jobs
        else:
            jobs = [
                _job(steps["faucet-head"], "faucet-head.png", (0.18, -1.0, 0.18)),
                _job(steps["faucet-head"], "faucet-side.png", (1.0, -1.4, 0.75)),
                _job(
                    steps["faucet-head-pressed"],
                    "faucet-side-pressed.png",
                    (1.0, -1.4, 0.75),
                ),
                _job(
                    steps["faucet-full"],
                    work / "faucet-full-front.png",
                    (0.0, -1.0, 0.28),
                ),
                *mount_render_jobs,
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
            if job in mount_frame_jobs:
                _shave_render_frame(output, MOUNT_FRAME_SHAVE)
            elif job in under_mount_jobs:
                _shave_under_render_frame(output, UNDER_MOUNT_FRAME_SHAVE)
            note_write(output)

        if not mount_studies:
            _crop("machine-front.png", "960x660+0+100", "machine-hopper-close.png")
            _crop(work / "machine-back.png", "720x560+180+300", "machine-back-close.png")
            _crop("machine-back-iso.png", "617x720+850+220", "machine-ports-iso.png")
            _crop(work / "faucet-full-front.png", "410x540+0+1060", "faucet-tails-front.png")
            _crop("mount-tighten.png", "772x560+0+700", "mount-tighten-close.png")


if __name__ == "__main__":
    main(mount_studies="--mount-studies" in sys.argv[1:])
