"""Doc-sync driver for hardware/requirements.md.

Run: tools/cad-venv/bin/python hardware/_requirements_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
from docgen import substitute_md


# ─── Top-level design requirements ────────────────────────────────────
# The two values every part downstream of the requirements has to
# honor. Anything else in requirements.md is prototype-history or
# manufacturer-published reference data; only these are live targets.

flavor_count = 2                # Independent flavor channels (each
                                # primed, valve-locked, dispensed in
                                # parallel with the carbonated-water
                                # path). Drives reservoir count, pump
                                # count, foam-shell pocket count, and
                                # the per-flavor solenoid groups in
                                # the fluid topology.
design_life_yr = 10             # Unmaintained appliance design life,
                                # in years. The 10-year owner is the
                                # design target; longer-tail use is
                                # allowed by the service paths
                                # (reservoirs, foam shell, internal
                                # plumbing not glued / potted) but
                                # not optimized for.


def main():
    variables = {
        "FLAVOR_COUNT": f"{flavor_count:.4g}",
        "DESIGN_LIFE_YR": f"{design_life_yr:.4g}",
        "DESIGN_LIFE_LABEL": f"{design_life_yr:.4g}-year",
    }

    substitute_md(
        _here / "requirements.md",
        variables=variables,
        expected_counts={
            # §1 line: "There are 2 separate parallel lines, one for
            # each flavor".
            # §4 line: "There are only 2 peristaltic pumps, one
            # dedicated to each flavor".
            "FLAVOR_COUNT": 2,
            # §4 line: "The target is 10 years".
            "DESIGN_LIFE_YR": 1,
            # §4 line: "The 10-year owner is the design target".
            "DESIGN_LIFE_LABEL": 1,
        },
    )
    print("-> requirements.md")


if __name__ == "__main__":
    main()
