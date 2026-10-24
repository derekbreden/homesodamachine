"""Native empty access panel with four discrete heatset bosses and a pry notch.

Run manually through the shared CAD queue. The study keeps production geometry
separate and contains the complete nominal screw/insert/counterbore stack.
"""
from pathlib import Path
import hashlib
import importlib.util
import json

import cadquery as cq
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(result)
    return result


ceiling = module('access_ceiling', HERE.parent / 'ceiling-fit/ceiling.py')


def rectangle(bounds, radius=0):
    shape = cq.Solid.makeBox(bounds['xmax']-bounds['xmin'],
        bounds['ymax']-bounds['ymin'], bounds['zmax']-bounds['zmin'],
        cq.Vector(bounds['xmin'], bounds['ymin'], bounds['zmin']))
    return cq.Workplane(obj=shape).edges('|Z').fillet(radius).val() if radius else shape


def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))


def cylinder(radius,x,y,z0,z1):
    return cq.Solid.makeCylinder(radius,z1-z0,cq.Vector(x,y,z0))


def screw(f):
    """Local head-bearing face is Z0; shaft extends in -Z."""
    shaft=cylinder(f['screw_diameter_mm']/2,0,0,-f['screw_length_mm'],0)
    head=cylinder(f['screw_head_diameter_mm']/2,0,0,0,f['screw_head_height_mm'])
    socket=(cq.Workplane('XY').workplane(offset=f['screw_head_height_mm']-1.6)
        .polygon(6,2.9).extrude(1.7).val())
    return shaft.fuse(head).cut(socket).clean()


def insert(f):
    """Nominal RX outside and thread-root envelopes; knurl bands are illustrated."""
    radius=f['insert_outer_diameter_mm']/2;length=f['insert_length_mm']
    shape=cylinder(radius-.13,0,0,-length,0)
    for z in np.linspace(-length+.3,-.5,5):
        shape=shape.fuse(cylinder(radius,0,0,float(z),float(z+.22)))
    return shape.cut(cylinder(f['insert_thread_root_diameter_mm']/2,0,0,-length-.1,.1)).clean()


def back_wall(plan):
    """Carry the C14's pocket and mounting holes with its revised flange pose."""
    context=json.loads((HERE.parent/'wall-supported/context-plan.json').read_text())
    wall=rectangle(context['rear_wall']).cut(rectangle(context['interior_panel_relief']))
    for port in context['wet_ports']:
        wall=wall.cut(cq.Solid.makeCylinder(port['bore_diameter_mm']/2,9.02,
            cq.Vector(port['center_x_mm'],462.29,port['center_z_mm']),cq.Vector(0,1,0)))
    c14=context['dry_openings']['c14'];x,y,z=plan['c14']['flange_centre_mm']
    for size,start in (('flange_pocket_half_xz_mm','flange_pocket_ymin_mm'),
                       ('body_opening_half_xz_mm','body_opening_ymin_mm')):
        hx,hz=c14[size]
        wall=wall.cut(box(x-hx,x+hx,c14[start],471.31,z-hz,z+hz))
    for dx in (-c14['mount_pitch_mm']/2,c14['mount_pitch_mm']/2):
        wall=wall.cut(cq.Solid.makeCylinder(c14['mount_hole_radius_mm'],9.02,
            cq.Vector(x+dx,462.29,z),cq.Vector(0,1,0)))
    jack=module('access_keystone',ROOT/'hardware/reference/riteav-keystone/riteav_keystone.py')
    jx,jy,jz=context['dry_openings']['keystone']['face_center_mm']
    patch,catches=jack.receptacle_boss(jx,jz,jy,462.3)
    cutter,_=jack.receptacle_cut(jx,jz,jy)
    if patch is not None:wall=wall.fuse(patch)
    wall=wall.cut(cutter)
    if catches is not None:wall=wall.fuse(catches)
    return wall.clean()


def export(name,shape,native=True):
    out=HERE/'parts';out.mkdir(exist_ok=True)
    if native:cq.exporters.export(shape,str(out/(name+'.step')))
    vertices,faces=shape.tessellate(.06,.15)
    np.savez_compressed(out/(name+'.npz'),
        v=np.asarray([p.toTuple() for p in vertices],np.float32),
        f=np.asarray(faces,np.uint32))


def main():
    plan=json.loads((HERE/'panel-plan.json').read_text());p=plan['panel'];f=plan['fasteners']
    source=(HERE/plan['ceiling_plan']).resolve();original=ceiling.build(source)
    bounds={key:p[key] for key in ('xmin','xmax','ymin','ymax','zmin','zmax')}
    gap=p['edge_clearance_mm'];radius=p['corner_radius_mm']
    panel=rectangle(bounds,radius)
    opening={key:value+(gap if key.endswith('max') else -gap) for key,value in bounds.items()}
    opening.update(zmin=p['zmin']-20,zmax=p['zmax']+1)
    fixed=original.cut(rectangle(opening,radius+gap))
    # These four pads are the complete bearing support. No edge ledge joins them.
    half=f['boss_width_mm']/2;depth=f['boss_depth_mm']/2
    boss=box(-half,half,-depth,depth,f['boss_bottom_z_mm'],f['bearing_z_mm'])
    boss=boss.cut(cylinder(f['pilot_diameter_mm']/2,0,0,
        f['bearing_z_mm']-f['pilot_depth_mm'],f['bearing_z_mm']+.1)).clean()
    for x,y in f['centres_xy_mm']:
        fixed=fixed.fuse(boss.translate((x,y,0)))
        panel=panel.cut(cylinder(f['clearance_hole_diameter_mm']/2,x,y,p['zmin']-.1,p['zmax']+.1),
            cylinder(f['counterbore_diameter_mm']/2,x,y,f['counterbore_floor_z_mm'],p['zmax']+.1))
    notch=plan['pry_notch'];cx=notch['centre_x_mm'];w=notch['width_mm']/2
    panel=panel.cut(box(cx-w,cx+w,p['ymin']-.1,p['ymin']+notch['depth_mm'],p['zmin']-.1,p['zmax']+.1)).clean()
    fixed=fixed.clean();bolt=screw(f);heatset=insert(f)
    parts={'access-fixed-ceiling':fixed,'electronics-access-panel':panel,
           'access-back-wall':back_wall(plan),'panel-screw-m3x12':bolt,
           'panel-insert-rx-m3x5p7':heatset}
    for name,shape in parts.items():export(name,shape)
    export('panel-boss',boss,native=False)
    # True native half sections through one fastener axis show every bearing floor.
    x,y=f['centres_xy_mm'][f['detail_corner_index']]
    window=box(x-12,x+12,y,y+12,f['boss_bottom_z_mm']-1,p['zmax']+1)
    section={'section-frame':fixed,'section-panel':panel,
             'section-screw':bolt.translate((x,y,f['counterbore_floor_z_mm'])),
             'section-insert':heatset.translate((x,y,f['bearing_z_mm']))}
    for name,shape in section.items():export(name,shape.intersect(window).clean(),native=False)
    tip=f['counterbore_floor_z_mm']-f['screw_length_mm']
    bottom=f['bearing_z_mm']-f['pilot_depth_mm']
    report={
        'scope':plan['scope'],'source_plan_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'valid_single_solids':{name:shape.isValid() and len(shape.Solids())==1 for name,shape in parts.items()},
        'panel_size_mm':[p['xmax']-p['xmin'],p['ymax']-p['ymin'],p['zmax']-p['zmin']],
        'panel_bearing':'Four discrete 18 × 12 mm heatset bosses; no perimeter rim',
        'boss_centres_xy_mm':f['centres_xy_mm'],
        'fastener_stack_mm':{'head_bearing_z':f['counterbore_floor_z_mm'],
            'head_top_z':f['counterbore_floor_z_mm']+f['screw_head_height_mm'],
            'head_recess_below_show_face':p['zmax']-f['counterbore_floor_z_mm']-f['screw_head_height_mm'],
            'panel_under_head':f['counterbore_floor_z_mm']-p['zmin'],
            'insert_top_z':f['bearing_z_mm'],'insert_bottom_z':f['bearing_z_mm']-f['insert_length_mm'],
            'screw_tip_z':tip,'pilot_bottom_z':bottom,'tip_reserve':tip-bottom,
            'insert_engagement':f['insert_length_mm'],'blind_floor_stock':bottom-f['boss_bottom_z_mm'],
            'minimum_boss_stock_from_pilot':min(half,depth)-f['pilot_diameter_mm']/2,
            'counterbore_to_panel_edge':f['edge_offset_mm']-f['counterbore_diameter_mm']/2},
        'closed_panel_fixed_ceiling_intersection_mm3':max(0.,panel.intersect(fixed).Volume()),
        'lift_samples':[{'lift_mm':lift,'fixed_ceiling_intersection_mm3':max(0.,panel.translate((0,0,lift)).intersect(fixed).Volume())}
            for lift in (.1,1.,3.,9.,30.,plan['illustrated_lift_mm'])],
        'equipment_carried_by_panel':[],
        'hardware_scope':'Nominal exterior and thread-root/knurl bands; mating thread and heatset press envelopes intentionally overlap',
        'pry_notch':notch,'retention_detail':plan['retention_detail']}
    (HERE/'geometry-report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
