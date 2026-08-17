"""Doc-sync driver for hardware/assembly/finish-pack-ship.md.

Run: tools/cad-venv/bin/python hardware/assembly/_finish_pack_ship_sync.py
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


# ─── The Founder Edition run ──────────────────────────────────────────
# Source: marketing/target-market.md — units 001-050 at $7,500, hand-built one at a time. This
# bench is the per-unit repeatable one across that run, so both figures are read here.

founder_edition_count = 50
founder_edition_price_usd = 7500

# ─── Drained-fluid masses (water + flavor concentrate) ────────────────
# Source: estimated reservoir + carbonator volumes after air-purge per
# topology/fluid-topology.md "Air Purge In/Out". Carbonator nominal fill
# ~1.5 L; two 1 L flavor reservoirs hold ~0.5 L each of remaining
# concentrate at the typical mid-run state when a unit comes off the
# burn-in bench.

water_drained_kg = 1.5
flavor_drained_kg = 1.0

# ─── Carton + shipping envelope ───────────────────────────────────────

appliance_weight_low_kg = 10           # appliance alone, dry
appliance_weight_high_kg = 15          # appliance alone, dry, upper-bound

carton_gross_weight_low_kg = 15        # appliance + install kit + faucet bag + packaging
carton_gross_weight_high_kg = 20       # same, upper-bound

carton_length_cm = 60                  # external L along the longest carton dim
carton_width_cm = 50                   # external W
carton_height_cm = 50                  # external H

scale_precision_kg = 0.1               # tape-and-platform measurement resolution

# ─── Carrier ground-shipping thresholds ───────────────────────────────
# Source: UPS Ground / FedEx Ground residential package limits.

carrier_ground_limit_lb = 70
carrier_ground_limit_kg = 32           # = 70 lb rounded to whole kg (70 lb = 31.75 kg)

# ─── Procedure-level details ──────────────────────────────────────────

splash_check_tilt_deg = 15             # gentle tilt for splash audibility at step 2


def main():
    variables = {
        # Identity / Founder Edition.
        "FOUNDER_EDITION_COUNT": f"{founder_edition_count:.4g}",
        "FOUNDER_EDITION_PRICE": f"${founder_edition_price_usd:,}",
        # Drained-fluid masses.
        "WATER_DRAINED": f"~{water_drained_kg:.4g} kg",
        "FLAVOR_DRAINED": f"~{flavor_drained_kg:.4g} kg",
        # Carton + appliance weights.
        "APPLIANCE_W_LOW": f"{appliance_weight_low_kg:.4g}",
        "APPLIANCE_W_HIGH": f"{appliance_weight_high_kg:.4g} kg",
        "CARTON_W_LOW": f"{carton_gross_weight_low_kg:.4g}",
        "CARTON_W_HIGH": f"{carton_gross_weight_high_kg:.4g} kg",
        "SLOSH_CARTON_W": f"{carton_gross_weight_high_kg:.4g} kg",
        # Carton dimensions.
        "CARTON_L": f"{carton_length_cm:.4g}",
        "CARTON_W_DIM": f"{carton_width_cm:.4g}",
        "CARTON_H_DIM": f"{carton_height_cm:.4g} cm",
        # Scale + tilt.
        "SCALE_PRECISION": f"{scale_precision_kg:.4g} kg",
        "TILT_ANGLE": f"~{splash_check_tilt_deg:.4g}°",
        # Carrier threshold.
        "CARRIER_LIMIT_LB": f"{carrier_ground_limit_lb:.4g} lb",
        "CARRIER_LIMIT_KG": f"~{carrier_ground_limit_kg:.4g} kg",
    }

    substitute_md(
        _here / "finish-pack-ship.md",
        variables=variables,
    )
    print("-> finish-pack-ship.md")


if __name__ == "__main__":
    main()
