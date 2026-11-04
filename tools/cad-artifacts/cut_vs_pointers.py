#!/usr/bin/env python3
"""The solids this machine just cut, against the ones the pointer file names.

    tools/cad-venv/bin/python tools/cad-artifacts/cut_vs_pointers.py
    tools/cad-venv/bin/python tools/cad-artifacts/cut_vs_pointers.py --annotate   # in a workflow

WHAT IT IS FOR. `pack.py --check` walks the TREE, and on a runner the tree's solids came from
`web/scripts/fetch-cad-artifacts.mjs`, which downloaded the bundle the pointer file names — so it hashes
the pointer file's own bundle against the pointer file and reports agreement. That is a tautology, and it is why
every green on a runner has meant nothing. This walks `bazel-bin` instead: the bytes THIS
machine's OpenCASCADE cut, which nothing else in the pipeline ever hashes.

Two kernels on two operating systems either write the same STEP for the same model or they do
not. `_cadq_export` canonicalizes each one so that they can; whether they do is measurable and
has never been measured. That is the first thing this answers.

THE SECOND IS WHETHER THE TREE HOLDS WHAT THIS MACHINE CUTS, and it is free once the bytes are
in hand. The workflow runs this immediately after Bazel and before `sync_tree` carries declared
outputs, so the comparison measures the fetched/hand-cut tree against this build's exact bytes.

IT NEEDS NO CARRY, WHICH IS WHY IT EXISTS SEPARATELY. The bytes are on disk in `bazel-bin` the
moment the build goes green; reading them there preserves the pre-carry measurement and lets an
incomplete build fail before any tree file moves.

A DIFFERENCE HAS THREE CAUSES AND ONLY ONE OF THEM IS THE ANSWER. The bytes cannot say which:

  1. the kernels disagree — the question, and the only reading worth the words
  2. the pointer file is behind the tree's current source, so it names an older shape
  3. `bazel-bin` holds a STALE cut — bazel keeps whatever a target wrote the last time it ran,
     and a target not requested since is still sitting there under its old bytes

Three is not hypothetical: the first local run of this script reported six differences, and all
six were outputs two days old for targets that had not re-run. So the up-to-date check below is
not ceremony. It is the thing that separates a finding from an artifact of a warm output tree,
and without it this script would produce exactly the confident-and-wrong line the rest of the
pipeline kept producing.

NOTHING COMPARED IS NOT AGREEMENT. A run whose solid-cutting targets were all cache hits still
has bytes to read — a disk-cache hit is this configuration's own output — but a run that cut and
restored nothing has nothing, and the one thing this must never do is print a calm line then.
`compared == 0` is its own verdict, worded as the absence it is.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bazel'))
from _bookkeeping import call as _bookkeeping_call

_ROOT = Path(__file__).resolve().parents[2]
_POINTERS = _ROOT / "hardware" / "cad-artifacts.json"

#: An output is `…/bin/out/<target>/<the path the tree keeps it under>`, the same shape
#: `sync_tree` reads. The suffix is the pointer file's key.
_DECLARED = re.compile(r"/bin/out/([^/]+)/(.+)$")


def _bazel(*args: str, timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(["bazel", *args], cwd=_ROOT, capture_output=True,
                          text=True, timeout=timeout)




def _sha256(path):
    from _bookkeeping import read
    return read('cut.sha256',path)


def _labels(raw):
    return _bookkeeping_call('cut.labels',raw=raw)


def _expected(labels,failed):
    query = f"set({' '.join(labels)})" if labels else 'deps(//:everything)'
    q = _bazel('cquery',query,'--output=files',timeout=300)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith('ERROR')),f'exit {q.returncode}')
        raise SystemExit(f'  the build graph could not name the expected cut: {detail}')
    return set(_bookkeeping_call('cut.expected',stdout=q.stdout,failed=failed))


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--annotate',action='store_true',help='also emit GitHub workflow annotations')
    ap.add_argument('--failed',default='',help='comma-separated targets that failed this build; their outputs are whatever they wrote last time and are excluded')
    ap.add_argument('--assume-fresh',action='store_true',help='skip the up-to-date check and trust bazel-bin. Only honest straight after a full build in a container that starts empty.')
    ap.add_argument('--targets',default='',help='compare this built slice and its dependencies; default: //:everything')
    args = ap.parse_args()
    def callback(query):
        result = _bazel(*query['args'],timeout=query['timeout'])
        return {'returncode':result.returncode,'stdout':result.stdout,'stderr':result.stderr}
    result = _bookkeeping_call('cut.main',callback=callback,root=str(_ROOT),pointers_path=str(_POINTERS),annotate=args.annotate,failed=args.failed,assume_fresh=args.assume_fresh,targets=args.targets)
    print(result['output'],end='')
    return result['status']


def _tree_verdict(stale,compared,note):
    result = _bookkeeping_call('cut.tree_verdict',stale=stale,compared=compared)
    print(result['output'],end='')
    for args in result['notes']:
        note(*args)
    return result['status']


if __name__ == "__main__":
    sys.exit(main())
