"""Doc-sync driver for hardware/assembly/cold-core.md.

Run: tools/cad-venv/bin/python hardware/assembly/_cold_core_sync.py
"""

import math
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))

from _cold_core_interface import (  # noqa: E402
    attachment_xy_positions,
    cap_cradles,
    cap_cradle_corner_radius,
    cap_cradle_xy,
    deck_mounts,
    deck_mount_xy,
    co2_inlet_y,
    foam_cap_interior_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_pour_xy,
    foam_cap_lid_vent_radius,
    foam_shell_outer_height,
    foam_cap_height,
    forward_band_width,
    gasket_thickness,
    insert_pocket_depth,
    insert_pocket_radius,
    lldpe_bend_radius,
    outer_shell_x_length,
    outer_shell_y_length,
    port_hole_radius,
    reservoir_bulkhead_port_x,
    reservoir_clearance,
    top_band_to_cap,
    wall_and_floor_thickness,
)
from _reed_channels import (  # noqa: E402
    cable_hole_offset_from_bulkhead_hole_x,
)

sys.path.insert(0, str(_hw / "printed-parts" / "cold-core" / "reservoir"))
from reservoir import insert_positions_for_side_plus_1  # noqa: E402

import importlib.util  # noqa: E402

# Every ruthex short this procedure presses, off the patterns that hold them.
# The shell clamps a cap on each face; the top cap's deck-mount columns take one
# each; each reservoir cap takes its own wall-top ring. Nothing else on this bench
# is threaded — the power column's inserts are the enclosure's `east_bosses`, and
# `enclosure-mechanical.md` §1 presses those.
CAP_CLAMP_INSERTS = len(attachment_xy_positions) * 2
CAP_DECK_INSERTS = sum(len(deck_mount_xy(n)) for n in deck_mounts)
RESERVOIR_INSERTS = len(insert_positions_for_side_plus_1) * 2

# What the bench's trim knife has to work in. The pour hole and the valve cradles open in
# the ONE face — the top lid's outer one — so the least a pad's corner arc stands off the
# hole is the land the cured foam is cut back to. Read on the corner arcs, which are the
# pad's nearest material to the hole, exactly as `_cold_core_interface.cap_cradle_room` does.
_POUR_XY = foam_cap_lid_pour_xy()
POUR_CRADLE_GAP = min(
    math.hypot(_POUR_XY[0] - x, _POUR_XY[1] - y)
    - foam_cap_lid_pour_radius - cap_cradle_corner_radius
    for name in cap_cradles for x, y in cap_cradle_xy(name)
)


def _load_module(name: str, file_path: Path):
    """Load a Python file as a uniquely-named module."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(file_path.parent))
    spec.loader.exec_module(module)
    return module


_coil_mandrel_gen = _load_module(
    "cold_core_coil_mandrel_gen",
    _hw / "printed-parts" / "cold-core" / "coil-mandrel" / "coil_mandrel.py",
)

# The wrap AS LAID on the tank, and the cut struck on it — `coil_mandrel` holds the two
# shorter readings (what the tool holds, what the same wraps come to once sprung off it)
# but only this module sees the lift over the reed bridge, so the cut lives here.
_coil_gen = _load_module("cold_core_coil_gen", _hw / "cold-core-layout" / "_coil.py")

# Carbonator reed switching levels — the bridge's own geometry sets where CLO
# and CHI sit above the tube's bottom rim.
_reed_bridge_gen = _load_module(
    "cold_core_reed_bridge_gen",
    _hw / "printed-parts" / "cold-core" / "reed-bridge" / "reed_bridge.py",
)

import _port_cuts  # noqa: E402
from docgen import substitute_md, substitute_py_comments  # noqa: E402


def main():
    variables = {
        # ─── Coil winding (step 1, line 47) ───────────────────────────
        "GROOVE_DEPTH": f"{_coil_mandrel_gen.groove_depth:.4g} mm",
        "MANDREL_OD": f"{_coil_mandrel_gen.mandrel_od:.4g} mm",
        "TANK_OD": f"{_coil_mandrel_gen.tank_od:.4g} mm",
        "NET_UNDERSIZE": f"{_coil_mandrel_gen.net_undersize:.4g} mm",
        "WIND_LENGTH": f"{_coil_mandrel_gen.wind_length:.4g} mm",
        # total_wraps is a derived float; .3f matches "9.687 wraps".
        "TOTAL_WRAPS": f"{_coil_mandrel_gen.total_wraps:.3f}",
        # pitch is derived; .2f matches "12.43 mm".
        "PITCH": f"{_coil_mandrel_gen.pitch:.2f} mm",
        # Copper consumption. SPRUNG_LEN is the wrap once it has sprung off the mandrel
        # onto the tank; LAID_FT is that same wrap with the reed bridge's lift in it —
        # what a build consumes, and what the cut stands on.
        "SPRUNG_LEN": f"{_coil_mandrel_gen.fitted_wrap_length / 1000:.4g} m",
        "LAID_FT": f"{_coil_gen.wrap_length() / 304.8:.4g} ft",
        "STUB_INLET": f"{_coil_mandrel_gen.stub_allowance['inlet']:.4g} mm",
        "STUB_OUTLET": f"{_coil_mandrel_gen.stub_allowance['outlet']:.4g} mm",
        "PROT_INLET": f"{_coil_mandrel_gen.stub_protrusion['inlet']:.4g} mm",
        "PROT_OUTLET": f"{_coil_mandrel_gen.stub_protrusion['outlet']:.4g} mm",
        "ROLL_SHARE": f"1/{_coil_mandrel_gen.vessels_per_roll}",
        "CUT_FT": f"{_coil_gen.cut_length() / 304.8:.4g} ft",
        "TAIL_INLET_Y": f"{_coil_mandrel_gen.tail_inlet_y:.4g}",
        "TAIL_OUTLET_Y": f"{_coil_mandrel_gen.tail_outlet_y:.4g}",
        # ─── Cap pour (step 3) ────────────────────────────────────────
        "CAP_H": f"{foam_cap_interior_height:.4g} mm",
        "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
        "LID_VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
        # The valve cradles on the top lid's outer face, and the land the pour hole
        # leaves beside the nearest of them.
        "CAP_CRADLES": f"{len(cap_cradles)}",
        "POUR_CRADLE_GAP": f"{POUR_CRADLE_GAP:.4g} mm",
        # ─── Inserts (step 2) ─────────────────────────────────────────
        # insert_pocket_depth is the FULL printed-pocket depth = insert
        # engagement (half) + relief (half).
        "INSERT_POCKET_D": f"{insert_pocket_radius * 2:.4g} mm",
        "INSERT_HALF_DEPTH": f"{insert_pocket_depth / 2:.4g} mm",
        "CC_INSERTS": f"{CAP_CLAMP_INSERTS + CAP_DECK_INSERTS + RESERVOIR_INSERTS}",
        "CAP_INSERTS": f"{CAP_CLAMP_INSERTS + CAP_DECK_INSERTS}",
        "CAP_CLAMP_INSERTS": f"{CAP_CLAMP_INSERTS}",
        "CAP_DECK_INSERTS": f"{CAP_DECK_INSERTS}",
        "RES_INSERTS": f"{RESERVOIR_INSERTS}",
        # ─── Penetrations (step 4, lines 70-72) ───────────────────────
        # Generic small-feature port hole (water outlet, reservoir
        # bulkheads, CO2 tube clearance through cap+lid).
        "TUBE_HOLE_D": f"{port_hole_radius * 2:.4g} mm",
        # CO2 inlet Y — the vessel's own port axis. The bore, the vessel
        # elbow and the tube all stand on it.
        "COTWO_INLET_Y": f"{co2_inlet_y:.4g}",
        # The band the water inlet's line turns and runs in — the top plate's
        # own lateral axis up to the cap's floor — against the arc the stock
        # wants, which is what makes the corner off that elbow the tight one.
        "TOP_BAND": f"{top_band_to_cap:.4g}",
        "LLDPE_BEND_R": f"{lldpe_bend_radius:.4g} mm",
        # The strip between a bag pocket's own wall and the shell's — the band
        # both reservoir draws climb to reach their cap conduits.
        "FORWARD_BAND": f"{forward_band_width:.4g} mm",
        # The two pocket-wall holes per reservoir side: flavor line inboard,
        # reed cable outboard of the bulkhead axis. There is no matching pair of
        # outer-wall holes — each run turns onto the port lane and leaves through
        # its own station on the front port field, which is why the second bore
        # is a Z on the column rather than an X on the line's own axis.
        "FLAVOR_HOLE_X": f"±{_port_cuts.flavor_line_hole_x:.4g}",
        "CABLE_HOLE_X": f"±{reservoir_bulkhead_port_x + cable_hole_offset_from_bulkhead_hole_x:.4g}",
        # Reservoir-to-pocket clearance — why the pockets take no foam.
        "RESERVOIR_GAP": f"{reservoir_clearance:.4g} mm",
        # ─── Output envelope (line 113) ───────────────────────────────
        "OUTER_X": f"{outer_shell_x_length:.4g} mm",
        "CCORE_OUTER_Y": f"{outer_shell_y_length:.4g}",
        "OUTER_H": f"{foam_shell_outer_height:.4g} mm",
        # Finished stack: the shell plus a cap + gasket on each face. The lid
        # nests in the cap mouth, so it adds no height.
        "CCORE_CAPPED_H": f"{foam_shell_outer_height + 2 * (foam_cap_height + gasket_thickness):.4g} mm",
        # ─── Carbonator reed levels and the bridge that sets them ─────
        # The two switching heights, and the two figures the paragraph explaining
        # them stands on: the bare channel a wrap leaves between turns, which is
        # why the reed cannot fit between wraps at all, and where the bridge's own
        # bottom edge lands off the tube's rim, which is what the setting gauge
        # marks. All four off the bridge's own module, so the witness list, the
        # explanation and the closed open item read one part.
        "LOW_LEVEL": f"{_reed_bridge_gen.low_level_z:.4g} mm",
        "HIGH_LEVEL": f"{_reed_bridge_gen.high_level_z:.4g} mm",
        "INTER_WRAP_CLEAR": f"{_reed_bridge_gen.inter_wrap_clear:.4g} mm",
        "BRIDGE_Z_BOTTOM": f"{_reed_bridge_gen.bridge_z_bottom:.4g} mm",
    }

    substitute_md(
        _here / "cold-core.md",
        variables=variables,
        expected_counts={
            "LOW_LEVEL": 3,
            "HIGH_LEVEL": 3,
            "INTER_WRAP_CLEAR": 1,
            "BRIDGE_Z_BOTTOM": 1,
            "GROOVE_DEPTH": 1,
            "MANDREL_OD": 1,
            "TANK_OD": 1,
            "NET_UNDERSIZE": 1,
            "WIND_LENGTH": 1,
            "TOTAL_WRAPS": 1,
            "PITCH": 2,
            "SPRUNG_LEN": 1,
            "LAID_FT": 1,
            "STUB_INLET": 1,
            "STUB_OUTLET": 1,
            "PROT_INLET": 2,
            "PROT_OUTLET": 2,
            "ROLL_SHARE": 1,
            "CUT_FT": 1,
            "TAIL_INLET_Y": 1,
            "TAIL_OUTLET_Y": 1,
            "CAP_H": 1,
            "POUR_D": 1,
            "LID_VENT_D": 1,
            "CAP_CRADLES": 1,
            "POUR_CRADLE_GAP": 1,
            "INSERT_POCKET_D": 1,
            "INSERT_HALF_DEPTH": 2,
            "CC_INSERTS": 1,
            "CAP_INSERTS": 1,
            "CAP_CLAMP_INSERTS": 1,
            "CAP_DECK_INSERTS": 1,
            "RES_INSERTS": 1,
            "TUBE_HOLE_D": 5,
            "COTWO_INLET_Y": 1,
            "TOP_BAND": 1,
            "LLDPE_BEND_R": 1,
            "FORWARD_BAND": 1,
            "FLAVOR_HOLE_X": 1,
            "CABLE_HOLE_X": 2,
            "RESERVOIR_GAP": 1,
            "OUTER_X": 1,
            "CCORE_OUTER_Y": 1,
            "OUTER_H": 1,
            "CCORE_CAPPED_H": 1,
        },
    )
    print("-> cold-core.md")

    # Pin the CO2-inlet bore's station in _port_cuts.py's docstring — the
    # bottom plate's own port offset in X, and the Z the −Y wall's two
    # bottom-plate lines share.
    substitute_py_comments(
        Path(_port_cuts.__file__),
        variables={
            "CO2_INLET_Y": f"{_port_cuts.co2_inlet_y:.4g}",
            "FRONT_FACE_PORT_Z": f"{_port_cuts.front_face_port_z:.4g}",
            # Off `_cold_core_interface`, the constant's own home — `_port_cuts`
            # imports what it needs and re-exports nothing on purpose.
            "PORT_HOLE_DIAMETER": f"{port_hole_radius * 2:.4g}",
            # Pocket-wall spacing between a side's flavor bore and its reed
            # cable bore — the two offsets from the bulkhead axis, one
            # inboard and one outboard.
            "FLAVOR_REED_PITCH": f"{_port_cuts.flavor_line_hole_offset_from_bulkhead_x + cable_hole_offset_from_bulkhead_hole_x:.4g}",
        },
        expected_counts={
            "CO2_INLET_Y": 1,
            "FRONT_FACE_PORT_Z": 1,
            "PORT_HOLE_DIAMETER": 3,
            "FLAVOR_REED_PITCH": 1,
        },
    )
    print("-> _port_cuts.py")


if __name__ == "__main__":
    main()
