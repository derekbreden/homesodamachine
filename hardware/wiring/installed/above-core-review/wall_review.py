"""Manual cached-wiring check against the lid's two upright valve walls.

Run through tmp/takeover/cadq after the wall's purchased-component review.
The saved wiring BREPs remain valid while all electrical part poses stay fixed.
No production model, wiring composition or enclosure shell is rebuilt.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[4]
sys.path[:0]=[str(ROOT/'hardware/manifold-layout'),
             str(ROOT/'hardware/printed-parts/cold-core')]
import cadquery as cq
import above_core
import _above_core_mounts as mounts

HERE=Path(__file__).resolve().parent
CACHE=ROOT/'tmp/above-core-electrical-fixture/wiring'


def bounds(shape):
    b=shape.BoundingBox()
    return [getattr(b,n) for n in ('xmin','ymin','zmin','xmax','ymax','zmax')]


def overlap(first,second):
    return all(first[i+3]>second[i]+1e-5 and second[i+3]>first[i]+1e-5
               for i in range(3))


def main():
    cache_index=CACHE/'index.json'
    fixture=json.loads(cache_index.read_text())
    files=fixture['parts']
    location=above_core.frame_location(above_core.cap_lid_pose())
    walls={name:mounts.valve_support(name).moved(location)
           for name in ('valve-v-a','vk-solenoid')}
    record={'scope':'Cached installed conductors, connector housings, sleeves and jackets '
                    'against both native lid-mounted valve walls; no physical qualification.',
            'body_count':len(files),'walls':{},'intersections':[],
            'fixture_aggregate_sha256':fixture.get('aggregate_sha256'),
            'fixture_index_sha256':hashlib.sha256(cache_index.read_bytes()).hexdigest(),
            'wire_brep_sha256':{},'source_sha256':{}}
    wall_bounds={name:bounds(solid) for name,solid in walls.items()}
    for name,solid in walls.items():
        record['walls'][name]={'bounds_mm':wall_bounds[name],
                               'valid':solid.isValid(),'solid_count':len(solid.Solids()),
                               'candidate_count':0}
    for name,file in files.items():
        path=CACHE/file
        solid=cq.Shape.importBrep(str(path))
        record['wire_brep_sha256'][name]=hashlib.sha256(path.read_bytes()).hexdigest()
        own_bounds=bounds(solid)
        for parent,wall in walls.items():
            if not overlap(own_bounds,wall_bounds[parent]):continue
            record['walls'][parent]['candidate_count']+=1
            intersection=solid.intersect(wall)
            volume=intersection.Volume()
            if volume>.01:
                row={'body':name,'wall':parent,'volume_mm3':volume,
                     'bounds_mm':bounds(intersection)}
                record['intersections'].append(row)
                print(json.dumps(row),flush=True)
    record['source_sha256']={str(path.relative_to(ROOT)):hashlib.sha256(path.read_bytes()).hexdigest()
                            for path in (Path(__file__),Path(mounts.__file__),
                                         ROOT/'hardware/manifold-layout/above-core.json')}
    record['geometrically_clear']=not record['intersections']
    output=HERE/'wall-review.json'
    output.write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:v for k,v in record.items()
                      if k not in ('wire_brep_sha256','source_sha256')},indent=2),flush=True)


if __name__=='__main__':main()
