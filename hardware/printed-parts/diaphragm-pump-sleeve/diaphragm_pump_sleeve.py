"""TPU elbow: a diaphragm pump port barb onto 1/4 in OD LLDPE, turned 90 degrees.

One part serves both ports, clocked on the barb at assembly. A rounded heel and a
smooth neck join the two round sockets, and a flat foot across the outer corner
stands it as a V with both mouths up. Each socket takes one 9 mm clamp band on
its plain outside. The barb socket is sized against the scanned G Ganen
profiles; the identified Siraya Tech Flex TPU 85A articles share this geometry.

Local frame: the barb tip at the origin, +X out along the barb, +Y the way the
tube leaves, Z = X x Y.
"""
from pathlib import Path
import argparse
import sys

HERE = Path(__file__).resolve().parent
HARDWARE = HERE.parents[1]
sys.path.insert(0, str(HARDWARE / "scripts"))

if __name__ == "__main__":
    import _rust_part
    _rust_part.start()

from _rust_data import request as _request


def _data(**payload):
    import _rust_part
    parameters = HARDWARE / 'reference/g-ganen-pump/reference-parameters.json'
    _rust_part._READ_TARGETS.add(parameters.resolve().relative_to(_rust_part.ROOT.resolve()).as_posix())
    return _request('part-data', 'part-data', {'part': 'diaphragm-pump-sleeve',
        'parameters': str(parameters), **payload})


globals().update(_data()['values'])
_COLOR_SRGB = tuple(_COLOR_SRGB)
CLAMP_RANGE = tuple(CLAMP_RANGE)
PORTS = {port: PORTS[port] for port in ('suction', 'discharge')}


def barb_rows(port):
    return [tuple(row) for row in _data(method='barb_rows', port=port)]


def engaged(port):
    return _data(method='engaged', port=port)


def crest():
    return _data(method='crest')


def root():
    return _data(method='root')


def installed_od(relaxed_od, bore, opened):
    return _data(method='installed_od', relaxed_od=relaxed_od, bore=bore, opened=opened)


def tube_port():
    return tuple(tuple(p) for p in _data(method='tube_port'))


def tube_mouth(tip, axis, toward):
    return tuple(tuple(p) for p in _data(method='tube_mouth', tip=tip, axis=axis, toward=toward))


def numbers():
    from _occt_color import rgba
    return _data(color=list(rgba(_COLOR_SRGB, {})[:3]))['numbers']


def _neck_radius(y):
    return _data(method='neck_radius', y=y)


def _foot_neck_end():
    return _data(method='foot_neck_end')


def foot_area():
    return _data(method='foot_area')


def volume():
    return _data(method='volume')


def _document(solid_volume, foot, height):
    sys.path.insert(0, str(HARDWARE.parent / 'tools'))
    from docgen import substitute_md
    variables = _data(method='document', volume=solid_volume, foot_area=foot, height=height)['variables']
    substitute_md(HERE / 'README.md', variables=variables)


def main(output=None):
    import _rust_part
    out = Path(output) if output is not None else HERE
    out.mkdir(parents=True, exist_ok=True)
    _rust_part.cut("tooling", "diaphragm-pump-sleeve", numbers(), out)
    solid_volume, foot = volume(), foot_area()
    height = _data()['height']
    _document(solid_volume, foot, height)
    print(f"-> diaphragm-pump-sleeve.step, diaphragm-pump-sleeve.stl, "
          f"diaphragm-pump-sleeve.step.mesh; {solid_volume / 1000:.3f} cm3")
    print(f"   tube axis {TUBE_AXIS:.2f} mm past the barb tip; foot {foot:.1f} mm2; "
          f"print height {height:.1f} mm")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    options = parser.parse_args()
    main(options.output)
