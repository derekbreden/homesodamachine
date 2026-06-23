"""Doc-sync driver for hardware/ledger/bom.md.

Run: tools/cad-venv/bin/python hardware/scripts/_bom_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent  # = hardware/scripts/
sys.path.insert(0, str(_here.parent / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "cold-core" / "reservoir"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet"))
sys.path.insert(0, str(_here.parent / "printed-parts" / "faucet" / "touch-flo-shell"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import foam_cap_attachment_xy_positions
from _reed_channels import reeds_per_reservoir
from docgen import substitute_md
from reservoir import insert_positions_for_side_plus_1
from touch_flo_shell import base_pod_centers


# Pressure vessel geometry: two laser-welded SS endcap plates per
# vessel, four 1/4" NPT ports tapped into the plates (water in, water
# out, CO2 in, PRV).
end_cap_plates_per_vessel = 2
vessel_ports_per_vessel = 4

# Flavor reservoirs per appliance.
reservoirs_per_build = 2

# Carbonator reeds (threshold-only). Per-reservoir count lives in
# `_reed_channels.py`.
reeds_per_carbonator = 2

# 12-valve manifold (V-A/B/C/D/E/F/G/H/I/J/KA/KB) per
# `topology/fluid-topology-trays.mmd`. Ten 3-port junctions split by
# geometry: 2 Y-dividers (Y-A/B, source-select trident) + 8 Tees
# (Y-C/D/E/F/G/H/KA/KB, in-line run + branch).
solenoid_count = 12
y_divider_count = 2
tee_count = 8

# Rear-panel umbilical port: 3 bulkheads on the back panel
# (1 carbonated water + 2 flavor). The same PP1208E SKU is reused
# for the reservoir-cap outlet ports (1 per reservoir).
panel_umbilical_bulkheads = 3

# Per-cap insert counts.
# Foam-shell: `foam_cap_attachment_xy_positions` is the list of (x, y)
# pairs for ONE face (4 corners + 2 mid-long-side = 6 per face); the
# foam shell has two such faces (top cap + bottom cap).
# Reservoir: `insert_positions_for_side_plus_1` is the list of (x, z)
# pairs for one reservoir cap (6 per cap).
inserts_per_foam_cap = len(foam_cap_attachment_xy_positions)
foam_caps_per_build = 2
inserts_per_reservoir_cap = len(insert_positions_for_side_plus_1)

# Reservoir cap vent filter: one ø13 PTFE membrane per cap.
vent_filters_per_reservoir_cap = 1


# ─── Derived totals ────────────────────────────────────────────────────

# Reeds.
reservoir_reeds_total = reeds_per_reservoir * reservoirs_per_build
total_reeds_per_build = reeds_per_carbonator + reservoir_reeds_total

# PP1208E (panel-umbilical only). The reservoir-cap outlet uses the
# PureSec B0968K4JRN single-piece 90° PTC bulkhead, so PP1208E serves
# only the rear-panel umbilical cluster.
pp1208e_per_build = panel_umbilical_bulkheads

# Foam-shell hardware (12 inserts + 12 M3 × 25 screws).
foam_cap_inserts_per_build = inserts_per_foam_cap * foam_caps_per_build
foam_cap_screws_per_build = foam_cap_inserts_per_build  # 1:1

# Reservoir-cap hardware (12 inserts + 12 M3 × 12 screws).
reservoir_cap_inserts_per_build = inserts_per_reservoir_cap * reservoirs_per_build
reservoir_cap_screws_per_build = reservoir_cap_inserts_per_build  # 1:1

# Touch-flo plate-to-shell hardware (3 inserts + 3 M3 × 12 screws, one
# per base pod).
touchflo_inserts_per_build = len(base_pod_centers)
touchflo_screws_per_build = touchflo_inserts_per_build  # 1:1

# Combined heat-set insert count across the appliance (27).
total_m3_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + touchflo_inserts_per_build
)

# Reservoir-cap vent filters per build (2).
vent_filters_per_build = vent_filters_per_reservoir_cap * reservoirs_per_build


def main():
    variables = {
        # Carbonator vessel.
        "END_CAPS": f"{end_cap_plates_per_vessel:.4g}",
        "VESSEL_PORTS": f"{vessel_ports_per_vessel:.4g}",
        # Reservoirs.
        "RESERVOIRS": f"{reservoirs_per_build:.4g}",
        "RESERVOIR_CAP_COUNT": f"{reservoirs_per_build:.4g}",
        # Reeds.
        "REEDS_PER_RES": f"{reeds_per_reservoir:.4g}",
        "CARB_REEDS": f"{reeds_per_carbonator:.4g}",
        "RES_REEDS_TOTAL": f"{reservoir_reeds_total:.4g}",
        "REEDS_TOTAL": f"{total_reeds_per_build:.4g}",
        # Flavor subsystem.
        "SOLENOIDS": f"{solenoid_count:.4g}",
        "Y_DIVIDERS": f"{y_divider_count:.4g}",
        "TEES": f"{tee_count:.4g}",
        "PP1208E_PANEL": f"{panel_umbilical_bulkheads:.4g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:.4g}",
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:.4g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:.4g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:.4g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
        "TOUCHFLO_INSERTS": f"{touchflo_inserts_per_build:.4g}",
        "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
        "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:.4g}",
        # Vent filters.
        "VENT_FILTERS": f"{vent_filters_per_build:.4g}",
    }

    substitute_md(
        _here.parent / "ledger" / "bom.md",
        variables=variables,
        expected_counts={
            "END_CAPS": 1,
            "VESSEL_PORTS": 2,
            "RESERVOIRS": 4,
            "RESERVOIR_CAP_COUNT": 1,
            "REEDS_PER_RES": 3,
            "CARB_REEDS": 2,
            "RES_REEDS_TOTAL": 3,
            "REEDS_TOTAL": 2,
            "SOLENOIDS": 2,
            "Y_DIVIDERS": 2,
            "TEES": 2,
            "PP1208E_PANEL": 1,
            "PP1208E_TOTAL": 1,
            "FOAM_INSERTS": 2,
            "FOAM_SCREWS": 2,
            "RES_INSERTS_PER_CAP": 1,
            "RES_INSERTS": 1,
            "RES_SCREWS": 1,
            "TOUCHFLO_INSERTS": 2,
            "TOUCHFLO_SCREWS": 2,
            "TOTAL_M3_INSERTS": 2,
            "VENT_FILTERS": 3,
        },
    )
    print("-> bom.md")


if __name__ == "__main__":
    main()
