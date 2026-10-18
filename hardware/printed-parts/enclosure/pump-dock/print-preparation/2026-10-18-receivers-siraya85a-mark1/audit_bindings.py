"""Read-only final binding/credential audit; writes its evidence record only.

No slicing, path review, printer connection or submission is performed. Local
connection values are used only as in-memory forbidden-byte comparisons and
are never written to the evidence record or standard output.
"""
import ast
from datetime import datetime,timezone
import hashlib
import io
import json
from pathlib import Path
import shlex
import subprocess
import sys
import xml.etree.ElementTree as ET
import zipfile

import numpy as np
from scipy.spatial import cKDTree
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').is_file())
sys.path.insert(0,str(HERE))
from prepare import SOURCE,POSES
CORE='http://schemas.microsoft.com/3dmanufacturing/core/2015/02'
PROD='http://schemas.microsoft.com/3dmanufacturing/production/2015/06'
Q=lambda s:f'{{{CORE}}}{s}'


def sha(data):
    return hashlib.sha256(data).hexdigest()


def git_bytes(path):
    return subprocess.check_output(['git','show',':'+str(path.relative_to(ROOT))],cwd=ROOT)


def transform(points,encoded):
    values=np.array([float(x) for x in encoded.split()])
    return points@values[:9].reshape(3,3)+values[9:12]


def triangle_keys(faces):
    values=np.sort(faces,axis=1)
    return sorted(map(tuple,values.tolist()))


def embedded_receivers(data,expected):
    records=[]
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        model=ET.fromstring(z.read('3D/3dmodel.model'))
        config=ET.fromstring(z.read('Metadata/model_settings.config'))
        objects={x.get('id'):x for x in model.findall('./'+Q('resources')+'/'+Q('object'))}
        configs={x.get('id'):x for x in config.findall('object')}
        items=model.findall('./'+Q('build')+'/'+Q('item'))
        for idx,item in enumerate(items):
            object_id=item.get('objectid')
            normal_ids={x.get('id') for x in configs[object_id].findall('part') if x.get('subtype')=='normal_part'}
            normals=[c for c in objects[object_id].findall('./'+Q('components')+'/'+Q('component'))
                     if c.get('objectid') in normal_ids]
            if len(normals)!=1:raise ValueError('Expected exactly one printed receiver in each build item')
            component=normals[0]
            member=component.get(f'{{{PROD}}}path').lstrip('/')
            child=ET.fromstring(z.read(member))
            volume=child.find('./'+Q('resources')+'/'+Q('object')+f"[@id='{component.get('objectid')}']")
            mesh=volume.find(Q('mesh'))
            points=np.array([[float(v.get(k)) for k in 'xyz'] for v in mesh.find(Q('vertices'))])
            faces=np.array([[int(t.get(k)) for k in ('v1','v2','v3')] for t in mesh.find(Q('triangles'))])
            points=transform(points,component.get('transform','1 0 0 0 1 0 0 0 1 0 0 0'))
            world=transform(points,item.get('transform'))
            local=world-np.array([*POSES[idx],0.])
            distance,mapping=cKDTree(expected.vertices).query(local)
            same_vertices=len(local)==len(expected.vertices) and len(np.unique(mapping))==len(expected.vertices)
            same_faces=len(faces)==len(expected.faces) and triangle_keys(mapping[faces])==triangle_keys(expected.faces)
            error=float(distance.max())
            records.append(dict(build_object_id=int(object_id),source_triangle_count=len(expected.faces),
                embedded_triangle_count=len(faces),vertices_match_bijectively=same_vertices,
                triangle_connectivity_matches=same_faces,maximum_vertex_difference_mm=error,
                matches_rotated_canonical_stl=same_vertices and same_faces and error<.000002,
                plate_center_xy_mm=list(POSES[idx])))
    return records


def private_printer_values():
    values=set();checked=False
    config=Path.home()/'Library/Application Support/BambuStudio/BambuStudio.conf'
    if config.exists():
        payload=json.loads(config.read_text())
        codes=payload.get('access_code',{})
        if isinstance(codes,dict):
            values.update(str(x) for pair in codes.items() for x in pair if str(x))
            checked=True
    runner=Path.home()/'.config/h2c-gc/run.sh'
    if runner.exists():
        for line in runner.read_text().splitlines():
            if not line.lstrip().startswith(('gc ','gc\t')):continue
            words=shlex.split(line,comments=True)
            if len(words)==4 and words[0]=='gc':
                values.update(words[2:]);checked=True
    return [x.encode() for x in values if len(x)>=6],checked


def credential_fields(value,path=''):
    sensitive={'access_code','access_token','api_key','password','auth_token','authorization',
               'printer_ip','printer_host','print_host','device_id','device_serial','serial_number'}
    findings=[]
    if isinstance(value,dict):
        for key,child in value.items():
            location=path+'/'+str(key)
            if str(key).lower() in sensitive and child not in (None,'',[],{},False):
                findings.append(location)
            findings.extend(credential_fields(child,location))
    elif isinstance(value,list):
        for idx,child in enumerate(value):findings.extend(credential_fields(child,path+f'/{idx}'))
    return findings


def main():
    binding=json.loads((HERE/'source-bindings.json').read_text())
    readback=json.loads((HERE/'native-readback.json').read_text())
    bound={path:sha((ROOT/path).read_bytes())==digest for path,digest in binding['source_sha256'].items()}
    mesh=trimesh.load(SOURCE,force='mesh',process=True)
    mesh.vertices=mesh.vertices@np.array(((1,0,0),(0,0,-1),(0,1,0)),float).T
    expected_stl=readback['source_geometry_sha256']
    geometry=dict(current_canonical_stl_sha256=sha(SOURCE.read_bytes()),
                  prepared_canonical_stl_sha256=expected_stl,
                  canonical_stl_bytes_identical=sha(SOURCE.read_bytes())==expected_stl,
                  project_geometry_input='Canonical STL; receiver source module is a design-reference binding, not a second mesh input')
    archive_rows={};private,private_checked=private_printer_values()
    value_matches=[];field_matches=[];scanned_members=0
    staged_files=subprocess.check_output(['git','ls-files','--cached','-z','--',str(HERE.relative_to(ROOT))],cwd=ROOT).decode().split('\0')
    staged_identity={}
    for rel in (x for x in staged_files if x):
        path=ROOT/rel;data=git_bytes(path)
        staged_identity[rel]=sha(data)==sha(path.read_bytes())
        payloads=[(rel,data)]
        if path.suffix=='.3mf':
            with zipfile.ZipFile(io.BytesIO(data)) as z:
                payloads.extend((rel+'::'+name,z.read(name)) for name in z.namelist())
        for location,payload in payloads:
            scanned_members+=1
            if any(needle in payload for needle in private):value_matches.append(location)
            try:parsed=json.loads(payload)
            except (ValueError,UnicodeDecodeError):continue
            field_matches.extend(location+'::'+field for field in credential_fields(parsed))
    for key in ('project','archive'):
        path=HERE/readback[key];staged=git_bytes(path)
        rows=embedded_receivers(staged,mesh)
        archive_rows[key]=dict(file=path.name,staged_sha256=sha(staged),working_sha256=sha(path.read_bytes()),
            bytes_match_original_preparation=sha(staged)==readback[key+'_sha256'],
            normal_volume_count=len(rows),all_receivers_match_canonical_stl=all(r['matches_rotated_canonical_stl'] for r in rows),
            receiver_meshes=rows)
    receiver=ROOT/'hardware/printed-parts/enclosure/pump-dock/pump_receiver.py'
    current=receiver.read_bytes()
    reference_path=HERE/'input-snapshots/receiver-source-reference.py.txt'
    reference=reference_path.read_bytes()
    def without_record(data):
        tree=ast.parse(data)
        tree.body=[n for n in tree.body if not isinstance(n,ast.FunctionDef) or n.name!='engineering_record']
        return ast.dump(tree,include_attributes=False)
    def without_print_neutral_fields(data):
        tree=ast.parse(data)
        tree.body=[n for n in tree.body
            if not (isinstance(n,ast.FunctionDef) and n.name=='engineering_record')
            and not (isinstance(n,ast.Assign) and any(
                isinstance(t,ast.Name) and t.id=='KEEPER_Y' for t in n.targets))]
        return ast.dump(tree,include_attributes=False)
    constants={}
    for node in ast.parse(current).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='KEEPER_Y' for t in node.targets):
            constants['keeper_axial_stations_mm']=list(ast.literal_eval(node.value))
    for node in ast.parse(reference).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='KEEPER_Y' for t in node.targets):
            constants['reference_keeper_axial_stations_mm']=list(ast.literal_eval(node.value))
    report=dict(audited_at=datetime.now(timezone.utc).isoformat(),
        scope='Current source/STL, embedded staged meshes and staged print-preparation credential audit; no slicing, path QA repeat or printer contact',
        all_existing_source_bindings_match_current_files=all(bound.values()),bound_file_identity=bound,
        geometry_identity=geometry,project_archive_identity=archive_rows,
        receiver_source=dict(current_sha256=sha(current),bound_sha256=binding['source_sha256'][str(receiver.relative_to(ROOT))],
            current_source_matches_bound=True if sha(current)==binding['source_sha256'][str(receiver.relative_to(ROOT))] else False,
            **constants,retained_reference_snapshot=str(reference_path.relative_to(HERE)),retained_reference_sha256=sha(reference),
            executable_source_excluding_engineering_record_identical_to_reference=without_record(current)==without_record(reference),
            executable_source_excluding_engineering_record_and_KEEPER_Y_identical_to_reference=without_print_neutral_fields(current)==without_print_neutral_fields(reference),
            dry_datum_delta_matches_review=constants['reference_keeper_axial_stations_mm']==[7.0,9.85] and constants['keeper_axial_stations_mm']==[7.0,10.0],
            source_delta_scope='engineering_record metadata and the dry KEEPERY assignment only. The retained reference has Y7.0..9.85; the current 3 mm keeper has Y7.0..10.0. All remaining executable AST, canonical wet STL bytes and eight embedded receiver meshes retain independent identity checks.'),
        staged_file_working_identity=staged_identity,
        credential_audit=dict(staged_payloads_scanned=scanned_members,
            known_local_private_printer_values_compared_in_memory=private_checked,
            known_private_value_matches=value_matches,nonempty_connection_or_credential_fields=field_matches,
            passed=private_checked and not value_matches and not field_matches,
            sensitive_values_recorded=False,printer_contacted=False),
        reran_slicer=False,repeated_path_qa=False,committed=False)
    (HERE/'binding-audit.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(dict(all_existing_source_bindings_match=all(bound.values()),
        canonical_stl_identical=geometry['canonical_stl_bytes_identical'],
        staged_embedded_meshes_match=all(row['all_receivers_match_canonical_stl'] for row in archive_rows.values()),
        staged_files_match_working=all(staged_identity.values()),credential_audit_passed=report['credential_audit']['passed'],
        no_slice_or_path_qa_repeated=True),indent=2),flush=True)


if __name__=='__main__':
    main()
