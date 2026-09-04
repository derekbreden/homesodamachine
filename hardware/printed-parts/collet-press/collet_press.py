"""Collet press — one-piece hand tool for releasing a 1/4-inch John Guest
push-to-connect collet.

Print orientation is the modelling orientation: the handle lies flat on Z=0
and the forked head rises from it at 45 degrees.  The head is one unstepped
slab.  Its U-slot passes the tube while the surrounding face bears on the
release sleeve.

Run:
    tools/cad-venv/bin/python \
        hardware/printed-parts/collet-press/collet_press.py
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import cadquery as cq


_here = Path(__file__).resolve().parent
_hardware = next(p for p in _here.parents if p.name == "hardware")
_repo = _hardware.parent
sys.path.insert(0, str(_hardware / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hardware / "reference" / "jg-pp0408w"))

from _cadq_export import (  # noqa: E402
    _write_mesh_payload,
    export_assembly,
    note_write,
)
from _materials import M_PETGF_BLACK, one_body  # noqa: E402
from docgen import substitute_md  # noqa: E402
import jg_pp0408w as jg  # noqa: E402


# --- working fit -----------------------------------------------------------

# A close slip over nominal 1/4-inch tube.  It remains narrower than the
# measured collet bore, so each jaw arm spans the sleeve's complete radial wall.
JAW_GAP = 6.55
JAW_RADIUS = JAW_GAP / 2.0
JAW_ROOT_U = 0.0
# With the tube seated in the semicircular root, the straight inner edges run
# through the collet's forward OD tangent.  Every part of the annular release
# face reachable by the two arms is therefore under straight material before
# their rounded noses turn away.
STRAIGHT_TIP_U = jg.COLLET_D / 2.0
JAW_DEPTH = STRAIGHT_TIP_U - (JAW_ROOT_U - JAW_RADIUS)
STRAIGHT_OVERRUN = STRAIGHT_TIP_U - jg.PORT_D / 2.0


# --- printable body --------------------------------------------------------

HEAD_ANGLE = 45.0
HEAD_THICKNESS = 6.00       # 25 layers at 0.24 mm; 50 at 0.12 mm
HEAD_WIDTH = 20.0
ARM_WIDTH = (HEAD_WIDTH - JAW_GAP) / 2.0
TIP_RADIUS = 2.0
HEAD_BACK_LAND = ARM_WIDTH
HEAD_BACK_U = JAW_ROOT_U - JAW_RADIUS - HEAD_BACK_LAND
# The two rounded noses carry on by exactly their fillet radius after the
# straight lands reach the collet's outer edge.
HEAD_FRONT_U = STRAIGHT_TIP_U + TIP_RADIUS
HEAD_LENGTH = HEAD_FRONT_U - HEAD_BACK_U
HEAD_CENTER_U = (HEAD_BACK_U + HEAD_FRONT_U) / 2.0

# Length of the handle's bottom bed edge before its front rises at 45°.
HANDLE_LENGTH = 96.0
HANDLE_WIDTH = HEAD_WIDTH
HANDLE_THICKNESS = HEAD_THICKNESS
HANDLE_CORNER_RADIUS = TIP_RADIUS
# Enough overlap for a broad fused root, while the head's underside clears the
# tube slot before that slot begins.
ROOT_BURY = HEAD_THICKNESS * math.cos(math.radians(HEAD_ANGLE))
HEAD_REAR_LOWER_Z = HANDLE_THICKNESS - ROOT_BURY
HEAD_Z_SHIFT = (
    HEAD_REAR_LOWER_Z
    - HEAD_BACK_U * math.sin(math.radians(HEAD_ANGLE))
)


def _head_underside_x(z: float) -> float:
    """World X of the head's lower face at world height ``z``."""
    return (z - HEAD_Z_SHIFT) / math.tan(math.radians(HEAD_ANGLE))


HANDLE_FRONT_BED_X = _head_underside_x(0.0)
HANDLE_FRONT_TOP_X = _head_underside_x(HANDLE_THICKNESS)
HANDLE_REAR_X = HANDLE_FRONT_BED_X - HANDLE_LENGTH


def _rounded_prism(
    length: float,
    width: float,
    height: float,
    radius: float,
    center_x: float,
) -> cq.Workplane:
    """Z extrusion of a plan-view rounded rectangle."""
    return (
        cq.Workplane("XY")
        .center(center_x, 0.0)
        .rect(length, width)
        .extrude(height)
        .edges("|Z")
        .fillet(radius)
    )


def build_handle() -> cq.Workplane:
    """Broad bed-contact paddle ending on the head's own 45° underside."""
    # The raw rounded prism deliberately runs beyond the desired front.  The
    # XZ half-space then removes its whole nose on z = x + HEAD_Z_SHIFT, so no
    # horizontal material survives beyond the rising head.
    raw_front = HANDLE_FRONT_TOP_X + 2.0
    raw_length = raw_front - HANDLE_REAR_X
    raw = _rounded_prism(
        raw_length,
        HANDLE_WIDTH,
        HANDLE_THICKNESS,
        HANDLE_CORNER_RADIUS,
        (HANDLE_REAR_X + raw_front) / 2.0,
    )
    clip_low_z = -1.0
    clip_high_z = HANDLE_THICKNESS + 1.0
    clip = (
        cq.Workplane("XZ")
        .polyline(
            [
                (HANDLE_REAR_X - 2.0, clip_low_z),
                (_head_underside_x(clip_low_z), clip_low_z),
                (_head_underside_x(clip_high_z), clip_high_z),
                (HANDLE_REAR_X - 2.0, clip_high_z),
            ]
        )
        .close()
        .extrude(HANDLE_WIDTH, both=True)
    )
    return raw.intersect(clip).clean()


def build_head_local() -> cq.Workplane:
    """The U-head before its local U/Y/W frame is tilted into world XYZ."""
    outer = (
        cq.Workplane("XY")
        .center(HEAD_CENTER_U, 0.0)
        .rect(HEAD_LENGTH, HEAD_WIDTH)
        .extrude(HEAD_THICKNESS)
    )

    # Rectangle open to +U plus a circular root: a true constant-width U-slot,
    # not a V-notch.  The extra W at both ends guarantees a through-cut.
    slot_straight = (
        cq.Workplane("XY")
        .center((JAW_ROOT_U + HEAD_FRONT_U + 1.0) / 2.0, 0.0)
        .rect(HEAD_FRONT_U + 1.0 - JAW_ROOT_U, JAW_GAP)
        .workplane(offset=-1.0)
        .extrude(HEAD_THICKNESS + 2.0)
    )
    slot_root = (
        cq.Workplane("XY")
        .center(JAW_ROOT_U, 0.0)
        .circle(JAW_RADIUS)
        .workplane(offset=-1.0)
        .extrude(HEAD_THICKNESS + 2.0)
    )
    sharp = outer.cut(slot_straight.union(slot_root)).clean()

    # Round only the two outside and two inside corners at the open end.  The
    # rear corners stay square and disappear inside the equal-width handle, so
    # no shoulder or roundover interrupts the strip at its 45-degree crease.
    # At the mouth, the fillets begin exactly at STRAIGHT_TIP_U, preserving a
    # complete straight bearing land through the collet's forward OD tangent.
    tip_edges = [
        edge
        for edge in sharp.edges("|Z").vals()
        if abs(edge.Center().x - HEAD_FRONT_U) < 1e-6
    ]
    return sharp.newObject(tip_edges).fillet(TIP_RADIUS).clean()


def _place_head(local: cq.Workplane) -> cq.Workplane:
    """Carry head-local U/Y/W geometry into the print-oriented world frame."""
    return (
        local
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), -HEAD_ANGLE)
        .translate((0.0, 0.0, HEAD_Z_SHIFT))
    )


def build_head() -> cq.Workplane:
    """Tilt the complete head so its broad faces cross the layer stack at 45°."""
    # CadQuery's -Y rotation maps +U toward both +X and +Z.  This shift puts
    # the neck's lowest rear edge exactly on Z=0; most of that rear length is
    # buried in the handle, leaving a wide fused root before the head emerges.
    return _place_head(build_head_local())


def build() -> cq.Workplane:
    """One supportless solid: flat handle, buried root, angled U-head."""
    handle = build_handle()
    protrusion = max(
        vertex.Center().x - vertex.Center().z + HEAD_Z_SHIFT
        for vertex in handle.vertices().vals()
    )
    if protrusion > 1e-6:
        raise ValueError(
            f"handle projects {protrusion:.6f} mm beyond the head's 45-degree underside"
        )
    if not math.isclose(STRAIGHT_TIP_U, jg.COLLET_D / 2.0, abs_tol=1e-9):
        raise ValueError("straight arms must reach the collet's forward OD tangent")
    if not math.isclose(HEAD_FRONT_U - STRAIGHT_TIP_U, TIP_RADIUS, abs_tol=1e-9):
        raise ValueError("rounded noses must begin beyond the collet face")
    if not math.isclose(HEAD_BACK_LAND, ARM_WIDTH, abs_tol=1e-9):
        raise ValueError("angled head must stop one arm width behind the U")
    if not math.isclose(HEAD_WIDTH, HANDLE_WIDTH, abs_tol=1e-9):
        raise ValueError("head and handle must remain one constant-width strip")
    if not math.isclose(HEAD_THICKNESS, HANDLE_THICKNESS, abs_tol=1e-9):
        raise ValueError("head and handle thicknesses must remain equal")
    if not math.isclose(HANDLE_CORNER_RADIUS, TIP_RADIUS, abs_tol=1e-9):
        raise ValueError("handle end and fork tips must use the same radius")

    tool = handle.union(build_head()).clean()

    solids = tool.solids().vals()
    if len(solids) != 1 or not solids[0].isValid():
        raise ValueError("collet press must resolve to one valid printable solid")
    bb = solids[0].BoundingBox()
    if abs(bb.zmin) > 1e-6:
        raise ValueError(f"print face drifted off Z=0: zmin={bb.zmin:.6f}")
    if not (jg.PORT_D < JAW_GAP < jg.COLLET_BORE):
        raise ValueError("jaw must pass the tube and remain inside the collet bore")
    jaw_cover = (jg.COLLET_D - JAW_GAP) / 2.0
    if jaw_cover < jg.COLLET_WALL:
        raise ValueError("jaw arms do not span the measured collet's radial wall")

    tube_local = (
        cq.Workplane("XY")
        .center(JAW_ROOT_U, 0.0)
        .circle(jg.PORT_D / 2.0)
        .workplane(offset=-2.0)
        .extrude(HEAD_THICKNESS + 4.0)
    )
    tube_interference = sum(
        solid.Volume()
        for solid in tool.intersect(_place_head(tube_local)).solids().vals()
    )
    if tube_interference > 1e-6:
        raise ValueError(
            f"handle or head fills {tube_interference:.6f} mm³ of the tube path"
        )
    return tool


def main() -> None:
    tool = build()
    solid = tool.val()
    bb = solid.BoundingBox()

    step_out = _here / "collet-press.step"
    stl_out = _here / "collet-press.stl"
    payload_out = Path(str(step_out) + ".mesh")
    assembly = one_body(tool, "collet-press", M_PETGF_BLACK)
    export_assembly(assembly, str(step_out))
    # A sibling STL normally tells the shared exporter that a specialist owns
    # the preview mesh.  This smooth part writes its STL directly, so it also
    # refreshes the matching viewer payload directly on every regeneration.
    note_write(payload_out)
    _write_mesh_payload(step_out, assembly)
    note_write(stl_out)
    cq.exporters.export(tool, str(stl_out), tolerance=0.02, angularTolerance=0.1)
    print(f"-> {step_out.name}")
    print(f"-> {stl_out.name}")
    print(
        "   envelope "
        f"{bb.xlen:.2f} x {bb.ylen:.2f} x {bb.zlen:.2f} mm; "
        f"volume {solid.Volume() / 1000.0:.2f} cm^3"
    )

    variables = {
        "TUBE_D": f"{jg.PORT_D:.2f} mm",
        "JAW_GAP": f"{JAW_GAP:.2f} mm",
        "JAW_DEPTH": f"{JAW_DEPTH:.2f} mm",
        "STRAIGHT_OVERRUN": f"{STRAIGHT_OVERRUN:.2f} mm",
        "ARM_W": f"{ARM_WIDTH:.3f} mm",
        "TIP_R": f"{TIP_RADIUS:.1f} mm",
        "HEAD_BACK_LAND": f"{HEAD_BACK_LAND:.3f} mm",
        "ROOT_BURY": f"{ROOT_BURY:.2f} mm",
        "TUBE_CLEARANCE": f"{JAW_GAP - jg.PORT_D:.2f} mm",
        "COLLET_D": f"{jg.COLLET_D:.2f} mm",
        "COLLET_BORE": f"{jg.COLLET_BORE:.2f} mm",
        "COLLET_WALL": f"{jg.COLLET_WALL:.2f} mm",
        "JAW_COVER": f"{(jg.COLLET_D - JAW_GAP) / 2.0:.2f} mm per side",
        "COLLET_TRAVEL": f"{jg.COLLET_TRAVEL:.3f} mm",
        "HEAD_ANGLE": f"{HEAD_ANGLE:.0f}°",
        "HEAD_T": f"{HEAD_THICKNESS:.2f} mm",
        "HEAD_W": f"{HEAD_WIDTH:.0f} mm",
        "HANDLE_L": f"{HANDLE_LENGTH:.0f} mm",
        "HANDLE_W": f"{HANDLE_WIDTH:.0f} mm",
        "HANDLE_T": f"{HANDLE_THICKNESS:.2f} mm",
        "TOOL_X": f"{bb.xlen:.1f} mm",
        "TOOL_Y": f"{bb.ylen:.1f} mm",
        "TOOL_Z": f"{bb.zlen:.1f} mm",
        "TOOL_VOLUME": f"{solid.Volume() / 1000.0:.1f} cm³",
    }
    substitute_md(_here / "README.md", variables=variables)
    print("-> README.md")


if __name__ == "__main__":
    main()
