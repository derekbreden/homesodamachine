"""Frozen retained wet neighbors and two illustrative farther-forward PCBs.

All meshes are source-world NPZ snapshots. Only the board and its carried
connections move between the two diagnostic poses. No production CAD imports.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
spec = importlib.util.spec_from_file_location("forward_pcb_connections", HERE.parent / "connections/model.py")
connection_model = importlib.util.module_from_spec(spec)
spec.loader.exec_module(connection_model)


def _read(name):
    return json.loads((HERE / name).read_text())


def library():
    """Return ``forward-*`` meshes plus the carried connection library."""
    result = connection_model.library()
    for path in sorted((HERE / "parts").glob("*.npz")):
        with np.load(path) as data:
            result["forward-" + path.stem] = data["v"], data["f"]
    return result


def obstacles():
    """Return unchanged retained front wet-part instances."""
    return copy.deepcopy(_read("pose.json")["obstacles"])


def ghost(height="low"):
    """Return the Z257 or Z316 board-underside diagnostic pose."""
    return copy.deepcopy(_read("pose.json")["ghosts"][height])


def connections(height="low", *, probes=False):
    """Return the ghost's active plugs/leads and optional access probes."""
    rows = connection_model.instances({"pcba": ghost(height)},
                                      owners={"pcba"}, probes=probes)
    for row in rows:
        row["name"] = "forward-" + height + "-" + row["name"]
        row["ghost"] = True
    return rows


def _world(instance, geometries):
    v, f = geometries[instance["geometry"]]
    r = np.array(instance.get("rotation", np.eye(3)), float)
    t = np.array(instance.get("translation", [0, 0, 0]), float)
    return v @ r.T + t, f


def _default_obstacles(geometries):
    result = {m["name"]: _world(m, geometries) for m in obstacles()}
    for row in _read("query-context.json")["instances"]:
        with np.load(ROOT / row["source_npz"]) as data:
            v, f = data["v"], data["f"]
        r, t = np.array(row["rotation"]), np.array(row["translation"])
        result[row["name"]] = v @ r.T + t, f
    return result


def query(height="low", *, obstacle_meshes=None):
    """Manually query this board/connection pose against supplied world meshes.

    The default small context is recorded in query-context.json. Access probes
    are reported separately from installed geometry. This is a surface
    intersection query, not a claim of complete assembly or service access.
    """
    import fcl

    def object_for(mesh):
        v, f = mesh
        model = fcl.BVHModel()
        model.beginModel(len(v), len(f))
        model.addSubModel(v, f.astype(np.int32))
        model.endModel()
        return fcl.CollisionObject(model)

    geometries = library()
    if obstacle_meshes is None:
        obstacle_meshes = _default_obstacles(geometries)
    objects = {n: object_for(m) for n, m in obstacle_meshes.items()}
    bounds = {n: (v.min(0), v.max(0)) for n, (v, _) in obstacle_meshes.items()}
    board = ghost(height)
    rows = [board] + connections(height, probes=True)
    hits = []
    for row in rows:
        mesh = _world(row, geometries)
        v, _ = mesh
        lo, hi = v.min(0), v.max(0)
        obj = object_for(mesh)
        category = "board" if row is board else "access" if row["kind"] == "probe" else "installed"
        for name, other in objects.items():
            low, high = bounds[name]
            if np.any(np.minimum(hi, high) - np.maximum(lo, low) < .001):
                continue
            result = fcl.CollisionResult()
            if fcl.collide(obj, other, fcl.CollisionRequest(num_max_contacts=1, enable_contact=True), result):
                hits.append({"part": row["name"], "category": category, "obstacle": name,
                             "witness_mm": result.contacts[0].pos.tolist() if result.contacts else None})
    v, _ = _world(board, geometries)
    return {"height": height, "pose": board,
            "board_bounds_mm": [v.min(0).tolist(), v.max(0).tolist()],
            "physical_interferences": [h for h in hits if h["category"] != "access"],
            "access_interferences": [h for h in hits if h["category"] == "access"],
            "obstacles_queried": sorted(obstacle_meshes)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Run the two selected manual mesh queries")
    args = parser.parse_args()
    if args.check:
        report = {"scope": "Two specified forward board poses against frozen retained wet neighbors and the recorded funnel/frame/WAGO/ceiling context",
                  "units": "mm", "unused_J8_included": False,
                  "cases": [query("low"), query("high")]}
        (HERE / "checks.json").write_text(json.dumps(report, indent=2) + "\n")
        for row in report["cases"]:
            print(row["height"], "physical:", sorted({h["obstacle"] for h in row["physical_interferences"]}),
                  "access:", sorted({h["obstacle"] for h in row["access_interferences"]}))


if __name__ == "__main__":
    main()
