"""Run a staged step once per machine-data binary, each in a fresh clone of its pristine
directory, and compare every file the runs leave.

usage: compare.py <workroot> <target> <label=program> [<label=program> ...]
   env: COVER_LOG=<path> sets HSM_COVER_LOG for the runs; KEEP=1 keeps the clones.
        BINDIR=<dir> takes the pinned workers from <dir> instead of bin/.
        SAVE=<dir> writes the first variant's file hashes to <dir>/<target>.json.
        AGAINST=<dir> compares every variant with the hashes saved in <dir>/<target>.json.
Prints one JSON line: per-variant CPU/wall/RSS, file counts and the files whose bytes differ.
"""
import hashlib, json, os, re, resource, subprocess, sys, time
from pathlib import Path

REPO = '/Users/derekbredensteiner/Developer/homesodamachine'
HERE = Path(__file__).resolve().parent
workroot, target = Path(sys.argv[1]), sys.argv[2]
variants = [arg.split('=', 1) for arg in sys.argv[3:]]
stage = json.loads((workroot / f'{target}.stage.json').read_text())
py = f'{REPO}/tools/cad-venv/bin/python'


#: The engine's per-request scratch directory, named for the requesting process's pid; the
#: equipment and route scratch JSON under tmp/machine-layout name it.
ENGINE_TMP = re.compile(rb'Library/Caches/hsm/parts/tmp/\d+-\d+')


def tree(work):
    """Each file's hash, with the clone's own directory written as <WORK> and the engine's
    scratch directory as <ENGINE-TMP>."""
    out = {}
    own = str(work).encode()
    for path in work.rglob('*'):
        if path.is_symlink() or not path.is_file() or '__pycache__' in path.parts:
            continue
        data = ENGINE_TMP.sub(b'<ENGINE-TMP>', path.read_bytes().replace(own, b'<WORK>'))
        out[str(path.relative_to(work))] = hashlib.sha256(data).hexdigest()
    return out


def run(label, program):
    pristine = workroot / target
    work = workroot / f'{target}.{label}'
    if work.exists():
        subprocess.run(['rm', '-rf', str(work)], check=True)
    subprocess.run(['cp', '-c', '-R', str(pristine), str(work)], check=True)
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe', 'HSM_WORKSPACE': REPO}
    if os.environ.get('COVER_LOG'):
        env['HSM_COVER_LOG'] = os.environ['COVER_LOG']
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    t = time.perf_counter()
    errors = []
    for line in stage['scripts']:
        argv = line.split()
        r = subprocess.run([py, str(HERE / 'harness.py'), os.environ.get('BINDIR', str(HERE / 'bin')), program, *argv], cwd=work,
                           env=env, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
        if r.returncode:
            errors.append({'script': line, 'stderr': r.stderr[-3000:]})
            break
    wall = time.perf_counter() - t
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    files = tree(work)
    if not os.environ.get('KEEP'):
        subprocess.run(['rm', '-rf', str(work)], check=True)
    return files, {'cpu': round(after.ru_utime - before.ru_utime + after.ru_stime - before.ru_stime, 2),
                   'wall': round(wall, 2), 'maxrss_mb': round(after.ru_maxrss / 2**20, 1),
                   'errors': errors}


if __name__ == '__main__':
    results, trees = {}, {}
    for label, program in variants:
        trees[label], results[label] = run(label, program)
    labels = [label for label, _ in variants]
    if os.environ.get('SAVE'):
        Path(os.environ['SAVE']).mkdir(parents=True, exist_ok=True)
        (Path(os.environ['SAVE']) / f'{target}.json').write_text(json.dumps(
            {'tree': trees[labels[0]], 'run': results[labels[0]], 'program': variants[0][1]}))
    if os.environ.get('AGAINST'):
        saved = json.loads((Path(os.environ['AGAINST']) / f'{target}.json').read_text())
        trees = {'saved': saved['tree'], **trees}
        labels = ['saved', *labels]
    base = trees[labels[0]]
    report = {'target': target, 'runs': results, 'files': len(base)}
    for label in labels[1:]:
        other = trees[label]
        differ = sorted(k for k in set(base) | set(other) if base.get(k) != other.get(k))
        report[f'differ:{label}'] = differ[:60]
        report[f'differ_count:{label}'] = len(differ)
    print(json.dumps(report), flush=True)
