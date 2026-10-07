"""Read the named installed assembly once for independent bay-layout queries."""
from pathlib import Path
import hashlib
import json
import re
import gzip
import os

# Study tools read production shape functions and emit only private study
# artifacts. They do not own the production CAD export/build lock.
os.environ.setdefault('HSM_NO_BUILD_LOCK','1')

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CACHE = ROOT / ".cache/pump-first-layout/baseline"
SOURCE = CACHE / 'frozen-enclosure-assembly.step'

def frozen_source(name):
    """Materialize the content-addressed study input, independent of live CAD."""
    manifest=json.loads((HERE/'inputs/baseline.json').read_text())
    record=manifest[name];target=CACHE/('frozen-'+name)
    CACHE.mkdir(parents=True,exist_ok=True)
    if target.exists() and digest(target)==record['sha256']:return target
    raw=gzip.decompress((ROOT/record['snapshot']).read_bytes())
    assert hashlib.sha256(raw).hexdigest()==record['sha256']
    target.write_bytes(raw)
    return target


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def prepare():
    CACHE.mkdir(parents=True, exist_ok=True)
    frozen_source('enclosure-assembly.step')
    index = CACHE / "index.json"
    source_hash = digest(SOURCE)
    if index.exists():
        saved = json.loads(index.read_text())
        if saved.get("sha256") == source_hash:
            return saved
    assembly = cq.Assembly.load(str(SOURCE))
    groups = {}

    def visit(node, parent=None):
        loc = node.loc if parent is None else parent * node.loc
        if node.obj is not None:
            values = node.obj.vals() if hasattr(node.obj, "vals") else [node.obj]
            name = re.sub(r"/\d+$", "", node.name)
            groups.setdefault(name, []).extend(v.moved(loc) for v in values)
        for child in node.children:
            visit(child, loc)

    visit(assembly)
    parts = {}
    for i, (name, shapes) in enumerate(groups.items()):
        shape = cq.Compound.makeCompound(shapes)
        filename = f"{i:03d}.brep"
        shape.exportBrep(str(CACHE / filename))
        box = shape.BoundingBox()
        parts[name] = {"file": filename, "bounds": [box.xmin, box.ymin, box.zmin,
                                                  box.xmax, box.ymax, box.zmax]}
    saved = {"source": str(SOURCE.relative_to(ROOT)), "sha256": source_hash,
             "parts": parts}
    index.write_text(json.dumps(saved, indent=2) + "\n")
    return saved


def read(names=None):
    saved = prepare()
    return {name: cq.Shape.importBrep(str(CACHE / part["file"]))
            for name, part in saved["parts"].items()
            if names is None or name in names}


if __name__ == "__main__":
    result = prepare()
    print(f"{len(result['parts'])} named bodies: {CACHE}", flush=True)
    print("\n".join(result["parts"]), flush=True)
