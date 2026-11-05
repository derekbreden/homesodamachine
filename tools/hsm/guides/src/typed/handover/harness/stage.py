"""Stage pristine genrule work directories at a revision.

usage: stage.py <rev> <genrule> [<genrule> ...]
Writes templates/<genrule>/ and templates/<genrule>.json (scripts, missing sources).
Sources come from `git show <rev>:<path>`, falling back to the working tree for
uncommitted generated inputs. `:out/<pkg>/<path>` maps to `<path>`.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
RUN = Path(__file__).resolve().parent
SCRIPT = r'tools/cad-venv/bin/python tools/run\.py -- \$\$HSM_WORKSPACE/tools/cad-venv/bin/python (\S+)'
rev, names = sys.argv[1], sys.argv[2:]


def git_show(path):
    r = subprocess.run(['git', '-C', str(REPO), 'show', f'{rev}:{path}'], capture_output=True)
    return r.stdout if r.returncode == 0 else None


build = git_show('BUILD.bazel').decode()
blocks = {re.search(r'name = "([^"]+)"', b).group(1): b for b in build.split('\ngenrule(')[1:]}
for name in names:
    block = blocks[name]
    srcs = re.findall(r'"([^"]+)"', block[block.index('srcs = ['):block.index('outs = [')])
    outs = re.findall(r'"([^"]+)"', block[block.index('outs = ['):block.index(']', block.index('outs = ['))])
    scripts = re.findall(SCRIPT, block[block.index('cmd = '):])
    work = RUN / 'templates' / name
    if work.exists():
        shutil.rmtree(work)
    missing, fallback = [], []
    for p in srcs:
        rel = p.lstrip(':')
        if rel.startswith('pysrc/'):
            rel = rel[len('pysrc/'):]
        elif rel.startswith('out/'):
            rel = rel.split('/', 2)[2]
        data = git_show(rel)
        if data is None and (REPO / rel).is_file():
            data = (REPO / rel).read_bytes()
            fallback.append(rel)
        if data is None:
            missing.append(rel)
            continue
        dest = work / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    (RUN / 'templates' / f'{name}.json').write_text(json.dumps(
        {'rev': rev, 'scripts': scripts, 'srcs': len(srcs), 'outs': outs,
         'missing': missing, 'fallback': fallback}, indent=1))
    print(name, len(srcs), 'missing', len(missing), 'fallback', len(fallback), flush=True)
