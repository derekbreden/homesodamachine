"""Integral tube and cable restraints on their owning enclosure quadrant."""
from pathlib import Path
import sys

_ROOT=next(p for p in Path(__file__).resolve().parents if (p/'hardware'/'wiring').is_dir())
for directory in (_ROOT,_ROOT/'hardware'/'printed-parts'/'cadlib'):
    if str(directory) not in sys.path:
        sys.path.insert(0,str(directory))

import route_snap


def features(host):
    """Named native additions; each root overlaps its existing host plane."""
    from hardware.wiring.installed.retainers import cable_sites
    from _tube_snap_sites import tube_sites
    result=[]
    for site in cable_sites():
        if site['host']!=host:
            continue
        body=route_snap.cable_hook(site['origin'],site['outward'],site['profile_up'],
            seat_depth=site['seat_depth'],seat_height=site['seat_height'],
            span=site['span'],stock=site['stock'],beak=site['beak'])
        result.append((dict(site,kind='cable'),body))
    for site in tube_sites():
        if site['host']!=host:
            continue
        body=route_snap.tube_clip(site['centre'],site['along'],site['outward'],
            site['root_distance'],tube_od=site['tube_od'],bore_diameter=site['bore_diameter'],
            span=site['span'],wing=site['wing'],print_up=site['print_up'])
        result.append((dict(site,kind='tube'),body))
    return tuple(result)


def apply(piece,y_side,z_side):
    additions=[shape for _site,shape in features(f'enclosure-{y_side}-{z_side}')]
    return piece.fuse(*additions) if additions else piece
