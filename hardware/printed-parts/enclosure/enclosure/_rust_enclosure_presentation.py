"""The enclosure's existing print-surface presentation, authored by Rust."""
import json
from pathlib import Path
import tempfile


def print_payload(step, *, check_print=False, preserve_print_triangles=False,
                  identity=None, source=None, stl=None, verbose=True):
    """Draw the printed STL without changing it or its fine physical model.

    ``check_print`` retains the quadrant writers' existing slicer refusal. The
    relaxed retainer and setting jig use their existing unchecked path.
    """
    import _rust_part
    from _payload_rules import CREASE_DEG, LINEAR_DEFLECTION_RATIO

    step = Path(step).resolve()
    numbers = dict(step_name=step.name, model=str(step.with_name(step.name+'.npz')),
                   stl=str(Path(stl).resolve() if stl is not None else step.with_suffix('.stl')),
                   check_print=check_print, preserve_print_triangles=preserve_print_triangles,
                   crease_deg=CREASE_DEG, deflection_ratio=LINEAR_DEFLECTION_RATIO)
    if identity is not None:
        numbers['identity'] = identity
    if source is not None:
        numbers['source'] = str(Path(source).resolve())
    with tempfile.TemporaryDirectory(prefix='hsm-enclosure-presentation-') as directory:
        source = Path(directory)/'enclosure-presentation.numbers.json'
        source.write_text(json.dumps(numbers, sort_keys=True)+'\n')
        result = json.loads(_rust_part.run('enclosure-shell', 'enclosure-presentation',
                                          source, step.parent))
    target = step.with_name(step.name+'.mesh')
    _rust_part._WRITE_TARGETS.add(_rust_part._relative(target))
    if verbose:
        print(f"-> {target.name}  {result['printed_triangles']} -> "
              f"{result['drawing_triangles']} facets, {result['deviation']:.3f} mm "
              f"inside a {result['bound']:.3f} mm budget")
    return result
