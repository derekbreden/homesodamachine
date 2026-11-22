"""Show dose forecasts from two calibration servings beside each independently tested serving."""
import argparse
import csv
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import numpy as np

names={'partial_top_off':'Partial-flow top-off','short_richer_pour':'Short, richer pour',
       'finish_at_full_flow':'Finish at full flow','near_full_glass':'Near-full-flow glass'}


def draw(rows, out):
    fig,axes=plt.subplots(1,2,figsize=(10.7,4.9),sharex=True,sharey=True)
    for ax,h in zip(axes,'AB'):
        for y,(name,label) in enumerate(names.items()):
            case=[v for v in rows if v['head']==h and v['scenario']==name]
            predicted=float(case[0]['recipe_forecast_ml'])
            old=float(case[0]['width_model_ml'])
            tol=max(1,.1*predicted)
            ax.fill_betweenx([y-.28,y+.28],predicted-tol,predicted+tol,color='#d2e9df')
            ax.plot([predicted,predicted],[y-.29,y+.29],color='#297150',lw=1.8)
            ax.scatter([old],[y],marker='D',facecolors='none',edgecolors='#a6512e',s=53,zorder=4)
            for j,v in enumerate(case):
                if not v['primary_ml'] or not v['heldout_ml']:
                    continue
                left,right=float(v['primary_ml']),float(v['heldout_ml'])
                ay=y-.19+j*.077
                ax.plot([left,right],[ay,ay],color='#597684',lw=1.0)
                ax.scatter([left],[ay],s=16,c='#164c68',zorder=5)
                ax.scatter([right],[ay],s=16,marker='|',c='#164c68',zorder=5)
        ax.set_title(f'Pump {h}',loc='left',fontsize=14,fontweight='bold')
        ax.set_xlabel('Concentrate (nominal mL)')
        ax.set_xlim(0,40)
        ax.set_yticks(np.arange(len(names)),names.values())
        ax.set_ylim(-.55,len(names)-.45)
        ax.tick_params(axis='y',length=0)
        ax.spines[['top','right','left']].set_visible(False)
        ax.grid(axis='x',alpha=.18)
    fig.suptitle('Can two calibration servings predict the next six?',x=.06,y=.98,ha='left',fontweight='bold',fontsize=17)
    handles=[Patch(color='#d2e9df',label='Recipe forecast tolerance'),
             Line2D([],[],color='#297150',marker='|',ls='',markersize=12,label='Recipe forecast'),
             Line2D([],[],marker='D',mfc='none',mec='#a6512e',ls='',label='Pulse-width forecast'),
             Line2D([],[],marker='o',ms=5,color='#164c68',ls='',label='Measured serving')]
    fig.legend(handles=handles,loc='lower center',bbox_to_anchor=(.53,.005),ncols=4,frameon=False)
    fig.subplots_adjust(left=.19,right=.98,top=.82,bottom=.22,wspace=.18)
    fig.savefig(out,dpi=165,facecolor='white')
    plt.close(fig)


if __name__=='__main__':
    a=argparse.ArgumentParser(description=__doc__)
    a.add_argument('attempts',type=Path);a.add_argument('figure',type=Path)
    v=a.parse_args()
    with v.attempts.open() as f:draw(list(csv.DictReader(f)),v.figure)
