"""Draw the east nameplate wing and PSU from their actual placed cross-sections."""
from pathlib import Path
import sys,numpy as np,trimesh,cadquery as cq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
Z=269.1785001
shell=trimesh.load_mesh(HERE.parent/'enclosure-back-top.stl')
def mesh(shape):
 v,t=shape.tessellate(.035)
 return trimesh.Trimesh(vertices=[(p.x,p.y,p.z) for p in v],faces=t,process=False)
psu=mesh(cq.importers.importStep(str(HERE/'placed-psu.step')).val())
plate=mesh(cq.importers.importStep(str(HERE.parent.parent/'nameplate/nameplate-001.step')).val().translate((38.16,471.3-3.36,Z)))
fig,ax=plt.subplots(figsize=(10,7.2));fig.patch.set_facecolor('#fafbfc');ax.set_facecolor('#fafbfc')
for m,color,label,lw in [(shell,'#116894','Enclosure',2.0),(plate,'#333333','Accepted nameplate',1.8),(psu,'#c45914','Power supply',2.2)]:
 section=m.section(plane_origin=(0,0,Z),plane_normal=(0,0,1))
 for entity in section.entities:
  points=entity.discrete(section.vertices)
  ax.plot(points[:,0],points[:,1],color=color,lw=lw)
def dim(x,y0,y1,label,color='#116894',right=True):
 ax.annotate('',xy=(x,y0),xytext=(x,y1),arrowprops={'arrowstyle':'<->','color':color,'lw':1.4})
 ax.text(x+(.12 if right else -.12),(y0+y1)/2,label,ha='left' if right else 'right',va='center',fontsize=10,color=color,
         bbox={'facecolor':'#fafbfc','edgecolor':'none','pad':1})
dim(94.7,465.8,467.94,'2.14 mm backing')
dim(92.05,464.8,465.8,'1.00 mm air','#c45914',False)
dim(92.05,470.07,471.3,'1.23 mm lip',right=False)
ax.annotate('Wing and slot fit unchanged',xy=(92.65,469.4),xytext=(94.1,469.6),arrowprops={'arrowstyle':'->','color':'#333333'},fontsize=11,color='#333333')
ax.text(88.35,472.0,'Outside / visible face',fontsize=10,color='#666666')
ax.text(88.35,463.1,'Inside enclosure',fontsize=10,color='#666666')
ax.set_xlim(88,99);ax.set_ylim(462.8,472.35);ax.set_aspect('equal');ax.set_xlabel('Assembly X (mm)');ax.set_ylabel('Assembly Y (mm)')
ax.set_title('Prepared back-top: nameplate / PSU clearance',loc='left',fontsize=15,pad=17)
ax.legend(handles=[Line2D([0],[0],color=c,lw=2,label=l) for c,l in [('#116894','Enclosure'),('#333333','Accepted nameplate'),('#c45914','Power supply')]],loc='lower right',framealpha=.95)
ax.grid(color='#d9e0e4',lw=.45);fig.tight_layout();fig.savefig(HERE/'backing-clearance.png',dpi=160)
print(HERE/'backing-clearance.png')
