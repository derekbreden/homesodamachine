"""AC hub — the H / N / G mains distribution block: three Wago 221-413 lever nuts
on one printed plate.

It is HELD BY ITS PLATE: one M3 clearance hole at each end of the row, on the row's own
centre line, through a pad the plate's end grows into. The plate's underside is the seat,
and whatever carries the hub stands a boss under each hole — in the appliance that is a
boss off the enclosure's +X wall. The two holes are the whole pattern; the row is 75 mm
long, so a pair on its axis fixes the plate against every load a lever's throw puts on it.

Each Wago stands on its butt end in a well that wraps its lower half on four
faces — both X and both Y — open at the top, so a lug drops in butt-first and its
wire ports face straight up. All three face the same way, and their wires leave
vertically, the way the board's JST headers beside them do. The wire half of each lug
stands proud above the wells.

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

# --- the hold-down ---------------------------------------------------------
# One M3 clearance hole at each end of the row. `end_margin` is what the plate reaches past
# the last well ON THE ROW AXIS — the bore and one ring of plate all round it, so the pad is
# the hole plus its own material and nothing else. The hole sits at the pad's own centre.
hold_dia = 3.4         # M3 clearance
hold_ring = 2.5        # plate all round the bore
end_margin = hold_dia + 2.0 * hold_ring


@dataclass(frozen=True)
class Layout:
    """Placement in the hub's own frame. ``wago_places`` is one (cx, cy) well centre
    per lug; the two hold-downs follow from the row's own ends, so they are derived rather
    than listed and a lug added to the row carries them outward with it."""
    wago_places: tuple

    def hold_places(self) -> tuple:
        """The two hold-down bores, (cx, cy) — one at each end of the row, on the row's own
        centre line, each at the middle of the pad its end of the plate grows into."""
        xs = [cx for cx, _cy in self.wago_places]
        cy = self.wago_places[0][1]
        return ((min(xs) - wago_slot_half - end_margin / 2.0, cy),
                (max(xs) + wago_slot_half + end_margin / 2.0, cy))


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
    """One rectangular plate: the wells, and a hold-down pad at each end of the row.

    ACROSS the row it keeps `margin` and no more — nothing is fastened on that axis, so the
    plate ends where the wells do. ALONG it the plate reaches `end_margin`, which is the
    hold-down's bore and its ring, so the two pads are the only thing the outline carries
    that a well did not put there."""
    xs, ys = [], []
    for cx, cy in L.wago_places:
        xs += [cx - wago_slot_half, cx + wago_slot_half]
        ys += [cy - wago_slot_half_y, cy + wago_slot_half_y]
    return _abox(min(xs) - end_margin, max(xs) + end_margin,
                 min(ys) - margin, max(ys) + margin, 0.0, floor_t)


def build_hub(L):
    """Build the hub for a given Layout."""
    hub = _build_floor(L)
    for cx, cy in L.wago_places:
        hub = hub.union(_wago_well(cx, cy))
    for cx, cy in L.hold_places():
        hub = hub.cut(
            cq.Workplane("XY").cylinder(floor_t + 2.0, hold_dia / 2.0,
                                        centered=(True, True, False))
            .translate((cx, cy, -1.0)))
    return hub


# --- Layout ---------------------------------------------------------------
# Three wells abreast, neighbours sharing a wall face, and one hold-down pad past the row at
# each end. Nothing else stands on the plate: its length is the row's plus those two pads.
_row_y = margin + wago_slot_half_y
LAYOUT = Layout(
    wago_places=tuple((end_margin + wago_slot_half + i * wago_pitch, _row_y)
                      for i in range(3)),
)

# The mount pattern in the hub's own frame, on the plate's underside — the two bores a boss
# under each stands the plate on.
holes = list(LAYOUT.hold_places())

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
    holds = LAYOUT.hold_places()
    print(f"   hub {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm — "
          f"{len(LAYOUT.wago_places)} Wago wells on a {floor_t:g} mm plate, held by "
          f"{len(holds)} Ø{hold_dia:g} bores {holds[1][0] - holds[0][0]:.1f} mm apart on the "
          f"row's centre line; a standing lug reaches "
          f"{floor_t + stand_h:.1f} mm up, ports at its top")
    export_step(hub, str(_here.parent / "ac-hub.step"))
    print("-> ac-hub.step")


if __name__ == "__main__":
    main()
