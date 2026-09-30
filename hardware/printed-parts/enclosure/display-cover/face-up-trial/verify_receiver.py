"""Check receiver-only native paths and bed-rooted trees beneath both open pockets."""
import hashlib,json,re,sys,zipfile
from pathlib import Path
import prepare_receiver as prep

ROOT,HERE,JOB=prep.ROOT,prep.HERE,prep.JOB
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(HERE.parents[1]/'nameplate')]
from verify_round_layer_band import wall_layers
from verify_mark2_print import segments
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
    with zipfile.ZipFile(prep.PROFILE) as z:shared=json.loads(z.read('Metadata/project_settings.config'))
    support_keys=[k for k in shared if k.startswith(('support_','tree_support_')) or k in ('enable_support','independent_support_layer_height')]
    diff={k:[shared[k],settings[k]] for k in support_keys if shared[k]!=settings[k]}
    assert set(diff)=={'support_filament','support_interface_filament'}
    for k,v in {'initial_layer_print_height':'0.2','layer_height':'0.24','filament_nozzle_map':['0'],
                'filament_colour':['#000000'],'nozzle_diameter':['0.4','0.4'],
                'support_type':'tree(auto)','wall_sequence':'inner wall/outer wall',
                'is_infill_first':'0','infill_wall_overlap':'15%'}.items():assert settings[k]==v,(k,settings[k])
    trims=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)];assert trims==[0.,.16]
    path=JOB/'ready/plate_1.gcode';path.write_bytes(gc)
    roads=list(segments(path));assert {r['object'] for r in roads}=={1901} and {r['tool'] for r in roads}=={0}
    layers=wall_layers(native,1901)
    assert layers[0]==(.2,.2) and all(abs(h-.24)<1e-5 for z,h in layers[1:])
    support=audit(path,'display-open-wing-receiver',profile=staged,include_unlabelled_support=True)
    support['physical_removal_tested']=False
    support['removal_access']='Both wing-pocket roofs have continuous print-down exits through the frame. Verify tree breakup and removal on the physical coupon.'
    (JOB/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    assert support['summary']['model_rooted_bodies']==0,support['summary']
    assert support['summary']['bed_rooted_bodies']>0
    geometry=json.loads((HERE/'geometry-check.json').read_text())
    assert all(x['print_down_blocked_volume_mm3']<1e-6 for x in geometry['support_exit_checks'])
    assert json.loads((HERE/'insertion-envelope.json').read_text())['pass']
    result=json.loads((JOB/'ready/result.json').read_text());assert result['return_code']==0
    sliced,=result['sliced_plates'];assert not sliced['warning_message']
    record={'pass':True,'printer':'H2C','native_archive':str(native.relative_to(ROOT)),
            'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
            'source_hashes_current':True,'model_layer_count':len(layers),'emitted_z_trim_mm':trims,
            'support_profile_differences':diff,'support_summary':support['summary'],
            'geometry_exit_checks':geometry['support_exit_checks'],
            'pure_axis_travel_mm':geometry['pure_axis_travel_mm'],'wing_tip_clearance_mm':prep.trial.TIP_AIR,
            'existing_cover_sha256':prepared['existing_cover_sha256'],
            'estimated_seconds':sliced['total_predication'],
            'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in sliced['filaments']),
            'submitted':False,'physical_qualification':'Support removal, fit, bow and retention need this physical receiver.'}
    (JOB/'verification.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps({k:record[k] for k in ('pass','support_summary','estimated_seconds')}))


if __name__=='__main__':main()
