"""Completed checkpoints reach the print build without waiting for a producer's final output."""
import json
import hashlib
from pathlib import Path
import tempfile
import unittest
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

from print_build import Publications, Progress, carry_file, main, placement_changed, progress_files


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
