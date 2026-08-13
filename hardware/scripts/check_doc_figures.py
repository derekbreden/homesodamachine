#!/usr/bin/env python3
"""check_doc_figures.py — whether a doc carries the figures its sources make.

A `[value](NAME)` text is what some run of a sync driver measured. Between two runs a source
moves and the doc goes on reading whatever the last one found — numbers that look like
measurements and are a memory of one. That is the state this answers, in two readings.

Beside each doc, `docgen.substitute_md` leaves `<doc>.figures.json`: per driver, the texts it
wrote, by name. THE DOC'S OWN BRACKETS ARE THE FIRST READING: a number standing in the doc that
is not the one recorded beside it is a number a hand typed over.

Under `.cache/stamps/docs/`, the same run leaves the hash of every file that decided those
texts. A doc whose sources all hash as they did is one this machine has watched its driver
make. A doc whose sources moved is named with the driver that would say what they make now —
and a driver that lands on the texts already recorded writes nothing, so the tree it leaves
behind is the tree it found.

    tools/cad-venv/bin/python hardware/scripts/check_doc_figures.py    (0 = current, 1 = owed)

THE RECORDED LIST IS THE READING, not a list to take again here. The walk resolves a module
name against the `sys.path` its driver is standing on, and the same name resolves to a
different file — or to none — from anywhere else. The driver records; this reads.

A doc with no sidecar and a figure to write is named and passes: it enrols the next time its
driver runs. A doc whose Sources section is prose about a drawing someone read, carrying no
`[value](NAME)` of its own, has nothing to enrol and is not counted.
"""

import json
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent
if str(_hw / "scripts") not in sys.path:
    sys.path.insert(0, str(_hw / "scripts"))

import _realized                                        # noqa: E402

FIGURES_SUFFIX = ".figures.json"

#: `docgen`'s own marker. A doc carrying none of these has no figure any run writes, so its
#: Sources section is prose about where a person read the numbers — `seaflo-22-pump/README.md`
#: transcribes a vendor drawing — and there is nothing for a driver to enrol.
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")


def _standing(text: str) -> dict:
    """`{NAME: {texts}}` for every marker in `text` — a set, because a name the doc carries
    twice with two different texts is already disagreeing with itself."""
    out: dict = {}
    for m in _LINK_RE.finditer(text):
        out.setdefault(m.group(2), set()).add(m.group(1))
    return out


def _typed_over(figures: dict, standing: dict) -> list:
    """Which of `figures` the doc no longer states as its driver wrote it."""
    out = []
    for name, was in sorted(figures.items()):
        now = standing.get(name)
        if now is None:
            out.append(f"{name} — no longer in the doc, recorded as {was}")
        elif now != {was}:
            out.append(f"{name} — doc says {', '.join(sorted(now))}, recorded as {was}")
    return out


def main() -> int:
    # Every doc that names a driver, whether or not it has enrolled — so a doc that has
    # never been synced is visible here rather than absent.
    docs = sorted(p for p in _hw.rglob("*.md") if "cad-venv" not in p.parts)
    # A doc is owed or it is not — two of its drivers reporting is one doc to resync.
    drifted, owed, enrolled, bare = set(), set(), 0, []
    for doc in docs:
        sidecar = doc.with_name(doc.stem + FIGURES_SUFFIX)
        text = doc.read_text()
        if not sidecar.is_file():
            if "## Sources" in text and _LINK_RE.search(text):
                bare.append(doc.relative_to(_root))
            continue
        enrolled += 1
        rel = doc.relative_to(_root)
        held = json.loads(sidecar.read_text())
        standing = _standing(text)
        stamp = _realized.stamp_read("docs", rel.as_posix())

        for driver, figures in sorted(held.items()):
            cmd = f"run tools/cad-venv/bin/python {driver.lstrip('/')}"

            over = _typed_over(figures, standing)
            if over:
                shown = "\n".join(f"        {o}" for o in over[:6])
                more = f"\n        …and {len(over) - 6} more" if len(over) > 6 else ""
                print(f"  {rel}\n      {len(over)} of {len(figures)} figures are not the ones "
                      f"its driver wrote:\n{shown}{more}\n      {cmd}")
                drifted.add(rel)
                continue

            watched = stamp.get(driver)
            if watched is None:
                print(f"  {rel}\n      nothing here has watched {driver.lstrip('/')} make "
                      f"these {len(figures)} figures\n      {cmd}")
                owed.add(rel)
                continue
            moved = _realized.moved(watched)
            if moved:
                shown = "\n".join(f"        {m}" for m in moved[:6])
                more = f"\n        …and {len(moved) - 6} more" if len(moved) > 6 else ""
                print(f"  {rel}\n      {len(moved)} of {len(watched)} sources moved since this "
                      f"doc was watched:\n{shown}{more}\n      {cmd}")
                owed.add(rel)

    if drifted or owed:
        # WHAT RUNS THEM. A reader who has this list in front of it writes a loop
        # around it — the same loop, by hand, every time — so the list says what
        # takes it. `owed` asks all three of us, runs exactly what is named, and
        # loops to a fixpoint, which a hand-rolled pass over one check's answer
        # cannot: a sync that rewrites a figure stales the doc watching it.
        print("\n  all of them, to a fixpoint: python3 hardware/scripts/owed.py --run")
    print(f"{enrolled - len(drifted | owed)}/{enrolled} docs carry the figures their sources "
          f"make" + (f", and {len(bare)} have yet to enrol" if bare else ""))
    return 1 if (drifted or owed) else 0


if __name__ == "__main__":
    raise SystemExit(main())
