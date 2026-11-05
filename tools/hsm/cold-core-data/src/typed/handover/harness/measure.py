"""Median CPU of three warm runs per step and pin set, the cold-core-data worker's own beside.

usage: measure.py <out.json> <label>=<pins.json> [...] -- <step> [<step> ...]
Each step runs once per pin set to warm, then three rounds run every pin set once, in turn.
cpu: user+sys of the generator and every process it waited for (its Rust workers included).
worker_cpu / worker_rss_mb: what wrap (wrap.c) records of each PROGRAM process.
"""
import json, os, resource, shutil, statistics, subprocess, sys, time
from pathlib import Path

REPO = Path('/Users/derekbredensteiner/Developer/homesodamachine')
RUN = Path(__file__).resolve().parent
PY = str(REPO / 'tools/cad-venv/bin/python')
split = sys.argv.index('--')
out_path = Path(sys.argv[1])
pin_sets = dict(a.split('=', 1) for a in sys.argv[2:split])
steps = sys.argv[split + 1:]
ROUNDS = 3
PROGRAM = 'cold-core-data'  # the worker timed on its own


def worker_records(directory):
    cpu, rss, count = 0.0, 0, 0
    for record in sorted(directory.glob('*')):
        user, system, peak = record.read_text().split()
        cpu += float(user) + float(system)
        rss = max(rss, int(peak))
        count += 1
    return round(cpu, 3), round(rss / 1e6, 1), count


def run(step, label):
    meta = json.loads((RUN / 'templates' / f'{step}.json').read_text())
    pins = json.loads(Path(pin_sets[label]).read_text())
    real = pins[PROGRAM]
    work = RUN / 'work' / f'{step}-measure-{label}'
    if work.exists():
        shutil.rmtree(work)
    subprocess.run(['cp', '-cR', str(RUN / 'templates' / step), str(work)], check=True)
    (work / '.cache').symlink_to(REPO / '.cache')
    for d in ('tools/render/node_modules', 'web/node_modules'):
        if (REPO / d).is_dir():
            (work / d).parent.mkdir(parents=True, exist_ok=True)
            (work / d).symlink_to(REPO / d)
    times = RUN / 'work' / f'{step}-measure-{label}.times'
    if times.exists():
        shutil.rmtree(times)
    wrapped = RUN / 'work' / f'{step}-measure-{label}.pins.json'
    wrapped.write_text(json.dumps({**pins, PROGRAM: str(RUN / 'wrap')}))
    env = {**os.environ, 'HSM_REPO_ROOT': str(work), 'HSM_INPUT_DIGEST': 'probe',
           'HSM_WORKSPACE': str(REPO), 'HSM_WRAP_REAL': real, 'HSM_TIME_DIR': str(times),
           'HSM_PINS': str(wrapped),
           'PYTHONPATH': os.pathsep.join(filter(None, [str(RUN / 'pinhook'), os.environ.get('PYTHONPATH')]))}
    cpu = wall = 0.0
    rss = 0
    for script in meta['scripts']:
        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        t = time.perf_counter()
        r = subprocess.run(['/usr/bin/time', '-l', PY, str(RUN / 'inner.py'), str(wrapped), script],
                           cwd=work, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                           text=True)
        wall += time.perf_counter() - t
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        if r.returncode:
            raise SystemExit(f'{step} {label} {script} failed:\n{r.stderr[-3000:]}')
        cpu += (after.ru_utime - before.ru_utime) + (after.ru_stime - before.ru_stime)
        rss = max(rss, next((int(line.split()[0]) for line in r.stderr.splitlines()
                             if 'maximum resident set size' in line), 0))
    worker_cpu, worker_rss, workers = worker_records(times) if times.exists() else (0.0, 0.0, 0)
    shutil.rmtree(work)
    shutil.rmtree(times, ignore_errors=True)
    wrapped.unlink()
    return {'cpu': round(cpu, 3), 'wall': round(wall, 3), 'top_rss_mb': round(rss / 1e6, 1),
            'worker_cpu': worker_cpu, 'worker_rss_mb': worker_rss, 'workers': workers}


results = json.loads(out_path.read_text()) if out_path.exists() else {}
for step in steps:
    rows = {label: [] for label in pin_sets}
    for label in pin_sets:
        run(step, label)
    for _ in range(ROUNDS):
        for label in pin_sets:
            rows[label].append(run(step, label))
    summary = {}
    for label, runs in rows.items():
        summary[label] = {key: statistics.median(r[key] for r in runs)
                          for key in ('cpu', 'wall', 'top_rss_mb', 'worker_cpu', 'worker_rss_mb')}
        summary[label]['runs'] = runs
    results[step] = summary
    out_path.write_text(json.dumps(results, indent=1))
    print(json.dumps({step: {label: {k: v for k, v in s.items() if k != 'runs'}
                             for label, s in summary.items()}}), flush=True)
