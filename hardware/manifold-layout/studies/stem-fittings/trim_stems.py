"""Square-cut the reference stems for the flush-shoulder layout assumption.

Run through cadq. Output is local to this study; stock reference models retain
their full purchased-part dimensions. All dimensions are millimetres.
"""
from pathlib import Path
import importlib.util
import json
import re

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REF = ROOT / "hardware/reference"


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, REF / path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trim(pieces, tip, shoulder, insertion):
    tip, shoulder = np.array(tip), np.array(shoulder)
    direction = (tip - shoulder) / np.linalg.norm(tip - shoulder)
    new_tip = shoulder + direction * insertion
    axis = int(np.argmax(np.abs(direction)))
    compound = cq.Compound.makeCompound([s for n, s in pieces])
    bb = compound.BoundingBox()
    low = np.array([bb.xmin, bb.ymin, bb.zmin]) - 1
    high = np.array([bb.xmax, bb.ymax, bb.zmax]) + 1
    if direction[axis] > 0:
        low[axis] = new_tip[axis]
    else:
        high[axis] = new_tip[axis]
    cutter = cq.Solid.makeBox(*(high - low), cq.Vector(*low))
    return [(n, s.cut(cutter).clean()) for n, s in pieces], new_tip


def main():
    elbow = load("neofit-stem-elbow/neofit_stem_elbow.py", "trim_source_elbow")
    run = load("neofit-stem-run-tee/neofit_stem_run_tee.py", "trim_source_run")
    branch = load("branch-stem-tees/branch_stem_tees.py", "trim_source_branch")
    specs = [
        ("stem-elbow", [(n, p.val()) for n, p in elbow.build()],
         elbow.stem_tip()[0], elbow.stem_shoulder()[0], 12.7, "V-K or check socket"),
        ("run-stem", [("body", run.build())], run.ports()["run_stem"]["position_mm"],
         run.ports()["run_stem"]["shoulder_mm"], 16.891, "NeoFit elbow socket"),
    ]
    for name, key in [("neofit-branch", "neofit"), ("jg-branch", "john-guest")]:
        stem = branch.stations(key)["branch_stem"]
        specs.append((name, [("body", branch.build(key))], stem["position"],
                      stem["shoulder"], 15.0, "ASSE TPU outlet socket"))
    out = HERE / "trimmed"; out.mkdir(exist_ok=True)
    record = {"assumption": "Stems may be square-cut so their shoulders meet the receiving socket mouths",
              "units": "mm", "models": {}}
    for name, pieces, tip, shoulder, insertion, host in specs:
        pieces, new_tip = trim(pieces, tip, shoulder, insertion)
        assembly = cq.Assembly(name=name + "-trimmed")
        vertices, faces, offset, solids = [], [], 0, 0
        for label, shape in pieces:
            if not shape.isValid():
                raise ValueError(f"Invalid trimmed solid: {name}/{label}")
            solids += len(shape.Solids())
            assembly.add(shape, name=label)
            v, f = shape.tessellate(.04, .12)
            v = np.asarray([p.toTuple() for p in v], dtype=np.float32)
            f = np.asarray(f, dtype=np.uint32)
            vertices.append(v); faces.append(f + offset); offset += len(v)
        path = out / (name + ".step")
        assembly.export(str(path))
        path.write_bytes(re.sub(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'",
                                b"'1970-01-01T00:00:00'", path.read_bytes()))
        np.savez_compressed(out / (name + ".npz"), v=np.vstack(vertices), f=np.vstack(faces))
        record["models"][name] = {"host": host, "remaining_stem_mm": insertion,
            "removed_mm": float(np.linalg.norm(np.array(tip) - shoulder) - insertion),
            "native_tip_mm": new_tip.tolist(), "native_shoulder_mm": list(shoulder),
            "valid": True, "solid_count": solids}
    (out / "dimensions.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
