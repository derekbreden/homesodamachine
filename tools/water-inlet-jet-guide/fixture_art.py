"""Assembly pictures from the two issued drilling-fixture STL files.

Face projection is a small vector renderer, not a fixture redesign. The loose
jaw is rotated only in the separate part-identification picture; assembly
pictures keep its groove facing the fixed jaw.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
import math

import numpy as np
import trimesh

from common import *
from jet_art import Iso, tag, elbow, cap, gun, DARK_STEEL, LIGHT_STEEL

ROOT = Path(__file__).resolve().parents[2]
PARTS = ROOT / "hardware/printed-parts/fixtures/water-inlet-jet"
# Populated by the guide from the scalar CAD sources, without importing CAD.
FIXTURE = {}
ROD_D = None


@lru_cache
def mesh(name):
    return trimesh.load(PARTS / f"water-inlet-jet-fixture-{name}.stl", force="mesh")


def item(name, fill=STEEL, move=(0,0,0), flip=False):
    m=mesh(name).copy()
    if flip:
        m.apply_transform(trimesh.transformations.rotation_matrix(math.pi,[0,0,1]))
    m.apply_translation(move)
    return m,fill


def shade(fill, normal):
    light=np.array([-.15,-.4,1]);light/=np.linalg.norm(light)
    gain=.76+.24*max(0,float(np.dot(normal,light)))
    rgb=[int(fill[j:j+2],16) for j in (1,3,5)]
    return '#'+''.join(f'{min(255,round(v*gain)):02x}' for v in rgb)


def paint(a, i, items):
    """Paint true mesh faces back-to-front, with only feature/silhouette edges."""
    view=-np.cross([i.sx,i.sy,0],[i.dx,i.dy,-i.sz]);view/=np.linalg.norm(view)
    faces=[]
    for m,fill in items:
        visible=m.face_normals@view > 1e-8
        feature={tuple(sorted(edge)) for edge in m.edges_unique[m.edges_unique_inverse[np.flatnonzero(np.repeat(visible,3))]]}
        # Coplanar tessellation diagonals do not become drawn part edges.
        flat=set()
        for pair,edge in zip(m.face_adjacency,m.face_adjacency_edges):
            if float(np.dot(m.face_normals[pair[0]],m.face_normals[pair[1]]))>.94:
                flat.add(tuple(sorted(edge)))
        feature-=flat
        for idx in np.flatnonzero(visible):
            verts=m.faces[idx];xyz=m.vertices[verts]
            outline=[]
            for j in range(3):
                if tuple(sorted((verts[j],verts[(j+1)%3]))) in feature:
                    outline.append((xyz[j],xyz[(j+1)%3]))
            faces.append((float(xyz.mean(axis=0)@view),xyz,shade(fill,m.face_normals[idx]),outline))
    for _,xyz,fill,edges in sorted(faces,key=lambda f:f[0]):
        a.shape([i.p(*v) for v in xyz],fill,fill,.15)
        for p,q in edges:a.line(*i.p(*p),*i.p(*q),INK,.75)


def print_parts(a):
    a.label("1  FIXED JAW + BASE",137,22,12,BLUE,align="center")
    a.label("2  LOOSE JAW",415,22,12,BLUE,align="center")
    left=Iso(a,origin=(139,254),sx=1.55,sy=.7,dx=.43,dy=-.36,sz=2)
    right=Iso(a,origin=(409,239),sx=2.15,sy=.9,dx=.54,dy=-.43,sz=2.7)
    paint(a,left,[item("fixed")])
    paint(a,right,[item("loose",ICE,flip=True)])
    a.label("half-round groove",16,65,11,BLUE)
    a.arrow(119,72,*left.p(0,4.9,28),BLUE,1)
    a.label("matching groove",333,64,11,BLUE)
    a.arrow(433,71,*right.p(0,4.9,23),BLUE,1)
    a.label("base stays attached",138,316,11,BLUE,align="center")
    a.label("shown from groove side",415,291,10.5,BLUE,align="center")
    a.label("flat bottom on print bed",270,349,11,BLUE,align="center")


def load_jaws(a):
    i=Iso(a,origin=(300,253),sx=2.0,sy=.9,dx=.56,dy=-.48,sz=2.8)
    f=FIXTURE; slip=f['GROOVE_R']-ROD_D/2
    rod=trimesh.creation.cylinder(radius=ROD_D/2,height=f['HANDLING_BLANK_L'],sections=48)
    rod.apply_translation((0,slip,f['BASE_T']+f['HANDLING_BLANK_L']/2))
    paint(a,i,[item("fixed"),item("loose",ICE,move=(-65,-35,f['BASE_T'])),(rod,LIGHT_STEEL)])
    # Exploded offset keeps the rod's contact with the solid floor visible.
    a.arrow(230,247,276,255,ORANGE,2)
    a.label("seat rod on the floor",16,40,12,BLUE)
    a.arrow(154,48,*i.p(-ROD_D/2-.25,slip,f['BASE_T']),BLUE,1)
    a.label("fixed jaw stays on base",300,35,11,BLUE)
    a.arrow(411,43,*i.p(26,17,38),BLUE,1)
    a.label("set loose jaw on base",15,335,11,BLUE)
    a.arrow(162,323,*i.p(-85,-48,29),BLUE,1)
    a.label("grooves face one another",335,338,11,BLUE,align="center")


def jaw_plan(a):
    f=FIXTURE;gap=f['OPEN_JAW_GAP'];closure=2*f['GROOVE_R']-ROD_D
    half=f['JAW_X']/2;depth=f['JAW_DEPTH']
    loose_front=-gap/2-depth+closure;loose_back=-gap/2+closure
    cx,cy,s=270,169,2.5
    def p(x,y):return cx+s*x,cy-s*y
    def rect(x0,x1,y0,y1,fill,stroke=INK):a.rect(*p(x0,y1),s*(x1-x0),s*(y1-y0),fill,stroke)
    rect(-f['BASE_X']/2,f['BASE_X']/2,-f['BASE_Y']/2,f['BASE_Y']/2,LIGHT_STEEL)
    rect(-half,half,gap/2,gap/2+depth,STEEL)
    rect(-half,half,loose_front,loose_back,ICE)
    # Clip each groove to its own jaw; the loose groove has moved 0.3 mm.
    for y0,y1,groove_y in [(gap/2,gap/2+depth,0),(loose_front,loose_back,closure)]:
        c=a.c;c.saveState();path=c.beginPath();x,y=p(-half,y1)
        path.rect(x,y,f['JAW_X']*s,(y1-y0)*s);c.clipPath(path,stroke=0,fill=0)
        x,y=p(0,groove_y);r=f['GROOVE_R']*s;a.ellipse(x-r,y-r,2*r,2*r,PAPER,INK,.8)
        c.restoreState()
    x,y=p(0,f['GROOVE_R']-ROD_D/2);r=ROD_D*s/2;a.ellipse(x-r,y-r,2*r,2*r,STEEL,INK,1)
    for sign in (-1,1):
        x=sign*f['JAW_CLAMP_X'];spine=sign*42
        a.shape([p(x,27),p(spine,27),p(spine,-36),p(x,-36)],None,BLUE,5,False)
        a.line(*p(x,-36),*p(x,loose_front),INK,2)
        a.line(*p(x-4,loose_front),*p(x+4,loose_front),BLUE,4)
        a.line(*p(x-5,-41),*p(x+5,-41),INK,2)
        a.line(*p(x-4,gap/2+depth),*p(x+4,gap/2+depth),BLUE,4)
        tag(a,"A",*p(spine,-9))
    a.label("TOP VIEW",270,25,12,BLUE,align="center")
    a.label("fixed jaw / behind rod",270,92,11,BLUE,align="center")
    a.label("loose jaw / in front",270,305,11,BLUE,align="center")
    a.label("C-frames point outward",270,347,11,BLUE,align="center")


def build_map(a):
    rows=[("A","BUILD THE DRILLING FIXTURE","2 prints + 4 C-clamps + wood backer","pp. 2-5"),
          ("B","MAKE THE DRILLED CAP","50-60 mm rod blank + 1/16-inch drill","pp. 6-8"),
          ("C","ASSEMBLE THE WELD SETUP","gas branch + metal holder + elbow + cap","pp. 9-10"),
          ("D","WELD THE JET","aim at seam, tack, then close the rim","pp. 11-13")]
    for n,(letter,title,body,pages) in enumerate(rows):
        y=10+n*86
        a.rect(12,y,516,72,ICE,None)
        tag(a,letter,35,y+25)
        a.label(title,58,y+26,11.5,BLUE)
        a.label(body,58,y+50,10.5,INK,"Plex")
        a.label(pages,510,y+26,10.5,BLUE,align="right")
        if n<3:a.arrow(270,y+74,270,y+83,ORANGE,1.5,4)


def cap_seating(a):
    # The two finished product parts are separate from their shop restraints.
    elbow(a,157,145,.91,False)
    a.rect(131,42,52,16,STEEL)
    a.ellipse(131,34,52,16,LIGHT_STEEL)
    a.ellipse(153,40,8,5,PAPER)
    a.arrow(157,73,157,116,ORANGE,2.5)
    a.label("finished drilled cap",30,19,12,BLUE)
    a.label("male / tank-facing tip",14,332,11,BLUE)
    a.arrow(143,317,133,147,BLUE,1)
    a.label("center it; seat it flat",397,35,12,BLUE,align="center")
    # A local section explains the overlap without inventing fitting dimensions.
    a.rect(316,132,61,119,STEEL);a.rect(440,132,61,119,STEEL)
    a.rect(329,105,61,27,LIGHT_STEEL);a.rect(426,105,61,27,LIGHT_STEEL)
    a.line(329,132,377,132,ORANGE,2);a.line(440,132,487,132,ORANGE,2)
    a.label("cap",350,85,11,BLUE,align="center")
    a.label("elbow wall",350,278,11,BLUE,align="center")
    a.label("open jet passage",409,316,11,BLUE,align="center")
    a.arrow(409,299,409,120,BLUE,1)


def seam_closeup(a):
    a.rect(83,172,136,150,STEEL);a.rect(327,172,136,150,STEEL)
    a.rect(108,121,133,51,LIGHT_STEEL);a.rect(305,121,133,51,LIGHT_STEEL)
    a.line(108,172,219,172,INK,2);a.line(327,172,438,172,INK,2)
    gun(a,(437,170),(454,40),19,True)
    a.label("CAP-TO-TIP SEAM",185,34,13,ORANGE,align="center")
    a.line(191,44,285,61,ORANGE,1)
    a.arrow(285,61,437,170,ORANGE,1)
    a.label("cap",172,98,12,BLUE,align="center")
    a.arrow(172,105,172,120,BLUE,1)
    a.label("jet bore stays clear",273,349,12,BLUE,align="center")
    a.arrow(273,329,273,145,BLUE,1)
