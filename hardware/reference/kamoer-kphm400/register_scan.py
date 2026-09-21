#!/usr/bin/env python3
"""Rigid scan-to-scan refinement on explicitly selected shared pump surfaces.

Inputs must already have independently observed approximate physical transforms.
This does not register to CAD and never scales or overwrites source clouds.
"""
from pathlib import Path
import argparse, hashlib, json
import numpy as np
from scipy.spatial import cKDTree
from scipy.spatial.transform import Rotation
def unit(v):
    v = np.asarray(v, dtype=float)
    n = np.linalg.norm(v)
    if n < 1e-10:
        raise ValueError("Degenerate direction")
    return v / n



def transform_points(points, matrix):
    matrix = np.asarray(matrix, dtype=float)
    if matrix.shape != (4, 4):
        raise ValueError("Expected a 4 by 4 homogeneous transform")
    r = matrix[:3, :3]
    if (not np.allclose(r.T @ r, np.eye(3), atol=1e-7)
            or not np.isclose(np.linalg.det(r), 1.0, atol=1e-7)
            or not np.allclose(matrix[3], [0, 0, 0, 1], atol=1e-9)):
        raise ValueError("Registration must be a proper rigid transform with unit scale")
    return points @ r.T + matrix[:3, 3]


def stats(values):
    values = np.asarray(values, dtype=float)
    return {
        "n": len(values), "mean": float(np.mean(values)),
        "median": float(np.median(values)), "rms": float(np.sqrt(np.mean(values ** 2))),
        "p05": float(np.percentile(values, 5)), "p95": float(np.percentile(values, 95)),
        "abs_p95": float(np.percentile(np.abs(values), 95)),
        "min": float(np.min(values)), "max": float(np.max(values)),
    }


def plane(points):
    if len(points) < 3:
        raise ValueError("At least three plane points are needed")
    center = np.mean(points, axis=0)
    _, singular, vh = np.linalg.svd(points - center, full_matrices=False)
    if singular[1] < 1e-8:
        raise ValueError("Plane observations are collinear")
    return center, unit(vh[-1]), singular




def load_cloud(path):
    raw=Path(path).read_bytes(); stop=raw.index(b'end_header\n')+len(b'end_header\n')
    header=raw[:stop].decode('ascii')
    expected=['property float x','property float y','property float z','property float nx','property float ny','property float nz']
    actual=[x for x in header.splitlines() if x.startswith('property ')]
    if 'format binary_little_endian 1.0' not in header or actual != expected:
        raise ValueError('Expected inspected RevoScan XYZ/normal float32 export; examine header before extending parser')
    count=int(next(x.split()[-1] for x in header.splitlines() if x.startswith('element vertex ')))
    if len(raw)-stop != count*24: raise ValueError('Unexpected trailing data or vertex length')
    data=np.frombuffer(raw,dtype='<f4',offset=stop).reshape(count,6).astype(float)
    return data[:,:3],data[:,3:],{'path':str(Path(path).resolve()),'sha256':hashlib.sha256(raw).hexdigest(),'points':count}


def voxel_sample(points,normals,spacing):
    _,ix=np.unique(np.floor(points/spacing).astype(np.int64),axis=0,return_index=True)
    return points[ix],normals[ix]


def choose(points,regions):
    selected=np.zeros(len(points),dtype=bool)
    for region in regions:
        if not region.get('enabled',False): continue
        m=np.all((points>=region['min'])&(points<=region['max']),axis=1)
        if 'radius_xy' in region:
            lo,hi=region['radius_xy'];rr=np.linalg.norm(points[:,:2]-np.asarray(region.get('center_xy',[0,0])),axis=1);m&=(rr>=lo)&(rr<=hi)
        selected|=m
    return selected


def rigid_icp(fixed,fn,moving,mn,max_distance=.8,normal_dot=.75,max_iterations=40):
    tree=cKDTree(fixed); total=np.eye(4);p=moving.copy();n=mn.copy();history=[]
    for iteration in range(max_iterations):
        distance,ix=tree.query(p,workers=1); target=fixed[ix];normal=fn[ix]
        ndot=np.sum(normal*n,axis=1)
        valid=(distance<max_distance)&(ndot>normal_dot)
        if valid.sum()<100: raise ValueError('Too little trustworthy overlap for six-degree rigid refinement')
        pp=p[valid];tar=target[valid];nn=normal[valid]
        residual=np.sum((pp-tar)*nn,axis=1)
        weight=np.minimum(1.,.08/np.maximum(np.abs(residual),1e-12))
        design=np.column_stack([np.cross(pp,nn),nn]);s=np.sqrt(weight)
        step,_,rank,_=np.linalg.lstsq(design*s[:,None],-residual*s,rcond=None)
        if rank<6: raise ValueError('Selected physical surfaces do not constrain all rigid degrees of freedom')
        if np.linalg.norm(step[:3])>.05 or np.linalg.norm(step[3:])>2.:
            raise ValueError('Refinement would require a large step; inspect initial physical registration')
        delta=np.eye(4);delta[:3,:3]=Rotation.from_rotvec(step[:3]).as_matrix();delta[:3,3]=step[3:]
        p=transform_points(p,delta);n=n@delta[:3,:3].T;total=delta@total
        history.append({'iteration':iteration,'paired':int(valid.sum()),'point_plane_residual_mm':stats(residual),'step_rotation_deg':float(np.degrees(np.linalg.norm(step[:3]))),'step_translation_mm':float(np.linalg.norm(step[3:]))})
        if np.linalg.norm(step[:3])<1e-6 and np.linalg.norm(step[3:])<1e-4:break
    angle=float(np.degrees(np.linalg.norm(Rotation.from_matrix(total[:3,:3]).as_rotvec())))
    if angle>5 or np.linalg.norm(total[:3,3])>3:
        raise ValueError('Total refinement exceeds physical-datum check limits')
    return total,history


def regional_distances(fixed,fn,moving,mn,regions):
    rows=[]
    for region in regions:
        if not region.get('enabled',False):continue
        fa=choose(fixed,[region]);mb=choose(moving,[region])
        row={'name':region['name'],'fixed_points':int(fa.sum()),'moving_points':int(mb.sum())}
        if min(fa.sum(),mb.sum())<30:
            row['status']='insufficient_overlap';rows.append(row);continue
        for name,src,sn,dst,dn in [('moving_to_fixed',moving[mb],mn[mb],fixed[fa],fn[fa]),('fixed_to_moving',fixed[fa],fn[fa],moving[mb],mn[mb])]:
            d,ix=cKDTree(dst).query(src,workers=1);dots=np.sum(sn*dn[ix],axis=1);compatible=dots>.75;paired=compatible&(d<.75)
            row[name]={'euclidean_all_mm':stats(d),'normal_compatible_fraction':float(np.mean(compatible)),'overlap_within_0_75mm_fraction':float(np.mean(paired)),'overlap_count':int(paired.sum())}
            if paired.sum():row[name]['point_plane_shared_mm']=stats(np.sum((src[paired]-dst[ix[paired]])*dn[ix[paired]],axis=1))
        rows.append(row)
    return rows


def run(config):
    clouds=[]
    for role in ['fixed','moving']:
        item=config[role];p,n,meta=load_cloud(item['path']);T=np.asarray(item['native_to_shared_initial']);p=transform_points(p,T);n=n@T[:3,:3].T
        finite=np.all(np.isfinite(p),axis=1)&np.all(np.isfinite(n),axis=1);p,n=p[finite],n[finite]
        length=np.linalg.norm(n,axis=1);good=length>.9;p,n=p[good],n[good]/length[good,None]
        p,n=voxel_sample(p,n,config.get('sample_spacing_mm',.30));clouds.append((p,n,meta,T))
    fp,fn,fmeta,fT=clouds[0];mp,mn,mmeta,mT=clouds[1]
    fm=choose(fp,config['fit_regions']);mm=choose(mp,config['fit_regions'])
    delta,history=rigid_icp(fp[fm],fn[fm],mp[mm],mn[mm])
    moved=transform_points(mp,delta);movedn=mn@delta[:3,:3].T
    result={'status':'rigid_scan_to_scan_measurement_not_CAD_fit','fixed':fmeta,'moving':mmeta,'scale_factor':1.,'configuration':config,'moving_refinement':delta.tolist(),'moving_native_to_shared_final':(delta@mT).tolist(),'fixed_native_to_shared':fT.tolist(),'fit_history':history,'regional_bidirectional_comparison':regional_distances(fp,fn,moved,movedn,config['validation_regions']),'limitation':'Only observed mutually covered regions are qualified; missing or moving surfaces are not filled. Scan residual is not manufacturing tolerance.'}
    return result


def selftest():
    grid=np.linspace(-12,12,37);points=[];normals=[]
    for axis in range(3):
        for side in [-1,1]:
            for a in grid:
                for b in grid:
                    p=[a,b];p.insert(axis,side*15);n=np.zeros(3);n[axis]=side;points.append(p);normals.append(n)
    fixed=np.array(points);fn=np.array(normals);truth=np.eye(4);truth[:3,:3]=Rotation.from_euler('xyz',[.4,-.3,.2],degrees=True).as_matrix();truth[:3,3]=[.2,-.25,.17]
    moving=transform_points(fixed,truth);mn=fn@truth[:3,:3].T
    measured,history=rigid_icp(fixed,fn,moving,mn)
    assert np.allclose(measured@truth,np.eye(4),atol=1e-6),measured@truth
    print('Synthetic six-degree rigid scan alignment recovered; no source scan loaded.')

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('configuration',nargs='?');p.add_argument('--out');p.add_argument('--selftest',action='store_true');a=p.parse_args()
    if a.selftest or a.configuration == 'selftest':selftest()
    else:
        if not a.configuration or not a.out:p.error('configuration and --out required')
        config = json.loads(Path(a.configuration).read_text())
        Path(a.out).write_text(json.dumps(run(config.get('configuration', config)), indent=2) + '\n')
