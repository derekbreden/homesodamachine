#!/usr/bin/env python3
"""Which solids the payload beside them does not stand for.

`loadStepFile` fetches `<file>.step.mesh` and parses the solid only where there is none
(`web/public/js/viewer/step.js`), and every picture this repository draws goes through that one
mount: `/3d` in a browser, `tools/render/render-thumbnails.js` for the grid,
`tools/render/render-step-posed.js` for the assembly cards. On the enclosure the payload is
where the show surface is — `printed-parts/enclosure/enclosure/flute_skin.py` cuts the flutes
into the printed mesh and `hardware/scripts/flute_payload.py` puts them into the payload at the
viewer's own deflection, and the solid beside them is a smooth prism of planes and cylinders. A
payload that is absent draws that prism; one older than the solid draws the surface the solid no
longer holds. The page reports neither: it draws, and what it draws is a part.

WHICH SOLIDS OWE ONE is `pack.py`'s `BUNDLED_PAYLOAD_DIRS` — the directories whose `.step.mesh`
goes into the bundle, so a solid under one is a solid a deploy is served a payload for. It is
imported, so the list a pack walks and the list read here are one list, and the walk is
`pack.solids`: this disk, which is what a pack reads, and not the lock the last one wrote. Every
other solid in the catalog is drawn from its STEP and owes nothing.

The comparison is the one `_cadq_export._current` makes: `_atomic_write` leaves an unchanged
target's mtime alone, so a payload no older than the solid beside it was tessellated from those
bytes. A fetched tree holds the pair at the epoch — both are members of one bundle,
`web/scripts/fetch-cad-artifacts.mjs` holds each to the hash the lock names on the way in, and
the bundle carries no mtime — so the two read equal and this is quiet.

WHAT A GREEN READING SAYS. Two stats per solid: nothing wrote the solid after the payload beside
it was written. The payload is not opened, so the triangles in it are not read and not held
against anything. And a build hands the tree the payloads that are in a step's `outs`.
`enclosure.step.mesh`, `enclosure-assembly.step.mesh` and `manifold-layout.step.mesh` are in
none: they are written inside the sandbox and go with it, so `tools/bazel/sync_tree.py` carries
the solid into the tree and leaves the payload the tree had. A run of the generator on this disk
is what writes those three.

Naming them costs a stat each. Writing one costs the generator's run.
"""
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]

# ONE WALK ANSWERS WHICH SOLIDS A BUNDLE CARRIES A PAYLOAD FOR and `pack.py` is where it lives.
# Its directory's hyphen keeps it out of a dotted import, so the path goes on `sys.path` and the
# module is imported by name — the way `tools/bazel/inventory.py` reaches the same walk.
sys.path.append(str(_ROOT / "tools" / "cad-artifacts"))
import pack  # noqa: E402

GRAPH = _ROOT / "tools" / "bazel" / "graph.json"


def owed(root: Path) -> list:
    """Every solid the bundle carries a `.step.mesh` for, repo-relative and sorted."""
    dirs = tuple(f"{d}/" for d in pack.BUNDLED_PAYLOAD_DIRS)
    return [rel for rel in pack.solids(root)
            if rel.endswith(".step") and rel.startswith(dirs)]


def behind(root: Path) -> list:
    """Every owed solid whose payload is absent or older than it, as (solid, which)."""
    out = []
    for rel in owed(root):
        try:
            solid = (root / rel).stat().st_mtime_ns
        except OSError:
            continue
        try:
            if (root / (rel + ".mesh")).stat().st_mtime_ns < solid:
                out.append((rel, "older than the solid"))
        except OSError:
            out.append((rel, "absent"))
    return sorted(out)


def graph() -> dict:
    try:
        return json.loads(GRAPH.read_text())
    except (OSError, ValueError):
        return {}


def writers(seen: dict, path: str) -> list:
    """The generators a trace was watched writing `path`."""
    return sorted(gen for gen, step in seen.items() if path in step.get("writes", ()))


def flute_dirs(seen: dict) -> tuple:
    """The directories `flute_payload.py` declares a payload in."""
    written = seen.get("hardware/scripts/flute_payload.py", {}).get("writes", ())
    return tuple(sorted({f"{Path(p).parent.as_posix()}/"
                         for p in written if p.endswith(".step.mesh")}))


def selftest() -> int:
    import tempfile
    import os

    holds = 0

    def hold(label, got, want):
        nonlocal holds
        ok = got == want
        holds += ok
        print(f"  {'✓' if ok else '✗'} {label}" + ("" if ok else f" — {got!r} != {want!r}"))

    # A REAL PAYLOAD DIRECTORY AND A REAL SOLID DIRECTORY, because the rule under test is which
    # of the two owes a payload, and `pack.BUNDLED_PAYLOAD_DIRS` is what answers.
    payload_dir = pack.BUNDLED_PAYLOAD_DIRS[0]
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        here = root / payload_dir
        here.mkdir(parents=True)
        elsewhere = root / "hardware" / "printed-parts" / "cap"
        elsewhere.mkdir(parents=True)
        (here / "a.step").write_text("x")
        (here / "a.step.mesh").write_text("m")
        (elsewhere / "cap.step").write_text("x")

        hold("only a solid in a payload directory owes one",
             owed(root), [f"{payload_dir}/a.step"])

        os.utime(here / "a.step", ns=(1_000_000_000_000_000_000,) * 2)
        os.utime(here / "a.step.mesh", ns=(1_000_000_000_000_000_000,) * 2)
        hold("one run writing both is not named", behind(root), [])

        os.utime(here / "a.step.mesh", ns=(2_000_000_000_000_000_000,) * 2)
        hold("a payload newer than its solid is not named", behind(root), [])

        os.utime(here / "a.step", ns=(3_000_000_000_000_000_000,) * 2)
        hold("a payload older than its solid is named", behind(root),
             [(f"{payload_dir}/a.step", "older than the solid")])

        (here / "a.step.mesh").unlink()
        hold("a solid with no payload at all is named", behind(root),
             [(f"{payload_dir}/a.step", "absent")])

        (elsewhere / "cap.step.mesh").write_text("m")
        os.utime(elsewhere / "cap.step", ns=(3_000_000_000_000_000_000,) * 2)
        hold("a solid outside a payload directory is never named",
             [rel for rel, _ in behind(root)], [f"{payload_dir}/a.step"])

    print(f"check_payloads selftest {holds}/6")
    return 0 if holds == 6 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()
    named = behind(_ROOT)
    if not named:
        return 0
    print(f"{len(named)} solid(s) whose surface is not in the payload beside them:")
    for rel, which in named:
        print(f"    {rel}.mesh — {which}")
    seen = graph()
    cut_by = sorted({gen for rel, _ in named for gen in writers(seen, rel)})
    if cut_by:
        print("  the run that cuts a solid writes the payload beside it:")
        for gen in cut_by:
            print(f"    tools/cad-venv/bin/python {gen}")
    flutes = flute_dirs(seen)
    if flutes and any(rel.startswith(flutes) for rel, _ in named):
        print("  and the enclosure's flutes go back into those payloads after:")
        print("    tools/cad-venv/bin/python hardware/scripts/flute_payload.py")
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
