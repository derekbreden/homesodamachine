"""Render an inspection view from the current native viewer meshes and wire paths."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from hardware.wiring.installed.review import load_mesh
from hardware.wiring.installed.route_search import sampled


def main():
    model=json.loads((ROOT/'hardware/wiring/enclosure-wiring.json').read_text())
    meshes=load_mesh(ROOT/'hardware/manifold-layout/enclosure-assembly.step.mesh')
    fig=plt.figure(figsize=(15,9.5),facecolor='#f6f7f9')
    axes=[fig.add_subplot(121,projection='3d'),fig.add_subplot(122,projection='3d')]
    palette={'valves':'#bf841d','pumps':'#8650c7','displays':'#257cb2','sensors':'#25856b','power':'#47566b'}
    def kind(h):
        if h in ('J1','J2'):return 'valves'
        if h in ('J13','Cartridge'):return 'pumps'
        if h in ('J3','J9'):return 'displays'
        if h in ('J4','J6','J7','J11'):return 'sensors'
        return 'power'
    for ax,limits in zip(axes,(((-108,108),(0,480),(0,355)),((-105,105),(0,240),(145,355)))):
        ax.set_facecolor('#f6f7f9')
        for n,(v,f) in meshes.items():
            if n.startswith(('wire-','terminal-pogo')):continue
            if n.startswith('cold-core/') and not any(s in n for s in ('carbonator-tube','reed-','probe-')):continue
            if n.startswith(('tube-','enclosure-','pump-receiver','pump-keeper','anchor-','magnet-','turn-','step-','stub-')):continue
            tri=v[f]
            mask=np.ones(len(tri),dtype=bool)
            for i,(lo,hi) in enumerate(limits):mask&=(tri[:,:,i].max(1)>=lo)&(tri[:,:,i].min(1)<=hi)
            tri=tri[mask]
            if not len(tri):continue
            tri=tri[::max(1,len(tri)//1800)]
            alpha=.11 if 'coil-' in n or n.startswith('valve-') else .075
            poly=Poly3DCollection(tri,facecolor='#718095',edgecolor='none',alpha=alpha,rasterized=True)
            ax.add_collection3d(poly)
        for r in model['routes']:
            p=sampled(r['segments'],1.8)
            outside=np.zeros(len(p),dtype=bool)
            for i,(lo,hi) in enumerate(limits):outside|=(p[:,i]<lo)|(p[:,i]>hi)
            p[outside]=np.nan
            unresolved=r['route_status']=='unresolved'
            ax.plot(p[:,0],p[:,1],p[:,2],color='#c7463e' if unresolved else palette[kind(r['harness'])],
                    linewidth=1.05 if unresolved else .85,linestyle=(0,(3,2)) if unresolved else '-',alpha=.82)
        for bundle in model.get('bundles',{}).values():
            if bundle['geometry_name'] is None:continue
            p=sampled(bundle['segments'],2.)
            outside=np.zeros(len(p),dtype=bool)
            for i,(lo,hi) in enumerate(limits):outside|=(p[:,i]<lo)|(p[:,i]>hi)
            p[outside]=np.nan
            ax.plot(p[:,0],p[:,1],p[:,2],color='#293543',linewidth=4,alpha=.45)
        ax.set_xlim(*limits[0]);ax.set_ylim(*limits[1]);ax.set_zlim(*limits[2])
        ax.set_box_aspect(tuple(hi-lo for lo,hi in limits));ax.view_init(elev=23,azim=-58)
        ax.set_xlabel('X · mm',fontsize=8);ax.set_ylabel('Y · mm',fontsize=8);ax.set_zlabel('Z · mm',fontsize=8)
        ax.tick_params(labelsize=7,pad=1)
        for pane in (ax.xaxis.pane,ax.yaxis.pane,ax.zaxis.pane):pane.fill=False
        ax.grid(False)
    axes[0].set_title('Complete enclosure wiring',fontsize=13,pad=12)
    axes[1].set_title('Front assembly and cartridge',fontsize=13,pad=12)
    handles=[Line2D([0],[0],color=c,lw=2,label=k.capitalize()) for k,c in palette.items()]
    handles.append(Line2D([0],[0],color='#c7463e',lw=2,ls='--',label='Unresolved route'))
    fig.legend(handles=handles,loc='lower center',ncol=6,frameon=False,fontsize=9,bbox_to_anchor=(.5,.045))
    fig.suptitle(f"{model['connection_count']} conductor runs · installed inspection model",fontsize=19,y=.97)
    fig.text(.5,.015,'Inspection colors identify harness functions. Device bodies are translucent; exact terminal details and route status are in the manifest.',ha='center',fontsize=9,color='#536174')
    fig.subplots_adjust(left=.015,right=.985,top=.90,bottom=.10,wspace=.02)
    out=Path(__file__).with_name('enclosure-wiring-overview.png');fig.savefig(out,dpi=130,facecolor=fig.get_facecolor());plt.close(fig)
    print(out.relative_to(ROOT))


if __name__=='__main__':main()
