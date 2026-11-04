"""1/4" push-to-connect union tee (John Guest PP0208E) — the water split that
sits on the ASSE 1022's 1/4" outlet and feeds the two valves downstream of the
backflow preventer: the ASSE supply enters the branch and splits along the run to
V-K (the fill/shutoff on the way to the SeaFlo suction) and to the flavor tap
(flow regulator → V-A). All three ports are 1/4" PTC — the split needs no
reducers, because the water reaches it at 1/4" and leaves at 1/4"
([`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §2).

THE SOLID IS `reference/tee-connector`'s — the same measured clearance reference the manifold's six
junctions are built from, turned into the frame below. This file writes none of its own: a
turned copy of a solid is that solid. The scalar interfaces below retain its frame. Its figures are
measured off that STEP and held to it, so the barrel a rib closes on and the collet faces a tube
pushes into are the fitting's own and not a drawing of one.

Frame: the run along ±Y, the supply at +Y and the flavor tap at −Y, and the branch along −X at a
right angle to both. Centre at the origin, the three collet faces in the Z = 0 plane. Which of the
three ends up pointing where is the enclosure's to say — it turns this frame on the way in
([`enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py) `SPLIT_TURN`), and the
branch is the port that turn is FOR: it is the only one of the three that can be given a level of
its own.

Run:
    python3 hardware/reference/water-split/water_split.py
"""

import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_hw / "reference" / "tee-connector"))
import tee_connector as tee


_reference_hardware = next(p for p in Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('water_split')
globals().update({name: _reference_values[name] for name in ('RUN_REACH', 'BRANCH_REACH', 'REACH', 'TUBE_D', '_TURNS')})


# What carries the tee's frame into this one: its run from ±Z onto ±Y, and its branch from +Y
# onto −X. A roll about X stands the run up, and a roll about the run swings the branch.


def supply():
    'The +Y run collet the 1/4" line from the ASSE 1022 outlet pushes into:\n    (position, outward axis).'
    return _reference_data('water_split', 'supply', (), {})


def to_vk():
    "The branch collet feeding V-K, on to the SeaFlo suction: (position, axis).\n    It takes V-K's share off the run at a right angle — the one port of the three\n    the enclosure can point at a level the other two are not on."
    return _reference_data('water_split', 'to_vk', (), {})


def to_flavor():
    "The −Y run collet feeding the flavor tap — flow regulator → V-A: the\n    supply's own line carried straight on: (position, axis)."
    return _reference_data('water_split', 'to_flavor', (), {})


def run_barrel():
    "The barrel on the SUPPLY arm — `(station, radius, length)`.\n\n    The shape a printed seat can close on. The hub is where all three arms meet and the branch is\n    the port this fitting is turned for, so what is left is the run, and the supply half of it is\n    the half with nothing downstream of it to fight for the joint's position.\n\n    `station` is its mid-point and the run axis through it, in the frame the three ports are\n    stated in."
    return _reference_data('water_split', 'run_barrel', (), {})


def clearance_seat(span, tie_width):
    'A seat envelope of `span`, centred on the measured fixed collar patch.\n\n    The rib may overhang that patch with its bore clear of the narrower root and terminal\n    sleeve. Its span is clearance, not a claim that the complete span is collar bearing.\n    The branch envelope stays outside one end and the fully pressed run face outside the\n    other. The sleeve radius and fixed/moving split retain `tee.UNQUALIFIED_DATUMS` status.\n    '
    return _reference_data('water_split', 'clearance_seat', (span, tie_width), {})


# --- controls -------------------------------------------------------------


if __name__ == "__main__":
    print(__doc__)
