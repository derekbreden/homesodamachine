"""Combine the native floor-relay and roof-junction modules for integration.

Run with --rebuild to regenerate both modules from installed reference bodies.
The matching shell post-process is sequential and runs after the parent shell.
"""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--rebuild',action='store_true')
    args=parser.parse_args()
    if args.rebuild:
        subprocess.run([sys.executable,str(HERE/'floor_relays.py'),'--x-shift','25'],check=True)
        subprocess.run([sys.executable,str(HERE/'roof_wagos.py')],check=True)
    modules=[json.loads((HERE/name).read_text()) for name in ['floor-candidate.json','roof-candidate.json']]
    result={'parts':{},'replacement_names':[],'expected_devices':{},'mounts':[],
      'pilot_cutters':{},'working_envelopes':{},'checks':[],'shell_fuse_part_names':[],
      'lid_fuse_part_names':[],'source_sha256':{},'qualification_limits':[],
      'endpoints':{},'intended_contacts':[]}
    for m in modules:
        for key in ['parts','expected_devices','pilot_cutters','working_envelopes','source_sha256','endpoints']:
            result[key].update(m.get(key,{}))
        for key in ['replacement_names','mounts','checks','shell_fuse_part_names','lid_fuse_part_names','qualification_limits']:
            result[key]+=m.get(key,[])
    result['pass_result']=all(m['pass_result'] for m in modules)
    result['intended_contacts'] += [['west-junction-platform','enclosure-back-top'],
      ['relay-lid-platform','cold-core/foam-cap-lid-top']]
    for name in result['expected_devices']:
        host='relay-lid-platform' if name.startswith('relay-') else 'west-junction-platform'
        result['intended_contacts'].append([host,name])
    for name in result['parts']:
        if not name.startswith('relay-') or name=='relay-lid-platform':continue
        owner='relay-1' if name.startswith('relay-1') else 'relay-2'
        result['intended_contacts'] += [[name,owner],[name,'relay-lid-platform']]
        if 'head-spacer' in name:
            screw_name=name.replace('head-spacer','mount-screw')
            result['intended_contacts'].append([name,screw_name])
    # Integration consumes parts. Bind those entries to the exact purchased
    # bodies used for every host and working-space comparison.
    result['parts'].update(result['expected_devices'])
    result['replacement_names']=sorted(set(result['replacement_names']+list(result['expected_devices'])))
    result['source_sha256'][str(Path(__file__).relative_to(ROOT))]=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    (HERE/'candidate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'parts':len(result['parts']),'expected_devices':len(result['expected_devices']),
      'pass_result':result['pass_result']},indent=2),flush=True)
    assert result['pass_result']

if __name__=='__main__':main()
