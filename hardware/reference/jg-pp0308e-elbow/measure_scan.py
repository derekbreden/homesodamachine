"""Reproduce the rigid frame and four tapered-band fits from the archived cloud.

Selections belong to the inspected seed frame. Every fourth 15-degree angular
sector is withheld from fitting; scan scale is fixed at 1. Output is a check,
so running this script does not alter the modeling profile table.
"""
import json
import numpy as np
from scipy.optimize import least_squares
from scipy.spatial.transform import Rotation
from scan_tools import HERE, read_cloud, rigid, stats, observations


def main():
    selection=json.loads((HERE/'scan-selection.json').read_text())
    p,n=read_cloud()
    table=(p-np.array(selection['table_origin_native']))@np.array(selection['table_basis_rows']).T
    keep=(table[:,2]>15)&(np.linalg.norm(table[:,:2]-[-10,-12],axis=1)<20)
    seed=np.array(selection['initial_native_to_reference'])
    p=rigid(p[keep],seed);n=n[keep]@seed[:3,:3].T
    bands=[('y_root',1,8.3,10.8,6.85),('z_root',2,8.3,10.8,6.85),
           ('y_collar',1,13.6,15.8,8.1),('z_collar',2,13.6,15.8,8.1)]
    selected=[]
    for name,a,lo,hi,rad in bands:
        radial=np.delete(p,a,1);r=np.linalg.norm(radial,axis=1)
        mask=(p[:,a]>lo)&(p[:,a]<hi)&(abs(r-rad)<.5)&(abs(n[:,a])<.3)&((radial*np.delete(n,a,1)).sum(1)>3)
        q=p[mask];theta=np.arctan2(q[:,0],q[:,3-a])
        withheld=(np.floor((theta+np.pi)/(np.pi/12)).astype(int)%4)==0
        selected.append((q,withheld))
    initial=np.r_[np.zeros(6),np.array([(b[-1],0) for b in bands]).ravel()]
    def errors(v):
        B=Rotation.from_rotvec(v[3:6]).as_matrix();out=[]
        for i,((name,a,lo,hi,rad),(points,ho)) in enumerate(zip(bands,selected)):
            q=(points-v[:3])@B
            out.append(np.linalg.norm(np.delete(q,a,1),axis=1)-v[6+2*i]-v[7+2*i]*(q[:,a]-(lo+hi)/2))
        return out
    fit=least_squares(lambda v:np.concatenate([r[~s[1]][::3] for r,s in zip(errors(v),selected)]),initial,
                      loss='soft_l1',f_scale=.04,max_nfev=150,xtol=1e-11,ftol=1e-11,gtol=1e-11)
    assert fit.success and np.linalg.matrix_rank(fit.jac)==len(initial)
    B=Rotation.from_rotvec(fit.x[3:6]).as_matrix();delta=np.eye(4)
    delta[:3,:3]=B.T;delta[:3,3]=-B.T@fit.x[:3];T=delta@seed
    result={'native_to_reference':T.tolist(),'coordinate_scale_factor':1.,'bands':[]}
    for i,(band,sel,res) in enumerate(zip(bands,selected,errors(fit.x))):
        result['bands'].append({'name':band[0],'diameter_mm':float(2*fit.x[6+2*i]),
                                'taper_mm_per_mm':float(fit.x[7+2*i]),'all':stats(res),'withheld':stats(res[sel[1]])})
    expected=json.loads((HERE/'scan-measurements.json').read_text())
    assert np.max(abs(T-np.array(expected['native_to_reference'])))<1e-5
    for got,want in zip(result['bands'],expected['patches']):
        assert abs(got['diameter_mm']-want['diameter_at_band_midpoint_mm'])<1e-5
    points,normals,_=observations();radius=np.hypot(points[:,0],points[:,2])
    face=points[(points[:,1]>20.3)&(points[:,1]<20.9)&(radius>3.4)&(radius<4.7)&(normals[:,1]>.9)]
    center=face.mean(0);_,_,vectors=np.linalg.svd(face-center,full_matrices=False)
    normal=vectors[-1];normal*=np.sign(normal[1])
    intercept=float(center@normal/normal[1])
    result['exposed_collet_face']={'points':len(face),'axis_intercept_mm':intercept,
                                   'plane_residual_mm':stats((face-center)@normal)}
    assert len(face)==expected['collet_measurement']['face_points']
    assert abs(intercept-expected['collet_measurement']['face_body_y_axis_intercept_mm'])<1e-5
    (HERE/'fit-reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
    print('Rigid frame and four band dimensions reproduced within 0.00001 mm; unit scale.')

if __name__=='__main__':main()
