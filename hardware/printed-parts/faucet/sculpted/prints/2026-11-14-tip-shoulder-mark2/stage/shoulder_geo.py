"""Measure and place the tip's mating lip in the model plane and on its printer bed."""
from __future__ import annotations

from dataclasses import dataclass
import json
import math
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

import manifold3d as m3
import numpy as np
from shapely import LineString, Polygon, MultiPolygon, union_all
import trimesh

FINISH = Path('hardware/printed-parts/faucet/sculpted/finish-selection.json')
BED_ROTATION_X = -105.0
FACE = json.loads(FINISH.read_text())['tip_supports']['joint_plane']
PLANE_CENTER = np.asarray(FACE['point'])
MODEL_A = np.array([1.0, 0.0, 0.0])
MODEL_N = np.asarray(FACE['normal'])
MODEL_B = np.cross(MODEL_N, MODEL_A)
BASIS = np.stack([MODEL_A, MODEL_B, MODEL_N])


@dataclass(frozen=True)
class Frame:
    center: np.ndarray
    basis: np.ndarray

    @property
    def n(self):
        return self.basis[2]

    @property
    def downhill(self):
        return self.basis[1]

    def world(self, p):
        return self.center + np.asarray(p) @ self.basis

    def relative(self, p):
        return (np.asarray(p) - self.center) @ self.basis.T

    def plane_z(self, xy, n):
        return (n - (np.asarray(xy)-self.center[:2]) @ self.n[:2]) / self.n[2] + self.center[2]


def exact_placement(project, part_id=4):
    with ZipFile(project) as z:
        core = ET.fromstring(z.read('3D/3dmodel.model'))
        objects = {int(ob.get('id')): ob for ob in core.findall('./{*}resources/{*}object')}
        mapping = next(ob for ob in core.findall('./{*}build/{*}item') if int(ob.get('objectid')) == part_id)
        transform = np.asarray(list(map(float, mapping.get('transform').split()))).reshape(4,3)
        raw = list(objects[part_id].findall('./{*}components/{*}component'))[0]
        member = next(value for key,value in raw.attrib.items() if key.endswith('}path')).lstrip('/')
        part = ET.fromstring(z.read(member)).find('./{*}resources/{*}object')
        vertices = np.asarray([[float(v.get(key)) for key in 'xyz'] for v in part.findall('./{*}mesh/{*}vertices/{*}vertex')])
    return transform[:3], transform[3], vertices


def placed(stl, project=None, yaw=0.0, xy=(186.5, 201.78512882)):
    mesh = trimesh.load_mesh(stl)
    if project:
        rot, trans, model = exact_placement(project)
        center = np.asarray(mesh.bounds).mean(axis=0)
        if np.max(abs(np.asarray(mesh.bounds) - center - np.stack([model.min(axis=0), model.max(axis=0)]))) > .15:
            raise ValueError('Tip source bounds differ from embedded centered mesh')
    else:
        beta, gamma = map(math.radians, [BED_ROTATION_X, yaw])
        to_bed = np.asarray([[1, 0, 0],[0, math.cos(beta),math.sin(beta)],[0,-math.sin(beta),math.cos(beta)]])
        turn = np.asarray([[math.cos(gamma), math.sin(gamma),0],[-math.sin(gamma),math.cos(gamma),0],[0,0,1]])
        rot = to_bed @ turn
        center = np.asarray(mesh.bounds).mean(axis=0)
        trans = np.r_[xy, -((mesh.vertices-center) @ rot)[:,2].min()]
    frame = Frame((PLANE_CENTER-center) @ rot + trans, BASIS @ rot)
    vertices_world = (mesh.vertices-center) @ rot + trans
    return mesh, vertices_world, frame


def shoulder(mesh):
    local = (mesh.vertices - PLANE_CENTER) @ BASIS.T
    f = local[mesh.faces]
    parallel = (np.abs(f[...,2]) <= .002).all(axis=1)
    polygons = [Polygon(q[:,:2]) for q in f[parallel] if Polygon(q[:,:2]).area > 1e-7]
    region = union_all(polygons).buffer(0)
    if not region.is_valid:
        raise ValueError('Invalid mating lip facet projection')
    shells = polygons_of(region)
    principal = max(shells,key=lambda g:g.area)
    outline = Polygon(principal.exterior)
    if len(principal.interiors) != 1:
        raise ValueError('Mating lip expected a single inner keepout')
    return principal, outline, Polygon(principal.interiors[0]), len(polygons)


def polygons_of(geometry):
    if geometry.is_empty:
        return []
    if geometry.geom_type == 'Polygon':
        return [geometry]
    return [piece for piece in geometry.geoms if piece.geom_type == 'Polygon']


def solid(vertices, faces):
    shell = m3.Manifold(m3.Mesh(vert_properties=np.asarray(vertices,np.float32),tri_verts=np.asarray(faces,np.uint32)))
    if shell.status() != m3.Error.NoError:
        raise ValueError(f'Tip STL not manifold: {shell.status()}')
    return shell


def section(volume, z):
    loops = [np.asarray(p) for p in volume.slice(float(z)).to_polygons() if len(p)>=3]
    def area(p):
        return sum(p[:,0]*np.roll(p[:,1],-1)-np.roll(p[:,0],-1)*p[:,1])/2
    outer = union_all([Polygon(p) for p in loops if area(p)>0])
    return outer.difference(union_all([Polygon(p) for p in loops if area(p)<0])).buffer(0)


def plate_projection(shape, frame, normal):
    def xy(points):
        return frame.world(np.c_[np.asarray(points),np.full(len(points),normal)])[:,:2]
    return union_all([Polygon(xy(p.exterior.coords),[xy(h.coords) for h in p.interiors]) for p in polygons_of(shape)])


if __name__ == '__main__':
    import argparse
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('stl',type=Path);p.add_argument('output',type=Path);p.add_argument('--project',type=Path)
    p.add_argument('--yaw',type=float,default=0.0)
    args=p.parse_args()
    msh,world,frame=placed(args.stl,args.project,args.yaw)
    lip,outline,hole,faces=shoulder(msh)
    real=solid(world,msh.faces)
    outward=frame.world(np.column_stack([lip.exterior.coords,np.zeros(len(lip.exterior.coords))]))
    roof=plate_projection(lip,frame,-.24)
    report={'frame':{'center':frame.center.tolist(),'basis':frame.basis.tolist()},'lip_area_mm2':lip.area,'lip_bounds_uv_mm':lip.bounds,
            'raw_lip_faces':faces,'hole_bounds_uv_mm':hole.bounds,'hole_area_mm2':hole.area,'outer_area_mm2':outline.area,
            'support_footprint_roof_top_mm':roof.bounds,'model_bounds_world_mm':[world.min(axis=0).tolist(),world.max(axis=0).tolist()],
            'lip_Z_mm':[min(outward[:,2]),max(outward[:,2])],'lip_wkt':lip.simplify(.005).wkt,'bed_levels':[]}
    for z in np.arange(.2,max(outward[:,2]),1):
        vol=section(real,z)
        report['bed_levels'].append({'z':z,'model_bounds':vol.bounds,'part_overlap_roof_area_mm2':vol.intersection(roof).area,'part_solid_mm2':vol.area})
    args.output.write_text(json.dumps(report,indent=2)+'\n')
