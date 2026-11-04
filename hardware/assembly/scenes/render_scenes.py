"""Named machine scenes exported by Rust from numeric layout and material records."""
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_HW = next(p for p in _HERE.parents if p.name == "hardware")
_ROOT = _HW.parent
for _p in (_HERE.parent, _HW / "scripts", _HW / "manifold-layout",
           _HW / "cold-core-layout", _HW / "printed-parts" / "cold-core",
           _ROOT / "tools"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import _scenes

GLB_DIR = _HERE.parent / "glb"
ASSEMBLY_MESH = _HW / "manifold-layout" / "enclosure-assembly.step.mesh"
CORE_MESH = _HW / "cold-core-layout" / "cold-core-assembly.step.mesh"


def numeric_spec(assembly):
    """Current scene membership from scalar fastening, route and placement records."""
    metadata = assembly.get('metadata', assembly)
    checks = assembly.get('checks', {})
    colours = metadata.get('logical_rgba', metadata.get('colours', {}))
    core_names = metadata.get('core_body_names', ())
    core_names = tuple(name.removeprefix('cold-core/') for name in core_names)
    external = set(metadata.get('core_external_names', ()))
    equipment = set(metadata.get('core_equipment_names', ()))
    promoted = equipment | external
    present = set(colours) | {'cold-core/'+name for name in core_names}
    present |= {name.rsplit('/', 1)[-1] for name in present
                if name.rsplit('/', 1)[-1] in external}
    present.add(_scenes.INNER_ROOT)
    tube_sites = metadata.get('tube_anchor_sites', ())
    cap_names = set(metadata.get('cap_anchor_names', ()))
    cap_names |= {'anchor-cap-'+rid for rid, station in tube_sites
                  if station[5:6] in (['cap'], ('cap',))}
    rows = checks.get('mounts', metadata.get('mounts', ()))
    rows = [row for row in rows
            if not row[0].startswith('anchor-cap-') or row[0] in cap_names]
    holders = {name: (by if isinstance(by, str) else None) or _scenes.BEARS_ON.get(name)
               for name, by, joint in rows}
    holders.update(metadata.get('manifold_tube_holders', {}))
    pieces = metadata.get('tube_anchor_pieces', {})
    for rid, _station in tube_sites:
        if 'tube-'+rid in present:
            holders['tube-'+rid] = pieces[rid]
    for name in equipment:
        if name in holders:
            holders[name] = _scenes.INNER_ROOT
    for name in (*_scenes.BACK_TOP_CARRIED_COMPONENTS, *_scenes.BACK_TOP_CARRIED_TUBES,
                 'tube-soda-core-rise'):
        if name in present:
            holders[name] = 'enclosure-back-top'
    for rider, host in checks.get('rides', metadata.get('rides', {})).items():
        if rider in holders and host in holders:
            holders[rider] = holders[host]
    runs = metadata.get('runs', ())
    conduits = set(metadata.get('cap_conduits', ()))
    crossings = {}
    for run in runs:
        for endpoint in (run['frm'], run['to']):
            part, _, mouth = endpoint.partition('.')
            if part == _scenes.INNER_ROOT and mouth in conduits:
                crossings['cold-core/line-'+mouth] = 'tube-'+run['id']

    def inner_of(scene):
        names = core_names if scene.inner == _scenes.INNER_ALL else scene.inner
        return {'cold-core/'+name for name in names}

    def named(scene):
        bodies = set()
        for root in scene.roots:
            bodies |= _scenes.held_by(root, holders, scene.later)
        if scene.id in _scenes.BARE:
            derived = set(scene.roots)
        else:
            tubes = {'tube-'+r['id'] for r in runs
                     if holders.get('tube-'+r['id']) in bodies
                     or {r['frm'].split('.')[0], r['to'].split('.')[0]} <= bodies}
            derived = bodies | tubes
        derived -= set(scene.later)
        inner = inner_of(scene)
        if inner:
            derived.discard(_scenes.INNER_ROOT)
            derived |= inner - set(scene.later)
        derived -= {'cold-core/'+n for n in promoted if n in derived}
        derived |= set(scene.also)
        derived |= {half for line, half in crossings.items() if line in derived}
        derived -= set(scene.later)
        derived -= {'cold-core/'+n for n in promoted if n in derived}
        if scene.without:
            derived -= named(_scenes.SCENE_BY_ID[scene.without]) - set(scene.roots)
        return derived

    for name in external:
        if 'cold-core/'+name in colours:
            colours = {**colours, name: colours['cold-core/'+name]}
    views = []
    for scene in _scenes.SCENES:
        names = sorted(named(scene))
        missing = set(names) - present
        if missing:
            raise ValueError(f'scene {scene.id!r} names bodies absent from the model: {sorted(missing)}')
        views.append({'id': scene.id, 'bodies': names, 'inner': sorted(inner_of(scene)),
                      'flip': scene.flip,
                      'overrides': {line: colours[half] for line, half in crossings.items()
                                    if line in names and half in names}})
    if 'finishes' in metadata:
        finishes = metadata['finishes']
    else:
        import _rust_part
        _rust_part.start()
        import _finishes
        finishes = _finishes.rows()
    return {'outer_payload': str(assembly.get('payload', ASSEMBLY_MESH)),
            'core_payload': str(assembly.get('core_payload', CORE_MESH)),
            'core_transform': metadata.get('core_carry3x4'),
            'colours': colours, 'core_colours': metadata.get('core_rgba', {}),
            'finishes': finishes, 'views': views}



def write_reference_glbs(assembly, output=GLB_DIR):
    """Write current named viewer scenes without loading Python geometry."""
    import _machine_export
    spec = assembly if 'views' in assembly else numeric_spec(assembly)
    output = Path(output)
    _machine_export.views(spec, output)
    return [Path(row['file']) if 'file' in row else output/(row['id']+'.glb')
            for row in spec['views']]



def write_glbs(assembly, require_core_payload=False) -> list:
    """Write every viewer scene from numeric membership and current model references."""
    return write_reference_glbs(assembly)
