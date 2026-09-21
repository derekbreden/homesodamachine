"""Classify rubber separately using its exposed axial end-face normals."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
records=json.loads((HERE/'inspection-inputs.json').read_text())['records']
fig,axes=plt.subplots(2,4,figsize=(18,10),constrained_layout=True)
for col,foot in enumerate(['rear_yminus','rear_yplus','head_yminus','head_yplus']):
    for rec in [r for r in records if r['foot']==foot]:
        a=np.load(rec['cache']);p=a['points'];n=a['normals']
        color={'pass-01-feet-up':'#264b96','pass-02-on-back':'#b25f17','pass-03-feet-down':'#329d76'}[rec['pass']]
        for row,mask in enumerate([(abs(n[:,0])>.94)&(abs(p[:,0])>7.2)&(abs(p[:,0])<10.8), (abs(n[:,0])>.80)&(abs(p[:,0])>7.2)&(abs(p[:,0])<10.8)]):
            q=p[mask];axes[row,col].scatter(q[:,1],q[:,2],s=1,alpha=.6,color=color,label=rec['pass'])
    for row in range(2):
        ax=axes[row,col];ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlim(-17,11);ax.set_ylim(-2,24)
        ax.set_title(foot+f' · |Nx|>{[.94,.8][row]}')
axes[0,0].legend(fontsize=6,markerscale=3)
fig.suptitle('Axial end faces of the rubber foot · adjacent continuous rail has no axial end at this foot station',fontsize=16)
fig.savefig(HERE/'axial-rubber-faces.png',dpi=150)
print(HERE/'axial-rubber-faces.png')
