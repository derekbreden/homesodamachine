"""What each loom conductor actually has to reach, measured off the placed machine.

Run: tools/cad-venv/bin/python hardware/wiring/_run_lengths.py

`_ac_wiring_schedule_sync.py` carries the run lengths as typed constants because it is a doc
driver and must not build the machine to render a table. This is where those constants come
from: it places the whole assembly, takes the centre of the main board and the centre of every
device a loom lands on, and reports the reach between them.

THE ROUTED FACTOR IS CALIBRATED, NOT GUESSED. A conductor does not fly — it drops a wall, runs
a floor and turns a corner, so the cut length is longer than the reach. `_ac_wiring_schedule_sync`
already carried one run derived by hand: DC-5's comment records a 275 mm straight line to the far
pump motor against a 400 mm cut. This module's own measure of that same pair is 273 mm, so the
ratio the repo already accepted is what every other run is scaled by. One calibration point is
one calibration point: a run that turns more corners than DC-5 reads short here, and a straighter
one reads long. What it is not is a guess, and it is not a metre because a neighbouring run is.

CENTRES, NOT NEAREST FACES. A conductor lands on a terminal somewhere on the body, not on the
face nearest the board, and the terminal is not modelled. Centre-to-centre is the measure that
reproduced DC-5, so it is the measure.
"""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_root / "hardware" / "manifold-layout"))

import enclosure_assembly as _ea  # noqa: E402

# DC-5, the one run `_ac_wiring_schedule_sync.py` derives in its own comment: 275 mm of reach
# carries a 400 mm cut. Every other run is scaled by that same ratio.
CAL_RUN = ("pump-b-motor", 400.0)

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
    "J13 PUMPS": [("AM1/AM2, BM1/BM2", 4, ["pump-a-motor", "pump-b-motor"])],
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
    cal_name, cal_cut = CAL_RUN
    factor = cal_cut / reach(cal_name)

    rows, total = [], 0
    for loom, legs in LEGS.items():
        for label, count, bodies in legs:
            routed = max(reach(b) for b in bodies) * factor
            rows.append((loom, label, count, routed))
            total += count * routed
    return rows, total, factor, reach(cal_name)


def main():
    rows, total, factor, cal = measure()
    print(f"calibration  DC-5 reach {cal:.0f} mm -> {CAL_RUN[1]:.0f} mm cut "
          f"(routed factor {factor:.2f})\n")
    print(f"{'loom':<16}{'conductors':<24}{'n':>3}{'cut':>7}")
    for loom, label, count, routed in rows:
        print(f"{loom:<16}{label:<24}{count:>3}{routed:>7.0f}")
    print(f"\n{'':<43}{total / 1000.0:>6.1f} m of 22 AWG, J3's ribbon excluded")


if __name__ == "__main__":
    main()
