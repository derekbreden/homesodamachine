"""Replay the bounded fluid-14 clearance evidence without building the assembly.

Default: check the saved native fore-bend witness and execute the exact recorded
production guard against both routes. --full also repeats the 210-body bounding
prefilter and all 24 nearby surface queries. Nothing is written to production.
"""

from pathlib import Path
import argparse
import ast
import hashlib
import json
import math
import os
import sys
import tempfile
from types import SimpleNamespace
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / "tools/cad-venv").is_dir())
os.environ["HSM_NO_BUILD_LOCK"] = "1"
sys.path[:0] = [str(ROOT / "hardware/scripts"), str(ROOT / "hardware/manifold-layout")]

import cadquery as cq
import _clearing
import _meshes
import _routing as R


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def box_gap(a, b):
    return math.sqrt(sum(max(0.0, a[k] - b[k + 3], b[k] - a[k + 3]) ** 2
                         for k in range(3)))


def recorded_guard(source, tube, solids):
    tree = ast.parse(source)
    fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef)
              and n.name == "_fluid_14")
    loop = next(n for n in fn.body if isinstance(n, ast.For)
                and isinstance(n.iter, ast.Tuple)
                and ast.literal_eval(n.iter) == ("valve-v-a", "vk-solenoid"))
    program = ast.fix_missing_locations(ast.Module(body=[loop], type_ignores=[]))
    env = {"tube": tube, "solids": solids, "clearance": _clearing.gap,
           "_card": SimpleNamespace(REPORT_NEAR=2.0, CLEARANCE_FLOOR=1.0)}
    try:
        exec(compile(program, "recorded _fluid_14 guard", "exec"), env)
    except ValueError as exc:
        return {"accepted": False, "error": str(exc)}
    return {"accepted": True}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--full", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    review = json.loads((HERE / "review.json").read_text())
    archive = HERE / "native-inputs.zip"
    assert sha(archive) == review["archive_sha256"]
    for relative, digest in review["query_source_sha256"].items():
        assert sha(ROOT / relative) == digest, f"query implementation changed: {relative}"
    with tempfile.TemporaryDirectory(prefix="fluid14-evidence-") as tmp:
        directory = Path(tmp)
        with zipfile.ZipFile(archive) as z:
            for name in z.namelist():
                assert Path(name).name == name, "only flat evidence members are allowed"
            z.extractall(directory)
        for name, digest in review["archive_members_sha256"].items():
            assert sha(directory / name) == digest, name
        manifest = json.loads((directory / "manifest.json").read_text())
        tube = cq.Shape.importBrep(str(directory / "candidate-fall-advance-4.brep"))
        former = cq.Shape.importBrep(str(directory / "tube-fluid-14.brep"))
        valve = cq.Shape.importBrep(str(directory / "valve-v-a.brep"))
        vk = cq.Shape.importBrep(str(directory / "vk-solenoid.brep"))
        solids = {"valve-v-a": valve, "vk-solenoid": vk}
        former_source = (directory / "lines-before.txt").read_text()
        current_source = (directory / "lines-current.txt").read_text()
        guards = {
            "former_guard_former_route": recorded_guard(former_source, former, solids),
            "current_guard_former_route": recorded_guard(current_source, former, solids),
            "current_guard_corrected_route": recorded_guard(current_source, tube, solids),
        }
        assert guards["former_guard_former_route"]["accepted"]
        assert not guards["current_guard_former_route"]["accepted"]
        assert guards["current_guard_corrected_route"]["accepted"]
        point = cq.Vertex.makeVertex(*review["native_witness"]["point_mm"])
        witness = {
            "point_to_former_tube_mm": point.distance(former),
            "point_to_actual_valve_mm": point.distance(valve),
            "former_whole_shape_distance_mm": former.distance(valve),
            "former_production_mesh_gap_mm": _clearing.gap(former, valve, 2.0),
            "corrected_production_mesh_gap_mm": _clearing.gap(tube, valve, 2.0),
        }
        # A point within three microns of the native tube has less than 0.89 mm
        # to the native valve. This independently rejects a tessellation-only cause.
        assert witness["point_to_former_tube_mm"] < 0.003
        assert witness["point_to_actual_valve_mm"] < 0.89
        assert witness["former_whole_shape_distance_mm"] > 1.0
        assert witness["former_production_mesh_gap_mm"] < 1.0
        assert witness["corrected_production_mesh_gap_mm"] >= 1.0
        result = {"status": "pass", "scope": "native witness and exact source guard",
                  "guards": guards, "native_witness": witness}
        if args.full:
            saved = json.loads((HERE / "candidate-clearance.json").read_text())
            seed = json.loads((directory / "route-seed.json").read_text())
            run = R.Run("fluid-14", "fluid", "valve-v-f.outlet",
                        "foam-assembly.reservoir-a-fill", seed["waypoints_mm"], 6.35, 14.0)
            points = list(run.pts)
            points[4] = (points[4][0], points[4][1] - 4.0, points[4][2])
            run = R.redrawn(run, points)
            assert max(abs(a - b) for p, q in zip(run.pts, saved["waypoints"])
                       for a, b in zip(p, q)) < 1e-9
            assert run.tightest >= 14.0 - 1e-6
            tangents = {i: run.radii[i] * math.tan(math.radians(turn) / 2.0)
                        for i, turn, *_ in run.bends}
            straight = [run.pts[6][1] + tangents[6], run.pts[7][1] - tangents[7]]
            assert straight[0] <= 254.4 and straight[1] >= 263.2
            bounds = tube.BoundingBox()
            tb = [bounds.xmin, bounds.ymin, bounds.zmin,
                  bounds.xmax, bounds.ymax, bounds.zmax]
            rows = []
            for name, body in manifest["bodies"].items():
                if name == "tube-fluid-14" or box_gap(tb, body["bounds"]) >= 2.0:
                    continue
                if name == "valve-v-f":
                    rows.append({"name": name, "checked": False,
                                 "reason": "own starting collet"})
                    continue
                shape = cq.Shape.importBrep(str(directory / body["brep"]))
                air = _clearing.gap(tube, shape, 2.0)
                overlap = (0.0 if box_gap(tb, body["bounds"]) > 0 else
                           abs((_meshes.meshed(tube) ^ _meshes.meshed(shape)).volume()))
                if name == "cold-core/foam-cap-lid-top":
                    native_air = tube.distance(shape)
                    assert native_air >= 0.15 - 2e-6
                    expected = "0.15 mm intentional full lid bearing air"
                elif name == "cold-core/line-reservoir-a-fill":
                    native_air = None
                    expected = "own reservoir fill endpoint"
                else:
                    native_air = None
                    expected = "at least 1 mm"
                    assert air >= 1.0 - 1e-6, (name, air)
                assert overlap < 1e-5, (name, overlap)
                rows.append({"name": name, "mesh_air_mm": air,
                             "mesh_overlap_mm3": overlap, "requirement": expected,
                             "native_air_mm": native_air, "pass": True})
            assert len(rows) == 25
            fine_gap = _meshes.meshed(tube, .005).min_gap(_meshes.meshed(valve, .005), 2.0)
            assert fine_gap >= 1.0
            result.update(scope="native witness, exact source guard and bounded neighbor replay",
                          neighbors=rows, bearing_straight_mm=straight,
                          minimum_radius_mm=run.tightest, fine_mesh_valve_air_mm=fine_gap)
        output = json.dumps(result, indent=2) + "\n"
        if args.output:
            args.output.write_text(output)
        print(output, end="")


if __name__ == "__main__":
    main()
