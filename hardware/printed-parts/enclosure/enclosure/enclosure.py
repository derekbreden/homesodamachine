"""Thin Edition enclosure — a tall, narrow PETG box, split into four printable
pieces (front/back × bottom/top) that telescope and pin together at two corner stacks.

WIDTH, HEIGHT and DEPTH are all BOUNDS, not consequences — `appliance_width` struck
symmetric about x = 0, `appliance_height` from the floor slab's underside to the top
wall's outer face, and `rear_plane_y` fixing the back while the front wall reaches the
pump cradle's plane from its interior datum. The contents do
not set them; they have to fit inside, and `_dims` measures every one of them against
the pack and enters the reading in `BOUNDS`. The box comes out at its stated size
either way, so a pack that overran it gets a wall drawn through it.

Three bodies stand on the floor slab — the compressor and the condenser side by side
across the front, and the cold core behind them. The Y seam's corner stacks occupy its
overlap in Y, the lower from the handhold ceiling to the Z seam and
the upper from over the tap-water line to the roof. A body is held one `side_band_inset`
off the wall where it meets their footprint in Y and Z; outside that footprint the band is
the wall's own air. The cold core meets the lower stack and is held off it; the compressor
stands under the front column and the condenser is not on the slab at all. The core is the widest of the three
even yawed a quarter turn (`enclosure_assembly.FOAM_YAW`), which is what puts its 181 mm
short face across the machine instead of its 283 mm long one. The pack is placed by
`../../../manifold-layout/enclosure_assembly.py`. Features:

  * A 30° machine-display plane between tangent front and roof curves. Rounded
    side edges meet the fluted walls; the rear top edge remains square. The
    rounded bezel snaps into the recessed plane, ahead of the inset funnel.
  * A front↔back split at the stated `y_seam`, so its machinery is aft of the
    front pack and a front-quadrant tray never has to be notched around it:
    the front pieces' aft walls telescope (a full-wall lip,
    nothing shaved) into the back pieces — a proud tongue on the side walls and
    ceiling, and on the floor, where the cold core rides the cavity side and a
    proud tongue cannot, a full-thickness tongue that ends square inside the slab
    (`_floor_tongue`). Each ±X corner of the seam is a STACK of knuckles that
    alternate between the front and back pieces, sliding past one another as
    the halves telescope, held by two vertical M5 rods: the lower driven up
    from the handhold ceiling through front-bottom's knuckle into an insert in
    back-bottom's knuckle under the Z seam, the upper down from back-top's
    roof into an insert in front-top's knuckle under the funnel frame. Each
    ordinary screw seats its head on a printed floor and runs in an as-printed
    clearance passage (`_y_stacks`).
  * A bottom↔top split per column that SLIDES HOME and takes no screw, at ONE
    stated height both sides of the Y seam (`z_seam`, one level line round the
    box). The BOTTOM pieces carry the lip — a 3-sided band, their outer ±Y
    wall + both side walls, stopping short of the Y-seam overlap — with a
    HOOKED RAIL on each flank's straight run: an ARM standing on the mouth
    whose HEAD steps outboard over the groove (`_z_rail_heads`). The TOP
    pieces run their wall to the mouth at full section — the FOOT — with a
    notch above it that swallows that head (`_z_rail_feet`,
    `_z_rail_channels`). THE TWO COLUMNS ARE MIRRORED: front-top enters fore of
    home and slides AFT over the front wall's own plane, back-top enters aft of
    home and slides FORE over the rear wall's — each to the stop block closing
    its own far end; the end walls and corner turns close head-on behind it, the
    same telescoping mate the Y seam makes, arrived at along Y. Lifting a seated
    top lands each foot's flat top on its head's flat underside down both whole
    runs. A top comes off the way it went on, toward the end of the box it
    stands at — front-top forward into open air, back-top aft — so neither is
    lifted over the other and neither asks the box to come out from under
    whatever it is built under. Front-top is held by the two upper rods
    alone, so with those two out it draws off the front. A WALL THAT
    LIP STANDS ON IS `2 * wall` THICK, floor slab to lip rim
    (`_lip_underwall`): the lip is a skin standing proud of the interior
    face, and a skin that began at the seam would land its underside in air —
    a soffit round three sides of a piece that prints floor-down. Carried to
    the slab it is a wall instead, and there is nothing in a bottom piece for
    the bed to bridge.

The walls stand off the bodies rather than on them — one side band at the ±X
walls, one wall at the back — because a body on the floor spans the interior wall
to wall, so a wall on its face would leave the seam machinery nowhere to stand.
The cold core seats flush against the seams instead, and stands flat on the floor slab — its bottom cap's lid is a plane and
every cap screw is down in a counterbore, so nothing goes under it. The ±X bands'
own seam furniture fences it sideways, the back Z seam's lip behind, and the floor's
two core lugs (`_core_fence`) ahead. The floor that core stands on is flat: the
Y seam's floor tongue stays within the slab and ends square, rather than standing
proud of its cavity-side face.

Three pieces print on their Z− FACE — the bottom pieces floor-down on the slab,
front-top mouth-down on its seam rim — and back-top prints on its Z+ face, its
ceiling on the bed. The build axis is the box's own Z on every piece and the sign
is the piece's (`print_up`): where it is +Z the face that hangs is the one looking
DOWN, where it is −Z the one looking UP, and every 45° relief in this file is
struck on the side that hangs for its piece. The anti-warp corner relief goes on
the arrises that run along the build axis: the box's four standing verticals. Each quadrant owns only two of them —
its other two "corners" are the Y-seam, a telescoping mating face with no
exterior arris to relieve — so the front pieces round the front-left/right
verticals, the back pieces the back-left/right, and every seam stays square.
The display plane meets rounded side edges, which continue into the fluted
walls. The rear top edge remains square.

Inside those same verticals stand the COLUMNS, and each is that relief MIRRORED —
congruent with it, a QUARTER TURN of the same radius, swung from the interior
corner because that is the only place such a turn fits with its ends on the two
inner faces. Two sharp corners and one arc between them, the corner behind it
solid, floor slab to ceiling. They are the cavity's own shape (`_cavity`), so everything held inside
it meets a column the way it meets a wall: a mount inside the footprint is the
column's material with only its bore left. At a front corner the rail channel's
deep lane passes through the pillar's flank side on its way to the stop, the one
mark the slide leaves on one.

A knuckle is a block of one piece standing in the other's overlap: a front knuckle
roots fore of the seam in its own flank and runs aft inside the back piece's skin, a
back knuckle grows out of that skin and its flank. Every face between knuckles keeps a
running fit, so the halves telescope. Back-bottom holds the lower screw at both ends,
capturing front-bottom between them. Front-top holds the upper screw's head and insert,
capturing back-top's middle knuckle. All four screws are fully threaded M5 × 100.

A Z seam is held shut along its whole run rather than pinned at its ends: the
rails' hooks bear over every millimetre both flanks carry, and the stop
blocks and end walls close the travel. At each Y-seam corner the upper screw pins
front-top to back-top, retaining front-top on its slide.

The enclosure program, `enclosure.rs`, cuts every printed piece from the declared Box
with the typed recipes in `recipe/`, then the enclosure model the site draws. This module
is the description the assembly, Box and bill-of-materials steps read.
"""
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "printed-parts/enclosure/enclosure"), str(_hardware / "printed-parts/cadlib")]
import _rust_part
_rust_part.start()
from _enclosure_compiled import compiled as _compiled

_rust_enclosure_module = 'enclosure'

def __getattr__(name):
    if name == "__all__":
        return _compiled('enclosure', action="public-names")
    if name.startswith("__"):
        raise AttributeError(name)
    try:
        return _compiled('enclosure', action="get", path=(name,))
    except ValueError as error:
        raise AttributeError(name) from error

from _enclosure_compiled import install as _install
_install(_sys.modules[__name__])
