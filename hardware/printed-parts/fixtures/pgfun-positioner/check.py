#!/usr/bin/env python3
"""Rebuild pinned reference meshes, screen assembly interference and loads.

Numerical geometry and beam/contact screens; no physical qualification claim.
Run with tools/cad-venv/bin/python from any directory.
"""
from pathlib import Path
import hashlib, importlib.util, itertools, json, math, sys
import numpy as np
import trimesh

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
D=json.loads((HERE/'design.json').read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def module(name,path):
    sys.path.insert(0,str(path.parent));spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def tm(s):
    s=s.val() if hasattr(s,'val') else s
    v,f=s.tessellate(.12,.15)
    m=trimesh.Trimesh([p.toTuple() for p in v],f,process=True);m.fix_normals();return m
def saved(z):return {k[:-3]:trimesh.Trimesh(z[k],z[k[:-3]+'__f'],process=True)for k in z.files if k.endswith('__v')}
def references():
    files=[ROOT/'hardware/reference/xlaserlab-sup29f-xh/xlaserlab_sup29f_xh.py',
           ROOT/'hardware/reference/xlaserlab-sup29f-xh/source/reconstructed-surfaces.npz',
           ROOT/'hardware/printed-parts/fixtures/weld-rotator/weld_rotator.py',
           ROOT/'hardware/printed-parts/fixtures/weld-rotator/_rotator_interface.py']
    hashes={str(p.relative_to(ROOT)):sha(p)for p in files}
    cache=HERE/'reference-meshes.npz';receipt=HERE/'reference-source.json'
    if cache.exists() and receipt.exists() and json.loads(receipt.read_text())['sources']==hashes:
        return saved(np.load(cache))
    print('building gun and existing rotator reference meshes',flush=True)
    gun=module('pgfun_gun_reference',files[0]);parts=gun.build_parts()
    mesh={k:tm(s)for k,s in parts.items()if k!='housing' and
          (not k.startswith('wire-feed-')or k in ('wire-feed-front-nut','wire-feed-thread-envelope'))}
    mesh.update(saved(np.load(files[1])))
    meshes={'gun:'+k:m for k,m in mesh.items()}
    r=module('pgfun_rotator_reference',files[2])
    builders={'base':r.build_base,'base-foot':r.build_base_foot,'motor-tower':r.build_motor_tower,
        'motor-carriage':r.build_motor_carriage,'motor-clamp-pad':r.build_motor_clamp_pad,
        'ground-tower':r.build_ground_tower,'ground-arm':r.build_ground_arm,
        'ground-shoe':r.build_ground_shoe_proxy,'turntable':r.build_turntable,'race-ring':r.build_race_ring,
        'ball-cage':r.build_cage,'spool':r.build_spool,'tube-nest':r.build_nest}
    solids={k:f()for k,f in builders.items()}
    for obj,name,loc,color in r._assembly(solids):
        meshes['rotator:'+name]=tm(obj.moved(loc))
    # Recessed cap face is the measured 208.05 mm joint plane.
    cap=trimesh.creation.cylinder(radius=123.698/2,height=3.175,sections=192)
    cap.apply_translation([0,0,D['aim'][2]-3.175/2]);meshes['rotator:recessed-cap']=cap
    values={}
    for n,m in meshes.items():values[n+'__v']=m.vertices;values[n+'__f']=m.faces
    np.savez_compressed(cache,**values)
    receipt.write_text(json.dumps({'sources':hashes,'mesh_sha256':sha(cache),
        'scope':'Pinned exterior gun reconstruction, rotator CAD and nominal recessed cap; received fit is unmeasured.'},indent=2)+'\n')
    return meshes
def overlap(a,b):
    if np.any(np.maximum(a.bounds[0],b.bounds[0])>=np.minimum(a.bounds[1],b.bounds[1])-.001):return 0.
    x=trimesh.boolean.intersection([a,b],engine='manifold',check_volume=False)
    return abs(x.volume)if x is not None else 0.
def transform(axis,deg,point):return trimesh.transformations.rotation_matrix(math.radians(deg),axis,point)
def gun_transform():
    r=transform([0,0,1],D['barrel_azimuth_deg'],[0,0,0])@transform([1,0,0],-D['barrel_down_deg'],[0,0,0])@transform([0,0,1],90,[0,0,0])@transform([1,0,0],D['gun_roll_deg'],[0,0,0])
    a=math.radians(D['barrel_down_deg']);az=math.radians(D['barrel_azimuth_deg'])
    r[:3,3]=np.array([*D['yaw_xy'],D['pivot_z']])+[0,D['working_lever_mm'],0]-(121+D['nozzle_gap'])*np.array([-math.cos(a)*math.sin(az),math.cos(a)*math.cos(az),-math.sin(a)])+D['gun_lateral_mm']*np.array([-math.cos(az),-math.sin(az),0])
    return r
def main():
    info={p['name']:p for p in json.loads((HERE/'display-meshes.json').read_text())}
    meshes=saved(np.load(HERE/'assembly-meshes.npz'));ref=references()
    for n,m in ref.items():
        if n.startswith('gun:'):meshes[n]=m.copy().apply_transform(gun_transform());info[n]={'group':'pitch','category':'reference'}
        else:meshes[n]=m;info[n]={'group':'fixed','category':'reference'}
    printed={n for n,p in info.items()if p['category']in('print','liner')}
    external={n for n in meshes if n in printed or n.startswith(('gun:','rotator:'))or n.endswith(('-reducer','-motor','-stop-follower'))or n in ('camera-envelope','raynox-dcr250')}
    intended={frozenset((a,b))for a,b in [('yaw-output-adapter','yaw-journal'),('pitch-output-adapter','pitch-journal'),
        ('yaw-stop-sector','yaw-stop-follower'),('pitch-stop-sector','pitch-stop-follower')]}
    findings=[];contacts=[];pairs=0;poses=list(itertools.product((-1.5,-1.,0.,1.,1.5),repeat=2))
    pivot=[*D['yaw_xy'],D['pivot_z']]
    for yaw,pitch in poses:
        print('checking pose',yaw,pitch,flush=True)
        ty=transform([0,0,1],yaw,pivot);tp=transform([1,0,0],pitch,pivot)
        moved={}
        for n in external:
            g=info[n]['group'];mat=ty@tp if g=='pitch' else ty if g=='yaw' else np.eye(4)
            moved[n]=meshes[n].copy().apply_transform(mat)
        for a,b in itertools.combinations(sorted(external),2):
            if a not in printed and b not in printed:continue
            same=info[a]['group']==info[b]['group']
            if same and (yaw,pitch)!=(0.,0.):continue
            # Nominal reference interference is evaluated for all printed parts;
            # repeated rigid pairs need only one pose.
            pairs+=1;vol=overlap(moved[a],moved[b])
            if vol>.5:
                row={'yaw_deg':yaw,'pitch_deg':pitch,'parts':[a,b],'overlap_mm3':round(vol,4)}
                (contacts if frozenset((a,b))in intended else findings).append(row)
    manifest=json.loads((HERE/'print-manifest.json').read_text());masses={p['name']:p['solid_mass_g']/1000 for p in manifest['parts']}
    gun=np.vstack([m.vertices for n,m in meshes.items()if n.startswith('gun:')])
    max_y=float(max(abs(gun[:,1]-pivot[1])));max_r=float(max(np.linalg.norm(gun-np.array(pivot),axis=1)))
    gravity_gun=D['gun_supported_mass_kg']*9.80665*max_y/1000
    gravity_print=sum(masses[n]*9.80665*abs(m.center_mass[1]-pivot[1])/1000 for n,m in meshes.items()if n in masses and info[n]['group']=='pitch')
    cable=D['design_cable_force_N']*max_r/1000
    torque=gravity_gun+gravity_print+cable
    t=D['design_joint_torque_Nm']*1000
    tf=D['structural_fault_torque_Nm']*1000
    net_polar=math.pi*(D['journal_diameter']**4-8**4)/32-6*(math.pi*9.4**4/32+math.pi*9.4**2/4*12**2)
    screening={'gun_mass_kg':D['gun_supported_mass_kg'],'gun_max_pitch_lever_mm':round(max_y,3),
       'gun_max_radial_lever_mm':round(max_r,3),'gun_gravity_upper_bound_Nm':gravity_gun,
       'printed_pitch_gravity_upper_bound_Nm':gravity_print,'cable_force_N':D['design_cable_force_N'],
       'cable_torque_upper_bound_Nm':cable,'pitch_service_torque_upper_bound_Nm':torque,
       'joint_screening_torque_Nm':D['design_joint_torque_Nm'],
       'six_key_bearing_stress_MPa':t/(6*20*6*6),
       'structural_fault_torque_Nm':D['structural_fault_torque_Nm'],
       'six_key_fault_bearing_stress_MPa':tf/(6*20*6*6),
       'journal_net_polar_moment_mm4':net_polar,
       'journal_torsion_MPa':t*(D['journal_diameter']/2)/net_polar,
       'bearing_moment_couple_N':t/14,
       '6808_seller_static_load_N':4180,'journal_flange_fastener_tangential_force_N_each':t/(6*29),
       'inner_bearing_seat_average_contact_MPa':500/(40*7),
       'outer_bearing_seat_average_contact_MPa':500/(52*7),
       'stop_follower_force_N':t/D['stop_radius'],
       'stop_slot_fault_average_bearing_MPa':(tf/D['stop_radius'])/(6*11.2),
       'yaw_stop_arm_root_bending_MPa':(t/D['stop_radius'])*11*9/(12*18**3/12),
       'yaw_stop_arm_fault_root_bending_MPa':(tf/D['stop_radius'])*11*9/(12*18**3/12),
       'pitch_stop_arm_fault_root_bending_MPa':tf*24/((14*(48**3-18.2**3)+10*(18.2**3-14.4**3))/12),
       'bridge_80mm_net_width_bending_MPa':t*9/(80*18**3/12),
       'journal_elastic_twist_at_7Nm_rad':t*25.2/(D['analysis_modulus_MPa']/2.7*net_polar),
       'assumed_print_allowable_MPa':D['analysis_allowable_MPa'],'assumed_print_E_MPa':D['analysis_modulus_MPa'],
       'scope':'Conservative whole-gun mass at exterior extremum; 10N cable bound. Beam/contact screening assumptions, not measured printed strength or life.'}
    receipt={'geometry_sha256':json.loads((HERE/'motion-geometry.json').read_text())['sha256'],
      'assembly_mesh_sha256':sha(HERE/'assembly-meshes.npz'),'reference_mesh_sha256':sha(HERE/'reference-meshes.npz'),
      'poses_deg':poses,'pair_evaluations':pairs,'reporting_threshold_mm3':.5,
      'intentional_key_interference_and_stop_contact':contacts,'unintended_intersections':findings,
      'scope':'Full-precision tessellated solids; 25 sampled poses. Fastener heads, physical cable, roller levers and continuous swept volumes require assembly checks.'}
    (HERE/'clearance-check.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (HERE/'load-screen.json').write_text(json.dumps(screening,indent=2)+'\n')
    print(json.dumps({'unintended_intersections':len(findings),'service_torque_upper_bound_Nm':torque},indent=2))
    if findings or torque>D['design_joint_torque_Nm']:raise SystemExit(1)
if __name__=='__main__':main()
