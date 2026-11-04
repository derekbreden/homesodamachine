"""Standalone drilling jaws for the candidate water-inlet jet cap stock.

The base lies on the drill table, Z=0. A rod stands on its 8 mm floor. Two
horizontal C-clamps close the loose jaw against the fixed jaw; two more hold
the base flanges to the owned wood backer and drill table. The grooves are
vertical and open at the top. There is no printed drill bushing.

The nominal stock diameter comes from the candidate jet dimensions. Physical
stock fit, printed grip, clamp clearance and spindle alignment are untested.
This bench fixture is not part of the machine assembly or its BOM.

Run with tools/cad-venv/bin/python. No argument exports both print parts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
for _path in (_hw / "scripts", _hw / "cold-core-layout", _repo / "tools"):
    sys.path.insert(0, str(_path))

from _water_inlet_jet import JET_CAP_D, JET_PASSAGE_D  # noqa: E402
from docgen import substitute_md  # noqa: E402


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()


ROD_D = JET_CAP_D
GROOVE_RADIAL_SLIP = 0.15
GROOVE_R = ROD_D / 2.0 + GROOVE_RADIAL_SLIP
OPEN_JAW_GAP = 1.0
BASE_X = 120.0
BASE_Y = 90.0
BASE_T = 8.0
JAW_X = 64.0
JAW_DEPTH = 25.0
GRIP_Z = 30.0
HANDLING_BLANK_L = 50.0
MIN_HANDLING_BLANK_L = 40.0
JAW_CLAMP_X = 20.0
BASE_CLAMP_X = 46.0
MESH_TOLERANCE = 0.02
MESH_ANGLE = 0.15


def numbers():
    """Existing drill jaws in their separate upright print frames."""
    import _rust_part
    _rust_part.start()
    from _material_base import M_PETGF_BLACK
    from _materials import linear
    return {"base": [BASE_X, BASE_Y, BASE_T],
            "jaw": [JAW_X, JAW_DEPTH, GRIP_Z],
            "gap": OPEN_JAW_GAP, "groove_radius": GROOVE_R,
            "stock_diameter": ROD_D, "radial_slip": GROOVE_RADIAL_SLIP,
            "minimum_blank": MIN_HANDLING_BLANK_L, "drill_diameter": JET_PASSAGE_D,
            "color": list(linear(M_PETGF_BLACK))}


def _document():
    substitute_md(_here.parent / "README.md", variables={
        "JET_FIXTURE_BASE": f"{BASE_X:g} × {BASE_Y:g} × {BASE_T:g} mm",
        "JET_FIXTURE_GRIP": f"{GRIP_Z:g} mm",
        "JET_FIXTURE_GROOVE": f"{2 * GROOVE_R:g} mm",
        "JET_FIXTURE_GAP": f"{OPEN_JAW_GAP:g} mm",
        "JET_FIXTURE_BLANK": f"{HANDLING_BLANK_L:g} mm",
        "JET_FIXTURE_MIN_BLANK": f"{MIN_HANDLING_BLANK_L:g} mm",
        "JET_FIXTURE_JAW_CLAMP_X": f"±{JAW_CLAMP_X:g} mm",
        "JET_FIXTURE_BASE_CLAMP_X": f"±{BASE_CLAMP_X:g} mm",
    })


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else _here.parent
    out.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut("tooling", "water-inlet-jet-fixture", numbers(), out)
    _document()
    print(f"-> water inlet jet fixture: {len(result['files'])} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
