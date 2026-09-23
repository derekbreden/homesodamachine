"""Per-face clearances between mating parts.

Assembly seats use `slip`; moving service fits use `running`.

The stock is Polymaker Fiberon PET-GF15 on a 0.4 mm tungsten carbide hotend, two loops to a
face at 0.42 and 0.45 (`printed-parts/enclosure/enclosure/print-log.md`).

A bore adds twice its per-face clearance to the diameter. A plate in an inset has the
clearance at each edge. A lap raked at 45 degrees takes the clearance times `sqrt(2)`
along its insertion axis.

A DATUM TAKES NONE OF IT. The face a screw pulls shut, the foot landing on the shoulder
under it, the stop block a slide comes home against, the plate bearing on the land it is set
down on — each of those stands on the plane the two pieces share.
"""

#: Assembly clearance at a printed seat.
slip = 0.15

#: Additional clearance on each face that slides past its mate.
sliding_extra = 0.10

#: Clearance on each face of a moving service fit.
running = slip + sliding_extra

#: Extra room per supported mating face, assigned once to either part of its gap.
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
