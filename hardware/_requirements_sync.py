"""Top-level design-requirement constants — source-of-truth values that
requirements.md (and, in the long run, any part dimensioned by them)
should consume rather than re-state.

Requirements numbers are *first-class design targets*, not consequences
of part geometry. The appliance's two-flavor architecture and ten-year
design life are the things every downstream choice has to satisfy;
they live here so requirements.md prose stays mechanically in sync
with the named constant whenever the value is revisited.

Scope kept narrow on purpose:

- Only the genuine top-level requirements: the flavor channel count
  and the design lifetime. Every other number in requirements.md is
  either a frozen prototype-build count (the §5 table — see the
  per-line "Qty" cells), an industry-standard / manufacturer-published
  reference value (the Bambu H2C build envelope and minimum layer
  height in §6), or a forward-reference handled by other docs
  (future.md, bom.md). Those are left raw — substituting them here
  would imply a derivation that doesn't exist.

- Numbers that *look* derived but aren't yet wired through this module
  (the prototype qty=2 for the two Kamoer pumps and the two Platypus
  bottles, the "2 peristaltic pumps" sentence in §4) are tagged with
  FLAVOR_COUNT so the connection is visible in source, even though
  the §5 prototype table is intentionally treated as a frozen-history
  parts-list snapshot rather than a live derivation.

Follow-up flagged for a later sweep (do not fix in this pass — only
this file + requirements.md are in scope):

- `hardware/cut-parts/compressor-shroud/_compressor_shroud_dimensions.py`
  carries its own `design_life_yr = 10` constant, framed locally as
  "G90 coating life in humid-kitchen ambient". The value happens to
  match the appliance design lifetime here, but the two are tracked
  independently. Promoting `design_life_yr` to a shared constant
  (e.g. imported from this module) would make the dependency
  explicit, but that crosses out of this sync's read-only-elsewhere
  budget and is left for a follow-up.

Run as a script to substitute requirements.md:

    tools/cad-venv/bin/python _requirements_sync.py
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
        "FLAVOR_COUNT": f"{flavor_count:g}",
        "DESIGN_LIFE_YR": f"{design_life_yr:g}",
        "DESIGN_LIFE_LABEL": f"{design_life_yr:g}-year",
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
