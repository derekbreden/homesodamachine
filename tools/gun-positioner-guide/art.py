"""Actual-CAD pictures and electrical schematics for the positioner guide.

The mechanical pictures import the same part builders as the fabrication
exports. Coral denotes the part installed in the pictured operation. Blue is
a measurement tool or a working-geometry reference, never a fabricated part.
Schematic wire locations describe nodes, not connector pin order.
"""
from __future__ import annotations

import html
import base64
import hashlib
import importlib.util
import json
import math
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
GUIDE = ROOT / "hardware/gun-positioner-guide"
ART = GUIDE / "art"
OUT = GUIDE / "out"
INK = "#202337"
BLUE = "#1749d1"
CORAL = "#d64050"
MUTED = "#606a78"
STEEL = "#e4e8ee"
PALE = "#f5f8ff"
BRASS = "#b08a2c"
MECHANICS = ROOT / "hardware/printed-parts/fixtures/gun-positioner/gun_positioner.py"
OPTICS = ROOT / 'tools/gun-positioner-optics/mounts.py'
MOUNTING = ROOT / 'hardware/gun-positioner/mounting/generate.py'


def import_file(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec)
    sys.modules[name]=module
    spec.loader.exec_module(module)
    return module


def mechanical_scenes():
    """Select parts from the fabrication assembly without rebuilding geometry."""
    os.environ.setdefault("HSM_NO_BUILD_LOCK","1")
    import cadquery as cq
    gp=import_file(MECHANICS,"positioner_guide_geometry")
    whole,receipt=gp.assembly(include_boom=True)
    rows={r['name']:r for r in receipt}
    flat={name:node for name,node in whole.traverse() if node.obj is not None}
    colors={k:cq.Color(*v) for k,v in gp.COLORS.items()}
    coral=cq.Color(.84,.25,.31)
    blue=cq.Color(.30,.52,.84)
    scenes={}
    details={}
    def make(name, *, groups=None, names=None, exclude=(), highlight=(), explode=None,
             screw_crop=None,poise=None,cam=(1,-1,.7),up=(0,0,1), size="2400x1600"):
        assy=cq.Assembly(name=f"guide-{name}")
        selected=[]
        for part_name,node in flat.items():
            row=rows[part_name]
            if groups is not None and row['group'] not in groups:continue
            if names is not None and not any(word in part_name for word in names):continue
            if any(word in part_name for word in exclude):continue
            loc=node.loc;shape=node.obj
            if screw_crop is not None and part_name.endswith('-screw'):
                center,length=screw_crop
                shape=shape.intersect(cq.Workplane('XY').box(length,160,160).translate((center,0,0)))
            if explode and row['group'] in explode:
                loc=cq.Location(cq.Vector(*explode[row['group']]))*loc
            if poise:
                for token,distance in poise.items():
                    if token in part_name:
                        v=[float(distance*row['rotation_matrix'][i][2]) for i in range(3)]
                        loc=cq.Location(cq.Vector(*v))*loc
                        break
            color=coral if any(word in part_name for word in highlight) else colors[row['material']]
            if row['kind']=='proxy':color=blue
            assy.add(shape,name=part_name,loc=loc,color=color)
            selected.append(part_name)
        if not selected:raise ValueError(f"No CAD instances selected for {name}")
        scenes[name]=(assy,dict(cam=cam,up=up,size=size))
        details[name]=dict(parts=selected,highlight=list(highlight),
                           exploded_offsets_mm=explode or {},screw_crop_local_mm=screw_crop,
                           part_axis_poise_mm=poise or {},camera_direction=list(cam),camera_up=list(up))
    make('hero',exclude=['fiber-'],cam=(-1,1,.5),size="2400x2400")
    make('whole-exploded',groups=['station','x','y','z','yaw','pitch','roll','crash','clamp'],
         explode={'x':(0,0,90),'y':(0,0,180),'z':(0,0,280),'yaw':(0,0,390),'pitch':(0,0,450),'roll':(0,0,490),'crash':(0,0,510),'clamp':(0,0,540)},
         cam=(1,-1,.55),size="2400x2400")
    make('station',groups=['station'],cam=(1,-1,1),highlight=['station-'])
    make('x-bed',groups=['station','x'],names=['station-','x-bed'],highlight=['x-bed'])
    make('x-rails',groups=['x'],names=['x-bed','x-rail','x-block'],highlight=['x-rail','x-block'],cam=(.6,-1,1))
    make('x-carriage',groups=['x'],names=['x-bed','x-rail','x-block','x-carriage'],highlight=['x-carriage'],cam=(.6,-1,1))
    make('x-complete',groups=['x'],highlight=['x-screw','x-nut-face','x-nut-spacer'],cam=(.5,-1,.8))
    make('y-bed',groups=['x','y'],names=['x-carriage','y-bed'],highlight=['y-bed'],cam=(.7,-1,.9))
    make('y-rails',groups=['y'],names=['y-bed','y-rail','y-block'],highlight=['y-rail','y-block'],cam=(.7,-1,.9))
    make('y-carriage',groups=['y'],names=['y-bed','y-rail','y-block','y-carriage'],highlight=['y-carriage'],cam=(.7,-1,.9))
    make('xy-complete',groups=['x','y'],highlight=['y-screw','y-nut-face','y-nut-spacer'],cam=(.5,-1,.7))
    make('z-mast',groups=['y','z'],names=['y-carriage','z-upright','z-bed'],highlight=['z-upright','z-bed'],cam=(1,-1,.5))
    make('z-rails',groups=['z'],names=['z-bed','z-rail','z-block'],highlight=['z-rail','z-block'],cam=(1,-1,.4))
    make('z-carriage',groups=['z'],names=['z-bed','z-rail','z-block','z-carriage'],highlight=['z-carriage'],cam=(1,-1,.4))
    make('z-head',groups=['z'],names=['z-carriage','z-head','z-yaw-head','yaw-head-adapter'],highlight=['z-head','yaw-head-adapter'],cam=(1,-1,.5))
    make('z-complete',groups=['z'],highlight=['z-screw','z-single-driving-nut','z-force-','z-nut-'],cam=(1,-1,.4))
    foundation=['x-fixed-floor','x-motor-support-leg','x-motor-upper-angle','x-motor-foot-angle','x-thrust-support-leg','x-thrust-post-angle','x-thrust-foot']
    make('drive-foundation',groups=['x'],names=foundation,highlight=['support-leg','angle'],cam=(.8,-1,.6))
    fixed=['x-screw','x-radial','x-thrust','x-fixed-retention']
    make('drive-thrust',groups=['x'],names=fixed,highlight=['thrust','fixed-retention'],screw_crop=(40,140),cam=(.8,-1,.6))
    make('drive-radial',groups=['x'],names=fixed,highlight=['radial'],screw_crop=(40,140),cam=(.8,-1,.6))
    make('drive-nuts',groups=['x'],names=['x-screw','x-single-driving','x-nut-face','x-nut-print','x-nut-metal'],
         highlight=['single-driving','nut-face','nut-print','nut-metal'],screw_crop=(220,140),cam=(.8,-1,.6))
    pulley=fixed+['x-pulley']
    make('drive-pulley',groups=['x'],names=pulley,highlight=['pulley'],screw_crop=(40,140),cam=(.8,-1,.6))
    motor=pulley+['x-motor','x-pinion']
    make('drive-motor',groups=['x'],names=motor,highlight=['motor','pinion'],screw_crop=(40,140),cam=(.8,-1,.6))
    belt=motor+['x-belt-span']
    make('drive-belt',groups=['x'],names=belt,highlight=['belt-span'],screw_crop=(40,140),cam=(.8,-1,.6))
    make('drive-guard',groups=['x'],names=belt+['x-belt-guard'],highlight=['belt-guard'],screw_crop=(40,140),cam=(.8,-1,.6))
    cage=['x-screw','x-single-driving','x-nut-','x-force-end','x-force-shoulder','x-force-cage']
    make('force-cage',groups=['x'],names=cage,highlight=['force-end','force-shoulder','force-cage'],screw_crop=(220,150),cam=(.7,-1,.6))
    force=cage+['x-overload','x-force-guide','x-force-boss','x-force-washer','x-force-spring','x-carriage-output']
    make('force-shuttle',groups=['x'],names=force,highlight=['overload-shuttle','force-guide','force-boss','force-washer','force-spring'],screw_crop=(220,150),cam=(.7,-1,.6))
    make('force-calibration',groups=['x'],names=force,highlight=['overload-switch','overload-flag'],screw_crop=(220,150),cam=(.7,-1,.6))
    make('yaw-bearings',groups=['yaw'],names=['yaw-bearing','yaw-shaft'],highlight=['bearing','shaft'],cam=(1,-1,.6))
    drive_tokens=['screw','radial','thrust','fixed-retention','pulley','pinion','motor','belt','nut-','single-driving','clevis','hinge','switch','stop','force-','overload','friction','base-web','lever']
    make('yaw-frame',groups=['yaw'],exclude=drive_tokens,highlight=['output-hub','crossbar','yaw-side'],cam=(1,-1,.5))
    make('pitch-bearings',groups=['yaw','pitch'],names=['yaw-side','pitch-foot','pitch-bearing','pitch-shaft'],highlight=['pitch-foot','pitch-bearing','pitch-shaft'],cam=(1,-1,.6))
    make('pitch-frame',groups=['pitch'],exclude=drive_tokens,highlight=['pitch-side','pitch-crossbar'],cam=(1,-1,.6))
    make('roll-bearings',groups=['pitch','roll'],names=['pitch-side','pitch-crossbar','roll-bearing','roll-shaft'],highlight=['roll-bearing','roll-shaft'],cam=(1,-1,.6))
    make('roll-cradle',groups=['roll'],exclude=drive_tokens,highlight=['roll-cradle','roll-output'],cam=(1,-1,.6))
    make('angular-anchors',groups=['yaw','pitch','roll'],names=['base-web','base-anchor','yaw-bearing-back','yaw-side','pitch-crossbar','pitch-side','base-clevis'],highlight=['base-web','base-anchor'],cam=(.6,-1,.7),size='2400x2000')
    make('angular-clevis',groups=['yaw'],names=['yaw-screw','yaw-radial','yaw-thrust','yaw-fixed-retention','yaw-nut-','yaw-single-driving','clevis','hinge','yaw-lever','yaw-force-','yaw-overload','base-web'],highlight=['clevis','lever'],cam=(.6,-1,.7))
    make('gimbal',groups=['yaw','pitch','roll','crash','clamp'],cam=(1,-1,.7),size="2400x2000")
    for axis in ('yaw','pitch','roll'):
        make(axis+'-shaft-capture',groups=[axis,'shaft-capture'],
             names=[axis+'-bearing',axis+'-shaft',axis+'-negative-shaft',axis+'-positive-shaft',axis+'-output-hub',axis+'-lever-hub',axis+'-foot'],
             exclude=[axis+'-bearing-back'],
             highlight=['capture-tube','end-retainer','end-flat-washer','M5-end-bolt'],
             cam=(1,-1,.65),size='2400x1700')
    make('gun-clamp',groups=['roll','crash','clamp','gun'],names=['roll-cradle','gun-','aim-','crash-released'],highlight=['jaw','pad'],cam=(.7,-1,.55))
    # Use the gun tray's own fabrication orientation for close assembly views.
    gun_R=rows['crash-released-tray']['rotation_matrix']
    def gv(v):return tuple(sum(gun_R[i][j]*v[j] for j in range(3)) for i in range(3))
    gcam,gup=gv((.65,-1,.8)),gv((0,0,1))
    guide_names=['roll-cradle','ground-guide','guide-support','lower-guide','lower-bushing','collar','fixed-crossbar']
    make('crash-guides',groups=['roll','crash'],names=guide_names,highlight=['ground-guide','guide-support','lower-guide','collar','fixed-crossbar'],cam=gcam,up=gup)
    pod_names=guide_names+['crash-left-shoulder','crash-right-shoulder','crash-left-boss','crash-right-boss','pressure-washer','crash-left-spring','crash-right-spring','crash-left-shuttle','crash-right-shuttle','upper-bushing','cage-tie']
    make('crash-pods',groups=['roll','crash'],names=pod_names,highlight=['shoulder','boss','pressure-washer','spring','shuttle'],cam=gcam,up=gup)
    make('crash-carriers',groups=['crash'],exclude=['released','ball','V-dowel','keeper','cup-','contact','presence'],highlight=['output-wall','carrier','magnetic-back'],cam=gcam,up=gup)
    seats=['crash-magnetic-back','crash-released-back','crash-ball','crash-V-dowel','crash-seat-keeper']
    make('crash-seats',groups=['crash'],names=seats,highlight=['ball','V-dowel','keeper'],cam=gv((1,-.7,.8)),up=gup)
    make('crash-magnets',groups=['crash'],names=seats+['crash-cup'],highlight=['cup-'],cam=gv((1,-.7,.8)),up=gup)
    make('crash-contacts',groups=['crash'],highlight=['axial-contact','plate-presence'],cam=gcam,up=gup)
    make('fiber-boom',groups=['fiber','gun'],highlight=['fiber-'],cam=(1,-1,.5),size='2400x2000')
    swivel_names=[n for n in flat if rows[n]['group']=='fiber' and
                  (n.endswith('-100') or 'fiber-base-' in n and '-100-' in n or 'fiber-bearing-cap-bolt-100-' in n)]
    make('fiber-swivel',groups=['fiber'],names=swivel_names,highlight=['fiber-saddle','fiber-bearing-cap','fiber-swivel-bearing'],
         poise={'fiber-bearing-cap':-35},cam=(1,-1,-.4),size='2400x1600')
    retention=['z-screw','z-radial','z-thrust','z-fixed-retention','z-friction']
    make('friction-washer',groups=['z'],names=retention,exclude=['preload-seat','preload-post','guide-pin'],
         highlight=['friction-washer','friction-spring'],screw_crop=(45,145),poise={'friction-washer':14,'friction-spring':28},cam=(.8,-1,.6))
    make('friction-preload',groups=['z'],names=retention,highlight=['preload-seat','preload-post','guide-pin'],
         screw_crop=(45,145),cam=(.8,-1,.6))
    make('limits-linear',groups=['x'],names=['x-bed','x-carriage','x-switch','x-stop'],highlight=['switch','stop'],cam=(.6,-1,.9))
    make('limits-angular',groups=['yaw'],names=['yaw-lever','yaw-switch','yaw-metal-stop'],highlight=['switch','stop'],cam=(.6,-1,.9))
    # Printable inventory is laid out from individual fabrication solids.
    for image_name,kind in [('print-parts','print'),('plate-parts','metal')]:
        assy=cq.Assembly(name=f"guide-{image_name}")
        position=0
        source_names=[]
        for part_name,data in gp.PARTS.items():
            if data['kind']!=kind:continue
            shape=data['model']
            bb=shape.val().BoundingBox()
            dx,dy=(160,190) if kind=='print' else (520,500)
            shape=shape.translate((position%4*dx-bb.xmin,position//4*dy-bb.ymin,-bb.zmin))
            assy.add(shape,name=part_name,color=colors[data['material']])
            source_names.append(part_name)
            position+=1
        scenes[image_name]=(assy,dict(cam=(.15,-.3,1),size="2400x1800"))
        details[image_name]=dict(fabrication_parts=source_names)
    opt=import_file(OPTICS,'positioner_guide_metal_inventory_optics');opt.init_parts()
    metals=[(n,d) for n,d in gp.PARTS.items() if d['kind']=='metal' and d.get('blank_mm')]
    metals += [(n,d) for n,d in opt.PARTS.items() if d['kind']=='metal']
    for first in range(0,len(metals),12):
        name=f'metal-kit-{first//12+1}';assy=cq.Assembly(name=name);part_names=[];display_scales={}
        for i,(part,data) in enumerate(metals[first:first+12]):
            shape=data['model'];bb=shape.val().BoundingBox()
            # Each cell is an identification view, with its own display scale.
            # This keeps an 8 mm spacer as readable as a 450 mm bed plate.
            display_scale=min(150/max(bb.xlen,.01),130/max(bb.ylen,.01),65/max(bb.zlen,.01))
            shape=cq.Workplane(obj=shape.val().scale(display_scale));bb=shape.val().BoundingBox()
            shape=shape.translate((i%4*190+95-(bb.xmin+bb.xmax)/2,
                                   i//4*160+80-(bb.ymin+bb.ymax)/2,-bb.zmin))
            assy.add(shape,name=part,color=cq.Color(.36,.43,.57));part_names.append(part)
            display_scales[part]=display_scale
        scenes[name]=(assy,dict(cam=(.15,-.3,1),size='2400x1800'))
        details[name]=dict(fabrication_parts=part_names,display_scales=display_scales,
                          order='Rows left-to-right match the page table; each part has its own identification-view scale.')
    for name,part in [('coupon','pulley-sector-coupon'),('hub','shaft-hub'),('metal-jaws','gun-jaw')]:
        assy=cq.Assembly(name=name)
        assy.add(gp.PARTS[part]['model'],name=part,color=coral)
        scenes[name]=(assy,dict(cam=(.5,-1,.7),size="2400x1500"))
        details[name]=dict(fabrication_parts=[part])
    # A separate shaft service lever preserves the actual payload on its output hub.
    a=cq.Assembly(name='guide-angular-load-lever');selected=[]
    for n in ['pitch-lever-hub','pitch-shaft--1']:
        node=flat[n];row=rows[n]
        a.add(node.obj,name=n,loc=node.loc,color=colors[row['material']]);selected.append(n)
    lever_loc=flat['pitch-lever'].loc*cq.Location(cq.Vector(-75,0,0))
    a.add(gp.PARTS['angular-load-lever']['model'],name='angular-load-lever',loc=lever_loc,color=blue)
    scenes['angular-load-lever']=(a,dict(cam=(1,-1,.7),size='2400x1600'))
    details['angular-load-lever']=dict(parts=selected,fabrication_parts=['angular-load-lever'],
                                      replaced_part='pitch-lever',local_pivot_offset_mm=[-75,0,0],
                                      scope='Actual drive-lever hub and shaft; temporary balanced lever replaces only the drive lever. Payload remains on the separate output hub.')
    fixture_names={'brake-torque':'installed-torque-lever',
                   'torque-redirect':'torque-redirect',
                   'powered-force-fixture':'powered-force-fixture',
                   'crash-loading':'nozzle-loading-fork',
                   'installed-z-load-bound':'installed-z-load-bound',
                   'hub-clamp-proof':'hub-clamp-proof',
                   'shaft-capture-proof':'shaft-capture-proof'}
    fixtures=gp.fixture_assemblies()
    for name,source_name in fixture_names.items():
        source,receipt=fixtures[source_name];by_name={r['name']:r for r in receipt}
        a=cq.Assembly(name='guide-'+name);selected=[]
        for n,node in source.traverse():
            if node.obj is None:continue
            row=by_name[n]
            proxy='envelope' in n or 'reference' in n
            color=blue if proxy or row['group']=='fixture' else colors[row['material']]
            if name in ('hub-clamp-proof','shaft-capture-proof'):
                color=blue if proxy else coral if any(t in n for t in ('specimen','loaded-lever','load-bridge','output-plate','proof-tube','-washer','-flat','-M5')) else colors[row['material']]
            a.add(node.obj,name=n,loc=node.loc,color=color)
            selected.append(n)
        scenes[name]=(a,dict(cam=(1,-1,.7) if name!='powered-force-fixture' else (1,-1,.4),size='2400x1800'))
        details[name]=dict(source_fixture=source_name,parts=selected,fixture_receipt=receipt,
                           scope='Actual source fixture models; gauge envelope is a catalog proxy, and received alignment remains a measured setup.')
        if source_name=='hub-clamp-proof':
            for close_name,gauge_view in [('hub-proof-joint',False),('hub-proof-gauge',True)]:
                close=cq.Assembly(name='guide-'+close_name);visible=[]
                for n,node in source.traverse():
                    if node.obj is None:continue
                    if not gauge_view and any(t in n for t in ('gauge','quill','cap-M5','vise','load-bridge','load-front','load-back','saddle')):continue
                    if gauge_view and not any(t in n for t in ('gauge','quill','cap-M5','load-','saddle','loaded-lever')):continue
                    shape=node.obj
                    if 'horizontal-column' in n:
                        shape=shape.intersect(cq.Workplane('XY').box(100,160,100).translate((0,250,0)))
                    if not gauge_view and 'loaded-lever' in n:
                        shape=shape.intersect(cq.Workplane('XY').box(95,50,25))
                    if gauge_view and 'loaded-lever' in n:
                        shape=shape.intersect(cq.Workplane('XY').box(65,50,25).translate((130,0,0)))
                    color=blue if 'envelope' in n or 'reference' in n else coral if any(t in n for t in ('specimen','loaded-lever','load-bridge','quill-cap')) else colors[by_name[n]['material']]
                    close.add(shape,name=n,loc=node.loc,color=color);visible.append(n)
                scenes[close_name]=(close,dict(cam=(.7,-1,.65),size='2400x1800'))
                details[close_name]=dict(source_fixture=source_name,parts=visible,fixture_receipt=receipt,
                                        scope='Actual source fixture detail; long column/gauge lever cropped only for this view. Gauge body remains a catalog envelope.')
        if source_name=='shaft-capture-proof':
            for close_name,gauge_view in [('shaft-capture-joint',False),('shaft-capture-gauge',True)]:
                close=cq.Assembly(name='guide-'+close_name);visible=[]
                for n,node in source.traverse():
                    if node.obj is None:continue
                    if not gauge_view and any(t in n for t in ('column','gauge','manual-jack','catch','vise','bearing','riser','foot-M8')):continue
                    if gauge_view and not any(t in n for t in ('gauge','manual-jack','closed-bridge','load-interface','bridge-spacer','bridge-M3')):continue
                    shape=node.obj
                    color=blue if 'envelope' in n or 'reference' in n else coral if any(t in n for t in ('interface','bridge','coupling','gauge-cap','manual-jack')) else colors[by_name[n]['material']]
                    close.add(shape,name=n,loc=node.loc,color=color);visible.append(n)
                scenes[close_name]=(close,dict(cam=(1,1,.5) if gauge_view else (1,-1,.5),size='2400x1800'))
                details[close_name]=dict(source_fixture=source_name,parts=visible,fixture_receipt=receipt,
                                        scope='Actual symmetric capture-fixture detail. Fixed column omitted to expose gauge guides, backing and jack; gauge remains a catalog envelope.')
        if source_name=='installed-z-load-bound':
            close=cq.Assembly(name='guide-installed-z-jack')
            for n,node in source.traverse():
                if node.obj is None:continue
                shape=node.obj
                if n=='z-test-column':
                    shape=shape.intersect(cq.Workplane('XY').box(100,100,280).translate((0,0,220)))
                color=blue if 'envelope' in n else coral if 'jack' in n else colors[by_name[n]['material']]
                close.add(shape,name=n,loc=node.loc,color=color)
            scenes['installed-z-jack']=(close,dict(cam=(1,-1,.6),size='2400x1800'))
            details['installed-z-jack']=dict(source_fixture=source_name,parts=selected,fixture_receipt=receipt,
                                             column_visible_Z_mm=[80,360],highlight=['z-gauge-jack-angle','z-gauge-jack-screw'],
                                             scope='Actual fixture geometry with the long column cropped for the feed-jack detail. Gauge body remains a catalog proxy.')
    return scenes,details


def controller_scenes():
    """The three supplied insulating mount solids, without invented PCB holes."""
    import cadquery as cq
    module=import_file(MOUNTING,'positioner_guide_controller_mounts')
    parts=module.make_parts();scenes,details={},{}
    coral=cq.Color(.84,.25,.31);dark=cq.Color(.23,.25,.31)
    a=cq.Assembly(name='guide-controller-print-parts')
    a.add(parts['controller-backplane'][0],name='controller-backplane',color=dark)
    a.add(parts['fan-stand-80mm'][0].translate((225,0,0)),name='fan-stand-80mm',color=coral)
    a.add(parts['m3-insulating-spacer-6mm'][0].translate((225,-65,0)),name='m3-insulating-spacer-6mm',color=coral)
    scenes['controller-print-parts']=(a,dict(cam=(.55,-1,.85),size='2400x1600'))
    details['controller-print-parts']=dict(fabrication_parts=list(parts),scope='One spacer shown; manifest requires28. The assembly pose is separate from supplied STL print orientation.')
    a=cq.Assembly(name='guide-controller-mounts')
    a.add(parts['controller-backplane'][0],name='controller-backplane',color=dark)
    stations=[]
    for x in (-70,40):
        for y in (-80,0,80):
            for dx,dy in [(-15,-15),(-15,15),(15,-15),(15,15)]:
                p=(x+dx,y+dy,6)
                n=f'carrier-spacer-{x}-{y}-{dx}-{dy}'
                a.add(parts['m3-insulating-spacer-6mm'][0].translate(p),name=n,color=coral);stations.append(list(p))
    for dx,dy in [(-15,-15),(-15,15),(15,-15),(15,15)]:
        p=(115+dx,dy,6)
        a.add(parts['m3-insulating-spacer-6mm'][0].translate(p),name=f'Pico-spacer-{dx}-{dy}',color=coral);stations.append(list(p))
    scenes['controller-mounts']=(a,dict(cam=(.6,-1,.85),size='2400x1600'))
    details['controller-mounts']=dict(fabrication_parts=['controller-backplane','m3-insulating-spacer-6mm'],
                                   illustrative_spacer_stations_mm=stations,
                                   scope='Clearance illustration only:28actual spacers on actual blank. Received PCB/socket footprints govern transfer-drilled final stations.')
    a=cq.Assembly(name='guide-controller-fan-stand')
    a.add(parts['fan-stand-80mm'][0],name='fan-stand-80mm',color=coral)
    scenes['controller-fan-stand']=(a,dict(cam=(1,-1,.7),size='2400x1600'))
    details['controller-fan-stand']=dict(fabrication_parts=['fan-stand-80mm'],scope='76mm opening and two base holes are in source CAD; fan bolt holes are transfer-drilled from the received frame.')
    return scenes,details


def camera_scenes():
    """Named subsets of the two-stage fabrication assembly, plus true-axis bolts."""
    import cadquery as cq
    opt=import_file(OPTICS,'positioner_guide_camera_geometry')
    opt.init_parts()
    scenes,details={},{}
    dark=cq.Color(.23,.25,.31);coral=cq.Color(.84,.25,.31);blue=cq.Color(.3,.52,.84)
    base=['stationary_plate','4040_riser','M8_height_post','height_locknut']
    rails=base+['rail_','block_']
    carriage=rails+['camera_plate']
    stops=carriage+['metal_stop']
    returns=stops+['return_spacer']
    def bolt(d,length):
        sh=cq.Workplane('XY',origin=(0,0,-length)).circle(d/2).extrude(length)
        head=cq.Workplane('XY').circle(d*.85).extrude(d*.65)
        socket=cq.Workplane('XY',origin=(0,0,d*.25)).polygon(6,d*.84).extrude(d)
        return sh.union(head.cut(socket))
    def washer(d):return cq.Workplane('XY').circle(d).circle(d*.55).extrude(1 if d>=5 else .5)
    def make(name,include,highlight=(),retract=0,lens=True,cam=(1,-1,.75),extra=None):
        source=opt.assembly(retract=retract,lens_inserted=lens)
        a=cq.Assembly(name='guide-'+name);selected=[]
        for n,node in source.traverse():
            if node.obj is None or not any(v in n for v in include):continue
            color=coral if any(v in n for v in highlight) else dark
            if n in ('camera_envelope','Raynox_envelope'):color=blue
            a.add(node.obj,name=n,loc=node.loc,color=color);selected.append(n)
        hardware=[]
        if extra:extra(a,hardware,bolt,washer,coral,dark)
        scenes[name]=(a,dict(cam=cam,size='2400x1800'))
        details[name]=dict(parts=selected,highlight=list(highlight),extra_hardware=hardware,
                           retraction_mm=retract,lens_module_installed=lens,camera_direction=list(cam))
    def block_fasteners(a,h,bolt,washer,c,d):
        for x in (-50,50):
            for y in (-90,90):
                for dx in (-13,13):
                    for dy in (-14,14):
                        p=(100+x+dx,y+dy,opt.CAMERA_PLATE_Z+opt.T+1)
                        n=f'M5_block_{x}_{y}_{dx}_{dy}'
                        a.add(bolt(5,16).translate((p[0],p[1],p[2]+25)),name=n,color=c)
                        a.add(washer(5).translate((p[0],p[1],p[2]-1)),name=n+'_washer',color=d)
                        h.append(dict(name=n,fastener='M5x16',final_underhead_mm=list(p),poised_along_axis_mm=[0,0,25]))
    def return_fasteners(a,h,bolt,washer,c,d):
        for y in (-130,130):
            p=(-30,y,opt.CAMERA_PLATE_Z+opt.T+1)
            n=f'M5_return_{y}'
            a.add(bolt(5,70).translate((p[0],p[1],p[2]+20)),name=n,color=c)
            a.add(washer(5).translate((p[0],p[1],p[2]-1)),name=n+'_washer',color=d)
            h.append(dict(name=n,fastener='M5x70',final_underhead_mm=list(p),poised_along_axis_mm=[0,0,20]))
    make('camera-base',base,highlight=base)
    make('camera-rails',rails,highlight=['rail_','block_'])
    make('camera-carriage',carriage,highlight=['camera_plate'],extra=block_fasteners)
    make('camera-stops',stops,highlight=['metal_stop'])
    make('camera-return',returns,highlight=['return_spacer'],extra=return_fasteners)
    make('camera-only',returns+['camera_envelope'],highlight=['camera_envelope'],lens=False)
    make('lens-stand',['metal_angle','upright','lens_cassette','lens_retainer','Raynox_envelope'],highlight=['metal_angle','upright'],cam=(1,-1,.5))
    make('camera-forward',[''],highlight=['lens_cassette','lens_retainer'],cam=(1,-1,.55))
    make('camera-retracted',[''],retract=200,highlight=['camera_plate','lens_cassette','lens_retainer'],cam=(1,-1,.55))
    # Cassette is shown on its own fabrication coordinates; every separation
    # and bolt is along the optical axis, matching the actual rear pockets.
    a=cq.Assembly(name='guide-lens-cassette')
    a.add(opt.PARTS['lens-cassette']['model'],name='lens-cassette',color=coral)
    glass=cq.Workplane('XY',origin=(0,0,12)).circle(26.5).extrude(15.5)
    a.add(glass,name='lens-rim-envelope',color=blue)
    a.add(opt.PARTS['lens-retainer']['model'].translate((0,0,48)),name='lens-retainer',color=coral)
    for x in (-32,32):
        for y in (-32,32):
            a.add(bolt(3,20).translate((x,y,74)),name=f'M3_retainer_{x}_{y}',color=coral)
            nut=cq.Workplane('XY').polygon(6,6/math.cos(math.pi/6)).circle(1.6).extrude(2.4)
            a.add(nut.translate((x,y,-10)),name=f'M3_captive_{x}_{y}',color=dark)
    scenes['lens-cassette']=(a,dict(cam=(.7,-1,.8),size='2400x1800'))
    details['lens-cassette']=dict(fabrication_parts=['lens-cassette','lens-retainer'],
                                exploded_offsets_mm={'lens_rim':[0,0,10],'retainer':[0,0,30]},
                                extra_hardware='4 M3x20 screws without head washers, poised along optical axis; 4 rear captive nuts')
    # Complete lens module set aside during self-test, with clear head travel.
    source=opt.assembly(lens_inserted=False)
    a=cq.Assembly(name='guide-camera-startup')
    for n,node in source.traverse():
        if node.obj is None:continue
        a.add(node.obj,name=n,loc=node.loc,color=blue if n=='camera_envelope' else dark)
    lens_nodes=[]
    for n,node in opt.assembly(lens_inserted=True).traverse():
        if node.obj is None or n not in ('metal_angle','upright','lens_cassette','lens_retainer','Raynox_envelope'):continue
        a.add(node.obj,name=n,loc=cq.Location(cq.Vector(160,330,0))*node.loc,
              color=blue if n=='Raynox_envelope' else coral);lens_nodes.append(n)
    scenes['camera-startup']=(a,dict(cam=(1,-1,.75),size='2400x1800'))
    details['camera-startup']=dict(removed_complete_module=lens_nodes,exploded_offsets_mm={'lens_module':[160,330,0]})
    # Rail stop fabrication receives an isolated close view, separate from the
    # broad assembly picture so its fork and upper bridge can be inspected.
    a=cq.Assembly(name='guide-camera-stop-detail')
    a.add(opt.PARTS['camera-rail-stop']['model'],name='camera-rail-stop',color=coral)
    scenes['camera-stop-detail']=(a,dict(cam=(1,-1,.7),size='2400x1500'))
    details['camera-stop-detail']=dict(fabrication_parts=['camera-rail-stop'])
    return scenes,details


def hashes(paths):
    return {str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}


def render_scenes(scenes,details,input_hashes,wanted=None):
    os.environ.setdefault("HSM_NO_BUILD_LOCK","1")
    sys.path.insert(0,str(ROOT/'hardware/scripts'))
    from _cadq_export import _per_solid_color
    names=wanted or list(scenes)
    missing=[n for n in names if n not in scenes]
    if missing:raise ValueError(f"Unknown CAD guide scenes: {missing}")
    def check():
        changed=[p for p,h in input_hashes.items() if hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
        if changed:raise RuntimeError(f'Geometry changed during guide rendering: {changed}')
    check()
    OUT.mkdir(parents=True,exist_ok=True)
    ART.mkdir(parents=True,exist_ok=True)
    stage=OUT/'steps'
    stage.mkdir(exist_ok=True)
    jobs=[]
    for name in names:
        assy,settings=scenes[name]
        # Project the assembly bounds onto this view. A world-axis maximum
        # alone can crop a posed exploded stack at its corners.
        bb=assy.toCompound().BoundingBox()
        direction=settings['cam']
        norm=math.sqrt(sum(v*v for v in direction));d=[v/norm for v in direction]
        reference_up=settings.get('up',[0,0,1])
        right=[d[1]*reference_up[2]-d[2]*reference_up[1],
               d[2]*reference_up[0]-d[0]*reference_up[2],
               d[0]*reference_up[1]-d[1]*reference_up[0]]
        rn=math.sqrt(sum(v*v for v in right));right=[v/rn for v in right]
        up=[right[1]*d[2]-right[2]*d[1],right[2]*d[0]-right[0]*d[2],right[0]*d[1]-right[1]*d[0]]
        # The sign of the corrected up vector does not affect its span.
        extent=[bb.xlen,bb.ylen,bb.zlen]
        projected_w=sum(abs(v)*s for v,s in zip(right,extent))
        projected_h=sum(abs(v)*s for v,s in zip(up,extent))
        viewport_w,viewport_h=map(float,settings['size'].split('x'))
        span=max(projected_h,projected_w/(viewport_w/viewport_h))*.56
        step=stage/f'{name}.step'
        _per_solid_color(assy).export(str(step))
        jobs.append(dict(step=str(step.relative_to(ROOT/'hardware')),out=str(ART/f'{name}.png'),
                         cam=list(settings['cam']),up=list(reference_up),size=settings['size'],bg='#ffffff',
                         span=span,
                         trim=False,solid=True,ortho=True,ground=False,fog=False,transparent=True))
        details[name]['orthographic_half_height_mm']=span
        print(f"Staged CAD scene: {name}",flush=True)
    subprocess.run(['node',str(ROOT/'tools/render/render-step-posed.js'),'--jobs','-'],
                   cwd=ROOT,input=json.dumps(jobs),text=True,check=True,timeout=1200)
    check()
    receipt_path=ART/'scene-receipt.json'
    receipt=json.loads(receipt_path.read_text()) if receipt_path.exists() else dict(scenes={})
    receipt['source_files']=sorted(set(receipt.get('source_files',[]))|set(input_hashes))
    receipt['scenes'].update({n:dict(**details[n],input_sha256=input_hashes,
                                   png_sha256=hashlib.sha256((ART/f'{n}.png').read_bytes()).hexdigest()) for n in names})
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')


def render_mechanics(wanted=None):
    inputs=hashes([MECHANICS,OPTICS,Path(__file__).resolve()])
    scenes,details=mechanical_scenes()
    render_scenes(scenes,details,inputs,wanted)


def render_camera(wanted=None):
    inputs=hashes([OPTICS,Path(__file__).resolve()])
    scenes,details=camera_scenes()
    render_scenes(scenes,details,inputs,wanted)


def render_controller(wanted=None):
    inputs=hashes([MOUNTING,MOUNTING.with_name('manifest.json'),Path(__file__).resolve()])
    scenes,details=controller_scenes()
    render_scenes(scenes,details,inputs,wanted)


class SVG:
    def __init__(self, width=2000, height=960):
        self.width, self.height = width, height
        font=base64.b64encode((ROOT/'hardware/guide-assets/fonts/IBMPlexSans-400-700-normal-latin.woff2').read_bytes()).decode()
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                      '<style>@font-face{font-family:"IBM Plex Sans";font-weight:400 700;src:url(data:font/woff2;base64,'+font+') format("woff2")}</style>',
                      '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="9" markerHeight="9" orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 Z" fill="#1749d1"/></marker></defs>']

    def box(self, x, y, w, h, label=None, fill=STEEL, color=INK, size=40):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{fill}" stroke="{color}" stroke-width="3"/>')
        if label:
            lines = label.split("\n")
            for i, line in enumerate(lines):
                self.text(line, x + w/2, y + h/2 + (i-(len(lines)-1)/2)*size*1.25 + size*.35,
                          size=size, anchor="middle", color=color)

    def text(self, value, x, y, *, size=34, color=INK, anchor="start", weight=400):
        size=max(34,size)
        self.parts.append(f'<text x="{x}" y="{y}" font-family="IBM Plex Sans, Arial, sans-serif" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{html.escape(str(value))}</text>')

    def line(self, points, color=BLUE, width=6, arrow=False, dash=False):
        path = " ".join(("M" if i == 0 else "L") + f" {x} {y}" for i,(x,y) in enumerate(points))
        self.parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"'+
                          (' marker-end="url(#arrow)"' if arrow else '')+
                          (' stroke-dasharray="12 12"' if dash else '')+'/>')

    def dot(self, x, y, color=BLUE, radius=8):
        self.parts.append(f'<circle cx="{x}" cy="{y}" r="{radius}" fill="{color}"/>')

    def save(self, name):
        ART.mkdir(parents=True, exist_ok=True)
        (ART / f"{name}.svg").write_text("\n".join(self.parts + ["</svg>"]) + "\n")


def visual_key():
    s = SVG(2000, 800)
    for x, color, title, desc in [
        (80, CORAL, "ADD THIS", "The part installed on this page"),
        (720, INK, "ALREADY BUILT", "The parts holding it in place"),
        (1360, BLUE, "CHECK THIS", "A tool, gauge or reference"),
    ]:
        s.box(x, 130, 560, 260, fill=color, color=color)
        s.text(title, x+280, 470, anchor="middle", size=42, weight=700, color=color)
        words = desc.split()
        half = math.ceil(len(words)/2)
        s.text(" ".join(words[:half]), x+280, 530, anchor="middle", size=30)
        s.text(" ".join(words[half:]), x+280, 575, anchor="middle", size=30)
    s.text("Pictures show the assembly. Dimensions and part IDs govern the build.", 1000, 710,
           size=35, anchor="middle", color=MUTED)
    s.save("visual-key")


def force_fixture():
    s=SVG(2000,1160)
    s.text('Gauge backing plate',65,90,size=42,weight=700)
    s.box(110,210,280,440,fill=STEEL,color=INK)
    for dx in(-82,82):
        for dy in(-146,146):
            s.parts.append(f'<circle cx="{250+dx}" cy="{430+dy}" r="9" fill="white" stroke="{INK}" stroke-width="3"/>')
    s.text('70 × 110 × 6.35 mm',65,720,size=40,weight=700)
    s.text('4 × Ø4.5 / 41 × 73 mm',65,780,size=38)
    s.text('Supplied rear M4 screws',65,840,size=37,color=MUTED)
    s.box(665,70,420,130,'Unpowered drill quill\nFlat metal pusher',fill=PALE,size=37)
    s.line([(875,200),(875,270)],color=BLUE,arrow=True)
    s.box(725,280,300,100,'Output shuttle',fill='#ffe5e8',color=CORAL,size=39)
    s.line([(875,380),(875,430)],color=BLUE,arrow=True)
    s.box(700,440,350,110,'Opposed springs',fill=STEEL,size=37)
    s.line([(875,550),(875,600)],color=BLUE,arrow=True)
    s.box(650,610,450,125,'Fixed cage only\nMetal test platen',fill=STEEL,size=37)
    s.line([(875,735),(875,785)],color=BLUE,arrow=True)
    s.box(780,800,190,80,'M6 head',fill=PALE,size=36)
    s.box(690,900,370,175,'500 N gauge\nVertical body',fill=PALE,size=44)
    s.text('LOAD AXIS UP',875,1128,size=39,anchor='middle',color=BLUE,weight=700)
    s.box(1240,270,700,200,'Pusher contacts the shuttle only.\nNo platen bridges it to the cage.',fill=PALE,size=37)
    s.box(1240,630,700,210,'Gauge reads the cage reaction.\nBacking plate is held vertically\nin the drill vise.',fill=PALE,size=37)
    s.text('Schematic path; CAD sets attachments.',1240,970,size=35,color=MUTED)
    s.text('Reverse the link for the opposite direction.',1240,1040,size=35,color=MUTED)
    s.save('force-fixture')


def spring_grade():
    s=SVG(2000,930)
    s.box(100,80,630,125,'Unpowered quill / upper platen',fill=PALE,size=40)
    s.line([(415,205),(415,280)],color=BLUE,arrow=True)
    s.box(150,290,530,275,'Received spring or pair\nParallel metal seats\nGuarded compression',fill='#ffe5e8',color=CORAL,size=42)
    s.line([(415,565),(415,630)],color=BLUE,arrow=True)
    s.box(160,640,510,140,'Gauge / lower metal platen',fill=PALE,size=40)
    s.line([(1000,730),(1850,730)],color=INK,arrow=True)
    s.line([(1000,730),(1000,170)],color=INK,arrow=True)
    s.text('Measured compression / mm',1370,810,size=37,anchor='middle')
    s.text('Force / N',1030,115,size=37)
    s.box(1150,290,740,270,'k = Δforce / Δtravel\nRecord repeated points\nand return after unloading',fill=PALE,size=42)
    s.text('Use the axis / direction preload table after grading the received springs.',70,895,size=38,weight=700)
    s.save('spring-grade')


def stop_power():
    s=SVG(2000,1080)
    s.box(30,315,285,200,'24 V adapter\n+ / -',fill=PALE,size=43)
    s.box(415,335,220,120,'F0 · 5 A',fill=PALE,size=42)
    s.line([(315,395),(415,395)],color=CORAL)
    s.line([(635,395),(680,395),(680,170),(740,170)],color=CORAL)
    s.line([(680,395),(680,770),(740,770)],color=CORAL)
    s.dot(680,395,CORAL)
    s.box(740,110,210,120,'500 mA\ncoil fuse',fill=PALE,size=37)
    s.box(990,100,265,140,'MOTOR POWER\nmaintained toggle',fill=PALE,size=35)
    s.box(1295,110,190,120,'STOP NC1',fill=PALE,size=35)
    s.box(1525,110,230,120,'BREAKAWAY\nCH1',fill=PALE,size=35)
    s.box(1795,110,165,120,'24 V\ncoil',fill=PALE,size=38)
    for x1,x2 in [(950,990),(1255,1295),(1485,1525),(1755,1795)]:s.line([(x1,170),(x2,170)],color=CORAL)
    s.line([(1960,170),(1975,170),(1975,950)],color=INK)
    s.line([(1775,170),(1775,60),(1790,60)],color=INK,width=3)
    s.box(1790,30,170,60,'1N4007',fill=PALE,size=34)
    s.line([(1800,32),(1800,88)],color=INK,width=6)
    s.line([(1960,60),(1975,60),(1975,170)],color=INK,width=3)
    s.text('Diode band → coil +',1330,43,size=35,color=MUTED)
    s.box(740,355,360,150,'Relay COM → NO\n≥24 V DC / 6 A',fill=PALE,size=37)
    s.line([(680,430),(740,430)],color=CORAL);s.dot(680,430,CORAL)
    s.box(1160,370,285,120,'6 × 1 A fuse\none per axis',fill=PALE,size=37)
    s.box(1505,355,430,150,'Six driver VM inputs\nGND → 0 V star',fill=STEEL,size=38)
    s.line([(1100,430),(1160,430)],color=CORAL)
    s.line([(1445,430),(1505,430)],color=CORAL)
    s.line([(1740,505),(1740,550),(1975,550)],color=INK)
    s.dot(1975,550,INK)
    s.box(740,710,240,120,'500 mA\nbuck fuse',fill=PALE,size=38)
    s.box(1060,710,375,120,'24 → 5 V buck',fill=PALE,size=40)
    s.box(1515,685,420,170,'Pico VSYS\nthrough 1N5819',fill=PALE,size=40)
    s.line([(980,770),(1060,770)],color=CORAL)
    s.line([(1435,770),(1515,770)],color=CORAL)
    s.line([(1250,830),(1250,950)],color=INK)
    s.line([(1800,855),(1800,950)],color=INK)
    s.line([(315,470),(350,470),(350,950),(1975,950)],color=INK)
    s.text('Common motor / logic 0 V star',800,920,size=38,weight=700)
    s.box(40,640,590,200,'GP26 → STOP NC2\n→ BREAKAWAY CH2 → GND\nSeparate 3.3 V loop',fill=PALE,size=35)
    s.text('STOP removes motor VM. The unswitched buck keeps controller logic alive.',40,1040,size=37,weight=700)
    s.save("stop-power")


def logic_power():
    s=SVG(2000,1000)
    s.box(50,285,340,190,"Unswitched 24 V\nafter main F0",fill=PALE,size=38)
    s.box(475,305,230,130,'500 mA\nbranch fuse',fill=PALE,size=37)
    s.box(790,280,355,200,"24 → 5 V buck\n≥0.5 A output",fill=STEEL,size=40)
    s.line([(390,370),(475,370)],color=CORAL)
    s.line([(705,370),(790,370)],color=CORAL)
    s.box(1210,305,230,105,"1N5819",fill=PALE,size=38)
    s.line([(1145,350),(1210,350)],color=CORAL)
    s.line([(1423,308),(1423,407)],color=INK,width=7)
    s.line([(1440,350),(1570,350)],color=CORAL)
    s.box(1570,255,390,250,"Pico\nVSYS pin 39\nGND pin 38",fill=PALE,size=38)
    s.text("Band toward VSYS",1190,470,size=37,color=BLUE)
    s.box(1130,40,700,135,"Host USB power + data\nPico Micro-USB",fill=PALE,size=39)
    s.line([(1690,175),(1690,255)],color=BLUE,width=5,arrow=True)
    s.text("Onboard USB diode",1380,226,size=36,color=MUTED)
    s.line([(220,475),(220,695),(1870,695),(1870,505)],color=INK)
    s.line([(950,480),(950,695)],color=INK)
    s.dot(950,695,INK)
    s.text("Common motor / logic 0 V star",710,760,size=42,weight=700)
    s.text("Measure 5.0 V at the buck before connecting the diode and VSYS.",80,870,size=39,weight=700)
    s.text("External 5 V goes to VSYS through the diode. Never connect it to VBUS.",80,945,size=37,color=MUTED)
    s.save("logic-power")


def fan_power():
    s=SVG(2000,860)
    s.box(70,250,405,230,'Switched motor VM\nRelay NO / +24 V',fill=PALE,size=43)
    s.box(610,285,330,160,'FFAN\n500 mA fuse',fill=PALE,size=41)
    s.box(1080,220,780,310,'80 mm / 24 V fan\nCurrent ≤0.2 A\nGuard + six-heatsink crossflow',fill=STEEL,size=40)
    s.line([(475,365),(610,365)],color=CORAL)
    s.line([(940,365),(1080,365)],color=CORAL)
    s.text('+',1120,365,size=46,color=CORAL)
    s.line([(1480,530),(1480,650),(280,650)],color=INK)
    s.text('Fan − → common 0 V star',350,730,size=44,weight=700)
    s.text('Keep blades and intake clear. Cooling is present only with motor VM.',70,820,size=38,color=MUTED)
    s.save('fan-power')


def limits():
    s = SVG(2000, 930)
    s.box(80, 200, 390, 380, "Pico input\nX: GP17\n3.3 V logic", fill=PALE, size=40)
    s.box(640,275,280,220,'Low travel\nCOM / NC',fill=STEEL,size=39)
    s.box(975,275,280,220,'High travel\nCOM / NC',fill=STEEL,size=39)
    s.box(1310,275,280,220,'Force -\nCOM / NC',fill=STEEL,size=39)
    s.box(1645,275,280,220,'Force +\nCOM / NC',fill=STEEL,size=39)
    s.line([(470,390),(640,390)], color=BLUE)
    s.line([(920,390),(975,390)], color=BLUE)
    s.line([(1255,390),(1310,390)],color=BLUE)
    s.line([(1590,390),(1645,390)],color=BLUE)
    s.line([(1925,390),(1960,390),(1960,690),(350,690),(350,580)], color=INK)
    s.text("GND", 1800, 670, size=38)
    s.line([(580,390),(580,125)], color=BLUE)
    s.dot(580,390)
    s.box(470,45,220,80,"10 kΩ", fill=PALE, size=35)
    s.text("3.3 V", 720, 98, size=36)
    s.text("Closed loop = ready; any switch opened or any broken wire = latched stop.", 90, 790,
           size=36, weight=700)
    s.text("Repeat independently: Y GP18  •  Z GP19  •  U GP20  •  V GP21  •  W GP22", 90, 865,
           size=32, color=MUTED)
    s.save("limit-loop")


def logic_stop():
    s=SVG(2000,940)
    s.box(80,250,430,300,"Pico GP26\nphysical pin 31",fill=PALE,size=42)
    s.box(790,300,425,210,"STOP NC2\nCOM → NC",fill=STEEL,size=44)
    s.box(1330,285,530,230,"BREAKAWAY CH2\nAxial COM / NC\nPlate COM / NO",fill=STEEL,size=39)
    s.line([(510,395),(790,395)],color=BLUE)
    s.line([(1215,395),(1330,395)],color=BLUE)
    s.line([(1860,395),(1930,395),(1930,690),(350,690),(350,550)],color=INK)
    s.text("GND",1720,665,size=42)
    s.line([(650,395),(650,180)],color=BLUE)
    s.dot(650,395)
    s.box(550,90,200,90,"10 kΩ",fill=PALE,size=38)
    s.line([(650,90),(650,45)],color=BLUE)
    s.text("3.3 V",785,130,size=40)
    s.text("Ready: stop released; axial NC closed; seated plate holds its NO closed.",90,790,size=37,weight=700)
    s.text("Either crash contact opens the chain. CH2 remains separate from 24 V CH1.",90,865,size=37,color=MUTED)
    s.save("logic-stop")


def uart():
    s = SVG(2000, 960)
    s.box(70, 140, 390, 630, "Pico\nUART0\nGP0 TX\nGP1 RX", fill=PALE, size=44)
    s.box(575, 295, 210, 110, "330 Ω", fill=PALE, size=35)
    green="#178453"
    s.line([(460,350),(575,350)], color=green)
    s.line([(785,350),(900,350)], color=green)
    s.line([(900,200),(900,700)], color=green)
    s.line([(900,200),(900,120)],color=green,width=4)
    s.box(805,45,190,75,"1.8 kΩ",fill=PALE,size=34)
    s.line([(900,45),(900,15)],color=green,width=4)
    s.text("3.3 V",1030,65,size=32,color=BLUE)
    s.line([(460,585),(900,585)], color=green)
    s.dot(900,585,green)
    s.text("TX",425,331,size=29,anchor="end",color=BLUE)
    s.text("RX",425,566,size=29,anchor="end",color=BLUE)
    s.text("Bus A", 830, 725, size=35, color=BLUE, weight=700)
    for y, axis, address in [(110,"X",0),(360,"Y",1),(610,"Z",2)]:
        s.box(1150,y,660,185,f"{axis} TMC2209  •  address {address}\nPDN_UART", fill=STEEL, size=38)
        s.line([(900,y+90),(1150,y+90)], color=green)
        s.dot(900,y+90,green)
    s.text("Duplicate on UART1: GP4 TX through 330 Ω, GP5 RX direct; U/V/W = 0/1/2.", 70, 870,
           size=32, weight=700)
    s.text("Address straps differ within each bus. Use the board's printed pin labels.", 70, 930,
           size=31, color=MUTED)
    s.save("uart-buses")


def stepdir():
    s = SVG(2000, 1060)
    s.box(50,100,360,820,"Pico\n3.3 V outputs",fill=PALE,size=45)
    for i,(axis,step,direction) in enumerate([( "X",2,3),("Y",6,7),("Z",8,9),("U",10,11),("V",12,13),("W",14,15)]):
        y=110+i*132
        s.box(1140,y,760,108,f"{axis}   STEP / DIR / ENN",fill=STEEL,size=36)
        s.line([(410,y+30),(790,y+30),(790,y+33),(1140,y+33)],color=BLUE,width=4)
        s.line([(410,y+77),(920,y+77),(920,y+75),(1140,y+75)],color="#7c3aed",width=4)
        s.text(f"GP{step}",460,y+20,size=40,color=BLUE)
        s.text(f"GP{direction}",590,y+107,size=40,color="#7c3aed")
    s.text("STEP is blue; DIR is violet. GP16 fans out to all six ENN pins.",70,982,size=36,weight=700)
    s.text("10 kΩ from the shared ENN node to 3.3 V holds the drivers disabled at boot.",70,1040,size=31,color=MUTED)
    s.save("step-dir")


def adc():
    s=SVG(2000,830)
    s.box(80,270,350,160,"Switched 24 V",fill=STEEL,size=40)
    s.box(560,290,250,120,"100 kΩ",fill=PALE,size=40)
    s.line([(430,350),(560,350)],color=CORAL)
    s.line([(810,350),(970,350),(1260,350)],color=BLUE)
    s.dot(970,350)
    s.box(1260,270,600,160,"Pico GP27 / ADC1",fill=PALE,size=42)
    s.box(850,525,240,100,"10 kΩ",fill=PALE,size=40)
    s.line([(970,350),(970,525)],color=INK)
    s.line([(970,625),(970,690),(1490,690)],color=INK)
    s.box(1290,525,400,100,"100 nF",fill=PALE,size=40)
    s.line([(1200,350),(1490,350),(1490,525)],color=BLUE)
    s.line([(1490,625),(1490,690)],color=INK)
    s.text("GND",1110,750,size=40)
    s.text("24 V at the motor bus produces 2.18 V at GP27.",1000,140,anchor="middle",size=43,weight=700)
    s.text("Meter the divider before connecting GP27. Keep the ADC node below 3.3 V.",1000,210,anchor="middle",size=34,color=MUTED)
    s.save("voltage-divider")


def software_stack():
    s=SVG(2000,1000)
    for x,y,w,h,label in [
        (60,70,1880,180,"Two camera views + timestamps → observed wire / dot / seam"),
        (60,350,840,185,"Host\nlearn response → bounded correction"),
        (1120,350,820,185,"Pico\nlimits + stop + watchdog + DDA"),
        (1120,680,820,185,"Six stepper drives\nX Y Z + U V W"),
        (60,680,840,185,"Actual loaded mechanism\nmove → settle → observe"),
    ]:
        s.box(x,y,w,h,label,fill=PALE,size=40)
    s.line([(480,250),(480,350)],arrow=True)
    s.line([(900,445),(1120,445)],arrow=True)
    s.line([(1550,535),(1550,680)],arrow=True)
    s.line([(1120,775),(900,775)],arrow=True)
    s.line([(185,680),(185,275)],arrow=True)
    s.text("Corrections are evaluated from fresh observations after each bounded move.",1000,955,
           anchor="middle",size=34,weight=700)
    s.save("software-stack")


def software_banner():
    s=SVG(2000,390)
    for x,w,label in [(30,560,'Observe / log'),(720,560,'Bound one request'),(1410,560,'Move / settle')]:
        s.box(x,90,w,180,label,fill=PALE,size=56)
    s.line([(590,180),(720,180)],arrow=True)
    s.line([(1280,180),(1410,180)],arrow=True)
    s.text('Fresh evidence precedes the next correction.',1000,355,anchor='middle',size=44,weight=700)
    s.save('software-banner')


def backplane():
    s=SVG(2000,1000)
    s.box(60,70,1880,750,fill=PALE)
    s.box(140,200,380,400,'Headered Pico\nterminal adapter\n3.3 V signals',fill=STEEL,size=42)
    for i,axis in enumerate('XYZ'):
        s.box(700,145+i*195,405,145,axis+' carrier / UART A',fill=STEEL,size=40)
    for i,axis in enumerate('UVW'):
        s.box(1270,145+i*195,405,145,axis+' carrier / UART B',fill=STEEL,size=40)
    s.line([(610,160),(610,675)],dash=True,color=BLUE,width=3)
    s.box(140,720,370,80,'Common 0 V star',fill=PALE,size=35)
    s.box(570,720,420,80,'Motor branch fuses',fill=PALE,size=35)
    s.box(1050,720,380,80,'Relay / coil fuse',fill=PALE,size=35)
    s.box(1490,720,370,80,'Buck / branch fuse',fill=PALE,size=35)
    s.text('Fixed insulated board; separate power routes from UART / GPIO.',1000,900,anchor='middle',size=43,weight=700)
    s.text('Placement map only. Meter each received carrier before driver insertion.',1000,965,anchor='middle',size=37,color=MUTED)
    s.save('control-backplane')


def driver_map():
    s=SVG(2000,1050)
    signals=[('VM','Fused switched 24 V',CORAL),('GND','Common motor 0 V',INK),('VIO','Pico 3V3',BLUE),
             ('GND','Common logic 0 V',INK),('ENN','GP16 + 10 kΩ pull-up',BLUE),('STEP / DIR','One named axis pair',BLUE),
             ('MS1 / MS2','Address straps 0 / 1 / 2',BLUE),('PDN_UART','Assigned shared bus A or B','#178453')]
    for i,(pin,route,color) in enumerate(signals):
        y=55+i*107
        s.box(80,y,510,87,pin,fill=PALE,color=color,size=44)
        s.line([(590,y+43),(920,y+43)],color=color,arrow=True)
        s.box(920,y,970,87,route,fill=STEEL,size=44)
    s.text('Received module ↔ metered carrier socket',1000,960,anchor='middle',size=44,weight=700)
    s.text('Logical names, not physical pin positions. Both sense resistors must be R110.',1000,1020,anchor='middle',size=36,color=MUTED)
    s.save('driver-map')


def motor_pairs():
    s=SVG(2000,920)
    s.box(80,120,390,540,'Unplugged\nbipolar motor',fill=PALE,size=49)
    for i,(label,color) in enumerate([('A1',BLUE),('A2',BLUE),('B1','#7c3aed'),('B2','#7c3aed')]):
        y=160+i*130
        s.line([(470,y),(1120,y)],color=color,width=8)
        s.text(label,590,y-25,size=49,color=color,weight=700)
        s.box(1120,y-48,740,100,label+' → same driver output',fill=STEEL,size=42)
    s.box(510,705,660,110,'A1 ↔ A2: one winding',fill=PALE,color=BLUE,size=43)
    s.box(1220,705,660,110,'B1 ↔ B2: one winding',fill=PALE,color='#7c3aed',size=43)
    s.text('Between pairs and to the motor case: open circuit.',1000,890,anchor='middle',size=43,weight=700)
    s.save('motor-pairs')


def harness_connectors():
    s=SVG(2000,640)
    s.box(80,65,875,320,'GX16-4 / 24 V domain\n6 motor winding pairs\n+ independent crash CH1',fill=STEEL,size=48)
    s.box(1045,65,875,320,'GX12-2 / 3.3 V domain\n6 axis loops + STOP sense\n+ independent crash CH2',fill=PALE,color=BLUE,size=48)
    s.text('CH1 pins 1 / 2: input / coil return',515,460,anchor='middle',size=39,weight=700)
    s.text('CH2 pins 1 / 2: sense / GND return',1485,460,anchor='middle',size=39,weight=700)
    s.text('Different shell sizes prevent cross-mating. Read the actual numbered solder contacts.',1000,585,anchor='middle',size=38,color=MUTED)
    s.save('harness-connectors')


def bypass():
    s=SVG(2000,1000)
    s.line([(100,170),(1900,170)],color=CORAL,width=8)
    s.line([(100,760),(1900,760)],color=INK,width=8)
    s.text('Switched VM +',100,100,size=49,color=CORAL,weight=700)
    s.text('Common 0 V -',100,835,size=49,weight=700)
    for x,top,lower in [(330,'Bulk capacitor','≥470 µF / ≥35 V'),(1000,'Each of six carriers','≥100 µF / ≥35 V')]:
        s.line([(x,170),(x,340)],color=CORAL)
        s.box(x-225,340,450,210,top+'\n'+lower,fill=PALE,size=39)
        s.line([(x,550),(x,760)],color=INK)
        s.text('+',x-60,316,size=50,color=CORAL,weight=700)
        s.text('Striped lead: -',x+30,620,size=37,weight=700)
        s.dot(x,170,CORAL);s.dot(x,760,INK)
    s.box(1450,340,470,210,'Driver VM / GND\nShort local routes',fill=STEEL,size=40)
    s.line([(1685,170),(1685,340)],color=CORAL)
    s.line([(1685,550),(1685,760)],color=INK)
    s.text('Observe polarity. Metering DC voltage does not qualify transients.',1000,950,anchor='middle',size=40,weight=700)
    s.save('local-bypass')


def linear_gauge():
    s=SVG(2000,740)
    s.box(80,430,780,170,'Fixed metal reference',fill=STEEL,size=47)
    s.box(1250,280,600,320,'Rigid moving carriage',fill=PALE,size=46)
    s.box(260,180,590,190,'Existing 12.7 µm\ngraduation indicator',fill=PALE,color=BLUE,size=43)
    s.line([(850,285),(1250,285)],color=BLUE,width=9)
    s.line([(555,370),(555,430)],color=BLUE,width=8)
    s.line([(1250,160),(1660,160)],color=BLUE,arrow=True)
    s.text('5.00 mm nominal span',1330,106,size=43,color=BLUE)
    s.text('Coarse scale screen: ±0.10 mm; align the probe to the travel axis.',1000,690,anchor='middle',size=42,weight=700)
    s.save('linear-gauge')


def angular_law():
    s=SVG(2000,990)
    ox,oy,scale=420,360,2.8
    r,L0=150,180
    def p(x,y):return ox+x*scale,oy-y*scale
    ax,ay=p(r,-L0)
    s.dot(ox,oy,INK,14)
    s.text('Output pivot',100,295,size=45,weight=700)
    for angle,color in [(-20,BLUE),(0,INK),(20,CORAL)]:
        t=math.radians(angle);px,py=p(r*math.cos(t),r*math.sin(t))
        s.line([(ox,oy),(px,py)],color=color,width=8)
        s.line([(ax,ay),(px,py)],color=color,width=5,dash=angle!=0)
        s.dot(px,py,color,10)
        s.text(f'{angle:+d}°',px+30,py+14,size=43,color=color,weight=700)
    s.dot(ax,ay,INK,13)
    s.text('Fixed clevis',ax-40,ay+65,size=42,anchor='end')
    s.text('r = 150 mm',490,286,size=44,weight=700)
    s.text('L0 = 180 mm',880,660,size=44,weight=700)
    s.box(1150,195,790,215,'Positive extension\nincreases the local angle',fill=PALE,size=46)
    s.box(1100,540,850,240,'L² = L0² + 2 L0 r sin θ\n+ 2 r² (1 - cos θ)',fill=PALE,size=42)
    s.text('Nominal geometry; actual pin datums and local response are measured.',1000,960,anchor='middle',size=39,weight=700)
    s.save('angular-law')


def weighed_loads():
    s=SVG(2000,760)
    s.box(75,65,555,200,'Check scale\n0 … 2000 g',fill=PALE,color=BLUE,size=48)
    s.box(725,65,555,200,'Weigh each aliquot\nunder 2 kg',fill=PALE,color=BLUE,size=45)
    s.box(1370,65,555,200,'Sum complete load\ncup + cord + masses',fill=PALE,color=BLUE,size=42)
    s.line([(630,165),(725,165)],arrow=True)
    s.line([(1280,165),(1370,165)],arrow=True)
    s.box(190,365,1620,240,'F = mass_g × 0.00980665 N/g\nAccept the complete [F − U, F + U] interval inside 20 … 30 N',fill=STEEL,size=46)
    s.text('U includes every aliquot, actual redirect loss, cord alignment and the force-step bracket.',1000,700,anchor='middle',size=37,color=MUTED)
    s.save('weighed-loads')


def shaft_end_threads():
    taps=json.loads((ROOT/'hardware/printed-parts/fixtures/gun-positioner/requirements.json').read_text())['fabrication']['shaft_end_threads']
    s=SVG(2000,950)
    # Dimensioned axial section: equal display scale in X and Y, with the
    # remainder of the shaft shortened to show only the blind end features.
    scale=25;end=520;cy=500
    s.parts.append(f'<path d="M{end} {cy-6*scale}h1050v{12*scale}h-1050z" fill="{STEEL}" stroke="{INK}" stroke-width="4"/>')
    full=taps['usable_full_thread_depth_mm']*scale;pilot=taps['pilot_depth_mm']*scale
    s.parts.append(f'<path d="M{end} {cy-2.5*scale}h{full}v{5*scale}h-{full}z" fill="white" stroke="{BLUE}" stroke-width="4"/>')
    s.parts.append(f'<path d="M{end+full} {cy-2.1*scale}h{pilot-full-35}l35 {2.1*scale}l-35 {2.1*scale}h-{pilot-full-35}z" fill="white" stroke="{BLUE}" stroke-width="4"/>')
    keeper=taps['steel_retainer_washer_mm']
    for x,w,od in [(end-keeper['thickness']*scale,keeper['thickness']*scale,keeper['OD']),(end-2.8*scale,.8*scale,10)]:
        s.parts.append(f'<path d="M{x} {cy-od/2*scale}h{w}v{(od-6)/2*scale}h-{w}z M{x} {cy+3*scale}h{w}v{(od-6)/2*scale}h-{w}z" fill="{CORAL}"/>')
    reach=taps['nominal_engagement_mm']*scale
    s.parts.append(f'<path d="M{end-2.8*scale} {cy-2.5*scale}h{reach+2.8*scale}v{5*scale}h-{reach+2.8*scale}z" fill="{PALE}" stroke="{INK}" stroke-width="4"/>')
    s.parts.append(f'<path d="M{end-7.8*scale} {cy-4.25*scale}h{5*scale}v{8.5*scale}h-{5*scale}z" fill="{INK}"/>')
    s.line([(240,cy),(1650,cy)],color=BLUE,width=2,dash=True)
    s.text('M5 × 12 keeper',70,160,size=45,weight=700)
    s.line([(345,185),(345,390)],color=BLUE,arrow=True,width=3)
    s.text(f'OD{keeper["OD"]:g} steel washer: {keeper["thickness"]:g} mm',60,880,size=36,color=CORAL,weight=700)
    s.text('M5 flat washer: 0.8 mm',1040,880,size=36,color=CORAL,weight=700)
    s.line([(end,200),(end+pilot,200)],color=BLUE,width=4)
    s.line([(end,185),(end,215)],color=BLUE,width=3)
    s.line([(end+pilot,185),(end+pilot,215)],color=BLUE,width=3)
    s.text('Ø4.2 pilot / 16 mm depth',end+pilot/2,160,anchor='middle',size=38,color=BLUE,weight=700)
    s.text('M5 × 0.8',1100,375,size=43,weight=700)
    s.text('≥10 mm usable full thread',1100,435,size=35,color=BLUE)
    s.text('9.2 mm nominal screw reach',1100,580,size=38,weight=700)
    s.text('Measure ≥8 mm engagement',1100,635,size=34,color=MUTED)
    s.text('and ≥0.8 mm bottom margin',1100,682,size=34,color=MUTED)
    s.text('Plain 12 mm shaft / axial section',1100,780,size=36,weight=700)
    s.save('shaft-end-threads')


def schematics():
    inputs=hashes([Path(__file__).resolve(),ROOT/'hardware/gun-positioner/wiring-manifest.json',MECHANICS,ROOT/'hardware/printed-parts/fixtures/gun-positioner/requirements.json'])
    for draw in [visual_key,force_fixture,spring_grade, stop_power, logic_power, fan_power, limits, logic_stop, uart, stepdir, adc, software_stack,
                 software_banner,backplane,driver_map,motor_pairs,harness_connectors,bypass,linear_gauge,angular_law,weighed_loads,shaft_end_threads]:
        draw()
    current=hashes([ROOT/p for p in inputs])
    if current!=inputs:raise RuntimeError('Schematic sources changed during authoring')
    (ART/'schematic-receipt.json').write_text(json.dumps(dict(input_sha256=inputs,
        svg_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in ART.glob('*.svg')}),indent=2)+'\n')


if __name__ == "__main__":
    schematics()
    if '--all' in sys.argv:
        render_mechanics()
        render_camera()
        render_controller()
    elif '--camera' in sys.argv:
        names=sys.argv[sys.argv.index('--camera')+1:]
        render_camera(names or None)
    elif '--cad' in sys.argv:
        names=sys.argv[sys.argv.index('--cad')+1:]
        render_mechanics(names or None)
    elif '--controller' in sys.argv:
        names=sys.argv[sys.argv.index('--controller')+1:]
        render_controller(names or None)
