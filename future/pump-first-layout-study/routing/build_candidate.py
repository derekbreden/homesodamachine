"""Place exact purchased bodies and a shallow west-pull ASSE pan in the study.

All canonical source files and manufactured part geometries remain read-only.
The private pan dimensions and WATER chip's decorative west finish are declared
here. The pan wall/floor/cove and pull face profiles retain their source
dimensions. Installed B-reps are disposable cache.
"""
from pathlib import Path
import hashlib
import json
import sys

import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
CACHE = ROOT/'.cache/pump-first-layout/routing'
sys.path[:0] = [str(STUDY), str(ROOT/'hardware/scripts'),
               str(ROOT/'hardware/printed-parts/enclosure/asse-drip-pan'),
               str(ROOT/'hardware/reference/water-split'),
               str(ROOT/'hardware/reference/neofit-flow-control')]
import baseline
import asse_drip_pan as pan
import water_split as split
import neofit_flow_control as flowreg
from water_ring_finish import flatten_water_ring, finish_record


def bounds(shape):
    b = shape.BoundingBox()
    return [b.xmin, b.ymin, b.zmin, b.xmax, b.ymax, b.zmax]


def box_place(shape, *, x0=None, y0=None, z0=None):
    b = shape.BoundingBox()
    return shape.translate((0. if x0 is None else x0-b.xmin,
                            0. if y0 is None else y0-b.ymin,
                            0. if z0 is None else z0-b.zmin))


def across(shape, x, y, z):
    s = shape.rotate((0, 0, 0), (0, 0, 1), 90.)
    b = s.BoundingBox()
    return s.translate((x-(b.xmin+b.xmax)/2,
                        y-(b.ymin+b.ymax)/2, z-b.zmin))


def main():
    CACHE.mkdir(parents=True, exist_ok=True)
    previous = json.loads((HERE/'candidate.json').read_text()) if (HERE/'candidate.json').exists() else {}
    names = ['asse1022-assembly', 'moisture-plate', 'relay-1', 'relay-2',
             'wr1110', 'gasher-co2', 'digiten-flow',
             'co2-adapter-regulator-in', 'co2-adapter-regulator-out',
             'co2-adapter-check-in', 'co2-adapter-check-out',
             'wago-reeds-a', 'wago-reeds-b', 'wago-sensors',
             'bulkhead-water', 'bulkhead-carb', 'co2-inlet',
             'bulkhead-ring-water', 'bulkhead-ring-water-word',
             'bulkhead-ring-carb', 'bulkhead-ring-carb-word',
             'bulkhead-ring-co2', 'bulkhead-ring-co2-word',
             'tube-customer-water', 'tube-customer-co2',
             'tube-collar-water', 'tube-collar-water-word',
             'tube-collar-co2', 'tube-collar-co2-word',
             'wago-h', 'wago-n', 'wago-g', 'wago-v12', 'wago-gnd']
    old = baseline.read(names)
    shapes, records = {}, {}

    def add(name, shape, role, detail, transform=None):
        assert shape.isValid(), name
        path = CACHE/(name+'.brep')
        shape.exportBrep(str(path))
        shapes[name] = shape
        records[name] = {'brep': str(path.relative_to(ROOT)), 'role': role,
                         'detail': detail, 'bounds': bounds(shape),
                         'sha256': hashlib.sha256(path.read_bytes()).hexdigest()}
        if transform is not None:
            records[name]['transform'] = transform
        print('placed', name, flush=True)

    add('asse1022-assembly', across(old['asse1022-assembly'], -13.325, 310.3, 279.45),
        'water', 'Transverse ASSE assembly; vent(-15.325,310.3,279.45), flow +X.',
        {'rotation_world_z_deg': 90, 'translation_after_rotation': [363.185,388.37,-27.76058083755]})

    pan.PAN_X, pan.PAN_Y, pan.PAN_Z = 102.5, 51., 12.
    p = pan.build().val().translate((-107.5, 279.6, 254.4))
    add('asse-drip-pan', p, 'water',
        'West-pull102.5x51x12mm basin;2.5mm walls,3mm floor,R2 coves;13.05mm atmospheric fall,40.122mL native rim-fill cavity and complete54x40mm probe floor.')
    plate = old['moisture-plate'].rotate((0,0,0),(0,0,1),-90.)
    b = plate.BoundingBox()
    plate = plate.translate((-52.25-(b.xmin+b.xmax)/2,
                             309.1-(b.ymin+b.ymax)/2, 257.4-b.zmin))
    add('moisture-plate', plate, 'water',
        'Existing 54 x 40 mm probe rotated long dimension across widened tray; seated on its flat floor.')

    # The bodies are serialized by the host generator, keeping the occupied
    # reference, mounting seat and terminal orientation under one declaration.
    for source in ['floor-candidate.json', 'roof-candidate.json']:
        module = json.loads((STUDY/'mounts'/source).read_text())
        for name, record in module['expected_devices'].items():
            add(name, cq.Shape.importBrep(str(ROOT/record['brep'])),
                'electronics', record['detail'])

    for name in ['wr1110','co2-adapter-regulator-in','co2-adapter-regulator-out']:
        q=cq.Shape.importBrep(str(CACHE/('chosen-'+name+'.brep')))
        add(name,q,'gas','Regulator rolled onto its narrow face in a diagonal west lane; inlet(-88.5,321,321.4), yaw75deg; supported below the high roof junction deck.')
    for name in ['gasher-co2','co2-adapter-check-in','co2-adapter-check-out']:
        q=cq.Shape.importBrep(str(CACHE/('chosen-'+name+'.brep')))
        add(name,q,'gas','Downstream check under the rolled meter, flow fore -Y; axisX74,Z265.5, inletY431,outletY357.5; native envelope clear of pump and supply.')
    q=old['digiten-flow'].rotate((-40.81,394.01,332.1),(-40.81,395.01,332.1),90.).translate((125.31,8.5,0.))
    add('digiten-flow',q,'water','Meter rolled 90 degrees about its flow axis on east side; axisX84.5,inletY372.01; removable side-cover pocket retains3.1mm outer shell stock.',
        {'rotation_about_flow_deg':90,'rotation_origin':[-40.81,394.01,332.1],'translation':[125.31,8.5,0.]})
    meter_box=q.BoundingBox()
    pocket=cq.Solid.makeBox(104.4-98.49,meter_box.ylen+2,meter_box.zlen+2,
                           cq.Vector(98.49,meter_box.ymin-1,meter_box.zmin-1))
    pocket_path=CACHE/'meter-wall-clearance.brep';pocket.exportBrep(str(pocket_path))
    q=split.build().rotate((0,0,0),(0,1,0),90.).translate((95.25,402.75,265.))
    add('water-split',q,'water','Measured union tee atX95.25,Y402.75,Z265; mainY and branchUP, fixed aft collar on the direct lid pad.')
    q=flowreg.build().rotate((0,0,0),(1,0,0),90.).translate((27.5,312.5,275.25))
    add('flow-regulator',q,'water','Flavor needle low fore of pump, flow+X and adjusterFORE; barrel axisX27.5/Y312.5/Z275.25.')

    for name in names:
        if name in records or not any(k in name for k in ['bulkhead','co2-inlet','customer','collar']):
            continue
        if 'water' in name:
            shift = (-12.43,0.,-22.71058083755)
            role='water'
        elif 'carb' in name:
            shift=(122.31,0.,-7.21058083755)
            role='water'
        else:
            shift=(75.05,0.,-63.96058083755)
            role='gas'
        q=old[name].translate(shift)
        if name=='bulkhead-ring-water':q=flatten_water_ring(q)
        add(name,q,role,
            'Rear interface with its fitted native body, colored identification collar and readable port label.',
            {'translation':list(shift)})
        if name=='bulkhead-ring-water':records[name]['decorative_finish']=finish_record()

    P=lambda pos,axis,diam=6.35: {'pos':pos,'axis':axis,'diam':diam}
    ports={
        'asse1022-assembly':{'tube-in':P([-83.325,310.3,308.45],[-1,0,0]),
          'tube-out':P([56.675,310.3,308.45],[1,0,0]),'vent-tip':P([-15.325,310.3,279.45],[0,0,-1],9.53)},
        'wr1110':{'inlet':P([-88.5,321,321.4],[-.258819045103,-.965925826289,0]),'outlet':P([-62.876914535,416.6266568026,321.4],[.258819045103,.965925826289,0])},
        'gasher-co2':{'inlet':P([74,431,265.5],[0,1,0]),'outlet':P([74,357.5,265.5],[0,-1,0])},
        'digiten-flow':{'inlet':P([84.5,372.01,332.1],[0,-1,0]),'outlet':P([84.5,433.01,332.1],[0,1,0])},
        'bulkhead-water':{'inboard':P([-90.5,446.51,313.5],[0,-1,0])},
        'co2-inlet':{'inboard':P([77.5,454.0026,272.],[0,-1,0])},
        'bulkhead-carb':{'tube-in':P([84.5,446.51,329.],[0,-1,0])},
        'water-split':{'supply':P([95.25,424,265.],[0,1,0]),'to-vk':P([95.25,381.5,265.],[0,-1,0]),
          'to-flavor':P([95.25,402.75,287.35],[0,0,1])},
        'flow-regulator':{'inlet':P([4.5,312.5,275.25],[-1,0,0]),'outlet':P([50.5,312.5,275.25],[1,0,0]),
          'adjuster':P([27.5,278.5,275.25],[0,-1,0],10)}}
    result={'parts':records,'replacement_names':list(records),'ports':ports,
       'clearance_cutters':{'meter-wall':{'brep':str(pocket_path.relative_to(ROOT)),
           'print_owner':'enclosure-back-top','radial_air_mm':1,'minimum_outer_stock_mm':3.1,
           'bounds':bounds(pocket),'detail':'Inner-east flank pocket for the complete rolled meter cover; outer face remainsX107.5.'}},
       'routing_status':{'finished':[],'pending':['water-supply-link','water-2','water-3','fluid-1','fluid-2','fluid-14','fluid-18','fluid-28','co2-0','co2-1','co2-2','carb-1','carb-2'],
          'note':'Rigid-body native placement published for integration; all pending original runs must be replaced before a complete candidate is claimed.'},
       'scope':'Native geometric study. Physical fit, load capacity, tube relaxation, longevity and factory workholding remain separate qualifications.'}
    for name, record in previous.get('parts', {}).items():
        if (name.startswith(('tube-', 'carb-foam-', 'routing-host-', 'routing-anchor-'))
                or name in ['nameplate','nameplate-ink','keystone-jack']) and name not in records:
            result['parts'][name] = record
    for key in ['routes', 'intended_contacts', 'routing_status', 'shell_fuse_part_names',
                'lid_fuse_part_names', 'pilot_cutters', 'hosts', 'anchors', 'interface_moves', 'shell_stock', 'bay_outer_extents', 'pan', 'standalone_print_parts']:
        if key in previous:
            result[key] = previous[key]
    result.setdefault('standalone_print_parts',{})['water-identification-ring']={
        'source_part':'bulkhead-ring-water','rotation_x_deg':90}
    result.setdefault('interface_moves',{})['water_identification_chip']=finish_record()
    result['replacement_names'] = sorted(set(result['replacement_names'] + previous.get('replacement_names', [])))
    (HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print('candidate manifest', HERE/'candidate.json', flush=True)


if __name__ == '__main__':
    main()
