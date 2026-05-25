"""BOM sync — pulls per-build part counts into `bom.md`.

The BOM is mostly prices, SKUs, and pack-amortization math, which are
external/volatile and stay raw. What this script handles is the
per-build part-count side: how many vessel ports, how many reservoir
caps, how many heat-set inserts, how many reeds. Those numbers are
design choices — some live in the geometry source (length of
`foam_cap_attachment_xz_positions`, length of `insert_positions_
for_side_plus_1`), others are BOM-defined constants pinned here.

Wherever the same count appears in multiple BOM cells (qty column +
prose explanation), every occurrence gets the same `[value](NAME)`
marker so they can't drift apart.

What this script DOES NOT touch:
- Prices, SKUs, ASINs (external / volatile).
- Industry-standard dimensions ("1/4" NPT", "5" OD") cited as
  catalog spec text.
- Line $ totals and pack-amortization math, which depend on per-unit
  price as well as quantity — if those need to change, the price
  changed, and the line is being rewritten by hand anyway.

Run:

    tools/cad-venv/bin/python hardware/_bom_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent  # = hardware/
sys.path.insert(0, str(_here / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_here / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_here / "printed-parts" / "cold-core" / "reservoir"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import foam_cap_attachment_xz_positions
from docgen import substitute_md
from generate_step_cadquery import insert_positions_for_side_plus_1


# ─── BOM-defined design choices (pinned here) ─────────────────────────

# Pressure vessel geometry: two laser-welded SS endcap plates per
# vessel (one vessel per appliance), four 1/4" NPT ports tapped into
# the plates (water in, water out, CO2 in, PRV).
end_cap_plates_per_vessel = 2
vessel_ports_per_vessel = 4

# Reservoirs: two flavor reservoirs per appliance. Sets the multiplier
# on every reservoir-side count (caps, cap screws, vent filters, etc.).
reservoirs_per_build = 2

# Level sensing: carbonator gets 2 reeds (threshold-only), each flavor
# reservoir gets 4 reeds (5-state fuel gauge). See
# `printed-parts/cold-core/reservoir/level-sensing.md`.
reeds_per_carbonator = 2
reeds_per_reservoir = 4

# Flavor subsystem: 12-valve manifold (V-A/B/C/D/E/F/G/H/I/J/KA/KB)
# per `topology/fluid-topology-manifold.mmd`; 10 Y-dividers
# (Y-A/B/C/D/E/F/G/H/KA/KB) in the matching manifold.
solenoid_count = 12
y_divider_count = 10

# Rear-panel umbilical port: 3 bulkheads on the back panel
# (1 carbonated water + 2 flavor). The same PP1208E SKU is reused
# for the reservoir-cap outlet ports (1 per reservoir).
panel_umbilical_bulkheads = 3

# Per-cap insert / screw counts (foam-shell + reservoir).
# Foam-shell: `foam_cap_attachment_xz_positions` is the list of (x, z)
# pairs for ONE face (4 corners + 2 mid-long-side = 6 per face); the
# foam shell has two such faces (top cap + bottom cap), so total
# inserts = len × 2.
# Reservoir: `insert_positions_for_side_plus_1` is the list of (x, z)
# pairs for one reservoir cap (6 per cap).
inserts_per_foam_cap = len(foam_cap_attachment_xz_positions)
foam_caps_per_build = 2
inserts_per_reservoir_cap = len(insert_positions_for_side_plus_1)

# Reservoir cap vent filter: one ø13 PTFE membrane per cap.
vent_filters_per_reservoir_cap = 1


# ─── Derived totals (kept here so the BOM never re-does the arithmetic) ──

# Reeds.
reservoir_reeds_total = reeds_per_reservoir * reservoirs_per_build
total_reeds_per_build = reeds_per_carbonator + reservoir_reeds_total

# PP1208E (reservoir-cap outlet + panel-umbilical, same SKU):
# 1 bulkhead per reservoir cap + the panel-umbilical bulkheads.
pp1208e_per_build = reservoirs_per_build + panel_umbilical_bulkheads

# Foam-shell hardware (12 inserts + 12 M3 × 25 screws).
foam_cap_inserts_per_build = inserts_per_foam_cap * foam_caps_per_build
foam_cap_screws_per_build = foam_cap_inserts_per_build  # 1:1

# Reservoir-cap hardware (12 inserts + 12 M3 × 12 screws).
reservoir_cap_inserts_per_build = inserts_per_reservoir_cap * reservoirs_per_build
reservoir_cap_screws_per_build = reservoir_cap_inserts_per_build  # 1:1

# Combined heat-set insert count across the appliance (24).
total_m3_inserts_per_build = (
    foam_cap_inserts_per_build + reservoir_cap_inserts_per_build
)

# Reservoir-cap vent filters per build (2).
vent_filters_per_build = vent_filters_per_reservoir_cap * reservoirs_per_build


def main():
    variables = {
        # Carbonator vessel.
        "END_CAPS": f"{end_cap_plates_per_vessel:g}",
        "VESSEL_PORTS": f"{vessel_ports_per_vessel:g}",
        # Reservoirs.
        "RESERVOIRS": f"{reservoirs_per_build:g}",
        "RESERVOIR_CAP_COUNT": f"{reservoirs_per_build:g}",
        # Reeds.
        "REEDS_PER_RES": f"{reeds_per_reservoir:g}",
        "CARB_REEDS": f"{reeds_per_carbonator:g}",
        "RES_REEDS_TOTAL": f"{reservoir_reeds_total:g}",
        "REEDS_TOTAL": f"{total_reeds_per_build:g}",
        # Flavor subsystem.
        "SOLENOIDS": f"{solenoid_count:g}",
        "Y_DIVIDERS": f"{y_divider_count:g}",
        "PP1208E_PANEL": f"{panel_umbilical_bulkheads:g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:g}",
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:g}",
        "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:g}",
        # Vent filters.
        "VENT_FILTERS": f"{vent_filters_per_build:g}",
    }

    substitute_md(
        _here / "bom.md",
        variables=variables,
        expected_counts={
            "END_CAPS": 1,
            "VESSEL_PORTS": 2,
            "RESERVOIRS": 3,
            "RESERVOIR_CAP_COUNT": 1,
            "REEDS_PER_RES": 3,
            "CARB_REEDS": 2,
            "RES_REEDS_TOTAL": 3,
            "REEDS_TOTAL": 2,
            "SOLENOIDS": 2,
            "Y_DIVIDERS": 2,
            "PP1208E_PANEL": 1,
            "PP1208E_TOTAL": 2,
            "FOAM_INSERTS": 2,
            "FOAM_SCREWS": 2,
            "RES_INSERTS_PER_CAP": 2,
            "RES_INSERTS": 1,
            "RES_SCREWS": 1,
            "TOTAL_M3_INSERTS": 2,
            "VENT_FILTERS": 3,
        },
    )
    print("-> bom.md")


if __name__ == "__main__":
    main()
