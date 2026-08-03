"""PCBA tray — the controller-board mount of the electronics shelf.

Carries the JLCPCB-assembled controller PCBA ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx),
85.05 × 72.85 mm as fabbed): four M3 heat-set standoff bosses under the board's
four electrically isolated plated mounting holes (MH1–MH4, 3.2 mm hole /
4.0 mm pad, a 78.0 × 66.3 mm rectangle) — M3 SHCS down through the board into
ruthex inserts, the board's bottom face seating on the boss tops. A single
convex-outline floor, no walls, heat-set bosses;
built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.
The 5 mm standoff clears the board's THT tails (XH wafers, the J10 screw
block, U10, BT1, J14's shield legs).

Local frame: the PCBA's own pcb frame (pcbX / pcbY exactly as in `pcba.tsx` —
outline x[−68, 17], y[−36.3, 36.5]), Z up, floor underside at Z = 0, so the
boss centres below are the MH1–MH4 coordinates verbatim. Connector openings
face the board edges: USB-C (J14) flush on the west edge, the J10 12 V screw
throats east — the tray leaves both edges open.
"""

import json
import struct
import sys
from pathlib import Path
from types import SimpleNamespace

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step
import module_tray as mt
from module_tray import Mount

# Board datum — pcba.tsx <board outline> + the MH1–MH4 <platedhole>s.
_outline_x = (-68.0, 17.0)
_outline_y = (-36.3, 36.5)
_holes_pcb = ((-64.5, 33.0), (13.5, 33.0), (13.5, -33.3), (-64.5, -33.3))
_centre = (sum(_outline_x) / 2.0, sum(_outline_y) / 2.0)
_thickness = 1.6
_GLB = _hw / "pcb" / "pcba" / "out" / "pcba.glb"


def _glb_component_boxes():
    """Every component's axis-aligned bounding box out of the fab model
    `hardware/pcb/pcba/out/pcba.glb` — one (xmin, xmax, ymin, ymax, zmin,
    zmax) per mesh node, in pcb frame, mm. The glTF POSITION accessors carry
    per-primitive min/max, so no mesh decoding: a node's bbox is its
    translation (+rotation/scale if any) applied to those extremes."""
    raw = _GLB.read_bytes()
    assert raw[:4] == b"glTF", "not a GLB"
    jlen = struct.unpack("<I", raw[12:16])[0]
    g = json.loads(raw[20:20 + jlen])
    accs, meshes = g["accessors"], g["meshes"]
    boxes = []
    for node in g.get("nodes", []):
        if "mesh" not in node:
            continue
        t = node.get("translation", (0.0, 0.0, 0.0))
        s = node.get("scale", (1.0, 1.0, 1.0))
        r = node.get("rotation")  # quaternion (x, y, z, w)
        lo = [float("inf")] * 3
        hi = [float("-inf")] * 3
        for prim in meshes[node["mesh"]]["primitives"]:
            a = accs[prim["attributes"]["POSITION"]]
            mn, mx = a["min"], a["max"]
            for corner in range(8):
                p = [mn[i] if corner >> i & 1 else mx[i] for i in range(3)]
                p = [p[i] * s[i] for i in range(3)]
                if r is not None:
                    x, y, z = p
                    qx, qy, qz, qw = r
                    p = [
                        x * (1 - 2 * (qy * qy + qz * qz)) + y * 2 * (qx * qy - qz * qw) + z * 2 * (qx * qz + qy * qw),
                        x * 2 * (qx * qy + qz * qw) + y * (1 - 2 * (qx * qx + qz * qz)) + z * 2 * (qy * qz - qx * qw),
                        x * 2 * (qx * qz - qy * qw) + y * 2 * (qy * qz + qx * qw) + z * (1 - 2 * (qx * qx + qy * qy)),
                    ]
                for i in range(3):
                    v = p[i] + t[i]
                    lo[i] = min(lo[i], v)
                    hi[i] = max(hi[i], v)
        boxes.append(tuple(1000.0 * v for v in (lo[0], hi[0], lo[1], hi[1], lo[2], hi[2])))
    return boxes


def _build_board():
    """The controller board as a simplified populated model: the fabbed
    outline slab + one box per component at the axis-aligned bounding box of
    its actual 3D model in `hardware/pcb/pcba/out/pcba.glb` (the full mesh
    detail stays in the glb; this carries every body's true footprint and
    height). The glb board slab itself is skipped — the outline slab with its
    MH1–MH4 holes stands in for it."""
    slab = cq.Workplane("XY").box(
        _outline_x[1] - _outline_x[0], _outline_y[1] - _outline_y[0], _thickness,
        centered=(True, True, False))
    for hx, hy in _holes_pcb:
        slab = slab.cut(
            cq.Workplane("XY").cylinder(_thickness + 1, 3.2 / 2.0, centered=(True, True, False))
            .translate((hx - _centre[0], hy - _centre[1], -0.5)))
    board_x = _outline_x[1] - _outline_x[0]
    board_y = _outline_y[1] - _outline_y[0]
    glb_top = 0.7  # glb board frame: slab mid at z=0, 1.4 thick fab board
    for x0, x1, y0, y1, z0, z1 in _glb_component_boxes():
        w, d = x1 - x0, y1 - y0
        if w < 0.2 or d < 0.2 or (z1 - z0) < 0.2:
            continue
        if w > board_x * 0.95 and d > board_y * 0.95:
            continue  # the glb's own board slab
        if z1 > glb_top + 0.05:      # body above the board top
            zb, ht = _thickness, z1 - glb_top
        elif z0 < -glb_top - 0.05:   # bottom-side body
            zb, ht = z0 + glb_top, -glb_top - z0
        else:
            continue                 # embedded/through geometry only
        slab = slab.union(
            cq.Workplane("XY").box(w, d, ht, centered=(False, False, False))
            .translate((x0 - _centre[0], y0 - _centre[1], zb)))
    return slab


board = SimpleNamespace(
    name="pcba",
    length=_outline_x[1] - _outline_x[0],
    width=_outline_y[1] - _outline_y[0],
    holes=tuple((hx - _centre[0], hy - _centre[1]) for hx, hy in _holes_pcb),
    hole_dia=3.2,
    build=_build_board,
)

MOUNTS = [Mount(board, _centre, 0.0)]


# --- The board's own stations -----------------------------------------------
# Two frames. `pcba.tsx` writes every pad and connector in the PCB FRAME; the board is DRAWN
# about its own outline centre, which is the datum its mount pattern and its box share. They
# differ by `_centre`, and `port` applies it — so a caller names a connector out of
# `pcba.tsx` verbatim.

def port(px, py) -> tuple:
    """A point in the board's `pcbX`/`pcbY` frame, as a station on the board's TOP FACE:
    `(position, outward axis)`.

    Every wafer, header and edge connector on this board mates off that face, so the axis is
    +Z and the height is the fab thickness — a station stands where a loom is pressed on, not
    where the copper is."""
    return ((px - _centre[0], py - _centre[1], _thickness), (0.0, 0.0, 1.0))


def stations_hold():
    """Hold the mating plane to the board this module draws.

    `port` measures `_thickness` up from zero, so zero has to be the board's underside. The
    drawn model is a slab plus one box per populated component, and a bottom-side body reaching
    below the slab would move that floor while every station stayed where it was."""
    floor = _build_board().val().BoundingBox().zmin
    if abs(floor) > 1e-9:
        raise ValueError(
            f"the board is drawn with its underside at z = {floor:.4f} and `port` measures "
            f"{_thickness:g} up from 0 — every connector station is off the mating face.")


def build_pcba_tray():
    return mt.build_module_tray(MOUNTS)


def main():
    tray = build_pcba_tray()
    export_step(tray, str(_here.parent / "pcba-tray.step"))
    print("-> pcba-tray.step (%.1f cm3)" % (tray.val().Volume() / 1000.0))


if __name__ == "__main__":
    main()
