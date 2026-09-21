#!/usr/bin/env python3
"""Run the existing --wall-step audit, redirecting its three report destinations.

The production verifier is compiled unchanged except for literal HERE/report-path
expressions. Geometry, source inputs, thresholds and command-line arguments are
the existing verifier's. Production reports remain untouched.
"""
import ast
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p/'hardware/scripts').is_dir())
SOURCE = ROOT/'hardware/printed-parts/enclosure/tee-carrier/verify_upper_backing.py'
REPORTS = {'upper-backing-check.json','readiness-audit.json','readiness-audit.svg'}


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class RedirectReports(ast.NodeTransformer):
    count = 0

    def visit_BinOp(self,node):
        node = self.generic_visit(node)
        if (isinstance(node.op,ast.Div) and isinstance(node.left,ast.Name)
                and node.left.id=='HERE' and isinstance(node.right,ast.Constant)
                and node.right.value in REPORTS):
            node.left = ast.copy_location(ast.Name(id='AUDIT_OUTPUT',ctx=ast.Load()),node.left)
            self.count += 1
        return node


def main():
    fixture = json.loads((HERE/'fixture.json').read_text())
    for path,digest in {**fixture['source_sha256'],**fixture['input_sha256']}.items():
        assert sha(ROOT/path)==digest,path
    assert sha(ROOT/fixture['step'])==fixture['step_sha256']
    before = {name:sha(SOURCE.parent/name) for name in REPORTS}
    source_hash = sha(SOURCE)
    source = ast.parse(SOURCE.read_text(),filename=str(SOURCE))
    redirect = RedirectReports()
    source = ast.fix_missing_locations(redirect.visit(source))
    assert redirect.count == 5, f'Verifier output expressions changed: {redirect.count}'
    sys.dont_write_bytecode = True
    sys.path.insert(0,str(SOURCE.parent))
    namespace = {'__name__':'bounded_upper_backing_audit','__file__':str(SOURCE),
                 'AUDIT_OUTPUT':HERE}
    exec(compile(source,str(SOURCE),'exec'),namespace)
    command = ['tools/cad-venv/bin/python',str(Path(__file__).relative_to(ROOT))]
    namespace['REPRODUCE'] = ' '.join(command)
    sys.argv = [str(SOURCE),'--wall-step',str(ROOT/fixture['step'])]
    result = namespace['main']()
    assert sha(SOURCE)==source_hash,'Production verifier changed during execution'
    assert before=={name:sha(SOURCE.parent/name) for name in REPORTS},'Production reports changed'
    audit = json.loads((HERE/'readiness-audit.json').read_text())
    audit['upper_backing_check'] = str((HERE/'upper-backing-check.json').relative_to(ROOT))
    audit['execution_scope'] = 'Unmodified existing verification logic with five literal report path expressions redirected into this fixture directory.'
    audit['wrapper_sha256'] = sha(__file__)
    (HERE/'readiness-audit.json').write_text(json.dumps(audit,indent=2)+'\n')
    print('Production carrier reports unchanged; report destinations redirected.',flush=True)
    return result


if __name__=='__main__':raise SystemExit(main())
