"""ASSE 1022 assembly: the Multiplex 19-0897 backflow preventer with everything
that threads or clamps directly onto it.

The water path's one non-negotiable component and the fittings that make it
reachable from 1/4" tube on both sides — the chain
[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) step 2 builds,
in the order it builds them:

    1/4" LLDPE → PP010822E → GAGIRA coupling → [ASSE 1022] → flare38-14ptc → 1/4" LLDPE
                                                     └ TPU sleeve ↓ 4 mm DRAIN → faucet bowl

The outlet leaves at 1/4" OD — the flare38-14ptc turns the ASSE's 3/8" male flare
straight onto 1/4" LLDPE, so no 3/8" tubing runs on toward the pump; the 1/4" line
carries the split (V-K + V-A) and only steps back up to 3/8" at the SeaFlo barbs.

Every station is read off the part upstream of it: each fitting's own module says
how deep its threads go, and this file stacks those reaches along the flow axis.
Move a length in any reference module and the chain closes on the new one.

A station is its module, its seat and its hue. The seat carries the fitting's metal and
the ports that fitting's module declares ([`_seating.py`](/hardware/scripts/_seating.py)).
This assembly's own terminals are its stations' ports, named.

The TPU sleeve covers the barb and connects directly to the 4 mm DRAIN return,
bulkhead and the separate faucet outlet over the bowl
([`asse-drain.md`](/hardware/assembly/asse-drain.md)).

Frame: the ASSE 1022's own — +X = flow, inlet upstream at its X = 0, the vent
running −Z. The upstream fittings therefore sit at negative X.

Run:
    tools/cad-venv/bin/python hardware/reference/asse1022-assembly/asse1022_assembly.py


The reference STEP and payloads are declared in `frozen-asset.json`.
Native builder functions remain available to current composition callers.
"""

from __future__ import annotations

import sys
from pathlib import Path
from functools import cache as _reference_cache

_REFERENCE_DIR = Path(__file__).resolve().parent
STEP_PATH = _REFERENCE_DIR / 'asse1022-assembly.step'
PAYLOAD_PATH = _REFERENCE_DIR / 'asse1022-assembly.step.mesh'
FINE_PAYLOAD_PATH = _REFERENCE_DIR / 'asse1022-assembly.step.mesh'
ASSET_MANIFEST_PATH = _REFERENCE_DIR / "frozen-asset.json"


def main():
    print(f"Frozen STEP: {STEP_PATH}")
    print(f"Display payload: {PAYLOAD_PATH}")
    print(f"Fine payload: {FINE_PAYLOAD_PATH}")


if __name__ == "__main__":
    main()
    raise SystemExit(0)


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (
    _hw / "scripts",
    _hw / "reference" / "multiplex-asse1022",
    _hw / "reference" / "gagira-reducing-coupling",
    _hw / "reference" / "jg-pp010822e",
    _hw / "reference" / "flare38-14ptc",
):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))
import flare38_14ptc as oadapt
import gagira_reducing_coupling as coupling
import jg_pp010822e as ptc
import multiplex_asse1022 as bfp

# EACH FITTING IS THE COLOUR OF ITS OWN STOCK, off `_materials` — the same constant its own
# generator next door bakes into its own STEP, so a body in this chain and the picture of that
# body alone are one colour. Two of the five are the same metal and are drawn the same metal:
# what tells the GAGIRA coupling from the barrel it swallows is the step between their hexes,
# which is what tells them apart on the bench.

# Where each fitting lands on the flow axis, each read off the part it threads into.
# The barrel's two shoulders are what the female fittings butt against.

_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('asse1022_assembly')
globals().update({name: _reference_values[name] for name in ('BARREL_UPSTREAM', 'BARREL_DOWNSTREAM', 'COUPLING_X', 'PTC_X', 'OUTLET_X', 'TERMINALS')})

# The coupling swallows the ASSE inlet to its full socket depth, so its large-end
# face lands on that shoulder and its body reaches upstream by its own length.
# The PTC's shank threads into the coupling's small socket, so the shank tip lands
# that far inside the coupling's upstream face.
# The swivel nut is drawn up over the flare, its face on the downstream shoulder.


def _along(x) -> Seat:
    """The seat a fitting takes on the flow axis: its own X origin at `x`, its axis onto
    the ASSE 1022's (y = 0, z = the body-centre height)."""
    from _seating import Seat
    return Seat.shift((x, 0.0, bfp.BODY_CENTER_Z))


def flow_axis():
    "The line every station on this chain stands on, in the assembly's own frame:\n    `(position, axis)` — the ASSE 1022's inlet plane on it, and the direction the water\n    runs. `_along` seats each fitting onto this line, and the cabinet that holds the chain\n    over a drain seats the whole assembly by it."
    return _reference_data('asse1022_assembly', 'flow_axis', (), {})


# The chain, in the order the water meets it: what draws each station, the seat it takes,
# and its hue. The ASSE 1022 is the frame the other four are seated in.
@_reference_cache
def _stations():
    from _seating import Seat
    from _materials import M_BRASS, M_JG_BLACK_PP, M_JG_GREY_ACETAL, M_STAINLESS
    return {
        "jg-pp010822e":       (ptc,      _along(PTC_X),      M_JG_BLACK_PP),
        "gagira-coupling":    (coupling, _along(COUPLING_X), M_STAINLESS),
        "multiplex-asse1022": (bfp,      Seat(),             M_BRASS),
        "flare38-14ptc":      (oadapt,   _along(OUTLET_X),   M_JG_GREY_ACETAL),
    }

# This assembly's boundary: the two mouths the cabinet plumbs to, and the one it catches
# under. Each names the station port it is.


def build():
    """The chain, each station at its seat."""
    import cadquery as cq
    assy = cq.Assembly(name="asse1022-assembly")
    for name, (part, seat, color) in _stations().items():
        assy.add(seat.solid(part.build()), name=name, color=color)
    return assy


def port(name: str) -> tuple:
    """One terminal in this assembly's own frame: `(position, outward axis)`.

    The station's module owns the station; the station's seat carries it here."""
    if name not in TERMINALS:
        raise KeyError(f"no terminal {name!r} (have: {', '.join(TERMINALS)})")
    station, local = TERMINALS[name]
    part, seat, _color = _stations()[station]
    return seat.port(getattr(part, local)())


def ports():
    'Every terminal, in the order the water meets them.'
    return _reference_data('asse1022_assembly', 'ports', (), {})


def __getattr__(name):
    if name == 'STATIONS':
        return _stations()
    if name == 'cq':
        import cadquery as cq
        return cq
    if name in {'export_assembly'}:
        import _cadq_export
        return getattr(_cadq_export, name)
    if name in {'Seat'}:
        import _seating
        return getattr(_seating, name)
    if name in {'M_JG_BLACK_PP', 'M_BRASS', 'M_JG_GREY_ACETAL', 'M_STAINLESS'}:
        import _materials
        return getattr(_materials, name)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
