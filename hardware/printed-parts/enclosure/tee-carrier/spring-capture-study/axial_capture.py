"""One-piece axial spring capture: closed moving bore and recessed bayonet guide/seat.

Study only. Inputs are a hash-frozen, internally matched native assembly. The
3 mm guide example remains unqualified until the delivered spring ID is measured.
No production source is imported, altered, or regenerated here.
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
BASELINE = json.loads((INPUTS / 'carrier-interface-baseline.json').read_text())
I = BASELINE['interface']
SPRING = json.loads((INPUTS / 'spring-measurements.json').read_text())
X = I['spring_stations'][1]['x']
Z = I['spring_stations'][1]['z']
FLOOR = I['spring_stations'][1]['seat_floor_y']
MOVING_FLOOR = I['spring_stations'][1]['bore_floor_y']
MOUTH = I['spring_bore_mouth_y']
FIXED_MOUTH = I['fixed_seat_mouth_y']
INBOARD = BASELINE['spec']['grip_back_x']
R = I['spring_bore_d'] / 2
FORE = 79.519
FACE_FORE = FORE + .25
FACE_BACK = FACE_FORE + 1.3
WALL_BACK = FACE_FORE + 2.4
PRESS = .25
GUIDE_PROJECTION = 19.0
GUIDE_TIP = FLOOR + GUIDE_PROJECTION
BODY_D = 7.2
FEED_D = BODY_D + .30
LUG_FORE = FLOOR - 2.1
LUG_BACK = FLOOR - .1
POCKET_BACK = LUG_BACK + PRESS + .15
HEAD_BACK = WALL_BACK + PRESS + .15
WALL_R0, WALL_R1 = 6.15, 7.45
WALL_A0, WALL_A1 = 20.0, 150.0
LIP_R = 8.25
RELEASE = 1.10
PRELOAD = .20
TOL = 1e-5
STATES = {'release':BASELINE['spec']['release_offset_y'],
          'connected':BASELINE['spec']['connected_offset_y'],
          'aft_limit':BASELINE['spec']['park_offset_y']+BASELINE['spec']['aft_overtravel_y']}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def box(xs, ys, zs):
    return cq.Solid.makeBox(xs[1]-xs[0],ys[1]-ys[0],zs[1]-zs[0],
                            cq.Vector(xs[0],ys[0],zs[0]))


def union(*parts):
    return parts[0].fuse(*parts[1:]).clean()


def ycyl(d, y0, y1):
    return cq.Solid.makeCylinder(d/2,y1-y0,cq.Vector(0,y0,0),cq.Vector(0,1,0))


def along_y(points, y0, y1):
    plane=cq.Plane(origin=(0,y0,0),xDir=(1,0,0),normal=(0,-1,0))
    return cq.Workplane(plane).polyline(points).close().extrude(y0-y1).val()


def polar(r, angle):
    a=math.radians(angle)
    return r*math.cos(a),r*math.sin(a)


def turn(shape, angle):
    return shape.rotate((0,0,0),(0,-1,0),angle)


def place(shape, side=1):
    # The wall receivers and guide/seat plugs have identical handedness.
    return shape.translate((side*X,0,Z))


def carrier_place(shape, side=1):
    # Only the carrier's inboard window needs a mirrored closure.
    result=shape.translate((X,0,Z))
    return result if side>0 else result.mirror('YZ')


def sector(r0, r1, a0, a1, y0, y1):
    """Analytic circular sector; outer and inner arcs are native circle edges."""
    plane=cq.Plane(origin=(0,y0,0),xDir=(1,0,0),normal=(0,-1,0))
    mid=(a0+a1)/2
    body=(cq.Workplane(plane).moveTo(0,0).lineTo(*polar(r1,a0))
          .threePointArc(polar(r1,mid),polar(r1,a1)).close().extrude(y0-y1).val())
    return body.cut(ycyl(2*r0,y0-.1,y1+.1)).clean() if r0 else body


def guide_passage(y0, y1):
    t=R/math.sqrt(2)
    return union(ycyl(2*R,y0,y1),along_y(((-t,t),(0,R*math.sqrt(2)),(t,t)),y0,y1))


def window_fill():
    # Close only the existing window inside the unchanged pull-bar boundary.
    u=INBOARD-X
    fill=along_y(((u,-R),(0,-R),(0,R),(u,R-u)),MOUTH,MOUTH+10.0)
    return fill.cut(guide_passage(MOUTH-.1,MOVING_FLOOR+.1)).clean()


def lug_shape(y0=LUG_FORE, y1=LUG_BACK):
    strip=box((-5.8,5.8),(y0,y1),(-2.0,2.0))
    return strip.intersect(ycyl(11.6,y0-.1,y1+.1)).clean()


def wall_shape(offset=0.0):
    """A broad curved wall, preformed or squeezed radially about its fixed root.

    The radial displacement grows along the wall. This is a geometric motion
    envelope, not a material solution or a force/fatigue claim.
    """
    def point(r,a):
        return polar(r+offset*(a-WALL_A0)/(WALL_A1-WALL_A0),a)
    angles=[WALL_A0+2*i for i in range(66)]
    outer=[point(WALL_R1,a) for a in angles]
    inner=[point(WALL_R0,a) for a in reversed(angles)]
    wall=along_y(outer+inner,FACE_FORE,WALL_BACK)
    lip_points=[point(7.30,130),point(LIP_R,130),point(LIP_R,140),
                point(WALL_R1,150),point(7.30,150)]
    lip=along_y(lip_points,FACE_FORE,WALL_BACK)
    # The aft lead-in cams the broad wall inward during fore insertion. The
    # anti-rotation faces remain radial planes; the bayonet bearings stay flat.
    cam_start=WALL_BACK-.8
    cone=cq.Solid.makeCone(LIP_R+offset,WALL_R1+offset,.8,
                           cq.Vector(0,cam_start,0),cq.Vector(0,1,0))
    cam_limit=union(ycyl(20,FACE_FORE-.1,cam_start),cone)
    return union(wall,lip.intersect(cam_limit))


def plug(guide_d, wall_offset=0.0, include_walls=True):
    body=union(ycyl(BODY_D,FACE_FORE,FLOOR),
               ycyl(guide_d,FLOOR-.1,GUIDE_TIP),
               ycyl(8.4,FACE_FORE,FACE_BACK),lug_shape())
    body=body.cut(box((-2.3,2.3),(FACE_FORE-.1,FACE_FORE+1.0),(-.7,.7)))
    # Broad roots tie the compliant walls to the face plate. They do not
    # transmit the spring reaction; the body and square bayonet lugs do that.
    root=sector(3.4,WALL_R1,19.5,35.0,FACE_FORE,FACE_BACK)
    if not include_walls:
        return union(body,root,turn(root,180))
    wall=wall_shape(wall_offset)
    return union(body,root,turn(root,180),wall,turn(wall,180))


def receiver_cuts():
    # The plug's seat face must pass its loaded station by PRESS while turning.
    # This shallow relief leaves the aft 1.6 mm of the existing 2 mm seat bore.
    cuts=[ycyl(FEED_D,FORE-.1,FLOOR+PRESS+.15),
          ycyl(15.2,FORE-.1,FACE_BACK+PRESS+.15),
          ycyl(15.2,FORE-.1,HEAD_BACK).cut(ycyl(9.6,FORE-.2,HEAD_BACK+.1)),
          # The straight entry slots take the lugs at -90 degrees.
          box((-2.15,2.15),(FORE-.1,POCKET_BACK),(-5.95,5.95))]
    for angle in (0,180):
        cuts.append(turn(sector(FEED_D/2-.05,5.95,-125.5,35.5,LUG_FORE,POCKET_BACK),angle))
        # The two pockets catch the full broad-wall lip on square angular faces.
        cuts.append(turn(sector(7.35,LIP_R,128.5,151.5,FORE-.1,HEAD_BACK),angle))
    return tuple(cuts)


def build_and_check(guide_d):
    if not 0 < guide_d < SPRING['outside_diameter_mm']-.5:
        raise ValueError('guide is an unqualified parameter and must fit within the OD envelope')
    manifest=json.loads((HERE/'input-manifest.json').read_text())
    for row in manifest.values():
        assert sha(HERE/row['frozen_path'])==row['source_sha256'],row['frozen_path']
    native={name:cq.importers.importStep(str(INPUTS/f'{name}.step')).val()
            for name in ('front_top','cartridge','cap','left','right')}
    moving={side:union(native['right' if side>0 else 'left'],carrier_place(window_fill(),side))
            for side in (-1,1)}
    cuts=[place(c,side) for side in (-1,1) for c in receiver_cuts()]
    fixed=native['front_top'].cut(*cuts).clean()
    seated=plug(guide_d)
    relaxed=plug(guide_d,PRELOAD)
    squeezed=plug(guide_d,-RELEASE)
    rigid_plug=plug(guide_d,include_walls=False)
    rows,failures=[],[]

    def clear(label,a,b):
        volume=a.intersect(b).Volume()
        rows.append({'check':label,'overlap_mm3':volume})
        if volume>TOL: failures.append(f'{label}: overlap {volume:.6f} mm³')

    def caught(label,a,b):
        volume=a.intersect(b).Volume()
        rows.append({'check':label,'engaged_mm3':volume})
        if volume<=TOL: failures.append(f'{label}: no positive engagement')

    def stock(label,probe,body):
        missing=probe.cut(body).Volume()
        rows.append({'check':label,'missing_stock_mm3':missing,'probe_mm3':probe.Volume()})
        if missing>TOL: failures.append(f'{label}: missing {missing:.6f} mm³')

    for name,body in [('fixed receiver',fixed),('seated plug',seated),
                      ('relaxed printable plug',relaxed),('squeezed envelope',squeezed)]+[
                          (f'moving {side}',shape) for side,shape in moving.items()]:
        valid=body.isValid() and len(body.Solids())==1
        rows.append({'check':name+' one valid solid','pass':valid})
        if not valid: failures.append(name+' is not one valid solid')

    # An exact planar seating annulus remains at the published spring-floor station.
    bearing_faces=[f for f in seated.Faces() if f.geomType()=='PLANE'
                   and abs(f.Center().y-FLOOR)<1e-7 and f.normalAt().y>.99]
    bearing_area=sum(f.Area() for f in bearing_faces)
    expected=math.pi*(BODY_D**2-guide_d**2)/4
    rows.append({'check':'guide-seat reaction face','y_mm':FLOOR,
                 'area_mm2':bearing_area,'expected_annulus_mm2':expected})
    if abs(bearing_area-expected)>1e-5: failures.append('guide-seat reaction face is not the full annulus')

    state_rows=[]
    for side in (-1,1):
        part=place(seated,side)
        clear(f'{side} seated plug versus fixed receiver',part,fixed)
        clear(f'{side} plug versus cartridge',part,native['cartridge'])
        clear(f'{side} plug versus pump cap',part,native['cap'])
        rows.append({'check':f'{side} cartridge air','clearance_mm':part.distance(native['cartridge'])})
        caught(f'{side} axial spring reaction on rigid lugs',part.translate((0,-.02,0)),fixed)
        caught(f'{side} rigid lug retention with detent walls absent',
               place(rigid_plug.translate((0,-.02,0)),side),fixed)
        caught(f'{side} detent blocks reverse rotation',place(turn(seated,-3),side),fixed)
        clear(f'{side} reverse rotation with detent walls absent',place(turn(rigid_plug,-3),side),fixed)
        caught(f'{side} bayonet stop blocks excess rotation',place(turn(seated,5),side),fixed)
        caught(f'{side} free wall preload',place(relaxed,side),fixed)
        # Probe actual wall stock immediately fore of the complete load-bearing footprint.
        footprint=lug_shape(LUG_FORE-1.25,LUG_FORE-.001).cut(
            ycyl(FEED_D+.02,LUG_FORE-1.3,LUG_FORE+.1))
        stock(f'{side} continuous 1.25 mm stock under lug bearing',place(footprint,side),fixed)
        load_area=footprint.Volume()/1.249
        rows.append({'check':f'{side} rigid bayonet bearing area','area_mm2':load_area})
        stock(f'{side} closed-window inboard wall',
              carrier_place(box((INBOARD-X,INBOARD-X+1.0),(MOUTH+.01,MOUTH+9.99),(-3,3)),side),moving[side])
        removed=native['right' if side>0 else 'left'].cut(moving[side]).Volume()
        rows.append({'check':f'{side} carrier material removed','volume_mm3':removed})
        if removed>TOL: failures.append(f'{side} closing the window removed native carrier material')
        for j in range(13):
            dy=STATES['aft_limit']*j/12
            carrier=moving[side].translate((0,dy,0))
            clear(f'{side} guide versus moving bore {j}/12',part,carrier)
            clear(f'{side} added closure versus fixed wall {j}/12',carrier_place(window_fill(),side).translate((0,dy,0)),fixed)
            outer=place(ycyl(SPRING['outside_diameter_mm'],FLOOR,MOVING_FLOOR+dy),side)
            clear(f'{side} spring OD versus moving bore {j}/12',outer,carrier)
            clear(f'{side} spring OD versus fixed seat {j}/12',outer,fixed)
        # Empty pump bay: a full-length spring enters along the axis, with no
        # lateral loading window or short compressed loading pose.
        spring_feed=place(ycyl(SPRING['outside_diameter_mm'],-10,MOVING_FLOOR),side)
        clear(f'{side} axial spring feed versus wall',spring_feed,fixed)
        clear(f'{side} axial spring feed versus moving bore',spring_feed,moving[side])
        clear(f'{side} axial spring feed versus pump cap',spring_feed,native['cap'])
        start=-(SPRING['free_length_mm']-(MOVING_FLOOR-FLOOR))
        # The broad walls are shown squeezed through insertion/rotation. The
        # lead-in supplies that displacement; its actual effort is a print trial.
        entry=turn(squeezed,-90)
        for j in range(13):
            dy=start+(PRESS-start)*j/12
            placed=place(entry.translate((0,dy,0)),side)
            clear(f'{side} axial guide/seat insertion {j}/12',placed,fixed)
            clear(f'{side} insertion guide versus moving bore {j}/12',placed,moving[side])
        for j in range(19):
            angle=-90+90*j/18
            rotated=place(turn(squeezed,angle).translate((0,PRESS,0)),side)
            clear(f'{side} quarter-turn {j}/18',rotated,fixed)
        clear(f'{side} detent release at operating seat',place(squeezed,side),fixed)
        clear(f'{side} detent rebound at pressed seat',place(seated.translate((0,PRESS,0)),side),fixed)
        # Complete cartridge movement in its native vertical direction preserves
        # the Y separation; test the full rectangular swept envelope as well.
        b=native['cartridge'].BoundingBox()
        cartridge_sweep=box((b.xmin,b.xmax),(b.ymin,b.ymax),(b.zmin,b.zmax+100))
        clear(f'{side} 100 mm vertical cartridge swept envelope',part,cartridge_sweep)
        tool=place(box((-9,9),(-10,FORE-.001),(-14,14)),side)
        clear(f'{side} fore tool corridor',tool,native['front_top'])
        clear(f'{side} fore tool corridor versus cap',tool,native['cap'])

    for name,dy in STATES.items():
        span=MOVING_FLOOR+dy-FLOOR
        state_rows.append({'state':name,'bearing_separation_mm':span,
                           'compression_from_free_mm':SPRING['free_length_mm']-span,
                           'guide_tip_to_floor_mm':MOVING_FLOOR+dy-GUIDE_TIP,
                           'guide_engagement_mm':GUIDE_TIP-MOUTH-dy})

    # The blind moving bore has one open fore support lane before installation.
    bore_support=guide_passage(MOUTH-.01,MOVING_FLOOR-.01)
    for j in range(7):
        clear(f'moving bore support fore withdrawal {j}/6',
              place(bore_support.translate((0,-12*j/6,0))),moving[1])
    # Bayonet pocket support must be split into small sectors. Each one can move
    # straight inward into the feed bore and then straight fore. These checks do
    # not claim an unbroken support body will peel out, or that its effort is known.
    for index,center in enumerate(range(-115,216,15)):
        # Leave the rigid circumferential end-stop wedges in the native wall.
        low,high=center-4,center+4
        if not ((low>=-125.5 and high<=35.5) or (low>=54.5 and high<=215.5)):
            continue
        chip=sector(FEED_D/2+.01,5.94,low,high,LUG_FORE+.01,POCKET_BACK-.01)
        ux,uz=polar(1,center)
        for j in range(5):
            shifted=chip.translate((-ux*4.8*j/4,0,-uz*4.8*j/4))
            clear(f'pocket support {index} inward {j}/4',place(shifted),fixed)
        for j in range(4):
            shifted=chip.translate((-ux*4.8,-8*j/3,-uz*4.8))
            clear(f'pocket support {index} fore exit {j}/3',place(shifted),fixed)

    report={
        'status':'pass' if not failures else 'fail','failures':failures,
        'scope':'Archived, matched native-interface study only. Production measured-tee integration, '
                'spring ID, material retention, physical support removal and production slice remain unqualified.',
        'preferred_variant':'Closed moving bore with one recessed guide/seat plug per spring',
        'added_loose_capture_parts_per_spring':1,
        'guide_seat_plug_unique_part_count':1,
        'fixture_status':'archived published baseline; do not combine with the revised tee carrier alone',
        'expected_production_interface_delta_mm':{'floor_y':1.392,'spring_z':1.109},
        'spring_sample':SPRING,'spring_rate_n_per_mm':None,'spring_force_n':None,
        'guide_diameter_mm':guide_d,'guide_diameter_qualified':False,
        'example_minimum_spring_id_with_0_25_mm_radial_air':guide_d+.50,
        'guide_projection_from_spring_floor_mm':GUIDE_PROJECTION,
        'feed_bore_diameter_mm':FEED_D,'plug_seat_diameter_mm':BODY_D,
        'head_fore_recess_mm':FACE_FORE-FORE,'release_press_mm':PRESS,
        'installation_spring_minimum_length_mm':MOVING_FLOOR-FLOOR-PRESS,
        'installation_tip_clearance_mm':MOVING_FLOOR-GUIDE_TIP-PRESS,
        'fixed_reaction_floor_y_mm':FLOOR,'moving_reaction_floor_y_mm':MOVING_FLOOR,
        'bayonet_lug_thickness_mm':LUG_BACK-LUG_FORE,
        'head_pocket_to_lug_bearing_minimum_stock_mm':LUG_FORE-HEAD_BACK,
        'bayonet_pocket_to_fixed_seat_mouth_stock_mm':FIXED_MOUTH-POCKET_BACK,
        'full_diameter_feed_relief_behind_floor_mm':PRESS+.15,
        'remaining_original_fixed_bore_length_mm':FIXED_MOUTH-FLOOR-PRESS-.15,
        'detent_wall':{'radial_stock_mm':WALL_R1-WALL_R0,
                       'axial_width_mm':WALL_BACK-FACE_FORE,
                       'arc_length_at_middle_mm':math.radians(WALL_A1-WALL_A0)*(WALL_R0+WALL_R1)/2,
                       'tip_relaxed_preload_mm':PRELOAD,'tip_release_displacement_mm':RELEASE,
                       'lip_projection_mm':LIP_R-WALL_R1,
                       'positive_rotation_engagement_mm':LIP_R-7.60,
                       'force_n':None,'physical_qualification':False},
        'states':state_rows,'readings':rows,
        'sources':{'axial_capture.py':sha(__file__),
                   'input-manifest.json':sha(HERE/'input-manifest.json')},
    }
    for row in manifest.values():
        assert sha(HERE/row['frozen_path'])==row['source_sha256'],row['frozen_path']
    return report,{'fixed':fixed,'moving_right':moving[1],'moving_left':moving[-1],
                   'plug':place(seated),'plug_relaxed':place(relaxed),'native':native}


def export(parts):
    fixed=parts['fixed'].intersect(box((X-9.5,X+9.5),(FORE,FIXED_MOUTH),(Z-14,Z+14)))
    moving=parts['moving_right'].intersect(box((INBOARD,X+6.5),(MOUTH,MOUTH+16),(Z-7,Z+11)))
    named={'axial-fixed-seat-coupon':fixed,'axial-closed-moving-seat-coupon':moving,
           'axial-guide-seat-plug-unqualified-example':parts['plug_relaxed'],
           'axial-guide-seat-plug-seated-reference':parts['plug']}
    for name,body in named.items():
        cq.exporters.export(body,str(HERE/f'{name}.step'))
        # No guide STL is released before the actual ID supplies its diameter.
        if 'plug' not in name:
            cq.exporters.export(body,str(HERE/f'{name}.stl'),tolerance=.03,angularTolerance=.1)
    assembly=cq.Assembly(name='axial-spring-capture-study')
    assembly.add(fixed,name='fixed-wall-coupon',color=cq.Color(.46,.50,.56))
    assembly.add(moving,name='closed-moving-bore-coupon',color=cq.Color(.52,.57,.65))
    assembly.add(parts['plug'],name='seated-unqualified-guide-seat',color=cq.Color(.90,.65,.20))
    assembly.export(str(HERE/'axial-spring-capture-study.step'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--guide-diameter',type=float,default=3.0,
                        help='Unqualified shaft example; not a measured spring ID')
    parser.add_argument('--export',action='store_true')
    args=parser.parse_args()
    report,parts=build_and_check(args.guide_diameter)
    if args.export: export(parts)
    (HERE/'axial-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(f"Axial capture: {report['status']}; {len(report['readings'])} readings")
    for failure in report['failures']: print('FAIL:',failure)
    return bool(report['failures'])


if __name__=='__main__':
    raise SystemExit(main())
