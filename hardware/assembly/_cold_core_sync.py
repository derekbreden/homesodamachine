"""Doc-sync driver for hardware/assembly/cold-core.md.

Run: tools/cad-venv/bin/python hardware/assembly/_cold_core_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))

from _cold_core_interface import (  # noqa: E402
    foam_cap_interior_height,
    foam_cap_lid_pour_radius,
    foam_cap_lid_vent_radius,
    foam_shell_outer_height,
    insert_pocket_depth,
    insert_pocket_radius,
    outer_shell_x_length,
    outer_shell_y_length,
    port_hole_radius,
    screw_boss_size,
)

import importlib.util  # noqa: E402


def _load_module(name: str, file_path: Path):
    """Load a Python file as a uniquely-named module."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(file_path.parent))
    spec.loader.exec_module(module)
    return module


_foam_cap_gen = _load_module(
    "cold_core_foam_cap_gen",
    _hw / "printed-parts" / "cold-core" / "foam-cap" / "foam_cap.py",
)
_coil_mandrel_gen = _load_module(
    "cold_core_coil_mandrel_gen",
    _hw / "printed-parts" / "cold-core" / "coil-mandrel" / "coil_mandrel.py",
)

from docgen import substitute_md  # noqa: E402


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
        "PLUG_INLET_Y": f"{_coil_mandrel_gen.plug_inlet_y:.4g}",
        "PLUG_OUTLET_Y": f"{_coil_mandrel_gen.plug_outlet_y:.4g}",
        # ─── Cap pour (step 2, line 53) ───────────────────────────────
        "CAP_H": f"{foam_cap_interior_height:.4g} mm",
        "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
        "VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
        # ─── Inserts (step 3, line 59) ────────────────────────────────
        # insert_pocket_depth is the FULL printed-pocket depth = insert
        # engagement (half) + relief (half).
        "INSERT_POCKET_D": f"{insert_pocket_radius * 2:.4g} mm",
        "INSERT_HALF_DEPTH": f"{insert_pocket_depth / 2:.4g} mm",
        # ─── Penetrations (step 4, lines 70-72) ───────────────────────
        # Generic small-feature port hole (water outlet, reservoir
        # bulkheads, CO2 tube clearance through cap+lid).
        "TUBE_HOLE_D": f"{port_hole_radius * 2:.4g} mm",
        # CO2 inlet Z coordinate in the foam-shell frame.
        "COTWO_INLET_Z": f"{_foam_cap_gen.co2_inlet_y:.4g}",
        # ─── Final assembly (step 6, line 90) ─────────────────────────
        # Screw-boss square footprint that the TPU gasket's pads sit on.
        "BOSS": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
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
            "PLUG_INLET_Y": 1,
            "PLUG_OUTLET_Y": 1,
            "CAP_H": 1,
            "POUR_D": 1,
            "VENT_D": 1,
            "INSERT_POCKET_D": 1,
            "INSERT_HALF_DEPTH": 2,
            "TUBE_HOLE_D": 3,
            "COTWO_INLET_Z": 1,
            "BOSS": 1,
            "OUTER_X": 1,
            "CCORE_OUTER_Y": 1,
            "OUTER_H": 1,
        },
    )
    print("-> cold-core.md")


if __name__ == "__main__":
    main()
