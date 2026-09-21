"""Show observed foot cross-sections, including the underside recesses."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
records=json.loads((HERE/'inspection-inputs.json').read_text())['records']
fig,axes=plt.subplots(3,4,figsize=(17,12),constrained_layout=True)
for col,foot in enumerate(['rear_yminus','rear_yplus','head_yminus','head_yplus']):
    for rec in [r for r in records if r['foot']==foot]:
        a=np.load(rec['cache']);p=a['points'];n=a['normals']
        color={'pass-01-feet-up':'#264b96','pass-02-on-back':'#b25f17','pass-03-feet-down':'#329d76'}[rec['pass']]
        cuts=[abs(p[:,0])<.6,(abs(p[:,0])>5)&(abs(p[:,0])<6),abs(p[:,1]+7)<.45]
        for row,mask in enumerate(cuts):
            c=p[mask]
            axes[row,col].scatter(c[:,1 if row<2 else 0],c[:,2],s=1,alpha=.45,color=color,label=rec['pass'])
    for row in range(3):
        ax=axes[row,col];ax.grid(alpha=.2);ax.set_aspect('equal');ax.set_ylim(-2,24)
        ax.set_xlim((-17,11) if row<2 else (-11,11))
        ax.set_title(foot+'\n'+['centre plane |X|<.6','pocket section 5<|X|<6','across underside recess Y=-7'][row])
axes[0,0].legend(fontsize=6,markerscale=4)
fig.suptitle('Observed foot cross-sections · blue feet-up / orange on-back / green feet-down\nIncludes adjacent fixed rail at inward edge; each observed surface remains identifiable',fontsize=16)
fig.savefig(HERE/'foot-cross-sections.png',dpi=150)
print(HERE/'foot-cross-sections.png')
