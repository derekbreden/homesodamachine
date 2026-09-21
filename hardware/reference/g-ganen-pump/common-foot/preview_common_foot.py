"""Render the common native foot beside the retained unscaled observations."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
from g_ganen_foot import build_foot, PROFILE_YZ
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
CACHE=ROOT/'.cache/g-ganen-common-foot'
shape=build_foot();v,t=shape.tessellate(.06,.12)
v=np.asarray([p.toTuple() for p in v]);t=np.asarray(t)
fig=plt.figure(figsize=(15,11),constrained_layout=True)
ax=fig.add_subplot(2,2,1)
a=np.load(CACHE/'pass-01-feet-up-rear_yminus.npz');p=a['points'];n=a['normals']
m=(p[:,2]<5.2)&(p[:,2]>-.3)&(n[:,2]<-.25)
q=p[m];ax.scatter(q[:,0],q[:,1],c=q[:,2],s=.2,cmap='viridis',vmin=0,vmax=5)
ax.set_title('Raw feet-up scan: bottom face, slot and two lower reliefs');ax.set_aspect('equal');ax.grid(alpha=.2);ax.set_xlim(-11,11);ax.set_ylim(-17,11)
ax.set_xlabel('Axial X / mm');ax.set_ylabel('Outward Y / mm')
def native(ax,elev,azim,title):
 tris=v[t];ns=np.cross(tris[:,1]-tris[:,0],tris[:,2]-tris[:,0]);ns/=np.maximum(np.linalg.norm(ns,axis=1)[:,None],1e-9)
 light=np.array([-.25,-.4,.8]);light/=np.linalg.norm(light)
 shade=.3+.5*abs(ns@light)
 colors=np.column_stack([shade*.8,shade*.87,shade,np.ones(len(shade))])
 coll=Poly3DCollection(tris,facecolors=colors,edgecolors='none',linewidths=0)
 ax.add_collection3d(coll);ax.set_xlim(-11,11);ax.set_ylim(-17,11);ax.set_zlim(0,20)
 ax.set_box_aspect((22,28,20));ax.view_init(elev,azim);ax.set_title(title);ax.set_xlabel('X');ax.set_ylabel('Y');ax.set_zlabel('Z')
native(fig.add_subplot(2,2,2,projection='3d'),-45,-55,'One shared native foot: underside openings are retained')
ax=fig.add_subplot(2,2,3)
a=np.load(CACHE/'pass-02-on-back-rear_yplus.npz');p=a['points'];n=a['normals']
m=(abs(n[:,0])>.94)&(abs(p[:,0])>7.2)&(abs(p[:,0])<10.8)
q=p[m];ax.scatter(q[:,1],q[:,2],s=.5,color='#bd732d',alpha=.5,label='Observed axial rubber end faces')
poly=np.array(PROFILE_YZ+PROFILE_YZ[:1]);ax.plot(poly[:,0],poly[:,1],color='#183d75',lw=1.7,label='Common nominal side profile')
ax.set_title('Exposed clip mouth; continuous fixed rail is excluded');ax.set_aspect('equal');ax.set_xlim(-17,10);ax.set_ylim(-1,21);ax.grid(alpha=.2);ax.legend(fontsize=8)
ax.set_xlabel('Outward Y / mm');ax.set_ylabel('Height Z / mm')
native(fig.add_subplot(2,2,4,projection='3d'),30,-55,'Identical purchased-foot reference · pad nominally 7 mm')
fig.suptitle('G Ganen rubber feet · native scan evidence and shared geometry\nScan scale unchanged; hidden rail engagement and elastomer compression are not a replacement-foot specification',fontsize=15)
fig.savefig(HERE/'common-foot-comparison.png',dpi=145)
print(HERE/'common-foot-comparison.png')
