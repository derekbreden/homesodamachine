"""Faucet-and-umbilical.md value sync — pulls CAD-driven dimensions
cited in the procedure prose from the upstream faucet-side part
generators and substitutes them into faucet-and-umbilical.md.

Sources of truth (each READ-ONLY from this side; substituted values
are pulled, never written back):

- `touch-flo-tpu-o-ring/touch_flo_tpu_o_ring.py` — TPU thimble
  geometry called out in the BOM "Touch-Flo TPU O-ring" row.
- `touch-flo-under-counter-plate/touch_flo_under_counter_plate.py` — keyhole plate disc /
  pocket / channel / fillet dimensions called out in the BOM
  "under-counter keyhole plate" row. Same hole positions match the
  TPU mounting gasket and the printed mounting plate exactly (the
  generators share NAMES so the same key refers to the same dimension
  across the stack-up).

Everything else in faucet-and-umbilical.md is intentionally raw:

- External standards baked into SKU identity — 1/4" OD LLDPE, 3/8" OD
  LLDPE, 1-3/8" countertop hole, 0.060" SS sheet gauge, 1-ft CARGEN
  foam segment length, 1/4" ID × 3/8" wall foam. Each IS the catalog
  identity of the part; there's nothing upstream to derive them from.
- Catalog / operating specs not owned by any CAD source — ~90 PSI
  CO2-saturated water pressure, 8–15 °C reservoir temperature.
- Procedure-loose dimensions — 8–12" coil loop diameter, ~3" rear-panel
  un-sleeved length, "hand-snug + 1/4 turn". Substituting these from a
  fixed numeric constant would misrepresent the intentional looseness.

Run from this directory or via absolute path:

    tools/cad-venv/bin/python hardware/assembly/_faucet_and_umbilical_sync.py
"""

import importlib.util
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware")))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from docgen import substitute_md  # noqa: E402


def _load_module(name: str, path: Path):
    """Load a module from an explicit file path, isolated from sys.modules.

    Each generator script lives in its own directory and has unique
    sys.path requirements (the generators themselves do sys.path.insert
    on their parent directories). Loading via importlib.util keeps each
    module under a stable name here without disturbing whatever module
    imports any of them does internally.
    """
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
        # Source-of-truth: `touch-flo-tpu-o-ring/touch_flo_tpu_o_ring.py`.
        "CAP_HOLE_D": f"{tpu.cap_hole_diameter:.4g} mm",  # 6.5
        "BODY_PORT_D": f"{tpu.body_port_diameter:.4g} mm",  # 10
        "OUTER_D": f"{tpu.outer_diameter:.4g} mm",  # 10.2
        "BODY_SQUEEZE": f"{tpu.body_squeeze:.4g} mm",  # 0.1
        "INNER_D": f"{tpu.inner_diameter:.4g} mm",  # 9.45
        "LLDPE_INTERFERENCE": f"{tpu.lldpe_interference:.4g} mm",  # 0.0375
        "TOTAL_H": f"{tpu.total_height:.4g} mm",  # 15
        "CAP_T": f"{tpu.cap_thickness:.4g} mm",  # 1.5
        "CYL_L": f"{tpu.cylinder_length:.4g} mm",  # 13.5
        "LLDPE_ID": f"{tpu.lldpe_id:.4g} mm",  # 6.35
        "LLDPE_OD": f"{tpu.lldpe_od:.4g} mm",  # 9.525
        # Under-counter keyhole plate (touch-flo-under-counter-plate) —
        # BOM row line 27. Hole positions are shared with the gasket /
        # mounting plate (same NAMES, same dimensions across the stack-up).
        # Source-of-truth: `touch-flo-under-counter-plate/touch_flo_under_counter_plate.py`.
        "PLATE_D": f"{plate.disc_diameter:.4g} mm",  # 54.35
        "SHANK_HOLE_D": f"{plate.shank_diameter:.4g} mm",  # 12.6
        "PILL_L": f"{plate.pill_long_y:.4g} mm",  # 13.2
        "PILL_W": f"{plate.pill_short_x:.4g} mm",  # 6.85
        "FILLET_R": f"{plate.fillet_radius:.4g} mm",  # 1.5
    }

    substitute_md(
        _here / "faucet-and-umbilical.md",
        variables=variables,
        expected_counts={
            # TPU thimble — every dimension appears once in the row prose,
            # except BODY_PORT_D (cited as the port the thimble seats
            # into) which the prose mentions twice.
            "CAP_HOLE_D": 1,
            "BODY_PORT_D": 1,
            "OUTER_D": 1,
            "BODY_SQUEEZE": 1,
            "INNER_D": 1,
            "LLDPE_INTERFERENCE": 1,
            "TOTAL_H": 1,
            "CAP_T": 1,
            "CYL_L": 1,
            "LLDPE_ID": 1,
            "LLDPE_OD": 1,
            # Under-counter plate — SHANK_HOLE_D appears twice (pocket
            # diameter + channel width that match by design), PILL_W
            # appears twice (pill short axis + channel width that match
            # by design). Other dimensions appear once.
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
