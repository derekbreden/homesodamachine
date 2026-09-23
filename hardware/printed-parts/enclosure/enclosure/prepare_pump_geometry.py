#!/usr/bin/env python3
"""Qualify the two Kamoer cartridge pieces for the complete enclosure print.

This consumes a successfully regenerated, explicitly identified Box. It does not
regenerate or qualify the complete enclosure or water pump.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys

HERE = Path(__file__).resolve().parent
ROOT = next(p for p in HERE.parents if (p / 'hardware/scripts').is_dir())
MANIFEST = HERE / 'pump-cartridge-generation.json'
BOX = ROOT / 'hardware/manifold-layout/enclosure-box.json'
MEASUREMENTS = ROOT / 'hardware/reference/kamoer-kphm400/scan-measurements.json'
INPUTS = (BOX, MEASUREMENTS,
          MEASUREMENTS.with_name('scan-evidence.json'),
          MEASUREMENTS.with_name('scan-registration.json'))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def relative(path):
    return str(Path(path).resolve().relative_to(ROOT))


def source_snapshot():
    names = subprocess.check_output(
        ['git', 'ls-files', '--cached', '--others', '--exclude-standard',
         '--', 'hardware', 'tools'], cwd=ROOT, text=True).splitlines()
    return {name: sha(ROOT / name) for name in names
            if name.endswith('.py') and (ROOT / name).is_file()}


def loaded_sources(before):
    paths = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        source = getattr(module, '__file__', None)
        if source and Path(source).suffix == '.py':
            path = Path(source).resolve()
            if path.is_relative_to(ROOT) and '/site-packages/' not in str(path):
                paths.add(path)
    output = {}
    for path in sorted(paths):
        name = relative(path)
        digest = sha(path)
        if before.get(name) != digest:
            raise ValueError(f'Loaded source changed during generation: {name}')
        output[name] = digest
    return output


def native_checks(enc, box, bounds):
    import cadquery as cq
    import trimesh
    import manifold_layout as ml

    rows = []

    def check(name, passed, **reading):
        rows.append({'check': name, 'pass': bool(passed), **reading})
        if not passed:
            raise ValueError(f'{name}: {reading}')

    def empty(name, a, b):
        volume = a.intersect(b).Volume()
        check(name, volume < 1e-5, interference_mm3=volume)

    needed = {'pump-cartridge-flush', 'pump-bay-cavity-throat', 'pump-bay-vertical-datums'}
    selected = [b for b in bounds if b.id in needed]
    check('all local Box bounds present and passing',
          len(selected) == len(needed) and all(b.ok for b in selected),
          readings=[b._asdict() for b in selected])

    pieces = {}
    for name in ('pump-cartridge', 'pump-cap'):
        path = HERE / f'enclosure-{name}.step'
        shape = cq.importers.importStep(str(path)).val()
        mesh = trimesh.load_mesh(path.with_suffix('.stl'))
        check(name + ' emitted STEP is one valid solid',
              shape.isValid() and len(shape.Solids()) == 1,
              volume_mm3=shape.Volume())
        check(name + ' emitted STL is one closed oriented volume',
              mesh.is_watertight and mesh.is_winding_consistent
              and mesh.body_count == 1 and mesh.volume > 0,
              facets=len(mesh.faces), volume_mm3=float(mesh.volume))
        pieces[name] = shape
    cradle, cap = pieces['pump-cartridge'], pieces['pump-cap']
    for dz in (-enc.cap_lift_clearance, 0., .25, 5., 35., 70.):
        empty(f'cap/cradle vertical path at {dz:g} mm lift',
              cap.translate((0, 0, dz)), cradle)

    trays, plate = box.pack.pump_trays, box.pack.collet_plate
    aft = enc.pump_cartridge_aft_y(trays,plate)
    nominal_aft = enc.bay_back_y(plate)-enc.cap_kiss
    retained_band = aft-max(cy+enc._tray.skirt_open_y_max for _,cy,_ in trays)
    actual_air = enc.bay_back_y(plate)-aft
    check('shared cap/cradle aft face preserves complete skirt band',
          retained_band >= enc._tray.skirt_upper_band-1e-9
          and actual_air >= enc.cap_kiss-enc.cap_kiss_station_allowance-1e-9,
          aft_y_mm=aft, retained_band_mm=retained_band, plate_air_mm=actual_air,
          adjustment_from_nominal_mm=aft-nominal_aft)
    # The unexported comparison suppresses only the conservative terminal-face bound.
    # It proves that this bounded correction cannot move the wells, seats or show face.
    saved_aft = enc.pump_cartridge_aft_y
    try:
        enc.pump_cartridge_aft_y = lambda _trays,_plate: enc.bay_back_y(_plate)-enc.cap_kiss
        nominal = {'pump-cartridge':enc.build_pump_cartridge(box).val(),
                   'pump-cap':enc.build_pump_cap(box).val()}
    finally:
        enc.pump_cartridge_aft_y = saved_aft
    for name,shape in pieces.items():
        b = shape.BoundingBox()
        terminal = enc._ybox(b.xmin-1,b.xmax+1,nominal_aft-.0001,aft+.0001,
                             b.zmin-1,b.zmax+1)
        added = shape.cut(nominal[name])
        removed = nominal[name].cut(shape)
        check(name+' bounded aft-face correction changes only terminal stock',
              added.cut(terminal).Volume()<1e-5 and removed.Volume()<1e-5,
              added_mm3=added.Volume(), removed_mm3=removed.Volume(),
              added_outside_terminal_mm3=added.cut(terminal).Volume(),
              terminal_y_mm=[nominal_aft,aft])
    measured = json.loads(MEASUREMENTS.read_text())
    land = enc.pump_skirt_support_z(trays)
    floor_bottom, floor_top = enc.bay_floor_z(trays)
    observed_front = measured['baseline_front_rim']['head_front_height_above_skirt_land_mm']['min']
    front_air = land + observed_front - floor_top
    declared_air = land - enc._tray.head_front_below_skirt - floor_top
    check('scan rigid front rim clears continuous floor', front_air >= enc.fits.running,
          minimum_observed_air_mm=front_air, floor_top_z_mm=floor_top)
    check('declared rigid front envelope clears floor', declared_air >= enc.fits.running,
          minimum_envelope_air_mm=declared_air)
    check('floor retains minimum stock', floor_top-floor_bottom >= 4.,
          stock_mm=floor_top-floor_bottom)
    check('emitted cradle beds on the corrected floor datum',
          abs(cradle.BoundingBox().zmin-floor_top) < 1e-6,
          native_bed_z_mm=cradle.BoundingBox().zmin)
    lands = [f for f in cradle.Faces() if f.geomType() == 'PLANE'
             and f.normalAt().z > .99999 and abs(f.Center().z-land) < 1e-5]
    check('emitted cradle retains both flat skirt bearing lands',
          all(any(abs(f.Center().x-cx) < 36 for f in lands) for cx, _, _ in trays)
          and sum(f.Area() for f in lands) > 1000,
          native_land_z_mm=land, native_area_mm2=sum(f.Area() for f in lands))
    base = enc.cap_base_z(trays)
    check('cap broad underside has no projections into the fitted pump seat',
          abs(cap.BoundingBox().zmin-base) < 1e-6,
          broad_base_z_mm=base, cap_lowest_z_mm=cap.BoundingBox().zmin)
    check('cap surrounding crown reaches the cartridge top',
          abs(cap.BoundingBox().zmax-cradle.BoundingBox().zmax)<1e-6,
          cap_top_z_mm=cap.BoundingBox().zmax,
          cartridge_top_z_mm=cradle.BoundingBox().zmax)
    terminal_rows = []
    for cx,cy,_ in trays:
        bottom = enc.cap_terminal_opening_z(box)
        room = enc._zcyl(enc.cap_terminal_opening_r-.001,
                         cx,cy+enc.clamp_pump_y_shift,bottom+.001,
                         cap.BoundingBox().zmax+1.)
        empty(f'X{cx:g} motor-terminal crown remains fully open',cap,room)
        terminal_rows.append({'center_xy_mm':[cx,cy+enc.clamp_pump_y_shift],
                              'diameter_mm':2*enc.cap_terminal_opening_r,
                              'bottom_z_mm':bottom})

    _, pilots = enc._cap_screws(box)
    tip = enc.cap_head_seat_z(box)-enc.cap_screw_len-enc.cap_lift_clearance
    tip_air = min(tip-p.BoundingBox().zmin for p in pilots)
    bridge_air = enc.cap_base_z(trays)-enc.cap_split_z(trays)-enc.cap_lift_clearance
    raised_tip = enc.cap_head_seat_z(box)+enc.cap_lift_clearance-enc.cap_screw_len
    check('cap lift allowance preserves screw and bridge clearances',
          tip_air >= .25-1e-6 and bridge_air > 0
          and raised_tip <= enc.cap_split_z(trays)-enc.cap_heatset_len+1e-6,
          tip_air_mm=tip_air, bridge_air_mm=bridge_air,
          full_insert_engagement_mm=enc.cap_heatset_len)

    floor = enc._bay_floor(box.inner,box.y_joint,plate,trays)
    wall = enc._tee_wall(box.inner,box.y_joint,plate,box.pump_bay)
    for cx, cy, cz in trays:
        above = enc._ybox(cx-32,cx+32,enc.front_plane_y,cy+33,
                         floor_top+.001,floor_top+2.)
        below = enc._ybox(cx-32,cx+32,enc.front_plane_y,cy+33,
                         floor_top-.1,floor_top-.001)
        empty(f'X{cx:g} head sliding floor has no raised lip',floor,above)
        check(f'X{cx:g} head sliding floor is continuous',below.cut(floor).Volume()<1e-5)
        outlet_z = cz-enc._interface.pump_seated_drop+enc._tray.outlet_axis_z
        for sx in (-1.,1.):
            x = cx+sx*enc._tray.outlet_pitch/2
            # The tube runs on its collet-plate passage's axis, from the seated pump's tube plane.
            hole_z = next(hz for hx, hz in plate['holes'] if abs(hx-x)<1e-6)
            datum = (x, plate['aft_y']-ml.PUMP_BARBS_TO_RELEASE_PLANE, hole_z)
            check(f'X{x:g} seated casing axis matches its collet plate passage',
                  abs(outlet_z-datum[2])<1e-6, seated_outlet_z_mm=outlet_z, passage_z_mm=datum[2])
            tube = enc._ycyl(3.175,x,outlet_z,datum[1],plate['seated_tube_bottom_y'])
            empty(f'X{x:g} quarter-inch tube clears emitted cradle',tube,cradle)
            empty(f'X{x:g} quarter-inch tube clears fixed plate passage',tube,wall)
    for dy in (0.,-plate['connected_release_travel'],-20.,-80.):
        empty(f'cradle/plate at {dy:g} mm cartridge withdrawal',
              cradle.translate((0,dy,0)),wall)
        empty(f'cap/plate at {dy:g} mm cartridge withdrawal',
              cap.translate((0,dy,0)),wall)
    return {'checks': rows, 'checks_pass': all(r['pass'] for r in rows),
            'pump_trays': trays, 'collet_plate': plate,
            'open_terminal_wells': terminal_rows, 'skirt_land_z_mm': land,
            'support_features': {
                'pull_y_mm': enc.pull_y_span(trays,plate),
                'pull_z_mm': enc.pull_z_span(box),
                'pull_outer_abs_x_mm': enc._cap_x_span(box.pump_bay)[1],
                'pull_inner_abs_x_mm': enc._cap_x_span(box.pump_bay)[1]-enc.pull_depth,
                'cap_screw_y_mm': enc.cap_screw_ys(box.inner,plate),
                'cap_head_seat_z_mm': enc.cap_head_seat_z(box),
                'cap_counterbore_radius_mm': enc.head_cbore_dia/2,
                'cap_crown_z_mm': enc.cap_crown_z(box)},
            'floor_z_mm': [floor_bottom,floor_top],
            'unqualified_tee_datums': ml.tee.UNQUALIFIED_DATUMS,
            'scope': 'Fresh emitted cartridge/cap, current local Box, independent scan rim readings, and local tube/plate passages. No complete enclosure or physical fit qualification.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--box-sha256', required=True,
                        help='Exact Box digest supplied by its completed producer checks')
    parser.add_argument('--existing-exports', action='store_true',
                        help='Check the completed enclosure producer outputs without rewriting them')
    args = parser.parse_args()
    if sha(BOX) != args.box_sha256:
        raise ValueError('Box is not the qualified producer output named on this command')
    before_sources = source_snapshot()
    before_inputs = {relative(p): sha(p) for p in INPUTS}
    MANIFEST.unlink(missing_ok=True)
    sys.path.insert(0,str(ROOT/'hardware/scripts'))
    sys.path.insert(0,str(HERE))
    sys.path.insert(0,str(ROOT/'hardware/manifold-layout'))
    import materialize_pump_cartridge as producer
    import _box_spec
    import enclosure as enc
    if args.existing_exports:
        result = {
            name: {'hashes': {
                f'enclosure-{name}{suffix}': sha(HERE / f'enclosure-{name}{suffix}')
                for suffix in ('.step', '.stl', '.step.mesh')}}
            for name in ('pump-cartridge', 'pump-cap')}
    else:
        result = producer.materialize()
    box,bounds = _box_spec.read(enc.Box,enc.Bound,(enc.Pack,enc.PortField,enc.Nameplate),path=BOX)
    native = native_checks(enc,box,bounds)
    after_inputs = {relative(p): sha(p) for p in INPUTS}
    if before_inputs != after_inputs:
        raise ValueError('Box or scan evidence changed during generation')
    sources = loaded_sources(before_sources)
    artifacts = {relative(HERE/name): digest for part in result.values()
                 for name,digest in part['hashes'].items()}
    if any(sha(ROOT / name) != digest for name, digest in artifacts.items()):
        raise ValueError('A cartridge output changed during its native checks')
    record = {'schema': 1, 'status': 'current_cartridge_only_native_checks_passed',
              'created_at_utc': datetime.now(timezone.utc).isoformat(),
              'assembly_current': False, 'production_enclosure_released': False,
              'physical_fit_tested': False, 'command': sys.argv,
              'existing_exports_checked': args.existing_exports,
              'source_sha256': sources, 'input_sha256': after_inputs,
              'artifact_sha256': artifacts, 'materializer_results': result,
              'native': native,
              'remaining': ['Current native slice and support removal review.',
                            'Assembled enclosure fit, terminal connectors and support cleanup; existing cap retention is recorded in physical-fit.json.',
                            'Complete carrier/collet dry cycle in the assembled enclosure.',
                            'Full enclosure regeneration and qualification are separate.']}
    MANIFEST.write_text(json.dumps(record,indent=2)+'\n')
    print(f'PASS cartridge only: {len(native["checks"])} native readings; '
          f'{len(sources)} frozen loaded sources; assembly_current=false',flush=True)


if __name__ == '__main__':
    main()
