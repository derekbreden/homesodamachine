"""Doc-sync driver for hardware/assembly/cold-core.md.

Run: tools/cad-venv/bin/python hardware/assembly/_cold_core_sync.py
"""

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
    co2_inlet_y,
    foam_cap_interior_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_shell_outer_height,
    insert_pocket_depth,
    insert_pocket_radius,
    outer_shell_x_length,
    outer_shell_y_length,
    port_hole_radius,
    wall_and_floor_thickness,
)

import importlib.util  # noqa: E402


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
        # Copper consumption: wrap arc, and per-vessel cut with stubs.
        "WRAP_LEN": f"{_coil_mandrel_gen.wrap_length / 1000:.4g} m",
        "WRAP_FT": f"{_coil_mandrel_gen.wrap_length / 304.8:.4g} ft",
        "CUT_FT": f"{_coil_mandrel_gen.cut_length / 304.8:.4g} ft",
        "PLUG_INLET_Y": f"{_coil_mandrel_gen.plug_inlet_y:.4g}",
        "PLUG_OUTLET_Y": f"{_coil_mandrel_gen.plug_outlet_y:.4g}",
        # ─── Cap pour (step 2) ────────────────────────────────────────
        "CAP_H": f"{foam_cap_interior_height:.4g} mm",
        "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
        "VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
        # ─── Inserts (step 3) ─────────────────────────────────────────
        # insert_pocket_depth is the FULL printed-pocket depth = insert
        # engagement (half) + relief (half).
        "INSERT_POCKET_D": f"{insert_pocket_radius * 2:.4g} mm",
        "INSERT_HALF_DEPTH": f"{insert_pocket_depth / 2:.4g} mm",
        # ─── Penetrations (step 4, lines 70-72) ───────────────────────
        # Generic small-feature port hole (water outlet, reservoir
        # bulkheads, CO2 tube clearance through cap+lid).
        "TUBE_HOLE_D": f"{port_hole_radius * 2:.4g} mm",
        # CO2 inlet Z coordinate in the foam-shell frame.
        "COTWO_INLET_Z": f"{co2_inlet_y:.4g}",
        # ─── Output envelope (line 113) ───────────────────────────────
        "OUTER_X": f"{outer_shell_x_length:.4g} mm",
        "CCORE_OUTER_Y": f"{outer_shell_y_length:.4g}",
        "OUTER_H": f"{foam_shell_outer_height:.4g} mm",
    }

    substitute_md(
        _here / "cold-core.md",
        variables=variables,
        expected_counts={
            "GROOVE_DEPTH": 1,
            "MANDREL_OD": 1,
            "TANK_OD": 1,
            "NET_UNDERSIZE": 1,
            "WIND_LENGTH": 1,
            "TOTAL_WRAPS": 1,
            "PITCH": 1,
            "WRAP_LEN": 1,
            "WRAP_FT": 1,
            "CUT_FT": 1,
            "PLUG_INLET_Y": 1,
            "PLUG_OUTLET_Y": 1,
            "CAP_H": 1,
            "POUR_D": 1,
            "VENT_D": 1,
            "INSERT_POCKET_D": 1,
            "INSERT_HALF_DEPTH": 2,
            "TUBE_HOLE_D": 3,
            "COTWO_INLET_Z": 1,
            "OUTER_X": 1,
            "CCORE_OUTER_Y": 1,
            "OUTER_H": 1,
        },
    )
    print("-> cold-core.md")

    # Pin the CO2-inlet bore dimensions in _port_cuts.py's docstring.
    # The doorway sits on the +Y (rear) centerward wall.
    co2_doorway_y = _port_cuts.co2_doorway_y
    substitute_py_comments(
        Path(_port_cuts.__file__),
        variables={
            "CO2_INLET_BORE_D": f"⌀{2 * _port_cuts.co2_inlet_bore_radius:.4g}",
            "CO2_INLET_BORE_Z": f"{_port_cuts.co2_inlet_bore_z:.4g}",
            "CO2_DOORWAY_Y": f"{co2_doorway_y:.4g}",
            "FLOOR_TOP_Z": f"{_port_cuts.wall_and_floor_thickness:.4g}",
            "PORT_HOLE_DIAMETER": f"{_port_cuts.port_hole_radius * 2:.4g}",
        },
        expected_counts={
            "CO2_INLET_BORE_D": 1,
            "CO2_INLET_BORE_Z": 1,
            "CO2_DOORWAY_Y": 1,
            "FLOOR_TOP_Z": 2,
            "PORT_HOLE_DIAMETER": 2,
        },
    )
    print("-> _port_cuts.py")


if __name__ == "__main__":
    main()
