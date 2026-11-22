"""Display frame-resolved cup contact at both sightlines of two gate-aligned recordings."""
from pathlib import Path
import argparse,json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('a',type=Path);parser.add_argument('b',type=Path);parser.add_argument('out',type=Path);a=parser.parse_args()
    fig,axes=plt.subplots(2,2,figsize=(10.2,6.3),sharex=True,sharey=True)
    fig.subplots_adjust(top=.81,left=.095,right=.98,bottom=.16,wspace=.1,hspace=.12)
    fig.suptitle('The cup surface after a 750 ms gate',x=.095,y=.965,ha='left',weight='bold',fontsize=19)
    fig.text(.095,.895,'Each time sample is one camera frame. Positive rows are lower in the cup image.',fontsize=10.3)
    heads=['A empties the cup','B fills the cup']; tags=['Right sightline','Middle sightline']
    for j,path in enumerate([a.a,a.b]):
        with np.load(path) as b:
            desc=json.loads(str(b['description']));time=(b['pts_ns']-b['gates'][0,0])/1e9
            off=(b['gates'][-1,2]-b['gates'][0,0])/1e9
            for k,lane in enumerate([6,2]):
                ax=axes[k,j];raw=b['luma_x4'][:,k,lane,:].T/4
                y=b['y0'][k]+np.arange(raw.shape[0])-desc['pre_y'][k]
                vmin,vmax=np.percentile(raw,[4,95])
                ax.pcolormesh(time,y,raw,cmap='gray',shading='nearest',vmin=vmin,vmax=vmax,rasterized=True)
                ax.axvline(0,color='#137899',lw=1.5);ax.axvline(off,color='#e69a27',lw=1.6,ls='--')
                ax.set_xlim(-.45,2.63);ax.set_ylim(36,-54);ax.spines[['top','right']].set_visible(False)
                if k==0:ax.set_title(heads[j],fontsize=12,weight='bold')
                if j==0:ax.set_ylabel(tags[k]+'\nNative rows from start',fontsize=9)
                if k==1:ax.set_xlabel('Time from command (s)',fontsize=10)
                ax.tick_params(labelsize=9)
    fig.legend([Line2D([0],[0],color='#137899',lw=2),Line2D([0],[0],color='#e69a27',lw=2,ls='--')],['Command transmitted','Controller completion received'],loc='lower center',bbox_to_anchor=(.51,.005),ncol=2,frameon=False,fontsize=10)
    fig.savefig(a.out,dpi=155,facecolor='white')
if __name__=='__main__':main()
