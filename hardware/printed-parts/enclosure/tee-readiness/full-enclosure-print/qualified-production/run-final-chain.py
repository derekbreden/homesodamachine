from pathlib import Path
import subprocess,sys,json,time,os
root=Path('/Users/derekbredensteiner/Developer/homesodamachine')
work=Path('/tmp/scanner-review/integration-correction')
python=root/'tools/cad-venv/bin/python'; runner=work/'trace-production.py'
phases=[
 'hardware/manifold-layout/enclosure_box.py',
 'hardware/printed-parts/enclosure/enclosure/enclosure.py',
 'hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py',
 'hardware/scripts/flute_payload_enclosure.py',
 'hardware/manifold-layout/enclosure_assembly.py']
results=[]
for producer in phases:
 start=time.time();name=Path(producer).stem;log=work/(name+'-generation.log')
 print('START',producer,flush=True)
 with log.open('w') as stream:
  completed=subprocess.run([str(python),str(runner),producer],cwd=root,stdout=stream,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONUNBUFFERED':'1','OPENBLAS_NUM_THREADS':'1'})
 result={'producer':producer,'exit_code':completed.returncode,'seconds':time.time()-start,'log':str(log)}
 results.append(result);(work/'final-chain.json').write_text(json.dumps(results,indent=2)+'\n')
 print(json.dumps(result),flush=True)
 if completed.returncode:
  print(log.read_text()[-10000:],flush=True);raise SystemExit(completed.returncode)
print('COMPLETE',flush=True)
