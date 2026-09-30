"""Verify native face-up artwork, standard-fit solids and tree-supported receiver."""
import hashlib,json,re,sys,zipfile
import cadquery as cq
import numpy as np
from shapely.geometry import LineString,Point,Polygon,box
from shapely.ops import unary_union
import prepare_pair as prep

ROOT,JOB,HERE,fit=prep.ROOT,prep.JOB,prep.HERE,prep.trial.interface
sys.path[:0]=[str(HERE.parent),str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/calibration/dual-nozzle-registration')]
from verify_mark2_print import segments
from verify_round_layer_band import wall_layers
from verify_correction import verify as verify_correction
from enclosure_support_audit import audit


def main():
    sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
    prepared=json.loads((JOB/'preparation.json').read_text())
    staged=next(JOB.glob('*-input.3mf'));native=next((JOB/'ready').glob('*.gcode.3mf'))
    assert sha(staged)==prepared['project_sha256']
    for path,digest in prepared['source_geometry_and_settings_sha256'].items():assert sha(ROOT/path)==digest,path
    with zipfile.ZipFile(native) as z:
        assert z.testzip() is None
        settings=json.loads(z.read('Metadata/project_settings.config'));gc=z.read('Metadata/plate_1.gcode')
        assert hashlib.md5(gc).hexdigest()==z.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        (JOB/'preview.png').write_bytes(z.read('Metadata/plate_1.png'))
    required={'initial_layer_print_height':'0.2','layer_height':'0.24',
              'filament_nozzle_map':['0','1'],'nozzle_diameter':['0.4','0.4'],
              'wall_sequence':'inner wall/outer wall','is_infill_first':'0','infill_wall_overlap':'15%',
              'extruder_offset':prepared['native_extruder_offset'],
              'support_type':'tree(auto)','support_style':'default','support_object_xy_distance':'0.4',
              'support_top_z_distance':'0.45','support_bottom_z_distance':'0.3',
              'support_filament':'1','support_interface_filament':'1','flush_into_support':'0'}
    for k,v in required.items():assert settings[k]==v,(k,settings[k])
    assert prep.support_settings(settings)==prepared['receiver_support_settings']
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.02]
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path));assert {r['object'] for r in roads}=={2303,2305}
    plate_roads=[r for r in roads if r['object']==2303]
    assert not any(r['feature'].startswith('Support') for r in plate_roads)
    receiver_roads=[r for r in roads if r['object']==2305]
    assert {r['tool'] for r in receiver_roads}=={0}
    plate_layers=wall_layers(native,2303)
    assert np.allclose([z for z,h in plate_layers],[.2]+[.24*i for i in range(2,17)])
    assert sorted({r['layer'] for r in plate_roads if r['tool']==1})==[2.88,3.12,3.36,3.6,3.84]
    assert max(r['layer'] for r in plate_roads if r['tool']==0)==3.36
    wings=[]
    for z in (.2,1.68,1.92):
        area=unary_union([LineString((r['a'],r['b'])).buffer(r['width']/2) for r in plate_roads if r['layer']==z])
        span=fit.WIDTH/2+fit.PROJECTION/2
        covered=[area.covers(Point(165+s*span,125)) for s in (-1,1)]
        assert covered==([True,True] if z<=1.68 else [False,False]),(z,covered)
        wings.append({'print_z_mm':z,'both_wings_covered':covered})
    artwork=[]
    for z in (3.6,3.84):
        raised=[r for r in plate_roads if r['layer']==z and r['tool']==1]
        counts={name:sum(all(lo<p[0]<hi for p in (r['a'],r['b'])) for r in raised)
                for name,(lo,hi) in {'logo_and_drop':(117,143),'lettering':(145,187),'qr':(188,214)}.items()}
        assert all(n>10 for n in counts.values()) and sum(counts.values())==len(raised)
        artwork.append({'print_z_mm':z,'white_paths_by_region':counts})
    # Both full-depth pocket and mouth lead-in must remain free of support beads.
    tx,ty,tz=prepared['receiver_transform']['translation']
    slots=[]
    for side in (-1,1):
        x0,x1=sorted((side*(fit.WIDTH/2-.1),side*(fit.WIDTH/2+fit.PROJECTION+fit.TIP_AIR)))
        mouth=fit.WIDTH/2+fit.FACE_SLIP;roof=fit.WING_THICK+fit.THICKNESS_AIR
        slot=box(tx+x0,ty-roof,tx+x1,ty)
        lead=Polygon([(tx+side*mouth,ty-roof),(tx+side*(mouth+fit.ENTRY_BEVEL_WIDTH),ty-roof),
                      (tx+side*mouth,ty-roof-fit.ENTRY_BEVEL_DEPTH)])
        slots.append(slot.union(lead))
    lo=tz-fit.WING_SPAN/2-fit.END_AIR;hi=tz+fit.WING_SPAN/2+fit.END_AIR+fit.SUPPORTED_END_AIR
    supports=[r for r in receiver_roads if r['feature'].startswith('Support')]
    slot_checks=[]
    for side,slot in zip(('left','right'),slots):
        overlap=sum(LineString((r['a'],r['b'])).buffer(r['width']/2).intersection(slot).area
                    for r in supports if lo<r['layer']<hi)
        assert overlap<1e-6,(side,overlap)
        slot_checks.append({'side':side,'support_bead_overlap_mm2':overlap})
    # Check actual exported solids at each pure-axis travel limit, and just beyond.
    part=cq.importers.importStep(str(HERE/(prep.trial.NAME+'.step'))).val()
    receiver=cq.importers.importStep(str(HERE/(prep.trial.RECEIVER+'.step'))).val()
    bounds={0:(-fit.FACE_X_AIR,fit.FACE_X_AIR),1:(0.,fit.THICKNESS_AIR),
            2:(-fit.FACE_SLIP-fit.SUPPORTED_END_AIR,fit.FACE_SLIP)}
    fit_checks=[]
    for axis,(low,high) in bounds.items():
        for value,outside in ((low,low-.01),(high,high+.01)):
            v=[0.,0.,0.];v[axis]=value
            overlap=abs(part.translate(v).intersect(receiver).Volume());assert overlap<1e-6,(axis,value,overlap)
            v[axis]=outside;blocked=abs(part.translate(v).intersect(receiver).Volume());assert blocked>1e-5
            fit_checks.append({'axis':'XYZ'[axis],'limit_mm':value,'at_limit_overlap_mm3':overlap,'past_limit_overlap_mm3':blocked})
    insertion=json.loads((HERE/'insertion-envelope.json').read_text());assert insertion['pass']
    baseline=next((JOB/'uncorrected/ready').glob('*.gcode.3mf'))
    registration=verify_correction(baseline,native,prepared['white_correction_mm'])
    (JOB/'registration-verification.json').write_text(json.dumps(registration,indent=2)+'\n')
    supports_report=audit(path,'flat-nameplate-and-standard-receiver',profile=staged,include_unlabelled_support=True)
    supports_report['removal_access']='Receiver front is open. No support bead enters either wing slot, including its entry bevel. Plate has no supports.'
    supports_report['physical_removal_tested']=False
    (JOB/'support-audit.json').write_text(json.dumps(supports_report,indent=2)+'\n')
    result=json.loads((JOB/'ready/result.json').read_text());sliced,=result['sliced_plates']
    assert result['return_code']==0 and not sliced['warning_message'] and len(sliced['objects'])==2
    record={'pass':True,'printer':'Mark2','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'source_hashes_current':True,'plate_layers':plate_layers,'plate_support_paths':0,
            'wing_checks':wings,'raised_artwork_checks':artwork,'raised_perimeter':False,
            'fit_checks':fit_checks,'pure_axis_play_mm':prepared['seated_pure_axis_travel_mm'],
            'receiver_slot_support_checks':slot_checks,'receiver_support_summary':supports_report['summary'],
            'white_correction_mm':prepared['white_correction_mm'],'registration_verification':'registration-verification.json',
            'emitted_z_trim_mm':trims,'estimated_seconds':sliced['total_predication'],
            'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
            'submitted':False,'physical_qualification':'Manual insertion force, looseness, retention, QR scan and support removal await this pair.'}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','estimated_seconds','estimated_grams_saved_profile_density','pure_axis_play_mm','plate_support_paths')}))


if __name__=='__main__':main()
