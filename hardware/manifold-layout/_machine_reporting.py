"""Scalar wiring context and reports from the machine's Rust reference plan."""
from __future__ import annotations

import hashlib
import importlib
import json
from pathlib import Path
import sys
import time
from types import SimpleNamespace


ROOT = Path(__file__).resolve().parents[2]
HW = ROOT / 'hardware'
LAYOUT = HW / 'manifold-layout'
_ANCHOR_SITES = (
    ('carb-1', 1, (0., 0., 1.), 'enclosure-back-top'),
    ('co2-2', 1, (0., 0., 1.), 'enclosure-back-top'),
    ('fluid-28', 2, (-1., 0., 0.), 'enclosure-back-top'),
)


def _paths():
    for path in (ROOT, HW / 'scripts', LAYOUT, HW / 'cold-core-layout',
                 HW / 'printed-parts/cold-core', HW / 'printed-parts/cold-core/foam-assembly',
                 HW / 'printed-parts/enclosure/enclosure',
                 HW / 'printed-parts/enclosure/bulkhead-ring',
                 HW / 'printed-parts/enclosure/pump-tray',
                 HW / 'printed-parts/electronics/pcba-tray',
                 HW / 'reference/digiten-flow-sensor',
                 HW / 'reference/sf76e-thermal-fuse', HW / 'reference/jg-bulkhead-union'):
        if str(path) not in sys.path:
            sys.path.insert(0, str(path))


def plain(value):
    """Source named records and JSON containers, without a geometry-object protocol."""
    if hasattr(value, '_asdict'):
        return {key: plain(row) for key, row in value._asdict().items()}
    if isinstance(value, dict):
        if '__hsm_namedtuple__' in value:
            return {key: plain(row) for key, row in zip(value['fields'], value['values'], strict=True)}
        if '__hsm_dict__' in value:
            return {str(key): plain(row) for key, row in value['__hsm_dict__']}
        if '__hsm_list__' in value:
            return [plain(row) for row in value['__hsm_list__']]
        return {str(key): plain(row) for key, row in value.items()}
    if isinstance(value, (tuple, list, set, frozenset)):
        return [plain(row) for row in value]
    if isinstance(value, Path):
        return str(value)
    return value


def scalar_namespace(spec=None):
    """The numeric installed-wiring providers, independent of the CAD assembly driver."""
    _paths()
    import _enclosure_datums
    enc = _enclosure_datums.load()
    import _cold_core_interface as cci
    import foam_assembly as foam
    import _carbonator as carbonator
    import pcba_tray as pcba
    import sf76e_thermal_fuse as fuse
    import digiten_flow_sensor as digiten

    x, y, z = (1., 0., 0.), (0., 1., 0.), (0., 0., 1.)
    relay = ((z, 270.), (y, 270.))
    wagos = {size: HW / f'reference/wago-221/wago-221-{size}.step'
             for size in ('413', '415', '420')}
    values = dict(
        _enc=enc, _cci=cci, _foam=foam, _pcba=pcba, _fuse=fuse, _digiten=digiten,
        _cca=SimpleNamespace(_V=SimpleNamespace(
            _bond=carbonator._bond, top_plate_z=carbonator.top_plate_z)),
        ml=SimpleNamespace(VALVE_STEP=HW / 'reference/beduan-solenoid/beduan-solenoid.step'),
        PCBA_STEP=HW / 'printed-parts/electronics/pcba-tray/pcba-board.step',
        PSU_STEP=HW / 'reference/meanwell-irm90/meanwell-irm90.step',
        RELAY_STEP=HW / 'reference/teyleten-relay/teyleten-relay.step',
        MQ6_STEP=HW / 'reference/mq6-gas-sensor/mq6-gas-sensor.step',
        DIGITEN_STEP=HW / 'reference/digiten-flow-sensor/digiten-flow-sensor.step',
        C14_STEP=HW / 'reference/iec-c14-inlet/iec-c14-inlet.step',
        PCBA_TURN=((y, -90.), (x, -90.)), PSU_TURN=((y, -90.),),
        RELAY_TURN=relay, RELAY2_TURN=relay + ((x, 90.),),
        WAGO_TURN=((x, 90.), (y, -90.)), WAGO_TURN_WEST=((x, 90.), (y, 90.)),
        FUSE_TURN=((x, 90.), (z, 90.)), MQ6_TURN=((x, -90.), (z, 90.)),
        DIGITEN_TURN=((z, 90.), (y, 90.)),
        DISPLAY_TILT=(x, enc.display_facet_angle_deg - 90.),
        wago_step=wagos.__getitem__, WAGO_POLES=('wago-v12', 'wago-gnd', 'wago-g', 'wago-h', 'wago-n'),
        CRADLE_TOL=.01, PORT_NUT_GAP=7., FLOOR_GROMMET_SQUEEZE=.4,
        DIGITEN_COLLET_FREE=digiten.port_face - digiten.port_collar_end,
    )
    values.update((spec or {}).get('metadata', {}).get('wiring_context', {}))
    return SimpleNamespace(**values)



def _request(op, **values):
    _paths()
    from _rust_data import request
    def wire(value):
        if hasattr(value, '_asdict'):
            return {key: wire(row) for key, row in value._asdict().items()}
        if isinstance(value, dict):
            return {str(key): wire(row) for key, row in value.items()}
        if isinstance(value, (tuple, list, set, frozenset)):
            return [wire(row) for row in value]
        return str(value) if isinstance(value, Path) else value
    values = wire(values)
    metadata = values.get('metadata')
    if 'spec' in values:
        metadata = values['spec'].get('metadata')
    if metadata is not None:
        specs = metadata.get('native_route_specs', metadata.get('routes', {}))
        metadata.setdefault('native_route_order', list(specs))
        groups = metadata.get('native_connections', {})
        metadata.setdefault('connection_order', metadata.get('native_connection_order', list(groups)))
    return request('machine-data', 'machine-data', {'op': op, **values})


def _bounds(spec):
    return _request('report_bounds', spec=spec)


def _ports(frame):
    return _request('report_ports', frame=frame)


def _route_rows(metadata):
    return tuple(_request('report_routes', metadata=metadata))


def _run_length(row):
    return _request('report_run_length', row=row)


def route_metadata(spec, checked):
    """The route handoff computed in Rust from live ports and local anchor stations."""
    metadata = spec['metadata']
    if 'route_metadata' in metadata:
        return _request('report_route_metadata', spec=spec, checked=checked)
    ea = scalar_namespace(spec)
    import _routing
    specs = metadata.get('native_route_specs', metadata.get('routes', {}))
    spools = {}
    for run in metadata['runs']:
        name = run['id']
        spool = (_routing.SPOOLS[specs[name]['spool']] if name in specs and specs[name].get('spool')
                 else _routing.spool_of(name))
        spools[name] = {key: plain(getattr(spool, key)) for key in
                       ('name', 'rgb', 'alpha', 'roughness', 'metalness', 'names')}
    # Providers retain their local coordinate APIs; Rust applies the installed carry.
    cap = {name: [*ea._foam.cap_anchor_station(name),
                   ea._foam.cap_face_z + ea._cci.cap_anchor_axis_over_face(name)]
           for name in ea._cci.cap_anchors}
    side = {name: [*ea._foam.cap_side_anchor_station(name), ea._foam.cap_face_z + row.over_face]
            for name, row in ea._cci.cap_side_anchors.items()}
    port_order = {name: list(ports) for name, ports in metadata.get('world_ports', {}).items()}
    port_order.update({name: list(frame.get('ports', {})) for name, frame in metadata['frames'].items()})
    return _request('report_route_metadata', spec=spec, checked=checked,
                    cap_local_points=cap, cap_side_local_points=side, spools=spools,
                    anchor_sites=_ANCHOR_SITES, port_order=port_order)


def scene_document(spec, checked, *, taken=None):
    """The schema-one scene document assembled by Rust from completed readings."""
    _paths()
    import _machine
    import _routing
    return _request('report_scene', spec=spec, checked=checked,
                    taken=time.time() if taken is None else taken,
                    sources=_machine.stamps(), run_fields=list(_routing.Run.__dataclass_fields__))


def _tray_inputs(ea):
    import above_core
    return dict(excluded_valves=[*above_core.valve_names(), *ea._cci.cap_cradles,
                                 *above_core.core_equipment_names()],
                interior_x=ea._enc.interior_x(), rear_axis_y_shift=ea._enc._tray.rear_axis_y_shift,
                pump_seated_drop=ea._enc._interface.pump_seated_drop,
                pump_relief_floor=ea._enc.pump_relief_floor)


def _tray_reports(bounds, ea):
    return tuple(_request('report_trays', bounds=bounds, **_tray_inputs(ea)))


def gather(spec, checked, physical_model, *, scene_path=None, step_path=None, scorecard_path=None):
    """Schema-two facts calculated by Rust from completed plan and scalar source providers."""
    _paths()
    import _facts
    import _realized
    import above_core
    import bulkhead_ring
    import jg_bulkhead_union
    ea = scalar_namespace(spec)
    metadata = spec['metadata']
    physical_model = Path(physical_model)
    step_path = Path(step_path) if step_path is not None else Path(str(physical_model).removesuffix('.npz'))
    scene_path = Path(scene_path) if scene_path is not None else step_path.with_suffix('.scene.npz')
    scorecard_path = Path(scorecard_path) if scorecard_path is not None else step_path.with_suffix('.scorecard.json')
    def artifact(path):
        from _cadq_export import note_read
        note_read(path)
        with path.open('rb') as source:
            digest = hashlib.file_digest(source, 'sha256').hexdigest()
        return {'path': str(path.relative_to(ROOT)), 'sha256': digest}
    with step_path.open('rb') as source:
        step_digest = hashlib.file_digest(source, lambda: hashlib.blake2b(digest_size=16)).hexdigest()
    constants = {'C14_STATION': [above_core.pose('c14-inlet')['translation_mm'][i] for i in (0, 2)],
                 'DIGITEN_COLLET_FREE': ea.DIGITEN_COLLET_FREE,
                 'FLOOR_GROMMET_SQUEEZE': ea.FLOOR_GROMMET_SQUEEZE,
                 'KEYSTONE_CLEARANCES': metadata.get('keystone_clearances', ()),
                 'KEYSTONE_STATION': metadata['keystone_station'],
                 'CRADLE_TOL': ea.CRADLE_TOL, 'PORT_NUT_GAP': ea.PORT_NUT_GAP, 'WAGO_POLES': ea.WAGO_POLES,
                 **{name: getattr(ea._enc, name) for name in ('appliance_width', 'side_band_inset', 'wall')}}
    standalone = metadata.get('standalone_names', (
        'compressor', 'condenser+fan', 'foam-assembly', 'g-ganen-pump', 'funnel',
        'discharge-chain', 'display', 'display-cover', 'display-gasket', 'psu', 'pcba',
        'relay-1', 'relay-2', 'asse1022-assembly', 'bulkhead-drain', 'asse-drain-adapter',
        'mq6-sensor', 'thermal-fuse', 'fuse-clamp', *ea.WAGO_POLES,
        'wago-mana', 'wago-manb', 'wago-reeds-b', 'wago-sensors', 'water-split',
        'flow-regulator', 'vk-solenoid', 'bulkhead-water', 'c14-inlet', 'co2-inlet',
        'gasher-co2', 'wr1110', 'nameplate', 'nameplate-ink', 'bulkhead-flavor-a',
        'bulkhead-flavor-b', 'bulkhead-carb', 'digiten-flow'))
    return _request('report_facts', spec=spec, checked=checked, tray_inputs=_tray_inputs(ea),
        box_fact_order=_facts._BOX_FACT_ORDER, card_port_bodies=_facts.CARD_PORT_BODIES,
        wet_ports=above_core.specification()['rear_wall']['wet_ports'], constants=constants,
        union_panel_footprint=jg_bulkhead_union.panel_footprint()[0],
        bulkhead_ring_union_od=bulkhead_ring.od('union'), fit_slip=importlib.import_module('fits').slip,
        union_body_d=jg_bulkhead_union.BODY_D, digiten_wire_exit=ea._digiten.wire_exit(),
        standalone_names=standalone, funnel_collar=[ea._enc._funnel.collar_w, ea._enc._funnel.collar_d],
        foam_cap_face_z=ea._foam.cap_face_z, card_digest=_realized.code_digest(scorecard_path),
        step_digest=step_digest, source_digest=_facts.source_digest(), routing=route_metadata(spec, checked),
        artifacts={'step': artifact(step_path), 'fine_model': artifact(physical_model), 'scene': artifact(scene_path)})


def write(spec, checked, physical_model, **paths):
    """Write the Rust-composed facts beside the completed model/card/scene outputs."""
    target = Path(paths.pop('facts_path', LAYOUT / 'enclosure-assembly.facts.json'))
    value = gather(spec, checked, physical_model, **paths)
    from _cadq_export import _atomic_write
    _atomic_write(target, lambda path: Path(path).write_text(json.dumps(value, indent=1, sort_keys=True)+'\n'))
    return target
