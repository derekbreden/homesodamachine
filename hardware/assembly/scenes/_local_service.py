#!/usr/bin/env python3
"""Build the enclosure back-top's current local service view.

    tools/cad-venv/bin/python hardware/assembly/scenes/_local_service.py
    tools/cad-venv/bin/python hardware/assembly/scenes/_local_service.py selftest

This is the short design loop for work inside ``enclosure-back-top``. The current Rust
placement plan and scalar Box size one back-top, which the enclosure program cuts alone, and
the Rust scene exporter draws the existing ``back-top`` bench unit from its placed model
references. The other enclosure pieces, scorecard, pictures and production scene meshes are
not part of this producer.

The output is deliberately named ``out/local-back-top.glb``.  ``out/`` is ignored and excluded
from the CAD artifact pack; the exact remote artifact remains ``glb/back-top.glb``.  The local
file therefore cannot replace a production scene or make an old full assembly look current.
"""

import hashlib
import sys
import tempfile
from pathlib import Path
from types import SimpleNamespace


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


def _body(name):
    stem, _, tail = name.rpartition("/")
    return stem if tail.isdigit() else name


def _members(plan, scene):
    """The back-top unit's source fastening, rider and tube ownership tables."""
    import _scenes
    import _scorecard

    metadata = plan["metadata"]
    present = set(metadata["raw_bounds"]) | {PIECE_NAME}
    rows = (*_scorecard.MOUNTS, *_scorecard._selected_mounts())
    holders = {name: (by if isinstance(by, str) else None) or _scenes.BEARS_ON.get(name)
               for name, by, _joint in rows if name in present}
    holders.update(metadata.get("manifold_tube_holders", {}))
    for name in metadata.get("core_equipment_names", ()):
        if name in holders:
            holders[name] = _scenes.INNER_ROOT
    for name in (*_scenes.BACK_TOP_CARRIED_COMPONENTS, *_scenes.BACK_TOP_CARRIED_TUBES,
                 "tube-soda-core-rise"):
        if name in present:
            holders[name] = PIECE_NAME
    for rider, host in _scorecard.RIDES.items():
        if rider in holders and host in holders:
            holders[rider] = holders[host]
    names = set()
    for root in scene.roots:
        names |= _scenes.held_by(root, holders, scene.later)
    runs = [SimpleNamespace(**row) for row in metadata.get("runs", ())]
    names |= _scenes.runs_for(names, runs, holders)
    names |= set(scene.also)
    names -= set(scene.later)
    return sorted(names)


def _instances(plan, names):
    """Select the scene's fine-model entries, retaining their authored f64 frames."""
    from _assembly_model import identity
    sources = {}
    selected = []
    for row in plan["instances"]:
        if row.get("name") is not None:
            if _body(row["name"]) in names:
                selected.append(row)
            continue
        model = row["model"]
        if model not in sources:
            sources[model] = identity(model)
        entries = sources[model]
        indices = [index for index in row.get("indices", range(len(entries)))
                   if _body(row.get("prefix", "") + entries[index][0]) in names]
        if indices:
            selected.append({**row, "indices": indices})
    return selected


def build_current(directory=None):
    """Return a fresh, file-reference back-top scene without the full assembly."""
    import _box_spec
    import _scenes
    import _enclosure_rust_driver
    _enclosure_rust_driver.load()
    import _machine_export
    import _machine_layout
    import _rust_part

    directory = Path(directory) if directory is not None else ROOT / "tmp/local-back-top"
    plan = _machine_layout.plan(stage="pack", directory=directory / "pack")
    shell, box = _enclosure_rust_driver.box_from_plan(plan)
    from _materials import linear
    piece = directory / "piece"
    piece.mkdir(parents=True, exist_ok=True)
    declared = _box_spec.write(box, shell.BOUNDS, directory / "enclosure-box.json")
    _rust_part.run("enclosure", "enclosure", "--box", declared, "--piece", PIECE_ID, piece)
    scene = _scenes.SCENE_BY_ID[SCENE_ID]
    names = _members(plan, scene)
    if PIECE_NAME not in names:
        raise RuntimeError(
            f"local {SCENE_ID!r} service view omitted its freshly built {PIECE_NAME!r}")
    selected = _instances(plan, set(names) - {PIECE_NAME})
    selected.append({"model": str(piece / (PIECE_NAME + ".step.npz")),
                     "name": PIECE_NAME, "color": linear(shell.PIECE_COLORS[PIECE_ID])})
    skins = [skin for skin in plan.get("presentation", ())
             if not skin.get("targets") or any(_body(name) in names for name in skin["targets"])]
    model_directory = directory / "model"
    _machine_export.export({"name": "local-back-top", "instances": selected,
                            "presentation": skins}, model_directory)
    return _view_spec(plan, scene, names, model_directory)


def _view_spec(plan, scene, names, model_directory):
    import _machine_layout
    import _finishes
    context = {"metadata": dict(plan["metadata"])}
    _machine_layout._view_metadata(context, model_directory / "local-back-top.step.npz")
    return {"outer_payload": str(model_directory / "local-back-top.step.mesh"),
            "colours": context["metadata"]["colours"], "finishes": _finishes.rows(),
            "views": [{"id": scene.id, "file": str(OUTPUT), "bodies": names,
                       "inner": [], "flip": scene.flip}]}


def _sha(path):
    if not path.is_file():
        return None
    with path.open("rb") as source:
        return hashlib.file_digest(source, "sha256").hexdigest()


def generate() -> tuple[Path, bool, int]:
    """Atomically write the local GLB; answer its path, whether bytes moved, and body count."""
    import _machine_export
    before = _sha(OUTPUT)
    work = ROOT / "tmp/local-back-top"
    work.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=work) as directory:
        scene = build_current(directory)
        _machine_export.views(scene, OUTPUT.parent)
    return OUTPUT, before != _sha(OUTPUT), len(scene["views"][0]["bodies"])


def selftest():
    """Hold the distinct local output and shared back-top scene contract."""
    import _scenes

    assert OUTPUT.parent.name == "out"
    assert OUTPUT.name == "local-back-top.glb"
    assert OUTPUT != HERE.parent / "glb" / "back-top.glb"
    assert _scenes.SCENE_BY_ID[SCENE_ID].roots == (PIECE_NAME,)

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
