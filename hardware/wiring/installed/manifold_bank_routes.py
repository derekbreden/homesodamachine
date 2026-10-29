"""Grouped J1/J2 fanouts through the lid's two front-manifold cable seats.

The existing routing composer owns terminal positions and end lands. These
guides use one common board crossing and one descent into each cable channel;
the front-going leads then separate into the open aisles between the valves.
"""

_J1 = ('J1-COM', 'J1-OUT3', 'J1-OUT4', 'J1-OUT5',
       'J1-OUT6', 'J1-OUT7', 'J1-OUT8')
_J2 = ('J2-OUT1', 'J2-OUT2', 'J2-FAN', 'J2-COM')


def dress_manifold_bank_guides(connection, guides, attachments, saved):
    """Return the named bank fanout, or None for an unrelated conductor."""
    if connection.id == 'J2-positive-K':
        saved['note'] = ('The V-K positive lead passes beside the manifold '
                         'bank before rejoining its retained east-wall hook '
                         'course; terminal positions and hook datums remain '
                         'fixed.')
        return [(84.8, 185., 267.), *guides]
    if connection.id not in _J1 + _J2:
        return None
    saved['note'] = ('Front-going J1/J2 leads retain their terminal lands and '
                     'pass through the two-channel lid bank using a shared '
                     'board crossing and separated fore fanouts; physical '
                     'dressing and packing remain unqualified.')
    from .retainers import manifold_bank_site
    site = manifold_bank_site()
    x, _y, z = site['target_centers'][connection.id]
    group = _J1 if connection.id in _J1 else _J2
    index = group.index(connection.id)
    start = attachments.terminals[connection.start].point
    end = attachments.terminals[connection.end].point
    flat_y = 203. + index * 1.85
    flat_z = 289.2 if group is _J1 else 291.15
    common = [(start[0], start[1], flat_z),
              (start[0], flat_y, flat_z), (x, flat_y, flat_z),
              (x, flat_y, z), (x, 178., z)]
    if connection.id == 'J1-COM':
        return common + [(end[0]-8., end[1], end[2])]
    if connection.id == 'J2-COM':
        return common + [(76.5, end[1], end[2])]
    if connection.id == 'J2-FAN':
        return common + [(x, 164., z), (92.5, 164., z),
                         (92.5, 164., 150.), (92.5, 50., 150.),
                         (end[0], 50., end[2])]
    if connection.id == 'J1-OUT6':
        return common + [(x, 163., end[2]+6.),
                         (end[0], 163., end[2]+6.),
                         (end[0], end[1], end[2]+6.)]
    if connection.id == 'J2-OUT1':
        return common + [(53., 180., z), (53., 180., 293.5),
                         (53., 166.5, 293.5), (end[0], 166.5, 293.5),
                         (end[0], end[1], 293.5)]
    lane, turn_y = {
        'J1-OUT3': (43.2, 135.),
        'J1-OUT4': (45.05, 131.),
        'J1-OUT5': (46.9, 144.),
        'J1-OUT7': (48.75, 143.),
        'J1-OUT8': (50.6, 140.),
        'J2-OUT2': (52.45, 139.),
    }[connection.id]
    height = end[2] - 6. if connection.end in (
        'V-C.negative', 'V-D.negative', 'V-E.negative', 'V-H.negative') else end[2]
    return common + [(lane, 168., z), (lane, 168., height),
                     (lane, turn_y, height), (end[0], turn_y, height)]
