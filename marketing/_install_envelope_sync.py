"""Doc-sync driver for marketing/install-envelope.md.

Run: tools/cad-venv/bin/python marketing/_install_envelope_sync.py

The install envelope is the cabinet the machine goes into. That cabinet belongs to the customer,
so no `_enclosure_dimensions.py` under `hardware/` owns its numbers, and this driver stands
beside the page it writes the way every other doc-sync driver stands beside its own.

IT STATES NO SILHOUETTE. The machine's own W x D x H is written where the box is cut —
`printed-parts/enclosure/enclosure/README.md` and `assembly/enclosure-mechanical.md` — and a
third copy here is a third thing to be wrong. What this page owes is the room AROUND the box:
the turn-in behind the +Y wall of back-top and the draw in front of the pump cartridge.

EVERY FIGURE IS A PLACED BODY READ OFF A FACE OF THE BOX, and not a part's own datum carried
here by arithmetic. What a cabinet has to give behind the wall is how far the fittings stand off
the WALL'S OUTER FACE; `jg_bulkhead_union.PROUD_LENGTH` is how far one stands off the face its
flange bears on, and the two are one figure only while the bulkhead ring under that flange lies
flush in the wall. So `_facts` — the machine as the last build wrote it down — is what is read here, and
a body that moves moves this page. A customer sizes a cabinet slot from these four.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_root = _here.parent
for _p in (_root / "tools", _root / "hardware" / "scripts"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _facts                       # noqa: E402  — the machine as the last build wrote it down
from docgen import substitute_md    # noqa: E402

MD = _here / "install-envelope.md"

# The sink base's interior clear height: a 34.5" carcass less the 4" toe kick less the 3/4"
# deck. Cabinet standard, not project geometry — the same derivation the umbilical's length
# stack-up runs on (hardware/assembly/faucet-and-umbilical.md §1).
CABINET_CLEAR_H = 755.7

# Lead and the 90° bend at R12 the umbilical takes behind the wall, before the collet. Typed:
# no run is drawn behind the rear face for the machine to read it off.
TURN_IN_LEAD_BEND = 50.5

# The PP1208E unions the +Y wall of back-top clamps, and the bulkhead rings its five stations
# land on.
# NAMED, not matched on a prefix: a body renamed out of the pack raises in `_facts.bb` here,
# where a prefix would leave the reading with one fewer fitting in it and nothing to say so.
UNIONS = ("bulkhead-carb", "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-water")
# The five body names are what `hardware/printed-parts/enclosure/bulkhead-ring/` exports today.
BULKHEAD_RINGS = ("bulkhead-ring-carb", "bulkhead-ring-co2", "bulkhead-ring-flavor-a",
                  "bulkhead-ring-flavor-b", "bulkhead-ring-water")

# The piece a hand hauls out of the front bay, both peristaltic pumps and their tubing aboard.
PUMP_CARTRIDGE = "enclosure-pump-cartridge"

# What two bodies struck to one figure may differ by and still be that figure. The boxes are an
# optimal-box reading of tessellated solids, so a ring's own 2 mm comes back 2.0000002.
TOL = 0.01


def agreed(what: str, readings: dict) -> float:
    """One figure off the several bodies struck to it, or a raise naming the spread.

    A page a customer sizes a cabinet slot from cannot quietly take the first of four fittings.
    If the wall's unions stop standing one distance proud of it, WHICH of them the published
    number came off is the whole question, and a doc written anyway answers it in silence."""
    lo, hi = min(readings.values()), max(readings.values())
    if hi - lo > TOL:
        spread = ", ".join(f"{n} {v:.4f}" for n, v in sorted(readings.items()))
        raise SystemExit(
            f"  the {what} no longer stand one figure off the face they are read from:\n"
            f"    {spread}\n"
            f"  install-envelope.md states one number for all of them. Say which, or say why "
            f"they differ, before this page tells a customer either.")
    return hi


def behind_the_rear_face():
    """The turn-in a cabinet has to give behind the wall, and the two figures it is made of.

    ONE READING, TWO PAGES. `assembly/faucet-and-umbilical.md` §1 sums this same turn-in into
    the umbilical's cut length, so it takes it from here rather than deriving it a second time
    — a figure a second page works out again is a figure one of them can hold stale.
    """
    f = _facts.read()
    rear = f.box.outer[3]

    # WHAT STANDS BEHIND THE REAR FACE. Each union is read off the wall's own outer plane, so
    # whatever is between the flange and that plane is already in the figure: the bulkhead
    # ring's pocket is cut one ring thickness INTO the face and the ring fills it, which is why
    # the two come out level and the ring buys the tube behind the wall nothing.
    collet = agreed("wall's unions", {n: f.bb(n).ymax - rear for n in UNIONS})
    ring = agreed("wall's bulkhead rings", {n: f.bb(n).ylen for n in BULKHEAD_RINGS})

    # AND THAT THE RINGS ARE STILL LEVEL WITH THAT FACE, because the page says so in words.
    # The figure above survives a ring that stands proud — it is measured past one — but the
    # sentence around it does not, and a customer reads the sentence.
    off = max(abs(f.bb(n).ymax - rear) for n in BULKHEAD_RINGS)
    if off > TOL:
        raise SystemExit(
            f"  the wall's bulkhead rings stand {off:.4f} mm off its outer face and no longer come out "
            f"level with it.\n  install-envelope.md says they lie flush, in the sentence the "
            f"turn-in is stated in.")

    return collet, ring


def main():
    f = _facts.read()
    front = f.box.outer[2]
    collet, ring = behind_the_rear_face()

    # WHAT THE FRONT OWES: how far the pump cartridge's aft face stands behind the front face,
    # which is how far forward of that face it has to come to clear the bay. Both pumps and
    # their tubing ride out on it, and it is the one service access on this machine that faces
    # the room instead of a wall. The page also calls that figure the pump cartridge's OWN
    # depth, which it is while the piece's face and the box's are one plane — held, not assumed.
    cart = f.bb(PUMP_CARTRIDGE)
    if abs(cart.ymin - front) > TOL:
        raise SystemExit(
            f"  the pump cartridge's face stands {cart.ymin - front:.4f} mm off the box's front "
            f"face.\n  install-envelope.md states the draw as the piece's own depth, which is "
            f"only that while the two are one plane.")

    variables = {
        "CABINET_CLEAR_H": f"{CABINET_CLEAR_H:.4g} mm",
        "COLLET_PROUD": f"{collet:g} mm",
        "BULKHEAD_RING_THICK": f"{ring:g} mm",
        "TURN_IN": f"{TURN_IN_LEAD_BEND + collet:g} mm",
        "CART_DRAW": f"{cart.ymax - front:.4g} mm",
    }
    substitute_md(MD, variables=variables)
    print(f"-> {MD.relative_to(_root)}")


if __name__ == "__main__":
    main()
