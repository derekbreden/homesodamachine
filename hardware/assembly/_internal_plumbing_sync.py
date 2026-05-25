"""Doc-sync driver for internal-plumbing.md.

Strategy: hybrid (A)/(C). The internal-plumbing procedure is overwhelmingly
strategy (C) — "leave raw" — because the dimensional content is one of
four kinds, none of which has a project-internal source of truth:

1. **External standards baked into SKU names** — 1/4" OD LLDPE, 3/8" NPT,
   3/8" MFL, 3/8" FFL, 1/4" PTC, 5/16" tube. Each is the catalog identity
   of the off-the-shelf part. There is no "source" to derive these from;
   they ARE the part.
2. **Catalog specs** — 12 V pump bus, 100 PSI / 90 PSI pressures,
   0.01 µm filter rating, 1.3 GPM, 10 ft silicone roll. Each is published
   by the manufacturer. The BOM ([`../bom.md`](../bom.md)) is the canonical
   place for SKU specs; the procedure repeats the most-load-bearing ones
   in line so the bench tech doesn't have to flip between tabs.
3. **Counts derived from topology** — 12 valves, 10 Y-dividers, 2 pumps,
   22 PTC tube terminations. These come from
   [`../topology/fluid-topology.md`](../topology/fluid-topology.md)'s
   valve/Y/segment truth table, which does not currently expose
   constants. Adding sync infrastructure for topology would belong in
   that file, not here. Per the coordination rules of the current
   sweep ("New shared constant needed? STOP, flag."), we do not add
   topology constants from this side.
4. **Procedure-loose dimensions** — ~12" silicone hose cut from the 10-ft
   roll, ~6" zip-tie span, ~150 × 200 mm manifold footprint, "snug + 1
   turn past hand-tight", "past finger-tight". These are intentionally
   approximate and would be misleading if substituted from a fixed
   numeric constant.

Strategy (A) is wired for exactly **one** site: the CO2 inlet point on
the foam-cap top, which the prose cites at `x=0, z=−68.75` with a
`Ø6.5` tube clearance hole. Both numbers are real upstream constants in
[`../printed-parts/cold-core/foam-cap/foam_cap.py`](../printed-parts/cold-core/foam-cap/foam_cap.py)
(`co2_inlet_z`, `co2_tube_clearance_radius`) so they sync against
source rather than being hand-typed.

Run from this directory or via absolute path:

    tools/cad-venv/bin/python hardware/assembly/_internal_plumbing_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
        / "foam-cap"
    ),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cadlib"
    ),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
    ),
)

import foam_cap as foam_cap_gen  # noqa: E402

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # Foam-cap CO2 inlet coordinate (Z, in cold-core foam-shell
        # coordinates) and the tube-clearance hole diameter that lets
        # the 1/4" OD LLDPE pass through cap + lid. Source-of-truth:
        # `co2_inlet_z` and `2 × co2_tube_clearance_radius` in
        # foam-cap/foam_cap.py.
        "COTWO_INLET_Z": f"{foam_cap_gen.co2_inlet_z:g}",
        "COTWO_TUBE_D": f"{2 * foam_cap_gen.co2_tube_clearance_radius:g}",
    }

    substitute_md(
        _here / "internal-plumbing.md",
        variables=variables,
        expected_counts={
            "COTWO_INLET_Z": 1,
            "COTWO_TUBE_D": 1,
        },
    )
    print("-> internal-plumbing.md")


if __name__ == "__main__":
    main()
