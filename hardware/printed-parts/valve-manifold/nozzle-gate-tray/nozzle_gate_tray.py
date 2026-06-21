"""Nozzle-gate tray: 2 axis-aligned Beduan valves + 2 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates as a
tray. A single −X column (V-G over V-J) meets a Tee on each row. Y-D seats run
along X (valve on the −X end) with its branch up (+Z). Y-G instead plugs its
**branch into V-J's inner port** — its run no longer butts the valve — then its
run swings 45° about that branch (X) axis.

    V-G ──┬──→        Y-D: run along X, branch ↑
    V-J ──● Y-G       Y-G: branch butts V-J's inner port, run swung 45° about X

Valve placement, the Tee placers, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/) via `build_tray`. Origin = cell
center, Z = 0 the mounting plane, ports at Z = 11.3.
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
    _hw.parent / "tools",
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_step
from docgen import substitute_md
import bag_circuit_tray as bc

# One valve column (−X) + a Tee on each row.
valves = {"VG": (-bc.valve_x, +bc.row_half), "VJ": (-bc.valve_x, -bc.row_half)}
tees = {"YD": (0.0, +bc.row_half), "YG": (0.0, -bc.row_half)}
yg_spin = 45.0  # YG run swung this many deg about its branch (X) axis

# The tray floors and walls the valves only: it hugs the single −X valve
# column, symmetric about it. The Tees still seat in the assembly, but the tray
# no longer extends a floor or grooves under them.
plate_x = (-bc.plate_half_x, -bc.valve_x + bc.valve_pad)
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    # Outlets point -X to the nozzles (the outer ports); inlets are from the
    # center Tees. The valve flow arrow (local +Y) points -X.
    parts = {nm: bc.place_valve(*p, 90.0) for nm, p in valves.items()}
    # YD seats run-along-X, branch up. YG plugs its branch into VJ's inner port
    # (X-facing), then its run swings about that branch (X) axis.
    parts["YD"] = bc.place_tee(*tees["YD"])
    vj_port = (-bc.tee_run_half, -bc.row_half, bc.port_z)  # VJ inner port tip
    parts["YG"] = bc.place_tee_branch_to_xport(vj_port, yg_spin)
    # An elbow turns each valve's outer (−X nozzle-outlet) port +Z up out of the tray.
    parts.update({
        f"E{nm}": bc.place_elbow(cx, cy, -1.0 if cx < 0 else 1.0, 0.0)
        for nm, (cx, cy) in valves.items()
    })
    return parts


def build_nozzle_gate_tray():
    return bc.build_tray(list(valves.values()), [], plate_x, plate_y_half)


def main():
    export_step(build_nozzle_gate_tray(), str(_here.parent / "nozzle-gate-tray.step"))
    print("-> nozzle-gate-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PORT_Z": f"{bc.port_z:.4g}",
            "TRAY_BOT_Z": f"{bc.bot_z:.4g}",
            "TRAY_TOP_Z": f"{bc.top_z:.4g}",
            "NOZ_PLATE_W": f"{plate_x[1] - plate_x[0]:.0f}",
            "NOZ_PLATE_D": f"{2 * plate_y_half:.0f}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
            "WALL_TOP_Z": f"{bc.wall_top_z:.4g}",
        },
        expected_counts={
            "PORT_Z": 1, "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1,
            "NOZ_PLATE_W": 1, "NOZ_PLATE_D": 1, "STACK_PITCH": 2, "WALL_TOP_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
