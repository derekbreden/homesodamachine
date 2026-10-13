"""Materialize the reviewed proposal and its bounded geometry evidence."""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from scipy.spatial import ConvexHull

from layout import world, ROOT
from tpu_elbow import Elbow

HERE = Path(__file__).resolve().parent
CACHE = ROOT / ".cache/pump-elbow-exploration"
sys.path.insert(0, str(ROOT / "hardware/scripts"))
from _cadq_export import export_assembly
import _overlap
import _boxes


def main():
    w, base = world()
    plumbing = json.loads((CACHE/"layout-initial.json").read_text())
    funnel = json.loads((CACHE/"funnel-layout.json").read_text())
    packs = {}
    for folder in ("layout-initial", "funnel-layout"):
        packs[folder] = {p.stem: cq.Shape.importBrep(str(p)) for p in (CACHE/folder).glob("*.brep")}
    cross = []
    for na, sa in packs["layout-initial"].items():
        for nb, sb in packs["funnel-layout"].items():
            ba, bb = _boxes.loose(sa), _boxes.loose(sb)
            if any(getattr(ba,a+"max") < getattr(bb,a+"min") or
                   getattr(bb,a+"max") < getattr(ba,a+"min") for a in "xyz"):
                continue
            v = _overlap.volume(sa,sb)
            if v > 1e-5:
                cross.append({"a":na,"b":nb,"volume_mm3":v})
    record = {"status": "First article launched; physical result pending",
              "scope": "Nominal native occupancy, routed ends and R14 bends; closed clamp bands",
              "baseline_world_sha256": hashlib.sha256((CACHE/"world/world.json").read_bytes()).hexdigest(),
              "baseline_source_sha256":base["source_sha256"],
              "plumbing":plumbing,"funnel":funnel,"combined_candidate_overlaps":cross,
              "unmeasured": ["clamp wings and screw access", "printed cuff fit and insertion force",
                             "pressure holding", "wet tube retention", "relaxation and lifetime",
                             "complete insertion/service motion", "wetted grade suitability"]}
    (HERE/"placement.json").write_text(json.dumps(record,indent=2)+"\n")
    print("Combined candidate overlaps:",cross,flush=True)
    geometry = {}
    for name, depth in (("suction-elbow", 15), ("discharge-elbow", 15)):
        shape = Elbow(tube_depth=depth).print_shape()
        path = HERE/f"{name}.stl"
        cq.exporters.export(shape, str(path), tolerance=.01, angularTolerance=.05)
        cq.exporters.export(shape, str(HERE/f"{name}.step"))
        mesh = trimesh.load(path, force="mesh")
        degenerate = ~mesh.nondegenerate_faces()
        removed = int(degenerate.sum())
        if removed:
            mesh.update_faces(~degenerate)
            mesh.remove_unreferenced_vertices()
            mesh.export(path)
        mask = (mesh.face_normals[:,2] < -1e-5) & (mesh.triangles_center[:,2] > .02)
        angles = np.degrees(np.arccos(np.clip(-mesh.face_normals[mask,2], -1, 1)))
        geometry[name] = {"closed_stl":bool(mesh.is_watertight),
                          "consistent_winding":bool(mesh.is_winding_consistent),
                          "removed_zero_area_triangles":removed,
                          "valid_brep":shape.isValid(),
                          "solid_count":len(shape.Solids()),
                          "foot_area_mm2":sum(f.Area() for f in shape.Faces()
                              if f.geomType()=="PLANE" and abs(f.Center().z)<1e-5),
                          "minimum_downward_surface_angle_deg":float(angles.min()),
                          "volume_mm3":float(mesh.volume), "bounds_mm":mesh.bounds.tolist(),
                          "tube_insertion_mm":depth, "barb_insertion_mm":11,
                          "stl_sha256":hashlib.sha256(path.read_bytes()).hexdigest()}
    (HERE/"geometry.json").write_text(json.dumps(geometry,indent=2)+"\n")
    scene = cq.Assembly(name="pump-elbow-and-funnel-proposal")
    colors={"funnel":(.21,.59,.58),"frame":(.28,.32,.37),"elbow":(.18,.66,.74),
            "band":(.65,.68,.72),"link":(.92,.65,.25),"candidate":(.42,.48,.58)}
    for folder, parts in packs.items():
        for name, shape in parts.items():
            if name in ("back-top-funnel-opening", "funnel-cover-715ml"):
                continue
            color=next((v for k,v in colors.items() if k in name),(.72,.72,.76))
            scene.add(shape,name=name,color=cq.Color(*color))
    scene.add(w.solid("g-ganen-pump"),name="g-ganen-pump",color=cq.Color(.28,.28,.30))
    scene.add(w.solid("valve-v-a").fuse(w.solid("coil-v-a")),name="source-valve-a",color=cq.Color(.45,.45,.48))
    scene.add(w.solid("valve-v-b").fuse(w.solid("coil-v-b")),name="source-valve-b",color=cq.Color(.45,.45,.48))
    export_assembly(scene,str(HERE/"installed-proposal.step"))
    for name in ("funnel-715ml","funnel-frame-715ml","funnel-cover-715ml","back-top-funnel-opening"):
        cq.exporters.export(packs["funnel-layout"][name],str(HERE/f"{name}.step"))
    draw(packs,w)


def silhouette(shape, ax, color, alpha=1):
    vertices,_=shape.tessellate(.15)
    points=np.array([[v.x,v.y] for v in vertices])
    hull=ConvexHull(points)
    ax.fill(points[hull.vertices,0],points[hull.vertices,1],color=color,alpha=alpha,lw=0)


def draw(packs,w):
    fig,(a,b)=plt.subplots(1,2,figsize=(12,6),gridspec_kw={"width_ratios":[1,1.1]})
    fig.patch.set_facecolor("#f5f4ef")
    for ax in (a,b):
        ax.set_facecolor("#f5f4ef");ax.set_aspect("equal");ax.spines[['top','right']].set_visible(False)
    m=trimesh.load(HERE/"discharge-elbow.stl",force='mesh')
    section=m.section(plane_origin=(0,0,0),plane_normal=(0,1,0))
    for entity in section.entities:
        loop = section.vertices[entity.points]
        a.plot(loop[:,0],loop[:,2],color="#268d9b",lw=2)
    a.set_xlim(-22,22);a.set_ylim(-2,28);a.set_title("Printed elbow · centre section",loc="left",fontweight="bold")
    a.set_xlabel("mm");a.set_ylabel("mm above the bed")
    a.text(0,25.0,"Round cuffs · V print pose",ha="center",fontsize=10)
    a.text(0,-1.5,"Nominal wall 2.8 mm · entry wall 2.4 mm",ha="center",fontsize=9)
    silhouette(packs['funnel-layout']['funnel-715ml'],b,"#72b8ab",.22)
    silhouette(w.solid('g-ganen-pump'),b,"#4b5058",.4)
    for name in ('vk-candidate','check-water','check-in-PP010822E','check-out-PP450822E'):
        silhouette(packs['layout-initial'][name],b,"#747c89",.8)
    for name in ('elbow-suction','elbow-discharge'):
        silhouette(packs['layout-initial'][name],b,"#268d9b",1)
    data=json.loads((CACHE/'layout-initial.json').read_text())
    for name in ('suction-link','discharge-link','check-to-core'):
        pts=np.array(data['routes'][name]['points_mm'])
        b.plot(pts[:,0],pts[:,1],color="#b77416",lw=2)
    b.text(0,170,"715 mL bowl",ha="center",fontsize=11,color="#266d60")
    b.text(0,423,"Pump",ha="center",fontsize=11,color="#30343a")
    b.annotate("15 mm cuff",xy=(42,323),xytext=(78,318),fontsize=9,
               arrowprops={'arrowstyle':'-','color':'#268d9b'})
    b.annotate("15 mm cuff\nclocked 25° down",xy=(-42,324),xytext=(-105,339),fontsize=9,
               arrowprops={'arrowstyle':'-','color':'#268d9b'})
    b.set_xlim(-111,111);b.set_ylim(475,88);b.set_xlabel("enclosure X / mm")
    b.set_ylabel("enclosure Y / mm · front at top")
    b.set_title("Installed plan envelopes",loc="left",fontweight="bold")
    fig.suptitle("TPU pump elbows and a larger funnel",x=.07,ha="left",fontsize=16,fontweight="bold")
    fig.text(.07,.025,"Unprinted geometry proposal. Sealing, clamp wings and service motion remain unmeasured.",fontsize=10,color="#52575e")
    fig.tight_layout(rect=(0,.045,1,.95))
    fig.savefig(HERE/'proposal.png',dpi=180,facecolor=fig.get_facecolor())
    plt.close(fig)


if __name__=="__main__":
    main()
