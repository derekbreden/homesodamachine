"""One exact right-half access check using the retained actual support roads.

No source model, export, or native print archive is changed. The branch is detached
from its accessible lower stem before the checked down-then-fore movement.
"""
from pathlib import Path
import hashlib,json,re,sys,time
import numpy as np
import cadquery as cq
from shapely.geometry import LineString,box
from shapely.ops import unary_union

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware/printed-parts/petgf.3mf').exists())
HERE=ROOT/'.cache/prints/2026-09-21-enclosure-carrier-pair-mark2-v1'
HERE.mkdir(parents=True,exist_ok=True)
DURABLE=ROOT/'hardware/printed-parts/enclosure/tee-readiness/full-enclosure-print/carrier-pair-receiver-access.json'
sys.path.insert(0,str(ROOT/'hardware/printed-parts/faucet'))
from prepare_display_print import extrusion_segments

def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()
def make_box(xs,ys,zs):
    return cq.Solid.makeBox(xs[1]-xs[0],ys[1]-ys[0],zs[1]-zs[0],cq.Vector(xs[0],ys[0],zs[0]))
def bounds(s):
    b=s.BoundingBox();return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]

start=time.monotonic()
base=HERE
audit_path=base/'enclosure-carrier-pair-black-z004-mark2-v1-input.support-audit.json'
audit=json.loads(audit_path.read_text())
reading=next(p for p in audit['parts'] if p['piece']=='enclosure-tee-carrier-right')
native_path=ROOT/'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-right.step'
assert sha(native_path)=='2d6b6565906328f6cfed75e7a41f1d5ca74037cf29f79fe060f5f9d8f235bb16'
gcode=base/'ready/support-labels-enclosure-tee-carrier-right.gcode'
assert sha(gcode)==reading['inputs']['gcode_sha256']
native_archive=HERE/'ready/enclosure-carrier-pair-black-z004-mark2-v1.gcode.3mf'
sources=[native_archive,ROOT/'hardware/printed-parts/faucet/prepare_display_print.py',ROOT/'hardware/scripts/enclosure_support_audit.py',native_path,audit_path,gcode,ROOT/'hardware/printed-parts/enclosure/tee-carrier/_simple_carrier.py',ROOT/'hardware/printed-parts/enclosure/tee-carrier/entry-backing-check.json']
input_hashes={str(p.relative_to(ROOT)):sha(p) for p in sources}
transform=reading['coordinate_frame']['plate_to_original_cad_transform']
matrix=np.array(transform[:9]).reshape((3,3));translation=np.array(transform[9:])
# Extract a small layer window while retaining the precise prior coordinate/mode
# state. All commands inside the window remain byte-for-byte from the native file.
word=re.compile(r'(?:^| )([XYZE])([-+0-9.]+)')
window=HERE/'analysis-receiver-layers.gcode'
pos=dict(X=0.,Y=0.,Z=0.,E=0.);absolute=True;relative_e=True;width=0.;started=False
with gcode.open() as inp,window.open('w') as out:
    for raw in inp:
        if raw.startswith('; LINE_WIDTH:'):width=float(raw.split(':',1)[1])
        if raw.startswith('; Z_HEIGHT:'):
            layer=float(raw.split(':',1)[1]);world=layer+translation[2]
            if world>217.4:break
            if world>=214.5 and not started:
                assert absolute and relative_e
                out.write('G90\nM83\nG92 '+' '.join(f'{k}{v:.9f}' for k,v in pos.items())+'\n')
                out.write(f'; LINE_WIDTH: {width}\n');started=True
        if started:
            out.write(raw);continue
        code=raw.split(';',1)[0].strip()
        if not code:continue
        command=code.split(None,1)[0]
        if command in ('G90','G91'):absolute=command=='G90'
        elif command in ('M82','M83'):relative_e=command=='M83'
        elif command in ('G0','G1','G2','G3','G92'):
            for key,value in word.findall(code):
                value=float(value)
                if command=='G92':pos[key]=value
                elif key=='E':pos[key]=pos[key]+value if relative_e else value
                else:pos[key]=value if absolute else pos[key]+value
assert started
# This branch uses straight native extrusion roads. Travel/retract arcs have no
# positive extrusion and do not enlarge its printed material envelope.
feature='';extruding_support_arcs=0
for raw in window.open():
    if raw.startswith('; FEATURE:'):feature=raw.split(':',1)[1].strip()
    if feature.startswith('Support') and raw.startswith(('G2 ','G3 ')) and re.search(r' E[+]?[0-9]',raw):
        extruding_support_arcs+=1
assert extruding_support_arcs==0
region=box(-8.,107.,14.,113.5)
roads=[];zs=[];count=0;crossings=0;max_width=0.
for seg in extrusion_segments(window):
    if seg['object']!=reading['inputs']['object_label'] or not seg['feature'].startswith('Support'):continue
    p=np.array([seg['a'],seg['b']])@matrix+translation
    z=float(p[:,2].mean())
    if not 215.5<=z<=217.1:continue
    material=LineString(p[:,:2]).buffer(seg['width']/2)
    if not material.intersects(region):continue
    if not region.covers(material):crossings+=1
    roads.append(material);zs.append(z);count+=1;max_width=max(max_width,seg['width'])
assert roads and not crossings,(count,crossings)
material=unary_union(roads)
# Split at the fore lip edge. Rectangular bounds on these two pieces give a
# conservative L-shaped envelope for every measured buffered road in the branch.
xy=[]
for side in (box(-20,90,-3.5,125),box(-3.5,90,25,125)):
    cut=material.intersection(side)
    assert not cut.is_empty
    xy.append(cut.bounds)
cover=unary_union([box(*b) for b in xy]);assert cover.covers(material)
cap_bottom=215.5;cap_top=max(zs)
native=cq.importers.importStep(str(native_path)).val()
assert native.isValid()
checks=[]
coordinate_contact_tolerance=1e-5
# The inverse STL/plate transform places emitted nominal contact within a few
# millionths of a millimetre of native Y112.640. Classify only this rear-plane sliver as
# coincident contact. It is not claimed as positive air or physical tolerance.
def check(name,prisms,allow_rear_contact=False):
    shape=prisms[0]
    for other in prisms[1:]:shape=shape.fuse(other)
    overlap_shape=native.intersect(shape)
    overlap=abs(overlap_shape.Volume())
    overlap_bounds=bounds(overlap_shape) if overlap>1e-8 else None
    coincident=(allow_rear_contact and overlap_bounds is not None and
        abs(overlap_bounds[0][1]-112.64)<coordinate_contact_tolerance and
        abs(overlap_bounds[1][1]-112.64)<coordinate_contact_tolerance)
    checks.append({'name':name,'probe_bounds_mm':bounds(shape),'overlap_mm3':overlap,
        'overlap_bounds_mm':overlap_bounds,'coincident_rear_contact':coincident,
        'pass':overlap<1e-8 or coincident})
    return shape
check('Emitted branch envelope in existing receiver; rear-wall contact retained',[
    make_box((b[0],b[2]),(b[1],b[3]),(cap_bottom,cap_top)) for b in xy],True)
check('Continuous 0.05 mm fore release of the detached emitted branch',[
    make_box((b[0],b[2]),(b[1]-.05,b[3]),(cap_bottom,cap_top)) for b in xy],True)
# After freeing the wall contact, include an extra 0.02 mm XY allowance around
# every emitted road. This is a path-sensitivity envelope, not a material claim.
padded=material.buffer(.02)
padded_xy=[]
for side in (box(-20,90,-3.5,125),box(-3.5,90,25,125)):
    padded_xy.append(padded.intersection(side).bounds)
padded_cover=unary_union([box(*b) for b in padded_xy]);assert padded_cover.covers(padded)
check('Released branch with 0.02 mm additional XY envelope',[
    make_box((b[0],b[2]),(b[1]-.05,b[3]-.05),(cap_bottom,cap_top)) for b in padded_xy])
check('Continuous 2 mm downward sweep into the shelf-entry opening',[
    make_box((b[0],b[2]),(b[1]-.05,b[3]-.05),(cap_bottom-2,cap_top)) for b in padded_xy])
check('Continuous 6 mm forward withdrawal after lowering',[
    make_box((b[0],b[2]),(b[1]-6.05,b[3]-.05),(cap_bottom-2,cap_top-2)) for b in padded_xy])
check('Open fore access for detaching the lower branch stem',[
    make_box((-8,13),(100,114.65),(209.225,215.55))])
result={'status':'pass' if all(c['pass'] for c in checks) else 'fail','scope':'One loose right carrier and one detached receiver-roof support branch; no mechanism geometry change or physical cleanup measurement.',
 'input_sha256':input_hashes,'script_sha256':sha(Path(__file__)),'analysis_gcode_sha256':sha(window),
 'native_archive':str(native_archive.relative_to(ROOT)),'native_archive_sha256':sha(native_archive),'rear_plane_emitted_gap_mm':112.64-max(b[3] for b in xy),
 'native_support_island':'interface-11 in the exact current two-carrier native slice','native_roads':count,'native_layers_z_mm':sorted(set(round(z,6) for z in zs)),'maximum_native_width_mm':max_width,'additional_xy_buffer_mm':0.0,
 'selected_branch_region_xy_mm':list(region.bounds),'all_selected_roads_inside_region':crossings==0,'conservative_xy_envelopes_mm':[list(b) for b in xy],
 'emitted_envelope_covers_roads':cover.covers(material),'positive_extruding_support_arcs':extruding_support_arcs,'coincident_contact_tolerance_mm':coordinate_contact_tolerance,'post_release_additional_xy_envelope_mm':.02,'post_release_xy_envelopes_mm':[list(b) for b in padded_xy],'post_release_envelope_covers_roads':padded_cover.covers(padded),'branch_cut_plane_z_mm':cap_bottom,'branch_top_z_mm':cap_top,'motions_mm':[[0,-.05,0],[0,0,-2],[0,-6,0]],'native_checks':checks,
 'assembly_sequence':['While the right half is loose, detach the short roof branch from its lower support stem through the broad shelf-entry opening.','Free its rear-wall contact and move it 0.05 mm fore; the following swept envelope includes an extra 0.02 mm XY allowance.','Lower the detached branch 2 mm into that opening.','Withdraw it 6 mm fore (−Y), then remove it from the open front.','Complete support cleanup before joining halves or installing tees/springs.'],
 'limits':['The check covers a detached short branch, not the entire connected bed-rooted support tree.','The emitted rear edge is nominally tangent within the recorded coordinate tolerance; no positive physical starting wall gap or low detachment force is inferred.','Detachment force, cleanup time and contact finish remain physical observations.','The proof is bound to this exact current two-carrier native archive; a different slice requires its own emitted-branch check.'],
 'source_geometry_modified':False,'native_exports_written':False,'elapsed_seconds':time.monotonic()-start}
result['source_drift']=[p for p,h in input_hashes.items() if sha(ROOT/p)!=h]
assert not result['source_drift']
(HERE/'receiver-access.json').write_text(json.dumps(result,indent=2)+'\n')
DURABLE.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result,indent=2))
if result['status']!='pass':raise SystemExit(1)
