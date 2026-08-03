"""AC hub — the H / N / G mains distribution block: three Wago 221-413 lever nuts
on one printed plate.

It is a TRAY and not a fastened part. It carries no hold-down of its own: whatever
body ends up carrying it grows this footprint into itself, so the joint is printed
rather than screwed and there is no pattern for a panel to bore. The plate therefore
ends where the wells end, and its length is the three wells and the margin — nothing
here is sized for a driver to reach.

Each Wago stands on its butt end in a well that wraps its lower half on four
faces — both X and both Y — open at the top, so a lug drops in butt-first and its
wire ports face straight up. All three face the same way, and their wires leave
vertically, the way the board's JST headers beside them do. The plate ends where
the wells do; the wire half of each lug stands proud above them.

Local frame: X right, Y deep, Z up; origin at the floor's bottom-left corner,
Z = 0 the floor underside, floor top at ``floor_t``.
"""

import sys
from dataclasses import dataclass
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "wago-221-413",
    _hw / "printed-parts" / "cold-core",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import wago_221_413 as wago

# --- Hub parameters -------------------------------------------------------
floor_t = 3.0          # base-plate thickness — the seat the panel boss clamps
wall_t = 3.0           # well wall thickness
press = 0.15           # per-side press-fit clearance (validated on the valve trays)
margin = 2.0           # plate edge past the last feature

# Standing the lug on its butt end lands its own axes this way: X stays the
# lever-hinge axis, the closed body's height lies across the strip in Y, and the
# wire-entry axis points up. Everything below is in those terms.
stand_w = wago.width     # X — lever-hinge axis
stand_d = wago.height    # Y — closed body height, across the strip
stand_h = wago.depth     # Z — wire-entry axis, ports up

wago_engage = stand_h / 2.0   # butt half in the well; wire half stands proud
wago_slot_half = stand_w / 2.0 + wall_t + press      # well half-width in X
wago_pitch = 2.0 * wago_slot_half                    # neighbours share a wall face
wago_slot_half_y = stand_d / 2.0 + wall_t + press    # well half-depth in Y


@dataclass(frozen=True)
class Layout:
    """Placement in the hub's own frame. ``wago_places`` is one (cx, cy) well centre
    per lug, and it is the whole of the layout — the plate holds nothing else."""
    wago_places: tuple


def _abox(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from corner (x0,y0,z0) to (x1,y1,z1)."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _wago_well(cx, cy):
    """One Wago's butt-end well: four walls around the standing lug's lower half —
    both X and both Y — open at the top, where the wire half stands out. The lug
    bottoms on the floor, ports up under the bay's own opening above; its levers
    clear the wall and swing out the −Y face."""
    tower = _abox(cx - wago_slot_half, cx + wago_slot_half,
                  cy - wago_slot_half_y, cy + wago_slot_half_y,
                  floor_t, floor_t + wago_engage)
    cav = _abox(cx - (stand_w / 2.0 + press), cx + (stand_w / 2.0 + press),
                cy - (stand_d / 2.0 + press), cy + (stand_d / 2.0 + press),
                floor_t, floor_t + wago_engage + 40.0)
    return tower.cut(cav)


def _build_floor(L):
    """One rectangular plate, reaching the wells and no further — it ends where they do."""
    xs, ys = [], []
    for cx, cy in L.wago_places:
        xs += [cx - wago_slot_half, cx + wago_slot_half]
        ys += [cy - wago_slot_half_y, cy + wago_slot_half_y]
    return _abox(min(xs) - margin, max(xs) + margin,
                 min(ys) - margin, max(ys) + margin, 0.0, floor_t)


def build_hub(L):
    """Build the hub for a given Layout."""
    hub = _build_floor(L)
    for cx, cy in L.wago_places:
        hub = hub.union(_wago_well(cx, cy))
    return hub


# --- Layout ---------------------------------------------------------------
# Three wells abreast, neighbours sharing a wall face, and one `margin` of plate past the
# row at each end. There is nothing outboard of them: the plate's length is the row's.
_row_y = margin + wago_slot_half_y
LAYOUT = Layout(
    wago_places=tuple((margin + wago_slot_half + i * wago_pitch, _row_y) for i in range(3)),
)

# --- Stations, in the hub's own frame -------------------------------------
poles = ("H", "N", "G")          # the order the Wago row runs in


def lug(pole):
    """One lug's wire-entry face: `(position, outward axis)`. Each Wago bottoms on the floor in
    its well and stands its wire half proud, ports UP off the top of the standing body —
    `stand_h` over the floor's own top face."""
    cx, cy = LAYOUT.wago_places[poles.index(pole)]
    return ((cx, cy, floor_t + stand_h), (0.0, 0.0, 1.0))


def build_ac_hub():
    return build_hub(LAYOUT)


def main():
    hub = build_ac_hub()
    bb = hub.val().BoundingBox()
    print(f"   hub {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm — "
          f"{len(LAYOUT.wago_places)} Wago wells on a {floor_t:g} mm plate, "
          f"no hold-down of its own; a standing lug reaches "
          f"{floor_t + stand_h:.1f} mm up, ports at its top")
    export_step(hub, str(_here.parent / "ac-hub.step"))
    print("-> ac-hub.step")


if __name__ == "__main__":
    main()
