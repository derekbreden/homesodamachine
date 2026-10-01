"""Read fresh enclosure toolpaths, including all labelled and unlabelled supports."""
from pathlib import Path
import argparse, hashlib, json, re, sys, zipfile
import xml.etree.ElementTree as ET
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
sys.path[:0]=[str(ROOT/'hardware/scripts'),str(ROOT/'hardware/printed-parts/faucet'),
             str(ROOT/'hardware/printed-parts/enclosure/nameplate')]
from enclosure_support_audit import audit
from verify_round_layer_band import wall_layers,check_span
import refresh_print_project as writer
from prepare_prints import JOBS
from verify_mark2_print import segments

sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def bead_bounds(path, identify_id):
    """Bound each linear extrusion with its own width plus 0.10 mm margin.

    The common reader pads the entire part by its widest bead. Here a broad
    internal solid-fill bead must not stand in for a narrow bed-edge tree bead.
    The segment reader rejects extrusion arcs; this profile disables them.
    """
    low, high = [float('inf')]*2, [-float('inf')]*2
    widest, count, extremes = 0., 0, {}
    for row in segments(path):
        if row['object'] != identify_id:
            continue
        width = row['width']
        assert width > 0, row
        widest = max(widest, width)
        count += 1
        for axis in (0,1):
            lo = min(row['a'][axis],row['b'][axis])-width/2-.1
            hi = max(row['a'][axis],row['b'][axis])+width/2+.1
            if lo < low[axis]:
                low[axis] = lo; extremes[f'min_{axis}'] = row
            if hi > high[axis]:
                high[axis] = hi; extremes[f'max_{axis}'] = row
    assert count
    return {'extrusion_bounds_xy_mm':[low,high], 'maximum_line_width_mm':widest,
            'additional_bounds_margin_mm':.1, 'extrusion_segment_count':count,
            'method':'Each G0/G1 extrusion plus its own half-width and 0.10 mm. Extruding arcs are rejected.',
            'extreme_segments':extremes}

def main(part):
    printer,trim,angle,directory,stem=JOBS[part]
    job=ROOT/'.cache/prints'/directory; ready=job/'ready'
    project=job/(stem+'-input.3mf');native=ready/(stem+'.gcode.3mf')
    report=json.loads((job/'preparation.json').read_text())
    assert sha(project)==report['project_sha256']
    assert sha(ROOT/report['parts'][0]['source'])==report['parts'][0]['stl_sha256']
    result=json.loads((ready/'result.json').read_text())
    assert result['return_code']==0,result
    plate,=result['sliced_plates'];assert not plate['warning_message'],plate['warning_message']
    assert len(plate['objects'])==1 and plate['objects'][0]['name']=='enclosure-'+part
    with zipfile.ZipFile(project) as a,zipfile.ZipFile(native) as b:
        assert b.testzip() is None
        before=json.loads(a.read(writer.SETTINGS_MEMBER));after=json.loads(b.read(writer.SETTINGS_MEMBER))
        differences={k:[before.get(k),after.get(k)] for k in before.keys()|after.keys() if before.get(k)!=after.get(k)}
        allowed={'filament_map_2':[None,['1']],'filament_prime_volume':[['30'],['45']]}
        assert all(allowed.get(k)==v for k,v in differences.items()),differences
        settings={'enable_support':'1','support_type':'tree(auto)','support_object_xy_distance':'0.4',
                  'support_top_z_distance':'0.45','support_bottom_z_distance':'0.3',
                  'support_filament':'1','support_interface_filament':'1',
                  'initial_layer_print_height':'0.2','layer_height':'0.24','wall_loops':'2','enable_arc_fitting':'0',
                  'is_infill_first':'0','wall_sequence':'inner wall/outer wall','infill_wall_overlap':'15%',
                  'filament_colour':['#000000'],'filament_nozzle_map':['0'],'nozzle_diameter':['0.4','0.4']}
        for k,v in settings.items():assert after[k]==v,(k,after[k],v)
        gc=b.read('Metadata/plate_1.gcode')
        assert b.read('Metadata/plate_1.gcode.md5').decode().strip().lower()==hashlib.md5(gc).hexdigest()
        (ready/'plate_1.gcode').write_bytes(gc)
        if 'Metadata/plate_1.png' in b.namelist():(job/'preview.png').write_bytes(b.read('Metadata/plate_1.png'))
        def ranges(payload):
            return [(float(r.get('min_z')),float(r.get('max_z')),{o.get('opt_key'):o.text for o in r.findall('option')}) for r in ET.fromstring(payload).findall('./object/range')]
        assert ranges(a.read('Metadata/layer_config_ranges.xml'))==ranges(b.read('Metadata/layer_config_ranges.xml'))
    trims=[float(z) for z in re.findall(rb'^\s*G29\.1 Z([-+.\d]+)',gc,re.M)]
    assert np.allclose(trims,[0,trim-.02]),trims
    by_z={}
    for z,h in wall_layers(native,1901):
        assert z not in by_z or abs(by_z[z]-h)<.001
        by_z[z]=round(h,3)
    layers=sorted(by_z.items());assert layers[0]==(.2,.2)
    rounds=([check_span(layers,'complete roof show rounds',187.392,195,.08,.001)] if part=='front-top'
            else [check_span(layers,'expanding roof chamfer and taper',.2,9.3,.24,.001)])
    assert all(row['pass'] for row in rounds),rounds
    runs=[]
    for z,h in layers:
        if not runs or abs(h-runs[-1]['height'])>.001:runs.append({'height':h,'bottom':round(z-h,4),'last_z':z,'count':1})
        else:runs[-1].update(last_z=z,count=runs[-1]['count']+1)
    assert [round(r['height'],2) for r in runs]==([.2,.24,.08] if part=='front-top' else [.2,.24]),runs
    global_width_bounds=writer.object_toolpaths(ready/'plate_1.gcode',ready/'support-labelled.gcode',1901)
    bounds=bead_bounds(ready/'plate_1.gcode',1901)
    area_low,area_high=np.array(report['shared_printable_area_mm'])
    low,high=np.array(bounds['extrusion_bounds_xy_mm']);margin=float(min(np.min(low-area_low),np.min(area_high-high)))
    # Model placement retains the preparer's 15 mm border. Sacrificial tree
    # bases are checked separately, including their full extrusion width.
    model_low,model_high=np.array(report['parts'][0]['plate_bounds_mm'])[:,:2]
    model_margin=float(min(np.min(model_low-area_low),np.min(area_high-model_high)))
    assert model_margin>=15 and margin>=10,(model_margin,margin)
    proof={'pass':True,'printer':printer,'native_archive':str(native.relative_to(ROOT)),
           'native_archive_sha256':sha(native),'gcode_sha256':hashlib.sha256(gc).hexdigest(),
           'project_sha256':sha(project),'source_step_sha256':sha(ROOT/report['parts'][0]['source'].replace('.stl','.step')),
           'native_export_normalizations':differences,'settings':settings,'emitted_z_trim_mm':trims,
           'rounds':rounds,'layer_count':len(layers),'layer_runs':runs,'toolpath_bounds':bounds,
           'conservative_global_width_bounds':global_width_bounds,
           'minimum_shared_bed_margin_mm':margin,'minimum_model_bed_margin_mm':model_margin,
           'required_model_margin_mm':15,'required_support_extrusion_margin_mm':10,
           'estimated_seconds':plate['total_predication'],
           'estimated_grams_saved_profile_density':sum(f['total_used_g'] for f in plate['filaments']),
           'support_removal_review_pending':True,'physical_full_enclosure_fit_tested':False,'submitted':False}
    (job/'verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:proof[k] for k in ('printer','layer_count','layer_runs','estimated_seconds','estimated_grams_saved_profile_density','minimum_shared_bed_margin_mm')},indent=2),flush=True)
    support=audit(ready/'support-labelled.gcode','enclosure-'+part,
                  ROOT/report['parts'][0]['source'],project,include_unlabelled_support=True)
    (job/'support-audit.json').write_text(json.dumps(support,indent=2)+'\n')
    print('SUPPORT',json.dumps(support['summary']),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('part',choices=JOBS)
    main(parser.parse_args().part)
