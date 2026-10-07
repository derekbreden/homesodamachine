"""Bind the unchanged relief tube's factory tuck and installed exit.

The native tube is rotated around its exact incoming circular-face axis, so its
length and curvature are unchanged. This is a temporary pose, not a rigid
untwist proof through the narrow core exit.
"""
from pathlib import Path
import sys,json,hashlib
import cadquery as cq
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(HERE.parent/'pump'))
import generate as G

def tucked(source,degrees=-70):
    inlet=max((f for f in source.Faces() if f.geomType()=='PLANE'),key=lambda f:f.Center().z)
    start=inlet.Center();axis=-inlet.normalAt()
    return source.rotate(start.toTuple(),(start+axis).toTuple(),degrees),start,axis

def main():
    native=G.baseline.read();source=native['cold-core/line-prv-vent']
    park,start,axis=tucked(source)
    out=ROOT/'.cache/pump-first-layout/structure/hose-closure'
    out.mkdir(parents=True,exist_ok=True)
    path=out/'prv-factory-tucked.brep';park.exportBrep(str(path))
    records={}
    for folder in ['funnel','pump','routing','structure','mounts','wiring']:
        p=HERE.parent/folder/'candidate.json'
        if p.exists():records.update(json.loads(p.read_text()).get('parts',{}))
    parts=native.copy()
    for n,r in records.items():parts[n]=cq.Shape.importBrep(str(ROOT/r['brep']))
    rows=[];box=G.bounds(park)
    for name,s in parts.items():
        if name in ['cold-core/line-prv-vent','enclosure-back-top']:continue
        b=G.bounds(s)
        if not all(box[i]<=b[i+3] and b[i]<=box[i+3] for i in range(3)):continue
        gap=park.distance(s);common=G.overlap(park,s) if gap<1e-6 else 0.
        rows.append({'other':name,'gap_mm':gap,'common_mm3':common,'pass':common<.01})
    slides=[];roof=parts['enclosure-back-top']
    for y in [70,40,20,10,5,2,1,.25,0]:
        s=roof.translate((0,y,0));common=G.overlap(s,park)
        slides.append({'back_top_offset_y_mm':y,'common_mm3':common,'gap_mm':park.distance(s),'pass':common<.01})
    halfway,_,_=tucked(source,-45)
    blocked=G.overlap(halfway,parts['cold-core/foam-shell'])
    installed_common=G.overlap(source,roof)
    result={'rigid_pose_and_y_slide_pass':all(r['pass']for r in rows+slides),
        'temporary_pose':{'brep':str(path.relative_to(ROOT)),'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
            'clock_deg':-70,'rotation_origin_mm':start.toTuple(),'rotation_axis':axis.toTuple(),
            'bounds_mm':G.bounds(park),'preserved_properties':'The unchanged native occupied tube is a rigid rotation about its measured incoming face. Length, circular sections and all local curvature are identical.'},
        'temporary_native_neighbors':rows,'y_slide_checks':slides,
        'installed_pose':{'source':'cold-core/line-prv-vent','bounds_mm':G.bounds(source),'roof_common_mm3':installed_common,'roof_gap_mm':source.distance(roof),'final_exit_preserved':True},
        'rigid_untwist_counterexample':{'clock_deg':-45,'foam_shell_common_mm3':blocked,'pass':blocked<.01},
        'factory_method':[
            'Before enclosing the core, place a removable fine pull loop at the relief outlet and route its free ends down the existing west vent chase to the open external groove. The fixture must fit the accepted6.8mm core exit around the6.35mm tube; no below-cap stock is altered.',
            'Temporarily park the outlet in the shown70° inward clocking about the shroud inlet. Keep the native source attachment at its original position and hold the free outlet within the internal pocket while the back-top follows its retained Y slides.',
            'After the back-top seats, use the free pull-loop ends at the outside groove to guide the compliant outlet through its accepted core exit to the exact flush west mouth. Remove the temporary loop and verify the clear vent/chase path before closing the appliance.',
        ],
        'scope':'Native temporary occupancy and nine sampled roof Y poses are checked. The exact installed vent and every below-cap interface are preserved.',
        'qualification_limits':[
            'The flexible transition through the narrow exit, temporary pull-loop size/material, source retention and complete loop removal require physical factory assembly qualification.',
            'Rigid rotation through the intermediate45° pose hits the foam-shell exit. It is not the proposed physical reseat trajectory and is deliberately recorded; the selected tucked pose alone does not prove continuous flexible motion.',
            'Inspect for an unpinched tube and an unobstructed relief chase after reseating. The installed relief capacity/backpressure qualification is unchanged.',
        ],
        'native_source_sha256':G.baseline.prepare()['sha256'],
        'roof_brep':records['enclosure-back-top']['brep'],
        'roof_sha256':hashlib.sha256((ROOT/records['enclosure-back-top']['brep']).read_bytes()).hexdigest()}
    (HERE/'prv-factory-handling.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'pass':result['rigid_pose_and_y_slide_pass'],'rigid_untwist_pass':blocked<.01}),flush=True)

if __name__=='__main__':main()
