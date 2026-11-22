"""Plot the held-out continuous and interrupted openings at the two photographed surface sites."""
import argparse
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from read_pour_timings import SITES,read_trace,replace_inner

def chart(trace,timeline,path):
    clock=trace['pts_ns'];grid=np.arange(-.3,3.61,.05)
    fig,axes=plt.subplots(2,2,figsize=(9.5,6.1),sharex=True)
    fig.subplots_adjust(left=.09,right=.98,bottom=.17,top=.78,wspace=.22,hspace=.26)
    fig.suptitle('The cup surface during a release and reopening',x=.09,y=.975,ha='left',weight='bold',fontsize=18)
    fig.text(.09,.905,'Native camera measurements aligned to the appliance’s pour-start acknowledgement.',fontsize=10)
    colors={'same_open_time':'#0c7669','release_reopen':'#b25725'}
    for i,(head,sign) in enumerate([('A',1),('B',-1)]):
        for j,site in enumerate(SITES):
            ax=axes[i,j];y=trace[site+'_shift_px']
            ax.axvspan(1.55,1.90,color='#82759e',alpha=.14,lw=0);ax.axhline(0,color='#999',lw=.5)
            for key,color in colors.items():
                samples=[]
                for p in timeline['pours']:
                    if p['prediction'].get('phase')!='validation' or p['head']!=head or p['prediction'].get('scenario')!=key or not p.get('trial'):continue
                    origin=p['start_ack_ns'];zero=(y[(clock>=origin-.58e9)&(clock<origin-.08e9)])
                    if not len(zero) or clock[-1]<origin+3.61e9:continue
                    samples.append(sign*(np.interp(origin+grid*1e9,clock,y)-np.median(zero)))
                if not samples:continue
                a=np.asarray(samples);low,middle,high=np.percentile(a,[25,50,75],axis=0)
                ax.fill_between(grid,low,high,color=color,alpha=.15,lw=0)
                ax.plot(grid,middle,color=color,lw=1.8)
            ax.set_title(f'Head {head}  ·  {site.capitalize()} rim',loc='left',fontsize=10.5,weight='semibold')
            ax.grid(axis='y',alpha=.19);ax.spines[['right','top']].set_visible(False);ax.tick_params(labelsize=8)
            if i==1:ax.set_xlabel('Seconds after pour start',fontsize=9)
            if j==0:ax.set_ylabel('Signed movement (pixels)',fontsize=9)
    fig.legend([Line2D([0],[0],color=colors['same_open_time'],lw=2),Line2D([0],[0],color=colors['release_reopen'],lw=2),Patch(color='#82759e',alpha=.25)],
               ['Continuous opening','Release, then reopen','Comparison window'],loc='upper left',bbox_to_anchor=(.082,.88),ncol=3,frameon=False,fontsize=9)
    fig.text(.09,.045,'Lines show block medians. Colored bands span the middle half of the trials. Positive motion follows each head’s delivery direction.',fontsize=8.2,color='#40423f')
    fig.savefig(path,dpi=150);plt.close(fig)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('trace',type=Path);parser.add_argument('direct_inner',type=Path)
    parser.add_argument('timeline',type=Path);parser.add_argument('output',type=Path)
    v=parser.parse_args();chart(replace_inner(read_trace(v.trace),read_trace(v.direct_inner)),json.loads(v.timeline.read_text()),v.output)
