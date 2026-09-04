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
MACHINE_FACTS = HARDWARE / "manifold-layout" / "enclosure-assembly.facts.json"
TUBE_COLLAR_DIR = HARDWARE / "printed-parts" / "faucet" / "tube-collar"
MOUNT_CAM = (1.0, -1.45, -0.38)
MOUNT_TARGET = (0.0, 0.0, 110.0)
MOUNT_FRAME_SHAVE = 18
MOUNT_FRAME_TRIM_TOP = 200
MOUNT_DROP_TRIM_TOP = 120
MOUNT_FRAME_TRIM_BOTTOM = 40
UNDER_MOUNT_CAM = (0.58, -1.60, -0.72)
# Centred on the stack the two frames are about, not on the slab that surrounds it.
UNDER_MOUNT_TARGET = (0.0, 0.0, -34.0)
UNDER_MOUNT_FRAME_SHAVE = 18
# The approach frame shows the plate clear of the retained washer before it moves. Its countertop
# window is long on the world-X slide axis and narrow across world Y, where the real under-sink
# approach is constrained.
PLATE_APPROACH_X = -72.0
UNDER_COUNTERTOP_X = 220.0
UNDER_COUNTERTOP_Y = 72.0

# Both rear-connection pictures are one literal scene viewed from one fixed camera. The stronger
# world-X component makes the +Y rear face visibly oblique and therefore narrower on the page.
# That foreshortening leaves room for a large physical +Y withdrawal while the detached bundle's
# modest projected move still clears the enclosure silhouette.
CONNECT_CAM = (0.70, 1.0, 0.16)
CONNECT_TARGET = (-6.0, 630.0, 370.0)
CONNECT_ORTHO_SPAN = 180.0
CONNECT_RENDER_SIZE = "1600x1800"
CONNECT_OPEN_GAP = 160.0
# One literal crop is applied to both fixed-camera frames. It preserves every collar and insertion
# tip in Before, cuts only the intentionally continuing routed ends, and keeps invariant appliance
# geometry in the same pixel coordinates in both final PNGs.
CONNECT_CROP = (0, 650, 1350, 1800)

sys.path.insert(0, str(HARDWARE / "scripts"))
os.environ.setdefault("HSM_NO_BUILD_LOCK", "1")
from _cadq_export import _per_solid_color, _write_mesh_payload, note_read, note_write  # noqa: E402


def _load_faucet_module():
    note_read(FAUCET_SOURCE)
    spec = importlib.util.spec_from_file_location("quickstart_faucet", FAUCET_SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {FAUCET_SOURCE}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _export_colored(assembly: cq.Assembly, target: Path, *, mesh: bool = False) -> Path:
    colored = _per_solid_color(assembly)
    colored.export(str(target))
    if mesh:
        _write_mesh_payload(target, colored)
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
        .circle(fa.soda_faucet_tube_r + 1)
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

    above_counter_names = (
        "westbrass",
        "soda_faucet_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "lever",
        "above_counter_plate",
        "above_counter_gasket",
        "shell_base",
        "shell_tip",
        "faucet_display",
        "faucet_display_screen",
    )

    def above_counter_with(lever, name):
        above = cq.Assembly(name=name)
        for part_name in above_counter_names:
            child = parts[part_name]
            obj = lever if part_name == "lever" else child.obj
            if part_name in {"westbrass", "flavor_tube_pos_x", "flavor_tube_neg_x"}:
                obj = _clip_z(obj, fa.countertop_top_z, 260.0)
            _add_child(above, child, obj=obj)
        return above

    user_step = _export_colored(above_counter_with(lever_rest, "faucet-user"), work / "faucet-user.step")
    pressed_step = _export_colored(
        above_counter_with(lever_pressed, "faucet-user-pressed"), work / "faucet-user-pressed.step"
    )

    # This full, direct-front assembly is an intermediate for the exact rear-wall tail crop. The
    # lever is outside that crop; every pictured tube, sleeve and word collar comes from source CAD.
    faucet_full_step = _export_colored(faucet, work / "faucet-full.step")

    # One literal countertop window appears in every mount state. The upper and lower cameras are
    # intentionally different, but the 220 x 72 mm footprint, opening and thickness are identical
    # so the securing frames read as the underside of the lowering frames above them.
    countertop_window = (
        cq.Workplane("XY")
        .workplane(offset=fa.countertop_bottom_z)
        .box(
            UNDER_COUNTERTOP_X,
            UNDER_COUNTERTOP_Y,
            fa.countertop_thickness,
            centered=(True, True, False),
        )
        .cut(
            cq.Workplane("XY")
            .workplane(offset=fa.countertop_bottom_z - 1.0)
            .center(0.0, fa.countertop_hole_center_y)
            .circle(fa.hole_radius)
            .extrude(fa.countertop_thickness + 2.0)
        )
    )

    mount_names = (
        "westbrass",
        "soda_faucet_tube",
        "tpu_o_ring",
        "flavor_tube_pos_x",
        "flavor_tube_neg_x",
        "soda_umbilical_tube",
        "lever",
        "above_counter_plate",
        "above_counter_gasket",
        "shell_base",
        "shell_tip",
        "faucet_display",
        "faucet_display_screen",
    )
    mount_tails = {"flavor_tube_pos_x", "flavor_tube_neg_x", "soda_umbilical_tube"}
    mount_clip = (-88.0, 380.0)
    washer_thickness = 1.5
    nut_height = 5.0
    # Until the plate is in, the pair hangs on the shank's last thread. A 50 mm shank through a
    # 30 mm slab leaves 14 mm of shank below the counter, and everything above the washer there
    # is the gap the open plate slides through — so the pair is drawn at the bottom of it.
    captive_washer_top_z = -fa.shank_length + nut_height + washer_thickness
    final_washer_top_z = fa.countertop_bottom_z - fa.under_counter_plate_thickness
    plate_steel = cq.Color(0.91, 0.92, 0.94, 1.0)
    washer_steel = cq.Color(0.82, 0.83, 0.84, 1.0)
    nut_steel = cq.Color(0.43, 0.45, 0.48, 1.0)
    countertop_stone = cq.Color(0.55, 0.55, 0.58, 1.0)
    # The two flavor lines and the flat SIG-6 faucet-display cable are physically black. Slightly
    # different instruction-lighting tones keep all three countable where their silhouettes meet.
    flavor_black_a = cq.Color(0.025, 0.027, 0.031, 1.0)
    flavor_black_b = cq.Color(0.20, 0.205, 0.215, 1.0)
    signal_black = cq.Color(0.035, 0.038, 0.043, 1.0)
    signal_stripe_black = cq.Color(0.16, 0.17, 0.19, 1.0)
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
            point = target.add(right.multiply(across * 137.0)).add(
                screen_up.multiply(rise * 58.0)
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
        out.add(ribbon, name="sig6-flat-ribbon", color=signal_black)
        out.add(ribbon_stripes, name="sig6-ribbon-face-stripes", color=signal_stripe_black)
        if washer_top_z is None:
            washer_top_z = captive_washer_top_z + lift_z
        washer, nut = donor_hardware(washer_top_z)
        out.add(washer, name="retained-donor-washer", color=washer_steel)
        out.add(nut, name="retained-donor-nut", color=nut_steel)

    def add_countertop_section(out: cq.Assembly):
        out.add(countertop_window, name="countertop-window", color=countertop_stone)

    def add_under_countertop(out: cq.Assembly):
        """Show the long slide runway and the narrow cross-slide working clearance."""
        out.add(countertop_window, name="under-countertop-window", color=countertop_stone)

    def add_under_mount_product(out: cq.Assembly, *, washer_top_z: float):
        """Show only the real shank, three attached tubes and captive donor pair below the slab."""
        under_clip = (-86.0, -2.0)
        for part_name in (
            "westbrass",
            "flavor_tube_pos_x",
            "flavor_tube_neg_x",
            "soda_umbilical_tube",
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
        obj=_moved(parts["under_counter_plate"].obj, (PLATE_APPROACH_X, 0.0, 0.0)),
        color=plate_steel,
    )
    add_render_frame(slide)
    slide_clean_step = _export_colored(slide, work / "mount-slide-clean.step")
    slide_step = _export_colored(slide, work / "mount-slide.step")

    # 4 — plate seated, same pair closed against it. The page-level circular cue asks for hand
    # rotation without hiding the zero-gap result behind an approximate CAD hand.
    tight = cq.Assembly(name="faucet-mount-tighten")
    add_countertop_section(tight)
    add_mount_product(tight, 0.0, washer_top_z=final_washer_top_z)
    _add_child(tight, parts["under_counter_plate"], color=plate_steel)
    add_render_frame(tight)
    final_clean_step = _export_colored(tight, work / "mount-final-clean.step")
    tight_step = _export_colored(tight, work / "mount-tighten.step")

    # 3A — once the faucet is seated, the installer is below the intact counter. The light steel
    # plate is the actual source DXF solid, still displaced at -X; its two open channels face the
    # attached shank/tube stack.
    under_slide = cq.Assembly(name="faucet-mount-under-slide")
    add_under_countertop(under_slide)
    add_under_mount_product(under_slide, washer_top_z=captive_washer_top_z)
    _add_child(
        under_slide,
        parts["under_counter_plate"],
        name="under-open-plate",
        obj=_moved(parts["under_counter_plate"].obj, (PLATE_APPROACH_X, 0.0, 0.0)),
        color=plate_steel,
    )
    add_under_render_frame(under_slide)
    under_slide_step = _export_colored(under_slide, work / "mount-under-slide-clean.step")

    # 3B — identical counter, camera and hanging assembly. Only the source plate is seated and
    # the captive donor washer/nut pair has closed into the real stack. The page anchors its
    # rotation cue directly on that one hex nut.
    under_tight = cq.Assembly(name="faucet-mount-under-tighten")
    add_under_countertop(under_tight)
    add_under_mount_product(under_tight, washer_top_z=final_washer_top_z)
    _add_child(
        under_tight,
        parts["under_counter_plate"],
        name="under-seated-plate",
        color=plate_steel,
    )
    add_under_render_frame(under_tight)
    under_tight_step = _export_colored(under_tight, work / "mount-under-tighten-clean.step")

    return {
        "faucet-user": user_step,
        "faucet-user-pressed": pressed_step,
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


def _build_connection_steps(work: Path) -> dict[str, Path]:
    """Build the two rear connection states as literal, fixed-camera CAD scenes.

    The appliance exterior and every connection station come from the current enclosure STEP and
    its generated facts.  All five tube collars are production solids, including their recessed
    lettering.  Only the field-cut tube lengths, the flat SIG-6 ribbon, and its
    modular plug are constructed here because those flexible customer-routed bodies have no single
    installed pose in the product assembly.
    """
    note_read(MACHINE_FACTS)
    facts = json.loads(MACHINE_FACTS.read_text())
    collar_steps = {
        "tap": "water",
        "co2": "co2",
        "carb": "carb",
        "flavor-a": "flavor-a",
        "flavor-b": "flavor-b",
    }
    for collar_step in collar_steps.values():
        note_read(TUBE_COLLAR_DIR / f"tube-collar-{collar_step}.step")

    machine = cq.Assembly.load(str(MACHINE_STEP))

    # The exact closed rear half, rather than the appliance's hidden internals.  These are the
    # source assembly nodes a customer can see from the rear: the printed shell, ceiling/funnel,
    # every through-wall fitting and jack, and the nameplate. TAP and CO2 customer leads are
    # deliberately withheld here and added to the movable field-lead assembly below, so the open
    # state cannot accidentally leave either one seated.
    exact_names = {
        "c14-inlet",
        "keystone-jack",
        "co2-inlet",
        "bulkhead-water",
        "bulkhead-flavor-a",
        "bulkhead-flavor-b",
        "bulkhead-carb",
        "funnel",
        "nameplate",
        "nameplate-ink",
        "enclosure-back-bottom",
        "enclosure-back-top",
        "enclosure-ceiling-panel",
    }
    exact_prefixes = ("bulkhead-ring-",)
    rear_children = [
        child
        for child in machine.children
        if child.name in exact_names or child.name.startswith(exact_prefixes)
    ]

    tube_blue = cq.Color(0.035, 0.31, 0.82, 1.0)
    tube_red = cq.Color(0.67, 0.042, 0.042, 1.0)
    tube_white = cq.Color(0.82, 0.84, 0.87, 1.0)
    # Both flavour tails are black stock.  A small lighting difference keeps the two round bodies
    # countable where they cross the same dark rear wall without turning either one grey.
    tube_black_a = cq.Color(0.025, 0.027, 0.031, 1.0)
    tube_black_b = cq.Color(0.115, 0.12, 0.13, 1.0)
    collar_blue = cq.Color(0.055, 0.34, 0.84, 1.0)
    collar_red = cq.Color(0.84, 0.055, 0.055, 1.0)
    collar_white = cq.Color(0.94, 0.945, 0.955, 1.0)
    collar_black_a = cq.Color(0.02, 0.022, 0.026, 1.0)
    collar_black_b = cq.Color(0.105, 0.11, 0.12, 1.0)
    collar_word = cq.Color(0.94, 0.945, 0.955, 1.0)
    collar_word_black = cq.Color(0.025, 0.027, 0.031, 1.0)
    ribbon_black = cq.Color(0.035, 0.038, 0.043, 1.0)
    ribbon_edge = cq.Color(0.16, 0.17, 0.19, 1.0)
    plug_body = cq.Color(0.72, 0.74, 0.78, 1.0)
    plug_latch = cq.Color(0.86, 0.87, 0.89, 1.0)
    contact_gold = cq.Color(0.73, 0.49, 0.14, 1.0)
    def round_sweep(points, radius: float):
        vectors = [cq.Vector(*point) for point in points]
        tangent = cq.Vector(0.0, 1.0, 0.0)
        path = cq.Edge.makeSpline(vectors, tangents=(tangent, tangent), scale=False)
        profile = cq.Wire.makeCircle(radius, vectors[0], tangent)
        # A parallel-transported profile stays continuous through the long, shallow bends used by
        # these hoses. A Frenet frame can flip at a spline inflection and leave a visible split.
        return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=False)

    def ribbon_sweep(points, width: float, thickness: float):
        vectors = [cq.Vector(*point) for point in points]
        tangent = cq.Vector(0.0, 1.0, 0.0)
        path = cq.Edge.makeSpline(vectors, tangents=(tangent, tangent), scale=False)
        p = vectors[0]
        profile = cq.Wire.makePolygon(
            [
                cq.Vector(p.x - width / 2.0, p.y, p.z - thickness / 2.0),
                cq.Vector(p.x + width / 2.0, p.y, p.z - thickness / 2.0),
                cq.Vector(p.x + width / 2.0, p.y, p.z + thickness / 2.0),
                cq.Vector(p.x - width / 2.0, p.y, p.z + thickness / 2.0),
            ],
            close=True,
        )
        return cq.Solid.sweep(profile, [], path, makeSolid=True, isFrenet=True)

    def split_collar(which: str):
        collar_step = collar_steps[which]
        loaded = cq.importers.importStep(
            str(TUBE_COLLAR_DIR / f"tube-collar-{collar_step}.step")
        ).val()
        solids = list(loaded.Solids())
        body = max(solids, key=lambda solid: solid.Volume())
        words = cq.Compound.makeCompound([solid for solid in solids if solid is not body])
        return body, words

    card_ports = facts["card_ports"]
    co2_bounds = facts["bodies"]["tube-customer-co2"]
    stations = {
        "tap": tuple(card_ports["bulkhead-water"]["outboard"]["pos"]),
        "carb": tuple(card_ports["bulkhead-carb"]["tube-out"]["pos"]),
        "co2": (
            (co2_bounds[0] + co2_bounds[3]) / 2.0,
            co2_bounds[1],
            (co2_bounds[2] + co2_bounds[5]) / 2.0,
        ),
        "flavor-a": tuple(card_ports["bulkhead-flavor-a"]["tube-out"]["pos"]),
        "flavor-b": tuple(card_ports["bulkhead-flavor-b"]["tube-out"]["pos"]),
    }
    tube_colors = {
        "tap": tube_white,
        "carb": tube_blue,
        "co2": tube_red,
        "flavor-a": tube_black_a,
        "flavor-b": tube_black_b,
    }
    collar_colors = {
        "tap": collar_white,
        "carb": collar_blue,
        "co2": collar_red,
        "flavor-a": collar_black_a,
        "flavor-b": collar_black_b,
    }
    collar_word_colors = {
        which: collar_word_black if which == "tap" else collar_word
        for which in collar_colors
    }
    # The bare tails stay straight through their collars, then flex into the compact end of the
    # common umbilical.  These target points preserve five distinct solids all the way out of the
    # picture instead of collapsing the tails into one illustrative stroke.
    pack_stations = {
        "tap": (-60.0, 322.0),
        "co2": (-40.0, 322.0),
        "carb": (-50.0, 312.0),
        "flavor-a": (-40.0, 302.0),
        "flavor-b": (-60.0, 302.0),
    }

    umbilical = cq.Assembly(name="customer-field-leads-wall-end")

    straight_end_y = 560.0
    pack_y = 626.0
    # The customer-routed side is deliberately longer than the fixed viewport: after the compact
    # fan-out, every lead continues beyond the picture instead of ending in a second visible free
    # face.  In the detached state the only visible ends are therefore the six ends the customer
    # is about to insert; in the connected state there are no loose ends at all.
    tail_y = 940.0
    # All five 30 mm collars use the insertion tip as their datum.  The near face sits 47.5 mm
    # behind that tip and the far face 77.5 mm behind it, matching the production bare-tail rule
    # despite CO2's port living on a slightly different Y plane from the four push-fit stations.
    collar_tip_setback = 47.5
    tube_radius = 6.35 / 2.0
    for which in ("tap", "co2", "carb", "flavor-a", "flavor-b"):
        x, tube_start_y, z = stations[which]
        pack_x, pack_z = pack_stations[which]
        tube = round_sweep(
            (
                (x, tube_start_y, z),
                (x, straight_end_y, z),
                (x, 578.0, z),
                ((2.0 * x + pack_x) / 3.0, 598.0, (2.0 * z + pack_z) / 3.0),
                (pack_x, pack_y, pack_z),
                (pack_x, tail_y, pack_z),
            ),
            tube_radius,
        )
        umbilical.add(
            tube,
            name=f"wall-end-tube-{which}",
            color=tube_colors[which],
        )
        collar, words = split_collar(which)
        move = (x, tube_start_y + collar_tip_setback, z)
        umbilical.add(
            collar.translate(move),
            name=f"wall-end-collar-{which}",
            color=collar_colors[which],
        )
        umbilical.add(
            words.translate(move),
            name=f"wall-end-collar-{which}-word",
            color=collar_word_colors[which],
        )

    # The jack's face is the enclosure's exact +Y outer plane.  Its opening is centred 1 mm below
    # the keystone show-face station in the production reference model.
    jack_x, jack_station_z = facts["constants"]["KEYSTONE_STATION"]
    jack_face_y = facts["box"]["outer"][3]
    jack_port_z = jack_station_z - 1.0
    plug_w = 9.0
    plug_h = 6.45
    plug_y0 = jack_face_y - 6.2
    plug_depth = 21.0
    plug = cq.Solid.makeBox(
        plug_w,
        plug_depth,
        plug_h,
        cq.Vector(jack_x - plug_w / 2.0, plug_y0, jack_port_z - plug_h / 2.0),
    )
    boot = cq.Solid.makeBox(
        7.8,
        5.5,
        5.5,
        cq.Vector(jack_x - 3.9, plug_y0 + plug_depth, jack_port_z - 2.75),
    )
    umbilical.add(
        cq.Compound.makeCompound([plug, boot]),
        name="wall-end-rj11-plug-body",
        color=plug_body,
    )
    # The flexible latch faces the jack's lower latch slot.  A thin tongue and its raised ramp are
    # separate molded volumes, so the silhouette reads at print size instead of as a line drawn on
    # the plug.
    latch_z = jack_port_z - plug_h / 2.0
    latch_tongue = cq.Solid.makeBox(
        3.4,
        12.0,
        0.75,
        cq.Vector(jack_x - 1.7, plug_y0 + 4.0, latch_z - 0.75),
    )
    latch_ramp = (
        cq.Workplane("YZ")
        .polyline(
            [
                (plug_y0 + 10.0, latch_z - 0.75),
                (plug_y0 + 16.0, latch_z - 0.75),
                (plug_y0 + 16.0, latch_z - 2.35),
                (plug_y0 + 10.0, latch_z - 0.75),
            ]
        )
        .wire()
        .extrude(3.4)
        .translate((jack_x - 1.7, 0.0, 0.0))
        .val()
    )
    umbilical.add(
        cq.Compound.makeCompound([latch_tongue, latch_ramp]),
        name="wall-end-rj11-latch",
        color=plug_latch,
    )
    for index, contact_x in enumerate((-2.7, -0.9, 0.9, 2.7), start=1):
        contact = cq.Solid.makeBox(
            0.48,
            7.0,
            0.18,
            cq.Vector(
                jack_x + contact_x - 0.24,
                plug_y0 + 0.4,
                jack_port_z + plug_h / 2.0 - 0.18,
            ),
        )
        umbilical.add(contact, name=f"wall-end-rj11-contact-{index}", color=contact_gold)

    ribbon_start_y = plug_y0 + plug_depth + 5.5
    ribbon_points = (
        (jack_x, ribbon_start_y, jack_port_z),
        (jack_x, 548.0, jack_port_z),
        (-42.0, 590.0, 298.0),
        (-48.5, pack_y, 294.0),
        (-48.5, tail_y, 294.0),
    )
    ribbon = ribbon_sweep(ribbon_points, 4.0, 1.2)
    ribbon_mark = ribbon_sweep(
        tuple((x + 1.55, y, z + 0.63) for x, y, z in ribbon_points),
        0.28,
        0.08,
    )
    umbilical.add(ribbon, name="wall-end-sig6-ribbon", color=ribbon_black)
    umbilical.add(ribbon_mark, name="wall-end-sig6-ribbon-mark", color=ribbon_edge)

    def state(name: str, shift_y: float):
        scene = cq.Assembly(name=name)
        for child in rear_children:
            scene.add(child)
        scene.add(
            umbilical,
            name=f"{name}-umbilical",
            loc=cq.Location(cq.Vector(0.0, shift_y, 0.0)),
        )
        return _export_colored(scene, work / f"{name}.step", mesh=True)

    open_step = state("connect-rear-open", CONNECT_OPEN_GAP)
    connected_step = state("connect-rear-connected", 0.0)

    # The production appliance's payload already carries the fluted printed skin that its B-rep
    # intentionally omits.  Graft those exact rear-body meshes into each scene payload by body
    # name; the modeled tubes, collars, ribbon and plug remain the new solids tessellated above.
    import flute_payload

    source_meshes = flute_payload.read_payload(MACHINE_MESH) or []
    exact_meshes = {entry["name"]: entry for entry in source_meshes}
    for step in (open_step, connected_step):
        mesh = Path(str(step) + ".mesh")
        landed = flute_payload.graft(mesh, exact_meshes)
        if landed < 3:
            raise RuntimeError(
                f"{step.name}: only {landed} exact appliance meshes landed in rear scene"
            )

    return {
        "connect-rear-open": open_step,
        "connect-rear-connected": connected_step,
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
        # The first faucet starts higher than the seated views. Preserve that real top geometry;
        # the page layout lets its image box extend into unused heading-row air.
        trim_top = MOUNT_DROP_TRIM_TOP if path.name == "mount-drop.png" else MOUNT_FRAME_TRIM_TOP
        top = margin + trim_top
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


def _crop_registered_connection(path: Path) -> None:
    """Apply the same fixed viewport crop to both rear-connection states."""
    with Image.open(path) as image:
        if image.size != tuple(map(int, CONNECT_RENDER_SIZE.split("x"))):
            raise ValueError(
                f"expected {CONNECT_RENDER_SIZE} rear render, found {image.width}x{image.height}: {path}"
            )
        cropped = image.crop(CONNECT_CROP)
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
        if not mount_studies:
            steps.update(_build_connection_steps(work))
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
        connect_jobs = [] if mount_studies else [
            _job(
                steps["connect-rear-open"],
                "connect-rear-open.png",
                CONNECT_CAM,
                target=CONNECT_TARGET,
            ),
            _job(
                steps["connect-rear-connected"],
                "connect-rear-connected.png",
                CONNECT_CAM,
                target=CONNECT_TARGET,
            ),
        ]
        for job in connect_jobs:
            # One literal orthographic viewport registers the rear panel pixel-for-pixel in both
            # states.  Its final canvas is the page crop; no scene geometry or content trim frames
            # it.  Native alpha keeps the separate tube and cable silhouettes free of the white
            # islands that an edge flood-fill cannot reach between disconnected objects.  Viewer
            # floor and distance effects are omitted for clean instruction-page art.
            job["size"] = CONNECT_RENDER_SIZE
            job["span"] = CONNECT_ORTHO_SPAN
            job["trim"] = False
            job["ground"] = False
            job["fog"] = False
            job["transparent"] = True
        if mount_studies:
            study_dir = OUT / "mount-studies"
            study_dir.mkdir(parents=True, exist_ok=True)
            for job in mount_render_jobs:
                job["out"] = str(study_dir / Path(job["out"]).name)
            jobs = mount_render_jobs
        else:
            jobs = [
                _job(steps["faucet-user"], "faucet-front.png", (0.18, -1.0, 0.18)),
                _job(steps["faucet-user"], "faucet-side.png", (1.0, -1.4, 0.75)),
                _job(
                    steps["faucet-user-pressed"],
                    "faucet-side-pressed.png",
                    (1.0, -1.4, 0.75),
                ),
                _job(
                    steps["faucet-full"],
                    work / "faucet-full-front.png",
                    (0.0, -1.0, 0.28),
                ),
                *mount_render_jobs,
                *connect_jobs,
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
            if job not in connect_jobs:
                _clear_connected_background(output)
            if job in mount_frame_jobs:
                _shave_render_frame(output, MOUNT_FRAME_SHAVE)
            elif job in under_mount_jobs:
                _shave_under_render_frame(output, UNDER_MOUNT_FRAME_SHAVE)
            elif job in connect_jobs:
                _crop_registered_connection(output)
            note_write(output)

        if not mount_studies:
            _crop("machine-front.png", "960x660+0+100", "machine-funnel-close.png")
            _crop(work / "machine-back.png", "720x560+180+300", "machine-back-close.png")
            _crop("machine-back-iso.png", "617x720+850+220", "machine-ports-iso.png")
            _crop("machine-ports-iso.png", "617x612+0+72", "machine-ports-action.png")
            _crop("machine-ports-iso.png", "594x393+23+293", "machine-signal-iso.png")
            _crop(work / "faucet-full-front.png", "410x540+0+1060", "faucet-tails-front.png")
            _crop("mount-tighten.png", "772x560+0+700", "mount-tighten-close.png")


if __name__ == "__main__":
    main(mount_studies="--mount-studies" in sys.argv[1:])
