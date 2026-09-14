"""Every solid this tree stands behind, repo-relative and sorted.

    from _solids import solids
    for rel in solids():
        ...

Two halves, because two things carry them. `hardware/cad-artifacts.json` names the generated
solids and the release asset they arrive in; `git ls-files` names the harvested few, which have no
builder here and are in the index. A fresh clone has the second half on disk and fetches the first
(`web/scripts/fetch-cad-artifacts.mjs`), so both are solids a check can expect to find.
"""

import json
import subprocess
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
POINTERS = _ROOT / "hardware" / "cad-artifacts.json"


def pointed() -> set:
    """The generated solids the pointer file names."""
    try:
        return set(json.loads(POINTERS.read_text()).get("solids", {}))
    except (OSError, ValueError):
        return set()


def tracked() -> set:
    """The `.step` files the index holds."""
    out = subprocess.run(["git", "-C", str(_ROOT), "ls-files", "*.step"],
                         capture_output=True, text=True).stdout
    return set(out.split())


def solids() -> list:
    return sorted(pointed() | tracked())
