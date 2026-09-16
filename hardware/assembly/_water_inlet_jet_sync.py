"""Update water-inlet jet trial figures from the nominal CAD dimensions.

Run: tools/cad-venv/bin/python hardware/assembly/_water_inlet_jet_sync.py
"""

import math
import sys
from fractions import Fraction
from pathlib import Path


_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_repo / "tools"))
sys.path.insert(0, str(_hw / "cold-core-layout"))

from _water_inlet_jet import JET_CAP_D, JET_CAP_T, JET_PASSAGE_D  # noqa: E402
from docgen import substitute_md  # noqa: E402


DRILL_TRIAL_RPM = 1100
MM_PER_INCH = 25.4


def main():
    bore_inches = JET_PASSAGE_D / MM_PER_INCH
    variables = {
        "CAP_OD": f"{JET_CAP_D:g} mm",
        "CAP_THICKNESS": f"{JET_CAP_T:g} mm",
        "JET_BORE": (
            f"{Fraction(bore_inches).limit_denominator(128)} inch / "
            f"{JET_PASSAGE_D:g} mm"
        ),
        "JET_LD": f"{JET_CAP_T / JET_PASSAGE_D:.2f}",
        "JET_AREA": f"{math.pi * JET_PASSAGE_D ** 2 / 4:.3f} mm²",
        "DRILL_RPM": f"{DRILL_TRIAL_RPM} rpm",
        "DRILL_SFM": f"{math.pi * bore_inches * DRILL_TRIAL_RPM / 12:.1f} surface feet/minute",
    }
    substitute_md(_here / "water-inlet-jet.md", variables=variables)
    print("-> water-inlet-jet.md")


if __name__ == "__main__":
    main()
