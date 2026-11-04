"""Every stocked thing in the shop, with the figure it is known by and where that came from.

This is one half of the answer; [`holders.py`](holders.py) is the other, and says which
holder each of these lives in.

Read [`_bound.py`](_bound.py) before adding a row. The short of it: a parcel's figure is
an upper bound and nothing else, and the only geometry allowed to read one is geometry
that grows to fit. `exact` is a standard or a maker's own drawing; `parcel` is a listing's
shipping box; `mixed` is the ordinary case, where a maker publishes an overall length and
the rest of the box is all anyone has.

A `heap` is a pack tipped in loose, and carries no direction — only the volume it stands
in. Everything else carries three figures in the pose its holder stores it in: X across
the holder, Y front to back, Z up.
"""

import math

from _bound import (
    EXACT,
    MOST,
    NEST_INTERLOCKS,
    NEST_TANGLES,
    bore,
    exact,
    heap,
    mixed,
    parcel,
)



import pathlib as _reference_pathlib
_reference_hardware = next(p for p in _reference_pathlib.Path(__file__).resolve().parents if p.name == 'hardware')
import sys as _reference_sys
_reference_sys.path.insert(0, str(_reference_hardware / 'reference'))
from _reference_data import data as _reference_data
_reference_values = _reference_data('catalog')
globals().update({name: _reference_values[name] for name in ('inch', 'DIN912', '_din912', 'M3X25', 'M3X12SS', 'M3X12', 'M3X10', 'M3X8', 'M5X10', 'M2X6', 'ULP_HEAD', 'ULPM3X6', 'ULPM3X8', 'M5WASHER', 'RUTHEX_M3', 'RUTHEX_M3S', 'RUTHEX_M2', 'RUTHEX_M5', 'MAGNETS', 'MEMBRANES', '_din46228', 'FERRULES', 'SHRINK', 'TERMINALS', 'LEVERS', 'TIES', 'XH_PITCH', 'XH_HOUSINGS', 'XH_CONTACTS', 'XH_LEADS', 'RJ11_JACKS', 'RJ11_PLUGS', 'UNION_TEES', 'UNION_ELBOWS', 'TWO_WAY', 'BULKHEADS', 'BULKHEADS_ACETAL', 'MALE_CONNECTORS', 'FEMALE_ADAPTERS', 'FLARE_ADAPTERS', 'BRASS_FLARE', 'NEOFIT_BULKHEADS', 'PURESEC_ELBOWS', 'BALL_VALVES', 'CHECK_VALVES', 'COUPLINGS', 'BARBS', 'PNEUMATIC', 'CLAMPS', 'STIFFENERS', 'REGULATOR', 'RELIEF_VALVE', 'WIRE_REEL', 'RIBBON_REEL', 'SOLDER_ROLL', 'SOLDER_POCKET', 'BRAID_BOBBIN', 'KAPTON_ROLLS', 'PTFE_TAPE', 'SN2549', 'HS9327', 'PRECIVA', 'KLEIN_11063W', 'KLEIN_11057', 'KLEIN_VDV427', 'KNIPEX_860180', 'VCE_GJ668BL', 'KATA_CUTTER', 'MUDDER_CUTTER', 'MASTERCOOL_70025', 'RIDGID_150', 'IFIXIT_TWEEZERS', 'T18_TIP', 'INSERT_TIP', 'COBALT_DRILL', 'PILOT_DRILL', 'NPT_TAP', 'TAP_GUIDE', 'COUNTERSINKS', 'DOWEL_PIN', 'SPADE_BIT', 'HOLE_SAW_ARBOR', 'FLUX_JAR', 'FLUX_BOTTLE', 'FLUX_SYRINGES', 'FLUX_BRUSHES', 'HEAT_GUN', 'HOTEND_SOCKS', 'HOTENDS', 'DEPRESSORS', 'PIGMENT', 'MIXING_CUPS', 'FLARE_NUTS', 'SLIP_COUPLINGS', 'FILTER_DRIER', 'PIERCING_VALVE', 'NOGA', 'NPT_DIE')})



def cylinder_volume(diameter, height):
    return _reference_data('catalog', 'cylinder_volume', (diameter, height), {})


def screw_volume(head_diameter, head_height, thread_diameter, length):
    "The cylinder a socket head cap screw sweeps: its head's diameter over its whole\n    length. A screw in a heap keeps its neighbours off at its head, not at its thread."
    return _reference_data('catalog', 'screw_volume', (head_diameter, head_height, thread_diameter, length), {})


# ============================================================
# FASTENERS — every figure a standard
# ============================================================

#: head diameter, head height, per nominal thread


def cap_screw(label, thread, length, count, asin):
    return _reference_data('catalog', 'cap_screw', (label, thread, length, count, asin), {})



#: McMaster publishes no head figure for the 91223A ultra-low-profile family. 6.0 x 1.5
#: is over every published ultra-low M3 head, and a heap read too large only ever asks
#: for a deeper compartment than it needs.


#: ONE INSERT, TWO BODIES. ruthex's short and full-length M3 share a knurl and a
#: recommended hole and differ only in length. Nothing about a loose one tells them
#: apart. Label these two troughs before anything else on the holder.



# ============================================================
# HARNESS — ferrules and sleeving to a standard, terminals to a listing
# ============================================================

#: DIN 46228-4: collar outside diameter, length over the collar, per cross-section.


def ferrule(section, colour, count):
    return _reference_data('catalog', 'ferrule', (section, colour, count), {})




def shrink(band, widest, pieces, piece_length, wall=0.5):
    'Sleeving lies flat, not round: a sleeve of outside diameter d flattens to a strip\n    pi*d/2 wide and two walls thick, and that strip is what a compartment fills with.'
    return _reference_data('catalog', 'shrink', (band, widest, pieces, piece_length, wall), {})




def spade(label, tab, count, asin, sleeve_diameter=6.5, length=22.0):
    return _reference_data('catalog', 'spade', (label, tab, count, asin, sleeve_diameter, length), {})



#: WAGO's own drawings for the 221 series. A lever nut is a brick and its three figures
#: are all published, which is rare enough here to be worth saying.


def zip_ties(length_in, strap, thickness, count, asin):
    return _reference_data('catalog', 'zip_ties', (length_in, strap, thickness, count, asin), {})




# ============================================================
# JST XH — the connector series' own datasheet
# ============================================================

#: JST XH is a 2.5 mm pitch series. A housing is (poles x 2.5 + 1.9) long, 5.8 wide and
#: 8.0 tall, and a SXH-001T contact is a 1.6 mm strip 8.6 mm long. Every figure here is
#: the connector standard's, so nothing about these depends on a parcel.


def xh_housing(poles, count):
    return _reference_data('catalog', 'xh_housing', (poles, count), {})




# ============================================================
# UMBILICAL — RJ11 is 6P4C and 6P4C is a standard
# ============================================================



# ============================================================
# FITTINGS — John Guest's own catalogue drawings, then the rest
# ============================================================

def jg(part, label, length, across, count):
    'A John Guest fitting. JG publishes a dimensioned drawing for every part number.'
    return _reference_data('catalog', 'jg', (part, label, length, across, count), {})


def listed(label, length, across, count, asin, nest=NEST_INTERLOCKS):
    "A fitting whose figures are the listing's own, not a drawing's."
    return _reference_data('catalog', 'listed', (label, length, across, count, asin, nest), {})




#: The two big single items on the fittings bench. Both stand on end.


# ============================================================
# ROUND STOCK — every one of these goes in a cradle, and the cradle
# reads none of these figures for a fit
# ============================================================



# ============================================================
# HAND TOOLS — a length is usually published and a cross-section
# almost never is. Every one of these goes in a comb, which reads
# the thinnest figure as an upper bound and nothing else.
# ============================================================



# ============================================================
# INDEXED STOCK — a bore is cut to a size, so every figure below
# is a standard's and `Env.size` refuses anything else
# ============================================================

#: Five bodies on one 1/4 in shank. They stand head down, so the bore is cut to the head
#: and the shank stands up — and a head is a nominal inch fraction, which is exact.
#: The saw set lies down rather than standing: the arbor's flange and the spade bit's
#: 1 in paddle are both wider than their shanks, and a bore cut to a shank leaves the
#: wide end to foul its neighbours.


# ============================================================
# THE REST OF THE BENCH — things that stand in a tub
# ============================================================

#: Both of these stand in a bundle rather than lying in a heap, so both are given a
#: shape: four syringes two by two, and the brushes as the column they make standing.



#: Lying down. A 155 mm tool standing wants a 168 mm bin for a 28 mm handle, and the
#: bin is then mostly air with a tool waving out of the top of it.
