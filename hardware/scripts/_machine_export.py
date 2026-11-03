"""File-reference model and presentation export through the Rust machine program.

The inputs are ordered fine-model selections and explicit installed frames. Python
passes metadata; the program streams physical arrays, prepares presentations and
writes STEP, viewer payloads and GLBs without constructing Python geometry objects.
"""
from __future__ import annotations
from pathlib import Path


def _run(spec, output):
    import _rust_part
    output = Path(output).resolve()
    output.mkdir(parents=True, exist_ok=True)
    result = _rust_part.cut('machine', 'machine-export', {'spec': spec}, output,
                            numbers_name='machine-export-' + spec.get('op', 'physical'))
    rows = result.get('results', ())
    return rows[-1] if rows else result


def export(spec, output):
    """Write physical STEP, exact fine archive and its paired drawing payload.

    ``split_components=True`` explicitly expands a coloured compound reference into
    its existing kernel components and ``name/1`` leaves. Other source entries pass
    through without reordering their arrays or face records.
    """
    return _run({**spec, 'op': 'physical'}, output)


def scene(model, target, *, aliases, envelope, document):
    """Publish the named machine scene from physical and foam model references."""
    target = Path(target).resolve()
    return _run({'op': 'scene', 'model': str(Path(model).resolve()),
                 'file': str(target), 'aliases': aliases, 'envelope': envelope,
                 'document': document}, target.parent)


def graft(target_payload, skins, *, model=None):
    """Replace explicit named drawing surfaces; retain the target physical geometry.

    Each skin supplies ``payload`` or ``model`` and an exact 3x4 ``transform``.
    ``indices`` select source leaves; ``targets`` map them one-to-one to exact host
    leaf names. ``names`` maps source names to logical host bodies instead.
    ``source_sha256`` can bind a retained source when its STEP is not present. The
    result's ``grafted`` is the number of replaced target meshes. An empty skin list
    binds the existing presentation to ``model`` without changing model arrays.
    """
    target = Path(target_payload).resolve()
    spec = {'op': 'graft', 'target_payload': str(target), 'skins': list(skins)}
    if model is not None:
        spec['model'] = str(Path(model).resolve())
    return _run(spec, target.parent)


def views(spec, output):
    """Write scene GLBs from existing mesh buffers and explicit body membership."""
    return _run({**spec, 'op': 'views'}, output)


def append_wiring(host_step, wire_step, *, wire_model=None):
    """Append generated wiring while retaining all physical STEP/payload records."""
    host = Path(host_step).resolve()
    spec = {'op': 'append', 'host_step': str(host),
            'wire_step': str(Path(wire_step).resolve())}
    if wire_model is not None:
        spec['wire_model'] = str(Path(wire_model).resolve())
    return _run(spec, host.parent)
