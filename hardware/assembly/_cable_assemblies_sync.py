"""Doc-sync driver for hardware/assembly/cable-assemblies.md.

Every conductor count in the schedule is a board connector's pin count, so the
board is the source: `<Jst name="Jn" ... count={N}>` for the XH wafers, and the
KF301 screw terminal's pinLabels for J10.

Run: tools/cad-venv/bin/python hardware/assembly/_cable_assemblies_sync.py
"""

import re
import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
sys.path.insert(0, str(_repo / "tools"))

from docgen import substitute_md  # noqa: E402

BOARD = _repo / "hardware" / "pcb" / "pcba" / "pcba.tsx"

# XH wafers carry their own pin count; J10 is a 2-position KF301 screw terminal
# declared by its pin labels instead.
_JST = re.compile(r'<Jst\s+name="(J\d+)"[^>]*?count=\{(\d+)\}')
_KF301 = re.compile(r'<KF301_5_0_2P\s+name="(J\d+)"')


def connector_pins() -> dict[str, int]:
    board = BOARD.read_text()
    pins = {name: int(count) for name, count in _JST.findall(board)}
    for name in _KF301.findall(board):
        pins[name] = 2
    return pins


def main():
    pins = connector_pins()
    wanted = [f"J{n}" for n in list(range(1, 12)) + [13]]

    missing = [j for j in wanted if j not in pins]
    if missing:
        raise ValueError(f"{BOARD.name}: no connector declaration found for {missing}")

    variables = {f"{j}_PINS": pins[j] for j in wanted}

    # J1 (MANIFOLD A), J4, J6, J7, and J13 carry their count in the basis
    # sentence and again in the schedule row; the rest appear in both too.
    # J2's schedule row states its populated count (5 of 6), not its pin count.
    expected_counts = {f"{j}_PINS": (1 if j == "J2" else 2) for j in wanted}

    substitute_md(_here / "cable-assemblies.md", variables, expected_counts)
    print(" ".join(f"{j}={pins[j]}" for j in wanted))


if __name__ == "__main__":
    main()
