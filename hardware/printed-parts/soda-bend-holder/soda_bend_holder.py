"""Accepted2mm PET-GF R14 holder with3mm legs, in its printable frame."""
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
HW = HERE.parents[1]
sys.path[:0] = [str(HW/'scripts'), str(HW/'manifold-layout')]
import soda_inlet


def build():
    return soda_inlet.holder_native()


def numbers():
    """Live dimensions from the production inlet plan, in the printable frame."""
    from _materials import M_PETGF_BLACK, linear
    return {**soda_inlet.holder_geometry_numbers(), 'color': list(linear(M_PETGF_BLACK))}


def _native_main(output=None):
    import cadquery as cq
    from _cadq_export import export_assembly
    from _materials import M_PETGF_BLACK, one_body
    from flute_payload import cut
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    step = out/'soda-bend-holder.step'
    stl = out/'soda-bend-holder.stl'
    shape = build()
    export_assembly(one_body(shape, 'soda-bend-holder', M_PETGF_BLACK), str(step))
    cq.exporters.export(shape, str(stl), tolerance=.01, angularTolerance=.1)
    cut(step, stl, preserve_print_triangles=True)
    print(f'soda-bend-holder: {shape.Volume()/1000.:.3f} cm3')


def main(output=None, native=False):
    if native:
        return _native_main(output)
    import _rust_part
    _rust_part.start()
    out = HERE if output is None else Path(output)
    out.mkdir(parents=True, exist_ok=True)
    said = _rust_part.cut('tooling', 'soda-bend-holder', numbers(), out)
    print(f"soda-bend-holder: {said['bodies'][0]['volume']/1000.:.3f} cm3")


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path)
    parser.add_argument('--native', action='store_true')
    args = parser.parse_args()
    main(args.output, args.native)
