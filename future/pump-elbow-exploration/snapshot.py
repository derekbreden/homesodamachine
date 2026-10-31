"""Capture the installed machine once for bounded elbow/layout exploration.

The cache is local working data. It is not an assembly producer or build check.
Run from the repository root with tools/cad-venv/bin/python.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / ".cache/pump-elbow-exploration/world"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
# CadQuery before probe: the capture is native B-reps, so this process stays on OCCT's kernel
# and builds its world rather than reading the mesh scene.
import cadquery  # noqa: F401
import probe


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    w = probe.world()
    print(w.measured, flush=True)
    bodies = {}
    for name in w.names:
        shape = w.solid(name)
        b = w.bb(name)
        path = CACHE / f"{name}.brep"
        if not hasattr(shape, "exportBrep"):
            raise TypeError(f"{name}: snapshot requires its native B-rep")
        shape.exportBrep(str(path))
        bodies[name] = {
            "bounds_mm": [b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax],
            "role": w.sources[name],
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
    frames = {
        name: {
            p: {"position_mm": f.at(p), "axis": f.normal(p), "diameter_mm": f.diam(p)}
            for p in f.ports
        }
        for name, f in w.frames().items()
    }
    routes = {
        name: {
            "from": r.frm, "to": r.to, "points_mm": r.pts,
            "diameter_mm": r.diam, "kind": r.kind, "radius_mm": r.tightest,
            "length_mm": r.length,
        }
        for name, r in w.runs.items()
    }
    sources = {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted((ROOT / "hardware").rglob("*.py"))
    }
    data = {"scope": w.measured, "bodies": bodies, "frames": frames,
            "routes": routes, "source_sha256": sources}
    (CACHE / "world.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"Saved {len(bodies)} bodies and {len(frames)} port frames", flush=True)


if __name__ == "__main__":
    main()
