"""Doc-sync driver for hardware/assembly/cold-core.md.

The cold-core production procedure cites dimensional content with three
distinct provenances; the sync driver handles each per the project's
three-strategy menu:

**Strategy A — multi-import from upstream generators.** Most numbers in
the procedure prose are owned by the cold-core CAD: foam-shell outer
envelope (foam_shell_outer_height, outer_shell_x_length,
outer_shell_z_length) and joinery (screw_boss_size) live in
`_cold_core_interface.py`; the foam-cap stack (foam_cap_interior_height,
foam_cap_lid_pour_radius, foam_cap_lid_vent_radius, insert_pocket_radius,
insert_pocket_depth, port_hole_radius) also flows through the interface;
the in-cavity CO2 inlet Z (co2_inlet_z) lives in the foam-cap generator;
and the coil-winding-mandrel-driven numbers (tube wind length, total
wraps, pitch, mandrel OD, tank OD, undersize, groove depth, plug Y span)
live in the coil-mandrel generator. All imported READ-ONLY.

**Strategy C — leave raw.** External standards baked into SKU names
(GOORY 1/4" OD × 0.031" wall ACR copper, 3M 425, M3 × 25 SHCS,
1/4" PTC, 1/4" NPT, 5/16" tube, FDA 21 CFR 177.1630, etc.), catalog
specs (~22 ft wrap per vessel, ~2 ft tie-in stubs, BOM quantities,
Amazon SKUs), and procedure-loose values (1/8" pitch target, 1–3 mm
springback band, six-screw counts, status tags) are intentionally not
substituted — they ARE the parts or are independent procedure
parameters.

**Strategy B — cross-reference.** Not used here. The cited numbers
flow from upstream constants, not from prose in other READMEs.

Run as a script:

    tools/cad-venv/bin/python hardware/assembly/_cold_core_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

# Each generator/module is on its own directory; add each to sys.path so
# the bare-module imports below resolve. The coil-mandrel and foam-cap
# generators are both named `generate_step_cadquery.py`, so we import
# them under distinct aliases by adding each directory + reading the
# module under its file-system parent path.
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

# Import the foam-cap and coil-mandrel generators under unique module
# names by manipulating sys.path one at a time around each import — the
# two generators share the filename `generate_step_cadquery.py`, so a
# single sys.path entry would shadow whichever was inserted second.
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
    _hw / "printed-parts" / "cold-core" / "foam-cap" / "generate_step_cadquery.py",
)
_coil_mandrel_gen = _load_module(
    "cold_core_coil_mandrel_gen",
    _hw / "printed-parts" / "cold-core" / "coil-mandrel" / "generate_step_cadquery.py",
)

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # ─── Coil winding (step 1, line 47) ───────────────────────────
        # Coil-mandrel-owned: groove depth, mandrel OD, tank OD, as-wound
        # undersize, wind length, total wraps, pitch, plug Y span.
        "GROOVE_DEPTH": f"{_coil_mandrel_gen.groove_depth:g} mm",
        "MANDREL_OD": f"{_coil_mandrel_gen.mandrel_od:g} mm",
        "TANK_OD": f"{_coil_mandrel_gen.tank_od:g} mm",
        "NET_UNDERSIZE": f"{_coil_mandrel_gen.net_undersize:g} mm",
        "WIND_LENGTH": f"{_coil_mandrel_gen.wind_length:g} mm",
        # total_wraps is a derived float; pin to .3f to match the doc's
        # "9.687 wraps" convention (the :g default would print 9.68717).
        "TOTAL_WRAPS": f"{_coil_mandrel_gen.total_wraps:.3f}",
        # pitch is also derived; .2f matches "12.43 mm" in the prose.
        "PITCH": f"{_coil_mandrel_gen.pitch:.2f} mm",
        "PLUG_INLET_Y": f"{_coil_mandrel_gen.plug_inlet_y:g}",
        "PLUG_OUTLET_Y": f"{_coil_mandrel_gen.plug_outlet_y:g}",
        # ─── Cap pour (step 2, line 53) ───────────────────────────────
        # foam_cap_interior_height is the 16 mm-tall cup interior; the
        # foam-cap-lid pour and vent holes get rendered as diameters.
        "CAP_H": f"{foam_cap_interior_height:g} mm",
        "POUR_D": f"{foam_cap_lid_pour_radius * 2:g} mm",
        "VENT_D": f"{foam_cap_lid_vent_radius * 2:g} mm",
        # ─── Inserts (step 3, line 59) ────────────────────────────────
        # insert_pocket_depth is the FULL printed-pocket depth = insert
        # engagement (half) + relief (half). The prose calls them out as
        # two distinct halves; both substitute against half-depth.
        "INSERT_POCKET_D": f"{insert_pocket_radius * 2:g} mm",
        "INSERT_HALF_DEPTH": f"{insert_pocket_depth / 2:g} mm",
        # ─── Penetrations (step 4, lines 70-72) ───────────────────────
        # Generic small-feature port hole (water outlet, reservoir
        # bulkheads, CO2 tube clearance through cap+lid).
        "PORT_D": f"{port_hole_radius * 2:g}",
        # CO2 inlet Z coordinate in the foam-shell frame; the foam-cap
        # generator owns it (the cap floor hole + boss are placed at
        # this z).
        "COTWO_INLET_Z": f"{_foam_cap_gen.co2_inlet_z:g}",
        # ─── Final assembly (step 6, line 90) ─────────────────────────
        # Screw-boss square footprint that the TPU gasket's pads sit on.
        "BOSS": f"{screw_boss_size:g} × {screw_boss_size:g} mm",
        # ─── Output envelope (line 113) ───────────────────────────────
        # The "External envelope ~283 × 181 × 213.4 mm" comes straight
        # from the foam-shell outer footprint + height.
        "OUTER_X": f"{outer_shell_x_length:g}",
        "OUTER_Z": f"{outer_shell_z_length:g}",
        "OUTER_H": f"{foam_shell_outer_height:g} mm",
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
