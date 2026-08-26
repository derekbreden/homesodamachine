#!/usr/bin/env python3
"""check_flutes.py — whether a payload still draws the surface its print has.

    tools/cad-venv/bin/python hardware/scripts/check_flutes.py
    tools/cad-venv/bin/python hardware/scripts/check_flutes.py selftest

THE FLUTES ARE IN THE MESH AND NOT IN THE STEP. `flute_payload` cuts each enclosure piece's
`.step.mesh` from the printed `.stl`, and `/3d` draws that payload rather than parsing the
B-rep — so the picture is fluted only while the payload is the one that cut carried. Every
other reading in this tree passes on a payload that has lost them: the file decodes, its
version is current, its digest answers to the STEP beside it, the lock names its bytes and the
bundle carries them. What none of those ask is whether the surface is the printed one.

WHAT MAKES A SMOOTH PAYLOAD STICK. `_cadq_export._write_payload_beside` writes a plain
tessellation for any STEP whose payload is not current, and stamps it with that STEP's digest.
A piece recut with the plain writer landing after the flute cut leaves a smooth payload
carrying a correct stamp, and `_payload_current` — which asks descent — then answers yes for
as long as the file stands. The reading that separates them is distance to the print.

MEASURED AS POINT TO SURFACE. `flute_payload.deviation` samples the printed mesh and takes the
closest point on a payload triangle, which is the same reading `simplify_within` accepted the
payload on. A payload that came out of that ladder stands within its own budget; one that
replaced it stands about a flute deep away, and the two do not overlap.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np  # noqa: E402
import trimesh  # noqa: E402

import flute_payload  # noqa: E402

#: Enough of the printed surface to find a flute and few enough to stay inside a check's
#: seconds. `flute_payload.deviation` probes 40,000 for a reading it writes into a payload's
#: own record; separating 0.16 mm from 1.48 mm does not need that many.
PROBE = 1500

#: What a payload may stand past the budget it was accepted on. `simplify_within` returns only
#: a mesh inside `deflection`, so a payload of that descent reads at or under 1.0 here; a plain
#: tessellation of the same solid reads about seven times it. Nothing sits between.
SLACK = 2.0


def reading(step: Path, stl: Path):
    """`(deviation, budget)` for the payload beside `step`, or None where there is none."""
    payload = flute_payload.read_payload(step.with_name(step.name + ".mesh"))
    if not payload or len(payload) != 1:
        return None
    e = payload[0]
    surface = trimesh.Trimesh(np.array(e["pos"], float).reshape(-1, 3),
                              np.array(e["idx"], int).reshape(-1, 3), process=False)
    printed = trimesh.load_mesh(str(stl))
    printed.merge_vertices()
    rng = np.random.default_rng(0)
    n = min(PROBE, len(printed.vertices))
    probe = printed.vertices[rng.choice(len(printed.vertices), n, replace=False)]
    dev = float(trimesh.proximity.closest_point(surface, probe)[1].max())
    return dev, flute_payload.deflection(printed)


def main() -> int:
    found = flute_payload.pieces()
    if not found:
        print(f"  no printed meshes beside the solids in {flute_payload.PIECES_DIR}")
        print("  nothing to hold a payload against")
        return 0

    # FIRST, THE STAMP. Every payload carries the sha256 of the STEP it was cut from
    # (`_mesh_payload.write`), so a payload standing beside a STEP it was not cut from is
    # one comparison, before any surface is probed — and it is the reading that catches a
    # payload the repair loop's own sync failed to carry, which the deviation probe only
    # sees where the surfaces happen to differ at the probe's samples.
    import hashlib
    import _mesh_payload
    stale = []
    for step, _stl in sorted(found):
        mesh = step.with_name(step.name + ".mesh")
        if not mesh.exists():
            continue
        stamped = _mesh_payload.read_source(mesh)
        actual = hashlib.sha256(step.read_bytes()).hexdigest()
        if stamped and stamped != actual:
            stale.append(step.stem)
    if stale:
        print(f"{len(stale)} payload(s) were cut from a STEP that is no longer the one "
              f"beside them:")
        for name in stale:
            print(f"  ✗ {name} — the viewer draws this file, and it is another machine's")
        print("\n  the flute cut is what puts the surface back:")
        print("    bazel build //:flute-payload && "
              "tools/cad-venv/bin/python tools/bazel/sync_tree.py --write "
              "--targets //:flute-payload")
        return 1

    flat = []
    for step, stl in sorted(found):
        got = reading(step, stl)
        if got is None:
            flat.append((step.stem, None, None))
            continue
        dev, budget = got
        if dev > budget * SLACK:
            flat.append((step.stem, dev, budget))

    print(f"payloads held against their print: {len(found)}")
    if flat:
        print(f"\n{len(flat)} payload(s) no longer draw the printed surface:")
        for name, dev, budget in flat:
            if dev is None:
                print(f"  ✗ {name}  — no payload beside the solid")
            else:
                print(f"  ✗ {name}  — stands {dev:.3f} mm off the print, "
                      f"cut to a {budget:.3f} mm budget")
        print("\n  the flute cut is what puts the surface back:")
        print("    bazel build //:flute-payload && "
              "tools/cad-venv/bin/python tools/bazel/sync_tree.py --write "
              "--targets //:flute-payload")
        return 1
    print("✓ every payload stands within the budget its print was cut to")
    return 0


def selftest() -> int:
    """A ridged slab against itself and against its own flat back."""
    holds = 0

    def hold(name, ok):
        nonlocal holds
        holds += 1
        print(f"  {'ok  ' if ok else 'FAIL'} {name}")
        return ok

    ridged = flute_payload._ridged_slab()
    flat = ridged.copy()
    # Flatten the show face onto its own minimum: the shape a plain tessellation of the same
    # solid has, and the shape a payload that lost its flutes has.
    depth_axis = int(np.argmin(ridged.bounding_box.extents))
    v = flat.vertices.copy()
    face = v[:, depth_axis] > v[:, depth_axis].min() + 1e-9
    v[face, depth_axis] = v[:, depth_axis].max()
    flat = trimesh.Trimesh(v, flat.faces, process=False)

    rng = np.random.default_rng(0)
    probe = ridged.vertices[rng.choice(len(ridged.vertices), min(PROBE, len(ridged.vertices)),
                                       replace=False)]
    same = float(trimesh.proximity.closest_point(ridged, probe)[1].max())
    lost = float(trimesh.proximity.closest_point(flat, probe)[1].max())
    budget = flute_payload.deflection(ridged)

    ok = hold("a surface stands no distance from itself", same <= budget * SLACK)
    ok &= hold("a flattened show face stands a flute's depth away", lost > budget * SLACK)
    ok &= hold("and the two readings do not overlap", lost > same * 10)
    print(f"check_flutes selftest {holds}/{holds}"
          if ok else f"check_flutes selftest FAILED ({same:.3f} vs {lost:.3f}, "
                     f"budget {budget:.3f})")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(selftest() if sys.argv[1:] == ["selftest"] else main())
