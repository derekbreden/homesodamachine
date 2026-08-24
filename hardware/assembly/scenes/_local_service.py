#!/usr/bin/env python3
"""Build the enclosure back-top's current local service view.

    tools/cad-venv/bin/python hardware/assembly/scenes/_local_service.py
    tools/cad-venv/bin/python hardware/assembly/scenes/_local_service.py selftest

This is the short design loop for work inside ``enclosure-back-top``.  It derives the current
pack and Box from ``enclosure_assembly.machine()``, realizes only that one enclosure quadrant,
and cuts the existing ``back-top`` bench scene from the result.  The other enclosure pieces,
the funnel, the ceiling, the scorecard, the pictures, and the production scene meshes are not
part of this producer.

The output is deliberately named ``out/local-back-top.glb``.  ``out/`` is ignored and excluded
from the CAD artifact pack; the exact remote artifact remains ``glb/back-top.glb``.  The local
file therefore cannot replace a production scene or make an old full assembly look current.
"""

import sys
from pathlib import Path


HERE = Path(__file__).resolve()
HW = next(p for p in HERE.parents if p.name == "hardware")
ROOT = HW.parent
for p in (HERE.parent, HW / "scripts", HW / "manifold-layout",
          HW / "printed-parts" / "enclosure" / "enclosure"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

SCENE_ID = "back-top"
PIECE_ID = "back-top"
PIECE_NAME = "enclosure-back-top"
OUTPUT = HERE.parent / "out" / "local-back-top.glb"
GLB_TOL = 0.5


def _realize_piece(enc, box, *, realized=None, keyed=None):
    """The one changed solid, under the same source-complete cache key as ``build_pieces``."""
    if realized is None or keyed is None:
        import _realized
        realized = _realized.realized if realized is None else realized
        keyed = _realized.key if keyed is None else keyed
    key = keyed(enc.__name__, box, PIECE_ID)
    return realized(key, lambda: enc.build_piece(box, "back", "top"))


def build_current():
    """Return the current back-top bench unit without standing the full assembly."""
    import _scenes
    import enclosure_assembly as ea
    import render_scenes

    assembly, _pack, box = ea.machine()
    piece = _realize_piece(ea._enc, box)
    assembly.add(piece, name=PIECE_NAME, color=ea.WALL_COLORS[PIECE_ID])

    scene = _scenes.SCENE_BY_ID[SCENE_ID]
    service, _target = render_scenes.cut(assembly, scene)
    drawn = {child.name for child in service.children}
    if PIECE_NAME not in drawn:
        raise RuntimeError(
            f"local {SCENE_ID!r} service view omitted its freshly built {PIECE_NAME!r}")
    return service


def generate() -> tuple[Path, bool, int]:
    """Atomically write the local GLB; answer its path, whether bytes moved, and body count."""
    # Import first: every CAD generator takes the global build lock here, before it starts
    # geometry.  The dev watcher runs this producer ahead of the exact wave, so they never pile
    # two OCCT processes onto the same cores.
    from _cadq_export import _atomic_write

    service = build_current()
    changed = _atomic_write(
        OUTPUT,
        lambda out: service.export(
            str(out), tolerance=GLB_TOL, angularTolerance=GLB_TOL),
    )
    return OUTPUT, changed, len(service.children)


def selftest():
    """Hold the changed-part/cache boundary and the distinct local output contract."""
    import _scenes
    from types import SimpleNamespace

    assert OUTPUT.parent.name == "out"
    assert OUTPUT.name == "local-back-top.glb"
    assert OUTPUT != HERE.parent / "glb" / "back-top.glb"
    assert _scenes.SCENE_BY_ID[SCENE_ID].roots == (PIECE_NAME,)

    calls = []

    def build_piece(box, y_side, z_side):
        calls.append(("build", box, y_side, z_side))
        return "fresh-piece"

    fake_enclosure = SimpleNamespace(__name__="fake_enclosure", build_piece=build_piece)
    box = object()

    def keyed(*description):
        calls.append(("key", description))
        return "current-key"

    def realized(key, producer):
        calls.append(("realized", key))
        return producer()

    assert _realize_piece(fake_enclosure, box, realized=realized, keyed=keyed) == "fresh-piece"
    assert calls == [
        ("key", ("fake_enclosure", box, PIECE_ID)),
        ("realized", "current-key"),
        ("build", box, "back", "top"),
    ]
    print("local service producer selftest OK")


def main(argv):
    if argv == ["selftest"]:
        selftest()
        return
    if argv:
        sys.exit("usage: _local_service.py [selftest]")
    output, changed, bodies = generate()
    state = "fresh bytes" if changed else "same bytes"
    print(f"-> {output.relative_to(ROOT)} ({bodies} bodies, {state})")


if __name__ == "__main__":
    main(sys.argv[1:])
