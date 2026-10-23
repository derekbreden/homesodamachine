"""Export host-trimmed stem elbows and native wall/roof study context.

Run manually through tmp/takeover/cadq. The purchased stock reference remains
unchanged; each trim leaves the selected receiving socket's full engagement.
"""
from pathlib import Path
import importlib.util
import json
import re

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


def export(name, pieces):
    out = HERE / "parts"
    out.mkdir(exist_ok=True)
    assembly = cq.Assembly(name=name)
    vertices, faces, offset = [], [], 0
    for label, shape in pieces:
        assembly.add(shape, name=label)
        v, f = shape.tessellate(.04, .12)
        v = np.array([p.toTuple() for p in v], np.float32)
        vertices.append(v)
        faces.append(np.array(f, np.int32) + offset)
        offset += len(v)
    path = out / (name + ".step")
    assembly.export(str(path))
    path.write_bytes(re.sub(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'",
                            b"'1970-01-01T00:00:00'", path.read_bytes()))
    v, f = np.vstack(vertices), np.vstack(faces)
    np.savez_compressed(out / (name + ".npz"), v=v, f=f)
    return {"valid": all(s.isValid() for _, s in pieces),
            "solid_count": sum(len(s.Solids()) for _, s in pieces),
            "bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
            "vertices": len(v), "triangles": len(f)}


def main():
    elbow = module("fold_stock_elbow", ROOT / "hardware/reference/neofit-stem-elbow/neofit_stem_elbow.py")
    trim = module("fold_stem_trim", HERE.parent / "stem-fittings/trim_stems.py")
    report = {"units": "mm", "assumption": "Stem shoulders seat flush at host mouths", "parts": {}}
    for name, depth in (("elbow-regulator", 17.), ("elbow-check", 16.1),
                        ("elbow-elbow", 16.891), ("elbow-bulkhead", 12.7)):
        pieces = [(n, p.val()) for n, p in elbow.build()]
        pieces, tip = trim.trim(pieces, elbow.stem_tip()[0], elbow.stem_shoulder()[0], depth)
        report["parts"][name] = {**export(name, pieces), "stem_remaining_mm": depth,
                                  "tip_mm": tip.tolist()}
    context = module("fold_native_context", HERE.parent / "co2-tpu/context.py")
    context.HERE = HERE
    for name, shape in context.build().items():
        report["parts"][name] = export(name, [("body", shape)])
    (HERE / "parts/build-report.json").write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
