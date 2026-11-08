#!/usr/bin/env python3
"""The print build carries and publishes each finished producer while the remaining build continues."""
from __future__ import annotations
import filecmp
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/scripts'))
import _run_slots


def main():
    args=sys.argv[1:]
    if args[:1]==['--']:args=args[1:]
    run=ROOT/'.cache/runs'/('print-build-'+time.strftime('%Y%m%dT%H%M%S'))
    run.mkdir(parents=True,exist_ok=True)
    events=run/'events.jsonl'
    # One admitted run carries its lease through the build and the required viewer work.
    command=[sys.executable,str(ROOT/'tools/run.py'),'--','bazel','build','--keep_going','--build_event_publish_all_actions',f'--build_event_json_file={events}',*(args or ['//:everything'])]
    started=time.monotonic();made=[];publishers=[]
    graph=json.loads((ROOT/'tools/bazel/graph.json').read_text())
    outputs={output for row in graph.values() for output in row.get('writes',[])}
    process=subprocess.Popen(command,cwd=ROOT,**_run_slots.subprocess_kwargs())
    seen=set();sets={};pending=[]
    def carry(files):
        moved=[]
        for entry in files:
            name=entry.get('name','')
            if name not in outputs:
                # File sets may name their output relative to the configuration directory.
                name=next((rel for rel in outputs if name.endswith('/'+rel)),name)
            if name not in outputs or not name.startswith('hardware/'):continue
            if not name.endswith(('.mesh','.step','.stl','.npz','.print-features.json')):continue
            source=Path(unquote(urlparse(entry.get('uri','')).path))
            if not source.is_file():continue
            target=ROOT/name
            if target.is_file() and filecmp.cmp(source,target,shallow=False):continue
            target.parent.mkdir(parents=True,exist_ok=True)
            temporary=target.with_name('.'+target.name+'.carry')
            shutil.copyfile(source,temporary);os.replace(temporary,target);moved.append(name)
            if name.endswith('.mesh'):
                with target.open('rb') as incoming:
                    size=int.from_bytes(incoming.read(4),'little');head=json.loads(incoming.read(size))
                if head.get('step_export') is False or name.endswith('.glb.mesh'):
                    old=Path(str(target)[:-5])
                    if old.is_file():old.unlink()
        if moved:
            made.append({'seconds':time.monotonic()-started,'files':moved})
            print('[print-build] carried '+', '.join(moved),flush=True)
        if any(name.endswith(('.step.mesh','.glb.mesh')) for name in moved):
            log=(run/f'publish-{len(publishers)}.log').open('w')
            child=subprocess.Popen([str(ROOT/'tools/cad-venv/bin/python'),str(ROOT/'tools/publish_now.py')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,**_run_slots.subprocess_kwargs())
            log.close();publishers.append(child)
    def files_for(key,visiting=None):
        visiting=set() if visiting is None else visiting
        if key in visiting:return []
        visiting.add(key)
        item=sets.get(key)
        if item is None:return None
        files=list(item.get('files',[]))
        for child in item.get('fileSets',[]):
            other=files_for(child['id'],visiting)
            if other is None:return None
            files.extend(other)
        return files
    def event(row):
        identity=row.get('id',{})
        if 'namedSet' in identity:sets[identity['namedSet']['id']]=row.get('namedSetOfFiles',{})
        if 'targetCompleted' in identity and row.get('completed',{}).get('success'):
            for group in row['completed'].get('outputGroup',[]):
                pending.extend(item['id'] for item in group.get('fileSets',[]))
        # Successful genrules appear independently of their requested umbrella target.
        if 'actionCompleted' in identity and row.get('action',{}).get('success'):
            label=identity['actionCompleted'].get('label')
            primary=row.get('action',{}).get('primaryOutput',{})
            if primary.get('uri'):carry([primary])
            if label:
                # The primary output supplies the configuration prefix for its completed action.
                path=unquote(urlparse(primary.get('uri','')).path)
                for rel in outputs:
                    if path.endswith('/'+rel):
                        prefix=path[:-len(rel)]
                        peers=[name for record in graph.values() if rel in record.get('writes',[]) for name in record.get('writes',[])]
                        carry([{'name':name,'uri':Path(prefix+name).as_uri()} for name in peers]);break
        for key in pending[:]:
            files=files_for(key)
            if files is not None and key not in seen:carry(files);seen.add(key);pending.remove(key)
    stream=None;buffer=''
    try:
        while process.poll() is None or (events.exists() and stream is None):
            if stream is None and events.exists():stream=events.open()
            if stream:
                text=stream.read()
                buffer+=text
                while '\n' in buffer:
                    line,buffer=buffer.split('\n',1)
                    if line.strip():event(json.loads(line))
            time.sleep(.1)
        if stream:
            for line in (buffer+stream.read()).splitlines():
                if line.strip():event(json.loads(line))
        code=process.wait()
        publications=[publisher.wait() for publisher in publishers]
        (run/'result.json').write_text(json.dumps({'purpose':'This record identifies each completed producer carried during the print build.','success':code==0,'wall_seconds':time.monotonic()-started,'carried':made},indent=2)+'\n')
        events.unlink(missing_ok=True)
        return code or (1 if any(publications) else 0)
    finally:
        if stream:stream.close()
        if process.poll() is None:process.terminate();process.wait()

if __name__=='__main__':raise SystemExit(main())
