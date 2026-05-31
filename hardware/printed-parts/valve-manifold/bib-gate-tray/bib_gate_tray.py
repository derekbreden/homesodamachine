"""BiB-gate tray: 2 axis-aligned Beduan valves + 2 Tees + 2 Y-dividers.

The [fluid-topology](../../../topology/fluid-topology.md) BiB gates as a tray.
A single −X column (V-K-A over V-K-B) feeds a Tee on each row; the Tee run lies
along X (one end to the valve, the other to a Y-divider butted right against
it), and the Tee branch rises (+Z) — that branch is the V-C / V-D inlet from a
source-select tray stacked above. Each Y-divider's outlets leave the tray to
the pump and the channel-select line.

    V-K-A ──┬──┤Y-C├─→     (Y-KA Tee, branch ↑ ← V-C)
            ┊
    V-K-B ──┴──┤Y-F├─→     (Y-KB Tee, branch ↑ ← V-D)

The valve placement, fitting placers, and tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/). Origin = cell center, Z = 0 the
mounting plane, ports at Z = 11.3.
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

# −X valve column meets the Tee run ports (Tee-based column).
VALVES = {"VKA": (-bc.Vx_t, +bc.row_half), "VKB": (-bc.Vx_t, -bc.row_half)}
# Near-valve junctions are Tees (run along X, branch up).
TEES = {"YKA": (0.0, +bc.row_half), "YKB": (0.0, -bc.row_half)}
# Y-dividers butt against each Tee's +X run port (stem at +TEE_RUN_HALF).
_yc_x = bc.TEE_RUN_HALF + bc.DIV_HALF
DIVIDERS = {"YC": (+_yc_x, +bc.row_half), "YF": (+_yc_x, -bc.row_half)}

_div_out_x = _yc_x + bc.DIV_HALF                   # +X divider outlet reach
plate_x = (-bc.plate_half_x_t, _div_out_x + 4.0)   # +X reaches past Y-C / Y-F
plate_y_half = bc.plate_half_y
gap_x = (-bc.cut_half_x_t, _div_out_x + 4.0)
gap_y_half = bc.cut_half_y     # Y-dividers spread to |Y| = 31.6
stack_pitch = bc.stack_pitch


def build_assembly():
    parts = {nm: bc.place_valve(*p) for nm, p in VALVES.items()}
    parts.update({nm: bc.place_tee(*p) for nm, p in TEES.items()})
    parts.update({nm: bc.place_divider(*p) for nm, p in DIVIDERS.items()})
    return parts


def build_bib_gate_tray():
    return bc.build_tray(list(VALVES.values()), plate_x, plate_y_half, gap_x, gap_y_half)


def main():
    export_step(build_bib_gate_tray(), str(_here.parent / "bib-gate-tray.step"))
    print("-> bib-gate-tray.step")


if __name__ == "__main__":
    main()
