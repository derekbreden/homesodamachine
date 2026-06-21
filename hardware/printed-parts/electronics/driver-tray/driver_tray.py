"""Driver tray — the 12 V switching / distribution group of the Zone-B shelf.

Carries the L298N pump driver (also makes the 5 V rail), both ULN2803A solenoid/
fan drivers, relay #2 (diaphragm-pump 12 V), and the DC distribution block. Same
idioms as the power tray: boards pack flush, a single convex-outline floor, no
walls, heat-set M3 bosses. Built by the shared
[`module_tray`](/hardware/printed-parts/electronics/module_tray.py) engine.

Layout: L298N at the left; the two ULN2803As stacked just to its right; relay #2
and the DC distribution block in the next column. Local frame: X right, Y deep,
Z up; origin at the floor's bottom-left corner.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics"))
for _r in ("l298n", "uln2803a", "teyleten-relay", "dc-dist-block"):
    sys.path.insert(0, str(_hw / "reference" / _r))
sys.path.insert(0, str(_hw / "scripts"))
from _cadq_export import export_step
import module_tray as mt
from module_tray import Mount
import l298n
import uln2803a as uln
import teyleten_relay as relay
import dc_dist_block as dcdist

m = mt.margin

# L298N lower-left; ULN pair flush to its right; relay #2 + DC block next column.
_l_c = (m + l298n.length / 2.0, m + l298n.width / 2.0)
_l_r = m + l298n.length
_uln_cx = _l_r + uln.length / 2.0
_uln_r = _l_r + uln.length
_relay_cx = _uln_r + relay.length / 2.0
_dc_cx = _uln_r + dcdist.length / 2.0

MOUNTS = [
    Mount(l298n, _l_c, 0.0),
    Mount(uln, (_uln_cx, m + uln.width / 2.0), 0.0),
    Mount(uln, (_uln_cx, m + uln.width + uln.width / 2.0), 0.0),
    Mount(relay, (_relay_cx, m + relay.width / 2.0), 0.0),
    Mount(dcdist, (_dc_cx, m + relay.width + dcdist.width / 2.0), 0.0),
]


def build_driver_tray():
    return mt.build_module_tray(MOUNTS)


def main():
    export_step(build_driver_tray(), str(_here.parent / "driver-tray.step"))
    print("-> driver-tray.step")


if __name__ == "__main__":
    main()
