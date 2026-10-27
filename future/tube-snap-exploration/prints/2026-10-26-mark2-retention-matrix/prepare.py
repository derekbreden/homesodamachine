"""Offline Mark2 preparation of three separate retention strips; never submit.

Run manually with tools/cad-venv/bin/python. Retains the current shared PET-GF
factory-tools process, changing only source geometry, yaw and bed border.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import math
from pathlib import Path
import sys
import zipfile

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools').is_dir())
SHARED=ROOT/'hardware/printed-parts/enclosure/trial-preparation'
STUDY=HERE.parents[1]
PIECE='tube-snap-retention-matrix'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def save(path,value):
    path.write_text(json.dumps(value,indent=2)+'\n')


def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    result=importlib.util.module_from_spec(spec)
    sys.modules[name]=result
    spec.loader.exec_module(result)
    return result


def source_binding():
    report_path=STUDY/'retention-matrix-geometry.json'
    report=json.loads(report_path.read_text())
    expected={report['source']:report['source_sha256'],**report['files']}
    actual={name:sha(ROOT/name)for name in expected}
    if actual!=expected:
        raise ValueError('Matrix report does not bind current source/STEP/STL')
    rows=report['samples']
    if len(rows)!=9 or {r['label']for r in rows}!={r+c for r in 'ABC'for c in '123'}:
        raise ValueError('Expected all nine A1 through C3 identities')
    for row in rows:
        if abs(row['bore_diameter_mm']-6.55)>1e-7:
            raise ValueError('All nine bores must retain the prior smallest diameter6.55')
        thickness={'A':1.44,'B':1.92,'C':2.40}[row['label'][0]]
        tip=120.42102606277044+5*(int(row['label'][1])-1)
        if abs(row['spring_wall_mm']-thickness)>1e-7 or abs(row['tip_angle_deg']-tip)>1e-7:
            raise ValueError('Matrix dimensions do not match requested row/column factors')
    a1=next(r for r in rows if r['label']=='A1')
    old=json.loads((STUDY/'geometry-report.json').read_text())['samples'][0]
    for key in ['bore_diameter_mm','spring_wall_mm','tip_angle_deg','outer_radius_mm']:
        if abs(a1[key]-old[key])>1e-7:
            raise ValueError(f'A1 differs from previous smallest snap: {key}')
    return {**actual,relative(report_path):sha(report_path)}


def declaration():
    shared_path=SHARED/'pieces.json'
    shared=json.loads(shared_path.read_text())
    spec={k:copy.deepcopy(v)for k,v in shared.items()if k!='pieces'}
    piece=copy.deepcopy(shared['pieces']['factory-tools'])
    piece.update(parts=[{'stl':relative(STUDY/'parts'/f'tube-snap-row-{row}-print.stl'),
                         'name':f'tube-snap-row-{row}'}for row in 'abc'],
                 yaw_degrees=0,plate_border_mm=80,spacing_mm=2,
                 placement_offsets_xy_mm=[[0,-18],[0,0],[0,18]],
                 placement_reason='Three separate60 x16 mm strips share a centered plate with2 mm gaps; source+X faces printer right.')
    spec['pieces']={PIECE:piece}
    spec['source_declaration']=relative(shared_path)
    spec['source_declaration_sha256']=sha(shared_path)
    save(HERE/'job.json',spec)


def summarize(directory,binding,review):
    prep=json.loads((directory/'preparation.json').read_text())
    archive=ROOT/prep['archive']
    native=json.loads((directory/'slice-result.json').read_text())
    plate=native['sliced_plates'][0]
    previews=[]
    with zipfile.ZipFile(archive)as sliced:
        settings=json.loads(sliced.read('Metadata/project_settings.config'))
        for name in sliced.namelist():
            if name.startswith('Metadata/')and name.endswith('.png'):
                destination=directory/Path(name).name
                destination.write_bytes(sliced.read(name))
                previews.append(relative(destination))
    if binding!=source_binding():
        raise ValueError('Matrix geometry inputs changed during offline slice')
    result={
        'status':'Offline native preparation/review; printer submission not performed.',
        'submitted':False,'source_sha256':binding,'preparer_sha256':sha(Path(__file__)),
        'directory':relative(directory),'project':prep['project'],
        'project_sha256':prep['project_sha256'],'archive':prep['archive'],
        'archive_sha256':prep['archive_sha256'],'profile':prep['profile'],
        'profile_sha256':prep['profile_sha256'],'printer':prep['printer'],
        'nozzle':prep['nozzle'],'material':prep['material'],
        'requested_z_trim_mm':prep['requested_z_trim_mm'],
        'emitted_z_trim_mm':review['emitted_z_trim_mm'],
        'process':{key:settings.get(key)for key in (
            'wall_loops','sparse_infill_density','sparse_infill_pattern','layer_height',
            'initial_layer_print_height','enable_support','support_type','support_style',
            'brim_type','brim_width','filament_colour','filament_map','curr_bed_type',
            'overhang_fan_threshold','overhang_fan_speed')},
        'model_pose':'Three separate60 x16 x3 mm floors flat on bed; tube axes Y, mouths +Z; A front atY-18, B middle atY0, C back atY+18 relative to bed center; columns1 left/2 middle/3 right.',
        'identity':{'rows_spring_mm':{'A':1.44,'B':1.92,'C':2.40},
                    'columns_per_wing_degrees':{'1':120.42102606277044,
                                               '2':125.42102606277044,
                                               '3':130.42102606277044},
                    'all_bores_diameter_mm':6.55},
        'estimated_seconds':plate['total_predication'],
        'estimated_filament_g':sum(float(f['total_used_g'])for f in plate['filaments']),
        'filaments':plate['filaments'],'slicer_warnings':plate.get('warning_message'),
        'native_preview_images':previews,'native_review':relative(directory/'review.json'),
        'native_review_pass':review['pass'],
        'minimum_bead_margin_mm':review['minimum_bed_margin_mm'],
        'first_second_layer_stack':review['first_second_layer_stack'],
        'support_topology':review['support_topology'],
        'physical_evaluation':'Compare insertion, wing/root survival, grip, axial slide and removal on actual1/4-inch tube. No force or life prediction.'}
    save(HERE/'offline-review.json',result)
    print(json.dumps(result,indent=2),flush=True)


def main():
    binding=source_binding()
    declaration()
    preparer=module('retention_matrix_shared_prepare',SHARED/'prepare.py')
    reader=module('retention_matrix_shared_review',SHARED/'review.py')
    preparer.SPEC_PATH=HERE/'job.json'
    def strip_layout(footprints,usable_low,usable_high,spacing,yaw):
        if len(footprints)!=3 or any(abs(dx-60)>1e-4 or abs(dy-16)>1e-4 for dx,dy in footprints):
            raise ValueError('Expected three independent60 x16 mm strips')
        cx,cy=(usable_low+usable_high)/2
        return [(0,float(cx),float(cy+offset))for offset in (-18,0,18)]
    preparer.layout=strip_layout
    if len(sys.argv)==2:
        directory=Path(sys.argv[1]).resolve()
    else:
        directory=preparer.prepare(PIECE,output=HERE)
        preparer.slice_project(directory)
    reviewed=reader.review(directory)
    summarize(directory,binding,reviewed)


if __name__=='__main__':
    main()
