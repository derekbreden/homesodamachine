"""Flute the faucet's base — the one printed piece that stands in the open on a counter.

A THIRD TREE, FOR THE SAME REASON THE OTHER TWO ARE APART. The box's six pieces and the cold
core's three are two rules because one rule over both comes back around on itself
(`flute_payload_enclosure.py`). This tree comes back around on nothing — no assembly under
`printed-parts/faucet/` reads a payload the box or the core writes — but the partition is the
same one either way: `inventory.py` writes all three entries out of one traced run of
`flute_payload.py`, on the directories `ENCLOSURE_DIRS`, `COLD_CORE_DIRS` and `FAUCET_DIRS`
name. A run over this tree opens `faucet-shell-base.step` beside its printed mesh, cuts the
payload the viewer draws, and grafts that surface into `faucet-shell.step.mesh` — the two
pieces as assembled, which is what `faucet-assembly` and `/3d` open.
"""

import flute_payload


if __name__ == "__main__":
    raise SystemExit(flute_payload.main(flute_payload.FAUCET_DIRS))
