"""Doc-sync driver for hardware/assembly/handwork.md.

Pins the carbonator rod to FR-CARB-01's finished length and tolerance, shared
with pressure-vessel.md. Reservoir rod lengths come from reservoir.py and are
shared with the reservoir's level-sensing.md.

Run: tools/cad-venv/bin/python hardware/assembly/_handwork_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(_here))  # _pressure_vessel_sync (same dir)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
        / "reservoir"
    ),
)
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)

from _pressure_vessel_sync import carbonator_rod_len, carbonator_rod_tolerance  # noqa: E402
import reservoir  # noqa: E402

from docgen import load_module, substitute_md  # noqa: E402


_hw = next(p for p in _here.parents if p.name == "hardware")

_coil_mandrel_gen = load_module(
    "handwork_coil_mandrel_gen",
    _hw / "printed-parts" / "cold-core" / "coil-mandrel" / "coil_mandrel.py",
)

# The wrap AS LAID on the carbonator — the figure `bom.md` §5 bills and the sentence in
# handwork.md cites it for. The mandrel's own two shorter readings stay in its module.
_coil_gen = load_module("handwork_coil_gen", _hw / "cold-core-layout" / "_coil.py")

MM_PER_IN = 25.4


def main():
    variables = {
        # Carbonator float-rod cut length — same value pinned in
        # pressure-vessel.md; specified by float_rod_dimensions.py.
        "ROD_LEN": (
            f"{carbonator_rod_len / MM_PER_IN:.3f} ±{carbonator_rod_tolerance / MM_PER_IN:.3f} in "
            f"({carbonator_rod_len:.2f} ±{carbonator_rod_tolerance:.2f} mm)"
        ),
        # Flavor-reservoir float-rod cut length — same value pinned in the
        # reservoir's level-sensing.md; computed in reservoir.py.
        "RESERVOIR_ROD_LEN": (
            f"{reservoir.reservoir_rod_len:.4g} mm "
            f"({reservoir.reservoir_rod_len / MM_PER_IN:.3g} in)"
        ),
        # Evaporator-coil wrap — pitch enforced by the mandrel's helical groove,
        # the tie-in allowances struck in coil_mandrel.py, the laid wrap drawn in
        # cold-core-layout/_coil.py.
        "PITCH": f"{_coil_mandrel_gen.pitch:.4g} mm",
        "LAID_FT": f"{_coil_gen.wrap_length() / 304.8:.4g} ft",
        "STUB_INLET": f"{_coil_mandrel_gen.stub_allowance['inlet']:.4g} mm",
        "STUB_OUTLET": f"{_coil_mandrel_gen.stub_allowance['outlet']:.4g} mm",
    }

    substitute_md(
        _here / "handwork.md",
        variables=variables,
    )
    print("-> handwork.md")


if __name__ == "__main__":
    main()
