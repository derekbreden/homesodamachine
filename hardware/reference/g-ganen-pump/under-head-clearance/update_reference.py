"""Export the scan-supported rigid switch passage and the isolated study mesh.

Run manually through the shared CAD queue. Production integration exports are
separate and remain untouched. No routing part defines the rigid correction.
"""
from pathlib import Path
import copy
import hashlib
import json
import struct
import sys
import cadquery as cq
import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components

HERE = Path(__file__).resolve().parent
REF = HERE.parent
ROOT = REF.parents[2]
sys.path.insert(0, str(REF))
import g_ganen_pump as pump
sys.path.insert(0, str(ROOT/'hardware/scripts'))
from _cadq_export import export_assembly

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,v): p.write_text(json.dumps(v,indent=2)+'\n')
def bounds(s):
    b=s.BoundingBox()
    return [[b.xmin,b.ymin,b.zmin],[b.xmax,b.ymax,b.zmax]]
def mesh(s):
    v,f=s.tessellate(.08,.15)
    return np.array([[p.x,p.y,p.z] for p in v]),np.array(f,dtype=np.int32)

def study_mesh(parts):
    study = ROOT/'hardware/manifold-layout/studies/east-feed'
    frozen = ROOT/'hardware/manifold-layout/studies/stem-fittings'
    pose_source = study.parent/'wall-supported/study.json'
    scene = json.loads(pose_source.read_text())
    inst = next(i for i in scene['instances'] if i['name']=='pump')
    rotation = np.array([[0.,-1.,0.],[1.,0.,0.],[0.,0.,1.]])
    translation = np.array(inst['translation'])-rotation@pump.suction()[0]
    metadata=json.loads((frozen/'socket-layout.json').read_text())
    row=next(i for i in metadata['meshes'] if i['name']=='pump')
    with np.load(frozen/'socket-layout.npz') as source:
        v,f=source[row['vertices']],source[row['faces']]
    merged, remap = np.unique(np.round(v,4),axis=0,return_inverse=True)
    ff=remap[f]
    edges=np.vstack((ff[:,[0,1]],ff[:,[1,2]],ff[:,[2,0]]))
    graph=coo_matrix((np.ones(len(edges)),(edges[:,0],edges[:,1])),shape=(len(merged),len(merged))).tocsr()
    _,labels=connected_components(graph,directed=False)
    feet={}
    for label in np.unique(labels):
        mask=labels[remap[f[:,0]]]==label
        indices=np.unique(f[mask]);points=v[indices]
        lo,hi=points.min(0),points.max(0)
        if not (lo[2]<-26.7 and hi[2]<-8.2 and len(points)>100): continue
        # These are already flat installed poses, distinct from free scan poses.
        name=('rear_' if hi[1]<-80 else 'head_')+('yminus' if hi[0]<20 else 'yplus')
        lookup=np.full(len(v),-1,dtype=np.int32);lookup[indices]=np.arange(len(indices))
        world=points@np.array(inst['rotation']).T+inst['translation']
        feet[name+'_installed_rubber_slider'] = ((world-translation)@rotation,lookup[f[mask]])
    expected={'rear_yminus_installed_rubber_slider','head_yminus_installed_rubber_slider','head_yplus_installed_rubber_slider'}
    if set(feet)!=expected: raise ValueError('Frozen installed feet not identified uniquely: '+str(set(feet)))
    vv=[];ff=[];rows=[];offset=0
    for name, shape in parts.items():
        if 'rubber_slider' in name: continue
        a,b=mesh(shape);vv.append(a);ff.append(b+offset)
        rows.append({'name':name,'source':'Corrected native detailed reference','vertices':[offset,offset+len(a)]})
        offset+=len(a)
    for name,(a,b) in feet.items():
        vv.append(a);ff.append(b+offset)
        rows.append({'name':name,'source':'Frozen installed study foot, pose and geometry unchanged','vertices':[offset,offset+len(a)]})
        offset+=len(a)
    destination=study/'parts/pump-under-head.npz'
    np.savez_compressed(destination,v=np.vstack(vv),f=np.vstack(ff))
    report={'schema':1,'geometry':'Pump detailed rigid envelope with measured switch passage',
        'coordinate_frame':'Native pump reference, millimetres',
        'native_to_world':{'rotation':rotation.tolist(),'translation_mm':translation.tolist(),
            'derivation':'Exact selected-study pump suction datum minus rotated canonical suction tip. The frozen source preserves the yaw-only native axes.',
            'native_suction_tip_mm':list(pump.suction()[0]),'world_suction_tip_mm':inst['translation']},
        'parts':rows,'independent_foot':'rear_yplus_observed_rubber_slider_envelope is omitted; the study retains its separately translated pump-sliding-foot instance',
        'scope':'Twenty-two corrected detailed rigid parts and the frozen study three installed feet. Observed free-foot poses are not substituted for installed feet.',
        'input_sha256':{'hardware/manifold-layout/studies/stem-fittings/socket-layout.json':sha(frozen/'socket-layout.json'),
            'hardware/manifold-layout/studies/stem-fittings/socket-layout.npz':sha(frozen/'socket-layout.npz'),
            'hardware/manifold-layout/studies/wall-supported/study.json':sha(pose_source),
            'hardware/reference/g-ganen-pump/g_ganen_pump.py':sha(REF/'g_ganen_pump.py'),
            'hardware/reference/g-ganen-pump/under-head-clearance.json':sha(REF/'under-head-clearance.json')},
        'mesh_sha256':sha(destination),'tessellation':{'linear_deflection_mm':.08,'angular_tolerance_rad':.15}}
    dump(destination.with_name('pump-under-head-source.json'),report)
    print('Study mesh',destination,flush=True)

def run():
    prior=HERE/'prior-native-validation.json'
    if not prior.exists(): prior.write_bytes((REF/'native-validation.json').read_bytes())
    previous=json.loads(prior.read_text())
    parts=pump.build_parts()
    native=[]
    for name,shape in parts.items():
        if not shape.isValid() or len(shape.Solids())!=1: raise ValueError('Invalid native part '+name)
        native.append({'name':name,'valid':True,'solids':1,'faces':len(shape.Faces()),'bounds_mm':bounds(shape)})
    print('Native valid solids',len(native),flush=True)
    study_mesh(parts)
    assembly=cq.Assembly(name='g-ganen-pump')
    for name,shape in parts.items():
        color=((.18,.19,.20) if 'rubber_slider' in name else (.64,.67,.70) if 'round_head' in name or 'motor_can' in name else (.31,.34,.37))
        assembly.add(shape,name=name,color=cq.Color(*color))
    native_path=REF/'g-ganen-pump.step'
    export_assembly(assembly,native_path)
    with native_path.with_suffix('.step.mesh').open('rb') as stream:
        header=json.loads(stream.read(struct.unpack('<I',stream.read(4))[0]))
    if header['src']!=sha(native_path): raise ValueError('STEP and viewer payload disagree')
    # The broad old head/switch residuals include the corrected region and are
    # retained only in the explicit prior report. Other observed regions lie
    # outside the bounded removal; their geometry and comparisons are unchanged.
    report=copy.deepcopy(previous)
    report.update(status='native_valid_with_scan_supported_rigid_switch_passage',native_solids=native,
        reference_parameters_sha256=sha(REF/'reference-parameters.json'),
        verified_parameter_input_digests={**pump.parameters()['input_sha256'], **pump.parameters()['tool_sha256']},
        readings=[row for row in previous['readings'] if row['region']!='head_switch_outer_walls'],
        tool_sha256={'g_ganen_pump.py':sha(REF/'g_ganen_pump.py'),
            'under-head-clearance/update_reference.py':sha(Path(__file__)),
            'under-head-clearance/measure.py':sha(HERE/'measure.py')},
        input_sha256={'under-head-clearance.json':sha(REF/'under-head-clearance.json'),
            'under-head-clearance/prior-native-validation.json':sha(prior)},
        rigid_readings_provenance={
            'predecessor_validation':'under-head-clearance/prior-native-validation.json',
            'sha256':sha(prior),
            'basis':'Retained residuals sample unchanged regions outside the bounded rigid switch correction. The broad head_switch_outer_walls readings are excluded from the current report.',
            'current_switch_evidence':'under-head-clearance.json',
            'evidence_sha256':sha(REF/'under-head-clearance.json')},
        prior_residual_scope='Unchanged motor, lower cradle, crown and barb comparisons are retained from the prior report. The affected broad head/switch residuals are not claimed for this geometry.',
        rigid_switch_passage={'evidence':'under-head-clearance.json','native_operation':'Remove independently observed external air from rigid casing and switch convex envelope only',
            'validity':'Each corrected body remains one valid native solid',
            'same_parameters_outside_operation':True,'production_integration_envelope_changed':False},
        native_sha256=sha(native_path))
    report.pop('diagnostic_sha256',None)
    dump(REF/'native-validation.json',report)
    print('Canonical export',native_path,flush=True)

if __name__=='__main__':run()
