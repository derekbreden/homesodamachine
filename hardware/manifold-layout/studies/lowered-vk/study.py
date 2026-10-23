"""Lower V-K beside the pump and bring the ASSE directly over the pump.

Mesh-only free-space study. Connections, nearest body gaps and pump-foot-plane
clearance guide the poses. No production enclosure geometry is modified.
"""
from pathlib import Path
import argparse
import importlib.util
import json
import math

import numpy as np

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("stem_layout", HERE.parent / "stem-fittings/study.py")
base = importlib.util.module_from_spec(spec)
spec.loader.exec_module(base)
I = np.eye(3)
UPPER = base.ASSE_GROUP | base.FLAVOR_GROUP | {"tee", "tee-fold"}
INLET = {"pump-inlet-tpu", "pump-inlet-barb-band", "pump-inlet-tube-band"}
RX90 = np.array([[1, 0, 0], [0, 0, -1], [0, 1, 0]])


def rx(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])


def rz(angle):
    c, s = math.cos(angle), math.sin(angle)
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])


def library():
    result = base.library()
    with np.load(HERE / "parts/stem-elbow-neofit-host.npz") as data:
        result["stacked-elbow"] = (data["v"], data["f"])
    return result


def pose(kind="inward"):
    angle = math.radians(25)
    q = np.array([0, math.cos(angle), -math.sin(angle)])
    shoulder = -base.ED["stem_shoulder"][0][0]
    socket = base.ED["socket"][0][1]
    pump_offset = np.array([-4.916132605004726, 0, 0])
    pump_mouth = pump_offset + 18.5 * q
    pump_elbow = pump_mouth + socket * q
    valve_elbow = pump_elbow - [socket + shoulder, 0, 0]
    valve_bottom = valve_elbow + [0, 0, shoulder]
    valve_delta = valve_bottom - np.array([-4.916132605004726, 0, 18.5])
    valve_top = valve_bottom + [0, 0, 59.5]
    header_axis = valve_top + [0, 0, shoulder]
    header_rotation = rz(math.radians(20 if kind == "inward" else 0))
    scene = base.variant("neofit-branch")
    scene["id"] = kind
    scene["title"] = "ASSE over motor" if kind == "inward" else "ASSE orientation preserved"
    for m in scene["instances"]:
        n = m["name"]
        p, r = np.array(m["translation"]), np.array(m["rotation"])
        if n in UPPER | {"vk"}:
            p += valve_delta
        if n in INLET:
            r = rx(-math.pi / 2 - angle)
            m["label"] = "Existing TPU pump elbow · clocked 25° downward toward +Y" if n == "pump-inlet-tpu" else m["label"]
        if n in {"reg", "va"}:
            # Rotate about the fluid run, keeping all port mouths fixed.
            p = header_axis + RX90 @ (p - header_axis)
            r = RX90 @ r
            m["label"] += " · head clocked outward"
        if n in UPPER:
            p = valve_top + header_rotation @ (p - valve_top)
            r = header_rotation @ r
        m["translation"], m["rotation"] = p.tolist(), r.tolist()
        if n == "vk":
            m["label"] = "V-K · lowered, vertical ports, head still −Y"
        if n == "asse":
            m["label"] = "ASSE 1022 · directly over pump" + (" · upper group clocked 20° inward" if kind == "inward" else " · orientation preserved")
    # Valve-side male stem enters V-K; its female socket accepts the second stem.
    r_valve = np.column_stack(([0, 0, -1], [1, 0, 0], [0, -1, 0]))
    x, y = np.array([1, 0, 0]), -q
    r_pump = np.column_stack((x, y, np.cross(x, y)))
    scene["instances"].extend([
        base.instance("lower-valve-elbow", "stem-elbow-trimmed", valve_elbow, r_valve,
                      role="stem", kind="elbow", label="Valve-side stem elbow · directly into V-K"),
        base.instance("lower-pump-elbow", "stacked-elbow", pump_elbow, r_pump,
                      role="stem", kind="elbow", label="Pump-side stem elbow · stem plugs into the other elbow"),
    ])
    mates = []
    for j in scene["mates"]:
        if {j["a"], j["b"]} == {"vk", "pump-inlet-tpu"}:
            continue
        if j["a"] in UPPER or j["b"] in UPPER:
            j["point"] = (valve_top + header_rotation @ (np.array(j["point"]) + valve_delta - valve_top)).tolist()
        mates.append(j)
    stacked_mouth = valve_elbow + [socket, 0, 0]
    mates.extend([
        {"a": "pump-inlet-tpu", "b": "lower-pump-elbow", "point": pump_mouth.tolist(),
         "connection": "female mouths connected by concealed tube", "concealed_tube_length_mm": 31.891,
         "exposed_tube_mm": 0},
        {"a": "lower-pump-elbow", "b": "lower-valve-elbow", "point": stacked_mouth.tolist(),
         "connection": "male stem into NeoFit socket", "insertion_mm": 16.891,
         "shoulder_gap_mm": 0, "exposed_tube_mm": 0},
        {"a": "lower-valve-elbow", "b": "vk", "point": valve_bottom.tolist(),
         "connection": "male stem into valve socket", "insertion_mm": 12.7,
         "shoulder_gap_mm": 0, "exposed_tube_mm": 0},
    ])
    scene["mates"] = mates
    # Shift direct labels and arrows with the body they describe.
    pins = []
    upper_pins = {"ASSE 1022", "Tee", "Regulator", "V-A", "Water in", "To flavor manifold", "Vent to faucet", "Stem elbow"}
    for p in scene["pins"]:
        t, at = p["text"], np.array(p["at"])
        if t.startswith("+"):
            continue
        if t.startswith("V-K"):
            at += valve_delta
        elif t in upper_pins:
            at += valve_delta
            if t in {"Regulator", "V-A"}:
                at = header_axis + RX90 @ (at - header_axis)
            at = valve_top + header_rotation @ (at - valve_top)
        p["at"] = at.tolist()
        if t == "Stem elbow":
            p.update(text="Upper elbow", offset=[-65, -18])
        pins.append(p)
    pins.append({"text": "Two stacked elbows", "at": ((valve_elbow + pump_elbow) / 2).tolist(),
                 "short": "Stacked elbows", "offset": [-70, 18]})
    scene["pins"] = pins
    for a in scene["arrows"]:
        p = np.array(a["at"])
        if a["role"] == "flavor" or (a["role"] == "neutral" and p[1] < -35 and p[2] > 60):
            a["at"] = (valve_top + header_rotation @ (p + valve_delta - valve_top)).tolist()
            a["dir"] = (header_rotation @ a["dir"]).tolist()
    # Omit the old position of the direction guide; put it beside the inlet.
    scene["arrows"] = [a for a in scene["arrows"] if a["at"] != [140, 30, -15]]
    scene["layout"] = {"pump_tpu_clock_degrees_below_plus_y": 25,
                       "upper_group_clock_degrees": 20 if kind == "inward" else 0,
                       "vk_translation_mm": valve_delta.tolist(), "vk_head_direction": [0, -1, 0],
                       "vk_ports_axis": [0, 0, 1], "vk_bottom_mouth_mm": valve_bottom.tolist(),
                       "pump_mouth_mm": pump_mouth.tolist(), "pump_elbow_junction_mm": pump_elbow.tolist(),
                       "valve_elbow_junction_mm": valve_elbow.tolist()}
    return scene


def surface_distance(a, b):
    import fcl
    objects = []
    for v, f in (a, b):
        model = fcl.BVHModel(); model.beginModel(len(v), len(f))
        model.addSubModel(v, f.astype(np.int32)); model.endModel()
        objects.append(fcl.CollisionObject(model))
    return float(fcl.distance(*objects, fcl.DistanceRequest(), fcl.DistanceResult()))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    geometries = library()
    reference = base.variant("run")
    reference.update(id="reference", title="Previous arrangement")
    scenes = [pose("inward"), pose("straight"), reference]
    report = {"scope": "Free-space relationship study for pump, V-K and ASSE; supports and enclosure omitted",
              "objective": "Bring ASSE close above pump with V-K vertical and its head toward −Y",
              "units": "mm", "variants": {}}
    for scene in scenes:
        meshes = base.world_meshes(scene, geometries)
        pump = meshes["pump"][0]
        floor, crown = float(pump[:, 2].min()), float(pump[:, 2].max())
        elbows = ["lower-pump-elbow", "lower-valve-elbow"] if scene["id"] != "reference" else ["pump-inlet-tpu"]
        metrics = {"pump_support_plane_z_mm": floor, "pump_crown_z_mm": crown,
                   "asse_bottom_z_mm": float(meshes["asse"][0][:, 2].min()),
                   "inlet_fittings_above_support_plane_mm": min(float(meshes[n][0][:, 2].min()) for n in elbows) - floor}
        if args.check:
            metrics["asse_to_pump_surface_gap_mm"] = surface_distance(meshes["asse"], meshes["pump"])
            metrics["unrelated_body_interferences"] = base.interference(scene, geometries)
        scene["metrics"] = metrics
        report["variants"][scene["id"]] = {"layout": scene.get("layout"), "metrics": metrics,
                                             "interfaces": scene["mates"], "instances": scene["instances"]}
    (HERE / "study.json").write_text(json.dumps(report, indent=2) + "\n")
    # Display only the geometries these three scenes use.
    used = {m["geometry"] for s in scenes for m in s["instances"]}
    packed = {n: base.pack(*geometries[n], 5200 if n == "pump" else 3600) for n in sorted(used)}
    out = HERE / "out"; out.mkdir(exist_ok=True)
    (out / "viewer-data.json").write_text(json.dumps({"geometries": packed, "variants": scenes}, separators=(",", ":")))
    print(json.dumps({s["id"]: s["metrics"] for s in scenes}, indent=2))


if __name__ == "__main__":
    main()
