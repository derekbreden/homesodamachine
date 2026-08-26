"""What one printed face keeps off another printed face.

ONE FIGURE, PER FACE. The box's Y seam and its two Z seams, the pump cartridge in its bay
and the cap screwed under it, the ceiling panel's dado, the faucet shell's split, every
cover plate laid into an inset — all struck on this.

The stock is Polymaker Fiberon PET-GF15 on a 0.4 mm tungsten carbide hotend, two loops to a
face at 0.42 and 0.45 (`printed-parts/enclosure/enclosure/print-log.md`).

WHAT A SITE NEEDS, IT DERIVES FROM THIS. A bore round a boss is `2 * slip` across. A plate
dropped in an inset is one `slip` at each of its four edges. A lap raked at 45 degrees is
given `slip * sqrt(2)` along the axis it is driven home on.

A DATUM TAKES NONE OF IT. The face a screw pulls shut, the foot landing on the shoulder
under it, the stop block a slide comes home against, the plate bearing on the land it is set
down on — each of those stands on the plane the two pieces share.
"""

#: The air one printed face keeps off the printed face it slides on or seats against.
slip = 0.15
