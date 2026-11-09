"""Completed checkpoints reach the print build without waiting for a producer's final output."""
import json
import hashlib
from copy import deepcopy
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from print_build import PublicationQueue, Publications, Progress, carry_file, main, placement_changed, progress_files, unchanged_checkpoint


def write_scene(path, head):
    path.parent.mkdir(parents=True,exist_ok=True)
    data=json.dumps(head).encode()
    data+=b' '*(-len(data)%4)
    path.write_bytes(len(data).to_bytes(4,'little')+data)


class Child:
    def __init__(self):
        self.code=None;self.waited=0

    def poll(self):
        return self.code

    def wait(self):
        self.waited+=1
        if self.code is None:self.code=0
        return self.code


class PublicationQueueTests(unittest.TestCase):
    def test_first_output_starts_immediately_and_later_requests_coalesce(self):
        held=['first'];children=[];published=[]
        def start():
            published.append(held[0])
            child=Child();children.append(child)
            return child
        queue=PublicationQueue(start)
        queue.request()
        self.assertEqual(published,['first'])
        held[0]='intermediate';queue.request()
        held[0]='latest';queue.request()
        self.assertEqual(len(children),1)
        children[0].code=0
        queue.poll()
        self.assertEqual(published,['first','latest'])
        self.assertEqual(queue.drain(),[0,0])
        self.assertEqual((queue.requests,queue.started,queue.coalesced),(3,2,2))

    def test_end_of_build_drains_the_latest_held_output_and_retains_failures(self):
        children=[]
        def start():
            child=Child();children.append(child)
            return child
        queue=PublicationQueue(start)
        queue.request();queue.request();queue.request()
        children[0].code=1
        self.assertEqual(queue.drain(),[1,0])
        self.assertEqual(len(children),2)
        self.assertEqual(children[1].waited,1)


class SharedCheckpointTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.name='hardware/manifold-layout/enclosure-assembly.step.mesh'
        self.target=self.root/self.name
        self.source=self.root/'action/work'/self.name
        self.head={'v':4,'src':'same scene revision','meshes':[
            {'name':'relay-2','asset':'unchanged geometry','transform':[[1,0,0,0],[0,1,0,0],[0,0,1,0]],
             'entries':[{'name':'relay-2','color':[0.1,0.2,0.3]}],
             'features':{'mount':'upper-relay'},'source':'hardware/reference/relay.step.mesh'}],
            'sources':{'hardware/reference/relay.step.mesh':'source revision'},
            'iteration':{'stage':'installed','complete':True}}
        write_scene(self.target,self.head)

    def test_geometry_materials_features_and_source_bindings_are_never_suppressed(self):
        changes=[
            lambda head:head['meshes'][0].update(asset='changed geometry'),
            lambda head:head['meshes'][0]['transform'][0].__setitem__(3,1),
            lambda head:head['meshes'][0]['entries'][0].update(color=[0.3,0.2,0.1]),
            lambda head:head['meshes'][0]['features'].update(mount='other mount'),
            lambda head:head['meshes'][0].update(source='hardware/reference/other.step.mesh'),
            lambda head:head['sources'].update({'hardware/reference/relay.step.mesh':'changed source revision'}),
        ]
        for change in changes:
            with self.subTest(change=changes.index(change)):
                incoming=deepcopy(self.head)
                incoming['iteration']={'stage':'mechanics','complete':False}
                change(incoming);write_scene(self.source,incoming)
                self.assertFalse(unchanged_checkpoint(self.source,self.target))

    def run_build(self, incoming, *, served=True):
        write_scene(self.source,incoming)
        graph=self.root/'tools/bazel/graph.json'
        graph.parent.mkdir(parents=True)
        graph.write_text(json.dumps({'producer':{'writes':[self.name]}}))
        digest=hashlib.sha256(self.target.read_bytes()).hexdigest() if served else 'previous published scene'
        (self.root/'hardware/cad-artifacts.json').write_text(json.dumps({'solids':{self.name:digest}}))
        process=Mock();process.poll.side_effect=[None,0,0];process.wait.return_value=0
        children=[]
        def start(command,**kwargs):
            if 'bazel' in command:
                progress=self.root/'.cache/realized/print-build-progress.jsonl'
                with progress.open('a') as log:
                    log.write(json.dumps({'stage':incoming['iteration']['stage'],'files':[str(self.source)]})+'\n')
                return process
            child=Child();children.append(child)
            return child
        with patch('print_build.ROOT',self.root),patch('sys.argv',['print_build','//:installed-machine']), \
             patch('print_build.placement_changed',return_value=False), \
             patch('print_build._run_slots.subprocess_kwargs',return_value={}), \
             patch('print_build.subprocess.Popen',side_effect=start):
            self.assertEqual(main(),0)
        return json.loads(next((self.root/'.cache/runs').glob('*/result.json')).read_text()),children

    def test_identical_nonfinal_checkpoint_keeps_the_complete_served_scene(self):
        before=self.target.read_bytes();identity=self.target.stat().st_ino
        incoming=deepcopy(self.head)
        incoming['iteration']={'stage':'mechanics','complete':False,'pending':['wiring']}
        result,children=self.run_build(incoming)
        self.assertEqual(self.target.read_bytes(),before)
        self.assertEqual(self.target.stat().st_ino,identity)
        self.assertEqual(children,[])
        self.assertEqual(result['publication_queue']['requests'],0)
        self.assertEqual(result['suppressed_checkpoints'][0]['files'],[self.name])

    def test_unserved_held_geometry_still_publishes_without_copying_a_status_change(self):
        before=self.target.read_bytes();identity=self.target.stat().st_ino
        incoming=deepcopy(self.head)
        incoming['iteration']={'stage':'mechanics','complete':False}
        result,children=self.run_build(incoming,served=False)
        self.assertEqual(self.target.read_bytes(),before)
        self.assertEqual(self.target.stat().st_ino,identity)
        self.assertEqual(len(children),1)
        self.assertEqual(result['publication_queue']['started'],1)

    def test_final_completion_metadata_advances_a_held_preview(self):
        preview=deepcopy(self.head)
        preview['iteration']={'stage':'mechanics','complete':False,'pending':['wiring']}
        write_scene(self.target,preview)
        result,children=self.run_build(self.head)
        self.assertEqual(self.target.read_bytes(),self.source.read_bytes())
        self.assertEqual(result['suppressed_checkpoints'],[])
        self.assertEqual(len(children),1)

    def test_ordinary_meshes_and_unrecognized_scene_bytes_are_not_suppressed(self):
        head=deepcopy(self.head);head['v']=3
        write_scene(self.source,head)
        self.assertFalse(unchanged_checkpoint(self.source,self.target))
        write_scene(self.source,self.head)
        with self.source.open('ab') as file:file.write(b'other geometry')
        self.assertFalse(unchanged_checkpoint(self.source,self.target))


class Checkpoints(unittest.TestCase):
    def test_completed_local_output_publishes_without_another_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            name='hardware/manifold-layout/enclosure-assembly.step.mesh'
            target=root/name;target.parent.mkdir(parents=True)
            target.write_bytes(b'published scene')
            pointers=root/'hardware/cad-artifacts.json'
            pointers.write_text(json.dumps({'solids':{name:hashlib.sha256(target.read_bytes()).hexdigest()}}))
            publication=Publications(root)
            self.assertFalse(publication.needs(name,target,False))
            target.write_bytes(b'completed traced scene')
            self.assertTrue(publication.needs(name,target,False))
            self.assertFalse(publication.needs(name,target,False))
            self.assertTrue(publication.needs(name,target,True))

    def test_tail_waits_for_a_complete_new_checkpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'progress.jsonl'
            path.write_text(json.dumps({'stage':'old','files':[]})+'\n')
            progress=Progress(path)
            try:
                self.assertEqual(progress.poll(),[])
                row={'stage':'mechanics','files':['/action/work/hardware/model.step.mesh']}
                line=json.dumps(row)+'\n'
                with path.open('a') as writer:
                    writer.write(line[:len(line)//2]);writer.flush()
                    self.assertEqual(progress.poll(),[])
                    writer.write(line[len(line)//2:]);writer.flush()
                    self.assertEqual(progress.poll(),[row])
                self.assertEqual(progress.poll(),[])
            finally:
                progress.close()

    def test_checkpoint_files_follow_declared_output_paths(self):
        relative='hardware/manifold-layout/enclosure-assembly.step.mesh'
        source=Path('/action/work')/relative
        entries=progress_files({'files':[str(source),'/action/work/unrelated.mesh',relative]},
                               {relative})
        self.assertEqual(entries,[{'name':relative,'uri':source.as_uri()}])

    def test_malformed_checkpoint_does_not_hide_the_next_completed_stage(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'progress.jsonl'
            progress=Progress(path)
            try:
                row={'stage':'mechanics','files':[]}
                with path.open('a') as writer:
                    writer.write('invalid\n[]\n'+json.dumps(row)+'\n')
                self.assertEqual(progress.poll(),[row])
                self.assertEqual(len(progress.errors),2)
            finally:
                progress.close()

    def test_placement_prepass_requires_changed_recorded_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            relative='hardware/manifold-layout/junctions.json'
            source=root/relative
            source.parent.mkdir(parents=True)
            source.write_text('{"translation_mm":[0,0,0]}')
            receipt=root/'.cache/realized/installed-machine/receipts'/(
                hashlib.sha256(b'presentation-state').hexdigest()+'.json')
            self.assertFalse(placement_changed(['//:installed-machine'],root))
            receipt.parent.mkdir(parents=True)
            receipt.write_text(json.dumps({'value':{'inputs':{
                relative:hashlib.sha256(source.read_bytes()).hexdigest()}}}))
            self.assertFalse(placement_changed(['//:installed-machine'],root))
            source.write_text('{"translation_mm":[0,0,1]}')
            self.assertTrue(placement_changed(['//:installed-machine'],root))
            self.assertFalse(placement_changed(['//:tpu-o-ring'],root))
            self.assertFalse(placement_changed(['--nobuild','//:installed-machine'],root))
            receipt.write_text('incomplete')
            self.assertFalse(placement_changed(['//:installed-machine'],root))

    def test_preview_spawn_failure_still_starts_the_normal_build(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            graph=root/'tools/bazel/graph.json'
            graph.parent.mkdir(parents=True)
            graph.write_text('{}')
            process=Mock()
            process.poll.return_value=0
            process.wait.return_value=0
            with patch('print_build.ROOT',root),patch('sys.argv',['print_build','//:installed-machine']), \
                 patch('print_build.placement_changed',return_value=True), \
                 patch('print_build._run_slots.subprocess_kwargs',return_value={}), \
                 patch('print_build.subprocess.run',side_effect=OSError('preview unavailable')), \
                 patch('print_build.subprocess.Popen',return_value=process) as start:
                self.assertEqual(main(),0)
                self.assertEqual(start.call_count,1)
            result=json.loads(next((root/'.cache/runs').glob('*/result.json')).read_text())
            self.assertTrue(result['success'])
            self.assertEqual(result['preview'][0]['error'],'preview unavailable')

    def test_concurrent_carries_have_independent_atomic_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            sources=[root/'first',root/'second']
            for source in sources:source.write_bytes(source.name.encode()*8192)
            target=root/'out/model.step.mesh'
            with ThreadPoolExecutor(max_workers=4) as workers:
                list(workers.map(lambda source:carry_file(source,target),sources*8))
            self.assertIn(target.read_bytes(),[source.read_bytes() for source in sources])
            self.assertEqual(list(target.parent.glob('.*.carry-*')),[])


if __name__=='__main__':
    unittest.main()
