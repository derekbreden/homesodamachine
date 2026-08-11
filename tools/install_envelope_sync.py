"""Doc-sync driver for marketing/install-envelope.md.

The install envelope is one document for every edition — the cabinet belongs to
the customer and does not change with which machine goes into it — so it cannot
live inside an edition's tree, and no edition's `_enclosure_dimensions.py` can
own its numbers. This driver sits in `tools/` with the rest of the shared
machinery and reads every edition web/lib/editions.js declares.

Each edition's silhouette is READ OFF ITS BOX (`enclosure.machine_of()`), the same
source its own README uses, so the shared doc and the per-edition docs cannot
state different machines. Editions are measured in subprocesses because their
modules are same-named duplicates that cannot coexist in one interpreter.

Run: tools/cad-venv/bin/python tools/install_envelope_sync.py
"""

import json
import re
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

# Measured inside the edition's own tree: put its enclosure module on the path and ask
# it for the machine. `machine_of` places the edition's own pack and hands back the box
# sized on it, putting the rest of the tree on the path itself, so this probe names one
# directory and the edition names the others. Emitted as JSON on stdout.
_PROBE = """
import json, sys
from pathlib import Path
sys.path.insert(0, str(Path(sys.argv[1]) / "enclosure"))
sys.path.insert(0, str(Path(sys.argv[1]) / "port-ring"))
sys.path.insert(0, str(Path(sys.argv[1]).parents[1] / "reference" / "jg-bulkhead-union"))
import enclosure, port_ring, jg_bulkhead_union
_pack, box = enclosure.machine_of()
o = box.outer
print(json.dumps({"w": o[1] - o[0], "d": o[3] - o[2], "h": o[5] - o[4],
                  "field": port_ring.THICK,
                  "collet": jg_bulkhead_union.PROUD_LENGTH}))
"""


def editions():
    """(id, label, root) per edition web/lib/editions.js declares, in order."""
    src = (REPO / "web" / "lib" / "editions.js").read_text()
    out = []
    for eid, label, dir_src in re.findall(
        r'id:\s*"([^"]+)".*?label:\s*"([^"]+)".*?dir:\s*\[([^\]]*)\]', src, re.S
    ):
        root = REPO.joinpath(*re.findall(r'"([^"]+)"', dir_src))
        if root.is_dir():
            out.append((eid, label, root))
    if not out:
        raise SystemExit("no editions found in web/lib/editions.js")
    return out


def measure(root):
    """The edition's outer W/D/H, read off its own box in its own interpreter."""
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
    expected = {"CABINET_CLEAR_H": 2}

    keys = []
    for eid, label, root in editions():
        m = measure(root)
        if not keys:
            # What the wall owes a fitting BEHIND it, off the two parts that state it: the
            # collet stands proud of the face it bears on, and that face is the port field's
            # crown rather than the wall.
            variables["COLLET_PROUD"] = f"{m['collet']:g} mm"
            variables["PORT_FIELD_PROUD"] = f"{m['field']:g} mm"
            variables["TURN_IN"] = f"{TURN_IN_LEAD_BEND + m['collet'] + m['field']:g} mm"
            expected.update({"COLLET_PROUD": 1, "PORT_FIELD_PROUD": 1, "TURN_IN": 1})
        key = eid.upper()
        keys.append(key)
        variables[f"{key}_WDH"] = f"{m['w']:.4g} × {m['d']:.4g} × {m['h']:.4g} mm"
        variables[f"{key}_FOOTPRINT"] = f"{m['w'] * m['d'] / 1e6:.3f} m²"
        variables[f"{key}_CLEAR_TOP"] = f"{CABINET_CLEAR_H - m['h']:.4g} mm"
        for suffix in ("WDH", "FOOTPRINT", "CLEAR_TOP"):
            expected[f"{key}_{suffix}"] = 1
        print(f"   {label}: {variables[f'{key}_WDH']}")

    # A row standing behind no edition is a silhouette nothing here can measure: its
    # figures hold whatever they last said, and the doc sends a customer to a cabinet for
    # an appliance the repo does not build. The table's own markers name the editions it
    # claims, so they are read back against the ones that answered.
    claimed = set(re.findall(r"\]\(([A-Z0-9]+)_(?:WDH|FOOTPRINT|CLEAR_TOP)\)", md.read_text()))
    orphans = sorted(claimed - set(keys))
    if orphans:
        raise SystemExit(
            f"marketing/install-envelope.md carries {', '.join(o.lower() for o in orphans)} "
            f"— no edition in web/lib/editions.js measures it")

    # An edition with no row in the table is the failure this asserts: the doc
    # would silently describe fewer machines than the repo holds.
    substitute_md(md, variables=variables, expected_counts=expected)
    print("-> marketing/install-envelope.md")


if __name__ == "__main__":
    main()
