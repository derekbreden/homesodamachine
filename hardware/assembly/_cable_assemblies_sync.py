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
# docgen is shared machinery — one copy at the repo root, every edition uses
# it. The board is content, so it comes from the nearest hardware/ tree: in a
# duplicated edition those are different trees, and content must be the near one.
_repo = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
_hw = next(p for p in _here.parents if p.name == "hardware")
sys.path.insert(0, str(_repo / "tools"))

from docgen import substitute_md  # noqa: E402

BOARD = _hw / "pcb" / "pcba" / "pcba.tsx"

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

    # Every connector carries its count in the basis sentence and again in the
    # schedule row. J2 carries it a third time in "MANIFOLD B — the empty
    # contact": its row reads "5 of 6", the populated count being a literal
    # (only 5 contacts are crimped) and the housing size the driven token.
    expected_counts = {f"{j}_PINS": (3 if j == "J2" else 2) for j in wanted}

    substitute_md(_here / "cable-assemblies.md", variables, expected_counts)
    print(" ".join(f"{j}={pins[j]}" for j in wanted))


if __name__ == "__main__":
    main()
