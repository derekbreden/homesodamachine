"""Render this manual path review from its saved measurements; no slicing."""
from pathlib import Path
import json
import math

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon, Rectangle
import numpy as np
import shapely
import trimesh

HERE=Path(__file__).resolve().parent

def main():
    source=json.loads((HERE/'stock-engine.json').read_text())['candidates'][1]
    revised=json.loads((HERE/'full-annulus/mark2/layout-engine.json').read_text())
    original=json.loads((HERE/'stock-vs-tree/mark2/rim-path-review.json').read_text())
    audit=json.loads((HERE/'full-annulus/mark2/rim-path-review.json').read_text())
    prep=json.loads((HERE/'full-annulus/mark2/preparation.json').read_text())
    part=trimesh.load(HERE/'foot-section.stl',force='mesh',process=True)
    mask=(part.face_normals[:,2]<-.999)&(np.abs(part.triangles_center[:,2])<.015)
    poly=shapely.union_all(shapely.polygons(part.triangles[mask,:,:2])).buffer(1e-5).buffer(-1e-5)
    theta=math.radians(-15)
    rot=np.array([[1,0,0],[0,math.cos(theta),-math.sin(theta)],[0,math.sin(theta),math.cos(theta)]])
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10})
    fig=plt.figure(figsize=(15,7),dpi=170,facecolor='#f6f7f8')
    axes=[fig.add_axes([.05,.24,.27,.61]),fig.add_axes([.36,.24,.27,.61])]
    for ax,data,title in zip(axes,[source,revised],['Submitted: 8 stock walls','Prepared: 34 Full-mode walls + 3 low walls']):
        ax.set_facecolor('#f6f7f8')
        ax.add_patch(Polygon(np.asarray(poly.exterior.coords),facecolor='#d8dce0',edgecolor='#8c9399',lw=1))
        for ring in poly.interiors:ax.add_patch(Polygon(np.asarray(ring.coords),facecolor='#f6f7f8',edgecolor='#aeb4ba',lw=.6))
        offset=np.array([data['offset'][k] for k in 'xyz'])
        for fin in data['fins']:
            line=(np.array(fin['line'])-offset)@rot
            ax.plot(line[:,0],line[:,1],c='#187e9b',lw=1.7,solid_capstyle='round')
        if data is revised:
            for wall in prep['rear_low_walls']:
                ax.plot([wall['cad_x_mm']]*2,wall['cad_y_interval_mm'],c='#c46d12',lw=3)
        ax.set(xlim=(-33,33),ylim=(-38,34),aspect='equal',xlabel='CAD X (mm)',ylabel='CAD Y (mm)')
        ax.set_title(title,fontweight='bold',fontsize=11,pad=13)
        ax.annotate('Lever / glass side',xy=(0,-29.5),xytext=(0,-34.5),ha='center',va='top',color='#b14137',
            arrowprops=dict(arrowstyle='->',color='#b14137'),fontsize=9)
        ax.spines[['top','right']].set_visible(False)
    axes[1].annotate('Low rear walls\nCAD X −6, 0, +6',xy=(0,25),xytext=(16,32),ha='center',fontsize=8,color='#995110',
        arrowprops=dict(arrowstyle='->',color='#995110'))
    ax=fig.add_axes([.69,.35,.285,.44]);ax.set_facecolor('#f6f7f8')
    for y,d,label in [(1,original,'Submitted'),(0,audit,'Prepared')]:
        row=next(r for r in d['cases'] if r['case']=='2: preceding straight wall')
        ax.plot([0,row['xy_length_mm']],[y,y],color='#ba473d',lw=6,solid_capstyle='butt')
        key=str(round(row['nominal_layer_nozzle_z_mm']-.48,5))
        for a,b in row['A_previous_courses'][key]['centreline_over_material_mm']:
            ax.plot([a,b],[y,y],color='#259063',lw=10,solid_capstyle='butt')
        value=row['A_previous_courses'][key]['longest_no_centreline_bearing_mm']
        ax.text(0,y+.20,f'{label}: {value:.2f} mm longest gap',fontsize=10)
    ax.set(xlim=(-.1,8),ylim=(-.6,1.6),yticks=[],xlabel='Distance along the 7.87 mm strand (mm)')
    ax.set_title('Your priority: directly under the lever',fontweight='bold',fontsize=11,pad=18)
    ax.spines[['top','right','left']].set_visible(False)
    ax.text(0,-.48,'Green: lower bead at Z14.84\nZ15.08 is empty; strand prints at Z15.32.',fontsize=9,color='#276c50')
    fig.text(.69,.25,'Same native recipe on both prepared specimens:\n125% bridge flow · 70% fan after 3 off layers\nBridge 15 mm/s · fully overhung wall 10 mm/s',fontsize=10,linespacing=1.65,va='top')
    fig.text(.035,.955,'Faucet underside: contact placement and native deposition',fontsize=18,fontweight='bold',color='#24313d')
    fig.text(.035,.905,'Plan view of the retained bottom annulus. Part geometry, bed contact and −15° pose are preserved.',fontsize=11,color='#55616c')
    fig.text(.035,.095,'Blue: engine contact lines. Orange: local low rear walls. The prepared plate is unsent.',fontsize=10,color='#394c5b')
    fig.text(.035,.055,'Measured XY bearings do not establish sag, removal effort or finished appearance. Physical comparison is pending.',fontsize=10,color='#59646d')
    fig.savefig(HERE/'support-layout-review.png',facecolor=fig.get_facecolor())

if __name__=='__main__':main()
