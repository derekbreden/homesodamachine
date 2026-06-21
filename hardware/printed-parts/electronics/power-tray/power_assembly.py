"""Assembled power tray: the tray with the PSU, relay #1, and the three Wago
AC-distribution connectors press-fit in place."""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "meanwell-irm90",
    _hw / "reference" / "wago-221-413",
    _hw / "reference" / "teyleten-relay",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import power_tray as t
import meanwell_irm90 as psu
import wago_221_413 as wago
import teyleten_relay as relay

TRAY_COLOR = cq.Color(0.85, 0.78, 0.62)    # PETG tan
PSU_COLOR = cq.Color(0.30, 0.32, 0.36)     # encapsulated brick, dark
RELAY_COLOR = cq.Color(0.20, 0.45, 0.75)   # PCB blue
WAGO_COLOR = cq.Color(0.85, 0.45, 0.15)    # orange levers


def build():
    assy = cq.Assembly(name="power-assembly")
    assy.add(t.build_power_tray().val(), name="tray", color=TRAY_COLOR)
    assy.add(psu.build().val().translate((t.psu_cx, t.psu_cy, t.floor_t)),
             name="PSU", color=PSU_COLOR)
    # Relay long-axis along Y; board underside on the post shoulders.
    assy.add(
        relay.build().val().rotate((0, 0, 0), (0, 0, 1), 90.0)
        .translate((t.relay_cx, t.relay_cy, t.floor_t + t.relay_standoff)),
        name="relay1", color=RELAY_COLOR,
    )
    for i, cy in enumerate(t.wago_cys):
        assy.add(wago.build().val().translate((t.wago_cx, cy, t.floor_t)),
                 name=f"wago{i}", color=WAGO_COLOR)
    return assy


def main():
    export_assembly(build(), str(_here.parent / "power-assembly.step"))
    print("-> power-assembly.step")


if __name__ == "__main__":
    main()
