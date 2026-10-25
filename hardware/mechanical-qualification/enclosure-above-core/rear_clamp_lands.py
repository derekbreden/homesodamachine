"""Manual native reading of the six selected rear fitting clamping lands.

Read the actual back-top STEP and six exported identification chips, with
the selected native fitting/nut builders and port frames. No producer,
hook or recurring check invokes this reader. Run through the CAD queue.
This measures nominal geometry, not thread form, tightening, load or sealing.
"""
import argparse
import hashlib
import json
from pathlib import Path
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
HW = ROOT/'hardware'
sys.path[:0] = [str(HW/'manifold-layout'), str(HW/'scripts')]
import above_core as layout
import above_core_parts as parts

TOL_MM3 = .001
FACE_PROBE_MM = .05


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def volume(shape):
    return 0. if shape.isNull() else abs(shape.Volume())


def signature(shape):
    b = shape.BoundingBox()
    return {'valid': shape.isValid(), 'solids': len(shape.Solids()),
        'faces': len(shape.Faces()), 'volume_mm3': volume(shape),
        'bounds_mm': [getattr(b,k) for k in ('xmin','ymin','zmin','xmax','ymax','zmax')]}


def face_at_y(shape, y):
    return max((f for f in shape.Faces() if f.geomType() == 'PLANE'
        and f.BoundingBox().ylen < 1.e-5 and abs(f.Center().y-y) < 1.e-5),
        key=lambda f:f.Area())


def projected(face, depth):
    return cq.Solid.extrudeLinear(face.outerWire(),face.innerWires(),cq.Vector(0.,depth,0.))


def cylinder(radius, x, z, y0, y1):
    return cq.Solid.makeCylinder(radius,y1-y0,cq.Vector(x,y0,z),cq.Vector(0.,1.,0.))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--back-top',type=Path,
        default=HW/'printed-parts/enclosure/enclosure/enclosure-back-top.step')
    parser.add_argument('--output',type=Path,default=HERE/'rear-clamp-lands.json')
    args=parser.parse_args()
    args.back_top=args.back_top.resolve()
    shell=cq.importers.importStep(str(args.back_top)).val()
    spec=layout.specification()
    plan=spec['rear_wall']['interior_panel_relief']
    ports={p['name']:p for p in spec['rear_wall']['wet_ports']}
    result={'scope':__doc__.strip(),
        'back_top':{'path':str(args.back_top.relative_to(ROOT)),
                    'sha256':sha(args.back_top),'signature':signature(shell)},
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (
            Path(__file__),Path(parts.__file__),HW/'manifold-layout/above-core.json')},
        'selected_planes_world_y_mm':{'flange':plan['flange_seat_y_mm'],
            'nut':plan['nut_seat_y_mm']},
        'selected_total_clamp_mm':plan['retained_panel_mm'],
        'volume_tolerance_mm3':TOL_MM3,'face_probe_mm':FACE_PROBE_MM,'ports':{},
        'limits':['The native wall and exported chips are the representations read; '
                  'this is not a printed-STL, torque, thread-engagement or lifetime qualification.',
                  'Fitting exterior subdivisions, PP1208E barrel/nut dimensions and operating '
                  'collet planes retain their documented nominal-reference estimates. '
                  'NeoFit A/E dimensions have the published manufacturer basis in their references.',
                  'No exterior recess or fitting/chip/nut/port pose is changed.']}
    for row in parts._grid():
        name=row['name']; x,z=row['x'],row['z']
        source=parts._grid_module(row)
        if row['native_kind']=='gas':
            native=source.build_neofit_bulkhead().val()
            thread_span=source.PANEL_THREAD+source.NUT_LEN
            basis='Manufacturer A panel span plus E nut width; external mouth division is nominal.'
        elif row['native_kind']=='quarter':
            native=parts.pp1208e_bulkhead()
            thread_span=source.THREAD_LEN
            basis='Selected PP1208E production adapter; nominal reference thread span, not a measured PP1208E thread.'
        else:
            native=parts.abu44m_bulkhead()
            thread_span=source.PANEL_THREAD+source.NUT_LEN
            basis='Manufacturer A panel span plus E nut width; inboard pass-through detail is a conservative bound.'
        result['source_sha256'][str(Path(source.__file__).relative_to(ROOT))]=sha(Path(source.__file__))
        # The production grid builder places these native references directly
        # from its shared flange row; they are not device entries in parts.
        pose=parts._frame(translation=(x,row['flange_y'],z))
        body=native.moved(layout.frame_location(pose))
        nut=parts._nut(row)
        which='co2' if name=='co2-inlet' else name.removeprefix('bulkhead-')
        chip_path=HW/f'printed-parts/enclosure/rear-identification/rear-label-{which}.step'
        chip_native=cq.importers.importStep(str(chip_path)).val()
        # The largest positive-Y planar face is the chip's full face; the
        # lettering has smaller proud faces and lies outside the flange land.
        chip_face=max((f for f in chip_native.Faces() if f.geomType()=='PLANE'
            and f.BoundingBox().ylen<1.e-5 and f.Center().y>1.e-5),key=lambda f:f.Area())
        chip_thickness=chip_face.Center().y-chip_native.BoundingBox().ymin
        flange_y=pose['translation_mm'][1]
        nut_y=nut.BoundingBox().ymax
        floor_y=flange_y-chip_thickness
        chip=chip_native.translate((x,floor_y-chip_native.BoundingBox().ymin,z))
        hole_r=ports[name]['bore_diameter_mm']/2
        hole=cylinder(hole_r,x,z,nut_y-.1,flange_y+.1)
        backing=projected(face_at_y(nut,nut_y),floor_y-nut_y).cut(hole)
        chip_land=projected(face_at_y(body,flange_y),-chip_thickness).cut(hole)
        missing_backing=volume(backing.cut(shell))
        missing_chip=volume(chip_land.cut(chip))
        barrel=cylinder(row['barrel_d_mm']/2,x,z,nut_y,flange_y)
        barrel_common=volume(barrel.intersect(shell))+volume(barrel.intersect(chip))
        clamp=flange_y-nut_y
        free=thread_span-clamp-row['nut_depth_mm']
        checks={
            'full_printed_backing_present':missing_backing<TOL_MM3,
            'full_chip_flange_land_present':missing_chip<TOL_MM3,
            'nominal_barrel_passes_both_bores':barrel_common<TOL_MM3,
            'selected_clamp_span_matches':abs(clamp-plan['retained_panel_mm'])<1.e-5,
            'actual_chip_is_2mm':abs(chip_thickness-2.)<1.e-5,
            'nominal_barrel_free_length_positive':free>0.}
        result['ports'][name]={
            'pose':pose,'chip':{'path':str(chip_path.relative_to(ROOT)),
                'sha256':sha(chip_path),'signature':signature(chip)},
            'body_signature':signature(body),'nut_signature':signature(nut),
            'clamping_planes_world_y_mm':{'nut':nut_y,'chip_floor':floor_y,'flange':flange_y},
            'clamped_stack_mm':{'printed_backing':floor_y-nut_y,
                'actual_chip':chip_thickness,'total':clamp},
            'native_missing_mm3':{'complete_nut_footprint_backing':missing_backing,
                'complete_flange_footprint_chip':missing_chip},
            'finite_land_area_mm2':{'nut':volume(backing)/(floor_y-nut_y),
                                  'flange':volume(chip_land)/chip_thickness},
            'inward_face_probe_supported_area_mm2':{
                'nut':volume(nut.translate((0.,FACE_PROBE_MM,0.)).intersect(shell))/FACE_PROBE_MM,
                'flange':volume(body.translate((0.,-FACE_PROBE_MM,0.)).intersect(chip))/FACE_PROBE_MM},
            'barrel_bore_overlap_mm3':barrel_common,
            'nominal_barrel':{'diameter_mm':row['barrel_d_mm'],
                'thread_span_mm':thread_span,'nut_axial_mm':row['nut_depth_mm'],
                'free_after_selected_stack_and_nut_mm':free,'basis':basis},
            'ports_world':{side:{'mouth_mm':layout.point(pose,source.port(sign)[0]),
                'outward':layout.vector(pose['rotation'],source.port(sign)[1])}
                for side,sign in (('outboard',1.),('inboard',-1.))},
            'checks':checks,'passed':all(checks.values())}
        print(name+': '+json.dumps({'passed':all(checks.values()),
            'stack_mm':[floor_y-nut_y,chip_thickness,clamp],
            'missing_mm3':[missing_backing,missing_chip], 'nominal_free_mm':free}),flush=True)
    result['passed']=all(row['passed'] for row in result['ports'].values())
    args.output.write_text(json.dumps(result,indent=2)+'\n')


if __name__=='__main__':
    main()
