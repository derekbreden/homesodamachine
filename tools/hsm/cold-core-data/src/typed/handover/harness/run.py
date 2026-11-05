"""Run staged genrules once each with one pin set; hash every file each leaves.

usage: run.py <label> <pins.json> <genrule> [<genrule> ...] [--trace]
Writes results/<label>/<genrule>.json: per-script cpu (user+sys of the generator and its
waited workers), wall, max RSS, and the SHA-256 of every regular file in the work dir.
"""
import fcntl, hashlib, json, os, resource, shutil, subprocess, sys, time
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
RUN = Path(__file__).resolve().parent
PY = str(REPO / 'tools/cad-venv/bin/python')
args = [a for a in sys.argv[1:] if not a.startswith('--')]
tracing = '--trace' in sys.argv
keep = '--keep' in sys.argv
label, pins, names = args[0], str(Path(args[1]).resolve()), args[2:]
out_dir = RUN / 'results' / label
out_dir.mkdir(parents=True, exist_ok=True)


def tree(work):
    out = {}
    for path in sorted(work.rglob('*')):
        if path.is_symlink() or not path.is_file() or '__pycache__' in path.parts:
            continue
        out[str(path.relative_to(work))] = hashlib.sha256(path.read_bytes()).hexdigest()
    return out


for name in names:
    meta = json.loads((RUN / 'templates' / f'{name}.json').read_text())
    # One path per step whatever the label: outputs that record absolute paths compare equal.
    # Runs of one step take turns on its lock.
    work = RUN / 'work' / name
    work.parent.mkdir(parents=True, exist_ok=True)
    lock = open(RUN / 'work' / f'{name}.lock', 'w')
    fcntl.flock(lock, fcntl.LOCK_EX)
    if work.exists():
        shutil.rmtree(work)
    subprocess.run(['cp', '-cR', str(RUN / 'templates' / name), str(work)], check=True)
    (work / '.cache').symlink_to(REPO / '.cache')
    for d in ('tools/render/node_modules', 'web/node_modules'):
        if (REPO / d).is_dir():
            (work / d).parent.mkdir(parents=True, exist_ok=True)
            (work / d).symlink_to(REPO / d)
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe',
           'HSM_WORKSPACE': str(REPO), 'HSM_PINS': pins,
           'PYTHONPATH': os.pathsep.join(filter(None, [str(RUN / 'pinhook'), os.environ.get('PYTHONPATH')]))}
    if tracing:
        env['HSM_TRACE_COLD'] = str(out_dir / f'{name}.trace.jsonl')
        Path(env['HSM_TRACE_COLD']).unlink(missing_ok=True)
    rows = []
    for script in meta['scripts']:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        t = time.perf_counter()
        r = subprocess.run(['/usr/bin/time', '-l', PY, str(RUN / 'inner.py'), pins, script],
                           cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True)
        wall = time.perf_counter() - t
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        rss = next((int(line.split()[0]) for line in r.stderr.splitlines()
                    if 'maximum resident set size' in line), 0)
        rows.append({'script': script, 'rc': r.returncode, 'wall': round(wall, 3),
                     'cpu': round((after.ru_utime - before.ru_utime)
                                  + (after.ru_stime - before.ru_stime), 3),
                     'top_rss_mb': round(rss / 1e6, 1),
                     'stderr': r.stderr[-3000:] if r.returncode else ''})
        if r.returncode:
            break
    files = tree(work)
    (out_dir / f'{name}.json').write_text(json.dumps({'runs': rows, 'files': files}, indent=0))
    status = 'ok' if all(row['rc'] == 0 for row in rows) else 'FAIL'
    print(json.dumps({'step': name, 'status': status, 'files': len(files),
                      'cpu': [row['cpu'] for row in rows], 'wall': [row['wall'] for row in rows]}),
          flush=True)
    if not keep:
        shutil.rmtree(work)
    lock.close()
