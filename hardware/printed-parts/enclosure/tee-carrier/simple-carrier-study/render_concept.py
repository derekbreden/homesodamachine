"""Native tessellation illustration of the carrier assembly-trial candidate."""
from pathlib import Path
import json
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import LightSource
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from build_concept import box

HERE=Path(__file__).resolve().parent
BLUE="#3e7eae"
ORANGE="#d5893f"


def triangles(s):
    v,f=s.tessellate(.12)
    v=np.array([p.toTuple() for p in v])
    return v[np.array(f)]


def body(ax,s,color):
    ax.add_collection3d(Poly3DCollection(triangles(s),facecolors=color,
         edgecolors=color,linewidths=0,shade=True,
         lightsource=LightSource(azdeg=315,altdeg=45)))


def setup(ax,xs,ys,zs,elev,azim):
    ax.set_xlim(xs); ax.set_ylim(ys); ax.set_zlim(zs)
    ax.set_box_aspect((xs[1]-xs[0],ys[1]-ys[0],zs[1]-zs[0]))
    ax.view_init(elev=elev,azim=azim)
    ax.set_axis_off()


def planar(ax,s,color,axes=(0,1)):
    from matplotlib.collections import PolyCollection
    mesh=triangles(s)
    ax.add_collection(PolyCollection(mesh[:,:,axes],facecolors=color,
                                    edgecolors="none",linewidths=0))


def main():
    I=json.loads((HERE/"inputs/manifest.json").read_text())["interface"]
    L=cq.importers.importStep(str(HERE/"left-concept.step")).val()
    R=cq.importers.importStep(str(HERE/"right-concept.step")).val()
    fig=plt.figure(figsize=(14,10),facecolor="#faf9f6")
    fig.suptitle("Simple carrier concept • two parts, no separate fastening step",fontsize=20,x=.04,ha="left",y=.965)
    fig.text(.04,.923,"Native geometry • measured tee datums • full-enclosure trial candidate",fontsize=11,color="#555")
    a=fig.add_axes((.02,.50,.58,.38),projection="3d")
    body(a,L,BLUE);body(a,R,ORANGE)
    setup(a,(-110,110),(86,150),(162,234),26,-67)
    a.set_title("Assembled beam · 215 mm overall width",loc="left",fontsize=13)
    b=fig.add_axes((.58,.50,.40,.38),projection="3d")
    clip=box((-40,40),(100,149),(164,234))
    body(b,L.intersect(clip),BLUE)
    body(b,R.intersect(clip).translate((0,20,8)),ORANGE)
    setup(b,(-40,40),(98,175),(164,242),28,65)
    b.set_title("Centre exploded · view from rear",loc="left",fontsize=13)
    c=fig.add_axes((.07,.135,.39,.28),facecolor="#faf9f6")
    slab=box((-18,18),(100,117),(187.99,188.01))
    planar(c,L.intersect(slab),BLUE);planar(c,R.intersect(slab),ORANGE)
    c.set_xlim(-18,18);c.set_ylim(100,117);c.set_aspect("equal")
    c.set_xlabel("X across carrier (mm)");c.set_ylabel("Y toward rear (mm)")
    c.set_title("Broad lap + captured rail · section Z188",loc="left",fontsize=12)
    c.spines[["top","right"]].set_visible(False)
    c.annotate("26.35 mm fore lap",(0,102.29),(0,100.8),ha="center",fontsize=10,
               arrowprops={"arrowstyle":"-","color":"#555"})
    d=fig.add_axes((.59,.135,.35,.28),facecolor="#faf9f6")
    x,z=I["spring_stations"][1]["x"],I["spring_stations"][1]["z"]
    fixed=cq.importers.importStep(str(HERE/"fixed-cup-local-section.step")).val()
    slab=box((x-7,x+8),(86,117),(z-.01,z+.01))
    planar(d,fixed.intersect(slab),BLUE,axes=(1,0))
    planar(d,R.translate((0,4.5,0)).intersect(slab),ORANGE,axes=(1,0))
    floor=I["fixed_seat_floor_y"]
    end=I["spring_stations"][1]["bore_floor_y"]+4.5
    d.plot([floor,end,end,floor,floor],[x-3,x-3,x+3,x+3,x-3],"--",color="#333",lw=1)
    d.set_xlim(86,117);d.set_ylim(x-7,x+8);d.set_aspect("equal")
    d.set_xlabel("Y along spring (mm)");d.set_ylabel("X across cup (mm)")
    d.set_title("Closed cups at aft stop · section through axis",loc="left",fontsize=12)
    d.spines[["top","right"]].set_visible(False)
    d.annotate("4.75 mm mouth gap",((98.04+102.79)/2,x+3.3),
               ((98.04+102.79)/2,x+6.2),ha="center",fontsize=10,
               arrowprops={"arrowstyle":"-","color":"#555"})
    fig.text(.04,.055,"Blue: left half / integral fixed cup     Orange: right half     Dashed: Ø6 spring envelope",fontsize=10)
    fig.text(.04,.028,"Native routes clear on the frozen wall. Full-enclosure trial: printed fit, support removal, whole-span bending and real spring retention.",
             fontsize=10,color="#7b3b2b")
    fig.savefig(HERE/"concept-overview.png",dpi=160,facecolor=fig.get_facecolor())


if __name__=="__main__":main()
