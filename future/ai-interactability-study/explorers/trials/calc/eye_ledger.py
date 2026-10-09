"""The eye's ledger (wave 3, scene trials-24-calibration-graph): what each eye error costs each reading, and what each event costs to put right.

Part 1: readings against eye errors (the scene's right-hand table).  Formulas [derived, illustrative]:
   scale error s (fraction) acts on the image separation between the dot and what it is read against:
        knee 0.3 mm residual | rim edge 6.35 tan(psi) + 1.0 mm | ports 19.05 mm | the room 61.85 mm
   camera translation t costs  t x (depth difference) / H  against the rim edge (6.35 mm above the plate), 0 for things in the plate plane, t against the room
   pointing theta costs H tan(theta) against the room only (a uniform shift cancels in any comparison made in one picture)
   latency tau at a dot speed v costs v tau, the same for every reading
Part 2: the dependency graph and what each event costs (stale = full trial, suspect = cheap check).  The same tables as in the scene.
Run: python3 eye_ledger.py
"""
import math

print('Part 1. Defaults of the scene: scale 1 %, camera moved 5 mm, pointing 0.1 deg, H = 300 mm, latency 125 ms at 0.5 mm/s.  Cost in micrometres')
H, s, t, th, tau, v = 300.0, 0.01, 5.0, 0.1, 0.125, 0.5
tanpsi = 61.85 / H
rows = [
    ('the knee (0 mm apart)', s * 0.3, 0.0, 0.0),
    ('dot vs rim edge (6.35 mm up)', s * (6.35 * tanpsi + 1.0), t * 6.35 / H, 0.0),
    ('dot vs the two ports (19 mm)', s * 19.05, 0.0, 0.0),
    ('dot in the room frame', s * 61.85, t, math.tan(math.radians(th)) * H),
]
print('   reading                          scale     camera moved    pointing    latency')
for name, a, b, c in rows:
    print(f'   {name:32s} {a*1000:7.0f}   {b*1000:10.0f}   {c*1000:9.0f}   {v*tau*1000:7.0f}')
print()

ARR = {
    'gantry':  dict(poses=25, sec=6.0,  check=10, unknown=6),
    'cage':    dict(poses=40, sec=7.5,  check=20, unknown=32),
    'hexapod': dict(poses=20, sec=6.0,  check=15, unknown=9),
    'arm':     dict(poses=40, sec=10.0, check=10, unknown=28),
}
NODES = {  # id: (parents, full s, check s)
    'lens': ([], 240, 2), 'exp': ([], 10, 3), 'pose': (['lens', 'exp'], 60, 1), 'judge': (['pose', 'exp'], 300, 20), 'clock': ([], 60, 5),
    'rot': ([], 60, 1), 'appr': (['judge', 'clock'], 120, 40), 'geom': (['pose', 'judge', 'appr'], None, None), 'dot': (['geom', 'judge'], 90, 30),
    'seat': (['pose', 'judge', 'geom', 'dot'], 60, 20), 'seam': (['seat', 'judge', 'appr', 'rot', 'clock'], 300, 130), 'melt': (['dot'], 900, 0),
}
ORDER = ['lens', 'exp', 'clock', 'rot', 'pose', 'judge', 'appr', 'geom', 'dot', 'seat', 'seam', 'melt']
EVENTS = {
    'Camera knocked': (['pose'], []), 'Lens refocused or zoom touched': (['lens', 'exp', 'pose'], []), 'Room light changed': (['exp'], []),
    'A new tube is loaded': (['seat', 'seam'], []), 'Rotator re-clamped to the bench': (['rot', 'seat'], ['geom']),
    'Gun re-seated, red light changed': (['dot'], []), 'Positioner lost steps': (['geom'], ['appr']), 'Umbilical re-routed': ([], ['geom', 'appr']),
    'Afternoon: the bench warms 5 K': ([], ['exp', 'pose', 'geom']), 'Driver update or frame-rate change': (['clock', 'exp'], []),
}

def children(n):
    return [c for c in ORDER if n in NODES[c][0]]

def desc(n, seen=None):
    seen = set() if seen is None else seen
    for c in children(n):
        if c not in seen:
            seen.add(c); desc(c, seen)
    return seen

def cost(node, arr, full):
    a = ARR[arr]
    if node == 'geom':
        return a['poses'] * a['sec'] if full else a['check']
    return NODES[node][1] if full else NODES[node][2]

print('Part 2. Cost of putting each event right, seconds: (stale nodes, suspect nodes) minimum = trials + checks, worst = every suspect also needs its trial')
print('   event                                   ' + '   '.join(f'{a:>16s}' for a in ARR))
for ev, (stale, sus) in EVENTS.items():
    row = []
    for arr in ARR:
        state = {n: 'ok' for n in ORDER}
        for n in stale:
            state[n] = 'stale'
        for n in stale:
            for d in desc(n):
                if state[d] == 'ok':
                    state[d] = 'suspect'
        for n in sus:
            if state[n] == 'ok':
                state[n] = 'suspect'
            for d in desc(n):
                if state[d] == 'ok':
                    state[d] = 'suspect'
        ns = [n for n in ORDER if state[n] == 'stale']; nu = [n for n in ORDER if state[n] == 'suspect']
        mn = sum(cost(n, arr, True) for n in ns) + sum(cost(n, arr, False) for n in nu)
        wr = sum(cost(n, arr, True) for n in ns + nu)
        row.append(f'{len(ns)}s/{len(nu)}u {mn:5.0f}/{wr:5.0f}')
    print(f'   {ev:38s}  ' + '   '.join(f'{r:>16s}' for r in row))
print('   (Ns/Mu = N stale nodes and M suspect nodes; minimum / worst seconds.  A melt witness pass is 900 s and is counted whenever the dot is suspect or stale.)')
print()
print('Unknown counts: ' + ', '.join(f'{a}: {v["unknown"]}' for a, v in ARR.items()) + '.  Least poses from a board (2 numbers per pose): ' + ', '.join(f'{a}: {math.ceil(v["unknown"]/2)}' for a, v in ARR.items()) + '; poses used: ' + ', '.join(f'{a}: {v["poses"]}' for a, v in ARR.items()))
