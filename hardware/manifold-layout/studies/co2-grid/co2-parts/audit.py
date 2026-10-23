"""One-time manual envelope/source question for the frozen CO2 hardware."""
from pathlib import Path
import hashlib
import json

import fcl
import numpy as np
import trimesh

import model

HERE = Path(__file__).resolve().parent


def collision_object(vertices, faces):
    bvh = fcl.BVHModel()
    bvh.beginModel(len(vertices), len(faces))
    bvh.addSubModel(vertices.astype(float), faces.astype(np.int32))
    bvh.endModel()
    return fcl.CollisionObject(bvh)


def main():
    evidence = model.evidence()
    records = model.direct_instances()
    meshes = model.world_meshes(records)
    envelope = np.vstack([v for v, _ in meshes.values()])
    tube_ports = model.direct_ports()
    frames = evidence["canonical_frames_to_original_world"]
    source_reconstruction = {}
    for name, row in evidence["authored_meshes"].items():
        with np.load(HERE / row["snapshot"]) as data:
            native = data["v"]
        pose = frames[row["coordinate_group"]]
        reconstructed = native @ np.array(pose["rotation"]).T + pose["translation_mm"]
        bb = np.array([reconstructed.min(0), reconstructed.max(0)])
        source_reconstruction[name] = float(np.max(np.abs(bb - row["source_world_bounds_mm"])))

    cap = model.cap_handoff()
    cross = cap["cross_check"]
    cap_calc = (np.array(cross["core_to_world_rotation"]) @
        np.array([*cross["core_native_after_cap_half_turn_xy_mm"], cross["core_native_cap_face_z_mm"]])
        + cross["core_to_world_translation_mm"])
    intended = {frozenset((row["a"], row["b"])) for row in model.mates()}
    objects = {n: collision_object(*mesh) for n, mesh in meshes.items()}
    pairs, unintended = [], []
    for i, a in enumerate(objects):
        for b in list(objects)[i+1:]:
            contact = bool(fcl.collide(objects[a], objects[b], fcl.CollisionRequest(), fcl.CollisionResult()))
            expected = frozenset((a, b)) in intended
            distance = float(fcl.distance(objects[a], objects[b], fcl.DistanceRequest(), fcl.DistanceResult()))
            row = {"a": a, "b": b, "intended_thread_mate": expected,
                   "triangle_surface_intersection": contact, "distance_mm": distance}
            pairs.append(row)
            if contact and not expected:
                unintended.append([a, b])
    mesh_quality = {}
    for path in sorted((HERE / "geometry").glob("*.npz")):
        with np.load(path) as data:
            mesh = trimesh.Trimesh(data["v"], data["f"], process=False)
        mesh_quality[path.stem] = {
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "finite_vertices": bool(np.isfinite(mesh.vertices).all()),
            "bounds_mm": mesh.bounds.tolist(),
            "watertight": bool(mesh.is_watertight),
            "triangles": len(mesh.faces),
        }
    result = {
        "scope": "One-time frozen-source reconstruction and direct-chain external occupancy query; no enclosure or routing claim",
        "coordinate_frame": "Regulator female faceY0, flow+Y",
        "direct_chain_parts": [row["name"] for row in records],
        "direct_chain_bounds_mm": [envelope.min(0).tolist(), envelope.max(0).tolist()],
        "direct_chain_size_xyz_mm": np.ptp(envelope, axis=0).tolist(),
        "direct_chain_tube_mouth_span_mm": float(np.linalg.norm(
            np.array(tube_ports["outlet"]["point_mm"]) - tube_ports["inlet"]["point_mm"])),
        "direct_chain_ports": tube_ports,
        "source_reconstruction_max_bound_error_mm": source_reconstruction,
        "cap_source_cross_check_error_mm": float(np.linalg.norm(cap_calc - cap["point_mm"])),
        "unintended_pair_intersections": unintended,
        "pairs": pairs,
        "mesh_quality": mesh_quality,
        "limits": [
            "Metal reference mouths contain display closures and simplified thread envelopes; the direct threaded pair is intentional overlap and not an internal-interference test.",
            "Nominal full14.3mm inlet-adapter thread engagement and9.18mm direct regulator/check engagement are layout estimates.",
            "No host enclosure, roof, support, gas tube or other assembly component is checked here; the parent study owns those checks.",
        ],
    }
    (HERE / "interfaces.json").write_text(json.dumps(model.interfaces(), indent=2) + "\n")
    (HERE / "audit.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k in [
        "direct_chain_size_xyz_mm", "direct_chain_tube_mouth_span_mm",
        "source_reconstruction_max_bound_error_mm", "cap_source_cross_check_error_mm",
        "unintended_pair_intersections"]}, indent=2))


if __name__ == "__main__":
    main()
