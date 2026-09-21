"""Positive spring-capture prototype using frozen, published appliance interfaces.

No production source is imported or changed. The guide diameter is an explicit
unqualified parameter; the example 3 mm shaft is not a measured spring ID.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

import cadquery as cq

HERE = Path(__file__).resolve().parent
INPUTS = HERE / 'inputs'
FROZEN = json.loads((INPUTS / 'carrier-interface-baseline.json').read_text())
INTERFACE = FROZEN['interface']
STATION = INTERFACE['spring_stations'][1]
X, Z = STATION['x'], STATION['z']
MOUTH = INTERFACE['spring_bore_mouth_y']
FLOOR = STATION['seat_floor_y']
MOVING_FLOOR = STATION['bore_floor_y']
FORE = 79.519
R = INTERFACE['spring_bore_d'] / 2
INBOARD = FROZEN['spec']['grip_back_x']
U_AXIS = X - INBOARD
STATES = {'release': 0.0, 'connected': 2.15, 'aft_limit': 4.65}
SAMPLE_OD = 6.0
SAMPLE_FREE = 27.0
SAMPLE_COMPRESSED_UPPER = 7.0
GUIDE_PROJECTION = 19.0
GUIDE_TIP = FLOOR + GUIDE_PROJECTION
AIR = .15
SUPPORTED_AIR = .40
COVER_WITHDRAWAL = 9.0
LOADING_LENGTH = 8.5
PLATE_FORE = FORE + .25
PLATE_BACK = PLATE_FORE + 1.3
HEAD_FORE = PLATE_BACK + .20
HEAD_BACK = HEAD_FORE + 2.0
HEAD_D = 6.0
HEAD_WALL_BACK = PLATE_FORE + 4.0
HEAD_LIP_FORE = PLATE_FORE + 1.8
HEAD_LIP_AFT = PLATE_FORE + 3.5
HEAD_ROOT_Z = 10.0
HEAD_LIP_TOP_Z = -5.0
HEAD_RELEASE = 1.20
HEAD_PRELOAD = .20
COVER_RELEASE = .80
VOL_TOL = 1e-5


def box(xs, ys, zs):
    return cq.Solid.makeBox(xs[1]-xs[0], ys[1]-ys[0], zs[1]-zs[0],
                            cq.Vector(xs[0], ys[0], zs[0]))


def union(*bodies):
    return bodies[0].fuse(*bodies[1:]).clean()


def ycyl(diameter, y0, y1, x=0.0, z=0.0):
    return cq.Solid.makeCylinder(diameter/2, y1-y0,
                                cq.Vector(x,y0,z), cq.Vector(0,1,0))


def along_y(points, start, end):
    plane=cq.Plane(origin=(0,start,0),xDir=(1,0,0),normal=(0,-1,0))
    return cq.Workplane(plane).polyline(points).close().extrude(start-end).val()


def at_carrier(shape, offset=0.0):
    return shape.translate((INBOARD,MOUTH+offset,Z))


def at_wall(shape):
    return shape.translate((X,0,Z))


def guide_passage(y0, y1):
    tangent=R/math.sqrt(2)
    return union(ycyl(2*R,y0,y1,U_AXIS),
                 along_y(((U_AXIS-tangent,tangent),(U_AXIS,R*math.sqrt(2)),
                          (U_AXIS+tangent,tangent)),y0,y1))


def cover_parts():
    """Rigid keys carry X/Z load; an 8 mm broad wall only locks -Y removal.

    The flexible wall has 1.3 mm stock and a full-width retaining lip. Its
    13 mm length, broad root and lip follow the continuous-wall construction
    of the physically accepted faucet display cover. Its force still needs
    a representative print trial; a beam equation is not that qualification.
    """
    core=along_y(((.15,-R+.15),(U_AXIS,-R+.15),(U_AXIS,R-.15),
                  (.15,R+U_AXIS-.30)),.15,9.85).cut(guide_passage(0,10))
    keys=union(
        box((1.5,4.4),(.15,14.5),(-6.0,-4.8)),
        box((2.2,3.2),(.15,9.85),(-5.0,-3.0)),
        box((1.5,4.4),(.15,9.85),(11.0,12.2)),
        box((2.2,3.2),(.15,9.85),(6.2,11.2)))
    root=box((1.8,4.1),(13.5,14.5),(-14.2,-5.8))
    rigid=union(core,keys,root)
    wall=box((1.8,3.1),(.5,14.0),(-14.2,-6.2))
    lip=(cq.Workplane('XY').workplane(offset=-14.2)
         .polyline(((1.8,1.2),(3.1,1.2),(3.1,3.3),(1.8,3.3),
                    (1.0,2.2),(1.0,1.2)))
         .close().extrude(8.0).val())
    return rigid,union(wall,lip)


def cover():
    return union(*cover_parts())


def cover_released():
    """Geometric release envelope with the broad aft root held stationary."""
    rigid,wall=cover_parts()
    slope=-COVER_RELEASE/(13.5-3.3)
    transform=cq.Matrix([[1,slope,0,-slope*13.5],[0,1,0,0],
                         [0,0,1,0],[0,0,0,1]])
    return union(rigid,wall.transformGeometry(transform))


def cover_receiver_cuts():
    # Both keyways are open to the fore face. Their constant cross-sections
    # give their support a straight fore extraction lane before assembly.
    return (
        box((1.35,4.55),(-.1,14.65),(-6.15,-4.40)),
        box((2.05,3.35),(-.1,10.0),(-5.0,-2.85)),
        box((1.35,4.55),(-.1,10.0),(10.85,12.60)),
        box((2.05,3.35),(-.1,10.0),(6.05,11.4)),
        box((1.65,4.30),(-.1,14.65),(-14.35,-5.80)),
        # The aft root reaches into the lower key. The channel remains open fore.
        box((1.65,4.30),(-.1,14.65),(-6.35,-5.40)),
        # This square latch pocket opens directly inboard for release and support removal.
        box((-1.0,1.65),(1.0,3.45),(-14.35,-5.80)),
    )


def head_retainer_parts():
    """Seated fit reference: broad sidewalls join a rigid guide-head plate.

    Each sidewall is 22 x 4 x 1.3 mm; the broad lip is 5.5 mm tall with
    1.2 mm radial projection. These are walls, not isolated narrow catches.
    The relaxed printable walls spread .20 mm at the upper lip edge so
    the seated groove roots retain wall preload. Force is unqualified.
    """
    rigid=union(ycyl(6.6,PLATE_FORE,PLATE_BACK),
                box((-3.3,3.3),(PLATE_FORE,PLATE_BACK),(1.0,11.5)),
                box((-5.55,5.55),(PLATE_FORE,PLATE_BACK),(10.0,12.0)))
    # A pick can hook through this hole where the wall has an open fore relief.
    rigid=rigid.cut(box((-1,1),(PLATE_FORE-.1,PLATE_BACK+.1),(4.0,5.2)))
    walls=[]
    for sign in (-1,1):
        wall=box((4.25,5.55),(PLATE_FORE,HEAD_WALL_BACK),(-11.0,11.0))
        lip=(cq.Workplane('XY').workplane(offset=-10.5)
             .polyline(((4.25,HEAD_LIP_FORE),(6.75,HEAD_LIP_FORE),
                        (6.75,HEAD_LIP_AFT),(5.55,HEAD_WALL_BACK),
                        (4.25,HEAD_WALL_BACK)))
             .close().extrude(5.5).val())
        side=union(wall,lip)
        walls.append(side if sign>0 else side.mirror('YZ'))
    return rigid,walls


def head_retainer(wall_offset=0.0):
    """Positive offset preforms walls outwards; negative models inward release.

    The affine shape is a geometric motion envelope, not an elastic solution.
    The same broad-wall preload construction appears in faucet_display_cover.py.
    """
    rigid,walls=head_retainer_parts()
    shifted=[]
    for sign,wall in zip((-1,1),walls):
        slope=-sign*wall_offset/(HEAD_ROOT_Z-HEAD_LIP_TOP_Z)
        transform=cq.Matrix([[1,0,slope,-slope*HEAD_ROOT_Z],
                             [0,1,0,0],[0,0,1,0],[0,0,0,1]])
        shifted.append(wall.transformGeometry(transform))
    return union(rigid,*shifted)


def fixed_receiver_cuts(guide_d):
    cuts=[
        ycyl(guide_d+2*AIR,HEAD_BACK-.1,FLOOR+.1),
        ycyl(HEAD_D+2*.25,FORE-.1,HEAD_BACK),
        ycyl(6.9,FORE-.1,PLATE_BACK+.15),
        box((-3.45,3.45),(FORE-.1,PLATE_BACK+.15),(.85,11.65)),
        box((-5.70,5.70),(FORE-.1,PLATE_BACK+.15),(9.85,12.40)),
        box((-1.2,1.2),(FORE-.1,PLATE_BACK+1.6),(3.85,5.45)),
    ]
    for sign in (-1,1):
        # Keyways open fore; the shallow retaining pockets connect to them.
        parts=(box((2.40,5.70),(FORE-.1,HEAD_WALL_BACK+.15),(-11.15,11.40)),
               box((5.55,6.75),(HEAD_LIP_FORE-.15,HEAD_WALL_BACK+.15),(-10.65,-4.60)),
               # Pliers can grip the guide head after removing the snap plate.
               box((2.8,4.15),(FORE-.1,HEAD_FORE+1.0),(-1.0,1.25)))
        cuts.extend(part if sign>0 else part.mirror('YZ') for part in parts)
    return tuple(cuts)


def guide(guide_d):
    return union(ycyl(HEAD_D,HEAD_FORE,HEAD_BACK),
                 ycyl(guide_d,HEAD_BACK-.1,GUIDE_TIP))


def sweep_box(shape, shift):
    b=shape.BoundingBox()
    return box((b.xmin+min(0,shift[0]),b.xmax+max(0,shift[0])),
               (b.ymin+min(0,shift[1]),b.ymax+max(0,shift[1])),
               (b.zmin+min(0,shift[2]),b.zmax+max(0,shift[2])))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def build_and_check(guide_d):
    if not 0 < guide_d < SAMPLE_OD-2*.25:
        raise ValueError('unqualified guide diameter is outside the measured OD envelope')
    manifest=json.loads((HERE/'input-manifest.json').read_text())
    for row in manifest.values():
        assert sha(HERE/row['frozen_path'])==row['source_sha256'],row['frozen_path']
    native={name:cq.importers.importStep(str(INPUTS/f'{name}.step')).val()
            for name in ('front_top','cartridge','cap','right')}
    moving=native['right'].cut(*(at_carrier(c) for c in cover_receiver_cuts())).clean()
    fixed=native['front_top'].cut(*(at_wall(c) for c in fixed_receiver_cuts(guide_d))).clean()
    clip=at_carrier(cover())
    retainer=at_wall(head_retainer())
    pin=at_wall(guide(guide_d))
    rows,failures=[],[]

    def clear(label,a,b):
        volume=a.intersect(b).Volume()
        rows.append({'check':label,'overlap_mm3':volume})
        if volume>VOL_TOL: failures.append(f'{label}: overlap {volume:.6f} mm³')

    def caught(label,a,b):
        volume=a.intersect(b).Volume()
        rows.append({'check':label,'engaged_mm3':volume})
        if volume<=VOL_TOL: failures.append(f'{label}: no positive bearing engagement')

    def stock(label,probe,body):
        missing=probe.cut(body).Volume()
        rows.append({'check':label,'missing_stock_mm3':missing,'required_stock_mm3':probe.Volume()})
        if missing>VOL_TOL: failures.append(f'{label}: missing {missing:.6f} mm³')

    for name,body in (('moving receiver',moving),('fixed receiver',fixed),
                      ('window cover',clip),('head retainer',retainer),('example guide',pin)):
        n=len(body.Solids())
        rows.append({'check':name+' validity','valid':body.isValid(),'solid_count':n})
        if not body.isValid() or n!=1: failures.append(f'{name}: not one valid solid')
    clear('closed cover in moving receiver',clip,moving)
    clear('head retainer in fixed receiver',retainer,fixed)
    clear('guide in fixed receiver',pin,fixed)
    clear('guide head against retainer',pin,retainer)
    clear('recessed retainer versus seated cartridge',retainer,native['cartridge'])
    rows.append({'check':'recessed retainer cartridge air',
                 'clearance_mm':retainer.distance(native['cartridge'])})
    # The unchanged fixed annular bearing and complete moving floor carry
    # axial spring load. The guide head and snap retainers do not replace them.
    fixed_annulus=ycyl(6.4,FLOOR-.8,FLOOR, X,Z).cut(
        ycyl(guide_d+2*AIR+.02,FLOOR-.9,FLOOR+.1,X,Z))
    stock('fixed spring reaction annulus',fixed_annulus,fixed)
    stock('moving spring reaction floor',ycyl(6.3,MOVING_FLOOR+.001,MOVING_FLOOR+.8,X,Z),moving)
    for axis,shift in (('inboard',(-.20,0,0)),('outboard',(.20,0,0)),
                       ('down',(0,0,-.20)),('up',(0,0,.45)),('aft',(0,.20,0)),
                       ('fore locked',(0,-.25,0))):
        caught('window cover '+axis+' restraint',clip.translate(shift),moving)
    caught('guide aft shoulder',pin.translate((0,.05,0)),fixed)
    caught('guide fore head capture',pin.translate((0,-.25,0)),retainer)
    caught('head retainer fore catch',retainer.translate((0,-.20,0)),fixed)
    # Snap deflection is a geometric envelope, not a fatigue/material prediction.
    deflected=cover_released()
    for step in range(19):
        pull=-COVER_WITHDRAWAL*step/18
        moved=at_carrier(deflected).translate((0,pull,0))
        clear(f'cover unlocked withdrawal {step}/18',moved,moving)
        clear(f'cover fore-gap withdrawal {step}/18',moved.translate((0,STATES['aft_limit'],0)),fixed)
    parked=at_carrier(deflected,STATES['aft_limit']).translate((0,-COVER_WITHDRAWAL,0))
    # Spring enters the remaining open window, compressed above the measured limit.
    load_y=MOUTH+STATES['aft_limit']+1.10
    spring_loaded=ycyl(SAMPLE_OD,load_y,load_y+LOADING_LENGTH,X,Z)
    clear('compressed spring versus parked cover',spring_loaded,parked)
    clear('compressed spring versus moving receiver',spring_loaded,moving.translate((0,STATES['aft_limit'],0)))
    clear('compressed spring versus fixed receiver',spring_loaded,fixed)
    # The compressed cylinder's entire outward movement from the outer well.
    spring_entry=box((88.5,X),(load_y,load_y+LOADING_LENGTH),(Z-3.0,Z+3.0))
    clear('spring near-window outward entry with parked cover',spring_entry,parked)
    clear('spring near-window outward entry versus fixed receiver',spring_entry,fixed)
    clear('spring near-window outward entry versus moving receiver',spring_entry,moving.translate((0,STATES['aft_limit'],0)))
    # Sample the full spring travel with a closed cover; the explicit guide
    # engagement includes the 0.20 mm fore play of the retained head.
    state_rows=[]
    for i in range(13):
        dy=STATES['aft_limit']*i/12
        placed=clip.translate((0,dy,0))
        for name in ('cartridge','cap'):
            clear(f'cover travel {i}/12 versus {name}',placed,native[name])
        clear(f'cover travel {i}/12 versus fixed receiver',placed,fixed)
        clear(f'guide travel {i}/12 versus cover',pin,placed)
        clear(f'guide travel {i}/12 versus receiver',pin,moving.translate((0,dy,0)))
        spring=ycyl(SAMPLE_OD,FLOOR,MOVING_FLOOR+dy,X,Z)
        clear(f'spring OD travel {i}/12 versus cover',spring,placed)
    for name,dy in STATES.items():
        separation=MOVING_FLOOR+dy-FLOOR
        state_rows.append({'state':name,'bearing_separation_mm':separation,
                           'compression_from_free_mm':SAMPLE_FREE-separation,
                           'guide_tip_to_floor_mm':MOVING_FLOOR+dy-GUIDE_TIP,
                           'guide_engagement_mm':GUIDE_TIP-MOUTH-dy,
                           'guide_engagement_with_head_fore_play_mm':GUIDE_TIP-.20-MOUTH-dy})
    # The head is introduced axially through the pump bay before the cartridge.
    pin_sweep=union(ycyl(HEAD_D,-10,HEAD_BACK,X,Z),
                    ycyl(guide_d,HEAD_BACK,GUIDE_TIP,X,Z))
    clear('guide axial installation from empty pump bay',pin_sweep,fixed)
    squeezed=head_retainer(-HEAD_RELEASE)
    for i in range(15):
        dy=-7.0*i/14
        clear(f'head retainer squeezed removal {i}/14',at_wall(squeezed).translate((0,dy,0)),fixed)
    # The input audit establishes this bay corridor with the cartridge absent.
    tool=box((X-7.5,X+7.5),(-10,FORE-.001),(Z-14,Z+14))
    clear('fore head tool corridor',tool,native['front_top'])
    clear('fore head tool corridor versus pump cap',tool,native['cap'])
    # One straight fore removal lane for every constant rail-support section.
    for index,cutter in enumerate(cover_receiver_cuts()[:4]):
        b=cutter.BoundingBox()
        probe=box((b.xmin+.01,b.xmax-.01),(-2,b.ymax-.01),(b.zmin+.01,b.zmax-.01))
        clear(f'rail support fore removal {index}',at_carrier(probe),moving)
    # Broad lip-pocket support can shift inward 1.2 mm into its open keyway, then
    # leave fore. Both moves are accessible with the head/clip absent.
    support=box((5.71,6.74),(HEAD_LIP_FORE-.14,HEAD_WALL_BACK+.14),(-10.64,-4.61))
    for sign in (-1,1):
        part=support if sign>0 else support.mirror('YZ')
        for i in range(5):
            shifted=part.translate((-sign*1.20*i/4,0,0))
            clear(f'head pocket support inward {sign} {i}/4',at_wall(shifted),fixed)
        clear(f'head pocket support fore exit {sign}',
              at_wall(sweep_box(part.translate((-sign*1.20,0,0)),
                                (0,FORE-HEAD_WALL_BACK-.1,0))),fixed)
    info={
        'status':'pass' if not failures else 'fail','failures':failures,
        'scope':'Frozen-interface prototype only; production tee integration, spring ID, '
                'material/load qualification and production-profile support slice are outstanding.',
        'guide_diameter_mm':guide_d,'guide_diameter_qualified':False,
        'required_spring_id_for_example_running_air_mm':guide_d+2*.25,
        'spring_rate_n_per_mm':None,'spring_force_n':None,
        'spring_loading_length_mm':LOADING_LENGTH,
        'loading_clearance_above_measured_compressed_estimate_mm':LOADING_LENGTH-SAMPLE_COMPRESSED_UPPER,
        'cover_staged_upper_rail_engagement_mm':9.85-COVER_WITHDRAWAL,
        'cover_staged_lower_rail_engagement_mm':14.5-COVER_WITHDRAWAL,
        'cover_front_to_fixed_seat_mouth_at_aft_limit_mm':MOUTH+STATES['aft_limit']+.15-COVER_WITHDRAWAL-INTERFACE['fixed_seat_mouth_y'],
        'head_recess_mm':PLATE_FORE-FORE,
        'fixed_floor_stock_behind_head_pocket_mm':FLOOR-HEAD_BACK,
        'head_fore_play_mm':.20,
        'cover_wall_mm':{'thickness':1.3,'width':8.0,'free_length':13.0,
                         'lip_radial_projection':.8,'positive_engagement':.65},
        'head_walls_mm':{'thickness':1.3,'depth':4.0,'length':22.0,
                         'lip_length':5.5,'lip_radial_projection':1.2,
                         'positive_engagement':1.05,'free_preload_at_lip_top':HEAD_PRELOAD},
        'retention_force_n':None,
        'flexure_status':'Broad compliant walls follow the accepted faucet-cover construction. '
                         'Seated and released shapes are geometric envelopes; force, fatigue '
                         'and insertion/removal effort require a physical print trial.',
        'fixed_floor_stock_behind_sidewall_pocket_mm':FLOOR-HEAD_WALL_BACK-.15,
        'states':state_rows,'readings':rows,
        'input_manifest_sha256':sha(HERE/'input-manifest.json'),
        'source_sha256':sha(__file__),
    }
    return info,{'moving':moving,'fixed':fixed,'cover':clip,'retainer':retainer,
                 'retainer_relaxed':at_wall(head_retainer(HEAD_PRELOAD)),'guide':pin}


def export_study(parts):
    # Crops are local interface coupons, not replacement production parts.
    moving_crop=parts['moving'].intersect(box((INBOARD,102),(MOUTH,MOUTH+16),(Z-16,Z+14)))
    fixed_crop=parts['fixed'].intersect(box((X-7.5,X+7.5),(FORE,FLOOR+2),(Z-14,Z+14)))
    named={'study-moving-seat-coupon':moving_crop,'study-fixed-seat-coupon':fixed_crop,
           'study-loading-window-cover':parts['cover'],
           'study-guide-head-retainer':parts['retainer_relaxed']}
    for name,body in named.items():
        cq.exporters.export(body,str(HERE/f'{name}.step'))
        cq.exporters.export(body,str(HERE/f'{name}.stl'),tolerance=.03,angularTolerance=.1)
    cq.exporters.export(parts['guide'],str(HERE/'unqualified-guide-example.step'))
    cq.exporters.export(parts['retainer'],str(HERE/'seated-guide-head-retainer-reference.step'))
    assembly=cq.Assembly(name='spring-capture-study')
    for name,body in (('moving-seat',moving_crop),('fixed-seat',fixed_crop),
                      ('window-cover',parts['cover']),('head-retainer',parts['retainer']),
                      ('unqualified-guide',parts['guide'])):
        assembly.add(body,name=name,color=cq.Color(.8,.65,.2) if 'retainer' in name or 'cover' in name
                     else cq.Color(.45,.5,.55))
    assembly.export(str(HERE/'spring-capture-study.step'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-diameter',type=float,default=3.0,
                        help='Unqualified analysis parameter; not a measured spring ID')
    parser.add_argument('--export',action='store_true')
    args=parser.parse_args()
    result,parts=build_and_check(args.guide_diameter)
    (HERE/'checks.json').write_text(json.dumps(result,indent=2)+'\n')
    print(f"Spring-capture study: {result['status']}; {len(result['readings'])} readings")
    for line in result['failures']: print('FAIL:',line)
    if args.export: export_study(parts)
    return bool(result['failures'])


if __name__=='__main__':
    raise SystemExit(main())
