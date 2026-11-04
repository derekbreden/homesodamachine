"""PET-GF cradle holding the funnel's uncut ATEU44W stem elbow under its frame.

Coordinates are local to the frame's drain hole: the origin is on the hole's axis in the frame's
flat underside, +Z up and +Y aft. The installed cradle hangs `CATCH_GAP` below
that datum. The elbow's stem points up to the silicone bowl opening and its socket aft.

The pocket adds `fits.slip` radially to the scanned profile. Its forward horizontal
following seat is retained; the aft mouth continues the largest section to a broad exit.
The opening above the axis uses a convex mouth. The body prints bottom-down. Its top
supports the lower half of the socket and bend. The stem and socket collet stand free above it.

Each X side of the block carries on up as a wing, the body's full length, through a straight slot
in the frame's bottom web. A flat hook at the wing's top reaches outward over the web to within
`TIP_GAP` of the counterbore's X wall, which sets the block's width and so how far the slots stand
off the drain hole. Going up, each wing bends inward into its slot's inboard lane until the hook
clears the slot's outer edge, then springs back over the web. The silicone plug's flat underside
rests on the two hook tops in that released pose.

The counterbore and the silicone plug are rectangles centred on the hole, the plug's width across
X. The counterbore's ±Y walls stand on the slots' farther ends, so the web carries no strip between
a slot and a wall.
"""

import functools
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
_tools = next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"
for _p in (_hw / "scripts", _hw / "printed-parts" / "cadlib",
           _hw / "reference" / "neofit-stem-elbow", _hw / "manifold-layout", _tools):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
import fits                                                   # noqa: E402
import above_core as _layout                                  # noqa: E402

from _zone_data import data as _zone


def _data(**payload):
    return _zone('elbow-cradle', **payload)


_state = _data()
_stem_parameters = _state['parameters']
globals().update(_state['values'])


def _profiles(leg):
    return tuple([tuple(p) for p in profile] for profile in _data(method='profiles', leg=leg))


def elbow_z():
    return _data(method='elbow_z')


def block():
    return tuple(_data(method='block'))


def _bent(points, length, tip):
    return [tuple(p) for p in _data(method='bent', points=points, length=length, tip=tip)]


def passage(w_in, w_out, tip, slot_out, base, face, top):
    return _data(method='passage', w_in=w_in, w_out=w_out, tip=tip,
                 slot_out=slot_out, base=base, face=face, top=top)


@functools.cache
def stations():
    return _data(method='stations')


def socket_half_length():
    return _data(method='socket_half_length')


def plug_half_length(half_width):
    return _data(method='plug_half_length', half_width=half_width)


def hook_corner_clearance(half_width):
    return _data(method='hook_corner_clearance', half_width=half_width)


def _turn_profile(points):
    return [tuple(p) for p in _data(method='turn_profile', points=points)]


def numbers():
    result = _data(method='numbers')
    for key in ('block', 'mouth_tangent', 'wing_x'):
        result[key] = tuple(result[key])
    return result


def _document(s):
    from docgen import substitute_md
    substitute_md(_here.parent / 'README.md', variables=_data(method='document', stations=s))


def main():
    import _rust_part
    said = _rust_part.cut('funnel', 'elbow-cradle', numbers(), _here.parent)
    _document(stations())
    print(f"-> elbow-cradle STEP, model, payload and STL; {said['bodies'][0]['volume']:.1f} mm3")


if __name__ == "__main__":
    import _rust_part
    _rust_part.start()
    if sys.argv[1:] == ["selftest"]:
        _rust_part.check('funnel', 'elbow-cradle', numbers())
        s = stations()
        print(f"  the elbow drops straight in and both wings stand on the body; the hook bends "
              f"{s['bend']['hook_deflection']:.2f} mm into a {s['lane']:.2f} mm lane")
        print("elbow_cradle selftest OK")
    else:
        main()
