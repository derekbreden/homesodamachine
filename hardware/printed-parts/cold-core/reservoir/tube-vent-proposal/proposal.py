"""Review geometry for flush tube grips and two unfiltered reservoir air tubes.

This writes only the explicitly supplied output directory. Production generators,
STEPs, print recipes and the appliance viewer are not changed by this proposal.
Run with tools/cad-venv/bin/python; native context comes from the current assembly.
"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import sys

os.environ['HSM_NO_BUILD_LOCK'] = '1'
ROOT = next(p for p in Path(__file__).resolve().parents if (p/'hardware/scripts').is_dir())
CORE = ROOT/'hardware/printed-parts/cold-core'
for p in (ROOT/'hardware/scripts', ROOT/'hardware/manifold-layout', CORE,
          CORE/'reservoir', ROOT/'hardware/printed-parts/cadlib'):
    sys.path.insert(0, str(p))
import cadquery as cq
import reservoir as reservoir
import _cold_core_interface as interface
import _internal_routes as routes
from _foam_cap import top_cap_height, cap_face_z

VENT_XY = {'a': (120., -26.), 'b': (-102., -32.5)}
AIR_OD, AIR_ID = 4., 2.5
AIR_PRIDE = 6.
PASSAGE_D, PASSAGE_WALL = 5.2, 2.
LID_BOTTOM = reservoir.cap_assembly_lift + reservoir.cap_wall_height
LID_TOP = reservoir.cap_top_z
FLUID_GRIP = dict(waist_d=9., flare_d=11., bore_d=6.2, lead_d=7., lead_h=.4)
AIR_GRIP = dict(waist_d=6., flare_d=8., bore_d=3.9, lead_d=4.5, lead_h=.3)


def cylinder(xy, z0, z1, d):
    return cq.Solid.makeCylinder(d/2., z1-z0, cq.Vector(*xy, z0))


def spool_outer(xy, z0, z1, waist_d, flare_d, **_):
    h=(flare_d-waist_d)/2.  # exact 45-degree mating faces
    shaft=cylinder(xy,z0,z1,waist_d)
    lower=cq.Solid.makeCone(flare_d/2.,waist_d/2.,h,cq.Vector(*xy,z0))
    upper=cq.Solid.makeCone(waist_d/2.,flare_d/2.,h,cq.Vector(*xy,z1-h))
    return shaft.fuse(lower,upper).clean()


def grommet(xy, spec):
    outer=spool_outer(xy,LID_BOTTOM,LID_TOP,**spec)
    bore=cylinder(xy,LID_BOTTOM-.1,LID_TOP+.1,spec['bore_d'])
    h=spec['lead_h']
    lower=cq.Solid.makeCone(spec['lead_d']/2.,spec['bore_d']/2.,h,
                           cq.Vector(*xy,LID_BOTTOM))
    upper=cq.Solid.makeCone(spec['bore_d']/2.,spec['lead_d']/2.,h,
                           cq.Vector(*xy,LID_TOP-h))
    return outer.cut(bore.fuse(lower,upper)).clean()


def cut_seat(shape, xy, spec):
    seat=spool_outer(xy,LID_BOTTOM,LID_TOP,**spec)
    seat=seat.fuse(cylinder(xy,LID_BOTTOM-.1,LID_BOTTOM,spec['flare_d']),
                   cylinder(xy,LID_TOP,LID_TOP+.1,spec['flare_d']))
    return shape.cut(seat).clean()


def baffle(xy):
    # The lower grommet flare remains exposed through this 9mm opening.
    # The tube ends 1mm below the lid, 1mm above the closed baffle floor.
    shell=cylinder(xy,LID_BOTTOM-3.,LID_BOTTOM+.01,13.)
    shell=shell.cut(cylinder(xy,LID_BOTTOM-2.,LID_BOTTOM+.1,9.))
    x,y=xy
    for direction in (0,90,180,270):
        slot=cq.Solid.makeBox(10.,3.,2.,cq.Vector(x,y-1.5,LID_BOTTOM-2.))
        slot=slot.rotate((x,y,0),(x,y,1),direction)
        shell=shell.cut(slot)
    return shell.clean()


def cap_candidate(side):
    """The approved geometry is implemented by the production generator."""
    letter = 'a' if side == 1 else 'b'
    cap = reservoir.build_reservoir_cap(side).val().translate((0, 0, reservoir.cap_assembly_lift))
    grips = {f'grip-{letter}-{name}': grommet(xy, FLUID_GRIP)
             for name, xy in (('fill', reservoir.fill_position[side]), ('draw', reservoir.draw_position[side]))}
    grips[f'grip-{letter}-air'] = grommet(VENT_XY[letter], AIR_GRIP)
    return cap, grips


def bb_row(shape):
    b=shape.BoundingBox()
    return [b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]


def box_near(first,second,margin=0.):
    a,b=bb_row(first),bb_row(second)
    return not any(a[i]>b[i+3]+margin or b[i]>a[i+3]+margin for i in range(3))


def build(out, native_cache):
    out.mkdir(parents=True,exist_ok=True)
    native_index=json.loads((native_cache/'native-index.json').read_text())
    native={}
    def load(name):
        if name not in native:
            native[name]=cq.Shape.importBrep(str(native_cache/native_index['parts'][name]['file']))
        return native[name]
    parts={}
    for letter,side in (('a',1),('b',-1)):
        cap,grips=cap_candidate(side)
        parts[f'cap-{letter}']=cap
        parts.update(grips)
        xy=VENT_XY[letter]
        tube=cylinder(xy,LID_BOTTOM-1.,cap_face_z+AIR_PRIDE,AIR_OD)
        tube=tube.cut(cylinder(xy,LID_BOTTOM-1.1,cap_face_z+AIR_PRIDE+.1,AIR_ID))
        parts[f'air-{letter}']=tube

    cup=load('cold-core/foam-cap-top')
    lid=load('cold-core/foam-cap-lid-top')
    cup_bottom=cup.BoundingBox().zmin
    lid_bottom=interface.foam_shell_outer_height+top_cap_height
    for xy in VENT_XY.values():
        column=cylinder(xy,cup_bottom,lid_bottom-interface.cap_lid_clearance,
                        PASSAGE_D+2.*PASSAGE_WALL)
        bore=cylinder(xy,cup_bottom-.1,cap_face_z+.1,PASSAGE_D)
        cup=cup.fuse(column).cut(bore).clean()
        lid=lid.cut(bore).clean()
    parts['outer-cup']=cup
    parts['outer-lid']=lid

    # Keep the native liquid routes. A-fill gets enough tail to cross its new grip.
    for letter,name in (('a','reservoir-a'),('b','reservoir-b'),('a-fill','reservoir-a-fill')):
        points=[list(p) for p in routes.routes[name]]
        if letter=='a-fill':points[0][2]=LID_BOTTOM-1.
        outer=routes.build_route(points,radius=interface.lldpe_tube_od/2.)
        inner=routes.build_route(points,radius=4.24/2.)
        parts[f'liquid-{letter}']=outer.cut(inner)
    parts['b-fill-lower']=load('cold-core/reservoir-b-fill-lower')
    parts['b-fill-upper']=load('cold-core/reservoir-b-fill-upper')
    parts['b-fill-link']=load('cold-core/line-reservoir-b-fill')

    ignore={'cold-core/foam-cap-top','cold-core/foam-cap-lid-top','cold-core/foam-shell',
            'cold-core/reservoir-a-cap','cold-core/reservoir-b-cap',
            'cold-core/vent-membrane-a','cold-core/vent-membrane-b',
            'cold-core/line-reservoir-a-fill'}
    report={'status':'Review candidate, not production geometry or a physical fit result.',
        'baseline_assembly':{'path':native_index['source'],'sha256':native_index['sha256']},
        'dimensions_mm':{'cap_plate_thickness':LID_TOP-LID_BOTTOM,'cap_top_z':LID_TOP,
          'cap_bottom_z':LID_BOTTOM,'existing_top_gap':cup_bottom-LID_TOP,
          'fluid_grommet':FLUID_GRIP,'air_grommet':AIR_GRIP,
          'vent_axes':VENT_XY,'air_tube_od':AIR_OD,'air_tube_id':AIR_ID,
          'air_tube_top_z':cap_face_z+AIR_PRIDE,'air_tube_above_outer_cap':AIR_PRIDE,
          'air_tube_tip_to_baffle_floor':1.,'passage_d':PASSAGE_D,
          'passage_wall':PASSAGE_WALL,'passage_radial_tube_clearance':(PASSAGE_D-AIR_OD)/2.},
        'checks':{},
        'limits':['Nominal CAD only; TPU insertion, sliding grip and printed fits need a trial.',
          'Tube/grommet interference is intentional: nominal diametral 0.15mm for 1/4-inch tube; 0.10mm for air tube.',
          'No filter, check valve, separate sleeve, clamp or fastener is proposed.',
          'Air stubs end above the insulation inside the appliance, not outside the appliance enclosure.',
          'Existing rigid B-fill elbow stem is retained; A-fill tail is extended through the shortened seat.']}
    for letter in ('a','b'):
        shape=parts[f'air-{letter}']
        distances=[]
        # Every placed assembly row whose bounds could be within 8mm is checked.
        for name,row in native_index['parts'].items():
            if name in ignore:continue
            bb=row['bounds'];sb=bb_row(shape)
            if any(sb[i]>bb[i+3]+8 or bb[i]>sb[i+3]+8 for i in range(3)):continue
            obstacle=load(name)
            distances.append([round(shape.distance(obstacle),6),name])
        report['checks'][f'air-{letter}-nearest-existing-objects']=sorted(distances)[:8]
        report['checks'][f'air-{letter}-proposed-cup-clearance']=shape.distance(cup)
        report['checks'][f'air-{letter}-proposed-lid-clearance']=shape.distance(lid)
        report['checks'][f'cap-{letter}-solid-count']=len(parts[f'cap-{letter}'].Solids())
        report['checks'][f'cap-{letter}-valid']=parts[f'cap-{letter}'].isValid()
        g=parts[f'grip-{letter}-draw']
        report['checks'][f'grip-{letter}-flush-z']=bb_row(g)[2::3]
        report['checks'][f'grip-{letter}-petg-intersection-mm3']=g.intersect(parts[f'cap-{letter}']).Volume()

    report['checks']['cup-solid-count']=len(cup.Solids())
    report['checks']['cup-valid']=cup.isValid()
    report['checks']['lid-valid']=lid.isValid()
    for letter in ('a','b'):
        report['checks'][f'cap-{letter}-body-intersection-mm3']=parts[f'cap-{letter}'].intersect(
            load(f'cold-core/reservoir-{letter}')).Volume()
        report['checks'][f'cap-{letter}-gasket-intersection-mm3']=parts[f'cap-{letter}'].intersect(
            load(f'cold-core/reservoir-{letter}-gasket')).Volume()
    report['checks']['B-fill-elbow-to-PETG-intersection-mm3']=parts['b-fill-lower'].intersect(parts['cap-b']).Volume()
    report['checks']['B-fill-elbow-to-TPU-nominal-interference-mm3']=parts['b-fill-lower'].intersect(parts['grip-b-fill']).Volume()
    # The float's full travel envelope ends at the unchanged register boss.
    # At its upper stop it remains below every newly added baffle or tube seat.
    import _float_interface as float_interface
    float_top=reservoir.float_magnet_travel_z[1]+float_interface.height-float_interface.magnet_midplane
    report['checks']['float-upper-stop-top-z-mm']=float_top
    report['checks']['new-baffle-below-lid-bottom-z-mm']=LID_BOTTOM-3.
    report['checks']['baffle-vertical-clearance-above-float-top-mm']=LID_BOTTOM-3.-float_top
    # Existing body seating, gasket and screws keep their native datums.
    for letter in ('a','b'):
        for suffix in ('','-gasket'):
            name=f'cold-core/reservoir-{letter}{suffix}'
            parts[name.removeprefix('cold-core/')]=load(name)
        for role in ('g-ganen-pump','pcba','valve-v-b'):
            parts[role]=load('cold-core/'+role)
    parts['foam-shell']=load('cold-core/foam-shell')
    for key in ('cold-core/float-rod-a','cold-core/float-rod-b'):
        parts[key.removeprefix('cold-core/')]=load(key)
    # Native obstacles nearest the vent stubs remain visible in the overview.
    for name in ('tube-above-core-va-fore-feed','wire-PE-bus','wire-PE-carbonator'):
        parts[name]=load(name)
    for name,shape in parts.items():
        shape.exportBrep(str(out/(name+'.brep')))
    report['baseline_part_sha256']={str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest()
        for p in (CORE/'reservoir/reservoir-cap-right.step',CORE/'reservoir/reservoir-cap-left.step',
                  CORE/'foam-cap/foam-cap-top.step',CORE/'foam-cap/foam-cap-lid-top.step')}
    (out/'fit-review.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report['checks'],indent=2),flush=True)
    return parts,report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--native-cache',required=True,type=Path)
    args=parser.parse_args()
    build(args.output,args.native_cache)
