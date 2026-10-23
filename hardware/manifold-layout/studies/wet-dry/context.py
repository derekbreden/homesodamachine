"""Plain wall and roof solids for the wet/dry arrangement study.

Panel cuts establish occupied space. Connector retention, the removable PCB
carrier and production fastening details are outside this study.
"""
from pathlib import Path
import importlib.util
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent


def box(x0, x1, y0, y1, z0, z1):
    return cq.Solid.makeBox(x1-x0, y1-y0, z1-z0, cq.Vector(x0,y0,z0))


def build():
    layout = json.loads((HERE / "layout.json").read_text())
    left = box(-107.5,-98.5,244,471.3,253.4,346)
    right = box(98.5,107.5,244,471.3,253.4,346)
    back = box(-98.5,98.5,462.3,471.3,253.4,346)
    # One flat exterior recess serves the six bare fittings; retained panel is 6 mm.
    back = back.cut(box(20,94,468.3,471.31,256,347))
    for p in layout["wet_ports"]:
        bore = cq.Solid.makeCylinder(p["bore_diameter_mm"]/2, 9.02,
            cq.Vector(p["center_x_mm"],462.29,p["center_z_mm"]),cq.Vector(0,1,0))
        back = back.cut(bore)
    by_name = {p["name"]:p for p in layout["instances"]}
    sources = json.loads((HERE / "source-inventory.json").read_text())["parts"]
    c14 = by_name["c14-inlet"]
    datum = np.array(sources["c14-inlet"]["native_to_original_world"]["translation_mm"])
    center = np.array(c14["rotation"]) @ datum + c14["translation"]
    x,y,z = center
    # Scanned flange pocket, manufacturer opening envelope and actual 40.21 mm pitch.
    back = back.cut(box(x-25.135,x+25.135,468.05,471.31,z-11.2,z+11.2))
    back = back.cut(box(x-15.725,x+15.725,462.29,471.31,z-11.325,z+11.325))
    for dx in (-20.105,20.105):
        back = back.cut(cq.Solid.makeCylinder(1.7,9.02,cq.Vector(x+dx,462.29,z),cq.Vector(0,1,0)))
    # Bare keystone occupancy opening only; a clip/retainer is not specified here.
    k = by_name["keystone-jack"]
    with np.load(HERE / "parts/keystone-jack.npz") as d:
        v = d["v"] @ np.array(k["rotation"]).T + k["translation"]
    low, high = v.min(0),v.max(0)
    back = back.cut(box(low[0]-.25,high[0]+.25,462.29,471.31,low[2]-.25,high[2]+.25))
    spec = importlib.util.spec_from_file_location("study_ceiling",HERE.parent / "ceiling-fit/ceiling.py")
    ceiling = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ceiling)
    return {"left-wall":left,"right-wall":right,"back-wall":back.clean(),
            "ceiling":ceiling.build(HERE / "ceiling-plan.json")}


def main():
    out = HERE / "parts"
    for name, shape in build().items():
        cq.exporters.export(shape,str(out / (name + ".step")))
        vertices, faces = shape.tessellate(.08,.12)
        np.savez_compressed(out / (name + ".npz"),v=np.array([p.toTuple() for p in vertices],dtype=np.float32),f=np.array(faces,dtype=np.uint32))
        bb = shape.BoundingBox()
        report = {"units":"mm","valid":bool(shape.isValid()),"solid_count":len(shape.Solids()),
            "volume_mm3":shape.Volume(),"bounds_mm":[[bb.xmin,bb.ymin,bb.zmin],[bb.xmax,bb.ymax,bb.zmax]],
            "scope":"Plain study context; final equipment carrier and connector retention not designed"}
        (out / (name + ".report.json")).write_text(json.dumps(report,indent=2)+"\n")
        print(name,report["valid"],report["solid_count"])


if __name__ == "__main__":
    main()
