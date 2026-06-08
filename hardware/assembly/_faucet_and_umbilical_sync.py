"""Doc-sync driver for hardware/assembly/faucet-and-umbilical.md.

Run: tools/cad-venv/bin/python hardware/assembly/_faucet_and_umbilical_sync.py
"""

import importlib.util
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from docgen import substitute_md  # noqa: E402


def _load_module(name: str, path: Path):
    """Load a module from an explicit file path."""
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load {name} from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    hardware_root = next(p for p in _here.parents if p.name == "hardware")

    tpu = _load_module(
        "_tpu_oring_gen",
        hardware_root
        / "printed-parts"
        / "faucet"
        / "touch-flo-tpu-o-ring"
        / "touch_flo_tpu_o_ring.py",
    )
    plate = _load_module(
        "_under_counter_plate_gen",
        hardware_root
        / "cut-parts"
        / "faucet"
        / "touch-flo-under-counter-plate"
        / "touch_flo_under_counter_plate.py",
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
    }

    substitute_md(
        _here / "faucet-and-umbilical.md",
        variables=variables,
        expected_counts={
            "CAP_HOLE_D": 1,
            "BODY_PORT_D": 1,
            "ORING_OUTER_D": 1,
            "BODY_SQUEEZE": 1,
            "ORING_INNER_D": 1,
            "LLDPE_INTERFERENCE": 1,
            "TOTAL_H": 1,
            "ORING_CAP_T": 1,
            "CYL_L": 1,
            "LLDPE_ID": 1,
            "LLDPE_OD": 1,
            "PLATE_D": 1,
            "SHANK_HOLE_D": 2,
            "PILL_L": 1,
            "PILL_W": 2,
            "FILLET_R": 1,
        },
    )
    print("-> faucet-and-umbilical.md")


if __name__ == "__main__":
    main()
