"""Nozzle-gate tray: 2 axis-aligned Beduan valves + 2 parallel Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates as a
tray. This is the bag-circuit tray (`../bag-circuit-tray/`) with one valve
column removed: a single −X column (V-G over V-J) feeds the two parallel
dividers (Y-D, Y-G) in the center; the dividers' +X outlets leave the tray to
the pumps and nozzles.

    V-G ┐
        ├  Y-D  ─→
    V-J ┘
        ├  Y-G  ─→

The valve placement, divider orientation, and tray construction are shared
with the bag-circuit tray. Origin = cell center, Z = 0 the mounting plane.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw,
    _hw / "printed-parts" / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import bag_circuit_tray as bc

# One valve column (−X) + the two center dividers; the +X column is gone.
VALVES = {"VG": (-bc.Vx, +bc.row_half), "VJ": (-bc.Vx, -bc.row_half)}
DIVIDERS = {"YD": (0.0, +bc.row_half), "YG": (0.0, -bc.row_half)}

plate_x = (-bc.plate_half_x, bc.cut_half_x)   # trimmed on +X — no valves there
plate_y_half = bc.plate_half_y
gap_x = (-bc.cut_half_x, bc.cut_half_x)
gap_y_half = bc.cut_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    parts = {nm: bc.place_valve(*p) for nm, p in VALVES.items()}
    parts.update({nm: bc.place_divider(*p) for nm, p in DIVIDERS.items()})
    return parts


def build_nozzle_gate_tray():
    return bc.build_tray(list(VALVES.values()), plate_x, plate_y_half, gap_x, gap_y_half)


def main():
    export_step(build_nozzle_gate_tray(), str(_here.parent / "nozzle-gate-tray.step"))
    print("-> nozzle-gate-tray.step")


if __name__ == "__main__":
    main()
