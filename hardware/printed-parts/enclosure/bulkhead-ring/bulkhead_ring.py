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
RING_W = 7.05
# A port pocket's depth into the wall's outer face, and the height of the boss behind it that
# keeps the wall's full stock under the pocket — `enclosure_assembly.PORT_BOSS_PROUD`.
# `tube_collar` weighs a collar's rock on its tube against a label this thick.
THICK = 2.0
# A pocket's top above the water and flavour axes. `rise` adds the CO2 axis's drop so all three
# upper pockets finish on the enclosure's top face, open above.
RISE = 18.789

# One word per station.
Chip = collections.namedtuple("Chip", "word")
STATIONS = {
    "water": Chip("TAP"),
    "carb": Chip("SODA"),
    "co2": Chip("CO2"),
    "flavor-a": Chip("FLAVOR"),
    "flavor-b": Chip("FLAVOR"),
    "drain": Chip("OVER"),
}

# The key each station reads its two filaments under in `_y_wall_dimensions` — both flavour
# labels print off one spool and letter in one colour, so both answer to `flavor`.
FLUIDS = {"water": "water", "carb": "carb", "co2": "co2",
          "flavor-a": "flavor", "flavor-b": "flavor", "drain": "drain"}

# THE FACE IS THE SYSTEM'S. This repo does not ship `WORD_FONT`, so `WORD_WIDTHS` carries what
# each word measures across in it at `WORD_SIZE`, and `tube_collar` reads its built words back
# against those figures. A machine that resolves the name to another face letters a different part.
WORD_FONT = "Helvetica"
WORD_KIND = "bold"
# The em the words are set at, and `WORD_CAP` the cap height that comes to.
WORD_SIZE = 6.5
WORD_CAP = 4.951
WORD_WIDTHS = {"TAP": 12.657, "SODA": 18.411, "CO2": 12.813, "FLAVOR": 25.952, "OVER": 17.827}
# How deep a word's recess is cut into a label's outboard face.
WORD_DEPTH = 1.0
# How far the word stands proud of that face: two 0.24 mm layers in the word's colour alone.
WORD_RAISE = 0.48
# What a word keeps clear of the edges of the band it stands in.
WORD_MARGIN = 1.0


def od(fam: str) -> float:
    """The common width of all six labels, including the longest FLAVOR word."""
    return port_chip.WIDTH


def bottom(fam: str) -> float:
    """A pocket's bottom edge below its fitting's axis, at the flange envelope."""
    return FAMILIES[fam].flange_footprint() / 2.0


def rise(which: str) -> float:
    """A pocket's top above its own fitting's axis."""
    return RISE + (_enc_interface.co2_axis_drop if which == "co2" else 0.0)


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
