"""Manual verification of the approved complete-faucet production project."""
from collections import Counter,defaultdict
from datetime import datetime,timezone
from pathlib import Path
from zipfile import ZipFile
import hashlib,json,re,shutil,sys
import xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
INDUSTRIAL=HERE.parents[1]
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_print.py').is_file())
sys.path.insert(0,str(INDUSTRIAL))
import prepare_print_project as production
from review_rim_supports import material_review
writer=production.writer
NATIVE=ROOT/'.cache/faucet-production-first020-20261025/native'
PROJECT=INDUSTRIAL/'faucet-industrial-petgf.3mf'


def main():
    report=json.loads(PROJECT.with_suffix('.print.json').read_text())
    audit=json.loads(PROJECT.with_suffix('.support-audit.json').read_text())
    archive=INDUSTRIAL/'faucet-industrial-petgf.gcode.3mf'
    shutil.copyfile(NATIVE/archive.name,archive)
    selection=json.loads((INDUSTRIAL/'production-selection.json').read_text())
    assert [p['stl_sha256'] for p in report['parts']]==[p['stl_sha256'] for p in selection['parts']]
    with ZipFile(PROJECT) as prepared,ZipFile(archive) as native,ZipFile(ROOT/selection['settings_source']) as accepted:
        settings=prepared.read(writer.SETTINGS_MEMBER)
        accepted_settings=json.loads(accepted.read(writer.SETTINGS_MEMBER))
        prepared_settings=json.loads(settings)
        changes={k:{'from':accepted_settings.get(k),'to':prepared_settings.get(k)}
                 for k in set(accepted_settings)|set(prepared_settings)
                 if accepted_settings.get(k)!=prepared_settings.get(k)}
        assert changes=={'initial_layer_print_height':{'from':'0.24','to':'0.2'}},changes
        assert float(json.loads(native.read(writer.SETTINGS_MEMBER))['initial_layer_print_height'])==.20
        assert not ET.fromstring(prepared.read('Metadata/layer_config_ranges.xml')).findall('object')
        commands=native.read('Metadata/plate_1.gcode')
        assert hashlib.md5(commands).hexdigest()==native.read('Metadata/plate_1.gcode.md5').decode().strip().lower()
        assert hashlib.sha256(commands).hexdigest()==audit['parts'][0]['inputs']['plate_gcode_sha256']
        full={'prepared_project_settings':json.loads(settings),'native_project_settings':json.loads(native.read(writer.SETTINGS_MEMBER)),
              'prepared_xml':{n:prepared.read(n).decode() for n in ['Metadata/model_settings.config','Metadata/layer_config_ranges.xml']},
              'native_xml':{n:native.read(n).decode() for n in ['Metadata/model_settings.config','Metadata/layer_config_ranges.xml'] if n in native.namelist()},
              'filament_presets':{n:native.read(n).decode() for n in native.namelist() if n.startswith('Metadata/filament_settings_')}}
        # The per-part process dictionaries match the approved five-part print.
        with ZipFile(ROOT/'hardware/printed-parts/faucet/industrial/prints/2026-10-24-buttons-sculpted-bands020-mark2/2026-10-24-industrial-sculpted-buttons-bands020v2-black-left04-z004-mark2.3mf') as reference:
            def per_object(payload):
                return {o.find("metadata[@key='name']").get('value'):{m.get('key'):m.get('value') for m in o.findall('metadata') if m.get('key')}
                        for o in ET.fromstring(payload).findall('object')}
            assert per_object(prepared.read('Metadata/model_settings.config'))==per_object(reference.read('Metadata/model_settings.config'))
    material,_=material_review(NATIVE/'plate_1.gcode',report,localized_cooling=True,first_three_max_z=.68)
    zvalues=[float(z) for z in re.findall(rb'^; Z_HEIGHT: ([-+0-9.]+)',commands,re.M)]
    increments=Counter(round(b-a,5) for a,b in zip([0.]+zvalues,zvalues))
    assert zvalues[0]==.20 and increments[.20]==1 and set(increments)=={.20,.24},increments
    declared=Counter(float(h) for h in re.findall(rb'^; LAYER_HEIGHT: ([-+0-9.]+)',commands,re.M))
    trim=[float(v) for v in re.findall(rb'^\s*G29\.1 Z([-+0-9.]+)',commands,re.M)]
    assert trim==[0.,.02],trim
    by_part=defaultdict(set);z=0.;obj=None;feature=''
    names={p['identify_id']:p['name'] for p in report['parts']}
    for line in commands.decode().splitlines():
        if line.startswith('; Z_HEIGHT:'):z=float(line.split(':',1)[1])
        elif line.startswith('; FEATURE:'):feature=line.split(':',1)[1].strip()
        elif line.startswith('; OBJECT_ID:'):obj=int(line.split(':',1)[1])
        elif line.startswith('; start printing object, unique label id:'):obj=int(line.rsplit(':',1)[1])
        elif line.startswith('; stop printing object'):obj=None
        elif obj in names and 'Support' not in feature and re.match(r'G[123] ',line):
            e=re.search(r' E([-+]?(?:\d+(?:\.\d*)?|\.\d+))',line)
            if e and float(e[1])>0:by_part[names[obj]].add(z)
    layers={name:{'first_z_mm':min(v),'last_z_mm':max(v),'model_layer_count':len(v),
                  'z_increment_counts_mm':dict(Counter(round(b-a,5) for a,b in zip([0.]+sorted(v),sorted(v))))} for name,v in by_part.items()}
    assert all(row['first_z_mm']==.20 and row['z_increment_counts_mm'].get(.20)==1
               and set(row['z_increment_counts_mm'])=={.20,.24} for row in layers.values()),layers
    (HERE/'all-settings.json').write_text(json.dumps(full,indent=2)+'\n')
    result={'recorded_at_utc':datetime.now(timezone.utc).isoformat(),'project_sha256':writer.digest(PROJECT.read_bytes()),
            'archive':str(archive.relative_to(ROOT)),'archive_sha256':writer.digest(archive.read_bytes()),
            'gcode_sha256':hashlib.sha256(commands).hexdigest(),'embedded_checksum_matches':True,
            'approved_geometry_sources_match':True,'project_settings_match_accepted_print_byte_for_byte':False,
            'intentional_settings_changes_from_accepted_print':changes,'other_settings_match_accepted_print':True,
            'object_process_overrides_match_accepted_complete_print':True,'variable_layer_ranges':[],
            'first_bed_layer_height_mm':.20,'normal_layer_height_mm':.24,
            'total_layer_planes':len(zvalues),'layer_increments_mm':dict(increments),
            'declared_feature_bead_heights_mm':dict(declared),
            'bead_height_scope':'Per-feature extrusion cross-sections include support and thick-bridge bead heights and floating-point quantization. Build-plane and per-part model increments are separately verified at 0.20 mm for the first bed layer and 0.24 mm afterward.',
            'part_layer_planes':layers,'emitted_trim_values_mm':trim,
            'material_commands':material,'plates':audit['plates'],'fit':audit['fit'],
            'scope':'Offline complete production slice of the exact approved source meshes, Bambu default 0.20 mm first layer and 0.24 mm later layers without fine bands. No printer submission. The accepted remaining corner gap is retained.'}
    (HERE/'native-review.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['total_layer_planes','part_layer_planes','plates','emitted_trim_values_mm']},indent=2),flush=True)


if __name__=='__main__':main()
