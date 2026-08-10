#!/usr/bin/env python3
"""check_doc_sources.py — whether a doc's figures are still the ones its inputs make.

A `[value](NAME)` text is what some run of a sync driver measured. Between two runs a source
moves and the doc goes on reading whatever the last one found — numbers that look like
measurements and are a memory of one. That is the state this answers.

Beside each doc, `docgen.substitute_md` leaves `<doc>.sources.json`: per driver, every repo
file whose text can decide what that driver substitutes, each with the hash of its bytes. This
hashes those files again and compares. What it costs is reading them.

    tools/cad-venv/bin/python hardware/scripts/check_doc_sources.py    (0 = current, 1 = stale)

THE RECORDED LIST IS THE READING, not a list to take again here. The walk resolves a module
name against the `sys.path` its driver is standing on, and the same name resolves to a
different file — or to none — from anywhere else, so a graph taken in this process would be a
different graph and the comparison would be against nothing. The driver records; this reads.

A doc with no sidecar is named and passes: it enrols the next time its driver runs.
"""

import hashlib
import json
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent
SIDECAR_SUFFIX = ".sources.json"


def _hash(path: Path) -> str | None:
    """The hash of `path`'s bytes, in `docgen`'s own terms. None when it is gone."""
    try:
        h = hashlib.blake2b(digest_size=16)
        h.update(path.read_bytes())
        return h.hexdigest()
    except OSError:
        return None


def _moved(files: dict) -> list[str]:
    """Which of `files` no longer hashes to what was recorded."""
    out = []
    for rel, held in sorted(files.items()):
        now = _hash(_root / rel)
        if now is None:
            out.append(f"{rel} — gone")
        elif now != held:
            out.append(rel)
    return out


def main() -> int:
    # Every doc that names a driver, whether or not it has enrolled — so a doc that has
    # never been synced is visible here rather than absent.
    docs = sorted(p for p in _hw.rglob("*.md") if "cad-venv" not in p.parts)
    # A doc is stale or it is not — two of its drivers reporting is one doc to resync.
    stale, enrolled, bare = set(), 0, []
    for doc in docs:
        sidecar = doc.with_name(doc.stem + SIDECAR_SUFFIX)
        if not sidecar.is_file():
            if "## Sources" in doc.read_text():
                bare.append(doc.relative_to(_root))
            continue
        enrolled += 1
        for driver, files in sorted(json.loads(sidecar.read_text()).items()):
            moved = _moved(files)
            if moved:
                rel = doc.relative_to(_root)
                shown = "\n".join(f"        {m}" for m in moved[:6])
                more = f"\n        …and {len(moved) - 6} more" if len(moved) > 6 else ""
                print(f"  {rel}\n      {len(moved)} of {len(files)} sources moved since this "
                      f"doc was written:\n{shown}{more}\n"
                      f"      run tools/cad-venv/bin/python {driver.lstrip('/')}")
                stale.add(rel)

    print(f"{enrolled - len(stale)}/{enrolled} docs carry the figures their sources make"
          + (f", and {len(bare)} have yet to enrol" if bare else ""))
    return 1 if stale else 0


if __name__ == "__main__":
    raise SystemExit(main())
