"""Normal enclosure construction from scalar recipes and ordered fine-model references."""
from __future__ import annotations

from contextlib import contextmanager
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def load():
    from _enclosure_datums import load as scalar_source
    return scalar_source()


def box_from_document(document):
    """Decode the existing schema5 description without a CAD geometry object."""
    shell = load()
    import _box_spec
    types = {kind.__name__: kind for kind in (shell.Pack, shell.PortField, shell.Nameplate)}
    box = shell.Box(*(_box_spec._tupled(document['box'][name], types)
                      for name in shell.Box._fields))
    bounds = [shell.Bound(*(_box_spec._tupled(row[name], types)
                            for name in shell.Bound._fields))
              for row in document.get('bounds', ())]
    return shell, box, bounds


def _model_instance(model, name=None, *, transform=None, indices=None, color=None):
    row = {'model': str(Path(model).resolve())}
    if name is not None:
        row['name'] = name
    if transform is not None:
        row['transform'] = transform
    if indices is not None:
        row['indices'] = indices
    if color is not None:
        row['color'] = list(color)
    return row


def _translation(point):
    x, y, z = point
    return ((1.,0.,0.,x), (0.,1.,0.,y), (0.,0.,1.,z))


def cut_pieces(shell, box, directory=HERE):
    """Cut every printable quadrant and both retainer poses on the Rust kernel."""
    import _enclosure_panel
    import _enclosure_back_top
    import _enclosure_front_top
    import _enclosure_front_bottom
    import _enclosure_pump_retainer

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for module in (_enclosure_panel, _enclosure_back_top,
                   _enclosure_front_top, _enclosure_front_bottom):
        module.cut(shell, box, directory)
    names = [name for name in shell.PIECE_COLORS if name != 'pump-retainer']
    installed = None
    if box.pump_bay and box.pack.collet_plate:
        _enclosure_pump_retainer.cut(shell, box, directory)
        _enclosure_pump_retainer.cut(shell, box, directory, seated=True)
        names.append('pump-retainer')
        installed = directory/'enclosure-pump-retainer-seated.step.npz'
    return {name: directory/f'enclosure-{name}.step.npz' for name in names}, installed


@contextmanager
def _dock_recipe(shell, graph):
    dock = shell._dock
    originals = dock.box, dock.ycyl
    dock.box = graph.box
    dock.ycyl = lambda r, x, z, y0, y1: graph.cylinder(1, r, x, z, y0, y1)
    try:
        yield
    finally:
        dock.box, dock.ycyl = originals


def cut_tube_setting_jig(shell, box, directory=HERE):
    import _rust_part
    import trimesh
    from _materials import linear, M_PETGF_BLACK
    from _enclosure_panel import _Graph
    from _enclosure_presentation import print_payload

    graph = _Graph()
    with _dock_recipe(shell, graph):
        solid = shell._dock.tube_setting_jig(box.pack.collet_plate,
            shell.pump_cartridge_aft_y(box.pack.pump_trays, box.pack.collet_plate))
    directory = Path(directory)
    numbers = dict(panel=graph.document(solid),
                   color=[round(c, 9) for c in linear(M_PETGF_BLACK)])
    _rust_part.cut('enclosure-shell', 'enclosure-dock', numbers, directory)
    step = directory/'enclosure-pump-tube-setting-jig.step'
    print_payload(step, trimesh.load_mesh(step.with_suffix('.stl')))


def installed_instances(box_document, directory=None):
    """Installed shell-owned models and the shared fastening datums for the machine plan."""
    shell, box, _bounds = box_from_document(box_document)
    import _rust_part
    from _materials import linear, M_PETGF_BLACK
    directory = Path(directory) if directory is not None else HERE/'installed'
    directory.mkdir(parents=True, exist_ok=True)
    instances = []
    if box.pump_bay and box.pack.collet_plate:
        instances.append(_model_instance(HERE/'enclosure-pump-retainer-seated.step.npz',
                                         'enclosure-pump-retainer'))
    frame = shell._funnel_frame_part
    centre = ((box.inner[0]+box.inner[1])/2., frame.center_y)
    seat = shell.funnel_seat_z(box.outer)
    floor = frame.datums(seat)[0]
    _rust_part.cut('funnel', 'funnel-frame',
                   frame.numbers(box.inner, box.y_joint, centre, seat), directory,
                   numbers_name='enclosure-funnel-frame')
    instances.append(_model_instance(directory/'funnel-frame.step.npz', 'funnel-frame',
        transform=_translation((*centre, floor)), color=linear(M_PETGF_BLACK)))
    identification = shell._above_core_shell.rear_identification()
    _rust_part.cut('enclosure-components', 'rear-identification',
                   identification.numbers(), directory)
    for station in identification.stations():
        which = station['which']
        model = directory/f'rear-label-{which}.step.npz'
        transform = _translation((station['center_x_mm'], station['floor_y_mm'],
                                  station['center_z_mm']))
        for index, suffix in enumerate(('', '-word')):
            instances.append(_model_instance(model, f'bulkhead-ring-{which}{suffix}',
                                              indices=[index], transform=transform))
    plate = identification.nameplate
    _rust_part.cut('enclosure-components', 'nameplate', plate.numbers(1), directory,
                   numbers_name='enclosure-nameplate')
    plan = identification.nameplate_plan()
    transform = _translation((plan['center_x_mm'], plan['face_y_mm']-plate.THICK,
                              plan['center_z_mm']))
    for index, name in enumerate(('nameplate', 'nameplate-ink')):
        colour = (identification.colours.word_color('flavor') if index
                  else identification.colours.chip_color('flavor'))
        instances.append(_model_instance(directory/'nameplate-001.step.npz', name,
                                          indices=[index], transform=transform,
                                          color=linear(identification._colour(colour))))
    return dict(instances=instances, datums={
        'funnel_frame_fasteners': frame.fastener_datums(
            box.inner, box.y_joint, centre, seat),
        'funnel_centre': centre, 'funnel_seat': seat, 'funnel_frame_floor': floor,
        'y_stack_rods': shell.y_stack_rods(box.inner),
    })


def box_from_plan(plan):
    """Size the stated enclosure around the Rust placement plan's scalar readings."""
    shell = load()
    import _box_spec
    from _rust_enclosure_checks import box_readings
    metadata = plan['metadata']
    raw = metadata['pack']
    types = {kind.__name__: kind for kind in (shell.Pack, shell.PortField, shell.Nameplate)}
    if '__hsm_namedtuple__' in raw:
        pack = _box_spec._tupled(raw, types)
        placed = pack.placed
    else:
        def stations(value):
            if isinstance(value, list):
                return tuple(stations(item) for item in value)
            if isinstance(value, dict):
                if any(name.startswith('__hsm_') for name in value):
                    return _box_spec._tupled(value, types)
                return {name: stations(item) for name, item in value.items()}
            return value
        values = {name: stations(raw[name]) for name in shell.Pack._fields if name in raw}
        for name, record in (('port_field', shell.PortField), ('nameplate', shell.Nameplate)):
            if isinstance(values.get(name), dict):
                values[name] = record(**values[name])
        placed = values.pop('placed')
        pack = shell.Pack(placed={}, **values)
    raw_bounds = metadata.get('raw_bounds', metadata.get('bounds'))
    order = metadata.get('pack_order', tuple(placed))
    bounds = {name: raw_bounds[name] for name in order if name in placed}
    references = metadata.get('pack_references', metadata.get('references'))
    if references is None:
        references = {row['name']: row for row in plan['instances'] if row.get('name')}
    pack = pack._replace(placed={name: (None, None) for name in bounds})
    shell.BOUNDS.clear()
    readings = box_readings(shell, pack, bounds, references)
    box = shell.stated_box(pack, readings=readings)
    centre = ((box.inner[0]+box.inner[1])/2., shell._funnel_frame_part.center_y)
    box = shell.with_funnel(box, centre)
    return shell, shell.documented(box)


def main(box_path=None, directory=None):
    shell = load()
    import _box_spec
    from _machine_export import export
    from _machine_layout import dock_instances
    from _rust_enclosure_checks import check_pieces

    box_path = Path(box_path) if box_path is not None else _box_spec.ARTIFACT
    document = json.loads(box_path.read_text())
    shell, box, bounds = box_from_document(document)
    shell.BOUNDS[:] = bounds
    directory = Path(directory) if directory is not None else HERE
    models, seated = cut_pieces(shell, box, directory)
    readings = check_pieces(shell, box, models, installed_retainer=seated)
    from _materials import linear
    instances = [_model_instance(seated if name == 'pump-retainer' else model,
                                f'enclosure-{name}'.replace('-', '_'),
                                color=[round(c, 9) for c in linear(shell.PIECE_COLORS[name])])
                 for name, model in models.items()]
    if box.pack.collet_plate:
        dock = dock_instances(box.pack.collet_plate, directory=directory/'installed')
        instances.extend(dock['instances'])
        cut_tube_setting_jig(shell, box, directory)
    export(dict(name='enclosure', instances=instances), directory)
    shell._report_columns(box)
    shell._report_seams(box)
    shell._report_stacks(box)
    shell._report_bounds()
    shell._write_docs(box, readings['vents'])
    return dict(models=models, installed_retainer=seated, checks=readings)
