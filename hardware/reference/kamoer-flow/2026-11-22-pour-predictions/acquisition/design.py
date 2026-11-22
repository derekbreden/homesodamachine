"""Freeze the flow inputs, actuator predictions, scoring rule and order before running the trials."""
import json,random,subprocess
from pathlib import Path
w=Path(__file__).resolve().parent
d=w.parents[3]/'hardware/reference/kamoer-flow/2026-11-22-pour-predictions'
design={
 'training':{'t_slow':(20,[(1,3500)]),'t_partial':(20,[(3,2700)]),'t_full':(20,[(6,2250)]),'t_rich':(15,[(6,1760)])},
 'validation':{'top_off':(20,[(6,650)]),'full_glass':(20,[(6,6375)]),'partial_glass':(20,[(3,12775)]),'ease_open':(20,[(2,1375),(4,1575),(6,1375)]),'same_open_time':(20,[(6,2100)]),'release_reopen':(20,[(6,725),(0,300),(6,1375)]),'stronger_setting':(15,[(6,2325)]),'trickle':(20,[(1,5400)])}}
out={'provenance':{'source_tree':'0183ad1abb78ee522038fa910030281ce0dc41b4','policy_files':['firmware/lib/machine_policy/pour_policy.cpp','firmware/lib/machine_policy/pour_policy.h'],'verified_flashed_build':'d6e49a5f6','earlier_comparator_data':'a21b1685370d62bad7cb620c013c4c01c3b7a19d','water_pulses_per_litre_assumption':2280,'hardware':'Undiluted Diet Cola concentrate, two open vessels, A withdraws from the measuring cup and B fills it. No faucet water flows.'},'scenarios':{},'orders':{},
 'primary':'Nominal mL change from the settled foreground contact and direct right ruler. Positive dose for each head. Left ruler or independent clear optical region is withheld from model fitting. Preserve both and their disagreement. Never fit to validation observations.',
 'candidate':'For each head, median per-acknowledged-burst volume at each of four training timings. Given a new ideal motor schedule, sum linear interpolation of the trained per-burst volumes by motor-on duration. All tested off times come from the specified appliance policy and covary with width. Predict concentration delivered before issuing each trace; confirm board start width, ratio, channel, and completed burst count independently.',
 'qualification':'Use only stationary controls and isolated setup transfers to establish the visible band. Separate from training and validation. Position cup near the reference for each pour; alternate starting volume in six validation blocks by planned offsets 0, +4, -4, +4, -4, 0 mL about a dose-centered pre-level. Record actual start and finish. Stop if the camera or the controller cannot establish a bounded transfer. Do not interrupt a pour to recenter.',
 'epochs':{'training_blocks':3,'validation_blocks':6,'validation_offset_ml':[0,4,-4,4,-4,0],'seed':2026112202},
 'scoring':{'unit':'nominal mL dispensed, calibrated to printed cup','practical_band':'max(1.0 mL, 10% of stated predicted dose)','per_head_and_scenario':'At least 5 of 6 fresh complete attempts inside the practical band AND absolute mean signed error <= max(0.6 mL, 5% of prediction). Missing endpoints or wrong burst counts cannot be counted as successful attempts. Show held-out optical bias, coverage and all misses. Only call a result corroborated where at least 5 of 6 independent optical doses also fall within the practical band. Quote the filmed volume span for assessable attempts.',
 'stricter_band':'Also report individual count within ±5% of forecast, relevant to eventual installed ratio acceptance. An uncertain absolute cup scale or unknown water flow cannot establish finished drink ratio.',
 'baseline':'Before training, score the existing restored head full-power rates and the previously published engineering pump speed/start-loss prior on all validation attempts. Report median absolute error and bias relative to primary. A new model need not win.',
 'cooldown_hypothesis':'At the same total high-flow meter exposure, release and reopen during cooldown gives at least 20% lower median settled dose on each head and lower dose in at least five of six matched blocks. Predicted burst counts must agree with the actual appliance.',
 'water':'Nominal water in each trace follows input meter pulses/50ms times duration and the project sensor factor. The catch vessel holds concentrate only.',
 'repeat_policy':'Log every attempted command. Repeat only interrupted acquisitions or unreadable endpoints with identifiable instrumental cause, never numerical outliers. Keep missing first attempts visible in coverage. Any model changes after seeing validation require a new freeze and fresh test set.'}}
for phase,rows in design.items():
 for name,(ratio,stages) in rows.items():
  args=[str(ratio)]+[str(v) for stage in stages for v in stage]
  result=subprocess.check_output([str(w/'policy_trace'),*args],text=True).splitlines()
  gates=[[int(a),int(b)] for a,b in (r.split() for r in result if not r.startswith('stop'))]
  t=sum(g[1] for g in gates)/1000
  out['scenarios'][name]=dict(phase=phase,ratio=ratio,meter=[[p,t] for p,t in stages],ideal_gates_start_ms_width_ms=gates,ideal_bursts=len(gates),ideal_on_s=t,ideal_stop_ms=[int(r.split()[1]) for r in result if r.startswith('stop')],nominal_water_ml=sum(p*t/50 for p,t in stages)*1000/2280,old_middle_ruler_rate_prediction_ml={'A':t*(11.688923+10.991666)/2,'B':t*(10.296783+9.508880)/2})
 rng=random.Random(out['epochs']['seed']+(phase=='validation'));blocks=3 if phase=='training' else 6
 order=[]
 for block in range(1,blocks+1):
  names=list(rows);rng.shuffle(names)
  for i,name in enumerate(names):
   heads=['A','B'] if (i+block)%2 else ['B','A']
   for head in heads:order.append({'block':block,'scenario':name,'head':head})
 out['orders'][phase]=order
(d/'preregistration.json').write_text(json.dumps(out,indent=2)+'\n')
print([(n,v['ideal_bursts'],round(v['ideal_on_s'],3),round(v['nominal_water_ml'])) for n,v in out['scenarios'].items()])
