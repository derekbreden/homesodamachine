"""Compare a native two-nozzle slice to its uncorrected nominal slice."""
import hashlib
import json
from pathlib import Path
import sys
import zipfile

from shapely.geometry import MultiLineString

ROOT=next(p for p in Path(__file__).resolve().parents if (p/'tools').is_dir())
sys.path.insert(0,str(ROOT/'hardware/printed-parts/enclosure/nameplate'))
from verify_mark2_print import segments


def verify(baseline, corrected, correction):
    archives=[]; road_sets=[]
    for archive in (baseline,corrected):
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            members={n:z.read(n) for n in z.namelist()}
        gc=members['Metadata/plate_1.gcode']
        assert hashlib.md5(gc).hexdigest()==members['Metadata/plate_1.gcode.md5'].decode().strip().lower()
        path=archive.parent/'plate_1.gcode';path.write_bytes(gc)
        road_sets.append(list(segments(path)))
        archives.append(members)
    model_members=[n for n in archives[0] if n.startswith('3D/')]
    assert model_members and all(archives[0][n]==archives[1][n] for n in model_members)
    settings=[json.loads(a['Metadata/project_settings.config']) for a in archives]
    changed={k:[settings[0].get(k),settings[1].get(k)] for k in set(settings[0])|set(settings[1])
             if settings[0].get(k)!=settings[1].get(k)}
    expected_offset=['0x0',f"{-correction['X']:g}x{-correction['Y']:g}"]
    assert changed=={'extruder_offset':[['0x0','0x0'],expected_offset]},changed
    for config in settings:
        assert config['filament_map']==['1','2'] and config['filament_nozzle_map']==['0','1']
        assert config['nozzle_diameter']==['0.4','0.4'] and config['enable_arc_fitting']=='0'
    # Native tower roads keep their machine-space endpoints. The first road
    # after each white-tool entry begins at the compensated travel position.
    towers=[[r for r in roads if r['feature']=='Prime tower'] for roads in road_sets]
    assert len(towers[0])==len(towers[1])
    tower_entries=[]
    for a,b in zip(*towers):
        assert all(a[k]==b[k] for k in ('tool','layer','width','b','extrusion_mm'))
        delta=[round(b['a'][i]-a['a'][i],6) for i in (0,1)]
        if delta!=[0.,0.]:
            assert a['tool']==1 and delta==[correction['X'],correction['Y']]
            tower_entries.append({'print_z_mm':a['layer'],'entry_displacement_mm':delta,
                                  'native_first_road_start_xy':b['a'],'native_first_road_end_xy':b['b']})
    assert len(tower_entries)==len({r['layer'] for r in towers[0] if r['tool']==1})
    checks=[]
    groups=[{(r['object'],r['tool'],r['layer']) for r in roads if r['feature']!='Prime tower'} for roads in road_sets]
    assert groups[0]==groups[1]
    for obj,tool,layer in sorted(groups[0]):
        original=[r for r in road_sets[0] if (r['object'],r['tool'],r['layer'])==(obj,tool,layer) and r['feature']!='Prime tower']
        actual=[r for r in road_sets[1] if (r['object'],r['tool'],r['layer'])==(obj,tool,layer) and r['feature']!='Prime tower']
        dx,dy=(correction['X'],correction['Y']) if tool==1 else (0.,0.)
        nominal=MultiLineString([(r['a'],r['b']) for r in original])
        normalized=MultiLineString([[(r[k][0]-dx,r[k][1]-dy) for k in ('a','b')] for r in actual])
        error=nominal.hausdorff_distance(normalized)
        length_error=abs(nominal.length-normalized.length)
        bounds_error=max(abs(a-b) for a,b in zip(nominal.bounds,normalized.bounds))
        # Native export quantizes XY to 0.001 mm and can reverse/resegment infill.
        assert error<.002 and bounds_error<.002 and length_error<.005,(tool,layer,error,length_error,bounds_error)
        checks.append({'object':obj,'tool':tool,'print_z_mm':layer,
                       'requested_displacement_mm':[dx,dy],
                       'baseline_segments':len(original),'corrected_segments':len(actual),
                       'normalized_path_hausdorff_mm':error,'normalized_bounds_error_mm':bounds_error,
                       'total_path_length_difference_mm':length_error})
    return {'pass':True,'baseline_archive':str(baseline.relative_to(ROOT)),
            'baseline_archive_sha256':hashlib.sha256(baseline.read_bytes()).hexdigest(),
            'corrected_archive_sha256':hashlib.sha256(corrected.read_bytes()).hexdigest(),
            'nominal_mesh_members_unchanged':model_members,
            'effective_setting_changes':changed,'native_purge_tower_endpoints_unchanged':True,
            'native_purge_tower_white_entries':tower_entries,
            'model_path_checks':checks,
            'maximum_normalized_path_error_mm':max(c['normalized_path_hausdorff_mm'] for c in checks),
            'physical_alignment':'Pending inspection of the printed nameplate; Y selection is tentative.'}
