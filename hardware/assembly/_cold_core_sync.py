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

# Each generator/module is in its own directory; add each to sys.path
# so the bare-module imports below resolve.
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
    outer_shell_z_length,
    port_hole_radius,
    screw_boss_size,
)

# Load the foam-cap and coil-mandrel generators by explicit file path.
# Each generator's own sys.path manipulation only runs after it loads,
# so loading via importlib.util keeps the import side-effects local
# to each module without inserting either part's directory globally.
import importlib.util  # noqa: E402


def _load_module(name: str, file_path: Path):
    """Load a Python file as a uniquely-named module."""
    spec = importlib.util.spec_from_file_location(name, file_path)
    module = importlib.util.module_from_spec(spec)
    # Add the file's directory to sys.path so the module's own
    # sys.path.insert lines find their siblings.
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
        # Coil-mandrel-owned: groove depth, mandrel OD, tank OD, as-wound
        # undersize, wind length, total wraps, pitch, plug Y span.
        "GROOVE_DEPTH": f"{_coil_mandrel_gen.groove_depth:.4g} mm",
        "MANDREL_OD": f"{_coil_mandrel_gen.mandrel_od:.4g} mm",
        "TANK_OD": f"{_coil_mandrel_gen.tank_od:.4g} mm",
        "NET_UNDERSIZE": f"{_coil_mandrel_gen.net_undersize:.4g} mm",
        "WIND_LENGTH": f"{_coil_mandrel_gen.wind_length:.4g} mm",
        # total_wraps is a derived float; pin to .3f to match the doc's
        # "9.687 wraps" convention (kept explicit even though :.4g now
        # happens to give the same result for this value).
        "TOTAL_WRAPS": f"{_coil_mandrel_gen.total_wraps:.3f}",
        # pitch is also derived; .2f matches "12.43 mm" in the prose.
        "PITCH": f"{_coil_mandrel_gen.pitch:.2f} mm",
        "PLUG_INLET_Y": f"{_coil_mandrel_gen.plug_inlet_y:.4g}",
        "PLUG_OUTLET_Y": f"{_coil_mandrel_gen.plug_outlet_y:.4g}",
        # ─── Cap pour (step 2, line 53) ───────────────────────────────
        # foam_cap_interior_height is the 16 mm-tall cup interior; the
        # foam-cap-lid pour and vent holes get rendered as diameters.
        "CAP_H": f"{foam_cap_interior_height:.4g} mm",
        "POUR_D": f"{foam_cap_lid_pour_radius * 2:.4g} mm",
        "VENT_D": f"{foam_cap_lid_vent_radius * 2:.4g} mm",
        # ─── Inserts (step 3, line 59) ────────────────────────────────
        # insert_pocket_depth is the FULL printed-pocket depth = insert
        # engagement (half) + relief (half). The prose calls them out as
        # two distinct halves; both substitute against half-depth.
        "INSERT_POCKET_D": f"{insert_pocket_radius * 2:.4g} mm",
        "INSERT_HALF_DEPTH": f"{insert_pocket_depth / 2:.4g} mm",
        # ─── Penetrations (step 4, lines 70-72) ───────────────────────
        # Generic small-feature port hole (water outlet, reservoir
        # bulkheads, CO2 tube clearance through cap+lid).
        "PORT_D": f"{port_hole_radius * 2:.4g}",
        # CO2 inlet Z coordinate in the foam-shell frame; the foam-cap
        # generator owns it (the cap floor hole + boss are placed at
        # this z).
        "COTWO_INLET_Z": f"{_foam_cap_gen.co2_inlet_z:.4g}",
        # ─── Final assembly (step 6, line 90) ─────────────────────────
        # Screw-boss square footprint that the TPU gasket's pads sit on.
        "BOSS": f"{screw_boss_size:.4g} × {screw_boss_size:.4g} mm",
        # ─── Output envelope (line 113) ───────────────────────────────
        # The "External envelope ~283 × 181 × 213.4 mm" comes straight
        # from the foam-shell outer footprint + height.
        "OUTER_X": f"{outer_shell_x_length:.4g}",
        "OUTER_Z": f"{outer_shell_z_length:.4g}",
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
            "PORT_D": 3,
            "COTWO_INLET_Z": 1,
            "BOSS": 1,
            "OUTER_X": 1,
            "OUTER_Z": 1,
            "OUTER_H": 1,
        },
    )
    print("-> cold-core.md")


if __name__ == "__main__":
    main()
