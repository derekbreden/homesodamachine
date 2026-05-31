"""BiB-gate tray: 2 axis-aligned Beduan valves + 4 parallel Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) BiB gates as a tray.
This is the nozzle-gate tray (`../nozzle-gate-tray/`) with a second pair of
dividers added on +X: a single −X column (V-K-A over V-K-B) feeds the center
dividers (Y-KA, Y-KB), which feed the +X dividers (Y-C, Y-F) in series; the
+X dividers' outlets leave the tray to the pumps and the channel-select line.

    V-K-A ┐
          ├  Y-KA ─ Y-C ─→
    V-K-B ┘
          ├  Y-KB ─ Y-F ─→

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

# One valve column (−X), the two center dividers, and a second divider pair on
# +X (where the bag-circuit tray's +X valves would sit), in series.
VALVES = {"VKA": (-bc.Vx, +bc.row_half), "VKB": (-bc.Vx, -bc.row_half)}
DIVIDERS = {
    "YKA": (0.0, +bc.row_half),
    "YKB": (0.0, -bc.row_half),
    "YC": (+bc.Vx, +bc.row_half),
    "YF": (+bc.Vx, -bc.row_half),
}

_div_out_x = bc.Vx + bc.DIV_HALF                 # +X divider outlet reach
plate_x = (-bc.plate_half_x, _div_out_x + 4.0)   # extend +X to clear Y-C / Y-F
plate_y_half = bc.plate_half_y
gap_x = (-bc.cut_half_x, _div_out_x + 4.0)
gap_y_half = bc.cut_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    parts = {nm: bc.place_valve(*p) for nm, p in VALVES.items()}
    parts.update({nm: bc.place_divider(*p) for nm, p in DIVIDERS.items()})
    return parts


def build_bib_gate_tray():
    return bc.build_tray(list(VALVES.values()), plate_x, plate_y_half, gap_x, gap_y_half)


def main():
    export_step(build_bib_gate_tray(), str(_here.parent / "bib-gate-tray.step"))
    print("-> bib-gate-tray.step")


if __name__ == "__main__":
    main()
