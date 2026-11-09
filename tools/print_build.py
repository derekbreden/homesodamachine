#!/usr/bin/env python3
"""The print build carries and publishes each finished producer while the remaining build continues."""
from __future__ import annotations
import filecmp
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import time
from urllib.parse import unquote, urlparse

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'hardware/scripts'))
import _run_slots


class Progress:
    """Read completed assembly stages while their producer continues its remaining work."""
    def __init__(self, path):
        self.errors=[];self.stream=None
        try:
            path.parent.mkdir(parents=True,exist_ok=True)
            self.stream=path.open('a+b')
            self.stream.seek(0,os.SEEK_END)
        except OSError as error:
            self.errors.append(str(error))
        self.pending=b''

    def poll(self):
        if self.stream is None:return []
        self.pending+=self.stream.read()
        lines=self.pending.split(b'\n')
        self.pending=lines.pop()
        rows=[]
        for line in lines:
            if not line.strip():continue
            try:
                row=json.loads(line)
                if not isinstance(row,dict) or not isinstance(row.get('files'),list):
                    raise ValueError('checkpoint has no file list')
                rows.append(row)
            except ValueError as error:
                self.errors.append(str(error))
        return rows

    def close(self):
        if self.stream:self.stream.close()


def progress_files(row, outputs):
    """A checkpoint can carry only files the existing producer graph declares."""
    entries=[]
    for name in row.get('files',[]):
        if not isinstance(name,str):continue
        source=Path(name)
        if not source.is_absolute():
            continue
        relative=next((rel for rel in outputs if source.as_posix().endswith('/'+rel)),None)
        if relative:
            entries.append({'name':relative,'uri':source.as_uri()})
    return entries


def placement_changed(args, root=ROOT):
    """A changed authored placement can update retained geometry before its mounts rebuild."""
    if any(arg.startswith('--nobuild') for arg in args):return False
    if args and not any(arg in ('//:installed-machine','//:everything')
                        or arg.startswith('//:enclosure-') for arg in args):
        return False
    receipt=root/'.cache/realized/installed-machine/receipts'/(
        hashlib.sha256(b'presentation-state').hexdigest()+'.json')
    try:
        inputs=json.loads(receipt.read_text())['value']['inputs']
        if not isinstance(inputs,dict):return False
        return bool(inputs) and any(hashlib.sha256((root/path).read_bytes()).hexdigest()!=expected
                                    for path,expected in inputs.items())
    except (OSError,ValueError,KeyError,TypeError):
        return False


def carry_file(source, target):
    """Concurrent completed producers replace a checkout file through independent atomic copies."""
    target.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=target.parent,prefix='.'+target.name+'.carry-',delete=False) as file:
        temporary=Path(file.name)
    try:
        shutil.copyfile(source,temporary)
        os.replace(temporary,target)
    finally:
        temporary.unlink(missing_ok=True)


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
    # The path stays the same between builds, so progress does not change compiler action keys.
    progress=Progress(ROOT/'.cache/realized/print-build-progress.jsonl')
    process=None;preview=[]
    seen=set();sets={};pending=[]
    def carry(files,stage=None):
        moved=[]
        for entry in files:
            name=entry.get('name','')
            if name not in outputs:
                # File sets may name their output relative to the configuration directory.
                name=next((rel for rel in outputs if name.endswith('/'+rel)),name)
            if name not in outputs or not name.startswith('hardware/'):continue
            if not name.endswith(('.mesh','.step','.stl','.npz','.print-features.json','.facts.json')):continue
            source=Path(unquote(urlparse(entry.get('uri','')).path))
            if not source.is_file():continue
            target=ROOT/name
            if target.is_file() and filecmp.cmp(source,target,shallow=False):continue
            carry_file(source,target);moved.append(name)
            if name.endswith('.mesh'):
                with target.open('rb') as incoming:
                    size=int.from_bytes(incoming.read(4),'little');head=json.loads(incoming.read(size))
                if head.get('step_export') is False or name.endswith('.glb.mesh'):
                    old=Path(str(target)[:-5])
                    if old.is_file():old.unlink()
        if moved:
            made.append({'seconds':time.monotonic()-started,'wall_time_ns':time.time_ns(),'files':moved,
                         **({'stage':stage} if stage else {})})
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
    def checkpoints():
        try:
            for row in progress.poll():
                try:
                    carry(progress_files(row,outputs),stage=row.get('stage'))
                except (OSError,ValueError,TypeError) as error:
                    progress.errors.append(str(error))
        except OSError as error:
            progress.errors.append(str(error))
    try:
        if progress.stream is not None and placement_changed(args):
            phase=time.monotonic()
            flags=[arg for arg in args if not arg.startswith(('//',':'))]
            try:
                built=subprocess.run([sys.executable,str(ROOT/'tools/run.py'),'--','bazel','build',
                                      '--check_up_to_date',*flags,'//:installed-machine-program'],cwd=ROOT,
                                     **_run_slots.subprocess_kwargs())
                preview.append({'phase':'current-program','seconds':time.monotonic()-phase,
                                'exit_code':built.returncode})
                program=ROOT/'bazel-bin/out/installed-machine-program/installed-machine'
                if built.returncode==0 and program.is_file():
                    phase=time.monotonic()
                    placed=subprocess.run([sys.executable,str(ROOT/'tools/run.py'),'--',str(program),
                                           str(run/'placement-preview'),'--placements-only'],cwd=ROOT,
                                          **_run_slots.subprocess_kwargs(dict(os.environ,
                                              HSM_BUILD_PROGRESS=str(ROOT/'.cache/realized/print-build-progress.jsonl'))))
                    preview.append({'phase':'placements','seconds':time.monotonic()-phase,
                                    'exit_code':placed.returncode})
                    checkpoints()
            except OSError as error:
                preview.append({'phase':'placements','error':str(error)})
        process=subprocess.Popen(command,cwd=ROOT,**_run_slots.subprocess_kwargs())
        while process.poll() is None or (events.exists() and stream is None):
            checkpoints()
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
        checkpoints()
        code=process.wait()
        publications=[publisher.wait() for publisher in publishers]
        (run/'result.json').write_text(json.dumps({'purpose':'This record identifies each completed producer carried during the print build.','success':code==0 and not any(publications),'wall_seconds':time.monotonic()-started,'preview':preview,'checkpoint_errors':progress.errors,'carried':made},indent=2)+'\n')
        events.unlink(missing_ok=True)
        return code or (1 if any(publications) else 0)
    finally:
        progress.close()
        if stream:stream.close()
        if process is not None and process.poll() is None:process.terminate();process.wait()

if __name__=='__main__':raise SystemExit(main())
