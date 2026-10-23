"""Selected enclosure arrangement with a regular rear grid and connected CO2.

Frozen reference meshes, straight fitting axes and explicit tube-mouth datums.
This is an isolated layout study; it does not alter the production pack.
Run --check manually to query the selected occupied geometry.
"""
from pathlib import Path
import argparse
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


parent = module("pcb_low_fore", HERE.parent / "pcb-low-fore/study.py")
gas = module("co2_parts", HERE / "co2-parts/model.py")
base = parent.base
I = np.eye(3)
FORE = np.array([0., -7., 0.])
COLS = [37.2499988712316, 77.5]
ROWS = [334.3760478805363, 302.3760478805363, 270.3760478805363]
ASSIGN = [["bulkhead-water", "co2-inlet"],
          ["bulkhead-drain", "bulkhead-carb"],
          ["bulkhead-flavor-a", "bulkhead-flavor-b"]]
SOURCE = json.loads((HERE.parent / "wet-dry/layout.json").read_text())
PORTS = {p["name"]: p for p in SOURCE["wet_ports"]}
GAS_R = np.diag([-1., -1., 1.])
GAS_INLET = np.array([COLS[1], 454.0026, ROWS[0]])
INLET_ENGAGEMENT = 11.
GAS_T = GAS_INLET - GAS_R @ np.array([0., -13.7+INLET_ENGAGEMENT-14.3, 0.])
ELBOW_R = np.array([[0., 0., 1.], [-1., 0., 0.], [0., -1., 0.]])


def tube(points, radius, inside=None, sections=24):
    """Closed annular occupancy with rings normal to the sampled centreline."""
    p = np.array(points, float)
    tangent = np.gradient(p, axis=0)
    tangent /= np.linalg.norm(tangent, axis=1)[:, None]
    normal = np.cross(tangent, [1., 0., 0.])
    fallback = np.linalg.norm(normal, axis=1) < .1
    normal[fallback] = np.cross(tangent[fallback], [0., 1., 0.])
    normal /= np.linalg.norm(normal, axis=1)[:, None]
    other = np.cross(tangent, normal)
    a = np.linspace(0, 2*np.pi, sections, endpoint=False)
    ring = np.cos(a)[None,:,None]*normal[:,None,:] + np.sin(a)[None,:,None]*other[:,None,:]
    inside = radius*.66 if inside is None else inside
    n = len(p)*sections
    v = np.vstack([(p[:,None,:]+r*ring).reshape(-1,3) for r in (radius,inside)])
    f = []
    for j in range(len(p)-1):
        for k in range(sections):
            a = j*sections+k; b = j*sections+(k+1)%sections
            f.extend([[a,b,b+sections],[a,b+sections,a+sections],
                      [a+n,b+sections+n,b+n],[a+n,a+sections+n,b+sections+n]])
    for j, reverse in ((0,True),(len(p)-1,False)):
        for k in range(sections):
            a = j*sections+k; b = j*sections+(k+1)%sections
            tris = [[a,a+n,b+n],[a,b+n,b]]
            f.extend([t[::-1] if reverse else t for t in tris])
    return v, np.array(f,dtype=np.int32)


def grid():
    result = []
    for row,names in enumerate(ASSIGN):
        for col,name in enumerate(names):
            p = PORTS[name]
            result.append({**p,"row":row,"column":col,"center_x_mm":COLS[col],
                "center_z_mm":ROWS[row],"inboard_mouth_mm":[COLS[col],p["inboard_mouth_mm"][1]+3.,ROWS[row]],
                "flange_seat_y_mm":471.3,"nut_seat_y_mm":465.3,
                "nut_AF_mm":21.0058 if name=="co2-inlet" else 20. if p["tube_od_mm"]==6.35 else 18.,
                "nut_depth_mm":7.0104 if name=="co2-inlet" else 4. if p["tube_od_mm"]==6.35 else 6.5})
    return result


def nut_mesh(port):
    """Bare hex occupancy with a clear barrel bore, axis +Y."""
    sections=48
    angle=np.linspace(0,2*np.pi,sections,endpoint=False)
    # Six face planes; sample corners explicitly on the shared 48-ring grid.
    outer=port["nut_AF_mm"]/2/np.cos((angle+np.pi/6)%(np.pi/3)-np.pi/6)
    inner=np.full(sections,port["bore_diameter_mm"]/2)
    v=[]
    for y in (465.3-port["nut_depth_mm"],465.3):
        for radius in (outer,inner):
            v.extend(np.column_stack([port["center_x_mm"]+radius*np.cos(angle),
                                      np.full(sections,y),port["center_z_mm"]+radius*np.sin(angle)]))
    f=[]
    for i in range(sections):
        j=(i+1)%sections
        for a,b,c,d in ((i,j,j+96,i+96),(i+48,i+144,j+144,j+48),
                        (i,i+48,j+48,j),(i+96,j+96,j+144,i+144)):
            f.extend([[a,b,c],[a,c,d]])
    return np.array(v),np.array(f,dtype=np.int32)


def gas_datums():
    ports = gas.direct_ports(GAS_R,GAS_T,inlet_engagement_mm=INLET_ENGAGEMENT)
    shoulder = np.array(ports["outlet"]["point_mm"])
    junction = shoulder - ELBOW_R @ np.array([-6.0452,0.,0.])
    mouth = junction + ELBOW_R @ np.array([0.,19.05,0.])
    cap = np.array(gas.cap_handoff()["point_mm"])
    return ports,junction,mouth,cap


def drop_points():
    _,_,mouth,cap = gas_datums()
    # Ten millimetres straight after the collet, then a broad S; vertical at
    # both interfaces. The guide carries a continuous tube into the core.
    start = mouth - [0.,0.,10.]
    end = cap + [0.,0.,10.]
    t = np.linspace(0,1,33)
    blend = t*t*(3-2*t)
    curve = start[None,:] + t[:,None]*(end-start)[None,:]
    curve[:,1] = start[1]+blend*(end[1]-start[1])
    return np.vstack([mouth+[0.,0.,16.891],mouth,start,
                      curve[1:-1],end,cap,cap-[0.,0.,12.]])


def departure(port, radius=14.):
    p = np.array(port["inboard_mouth_mm"])
    if port["name"] in ("bulkhead-drain","bulkhead-flavor-a"):
        angle = np.linspace(0,np.pi/2,33)
        points = p + np.column_stack([radius*(1-np.cos(angle)),
                                      -radius*np.sin(angle),np.zeros(len(angle))])
        return np.vstack([p+[0.,10.,0.],points,points[-1]+[15.,0.,0.]])
    return np.array([p+[0.,12.7 if port["tube_od_mm"]==6.35 else 10.,0.],p,p-[0.,20.,0.]])


def library():
    result = parent.parent.library()
    result.update(gas.library())
    for path in sorted((HERE/"parts").glob("*.npz")):
        with np.load(path) as data: result[path.stem] = (data["v"],data["f"])
    for port in grid():
        n=port["name"]
        result[n+"-nut"]=nut_mesh(port)
        if n not in ("bulkhead-water","co2-inlet"):
            result[n+"-departure"]=tube(departure(port),port["tube_od_mm"]/2)
    inlet=np.array(parent.pose(result)["layout"]["asse_inlet_mouth_world_mm"])+FORE
    result["grid-water-link"]=tube([inlet-[0.,15.,0.],
        np.array([COLS[0],446.51+12.7,ROWS[0]])],3.175,2.12)
    # Concealed tube between touching female mouths; no exposed stub.
    result["co2-inlet-link"]=tube([GAS_INLET+[0.,12.7,0.],GAS_INLET-[0.,15.7,0.]],3.175,2.12)
    result["co2-core-drop"]=tube(drop_points(),3.175,2.12)
    # Same external elbow, with its concealed stem trimmed for the selected
    # JG insertion. Only the parallel cylindrical stem is lengthened here.
    v,f=result["stem-elbow-trimmed"]
    v=v.copy();mask=v[:,0]<-6.0452
    v[mask,0]=-6.0452+(v[mask,0]+6.0452)*15.7/12.7
    result["gas-stem-elbow"]=(v,f)
    return result


def pose(geometries):
    scene=parent.pose(geometries)
    header={m["name"] for m in scene["instances"] if not m.get("context")}
    for m in scene["instances"]:
        if m["name"] in header:m["translation"]=(np.array(m["translation"])+FORE).tolist()
    for mate in scene["mates"]:
        if mate["a"] in header and mate["b"] in header and "point" in mate:
            mate["point"]=(np.array(mate["point"])+FORE).tolist()
    # Clock the matching heads fore about the unchanged vertical port axes.
    for name in ("vk","va"):
        m=next(m for m in scene["instances"] if m["name"]==name)
        pivot=np.array([76.40409887123158 if name=="vk" else -76.40410112876839,
                        303.3397605281867,0.])+FORE
        r=np.diag([-1.,-1.,1.])
        m["translation"]=(r@(np.array(m["translation"])-pivot)+pivot).tolist()
        m["rotation"]=(r@np.array(m["rotation"])).tolist()
        m["label"]=name.upper().replace("V","V-")+" · vertical ports · head fore"
    scene["instances"]=[m for m in scene["instances"] if m["name"] not in
        {"bulkhead-nut","carb-nut"} and not m["name"].endswith("-departure")]
    for port in grid():
        n=port["name"];old=PORTS[n]
        delta=np.array(port["inboard_mouth_mm"])-old["inboard_mouth_mm"]
        m=next(m for m in scene["instances"] if m["name"]==n)
        m.update(translation=(np.array(m["translation"])+delta).tolist(),
                 center_x_mm=port["center_x_mm"],center_z_mm=port["center_z_mm"],flange_seat_y_mm=471.3)
        if n=="co2-inlet":m["role"]="gas"
        scene["instances"].append(base.instance(n+"-nut",n+"-nut",role="wet",kind="component",context=True,
            label=port["label"]+" · bare retention nut"))
        if n=="co2-inlet":scene["instances"][-1]["role"]="gas"
        scene["mates"].extend([{"a":n,"b":n+"-nut","connection":"Retention nut on fitting barrel"},
                               {"a":n+"-nut","b":"back-wall","connection":"Nut seats at Y465.3"}])
        if n not in ("bulkhead-water","co2-inlet"):
            scene["instances"].append(base.instance(n+"-departure",n+"-departure",role="wet",kind="tube",context=True,
                label=port["label"]+" · local departure only"))
            scene["mates"].append({"a":n+"-departure","b":n,"connection":"Tube inserted in socket"})
    for m in scene["instances"]:
        if m["name"]=="water-in":m.update(geometry="grid-water-link",translation=[0.,0.,0.],rotation=I.tolist())
    scene["instances"].extend(gas.direct_instances(GAS_R,GAS_T,inlet_engagement_mm=INLET_ENGAGEMENT))
    _,junction,mouth,cap=gas_datums()
    scene["instances"].extend([
        base.instance("co2-inlet-link","co2-inlet-link",role="gas",kind="tube",context=True,label="CO₂ · concealed inlet tube"),
        base.instance("co2-turn","gas-stem-elbow",junction,ELBOW_R,role="gas",kind="elbow",context=True,
                      label="CO₂ · trimmed stem elbow · down to core"),
        base.instance("co2-core-drop","co2-core-drop",role="gas",kind="tube",context=True,
                      label="CO₂ · continuous tube through core guide")])
    scene["mates"].extend(gas.mates())
    scene["mates"].extend([
        {"a":"asse","b":"asse-inlet-tpu","connection":"TPU joint on ASSE inlet"},
        {"a":"asse","b":"asse-outlet-tpu","connection":"TPU joint on ASSE outlet"},
        {"a":"asse","b":"vent-sleeve","connection":"Sleeve on ASSE atmospheric port"},
        {"a":"pump","b":"pump-sliding-foot","connection":"Rubber slider on pump rail"},
        {"a":"pump","b":"pump-inlet-tpu","connection":"TPU elbow on pump barb"},
        {"a":"pump","b":"pump-outlet-tpu","connection":"TPU elbow on pump barb"},
        {"a":"co2-inlet-link","b":"co2-inlet","insertion_mm":12.7},
        {"a":"co2-inlet-link","b":"co2-adapter-regulator-in","insertion_mm":15.7},
        {"a":"co2-turn","b":"co2-adapter-check-out","connection":"Trimmed stem; shoulders meet","insertion_mm":15.7},
        {"a":"co2-core-drop","b":"co2-turn","insertion_mm":16.891}])
    names={m["name"] for m in scene["instances"]}
    scene["mates"]=[m for m in scene["mates"] if m["a"] in names and m["b"] in names
                    and not ({m["a"],m["b"]}=={"water-in","bulkhead-water"})]
    for m in scene["mates"]:
        if {m["a"],m["b"]}=={"water-in","asse-inlet-tpu"}:m["point"]=(np.array(scene["layout"]["asse_inlet_mouth_world_mm"])+FORE).tolist()
    scene["mates"].append({"a":"water-in","b":"bulkhead-water","point":[COLS[0],446.51,ROWS[0]],"insertion_mm":12.7})
    scene["pins"]=[p for p in scene["pins"] if not any(s in p["text"] for s in ("WAGO","Water in","Soda out","Flavor A","Flavor B","Faucet vent","CO2","CO₂"))]
    header_labels={"ASSE 1022","Pump","V-K","Regulator","V-A","ASSE inlet → back wall",
                   "To flavor manifold","To carbonator"}
    for p in scene["pins"]:
        if p["text"] in header_labels:p["at"]=(np.array(p["at"])+FORE).tolist()
        if p["text"] in ("V-K","V-A"):p["at"][1]=303.3397605281867+FORE[1]-27.
        if p["text"].startswith("Relay "):p["text"]=p["text"].replace(" · beneath PCB","")
    for arrow in scene["arrows"]:arrow["at"]=(np.array(arrow["at"])+FORE).tolist()
    scene["pins"].extend([
        {"text":"CO₂ regulator + check","at":[77.5,393.,334.376],"views":["three","top","gas"]},
        {"text":"CO₂ to core","at":cap.tolist(),"views":["gas"]}])
    scene.update(id="co2-grid",title="CO₂ connection and aligned rear ports")
    scene["layout"].update(water_header_translation_from_pcb_low_fore_mm=FORE.tolist(),
        va_head_direction=[0,-1,0],vk_head_direction=[0,-1,0],
        valve_clocking="Matching heads fore; vertical ports and all connected fitting axes held fixed",
        water_header_poses="Rigid group 7mm fore; matching valve bodies clocked 180 degrees about their own port axes",
        context_scope="Selected water header and CO2 chain, dry-side electronics with local leads, funnel/frame and ideal native walls/roof; WAGOs deferred, V-B and reservoir routes set aside",
        comparison_y_placement="Rear fittings seated in the common 6mm panel, water inlet straight to ASSE, gas drop registered to the fixed core guide",
        bulkhead_grid={"columns_x_mm":COLS,"rows_z_mm":ROWS,"column_pitch_mm":COLS[1]-COLS[0],"row_pitch_mm":32.,"assignment":ASSIGN},
        rear_panel={"outer_face_y_mm":471.3,"inner_pocket_floor_y_mm":465.3,"mounting_stock_mm":6.,"relief_side":"interior"},
        co2_flow="Rear bulkhead → inlet JG → regulator → directly threaded check → outlet JG → trimmed stem elbow → continuous core tube",
        co2_inlet_thread_engagement_mm=INLET_ENGAGEMENT,
        co2_datums={"inlet_mouth_mm":GAS_INLET.tolist(),"elbow_socket_mm":mouth.tolist(),"core_guide_mm":cap.tolist()},
        deferred_connections="Soda, vent and flavor ports show local departures; full onward routes are not placed")
    for key in ("va_inlet_world_mm","va_outlet_world_mm","flavor_mouth_world_mm","asse_inlet_mouth_world_mm"):
        scene["layout"][key]=(np.array(scene["layout"][key])+FORE).tolist()
    return scene


def check(scene,geometries):
    import fcl
    meshes=base.world_meshes(scene,geometries)
    objects={};bounds={}
    for name,(v,f) in meshes.items():
        model=fcl.BVHModel();model.beginModel(len(v),len(f));model.addSubModel(v,f.astype(np.int32));model.endModel()
        objects[name]=fcl.CollisionObject(model);bounds[name]=(v.min(0),v.max(0))
    mates={frozenset((m["a"],m["b"])) for m in scene["mates"]}
    # The two barb bands and two tube bands intentionally surround their TPU.
    for side in ("inlet","outlet"):
        for band in ("barb","tube"):
            mates.add(frozenset((f"pump-{side}-{band}-band",f"pump-{side}-tpu")))
    hits=[];names=list(meshes)
    for i,a in enumerate(names):
        lo,hi=bounds[a]
        for b in names[i+1:]:
            if frozenset((a,b)) in mates:continue
            low,high=bounds[b]
            if np.any(np.minimum(hi,high)-np.maximum(lo,low)<.001):continue
            if fcl.collide(objects[a],objects[b],fcl.CollisionRequest(),fcl.CollisionResult()):hits.append([a,b])
    def gap(a,b):return float(fcl.distance(objects[a],objects[b],fcl.DistanceRequest(),fcl.DistanceResult()))
    return {"scope":"Selected installed bodies, all tubes and local wires, bare nuts and native wall/roof context; intended interfaces excluded",
        "unrelated_interferences":hits,"selected_gaps_mm":{a+"_to_"+b:gap(a,b) for a,b in
            [("co2-core-drop","vk"),("co2-core-drop","pump"),("co2-turn","tee-fold"),("co2-turn","vk"),
             ("bulkhead-flavor-a-departure","pump"),("co2-inlet","ceiling"),("vk","funnel-frame"),
             ("va","funnel-frame"),("reg","ceiling"),("asse","ceiling")]},
        "grid":{"columns_x_mm":COLS,"rows_z_mm":ROWS,"row_pitch_mm":32.,"column_pitch_mm":COLS[1]-COLS[0]},
        "minimum_ceiling_stock_mm":3.,"co2_pocket_stock_mm":7.,"rear_fitting_mounting_stock_mm":6.,
        "gas_tube_cap_handoff_mm":gas_datums()[3].tolist(),
        "limits":"Thread make-up, socket insertions and formed local departures are estimates. Full onward soda/vent/flavor and complete wire routes are outside this selected arrangement."}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true");args=parser.parse_args()
    geometries=library();scene=pose(geometries)
    if args.check:scene["metrics"]=check(scene,geometries)
    (HERE/"study.json").write_text(json.dumps(scene,indent=2)+"\n")
    (HERE/"interfaces.json").write_text(json.dumps({"units":"mm","grid":grid(),
        "gas":gas.direct_ports(GAS_R,GAS_T,inlet_engagement_mm=INLET_ENGAGEMENT),"tube_path_mm":drop_points().tolist(),
        "selected_inlet_thread_engagement_mm":INLET_ENGAGEMENT,
        "gas_assumptions":{**gas.interfaces()["connection_assumptions"],
            "male_inlet_makeup":"11mm selected engagement; 3.3mm of published thread projection remains outside the regulator face"}},indent=2)+"\n")
    used={m["geometry"] for m in scene["instances"]}
    packed={n:base.pack(*geometries[n],12000 if n.startswith("connection-") else 5200 if n=="pump" else 3600) for n in sorted(used)}
    out=HERE/"out";out.mkdir(exist_ok=True)
    (out/"viewer-data.json").write_text(json.dumps({"space":parent.parent.parent.water.SPACE,
        "geometries":packed,"variants":[scene]},separators=(",",":")))
    print(json.dumps(scene.get("metrics",{}),indent=2))


if __name__=="__main__":main()
