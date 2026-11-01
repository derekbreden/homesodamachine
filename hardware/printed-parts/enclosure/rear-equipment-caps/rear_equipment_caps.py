"""Four removable snap caps for the rear inlet equipment."""
import json
import math
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = next(p for p in HERE.parents if p.name=='hardware')
sys.path[:0] = [str(HW/'manifold-layout'),str(HW/'scripts'),str(HW/'printed-parts/cadlib')]
sys.path.insert(0, str(HW/'printed-parts/cold-core'))
if __name__=='__main__':
    import _rust_part
    _rust_part.start()

import cadquery as cq
import rear_plumbing
from _cadq_export import export_assembly
from _materials import M_PETGF_BLACK, linear, one_body

NAMES = ('asse-snap-cap','pisco-snap-cap','meter-snap-cap','regulator-snap-cap')


def printable(name):
    shape = rear_plumbing.seats()[name]
    if name=='meter-snap-cap':
        shape = shape.rotate((0,0,0),(0,1,0),-90.)
    bounds = shape.BoundingBox()
    return shape.translate((-(bounds.xmin+bounds.xmax)/2.,
                            -(bounds.ymin+bounds.ymax)/2.,-bounds.zmin))


def _world_bounds(frame, lo, hi):
    import above_core as layout
    points = [layout.point(frame,(x,y,z)) for x in (lo[0],hi[0])
              for y in (lo[1],hi[1]) for z in (lo[2],hi[2])]
    return (tuple(min(p[k] for p in points) for k in range(3)),
            tuple(max(p[k] for p in points) for k in range(3)))


def numbers():
    """Live snap stock, fits and poses around reference-local measured cap clearances."""
    import above_core as layout
    import above_core_parts as parts
    import rear_snaps as snaps
    import fits
    profiles = json.loads((HW/'printed-parts/enclosure/enclosure/rear-seat-profiles.json').read_text())
    cap_profiles = json.loads((HERE/'rear-cap-profiles.json').read_text())
    datums, plan = rear_plumbing.snap_datums(), rear_plumbing.plan()
    bfp = rear_plumbing.chain().bfp
    c,s = fits.running,fits.slip

    def runs(rows, frame, air):
        t = frame['translation_mm'][1]
        return [(t-hi,t-lo,r+air) for lo,hi,r in reversed(rows)]

    def box(x0,x1,y0,y1,z0,z1):
        return {'op':'box','bounds':(x0,x1,y0,y1,z0,z1)}

    def turned(rows, axis):
        return {'op':'turned','profile':rows,'axis':axis}

    axis,frame = datums['asse_axis'],plan['chain_frame']
    seat = runs(profiles['asse']['seat_runs'],frame,c)
    bonnet = max(x for x,r in bfp.CAP_PROFILE if r==max(r for _,r in bfp.CAP_PROFILE))
    cap_y = (layout.point(frame,(bonnet,0.,bfp.BODY_CENTER_Z))[1]-s,
             layout.point(frame,(cap_profiles['asse']['gagira_fore_x'],0.,bfp.BODY_CENTER_Z))[1]-s)
    wrenches = []
    for profile,across,clock in ((bfp.BODY_PROFILE,bfp.HEX_ACROSS_FLATS,.3),
                                 (bfp.CAP_PROFILE,bfp.CAP_ACROSS_FLATS,.9)):
        y = sorted(layout.point(frame,(x,0.,bfp.BODY_CENTER_Z))[1]
                   for x in (profile[0][0],profile[-1][0]))
        wrenches.append((y,across/2.,clock+datums['asse_turn'],max(r for _,r in profile)))
    widest = max(*(r for y0,y1,r in seat if y1>=cap_y[0]-.25 and y0<=cap_y[1]+.25),
                 *(corner+c for *_,corner in wrenches))
    split = axis[1]+c
    st = snaps.station(axis[0],snaps.half_width(widest,split,axis[1])+snaps.WALL,
                       *cap_y,split=split,wing_root=axis[1])
    cuts = [turned(runs(cap_profiles['asse']['cap_runs'],frame,s),axis)]
    for (y0,y1),apothem,clock,corner in wrenches:
        radius = (apothem+s)/math.cos(math.pi/6)
        points = [(axis[0]+radius*math.sin(math.radians(clock+60*i)),
                   axis[1]-radius*math.cos(math.radians(clock+60*i))) for i in range(6)]
        cuts.append({'op':'hex','points':points,'axis':axis,'corner':corner+s,
                     'span':(math.floor((y0-snaps.THREAD)*10.)/10.,
                             math.ceil((y1+snaps.THREAD)*10.)/10.)})
    lo,hi = _world_bounds(layout.pose('asse1022-assembly'),
                          *cap_profiles['asse']['vent_bounds'])
    cuts.append(box(lo[0]-c,hi[0]+c,lo[1]-snaps.THREAD-c,hi[1]+snaps.THREAD+c,
                    lo[2]-1.,axis[1]))
    adapter = parts._module('rear_cap_vent_adapter','printed-parts/asse-drain-adapter/asse_drain_adapter.py')
    rb = math.sqrt(adapter.BARB_OD**2+bfp.VENT_D**2-adapter.BARB_BORE**2)/2.
    rt = math.sqrt(adapter.TUBE_OD**2+4.**2-adapter.TUBE_BORE**2)/2.
    tip = bfp.vent()[0]
    sleeve_lo = (tip[0]-adapter.ELBOW_REACH,tip[1]-rb,tip[2]-adapter.SOCKET_DROP-rt)
    sleeve_hi = (tip[0]+rb,tip[1]+rb,tip[2]+adapter.INSTALLED_REACH)
    lower,upper = _world_bounds(layout.pose('asse1022-assembly'),sleeve_lo,sleeve_hi)
    cuts.append(box(min(lower[0],lo[0])-c,max(upper[0],hi[0])+c,
                    min(lower[1],lo[1]-snaps.THREAD)-c,
                    max(upper[1],hi[1]+snaps.THREAD)+c,lower[2]-1.,axis[1]))
    caps = [{'name':'asse-snap-cap','section':snaps.cap_section(st,axis[1],None,axis[1],True),
             'cuts':cuts}]

    axis,frame = datums['pisco_axis'],plan['gas_frame']
    seat = runs(profiles['pisco']['seat_runs'],frame,c)
    dims = json.loads((HW/'reference/compact-inline-candidates/dimensions.json').read_text())['pisco_rvfup_quarter']
    ranges,profile = dims['fitted_exterior']['component_ranges_mm'],dims['fitted_exterior']['profile_z_radius_mm']
    fitting,collet = ranges['outlet_fitting'],ranges['outlet_collet']
    neck_z = next(z for z,r in profile if z>fitting[0] and r<6.5)
    cap_y = (datums['mouth_y']-collet[0]+c+.01,datums['mouth_y']-fitting[0]-2.6)
    widest = max(r for y0,y1,r in seat if y1>=cap_y[0]-.25 and y0<=cap_y[1]+.25)
    st = snaps.station(axis[0],snaps.half_width(widest,snaps.SPLIT,axis[1])+snaps.WALL,
                       *cap_y,wing_root=axis[1])
    body_r = max(r for z,r in profile if datums['mouth_y']-cap_y[1]-1.<=z<=neck_z)+s
    neck_r = max(r for z,r in profile if z>neck_z)+c
    lip = datums['mouth_y']-neck_z-s
    cuts = [turned([(cap_y[0]-1.,lip,neck_r),(lip,cap_y[1]+1.,body_r)],axis)]
    caps.append({'name':'pisco-snap-cap',
                 'section':snaps.cap_section(st,axis[1],axis[1]-body_r-snaps.WALL,axis[1]),
                 'cuts':cuts})

    meter = rear_plumbing.reference('cap_digiten','reference/digiten-flow-sensor/digiten_flow_sensor.py')
    frame = layout.pose('digiten-flow')
    def at(point):
        return layout.point(frame,point)
    centre,port = at((meter.body_center_x,0.,meter.body_center_z)),at((0.,0.,0.))
    my,mz = centre[1],centre[2]
    soda = (port[0],port[2])
    def wx(y):
        return at((meter.body_center_x,y,meter.body_center_z))[0]
    def wy(x):
        return at((x,0.,0.))[1]
    mx = wx(7.3)-c
    seat_y,cap_y = (386.,446.),(397.,435.)
    collar = max(meter.port_collar_radii)
    core,west = wx(meter.boss_y_range[0])-s,wx(meter.underside_y)
    st = snaps.station(0.,soda[1]+collar+c-mz+snaps.WALL,
                       *cap_y,split=0.,wing_root=core-mx)
    cuts = [{'op':'stadium-x','centre':(my,mz),'radius':15.45+s,'fore':0.,'aft':snaps.VAR,
             'span':(wx(-8.1),core+1.)},
            {'op':'stadium-x','centre':(my,mz),'radius':15.1+s,'fore':0.,'aft':snaps.VAR,
             'span':(west-s,wx(-8.1)+.01)},
            {'op':'cylinder-y','centre':soda,'radius':meter.port_neck_radius+s,'span':seat_y}]
    slot_aft = wy(meter.wire_root_width/2.)+snaps.VAR+c+.75
    cuts.append(box(core,mx+10.,cap_y[0]-7.,slot_aft,mz-st['outer']-1.,mz-st['hook']+.1))
    row = next(r for r in parts._grid() if r['name']=='bulkhead-flavor-a')
    source = parts._grid_module(row)
    mouth = source.port(-1.)[0]
    destination = (row['x']+mouth[0],row['flange_y']+mouth[1],row['z']+mouth[2])
    cuts.append({'op':'sweep','radius':2.5,'segments':rear_plumbing._flavor_rear('a',destination)})
    cuts.append(box(71.25,80.,396.,403.75,260.,267.))
    caps.append({'name':'meter-snap-cap',
                 'section':snaps.cap_section(st,core-mx,west-s-snaps.WALL-mx),
                 'placement':{'rotate_y':90.,'translation':(mx,0.,mz)},
                 'cuts':cuts,'print_rotate_y':-90.})

    mount = plan['regulator_mount']
    st,axis = mount['station'],mount['axis']
    caps.append({'name':'regulator-snap-cap',
                 'section':snaps.cap_section(st,axis[1],mount['cap_bottom'],axis[1]),
                 'cuts':[turned(mount['cap_runs'],axis)],'rotate_z':90.})
    return {'caps':caps,'color':linear(M_PETGF_BLACK)}


def main():
    import _rust_part
    result = _rust_part.cut('enclosure-components','rear-equipment-caps',numbers(),HERE)
    for file in result['files']:
        print(f'-> {file}',flush=True)


if __name__=='__main__':
    main()
