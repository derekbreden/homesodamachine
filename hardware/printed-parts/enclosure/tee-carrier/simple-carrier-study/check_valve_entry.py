"""Actual lower-valve rise and post insertion against the candidate carrier."""
import json
from pathlib import Path
import cadquery as cq
from build_concept import build,sha,box,bounds,SIDE_WEB_Z0
from check_joint_motion import swept_overlap
HERE=Path(__file__).resolve().parent


def main():
    M,I,plain,blank,L,R,*_=build()
    carrier=cq.Compound.makeCompound([L,R])
    folder=HERE/'inputs/placed-neighbors'
    m=json.loads((folder/'manifest.json').read_text())
    rows=[];projection=[]
    entry=-5.45
    for valve in 'cdgj':
        for kind in ('coil','valve'):
            name=f'{kind}-v-{valve}';row=m['bodies'][name];p=folder/row['brep']
            assert sha(p)==row['sha256']
            native=cq.Shape.importBrep(str(p))
            for label,start,end in (('rise',(0,entry,-100),(0,entry,0)),
                                     ('post insertion',(0,entry,0),(0,0,0))):
                result={'component':name,'stage':label,**swept_overlap(native,start,end,carrier)}
                rows.append(result);print(json.dumps(result),flush=True)
            if kind=='coil' and valve in 'cd':
                zone=box((-57,57),(0,I['web_aft_y']+.9-entry+.25),(0,300))
                feature=native.intersect(zone)
                projection.append({'component':name,'forward_feature_bounds':bounds(feature),
                    'native_top_to_backing_floor_air_mm':SIDE_WEB_Z0-feature.BoundingBox().zmax})
    report={'scope':'Current frozen lower valves/coils follow the existing -5.45 mm fore staging, a 100 mm rise and complete post insertion. All rigid constituent faces swept. Pusher and carrier installation occur before these valves.',
        'generator_sha256':sha(HERE/'build_concept.py'),'script_sha256':sha(__file__),
        'sweep_script_sha256':sha(HERE/'check_joint_motion.py'),
        'neighbor_manifest_sha256':sha(folder/'manifest.json'),'sweeps':rows,
        'inner_forward_features':projection,
        'all_reported_native_readings_clear':all(r['initial_overlap_mm3']<1e-5 and r['max_prism_overlap_mm3']<1e-5 for r in rows)}
    (HERE/'valve-entry-checks.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'clear':report['all_reported_native_readings_clear'],'forward_features':projection}),flush=True)


if __name__=='__main__':main()
