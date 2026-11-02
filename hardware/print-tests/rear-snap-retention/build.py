"""Export full object-fit receivers and caps from the five production snap families."""
from pathlib import Path
import argparse
import hashlib
import json
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path[:0] = [str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/cadlib'),
               str(ROOT/'hardware/printed-parts/cold-core'),str(ROOT/'hardware/manifold-layout')]
import cadquery as cq
import above_core
import above_core_parts as refs
import _above_core_mounts as mounts
import rear_plumbing
import rear_snaps as snaps
from _cadq_export import export_step
from print_mesh import write_print_stl


def centered(shape):
    b = shape.BoundingBox()
    return shape.translate((-(b.xmin+b.xmax)/2.,-(b.ymin+b.ymax)/2.,-b.zmin))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,default=HERE/'v2')
    parser.add_argument('--check-fit',action='store_true')
    args=parser.parse_args()
    output=args.output.resolve()
    began = time.monotonic()
    folder = output/'parts'
    folder.mkdir(parents=True,exist_ok=True)
    report = {'reference':{'physical_result':'Reinforced revision for the failed PISCO and meter trial; physical fit pending.',
      'leaf_mm':snaps.WING,'flat_overlap_mm':snaps.REACH,'hook_mm':snaps.HOOK,
      'default_leaf_length_mm':snaps.FREE_LENGTH,'regulator_leaf_length_mm':21.5,
      'catch_gap_mm':snaps.CATCH,'hook_nose_land_mm':snaps.NOSE_LAND},
      'scope':'Full object-fit trial seats and caps. Physical retention, insertion force, fatigue and pump vibration remain to be tested.',
      'families':{},'parts':[]}

    def export(name,shape,pose):
        assert shape.isValid() and len(shape.Solids())==1,(name,len(shape.Solids()))
        step,stl=folder/(name+'.step'),folder/(name+'.stl')
        export_step(shape,str(step))
        mesh=write_print_stl(shape,stl)
        assert mesh.is_watertight,name
        row={'name':name,'stl':str(stl.relative_to(ROOT)),'step':str(step.relative_to(ROOT)),
          'stl_sha256':hashlib.sha256(stl.read_bytes()).hexdigest(),
          'bounds_mm':mesh.bounds.tolist(),'volume_mm3':shape.Volume(),
          'valid':True,'solids':1,'watertight':True,'print_orientation':pose}
        report['parts'].append(row)
        print(json.dumps(row),flush=True)

    def family(name,seat,cap,on,station):
        overlap=seat.intersect(cap).Volume()
        pulled=cap.translate(tuple(-(snaps.CATCH+.1)*v for v in on))
        obstruction=seat.intersect(pulled).Volume()
        assert overlap<1.e-5,(name,'seated intersection',overlap)
        assert obstruction>1.,(name,'no empty-cap retention',obstruction)
        report['families'][name]={'station':station,'seated_intersection_mm3':overlap,
          'removal_direction':[-v for v in on], 'pullout_travel_mm':snaps.CATCH+.1,
          'blocked_pullout_intersection_mm3':obstruction,
          'effective_horizontal_bearing_mm2':obstruction/.1,
          'physical_result':'Awaiting this fit trial.'}
        if args.check_fit:
            names={'pump':('g-ganen-pump',),'asse':('bulkhead-water','gagira-coupling','asse1022-assembly','jg-pi4512f6s','jg-pp061208w'),
                   'pisco':('gas-regulator','co2-inlet','gas-check'),'meter':('digiten-flow',),
                   'regulator':('flow-regulator',)}[name]
            objects=refs.components()
            fitted={}
            for key in names:
                shape=objects[key][0]
                pair={'receiver_mm3':seat.intersect(shape).Volume(),'cap_mm3':cap.intersect(shape).Volume()}
                assert max(pair.values())<1.e-4,(name,key,pair)
                fitted[key]=pair
            report['families'][name]['installed_hardware_overlap']=fitted
            if name=='meter':
                shape=objects['digiten-flow'][0]
                slide={str(travel):seat.intersect(shape.translate((0.,-travel,0.))).Volume() for travel in (0.,4.,8.,12.,16.)}
                assert max(slide.values())<1.e-4,('meter insertion',slide)
                report['families'][name]['forward_insertion_overlap_mm3']=slide

    d=mounts.pump_cradle_datums()
    cx=d['centre_world_mm'][0];fy=d['frame']['translation_mm'][1]
    selected=d['selected'];first,last=selected['motor_band_native_x_mm']
    face=above_core.specification()['cap_face_z_mm']
    xa,xb=cx-d['stock_half_width_mm']-3.,cx+d['stock_half_width_mm']+3.
    ya=fy+min(first,min(p[0] for p in selected['rail_stop_native_x_mm']))-3.
    yb=fy+max(last,max(p[1] for p in selected['rail_stop_native_x_mm']))+3.
    plate=snaps.box(xa,xb,ya,yb,face-7.4,face)
    seat=plate.fuse(mounts.pump_cradle()).cut(mounts.pump_lid_clearance()).clean()
    cap=mounts.pump_snap_cap()
    family('pump',seat,cap,(0.,0.,-1.),d['snap_station'])
    report['pump_rail']={'front_projection_beyond_rear_mm':1.,
      'front_to_lid_air_mm':d['frame']['translation_mm'][2]+3.2105828415973967-face+selected['cover_channel_recess_mm'],
      'pump_origin_z_mm':d['frame']['translation_mm'][2]}
    export('pump-seat',centered(seat),'Production lid orientation, flat 7.4 mm root plate down.')
    export('pump-cap',mounts.pump_snap_printable(),'Production pump cap orientation, axial end down.')
    print('Building rear object seats',flush=True)
    parts=rear_plumbing.seats()
    for name in ('asse','pisco','regulator','meter'):
        seat,cap=parts[name+'-seat'],parts[name+'-snap-cap']
        # The parent roof or side wall joins the entire seat's root face.
        b=seat.BoundingBox()
        if name=='meter':
            root=snaps.box(98.4,101.5,b.ymin,b.ymax,b.zmin,b.zmax)
        else:
            root=snaps.box(b.xmin,b.xmax,b.ymin,b.ymax,346.,349.5)
        seat=seat.fuse(root).clean()
        station=rear_plumbing.plan()['regulator_mount']['station'] if name=='regulator' else None
        family(name,seat,cap,(1.,0.,0.) if name=='meter' else (0.,0.,1.),station)
        export(name+'-seat',centered(seat.rotate((0,0,0),(0,1,0),180.)),
               'Production back-top orientation, appliance -Z is print +Z; integral roof/side-wall root retained.')
        export(name+'-cap',rear_plumbing.printable_cap(name+'-snap-cap',cap),
               'Production end-down cap orientation; spring bending stays in the layer plane.')
    inputs=['hardware/manifold-layout/rear_snaps.py','hardware/manifold-layout/rear_plumbing.py',
      'hardware/manifold-layout/above-core.json','hardware/printed-parts/cold-core/_above_core_mounts.py',
      'hardware/reference/g-ganen-pump/reference-parameters.json']
    report['input_sha256']={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in inputs}
    report['elapsed_seconds']=time.monotonic()-began
    (output/'geometry.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Exported all ten printable pieces',flush=True)


if __name__=='__main__':
    main()
