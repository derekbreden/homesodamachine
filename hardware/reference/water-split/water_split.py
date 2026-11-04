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

RUN_REACH = tee.RUN_HALF
BRANCH_REACH = tee.BRANCH_REACH  # caliper width less the nominal fixed-collar back radius
REACH = RUN_REACH  # compatibility for callers which use the supply-run reach
TUBE_D = tee.TUBE_D          # 1/4" OD LLDPE the three ports accept

# What carries the tee's frame into this one: its run from ±Z onto ±Y, and its branch from +Y
# onto −X. A roll about X stands the run up, and a roll about the run swings the branch.
_TURNS = (((1.0, 0.0, 0.0), -90.0), ((0.0, 1.0, 0.0), 90.0))


def supply():
    """The +Y run collet the 1/4" line from the ASSE 1022 outlet pushes into:
    (position, outward axis)."""
    return (0.0, REACH, 0.0), (0.0, 1.0, 0.0)


def to_vk():
    """The branch collet feeding V-K, on to the SeaFlo suction: (position, axis).
    It takes V-K's share off the run at a right angle — the one port of the three
    the enclosure can point at a level the other two are not on."""
    return (-BRANCH_REACH, 0.0, 0.0), (-1.0, 0.0, 0.0)


def to_flavor():
    """The −Y run collet feeding the flavor tap — flow regulator → V-A: the
    supply's own line carried straight on: (position, axis)."""
    return (0.0, -REACH, 0.0), (0.0, -1.0, 0.0)


def run_barrel():
    """The barrel on the SUPPLY arm — `(station, radius, length)`.

    The shape a printed seat can close on. The hub is where all three arms meet and the branch is
    the port this fitting is turned for, so what is left is the run, and the supply half of it is
    the half with nothing downstream of it to fight for the joint's position.

    `station` is its mid-point and the run axis through it, in the frame the three ports are
    stated in."""
    near, far = tee.RUN_COLLAR_BAND
    return (((0.0, (near + far) / 2.0, 0.0), (0.0, 1.0, 0.0)),
            tee.BARREL_R, far - near)


def clearance_seat(span, tie_width):
    """A seat envelope of `span`, centred on the measured fixed collar patch.

    The rib may overhang that patch with its bore clear of the narrower root and terminal
    sleeve. Its span is clearance, not a claim that the complete span is collar bearing.
    The branch envelope stays outside one end and the fully pressed run face outside the
    other. The sleeve radius and fixed/moving split retain `tee.UNQUALIFIED_DATUMS` status.
    """
    station, radius, _ = run_barrel()
    mid = station[0][1]
    lo, hi = mid - span / 2.0, mid + span / 2.0
    if lo <= tee.BARREL_R or hi >= RUN_REACH - tee.RUN_COLLET_TRAVEL:
        raise ValueError("water-split seat reaches the branch or the fully pressed run face")
    if tee.COLLET_NOSE_R > radius:
        raise ValueError("water-split release sleeve exceeds the seat clearance envelope")
    return station, radius, span


# --- controls -------------------------------------------------------------


if __name__ == "__main__":
    print(__doc__)
