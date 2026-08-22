"""Doc-sync driver for marketing/install-envelope.md.

The install envelope is about the cabinet the machine goes into, which belongs to
the customer, so it does not live under `hardware/` and no
`_enclosure_dimensions.py` owns its numbers. This driver sits in `tools/` with the
rest of the shared machinery.

IT STATES NO SILHOUETTE. The machine's own W x D x H is written where the box is cut —
`printed-parts/enclosure/enclosure/README.md` and `assembly/enclosure-mechanical.md` — and a
third copy here is a third thing to be wrong. What this page owes is the room AROUND the box:
the turn-in behind the rear wall and the draw in front of the cartridge. Those are measured in
a subprocess, because `machine_of` places the pack and puts the tree on the path itself, which
is a path this interpreter does not want.

Run: tools/cad-venv/bin/python tools/install_envelope_sync.py
"""

import json
import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
REPO = _here.parents[1]
sys.path.insert(0, str(REPO / "tools"))

from docgen import substitute_md


# The sink base's interior clear height: a 34.5" carcass less the 4" toe kick
# less the 3/4" deck. Cabinet standard, not project geometry — the same
# derivation the umbilical's length stack-up runs on
# (hardware/assembly/faucet-and-umbilical.md §1).
CABINET_CLEAR_H = 755.7

# Put the enclosure module on the path and ask it for the machine. `machine_of` places
# the pack and hands back the box sized on it, putting the rest of the tree on the path
# itself, so this probe names one directory. Emitted as JSON on stdout.
_PROBE = """
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "enclosure"))
sys.path.insert(0, str(Path(sys.argv[1]) / "port-ring"))
sys.path.insert(0, str(Path(sys.argv[1]).parents[1] / "reference" / "jg-bulkhead-union"))
import enclosure, port_ring, jg_bulkhead_union
_pack, box = enclosure.machine_of()
o = box.outer
cart = box.collet_plate["fore_y"] - enclosure.cap_kiss - o[2] if box.collet_plate else 0.0
print(json.dumps({"field": port_ring.THICK,
                  "collet": jg_bulkhead_union.PROUD_LENGTH,
                  "cart": cart}))
"""


# The tree the machine's box is drawn in. The doc states no silhouette — that is
# `printed-parts/enclosure`'s own README and `assembly/enclosure-mechanical.md`, both cut by
# the run that places the pack — so the box is measured here only for what the ROOM around it
# owes: the draw the cartridge takes out of the front face.
TREE = "hardware"


def measure(root):
    """What the room around the box owes it, read off the placed pack in its own
    interpreter: the collet's proud length, its port ring's field, and the cartridge draw."""
    enc = root / "printed-parts" / "enclosure"
    r = subprocess.run(
        [sys.executable, "-c", _PROBE, str(enc)],
        capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise SystemExit(f"{root.relative_to(REPO)}: could not measure the box\n{r.stderr}")
    return json.loads(r.stdout)


# Lead and the 90° bend at R12 the umbilical takes behind the wall, before the collet.
# Typed: no run is drawn behind the rear face for the machine to read it off.
TURN_IN_LEAD_BEND = 50.5


def main():
    md = REPO / "marketing" / "install-envelope.md"
    variables = {"CABINET_CLEAR_H": f"{CABINET_CLEAR_H:.4g} mm"}
    m = measure(REPO / TREE)

    # What the wall owes a fitting BEHIND it, off the two parts that state it: the
    # collet stands proud of the face it bears on, and that face is its port ring's
    # rather than the wall's.
    variables["COLLET_PROUD"] = f"{m['collet']:g} mm"
    variables["PORT_RING_THICK"] = f"{m['field']:g} mm"
    variables["TURN_IN"] = f"{TURN_IN_LEAD_BEND + m['collet'] + m['field']:g} mm"

    # WHAT THE FRONT OWES. The pump cartridge draws straight out of the bay with both pumps
    # aboard, so what the room has to give it is its own depth — exterior face to the aft
    # face that stops on the collet plate. The one service access on this machine that
    # faces the room instead of the wall.
    variables["CART_DRAW"] = f"{m['cart']:.4g} mm"

    substitute_md(md, variables=variables)
    print("-> marketing/install-envelope.md")


if __name__ == "__main__":
    main()
