"""Narrow power tray — a wide-and-shallow variant of the power tray.

Same parts and retention as [power-tray](/hardware/printed-parts/electronics/power-tray/),
re-laid-out for a wide/shallow Zone-B slot: the Mean Well PSU is turned 90° (its
109 mm length runs along X), the relay and the Wago column pack flush to its
right, and the ground ring-stack moves into the open space above the PSU. Net:
**more X, less Y** than power-tray.

Reuses ``power_tray.build_tray`` and the ``Layout`` engine — see power_tray.py.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "electronics" / "power-tray"))
sys.path.insert(0, str(_hw / "scripts"))
import power_tray as base
from power_tray import Layout
from _cadq_export import export_step

psu, wago, relay = base.psu, base.wago, base.relay
m = base.margin

# PSU turned 90° (109 along X) at the lower-left; relay and Wago column flush to
# its right; ground ring-stack in the open space above the PSU.
_psu_c = (m + psu.length / 2.0, m + psu.width / 2.0)
_relay_cx = m + psu.length + relay.width / 2.0
_relay_cy = m + relay.length / 2.0
_wago_cx = _relay_cx + relay.width / 2.0 + base.wago_slot_half
NARROW = Layout(
    psu_c=_psu_c, psu_rot=90.0,
    relay_c=(_relay_cx, _relay_cy), relay_rot=90.0,
    wago_places=tuple((_wago_cx, m + 8.454 + i * base.wago_pitch) for i in range(3)),
    gnd_c=(m + 22.0, m + psu.width + 11.0),
)


def build_narrow_power_tray():
    return base.build_tray(NARROW)


def main():
    export_step(build_narrow_power_tray(), str(_here.parent / "narrow-power-tray.step"))
    print("-> narrow-power-tray.step")


if __name__ == "__main__":
    main()
