"""Read emitted deposition in the complete back-top solid host/root modifiers.

Every region is sampled at 1 mm vertical intervals, its first two complete slabs,
and its last two complete slabs. Exact STL stock sections are compared with the
actual roads' own-width envelopes. This is deposition evidence, not a strength test.
"""
from pathlib import Path
import hashlib
import json
import math
import re
import zipfile

import numpy as np
import shapely
from shapely.geometry import LineString, box
from shapely.ops import polygonize, unary_union
import trimesh

from review_roads import layers, MODEL

ROOT = next(p for p in Path(__file__).resolve().parents if (p / "tools/docgen").is_dir())
JOB = ROOT / ".cache/prints/2026-10-07-drain/back-top-mark2"
ARCHIVE = JOB / "ready/back-top-black-z004-mark2.gcode.3mf"
PREP = JOB / "back-top-black-z004-mark2.preparation.json"


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def sections(edges):
    edges = np.round(edges[:, :, :2], 6)
    a, b = edges[:, 0], edges[:, 1]
    polygons = []
    for polygon in polygonize(unary_union([LineString(p) for p in edges])):
        point = polygon.representative_point()
        crossing = (a[:, 1] > point.y) != (b[:, 1] > point.y)
        st, en = a[crossing], b[crossing]
        x = st[:, 0] + (point.y - st[:, 1]) * (en[:, 0] - st[:, 0]) / (en[:, 1] - st[:, 1])
        if np.count_nonzero(x > point.x) % 2:
            polygons.append(polygon)
    return unary_union(polygons)


def main():
    prep = json.loads(PREP.read_text())
    part = prep["parts"][0]
    source = ROOT / part["source"]
    assert sha(source) == part["stl_sha256"]
    mesh = trimesh.load(source, force="mesh", process=True)
    assert mesh.is_watertight and mesh.is_winding_consistent
    rotation = np.array(part["build_transform"][:9]).reshape(3, 3)
    translate = np.array(part["build_transform"][9:])
    center = np.array(part["source_center_mm"])
    mesh.vertices = (mesh.vertices - center) @ rotation + translate
    triangles = mesh.triangles
    zmin, zmax = triangles[:, :, 2].min(axis=1), triangles[:, :, 2].max(axis=1)
    regions = []
    wanted = {}
    for region in prep["solid_host_regions"]:
        bounds = np.array(region["applied_machine_bounds_mm"]).reshape(3, 2)
        corners = np.array([[x, y, z] for x in bounds[0] for y in bounds[1] for z in bounds[2]])
        corners = (corners - center) @ rotation + translate
        low, high = corners.min(axis=0), corners.max(axis=0)
        valid = [n for n in range(1, 900) if low[2] <= .2 + .24*n - .24
                 and .2 + .24*n <= high[2]]
        assert valid, region["name"]
        selected = set(valid[:2] + valid[-2:])
        for station in np.arange(low[2] + .36, high[2], 1.):
            selected.add(min(valid, key=lambda n: abs(.2 + .24*n - .12 - station)))
        insert = re.fullmatch(r"Electronics host and wall root ([-.\d]+)/([-.\d]+)", region["name"])
        axis = None
        axis_layers = []
        if insert:
            y, z = map(float, insert.groups())
            axis = (np.array([0., y, z]) - center) @ rotation + translate
            nearest = min(valid, key=lambda n: abs(.2 + .24*n - .12 - axis[2]))
            axis_layers = [n for n in (nearest - 1, nearest, nearest + 1) if n in valid]
            selected.update(axis_layers)
        index = len(regions)
        regions.append({"name": region["name"], "machine_bounds_mm": bounds.flatten().tolist(),
                        "plate_bounds_mm": [low.tolist(), high.tolist()], "samples": [],
                        "insert_axis_plate_mm": axis.tolist() if axis is not None else None,
                        "insert_axis_layer_z_mm": [round(.2 + .24*n, 5) for n in axis_layers]})
        for n in selected:
            wanted.setdefault(round(.2 + .24*n, 5), []).append(index)
    with zipfile.ZipFile(ARCHIVE) as z:
        for height, slab, roads, _ in layers(z.open("Metadata/plate_1.gcode")):
            indices = wanted.get(round(height, 5))
            if not indices:
                continue
            model = [r for r in roads if r[6] == part["identify_id"] and r[7] in MODEL]
            assert model and all(r[8] in {"G0", "G1"} and r[5] == 0 for r in model)
            cut = height - slab / 2
            ids = np.flatnonzero((zmin < cut) & (zmax > cut))
            stock = sections(trimesh.intersections.mesh_plane(mesh, [0, 0, 1], [0, 0, cut], local_faces=ids))
            lines = np.array([LineString((r[:2], r[2:4])) for r in model], dtype=object)
            widths = np.array([r[4] for r in model])
            tree = shapely.STRtree(lines)
            for index in indices:
                region = regions[index]
                low, high = region["plate_bounds_mm"]
                target = stock.intersection(box(low[0], low[1], high[0], high[1]))
                if target.area <= .05:
                    continue
                hits = tree.query(target, predicate="dwithin", distance=float(widths.max()/2))
                beads = shapely.union_all(shapely.buffer(lines[hits], widths[hits]/2, quad_segs=8))
                fraction = target.intersection(beads).area / target.area
                sample = {"print_z_mm": height, "native_section_z_mm": cut,
                    "native_stock_area_mm2": target.area, "model_road_count": len(hits),
                    "own_width_bead_coverage_fraction": fraction,
                    "dense_feature_road_count": sum(model[i][7] != "Sparse infill" for i in hits),
                    "passed": fraction >= .98}
                if round(height, 5) in region["insert_axis_layer_z_mm"]:
                    # These electronics insert axes run in machine X, hence bed Y.
                    # Record the blind cap independently of the radial supplier wall.
                    # An axial 2 mm requirement is not specified for this insert.
                    x = region["insert_axis_plate_mm"][0]
                    ray = LineString(((x, low[1] - 1), (x, high[1] + 1)))
                    intervals = [s for s in shapely.get_parts(target.intersection(ray))
                                 if s.geom_type == "LineString" and s.length > .001]
                    cap = max(intervals, key=lambda s: s.bounds[3])
                    filled = [s for s in shapely.get_parts(cap.intersection(beads))
                              if s.geom_type == "LineString" and s.length > .001]
                    outside = max(filled, key=lambda s: s.bounds[3]) if filled else None
                    reach = outside.length if outside is not None else 0.
                    missed_edge = cap.bounds[3] - outside.bounds[3] if outside is not None else cap.length
                    backing = {"native_stock_blind_cap_mm": cap.length,
                               "connected_nominal_exterior_backing_mm": reach,
                               "exterior_edge_gap_mm": missed_edge,
                               "native_cap_interval_plate_y_mm": [cap.bounds[1], cap.bounds[3]],
                               "printed_cap_intervals_plate_y_mm": [[s.bounds[1], s.bounds[3]] for s in filled],
                               "scope": "Axial blind-cap deposition diagnostic; the supplier's 1.6 mm surrounding-wall rule is radial."}
                    sample["insert_axis_backing"] = backing
                region["samples"].append(sample)
            print("Dense regions", round(height, 3), flush=True)
    for region in regions:
        region["passed"] = bool(region["samples"]) and all(s["passed"] for s in region["samples"])
        region["minimum_sample_coverage_fraction"] = min((s["own_width_bead_coverage_fraction"] for s in region["samples"]), default=None)
    result = {"native_archive_sha256": sha(ARCHIVE), "source_stl_sha256": sha(source),
              "preparation_sha256": sha(PREP), "regions": regions,
              "sampling": "Every region at 1 mm vertical intervals and first/last two complete emitted slabs; electronics insert axes also use the nearest three complete slabs. Whole native STL sections at each slab's mid-height are clipped to the applied modifier box. Actual model roads use their own nominal width. At each sampled insert height, the exterior blind-cap intervals and edge gap are recorded independently of the radial supplier wall rule.",
              "diagnostic_coverage_threshold": .98,
              "scope": "Nominal sampled deposition and location of the 23 solid host/root regions. No measured density, bond strength, load capacity, pullout or lifetime is established.",
              "passed": all(r["passed"] for r in regions)}
    (JOB / "dense-region-review.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"passed": result["passed"], "minimum_coverage": min(r["minimum_sample_coverage_fraction"] for r in regions),
                      "failed_regions": [r["name"] for r in regions if not r["passed"]]}, indent=2), flush=True)


if __name__ == "__main__":
    main()
