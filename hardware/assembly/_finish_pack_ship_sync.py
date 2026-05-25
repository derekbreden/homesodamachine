"""Finish, pack, ship — procedure-level constants for the per-unit
ship-bench README. No CAD geometry; this is the production-procedure
counterpart to the part-level dimension modules elsewhere in this tree.

Most numbers are working-assumption estimates that calibrate against
the first-unit measurement (see Open item 7 in finish-pack-ship.md);
they live here so the prose stays in sync once the first carton
measures and constants here are updated.

`founder_edition_count` is the one number with an upstream source —
the canonical nameplate dimension module already owns it because the
plaque needs the count baked into the per-unit serial range. Imported
read-only so a future shift (e.g., the Founder Edition run extends
past 50) propagates through both prose surfaces from one edit.

Run as a script to substitute the README:

    tools/cad-venv/bin/python _finish_pack_ship_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hardware = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hardware / "printed-parts" / "enclosure" / "nameplate"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from docgen import substitute_md
from _nameplate_dimensions import founder_edition_count  # type: ignore[import-not-found]


# ─── Founder Edition pricing ──────────────────────────────────────────
# Source: marketing/target-market.md "Founder Edition — units 001-050,
# $7,500". Procedure-level prose cites the price three times — at the
# unboxing-care line, the carrier-declared-value line, and the
# handoff-email line. The number is a marketing-tier commitment, not a
# physical measurement; defined here so the three sites stay locked.

founder_edition_price_usd = 7500

# ─── Drained-fluid masses (water + flavor concentrate) ────────────────
# Source: estimated reservoir + carbonator volumes after air-purge per
# topology/fluid-topology.md "Air Purge In/Out". Carbonator nominal fill
# ~1.5 L; two 1 L flavor reservoirs hold ~0.5 L each of remaining
# concentrate at the typical mid-run state when a unit comes off the
# burn-in bench. Refine after first-unit weigh-out.

water_drained_kg = 1.5
flavor_drained_kg = 1.0

# ─── Carton + shipping envelope (working assumptions) ─────────────────
# Source: rough estimate for the appliance + install kit + faucet-and-
# umbilical bag in a single carton; calibrated by the first-unit
# measurement per Open item 7. The two-number range (low–high) is
# preserved as a paired pair (e.g., 15–20 kg) — both ends move together
# when the working assumption shifts.

appliance_weight_low_kg = 10           # appliance alone, dry, off the burn-in bench
appliance_weight_high_kg = 15          # appliance alone, dry, upper-bound estimate

carton_gross_weight_low_kg = 15        # appliance + install kit + faucet bag + packaging
carton_gross_weight_high_kg = 20       # same, upper-bound estimate

carton_length_cm = 60                  # external L along the longest carton dim
carton_width_cm = 50                   # external W
carton_height_cm = 50                  # external H

scale_precision_kg = 0.1               # tape-and-platform measurement resolution

# ─── Carrier ground-shipping thresholds ───────────────────────────────
# Source: UPS Ground / FedEx Ground residential package limits
# (industry standard; both carriers cap residential ground at 70 lb).
# Above this, the package routes LTL freight (Open item 1). Listed here
# so the threshold-vs-expected-envelope comparison in step 8 lives in
# one place.

carrier_ground_limit_lb = 70
carrier_ground_limit_kg = 32           # = 70 lb rounded to whole kg (70 lb = 31.75 kg)

# ─── Procedure-level details ──────────────────────────────────────────
# Source: bench-procedure parameters; revise as the procedure firms up.

splash_check_tilt_deg = 15             # gentle tilt for splash audibility at step 2


def main():
    variables = {
        # Identity / Founder Edition.
        "FOUNDER_EDITION_COUNT": f"{founder_edition_count:g}",
        "FOUNDER_EDITION_PRICE": f"${founder_edition_price_usd:,}",
        # Drained-fluid masses.
        "WATER_DRAINED": f"~{water_drained_kg:g} kg",
        "FLAVOR_DRAINED": f"~{flavor_drained_kg:g} kg",
        # Carton + appliance weights.
        "APPLIANCE_W_LOW": f"{appliance_weight_low_kg:g}",
        "APPLIANCE_W_HIGH": f"{appliance_weight_high_kg:g} kg",
        "CARTON_W_LOW": f"{carton_gross_weight_low_kg:g}",
        "CARTON_W_HIGH": f"{carton_gross_weight_high_kg:g} kg",
        "SLOSH_CARTON_W": f"{carton_gross_weight_high_kg:g} kg",
        # Carton dimensions.
        "CARTON_L": f"{carton_length_cm:g}",
        "CARTON_W_DIM": f"{carton_width_cm:g}",
        "CARTON_H_DIM": f"{carton_height_cm:g} cm",
        # Scale + tilt.
        "SCALE_PRECISION": f"{scale_precision_kg:g} kg",
        "TILT_ANGLE": f"~{splash_check_tilt_deg:g}°",
        # Carrier threshold.
        "CARRIER_LIMIT_LB": f"{carrier_ground_limit_lb:g} lb",
        "CARRIER_LIMIT_KG": f"~{carrier_ground_limit_kg:g} kg",
    }

    substitute_md(
        _here / "finish-pack-ship.md",
        variables=variables,
        expected_counts={
            "FOUNDER_EDITION_COUNT": 4,
            "FOUNDER_EDITION_PRICE": 4,
            "WATER_DRAINED": 1,
            "FLAVOR_DRAINED": 1,
            "APPLIANCE_W_LOW": 1,
            "APPLIANCE_W_HIGH": 1,
            "CARTON_W_LOW": 3,
            "CARTON_W_HIGH": 3,
            "SLOSH_CARTON_W": 1,
            "CARTON_L": 1,
            "CARTON_W_DIM": 1,
            "CARTON_H_DIM": 1,
            "SCALE_PRECISION": 1,
            "TILT_ANGLE": 1,
            "CARRIER_LIMIT_LB": 1,
            "CARRIER_LIMIT_KG": 1,
        },
    )
    print("-> finish-pack-ship.md")


if __name__ == "__main__":
    main()
