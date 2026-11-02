"""The under-sink instruction scenes as Rust-kernel illustration geometry."""
from __future__ import annotations

import json
from pathlib import Path
import tempfile

from _materials import linear
from _cadq_export import note_read, note_write
import _rust_part


def export(module, names, directory, *, modern=False):
    """Export the caller's existing named states and its exact instruction palette."""
    colors = {name: list(linear(value)) for name, value in vars(module).items()
              if name.startswith("C_")}
    dimensions = {name: value for name, value in vars(module).items()
                  if name.isupper() and not name.startswith("C_")
                  and (isinstance(value, (int, float))
                       or isinstance(value, tuple)
                       and all(isinstance(item, (int, float)) for item in value))}
    spec = {"kind": "modern" if modern else "legacy", "names": list(names),
            "dimensions": dimensions}
    if modern:
        union = module.union_ref
        note_read(union.PAYLOAD_PATH)
        spec["union"] = {"payload": str(union.PAYLOAD_PATH.relative_to(module.ROOT)),
                         "ring_start": union.ring_face_z, "ring_end": union.port_face_z,
                         "collet_d": union.COLLET_D, "collet_bore": union.COLLET_BORE}
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".plumbing-props-", dir=module.HERE) as temporary:
        path = Path(temporary) / "numbers.json"
        path.write_text(json.dumps({"plumbing_art": spec, "colors": colors}, sort_keys=True)+"\n")
        for line in _rust_part.run("tooling", "install-art-props", path, directory).splitlines():
            if line.strip():
                for name in json.loads(line)["files"]:
                    note_write(directory / name)
    return {name: directory / f"{name}.step" for name in names}
