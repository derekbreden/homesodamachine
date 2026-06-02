"""Nozzle-gate tray: 2 axis-aligned Beduan valves + 2 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates as a
tray. A single −X column (V-G over V-J) meets a Tee on each row; the Tee run
lies along X (valve on the −X end), and the branch rises (+Z). The +X run end
and the branch leave the tray to the pump and the nozzle.

    V-G ──┬──→      Y-D run; branch ↑
    V-J ──┴──→      Y-G run; branch ↑

Valve placement, the Tee placer, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/) via `build_tray`. Origin = cell
center, Z = 0 the mounting plane, ports at Z = 11.3.
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

# One valve column (−X) + a Tee on each row.
VALVES = {"VG": (-bc.Vx, +bc.row_half), "VJ": (-bc.Vx, -bc.row_half)}
TEES = {"YD": (0.0, +bc.row_half), "YG": (0.0, -bc.row_half)}

plate_x = (-bc.plate_half_x, bc.TEE_RUN_HALF)   # +X wall ends at the Tee run port
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    # Outlets point -X to the nozzles (the outer ports); inlets are from the
    # center Tees. The valve flow arrow (local +Y) points -X.
    parts = {nm: bc.place_valve(*p, 90.0) for nm, p in VALVES.items()}
    parts.update({nm: bc.place_tee(*p) for nm, p in TEES.items()})
    return parts


def build_nozzle_gate_tray():
    return bc.build_tray(list(VALVES.values()), bc.tee_grooves(TEES.values()), plate_x, plate_y_half)


def main():
    export_step(build_nozzle_gate_tray(), str(_here.parent / "nozzle-gate-tray.step"))
    print("-> nozzle-gate-tray.step")


if __name__ == "__main__":
    main()
