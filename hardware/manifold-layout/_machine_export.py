"""Finish the machine's files after its geometry-building process exits.

The builder supplies its existing fine models and drawn arrays, plus the facts,
scene membership and exact printed-surface frame read off its live assembly.
Writing STEP, payloads and scene GLBs needs those values, not the builder's
boolean history, selectors or query state.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[2]
BUILD_ARG = "--export-handoff"
for _path in (ROOT, ROOT / "hardware/scripts", ROOT / "hardware/assembly/scenes"):
    if str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


def run(source):
    """Build in a child, wait for its exit, then finish with no live builder."""
    from _run_lock import acquire
    import _run_slots

    source = Path(source).resolve()
    acquire(source.relative_to(ROOT).as_posix())
    with tempfile.TemporaryDirectory(prefix="hsm-machine-export-") as directory:
        plan = Path(directory) / "export.json"
        subprocess.run([sys.executable, str(source), BUILD_ARG, str(plan)],
                       check=True, **_run_slots.subprocess_kwargs())
        finish(plan)


def stage_assembly(assembly, target, directory):
    """Keep the current export's exact fine and drawn data in their own order."""
    import meshcad
    import _mesh_payload
    from _cadq_export import _atomic_write, _mesh_bodies

    writer = meshcad.writer()
    target = Path(target).resolve()
    bodies = _mesh_bodies(assembly)
    solids = [shape for _, shape, _ in bodies]
    names = [name for name, _, _ in bodies]
    colors = [color for _, _, color in bodies]
    boxes = [solid.BoundingBox() for solid in solids]
    size = [max(getattr(box, axis + "max") for box in boxes)
            - min(getattr(box, axis + "min") for box in boxes) for axis in "xyz"]
    deflection = sum(size) / 3.0 * _mesh_payload.LINEAR_DEFLECTION_RATIO
    drawing = Path(directory) / (target.name + ".drawing.npz")

    def items():
        for index, solid in enumerate(solids):
            vertices, triangles = writer.drawn(solid, deflection)
            yield f"V{index}", vertices
            yield f"T{index}", triangles
        yield "identity", writer.text_array(json.dumps({"names": names, "colors": colors}))

    with drawing.open("wb") as stream:
        writer.write_npz(stream, items())
    model = target.with_name(target.name + ".npz")
    _atomic_write(model, lambda path: writer.write_model(solids, path, names, colors))
    return {"target": str(target), "drawing": str(drawing),
            "root_name": assembly.name,
            "payload": not (target.with_suffix(".stl").is_file()
                            or os.environ.get("HSM_SKIP_MESH_PAYLOAD"))}


def write_assembly(export):
    """Write the existing STEP and payload from already drawn arrays."""
    import numpy as np
    from meshcad import write
    import _mesh_payload
    from _cadq_export import _atomic_write

    target = Path(export["target"])
    with np.load(export["drawing"], allow_pickle=False) as model:
        identity = json.loads(bytes(model["identity"]))
        names, colors = identity["names"], identity["colors"]
        drawn = [(model[f"V{i}"], model[f"T{i}"]) for i in range(len(names))]
    stem = target.name.split(".")[0]
    _atomic_write(target, lambda path: write.write_step(
        [(name or stem, arrays, color) for name, arrays, color in zip(names, drawn, colors)],
        path, export["root_name"] or stem))
    if export["payload"]:
        meshes = [write.drawn_payload(name, color, *arrays)
                  for name, arrays, color in zip(names, drawn, colors)]
        model = target.with_name(target.name + ".npz")
        _atomic_write(target.with_name(target.name + ".mesh"),
                      lambda path: write.write_payload(
                          meshes, path, src=_mesh_payload.source_digest(model)))


def printed_frame(assembly):
    """The shell's exact frame, using the same carried points as its graft."""
    import numpy as np

    carry = assembly.core_carry
    origin = np.array(carry(((0., 0., 0.), (0., 0., 1.)))[0])
    axes = [np.array(carry((point, (0., 0., 1.)))[0]) - origin
            for point in ((1., 0., 0.), (0., 1., 0.), (0., 0., 1.))]
    return {"rotation": np.column_stack(axes).tolist(), "translation": origin.tolist()}


def graft_printed(mesh, frame):
    """Graft the current printed surfaces in the builder's captured shell frame."""
    import numpy as np
    import flute_payload

    surfaces = flute_payload.surfaces()
    shell = surfaces.pop("foam-shell", None)
    landed = flute_payload.graft(mesh, surfaces)
    if shell is not None:
        installed = flute_payload.carried(shell, (np.asarray(frame["rotation"]),
                                                  np.asarray(frame["translation"])))
        landed += flute_payload.graft(mesh, {"foam-shell": installed}, same_frame=True)
    return landed


def prepare(assembly, target, path, *, action, module):
    """Read geometry-dependent export metadata once, while the builder is live."""
    from hardware.wiring.installed.build import prepare_enclosure
    import _facts
    import _scorecard as card
    import render_scenes

    path = Path(path)
    exports = prepare_enclosure(assembly, target, path.parent)
    module.report(assembly, card.pack_clashes(assembly))
    card.report(assembly)
    print(f"-> {card.write(assembly, Path(target)).name}")
    plan = {"schema": 1, "exports": exports,
            "facts": _facts.gather(assembly, module),
            "printed_frame": printed_frame(assembly),
            "scenes": render_scenes.describe(assembly), "require_core_payload": action}
    path.write_text(json.dumps(plan) + "\n")
    return path


def finish(path):
    """Complete files from a handoff, with no assembly reconstruction."""
    import meshcad
    meshcad.activate()
    from hardware.wiring.installed.build import finish_enclosure
    import _facts
    import _mesh_payload
    import _realized
    import render_scenes

    plan = json.loads(Path(path).read_text())
    finish_enclosure(plan["exports"])
    target = Path(plan["exports"]["physical"]["target"])
    print(f"-> {target.name}")
    mesh = target.with_name(target.name + ".mesh")
    try:
        current = (mesh.stat().st_mtime_ns >= target.stat().st_mtime_ns
                   and _mesh_payload.read_version(mesh) == _mesh_payload.VERSION)
    except Exception as exc:
        raise RuntimeError(f"{target.name} did not produce a readable mesh payload") from exc
    if not current:
        raise RuntimeError(f"{target.name} did not produce a current v{_mesh_payload.VERSION} mesh payload")
    grafted = graft_printed(mesh, plan["printed_frame"])
    if grafted:
        print(f"-> {target.name}.mesh  ({grafted} fluted piece(s))")
    facts = plan["facts"]
    facts["step"] = _realized.code_digest(_facts.STEP)
    facts["card"] = _realized.code_digest(_facts.SCORECARD)
    print(f"-> {_facts.write(facts=facts).name}")
    render_scenes.write_described_glbs(plan["scenes"],
                                      require_core_payload=plan["require_core_payload"])
