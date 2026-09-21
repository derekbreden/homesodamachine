from pathlib import Path
import hashlib, importlib.util, json, os, shutil, subprocess, sys
root=Path('/Users/derekbredensteiner/Developer/homesodamachine')
gen=sys.argv[1]
args=sys.argv[2:]
logdir=Path('/tmp/scanner-review/integration-correction/generation')
logdir.mkdir(parents=True,exist_ok=True)
stem=Path(gen).stem
spec=importlib.util.spec_from_file_location('hsm_trace_logged',root/'tools/bazel/trace_inputs.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
source_paths=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','--','hardware','tools'],cwd=root,text=True).splitlines()
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
before={n:sha(root/n) for n in source_paths if n.endswith('.py') and (root/n).is_file()}
prelude=f"    sys.stdout = sys.stderr = open({str(logdir/(stem+'.native.log'))!r},'w',buffering=1)\n"
needle='    runpy.run_path(os.path.join(ROOT, GEN), run_name="__main__")'
assert m.RUNNER.count(needle)==1
m.RUNNER=m.RUNNER.replace(needle,prelude+needle)
m.RUNNER=m.RUNNER.replace('raised = type(exc).__name__','raised = repr(exc); __import__("traceback").print_exc()')
sys.argv=['tools/bazel/trace_inputs.py',gen,*args]
if gen in ("hardware/scripts/flute_payload_enclosure.py", "hardware/scripts/flute_payload_cold_core.py"):
    seen=m.trace(gen,m._tracked())
    rc=int(bool(seen.get("raised")))
else:
    rc=m.main()
p=Path(os.environ.get('TMPDIR','/tmp'))/f'hsm-trace-{stem}.json'
d=json.loads(p.read_text());shutil.copy2(p,logdir/(stem+'.input-trace.json'))
loaded={n:sha(root/n) for n in d['reads'] if n.endswith('.py') and n.startswith(('hardware/','tools/')) and '/site-packages/' not in n and (root/n).is_file()}
drift=[n for n,h in loaded.items() if before.get(n)!=h and n not in d['writes']]
record={'producer':gen,'raised':d.get('raised'),'loaded_source_sha256':loaded,'loaded_source_drift':drift,'rewritten_sources':[n for n in loaded if n in d['writes']],'output_sha256':{n:sha(root/n) for n in d['writes'] if (root/n).is_file() and not n.startswith('.cache/')}}
(logdir/(stem+'.generation.json')).write_text(json.dumps(record,indent=2)+'\n')
if d.get('raised') or drift:
 print('FAILED',d.get('raised'),drift,flush=True);sys.exit(1)
print('PASS',gen,len(loaded),'loaded sources stable',len(record['output_sha256']),'outputs',flush=True)
raise SystemExit(rc)
