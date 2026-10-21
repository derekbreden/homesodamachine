"""Adapt the recovered May Water controls to current right-0.8 reservoir geometry."""
from pathlib import Path
import copy,hashlib,io,json,subprocess,zipfile
HERE=Path(__file__).resolve().parent
PART=HERE.parents[1]
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').exists())
MAY='f25975cd045cc835eccf1a207cb12fe48dc63ada:hardware/printed-parts/cold-core/reservoir/reservoir.3mf'
def native(ref):
 data=subprocess.check_output(['git','show',ref],cwd=ROOT)
 with zipfile.ZipFile(io.BytesIO(data)) as z:return data,json.loads(z.read('Metadata/project_settings.config'))
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 recipe=json.loads((PART/'print-settings.json').read_text())
 settings=copy.deepcopy(recipe['project_settings'])
 may_bytes,may=native(MAY)
 base_bytes,base=native(recipe['historical_source']['commit']+':'+recipe['historical_source']['path'])
 # Preserve the current machine/start code, material identity, right-nozzle mapping,
 # placement, and automatic Tree/Default supports for the current flat-floor geometry.
 process_keys={k for k in may if k in settings and
  (k.startswith(('seam_','wall_','sparse_infill_','top_shell_','bottom_shell_'))
   or k.endswith('_line_width') or k in ['line_width','infill_wall_overlap','internal_solid_infill_pattern','override_filament_scarf_seam_setting'])}
 speed_keys={k for k in may if k in settings and
  ('speed' in k or 'acceleration' in k) and not k.startswith(('machine_','filament_','support_'))
  and (not isinstance(may[k],list) or len(may[k])==len(settings[k]))}
 filament_keys={'filament_flow_ratio','filament_max_volumetric_speed','nozzle_temperature','nozzle_temperature_initial_layer',
  'fan_min_speed','fan_max_speed','overhang_fan_speed','overhang_fan_threshold','enable_overhang_bridge_fan',
  'additional_cooling_fan_speed','close_fan_the_first_x_layers','fan_cooling_layer_time','slow_down_layer_time',
  'slow_down_min_speed','slow_down_for_layer_cooling','filament_retraction_length','filament_wipe_distance','filament_z_hop',
  'bridge_flow','internal_bridge_flow','textured_plate_temp','textured_plate_temp_initial_layer'}
 applied={}
 for key in sorted(process_keys|speed_keys|filament_keys):
  if key not in may or key not in settings:continue
  value=copy.deepcopy(may[key])
  if isinstance(settings[key],list):
   value=copy.deepcopy(value if isinstance(value,list) and key not in filament_keys and len(value)==len(settings[key]) else [may[key][0]]*len(settings[key]))
  if key=='line_width' or key.endswith('_line_width'):
   value=['0.8']*len(settings[key]) if isinstance(settings[key],list) else '0.8'
  settings[key]=value
  applied[key]={'may_active_value':may[key][0] if isinstance(may[key],list) else may[key],'adapted_value':value}
 settings.update(layer_height='0.24',initial_layer_print_height='0.3',brim_type='no_brim',brim_width='0',
  ironing_type='no ironing',enable_support_ironing='0',print_settings_id='Reservoir May Water 0.8 - 0.24mm',
  filament_settings_id=['Reservoir May Water Clear 260C Flow1.02'])
 assert settings['filament_flow_ratio']==['1.02','1.02']
 assert settings['filament_max_volumetric_speed']==['21','21']
 assert settings['nozzle_temperature']==['260','260']
 assert settings['nozzle_temperature_initial_layer']==['255','255']
 assert settings['support_type']=='tree(auto)' and settings['support_style']=='default'
 assert settings['filament_map']==['2'] and settings['filament_nozzle_map']==['1']
 old=recipe['project_settings'];recipe['project_settings']=settings
 recipe['accepted_result_id']='may-30-clear-06'
 recipe['physical_recipe_source']={'project':'git:'+MAY,'project_sha256':sha(may_bytes),'native_application':'BambuStudio-02.07.00.55','acceptance_id':'may-30-clear-06','active_source_nozzle':'left 0.6 mm Standard','adapted_to':'Mark1 right 0.8 mm Standard, current flat-floor body/cap geometry','material':'Actual May material was Bambu PETG clear; retain current GFG01 identity for the loaded clear Translucent spools.'}
 recipe['accepted_result_scope']='May water hold belongs to the historical article. Current 0.8 mm adaptation, zero user trim, no brim and ironing Off await physical results.'
 identity={'filament_settings_id','print_settings_id'}
 assignment={'filament_map_mode','filament_map','filament_nozzle_map'}
 machine=set(recipe.get('machine_changes',{}))
 groups={'identity_changes':identity,'assignment_changes':assignment,'machine_changes':machine,'filament_changes':filament_keys}
 for name,keys in groups.items():recipe[name]={k:{'from':base[k],'to':settings[k]} for k in sorted(keys) if k in settings and settings[k]!=base.get(k)}
 reserved=set().union(*groups.values())
 recipe['process_changes']={k:{'from':base[k],'to':settings[k]} for k in sorted(settings) if k not in reserved and settings[k]!=base.get(k)}
 # Source verification uses the frozen 0.8 mm native base; the physical recipe
 # source above separately identifies the successful May controls.
 (PART/'print-settings.json').write_text(json.dumps(recipe,indent=2)+'\n')
 report={'recorded_date':'2026-10-21','recipe':'../../print-settings.json','physical_recipe_source':recipe['physical_recipe_source'],
  'native_base':recipe['historical_source'],'applied_may_controls':applied,
  'explicit_adaptations':{'normal_layer_mm':0.24,'first_layer_mm':0.3,'line_widths_mm':0.8,'right_nozzle_mm':0.8,'flow':1.02,'brim':'None','ironing':'Off for model and support','user_z_trim_mm':0,'textured_stock_compensation_mm':-0.02,'supports':'Current Tree(auto)/Default, bed-only, 0.18 mm contact gaps; May normal supports belonged to its raised slanted floor.'},
  'founder_quote':"Let's try the May Water recipe adapted to the 0.8 nozzle, with 1.02 flow, no brim, zero added Z trim, and ironing off. Mark1 is clear; go ahead and start the next reservoir print."}
 (HERE/'adaptation.json').write_text(json.dumps(report,indent=2)+'\n')
 print('May controls applied:',len(applied),'; flow 1.02, 21 mm3/s, 255/260 C; 0.30/0.24 layers; all lines 0.8; no brim/ironing.')
if __name__=='__main__':main()
