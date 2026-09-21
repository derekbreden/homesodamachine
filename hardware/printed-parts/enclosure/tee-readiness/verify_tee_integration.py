#!/usr/bin/env python3
"""Native checks of the measured tee radial correction and its coupled interfaces.

Builds the small tee/valve/carrier region, not the complete appliance. Its positive
result establishes those checks only; unresolved sleeve datums and the complete
printed enclosure still require qualification before a production print.
"""
from __future__ import annotations
import dataclasses
import hashlib
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
sys.path.insert(0, str(ROOT / 'hardware/manifold-layout'))
import enclosure_assembly as ea
import cadquery as cq

ml, enc, carrier, tee = ea.ml, ea._enc, ea._carrier, ea.ml.tee
INPUTS = (
    'hardware/printed-parts/enclosure/tee-readiness/verify_tee_integration.py',
    'hardware/reference/tee-connector/tee_connector.py',
    'hardware/reference/tee-connector/tee-connector.step',
    'hardware/reference/jg-pp0208e-tee/scan-registration.json',
    'hardware/reference/jg-pp0208e-tee/branch-operating-measurements.json',
    'hardware/reference/kamoer-kphm400/kamoer_kphm400.py',
    'hardware/reference/kamoer-kphm400/kamoer-kphm400.step',
    'hardware/reference/water-split/water_split.py',
    'hardware/manifold-layout/manifold_layout.py',
    'hardware/manifold-layout/enclosure_assembly.py',
    'hardware/printed-parts/enclosure/enclosure/_enclosure_interface.py',
    'hardware/printed-parts/enclosure/enclosure/enclosure.py',
    'hardware/printed-parts/enclosure/tee-carrier/tee_carrier.py',
    'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-left.step',
    'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-right.step',
)


def hashes():
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INPUTS}


def small_placed_region():
    """The production transforms, with one copy of each native valve constituent.

    Reusing that one body avoids regenerating the identical Beduan sixteen times.
    Tube-datum and moving tee geometry use the production builders directly.
    """
    v = ml.vlv
    body = v.build_body().union(v.build_port()).val()
    coil = cq.Compound.makeCompound([v.build_coil().val()] + [s.val() for s in v.build_spades()])
    shapes = []
    for name, p in ml.P.items():
        if name in ml.CARRIER_TEES:
            shapes.append((ml.body_name(name), ml.carrier_tee(name, ml.CARRIER_SQUEEZE), None))
            continue
        if not name.startswith('V-'):
            continue
        xdir, zdir = ml.valve_dirs(p['arg'])
        for kind, source in (('valve', body), ('coil', coil)):
            solid = ml.place(source, (p['x'], p['y'], ml.DECK_Z-ml.VALVE_PORT_Z), xdir, zdir)
            if p['fold']:
                solid = ml.folded(solid)
            if name in ml.BENT:
                solid = ml.bent(solid, ml.BENT[name])
            if name in ml.SHIFT:
                solid = solid.translate(ml.SHIFT[name])
            shapes.append((f'{kind}-{name.lower()}', solid, None))
    outer_loops = [ea.pose_manifold(ml.uturn(ml.SPINE[cid], ml.CARRIER_RELEASE)) for cid in (17,27)]
    lift = (ea.PACK_CROWN + enc._interface.manifold_rise - ml.CARRIER_DROP
            - min(ea.box(s).zmin for s in outer_loops))
    for name, px in ml.PUMPS.items():
        for label, shape in zip(('head','boss','motor'), ml.build_pump(px)):
            shapes.append((f'{name}-{label}', shape, None))
    stood = [(n,ea.pose_manifold(s).translate((0,ea.PACK_Y,lift)),c) for n,s,c in shapes]
    return lift, ea.manifold_carry(lift), stood


def main():
    before = hashes()
    rows = []
    def check(name, value, limit=1e-5):
        passed = value <= limit
        rows.append({'check':name,'value':float(value),'maximum':float(limit),'pass':passed})
        if not passed:
            raise ValueError(f'{name}: {value:g} exceeds {limit:g}')
    tee.stations_hold()
    ea._split.stations_hold()
    measured = json.loads((ROOT/'hardware/reference/jg-pp0208e-tee/scan-registration.json').read_text())
    for patch in measured['patches']:
        lo, hi = patch['axial_band_mm']
        outside = (patch['diameter_at_mid_station_mm']/2
                   + max(abs(lo-patch['mid_station_mm']), abs(hi-patch['mid_station_mm']))
                   * abs(patch['radius_taper_per_axial_mm']))
        envelope = tee.BARREL_R if 'collar' in patch['name'] else tee.ARM_R
        check(patch['name']+' fitted draft exceeds reference envelope', max(0,outside-envelope))
    check('measured 42.5 run span',abs(tee.RUN_SPAN-42.5),1e-8)
    check('measured 39.2 pressed run span',abs(2*(tee.RUN_HALF-tee.RUN_COLLET_TRAVEL)-39.2),1e-8)
    check('measured branch extended caliper width',
          abs(tee.BRANCH_REACH+tee.COLLAR_NOMINAL_D/2-30.5),1e-8)
    check('measured branch pressed caliper width',
          abs(tee.BRANCH_PRESSED_REACH+tee.COLLAR_NOMINAL_D/2-29.0),1e-8)
    check('branch carrier seating travel',abs(tee.CARRIER_STROKE-2.0),1e-8)
    lift, carry, stood = small_placed_region()
    solids = {n:s for n,s,c in stood}
    trays = ea.pump_tray_stations(solids)
    plate = ea.collet_plate_spec(carry,trays)
    spec = ea.tee_carrier_spec(carry,stood,plate)
    mismatch = carrier.placement_mismatches(spec)
    if mismatch:
        raise ValueError(f'printed/derived carrier mismatch: {mismatch}')
    interface = ea.tee_carrier_interface(spec,plate,stood)
    check('journal below measured sample envelope plus running air',
          max(0,8.25+spec.slide_air-plate['bore_r']))
    axes = {}
    for name in ml.BARB_OF:
        pump = carry((ml.barb_station(name),(0,0,1)))[0]
        nose = carry(ml.carrier_collet_port(name,ml.CARRIER_SQUEEZE))[0]
        axes[name]={'pump':pump,'tee_release':nose}
        check(name+' cartridge tube X alignment',abs(pump[0]-nose[0]),1e-6)
        check(name+' cartridge tube Z alignment',abs(pump[2]-nose[2]),1e-6)
    halves = {side:cq.importers.importStep(str(ROOT/f'hardware/printed-parts/enclosure/tee-carrier/enclosure-tee-carrier-{label}.step')).val()
              for side,label in ((-1,'left'),(1,'right'))}
    inner = (*enc.interior_x(),enc.front_plane_y,enc.rear_plane_y)
    wall = enc._tee_wall(inner,0,plate,(0,0,plate['z1']))
    wall = wall.fuse(enc._tee_carrier_fixed_features(inner,plate,interface))
    for cut in enc._tee_carrier_service_slots(interface):
        wall = wall.cut(cut)
    # Circular openings preserve the complete annulus. R5.0 is an explicit
    # geometric probe, not a caliper-qualified minimum terminal-ring radius.
    for x,z in plate['holes']:
        annulus = enc._ycyl(5.0,x,z,plate['aft_y']-.10,plate['aft_y']-.01).cut(
            enc._ycyl(plate['hole_d']/2+.01,x,z,plate['aft_y']-.11,plate['aft_y']))
        check(f'X{x:g} circular release face R4.26..5.0 annulus missing stock',
              annulus.cut(wall).Volume())
        tube = enc._ycyl(tee.TUBE_D/2,x,z,plate['fore_y']-.1,plate['aft_y']+.1)
        check(f'X{x:g} circular plate tube clearance',tube.intersect(wall).Volume())
    tee_solids = {name:solids[ml.body_name(name)] for name in ml.CARRIER_TEES}
    for state,row in plate['carrier_states'].items():
        dy = row['offset_y']
        for name in sorted(ml.CARRIER_TEES):
            shape = ea.pose_manifold(ml.carrier_tee(name,dy)).translate((0,ea.PACK_Y,lift))
            check(f'{state} {name} / native tee wall',shape.intersect(wall).Volume())
            for side,half in halves.items():
                check(f'{state} {name} / carrier {side:+d}',shape.intersect(half.translate((0,dy,0))).Volume())
        for side,half in halves.items():
            check(f'{state} carrier {side:+d} / local fixed guide body',half.translate((0,dy,0)).intersect(wall).Volume())
        for index, head in enumerate(carrier.tie_head_envelopes(spec), 1):
            moved = head.translate((0,dy,0))
            check(f'{state} tie {index} lock / local fixed guide body',moved.intersect(wall).Volume())
            for name,shape in solids.items():
                if name.startswith(('valve-','coil-')):
                    check(f'{state} tie {index} lock / {name}',moved.intersect(shape).Volume())
    # Native positive stock read from the files a printer will receive.
    for side,half in halves.items():
        for x in spec.tee_xs:
            if (x>0)!=(side>0):
                continue
            backing=carrier._box(x-spec.trough_r+.01,x+spec.trough_r-.01,
                spec.stub_relief_y+.01,spec.web_aft_y-.01,
                spec.trough_top_z+.01,spec.web_z[1]-.01).val()
            check(f'X{x:g} retained upper backing missing native stock',backing.cut(half).Volume())
    entry = interface['aft_valve_entry_y']
    for valve in 'cdgj':
        for kind in ('valve','coil'):
            shape=solids[f'{kind}-v-{valve}'].translate((0,entry,0))
            for side,half in halves.items():
                check(f'{kind}-v-{valve} full post entry / carrier {side:+d}',shape.intersect(half).Volume())
    after=hashes()
    if after!=before:
        raise ValueError('inputs changed during native verification; rerun against one source state')
    report={
        'scope':'native measured tee/valve/carrier region; full printed enclosure requires its separate complete motion/support checks',
        'checks_pass':all(r['pass'] for r in rows),'print_release':False,
        'unqualified_tee_datums':tee.UNQUALIFIED_DATUMS,
        'inputs_sha256':after,'checks':rows,
        'dimensions':{'collar_nominal_diameter':tee.COLLAR_NOMINAL_D,
            'collar_sample_envelope_diameter':tee.COLLAR_ENVELOPE_D,
            'branch_extended_caliper_width':tee.BRANCH_WIDTH_EXTENDED,
            'branch_pressed_caliper_width':tee.BRANCH_WIDTH_PRESSED,
            'branch_extended_face':tee.BRANCH_REACH,
            'branch_pressed_face':tee.BRANCH_PRESSED_REACH,
            'run_collet_travel':tee.RUN_COLLET_TRAVEL,
            'branch_collet_travel':tee.BRANCH_COLLET_TRAVEL,
            'carrier_seating_travel':tee.CARRIER_STROKE,
            'pump_to_release_span':ml.PUMP_BARBS_TO_RELEASE_PLANE,
            'journal_diameter':2*plate['bore_r'],'trough_radius':spec.trough_r,
            'retained_upper_backing':spec.web_aft_y-spec.stub_relief_y,
            'aft_deck_separation':ml.DECK_SEP,
            'full_valve_post_entry_air':spec.aft_coil_fore_y+entry-spec.web_aft_y,
            'carrier_drop':ml.CARRIER_DROP,'manifold_lift':lift,
            'pump_tube_projection':ml.PUMP_TUBE_PROJECTION},
        'pump_trays':trays,'pump_to_tee_axes':axes,
        'carrier_spec':dataclasses.asdict(spec),'collet_plate':plate,'carrier_interface':interface,
        'remaining_release_checks':[
            'Terminal-ring OD, fixed/moving seam and physical release-ring bearing qualification; nominal branch face stations are caliper-derived.',
            'Spring ID and positive capture design/physical qualification.',
            'Complete regenerated enclosure interference and insertion checks, current support-removal audit and exact slice identity.'],
    }
    (HERE/'tee-integration.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({'checks_pass':report['checks_pass'],'count':len(rows),'dimensions':report['dimensions'],
                      'spring_stations':carrier.spring_stations(spec),'print_release':False},indent=2))


if __name__=='__main__':
    main()
