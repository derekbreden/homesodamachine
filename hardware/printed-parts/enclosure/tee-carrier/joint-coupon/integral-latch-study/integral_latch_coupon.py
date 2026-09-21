#!/usr/bin/env python3
"""Two-piece joint coupon with an integral broad-wall latch in the receiver.

The proven left half and key/lap contact faces are preserved. Forward entry bends
one broad receiver wall; the existing outward slide lets its lip engage beside
the key. There is no separate keeper and no additional assembly operation.
"""
from __future__ import annotations
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import cadquery as cq

HERE=Path(__file__).resolve().parent
V1=HERE.parent
spec=importlib.util.spec_from_file_location('proven_joint_coupon',V1/'joint_coupon.py')
v1=importlib.util.module_from_spec(spec)
spec.loader.exec_module(v1)
box,union=v1.box,v1.union

# The broad-wall pattern follows the faucet display cover: a long thin wall,
# 1.2 mm positive engagement and a square 3 mm retaining lip. Actual force and
# durability remain a physical PET-GF reading, not a CAD result.
WALL_X=(-2.15,10.85)
WALL_Z=(11.0,47.5)
ROOT_Z=46.5
ROOT_FILLET=0.45
WALL_T=1.3
WALL_FORE=v1.HEAD_Y[1]+v1.STATIC_AIR
WALL_AFT=WALL_FORE+WALL_T
LIP_X=v1.KEEPER_X
LIP_Z=(12.8,15.8)
ENGAGEMENT=1.2
LIP_FORE=v1.HEAD_Y[1]-ENGAGEMENT
DEFLECTION=ENGAGEMENT+v1.STATIC_AIR
RELIEF_X=(WALL_X[0]-.25,WALL_X[1]+.25)
RELIEF_Z=(WALL_Z[0]-.4,ROOT_Z)
RELIEF_FORE=WALL_FORE-.60
RELEASE_X=(-1.0,1.8)
RELEASE_Z=(18.0,21.7)
TOL=1e-5


def left_half():
    return v1.left_half()


def fixed_receiver():
    """Original entry, stem and head sweeps; only the receiver latch region changes."""
    body=box((v1.RIGHT_EDGE_X,25.),(0.,6.),(0.,v1.HEIGHT))
    cuts=[]
    for z in v1.KEY_ZS:
        cuts.extend((
            box(v1.ENTRY_X,(-.1,6.1),(z-v1.HEAD_Z_HALF-v1.SUPPORTED_AIR,z+v1.HEAD_Z_HALF+v1.SUPPORTED_AIR)),
            box((v1.HEAD_X[0]-v1.STATIC_AIR,v1.ENTRY_X[1]),(v1.HEAD_Y[0]-v1.STATIC_AIR,6.1),
                (z-v1.HEAD_Z_HALF-v1.SUPPORTED_AIR,z+v1.HEAD_Z_HALF+v1.SUPPORTED_AIR)),
            box((v1.STEM_X[0]-v1.STATIC_AIR,v1.STEM_X[1]+v1.TRAVEL+v1.STATIC_AIR),(-.1,v1.STEM_Y[1]+v1.STATIC_AIR),
                (z-v1.STEM_Z_HALF-v1.SUPPORTED_AIR,z+v1.STEM_Z_HALF+v1.SUPPORTED_AIR)),
        ))
    cuts.append(box(RELIEF_X,(RELIEF_FORE,6.1),RELIEF_Z))
    return body.cut(*cuts).clean()


def displacement(z,amount):
    """Prescribed clearance family; not an elastic solution or a force prediction."""
    u=max(0.,min(1.,(ROOT_Z-z)/(ROOT_Z-LIP_Z[1])))
    return amount*u*u*(3.-u)/2.


def flexible_wall(amount=0.):
    zs=sorted(set([WALL_Z[0],LIP_Z[0],LIP_Z[1],ROOT_Z,WALL_Z[1]]+
                  [LIP_Z[1]+(ROOT_Z-LIP_Z[1])*i/24 for i in range(25)]))
    points=[(WALL_FORE+displacement(z,amount),z) for z in zs]
    points += [(WALL_AFT+displacement(z,amount),z) for z in reversed(zs)]
    wall=(cq.Workplane('YZ',origin=(WALL_X[0],0,0)).polyline(points).close()
          .extrude(WALL_X[1]-WALL_X[0]).val())
    # A 2.5 mm wide access probe reaches this slot from the centre corridor, between
    # the keys and between the neighbouring coils. Follow the prescribed wall
    # shape so the slot remains a through opening at every checked deflection.
    slot_zs=sorted(set([*RELEASE_Z]+[z for z in zs if RELEASE_Z[0]<z<RELEASE_Z[1]]))
    points=[(WALL_FORE-.1+displacement(z,amount),z) for z in slot_zs]
    points += [(WALL_AFT+.1+displacement(z,amount),z) for z in reversed(slot_zs)]
    slot=(cq.Workplane('YZ',origin=(RELEASE_X[0],0,0)).polyline(points).close()
          .extrude(RELEASE_X[1]-RELEASE_X[0]).val())
    return wall.cut(slot).clean()


def lip(amount=0.):
    return box(LIP_X,(LIP_FORE+amount,WALL_FORE+amount),LIP_Z)


def release_tool(amount=0.):
    tool_z=(RELEASE_Z[0]+1.2,RELEASE_Z[0]+1.6)
    offset=displacement(sum(tool_z)/2,amount)
    return box((RELEASE_X[0]+.15,RELEASE_X[1]-.15),
               (RELIEF_FORE+.10+offset,25.+offset),tool_z)


def right_half(amount=0.,with_lip=True):
    body=union([fixed_receiver(),flexible_wall(amount),*([lip(amount)] if with_lip else [])])
    if amount==0.:
        edges=[]
        for e in body.Edges():
            bb=e.BoundingBox();c=e.Center()
            if (e.geomType()=='LINE' and bb.xlen>10 and bb.ylen<1e-6 and bb.zlen<1e-6
                    and abs(c.z-ROOT_Z)<1e-6
                    and min(abs(c.y-WALL_FORE),abs(c.y-WALL_AFT))<1e-6):
                edges.append(e)
        if len(edges)!=2:
            raise ValueError(f'expected two broad wall root edges, got {len(edges)}')
        body=body.fillet(ROOT_FILLET,edges).clean()
    return body


def check():
    left,right=left_half(),right_half()
    flexed=right_half(DEFLECTION)
    rows={};errors=[]
    def clear(name,a,b):
        volume=a.intersect(b).Volume();rows[name]={'overlap_mm3':volume}
        if volume>TOL:errors.append(f'{name}: {volume:.6g} mm3 overlap')
    def contact(name,a,b):
        volume=a.intersect(b).Volume();rows[name]={'overlap_mm3':volume}
        if volume<=TOL:errors.append(f'{name}: no positive native contact')
    for name,body in (('left',left),('right',right),('right_prescribed_deflection',flexed)):
        bb=body.BoundingBox()
        rows[name]={'valid':body.isValid(),'solids':len(body.Solids()),'volume_mm3':body.Volume(),
                    'bounds_mm':[bb.xlen,bb.ylen,bb.zlen]}
        if not body.isValid() or len(body.Solids())!=1:errors.append(name+' is not one valid solid')
    clear('assembled_two_halves',left,right)
    # Exact original contact geometry, not just matching dimension labels.
    original_left,original_right=v1.left_half(),v1.right_half()
    clear('left_addition',left,box((-100,100),(-100,100),(-100,100)).cut(original_left))
    clear('left_missing',original_left,box((-100,100),(-100,100),(-100,100)).cut(left))
    bearing=box((v1.RIGHT_EDGE_X,v1.LAP_X[1]),(0.,v1.HEAD_Y[0]-v1.STATIC_AIR),(0.,v1.HEIGHT))
    before,after=original_right.intersect(bearing),right.intersect(bearing)
    rows['unchanged_fore_lap_and_key_shoulders']={'added_mm3':after.cut(before).Volume(),'removed_mm3':before.cut(after).Volume()}
    if max(rows['unchanged_fore_lap_and_key_shoulders'].values())>TOL:errors.append('key/lap bearing geometry changed')
    for i,z in enumerate(v1.KEY_ZS,1):
        entry=union([box((v1.HEAD_X[0]+v1.TRAVEL,v1.HEAD_X[1]+v1.TRAVEL),(-8.,v1.HEAD_Y[1]),(z-v1.HEAD_Z_HALF,z+v1.HEAD_Z_HALF)),
                     box((v1.STEM_X[0]+v1.TRAVEL,v1.STEM_X[1]+v1.TRAVEL),(-8.,v1.STEM_Y[1]),(z-v1.STEM_Z_HALF,z+v1.STEM_Z_HALF))])
        slide=union([box((v1.HEAD_X[0],v1.HEAD_X[1]+v1.TRAVEL),v1.HEAD_Y,(z-v1.HEAD_Z_HALF,z+v1.HEAD_Z_HALF)),
                     box((v1.STEM_X[0],v1.STEM_X[1]+v1.TRAVEL),v1.STEM_Y,(z-v1.STEM_Z_HALF,z+v1.STEM_Z_HALF))])
        clear(f'key_{i}_complete_forward_entry_with_wall_deflected',entry,flexed)
        clear(f'key_{i}_complete_outward_slide_with_wall_deflected',slide,flexed)
    # The existing forward entry supplies a force normal to the broad wall.
    # There is no second keeper, pin or manual latch operation after the slide.
    entry_key=left.translate((v1.TRAVEL,0,0))
    contact('key_drives_lip_during_forward_entry',entry_key,lip())
    clear('full_body_entry_end_with_wall_deflected',left,flexed.translate((-v1.TRAVEL,0,0)))
    contact('latched_reverse_slide_bearing',left,right.translate((-v1.STATIC_AIR-.001,0,0)))
    clear('reverse_slide_contact_is_integral_lip',left,right_half(with_lip=False).translate((-v1.STATIC_AIR-.001,0,0)))
    clear('released_reverse_slide_endpoint',left,flexed.translate((-v1.TRAVEL,0,0)))
    contact('fore_aft_key_bearing',left,right.translate((0,v1.STATIC_AIR+.001,0)))
    contact('lap_compression_bearing',left,right.translate((0,-.001,0)))
    contact('outward_shear_bearing',left,right.translate((v1.STATIC_AIR+.001,0,0)))
    for sign in (-1,1):
        contact(f'vertical_shear_bearing_{sign:+d}',left,right.translate((0,0,sign*(v1.SUPPORTED_AIR+.001))))
    tool=release_tool()
    clear('rear_flat_blade_access_to_release_slot',tool,right)
    clear('release_tool_clears_left_half',tool,left)
    clear('rear_flat_blade_access_when_wall_is_deflected',release_tool(DEFLECTION),flexed)
    clear('release_tool_clears_left_half_when_deflected',release_tool(DEFLECTION),left)
    # The declared relaxed-to-deflected wall envelope keeps continuous normal
    # clearance to the fixed receiver. Its internal force law is not asserted.
    for i in range(1,6):
        amount=DEFLECTION*i/5
        free_wall=union([flexible_wall(amount),lip(amount)]).intersect(
            box((-100,100),(-100,100),(-100,ROOT_Z)))
        clear(f'wall_fixed_body_clearance_at_{amount:.2f}',free_wall,fixed_receiver())
    rows['integral_root_attachment']={'shared_volume_mm3':flexible_wall().intersect(fixed_receiver()).Volume(),
                                    'height_mm':WALL_Z[1]-ROOT_Z}
    length=ROOT_Z-ROOT_FILLET-LIP_Z[1]
    strain=1.5*WALL_T*DEFLECTION/length**2
    return {'status':'two_piece_coupon_geometry_pass' if not errors else 'two_piece_coupon_geometry_fail',
        'production_ready':False,'parts':2,'additional_assembly_operations':0,
        'dimensions_mm':{'wall_width':WALL_X[1]-WALL_X[0],'wall_thickness':WALL_T,
            'effective_flex_length':length,'root_fillet':ROOT_FILLET,
            'lip_engagement':ENGAGEMENT,'lip_height':LIP_Z[1]-LIP_Z[0],
            'required_tip_clearance_deflection':DEFLECTION,'outward_slide':v1.TRAVEL,
            'vertical_relief_gap':WALL_FORE-RELIEF_FORE,
            'release_slot':[RELEASE_X[1]-RELEASE_X[0],RELEASE_Z[1]-RELEASE_Z[0]]},
        'beam_surface_strain_estimate':strain,
        'mechanics_scope':'Small-deflection 3*t*delta/(2*L^2) comparison only. The broad plate, slot, root, layer bonds, force and fatigue require the PET-GF coupon.',
        'readings':rows,'errors':errors,
        'physical_status':'unprinted; existing v1 keys/lap accepted by Derek, integral wall/lip unqualified',
        'assembly':'Forward entry bends the integral wall; the same 3.25 mm outward slide lets the lip return beside the key.',
        'release':'Pull the broad wall aft through the rear slot while the receiver slides inboard. The 2.5 by 0.4 mm probe establishes a clear approach corridor; the actual hook/pry gesture and force require the physical trial.',
        'print_orientation':{'left':'exact original upright v1 mesh; existing physical left coupon can be reused',
            'right':'inverted in Z, wall root first and long wall vertical, matching broad sidewalls rising from the faucet cover bezel'},
        'support_geometry':{'wall_relief':'0.6 mm vertical gap, open at the long edges and free tip; no horizontal support sheet is required inside it',
            'lip':'square projection in the open lower key-entry window; support removes through that window before assembly',
            'key_pockets':'unchanged square contact faces; crowns open aft for straight support removal',
            'status':'geometry review only; actual sliced roads and physical removal remain unverified'},
    }


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--export',action='store_true')
    args=parser.parse_args(argv)
    result=check()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    result['v1_source_sha256']=hashlib.sha256((V1/'joint_coupon.py').read_bytes()).hexdigest()
    if args.export and not result['errors']:
        import trimesh
        result['printed_meshes']={}
        for name,body in (('left',left_half()),('right',right_half())):
            step=HERE/f'integral-coupon-{name}.step'
            path=HERE/f'integral-coupon-{name}.stl'
            if name=='left':
                # Reuse the accepted canonical assets; duplicate identical hashes
                # would add a second name for the same geometry to the public pack.
                step=V1/'coupon-only-left.step'
                path=V1/'coupon-only-left.stl'
            else:
                cq.exporters.export(body,str(step))
                printed=body.rotate((0,0,0),(1,0,0),180)
                bb=printed.BoundingBox();printed=printed.translate((-bb.xmin,-bb.ymin,-bb.zmin))
                cq.exporters.export(printed,str(path),tolerance=.02,angularTolerance=.08)
            mesh=trimesh.load_mesh(path)
            delta=abs(float(mesh.volume)-body.Volume())
            ok=bool(mesh.is_watertight and mesh.is_winding_consistent and mesh.volume>0 and abs(mesh.bounds[0][2])<1e-5 and delta<.05)
            result['printed_meshes'][name]={'path':str(path.relative_to(V1)),
                'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                'watertight':bool(mesh.is_watertight),'winding_consistent':bool(mesh.is_winding_consistent),
                'native_volume_difference_mm3':delta,'bounds_mm':mesh.bounds.tolist(),'pass':ok}
            if not ok:result['errors'].append(name+' print mesh fails native comparison')
        drawing=cq.Compound.makeCompound([left_half(),right_half().translate((30,10,0))])
        cq.exporters.export(drawing,str(HERE/'geometry.svg'),opt={'width':1100,'height':700,
            'projectionDir':(-1,2,.7),'showHidden':False,'showAxes':False,'strokeWidth':.13})
        tree=ET.parse(HERE/'geometry.svg')
        tree.getroot().insert(0,ET.Element('{http://www.w3.org/2000/svg}rect',width='100%',height='100%',fill='white'))
        tree.write(HERE/'geometry.svg',encoding='unicode',xml_declaration=True)
    if result['errors']:result['status']='two_piece_coupon_geometry_fail'
    (HERE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result['status'],'dimensions_mm':result['dimensions_mm'],
                      'errors':result['errors'],'parts':2},indent=2))
    return int(bool(result['errors']))


if __name__=='__main__':
    raise SystemExit(main())
