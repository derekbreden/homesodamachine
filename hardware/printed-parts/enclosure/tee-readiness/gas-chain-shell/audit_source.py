#!/usr/bin/env python3
"""Read the gas chain's shell-fit assumptions without running CAD generators."""
from pathlib import Path
from datetime import datetime,timezone
import ast,json,hashlib
ROOT=next(p for p in Path(__file__).resolve().parents if p.name=='hardware').parent
OUT=ROOT/'hardware/printed-parts/enclosure/tee-readiness/gas-chain-shell'
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def constants(path):
 result={}
 for node in ast.parse(path.read_text()).body:
  if isinstance(node,ast.Assign):
   try:value=ast.literal_eval(node.value)
   except (ValueError,TypeError):continue
   for target in node.targets:
    if isinstance(target,ast.Name):result[target.id]=value
 return result
paths={
 'gas_chain':ROOT/'hardware/manifold-layout/_gas_chain.py',
 'assembly':ROOT/'hardware/manifold-layout/enclosure_assembly.py',
 'scorecard':ROOT/'hardware/manifold-layout/_scorecard.py',
 'enclosure':ROOT/'hardware/printed-parts/enclosure/enclosure/enclosure.py',
 'fits':ROOT/'hardware/printed-parts/cadlib/fits.py',
 'check':ROOT/'hardware/reference/gasher-check-valve/gasher_check_valve.py',
 'regulator':ROOT/'hardware/reference/wr1110-regulator/wr1110_regulator.py',
 'adapter_proxy':ROOT/'hardware/reference/jg-pp010822e/jg_pp010822e.py',
 'bulkhead':ROOT/'hardware/reference/neofit-bulkhead/neofit_bulkhead.py',
 'box':ROOT/'hardware/manifold-layout/enclosure-box.json'}
c={k:constants(p) for k,p in paths.items() if p.suffix=='.py'}
slip=c['fits']['slip']; rib=c['enclosure']['tie_w']+c['enclosure']['tie_cav_buffer']+2*c['enclosure']['tie_cav_wall']
reach=c['adapter_proxy']['HEX_LENGTH']+c['adapter_proxy']['COLLET_LENGTH']
reg=c['regulator'];check=c['check'];gas=c['gas_chain']
box=json.loads(paths['box'].read_text()); packed=box['box']['pack'];pack=dict(zip(packed['fields'],packed['values']))
gasnames=['wr1110','gasher-co2','co2-inlet','co2-adapter-regulator-in','co2-adapter-regulator-out','co2-adapter-check-in','co2-adapter-check-out','co2-check-coupling-nominal']
report={
 'created_at_utc':datetime.now(timezone.utc).isoformat(),
 'scope':'Read-only shell-fit audit of current source and an explicitly identified captured Box. No received gas-part dimensions or physical fits are invented.',
 'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in (*paths.values(),Path(__file__))},
 'source_rule':{'gas_chain_qualification_kind':'goal','gas_chain_qualification_status':'warn','source':'_scorecard._build'},
 'seat_geometry':{
  'wr1110':{'owner':'enclosure-back-top','received_diameter_caliper_record_found':False,'model_barrel_diameter_mm':reg['BODY_D'],'printed_bore_diameter_mm':reg['BODY_D']+2*slip,'model_usable_barrel_length_mm':reg['TOTAL_LENGTH']-2*reg['HEX_LENGTH'],'printed_anchor_length_mm':rib,'nominal_axial_margin_each_end_mm':(reg['TOTAL_LENGTH']-2*reg['HEX_LENGTH']-rib)/2},
  'gasher_co2':{'owner':'enclosure-back-top','received_diameter_caliper_record_found':False,'model_boss_diameter_mm':check['SOCKET_D'],'printed_bore_diameter_mm':check['SOCKET_D']+2*slip,'model_usable_boss_length_mm':check['SOCKET_LENGTH'],'printed_anchor_length_mm':rib,'nominal_axial_margin_each_end_mm':(check['SOCKET_LENGTH']-rib)/2}},
 'nominal_made_up_envelopes':{
  'adapter_external_reach_from_threaded_parent_face_mm':reach,
  'regulator_collet_to_collet_span_mm':reg['TOTAL_LENGTH']+2*reach,
  'check_coupling_diameter_mm':gas['COUPLING_OD'],
  'check_coupling_length_mm':gas['COUPLING_LENGTH'],
  'assumed_check_to_coupling_engagement_mm':gas['COUPLING_ENGAGEMENT'],
  'check_collet_to_collet_span_mm':check['TOTAL_LENGTH']+gas['COUPLING_LENGTH']-gas['COUPLING_ENGAGEMENT']+2*reach,
  'check_inlet_collet_reach_from_metal_inlet_face_mm':reach,
  'check_outlet_collet_reach_from_metal_inlet_face_mm':check['TOTAL_LENGTH']+gas['COUPLING_LENGTH']-gas['COUPLING_ENGAGEMENT']+reach,
  'qualification':'The PI010822S uses a PP010822E nominal envelope; coupling dimensions and makeup are explicitly provisional. These are comparison figures, not measured limits.'},
 'ceiling_pockets':{
  'owner':'enclosure-back-top','source_plan_slip_mm':c['assembly']['CEILING_RELIEF_PLAN_SLIP'],'source_crown_air_mm':c['assembly']['CEILING_RELIEF_Z_CLEAR'],
  'captured_box_sha256':sha(paths['box']),
  'captured_rows':[row for row in pack['ceiling_reliefs'] if row[0] in gasnames],
  'captured_rows_qualification':'Source-defined nominal gas pockets in the stored Box, not the pending coordinated Box/native-shell proof. The supplied-part envelope must be compared at its seat datum.'},
 'real_shell_fit_risks':[
  'A received WR1110 barrel appreciably larger than the 19.3 mm printed seat cannot fully bed in the modeled cradle.',
  'A received GASHER inlet boss larger than the 15.8 mm seat or with less than 9.5 mm usable round length can meet the printed cradle or its shoulder.',
  'A made-up check/coupling/adapter envelope exceeding its nominal pocket can hit the back-top ceiling. Hose cut-length adjustment alone cannot fix a larger rigid fitting inside that pocket.'
 ],
 'minimal_geometry_observation':[
  {'part':'WR1110','surfaces':'Outside diameter of the smooth barrel between the two wrench hexes; verify the 9.5 mm rib can sit wholly on that straight barrel.','nominal_comparison':'19.0 mm barrel, 19.3 mm printed seat, 27 mm nominal straight barrel.'},
  {'part':'GASHER female inlet boss','surfaces':'Outside diameter and clear axial length of the round metal boss from the female inlet mouth to the start of the wrench hex.','nominal_comparison':'15.5 mm by 11 mm boss, 15.8 mm by 9.5 mm seat.'},
  {'part':'Made-up warm gas units','surfaces':'External coupling maximum diameter and length, plus collet-face reaches from the metal bearing/body datum with the actual adapters installed; one datum-identified side photo can locate the steps.','nominal_comparison':'Coupling 22 × 25.4 mm; adapters 18.5 mm exposed reach; regulator 94 mm and check 91.4 mm collet-to-collet.'}
 ],
 'thread_engagement_measurement':{'separate_internal_depth_needed_for_shell':False,'reason':'Made-up external diameters, steps and collet-face reaches already include the geometric effect of engagement. Proper engagement and sealing remain assembly qualification.'},
 'after_print_observations':['Tie threading, seating and retention under the real part.','Actual hose insertion, bend behavior and wrench access during assembly.','Thread sealing, reverse sealing, material/rating verification and operating checks before commissioning.'],
 'quadrant_scope':{
  'front_top_mechanism':'May proceed independently once its own current native and slice checks pass; no gas-chain part locates the tees, spring cups, release plate or cartridge.',
  'front_bottom':'No direct gas-chain fitting mount or pocket dependency identified.',
  'back_bottom':'No direct gas-chain fitting mount or pocket dependency identified.',
  'back_top':'Contains both gas-body cradles, rigid-fitting ceiling pockets and related hose supports. The existing record does not establish received-part fit.'},
 'assessment':{
  'known_actual_gas_interference_found':False,
  'received_part_back_top_fit_qualified':False,
  'additional_full_scans_indicated':False,
  'gas_commissioning_required_before_shell_print':False,
  'front_top_should_wait_for_gas_measurements':False,
  'all_quadrants_fit_trial_possible':True,
  'qualification':'The gas item is not a safety prerequisite to an unpowered enclosure assembly-test print. It is a specific back-top reprint risk. The short geometry observations above are needed before calling that gas fit verified; they need not hold the other quadrants or require a new coupon.'
 }
}
(OUT/'source-audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'seat_geometry':report['seat_geometry'],'nominal_made_up_envelopes':report['nominal_made_up_envelopes'],'assessment':report['assessment']},indent=2))
