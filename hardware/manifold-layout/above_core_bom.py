"""Selected above-core fitting names without native CAD imports."""

import above_core as layout


from _layout_data import data as _data

def reservoir_gate_elbow_hosts():
    return {name: tuple(row) for name, row in _data('reservoir-gates').items()}


def stem_elbow_names():
    return tuple(_data('stem-elbow-names', spec=layout.specification()))


def core_stem_elbow_names():
    """Cold-core-owned stems, excluded from the warm component builder."""
    return ()


def union_elbow_names():
    return tuple(_data('union-elbow-names', spec=layout.specification()))


def core_union_elbow_names():
    """Two-socket JG elbows owned by the cold-core assembly."""
    return ()
