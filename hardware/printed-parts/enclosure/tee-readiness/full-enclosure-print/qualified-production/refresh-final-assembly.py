from pathlib import Path
import json,time,subprocess,shutil
root=Path('/Users/derekbredensteiner/Developer/homesodamachine');w=Path('/tmp/scanner-review/integration-correction')
producer='hardware/manifold-layout/enclosure_assembly.py';start=time.monotonic();log=w/'enclosure_assembly-generation.log'
with log.open('w') as f:
 r=subprocess.run([str(root/'tools/cad-venv/bin/python'),str(w/'trace-production.py'),producer],cwd=root,stdout=f,stderr=subprocess.STDOUT)
print('assembly_exit',r.returncode,flush=True)
if r.returncode:raise SystemExit(r.returncode)
chain=json.loads((w/'final-chain.json').read_text());chain[-1]={'producer':producer,'exit_code':r.returncode,'seconds':time.monotonic()-start,'log':str(log),'refresh_reason':'Same geometry after all published-surface lint explanations were completed; current facts include those declared documentation inputs.'};(w/'final-chain.json').write_text(json.dumps(chain,indent=2)+'\n')
card=json.loads((root/'hardware/manifold-layout/enclosure-assembly.scorecard.json').read_text())
if card.get('gatesPass') is not True:raise SystemExit('Final gates failed')
dest=w/'assembly-before-final-publication.step.mesh';shutil.copyfile(root/'hardware/manifold-layout/enclosure-assembly.step.mesh',dest)
print('PASS current aggregate gates; retained prepublication payload '+str(dest),flush=True)
