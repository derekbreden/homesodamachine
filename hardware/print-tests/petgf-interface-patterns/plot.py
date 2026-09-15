"""Draw measured support and roof paths from the verified machine file."""
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
exp=json.loads((HERE/'experiment.json').read_text())
traces=json.loads(((ROOT/exp['project']).parent/'traces.json').read_text())
fig,axs=plt.subplots(2,4,figsize=(13,7.2))
names=['A · crossed interface','B · connected parallel lines','C · separate parallel lines','D · tree tips, no interface']
for col,spec in enumerate(exp['specimens']):
    t=traces[str(col+1)];cx,cy=spec['plate_center_xy']
    def draw(ax,segments,color,lw):
        ax.add_collection(LineCollection([[(x-cx,y-cy),(u-cx,v-cy)] for x,y,u,v in segments],colors=color,linewidths=lw))
    interface=t.get('Support interface',{})
    if interface:
        top=max(map(float,interface))
        for z,segments in interface.items():
            draw(axs[0,col],segments,'#007e94' if float(z)==top else '#adb8c5',.9 if float(z)==top else .6)
    else:
        top=max(map(float,t['Support']))
        draw(axs[0,col],t['Support'][str(top)],'#007e94',.9)
    z=min(map(float,t['Bridge']))
    draw(axs[1,col],t['Bridge'][str(z)],'#b06526',.5)
    axs[0,col].set_title(names[col],fontsize=10)
    axs[1,col].set_title(f"{spec['id']} · first roof layer",fontsize=10)
    for ax in axs[:,col]:
        ax.plot([-15,-15,15,15],[-18,15,15,-18],c='#222222',lw=2)
        ax.axhline(-18,c='#555555',ls=':',lw=.7)
        ax.set(xlim=(-17,17),ylim=(-20,17),aspect='equal')
        ax.tick_params(labelsize=7)
fig.suptitle('Actual G-code paths · support above, first roof layer below\nGray: lower interface or branch transition · Black: model walls · Dimensions in mm',fontsize=12)
fig.tight_layout(h_pad=1.5,rect=(0,0,1,.91))
fig.savefig(HERE/'toolpaths.png',dpi=150)
