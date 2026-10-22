"""Continue perimeters across every model section using the May Water baseline."""
from pathlib import Path
import copy,io,json,subprocess,zipfile
HERE=Path(__file__).resolve().parent
PART=HERE.parents[1]
ROOT=next(p for p in HERE.parents if (p/'tools/bambu_printer.py').exists())
def main():
 recipe=json.loads((HERE/'baseline-settings.json').read_text())
 before=copy.deepcopy(recipe['project_settings']);settings=recipe['project_settings']
 changes={'wall_loops':'999','sparse_infill_density':'0%','top_shell_layers':'0','top_shell_thickness':'0','bottom_shell_layers':'0','bottom_shell_thickness':'0','print_settings_id':'Reservoir May Water 0.8 - walls only'}
 settings.update(changes)
 source=recipe['historical_source']
 raw=subprocess.check_output(['git','show',source['commit']+':'+source['path']],cwd=ROOT)
 with zipfile.ZipFile(io.BytesIO(raw)) as z:base=json.loads(z.read('Metadata/project_settings.config'))
 reserved=set()
 for name in ['identity_changes','assignment_changes','machine_changes','filament_changes']:
  keys=set(recipe.get(name,{}));reserved.update(keys)
  recipe[name]={k:{'from':base[k],'to':settings[k]} for k in sorted(keys) if settings[k]!=base[k]}
 recipe['identity_changes']['print_settings_id']={'from':base['print_settings_id'],'to':settings['print_settings_id']}
 reserved.add('print_settings_id')
 recipe['process_changes']={k:{'from':base[k],'to':settings[k]} for k in sorted(settings) if k not in reserved and settings[k]!=base.get(k)}
 recipe['accepted_result_scope']='Historical May water hold belongs to its identified article. Current flat-floor walls-only 0.8 mm construction awaits its own physical result.'
 (PART/'print-settings.json').write_text(json.dumps(recipe,indent=2)+'\n')
 (HERE/'adaptation.json').write_text(json.dumps({'recorded_on_central':'2026-10-21','baseline':'baseline-settings.json','baseline_print':'../2026-10-21-mark1-may-water-right08-z000/README.md','setting_changes':{k:{'from':before[k],'to':settings[k]} for k in changes if before[k]!=settings[k]},'retained':'May Water 255/260 C, flow 1.02, 21 mm3/s, 0.30/0.24 mm layers, nominal 0.8 mm lines, Arachne, random conditional scarf, cooling, right 0.8 Standard, zero user Z trim, no brim, no ironing, same geometry/placement and Tree Default supports.','reason':'Derek reports leakage between floor infill and walls and selects continued perimeters as used in his sphere pressure trials.','start_slot':'A4','preferred_consumption_order':['A4','A1','A3'],'order_basis':'Derek selects A4 first as the spool to finish; current telemetry reports A1 57%, A3 100%, A4 unknown. Auto-refill backup priority is not verified.','founder_quotes':["I think I'd rather continue the walls forever, as we did in the sphere pressure vessel test. Another agent suggested at some point infill works better, but I haven't seen that.","Mark1 bed is clear and ready for walls only. I think there is still filament on A4 that is unused please use that first.","Do you understand what I meant about the spool order? That we want to use up the spools that are most empty first ..."]},indent=2)+'\n')
 print('999 wall loops; sparse/top/bottom fill disabled; all other physical settings retained.')
if __name__=='__main__':main()
