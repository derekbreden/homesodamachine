"""Assembled DC hub: the printed hub with its two Wago 221-413 lever nuts standing
butt-first in their wells, wire ports up.

``build_assembly(L)`` takes a ``Layout`` from dc_hub — which is the AC hub's Layout, so
``ac_hub_assembly.build_assembly`` stands the lugs for both parts and this module only
names the row it stands them on."""

import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "wago-221-413",
    _hw / "printed-parts" / "electronics" / "ac-hub",
    _here.parent,
):
    sys.path.insert(0, str(_p))
from _cadq_export import export_assembly
import ac_hub_assembly as _ac
import dc_hub as t

HUB_COLOR = _ac.HUB_COLOR
WAGO_COLOR = _ac.WAGO_COLOR


def build_assembly(L, name="dc-hub-assembly"):
    return _ac.build_assembly(L, name=name)


def main():
    export_assembly(build_assembly(t.LAYOUT, "dc-hub-assembly"),
                    str(_here.parent / "dc-hub-assembly.step"))
    print("-> dc-hub-assembly.step")


if __name__ == "__main__":
    main()
