"""Flat PCB near the front on the cold core, with the selected water/electronics group.

This arrangement uses only the selected wet/dry component group and ideal shell
context. V-B and its connected routes are left for placement on the other side.
The manual --check asks about the carried PCB plugs and local leads.
"""
from pathlib import Path
import argparse
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("wet_dry", HERE.parent / "wet-dry/study.py")
parent = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parent)
base = parent.base


def pose(geometries):
    scene = parent.pose(geometries)
    # Source-world pose: board underside Z257; bottom tails Z255.
    rotation = [[0,0,1],[0,1,0],[-1,0,0]]
    translation = [-325.3999938964844,-53.98393249511719,353.25]
    pcb = next(m for m in scene["instances"] if m["name"] == "pcba")
    pcb.update(rotation=rotation,translation=translation,
               label="Main PCB · flat and forward · underside Z257")
    scene["instances"] = [m for m in scene["instances"] if "connection_owner" not in m]
    scene["instances"].extend(parent.connections.instances(scene["instances"]))
    scene.update(id="pcb-low-fore",title="PCB flat, low and forward")
    scene["pins"] = [p for p in scene["pins"] if not p["text"].startswith("Main PCB")]
    scene["pins"].append({"text":"PCB · low and forward","at":[-35.6,227.4,267.6],
                          "views":["three","top","electronics"]})
    scene["layout"].update(pcb_orientation="Flat on its back, components upward, near the front of the cold core",
        pcb_underside_z_mm=257, pcb_footprint_mm={"xmin":-72,"xmax":.800018310546875,
        "ymin":182,"ymax":272.81605529785156},
        context_scope="Selected water header, existing dry-side electronics and WAGOs, funnel/frame and ideal walls/ceiling; V-B and reservoir routes set aside",
        relay_service="PCB is forward of the relays and supply; no PCB removal for their terminal tool columns",
        planned_funnel_minus_y_expansion="Future funnel shape to be considered with the PCB below its current bowl")
    return scene


def check(scene, geometries):
    import fcl
    meshes = base.world_meshes(scene,geometries)
    bounds,objects = {},{}
    for name,(v,f) in meshes.items():
        b=fcl.BVHModel();b.beginModel(len(v),len(f));b.addSubModel(v,f.astype(np.int32));b.endModel()
        objects[name]=fcl.CollisionObject(b);bounds[name]=(v.min(0),v.max(0))
    mates={frozenset((m["a"],m["b"])) for m in scene["mates"]}
    moving=[m["name"] for m in scene["instances"]
            if m["name"]=="pcba" or m.get("connection_owner")=="pcba"]
    done,hits=set(),[]
    for name in moving:
        lo,hi=bounds[name]
        for other,(low,high) in bounds.items():
            pair=frozenset((name,other))
            if name==other or pair in done or pair in mates:continue
            done.add(pair)
            if np.any(np.minimum(hi,high)-np.maximum(lo,low)<.001):continue
            if fcl.collide(objects[name],objects[other],fcl.CollisionRequest(),fcl.CollisionResult()):
                hits.append([name,other])
    v=np.vstack([meshes[n][0] for n in moving])
    return {"scope":"Repositioned PCB, mating plugs and local conductors against the selected previous component group; V-B and reservoir routes excluded",
            "interferences":hits,"connected_pcb_bounds_mm":[v.min(0).tolist(),v.max(0).tolist()],
            "lowest_tail_to_plain_core_mm":float(meshes["pcba"][0][:,2].min()-253.4),
            "pcb_to_funnel_mm":parent.parent.lower.surface_distance(meshes["pcba"],meshes["funnel"]),
            "pcb_to_frame_mm":parent.parent.lower.surface_distance(meshes["pcba"],meshes["funnel-frame"])}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check",action="store_true")
    args=parser.parse_args()
    geometries=parent.library();scene=pose(geometries)
    if args.check:scene["metrics"]=check(scene,geometries)
    (HERE/"study.json").write_text(json.dumps(scene,indent=2)+"\n")
    datums=parent.connections.world_datums(scene["instances"])
    datums["service"]={"scope":"Terminal datums and local installed leads; full service sequence is not designed here",
        "PCB":"Flat near the front of the core; below the removable funnel",
        "power":"The supply and relay terminal columns are aft of the PCB footprint"}
    (HERE/"connection-datums.json").write_text(json.dumps(datums,indent=2)+"\n")
    used={m["geometry"] for m in scene["instances"]}
    packed={n:base.pack(*geometries[n],12000 if n.startswith("connection-")
                       else 5200 if n=="pump" else 3600) for n in sorted(used)}
    out=HERE/"out";out.mkdir(exist_ok=True)
    (out/"viewer-data.json").write_text(json.dumps({"space":parent.parent.water.SPACE,
        "geometries":packed,"variants":[scene]},separators=(",",":")))
    print(json.dumps(scene.get("metrics",{}),indent=2))


if __name__=="__main__":main()
