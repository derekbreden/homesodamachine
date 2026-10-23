"""A down/up/down CO2 fold with native push-connect candidate devices.

This isolated arrangement preserves the selected water group and PCB poses.
The wet rear grid translates upward as a unit. The final continuous tube
uses a proposed new guide in the cold core's existing port lane.
"""
from pathlib import Path
import argparse
import copy
import importlib.util
import json

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


parent = module("fold_parent_tpu", HERE.parent / "co2-tpu/study.py")
base = parent.base
I = np.eye(3)
UP, FORE = np.array([0., 0., 1.]), np.array([0., -1., 0.])
GRID_SHIFT = np.array([0., 0., 4.])
EXPOSED_INLET = 16.
STEM_TO_CORNER, SOCKET_TO_CORNER = 6.0452, 19.05
PITCH = STEM_TO_CORNER + SOCKET_TO_CORNER
REG_LENGTH, CHECK_LENGTH = 62.4, 45.5
REF = ROOT / "hardware/reference/compact-inline-candidates/geometry"
OLD_GAS = {"wr1110", "gasher-co2", "co2-inlet-link", "co2-core-drop"}


def grid():
    rows = copy.deepcopy(parent.parent.grid())
    for row in rows:
        row["center_z_mm"] += GRID_SHIFT[2]
        row["inboard_mouth_mm"] = (np.array(row["inboard_mouth_mm"]) + GRID_SHIFT).tolist()
    return rows


def elbow_rotation(stem_direction, socket_direction):
    x, y = -np.array(stem_direction), np.array(socket_direction)
    return np.column_stack([x, y, np.cross(x, y)])


def datums():
    inlet = parent.GAS_INLET + GRID_SHIFT
    c0 = inlet - [0., SOCKET_TO_CORNER + EXPOSED_INLET, 0.]
    reg_in = c0 - STEM_TO_CORNER * UP
    reg_out = reg_in - REG_LENGTH * UP
    c1 = reg_out - STEM_TO_CORNER * UP
    c2 = c1 + PITCH * FORE
    check_in = c2 + SOCKET_TO_CORNER * UP
    check_out = check_in + CHECK_LENGTH * UP
    c3 = check_out + STEM_TO_CORNER * UP
    c4 = c3 + PITCH * FORE
    drop = c4 - SOCKET_TO_CORNER * UP
    guide = np.array([drop[0], drop[1], 253.4])
    return {k: v for k, v in locals().items() if isinstance(v, np.ndarray)}


def rows():
    d = datums()
    items = []
    for name, geometry, center, male, female in (
        ("gas-inlet-elbow", "elbow-regulator", "c0", -UP, -FORE),
        ("gas-lower-a", "elbow-regulator", "c1", UP, FORE),
        ("gas-lower-b", "elbow-elbow", "c2", -FORE, UP),
        ("gas-upper-a", "elbow-check", "c3", -UP, FORE),
        ("gas-upper-b", "elbow-elbow", "c4", -FORE, -UP),
    ):
        items.append(base.instance(name, geometry, translation=d[center], rotation=elbow_rotation(male, female),
                     kind="component", role="stem", context=True, gas_fold=True,
                     label="Trimmed stem elbow · " + name.removeprefix("gas-")))
    items.extend([
        base.instance("gas-regulator", "candidate-regulator", translation=d["reg_in"], rotation=np.diag([1., -1., -1.]),
            kind="component", role="gas-regulator", context=True, gas_fold=True,
            label="PISCO RVFUP1/4-1/4-0.3 · regulator · flow down"),
        base.instance("gas-check", "candidate-check", translation=d["check_in"], rotation=I,
            kind="component", role="gas-check", context=True, gas_fold=True,
            label="Fluidfit HCVU1/4-1/4G · check valve · flow up"),
    ])
    for name in ("gas-inlet-tube", "gas-check-link", "gas-core-drop"):
        items.append(base.instance(name, name, role="gas", kind="tube", context=True,
                     gas_fold=True, label={
                         "gas-inlet-tube": "CO₂ inlet · 16 mm exposed at external handoff",
                         "gas-check-link": "Concealed tube · elbow to check inlet",
                         "gas-core-drop": "Continuous CO₂ tube · proposed cap-guide position",
                     }[name]))
    return items


def library():
    g = parent.library()
    for folder in (HERE / "parts", REF):
        for path in sorted(folder.glob("*.npz")):
            with np.load(path) as data:
                g[path.stem] = data["v"].copy(), data["f"].copy()
    d = datums()
    tube = parent.parent.tube
    g["gas-inlet-tube"] = tube([d["inlet"] - 12.7*FORE,
        d["c0"] + [0., SOCKET_TO_CORNER - 16.891, 0.]], 3.175, 2.12)
    g["gas-check-link"] = tube([d["check_in"] - 16.891*UP,
                               d["check_in"] + 16.1*UP], 3.175, 2.12)
    g["gas-core-drop"] = tube([d["drop"] + 16.891*UP,
                              d["guide"] - 12.*UP], 3.175, 2.12)
    source = parent.pose(g)
    mouth = np.array(source["layout"]["asse_inlet_mouth_world_mm"])
    end = np.array(grid()[0]["inboard_mouth_mm"])
    # Horizontal at both socket faces; the external water feed rises gently
    # over its existing span to meet the translated grid.
    t = np.linspace(0., 1., 33)
    line = mouth + t[:, None]*(end-mouth)
    line[:, 2] = mouth[2] + (t*t*(3.-2.*t))*(end[2]-mouth[2])
    g["fold-water-link"] = tube(np.vstack([mouth-[0.,15.,0.], line,
                                         end+[0.,12.7,0.]]), 3.175, 2.12)
    ports = {p["name"]: p for p in grid()}
    drain = np.array(ports["bulkhead-drain"]["inboard_mouth_mm"])
    g["fold-drain-departure"] = tube([drain+[0.,10.,0.], drain-[0.,15.,0.]], 2., 1.25)
    soda = np.array(ports["bulkhead-carb"]["inboard_mouth_mm"])
    soda_corner = soda - [0., STEM_TO_CORNER, 0.]
    soda_mouth = soda_corner - [SOCKET_TO_CORNER, 0., 0.]
    g["fold-soda-departure"] = tube([soda_mouth+[16.891,0.,0.],
                                    soda_mouth-[15.,0.,0.]], 3.175, 2.12)
    return g


def pose(g):
    scene = parent.pose(g)
    scene["instances"] = [m for m in scene["instances"]
                          if m["name"] not in OLD_GAS and not m.get("co2_group")]
    wet_names = {p["name"] for p in grid()}
    for m in scene["instances"]:
        n = m["name"]
        if n in wet_names or n.removesuffix("-nut") in wet_names or n.removesuffix("-departure") in wet_names:
            m["translation"] = (np.array(m["translation"]) + GRID_SHIFT).tolist()
            if "center_z_mm" in m:
                m["center_z_mm"] += GRID_SHIFT[2]
        if n == "water-in":
            m.update(geometry="fold-water-link", rotation=I.tolist(), translation=[0.,0.,0.])
        if n == "bulkhead-drain-departure":
            m.update(geometry="fold-drain-departure", rotation=I.tolist(), translation=[0.,0.,0.],
                     label="Vent/drain · straight local departure; full route deferred")
        if n == "bulkhead-carb-departure":
            m.update(geometry="fold-soda-departure", rotation=I.tolist(), translation=[0.,0.,0.],
                     label="Soda · local west departure from stem elbow")
    soda = next(p for p in grid() if p["name"] == "bulkhead-carb")
    scene["instances"].append(base.instance("soda-stem-elbow", "elbow-bulkhead",
        rotation=elbow_rotation(-FORE, [-1.,0.,0.]),
        translation=np.array(soda["inboard_mouth_mm"]) + STEM_TO_CORNER*FORE,
        kind="component", context=True, role="wet", label="Soda outlet · trimmed stem elbow points west"))
    scene["instances"].extend(rows())
    names = {m["name"] for m in scene["instances"]}
    scene["mates"] = [m for m in scene["mates"] if m["a"] in names and m["b"] in names]
    for a,b in (
        ("co2-inlet","gas-inlet-tube"), ("gas-inlet-tube","gas-inlet-elbow"),
        ("gas-inlet-elbow","gas-regulator"), ("gas-regulator","gas-lower-a"),
        ("gas-lower-a","gas-lower-b"), ("gas-lower-b","gas-check-link"),
        ("gas-check-link","gas-check"), ("gas-check","gas-upper-a"),
        ("gas-upper-a","gas-upper-b"), ("gas-upper-b","gas-core-drop"),
        ("bulkhead-carb","soda-stem-elbow"), ("soda-stem-elbow","bulkhead-carb-departure"),
    ):
        scene["mates"].append({"a":a,"b":b,"connection":"Intended fully seated socket or concealed tube"})
    scene.update(id="co2-fold", title="CO₂ · down / up / down")
    scene["pins"] = []
    scene["layout"].update(
        co2_flow="Bulkhead → 90° down → PISCO regulator → 180° up → Fluidfit check → 180° down → proposed core guide",
        co2_route_status="Layout candidate: proposed new cap guide remains unimplemented below the crown",
        co2_datums={k:v.tolist() for k,v in datums().items()},
        wet_grid_translation_from_co2_tpu_mm=GRID_SHIFT.tolist(),
        inlet_exposed_tube_mm=EXPOSED_INLET,
        new_cap_guide_world_mm=datums()["guide"].tolist(),
        existing_cap_guide_world_mm=parent.parent.gas.cap_handoff()["point_mm"],
        device_selection="Geometry candidates; PISCO CO₂ suitability and immediate dispatch remain unconfirmed",
        bulkhead_grid={**scene["layout"]["bulkhead_grid"],
                       "rows_z_mm":[z+GRID_SHIFT[2] for z in parent.parent.ROWS]},
    )
    scene["layout"].pop("co2_clamps",None)
    return scene


def check(scene, g):
    import fcl
    meshes = base.world_meshes(scene, g)
    objects, bounds = {}, {}
    for name,(v,f) in meshes.items():
        model=fcl.BVHModel(); model.beginModel(len(v),len(f))
        model.addSubModel(v,f.astype(np.int32)); model.endModel()
        objects[name]=fcl.CollisionObject(model);bounds[name]=(v.min(0),v.max(0))
    mates={frozenset((m["a"],m["b"])) for m in scene["mates"]}
    for side in ("inlet","outlet"):
        for band in ("barb","tube"):
            mates.add(frozenset((f"pump-{side}-{band}-band",f"pump-{side}-tpu")))
    hits=[]; names=list(meshes)
    for i,a in enumerate(names):
        for b in names[i+1:]:
            if frozenset((a,b)) in mates: continue
            if np.any(np.minimum(bounds[a][1],bounds[b][1])-np.maximum(bounds[a][0],bounds[b][0])<.001): continue
            if fcl.collide(objects[a],objects[b],fcl.CollisionRequest(),fcl.CollisionResult()): hits.append([a,b])
    hardware=[m["name"] for m in rows() if m["kind"]!="tube"]
    v=np.vstack([meshes[n][0] for n in hardware])
    return {"scope":"Selected exterior meshes and local departures; intended socket mates excluded",
            "unrelated_interferences":hits,
            "fold_hardware_bounds_mm":[v.min(0).tolist(),v.max(0).tolist()],
            "fold_hardware_size_mm":(v.max(0)-v.min(0)).tolist(),
            "fold_hardware_floor_gap_mm":float(v[:,2].min()-253.4),
            "fold_hardware_to_plain_ceiling_mm":float(346.-v[:,2].max()),
            "minimum_pocket_roof_stock_mm":3.,
            "scope_limit":"Cap guide is proposed; its below-cap route is not modeled or migrated. Device service suitability, stem fits and dispatch are not established by this exterior query."}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument("--check",action="store_true")
    args=parser.parse_args();g=library();scene=pose(g)
    if args.check:scene["metrics"]=check(scene,g)
    (HERE/"study.json").write_text(json.dumps(scene,indent=2)+"\n")
    (HERE/"interfaces.json").write_text(json.dumps({"units":"mm","grid":grid(),
        "stem_insertions_mm":{"regulator":17.,"check":16.1,"elbow":16.891,"soda_bulkhead_estimate":12.7},
        "flow":"down through regulator, up through check, down into core",
        "datums":{k:v.tolist() for k,v in datums().items()},
        "existing_cap_guide_world_mm":parent.parent.gas.cap_handoff()["point_mm"],
        "cap_guide_scope":"Proposed relocation along the existing gas port lane; not implemented in the core",
        "external_input_exposed_mm":EXPOSED_INLET,"grid_translation_mm":GRID_SHIFT.tolist(),
        "new_reference_models":"hardware/reference/compact-inline-candidates",
    },indent=2)+"\n")
    used={m["geometry"] for m in scene["instances"]}
    packed={n:base.pack(*g[n],12000 if n.startswith("connection-") else 5200 if n=="pump" else 3600) for n in sorted(used)}
    out=HERE/"out";out.mkdir(exist_ok=True)
    (out/"viewer-data.json").write_text(json.dumps({"geometries":packed,"variants":[scene],"grid":grid()},separators=(",",":")))
    print(json.dumps(scene.get("metrics",{}),indent=2))


if __name__=="__main__":main()
