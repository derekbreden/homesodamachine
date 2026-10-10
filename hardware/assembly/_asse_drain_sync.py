"""Keep ASSE drain assembly dimensions tied to the production geometry."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for path in (ROOT / "tools", ROOT / "hardware/manifold-layout",
             ROOT / "hardware/reference/neofit-drain-bulkhead"):
    sys.path.insert(0, str(path))

import _drain
import neofit_drain_bulkhead as bulkhead
from docgen import substitute_md


def main():
    substitute_md(HERE / "asse-drain.md", variables={
        "DRAIN_OD": f"{_drain.OD:g}",
        "DRAIN_ID": f"{_drain.ID:g}",
        "DRAIN_WALL": f"{(_drain.OD - _drain.ID) / 2:g}",
        "DRAIN_BEND_R": f"{_drain.MIN_R:g}",
        "DRAIN_THREAD_D": f"{bulkhead.THREAD_D:g}",
        "DRAIN_THREAD_PITCH": f"{bulkhead.THREAD_PITCH:g}",
        "DRAIN_PANEL_BARREL": f"{bulkhead.PANEL_THREAD:g}",
    })
    print("-> asse-drain.md")


if __name__ == "__main__":
    main()
