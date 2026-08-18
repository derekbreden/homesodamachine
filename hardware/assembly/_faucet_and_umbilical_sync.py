"""Doc-sync driver for hardware/assembly/faucet-and-umbilical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_faucet_and_umbilical_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from docgen import load_module, substitute_md  # noqa: E402


def main():
    hardware_root = next(p for p in _here.parents if p.name == "hardware")

    tpu = load_module(
        "_tpu_oring_gen",
        hardware_root
        / "printed-parts"
        / "faucet"
        / "touch-flo-tpu-o-ring"
        / "touch_flo_tpu_o_ring.py",
    )
    plate = load_module(
        "_under_counter_plate_gen",
        hardware_root
        / "cut-parts"
        / "faucet"
        / "touch-flo-under-counter-plate"
        / "touch_flo_under_counter_plate.py",
    )
    faucet = load_module(
        "_faucet_assembly_gen",
        hardware_root / "faucet-layout" / "faucet_assembly.py",
    )

    variables = {
        # TPU thimble (touch-flo-tpu-o-ring) — BOM row line 26.
        # Source: `touch-flo-tpu-o-ring/touch_flo_tpu_o_ring.py`.
        "CAP_HOLE_D": f"{tpu.cap_hole_diameter:.4g} mm",
        "BODY_PORT_D": f"{tpu.body_port_diameter:.4g} mm",
        "ORING_OUTER_D": f"{tpu.outer_diameter:.4g} mm",
        "BODY_SQUEEZE": f"{tpu.body_squeeze:.4g} mm",
        "ORING_INNER_D": f"{tpu.inner_diameter:.4g} mm",
        "LLDPE_INTERFERENCE": f"{tpu.lldpe_interference:.4g} mm",
        "TOTAL_H": f"{tpu.total_height:.4g} mm",
        "ORING_CAP_T": f"{tpu.cap_thickness:.4g} mm",
        "CYL_L": f"{tpu.cylinder_length:.4g} mm",
        "LLDPE_ID": f"{tpu.lldpe_id:.4g} mm",
        "LLDPE_OD": f"{tpu.lldpe_od:.4g} mm",
        # Under-counter keyhole plate (touch-flo-under-counter-plate) —
        # BOM row line 27.
        # Source: `touch-flo-under-counter-plate/touch_flo_under_counter_plate.py`.
        "PLATE_D": f"{plate.disc_diameter:.4g} mm",
        "SHANK_HOLE_D": f"{plate.shank_diameter:.4g} mm",
        "PILL_L": f"{plate.pill_long_y:.4g} mm",
        "PILL_W": f"{plate.pill_short_x:.4g} mm",
        "FILLET_R": f"{plate.fillet_radius:.4g} mm",
        # The countertop hole the faucet seats itself in — §1 and open item 4.
        # Source: `faucet-layout/faucet_assembly.py`.
        "COUNTERTOP_HOLE_D": f"{faucet.countertop_hole_diameter:.4g} mm",
        "GASKET_COVER": f"{faucet.gasket_hole_cover():.4g} mm",
        # The collar the bench threads onto each tail, and where the sleeve above it stops — §4.
        # Source: `printed-parts/faucet/tube-collar/tube_collar.py` through the assembly that
        # seats three of them, so the bench and the picture read one figure.
        "COLLAR_LENGTH": f"{faucet.tube_collar.LENGTH:.4g} mm",
        # The bench holds a finished collar, so the figure §4 reads is the one off the plate and
        # not the one the slicer was handed — `tube_collar.BORE_SHRINK` is the difference.
        "COLLAR_BORE_PRINTED": f"{faucet.tube_collar.bore_printed():.4g}",
        "COLLAR_TUBE_OD": f"{faucet.tube_collar.TUBE_OD:.4g}",
        "COLLAR_SLEEVE_TAIL": f"{faucet.foam_bare_at_wall:.3g} mm",
        # The braid over the pack — §3 and open item 2. It is bought by what it opens to.
        "SLEEVE_GIRTH": f"{faucet.bundle_girth():.4g} mm",
        "SLEEVE_BORE": f"{faucet.bundle_bore():.4g} mm",
        "SLEEVE_BORE_IN": f'{faucet.bundle_bore() / 25.4:.3g}"',
    }

    substitute_md(
        _here / "faucet-and-umbilical.md",
        variables=variables,
    )
    print("-> faucet-and-umbilical.md")


if __name__ == "__main__":
    main()
