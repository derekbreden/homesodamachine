"""Per-face clearances for rigid printed mating parts.

AN ALLOWANCE IS SURFACE, NOT AIR. A printed face stands proud of its CAD face: press two
printed 1 mm parts together and they measure 2.15 mm. So 0.15 mm between two nominal faces is
a friction fit, hard to slide; sliding needs 0.25 and is still tight; an overhang's underside
sags into bumps and takes 0.25 more. Each allowance describes the surface of the face it is
on and stays on that face. It is not free space a stack can spend elsewhere, and a body
resting on a face rests on its rough surface, about where it is drawn.

Head-on assembly seats use `slip`; faces that slide past their mates use `running`.

Rough or oozed printed material occupies space beyond the nominal face. The modeled gap
provides room for that material at assembly. This applies to seating faces loaded by
gravity or screws as well as other mating faces.

The enclosure's reference stock is Polymaker Fiberon PET-GF15 on a 0.4 mm tungsten carbide
hotend, two loops to a face at 0.42 and 0.45
(`printed-parts/enclosure/enclosure/print-log.md`).

A bore adds twice its per-face clearance to the diameter. A plate in an inset has the
clearance at each edge. A lap raked at 45 degrees takes the clearance times `sqrt(2)`
along its insertion axis.

Rigid printed mating and seating faces receive the applicable static or sliding allowance,
including the additional allowance for each supported face. A locating datum, screw clamp,
bearing shoulder or travel stop does not waive those clearances.
A face printed against the build plate retains its base fit allowance without the
additional finish allowance used for a supported overhang.

Compliant gaskets and seals use their specified installed squeeze in the compression
direction rather than a rigid-fit clearance through their thickness.
"""

#: What two printed faces pressed together add to their nominal stack: a seat, a friction fit.
slip = 0.15

#: Additional clearance on each face that slides past its mate.
sliding_extra = 0.10

#: A face that slides past its mate: still a tight slide.
running = slip + sliding_extra

#: The sag and bumps of a supported overhang's underside, per supported mating face, assigned
#: once to either part of its gap.
supported_surface = 0.25

#: Additional clearance across the floor of a printed cavity a part slides to: the layers where
#: the floor turns up into the walls print slightly rounded, so the cavity narrows at its tip.
layer_transition = 0.10


def clearance(*, sliding=False, supported=False, at_floor=False):
    """One mating-face allowance, including motion, bridge finish and a cavity floor's rounded
    turn where present."""
    return (slip + (sliding_extra if sliding else 0.0)
            + (supported_surface if supported else 0.0)
            + (layer_transition if at_floor else 0.0))
