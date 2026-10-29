"""Selected above-core fitting names without native CAD imports."""

import above_core as layout


def reservoir_gate_elbow_hosts():
    """Front-valve stem elbows for the reservoir fill/draw continuations."""
    return {'reservoir-a-fill-turn': ('valve-v-f', 'outlet'),
            'reservoir-a-draw-turn': ('valve-v-e', 'inlet'),
            'reservoir-b-fill-turn': ('valve-v-i', 'outlet')}


def stem_elbow_names():
    """Warm native NeoFit stem elbows, in their component build order."""
    names = ('tee-fold', 'lower-valve-elbow', 'lower-pump-elbow',
             'reg-va-elbow', 'va-outlet-elbow', 'carbonator-fold',
             'gas-inlet-elbow', 'gas-lower-a', 'gas-lower-b',
             'gas-upper-a', 'gas-upper-b', 'soda-stem-elbow', 'soda-outlet-return-stem',
             'ya-stem-elbow', 'drain-outlet-stem', 'vb-inlet-turn',
             'vb-outlet-stem', 'vb-outlet-return', 'yb-stem-elbow',
             *reservoir_gate_elbow_hosts())
    selected = layout.specification()['snapshots']
    return tuple(name for name in names if name in selected
                 and selected[name].get('geometry') != 'jg-turn-elbow')


def core_stem_elbow_names():
    """Cold-core-owned stems, excluded from the warm component builder."""
    return ()


def union_elbow_names():
    """Warm two-socket JG elbows; frame-carried drain and core fittings excluded."""
    selected = layout.specification()['snapshots']
    names = ('va-east-turn', 'ya-fold-inner', 'vb-inlet-turn', 'vb-outlet-return')
    return tuple(name for name in names
                 if selected.get(name, {}).get('geometry') == 'jg-turn-elbow')


def core_union_elbow_names():
    """Two-socket JG elbows owned by the cold-core assembly."""
    return ()
