"""Prepare the combined cooled snap trial; does not submit a printer job.

Cooling overrides are local to this experimental plate and its embedded filament
preset. The shared PET-GF source profile remains unchanged.
"""
from pathlib import Path
import copy
import hashlib
import importlib.util
import json
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
SHARED=ROOT/'hardware/printed-parts/enclosure/trial-preparation'
TUBE=ROOT/'future/tube-snap-exploration'
CABLE=ROOT/'future/cable-clip-exploration'
PIECE='tube-and-cable-snaps-wall9-cooled'
COOLING={
    'fan_min_speed':['100'],'fan_max_speed':['100'],
    'reduce_fan_stop_start_freq':['1'],
    'close_fan_the_first_x_layers':['3'],'full_fan_speed_layer':['4'],
    'enable_overhang_bridge_fan':['1'],'overhang_fan_speed':['100'],
    'additional_cooling_fan_speed':['0'],
    'slow_down_for_layer_cooling':['1'],'slow_down_layer_time':['20'],
    'slow_down_min_speed':['5'],'no_slow_down_for_cooling_on_outwalls':['0'],
}
COOLING_REASON="Derek reports a melty upright cable hook and requests major part cooling and time between layers on the combined 9 mm-wall trial. This plate alone uses full part cooling after three bed layers and a 20-second layer target."


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    obj=importlib.util.module_from_spec(spec)
    sys.modules[name]=obj
    spec.loader.exec_module(obj)
    return obj


def source_binding():
    tube_path=TUBE/'c2-bore-geometry.json'
    cable_path=CABLE/'wall9-span-geometry.json'
    tube=json.loads(tube_path.read_text())
    cable=json.loads(cable_path.read_text())
    expected={tube['source']:tube['source_sha256'],**tube['files'],**tube['provenance'],
              cable['source']:cable['source_sha256'],**cable['files'],**cable['original_input_sha256']}
    actual={name:sha(ROOT/name) for name in expected}
    if actual!=expected:
        raise ValueError('The geometry reports must bind every current source and export')
    if [s['bore_diameter_mm'] for s in tube['samples']]!=[6.55,6.45,6.35]:
        raise ValueError('The requested C2 bore trio must remain unchanged')
    for sample in tube['samples']:
        if abs(sample['spring_wall_mm']-2.4)>1e-7 or abs(sample['tip_angle_deg']-125.42102606277044)>1e-7:
            raise ValueError('All tube clips retain C2 wing thickness and wrap')
    if [v['span_along_cable_mm'] for v in cable['variants']]!=[16.,24.]:
        raise ValueError('Two cable span variants are required')
    for variant in cable['variants']:
        if variant['dimensions']['host_wall_mm']!=9 or not variant['native_cross_section_comparison']['identical']:
            raise ValueError('Cable coupons require 9 mm walls and the accepted cross-section')
    return {**actual,relative(tube_path):sha(tube_path),relative(cable_path):sha(cable_path)}


def declaration():
    base_path=SHARED/'pieces.json'
    base=json.loads(base_path.read_text())
    spec={k:copy.deepcopy(v) for k,v in base.items() if k!='pieces'}
    piece=copy.deepcopy(base['pieces']['factory-tools'])
    settings={key:{'value':value,'reason':COOLING_REASON} for key,value in COOLING.items()}
    settings.update(
        brim_type={'value':'no_brim','reason':'Three broad model footprints provide bed attachment; no added brim.'},
        brim_width={'value':'0','reason':'No brim on this plate.'},
        print_sequence={'value':'by layer','reason':'Print all pieces on every layer to provide cooling time between returns to a cable hook.'})
    piece.update(parts=[
        {'stl':relative(TUBE/'parts/tube-snap-c2-three-bores.stl'),'name':'Tube-C2-6.55-6.45-6.35'},
        {'stl':relative(CABLE/'parts/relay-ribbon-wall9-span16.stl'),'name':'Cable-wall9-span16'},
        {'stl':relative(CABLE/'parts/relay-ribbon-wall9-span24.stl'),'name':'Cable-wall9-span24'}],
        yaw_degrees=0,plate_border_mm=80,settings=settings,
        placement_offsets_xy_mm=[[0,-28],[-18,12],[18,12]],
        placement_reason='Centered group: tube strip at front, cable span16 rear-left and span24 rear-right. Each object keeps its source axes, mouths upward, and layer-by-layer printing.')
    spec['pieces']={PIECE:piece}
    spec['source_declaration']=relative(base_path)
    spec['source_declaration_sha256']=sha(base_path)
    save(HERE/'job.json',spec)


def main():
    binding=source_binding()
    declaration()
    preparer=module('combined_snap_shared_prepare',SHARED/'prepare.py')
    reader=module('combined_snap_shared_review',SHARED/'review.py')
    preparer.SPEC_PATH=HERE/'job.json'
    original_profile=preparer._native.profile_settings
    def experiment_profile(*args,**kwargs):
        profile=original_profile(*args,**kwargs)
        # Keep the embedded filament preset consistent with this plate's explicit
        # project overrides, so an editable re-slice retains the same experiment.
        for name,payload in list(profile['members'].items()):
            if name.startswith('Metadata/filament_settings_') and name.endswith('.config'):
                settings=json.loads(payload)
                settings.update(copy.deepcopy(COOLING))
                profile['members'][name]=(json.dumps(settings,indent=2)+'\n').encode()
        return profile
    preparer._native.profile_settings=experiment_profile
    def combined_layout(footprints,usable_low,usable_high,spacing,yaw):
        expected=((60,16),(14.2,28),(14.2,36))
        if len(footprints)!=3 or any(abs(a-c)>1e-3 or abs(b-d)>1e-3 for (a,b),(c,d) in zip(footprints,expected)):
            raise ValueError('Combined source footprint dimensions changed')
        cx,cy=(usable_low+usable_high)/2
        return [(0,float(cx+x),float(cy+y)) for x,y in ((0,-28),(-18,12),(18,12))]
    preparer.layout=combined_layout
    if len(sys.argv)==2:
        directory=Path(sys.argv[1]).resolve()
    else:
        directory=preparer.prepare(PIECE,output=HERE)
        preparer.slice_project(directory)
    review=reader.review(directory)
    prep=json.loads((directory/'preparation.json').read_text())
    result=json.loads((directory/'slice-result.json').read_text())['sliced_plates'][0]
    with zipfile.ZipFile(ROOT/prep['archive']) as archive:
        settings=json.loads(archive.read('Metadata/project_settings.config'))
        for name in archive.namelist():
            if name.startswith('Metadata/') and name.endswith('.png'):
                (directory/Path(name).name).write_bytes(archive.read(name))
    if binding!=source_binding():
        raise ValueError('The geometry changed during preparation')
    if sha(ROOT/prep['profile'])!=prep['profile_sha256']:
        raise ValueError('The shared source profile changed during this experiment')
    overview=dict(status='Offline reviewed plate; no printer submission.',submitted=False,
        source_sha256=binding,preparer_sha256=sha(Path(__file__)),directory=relative(directory),
        project=prep['project'],project_sha256=prep['project_sha256'],
        archive=prep['archive'],archive_sha256=prep['archive_sha256'],
        profile=prep['profile'],profile_sha256=prep['profile_sha256'],
        printer=prep['printer'],nozzle=prep['nozzle'],material=prep['material'],
        requested_z_trim_mm=prep['requested_z_trim_mm'],emitted_z_trim_mm=review['emitted_z_trim_mm'],
        estimated_seconds=result['total_predication'],
        estimated_filament_g=sum(float(f['total_used_g']) for f in result['filaments']),
        process={k:settings.get(k) for k in list(COOLING)+['layer_height','initial_layer_print_height',
            'print_sequence','brim_type','brim_width','enable_support','support_type','support_style',
            'wall_loops','sparse_infill_density','filament_colour','filament_map','curr_bed_type']},
        native_review_pass=review['pass'],minimum_bead_margin_mm=review['minimum_bed_margin_mm'],
        first_second_layer_stack=review['first_second_layer_stack'],support_topology=review['support_topology'],
        model_pose='Tube floor flat; cable coupons upright entry-up on9mm walls; all three objects printed by layer.',
        physical_evaluation='Tube diameters compare under the same experimental cooling recipe, including C2 control. Cable cooling, shape, fit and spring survival require physical review.')
    save(HERE/'offline-review.json',overview)
    print(json.dumps({k:v for k,v in overview.items() if k!='source_sha256'},indent=2),flush=True)


if __name__=='__main__':
    main()
