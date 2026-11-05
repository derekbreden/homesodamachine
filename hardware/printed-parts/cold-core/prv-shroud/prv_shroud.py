'PRV shroud — printed PETG cup that surrounds the Control Devices\nSV-125 pressure-relief valve during the cold-core body foam pour.\n\nThe SV-125 is an open-port pop-off valve: gas exits through a single\nradial discharge port on the smooth cylinder between the NPT threads\nand the hex, and the spring chamber above the hex is open to\natmosphere through bonnet windows above. Both features need to see\nair, not cured polyurethane foam, for the valve to function as a\nrelief device.\n\nThe shroud slips over the entire valve from the pull-ring end and\nseats on the smooth ⌀18.8 mm cylindrical section of the TAISHER 316L\nSS 90° street elbow (B0CZ38MYL1) that threads into Port 4. The\nopen shroud end-to-elbow joint is sealed with a bead of 100% RTV\nsilicone caulk, tooled to a fillet — foam-tight, not airtight.\n\nA ⌀ hole through the BARREL accepts a length of 1/4" OD\nLLDPE tubing — the unpressurized vent line. The LLDPE runs down the\nfoam shell\'s WEST LANE and out its slot in the −X wall, one station\nbelow the evaporator outlet copper that shares it, into the appliance\ninterior, where it terminates open.\n\nThe hole is radial and not in the cap because THE CAP HAS NOWHERE TO\nSEND A TUBE. Installed, the shroud lies horizontally on the +Y port\'s\nlateral axis and its cap face stands ~3 mm off the foam shell\'s own\ninner wall — less than a tube\'s radius, so a line leaving axially has\nno room to turn. Leaving radially through the barrel\'s underside, the\nline is already pointing down the lane it has to fall, and needs no\ncorner at all. The hole\'s station along the barrel\n( from the open end) is what lands it on that\nlane\'s centreline once the shroud is made up on the elbow.\n\nGeometry\n--------\n\n    Z =  ┌──────────────────────┐  ← cap outside surface\n               │ ░░░░ cap ░░░░░░ │  ← closed, no hole\n    Z =  ├──────────────────────┤  ← cap inside surface\n               │                      │\n               │   (cavity around     │\n               │    PRV body, hex,    │  ← ID\n               │    upper smooth cyl, │     OD ( wall)\n               │    bonnet windows,   │\n               │    pull-ring)        │\n               │                      │\n    Z = 0      └ open ────────────────┘  ← seats on elbow ⌀18.8 mm cyl\n\n               ⌀ vent bored radially through the −Y wall at\n               Z =; the cup is rolled about its own axis at\n               install so that wall faces the shell\'s −Z, and the tube leaves\n               DOWNWARD onto the west lane (`cold_core_assembly._prv_roll`).\n\nThe cavity length spans from the bottom of the elbow\'s smooth\ncylinder to the tip of the PRV pull-ring with the valve hand-tight\nin the elbow\'s lateral F outlet.\n\nCoordinate convention: cylinder axis along Z, open end at Z=0, cap\ntop at Z=. Installed orientation is horizontal — the shroud\'s Z\naxis aligns with the lateral run of the TAISHER elbow off Port 4.\n'
from __future__ import annotations

import sys as _sys
from pathlib import Path as _Path

_hardware = next(p for p in _Path(__file__).resolve().parents if p.name == "hardware")
_sys.path[:0] = [str(_hardware / "scripts"), str(_hardware / "cold-core-layout")]
from _cold_core_data import compiled as _compiled, member as _member

def __getattr__(name):
    if name == "__all__":
        return _compiled('prv_shroud', action="public-names")
    try:
        return _member('prv_shroud', name)
    except ValueError as error:
        raise AttributeError(name) from error

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    _compiled('prv_shroud', action="main")
