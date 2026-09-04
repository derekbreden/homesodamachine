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
# The mouth ends at the tube's forward tangent when the tube is seated in the
# semicircular root.  Bottom-to-mouth depth is therefore exactly one jaw gap.
JAW_MOUTH_U = JAW_RADIUS
JAW_DEPTH = JAW_MOUTH_U - (JAW_ROOT_U - JAW_RADIUS)


# --- printable body --------------------------------------------------------

HEAD_ANGLE = 45.0
HEAD_THICKNESS = 7.20       # 30 layers at 0.24 mm; 60 at 0.12 mm
HEAD_BACK_U = -16.0
HEAD_FRONT_U = JAW_MOUTH_U
HEAD_LENGTH = HEAD_FRONT_U - HEAD_BACK_U
HEAD_WIDTH = 28.0
HEAD_CORNER_RADIUS = 5.0
HEAD_CENTER_U = (HEAD_BACK_U + HEAD_FRONT_U) / 2.0

NECK_U_MIN = -32.0
NECK_U_MAX = -8.0
NECK_LENGTH = NECK_U_MAX - NECK_U_MIN
NECK_WIDTH = 24.0
NECK_CORNER_RADIUS = 4.0
NECK_CENTER_U = (NECK_U_MIN + NECK_U_MAX) / 2.0
HEAD_U_MIN = NECK_U_MIN
HEAD_Z_SHIFT = -HEAD_U_MIN * math.sin(math.radians(HEAD_ANGLE))

# Length of the handle's bottom bed edge before its front rises at 45°.
HANDLE_LENGTH = 96.0
HANDLE_WIDTH = 24.0
HANDLE_THICKNESS = 7.20
HANDLE_CORNER_RADIUS = 8.0
HANDLE_FRONT_BED_X = -HEAD_Z_SHIFT
HANDLE_FRONT_TOP_X = HANDLE_FRONT_BED_X + HANDLE_THICKNESS
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
    clip = (
        cq.Workplane("XZ")
        .polyline(
            [
                (HANDLE_REAR_X - 2.0, -1.0),
                (HANDLE_FRONT_BED_X - 1.0, -1.0),
                (HANDLE_FRONT_TOP_X + 1.0, HANDLE_THICKNESS + 1.0),
                (HANDLE_REAR_X - 2.0, HANDLE_THICKNESS + 1.0),
            ]
        )
        .close()
        .extrude(HANDLE_WIDTH, both=True)
    )
    return raw.intersect(clip).clean()


def build_head_local() -> cq.Workplane:
    """The U-head before its local U/Y/W frame is tilted into world XYZ."""
    crown = _rounded_prism(
        HEAD_LENGTH,
        HEAD_WIDTH,
        HEAD_THICKNESS,
        HEAD_CORNER_RADIUS,
        HEAD_CENTER_U,
    )
    neck = _rounded_prism(
        NECK_LENGTH,
        NECK_WIDTH,
        HEAD_THICKNESS,
        NECK_CORNER_RADIUS,
        NECK_CENTER_U,
    )
    outer = crown.union(neck).clean()

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
    return outer.cut(slot_straight.union(slot_root)).clean()


def build_head() -> cq.Workplane:
    """Tilt the complete head so its broad faces cross the layer stack at 45°."""
    # CadQuery's -Y rotation maps +U toward both +X and +Z.  This shift puts
    # the neck's lowest rear edge exactly on Z=0; most of that rear length is
    # buried in the handle, leaving a wide fused root before the head emerges.
    return (
        build_head_local()
        .rotate((0.0, 0.0, 0.0), (0.0, 1.0, 0.0), -HEAD_ANGLE)
        .translate((0.0, 0.0, HEAD_Z_SHIFT))
    )


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
    if not math.isclose(JAW_DEPTH, JAW_GAP, abs_tol=1e-9):
        raise ValueError("U depth must remain exactly one jaw diameter")
    if not math.isclose(HEAD_FRONT_U, JAW_MOUTH_U, abs_tol=1e-9):
        raise ValueError("fork arms must end with the U mouth")

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
