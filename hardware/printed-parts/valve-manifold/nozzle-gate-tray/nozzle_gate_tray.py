"""Nozzle-gate tray: 2 axis-aligned Beduan valves — the manifold stack's top tray.

The [fluid-topology](../../../topology/fluid-topology.md) nozzle gates as a
tray. One valve column — V-G and V-J butted on the two channel rows, ports
along X, no tilt — with an elbow on each port: the INLET pair turns the −X
ports up out of the tray, the OUTLET pair turns the +X ports sideways along
+Y. The enclosure hangs this tray INVERTED directly over the bag-circuit
tray's east bank (the same 180°-about-Y hang the bag tray rides, sharing its
X/Y origin), which lands each inlet-elbow corner on a bag east elbow column
and turns its collet straight DOWN, coaxial over the up-facing V-F-I / V-I-I
collet below. The pump-discharge tees (Y-D / Y-G) stand on those shared
verticals — one straight stub at every collet, no bends — and the outlet
collets turn aft toward the nozzle lines (fluid-18/28).

    V-G ●  EI down to Y-D-3 · EO aft to Nozzle A
    V-J ●  EI down to Y-G-3 · EO aft to Nozzle B

Valve placement, the elbow placer + its collet accessor, and the tray builder
are shared with the [bag-circuit tray](../bag-circuit-tray/) via `build_tray`.
Origin = cell center, Z = 0 the mounting plane, ports at Z = 11.3. The
inversion keeps local Y, so the name↔row assignment puts V-G on the −Y row
(world channel A, forward, over V-F) and V-J on +Y (channel B, over V-I).
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
# forward row (the inverted hang keeps local Y), so V-G rides it over V-F.
valves = {"VG": (-bc.valve_x, -bc.row_half), "VJ": (-bc.valve_x, +bc.row_half)}

# Per-port elbow rolls, authored for this tray's INVERTED pose in the
# enclosure (hung 180° about Y, like the bag tray):
#   * the −X INLET ports keep the local up-turn (roll 0), which the inversion
#     points straight DOWN in world — each collet coaxial over the bag tray's
#     up-facing east collet, with a pump-discharge tee standing between;
#   * the +X OUTLET ports roll −90 to local +Y, which the inversion keeps as
#     world AFT — each collet facing the rear wall the nozzle lines leave by.
inlet_roll = 0.0
outlet_roll = -90.0

# The tray floors and walls the valves only: it hugs the single −X valve
# column, symmetric about it; the X-ends stay open for the elbows.
plate_x = (-bc.plate_half_x, -bc.valve_x + bc.valve_pad)
plate_y_half = bc.plate_half_y
stack_pitch = bc.stack_pitch


def build_assembly():
    # Flow runs −X → +X locally (east → west in the inverted world pose):
    # inlets from the discharge tees on the −X side, outlets to the nozzles
    # on +X. The valve flow arrow (local +Y) points +X.
    parts = {nm: bc.place_valve(*p, -90.0) for nm, p in valves.items()}
    for nm, (cx, cy) in valves.items():
        parts[f"EI{nm}"] = bc.place_elbow(cx, cy, -1.0, 0.0, roll=inlet_roll)
        parts[f"EO{nm}"] = bc.place_elbow(cx, cy, +1.0, 0.0, roll=outlet_roll)
    return parts


def boundary_collets():
    """Every elbow's free collet in tray coordinates: {name: (position,
    outward axis)} — two per valve, `-I` the inlet turn, `-O` the outlet.
    The tray's boundary — what the enclosure routes lines to."""
    out = {}
    for nm, (cx, cy) in valves.items():
        out[f"{nm}-I"] = bc.elbow_collet(cx, cy, -1.0, 0.0, roll=inlet_roll)
        out[f"{nm}-O"] = bc.elbow_collet(cx, cy, +1.0, 0.0, roll=outlet_roll)
    return out


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
