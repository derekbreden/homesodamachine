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
sys.path.insert(0, str(_here.parent / "reference" / "beduan-solenoid"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _cold_core_interface import attachment_xy_positions, deck_mounts, deck_mount_xy
from _reed_channels import reeds_per_reservoir
from docgen import substitute_md
from reservoir import insert_positions_for_side_plus_1
from touch_flo_shell import base_pod_centers

import importlib.util


def _load_module(name: str, file_path: Path):
    """Load a Python file as a uniquely-named module."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(file_path.parent))
    spec.loader.exec_module(module)
    return module


# Evaporator-coil copper consumption (§5 GOORY row) — pitch and wrap arc
# from the coil-mandrel generator, whose printed groove enforces them.
_coil_mandrel_gen = _load_module(
    "bom_coil_mandrel_gen",
    _here.parent / "printed-parts" / "cold-core" / "coil-mandrel" / "coil_mandrel.py",
)


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

# 10-valve manifold (V-A/B/C/D/E/F/G/H/I/J) per
# `topology/fluid-topology-trays.mmd`. Eight 3-port junctions split by
# geometry: 1 Y-divider (Y-H, the trident) + 7 Tees (in-line run +
# branch). Which a junction is follows the pose of the pair it joins AND
# the room the fitting has. Every tray lies plate-up, so a junction
# reaching between trays can only be a Tee — that is six of them. The two
# bag circuits are the only pairs meeting on one tray, and they part: Y-H
# has a column ahead of it in the loft and takes the trident; Y-E has a
# strip a fitting's own diameter deep between the pump row and the head
# column, and takes a Tee standing across it.
solenoid_count = 10
y_divider_count = 1
tee_count = 7

# Rear-panel PP1208E bulkheads. Umbilical port: 3 on the back panel
# (1 carbonated water + 2 flavor). Water inlet: 1 more, same SKU and
# panel hole (the customer-facing 1/4" QC potable-water inlet).
panel_umbilical_bulkheads = 3
panel_water_inlet_bulkheads = 1

# Per-cap insert counts.
# Foam caps: `attachment_xy_positions` is the list of (x, y) pairs for one
# shell face (4 corners + 2 mid-long-side = 6); a cap stack fastens on each
# face (top mouth-up, bottom mouth-down), inserts pressed from each face.
# Reservoir: `insert_positions_for_side_plus_1` is the list of (x, z)
# pairs for one reservoir cap (6 per cap).
foam_cap_faces = 2
inserts_per_foam_cap_face = len(attachment_xy_positions)
inserts_per_reservoir_cap = len(insert_positions_for_side_plus_1)

# Reservoir cap vent filter: one ø13 PTFE membrane per cap.
vent_filters_per_reservoir_cap = 1


# ─── Derived totals ────────────────────────────────────────────────────

# Reeds.
reservoir_reeds_total = reeds_per_reservoir * reservoirs_per_build
total_reeds_per_build = reeds_per_carbonator + reservoir_reeds_total

# PP1208E per build: umbilical cluster (3) + water inlet (1) = 4. The
# reservoir-cap outlet uses the PureSec B0968K4JRN single-piece 90° PTC
# bulkhead, not PP1208E.
pp1208e_per_build = panel_umbilical_bulkheads + panel_water_inlet_bulkheads

# PP0308E union elbows per build: two on each of the two Kamoer pump outlets,
# and that is all the geometry declares. The valve manifold turns none: the
# two-valve tray carries no fitting on any of its four collets, so how a valve
# leaves its tray is set when the manifold is placed, not by the tray — and an
# elbow nothing has posed is a number with no solid behind it. The CO2 path
# takes none either: its line runs straight in through the foam shell's −Y wall
# to the adapter on the vessel's own bottom-plate elbow, so no bend is made in
# the cavity.
pp0308e_valve_elbows = 0
pp0308e_pump_elbows = 4
pp0308e_per_build = pp0308e_valve_elbows + pp0308e_pump_elbows

# Foam-cap hardware: 6 clamp inserts + 6 M3 × 25 screws per face, both faces,
# PLUS the top cap's deck-mount columns — each takes a ruthex short in its top
# bore and an M3 SHCS down through the module it carries. The clamp screws are
# 1:1 with the clamp inserts only; the deck mounts add inserts on their own.
foam_cap_deck_inserts_per_build = sum(len(deck_mount_xy(n)) for n in deck_mounts)
foam_cap_inserts_per_build = (inserts_per_foam_cap_face * foam_cap_faces
                              + foam_cap_deck_inserts_per_build)
foam_cap_screws_per_build = inserts_per_foam_cap_face * foam_cap_faces  # 1:1 clamp only

# Reservoir-cap hardware (12 inserts + 12 M3 × 12 screws).
reservoir_cap_inserts_per_build = inserts_per_reservoir_cap * reservoirs_per_build
reservoir_cap_screws_per_build = reservoir_cap_inserts_per_build  # 1:1

# Touch-flo plate-to-shell hardware (3 inserts + 3 M3 × 12 screws, one
# per base pod).
touchflo_inserts_per_build = len(base_pod_centers)
touchflo_screws_per_build = touchflo_inserts_per_build  # 1:1

# Electronics-shelf hardware (Zone B, assembly/electronics-shelf.md). Every insert on
# this shelf is in a deck-mount column of the top foam cap, counted with the cap above:
# the board, the PSU, relay #1, the AC hub and the ground stack all land on one. No
# printed part on the shelf carries a boss of its own, and no tray ships.
shelf_inserts_per_build = 0
# One SHCS down through each module into its column. The ground stack's is the long one
# — `deck_mounts` carries the length each station takes.
shelf_screws_per_build = foam_cap_deck_inserts_per_build
shelf_long_screws_per_build = sum(
    len(deck_mount_xy(n)) for n, m in deck_mounts.items() if m.screw > 8.0)
shelf_short_screws_per_build = shelf_screws_per_build - shelf_long_screws_per_build

# Combined heat-set insert count across the appliance (40).
total_m3_inserts_per_build = (
    foam_cap_inserts_per_build
    + reservoir_cap_inserts_per_build
    + touchflo_inserts_per_build
    + shelf_inserts_per_build
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
        "PP1208E_INLET": f"{panel_water_inlet_bulkheads:.4g}",
        "PP1208E_TOTAL": f"{pp1208e_per_build:.4g}",
        "PP0308E_VALVE": f"{pp0308e_valve_elbows:.4g}",
        "PP0308E_PUMP": f"{pp0308e_pump_elbows:.4g}",
        "PP0308E_TOTAL": f"{pp0308e_per_build:.4g}",
        # Heat-set insert + screw hardware.
        "FOAM_INSERTS": f"{foam_cap_inserts_per_build:.4g}",
        "FOAM_SCREWS": f"{foam_cap_screws_per_build:.4g}",
        "RES_INSERTS_PER_CAP": f"{inserts_per_reservoir_cap:.4g}",
        "RES_INSERTS": f"{reservoir_cap_inserts_per_build:.4g}",
        "RES_SCREWS": f"{reservoir_cap_screws_per_build:.4g}",
        "TOUCHFLO_INSERTS": f"{touchflo_inserts_per_build:.4g}",
        "TOUCHFLO_SCREWS": f"{touchflo_screws_per_build:.4g}",
        "SHELF_INSERTS": f"{shelf_inserts_per_build:.4g}",
        "SHELF_SCREWS": f"{shelf_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X8": f"{shelf_short_screws_per_build:.4g}",
        "SHELF_SCREWS_M3X10": f"{shelf_long_screws_per_build:.4g}",
        "DECK_INSERTS": f"{foam_cap_deck_inserts_per_build:.4g}",
        "TOTAL_M3_INSERTS": f"{total_m3_inserts_per_build:.4g}",
        # Vent filters.
        "VENT_FILTERS": f"{vent_filters_per_build:.4g}",
        # Evaporator-coil copper (§5 GOORY row).
        "PITCH": f"{_coil_mandrel_gen.pitch:.4g} mm",
        "WRAP_FT": f"{_coil_mandrel_gen.wrap_length / 304.8:.4g} ft",
        "STUB_LEN": f"{_coil_mandrel_gen.stub_allowance:.4g} mm",
        "CUT_FT": f"{_coil_mandrel_gen.cut_length / 304.8:.4g} ft",
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
            "PP1208E_PANEL": 2,
            "PP1208E_INLET": 1,
            "PP1208E_TOTAL": 1,
            "PP0308E_VALVE": 1,
            "PP0308E_PUMP": 1,
            "PP0308E_TOTAL": 2,
            "FOAM_INSERTS": 2,
            "FOAM_SCREWS": 2,
            "RES_INSERTS_PER_CAP": 1,
            "RES_INSERTS": 1,
            "RES_SCREWS": 1,
            "TOUCHFLO_INSERTS": 2,
            "TOUCHFLO_SCREWS": 2,
            "SHELF_INSERTS": 1,
            "SHELF_SCREWS": 1,
            "SHELF_SCREWS_M3X8": 2,
            "SHELF_SCREWS_M3X10": 1,
            "DECK_INSERTS": 2,
            "TOTAL_M3_INSERTS": 2,
            "VENT_FILTERS": 3,
            "PITCH": 1,
            "WRAP_FT": 1,
            "STUB_LEN": 1,
            "CUT_FT": 1,
        },
    )
    print("-> bom.md")


if __name__ == "__main__":
    main()
