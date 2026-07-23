"""Nozzle-gate tray: 2 axis-aligned Beduan valves.

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates as a
tray. A single −X column — V-G and V-J butted on the two channel rows, ports
along X, no tilt — and nothing else: the pump-discharge tees (Y-D / Y-G) that
feed the inner ports are the enclosure's to pack, and the ports run bare
until their lines land. The enclosure hangs this tray INVERTED (180° about
Y, like the bag-circuit tray) in the pocket east of the bag assembly, so the
inner ports face west at the bag tray's own port plane and the outer
(nozzle-outlet) ports face east.

    V-G ●    inner port ← Y-D (deferred) · outer port → Nozzle A
    V-J ●    inner port ← Y-G (deferred) · outer port → Nozzle B

Valve placement and the tray builder are shared with the
[bag-circuit tray](../bag-circuit-tray/) via `build_tray`. Origin = cell
center, Z = 0 the mounting plane, ports at Z = 11.3. The inverted hang keeps
local Y, so the name↔row assignment puts V-G on the −Y row (world channel A,
forward, beside V-F) and V-J on +Y (channel B, beside V-I).
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

# One valve column (−X), a row per channel. Local −row_half is the enclosure's
# forward row (the inverted hang keeps local Y), so V-G rides it beside V-F.
valves = {"VG": (-bc.valve_x, -bc.row_half), "VJ": (-bc.valve_x, +bc.row_half)}

# The tray floors and walls the valves only: it hugs the single −X valve
# column, symmetric about it; the X-ends stay open for the ports.
plate_x = (-bc.plate_half_x, -bc.valve_x + bc.valve_pad)
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch
# This tray seats nothing on its wall tops. The enclosure hangs it inverted and then
# flips it valves-up in place, so its FLOOR carries the stack (onto the source tray's
# wall tops) and its wall tops face open air — the channel the nozzle-outlet runs cross
# on their way aft. So the walls end level with the coils they retain, taking none of
# the stacked trays' `stack_coil_clear` standoff: that standoff buys clearance against
# a facing tray, and there is no tray facing these.
wall_top_z = bc.valve_coil_top_z


def build_assembly():
    # Outlets point −X to the nozzles (the outer ports); the inner (+X) ports
    # await the pump-discharge tees. The valve flow arrow (local +Y) points −X.
    return {nm: bc.place_valve(*p, 90.0) for nm, p in valves.items()}


def port_collets():
    """Every valve port's bare collet tip in tray coordinates: {name:
    (position, outward axis)} — `-I` the inner (tee-side) port, `-O` the
    outer (nozzle-outlet) port. The tray's boundary — what the enclosure
    routes lines to — with no fitting yet turned onto either."""
    out = {}
    for nm, (cx, cy) in valves.items():
        out[f"{nm}-O"] = ((cx - bc.port_half, cy, bc.port_z), (-1.0, 0.0, 0.0))
        out[f"{nm}-I"] = ((cx + bc.port_half, cy, bc.port_z), (+1.0, 0.0, 0.0))
    return out


def build_nozzle_gate_tray():
    return bc.build_tray(list(valves.values()), [], plate_x, plate_y_half, wall_top=wall_top_z)


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
            "NOZ_WALL_TOP_Z": f"{wall_top_z:.4g}",
        },
        expected_counts={
            "PORT_Z": 1, "TRAY_BOT_Z": 1, "TRAY_TOP_Z": 1,
            "NOZ_PLATE_W": 1, "NOZ_PLATE_D": 1, "STACK_PITCH": 2, "NOZ_WALL_TOP_Z": 1,
        },
    )
    print("-> README.md")


if __name__ == "__main__":
    main()
