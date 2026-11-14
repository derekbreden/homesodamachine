"""Measure the actual tip's joint section, plug, and support dependencies in print coordinates."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import numpy as np
from shapely import LineString, MultiLineString, Polygon, line_merge
from shapely.ops import polygonize

POSE_ANGLE=-105
SHOULDER_DONOR_ANGLE=-70
CANONICAL_POINT=np.array([0.,-38.36796889030837,220.8576411168048])
PICK_POINT=np.array([.213,-36.917,224.843])
STL=np.dtype([("normal","<f4",(3,)),("points","<f4",(3,3)),("attr","<u2")])


def rotate_x(degrees):
    sin,cos=np.sin(np.radians(degrees)),np.cos(np.radians(degrees))
    return np.array([[1,0,0],[0,cos,-sin],[0,sin,cos]])


def triangles(path):
    with path.open("rb") as stream:
        stream.seek(80)
        size=int.from_bytes(stream.read(4),"little")
        return np.fromfile(stream,dtype=STL,count=size)["points"].astype(float)


def physical_origin(project,mesh=None):
    with ZipFile(project) as archive:
        model=ET.fromstring(archive.read('3D/3dmodel.model'))
        settings=ET.fromstring(archive.read('Metadata/model_settings.config'))
        number=next(o.get('id') for o in settings.findall('./object')
                    if any(m.get('key')=='name' and m.get('value')=='faucet-shell-tip' for m in o.findall('metadata')))
        transform=next(i.get('transform') for i in model.findall('./{*}build/{*}item') if i.get('objectid')==number)
        placed=np.fromstring(transform,sep=' ').reshape((4,3))
        if mesh is None:
            return placed[:3].T,placed[3]
        # Print prep centers the model in source CAD prior to the build transform.
        ctr=(mesh.min(axis=(0,1))+mesh.max(axis=(0,1)))*.5
        return placed[:3].T,placed[3]-placed[:3].T@ctr


def outlines(mesh,height,tolerance=5):
    low=mesh[:,:,2]<height
    sliced=mesh[low.any(axis=1)&(~low).any(axis=1)]
    if not len(sliced):
        return []
    segments=[]
    for triangle in sliced:
        cuts=[]
        for a,b in zip(triangle,np.roll(triangle,-1,axis=0)):
            if (a[2]<height)==(b[2]<height):
                continue
            p=a+(b-a)*((height-a[2])/(b[2]-a[2]))
            cuts.append(tuple(round(float(q),tolerance) for q in p[:2]))
        if len(set(cuts))==2:
            segments.append(LineString(cuts))
    figures=list(polygonize(line_merge(MultiLineString(segments))))
    shells=[Polygon(p.exterior) for p in figures]
    blocks=[p for p in figures if sum(shell.covers(p.representative_point()) for shell in shells)%2==1]
    return sorted(blocks,key=lambda polygon:-polygon.area)


def readings(mesh,levels):
    rows=[]
    for height in levels:
        regions=outlines(mesh,height)
        rows.append({"height_mm":height,"part_area_mm2":sum(s.area for s in regions),
                     "islands":len(regions),"bounds":regions[0].bounds if regions else None,
                     "inner_voids": [round(Polygon(r).area,3) for s in regions for r in s.interiors],
                     "islands_wkt":[s.simplify(.012).wkt for s in regions]})
    return rows


def plane_surface(sheet):
    normal=np.cross(sheet[:,1] - sheet[:,0],sheet[:,2] - sheet[:,0])
    near=np.max(np.abs(sheet[:,:,2]),axis=1)<.001
    signed=normal[:,2]
    patch=sheet[near & (signed < 0)]
    xy=patch[:,:,:2]
    return {"triangles_near_joint":len(patch),"area_mm2":float(-.5*signed[near & (signed<0)].sum()),
            "bounds_mm":[xy.min(axis=(0,1)).tolist(),xy.max(axis=(0,1)).tolist()]}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('mesh',type=Path)
    p.add_argument('project',type=Path)
    p.add_argument('output',type=Path)
    a=p.parse_args()
    mesh=triangles(a.mesh)
    physical,origin=physical_origin(a.project,mesh)
    sheet_frame=rotate_x(SHOULDER_DONOR_ANGLE)
    sheet=(mesh-CANONICAL_POINT)@sheet_frame.T
    world=mesh@physical.T+origin
    result={"pose":physical.tolist(),
            "cad_to_plate_translation":origin.tolist(),
            "plate_placed_joint_center":(physical@CANONICAL_POINT+origin).tolist(),
            "exact_pick_height_from_drawn_mm":float((sheet_frame@(PICK_POINT-CANONICAL_POINT))[2]),
            "relative_shoulder_axis_to_plate":(physical@sheet_frame.T).tolist(),
            "mesh_plate_bounds":[world.min(axis=(0,1)).tolist(),world.max(axis=(0,1)).tolist()],
            "normal_section_bounds":[sheet.min(axis=(0,1)).tolist(),sheet.max(axis=(0,1)).tolist()],
            "joint_bearing_surface":plane_surface(sheet),
            "normal_sections":readings(sheet,[-18.5,-18.0,-15.,-12.,-8.,-4.,-2.,-1.,-.50,-.24,-.05,.05,.12,.24,.48,.72,.96,1.2,1.68,2.4,3.6,4.8,6.,8.,10.,12.,15.,18.,22.,28.]),
            "physical_sections":readings(world,[.20,2.,4.,6.,8.,12.,16.,18.,20.,22.,24.,26.,28.,30.,32.,34.,36.,38.,40.,42.,44.,46.,48.,50.,52.,54.,56.,58.,60.,64.,68.])}
    a.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
