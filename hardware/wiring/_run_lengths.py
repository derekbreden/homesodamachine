"""Centre-based loom reach estimates from the placed machine.

Run: tools/cad-venv/bin/python hardware/wiring/_run_lengths.py

This tool multiplies board-to-device centre distance by the recorded DC-5
400/273 routing factor. It does not locate terminals, follow installed wires,
or check clearance. The factor applies one mock-up observation to other runs;
different bends and terminal positions can require longer or shorter cuts.

The doc driver _ac_wiring_schedule_sync.py carries bench cuts without building
the machine. Its manifold, fan and V-K cuts instead use the authored wire paths
and qualifications in manifold-junction-clearance-check.json. This tool's
corresponding rows remain reach estimates, not those routed cut lengths.
"""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_root / "hardware" / "manifold-layout"))

import enclosure_assembly as _ea  # noqa: E402

# The measured cabinet routing calibration: 273 mm of direct reach carries a 400 mm cut.
CAL_REACH = 273.0
CAL_CUT = 400.0

# Each loom's conductors, grouped by the body they land on. The board end is `pcba` for all of
# them. AC-1…AC-6 are not here: they are built in place, not as cable assemblies.
LEGS = {
    "J1 MANIFOLD A": [("OUT1–OUT8", 8, [f"valve-v-{c}" for c in "abcdefgh"]),
                      ("COM → 221-420", 1, ["wago-mana"])],
    "J2 MANIFOLD B": [("OUT1, OUT2", 2, ["valve-v-i", "valve-v-j"]),
                      ("FAN", 1, ["condenser+fan"]),
                      ("OUT3 → V-K", 1, ["vk-solenoid"]),
                      ("COM → 221-415", 1, ["wago-manb"])],
    "J4 SENSORS": [("3V3, IO26 → 1-wire", 2, ["cold-core/probe-carbonator-ds18b20"]),
                   ("V5, IO25 → flow", 2, ["digiten-flow"]),
                   ("IO27, IO23 → moisture", 2, ["moisture-plate"]),
                   ("GND → 221-415", 1, ["wago-sensors"])],
    "J5 RELAYS": [("all four", 4, ["relay-1", "relay-2"])],
    "J6 REEDS A": [("RA1–RA4", 4, [f"cold-core/reed-a-{i}" for i in (1, 2, 3, 4)]),
                   ("GND → 221-415", 1, ["wago-reeds-a"])],
    "J7 REEDS B": [("RB1–RB4", 4, [f"cold-core/reed-b-{i}" for i in (1, 2, 3, 4)]),
                   ("CLO, CHI", 2, ["cold-core/reed-carb-1", "cold-core/reed-carb-2"]),
                   ("GND → 221-420", 1, ["wago-reeds-b"])],
    "J9 DISPLAY": [("all four", 4, ["display"])],
    "J11 GAS": [("all four", 4, ["mq6-sensor"])],
    "J13 PUMPS": [("fixed AM1/AM2, BM1/BM2", 4, ["pump-contact-male"])],
}

# J3 is not measured: SIG-6 is the one loom that leaves the box, climbing the umbilical to the
# faucet head above the counter, and nothing above the enclosure's ceiling is in this model.


def centres(assembly):
    out = {}
    for child in assembly.children:
        for body in [child] + list(child.children):
            try:
                bb = body.toCompound().BoundingBox()
            except Exception:
                continue
            out[body.name] = ((bb.xmin + bb.xmax) / 2.0,
                              (bb.ymin + bb.ymax) / 2.0,
                              (bb.zmin + bb.zmax) / 2.0)
    return out


def measure():
    pos = centres(_ea.build_enclosure_assembly())
    board = pos["pcba"]
    reach = lambda name: math.dist(board, pos[name])
    factor = CAL_CUT / CAL_REACH

    rows, total = [], 0
    for loom, legs in LEGS.items():
        for label, count, bodies in legs:
            routed = max(reach(b) for b in bodies) * factor
            rows.append((loom, label, count, routed))
            total += count * routed
    # DC-5's cartridge half starts at the contact pair's female half, inside the clamp, and ends on
    # the two motors' tabs: it rides the cartridge and never reaches the board.
    cartridge = max(math.dist(pos["pump-contact-female"], pos[m])
                    for m in ("pump-a-motor", "pump-b-motor")) * factor
    rows.append(("DC-5 CARTRIDGE", "contact pair → motors", 4, cartridge))
    total += 4 * cartridge
    return rows, total, factor


def main():
    rows, total, factor = measure()
    print(f"calibration  cabinet reach {CAL_REACH:.0f} mm -> {CAL_CUT:.0f} mm cut "
          f"(routed factor {factor:.2f})\n")
    print(f"{'loom':<16}{'conductors':<24}{'n':>3}{'cut':>7}")
    for loom, label, count, routed in rows:
        print(f"{loom:<16}{label:<24}{count:>3}{routed:>7.0f}")
    print(f"\n{'':<43}{total / 1000.0:>6.1f} m of 22 AWG, J3's ribbon excluded")


if __name__ == "__main__":
    main()
