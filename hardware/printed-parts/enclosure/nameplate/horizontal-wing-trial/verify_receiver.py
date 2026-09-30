"""Verify the wall-pose coupon and unobstructed sideways wing slots."""
import hashlib,json,re,sys,zipfile
import numpy as np
import trimesh
from shapely.geometry import LineString,Polygon,box
from shapely.ops import unary_union
import prepare_receiver as prep
import wing_interface as interface

ROOT,JOB,HERE=prep.ROOT,prep.JOB,prep.HERE
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from enclosure_support_audit import audit

def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    prepared=json.loads((JOB/'preparation.json').read_text())
    staged=next(JOB.glob('*-input.3mf'));native=next((JOB/'ready').glob('*.gcode.3mf'))
    assert sha(staged)==prepared['project_sha256']
    for path,digest in prepared['source_geometry_and_settings_sha256'].items():assert sha(ROOT/path)==digest,path
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings=json.loads(z.read('Metadata/project_settings.config'))
        gc=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    required={'filament_nozzle_map':['0'],'filament_colour':['#000000'],
              'nozzle_diameter':['0.4','0.4'],'layer_height':'0.24','initial_layer_print_height':'0.2',
              'wall_sequence':'inner wall/outer wall','is_infill_first':'0','infill_wall_overlap':'15%',
              'support_object_xy_distance':'0.4','support_top_z_distance':'0.45',
              'support_bottom_z_distance':'0.3','support_type':'tree(auto)','support_style':'default'}
    for k,v in required.items():assert settings[k]==v,(k,settings[k])
    assert prep.support_settings(settings)==prepared['inherited_support_settings']
    assert prepared['enclosure_build_direction']==-1.
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.02]
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path));assert {r['object'] for r in roads}=={1901} and {r['tool'] for r in roads}=={0}
    layers=wall_layers(native,1901)
    assert layers[0]==(.2,.2) and all(abs(h-.24)<1e-5 for _,h in layers[1:])
    support=[r for r in roads if r['feature'].startswith('Support')]
    # Derive the X180 placement from the mesh and saved printable area.
    mesh=trimesh.load(HERE/(prep.NAME+'.stl'),force='mesh')
    centre=mesh.bounds.mean(axis=0)
    part=prepared['parts'][0]
    print_centre=np.array(prepared['shared_printable_area_mm']).mean(axis=0)
    tx,ty=print_centre[0]-centre[0],print_centre[1]+centre[1]
    zmax=mesh.bounds[1,2]
    # Measure emitted bead envelopes across both flat slot bearings. The Y-fit
    # trial must survive slicing; this does not measure physical bead distortion.
    bearing_checks=[]
    for layer in sorted({r['layer'] for r in roads if abs(zmax-r['layer'])<=14}):
        walls=[r for r in roads if r['layer']==layer and r['feature']=='Outer wall']
        for side in (-1,1):
            for beyond in (1.55,2.0):
                x=tx+side*(interface.WIDTH/2+beyond)
                cut=LineString(((x,ty-interface.THICK-.5),(x,ty+1)))
                beads=[]
                for r in walls:
                    if min(r['a'][0],r['b'][0])-r['width']/2<=x<=max(r['a'][0],r['b'][0])+r['width']/2:
                        piece=LineString((r['a'],r['b'])).buffer(r['width']/2).intersection(cut)
                        if not piece.is_empty:beads.append(piece)
                section=unary_union(beads)
                pieces=list(section.geoms) if hasattr(section,'geoms') else [section]
                bands=sorted((ty-p.bounds[3],ty-p.bounds[1]) for p in pieces if not p.is_empty)
                floor=max(b for a,b in bands if b<.8)
                roof=min(a for a,b in bands if a>1.2)
                outer=max(b for a,b in bands if a>1.2)
                assert abs(floor)<.015 and abs(roof-(interface.WING_THICK+interface.THICKNESS_AIR))<.015
                assert outer-roof>=1.2-.015,(layer,side,outer-roof)
                bearing_checks.append((floor,roof,roof-floor,outer-roof))
    assert bearing_checks
    bearing_envelope={'sections':len(bearing_checks),
        'floor_Y_range_mm':[min(c[0] for c in bearing_checks),max(c[0] for c in bearing_checks)],
        'roof_Y_range_mm':[min(c[1] for c in bearing_checks),max(c[1] for c in bearing_checks)],
        'slot_Y_opening_range_mm':[min(c[2] for c in bearing_checks),max(c[2] for c in bearing_checks)],
        'flat_lip_Y_stock_range_mm':[min(c[3] for c in bearing_checks),max(c[3] for c in bearing_checks)],
        'scope':'Nominal outer-wall bead envelopes across flat bearings in the central 28 mm of both slots; physical distortion and end/corner contact are unmeasured.'}
    # Check every support bead against both slots and their entry bevels.
    slots=[]
    for side in (-1,1):
        x0,x1=sorted((side*(interface.WIDTH/2-.1),side*(interface.WIDTH/2+interface.PROJECTION+interface.TIP_AIR)))
        roof=interface.WING_THICK+interface.THICKNESS_AIR
        mouth=interface.WIDTH/2+interface.FACE_SLIP
        slot=box(tx+x0,ty-roof,tx+x1,ty)
        lead=Polygon([(tx+side*mouth,ty-roof),
                      (tx+side*(mouth+interface.ENTRY_BEVEL_WIDTH),ty-roof),
                      (tx+side*mouth,ty-roof-interface.ENTRY_BEVEL_DEPTH)])
        slots.append(slot.union(lead))
    zlo=zmax-interface.WING_SPAN/2-interface.END_AIR
    zhi=zmax+interface.WING_SPAN/2+interface.END_AIR+interface.SUPPORTED_END_AIR
    slot_overlaps=[]
    for side,slot in zip(('left','right'),slots):
        volume=0.
        for r in support:
            if zlo<r['layer']<zhi:
                volume+=LineString((r['a'],r['b'])).buffer(r['width']/2).intersection(slot).area
        assert volume<1e-6,(side,volume)
        slot_overlaps.append({'side':side,'sum_of_support_bead_intersection_areas_mm2':volume})
    a=audit(path,'nameplate-flat-wing-receiver',profile=staged,include_unlabelled_support=True)
    a['removal_access']='Inspect tree branches through the open front before installing the plate. No support bead enters either sideways wing slot. Bead clearance does not establish physical removal effort.'
    a['physical_removal_tested']=False
    (JOB/'support-audit.json').write_text(json.dumps(a,indent=2)+'\n')
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    assert interface.TIP_AIR==.45 and interface.FACE_X_AIR==.35 and interface.FACE_SLIP==.15
    assert interface.THICKNESS_AIR==.45 and interface.WING_THICK==1.68
    record={'pass':True,'printer':'Mark2','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'source_hashes_current':True,'model_layers':len(layers),'independent_support_layers':True,
            'enclosure_build_direction':prepared['enclosure_build_direction'],
            'support_profile_differences':prepared['support_profile_differences'],
            'emitted_z_trim_mm':trims,'slot_support_clearance_checks':slot_overlaps,
            'slot_bearing_envelopes':bearing_envelope,
            'support_summary':a['summary'],'support_removal':'Physical trial pending; front-access lane verified.',
            'estimated_seconds':sliced['total_predication'],
            'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
            'submitted':False}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','estimated_seconds','model_layers')}))

if __name__=='__main__':main()
