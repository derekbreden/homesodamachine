"""Render the exported CAD and the unfilled native surface in the same mm frame."""
import gzip,io,json
from pathlib import Path
import numpy as np,trimesh,cadquery as cq
import matplotlib;matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
HERE=Path(__file__).resolve().parent

def shaded(mesh,color):
    light=np.array([.7,.4,.8]);light/=np.linalg.norm(light)
    shade=.62+.38*np.clip(mesh.face_normals@light,0,1)
    return mesh.triangles,np.asarray(color)[None,:]*shade[:,None]

fig=plt.figure(figsize=(13,6));fig.patch.set_facecolor('#f0f3f5')
for i in range(2):
    ax=fig.add_subplot(1,2,i+1,projection='3d');ax.set_facecolor('#f0f3f5')
    if i==0:
        shape=cq.importers.importStep(str(HERE/'jg-pp0308e-elbow.step')).val()
        triangles=[];colors=[]
        for j,solid in enumerate(shape.Solids()):
            v,f=solid.tessellate(.04,.12);mesh=trimesh.Trimesh([x.toTuple() for x in v],f,process=False)
            t,c=shaded(mesh,[(.28,.38,.44),(.17,.67,.64),(.85,.58,.24)][j]);triangles.append(t);colors.append(c)
        triangles=np.concatenate(triangles);colors=np.concatenate(colors)
    else:
        mesh=trimesh.load(io.BytesIO(gzip.decompress((HERE/'observed-surface.ply.gz').read_bytes())),file_type='ply',process=False)
        triangles,colors=shaded(mesh,(.18,.55,.60))
    ax.add_collection3d(Poly3DCollection(triangles,facecolors=colors,linewidth=0,rasterized=True))
    ax.set(xlim=(-11,11),ylim=(-9,23),zlim=(-9,23),xlabel='X (mm)',ylabel='Y (mm)',zlabel='Z (mm)')
    ax.set_box_aspect((22,32,32));ax.view_init(elev=23,azim=35);ax.set_proj_type('ortho')
    ax.set_xticks([-8,0,8]);ax.set_yticks([-5,0,10,20]);ax.set_zticks([-5,0,10,20])
    ax.set_title(['Editable exterior CAD · three components','Captured surface · no hole filling'][i],fontsize=12)
fig.suptitle('John Guest PP0308E · measured elbow reference',fontsize=19,y=.99)
fig.text(.5,.04,'+Y release face measured at 20.56 mm  •  +Z collet completed by symmetry  •  Nominal tube Ø6.35 mm',ha='center',fontsize=11)
fig.text(.5,.008,'95% of retained observations within 0.15 mm of CAD; coating thickness and absolute accuracy unverified.',ha='center',fontsize=10,color='#52606a')
fig.tight_layout(rect=(0,.07,1,.96));fig.savefig(HERE/'model-preview.png',dpi=150)
print(HERE/'model-preview.png')
