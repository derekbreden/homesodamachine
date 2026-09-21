"""Render native study geometry; no source or production model is regenerated."""
from pathlib import Path
import json

import cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
import numpy as np

import axial_capture as study

HERE=Path(__file__).resolve().parent
INK='#203344'
GOLD='#d6a347'
BLUE='#387fa9'
GREEN='#4c9070'
GRAY='#a5b0ba'


def draw(ax,body,color,frame,alpha=1):
    vertices,triangles=body.tessellate(.035,.12)
    v=np.array([frame(p) for p in vertices])
    faces=v[np.array(triangles)]
    normals=np.cross(faces[:,1]-faces[:,0],faces[:,2]-faces[:,0])
    length=np.linalg.norm(normals,axis=1)
    normals=normals/np.maximum(length[:,None],1e-10)
    light=np.array([.15,-.45,.88]);light/=np.linalg.norm(light)
    shade=.68+.32*np.abs(normals@light)
    rgb=np.array(matplotlib.colors.to_rgb(color))
    colors=np.column_stack((shade[:,None]*rgb, np.full(len(faces),alpha)))
    mesh=Poly3DCollection(faces,facecolors=colors,edgecolors='none',zsort='average')
    ax.add_collection3d(mesh)


def main():
    info=json.loads((HERE/'axial-checks.json').read_text())
    if info['status']!='pass':
        raise SystemExit('Render only a passing native geometry audit')
    fixed=cq.importers.importStep(str(HERE/'axial-fixed-seat-coupon.step')).val()
    moving=cq.importers.importStep(str(HERE/'axial-closed-moving-seat-coupon.step')).val()
    seated=cq.importers.importStep(str(HERE/'axial-guide-seat-plug-seated-reference.step')).val()
    relaxed=cq.importers.importStep(str(HERE/'axial-guide-seat-plug-unqualified-example.step')).val()
    cutaway=study.box((study.X,study.X+15),(study.FORE-2,study.MOUTH+20),(study.Z-20,study.Z+20))
    figure=plt.figure(figsize=(15,9),facecolor='#fcfcfa')
    figure.text(.035,.948,'ONE PLUG PER SPRING',fontsize=23,color=INK,weight='bold')
    figure.text(.035,.914,'Closed moving bore  ·  axial spring loading  ·  rigid quarter-turn retention',
                fontsize=13,color=INK)
    figure.text(.035,.879,'Native study on archived matched geometry — guide Ø3 is an unqualified example',
                fontsize=11,color='#8b5b29')

    ax=figure.add_axes([.018,.28,.61,.59],projection='3d')
    frame=lambda p:(p.y-study.FORE,p.x-study.X,p.z-study.Z)
    draw(ax,fixed.intersect(cutaway),GRAY,frame)
    draw(ax,moving.intersect(cutaway),'#b6c0c7',frame)
    draw(ax,seated,GOLD,frame)
    spring=study.place(study.ycyl(6,study.FLOOR,study.MOVING_FLOOR))
    draw(ax,spring,GREEN,frame,.17)
    ax.set_xlim(-3,33);ax.set_ylim(-9,10);ax.set_zlim(-14,14)
    ax.set_box_aspect((36,19,28));ax.view_init(elev=16,azim=-84)
    ax.set_proj_type('ortho');ax.set_axis_off()
    ax.text(2,0,-16,'FIXED WALL',fontsize=10,color=INK,ha='center')
    ax.text(25,0,-12,'CLOSED MOVING BORE',fontsize=10,color=INK,ha='center')
    figure.text(.045,.274,'Cutaway at the spring axis',fontsize=13,color=INK,weight='bold')
    figure.text(.045,.245,'Green: Ø6 spring envelope.  Gold: one guide-and-seat plug.',fontsize=11,color=INK)
    figure.text(.045,.218,'The guide remains 5.95 mm inside the moving bore at maximum travel.',fontsize=11,color=INK)

    ax2=figure.add_axes([.62,.35,.365,.52],projection='3d')
    head_limit=study.box((study.X-10,study.X+10),(study.FORE,study.FLOOR+2),(study.Z-10,study.Z+10))
    head=relaxed.intersect(head_limit)
    walls=study.union(study.wall_shape(study.PRELOAD),study.turn(study.wall_shape(study.PRELOAD),180))
    walls=study.place(walls)
    frame2=lambda p:(p.x-study.X,p.z-study.Z,p.y-study.FACE_FORE)
    draw(ax2,head.cut(walls),GOLD,frame2)
    draw(ax2,walls,BLUE,frame2)
    ax2.set_xlim(-9,9);ax2.set_ylim(-9,9);ax2.set_zlim(-1,9)
    ax2.set_box_aspect((18,18,10));ax2.view_init(elev=26,azim=-57)
    ax2.set_proj_type('ortho');ax2.set_axis_off()
    figure.text(.66,.326,'Gold lugs carry spring reaction.',fontsize=12,color=INK,weight='bold')
    figure.text(.66,.296,'Blue broad walls only prevent rotation.',fontsize=12,color=BLUE,weight='bold')
    figure.text(.66,.258,'1.3 × 2.4 mm curved walls, 15.4 mm long',fontsize=10.5,color=INK)
    figure.text(.66,.231,'Relaxed plug shown; guide cropped for clarity',fontsize=10,color='#5c6b76')

    figure.add_artist(plt.Line2D([.04,.96],[.184,.184],transform=figure.transFigure,color='#bdc7cd',lw=.8))
    figure.text(.045,.142,'ASSEMBLY',fontsize=10,color=INK,weight='bold')
    figure.text(.135,.142,'Carrier → axial spring → guide/seat plug → 90° turn → cartridge',fontsize=12,color=INK)
    figure.text(.045,.094,'27 mm free spring → 19.25 mm shortest installation length.  Cartridge air: 0.50 mm.',fontsize=11,color=INK)
    figure.text(.045,.049,'Pending: matched production wall, measured spring ID, physical detent/retention and support-removal trial.',
                fontsize=10.5,color='#8b5b29')
    figure.savefig(HERE/'axial-capture-study.png',dpi=160,facecolor=figure.get_facecolor())
    figure.savefig(HERE/'axial-capture-study.svg',facecolor=figure.get_facecolor())
    svg = HERE/'axial-capture-study.svg'
    svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
    plt.close(figure)
    print('Rendered native axial spring-capture study')


if __name__=='__main__':
    main()
