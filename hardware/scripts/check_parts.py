#!/usr/bin/env python3
"""check_parts.py — whether a committed solid is the one its generator draws.

A `.step` is what some run of a generator cut, and the next build LOADS IT RATHER THAN DRAWING
IT: `foam_assembly` reads `foam-cap-top.step` off the disk, `enclosure_assembly` reads
`foam-assembly.step`. Neither edge is an import, so `_realized.source_files` cannot walk it —
a card's digest covers the Python that could reach the reading and says nothing about the solid
the reading was taken off. That is the state this answers.

    tools/cad-venv/bin/python hardware/scripts/check_parts.py     (0 = current, 1 = owed)

Under `.cache/stamps/parts/`, `_cadq_export._atomic_write` leaves, per solid, the generator that
drew it and the digest of every file that generator's text can reach. This hashes those files
again and compares. What it costs is reading them; what drawing the solid costs is the build.

A SOLID NOTHING HERE HAS STAMPED IS CARRIED, NOT OWED. `hardware/reference/` holds solids
harvested from a vendor — `tee-connector.step` stands in for a John Guest PP0208E — and the
`.py` beside one of those READS it to hold figures against, so naming that script as the remedy
asks it to draw what it was written to measure, and asks again on the next pass forever. What
this counts is the solids a run of this repo has been seen to cut. A part whose first build has
yet to happen on this machine enrols at that build; `verify_clean.py`, which starts from no
stamps at all, is what asks the question of a whole commit.
"""

import subprocess
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent
if str(_hw / "scripts") not in sys.path:
    sys.path.insert(0, str(_hw / "scripts"))

import _realized                                        # noqa: E402


def main() -> int:
    tracked = subprocess.run(["git", "-C", str(_root), "ls-files", "hardware"],
                             capture_output=True, text=True, check=True).stdout.split()
    steps = [_root / f for f in tracked if f.endswith(".step")]

    watched, owed, carried = 0, set(), []
    for step in sorted(steps):
        rel = step.relative_to(_root)
        held = _realized.stamp_read("parts", step)
        if not held:
            carried.append(rel)
            continue
        watched += 1
        moved = _realized.moved(held.get("sources") or {})
        if moved:
            shown = "\n".join(f"        {m}" for m in moved[:6])
            more = f"\n        …and {len(moved) - 6} more" if len(moved) > 6 else ""
            print(f"  {rel}\n      {len(moved)} of {len(held['sources'])} sources moved since "
                  f"this solid was cut:\n{shown}{more}\n"
                  f"      run tools/cad-venv/bin/python {held['by']}")
            owed.add(rel)

    if owed:
        # WHAT RUNS THEM. `owed` asks every check, runs exactly what they name, and does it in
        # the order a part is drawn before an assembly measures it and a sync copies the
        # measurement — which a hand-rolled pass over one check's answer cannot.
        print("\n  all of them, to a fixpoint: python3 hardware/scripts/owed.py --run")
    print(f"{watched - len(owed)}/{watched} solids are the ones their generators cut"
          + (f", and {len(carried)} are carried" if carried else ""))
    return 1 if owed else 0


if __name__ == "__main__":
    raise SystemExit(main())
