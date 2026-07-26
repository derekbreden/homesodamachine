"""AC hub — the H / N / G mains distribution block: three Wago 221-413 lever nuts
on one printed plate.

Two boss columns of the cold core's top foam cap carry it
(`_cold_core_interface.deck_mounts["ac-hub"]`), one either side of the foam-cap
lid's pour hole, which the plate spans. Everything else in the strip lands on
columns of that same cap with nothing printed beneath it — the controller PCBA,
the Mean Well PSU, Teyleten relay #1, and the ground ring-terminal stack.

Each Wago drops into a flat pocket that wraps its butt half on five faces — both
X, both Z, and the −Y end — open toward the wire end, so a lug slides in
butt-first and its wire ports and levers stay clear above. All three face the same
way. The plate ends where the buried butts do; the wire half of each lug hangs
past it over the lid.

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
from _cold_core_interface import deck_mount_xy, deck_mounts

# --- Hub parameters -------------------------------------------------------
floor_t = 3.0          # base-plate thickness — the seat the cap station clamps
wall_t = 3.0           # pocket wall thickness
press = 0.15           # per-side press-fit clearance (validated on the valve trays)
margin = 2.0           # plate edge past the last feature

# The hub's own hold-down: a clearance hole over each cap column. The SHCS head
# bears on the floor's top face, which is what `deck_mounts["ac-hub"].seat` is.
mount_clear_d = 3.4
mount_pad_d = 9.0

wago_engage = wago.depth / 2.0   # butt half buried; wire half hangs past the plate
wago_slot_half = wago.width / 2.0 + wall_t + press   # pocket half-width in X
wago_pitch = 2.0 * wago_slot_half                    # neighbours share a wall face


@dataclass(frozen=True)
class Layout:
    """Placement in the hub's own frame. ``wago_places`` is one (cx, butt_y) per
    pocket; ``mount_places`` is one (x, y) per cap column."""
    wago_places: tuple
    mount_places: tuple


def _abox(x0, x1, y0, y1, z0, z1):
    """Axis-aligned box from corner (x0,y0,z0) to (x1,y1,z1)."""
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def _wago_pocket(cx, by):
    """One Wago's butt-end pocket: five faces around the butt half — both X, both
    Z, and the −Y end — open toward +Y, where the wire half slides out. The lug
    lies flat, levers up, under the bay's own opening above."""
    e = wall_t + press
    hw = wago.width / 2.0
    tower = _abox(cx - (hw + e), cx + (hw + e), by - e, by + wago_engage,
                  floor_t, floor_t + wago.height + e)
    cav = _abox(cx - (hw + press), cx + (hw + press), by - press, by + wago_engage + 40.0,
                floor_t, floor_t + wago.height + press)
    return tower.cut(cav)


def _build_floor(L):
    """One rectangular plate, reaching the pockets and both hold-down pads and no
    further — it ends where the buried butts do."""
    xs, ys = [], []
    for cx, by in L.wago_places:
        xs += [cx - wago_slot_half, cx + wago_slot_half]
        ys += [by - (wall_t + press), by + wago_engage]
    for mx, my in L.mount_places:
        xs += [mx - mount_pad_d / 2.0, mx + mount_pad_d / 2.0]
        ys += [my - mount_pad_d / 2.0, my + mount_pad_d / 2.0]
    return _abox(min(xs) - margin, max(xs) + margin,
                 min(ys) - margin, max(ys) + margin, 0.0, floor_t)


def build_hub(L):
    """Build the hub for a given Layout."""
    hub = _build_floor(L)
    for cx, by in L.wago_places:
        hub = hub.union(_wago_pocket(cx, by))
    for mx, my in L.mount_places:
        hub = hub.cut(
            cq.Workplane("XY").center(mx, my).circle(mount_clear_d / 2.0).extrude(floor_t)
        )
    return hub


# --- Layout ---------------------------------------------------------------
# The two hold-down holes are spaced off the cap's OWN station pitch, so they land
# on the `ac-hub` columns by construction. They sit outboard of the Wago row, one
# at each end, open to a driver from above.
_span = (max(p[0] for p in deck_mount_xy("ac-hub"))
         - min(p[0] for p in deck_mount_xy("ac-hub")))
_row_y = margin + wall_t + press
_mount_y = _row_y + wago_engage / 2.0
_row_w = 3 * wago_pitch
_mount_x0 = margin + mount_pad_d / 2.0
LAYOUT = Layout(
    wago_places=tuple((_mount_x0 + (_span - _row_w) / 2.0 + wago_slot_half + i * wago_pitch,
                       _row_y) for i in range(3)),
    mount_places=((_mount_x0, _mount_y), (_mount_x0 + _span, _mount_y)),
)


def build_ac_hub():
    return build_hub(LAYOUT)


def main():
    hub = build_ac_hub()
    bb = hub.val().BoundingBox()
    print(f"   hub {bb.xlen:.1f} × {bb.ylen:.1f} × {bb.zlen:.1f} mm — "
          f"{len(LAYOUT.wago_places)} Wago pockets on "
          f"{len(deck_mount_xy('ac-hub'))} cap columns "
          f"(seat {deck_mounts['ac-hub'].seat:g} mm); a seated lug reaches "
          f"{LAYOUT.wago_places[0][1] + wago.depth:.1f} mm deep")
    export_step(hub, str(_here.parent / "ac-hub.step"))
    print("-> ac-hub.step")


if __name__ == "__main__":
    main()
