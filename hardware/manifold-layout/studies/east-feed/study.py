"""V-A routes east then fore to Y-A, with the PCB packed across the dry side.

The study carries selected wall-supported parts and their native geometry.
Local connection meshes participate in the manual fit query but are hidden
in the view. Regulator research is a separate free-space size comparison.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json
import math

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name,path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


parent = module("east_feed_parent", HERE.parent / "wall-supported/study.py")
base = parent.base
grid_model = module("east_feed_mesh", HERE.parent / "co2-grid/study.py")
ecoreg = module("east_feed_ecoreg", ROOT / "hardware/reference/ecoreg-regulator/model.py")
I = np.eye(3)
PCB_R = np.array([[0,1,0],[0,0,-1],[-1,0,0]])
PCB_T = [-328.9839324951172,508.20001220703125,353.25]
DEST = np.array([22.35,166.24,270.675])
SMALL_R = 14.


def route():
    elbow = np.array([-76.40410112876839,296.3397605281867,262.7856478805363])
    mouth = elbow+[19.05,0.,0.]
    broad_r = DEST[0]-mouth[0]
    a = np.linspace(0.,math.pi/2,49)
    broad = mouth+np.column_stack([broad_r*np.sin(a),broad_r*(np.cos(a)-1),np.zeros(len(a))])
    fore = broad[-1]
    center = DEST+[0.,SMALL_R,0.]
    dy,dz = fore[1]-center[1],center[2]-fore[2]
    angle = math.asin(2*SMALL_R/math.hypot(dy,SMALL_R-dz))-math.atan2(SMALL_R-dz,dy)
    a = np.linspace(0.,angle,17)
    rising = fore+np.column_stack([np.zeros(len(a)),-SMALL_R*np.sin(a),SMALL_R*(1-np.cos(a))])
    a = np.linspace(angle,-math.pi/2,41)
    final = center+np.column_stack([np.zeros(len(a)),SMALL_R*np.sin(a),SMALL_R*np.cos(a)])
    points = np.vstack([mouth-[16.891,0.,0.],broad,rising[1:],final,DEST-[0.,0.,15.7]])
    return {"elbow_corner_mm":elbow.tolist(),"elbow_socket_mm":mouth.tolist(),
            "east_to_fore_radius_mm":float(broad_r),"minimum_centerline_radius_mm":SMALL_R,
            "incline_degrees":math.degrees(angle),"inclined_straight_length_mm":float(np.linalg.norm(final[0]-rising[-1])),
            "fore_tangent_mm":fore.tolist(),"incline_start_mm":rising[-1].tolist(),
            "final_turn_start_mm":final[0].tolist(),"destination_mm":DEST.tolist(),
            "destination_outward_axis":[0.,0.,1.],"peak_z_mm":float(center[2]+SMALL_R),
            "source_insertion_mm":16.891,"destination_insertion_nominal_mm":15.7,
            "centerline_mm":points.tolist(),"tube_od_mm":6.35,"tube_id_mm":4.24}


def library():
    g = parent.library()
    g.update(ecoreg.library())
    d = route()
    g["va-to-ya"] = grid_model.tube(d["centerline_mm"],3.175,2.12)
    v,f = g["forward-tee-y-b"]
    g["tee-ya-target"] = v*np.array([-1.,1.,1.]),f[:,::-1].copy()
    return g


def pose(g):
    scene = parent.pose(g)
    for m in scene["instances"]:
        if m["name"]=="va-outlet-elbow":
            m.update(rotation=PCB_R.tolist(),label="V-A outlet · stem elbow points east (+X)")
        if m["name"]=="va-flavor":
            m.update(geometry="va-to-ya",rotation=I.tolist(),translation=[0.,0.,0.],
                     label="V-A → Y-A · east around pump, fore beside PCB, down into tee")
        if m["name"]=="pcba" or m.get("connection_owner")=="pcba":
            m.update(rotation=PCB_R.tolist(),translation=PCB_T)
            if m["name"]=="pcba":
                m["label"]="Main PCB · west · long dimension across X · J10 faces east"
        if m["role"]=="wire":
            m["display_suppressed"]=True
    scene["instances"].append(base.instance("tee-ya-target","tee-ya-target",kind="component",role="wet",context=True,
        label="Y-A · shared-source tee for flavor manifold · V-A lands in upper port1"))
    for mate in scene["mates"]:
        if {mate["a"],mate["b"]}=={"va-outlet-elbow","va-flavor"}:
            mate["point"]=route()["elbow_socket_mm"]
    scene["mates"].append({"a":"va-flavor","b":"tee-ya-target",
                           "connection":"Fluid3 V-A-O to Y-A1; upper socket, nominal15.7mm insertion"})
    scene.update(id="east-feed",title="East-facing V-A outlet and west-packed PCB")
    scene["layout"].update(
        pcb_orientation="Flat, components up; long dimension across X and J10 entry facing east",
        pcb_footprint_mm={"xmin":-93.,"xmax":-2.1839447021484375,"ymin":182.,"ymax":254.80001831054688},
        pcb_lead_dressing="Carried local connector and wire envelopes checked quietly; harness drawings omitted",
        flavor_mouth_world_mm=route()["elbow_socket_mm"],flavor_handoff_direction_world=[1.,0.,0.],
        va_destination="Y-A port1, the flavor manifold shared-source tee; clean-water supply",
        va_route=route(),
        route_context="V-B and reservoir routes remain deferred; Y-A alone supplies the actual destination datum",
        regulator_selection="Selected Yetaha arrangement retained; EcoReg is a separate research size comparison",
    )
    return scene


def comparison(scene):
    old = copy.deepcopy(next(m for m in scene["instances"] if m["name"]=="reg"))
    inlet = np.array([2.1458988712315943,296.3397605281867,334.3760478805363])
    q = np.diag([-1.,1.,-1.])
    old.update(name="comparison-current-regulator",translation=(q@np.array(old["translation"])-q@inlet+[0.,70.,0.]).tolist(),
               rotation=(q@np.array(old["rotation"])).tolist(),role="current-regulator",
               label="Current Yetaha estimate · 59.5mm mouths · 63mm fork span · 53mm height")
    candidate = ecoreg.instances(translation=[18.5,-10.,0.])
    for m in candidate:
        m["role"]="candidate-regulator" if m["name"]=="ecoreg-body" else "fitting"
    return {"id":"regulator-comparison","instances":[old,*candidate],
            "scope":"Free-space size comparison; candidate not installed in the selected water group",
            "available_straight_gap_mm":74.5,"candidate_tube_mouth_span_estimate_mm":89.,
            "candidate_selection":"Research candidate,45psi; not a production or purchase selection"}


def check(scene,g):
    result = parent.check(scene,g)
    meshes = base.world_meshes(scene,g)
    moving = ["pcba",*[m["name"] for m in scene["instances"] if m.get("connection_owner")=="pcba"]]
    v = np.vstack([meshes[n][0] for n in moving])
    result["connected_pcb_bounds_mm"]=[v.min(0).tolist(),v.max(0).tolist()]
    result["connected_pcb_to_ideal_west_wall_mm"]=float(v[:,0].min()+98.5)
    # FCL's distance query uses the same detailed exterior meshes as the fit query.
    import fcl
    def obj(mesh):
        v,f=mesh;model=fcl.BVHModel();model.beginModel(len(v),len(f));model.addSubModel(v,f.astype(np.int32));model.endModel();return fcl.CollisionObject(model)
    tube = obj(meshes["va-flavor"])
    result["tube_gaps_mm"]={n:float(fcl.distance(tube,obj(meshes[n]),fcl.DistanceRequest(),fcl.DistanceResult()))
                           for n in ("pump","pcba","funnel-frame")}
    result["scope"]="Changed elbow, complete V-A tube, moved PCB and carried local connections against the selected arrangement and Y-A target"
    return result


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true")
    args=parser.parse_args();g=library();scene=pose(g)
    if args.check:
        scene["metrics"]=check(scene,g)
    (HERE/"study.json").write_text(json.dumps(scene,indent=2)+"\n")
    (HERE/"route.json").write_text(json.dumps(route(),indent=2)+"\n")
    datums=parent.connections.world_datums(scene["instances"])
    datums["service"]={"scope":"Local envelopes only; harness drawings omitted","J10":"Wire entry faces east (+X)"}
    (HERE/"connection-datums.json").write_text(json.dumps(datums,indent=2)+"\n")
    comp=comparison(scene)
    visible=copy.deepcopy(scene);visible["instances"]=[m for m in visible["instances"] if not m.get("display_suppressed")]
    used={m["geometry"] for s in (visible,comp) for m in s["instances"]}
    packed={n:base.pack(*g[n],10000 if n=="va-to-ya" else 12000 if n.startswith("connection-") else 5200 if n=="pump" else 3600) for n in sorted(used)}
    out=HERE/"out";out.mkdir(exist_ok=True)
    (out/"viewer-data.json").write_text(json.dumps({"geometries":packed,"variants":[visible],"comparison":comp,
        "grid":parent.parent.grid()},separators=(",",":")))
    print(json.dumps(scene.get("metrics",{}),indent=2))


if __name__=="__main__":
    main()
