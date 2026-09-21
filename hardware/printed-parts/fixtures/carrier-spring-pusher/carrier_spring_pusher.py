"""Flat reusable axial spring-loading tool for the complete enclosure trial.

The canonical part lies flat on XY with +Z print-up. Rotate it about X by
-90 degrees to put the thickness along the installed spring axis +Y.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
NAME='carrier-spring-pusher'
TIP_D=6.3
THICKNESS=2.0
TONGUE_LENGTH=10.0
TONGUE_WIDTH=3.0
HELD_SPRING_LENGTH=12.15


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build():
    disc=cq.Solid.makeCylinder(TIP_D/2,THICKNESS,cq.Vector(),cq.Vector(0,0,1))
    tongue=cq.Solid.makeBox(TONGUE_LENGTH,TONGUE_WIDTH,THICKNESS,
                          cq.Vector(-TONGUE_LENGTH,-TONGUE_WIDTH/2,0))
    return disc.fuse(tongue).clean()


def installed(interface,side=1):
    """Tool at release; the pusher's aft face fixes the held spring length."""
    if side not in (-1,1):raise ValueError('side must be -1 or +1')
    station=next(s for s in interface['spring_stations'] if s['x']*side>0)
    tip=station['bore_floor_y']-HELD_SPRING_LENGTH
    shape=build()
    if side<0:shape=shape.rotate((0,0,0),(0,0,1),180)
    return shape.rotate((0,0,0),(1,0,0),-90).translate(
        (station['x'],tip-THICKNESS,station['z']))


def selftest():
    body=build();b=body.BoundingBox()
    if not body.isValid() or len(body.Solids())!=1:raise ValueError('Tool is not one valid body')
    if any(abs(a-c)>1e-6 for a,c in zip((b.xlen,b.ylen,b.zlen),(TONGUE_LENGTH+TIP_D/2,TIP_D,THICKNESS))):
        raise ValueError('Tool dimensions changed')
    if abs(b.zmin)>1e-6:raise ValueError('Tool does not start on the print bed')
    # Every layer has the same native section; no unsupported overhang or roof.
    lower=body.intersect(cq.Solid.makeBox(30,20,.2,cq.Vector(-15,-10,0)))
    if abs(lower.Volume()/.2-body.Volume()/THICKNESS)>1e-6:raise ValueError('Footprint changes through thickness')
    print('ok carrier-spring-pusher: one flat solid, constant section, 2.0 mm thickness')
    return body


def main():
    sys.path[:0]=[str(ROOT/'hardware/scripts')]
    from _cadq_export import export_assembly
    from _material_base import M_PETGF_BLACK,one_body
    from flute_payload import cut
    import trimesh
    body=selftest()
    step=HERE/(NAME+'.step');stl=HERE/(NAME+'.stl')
    cq.exporters.export(body,str(stl),tolerance=.015,angularTolerance=.04)
    export_assembly(one_body(cq.Workplane(obj=body),NAME,M_PETGF_BLACK),str(step))
    cut(step,stl)
    mesh=trimesh.load_mesh(stl)
    if not mesh.is_watertight or len(mesh.split())!=1:raise ValueError('Tool mesh is not one closed body')
    report={
        'status':'native_tool_exported_for_complete_enclosure_trial',
        'scope':'Reusable temporary assembly tool. Its native route is recorded separately; actual spring force, handling effort and tool durability remain unmeasured.',
        'quantity_required':1,
        'reuse_sequence':'Load and seat left half, remove pusher so left spring expands into both cups, then turn the same tool 180 degrees about the spring axis and use it for the right half.',
        'print_frame':'Flat XY, broad face on bed at Z0, +Z up; no rotation required.',
        'print_dimensions_mm':{'x':TONGUE_LENGTH+TIP_D/2,'y':TIP_D,'z':THICKNESS},
        'tip_diameter_mm':TIP_D,'tongue_length_from_tip_center_mm':TONGUE_LENGTH,
        'tongue_width_mm':TONGUE_WIDTH,'constant_thickness_mm':THICKNESS,
        'held_spring_length_mm':HELD_SPRING_LENGTH,
        'support_required':False,
        'toolpath_review':'Confirm the whole tongue/head footprint survives every tool layer; at 0.20 mm uniform layer height the 2.0 mm body is ten layers. Use the actual slice layer heights for the recorded count.',
        'native_valid':body.isValid(),'native_solids':len(body.Solids()),'native_volume_mm3':body.Volume(),
        'mesh_watertight':True,'mesh_bodies':1,'mesh_faces':len(mesh.faces),
        'source_sha256':{str(Path(__file__).relative_to(ROOT)):sha(__file__)},
        'artifacts':{str(p.relative_to(ROOT)):sha(p) for p in (step,stl,step.with_suffix('.step.mesh'))}}
    (HERE/'geometry-check.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    if sys.argv[1:]==['selftest']:selftest()
    else:main()
