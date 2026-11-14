"""Slice the tip through a gradual plug ramp while preserving its print pose."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import math
from pathlib import Path

import numpy as np
import trimesh

from tip_geometry import CANONICAL_POINT, physical_origin, triangles

NORMAL_COURSE = .20
BED_THROUGH = .92
START_HOLD = 18.44
END_HOLD = 29.0
NORMAL_AGAIN = 66.20
BEARING_ANGLE = 35.0
PEAK_ANGLE = 15.0
FLAT_SHOULDER_Y_PADDING = 1.45
EDGE_EASE_WIDTH = 2.0
MAX_REMAP_EDGE_ERROR = .0125


@dataclass(frozen=True)
class TipWarp:
    shoulder_xyz: tuple[float, float, float]
    angle_degrees: float = PEAK_ANGLE
    shoulder_layer: float | None = None

    def __post_init__(self):
        if self.shoulder_layer is None:
            object.__setattr__(self, "shoulder_layer", self.shoulder_xyz[2])

    @property
    def sec_minus_one(self):
        return 1 / math.cos(math.radians(self.angle_degrees)) - 1

    @property
    def tangent(self):
        return math.tan(math.radians(self.angle_degrees))

    @property
    def exact_y_limits(self):
        radius = 13.5
        center_v = 4.024
        c = math.cos(math.radians(BEARING_ANGLE))
        return (self.shoulder_xyz[1] + (center_v-radius)*c-FLAT_SHOULDER_Y_PADDING,
                self.shoulder_xyz[1] + (center_v+radius)*c+FLAT_SHOULDER_Y_PADDING)

    def effective_y(self, y):
        low, high = self.exact_y_limits
        left = np.clip((low-y)/EDGE_EASE_WIDTH, 0, 1)
        right = np.clip((y-high)/EDGE_EASE_WIDTH, 0, 1)
        drift = lambda x: EDGE_EASE_WIDTH * x * (1 - x/2)
        return np.clip(y, low, high) - drift(left) + drift(right)

    def parameters_at(self, u):
        w0 = START_HOLD - BED_THROUGH
        w1 = NORMAL_AGAIN - END_HOLD
        left = np.clip((u-BED_THROUGH)/w0, 0, 1)
        right = np.clip((NORMAL_AGAIN-u)/w1, 0, 1)
        a = left*left*(3-2*left)*right*right*(3-2*right)
        return a, (u-self.shoulder_layer)*a

    def forward(self, y, u):
        # The height field keeps model XY fixed and returns to the same physical Z at
        # the bed and nose. Along the hold the pitch is normal to the course plane.
        a, b = self.parameters_at(u)
        root = self.shoulder_xyz[2] - self.tangent * (self.effective_y(y)-self.shoulder_xyz[1])
        return u + a*(root-self.shoulder_layer) + self.sec_minus_one*b

    def derivative(self, y, u):
        y, u = np.asarray(y), np.asarray(u)
        ds = .0001
        return (self.forward(y,u+ds)-self.forward(y,u-ds))/(2*ds)

    def inverse(self,y,z):
        low,high=np.minimum(z,BED_THROUGH),np.maximum(z,NORMAL_AGAIN)
        for _ in range(36):
            middle=(low+high)*.5
            too_low=self.forward(y,middle)<z
            low=np.where(too_low,middle,low)
            high=np.where(too_low,high,middle)
        return np.where((z<=BED_THROUGH)|(z>=NORMAL_AGAIN),z,(low+high)*.5)


def edge_templates(faces, edge_vertices, flags):
    a,b,c=faces.T
    x,y,z=edge_vertices.T
    recipes=[
        [(a,b,c)],[(a,x,c),(x,b,c)],[(a,b,y),(a,y,c)],
        [(x,b,y),(a,x,y),(a,y,c)],[(a,b,z),(b,c,z)],
        [(a,x,z),(x,b,c),(x,c,z)],[(c,z,y),(b,y,z),(b,z,a)],
        [(a,x,z),(x,b,y),(z,y,c),(x,y,z)]
    ]
    pieces=[]
    for pattern, rows in enumerate(recipes):
        match=flags==pattern
        if match.any():
            pieces.extend(np.column_stack([v[match] for v in row]) for row in rows)
    return np.concatenate(pieces,axis=0)


def refine(mesh,warp):
    vertices=mesh.vertices.copy()
    faces=mesh.faces.copy()
    measured={}
    for _ in range(12):
        placed=trimesh.Trimesh(vertices=vertices,faces=faces,process=False)
        e=placed.edges_unique
        orig_p=vertices[e]
        sy=orig_p[:,:,1]
        sz=orig_p[:,:,2]
        wz=warp.inverse(sy,sz)
        max_errors=np.zeros(len(e))
        for t in (.25,.5,.75):
            residual=np.abs(warp.forward(sy[:,0]*(1-t)+sy[:,1]*t,wz[:,0]*(1-t)+wz[:,1]*t)
                            -(sz[:,0]*(1-t)+sz[:,1]*t))
            max_errors=np.maximum(max_errors,residual)
        face_xy=vertices[faces]
        face_warp=warp.inverse(face_xy[:,:,1],face_xy[:,:,2])
        centroid_error=np.abs(warp.forward(face_xy[:,:,1].mean(axis=1),face_warp.mean(axis=1))
                              -face_xy[:,:,2].mean(axis=1))
        refine_indices = max_errors > MAX_REMAP_EDGE_ERROR
        needs_center=centroid_error > MAX_REMAP_EDGE_ERROR
        if needs_center.any():
            refine_indices[placed.edges_unique_inverse.reshape((-1,3))[needs_center].ravel()] = True
        if not refine_indices.any():
            measured={"max_sampled_edge_remap_error_mm":float(max_errors.max()),
                      "max_sampled_centroid_remap_error_mm":float(centroid_error.max())}
            break
        midpoints=orig_p[refine_indices].mean(axis=1)
        mid_id=np.full(len(e),-1,dtype=np.int64)
        mid_id[refine_indices]=np.arange(len(midpoints))+len(vertices)
        which=mid_id[placed.edges_unique_inverse].reshape((-1,3))
        flags=(which>=0)@np.array([1,2,4])
        faces=edge_templates(faces,which,flags)
        vertices=np.concatenate((vertices,midpoints),axis=0)
    if not measured:
        raise ValueError("Nonplanar slicing mesh refinement did not meet fidelity target")
    return vertices,faces,measured


def prepare(mesh_path,project,output):
    mesh=trimesh.load(mesh_path,force="mesh")
    source=triangles(mesh_path)
    physical,translation=physical_origin(project,source)
    world=mesh.vertices@physical.T+translation
    warp=TipWarp(tuple(physical@CANONICAL_POINT+translation))
    ys=np.linspace(world[:,1].min(),world[:,1].max(),221)
    us=np.linspace(BED_THROUGH,NORMAL_AGAIN,301)
    derivative=warp.derivative(ys[:,None],us[None,:])
    if derivative.min()<=.08:
        raise ValueError(f"Tip inverse needs a single, continuous crossing, got {derivative.min()}")
    world_mesh=trimesh.Trimesh(vertices=world,faces=mesh.faces,process=False)
    refined,faces,error=refine(world_mesh,warp)
    mapped=refined.copy()
    mapped[:,2]=warp.inverse(mapped[:,1],mapped[:,2])
    in_model=warp.derivative(mapped[:,1],mapped[:,2])
    mapped=(mapped-translation)@physical
    virtual=trimesh.Trimesh(vertices=mapped,faces=faces,process=False)
    if not virtual.is_watertight:
        raise ValueError("The conforming warp yielded an open model")
    virtual.export(output)
    result=dict(purpose=__doc__,orientation_degrees=-70-BEARING_ANGLE, bearing_plane_degrees=BEARING_ANGLE,
                authored_plane_pick_world_xyz_mm=warp.shoulder_xyz,
                physical_cad_to_plate_translation=translation.tolist(),
                physical_rotation=physical.tolist(),
                virtual_shoulder_z_mm=warp.shoulder_layer,
                incoming_fade_virtual_mm=[BED_THROUGH,START_HOLD],
                outgoing_fade_virtual_mm=[END_HOLD,NORMAL_AGAIN],
                exactly_inclined_virtual_mm=[START_HOLD,END_HOLD],
                xy_limits_exact_plane_y_mm=warp.exact_y_limits,
                outside_edge_blend_width_y_mm=EDGE_EASE_WIDTH,
                full_angle_degrees=warp.angle_degrees,
                normal_course_mm=NORMAL_COURSE,
                maximum_cad_error=dict(error,tip_unchanged_under_z=BED_THROUGH,tip_unchanged_above_z=NORMAL_AGAIN),
                area_scope=dict(physical_print_bounds_mm=[world.min(axis=0).tolist(),world.max(axis=0).tolist()],
                                donor_nominal_physical_pitch_sample_mm=[float(in_model.min()*NORMAL_COURSE),float(in_model.max()*NORMAL_COURSE)]),
                original_facet_count=len(mesh.faces),warped_facet_count=len(virtual.faces),
                minimum_invertibility_derivative=float(derivative.min()))
    output.with_suffix('.json').write_text(json.dumps(result,indent=2)+"\n")


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mesh',type=Path)
    parser.add_argument('ref_project',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    prepare(args.mesh,args.ref_project,args.output)
