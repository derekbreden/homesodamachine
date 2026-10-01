"""Materialize the bottom halves with full-thickness handhold wall ends."""
from pathlib import Path
import hashlib
import json
import os
import sys
import time

import cadquery as cq

HERE = Path(__file__).resolve().parent
ENC = HERE.parent
ROOT = next(p for p in HERE.parents if (p / "tools").is_dir())
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ENC)]
import enclosure as e
import _box_spec
import flute_payload
from materialize_pump_cartridge import _declared_box


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    box, bounds, box_path = _declared_box(_box_spec, e)
    e.BOUNDS[:] = bounds
    e._last_box[0] = box
    pieces, cache = {}, {}
    started = time.monotonic()
    for name in ("front-bottom", "back-bottom"):
        pieces[name] = e.build_piece(box, *name.split("-"), halves_cache=cache)
        solid = pieces[name].val()
        assert solid.isValid() and len(solid.Solids()) == 1, name
        print(name, "built", round(time.monotonic()-started, 1), "seconds", flush=True)
    for name in e.PIECE_COLORS:
        if name not in pieces:
            pieces[name] = cq.importers.importStep(str(ENC / f"enclosure-{name}.step"))
    bodies = {name:e._piece_mesh(part.val()) for name,part in pieces.items()}
    steel = [e._piece_mesh(e._collet_plate_body(box.pack.collet_plate))]
    output = {}
    for name in ("front-bottom", "back-bottom"):
        path = ENC / f"enclosure-{name}.step"
        os.environ["HSM_SKIP_MESH_PAYLOAD"] = "1"
        e.export_assembly(e.one_body(pieces[name],f"enclosure-{name}",e.PIECE_COLORS[name]),str(path))
        os.environ.pop("HSM_SKIP_MESH_PAYLOAD", None)
        rails = e.flute_rails(box, [m for n,m in bodies.items() if n != name]+steel)
        mesh = e._flute_skin.flute(bodies[name],rails,e.flute_pitch(box.outer),e.flute_depth,e.flute_rise)
        if name == "back-bottom":
            # Match the full producer: restore the raised outlines after the
            # flute cutter closes outside the smooth lettering field.
            letters=e._piece_mesh(e.disposal_letters(box.outer))
            mesh=e.trimesh.boolean.union(
                [e._flute_skin.as_written(mesh),e._flute_skin.as_written(letters)],
                engine="manifold",check_volume=False)
            mesh=e.trimesh.boolean.union(
                [e._flute_skin.as_written(mesh)],engine="manifold",check_volume=False)
        mesh.export(str(path.with_suffix(".stl")))
        printed = e.trimesh.load_mesh(path.with_suffix(".stl"))
        assert printed.is_watertight and printed.is_winding_consistent, name
        assert not e._flute_skin.non_manifold_edges(printed), name
        flute_payload.cut(path,path.with_suffix(".stl"))
        output[name] = {p.name:sha(p) for p in (path,path.with_suffix(".stl"),path.with_suffix(".step.mesh"))}
        print(name, "exported", round(time.monotonic()-started, 1), "seconds", flush=True)
    sources = {Path(__file__),box_path}
    for module in tuple(sys.modules.values()):
        path = getattr(module,"__file__",None)
        if path and str(path).endswith(".py"):
            path = Path(path).resolve()
            if path.is_relative_to(ROOT) and "site-packages" not in str(path):
                sources.add(path)
    report = {"outputs":output,"box":str(box_path.relative_to(ROOT)),
              "source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sorted(sources)},
              "scope":"Production front-bottom and back-bottom with square 3 mm handhold wall ends."}
    (HERE/"generation.json").write_text(json.dumps(report,indent=2)+"\n")


if __name__ == "__main__":
    main()
