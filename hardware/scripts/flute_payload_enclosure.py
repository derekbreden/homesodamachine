"""Flute the box's six pieces. The cold core's three are `flute_payload_cold_core.py`.

ONE RUN OVER BOTH TREES IS ONE RULE, AND ONE RULE HERE COMES BACK AROUND. The cold core's
payloads are read by `foam_assembly.py`, the box is built from the foam assembly, and the
enclosure's payloads are cut off the box — so a single fluting rule waits on the enclosure to
produce a payload the enclosure's own inputs are made from, and bazel will not load a graph like
that at all. Nothing passes between the two trees, so they are two rules: `inventory.py` writes
this entry and its sibling's out of one traced run of `flute_payload.py`, partitioned on the same
directories `flute_payload.ENCLOSURE_DIRS` and `COLD_CORE_DIRS` name.
"""

import flute_payload


if __name__ == "__main__":
    raise SystemExit(flute_payload.main(flute_payload.ENCLOSURE_DIRS))
