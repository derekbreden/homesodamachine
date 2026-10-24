"""Selected connected layout with dry-wall relays and explicit printed supports.

This study carries the accepted water group, PCB and folded CO2 poses. Native
wall geometry is built separately through the shared CAD queue.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("supported_parent", HERE.parent / "co2-fold/study.py")
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
base = parent.base
connections = parent.module("supported_connections", HERE.parent / "wet-dry/connections/model.py")
I = np.eye(3)
C14_CENTER = [-68.5, 471.3, 330.]
RJ11_CENTER = [-30., 471.3, 274.3760478805363]
POSES = {
    "c14-inlet": {"rotation": I.tolist(), "translation": [-135.4, 10.09, -6.21058083755679],
                  "label": "C14 · horizontal · balanced upper dry corner"},
    "keystone-jack": {"rotation": I.tolist(), "translation": [10.71, 3.52, -28.026242538242116],
                      "label": "RJ11 · low beside the umbilical · flush snap-in receptacle"},
    "relay-1": {"rotation": [[-1,0,0],[0,-1,0],[0,0,1]],
                "translation": [1.75, 689.8, -34.7],
                "label": "Compressor relay · dry wall · terminals aft"},
    "relay-2": {"rotation": [[-1,0,0],[0,0,-1],[0,-1,0]],
                "translation": [1.75, 686.4, 666.3],
                "label": "Water-pump relay · dry wall · terminals aft"},
}


def library():
    g = parent.library()
    for path in sorted((HERE / "parts").glob("*.npz")):
        with np.load(path) as d:
            g[path.stem] = d["v"], d["f"]
    return g


def pose(g):
    scene = parent.pose(g)
    scene["instances"] = [m for m in scene["instances"]
                          if m["name"] != "ground-stack"
                          and m.get("connection_owner") not in POSES]
    for m in scene["instances"]:
        if m["name"] in POSES:
            m.update(copy.deepcopy(POSES[m["name"]]))
        if m["name"] == "left-wall":
            m.update(label="Dry wall · integral relay mounts and V-A support")
        if m["name"] == "right-wall":
            m.update(label="Wet wall · integral V-K support")
        if m["name"] == "back-wall":
            m.update(label="Rear wall · upper horizontal C14 and low RJ11 receptacle")
    scene["instances"].extend(connections.instances(scene["instances"], owners=set(POSES)))
    names = {m["name"] for m in scene["instances"]}
    scene["mates"] = [m for m in scene["mates"] if m["a"] in names and m["b"] in names]
    for relay in ("relay-1", "relay-2"):
        scene["mates"].append({"a": relay, "b": "left-wall",
                               "connection": "Four M3 mounting holes seat on integral wall bosses"})
    for valve, wall in (("vk", "right-wall"), ("va", "left-wall")):
        scene["mates"].append({"a": valve, "b": wall,
                               "connection": "Printed mounting structure at the valve's existing feet"})
    for name, label in (("relay-mount-highlight", "Integral relay mounting bosses"),
                        ("vk-support-highlight", "V-K · four sockets on integral raised wall seat"),
                        ("va-support-highlight", "V-A · four sockets on integral raised wall seat")):
        scene["instances"].append(base.instance(name, name, role="support", kind="display",
            context=True, render_only=True, label=label))
    scene.update(id="wall-supported", title="Dry-wall electronics and printed valve supports")
    scene["layout"].update(
        ground_placement="Deferred until primary components and complete wire routes are placed",
        relay_mount="Both PCB backs face the -X wall; components and screw heads face inward (+X)",
        relay_service="Roof removed; terminal tool approaches face +X",
        c14_flange_center_mm=C14_CENTER, rj11_face_center_mm=RJ11_CENTER,
        psu_mount_service="Supply remains flat on the core; its independent fasteners and insulation detail remain to design",
        context_scope="Selected arrangement and explicit wall-mounted supports; not a production-pack migration",
    )
    scene["layout"]["device_selection"] = "PISCO regulator ordered (8638); separate check valve sourcing remains open"
    scene["layout"].pop("wago_groups", None)
    return scene


def check(scene, g):
    physical = copy.deepcopy(scene)
    physical["instances"] = [m for m in physical["instances"] if not m.get("render_only")]
    result = parent.check(physical, g)
    result.pop("scope_limit", None)
    result["scope"] = "Selected exterior bodies, local electrical connections and native printed walls; intended seats excluded"
    meshes = base.world_meshes(scene, g)
    result["changed_component_bounds_mm"] = {n: [meshes[n][0].min(0).tolist(), meshes[n][0].max(0).tolist()] for n in POSES}
    result["c14_surround_mm"] = {"to_left_inner_wall": float(meshes["c14-inlet"][0][:,0].min()+98.5),
                                "to_plain_roof": float(346.-meshes["c14-inlet"][0][:,2].max())}
    result["scope_limit"] = "Native placement/fit query only. Complete harnesses, final equipment retention and production shell migration remain to design."
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    g = library(); scene = pose(g)
    if args.check:
        scene["metrics"] = check(scene, g)
    (HERE / "study.json").write_text(json.dumps(scene, indent=2)+"\n")
    datums = connections.world_datums(scene["instances"])
    datums["service"] = {"PCB": "Low and forward; connector departures retained",
                         "relays": "Boards on dry wall; screw axes +X with roof removed",
                         "scope": "Local installed connections; full harness routing is pending"}
    (HERE / "connection-datums.json").write_text(json.dumps(datums, indent=2)+"\n")
    used = {m["geometry"] for m in scene["instances"]}
    packed = {n: base.pack(*g[n], 12000 if n.startswith("connection-") else 5200 if n=="pump" else 3600) for n in sorted(used)}
    out = HERE / "out"; out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"geometries": packed, "variants": [scene], "grid": parent.grid()}, separators=(",", ":")))
    print(json.dumps(scene.get("metrics", {}), indent=2))


if __name__ == "__main__":
    main()
