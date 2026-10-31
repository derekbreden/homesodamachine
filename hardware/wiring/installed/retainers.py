"""Integral cable-retainer datums and their local installed guide stations.

All coordinates use enclosure-world millimetres. This module is pure data and
route dressing; each host constructs its clips with cadlib.route_snap.
Terminal positions and the remaining guide stations belong to the wiring model.
"""


def manifold_bank_site():
    """The lid's front-going J1/J2 leads, beside the retained PCB."""
    groups = (
        ('J1', 74.1, 263.05,
         ('J1-OUT8', 'J1-OUT7', 'J1-OUT6', 'J1-OUT5',
          'J1-OUT4', 'J1-OUT3', 'J1-COM')),
        ('J2', 79.3, 260.275,
         ('J2-COM', 'J2-FAN', 'J2-OUT2', 'J2-OUT1')),
    )
    return {
        'id': 'front-manifold-bank',
        'host': 'foam-cap-lid-top',
        'origin': (70., 192.6, 253.4),
        'seat_depth': 2.2,
        'seat_heights': (13.3, 7.75),
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'target_centers': {
            wire: (x, 192.6, z+(i-(len(wires)-1)/2.)*1.85)
            for _group, x, z, wires in groups
            for i, wire in enumerate(wires)
        },
        'stock_basis': 'Eleven nominal 1.70 mm insulated 22 AWG leads on 1.85 mm pitch; the V-A, V-B and V-K branches split before this bank.',
        'fit_scope': 'The 2.2 mm depth, retaining lip and four-lead section use the accepted cable coupon. The seven-lead grouping and installed dressing retain their physical-fit scope.',
    }


def rear_level_hook_site():
    """Reservoir A's five level leads beside the PSU, after the sensor fork."""
    wires = ('J6-GND', 'J6-RA4', 'J6-RA3', 'J6-RA2', 'J6-RA1')
    return {
        'id': 'reservoir-a-levels',
        'host': 'foam-cap-lid-top',
        'origin': (-78., 424., 253.4),
        'seat_depth': 2.2,
        'seat_height': 9.6,
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'target_centers': {
            wire: (-73.9, 424., 257.5+i*1.85)
            for i, wire in enumerate(wires)
        },
        'stock_basis': 'Five nominal 1.70 mm insulated 22 AWG leads on 1.85 mm pitch.',
        'fit_scope': 'The accepted cable entry and retaining lip with a five-lead seat; complete installed dressing retains its physical-fit scope.',
    }


def cable_sites():
    """One row per hook, using cable_hook's explicit frame and section keys."""
    return ({
        'id': 'dc1-west-pair',
        'host': 'enclosure-back-top',
        'origin': (-98.5, 320.5, 271.35),
        'outward': (1., 0., 0.),
        'profile_up': (0., 0., -1.),
        'seat_depth': 3.5,
        'seat_height': 7.5,
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'centre_world_mm': (-96.75, 320.5, 258.1),
        'target_centers': {
            'DC1-GND': (-96.75, 320.5, 256.1),
            'DC1-V12': (-96.75, 320.5, 260.1),
        },
        'stock_basis': 'Two nominal 3.0 mm insulated 16 AWG wires; physical insulation OD unmeasured.',
        'fit_scope': 'Matched two-wire seat; physical insertion, retention and layer survival remain observations.',
    }, {
        'id': 'fan-east-pair',
        'host': 'enclosure-front-top',
        'origin': (98.5, 150., 182.775),
        'outward': (-1., 0., 0.),
        'profile_up': (0., 0., 1.),
        'seat_depth': 2.2,
        'seat_height': 4.05,
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'centre_world_mm': (97.4, 150., 193.),
        'target_centers': {
            'J2-FAN': (97.4, 150., 193.925),
            'J2-positive-fan': (97.4, 150., 192.075),
        },
        'stock_basis': 'Two nominal 1.70 mm insulated 22 AWG fan leads on 1.85 mm pitch.',
        'fit_scope': 'The accepted retaining lip and 2.2 mm seat depth retain the fan-only pair; the donor fan landing remains unlocated.',
    }, {
        'id': 'j11-west-ribbon',
        'host': 'enclosure-front-bottom',
        'origin': (-98.5, 90., 5.925),
        'outward': (1., 0., 0.),
        'profile_up': (0., 0., 1.),
        'seat_depth': 2.2,
        'seat_height': 7.75,
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'centre_world_mm': (-97.4, 90., 18.),
        'target_centers': {
            'J11-GND': (-97.4, 90., 20.775),
            'J11-V5': (-97.4, 90., 18.925),
            'J11-DOUT': (-97.4, 90., 17.075),
            'J11-AOUT': (-97.4, 90., 15.225),
        },
        'stock_basis': 'Bare 4P 22 AWG ribbon, nominal 1.70 mm conductor OD on 1.85 mm pitch.',
        'fit_scope': 'The accepted 4P seat and entry section on a full solid wall root below the ventilation field; installed harness dressing remains a physical observation.',
    }, {
        'id': 'j5-west-ribbon',
        'host': 'enclosure-back-top',
        'origin': (-98.5, 267., 290.075),
        'outward': (1., 0., 0.),
        'profile_up': (0., 0., -1.),
        'seat_depth': 2.2,
        'seat_height': 7.75,
        'span': 16.,
        'stock': 3.,
        'beak': .75,
        'centre_world_mm': (-97.4, 267., 278.),
        'target_centers': {
            'J5-GND': (-97.4, 267., 280.775),
            'J5-V5': (-97.4, 267., 278.925),
            'J5-IO2': (-97.4, 267., 277.075),
            'J5-IO19': (-97.4, 267., 275.225),
        },
        'stock_basis': 'Bare 4P 22 AWG ribbon, 1.70 mm modeled conductor OD on 1.85 mm pitch.',
        'fit_scope': 'Bare 4P fit accepted on the 16 mm coupon; installed routing and assembly access have their own scope.',
    }, {
        'id': 'vk-positive-east',
        'host': 'enclosure-back-top',
        'origin': (98.5, 274., 329.3),
        'outward': (-1., 0., 0.),
        'profile_up': (0., 0., -1.),
        'seat_depth': 2.2,
        'seat_height': 2.2,
        'span': 8.,
        'stock': 3.,
        'beak': .60,
        'centre_world_mm': (97.4, 274., 320.),
        'target_centers': {'J2-positive-K': (97.4, 274., 320.)},
        'stock_basis': 'One modeled 1.70 mm insulated 22 AWG silicone wire.',
        'fit_scope': 'Provisional compact seat, 1.60 mm mouth; soft-insulation entry is a physical fit observation.',
    })


def dress_guides(connection, guides, attachments, saved):
    """Dress retained cable groups without moving their terminals."""
    if saved.get('preserve_stations') and 'stations' in saved:
        return guides
    from .manifold_bank_routes import dress_manifold_bank_guides
    bank_guides = dress_manifold_bank_guides(connection, guides, attachments, saved)
    if bank_guides is not None:
        guides = bank_guides
    target = next((site['target_centers'][connection.id] for site in cable_sites()
                   if connection.id in site['target_centers']), None)
    if target is None:
        return guides
    x, _y, z = target
    if connection.id.startswith('J5-'):
        # The four leads share the west-wall hook and pass below V-A.
        start=attachments.terminals[connection.start].point
        end=attachments.terminals[connection.end].point
        return [(-88.5,start[1],z-4.),(x,256.5,z),
                (x,357.,z),(-72.,357.,z),(-72.,end[1],z),
                (-72.,end[1],end[2])]
    if connection.id == 'J2-positive-K':
        # Extend the existing horizontal leg toward the fore side of its
        # corner. The short hook ends before the owner's internal stock.
        corner = next((i for i, point in enumerate(guides)
                       if point[0] > 93. and 270. < point[1] < 280.
                       and abs(point[2]-z) < .01), None)
        if corner is None:
            return guides
        return [*guides[:corner], (x, 266.5, z), (x, 281.5, z), *guides[corner+1:]]
    # These are the existing source-side wall-lane stations, away from the
    # central paths and WAGO fanouts. The straight land includes both bends'
    # tangent room around the complete 16 mm hook span.
    lane = [i for i, point in enumerate(guides)
            if point[0] < -92. and 308. <= point[1] <= 335.
            and abs(point[2]-z) < .01]
    if not lane:
        return guides
    first, last = min(lane), max(lane)
    rejoin = (-80., guides[last][1], z)
    return [*guides[:first], (x, 331.5, z), (x, 305.5, z), rejoin, *guides[last+1:]]
