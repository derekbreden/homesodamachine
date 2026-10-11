"""The Pour's working service cabinet, using native production interfaces."""
from __future__ import annotations
from dataclasses import replace
import json
from pathlib import Path
import sys
import cadquery as cq
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
sys.path[:0]=[str(HERE),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib')]
import enclosure_core
import enclosure_features as f
import drawer_v3
import captive_shutters as q
import ceiling_hardware_rooms
import funnel_joint_v3
import small_fronts_v3
import comparison_additions_v3

CACHE_DIR=ROOT/'.cache/the-pour-v3/cabinet'
WIDTH,DEPTH,HEIGHT=258.,216.,140.
FAUCET=(-80.,138.,146.)

def box(x0,x1,y0,y1,z0,z1):
    return cq.Solid.makeBox(x1-x0,y1-y0,z1-z0,cq.Vector(x0,y0,z0))

def union(shapes):
    result=shapes[0]
    for shape in shapes[1:]: result=result.fuse(shape)
    return result.clean()

def placed(feature,at,angle=0.):
    """Rotate only about build Z, retaining the source manufacturing direction."""
    shaped={k:{n:s.rotate((0,0,0),(0,0,1),angle).translate(at)
               for n,s in getattr(feature,k).items()}
            for k in ('add','cut','post_add','parts')}
    result=replace(feature,**shaped)
    angle_r=np.radians(angle)
    rotate_axis=lambda v:(float(np.cos(angle_r)*v[0]-np.sin(angle_r)*v[1]),
                          float(np.sin(angle_r)*v[0]+np.cos(angle_r)*v[1]),float(v[2]))
    result.source_print_up=rotate_axis(feature.source_print_up)
    result.part_print_up={n:rotate_axis(v) for n,v in feature.part_print_up.items()}
    result.layout={'translation_mm':list(at),'rotation_z_deg':angle,
                   'axes_rotated':True,
                   'source_origin_mm':list(feature.source_origin_mm)}
    return result

def base_core(use_cache=True):
    native=enclosure_core.source_module()
    b=enclosure_core.compact_box(native)
    folder=enclosure_core.CACHE_DIR
    if use_cache and all((folder/(name+'.step')).exists() for name in
                        ('front-bottom','front-top','back-bottom','back-top')):
        pieces={name:cq.importers.importStep(str(folder/(name+'.step'))).val()
                for name in ('front-bottom','front-top','back-bottom','back-top')}
    else:
        native,b,pieces=enclosure_core.build_core()
    return native,b,pieces

def build(*,use_core_cache=True):
    e,b,pieces=base_core(use_core_cache)
    original_back_top=pieces['back-top']
    features=[]
    owners={}
    moving={}
    notes=[]
    d=drawer_v3.build(pump_axis=(12.,126.))
    print('drawer integration',flush=True)
    # The actual clamp is installed with the withdrawn drawer. Its vertical
    # installation corridor is not an aperture through the working counter.
    rear=f.bounds(d.cut['native_rear_drawer_room'])
    d.cut['native_rear_drawer_room']=box(*rear[:4],5.75,rear[5])
    pieces['back-bottom']=pieces['back-bottom'].fuse(d.fixed['fixed_docking_wall'])
    for name,host in pieces.items():
        for room in d.cut.values(): host=host.cut(room)
        pieces[name]=host.clean()
    moving.update(d.parts)
    # The upper front is removed for service. The stationary lower front
    # must clear the whole cartridge and cap crown as they leave the bay.
    front_service_rooms=[]
    for name,room in d.cut.items():
        rb=f.bounds(room)
        if rb[2]<=.001 and rb[5]<80.:
            full_room=box(*rb[:4],rb[4],125.479)
            front_service_rooms.append(full_room)
            pieces['front-bottom']=pieces['front-bottom'].cut(full_room)

    def install(feature,owner,at,angle=0.):
        feature=placed(feature,at,angle)
        features.append(feature)
        owners[id(feature)]=owner
        pieces[owner]=feature.apply(pieces[owner])
        for name,shape in feature.parts.items(): moving[name]=shape
        print('  '+feature.name+' -> '+owner,flush=True)
        return feature

    # Refrigeration contacts grow from the actual floor and wall, with the
    # native open grooves, corbels and pilots intact.
    install(f.m5_floor_post(),'front-bottom',(-85.,80.,6.))
    install(f.condenser_upper_mount(),'front-bottom',(-120.,35.,70.),180.)
    install(f.condenser_crown_rail(),'back-bottom',(-120.,148.,55.),-90.)
    install(f.core_corner_stop(),'back-bottom',(103.,141.,6.),180.)
    install(f.mq6_slot(),'back-bottom',(-80.,213.,6.),-90.)
    coldhold=install(f.core_hold_down(),'back-top',(-120.,163.,97.),90.)

    # The fixed display/plumbing divider is broad 3 mm stock on the floor.
    # Its two native interfaces remain individual working mechanisms.
    pieces['front-bottom']=pieces['front-bottom'].fuse(
        box(-112.,-61.,64.,67.,6.,105.3))
    install(f.valve_seat_section(),'front-bottom',(-85.1,64.,51.))
    install(f.cable_clip(),'front-bottom',(-92.,64.,66.3),180.)

    install(f.tee_carrier_section(),'front-bottom',(120.,23.,6.))
    install(f.m3_wall_mount(),'back-top',(-120.,130.,116.2),180.)
    install(f.wago_well(),'back-top',(-120.,150.,108.),180.)
    # A plumbing ceiling carries the whole flow meter below the counter. Its
    # twelve-millimetre source roof retains the matched housing reliefs.
    flow_place=(-75.5,172.,104.)
    roof=box(-120.,-63.2,118.,173.,95.,107.)
    flow_rooms=placed(ceiling_hardware_rooms.build('flow_meter'),flow_place,180.)
    for room in flow_rooms.cut.values(): roof=roof.cut(room)
    pieces['back-top']=pieces['back-top'].fuse(roof)
    meter=install(f.flow_meter_anchors(),'back-top',flow_place,180.)
    features.append(flow_rooms)
    owners[id(flow_rooms)]='back-top'
    # The threaded-chain seat has its own lower plumbing ceiling, clear of
    # the native C14 mouth above. Broad roof and side stock join the counter.
    asse_roof_z=64.789419
    asse_rooms=placed(ceiling_hardware_rooms.build('asse'),(120.,170.,58.),180.)
    asse_roof=box(75.413,120.,104.,213.,asse_roof_z,asse_roof_z+12.)
    for room in asse_rooms.cut.values(): asse_roof=asse_roof.cut(room)
    pieces['back-top']=pieces['back-top'].fuse(asse_roof).fuse(
        box(120.,129.,104.,213.,asse_roof_z+9.,128.))
    asse=install(f.asse_anchor(),'back-top',(120.,170.,58.),180.)
    features.append(asse_rooms);owners[id(asse_rooms)]='back-top'
    pieces['back-top']=pieces['back-top'].fuse(
        box(-66.2,-63.2,115.,130.,114.,137.))
    install(f.tube_anchor(),'back-top',(-66.2,122.,122.68))
    funnel=install(funnel_joint_v3.build(),'back-top',(67.5,101.,84.9))
    c14=install(f.c14_tunnel(),'back-top',(129.,174.,90.),-90.)
    # One source C14 tunnel spans below the Z joint. The opposite native rail
    # stays complete; this side receives the same fixture's exact clearance.
    c14b=f.bounds(union(list(c14.add.values())))
    relief=box(c14b[0]-.25,129.25,c14b[2]-.25,c14b[3]+.25,
               c14b[4]-.25,80.25)
    pieces['back-bottom']=pieces['back-bottom'].cut(relief)
    pieces['back-bottom']=pieces['back-bottom'].cut(
        box(115.,126.1,112.,210.,79.5,95.05))

    chase=placed(f.prv_chase(),(-103.,216.,97.05),-90.)
    features.append(chase)
    for half,owner in (('lower','back-bottom'),('upper','back-top')):
        for name,stock in chase.add.items():
            if name.startswith(half): pieces[owner]=pieces[owner].fuse(stock)
        for name,room in chase.cut.items():
            if name.startswith(half): pieces[owner]=pieces[owner].cut(room)

    # The complete source side pull is accessible through a tall lower window,
    # then fully exposed when the top service member slides off.
    pull=d.metadata['genuine_side_pull']
    service=box(pull['opening_world_x_mm'],130.,
                pull['y_mm'][0],pull['y_mm'][1],pull['z_mm'][0],71.5)
    pieces['back-bottom']=pieces['back-bottom'].cut(service)

    # Full upward extraction of the native window cover, after the upper
    # front is removed. The stationary cap stock cannot re-close its tongue.
    cover=moving['vertical_window_cover']
    cv=f.bounds(cover)
    pieces['front-bottom']=pieces['front-bottom'].cut(
        box(cv[0]-.25,cv[1]+.25,cv[2]-.25,cv[3]+.25,cv[4]-.25,cv[5]+22.75))

    # The quiet row uses three actual fitting families in their full native
    # clamped stack. Flange/nut proxies are explicit dry display components.
    for which,at,angle in (
        ('water',(127.,156.,117.7),-90.),
        ('co2',(127.,190.,117.7),-90.),
        ('drain',(-127.,190.,117.7),90.)):
        pf=install(small_fronts_v3.port(which,nominal_clamp=True),'back-top',at,angle)
        clamp=pf.backing['nominal_clamp']
        nut=pf.parts['nominal_'+which+'_nut']
        # Circular access to the true inboard bearing plane leaves the
        # source three-millimetre wall at the fitting, with normal wall stock
        # surrounding the purchased-part room.
        radius=clamp['source_nut_envelope_diameter_mm']/2.+.25
        inward=(-1.,0.,0.) if angle<0 else (1.,0.,0.)
        x=124.001 if angle<0 else -124.001
        room=cq.Solid.makeCylinder(radius,8.251,cq.Vector(x,at[1],at[2]),cq.Vector(*inward))
        pieces['back-top']=pieces['back-top'].cut(room)

    # Source DATA and two bare inspection openings are covered by the captive
    # reference flags. DATA lettering is discovered when that flag slides.
    pieces['back-top']=pieces['back-top'].fuse(q.added_frames()).clean()
    moving.update(q.members())
    data=install(small_fronts_v3.data(),'back-top',(-76.,216.,112.))
    for x in (-13.,50.):
        passage=(cq.Workplane('XZ',origin=(x,217.,112.))
            .rect(20.8,18.3).extrude(5.).edges('|Y').fillet(.4).val())
        pieces['back-top']=pieces['back-top'].cut(passage)

    # The original thirty-degree glass seat, bezel and both wing lips form
    # the front face; the one-millimetre printed backer is named as a proxy.
    display=small_fronts_v3.moved(small_fronts_v3.display(full_facet_stock=False),
                                 small_fronts_v3.display_datum(b.outer))
    features.append(display);owners[id(display)]='front-top'
    pieces['front-top']=display.apply(pieces['front-top'])
    moving.update(display.parts)

    # All moving corridors and source native rooms are last cuts. A broad
    # wall added by a neighbouring fixture cannot fill a fit or a lead exit.
    for owner,host in pieces.items():
        for room in d.cut.values(): host=host.cut(room)
        if owner=='front-bottom':
            for room in front_service_rooms: host=host.cut(room)
        for feature in features:
            for room in feature.cut.values(): host=host.cut(room)
        for feature in features:
            if owners.get(id(feature))==owner:
                for catch in feature.post_add.values(): host=host.fuse(catch)
        pieces[owner]=host.clean()

    # The source roof fixtures belong to the rear service member. Its native
    # neighbours receive their complete stationary envelope and withdrawal
    # air, rather than losing working stock from those fixtures.
    for feature in (meter,asse,coldhold):
        bounds=f.bounds(union(list(feature.add.values())))
        room=box(*(v+(-.25 if i%2==0 else .25) for i,v in enumerate(bounds)))
        pieces['front-top']=pieces['front-top'].cut(room)
    # The upper member's lower service ceiling receives broad stock in the
    # bottom member, retaining the opposite complete native Z rail.
    lower_room=box(75.163,129.25,103.75,216.25,41.51,80.25)
    pieces['back-bottom']=pieces['back-bottom'].cut(lower_room)
    pieces['front-bottom']=pieces['front-bottom'].cut(lower_room)
    for feature in features:
        if feature.name in ('wall_cable_clip','complete_rear_funnel_joint','tube_anchor_2'):
            bounds=f.bounds(union([*feature.add.values(),*feature.post_add.values()]))
            room=box(*(v+(-.25 if i%2==0 else .25) for i,v in enumerate(bounds)))
            pieces['front-top']=pieces['front-top'].cut(room)
    pieces['front-top']=pieces['front-top'].cut(box(-112.25,-60.75,63.75,67.25,6.,105.55))
    pieces['front-top']=pieces['front-top'].cut(box(-66.45,-62.95,114.75,130.25,113.75,137.25))
    fixed_bounds=f.bounds(d.fixed['fixed_docking_wall'])
    receiving=box(*(v+(-.25 if i%2==0 else .25) for i,v in enumerate(fixed_bounds)))
    pieces['back-top']=pieces['back-top'].cut(receiving)

    # Native flat-wing nameplate on the drawer's broad front fascia.
    npfit=e._nameplate_fit
    frame=(2.,0.,38.)
    blank=box(-70.,70.,-12.,1.,-27.,27.)
    remote=box(1000.,1001.,1000.,1001.,1000.,1001.)
    receiver=lambda s:npfit.apply(s,npfit.dimensions.station(0,0),0.,up=1.)
    stock=receiver(remote).cut(remote)
    rooms=blank.cut(receiver(blank))
    stock=stock.rotate((0,0,0),(0,0,1),180.).translate(frame)
    rooms=rooms.rotate((0,0,0),(0,0,1),180.).translate(frame)
    moving['pump_drawer']=moving['pump_drawer'].fuse(stock).cut(rooms).clean()
    nameplate_src=ROOT/'hardware/printed-parts/enclosure/nameplate'
    sys.path.insert(0,str(nameplate_src))
    import nameplate
    black=nameplate.build_plate(1)
    white=nameplate.build_ink(1)
    black=black.val() if isinstance(black,cq.Workplane) else black
    white=white.val() if isinstance(white,cq.Workplane) else white
    label_place=(2.,npfit.THICK,38.)
    nameplate_parts={'nameplate_black':black.rotate((0,0,0),(0,0,1),180.).translate(label_place),
                     'nameplate_white':white.rotate((0,0,0),(0,0,1),180.).translate(label_place)}
    moving.update(nameplate_parts)

    grip=e.grip_interface(b.inner)
    moving['handhold_grip']=grip.placed(grip.cover(),-1)
    comparisons=comparison_additions_v3.build()
    moving['pump_drawer']=comparisons.apply_drawer(moving['pump_drawer'])
    moving.update(comparisons.parts)

    # One native pierced-flute ventilation field, at the field's own phase.
    # Source transoms/hips retain exactly their working profiles.
    courses=((84.,95.),(99.,110.),(114.,125.),(129.,136.))
    for arc in e.flute_centres(b.outer):
        (_px,py),(nx,ny)=e.plan_at(arc,b.outer)
        if abs(nx-1.)<1e-8 and 21.<=py<=70.:
            for low,high in courses:
                pieces['front-top']=pieces['front-top'].cut(
                    e._vent_cutter(b.outer,1.,py,low,high))

    # Counter holes follow the source three M3 axes. Ordinary ceiling stock
    # remains under the 2 mm gasket and 4 mm mounting plate.
    axes=[(FAUCET[0]+22.5,FAUCET[1]-2.),
          (FAUCET[0]-22.5,FAUCET[1]-2.),
          (FAUCET[0],FAUCET[1]-22.3)]
    for x,y in axes:
        pilot=cq.Solid.makeCylinder(4./2.,5.7,cq.Vector(x,y,128.))
        shank=cq.Solid.makeCylinder(3.9/2.,14.,cq.Vector(x,y,127.))
        pieces['back-top']=pieces['back-top'].cut(pilot).cut(shank)
    front_bolt=cq.Solid.makeCylinder(3.9/2.,14.,cq.Vector(-80.,115.7,127.))
    pieces['front-top']=pieces['front-top'].cut(front_bolt).cut(box(-82.2,-77.8,115.7,120.,127.,141.))
    # Three actual source openings continue the shank, flavor/drain pill
    # and flat signal lane through the counter; no surrounding show stock
    # or working fixture is removed by an enclosing circular approximation.
    import faucet_module
    sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
    import _faucet_interface as fi
    import faucet_paths as paths
    import faucet_shell as shell
    counter_rooms=[cq.Solid.makeCylinder(fi.shank_hole_diameter/2.,20.,
                    cq.Vector(FAUCET[0],FAUCET[1],125.)),
        cq.Workplane('XY').workplane(offset=125.).center(
            FAUCET[0]+fi.bundle_slot_center_x,FAUCET[1]+fi.flavor_tube_depth)
            .slot2D(fi.bundle_slot_length_x,fi.pill_width_y).extrude(20.).val(),
        cq.Solid.extrudeLinear(shell._lower_signal_profile(125.,FAUCET[0]+paths.LOWER_BUNDLE_X,
            FAUCET[1]+paths.LOWER_RIBBON_Y,shell.signal_lane_width,
            shell.signal_lane_depth,True),[],cq.Vector(0,0,20.))]
    for owner in ('front-top','back-top'):
        for room in counter_rooms: pieces[owner]=pieces[owner].cut(room)

    # The ordinary ASSE side wall receives the native upper-right Y plug.
    # Source rear-shell stock is preserved; only its original empty air is
    # removed from the transplanted broad column.
    native_receiver_air=box(125.,126.,100.75,136.944,84.65,140.25).cut(original_back_top)
    pieces['back-top']=pieces['back-top'].cut(native_receiver_air)
    notes.append('Upper-right Y receiver retains every original rear-shell face; the added ASSE side column receives its exact native empty air.')

    for name,shape in pieces.items():
        pieces[name]=shape.clean()
        print(name,len(shape.Solids()),shape.isValid(),round(shape.Volume()),flush=True)
    return {'native':e,'box':b,'pieces':pieces,'moving':moving,
            'features':features,'drawer':d,'nameplate_frame':frame,
            'feature_owners':{x.name:owners.get(id(x),'split at source seam') for x in features},
            'counter_M3_axes_xy_mm':axes,
            'reference_hardware':d.reference,'comparisons':comparisons,'notes':notes}

def export_cache(result):
    from _cadq_export import export_assembly
    folder=CACHE_DIR
    folder.mkdir(parents=True,exist_ok=True)
    assembly=cq.Assembly(name='The Pour working cabinet')
    report={'features':[f.report() for f in result['features']],
            'drawer':result['drawer'].report(),'comparisons':result['comparisons'].report(),'parts':{}}
    for name,shape in {**result['pieces'],**result['moving']}.items():
        cq.exporters.export(shape,str(folder/(name+'.step')))
        color=(.8,.8,.78) if name.endswith('white') else (.13,.15,.16)
        assembly.add(shape,name=name,color=cq.Color(*color))
        report['parts'][name]={'bounds_mm':f.bounds(shape),'solids':len(shape.Solids()),
                              'valid':shape.isValid(),'volume_mm3':shape.Volume()}
    export_assembly(assembly,str(folder/'cabinet.step'))
    (folder/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')

if __name__=='__main__': export_cache(build())
