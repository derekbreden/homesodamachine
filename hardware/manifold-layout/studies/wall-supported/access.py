"""Manually inspect 40 mm driver shafts for the selected wall-mounted relays."""
import importlib.util
import json
from pathlib import Path

import fcl
import numpy as np
import trimesh

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("supported_access_scene", HERE / "study.py")
study = importlib.util.module_from_spec(spec)
spec.loader.exec_module(study)


def main():
    g = study.library(); scene = study.pose(g)
    scene["instances"] = [m for m in scene["instances"] if not m.get("render_only") and m["name"]!="ceiling"]
    meshes = study.base.world_meshes(scene, g)
    probes = [m for m in study.connections.instances(scene["instances"], probes=True,
              owners={"relay-1", "relay-2", "psu"}) if m["kind"]=="probe"]
    targets = {m["name"]:m["connection_owner"] for m in probes}
    probe_meshes = study.base.world_meshes({"instances":probes}, g)
    rotation = np.array([[0,0,1],[1,0,0],[0,1,0]])
    shaft = trimesh.creation.cylinder(radius=1.75,height=40.,sections=24)
    for relay,cz in (("relay-1",303.),("relay-2",328.)):
        for y in (365.,431.):
            for z in (cz-6.5,cz+6.5):
                name = f"mount-driver-{relay}-{y:g}-{z:g}"
                targets[name] = relay
                probe_meshes[name] = (
                    shaft.vertices @ rotation.T + [-72.9,y,z], shaft.faces)
    objects = {}; bounds = {}
    for name,(v,f) in {**meshes,**probe_meshes}.items():
        model = fcl.BVHModel(); model.beginModel(len(v),len(f))
        model.addSubModel(v,f.astype(np.int32)); model.endModel()
        objects[name] = fcl.CollisionObject(model); bounds[name] = v.min(0),v.max(0)
    hits = []
    for p in probe_meshes:
        for n in meshes:
            if np.any(np.minimum(bounds[p][1],bounds[n][1])-np.maximum(bounds[p][0],bounds[n][0])<.001):
                continue
            if fcl.collide(objects[p],objects[n],fcl.CollisionRequest(),fcl.CollisionResult()):
                hits.append([p,n])
    result = {"scope":"Roof removed; 3.5 mm diameter, 40 mm working shafts, without hand or handle envelopes",
        "tool_probe_count":len(probe_meshes),"raw_interferences":hits,
        "intended_terminal_entries":[[p,n] for p,n in hits if targets[p]==n],
        "terminal_entry_basis":"The driver starts at its own terminal's modeled screw location; reference terminal blocks have no internal screw wells",
        "unrelated_fixed_body_interferences":[[p,n] for p,n in hits if targets[p]!=n and not n.startswith("local-lead-")],
        "assembly_order":"Install relay mounting screws before landing COM; disconnect COM for module removal",
        "service":"Use a compact/right-angle driver at the wall-facing relay terminals or wire before final mounting; long straight driver and handle access are not established"}
    (HERE / "access-audit.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    main()
