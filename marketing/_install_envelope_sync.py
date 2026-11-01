"""Doc-sync driver for marketing/install-envelope.md.

Run: tools/cad-venv/bin/python marketing/_install_envelope_sync.py

The install envelope is the cabinet the machine goes into. That cabinet belongs to the customer,
so no `_enclosure_dimensions.py` under `hardware/` owns its numbers, and this driver stands
beside the page it writes the way every other doc-sync driver stands beside its own.

IT STATES NO SILHOUETTE. The machine's own W x D x H is written where the box is cut —
`printed-parts/enclosure/enclosure/README.md` and `assembly/enclosure-mechanical.md` — and a
third copy here is a third thing to be wrong. What this page owes is the room AROUND the box:
the turn-in behind the +Y wall of back-top.

EVERY FIGURE IS A PLACED BODY READ OFF A FACE OF THE BOX, and not a part's own datum carried
here by arithmetic. What a cabinet has to give behind the wall is how far the fittings stand off
the WALL'S OUTER FACE; `jg_bulkhead_union.PROUD_LENGTH` is how far one stands off the face its
flange bears on. The identification tiles sit inside their rear channels. `_facts` — the
machine as the last build wrote it down — is what is read here, and
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

# 38.5 mm straight lead for the collar/release access plus the 4 mm stock's R25 bend. Typed:
# no run is drawn behind the rear face for the machine to read it off.
TURN_IN_LEAD_BEND = 38.5 + 25.0

# The PP1208E unions the +Y wall of back-top clamps, and the bulkhead rings its five stations
# land on.
# NAMED, not matched on a prefix: a body renamed out of the pack raises in `_facts.bb` here,
# where a prefix would leave the reading with one fewer fitting in it and nothing to say so.
UNIONS = ("bulkhead-carb", "bulkhead-flavor-a", "bulkhead-flavor-b", "bulkhead-water")
# The five body names are what `hardware/printed-parts/enclosure/bulkhead-ring/` exports today.
BULKHEAD_RINGS = ("bulkhead-ring-carb", "bulkhead-ring-co2", "bulkhead-ring-flavor-a",
                  "bulkhead-ring-flavor-b", "bulkhead-ring-water")


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
    """Read fitting projection, tile thickness and tile inset from the installed bodies.

    ONE READING, TWO PAGES. `assembly/faucet-and-umbilical.md` §1 sums this same turn-in into
    the umbilical's cut length, so it takes it from here rather than deriving it a second time
    — a figure a second page works out again is a figure one of them can hold stale.
    """
    f = _facts.read()
    rear = f.box.outer[3]

    # Each union is read off the wall's outer plane. The tile and channel dimensions
    # are separate readings; a tile face does not redefine the cabinet datum.
    collet = max(f.bb(n).ymax - rear for n in UNIONS)
    ring = agreed("wall's bulkhead rings", {n: f.bb(n).ylen for n in BULKHEAD_RINGS})

    recess = agreed("identification tile insets",
                    {n: rear - f.bb(n).ymax for n in BULKHEAD_RINGS})
    return collet, ring, recess


def main():
    collet, ring, recess = behind_the_rear_face()

    variables = {
        "CABINET_CLEAR_H": f"{CABINET_CLEAR_H:.4g} mm",
        "COLLET_PROUD": f"{collet:g} mm",
        "BULKHEAD_RING_THICK": f"{ring:g} mm",
        "BULKHEAD_RING_RECESS": f"{recess:g} mm",
        "TURN_IN": f"{TURN_IN_LEAD_BEND + collet:g} mm",
    }
    substitute_md(MD, variables=variables)
    print(f"-> {MD.relative_to(_root)}")


if __name__ == "__main__":
    main()
