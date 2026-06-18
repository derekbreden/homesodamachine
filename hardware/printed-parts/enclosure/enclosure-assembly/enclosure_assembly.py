"""Kitchen Edition enclosure assembly — the two enclosure halves wrapped
around the contents.

Combines `../enclosure/enclosure-front.step` and `enclosure-back.step` with the
placed parts from `_contents.build()` in their shared coordinates. The contents
keep their per-part colors; the halves are translucent so the arrangement
(and the front↔back split) reads through them.
"""

import sys
from pathlib import Path

import cadquery as cq

_here = Path(__file__).resolve()
_repo = next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
sys.path.insert(0, str(_repo / "hardware" / "scripts"))
sys.path.insert(0, str(_repo / "tools"))
from _cadq_export import export_assembly
from docgen import substitute_py_comments
import _contents as contents

_ENCLOSURE_DIR = _repo / "hardware" / "printed-parts" / "enclosure" / "enclosure"
FRONT_STEP = _ENCLOSURE_DIR / "enclosure-front.step"
BACK_STEP = _ENCLOSURE_DIR / "enclosure-back.step"
FRONT_COLOR = cq.Color(0.85, 0.92, 1.00, 0.22)  # transparent PETG, front half
BACK_COLOR = cq.Color(0.80, 0.88, 0.98, 0.22)   # transparent PETG, back half


def build():
    placed = contents.build()
    front = cq.importers.importStep(str(FRONT_STEP)).val()
    back = cq.importers.importStep(str(BACK_STEP)).val()

    assy = cq.Assembly(name="kitchen-edition-enclosure-assembly")
    assy.add(front, name="enclosure_front", color=FRONT_COLOR)
    assy.add(back, name="enclosure_back", color=BACK_COLOR)
    for name, (shape, color) in placed.items():
        assy.add(shape, name=name, color=color)
    return assy


def main():
    assy = build()
    out = _here.parent / "enclosure-assembly.step"
    export_assembly(assy, str(out))
    print(f"-> {out.name}")

    # Pin the hand-typed placeholder dimensions in _contents.py's prose.
    substitute_py_comments(
        Path(contents.__file__),
        variables={
            "CONDENSER_AIRFLOW": f"{contents.CONDENSER_AIRFLOW:.4g} mm",
            "SEAFLO_DIMS": "{:g} x {:g} x {:g}".format(*contents.SEAFLO_DIMS),
        },
        expected_counts={
            "CONDENSER_AIRFLOW": 1,
            "SEAFLO_DIMS": 1,
        },
    )
    print("-> _contents.py")


if __name__ == "__main__":
    main()
