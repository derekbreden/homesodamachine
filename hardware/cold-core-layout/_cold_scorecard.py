"The cold core's arrangement as a scorecard, written beside its STEP.\n\nSame sidecar the enclosure's card writes ([`web/contracts/scorecard-sidecar.js`]\n(/web/contracts/scorecard-sidecar.js)), so the 3D viewer draws this card with the machinery it\nalready has. The checks are this assembly's own — a carbonator, a wound coil, two reservoirs, and\nthe lines potted among them.\n\nREPORTING, NOT GATING. `main` never exits nonzero on a finding — every row lands in the card\nand on the terminal, and the build still writes its STEP. A reading that stops the build is a\nreading nobody sees at `/3d`.\n\n  bom-covered    every billed cold-core part against the body that realizes it\n  bodies-clear   no two solids share volume\n  routes-fit     no line meets a solid\n  lines-apart    no line meets another line\n  arcs-hold      every corner turns at the stock arc\n  floats-couple  every Aero float clears its wall and rides within the reed distance limit\n"
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

from dataclasses import dataclass, field
@dataclass
class Scorecard:
    checks: list
    bends: list = field(default_factory=list)
    bodies: list = field(default_factory=list)
    @property
    def gates_pass(self, *args, **kwargs):
        return _compiled('_cold_scorecard', path=('Scorecard.gates_pass',), args=(self, *args), kwargs=kwargs)

def __getattr__(name):
    if name == "__all__":
        return _compiled('_cold_scorecard', action="public-names")
    try:
        return _member('_cold_scorecard', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('_cold_scorecard', action="main")
