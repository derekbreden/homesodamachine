"""Reference solid for the chassis-ground ring-terminal stack — the physical
realization of the single-point "ground bus" on the electronics shelf.

This is not one SKU: it is the bolted stack that *is* the bus. An M3 × 10
stainless SHCS through a tooth washer clamps a fan of insulated ring terminals —
one green bond per exposed-metal part (pressure vessel, compressor body,
faucet SS plate, PSU chassis, + the C14 earth feed) — down
onto the heat-set insert in its own column of the top foam cap. The lugs are
bolted together, so they are equipotential to each other: the *stack* is the
bus, and the plastic column it sits on is electrically irrelevant — it only
provides the clamp reaction and the earthed thread. Modeled so the column's
purpose reads at a glance in the assembly.

Cables are intentionally omitted — only the ring tongues and crimp barrels are
shown; the green wire would crimp into each barrel and route off to its target.

Coordinate frame
----------------
- Z up, the screw axis on Z. Origin at the landing surface (the boss top) =
  Z = 0. Rings stack upward; the screw shank runs down into the insert (−Z).
- Drop at the tray's ``gnd`` boss top (floor_t + gnd_boss_h) in the assembly.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

# --- Stack geometry (standard M3 hardware + insulated ring terminals) ------
ring_count = 5          # one green bond per exposed-metal part + the C14 feed
fan_step = 60.0         # deg between successive lugs — a radial fan up the stud

eye_od = 8.0            # ring-terminal tongue outer diameter
hole_d = 3.2            # ring eye / washer bore (M3 clearance)
tongue_t = 0.8          # tongue (and washer) thickness — sets the stack pitch
barrel_d = 4.2          # insulated crimp-barrel diameter (16 AWG green)
barrel_len = 6.0        # barrel stub — no wire past it

washer_od = 7.0         # external-tooth washer over the top lug
washer_t = 0.8

head_d = 5.5            # M3 socket-head cap screw head
head_h = 3.0
shank_d = 3.4           # fills the eyes/washer (slightly proud for a clean fuse)
engage = 6.0            # thread length down into the heat-set insert

# The mount pattern in the stack's own frame: ONE hole, on the screw's own axis, at the
# landing surface. The stack IS its screw — the lugs are clamped by it and there is nothing
# else to fasten — so what holds this body is a single threaded column under the origin.
holes = [(0.0, 0.0)]


def _ring(z0, ang):
    """One ring terminal: a flat eye (bore on Z) + a crimp-barrel stub on +X,
    its base at z0, rotated ``ang`` about the stud axis."""
    eye = (
        cq.Workplane("XY").cylinder(tongue_t, eye_od / 2.0, centered=(True, True, False))
        .translate((0, 0, z0))
    )
    eye = eye.cut(
        cq.Workplane("XY").cylinder(tongue_t + 2, hole_d / 2.0, centered=(True, True, False))
        .translate((0, 0, z0 - 1))
    )
    barrel = (
        cq.Workplane("XY").cylinder(barrel_len, barrel_d / 2.0, centered=(True, True, False))
        .rotate((0, 0, 0), (0, 1, 0), 90.0)            # axis Z -> +X
        .translate((eye_od / 2.0 - 1.0, 0.0, z0 + barrel_d / 2.0))  # barrel bottom on the tongue plane
    )
    return eye.union(barrel).rotate((0, 0, 0), (0, 0, 1), ang)


def landing():
    """The top of the lug fan, in the stack's OWN frame: `(position, outward axis)` — where the
    next ring terminal goes on and the screw comes down. `build` stands the washer on it."""
    return ((0.0, 0.0, ring_count * tongue_t), (0.0, 0.0, 1.0))


def build():
    part = _ring(0.0, 0.0)
    for i in range(1, ring_count):
        part = part.union(_ring(i * tongue_t, i * fan_step))
    top = landing()[0][2]

    washer = (
        cq.Workplane("XY").cylinder(washer_t, washer_od / 2.0, centered=(True, True, False))
        .translate((0, 0, top))
    )
    washer = washer.cut(
        cq.Workplane("XY").cylinder(washer_t + 2, hole_d / 2.0, centered=(True, True, False))
        .translate((0, 0, top - 1))
    )
    part = part.union(washer)

    head_z = top + washer_t
    shank = (
        cq.Workplane("XY").cylinder(head_z + engage, shank_d / 2.0, centered=(True, True, False))
        .translate((0, 0, -engage))
    )
    head = (
        cq.Workplane("XY").cylinder(head_h, head_d / 2.0, centered=(True, True, False))
        .translate((0, 0, head_z))
    )
    return part.union(shank).union(head)


def main():
    export_step(build(), str(_here.parent / "ground-ring-stack.step"))
    print("-> ground-ring-stack.step")


if __name__ == "__main__":
    main()
