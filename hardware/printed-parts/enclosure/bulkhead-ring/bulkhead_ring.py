"""Rear-port identification figures: the word each of the +Y wall of back-top's six stations
carries, the lettering those words are set in, and the label envelope the wall's port pockets
are read from.

Nothing here builds a part. `rear_identification` cuts the six installed tiles and `tube_collar`
the collars that name the same lines, and both take each station's word, the key its two filaments
are read under and the lettering from here, so a word changed for a port is changed on the wall
and on the tube by one edit. `data_ring` letters in the same face.

    STATIONS, FLUIDS    each station's word, and the key `_y_wall_dimensions` reads its chip and
                        word filaments under
    WORD_*              the face, em, recess depth, raise and measured widths of the lettering
    RING_W, THICK, RISE, od, bottom, rise
                        the label envelope `enclosure_assembly` reads for the wall's port
                        pockets, the bosses behind them and the clamp stack
    split               a two-colour label STEP back apart, as `(tile, word)`

Coordinate frame — THE FITTING'S:
  Y = the fitting's flow axis. +Y = outboard, toward the customer's tube.
  Origin = the label's INBOARD face, the one that lands on the wall. A label spans y = 0 to its
      own thickness, and its word fills a recess in the outboard face and stands proud of it.
  +Z = up. X completes the right-handed frame, so from outside the machine — looking down −Y —
      +X runs to the LEFT and a word reads along −X.
"""

import collections
import sys
from pathlib import Path

_here = Path(__file__).resolve()
_hw = next(p for p in _here.parents if p.name == "hardware")
for _p in (_hw / "scripts",
           _hw / "printed-parts" / "cadlib",
           _hw / "printed-parts" / "enclosure" / "enclosure",
           _hw / "printed-parts" / "enclosure" / "y-wall-of-back-top",
           _hw / "reference" / "jg-bulkhead-union",
           _hw / "reference" / "neofit-bulkhead",
           _hw / "reference" / "neofit-drain-bulkhead"):
    sys.path.insert(0, str(_p))
sys.path.insert(0, str(next(p for p in _here.parents
                            if (p / "tools" / "docgen").is_dir()) / "tools"))

import cadquery as cq
import jg_bulkhead_union as _jg  # noqa: E402
import neofit_drain_bulkhead as _drain
import neofit_bulkhead as _neo  # noqa: E402
import port_chip  # noqa: E402
import _enclosure_interface as _enc_interface  # noqa: E402

# THREE FAMILIES OF FITTING CROSS THIS WALL, and a pocket's lower edge is struck on the flange of
# the one it sits under — `union` for the PP1208E the water and umbilical ports use, `neofit` for
# the ABU44, and the metric DRAIN fitting. All labels share one width.
FAMILIES = {"union": _jg, "neofit": _neo, "drain": _drain}

# The band a port's identification is lettered and painted in: `tube_collar` stands its word in
# a band this tall above the tube's axis, and `drawings/line-art/_appliance_model` paints each
# port's mark this far past the fitting.
from _enclosure_data import dimensions as _dimensions, read as _read

_values = _dimensions()['bulkhead']
globals().update({name: value for name, value in _values.items()
                  if name.isupper() and name != 'STATIONS'})
Chip = collections.namedtuple('Chip', 'word')
STATIONS = {name: Chip(_values['STATIONS'][name]) for name in _values['station_order']}
FLUIDS = {name: _values['FLUIDS'][name] for name in _values['station_order']}


def od(fam: str) -> float:
    """The common width of all six labels, including the longest FLAVOR word."""
    return _values['width']


def bottom(fam: str) -> float:
    """A pocket's bottom edge below its fitting's axis, at the flange envelope."""
    return _read('bulkhead-bottom', flange_footprint=FAMILIES[fam].flange_footprint())


def rise(which: str) -> float:
    """A pocket's top above its own fitting's axis."""
    return _read('bulkhead-rise', bulkhead=_values, which=which,
                 co2_axis_drop=_enc_interface.co2_axis_drop)


def split(shape) -> tuple:
    """A two-colour label's STEP back apart, as `(tile, word)`.

    The tile spans its whole thickness from the inboard face at y = 0; the lettering stands in the
    recess and reaches nowhere near that face. So the ONE body touching it is the tile and every
    other body is a letter. Counting letters would tie this to the word each station happens to
    carry; reading the face does not."""
    solids = shape.Solids() if hasattr(shape, "Solids") else shape
    floor = [s for s in solids if abs(s.BoundingBox().ymin) < 1e-6]
    if len(floor) != 1 or len(solids) < 2:
        raise ValueError(
            f"a label's STEP is a tile and the letters lying in it, and this one carries "
            f"{len(solids)} {'body' if len(solids) == 1 else 'bodies'}, {len(floor)} of them on "
            f"the inboard face")
    return (floor[0], cq.Compound.makeCompound([s for s in solids if s is not floor[0]]))
