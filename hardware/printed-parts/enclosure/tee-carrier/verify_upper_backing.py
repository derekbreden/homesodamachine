"""Audit current native carrier backing, printed sections and declared body-bending loads.

This does not qualify complete assembled rigidity. The common centre-joint region,
contact play, torsion, material anisotropy and actual print structure remain separate.
"""
from pathlib import Path
import argparse
import ast
import hashlib
import io
import json
import math
import os
import shlex
import subprocess

import cadquery as cq
import numpy as np
from shapely.geometry import LineString, Polygon
from shapely.ops import polygonize, unary_union
import trimesh

# This audit reads finished native/print files and writes only audit reports.
# Repository probe tooling opts out of the generator mutex for this exact use.
os.environ.setdefault('HSM_NO_BUILD_LOCK','1')
import tee_carrier as carrier

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / '.git').exists())
SPEC = carrier.DEFAULT_SPEC
BASELINE_COMMIT = '583b5e2a32ed9c6b7a546e954510b3aa0a5cd71f'
_inner_x = min(x for x in SPEC.tee_xs if x > 0)
_outer_x = max(SPEC.tee_xs)
SAMPLES = ((_inner_x, 'inner tee centre'),
           (_inner_x + SPEC.tie_slot_offset_x, 'inner tie slot'),
           (40.0, 'inner web and shelf'), (49.945, 'previous spring station'),
           (60.0, 'outer web'), (_outer_x - SPEC.tie_slot_offset_x, 'outer tie slot'),
           (_outer_x, 'outer tee centre'), (90.0, 'outermost tie slot'), (92.0, 'grip root'))
REPRODUCE = 'tools/cad-venv/bin/python hardware/printed-parts/enclosure/tee-carrier/verify_upper_backing.py'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def moment(mesh, x):
    segments = trimesh.intersections.mesh_plane(mesh, plane_origin=[x, 0, 0],
                                                plane_normal=[1, 0, 0])
    lines = [LineString(np.round(line[:, 1:3], 7)) for line in segments]
    loops = [Polygon(poly.exterior) for poly in polygonize(unary_union(lines))]
    if not loops:
        raise ValueError(f'No closed printed material section at X={x:g}')
    origin = np.mean(np.concatenate([np.array(poly.exterior.coords) for poly in loops]), axis=0)
    total = np.zeros(6)
    for index, poly in enumerate(loops):
        point = poly.representative_point()
        depth = sum(other.contains(point) and other.area > poly.area
                    for other_index, other in enumerate(loops) if other_index != index)
        points = np.array(poly.exterior.coords)-origin
        y, z = points[:-1].T
        yn, zn = points[1:].T
        cross = y * zn - yn * z
        area = cross.sum() / 2
        first_y = ((y + yn) * cross).sum() / 6
        first_z = ((z + zn) * cross).sum() / 6
        second_y = ((y*y+y*yn+yn*yn)*cross).sum()/12
        second_z = ((z*z+z*zn+zn*zn)*cross).sum()/12
        product = ((2*y*z+y*zn+yn*z+2*yn*zn)*cross).sum()/24
        total += (1 if area > 0 else -1) * (-1 if depth % 2 else 1) * np.array(
            [area, first_y, first_z, second_y, second_z, product])
    area, fy, fz, sy, sz, product = total
    izz, iyy, iyz = sy-fy*fy/area, sz-fz*fz/area, product-fy*fz/area
    effective = izz-iyz*iyz/iyy
    if min(area,iyy,izz,effective)<=0:
        raise ValueError(f'Non-positive material section or inertia tensor at X={x:g}')
    return {'area_mm2':float(area),'centroid_y_mm':float(fy/area+origin[0]),
            'centroid_z_mm':float(fz/area+origin[1]),'Izz_mm4':float(izz),
            'Iyy_mm4':float(iyy),'Iyz_mm4':float(iyz),
            'I_for_pure_Mz_mm4':float(effective)}


def baseline_inputs():
    """Read committed print meshes and literal baseline datums without importing old CAD."""
    source_path=(HERE/'tee_carrier.py').relative_to(ROOT)
    source=subprocess.check_output(['git','show',f'{BASELINE_COMMIT}:{source_path}'],cwd=ROOT)
    tree=ast.parse(source)
    call=next(node.value for node in tree.body if isinstance(node,ast.Assign)
              and any(isinstance(t,ast.Name) and t.id=='DEFAULT_SPEC' for t in node.targets))
    datums={kw.arg:ast.literal_eval(kw.value) for kw in call.keywords}
    meshes,inputs={},{}
    for side in ('left','right'):
        path=(HERE/f'enclosure-tee-carrier-{side}.stl').relative_to(ROOT)
        content=subprocess.check_output(['git','show',f'{BASELINE_COMMIT}:{path}'],cwd=ROOT)
        meshes[side]=trimesh.load(io.BytesIO(content),file_type='stl')
        inputs[side]={'path':str(path),'sha256':hashlib.sha256(content).hexdigest()}
    inputs['source']={'path':str(source_path),'sha256':hashlib.sha256(source).hexdigest()}
    return meshes,datums,inputs


def load_case(name,tee_xs,spring_xs):
    """Self-equilibrated, unit-total load patterns in the projected X/Y beam plane."""
    if name=='spring_return':
        loads=[(x,-.5,'spring') for x in spring_xs]+[(x,.25,'tee') for x in tee_xs]
    else:
        left,right=(.5,.5) if name=='equal_grips' else (1/3,2/3)
        moment_demand=100*(right-left)
        gradient=moment_demand/sum(x*x for x in tee_xs)
        loads=[(-100,left,'grip'),(100,right,'grip')]
        loads += [(x,-.25-gradient*x,'tee') for x in tee_xs]
    if abs(sum(f for x,f,_ in loads))>1e-10 or abs(sum(x*f for x,f,_ in loads))>1e-8:
        raise ValueError('The declared beam load pattern is not self-equilibrated')
    return [{'x_mm':x,'force_y_per_unit_total_N':f,'application':role} for x,f,role in sorted(loads)]


def section_actions(x,loads):
    left=[row for row in loads if row['x_mm']<x]
    return (sum(row['force_y_per_unit_total_N']*(x-row['x_mm']) for row in left),
            sum(row['force_y_per_unit_total_N'] for row in left))


def bending_comparison(baseline_meshes,current_meshes,baseline_datums):
    """Complementary strain energy outside the joint; no joint is assumed bonded.

    Unit load P gives q/P = integral(m_z^2 / I_effective) dx / E, where q is
    the load-weighted relative displacement. I_effective includes Iyz coupling.
    This body term omits the central joint and is not complete-device stiffness.
    """
    cases=('equal_grips','spring_return','unequal_grips_2_to_1')
    datums={'before_spring_move':{'tees':baseline_datums['tee_xs'],
                                'springs':baseline_datums['spring_xs']},
            'current':{'tees':SPEC.tee_xs,'springs':(-SPEC.spring_x,SPEC.spring_x)}}
    loads={model:{name:load_case(name,d['tees'],d['springs']) for name in cases}
           for model,d in datums.items()}
    grids=[]
    for step in (.5,.25):
        sample_x=np.concatenate((np.arange(-100+step/2,-13,step),np.arange(13+step/2,100,step)))
        grid={'step_mm':step,'sections_per_model':len(sample_x),'models':{}}
        for model,meshes in (('before_spring_move',baseline_meshes),('current',current_meshes)):
            sections=[moment(meshes['left' if x<0 else 'right'],float(x)) for x in sample_x]
            effective=np.array([r['I_for_pure_Mz_mm4'] for r in sections])
            values={}
            for name in cases:
                m=np.array([section_actions(float(x),loads[model][name])[0] for x in sample_x])
                density=m*m/effective
                values[name]={'C_times_E_per_mm':float(np.sum(density)*step),
                              'zones':{label:float(np.sum(density[(np.abs(sample_x)>=lo)&(np.abs(sample_x)<hi)])*step)
                                       for label,lo,hi in (('inner_body',13,56.82),('outer_body',56.82,91),('grip',91,100))}}
            profile=[[float(x),r['Izz_mm4'],r['Iyy_mm4'],r['Iyz_mm4'],r['I_for_pure_Mz_mm4']]
                     for x,r in zip(sample_x,sections)]
            grid['models'][model]={'cases':values,'minimum_effective_I_mm4':float(effective.min()),
                                   'sample_profile_sha256':hashlib.sha256(json.dumps(profile,separators=(',',':')).encode()).hexdigest()}
        grids.append(grid)
    rows=[]
    for name in cases:
        row={'case':name,'models':{}}
        for model in datums:
            fine=grids[-1]['models'][model]['cases'][name]
            coarse=grids[0]['models'][model]['cases'][name]['C_times_E_per_mm']
            m,v=section_actions(0,loads[model][name])
            row['models'][model]={**fine,'loads':loads[model][name],
                                  'coarse_to_fine_relative_change':abs(fine['C_times_E_per_mm']-coarse)/fine['C_times_E_per_mm'],
                                  'joint_Mz_per_unit_total_N_mm':m,'joint_Vy_per_unit_total_N':v}
        old,new=(row['models'][model]['C_times_E_per_mm'] for model in datums)
        row['current_to_baseline_body_compliance_ratio']=new/old
        row['equal_modulus_body_bending_gain']=old/new
        if name=='spring_return' and old>new:
            m=row['models']['current']['joint_Mz_per_unit_total_N_mm']
            row['conditional_joint_Ktheta_over_E_threshold_mm3']=m*m/(old-new)
            row['threshold_scope']=('Only this symmetric projected load case: a lumped, linear central rotational '
                                    'compliance would need Ktheta/E above this value to preserve the body-only advantage. '
                                    'This omits torsion, guide/contact compliance and actual joint backlash.')
        rows.append(row)
    max_change=max(r['models'][m]['coarse_to_fine_relative_change'] for r in rows for m in datums)
    return {'status':'converged' if max_change<.01 else 'sampling_needs_refinement',
            'formula':'C_body * E = integral_{[-100,-13] U [13,100]} m_z(x)^2 / (Izz-Iyz^2/Iyy) dx',
            'quantity':'Load-weighted body bending compliance coefficient, in 1/mm; divide by E in N/mm^2 for mm/N.',
            'integration':'Midpoint quadrature at 0.5 and 0.25 mm; cross-section holes retained; common |X|<13 mm joint region excluded.',
            'excluded_joint_interval_mm':[-13,13],
            'grip_load_x_mm':[-100,100],
            'orthogonal_bending':'The full centroidal Y/Z inertia tensor allows coupled bending under Mz; torsion and shear are omitted.',
            'load_notes':{'equal_grips':'0.5 N at each grip; -0.25 N at each tee.',
                          'spring_return':'-0.5 N at each spring; +0.25 N at each tee. Spring locations follow each model.',
                          'unequal_grips_2_to_1':'Right/left grips 2/3 and 1/3 N; tee reactions vary linearly with X to balance force and moment. '
                                                 'This is a specified comparison pattern, not measured contact forces.'},
            'actual_spring_force_N':None,'grids':grids,'cases':rows,
            'max_coarse_to_fine_relative_change':max_change,
            'limits':['The centre joint is excluded, not assigned infinite stiffness.',
                      'Force application heights are projected to one beam plane; roll torque is recorded separately.',
                      'This does not model guide bearing contact, clearance take-up, tie/tee compliance, torsion, shear, local plate distortion, infill or layer anisotropy.',
                      'No absolute deflection, allowable load, material modulus, assembled rigidity or print readiness is established.']}


def native_roll_restraint(wall_path,native_halves,interface):
    """Read actual opposed guide contacts, without crediting a spring guide shaft."""
    wall_hash=sha(wall_path)
    wall=cq.importers.importStep(str(wall_path)).val()
    rows,errors=[],[]
    air=SPEC.slide_air
    slot_floor=interface['service_slot_z'][0]
    slot_roof=interface['service_slot_z'][1]+carrier.fits.supported_surface
    rim_roof=interface['service_recess_z'][1]
    fore_top=SPEC.rim_z[0]-air
    fore_y=(SPEC.rim_y[0]-air,SPEC.grip_y[0]-air)

    def probe(label,shape,solid,expected):
        amount=shape.cut(solid).Volume() if expected=='stock' else shape.intersect(solid).Volume()
        rows.append({'check':label,'reading':expected,'missing_or_overlap_mm3':amount})
        if amount>1e-5: errors.append(label+f': {amount:.6f} mm³')

    contacts=[]
    for side,label in ((-1,'left'),(1,'right')):
        x=side*SPEC.spring_x
        # Reject a stale wall before interpreting any of its restraint readings.
        bore=cq.Solid.makeCylinder(SPEC.spring_bore_d/2-.01,SPEC.fixed_seat_depth-.02,
                                   cq.Vector(x,SPEC.fixed_seat_floor_y+.01,SPEC.spring_z),cq.Vector(0,1,0))
        floor=cq.Solid.makeCylinder(3.0,.13,cq.Vector(x,SPEC.fixed_seat_floor_y-.15,SPEC.spring_z),cq.Vector(0,1,0))
        probe(label+' current spring bore alignment',bore,wall,'clear')
        probe(label+' current spring floor stock',floor,wall,'stock')
        xa,xb=sorted((side*SPEC.guide_inner_x,side*SPEC.exterior_x))
        region=carrier._box(xa,xb,SPEC.rim_y[0]-1,SPEC.rim_y[1]+SPEC.aft_limit_offset_y+1,
                            min(SPEC.rim_z[0],SPEC.grip_z[0])-1,SPEC.rim_z[1]+1).val()
        guides=wall.intersect(region)
        def handed_box(xs,ys,zs):
            return carrier._box(*sorted((side*xs[0],side*xs[1])),*ys,*zs).val()
        probe(label+' full source recess-roof stock',
              handed_box((SPEC.rim_x[0]+.01,SPEC.rim_x[1]-.01),
                         (fore_y[0]+.5,fore_y[1]-.5),
                         (rim_roof+.01,interface['body_top_z']-.01)),wall,'stock')
        probe(label+' fore guide bearing stock 1 mm below face',
              handed_box((SPEC.rim_x[0]+.01,SPEC.rim_x[1]-.01),
                         (fore_y[0]+.01,fore_y[1]-.01),(fore_top-1,fore_top-.01)),wall,'stock')
        for state,dy in (('release',0),('connected',SPEC.connected_offset_y),('aft_limit',SPEC.aft_limit_offset_y)):
            ys=(SPEC.grip_y[0]+dy+2.1,SPEC.grip_y[1]+dy-2.1)
            for name,zs in (('lower',(slot_floor-1,slot_floor-.01)),('upper',(slot_roof+.01,slot_roof+1))):
                probe(f'{label} {state} {name} service-slot land stock',
                      handed_box((interface['service_slot_x'][0]+.01,SPEC.exterior_x-.01),ys,zs),wall,'stock')
            body=native_halves[label].translate((0,dy,0))
            probe(f'{label} {state} carrier guide clearance',body,guides,'clear')
            center=(0,sum(SPEC.grip_y)/2+dy,sum(SPEC.printed_grip_z)/2)
            tip=(1,center[1],center[2])
            for sign in (-1,1):
                def contact(angle):
                    return body.rotate(center,tip,sign*angle).intersect(guides)
                beyond=contact(SPEC.capture_probe_angle)
                if beyond.Volume()<=1e-5:
                    errors.append(f'{label} {state}: no native X{sign:+} rotation stop')
                    continue
                low,high=0.0,SPEC.capture_probe_angle
                for _ in range(12):
                    mid=(low+high)/2
                    if contact(mid).Volume()>1e-5: high=mid
                    else: low=mid
                witness=contact(high+.05)
                b=witness.BoundingBox()
                contacts.append({'side':label,'state':state,'rotation_about_X_sign':sign,
                                 'fixed_center_first_contact_bracket_deg':[low,high],
                                 'probe_angle_deg':SPEC.capture_probe_angle,
                                 'beyond_clearance_overlap_mm3':beyond.Volume(),
                                 'first_contact_witness_bbox_mm':[b.xmin,b.ymin,b.zmin,b.xmax,b.ymax,b.zmax]})
    if sha(wall_path)!=wall_hash: raise ValueError('Native wall changed during the restraint audit')
    return {'status':'pass' if not errors else 'fail','errors':errors,
            'wall_path':str(wall_path),'wall_sha256':wall_hash,'stock_and_alignment':rows,'contacts':contacts,
            'scope':'Native positive contact and stock only. First-contact brackets hold the carrier centre fixed; '
                    'they are not free-body backlash or stiffness. No spring guide or tee contact contributes to the guide probes.'}


def roll_restraint(wall_path=None,native_halves=None):
    """Current source-derived contact geometry, pending its refreshed full native wall."""
    path=HERE.parent/'tee-readiness'/'tee-integration.json'
    source_bytes=path.read_bytes()
    report=json.loads(source_bytes)
    interface=report['carrier_interface']
    for key,expected in (('spring_bore_mouth_y',SPEC.grip_y[0]),('fixed_seat_floor_y',SPEC.fixed_seat_floor_y)):
        if abs(interface[key]-expected)>1e-5:
            raise ValueError('Derived tee interface does not match the current carrier: '+key)
    air=SPEC.slide_air
    supported=carrier.fits.supported_surface
    slot_floor=interface['service_slot_z'][0]
    slot_roof=interface['service_slot_z'][1]+supported
    recess_roof=interface['service_recess_z'][1]
    fore_top=SPEC.rim_z[0]-air
    fore_ys=(SPEC.rim_y[0]+SPEC.release_offset_y-air,SPEC.grip_y[0]+SPEC.release_offset_y-air)
    height=(SPEC.printed_grip_z[1]-SPEC.printed_grip_z[0])/2
    half_run=SPEC.grip_bar_t/2
    gap=SPEC.printed_grip_z[0]-slot_floor
    bar_angle=math.degrees(math.atan2(half_run,height)-math.acos((height+gap)/math.hypot(half_run,height)))
    result={
        'status':'positive restraints identified in current source; refreshed full native wall contact/stock audit pending',
        'source_evidence':{'tee-integration.json':hashlib.sha256(source_bytes).hexdigest(),
                           'enclosure.py':sha(HERE.parent/'enclosure'/'enclosure.py'),
                           'enclosure_assembly.py':sha(ROOT/'hardware/manifold-layout/enclosure_assembly.py')},
        'restraints':['Top and bottom of each solid pull bar bear on opposed service-slot lands in the flank wall.',
                      'The retaining rim bears under the recess roof and above the floor-rooted fore-guide land.',
                      'These fixed contacts provide a positive reaction couple about X after clearance take-up. The spring guide shaft is not credited.'],
        'spring_to_tee_height_offset_mm':SPEC.spring_z-SPEC.tee_axis_z,
        'roll_torque_about_X_per_unit_total_spring_N_mm':SPEC.spring_z-SPEC.tee_axis_z,
        'bar_bearing_y_length_mm':SPEC.grip_bar_t,
        'bar_flat_y_length_at_outer_rounded_edge_mm':SPEC.grip_bar_t-2*SPEC.grip_edge_r,
        'bar_printed_z_mm':list(SPEC.printed_grip_z),'fixed_service_land_z_mm':[slot_floor,slot_roof],
        'bar_lower_upper_clearance_mm':[SPEC.printed_grip_z[0]-slot_floor,slot_roof-SPEC.printed_grip_z[1]],
        'rim_printed_z_mm':list(SPEC.printed_rim_z),'fixed_recess_roof_z_mm':recess_roof,
        'rim_to_roof_clearance_mm':recess_roof-SPEC.printed_rim_z[1],
        'fore_guide_top_z_mm':fore_top,'rim_to_fore_guide_clearance_mm':SPEC.printed_rim_z[0]-fore_top,
        'fore_guide_y_mm':list(fore_ys),
        'source_fore_guide_x_width_mm':interface['service_recess_x'][1]-(SPEC.rim_x[0]-air),
        'source_fore_guide_root_height_mm':SPEC.rim_z[0]-SPEC.web_z[0]+3.0,
        'fore_guide_overlap_by_state_mm':{name:max(0,min(fore_ys[1],SPEC.rim_y[1]+dy)-max(fore_ys[0],SPEC.rim_y[0]+dy))
                                         for name,dy in (('release',0),('connected',SPEC.connected_offset_y),('aft_limit',SPEC.aft_limit_offset_y))},
        'rim_bearing_width_x_mm':SPEC.grip_rim_t,
        'nominal_flank_wall_width_x_mm':SPEC.exterior_x-interface['service_slot_x'][0],
        'source_recess_roof_stock_mm':interface['recess_roof_wall'],
        'source_recess_socket_wall_mm':interface['recess_socket_wall'],
        'bar_only_rectangular_contact_angle_deg':bar_angle,
        'existing_beyond_clearance_capture_probe_deg':SPEC.capture_probe_angle,
        'angle_scope':'The rectangular bar calculation and existing probe are geometric contact comparisons, '
                      'not measured backlash. Rim contacts may engage earlier; actual full-wall contact must be rechecked.',
        'physical_roll_stiffness_N_mm_per_rad':None,
    }
    if wall_path is not None:
        result['native_wall']=native_roll_restraint(wall_path,native_halves,interface)
        result['status']='native positive restraints and stock verified' if result['native_wall']['status']=='pass' else 'native restraint audit failed'
    if sha(path)!=hashlib.sha256(source_bytes).hexdigest():
        raise ValueError('Derived current interface changed during the audit')
    return result


def render_audit(audit):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    matplotlib.rcParams['svg.hashsalt']='tee-carrier-readiness-audit'
    matplotlib.rcParams['svg.fonttype']='none'
    fig=plt.figure(figsize=(14,9),facecolor='#fcfcfa')
    fig.text(.04,.951,'Carrier rigidity: current print geometry',fontsize=21,weight='bold',color='#243747')
    fig.text(.04,.912,'Local sections and a stated body-bending comparison; assembled rigidity remains unqualified',fontsize=12,color='#526575')
    ax=fig.add_axes([.22,.36,.31,.47])
    rows=audit['sections'];ys=np.arange(len(rows))
    values=[r['Izz_ratio'] for r in rows]
    ax.barh(ys,values,color=['#b07a41' if v<1 else '#467b8b' for v in values],height=.65)
    ax.set_yticks(ys,[f"{r['section']} · X{r['x_mm']:g}" for r in rows],fontsize=9)
    ax.set_xscale('log');ax.set_xlim(.5,700);ax.invert_yaxis();ax.axvline(1,color='#8c959b',lw=1)
    for y,v in zip(ys,values): ax.text(v*1.08,y,f'{v:.3g}×',va='center',fontsize=9,color='#243747')
    ax.set_xlabel('Local centroidal Izz / pre-spring-move Izz',fontsize=10)
    ax.set_title('Equal-modulus section evidence',fontsize=13,pad=13)
    ax.spines[['top','right']].set_visible(False);ax.grid(axis='x',alpha=.15)
    ax2=fig.add_axes([.66,.48,.28,.34])
    cases=audit['body_bending_comparison']['cases']
    labels=['Equal grips','Spring return','Unequal grips 2:1']
    ratios=[r['current_to_baseline_body_compliance_ratio'] for r in cases]
    ax2.barh(np.arange(3),ratios,color='#467b8b',height=.55)
    ax2.set_yticks(np.arange(3),labels,fontsize=10);ax2.invert_yaxis();ax2.set_xlim(0,max(1.1,max(ratios)*1.2))
    ax2.axvline(1,color='#8c959b',lw=1)
    for y,v in enumerate(ratios): ax2.text(v+.02,y,f'{v:.3f}',va='center',fontsize=10,color='#243747')
    ax2.set_xlabel('Current / baseline body compliance',fontsize=10)
    ax2.set_title('Declared unit-load beam model',fontsize=13,pad=13)
    ax2.spines[['top','right']].set_visible(False);ax2.grid(axis='x',alpha=.15)
    fig.text(.60,.399,'Central ±13 mm omitted; no bonded-joint assumption.',fontsize=10,color='#526575')
    fig.text(.60,.373,'Includes section coupling; excludes torsion and contacts.',fontsize=10,color='#526575')
    fig.text(.04,.251,'What the spring move asks of the assembly',fontsize=14,weight='bold',color='#243747')
    spring_case=next(row for row in cases if row['case']=='spring_return')
    joint=abs(spring_case['models']['current']['joint_Mz_per_unit_total_N_mm'])
    roll=audit['roll_restraint']['roll_torque_about_X_per_unit_total_spring_N_mm']
    fig.text(.04,.210,f'Per 1 N total return load: centre-joint bending {joint:.3f} N·mm; X-roll torque {roll:.3f} N·mm.',fontsize=11,color='#243747')
    gap=audit['roll_restraint']['bar_lower_upper_clearance_mm'][0]
    fig.text(.04,.173,f'Existing restraint: service-slot lands, rim roof and fore guide. Nominal vertical bearing air: {gap:.2f} mm.',fontsize=11,color='#243747')
    pending=('Pending: joint compliance, printed material response and full-width unequal-hand trial.'
             if audit['roll_restraint'].get('native_wall',{}).get('status')=='pass' else
             'Pending: matched wall contacts/stock, joint compliance, printed material response and full-width unequal-hand trial.')
    fig.text(.04,.135,pending,fontsize=11,color='#93622d')
    sample=audit['spring_sample']
    fig.text(.04,.082,f"Measured spring: Ø{sample['outside_diameter_mm']:g} × {sample['free_length_mm']:g} mm free; ≈{sample['compressed_length_upper_estimate_mm']:g} mm compressed. Rate and force unknown; positive capture still pending.",fontsize=10.5,color='#526575')
    fig.text(.04,.043,'Source '+audit['source_sha256'][:12]+' · right STL '+audit['current_mesh_sha256'][:12]+' · baseline '+BASELINE_COMMIT[:12],fontsize=9,color='#687987')
    out=HERE/'readiness-audit.svg'
    fig.savefig(out,metadata={'Date':None})
    out.write_text('\n'.join(line.rstrip() for line in out.read_text().splitlines())+'\n')
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline-dir', type=Path,
                        help='Optional saved pre-correction native halves for an exact change-volume comparison')
    parser.add_argument('--wall-step',type=Path,
                        help='Matching regenerated front-top STEP for native guide contact/stock readings; rejects stale spring seats')
    args = parser.parse_args()
    reproduce=REPRODUCE+(' --wall-step '+shlex.quote(str(args.wall_step)) if args.wall_step else '')
    errors, rows, inputs = [], [], {}
    source_hash=sha(HERE/'tee_carrier.py')
    verifier_hash=sha(__file__)
    # Validate the section integral against an independent analytic rectangle.
    rectangle=trimesh.creation.box(extents=(2,6,20))
    rectangle.apply_translation((0,117,208))
    rectangle_reading=moment(rectangle,0)
    rectangle_expected={'area_mm2':120.0,'Izz_mm4':360.0,'Iyy_mm4':4000.0,'Iyz_mm4':0.0}
    if any(abs(rectangle_reading[key]-value)>1e-6 for key,value in rectangle_expected.items()):
        errors.append('Polygon section integrals fail the analytic rectangle check')
    current_meshes,native_halves={},{}
    for side, name in ((-1, 'left'), (1, 'right')):
        native = HERE / f'enclosure-tee-carrier-{name}.step'
        stl = native.with_suffix('.stl')
        inputs[name] = {'step_path':str(native.relative_to(ROOT)),'stl_path':str(stl.relative_to(ROOT)),
                        'step_sha256': sha(native), 'stl_sha256': sha(stl)}
        body = cq.importers.importStep(str(native)).val()
        native_halves[name]=body
        current_meshes[name]=trimesh.load_mesh(stl)
        station_rows = []
        for x in SPEC.tee_xs:
            if (x > 0) != (side > 0):
                continue
            stock = carrier._box(x - SPEC.trough_r + 0.01, x + SPEC.trough_r - 0.01,
                                 SPEC.stub_relief_y + 0.01, SPEC.web_aft_y - 0.01,
                                 SPEC.trough_top_z + 0.01, SPEC.web_z[1] - 0.01).val()
            missing = stock.cut(body).Volume()
            # Reintroduce the defect to prove this stock reading rejects it.
            continued_trough = cq.Solid.makeCylinder(
                SPEC.trough_r, SPEC.web_z[1] - SPEC.trough_top_z + 1.0,
                cq.Vector(x, SPEC.trough_axis_y, SPEC.trough_top_z), cq.Vector(0, 0, 1))
            defect = body.cut(continued_trough)
            defect_missing = stock.cut(defect).Volume()
            station_rows.append({'x_mm': x, 'required_stock_mm3': stock.Volume(),
                                 'missing_stock_mm3': missing,
                                 'continued_trough_missing_stock_mm3': defect_missing})
            if missing > 1e-5 or defect_missing < 1.0:
                errors.append(f'{name} station X{x:g}: retained-stock regression check failed')
        comparison = None
        baseline = args.baseline_dir / native.name if args.baseline_dir else None
        if baseline is not None:
            if not baseline.is_file():
                raise FileNotFoundError(baseline)
            before = cq.importers.importStep(str(baseline)).val()
            added = body.cut(before)
            removed = before.cut(body).Volume()
            web = carrier._box(*SPEC.web_x, SPEC.web_fore_y, SPEC.web_aft_y, *SPEC.web_z).val()
            outside_web_envelope = added.cut(web).Volume()
            arm_overlap = sum(added.intersect(arm).Volume() for arm in carrier.arm_probes(SPEC))
            allowed = cq.Compound.makeCompound([
                carrier._box(x - SPEC.trough_r, x + SPEC.trough_r,
                             SPEC.web_fore_y, SPEC.bearing_y,
                             SPEC.trough_top_z, SPEC.web_z[1]).val()
                for x in SPEC.tee_xs if (x > 0) == (side > 0)])
            outside_upper_troughs = added.cut(allowed).Volume()
            comparison = {'baseline_step_sha256': sha(baseline), 'added_mm3': added.Volume(),
                          'removed_mm3': removed, 'added_outside_web_envelope_mm3': outside_web_envelope,
                          'added_arm_overlap_mm3': arm_overlap,
                          'added_outside_upper_trough_regions_mm3': outside_upper_troughs}
            if (added.Volume() <= 0 or max(removed, outside_web_envelope, arm_overlap,
                                           outside_upper_troughs) > 1e-5):
                errors.append(f'{name}: correction changes geometry outside the retained upper station stock')
        rows.append({'side': name, 'stations': station_rows, 'native_comparison': comparison})
    baseline_meshes,baseline_datums,baseline_hashes=baseline_inputs()
    sections = []
    for x, name in SAMPLES:
        before, current = moment(baseline_meshes['right'],x),moment(current_meshes['right'],x)
        sections.append({'section': name, 'x_mm': x, 'before_spring_move': before,
                         'current': current, 'Izz_ratio': current['Izz_mm4'] / before['Izz_mm4'],
                         'pure_Mz_I_ratio':current['I_for_pure_Mz_mm4']/before['I_for_pure_Mz_mm4']})
    bending=bending_comparison(baseline_meshes,current_meshes,baseline_datums)
    restraint=roll_restraint(args.wall_step,native_halves)
    errors.extend(restraint.get('native_wall',{}).get('errors',[]))
    if bending['status']!='converged':
        errors.append('Body-bending comparison changes by 1% or more on mesh-section grid refinement')
    result = {
        'status': 'pass' if not errors else 'fail', 'errors': errors,
        'source_sha256': source_hash,'verifier_sha256':verifier_hash,'reproduce':reproduce,'inputs':inputs,
        'method_validation':{'rectangle_expected':rectangle_expected,'rectangle_reading':rectangle_reading},
        'current_trough_top_z_mm': SPEC.trough_top_z,
        'current_retained_upper_backing_mm': SPEC.web_aft_y - SPEC.stub_relief_y,
        'current_retained_upper_height_mm': SPEC.web_z[1] - SPEC.trough_top_z,
        'native_stock_readings': rows,
        'pre_spring_move_baseline_commit': BASELINE_COMMIT,
        'pre_spring_move_mesh_sha256': baseline_hashes['right']['sha256'],
        'pre_spring_move_inputs':baseline_hashes,
        'printed_sections': sections,
        'section_scope':'Sections normal to X from actual printed STL meshes; centroidal inertia tensor with holes. '
                        'Local Izz ratios are not whole-carrier rigidity ratios.',
        'body_bending_comparison':bending,'roll_restraint':restraint,
        'clearance_scope':'This report checks retained native stock and printed sections. It does not establish tee '
                          'fit or complete enclosure clearance; those are separate integration audits. An optional '
                          '--baseline-dir comparison is valid only for the exact isolated upper-trough correction.',
        'source_artifact_scope':'Source and native/mesh bytes are hashed separately. No stale source-equivalence assertion is reused.',
        'production_ready': False,
    }
    for name,row in inputs.items():
        if sha(ROOT/row['step_path'])!=row['step_sha256'] or sha(ROOT/row['stl_path'])!=row['stl_sha256']:
            raise ValueError(name+' input changed during the audit; rerun against stable files')
    if sha(HERE/'tee_carrier.py')!=source_hash or sha(__file__)!=verifier_hash:
        raise ValueError('A source changed during the audit; rerun against stable files')
    (HERE / 'upper-backing-check.json').write_text(json.dumps(result, indent=2) + '\n')
    sample=json.loads((HERE/'spring-measurements.json').read_text())
    spring_states={}
    for name,dy in (('release',SPEC.release_offset_y),('squeeze',SPEC.release_offset_y),
                    ('connected',SPEC.connected_offset_y),('park',SPEC.park_offset_y),('aft_limit',SPEC.aft_limit_offset_y)):
        length=SPEC.spring_bore_floor_y+dy-SPEC.fixed_seat_floor_y
        spring_states[name]={'bearing_length_mm':length,
                             'compression_from_measured_free_mm':sample['free_length_mm']-length,
                             'margin_above_compressed_upper_estimate_mm':length-sample['compressed_length_upper_estimate_mm'],
                             'gap_between_closed_seats_mm':length-SPEC.spring_bore_depth-SPEC.fixed_seat_depth}
    audit={
        'baseline_commit':BASELINE_COMMIT,'reproduce':reproduce,'verification_status':result['status'],
        'method':result['section_scope'],'sections':sections,
        'before_spring_move_mesh_sha256':baseline_hashes['right']['sha256'],
        'current_mesh_sha256':inputs['right']['stl_sha256'],'current_native_inputs':inputs,
        'baseline_inputs':baseline_hashes,'source_sha256':source_hash,'verifier_sha256':verifier_hash,
        'current_path':str(HERE/'enclosure-tee-carrier-right.stl'),
        'spring_sample':sample,'spring_measurements_sha256':sha(HERE/'spring-measurements.json'),
        'spring_states':spring_states,
        'spring_capture':{'fixed_seat_depth_mm':SPEC.fixed_seat_depth,'moving_bore_depth_mm':SPEC.spring_bore_depth,
                          'moving_loading_window_length_mm':SPEC.spring_window_y[1]-SPEC.spring_window_y[0],
                          'moving_closed_ring_length_mm':SPEC.spring_ring,'loading_length_mm':SPEC.spring_load_length,
                          'loading_margin_above_measured_compressed_mm':SPEC.spring_load_length-sample['compressed_length_upper_estimate_mm'],
                          'side_window_has_keeper':False,'continuous_internal_guide':False},
        'body_bending_comparison':bending,'roll_restraint':restraint,
        'upper_backing_check':'hardware/printed-parts/enclosure/tee-carrier/upper-backing-check.json',
        'upper_backing_check_sha256':sha(HERE/'upper-backing-check.json'),
        'release_readiness':{'ready':False,'reason':'Positive spring capture is not integrated; full-width physical stiffness, '
                             'joint and material behavior remain unqualified.',
                             'matching_native_wall_restraint_verified':restraint.get('native_wall',{}).get('status')=='pass'},
    }
    render_audit(audit)
    audit['visual_sha256']=sha(HERE/'readiness-audit.svg')
    (HERE/'readiness-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'errors': errors,
                      'sections': [(row['section'], row['Izz_ratio']) for row in sections],
                      'body_bending':[(row['case'],row['equal_modulus_body_bending_gain']) for row in bending['cases']],
                      'grid_relative_change':bending['max_coarse_to_fine_relative_change']}, indent=2))
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
