"""BiB-gate tray: 2 axis-aligned Beduan valves + 4 Tee fittings.

The [fluid-topology](../../../topology/fluid-topology.md) BiB gates as a tray.
A single −X column (V-K-A over V-K-B) feeds one near-valve Tee per row: the
valve butts the Tee's −X run end and its branch rises (+Z). The row's second
Tee hangs **branch-down on that riser** — its branch port butts the near Tee's
branch top — with its run swung 45° about Z.

    V-K-A ──┬─ Y-KA ╲Y-C     near Tee: run along X, branch ↑;
    V-K-B ──┴─ Y-KB ╲Y-F     far Tee: branch ↓ butting that riser, run at 45°

Valve placement, the Tee placers, and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/). Origin = cell center, Z = 0 the
mounting plane, near-Tee run ports at Z = 11.3, the branch-butt riser at
Z = 31.366.
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

# −X valve column. Each row's near-valve Tee seats run-along-X (branch +Z); the
# row's far Tee hangs branch-down on that riser (placed in build_assembly).
valves = {"VKA": (-bc.valve_x, +bc.row_half), "VKB": (-bc.valve_x, -bc.row_half)}
near_tees = {"YKA": (0.0, +bc.row_half), "YKB": (0.0, -bc.row_half)}
hung_tees = {"YC": "YKA", "YF": "YKB"}   # far Tee -> near Tee whose riser it hangs on
hung_spin = 45.0                         # far-Tee run swung this many deg about Z

# The tray floors and walls the valves only: it hugs the single −X valve
# column, symmetric about it. The Tees still seat in the assembly, but the tray
# no longer extends a floor or grooves under them.
plate_x = (-bc.plate_half_x, -bc.valve_x + bc.valve_pad)
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    # Outlets point +X to the near Tees (V-K-A/V-K-B feed Y-KA/Y-KB); inlets
    # are from the BiB connectors (outer ports). Arrow (local +Y) -> +X = -90.
    parts = {nm: bc.place_valve(*p, -90.0) for nm, p in valves.items()}
    # Near-valve Tees seat run-along-X, branch up.
    parts.update({nm: bc.place_tee(*p) for nm, p in near_tees.items()})
    # Each row's far Tee hangs branch-down on the near Tee's up-riser, butting
    # its branch top, run swung by ``hung_spin`` about Z.
    riser_z = bc.port_z + bc.tee_branch_reach
    for far, near in hung_tees.items():
        nx, ny = near_tees[near]
        parts[far] = bc.place_tee_hung((nx, ny, riser_z), hung_spin)
    # An elbow turns each valve's outer (−X BiB-inlet) port +Z up out of the tray.
    parts.update({
        f"E{nm}": bc.place_elbow(cx, cy, -1.0 if cx < 0 else 1.0, 0.0)
        for nm, (cx, cy) in valves.items()
    })
    return parts


def build_bib_gate_tray():
    return bc.build_tray(list(valves.values()), [], plate_x, plate_y_half)


def main():
    export_step(build_bib_gate_tray(), str(_here.parent / "bib-gate-tray.step"))
    print("-> bib-gate-tray.step")
    substitute_md(
        _here.parent / "README.md",
        variables={
            "PORT_Z": f"{bc.port_z:.4g}",
            "TRAY_BOT_Z": f"{bc.bot_z:.4g}",
            "TRAY_TOP_Z": f"{bc.top_z:.4g}",
            "BIB_PLATE_W": f"{plate_x[1] - plate_x[0]:.0f}",
            "BIB_PLATE_D": f"{2 * plate_y_half:.0f}",
            "STACK_PITCH": f"{stack_pitch:.4g}",
            "WALL_TOP_Z": f"{bc.wall_top_z:.4g}",
        },
        expected_counts={
            "PORT_Z": 1, "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1,
            "BIB_PLATE_W": 1, "BIB_PLATE_D": 1, "STACK_PITCH": 2, "WALL_TOP_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
