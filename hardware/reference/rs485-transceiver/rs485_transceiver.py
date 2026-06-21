"""Reference solid for the ALMOCN TTL-to-RS485 auto-direction transceiver
(bom: B09998FY4X), 1x on the controller tray — base side of the SIG-7 link to
the front 4.3" config display.

A tiny breakout with no mounting holes — it rides on adhesive / tucks under a
neighbour, so ``holes`` is empty (no heat-set bosses; rests on the floor).
**Geometry estimated**; verify by caliper.

Frame: X = length, Y = width, Z up from the PCB underside; origin at the
footprint centre, Z = 0 the seating plane.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step

name = "rs485"
length = 40.0
width = 18.0
pcb_t = 1.6
envelope_z = 11.0
pin_drop = 2.5
holes = []             # no mounting holes — adhesive / tucked


def build():
    pcb = cq.Workplane("XY").box(length, width, pcb_t, centered=(True, True, False))
    blk = (
        cq.Workplane("XY").box(12.0, 12.0, envelope_z - pcb_t, centered=(True, True, False))
        .translate((-length / 2.0 + 8.0, 0.0, pcb_t))
    )
    return pcb.union(blk)   # rests flat on the floor (no holes); no under-pins modelled


def main():
    export_step(build(), str(_here.parent / "rs485-transceiver.step"))
    print("-> rs485-transceiver.step")


if __name__ == "__main__":
    main()
