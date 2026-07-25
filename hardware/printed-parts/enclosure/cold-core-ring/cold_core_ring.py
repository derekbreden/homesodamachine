"""Cold-core support ring — the printed seat the cold core lands on at the back
of the enclosure floor.

The cold core's bottom foam cap is fastened to the outer shell by six M3 SHCS
driven up from below, so the assembly's lowest surface is not its bottom lid: it
is six screw heads standing proud of that lid. This part is the plane those heads
are missing. A closed bearing rail carries the lid's own perimeter — the line
where the bottom cap's outer wall stands — six wells swallow the heads, and two
front lugs fence the core forward.

Nothing else needs fencing, and nothing fastens the ring. The enclosure's Y-seam
corner posts and Z-seam pin pods stand in the side bands with their inboard faces
on x = 0 and x = footprint_x — the footprint's own edges — at three Y stations
per wall, and they are the X fence for the core and for the ring. Behind, the
core's rear face already seats on the back Z-seam lip's inner face. The ring's
own fore-and-aft key is a pair of ears reaching into the side band between two of
those pods.

The ring is one part rather than a floor feature because the enclosure floor is
not one part here: the box's Y seam falls inside the core's own footprint, so a
rail cast into the floor would print in two pieces and the core's seat would
carry the seam's Z tolerance. Dropped in whole, the bearing plane is a single
print and the ring bridges the two bottom pieces.

Frame: +X right, +Y back, +Z up. Origin at the FOOTPRINT's front-left corner on
the enclosure floor — the same point the foam assembly's own origin lands on, so
the ring places at the core's (x, y) and the core places one `seat_z` above it.
The ears and the front lugs reach outboard of the footprint, so the part's
bounding box runs negative in both X and Y.

Run:
    tools/cad-venv/bin/python \\
        hardware/printed-parts/enclosure/cold-core-ring/cold_core_ring.py
"""

import math
import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure-assembly"))
sys.path.insert(0, str(_hw.parent / "tools"))
from _cadq_export import export_step
from docgen import substitute_md
from _cold_core_interface import (
    attachment_xy_positions,
    corner_round_radius,
    outer_shell_x_length,
    outer_shell_y_length,
)
import _contents


# --- the footprint this ring captures ---------------------------------------
# The cold core's own outer shadow, read from the interface that owns it, so the
# seat and the thing seated cannot be drawn to different rectangles.
footprint_x = outer_shell_x_length
footprint_y = outer_shell_y_length
footprint_r = corner_round_radius

# The cap screws: six M3 × 25 DIN 912 SHCS threading up through the bottom
# foam-cap stack into the outer shell's bottom-face inserts. Their heads are the
# assembly's true lowest surface.
head_dia = 5.5               # DIN 912 M3 head
head_len = 3.0               # how far a head stands below the bottom cap's lid
head_well_clear = 2.75       # air around a head, radially
head_floor_gap = 2.0         # head tip to the enclosure floor the ring stands on

# The lift. Not a chosen height: a head hangs its whole length through the rail
# and still has to miss the floor the rail stands on.
seat_z = head_len + head_floor_gap
well_dia = head_dia + 2.0 * head_well_clear

# The bearing rail. Its outer edge is the footprint edge, because that is where
# the bottom cap's perimeter wall stands — everywhere inboard of it the cap's lid
# is an unsupported plate over pour foam.
rail_w = 20.0
rail_inner_r = 4.0

# The front lugs — the core's fence ahead. Only ahead: the enclosure's rear
# standoff band cannot hold a curb, because the box's rear wall is placed one
# standoff behind the REARMOST content and a curb standing in that band simply
# pushes the wall back off it. Behind, the core is fenced by the back Z-seam's
# lip, whose inner face its rear face already seats against; ahead there is
# nothing, and these are it.
#
# Discontinuous on purpose: the band ahead of the core at floor height is the
# machine corridor's aft mouth, where the evaporator stubs and the water-in line
# cross to the core's front face.
lug_rise = 8.0                          # lug standing proud of the seat
lug_z = seat_z + lug_rise
lug_t = 3.0
seat_slip = 0.5                         # Y air the core drops into, taken at the front
# Symmetric about the footprint's centre line, and inset clear of the corner
# wells, which open diagonally out of the footprint's corners.
lug_w = 60.0
lug_inset = 20.0

# The enclosure's side bands, where its seam posts stand on the footprint's ±X
# edges — the core's X fence and this ring's, which is why the ring is the
# footprint's shadow in X.
side_band = _contents.SIDE_RIB_INSET
wall_slip = 0.5                         # air between an ear's end face and the side wall

# The window those posts leave open in the side band, in this frame: solid from
# y = 2 up to here (the front column's aft Z pod, then the Y-seam corner column,
# then the back column's forward Z pod) and solid again from the far bound back
# to the rear wall. Measured off the box, not chosen — the ears run this window.
side_band_open_y0 = 54.7
side_band_open_y1 = 167.7

# The ears — the ring's own Y key. Each runs the open window less a travel
# allowance at both ends, so the ring can move that far and no further before a
# pod stops it, and its head wells stay over the screws they swallow.
ear_travel = 4.0
ear_reach = side_band - wall_slip
ear_y0 = side_band_open_y0 + ear_travel
ear_y1 = side_band_open_y1 - ear_travel


def _rounded_slab(x0, x1, y0, y1, z0, z1, r):
    slab = (cq.Workplane("XY")
            .box(x1 - x0, y1 - y0, z1 - z0, centered=False)
            .translate((x0, y0, z0)))
    return slab.edges("|Z").fillet(r) if r > 0 else slab


def build_rail():
    """The bearing plane: the footprint's shadow, hollowed to a band `rail_w`
    wide. The core's bottom lid lands on its top face at `seat_z`."""
    outer = _rounded_slab(0.0, footprint_x, 0.0, footprint_y, 0.0, seat_z, footprint_r)
    window = _rounded_slab(rail_w, footprint_x - rail_w, rail_w, footprint_y - rail_w,
                           -1.0, seat_z + 1.0, rail_inner_r)
    return outer.cut(window)


def build_ears():
    """The ring's own Y key: one pad per side reaching into the enclosure's side
    band, at seat height, spanning the window its Z-seam pin pods leave open."""
    ears = None
    for x0, x1 in ((-ear_reach, 0.0), (footprint_x, footprint_x + ear_reach)):
        ear = (cq.Workplane("XY")
               .box(x1 - x0, ear_y1 - ear_y0, seat_z, centered=False)
               .translate((x0, ear_y0, 0.0)))
        ears = ear if ears is None else ears.union(ear)
    return ears


def build_front_lugs():
    """The two front stops, standing from the floor to `lug_z` at the footprint's
    front edge with `seat_slip` of air, so the core drops in rather than presses
    in. They carry their own foot: the rail stops at the footprint edge, and a
    lug outboard of it would otherwise stand on nothing."""
    y0 = -seat_slip - lug_t
    lugs = None
    for x0 in (lug_inset, footprint_x - lug_inset - lug_w):
        lug = (cq.Workplane("XY")
               .box(lug_w, lug_t, lug_z, centered=False)
               .translate((x0, y0, 0.0)))
        lugs = lug if lugs is None else lugs.union(lug)
    return lugs


def head_stations():
    """The six cap-screw positions in this part's frame, each with the outward
    direction its well opens along — read from the shell interface that places
    the screws, so a station cannot drift from the boss it clears.

    A well opens toward whichever edges the station stands nearer than the bore's
    own diameter, because those are exactly the edges the bore would otherwise
    leave a sliver of rail outboard of. The four corner bosses are near both; the
    two mid-side bosses only their long edge."""
    out = []
    for x, y in attachment_xy_positions:
        sx = math.copysign(1.0, x) if footprint_x / 2.0 - abs(x) < well_dia else 0.0
        sy = math.copysign(1.0, y) if footprint_y / 2.0 - abs(y) < well_dia else 0.0
        out.append((x + footprint_x / 2.0, y + footprint_y / 2.0, sx, sy))
    return out


def build_head_wells():
    """The six wells a cap-screw head hangs in — a bore at each station plus a
    slot running outward from it, so a station nearer its edge than the bore's
    own radius opens as a notch instead of leaving a sliver of rail standing
    outboard of it. Every corner station is such a station: its boss is tangent
    to the footprint's corner arc."""
    reach = footprint_r + well_dia
    tall = lug_z + 1.0
    wells = None
    for cx, cy, sx, sy in head_stations():
        cut = (cq.Workplane("XY").circle(well_dia / 2.0).extrude(tall)
               .translate((cx, cy, -0.5)))
        if (sx, sy) != (0.0, 0.0):
            # A slot drawn along +Y from the station, turned until +Y lies on (sx, sy).
            cut = cut.union(
                cq.Workplane("XY")
                .box(well_dia, reach, tall, centered=(True, False, False))
                .rotate((0, 0, 0), (0, 0, 1), math.degrees(math.atan2(sy, sx)) - 90.0)
                .translate((cx, cy, -0.5)))
        wells = cut if wells is None else wells.union(cut)
    return wells


def build():
    """Rail, ears and lugs, less the wells: one solid, printed flat on its floor
    face."""
    ring = build_rail().union(build_ears()).union(build_front_lugs())
    return ring.cut(build_head_wells())


def main():
    ring = build()
    solid = ring.val()
    bb = solid.BoundingBox()
    volume = solid.Volume()
    print("Cold-core support ring")
    print(f"  Bounding box: X [{bb.xmin:.2f}, {bb.xmax:.2f}]  "
          f"Y [{bb.ymin:.2f}, {bb.ymax:.2f}]  Z [{bb.zmin:.2f}, {bb.zmax:.2f}]")
    print(f"  Footprint captured: {footprint_x:g} × {footprint_y:g}, r{footprint_r:g} corners")
    print(f"  Seat {seat_z:g}, lug {lug_z:g}, rail {rail_w:g} wide, wells ⌀{well_dia:g}")
    print(f"  Volume {volume / 1000.0:.1f} cm³ — {volume * 1.27e-3:.0f} g solid PETG")
    for cx, cy, sx, sy in sorted(head_stations()):
        print(f"    well at ({cx:8.3f}, {cy:8.3f}) opening ({sx:+.0f}, {sy:+.0f})")

    out = _here.parent / "cold-core-ring.step"
    export_step(ring, str(out))
    print(f"-> {out.name}")

    substitute_md(
        _here.parent / "README.md",
        variables={
            "FOOTPRINT_X": f"{footprint_x:.4g}",
            "FOOTPRINT_Y": f"{footprint_y:.4g}",
            "SEAT_Z": f"{seat_z:.4g} mm",
            "LUG_Z": f"{lug_z:.4g} mm",
            "RAIL_W": f"{rail_w:.4g} mm",
            "WELL_DIA": f"{well_dia:.4g} mm",
            "HEAD_LEN": f"{head_len:.4g} mm",
            "SIDE_BAND": f"{side_band:.4g} mm",
            "RING_MASS": f"{volume * 1.27e-3:.0f} g",
            "RING_ENVELOPE": f"{bb.xlen:.0f} × {bb.ylen:.0f} × {bb.zlen:.0f} mm",
        },
        expected_counts={
            "FOOTPRINT_X": 1, "FOOTPRINT_Y": 1, "SEAT_Z": 2, "LUG_Z": 2,
            "RAIL_W": 1, "WELL_DIA": 1, "HEAD_LEN": 2, "SIDE_BAND": 1,
            "RING_MASS": 1, "RING_ENVELOPE": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
