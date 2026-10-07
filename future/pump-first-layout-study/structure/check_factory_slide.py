"""Native factory closure on the retained aft-to-fore back-top Y slides.

Each carried and fixed part is named. Flexible roof-to-floor connections remain
free during sliding, then take their final installed shape after seating.
The lower captured seam also gets a separate vertical-motion witness.
"""
from pathlib import Path
import sys, json, hashlib, time
import cadquery as cq

HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
ROOT = STUDY.parents[1]
sys.path.insert(0, str(STUDY / 'pump'))
import generate as G
import check_prv_handling as PRV
import check_asse_factory as AF
import factory_stock_cells as stock_cells
from evidence_binding import content_sha256,manifest_content_sha256
from structure import proof_sources,received_native


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def broad(a, b):
    return all(a[i] <= b[i + 3] and b[i] <= a[i + 3] for i in range(3))


def main():
    sources=proof_sources.snapshot(__file__,G.__file__,PRV.__file__,AF.__file__,
                                   received_native.__file__,stock_cells.__file__,
                                   stock_cells.material.__file__)
    started = time.time()
    index = G.baseline.prepare()
    records = {name: {'brep': str((G.baseline.CACHE / rec['file']).relative_to(ROOT))}
               for name, rec in index['parts'].items()}
    manifests = {};manifest_contents={}
    removed = set()
    manifest_paths = [STUDY/folder/'candidate.json'
                      for folder in ['funnel','pump','routing','structure','mounts']]
    manifest_paths += [STUDY/'wiring'/name for name in
                       ['controls-candidate.json','power-candidate.json',
                        'control-reserves.json','control-fanouts-check.json']]
    manifest_paths += [STUDY/'mounts/fluid-candidate.json',STUDY/'mounts/body-candidate.json',
                       STUDY/'mounts/water5-hosts.json',STUDY/'routing/tube-hosts.json',
                       STUDY/'routing/co2-candidate.json',HERE/'roof-hatch.json',
                       HERE/'scene-stock.json',STUDY/'wiring/front-loom-handling.json']
    manifest_data=[]
    current_names=set()
    for path in manifest_paths:
        if not path.exists():
            continue
        manifest = json.loads(path.read_text())
        if path.name=='scene-stock.json' and not proof_sources.scene_stock_current(manifest):continue
        manifest_data.append(manifest)
        manifests[str(path.relative_to(ROOT))] = sha(path)
        manifest_contents[str(path.relative_to(ROOT))]=content_sha256(manifest)
        removed.update(manifest.get('replacement_names', []))
        records.update(manifest.get('parts', {}))
        current_names.update(manifest.get('parts',{}))
    supplement = STUDY / 'pump/fluid24-candidate.json'
    if supplement.exists():
        manifests[str(supplement.relative_to(ROOT))] = sha(supplement)
        packet=json.loads(supplement.read_text())
        manifest_contents[str(supplement.relative_to(ROOT))]=content_sha256(packet)
        records.update(packet['parts'])
    # Remove original names replaced by a composite without a same-name body.
    records = {n: r for n, r in records.items() if n not in removed or n in current_names}
    moving = {
        'enclosure-back-top', 'pcba', 'west-junction-platform',
        'c14-inlet', 'keystone-jack',
        'nameplate', 'nameplate-ink', 'bulkhead-flavor-a', 'bulkhead-flavor-b',
        'psu', 'digiten-flow', 'tube-carb-2', 'carb-foam-carb-2',
    }
    moving.update(n for n in records if n.startswith(('controller-',
                  'bulkhead-water', 'bulkhead-carb', 'co2-inlet', 'bulkhead-ring-',
                  'tube-collar-', 'tube-customer-')))
    moving.update(n for n in current_names if n.startswith('wago-'))
    # The bare measured controller header escapes travel with their board;
    # they are separate reservations from the later dressed grouped looms.
    moving.update(n for n in records if n.startswith('header-'))
    for m in manifest_data:
        moving.update(m.get('shell_fuse_part_names',[]))
        moving.update(m.get('factory_carried_part_names',[]))
    # Final front-top and removable funnel article are absent during factory work.
    absent = {'enclosure-front-top', 'funnel', 'funnel-frame', 'funnel-cover',
              'asse-drip-pan', 'moisture-plate', 'display', 'display-cover',
              'display-gasket', 'elbow-cradle', 'funnel-drain-union',
              'funnel-drain-stub', 'tube-fluid-4','vk-solenoid'}
    for m in manifest_data:
        for key in ['front_shell_fuse_part_names','front_carried_part_names','frame_fuse_part_names']:
            absent.update(m.get(key,[]))
    absent.update(AF.front_members(records,manifest_data))
    deferred = {'tube-water-5', 'tube-water-6', 'tube-water-2',
                'tube-water-supply-link', 'tube-co2-0', 'tube-co2-1',
                'tube-carb-1', 'tube-carb-2', 'carb-foam-carb-1', 'carb-foam-carb-2',
                'tube-fluid-1', 'tube-fluid-2', 'tube-fluid-14',
                'tube-fluid-18', 'tube-fluid-28'}
    deferred.update(n for n in records if n.startswith(('wire-', 'control-', 'loom-', 'harness-')))
    deferred.update(n for n in records if n.startswith(('tube-fluid-','tube-water-',
                                                       'tube-co2-','tube-carb-','carb-foam-')))
    deferred.update({'compressor-jacket-reserve','lower-carbonator-earth-reserve',
                     'lower-under-counter-earth-reserve'})
    deferred.update(n for n in records if n.startswith(('supply-screw-', 'supply-washer-')))
    for m in manifest_data:deferred.update(m.get('factory_deferred_part_names',[]))
    moving-=deferred
    # Purchased side-mounted devices move only when their mounting module
    # explicitly declares them as carried; a plan position is not a host.
    hatch=next(m for m in manifest_data if 'rectangle_xy_mm' in m)
    absent.update(hatch['carried_names'])
    absent.update(n for n in hatch['parts'] if n=='rear-roof-hatch'
                  or n.startswith(('hatch-screw-','hatch-seam-')))
    moving-=absent
    moving &= records.keys()
    fixed = set(records) - moving - absent - deferred
    shapes = {n: cq.Shape.importBrep(str(ROOT / records[n]['brep'])) for n in moving | fixed | deferred}
    prv_pose,prv_origin,prv_axis=PRV.tucked(shapes['cold-core/line-prv-vent'])
    shapes['cold-core/line-prv-vent']=prv_pose
    boxes = {n: G.bounds(s) for n, s in shapes.items()}
    inputs = {n: {'brep': records[n]['brep'], 'sha256': sha(ROOT / records[n]['brep'])}
              for n in shapes}
    poses = []
    blockers = []
    deferred_bbox_trials = []
    close = []
    first_poses=[];first_blockers=[]
    # The first stage is a pure Y translation. Every potential contact with
    # the empty lower tub lies in the shared native Z interval. Clipping it
    # once removes the dense upper wire pockets from unchanged rail checks.
    tub=shapes['enclosure-back-bottom']
    tub_bounds=boxes['enclosure-back-bottom']
    rail_low=max(min(boxes[n][2]for n in moving),tub_bounds[2])
    rail_high=min(max(boxes[n][5]for n in moving),tub_bounds[5])
    padding=1e-5
    rail_full_bounds=[boxes[n]for n in moving|{'enclosure-back-bottom'}]
    rail_xy=[min(b[j]for b in rail_full_bounds)-1 for j in range(2)]
    rail_xy += [max(b[j+3]for b in rail_full_bounds)+1 for j in range(2)]
    rail_scope=cq.Solid.makeBox(rail_xy[2]-rail_xy[0],rail_xy[3]-rail_xy[1],
                               rail_high-rail_low+2*padding,
                               cq.Vector(rail_xy[0],rail_xy[1],rail_low-padding))
    rail_parts={};rail_boxes={};rail_clip_rows=[]
    rail_out=ROOT/'.cache/pump-first-layout/structure/factory-rail-band'
    rail_out.mkdir(parents=True,exist_ok=True)
    for name in sorted(moving|{'enclosure-back-bottom'}):
        original_bounds=boxes[name]
        if original_bounds[5]<rail_low or original_bounds[2]>rail_high:
            rail_clip_rows.append({'part':name,'full_received_bounds_mm':original_bounds,
                                   'outside_z_interval':True,'pass':True})
            continue
        clipped=shapes[name].intersect(rail_scope,tol=0)
        solids=clipped.Solids()
        if solids and (not clipped.isValid()or any(not s.isValid()for s in solids)):
            raise ValueError('Invalid native empty-tub rail clip: '+name)
        row={'part':name,'full_received_bounds_mm':original_bounds,
             'outside_z_interval':False,'valid':True,'solid_count':len(solids),'pass':True}
        if solids:
            target=rail_out/(name.replace('/','--')+'.brep')
            clipped.exportBrep(str(target))
            key='factory-rail-band/'+name
            inputs[key]={'brep':str(target.relative_to(ROOT)),'sha256':sha(target)}
            row.update(inputs[key],clipped_bounds_mm=G.bounds(clipped))
            rail_parts[name]=clipped;rail_boxes[name]=row['clipped_bounds_mm']
        rail_clip_rows.append(row)
    rail_tub=rail_parts['enclosure-back-bottom']
    for travel in [237.5,200.,150.,100.,70.,40.,20.,10.,5.,2.,1.,.25,0.]:
        bad=[]
        for name in sorted(moving&rail_parts.keys()):
            b=rail_boxes[name].copy();b[1]+=travel;b[4]+=travel
            if not broad(b,rail_boxes['enclosure-back-bottom']):continue
            s=rail_parts[name].translate((0,travel,0))
            common=G.overlap(s,rail_tub)
            if common>.01:bad.append({'carried':name,'fixed':'enclosure-back-bottom','common_mm3':common})
        first_poses.append({'back_top_offset_y_mm':travel,'blockers':bad,'pass':not bad})
        first_blockers+=bad
        print('empty back-bottom rail entry',travel,'blockers',bad,flush=True)
    column_moving=moving|{'enclosure-back-bottom'}
    fixed.discard('enclosure-back-bottom')
    leading=min(boxes[n][1]for n in column_moving)
    core_rear=max(boxes[n][4]for n in fixed if n.startswith('cold-core/'))
    column_stroke=max(237.5,core_rear-leading+1.)
    travels=sorted(set([column_stroke,237.5,200.,150.,100.,70.,40.,20.,10.,5.,2.,1.,.25,0.]),reverse=True)
    for travel in travels:
        bad = []
        count = 0
        deferred_count = 0
        for name in sorted(column_moving):
            b = boxes[name].copy()
            b[1] += travel
            b[4] += travel
            deferred_count += sum(broad(b, boxes[n]) for n in deferred)
            # Deferred cross-boundary connections have free ends during this
            # motion. Their final installed shapes are not rigid obstacles.
            # The independent seated receipts qualify those occupied shapes.
            neighbors = [n for n in sorted(fixed) if broad(b, boxes[n])]
            if not neighbors:
                continue
            carried = shapes[name].translate((0, travel, 0))
            for other in neighbors:
                count += 1
                gap = carried.distance(shapes[other])
                if gap >= 1 - 1e-6:
                    continue
                common = G.overlap(carried, shapes[other]) if gap < 1e-6 else 0.
                row = {'back_top_offset_y_mm': travel, 'carried': name,
                       'fixed': other, 'gap_mm': gap, 'common_mm3': common}
                if common > .01:
                    bad.append(row)
                    blockers.append(row)
                else:
                    close.append(row)
        poses.append({'back_top_offset_y_mm': travel, 'native_pairs': count,
                      'pass': not bad, 'blockers': bad})
        deferred_bbox_trials.append({'back_top_offset_y_mm':travel,
                                     'installed_shape_bbox_candidates':deferred_count})
        print('Y slide', travel, 'pairs', count, 'blockers', len(bad), flush=True)
    seam = []
    for z in [18, 10, 5, 2, 1, .5, 0]:
        roof = shapes['enclosure-back-top'].translate((0, 0, z))
        floor = shapes['enclosure-back-bottom']
        common = G.overlap(roof, floor)
        seam.append({'back_top_offset_z_mm': z, 'common_mm3': common,
                     'gap_mm': roof.distance(floor), 'pass': common < .01})
    continuous=[]
    stock_decompositions=[]
    upper_fixed={n:s for n,s in shapes.items()if n in fixed and boxes[n][5]>=253.4}
    upper_padding=1e-5
    fixed_upper_max=max(boxes[n][5]for n in upper_fixed)
    upper_high=fixed_upper_max+upper_padding
    upper_scope=cq.Solid.makeBox(240,800,upper_high-253.4,cq.Vector(-120,-100,253.4))
    upper_fixed_rows=[{'part':n,'full_received_bounds_mm':boxes[n],
                      'native_sha256':inputs[n]['sha256'],
                      'maximum_z_mm':boxes[n][5],'pass':boxes[n][5]<=fixed_upper_max}
                     for n in sorted(upper_fixed)]
    upper_bounding={'contact_z_interval_mm':[253.4,fixed_upper_max],
                    'native_clip_z_interval_mm':[253.4,upper_high],
                    'native_clip_padding_mm':upper_padding,
                    'fixed_upper_maxima':upper_fixed_rows,'native_clips':[],
                    'proof':'The rear column follows a pure Y translation, preserving every native Z coordinate. Every fixed upper article lies at or below the recorded maximum Z. Shell material above that maximum cannot contact any fixed article; the clipped shell retains the complete possible contact band. Full original input hashes and valid individual clipped material solids are bound. Every sampled pose and the identical continuous displacement/separation criterion remain unchanged.',
                    'pass':all(r['pass']for r in upper_fixed_rows)}
    cert=AF.Certifier(upper_fixed)
    for n in sorted(column_moving-{'enclosure-back-bottom'}):
        article=shapes[n]
        if n=='enclosure-back-top':
            article=article.intersect(upper_scope,tol=0)
            solids=article.Solids()
            if not solids or not article.isValid()or any(not q.isValid()for q in solids):
                raise ValueError('Invalid native shell contact-band clip')
            clip_out=ROOT/'.cache/pump-first-layout/structure/factory-upper-bay-motion'
            clip_out.mkdir(parents=True,exist_ok=True)
            clip_path=clip_out/(n+'.brep');article.exportBrep(str(clip_path))
            key='factory-upper-bay-motion/'+n
            inputs[key]={'brep':str(clip_path.relative_to(ROOT)),'sha256':sha(clip_path)}
            stock=[]
            for i,q in enumerate(solids):
                qb=G.bounds(q)
                stock.append({'solid_index':i,'bounds_mm':qb,'valid':q.isValid(),
                    'volume_mm3':q.Volume(tol=1e-9),
                    'pass':q.isValid()and qb[2]>=253.4-1e-6 and qb[5]<=upper_high+1e-6})
            coverage=received_native.full_material_coverage(article,shapes[n])
            scoped_common=[]
            for i,q in enumerate(shapes[n].Solids()):
                volume,witness=received_native.material_common(q,upper_scope,0.)
                scoped_common.append({'full_source_solid':i,**witness,'scoped_volume_mm3':volume})
            independent_volume=sum(r['scoped_volume_mm3']for r in scoped_common)
            clip_volume=sum(abs(q.Volume(tol=1e-9))for q in solids)
            complete=coverage['pass']and abs(independent_volume-clip_volume)<.001
            if not complete:raise ValueError('Shell contact-band clip fails independent complete material witness')
            upper_bounding['native_clips'].append({'part':n,'full_native_sha256':inputs[n]['sha256'],
                **inputs[key],'solid_count':len(solids),'per_solid_stock':stock,
                'clipped_material_in_full_source':coverage,
                'independent_source_scope_commons':scoped_common,
                'independent_scoped_volume_mm3':independent_volume,'clipped_volume_mm3':clip_volume,
                'complete_scoped_material_error_mm3':abs(independent_volume-clip_volume),
                'full_received_bounds_mm':boxes[n],'clipped_bounds_mm':G.bounds(article),
                'full_native_faces':len(shapes[n].Faces()),'clipped_faces':len(article.Faces()),
                'pass':complete and all(r['pass']for r in stock)})
            cells,cell_records,decomposition=stock_cells.decompose(
                article,clip_out/'cells',inputs[key])
            inputs.update({'factory-shell-cell/'+name:record
                           for name,record in cell_records.items()})
            cap_name='cold-core/foam-cap-lid-top'
            cap_certificate=stock_cells.monotone_cap_contact(
                cells['x1-y1'],cell_records['x1-y1'],
                [-97.5,463.,253.3,97.5,700.,314.3],
                shapes[cap_name],inputs[cap_name],column_stroke)
            decomposition['nominal_cap_contact']=cap_certificate
            stock_decompositions.append(decomposition)
            for cell_name,cell in cells.items():
                at,bound=AF.translation(cell.translate((0,column_stroke,0)),
                                        (0,-column_stroke,0))
                independent=(cap_name,)if cell_name=='x1-y1'else()
                row=cert.motion('back-column-'+n+'-'+cell_name,at,bound,
                                ignore=independent)
                if independent:
                    row['independent_named_pair_certificate']=cap_certificate
                continuous.append(row)
            continue
        if not article.Solids():continue
        at,bound=AF.translation(article.translate((0,column_stroke,0)),(0,-column_stroke,0))
        continuous.append(cert.motion('back-column-'+n,at,bound))
    upper_bounding['pass']=upper_bounding['pass']and all(r['pass']for r in upper_bounding['native_clips'])
    result = {
        'pass': not blockers and not first_blockers and upper_bounding['pass']
                and all(r['pass']for r in stock_decompositions)
                and all(r['pass']for r in continuous),
        'empty_tub_rail_entry':{'stroke_mm':237.5,'poses':first_poses,'blockers':first_blockers,
            'bounding_reduction':{
                'contact_z_interval_mm':[rail_low,rail_high],
                'native_clip_xy_bounds_mm':rail_xy,
                'native_clip_padding_mm':padding,'native_clips':rail_clip_rows,
                'proof':'Pure Y translation preserves every Z coordinate. A common point must belong to both received Z ranges, so all first-stage contacts lie in their shared interval. The identical received shapes are clipped once to that interval and tested per solid at all thirteen unchanged Y offsets; complete original input hashes remain bound.',
                'pass':all(r['pass']for r in rail_clip_rows)}},
        'whole_back_column_entry':{'stroke_mm':column_stroke,'column_leading_y_mm':leading,
                                   'fixed_core_rear_y_mm':core_rear,'starting_plan_air_mm':leading+column_stroke-core_rear},
        'continuous_upper_bay_motions':continuous,
        'continuous_upper_bay_stock_decomposition':stock_decompositions,
        'continuous_upper_bay_bounding_reduction':upper_bounding,
        'poses': poses, 'blockers': blockers,
        'moving_names': sorted(moving), 'fixed_names': sorted(fixed),
        'absent_names': sorted(absent & records.keys()),
        'deferred_connection_names': sorted(deferred & records.keys()),
        'deferred_installed_shape_trials':{
            'native_intersections_evaluated':False,'bbox_counts':deferred_bbox_trials,
            'scope':'These final installed connection shapes are absent while the back column moves. Bounding-box candidates describe where free-end handling is needed; they are neither rigid-motion blockers nor flexible assembly proofs.'},
        'seated_occupancy_receipt_paths':[
            'future/pump-first-layout-study/native-audit.json',
            'future/pump-first-layout-study/pump/external-native-check.json',
            'future/pump-first-layout-study/routing/strict-route-audit.json',
            'future/pump-first-layout-study/wiring/power-members-check.json',
            'future/pump-first-layout-study/wiring/control-fluid-air-check.json'],
        'close_native_pairs': close,
        'temporary_fixed_poses':{'cold-core/line-prv-vent':{'clock_deg':-70,'origin_mm':prv_origin.toTuple(),'axis':prv_axis.toTuple(),'scope':'Unchanged native tube in a temporary inward clocking. Flexible reseat and outside pull-loop handling are detailed in prv-factory-handling.json.'}},
        'vertical_seam_witness': seam,
        'native_inputs': inputs, 'manifest_sha256': manifests,
        'manifest_content_sha256':manifest_contents,
        'source_inputs':sources,
        'source_drift': [n for n, r in inputs.items() if sha(ROOT / r['brep']) != r['sha256']]+proof_sources.changed(sources),
        'factory_sequence': [
            'Mount the lid relays, set pump sliders and tighten its downward-facing discharge clamp before mounting all four feet; install side valve and suction-chain subassemblies. Park the unchanged relief tube in its specified temporary inward clocking and leave its removable pull loop accessible at the external west vent groove.',
            'Prewire the controller and WAGO deck and attach the retained rear interfaces and explicitly carried side-wall subassemblies to the removed back-top. Keep the rear hatch, ground fan and discharge-chain subassembly absent. Carry the supply body at its final roof-relative station using factory workholding; its four screws and washers are absent during sliding. Roof-to-floor connections remain free.',
            'Slide the populated back-top237.5mm fore into the EMPTY back-bottom on its retained rails. The ASSE/carrier, purchasedVK, front-top/frame and rear hatch remain absent. Bring that closed rear column from fully behind the upright cold-core cart through the computed full entry stroke. Its lid tenants and supply hosts are already on the core. Seat the supply on those hosts, insert its four washers and screws through the rear aperture and tighten with the native vertical160mm key leg; withdraw the key upward.',
            'Install the separately held ASSE and bolted carrier through the open fore aperture using asse-factory-check.json, then fit the purchased VK on its retained lid cradle. The ASSE west tube retains a free opposite end during its staged valve motion and final dressing. The check and TEE remain preassembled on the core throughout its ride; their opposite tube ends remain free.',
            'On the removed rear hatch, crimp the four ground-ring wires at their final cut lengths with their opposite ends free; torque the five-ring ground fan, seat the discharge-chain lower key, tighten its two screws and prepare its clamp. Present the article14mm above its installed plane, engage the free reinforced discharge hose, then follow the constant-length R15.9 family in hatch-hose-check.json and the four free-tail reservations in ground-make-up-check.json while landing. Water5 and all opposite electrical endpoints remain free.',
            'Complete WAGO-G2 first through the open front-top/funnel aperture, before dressing other harnesses in its fore approach. The hook fixture and34mm normal wire insertion follow g2-factory-tool-probe.json. Dress and terminate each remaining compliant ground tail in its separately audited final route; connect water5, gas/carbonated-water/flavor links and roof-to-floor harnesses. Keep J13 parked on the front article and J9/display absent. These final shapes qualify seated occupancy, while the stated free-end handling remains a physical factory process.',
            'Tighten the four recessed hatch M3×8 screws from the top and install the sensed pan. Carry the complete constant-length parked J13 lead through the102.2mm late front-top/frame closure, using wiring/front-loom-handling.json. With the hatch seated and silicone funnel absent, manually unstow J13 through the open funnel/display apertures, dress its unchanged installed route and make its existing XH board termination. Install the display and J9 after mechanical closure. Inspect all connections, then cast and permanently bond the continuous hatch silicone seam and flush caps and fit the silicone funnel and cover.',
            'Reseat the compliant relief outlet through the accepted core exit using the outside pull loop, remove that temporary loop and verify the clear vent mouth and chase before closing the appliance.',
        ],
        'scope': 'Thirteen native back-top poses over the actual237.5mm empty-tub rail stroke, followed by the complete rear-column entry beginning fully aft of the fixed core. Modified upper-bay rigid articles have continuous midpoint-displacement certificates. Retained lower interfaces receive full named multi-pose checks. Only articles actually fixed during motion are collision obstacles. Explicit absent/deferred inventories and separate seated-occupancy receipt paths preserve the flexible handling scope.',
        'limits': [
            'Continuous upper-bay rigid separation does not qualify inherited lower seam tolerance, factory workholding, loads, tool availability or flexible hose/wire dressing. Lower interfaces retain their accepted assembly path and receive the stated multi-pose checks.',
            'The whole back-top follows the retained Y rails. Only the separate rear hatch follows +Z; its constant-length water6 handling family keeps the west roof high plane fixed. The captured back-bottom seam blocks whole-roof Z closure.',
            'A deferred connection must be free during Y sliding and connected in its final shape after seating. Its final seated fit is checked by the complete assembly audit.',
            'The supply is carried unfastened during sliding; its installed body and lid hosts are unchanged. Temporary workholding is a physical process. The separate hatch report binds its post-slide screw-tool insertion/removal path.',
            'The relief tube tuck is an exact native temporary pose. Its flexible pull-loop reseat through the accepted exit is an explicit physical factory qualification; the intermediate rigid untwist is blocked by the exit skin.',
            'The controller/WAGO subassembly is prewired. Ground and discharge are preassembled on the separate hatch. Flexible floor connections remain free during the large Y approach; their installed occupancy is not a continuous flexible assembly proof.',
            'The complete parked J13 article has a native closing-travel witness. Unstowing, final dressing, XH insertion and J9/display make-up through the remaining apertures are unqualified manual operations; no inherited donor harness reach is claimed.',
            'The hatch seam and flush caps use the existing funnel silicone. Bonding, cure, leak retention, insert load and applied torque require physical qualification.',
        ],
        'elapsed_seconds': time.time() - started,
        'required_rail_entry_travel_mm':237.5,
        'retained_assembly_source':'hardware/assembly/enclosure-mechanical.md section6',
        'front_loom_handling_report':'future/pump-first-layout-study/wiring/front-loom-handling.json',
    }
    result['manifest_drift']=[n for n,h in manifest_contents.items()if manifest_content_sha256(ROOT/n)!=h]
    result['pass']=result['pass'] and not result['source_drift'] and not result['manifest_drift']
    (HERE / 'factory-slide-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'pass': result['pass'], 'blockers': len(blockers),
                      'deferred_connections': len(deferred & records.keys())}), flush=True)


if __name__ == '__main__':
    main()
