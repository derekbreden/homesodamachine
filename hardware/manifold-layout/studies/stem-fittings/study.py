"""Free-space water group with seated stem fittings, in millimetres.

Mesh-only study: no enclosure placement or production geometry is changed.
Run with tools/cad-venv/bin/python; --check asks FCL about unrelated bodies.
The baseline snapshot is deliberately self-contained and fixes the agreed poses.
"""
from pathlib import Path
import argparse
import base64
import copy
import gzip
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
REF = ROOT / "hardware/reference"
I = np.eye(3)
ELBOW_R = np.array([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
CHECK_R = np.array([[0, 0, 1], [-1, 0, 0], [0, -1, 0]])
BRANCH_R = np.diag([-1, -1, 1])
ASSE_GROUP = {"asse", "asse-inlet-tpu", "asse-outlet-tpu", "vent-sleeve", "water-in", "vent"}
FLAVOR_GROUP = {"reg", "va", "va-flavor"}
HANDOFFS = {"water-in", "vent", "va-flavor", "check-carbonator"}
MODEL_FILES = {
    "stem-elbow": "neofit-stem-elbow/neofit-stem-elbow.npz",
    "run-stem": "neofit-stem-run-tee/neofit-stem-run-tee.npz",
    "neofit-branch": "branch-stem-tees/neofit-atbu444-e-estimate.npz",
    "jg-branch": "branch-stem-tees/john-guest-ci580808w-estimate.npz",
}


def read_json(path):
    return json.loads(path.read_text())


BASE = read_json(HERE / "socket-layout.json")
ED = read_json(REF / "neofit-stem-elbow/model-check.json")
RD = read_json(REF / "neofit-stem-run-tee/model-check.json")["ports"]
BD = read_json(REF / "branch-stem-tees/dimensions.json")["variants"]
VK_MOUTH = np.array(next(j["point"] for j in BASE["interfaces"] if j["a"] == "vk" and j["b"] == "tee-fold"))
CHECK_MOUTH = np.array(next(j["point"] for j in BASE["interfaces"] if j["a"] == "check"))
OLD_ASSE_MOUTH = np.array(BASE["interfaces"][0]["point"])
OLD_REG_MOUTH = np.array(BASE["interfaces"][1]["point"])
OLD_CARB_MOUTH = np.array(next(p["at"] for p in BASE["pins"] if p["text"].startswith("To carbonator"))) + [0, 0, 24]


def library():
    result = {}
    with np.load(HERE / "socket-layout.npz") as data:
        for m in BASE["meshes"]:
            result[m["name"]] = (data[m["vertices"]], data[m["faces"]])
    for name, path in MODEL_FILES.items():
        with np.load(REF / path) as data:
            result[name] = (data["v"], data["f"])
        with np.load(HERE / "trimmed" / (name + ".npz")) as data:
            result[name + "-trimmed"] = (data["v"], data["f"])
    return result


def instance(name, geometry, translation=(0, 0, 0), rotation=I, **metadata):
    return {"name": name, "geometry": geometry, "translation": list(translation),
            "rotation": np.asarray(rotation).tolist(), **metadata}


def variant(kind, insertion=12.7, socket_reach_offset=0, trim=True):
    """Hold pump, check, V-K and existing bent TPU adapters in their poses."""
    baseline = kind == "union"
    trim = trim and not baseline
    result = {"id": kind + ("-stock" if not trim and not baseline else ""), "instances": [], "pins": copy.deepcopy(BASE["pins"]),
              "arrows": copy.deepcopy(BASE["arrows"]), "mates": [],
              "unknown_host_insertion_mm": insertion, "trimmed_stems": trim}
    tip_reach = -ED["stem_tip"][0][0]
    socket_reach = ED["socket"][0][1] + socket_reach_offset
    elbow_reach = -ED["stem_shoulder"][0][0] if trim else tip_reach - insertion
    elbow = VK_MOUTH + [0, 0, elbow_reach]
    socket = elbow + [socket_reach, 0, 0]
    check_elbow = CHECK_MOUTH + [0, -elbow_reach, 0]
    carb = check_elbow + [0, 0, -socket_reach]
    if kind == "run":
        reach = -RD["run_stem"]["shoulder_mm"][0] if trim else -RD["run_stem"]["position_mm"][0] - 16.891
        center = socket + [reach, 0, 0]
        asse = center + RD["branch_socket"]["position_mm"]
        reg = center + RD["run_socket"]["position_mm"]
        tee_geometry, tee_rotation = "run-stem", I
    elif kind in ("neofit-branch", "jg-branch"):
        spec = BD["neofit" if kind == "neofit-branch" else "john-guest"]
        p = spec["ports"]
        center = socket + [p["run_plus"]["position"][0], 0, 0]
        reach = p["branch_stem"]["shoulder"][1] if trim else p["branch_stem"]["position"][1] - 15
        asse = center + [0, -reach, 0]
        reg = center + p["run_plus"]["position"]
        tee_geometry, tee_rotation = kind, BRANCH_R
    else:
        center = np.array(next(p["at"] for p in BASE["pins"] if p["text"] == "Tee"))
        asse, reg = OLD_ASSE_MOUTH.copy(), OLD_REG_MOUTH.copy()
    asse_delta, flavor_delta, carb_delta = asse - OLD_ASSE_MOUTH, reg - OLD_REG_MOUTH, carb - OLD_CARB_MOUTH
    if baseline:
        asse_delta *= 0; flavor_delta *= 0; carb_delta *= 0
    for metadata in BASE["meshes"]:
        n = metadata["name"]
        m = {k: v for k, v in metadata.items() if k not in ("vertices", "faces")}
        m.pop("name")
        delta, rotation, geometry = np.zeros(3), I, n
        if n in ASSE_GROUP:
            delta = asse_delta
        elif n in FLAVOR_GROUP:
            delta = flavor_delta
        elif n == "check-carbonator":
            delta = carb_delta
        if not baseline and n in ("tee-fold", "carbonator-fold", "tee"):
            if n == "tee-fold":
                geometry, rotation, delta = "stem-elbow", ELBOW_R, elbow
            elif n == "carbonator-fold":
                geometry, rotation, delta = "stem-elbow", CHECK_R, check_elbow
            else:
                geometry, rotation, delta = tee_geometry, tee_rotation, center
            m["role"] = "stem"
            m["label"] = {"tee-fold": "NeoFit stem elbow directly into V-K",
                          "carbonator-fold": "NeoFit stem elbow directly into check outlet",
                          "tee": {"run": "NeoFit ATRU444-E run-stem tee into the elbow",
                                  "neofit-branch": "NeoFit ATBU444-E branch stem into the ASSE TPU adapter",
                                  "jg-branch": "John Guest CI580808W branch stem · published pressed-collet state"}[kind]}[n]
            if trim:
                geometry += "-trimmed"
                m["label"] += " · stem trimmed, shoulder flush"
        result["instances"].append(instance(n, geometry, delta, rotation, **m))

    pin_groups = {"ASSE 1022": asse_delta, "Water in": asse_delta,
                  "Vent to faucet": asse_delta, "Regulator": flavor_delta,
                  "V-A": flavor_delta, "To flavor manifold": flavor_delta}
    for p in result["pins"]:
        if p["text"] in pin_groups:
            p["at"] = (np.array(p["at"]) + pin_groups[p["text"]]).tolist()
        elif p["text"] == "Tee":
            p["at"] = center.tolist()
        elif p["text"] == "Added elbow" and not baseline:
            p.update(text="Stem elbow", at=elbow.tolist())
        elif p["text"].startswith("To carbonator"):
            p["at"] = (np.array(p["at"]) + carb_delta).tolist()
    for a in result["arrows"]:
        p = np.array(a["at"])
        if a["role"] == "flavor":
            p += flavor_delta
        elif a["role"] == "neutral" and p[1] < -35 and p[2] > 60:
            p += asse_delta
        elif a["role"] == "carbonator" and a["dir"] == [0, 0, -1]:
            p += carb_delta
        a["at"] = p.tolist()
    result["tee_center_mm"] = center.tolist()
    result["asse_translation_mm"] = asse_delta.tolist()
    result["flavor_translation_mm"] = flavor_delta.tolist()
    result["mates"] = copy.deepcopy(BASE["interfaces"])
    if not baseline:
        points = {frozenset(("asse-outlet-tpu", "tee")): asse,
                  frozenset(("tee", "reg")): reg,
                  frozenset(("reg", "va")): np.array(BASE["interfaces"][2]["point"]) + flavor_delta,
                  frozenset(("check", "carbonator-fold")): CHECK_MOUTH,
                  frozenset(("vk", "tee-fold")): VK_MOUTH,
                  frozenset(("tee-fold", "tee")): socket}
        for j in result["mates"]:
            pair = frozenset((j["a"], j["b"]))
            if pair in points:
                j["point"] = points[pair].tolist()
            if pair in (frozenset(("check", "carbonator-fold")), frozenset(("vk", "tee-fold"))):
                j.update(connection="male stem into female socket", insertion_mm=insertion,
                         shoulder_gap_mm=0 if trim else 21.0058 - insertion,
                         stem_trim_mm=21.0058 - insertion if trim else 0)
            elif pair == frozenset(("tee-fold", "tee")) and kind == "run":
                j.update(connection="male stem into NeoFit socket", insertion_mm=16.891,
                         shoulder_gap_mm=0 if trim else 21.0058 - 16.891,
                         stem_trim_mm=21.0058 - 16.891 if trim else 0)
            elif pair == frozenset(("asse-outlet-tpu", "tee")) and kind != "run":
                length = BD["neofit" if kind == "neofit-branch" else "john-guest"]["model_mm"]["stem_length"]
                j.update(connection="male stem into TPU socket", insertion_mm=15,
                         shoulder_gap_mm=0 if trim else length - 15,
                         stem_trim_mm=length - 15 if trim else 0)
            elif pair == frozenset(("tee-fold", "tee")):
                depth = BD["neofit" if kind == "neofit-branch" else "john-guest"]["model_mm"]["female_insertion"]
                j.update(connection="female sockets joined by concealed tube",
                         concealed_tube_length_mm=16.891 + depth)
            else:
                j["connection"] = "female faces meet; concealed tube connects sockets"
    return result


def world_meshes(scene, geometries):
    return {m["name"]: (geometries[m["geometry"]][0] @ np.array(m["rotation"]).T + m["translation"],
                        geometries[m["geometry"]][1]) for m in scene["instances"]}


def envelope(meshes):
    points = np.vstack([v for n, (v, f) in meshes.items() if n not in HANDOFFS])
    low, high = points.min(0), points.max(0)
    return {"bounds_mm": [low.tolist(), high.tolist()], "size_xyz_mm": (high - low).tolist()}


def interference(scene, geometries):
    """Manual exterior question; intended mating overlaps are reported separately."""
    import fcl
    meshes = world_meshes(scene, geometries)
    selected = [m["name"] for m in scene["instances"] if m["kind"] not in ("clamp", "tube")]
    objects = {}
    for n in selected:
        v, f = meshes[n]
        b = fcl.BVHModel(); b.beginModel(len(v), len(f))
        b.addSubModel(v, f.astype(np.int32)); b.endModel()
        objects[n] = fcl.CollisionObject(b)
    mates = {frozenset((j["a"], j["b"])) for j in scene["mates"]}
    mates.update(frozenset(p) for p in [("pump", "pump-inlet-tpu"), ("pump", "pump-outlet-tpu"),
        ("pump", "pump-sliding-foot"), ("asse", "asse-inlet-tpu"), ("asse", "asse-outlet-tpu"), ("asse", "vent-sleeve")])
    issues = []
    for i, n in enumerate(selected):
        v = meshes[n][0]
        for other in selected[i + 1:]:
            if frozenset((n, other)) in mates:
                continue
            w = meshes[other][0]
            if np.any(np.minimum(v.max(0), w.max(0)) - np.maximum(v.min(0), w.min(0)) < .001):
                continue
            if fcl.collide(objects[n], objects[other], fcl.CollisionRequest(), fcl.CollisionResult()):
                issues.append([n, other])
    return issues


def pack(v, f, limit):
    import trimesh
    q, inverse = np.unique(np.rint(v * 50).astype(np.int16), axis=0, return_inverse=True)
    f = inverse[f]
    if len(f) > limit:
        mesh = trimesh.Trimesh(q.astype(float) / 50, f, process=False).simplify_quadric_decimation(face_count=limit)
        q, f = np.rint(mesh.vertices * 50).astype(np.int16), np.asarray(mesh.faces)
    raw = q.astype('<i2').tobytes() + f.astype('<u4').tobytes()
    return {"vc": len(q), "ic": int(f.size), "data": base64.b64encode(gzip.compress(raw, 6)).decode()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = library()
    variants = [variant(k) for k in ("run", "neofit-branch", "jg-branch", "union")]
    variants.append(variant("run", trim=False))
    summary = {"scope": BASE["scope"], "units": "mm", "envelope_excludes": sorted(HANDOFFS),
               "unknown_host_insertion": {"nominal_mm": 12.7, "range_mm": [10, 15],
                   "status": "layout estimate, controls cut length; flush shoulders fix exterior poses"},
               "stem_assumption": "Stems are trimmed to host depth with shoulders flush at socket mouths", "variants": {}}
    for scene in variants:
        report = {k: scene[k] for k in ("trimmed_stems", "tee_center_mm", "asse_translation_mm", "flavor_translation_mm", "mates")}
        report.update(envelope(world_meshes(scene, geometries)))
        if args.check:
            report["unrelated_body_interferences"] = interference(scene, geometries)
        if scene["trimmed_stems"]:
            study = [envelope(world_meshes(variant(scene["id"], socket_reach_offset=offset), geometries))["size_xyz_mm"]
                     for offset in (-1, 0, 1)]
            report["envelope_range_for_elbow_reach_estimate_mm"] = [np.min(study, axis=0).tolist(), np.max(study, axis=0).tolist()]
        elif scene["id"] != "union":
            study = [envelope(world_meshes(variant(scene["id"].removesuffix("-stock"), d, offset, trim=False), geometries))["size_xyz_mm"]
                     for d in (10, 12.7, 15) for offset in (-1, 0, 1)]
            report["envelope_range_for_host_depth_and_elbow_reach_estimates_mm"] = [np.min(study, axis=0).tolist(), np.max(study, axis=0).tolist()]
        summary["variants"][scene["id"]] = report
        scene["size_xyz_mm"] = report["size_xyz_mm"]
    (HERE / "study.json").write_text(json.dumps(summary, indent=2) + "\n")
    packed = {n: pack(v, f, 5200 if n == "pump" else 3600) for n, (v, f) in geometries.items()}
    out = HERE / "out"; out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"geometries": packed, "variants": variants}, separators=(",", ":")))
    print(json.dumps({k: {p: r[p] for p in ("size_xyz_mm", "unrelated_body_interferences") if p in r}
                      for k, r in summary["variants"].items()}, indent=2))


if __name__ == "__main__":
    main()
