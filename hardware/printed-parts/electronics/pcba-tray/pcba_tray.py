"""PCBA tray — the main board's bench mount, off the +X wall of back-top.

Carries the JLCPCB-assembled main board ([`pcba.tsx`](/hardware/pcb/pcba/pcba.tsx),
[85 × 72.8 mm](PCBA_SIZE) as fabbed): four M3 heat-set standoff bosses under the board's
four electrically isolated plated mounting holes (MH1–MH4, 3.2 mm hole /
4.0 mm pad, a 78.0 × 66.3 mm rectangle) — M3 SHCS down through the board into
ruthex inserts, the board's bottom face seating on the boss tops. A single
convex-outline floor, no walls, heat-set bosses;
built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.
The 5 mm standoff clears the board's THT tails (XH wafers, the J10 screw
block, U10, BT1, J14's shield legs).

The populated-board model carries those tails 2 mm below the PCB underside.
That underside remains the Z = 0 mounting datum; the tail envelope is what
keeps either a bench-tray floor or the appliance wall out from under it.

Local frame: the main board's own pcb frame (pcbX / pcbY exactly as in `pcba.tsx` —
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
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_py_comments
from module_tray import Mount, _boss_spec

# Board datum — pcba.tsx <board outline> + the MH1–MH4 <platedhole>s.
_outline_x = (-68.0, 17.0)
_outline_y = (-36.3, 36.5)
_holes_pcb = ((-64.5, 33.0), (13.5, 33.0), (13.5, -33.3), (-64.5, -33.3))
_centre = (sum(_outline_x) / 2.0, sum(_outline_y) / 2.0)
_thickness = 1.6
_hole_dia = 3.2
pin_drop = 2.0
_mount_boss_dia = _boss_spec(_hole_dia)[0]
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
    """The main board as a simplified populated model: the fabbed
    outline slab + one box per component at the axis-aligned bounding box of
    its actual 3D model in `hardware/pcb/pcba/out/pcba.glb` (the full mesh
    detail stays in the glb; this carries every body's true footprint and
    height). The glb board slab itself is skipped — the outline slab with its
    MH1–MH4 holes stands in for it.

    A through-hole component's glb box spans both sides of the board. Its body
    is kept above the top face and its wall-facing projection is kept separately
    as the 2 mm pin-tail envelope. Imported lead lengths vary by model, so that
    projection is capped at the assembly clearance this board states rather than
    letting one decorative component model move the PCB mounting datum. The four
    established boss footprints are cut back out: component AABBs are conservative
    rectangles, while the real MH1–MH4 lands must remain clear for the board to seat."""
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
    tails = None
    for x0, x1, y0, y1, z0, z1 in _glb_component_boxes():
        w, d = x1 - x0, y1 - y0
        if w < 0.2 or d < 0.2 or (z1 - z0) < 0.2:
            continue
        if w > board_x * 0.95 and d > board_y * 0.95:
            continue  # the glb's own board slab
        if z1 > glb_top + 0.05:      # body above the board top
            zb, ht = _thickness, z1 - glb_top
            slab = slab.union(
                cq.Workplane("XY").box(w, d, ht, centered=(False, False, False))
                .translate((x0 - _centre[0], y0 - _centre[1], zb)))
        if z0 < -glb_top - 0.05:     # pins/tails below the PCB underside
            zb = max(-pin_drop, z0 + glb_top)
            tail = (cq.Workplane("XY").box(w, d, -zb, centered=(False, False, False))
                    .translate((x0 - _centre[0], y0 - _centre[1], zb)))
            tails = tail if tails is None else tails.union(tail)
    if tails is not None:
        for hx, hy in _holes_pcb:
            tails = tails.cut(
                cq.Workplane("XY")
                .box(_mount_boss_dia, _mount_boss_dia, pin_drop + 1.0,
                     centered=(True, True, False))
                .translate((hx - _centre[0], hy - _centre[1], -pin_drop - 0.5)))
        slab = slab.union(tails)
    return slab


board = SimpleNamespace(
    name="pcba",
    length=_outline_x[1] - _outline_x[0],
    width=_outline_y[1] - _outline_y[0],
    holes=tuple((hx - _centre[0], hy - _centre[1]) for hx, hy in _holes_pcb),
    hole_dia=_hole_dia,
    pin_drop=pin_drop,
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

    `port` measures `_thickness` up from zero, so zero remains the PCB underside. The populated
    model deliberately continues `pin_drop` below it: that floor is the tail-clearance plane a
    wall or tray may approach, while every mounting hole remains on Z = 0."""
    floor = _build_board().val().BoundingBox().zmin
    if abs(floor + pin_drop) > 1e-9:
        raise ValueError(
            f"the board's tail envelope ends at z = {floor:.4f}, not {-pin_drop:g}; "
            "the placed solid no longer gives the mounting plane its stated below-board air.")


def main():
    substitute_py_comments(
        _here,
        variables={"PCBA_SIZE": f"{board.length:.4g} × {board.width:.4g} mm"},
    )
    print(f"-> {_here.name}")


if __name__ == "__main__":
    main()
