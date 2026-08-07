"""Doc-sync driver for hardware/assembly/internal-plumbing.md.

Run: tools/cad-venv/bin/python hardware/assembly/_internal_plumbing_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cadlib"
    ),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
    ),
)

from _cold_core_interface import cap_conduits, cap_conduit_bore_radius  # noqa: E402

from docgen import substitute_md  # noqa: E402


def main():
    variables = {
        # Every warm-side fluid termination this procedure lands on is a conduit
        # in the cold core's top cap — a bore up one of the cup's own columns,
        # opening on the lid's outer face. `cap_conduits` is the table; a conduit
        # added or dropped there moves this count, and the procedure's own list
        # of what it closes has to move with it.
        "CAP_CONDUITS": f"{len(cap_conduits)}",
        "CAP_CONDUIT_D": f"{2 * cap_conduit_bore_radius:.4g} mm",
    }

    substitute_md(
        _here / "internal-plumbing.md",
        variables=variables,
        expected_counts={
            "CAP_CONDUITS": 2,
            "CAP_CONDUIT_D": 1,
        },
    )
    print("-> internal-plumbing.md")


if __name__ == "__main__":
    main()
