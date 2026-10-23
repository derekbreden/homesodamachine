"""The stacked elbow's male end, cut for its NeoFit receiving socket.

Run through the serial CAD queue. The valve-side elbow uses the existing
12.7 mm stem study model; this elbow requires 16.891 mm in the other elbow.
"""
from pathlib import Path
import importlib.util
import json
import re

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent


def load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main():
    trim = load(HERE.parent / "stem-fittings/trim_stems.py", "lowered_trim")
    elbow = trim.load("neofit-stem-elbow/neofit_stem_elbow.py", "lowered_elbow")
    pieces = [(n, p.val()) for n, p in elbow.build()]
    pieces, tip = trim.trim(pieces, elbow.stem_tip()[0], elbow.stem_shoulder()[0], 16.891)
    assembly = cq.Assembly(name="stacked-stem-elbow")
    vertices, faces, offset = [], [], 0
    for name, shape in pieces:
        if not shape.isValid():
            raise ValueError(f"Invalid cut elbow: {name}")
        assembly.add(shape, name=name)
        v, f = shape.tessellate(.04, .12)
        v = np.asarray([p.toTuple() for p in v], dtype=np.float32)
        f = np.asarray(f, dtype=np.uint32)
        vertices.append(v); faces.append(f + offset); offset += len(v)
    out = HERE / "parts"; out.mkdir(exist_ok=True)
    path = out / "stem-elbow-neofit-host.step"
    assembly.export(str(path))
    path.write_bytes(re.sub(rb"'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}'",
                            b"'1970-01-01T00:00:00'", path.read_bytes()))
    np.savez_compressed(out / "stem-elbow-neofit-host.npz", v=np.vstack(vertices), f=np.vstack(faces))
    record = {"source": "../../../../reference/neofit-stem-elbow/neofit_stem_elbow.py",
              "units": "mm", "receiving_host": "NeoFit stem elbow female socket",
              "remaining_stem_mm": 16.891, "removed_mm": elbow.STEM_LENGTH - 16.891,
              "native_tip_mm": tip.tolist(), "native_shoulder_mm": list(elbow.stem_shoulder()[0]),
              "assumption": "Square-cut stem, shoulder flush at receiving mouth", "valid": True}
    (out / "dimensions.json").write_text(json.dumps(record, indent=2) + "\n")
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
