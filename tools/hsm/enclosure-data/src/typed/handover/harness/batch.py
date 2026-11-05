"""Stage genrules at a revision, run them once per worker variant, and compare every file.

usage: batch.py --rev REV --rules all|a,b --variant label=pins.json [--variant ...]
                [--repeat N] [--jobs N] [--trace-dir DIR] [--keep] --out results.jsonl

A rule's work directory is rebuilt from the genrule's srcs in BUILD.bazel at REV (git cat-file),
falling back to the working tree for inputs the revision lacks. .cache and node_modules are
symlinked. Each variant runs in its own APFS clone of the staged template, under /usr/bin/time -l,
with HSM_REPO_ROOT=<work>, HSM_INPUT_DIGEST=probe and HSM_WORKSPACE=<repo>.
"""
import argparse
import concurrent.futures
import hashlib
import io
import json
import os
import re
import shutil
import subprocess
import threading
import time
import zipfile
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
RUN = Path(__file__).resolve().parents[1]
PY = REPO / 'tools/cad-venv/bin/python'
HARNESS = RUN / 'harness/run_step.py'
ENCLOSURE_READS = 'tools/hsm/enclosure-data/src/'

_git_lock = threading.Lock()
_git = None


def git_blob(rev, path):
    global _git
    with _git_lock:
        if _git is None:
            _git = subprocess.Popen(['git', '-C', str(REPO), 'cat-file', '--batch'],
                                    stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        _git.stdin.write(f'{rev}:{path}\n'.encode())
        _git.stdin.flush()
        header = _git.stdout.readline().decode()
        if header.endswith('missing\n'):
            return None
        size = int(header.split()[2])
        data = _git.stdout.read(size)
        _git.stdout.read(1)
        return data


def rules_at(rev):
    build = git_blob(rev, 'BUILD.bazel').decode()
    out = {}
    for m in re.finditer(r'genrule\(\n    name = "([^"]+)",', build):
        start = m.start()
        end = build.find('\n)\n', start)
        out[m.group(1)] = build[start:end]
    return out


def enclosure_rules(rev, rules):
    graph = json.loads(git_blob(rev, 'tools/bazel/graph.json'))
    entries = [k for k, v in graph.items() if any(ENCLOSURE_READS in r for r in v.get('reads', []))]
    names = []
    for name, block in rules.items():
        lines = [l for l in block.splitlines() if 'tools/run.py --' in l]
        if any(e in l for e in entries for l in lines):
            names.append(name)
    return sorted(names), entries


def parse_rule(block):
    srcs = re.findall(r'"([^"]+)"', block[block.index('srcs = ['):block.index('outs = [')])
    support = dict(re.findall(r'\*/bin/(support/\S+)\) t=(\S+);;', block))
    scripts = []
    for line in block.splitlines():
        if 'tools/run.py --' not in line:
            continue
        unset = re.findall(r'env -u (\S+)', line.split('tools/run.py --')[0])
        tail = line.split('tools/run.py -- $$HSM_WORKSPACE/tools/cad-venv/bin/python ', 1)[1]
        argv = tail.split(' > /dev/null')[0].split()
        scripts.append({'argv': argv, 'unset': unset})
    return srcs, support, scripts


def stage(rev, name, block, root):
    srcs, support, scripts = parse_rule(block)
    template = root / 'stage' / name
    marker = template / '.staged.json'
    if marker.exists():
        return template, json.loads(marker.read_text())
    if template.exists():
        shutil.rmtree(template)
    missing, fallback = [], []
    for label in srcs:
        label = label.lstrip(':')
        if '/node_modules/' in label:
            continue
        if label.startswith('pysrc/'):
            rel = label[len('pysrc/'):]
        elif label.startswith('out/'):
            rel = label.split('/', 2)[2]
        elif label.startswith('support/'):
            rel = support.get(label)
            if rel is None:
                missing.append(label)
                continue
        else:
            rel = label
        data = git_blob(rev, rel)
        if data is None and (REPO / rel).is_file():
            data = (REPO / rel).read_bytes()
            fallback.append(rel)
        if data is None:
            missing.append(rel)
            continue
        dest = template / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    (template / '.cache').symlink_to(REPO / '.cache')
    for d in ('tools/render/node_modules', 'web/node_modules', 'hardware/pcb/pcba/node_modules'):
        if (REPO / d).is_dir():
            (template / d).parent.mkdir(parents=True, exist_ok=True)
            (template / d).symlink_to(REPO / d)
    info = {'scripts': scripts, 'missing': missing, 'fallback': fallback, 'files': len(srcs)}
    marker.write_text(json.dumps(info))
    return template, info


# A graph node's construction site names this crate's source file and line: the generated file
# before the conversion, the typed file after it. Both are masked, and so is the run's own work
# directory, so that the comparison sees everything else.
_SOURCE = re.compile(rb'"source":\s*\{\s*(?:"line":\s*\d+,\s*"path":\s*"tools/hsm/enclosure-data/src/[^"]*"'
                     rb'|"path":\s*"tools/hsm/enclosure-data/src/[^"]*",\s*"line":\s*\d+)\s*\}')
_SRC = re.compile(rb'"src":\s*"tools/hsm/enclosure-data/src/[^"]*"')
_NPY_SHAPE = re.compile(rb"'shape':\s*\([^)]*\),?\s*")


def mask(data, work):
    data = data.replace(work, b'<WORK>')
    if b'enclosure-data/src/' in data:
        data = _SOURCE.sub(b'"source": {}', data)
        data = _SRC.sub(b'"src": ""', data)
    return data


def _npy(member, work):
    if member[:6] != b'\x93NUMPY':
        return mask(member, work)
    major = member[6]
    size = 2 if major == 1 else 4
    length = int.from_bytes(member[8:8 + size], 'little')
    header = member[8 + size:8 + size + length]
    body = mask(member[8 + size + length:], work)
    header = _NPY_SHAPE.sub(b'', header).replace(b' ', b'') if body != member[8 + size + length:] else header
    return header + body


def normalized(rel, data, work):
    """The bytes the comparison hashes: `data` with source sites and the work path masked."""
    if rel.endswith('.npz') and data[:2] == b'PK':
        try:
            z = zipfile.ZipFile(io.BytesIO(data))
            parts = []
            for info in z.infolist():
                parts.append(info.filename.encode() + b'\0' + _npy(z.read(info.filename), work))
            return b'\1'.join(parts)
        except zipfile.BadZipFile:
            return mask(data, work)
    if rel.endswith('.mesh') and len(data) > 4:
        length = int.from_bytes(data[:4], 'little')
        if 4 + length <= len(data) and data[4:5] == b'{':
            return mask(data[4:4 + length], work) + b'\0' + mask(data[4 + length:], work)
    return mask(data, work)


# Extended hashing (`tree(work, extended=True)`, the `.base.1` manifests) also leaves out the wall-time
# samples, masks a part program's scratch directory under the parts cache (new on every run), and
# replaces a sha256 that names a file of the same run by that file's path: the file itself is compared
# on its own, while its raw digest carries the work path and source sites the masks remove.
NOISE = {'hardware/ledger/.build-time.samples.json'}
_PARTS_TMP = re.compile(rb'(Library/Caches/hsm/parts/tmp/)\d+-\d+')
_HEX = re.compile(rb'[0-9a-f]{64}')


def _digest(path):
    h = hashlib.sha256()
    with open(path, 'rb') as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest().encode()


def tree(work, extended=False):
    """Every file under `work`: its relative path and the hash of its normalized bytes."""
    paths = {}
    marker = str(work).encode()
    for dirpath, dirnames, filenames in os.walk(work):
        dirnames[:] = [d for d in dirnames if d != '__pycache__' and not os.path.islink(os.path.join(dirpath, d))]
        for f in filenames:
            p = os.path.join(dirpath, f)
            if os.path.islink(p) or f == '.staged.json':
                continue
            paths[os.path.relpath(p, work)] = p
    names = {}
    if extended:
        for rel in sorted(paths):
            names.setdefault(_digest(paths[rel]), rel.encode())
    out = {}
    for rel, p in paths.items():
        if extended and rel in NOISE:
            continue
        with open(p, 'rb') as fh:
            data = fh.read()
        body = normalized(rel, data, marker)
        if extended:
            body = _PARTS_TMP.sub(rb'\1<TMP>', body)
            body = _HEX.sub(lambda m: b'<sha256:' + names[m.group()] + b'>' if m.group() in names else m.group(), body)
        out[rel] = hashlib.sha256(body).hexdigest()
    return out


def time_l(stderr):
    """Parse /usr/bin/time -l's trailer."""
    real = user = sys_ = rss = None
    m = re.search(r'^\s*([\d.]+) real\s+([\d.]+) user\s+([\d.]+) sys', stderr, re.M)
    if m:
        real, user, sys_ = map(float, m.groups())
    m = re.search(r'^\s*(\d+)\s+maximum resident set size', stderr, re.M)
    if m:
        rss = int(m.group(1))
    return real, user, sys_, rss


def run_variant(rule, template, info, label, pins, index, args):
    work = RUN / 'work' / f'{rule}.{label}.{index}'
    if work.exists():
        shutil.rmtree(work)
    work.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(['cp', '-cR', str(template), str(work)], check=True)
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe',
           'HSM_WORKSPACE': str(REPO), 'HSM_PIN_SPEC': pins, 'HSM_NO_REALIZED_CACHE': '1'}
    if args.trace_dir:
        env['HSM_TRACE_DIR'] = args.trace_dir
        env['HSM_TRACE_STEP'] = rule
    totals = {'wall': 0.0, 'cpu': 0.0, 'maxrss_mb': 0.0}
    status, error = 'ok', None
    for script in info['scripts']:
        senv = dict(env)
        for var in script['unset']:
            senv.pop(var, None)
        t = time.perf_counter()
        r = subprocess.run(['python3', str(REPO / 'tools/run.py'), *(['--timing'] if args.timing else []), '--',
                            '/usr/bin/time', '-l', str(PY), str(HARNESS), *script['argv']],
                           cwd=work, env=senv, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                           text=True, errors='replace')
        wall = time.perf_counter() - t
        real, user, sys_, rss = time_l(r.stderr)
        totals['wall'] += wall
        totals['cpu'] += (user or 0) + (sys_ or 0)
        totals['maxrss_mb'] = max(totals['maxrss_mb'], (rss or 0) / 1e6)
        if r.returncode:
            status = 'error'
            error = r.stderr[-4000:]
            break
    hashes = tree(work, getattr(args, 'extended', False))
    row = {'rule': rule, 'variant': label, 'index': index, 'status': status,
           'wall': round(totals['wall'], 2), 'cpu': round(totals['cpu'], 2),
           'maxrss_mb': round(totals['maxrss_mb'], 1), 'files': len(hashes)}
    if error:
        row['error'] = error
    return row, hashes, work


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--rev', required=True)
    ap.add_argument('--rules', required=True)
    ap.add_argument('--variant', action='append', required=True)
    ap.add_argument('--repeat', type=int, default=1)
    ap.add_argument('--jobs', type=int, default=1)
    ap.add_argument('--trace-dir')
    ap.add_argument('--keep', action='store_true')
    ap.add_argument('--timing', action='store_true')
    ap.add_argument('--save-hashes', help='directory for <rule>.<label>.<index>.json hash manifests')
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    rules = rules_at(args.rev)
    if args.rules == 'all':
        names, _ = enclosure_rules(args.rev, rules)
    else:
        names = args.rules.split(',')
    variants = [v.split('=', 1) for v in args.variant]
    out = open(args.out, 'a')
    lock = threading.Lock()

    def emit(row):
        with lock:
            out.write(json.dumps(row) + '\n')
            out.flush()

    def one(rule):
        template, info = stage(args.rev, rule, rules[rule], RUN)
        emit({'rule': rule, 'staged': True, 'scripts': info['scripts'],
              'missing': info['missing'], 'fallback': info['fallback'][:20],
              'fallback_count': len(info['fallback'])})
        base = None
        works, differs = [], False
        for index in range(args.repeat):
            for label, pins in variants:
                row, hashes, work = run_variant(rule, template, info, label, pins, index, args)
                works.append(work)
                if args.save_hashes:
                    os.makedirs(args.save_hashes, exist_ok=True)
                    with open(os.path.join(args.save_hashes, f'{rule}.{label}.{index}.json'), 'w') as fh:
                        json.dump({'row': row, 'hashes': hashes}, fh, sort_keys=True)
                if base is None:
                    base = (label, hashes)
                    row['outputs'] = sorted(k for k in hashes
                                            if not (template / k).exists()
                                            or hashlib.sha256(normalized(k, (template / k).read_bytes(),
                                                                         str(template).encode())).hexdigest() != hashes[k])
                    row['output_count'] = len(row['outputs'])
                    row['outputs'] = row['outputs'][:200]
                else:
                    differ = sorted(k for k in set(hashes) | set(base[1]) if hashes.get(k) != base[1].get(k))
                    row['against'] = base[0]
                    row['differ'] = differ[:100]
                    row['differ_count'] = len(differ)
                    differs = differs or bool(differ)
                if row['status'] != 'ok':
                    differs = True
                emit(row)
        # A rule whose variants differ keeps its work directories for reading.
        if not args.keep and not differs:
            for work in works:
                shutil.rmtree(work, ignore_errors=True)

    with concurrent.futures.ThreadPoolExecutor(args.jobs) as pool:
        for f in concurrent.futures.as_completed([pool.submit(one, r) for r in names]):
            f.result()


if __name__ == '__main__':
    main()
