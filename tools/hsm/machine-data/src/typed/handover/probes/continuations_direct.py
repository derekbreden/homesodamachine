"""Rebuild the probe's `continuations` request, send it to layout-data workers directly, and
compare each answer with the base and rear probe results.

    python3 continuations_direct.py <layout-data binary> [...]
"""
import json, subprocess, sys
R = '/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700'
spec = json.loads(open(f'{R}/steps/enclosure/hardware/manifold-layout/above-core.json').read())
probes = {k: json.load(open(f'{R}/ws/rear/probe-{k}.json')) for k in ('base', 'rear')}


def plain(d):
    if d is None or isinstance(d, (bool, str)):
        return d
    (kind, v), = [(k, d[k]) for k in d if k in ('int', 'float', 'list', 'tuple', 'dict')] or [(None, None)]
    if kind == 'int':
        return v
    if kind == 'float':
        return float(v)
    if kind in ('list', 'tuple'):
        return [plain(x) for x in v]
    if kind == 'dict':
        return {plain(k): plain(x) for k, x in v}
    raise ValueError(d)


modules = plain(probes['base']['modules'])
params = {'check_insertion': modules[2], 'bulkhead_tube_stop': plain(probes['base']['reference'])}


def ask(binary, request):
    p = subprocess.run([binary, '--serve'], input=json.dumps(request) + '\n', capture_output=True, text=True, check=True)
    return json.loads(p.stdout)


def fake_station(name, port):
    return [float(len(name)), float(len(port)), 0.5], [0., 0., 1.], 6.35


def same(a, b, path='', out=None):
    if isinstance(a, list) and isinstance(b, list) and len(a) == len(b):
        for i, (x, y) in enumerate(zip(a, b)):
            same(x, y, f'{path}[{i}]', out)
    elif isinstance(a, dict) and isinstance(b, dict) and list(a) == list(b):
        for k in a:
            same(a[k], b[k], f'{path}.{k}', out)
    elif not (a == b and type(a) is type(b)):
        out.append((path, a, b))
    return out


for binary in sys.argv[1:]:
    wanted = ask(binary, {'op': 'route-stations', 'operation': 'rear-continuations', 'spec': spec})
    stations = {f'{n}.{p}': fake_station(n, p) for n, p in wanted}
    rows = ask(binary, {'op': 'rear-continuations', 'spec': spec, 'stations': stations, 'params': params})
    answer = {k: v for k, v in rows}
    print('==', binary, len(wanted), 'stations,', len(answer), 'routes')
    for label, probe in probes.items():
        d = same(answer, plain(probe['continuations']), '', [])
        print(f'  vs probe-{label}: {len(d)} differ', d[:3])
