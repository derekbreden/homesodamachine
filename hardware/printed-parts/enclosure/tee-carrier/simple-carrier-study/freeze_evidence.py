"""Verify completed native evidence and write its digest manifest; no CAD build."""
import ast
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
TOL=1e-5


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def read(name):return json.loads((HERE/name).read_text())
def require(ok,label):
    if not ok:raise ValueError(label)


def main():
    generators={
        'checks.json':'build_concept.py',
        'joint-motion-checks.json':'check_joint_motion.py',
        'wall-checks.json':'check_wall.py',
        'neighbor-checks.json':'check_neighbors.py',
        'valve-entry-checks.json':'check_valve_entry.py',
        'spring-capture-checks.json':'check_spring_capture.py',
        'access-checks.json':'check_access.py',
        'grip-stock-checks.json':'check_grip_stock.py',
        'section-stock-checks.json':'check_sections.py',
        'production-integration-checks.json':'check_production_integration.py'}
    reports={n:read(n) for n in generators}
    gen_sha=sha(HERE/'build_concept.py')
    for name,script in generators.items():
        j=reports[name]
        require(j['script_sha256']==sha(HERE/script),f'{name}: script changed')
        if name!='checks.json':
            require(j.get('generator_sha256',j.get('study_generator_sha256'))==gen_sha,f'{name}: study geometry source changed')
    for name in ('joint-motion-checks.json','neighbor-checks.json','valve-entry-checks.json','access-checks.json'):
        require(reports[name]['all_reported_native_readings_clear'],f'{name}: native check not clear')
    wall=reports['wall-checks.json']
    require(wall['all_reported_native_clearance_readings_clear'] and wall['opposed_guide_contact_at_every_stop'],'Wall/guide readings')
    require(reports['grip-stock-checks.json']['all_declared_regions_preserved'],'Preserved grip regions')
    spring=reports['spring-capture-checks.json']
    require(spring['continuous_final_seating_outside_envelope_overlap_mm3']<TOL,'Cup seating sweep')
    for r in spring['working']:
        require(all(r[k]<TOL for k in ('fixed_vs_moving_mm3','spring_envelope_vs_fixed_mm3','spring_envelope_vs_moving_mm3')),'Spring working clearance')
        require(r['gap_less_than_spring_od_mm']>0 and r['rigid_d6_ball_straight_lateral_escape_witness_overlap_mm3']>TOL,'Rigid lateral witness')
    for r in spring['loading']:
        require(r['fixed_overlap_mm3']<TOL and r['moving_overlap_mm3']<TOL,'Local pusher path')
    for r in spring['assembly']:require(r['fixed_cup_overlap_mm3']<TOL,'Cup assembly pose')
    production=reports['production-integration-checks.json']
    require(production['all_native_bodies_equal'] and production['selftest']['exit_code']==0,'Production geometry/selftest')
    for path,digest in production['source_sha256'].items():require(sha(REPO/path)==digest,f'Production source changed: {path}')
    for path,expected in production['owned_region_sha256'].items():
        source=(REPO/path).read_text();actual={}
        for node in ast.parse(source).body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in expected:
                actual[node.name]=hashlib.sha256(ast.get_source_segment(source,node).encode()).hexdigest()
        require(actual==expected,f'Owned production region changed: {path}')
    input_manifest=read('inputs/manifest.json')
    for row in input_manifest['files'].values():require(sha(HERE/'inputs'/row['path'])==row['sha256'],'Frozen blank input changed')
    placed=read('inputs/placed-neighbors/manifest.json')
    for row in placed['bodies'].values():require(sha(HERE/'inputs/placed-neighbors'/row['brep'])==row['sha256'],'Frozen neighbor changed')
    fixture=read('inputs/current-front-top/manifest.json')
    for name,digest in fixture['files'].items():require(sha(HERE/'inputs/current-front-top'/name)==digest,'Frozen wall changed')
    for name,digest in reports['checks.json']['outputs'].items():require(sha(HERE/name)==digest,f'Native output changed: {name}')
    for report in ('neighbor-checks.json','valve-entry-checks.json','access-checks.json'):
        require(reports[report]['neighbor_manifest_sha256']==sha(HERE/'inputs/placed-neighbors/manifest.json'),f'{report}: neighbors changed')
    sections=reports['section-stock-checks.json']
    minima=sections['sampled_minima'];ratios={}
    for axis in ('Iy_geometric_mm4','Iz_geometric_mm4'):
        ratios[axis]={'sampled_minimum_ratio':minima['concept'][axis]['value']/minima['screwed_reference'][axis]['value'],
            'least_local_ratio':min([{'x_mm':r['x_mm'],'ratio':r['concept'][axis]/r['screwed_reference'][axis]} for r in sections['rows']],key=lambda r:r['ratio'])}
        require(ratios[axis]['sampled_minimum_ratio']>=1,'Sampled section floor below frozen CAD reference')
    files={}
    for p in sorted(HERE.rglob('*')):
        if not p.is_file() or '__pycache__' in p.parts or p.name in ('artifact-manifest.json','.DS_Store'):continue
        files[str(p.relative_to(HERE))]={'bytes':p.stat().st_size,'sha256':sha(p)}
    manifest={
        'status':'native_geometry_ready_for_combined_enclosure_trial_build',
        'recorded_utc':datetime.now(timezone.utc).isoformat(),
        'scope':'Isolated native carrier and fixed-cup integration; combined enclosure generation, printable meshes and their actual slices are separate production evidence.',
        'physical_status':'Full-enclosure trial not yet observed. Spring feel, actual coil retention, snap fit, support removal and assembled rigidity are trial outcomes.',
        'source_sha256':production['source_sha256'],
        'owned_region_sha256':production['owned_region_sha256'],
        'native_readings':{'production_selftest_exit':0,'production_added_missing_volume_mm3':0,
            'joint_continuous_sweeps':len(reports['joint-motion-checks.json']['continuous_rigid_sweeps']),
            'joint_deflection_witnesses':len(reports['joint-motion-checks.json']['elastic_wall_clearance']),
            'wall_half_sweeps':len(wall['rigid_installation']),'held_spring_tool_sweeps':len(wall['tool_installation']),
            'pusher_removal_sweeps':len(wall['pusher_withdrawal']),'working_wall_states':len(wall['working']),
            'opposed_guide_contacts':len(wall['guide_contact_witnesses']),
            'working_neighbor_readings':len(reports['neighbor-checks.json']['operating']),
            'tee_entry_sweeps':len(reports['neighbor-checks.json']['tee_assembly_sweeps']),
            'lower_valve_entry_sweeps':len(reports['valve-entry-checks.json']['sweeps']),
            'declared_tie_passages':len(reports['access-checks.json']['tie_passages']),
            'fixed_cup_neighbor_readings':len(reports['access-checks.json']['fixed_cup_neighbors'])},
        'section_moment_ratios':ratios,
        'section_scope':'Geometric stock only. Improved sampled minima do not imply uniform local improvement or assembled stiffness.',
        'files':files}
    (HERE/'artifact-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    print(json.dumps({'status':manifest['status'],'files':len(files),'native_readings':manifest['native_readings'],'section_ratios':ratios},indent=2))


if __name__=='__main__':main()
