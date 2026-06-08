"""BiB-gate tray: 2 axis-aligned Beduan valves + 4 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) BiB gates as a tray.
A single −X column (V-K-A over V-K-B) feeds two Tees per row, butted in series:
the near-valve Tee (Y-KA / Y-KB) takes the valve on its −X run end, and a
second Tee (Y-C / Y-F) butts against its +X run end. Every Tee's run lies along
X and its branch rises (+Z) — the near-valve branches are the V-C / V-D inlets
from a source-select tray stacked above; the far branches and +X run ends leave
the tray to the pump and the channel-select line.

    V-K-A ──┬──┬──→     Y-KA · Y-C  (branches ↑)
            ┊
    V-K-B ──┴──┴──→     Y-KB · Y-F  (branches ↑)

Valve placement, the Tee placer, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/). Origin = cell center, Z = 0 the
mounting plane, ports at Z = 11.3.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "beduan-solenoid",
    _hw / "printed-parts" / "valve-manifold" / "single-tray",
    _hw / "printed-parts" / "valve-manifold" / "bag-circuit-tray",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
import bag_circuit_tray as bc

# −X valve column + two Tees per row in series (near-valve Tee, then a Tee
# butted against its +X run port).
valves = {"VKA": (-bc.valve_x, +bc.row_half), "VKB": (-bc.valve_x, -bc.row_half)}
_yc_x = 2.0 * bc.tee_run_half        # second Tee center: its −X run butts the first
tees = {
    "YKA": (0.0, +bc.row_half),
    "YKB": (0.0, -bc.row_half),
    "YC": (+_yc_x, +bc.row_half),
    "YF": (+_yc_x, -bc.row_half),
}

_run_out_x = _yc_x + bc.tee_run_half               # +X run port of the far Tees
plate_x = (-bc.plate_half_x, _run_out_x)           # +X wall ends at the far Tee port
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    # Outlets point +X to the center Tees (V-K-A/V-K-B feed Y-KA/Y-KB); inlets
    # are from the BiB connectors (outer ports). Arrow (local +Y) -> +X = -90.
    parts = {nm: bc.place_valve(*p, -90.0) for nm, p in valves.items()}
    parts.update({nm: bc.place_tee(*p) for nm, p in tees.items()})
    return parts


def build_bib_gate_tray():
    return bc.build_tray(list(valves.values()), bc.tee_grooves(tees.values()), plate_x, plate_y_half)


def main():
    export_step(build_bib_gate_tray(), str(_here.parent / "bib-gate-tray.step"))
    print("-> bib-gate-tray.step")


if __name__ == "__main__":
    main()
