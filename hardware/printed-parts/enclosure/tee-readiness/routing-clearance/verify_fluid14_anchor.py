#!/usr/bin/env python3
"""Read fluid-14 cap bearing/tie stock locally or from an emitted native lid."""
import argparse
from datetime import datetime, timezone
import hashlib
import inspect
import json
import os
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--native-step',type=Path)
    parser.add_argument('--output',type=Path,default=HERE/'fluid14-anchor.json')
    args = parser.parse_args()
    os.environ['HSM_NO_BUILD_LOCK'] = '1'
    sys.path[:0] = [str(ROOT/'hardware/printed-parts/cold-core'),
                    str(ROOT/'hardware/printed-parts/cold-core/foam-cap')]
    import cadquery as cq
    import _cold_core_interface as interface
    import foam_cap
    station = interface.cap_anchors['fluid-14']
    cx,cy = station.centre
    radius = station.seat_r
    reach = radius+interface.cap_anchor_wall
    length = interface.cap_anchor_len
    face = foam_cap.lid_total_height if args.native_step else 0.
    axis_z = face+interface.cap_anchor_axis_over_face('fluid-14')
    if args.native_step:
        solid = cq.importers.importStep(str(args.native_step)).val()
    else:
        # A local lid slab, using the real production appender and its exact current row.
        base = cq.Solid.makeBox(length+4.,2*reach+8.,5.,cq.Vector(cx-length/2-2,cy-reach-4,-5.))
        saved = dict(interface.cap_anchors)
        interface.cap_anchors.clear()
        interface.cap_anchors['fluid-14'] = station
        try:
            solid = foam_cap.add_chain_anchors(cq.Workplane(obj=base),0.).val()
        finally:
            interface.cap_anchors.clear()
            interface.cap_anchors.update(saved)
    rows = []

    def maximum(name,value,limit=1e-5):
        passed = value <= limit
        rows.append({'check':name,'value':value,'maximum':limit,'pass':passed})
        print(('PASS ' if passed else 'FAIL ')+name+f': {value:.8g}',flush=True)

    maximum('lid and rib are one valid native solid',int(not solid.isValid())+abs(len(solid.Solids())-1),0)
    origin = cq.Vector(cx-length/2+.01,cy,axis_z)
    outer = cq.Solid.makeCylinder(reach-.01,length-.02,origin,cq.Vector(1,0,0))
    inner = cq.Solid.makeCylinder(radius+.01,length-.02,origin,cq.Vector(1,0,0))
    lower = cq.Solid.makeBox(length+2,2*reach+2,reach+1,
                            cq.Vector(cx-length/2-1,cy-reach-1,axis_z-reach-1))
    bearing = outer.cut(inner).intersect(lower)
    maximum('complete 3 mm lower bearing annulus retained mm3',bearing.cut(solid).Volume())
    tube = cq.Solid.makeCylinder(radius-interface.fits.slip,length-.02,origin,cq.Vector(1,0,0))
    maximum('actual tube clears the declared anchor bore mm3',tube.intersect(solid).Volume())
    tube_air = tube.distance(solid)
    maximum('native tube-to-bearing air equals declared slip mm',abs(tube_air-interface.fits.slip),1e-5)
    tie_width = interface.cap_anchor_tie_w
    tail = cq.Solid.makeBox(tie_width,2*reach+6,1.,cq.Vector(cx-tie_width/2,cy-reach-3,face+1.))
    maximum('2.5 x 1 mm tie has straight open threading lane mm3',tail.intersect(solid).Volume())
    height = interface.cap_anchor_wall+interface.fits.supported_surface
    tunnel = cq.Solid.makeBox(interface.cap_anchor_cav_w-.02,2*reach+6,height-.02,
        cq.Vector(cx-interface.cap_anchor_cav_w/2+.01,cy-reach-3,face-interface.fits.supported_surface+.01))
    full_void_exit_interference = tunnel.intersect(solid).Volume()
    mouth = cq.Solid.makeBox(interface.cap_anchor_cav_w-.02,2*reach+6,
        interface.cap_anchor_wall-.02,cq.Vector(cx-interface.cap_anchor_cav_w/2+.01,cy-reach-3,face+.01))
    maximum('nominal 3 mm channel mouth is open along its axis mm3',mouth.intersect(solid).Volume())
    room,neighbor = interface.cap_anchor_room('fluid-14')
    maximum('cap footprint preserves required room mm',interface.cap_cradle_room_gap-room,0.)
    record = {'status':'pass' if all(r['pass'] for r in rows) else 'fail',
        'created_at_utc':datetime.now(timezone.utc).isoformat(),
        'scope':('Actual regenerated foam-cap-lid-top STEP, current declared fluid-14 seat, wall stock and tie/support mouth.' if args.native_step else
                 'Exact production add_chain_anchors appender with fluid-14 row on a bounded native lid slab. Full current cap and G-pump neighbors are checked during coordinated assembly regeneration.'),
        'assembly_current':False,'production_print_released':False,
        'station':station._asdict(),'lid_outer_face_z_mm':face,'axis_height_over_face_mm':axis_z-face,
        'native_step':str(args.native_step.resolve()) if args.native_step else None,
        'native_step_sha256':hashlib.sha256(args.native_step.read_bytes()).hexdigest() if args.native_step else None,
        'anchor_length_mm':length,'bearing_web_mm':interface.cap_anchor_wall,
        'native_tube_air_mm':tube_air,
        'tie_channel_mm':{'width':interface.cap_anchor_cav_w,'height':height},
        'shortest_closed_tie_loop_mm':interface.cap_anchor_tie_loop('fluid-14'),
        'footprint_room_mm':room,'footprint_neighbor':neighbor,
        'source_sha256':{str(Path(p).relative_to(ROOT)):hashlib.sha256(Path(p).read_bytes()).hexdigest()
                         for p in (__file__,interface.__file__,foam_cap.__file__)},
        'native_builder_sha256':hashlib.sha256(inspect.getsource(foam_cap.add_chain_anchors).encode()).hexdigest(),
        'checks':rows,
        'support_access':{'mouth_axis':'cap local Y / world X',
            'mouth_height_mm':interface.cap_anchor_wall,
            'recessed_floor_step_at_mouth_mm':interface.fits.supported_surface,
            'full_native_void_extraction_probe_overlap_mm3':full_void_exit_interference,
            'full_native_void_has_straight_exit':full_void_exit_interference <= 1e-5,
            'removal_state':'Separate cap before water-pump, fitting or tube installation.',
            'actual_slice_bodies_reviewed':False,'physical_cleanup_tested':False,
            'limit':'A plug filling the entire 3.25 mm void meets the 0.25 mm exterior floor ledge. Actual connected support bodies must fit the 3 mm mouth after separation/lift; native mouth clearance alone does not qualify removal.'}}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(record,indent=2)+'\n')
    if not all(r['pass'] for r in rows):
        raise ValueError('Native cap-anchor checks failed')


if __name__ == '__main__':
    main()
