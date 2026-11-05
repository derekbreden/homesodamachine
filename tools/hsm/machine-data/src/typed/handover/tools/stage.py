"""Stage genrule work directories at one revision, from BUILD.bazel's srcs.

usage: stage.py <rev> <workroot> <target> [<target> ...]
Each target's pristine directory is <workroot>/<target>; a JSON line per target names its
scripts (with arguments), staged file count and any srcs taken from the working tree.
"""
import json, re, subprocess, sys
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
rev, workroot, targets = sys.argv[1], Path(sys.argv[2]), sys.argv[3:]


def show(rev, paths):
    """Blob bytes per path at rev (None where absent), through one cat-file process."""
    proc = subprocess.Popen(['git', '-C', str(REPO), 'cat-file', '--batch'], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE)
    out = {}
    for p in paths:
        proc.stdin.write(f'{rev}:{p}\n'.encode()); proc.stdin.flush()
        header = proc.stdout.readline().split()
        if len(header) == 2 and header[1] == b'missing':
            out[p] = None
            continue
        size = int(header[2])
        out[p] = proc.stdout.read(size)
        proc.stdout.read(1)
    proc.stdin.close(); proc.wait()
    return out


build = show(rev, ['BUILD.bazel'])['BUILD.bazel'].decode()


def block(target):
    start = build.index(f'    name = "{target}",')
    end = build.find('\ngenrule(', start)
    return build[start:end if end >= 0 else len(build)]


def relpath(label):
    rel = label.lstrip(':')
    if rel.startswith('pysrc/'):
        return rel[len('pysrc/'):]
    if rel.startswith('out/'):
        return rel.split('/', 2)[2]
    if rel == 'support/enclosure-assembly-graph.json':
        return 'tools/bazel/graph.json'
    return rel


for target in targets:
    b = block(target)
    srcs = re.findall(r'"([^"]+)"', b[b.index('srcs = ['):b.index('outs = [')])
    outs = re.findall(r'"([^"]+)"', b[b.index('outs = ['):b.index('cmd = ')])
    cmd = b[b.index('cmd = '):]
    scripts = [line.strip() for line in re.findall(
        r'tools/run\.py -- \$\$HSM_WORKSPACE/tools/cad-venv/bin/python ([^>\n]*)', cmd)]
    work = workroot / target
    if work.exists():
        subprocess.run(['rm', '-rf', str(work)], check=True)
    rels = []
    for label in srcs:
        rel = relpath(label)
        if '/node_modules/' in rel:
            continue
        rels.append(rel)
    blobs = show(rev, rels)
    tree = []
    for rel in rels:
        data = blobs[rel]
        if data is None and (REPO / rel).is_file():
            data = (REPO / rel).read_bytes()
            tree.append(rel)
        if data is None:
            continue
        dest = work / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    (work / '.cache').symlink_to(REPO / '.cache')
    for d in ('tools/render/node_modules', 'web/node_modules', 'hardware/pcb/pcba/node_modules'):
        if (REPO / d).is_dir():
            (work / d).parent.mkdir(parents=True, exist_ok=True)
            (work / d).symlink_to(REPO / d)
    record = {'target': target, 'rev': rev, 'scripts': scripts, 'files': len(rels),
              'outs': [relpath(o) for o in outs], 'from_tree': tree}
    (workroot / f'{target}.stage.json').write_text(json.dumps(record))
    print(json.dumps(record), flush=True)
