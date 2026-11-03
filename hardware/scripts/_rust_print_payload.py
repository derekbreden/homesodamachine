"""File-reference print surfaces and their owning family payloads."""
from pathlib import Path
import json
import sys


def _presentation():
    root = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(root/'hardware/printed-parts/enclosure/enclosure'))
    import _rust_enclosure_presentation
    return _rust_enclosure_presentation


def cut(step, stl, *, verbose=True, preserve_print_triangles=False, identity=None):
    """Keep STEP identity/source binding while Rust authors the printed drawing."""
    if identity is None:
        import flute_payload
        identity = flute_payload.solid_identity(step)
    step, stl = Path(step), Path(stl)
    return _presentation().print_payload(step, stl=stl, source=step,
        identity=identity, verbose=verbose,
        preserve_print_triangles=preserve_print_triangles)


def _header(path):
    import struct
    with Path(path).open('rb') as stream:
        length, = struct.unpack('<I', stream.read(4))
        return json.loads(stream.read(length))


def main(directories, *, preserve_print_triangles=None):
    import flute_payload
    import _rust_part
    import _machine_export

    directories = tuple(Path(path) for path in directories)
    found = flute_payload.pieces(directories)
    if not found:
        raise SystemExit('no printed meshes beside the solids in '
                         + ', '.join(str(d) for d in directories))
    skins = {}
    for step, stl in found:
        cut(step, stl, preserve_print_triangles=flute_payload.keeps_print_triangles(
            step, preserve_print_triangles))
        payload = Path(str(step)+'.mesh')
        for index, mesh in enumerate(_header(payload)['meshes']):
            skins[mesh['name']] = dict(payload=str(payload.resolve()), index=index)
    cut_here = {step.name+'.mesh' for step, _stl in found}
    for path in flute_payload.payloads(directories):
        if path.name in cut_here:
            continue
        owner = flute_payload.payload_owner(path)
        candidates = []
        for entry in _header(path)['meshes']:
            name = flute_payload.fluted_key(entry['name'], skins, owner=owner)
            if name is not None:
                candidates.append(dict(skins[name], target=entry['name']))
        if not candidates:
            continue
        plan = _rust_part.check('enclosure-shell', 'enclosure-presentation', dict(
            op='graft_plan', target_payload=str(path.resolve()), candidates=candidates))
        for row in plan.get('moved', ()):
            print(f"   {path.name}: {row['name']} keeps its host surface; no placement "
                  f"recovered across {row['drift_mm']:.1f} mm")
        if plan['skins']:
            result = _machine_export.graft(path, plan['skins'])
            if result['grafted']:
                print(f"-> {path}  {result['grafted']} piece(s) grafted, "
                      f'{path.stat().st_size/1e6:.2f} MB')
    return 0
