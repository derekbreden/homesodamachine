"""Selected above-core fitting names without native CAD imports."""

import above_core as layout


def stem_elbow_names():
    """Warm native NeoFit stem elbows, in their component build order."""
    names = ('tee-fold', 'lower-valve-elbow', 'lower-pump-elbow',
             'reg-va-elbow', 'va-outlet-elbow', 'carbonator-fold',
             'gas-inlet-elbow', 'gas-lower-a', 'gas-lower-b',
             'gas-upper-a', 'gas-upper-b', 'soda-stem-elbow', 'soda-outlet-return-stem',
             'ya-stem-elbow', 'ya-fold-return', 'drain-outlet-stem', 'vb-inlet-turn',
             'vb-outlet-stem', 'vb-outlet-return', 'yb-stem-elbow')
    selected = layout.specification()['snapshots']
    return tuple(name for name in names if name in selected
                 and selected[name].get('geometry') != 'jg-turn-elbow')


def core_stem_elbow_names():
    """Cold-core-owned stems, excluded from the warm component builder."""
    names = ['reservoir-b-fill-lower'] if 'reservoir_b_fill_link' in layout.specification() else []
    return tuple(names)


def union_elbow_names():
    """Warm two-socket JG elbows; frame-carried drain and core fittings excluded."""
    selected = layout.specification()['snapshots']
    names = ('va-east-turn', 'ya-fold-inner', 'vb-inlet-turn', 'vb-outlet-return')
    return tuple(name for name in names
                 if selected.get(name, {}).get('geometry') == 'jg-turn-elbow')


def core_union_elbow_names():
    """Two-socket JG elbows owned by the cold-core assembly."""
    names = ['reservoir-b-fill-upper'] if 'reservoir_b_fill_link' in layout.specification() else []
    return tuple(names)
