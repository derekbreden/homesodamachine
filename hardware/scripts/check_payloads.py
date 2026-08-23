#!/usr/bin/env python3
"""Which solids the payload beside them does not stand for.

`loadStepFile` fetches `<file>.step.mesh` and parses the solid only where there is none
(`web/public/js/viewer/step.js`), and every picture this repository draws goes through that one
mount: `/3d` in a browser,
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

WHETHER A PAYLOAD STANDS FOR ITS SOLID IS READ OFF ITS BYTES AND NEVER OFF ITS MTIME. The
payload states `src`, the sha256 of the STEP it was cut from (`_mesh_payload.write`), and the
reading here is that digest against the solid's own bytes.

`src` RECORDS DESCENT AND NOT AGREEMENT. Under the directories above the payload carries surface
the solid does not — that is the whole reason it is bundled — so the two are unequal by design
and equality is not a thing there is to test. What the digest settles is which STEP's bytes the
payload answers to; `flute_payload` grafting flutes into one carries the host's own `src`
forward, because grafting a surface does not change which bytes it descends from.

An mtime test cannot answer this across a cache boundary: a restore stamps what it restores with the time it restored it, so a
stale payload arrives NEWER than the STEP just cut beside it, and the one ordering an mtime test
calls current is exactly the one where it is not.

A payload that states no `src`, or a version this repository no longer writes, is named too —
`decodeMeshPayload` reads the STEP for any version it does not know, so such a payload is one to
write again whether or not the solid's bytes have moved.

WHAT A GREEN READING SAYS. Per solid, one header read and one hash: the payload beside it names
these exact bytes. The triangles in it are still not read and not held against anything. And a
build hands the tree the payloads that are in a step's `outs`.
`enclosure.step.mesh`, `enclosure-assembly.step.mesh` and `manifold-layout.step.mesh` are in
none: they are written inside the sandbox and go with it, so `tools/bazel/sync_tree.py` carries
the solid into the tree and leaves the payload the tree had. A run of the generator on this disk
is what writes those three.

Naming them costs a stat each. Writing one costs the generator's run.
"""
import json
import struct
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


# `_mesh_payload` owns this format, and its four header readers need nothing but `struct` and
# `json` — but the module imports OCP at its top, which this checker does not have and must not
# pay for. The read is repeated here against the version that module writes.
PAYLOAD_VERSION = 3


def payload_header(path) -> dict:
    """An existing payload's header dict — u32 length, then that many bytes of JSON."""
    with open(path, "rb") as f:
        return json.loads(f.read(struct.unpack("<I", f.read(4))[0]))


def behind(root: Path) -> list:
    """Every owed solid whose payload is absent, unreadable, of a version the page does not
    decode, or cut from bytes the solid no longer holds, as (solid, which)."""
    out = []
    for rel in owed(root):
        mesh = root / (rel + ".mesh")
        if not mesh.exists():
            out.append((rel, "absent"))
            continue
        try:
            header = payload_header(mesh)
        except (OSError, ValueError, struct.error):
            out.append((rel, "not a payload"))
            continue
        if header.get("v") != PAYLOAD_VERSION:
            out.append((rel, "a payload version the page does not decode"))
            continue
        src = header.get("src")
        if src is None:
            out.append((rel, "states no source digest"))
            continue
        try:
            if src != pack._sha256(root / rel):
                out.append((rel, "cut from other bytes than the solid holds"))
        except OSError:
            continue
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
        def payload(path, src, v=PAYLOAD_VERSION):
            """A payload carrying just the header this checker reads."""
            head = json.dumps({"v": v, "src": src}).encode()
            path.write_bytes(struct.pack("<I", len(head)) + head)

        (here / "a.step").write_text("x")
        solid_x = pack._sha256(here / "a.step")
        payload(here / "a.step.mesh", solid_x)
        (elsewhere / "cap.step").write_text("x")

        hold("only a solid in a payload directory owes one",
             owed(root), [f"{payload_dir}/a.step"])

        hold("a payload cut from these bytes is not named", behind(root), [])

        # THE READING THAT AN MTIME TEST GETS BACKWARDS. A cache restore stamps a stale payload
        # with the time it restored it, so it lands newer than the STEP cut beside it.
        os.utime(here / "a.step", ns=(1_000_000_000_000_000_000,) * 2)
        os.utime(here / "a.step.mesh", ns=(9_000_000_000_000_000_000,) * 2)
        hold("mtime alone does not make a payload current", behind(root), [])

        (here / "a.step").write_text("moved")
        hold("a payload cut from other bytes is named", behind(root),
             [(f"{payload_dir}/a.step", "cut from other bytes than the solid holds")])

        payload(here / "a.step.mesh", pack._sha256(here / "a.step"), v=PAYLOAD_VERSION - 1)
        hold("a payload of a version the page does not decode is named", behind(root),
             [(f"{payload_dir}/a.step", "a payload version the page does not decode")])

        (here / "a.step.mesh").write_bytes(b"m")
        hold("a file that is not a payload is named", behind(root),
             [(f"{payload_dir}/a.step", "not a payload")])

        (here / "a.step.mesh").unlink()
        hold("a solid with no payload at all is named", behind(root),
             [(f"{payload_dir}/a.step", "absent")])

        payload(elsewhere / "cap.step.mesh", "0" * 64)
        hold("a solid outside a payload directory is never named",
             [rel for rel, _ in behind(root)], [f"{payload_dir}/a.step"])

    print(f"check_payloads selftest {holds}/8")
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
