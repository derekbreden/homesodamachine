"""Ask once about the local installed TPU/direct-metal assembly occupancy."""
from pathlib import Path
import json

import fcl
import numpy as np

import model

HERE = Path(__file__).resolve().parent


def collision_object(v, f):
    bvh = fcl.BVHModel()
    bvh.beginModel(len(v), len(f))
    bvh.addSubModel(v.astype(float), f.astype(np.int32))
    bvh.endModel()
    return fcl.CollisionObject(bvh)


def main():
    records = model.direct_instances(include_metals=True)
    meshes = model.world_meshes(records)
    objects = {n: collision_object(*m) for n, m in meshes.items()}
    intended = {frozenset((m["a"], m["b"])) for m in model.mates()}
    pairs, unexpected = [], []
    for i, a in enumerate(objects):
        for b in list(objects)[i+1:]:
            overlap = bool(fcl.collide(objects[a], objects[b], fcl.CollisionRequest(), fcl.CollisionResult()))
            expected = frozenset((a, b)) in intended
            d = float(fcl.distance(objects[a], objects[b], fcl.DistanceRequest(), fcl.DistanceResult()))
            pairs.append({"a": a, "b": b, "intended_contact": expected,
                          "surface_intersection": overlap, "distance_mm": d})
            if overlap and not expected:
                unexpected.append([a, b])
    ports = model.direct_ports()
    data = model.interfaces()
    all_v = np.vstack([v for v, _ in meshes.values()])
    tube_bands = [n for n in objects if n.endswith("-band-tube")]
    cuff_bands = [n for n in objects if n.endswith("-band-cuff")]
    result = {
        "scope": "One-time local installed TPU/band/metal occupancy query; no enclosure or gas-performance claim",
        "parts": [r["name"] for r in records],
        "bounds_mm": [all_v.min(0).tolist(), all_v.max(0).tolist()],
        "size_xyz_mm": np.ptp(all_v, axis=0).tolist(),
        "tube_ports_in_direct_assembly": ports,
        "all_native_models_valid": all(row["valid_native_solid"] for row in data["geometry"].values()),
        "all_native_models_single_solid": all(row["native_solid_count"] == 1 for row in data["geometry"].values()),
        "unintended_pair_intersections": unexpected,
        "minimum_cuff_to_tube_band_distance_mm": min(
            float(fcl.distance(objects[a], objects[b], fcl.DistanceRequest(), fcl.DistanceResult()))
            for a in cuff_bands for b in tube_bands),
        "pairs": pairs,
        "limits": [
            "Threaded metal pair, matched installed cuffs and bands are intended contacts. Their coincident or display surfaces do not establish a mechanical or sealing result.",
            "The closed rings omit clamp housing/screw/key occupancy. Metal-cuff bands need larger ranges than the owned10–16mm tube clamps.",
            "Installed diameters use the pump model's annular-area approximation. New metal cuff interference and contact length remain estimates.",
        ],
    }
    (HERE / "audit.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({k: v for k, v in result.items() if k in [
        "size_xyz_mm", "tube_ports_in_direct_assembly", "all_native_models_valid",
        "all_native_models_single_solid", "unintended_pair_intersections",
        "minimum_cuff_to_tube_band_distance_mm"]}, indent=2))


if __name__ == "__main__":
    main()
