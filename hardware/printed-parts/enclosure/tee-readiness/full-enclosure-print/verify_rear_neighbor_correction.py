"""Recheck the retained rear correction solids without building the enclosure.

This reads exact archived native bodies and the corresponding source records.
It does not regenerate or qualify an altered live enclosure source tree.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import tempfile
import time
import zipfile
import cadquery as cq

HERE = Path(__file__).resolve().parent


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bounds(shape):
    b = shape.BoundingBox()
    return (b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax)


def box_gap(a, b):
    return math.sqrt(sum(max(0.0, a[k] - b[k + 3], b[k] - a[k + 3]) ** 2
                         for k in range(3)))


def pair_read(a, b):
    """Exact closest native distance, pruning only by a proven box lower bound."""
    ab = bounds(a)
    ordered = sorted(((box_gap(ab, bounds(s)), s) for s in b.Solids()),
                     key=lambda row: row[0])
    best, overlap, tested = float("inf"), 0.0, 0
    for lower, solid in ordered:
        if lower > best:
            continue
        tested += 1
        volume = abs(a.intersect(solid).Volume()) if lower < 1e-7 else 0.0
        overlap += volume
        best = min(best, 0.0 if volume > 1e-8 else a.distance(solid))
    return {"overlap_mm3": overlap, "air_mm": best, "native_components_tested": tested}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path,
                        default=HERE / "rear-neighbor-correction-inputs.zip")
    parser.add_argument("--out", type=Path,
                        default=HERE / "rear-neighbor-native-recheck.json")
    args = parser.parse_args()
    start = time.monotonic()
    archive_bytes = args.archive.read_bytes()
    with zipfile.ZipFile(args.archive) as archive, tempfile.TemporaryDirectory() as td:
        manifest = json.loads(archive.read("manifest.json"))
        objects = {}
        for name, row in manifest["objects"].items():
            data = archive.read(row["member"])
            assert digest(data) == row["sha256"], name
            target = Path(td) / (name + ".brep")
            target.write_bytes(data)
            objects[name] = cq.Shape.importBrep(str(target))
            assert objects[name].isValid(), name
        readings = []
        for case in manifest["pairs"]:
            row = {**case, **pair_read(objects[case["a"]], objects[case["b"]])}
            row["pass"] = (row["overlap_mm3"] <= case["maximum_overlap_mm3"]
                           and row["air_mm"] >= case["minimum_air_mm"] - 1e-6
                           and abs(row["air_mm"] - case["expected_air_mm"]) < 1e-5)
            readings.append(row)
            print(case["a"], case["b"], row["pass"], row["air_mm"], flush=True)
        bearings = []
        foam = objects["foam-assembly"]
        for row in manifest["bearing_probes"]:
            b = row["bounds_mm"]
            probe = cq.Solid.makeBox(b[3] - b[0], b[4] - b[1], b[5] - b[2],
                                     cq.Vector(*b[:3]))
            volume = sum(abs(probe.intersect(s).Volume()) for s in foam.Solids()
                         if box_gap(bounds(probe), bounds(s)) < 1e-6)
            bearings.append({"bounds_mm": b, "coverage_fraction": volume / probe.Volume(),
                             "pass": abs(volume - row["probe_volume_mm3"]) < 1e-6})
        c14 = manifest["c14_bound"]
        c14_air = box_gap(c14["c14_bounds_mm"], bounds(objects["flavor-b"]))
        result = {
            "status": "retained_native_recheck_pass" if all(r["pass"] for r in readings + bearings)
                      else "retained_native_recheck_fail",
            "scope": "Frozen native correction evidence; no live-source regeneration or whole-shell release.",
            "archive_sha256": digest(archive_bytes),
            "reproducer_sha256": digest(Path(__file__).read_bytes()),
            "pair_readings": readings,
            "bearing_readings": bearings,
            "c14_distance_lower_bound_mm": c14_air,
            "elapsed_seconds": time.monotonic() - start,
        }
    args.out.write_text(json.dumps(result, indent=2) + "\n")
    assert result["status"] == "retained_native_recheck_pass", args.out
    print(result["status"], len(readings), "pairs", len(bearings), "bearings", flush=True)


if __name__ == "__main__":
    main()
