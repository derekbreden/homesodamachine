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


inch = 25.4


def cylinder_volume(diameter, height):
    return math.pi * (diameter / 2.0) ** 2 * height


def screw_volume(head_diameter, head_height, thread_diameter, length):
    """The cylinder a socket head cap screw sweeps: its head's diameter over its whole
    length. A screw in a heap keeps its neighbours off at its head, not at its thread."""
    return cylinder_volume(head_diameter, head_height + length)


# ============================================================
# FASTENERS — every figure a standard
# ============================================================

DIN912 = "DIN 912 / ISO 4762 socket head cap screw"
#: head diameter, head height, per nominal thread
_din912 = {2.0: (3.80, 2.00), 3.0: (5.50, 3.00), 5.0: (8.50, 5.00)}


def cap_screw(label, thread, length, count, asin):
    head_d, head_h = _din912[thread]
    return heap(
        label,
        count,
        screw_volume(head_d, head_h, thread, length),
        f"{DIN912}, M{thread:.0f} x {length:.0f}; count from {asin}",
    )


M3X25 = cap_screw("BNUOK M3 x 25, 12.9 black oxide", 3.0, 25.0, 60, "B0DJQGF665")
M3X12SS = cap_screw("BNUOK M3 x 12, 304 SS — wet joints", 3.0, 12.0, 120, "B0DJQGMQZM")
M3X12 = cap_screw("BNUOK M3 x 12, 12.9 black oxide — dry joints", 3.0, 12.0, 120, "B0DJQGVK8S")
M3X10 = cap_screw("BNUOK M3 x 10, 12.9 black oxide", 3.0, 10.0, 120, "B0DJQGGDP2")
M3X8 = cap_screw("BNUOK M3 x 8, 12.9 black oxide", 3.0, 8.0, 120, "B0DJQGPRPV")
M5X10 = cap_screw("MewuDecor M5 x 10, 12.9 black oxide", 5.0, 10.0, 100, "B0BHZVXNJX")
M2X6 = cap_screw("Sutemribor M2 x 6, 12.9 black oxide", 2.0, 6.0, 105, "B0CXQ7Q7L3")

#: McMaster publishes no head figure for the 91223A ultra-low-profile family. 6.0 x 1.5
#: is over every published ultra-low M3 head, and a heap read too large only ever asks
#: for a deeper compartment than it needs.
ULP_HEAD = (6.0, 1.5)
ULPM3X6 = heap(
    "McMaster 91223A412 M3 x 6 ultra-low-profile, 316 SS",
    100,
    screw_volume(*ULP_HEAD, 3.0, 6.0),
    "McMaster 91223A412; head over every published ultra-low M3",
)
ULPM3X8 = heap(
    "McMaster 91223A413 M3 x 8 ultra-low-profile, 316 SS",
    100,
    screw_volume(*ULP_HEAD, 3.0, 8.0),
    "McMaster 91223A413; head over every published ultra-low M3",
)

M5WASHER = heap(
    "M5 x 25 mm OD fender washer, 304 SS",
    60,
    cylinder_volume(25.0, 1.5),
    "B0GSMDY5GL states both diameters; 1.5 mm is the thick end of 304 at this width",
    nest=0.8,
)

#: ONE INSERT, TWO BODIES. ruthex's short and full-length M3 share a knurl and a
#: recommended hole and differ only in length. Nothing about a loose one tells them
#: apart. Label these two troughs before anything else on the holder.
RUTHEX_M3 = heap(
    "ruthex RX-M3x5.7 heat-set insert — the appliance default",
    100,
    cylinder_volume(4.6, 5.7),
    "ruthex RX-M3x5.7 published body; count from B08BCRZZS3",
)
RUTHEX_M3S = heap(
    "ruthex RX-M3Sx4.0 heat-set insert — shallow bores only",
    100,
    cylinder_volume(4.6, 4.0),
    "ruthex RX-M3Sx4.0 published body; count from B09ZHSGHXD",
)
RUTHEX_M2 = heap(
    "ruthex RX-M2x4 heat-set insert",
    70,
    cylinder_volume(3.6, 4.0),
    "ruthex RX-M2x4 published body; count from B088QJG676",
)
RUTHEX_M5 = heap(
    "ruthex RX-M5x9.5 heat-set insert",
    50,
    cylinder_volume(7.1, 9.5),
    "ruthex RX-M5x9.5 published body; count from B07YSVXWS8",
)

MAGNETS = heap(
    "neodymium disc magnets, 3 x 1 mm N52",
    100,
    cylinder_volume(3.0, 1.0),
    "B0BQ3LPGZ1 states 3 x 1 mm",
    nest=0.9,
)
MEMBRANES = heap(
    "LVDALAB PTFE membrane filters, 13 mm x 0.45 um",
    100,
    cylinder_volume(13.0, 0.15),
    "B0D41KT345 states the diameter; 0.15 mm is the thick end of a supported membrane",
    nest=0.9,
)


# ============================================================
# HARNESS — ferrules and sleeving to a standard, terminals to a listing
# ============================================================

#: DIN 46228-4: collar outside diameter, length over the collar, per cross-section.
_din46228 = {
    0.34: (3.4, 12.0),
    0.50: (3.8, 14.0),
    0.75: (4.0, 14.0),
    1.00: (4.4, 14.0),
    1.50: (4.8, 14.0),
    2.50: (5.6, 16.0),
}


def ferrule(section, colour, count):
    collar_d, length = _din46228[section]
    return heap(
        f"{section:g} mm2 ferrule, {colour}",
        count,
        cylinder_volume(collar_d, length),
        f"DIN 46228-4 {section:g} mm2; count from the Preciva kit B0DS622GKN",
    )


FERRULES = (
    ferrule(0.34, "turquoise — 22 AWG", 250),
    ferrule(1.50, "black — 16 AWG", 250),
    ferrule(0.50, "white", 150),
    ferrule(0.75, "grey", 100),
    ferrule(1.00, "red", 100),
    ferrule(2.50, "blue", 100),
)


def shrink(band, widest, pieces, piece_length, wall=0.5):
    """Sleeving lies flat, not round: a sleeve of outside diameter d flattens to a strip
    pi*d/2 wide and two walls thick, and that strip is what a compartment fills with."""
    return heap(
        f"2:1 heat shrink, {band}",
        pieces,
        (math.pi * widest / 2.0) * (2.0 * wall) * piece_length,
        f"Ginsco B01MFA3OFA states eleven fractional-inch diameters; {band} is its band",
        nest=NEST_TANGLES,
    )


SHRINK = (
    shrink("1.06 - 1.59 mm", 1.59, 190, 40.0),
    shrink("2.12 mm", 2.12, 100, 40.0),
    shrink("3.18 - 3.57 mm", 3.57, 90, 40.0),
    shrink("3.97 mm", 3.97, 70, 40.0),
    shrink("5.08 - 5.95 mm", 5.95, 50, 40.0),
    shrink("7.94 - 9.92 mm", 9.92, 80, 40.0),
)


def spade(label, tab, count, asin, sleeve_diameter=6.5, length=22.0):
    return heap(
        label,
        count,
        cylinder_volume(sleeve_diameter, length),
        f"{tab} tab is a standard; count from {asin}; the insulated sleeve is generous",
        nest=NEST_INTERLOCKS,
    )


TERMINALS = (
    spade("6.3 mm female push-on, red — Baomain", "6.3 mm", 100, "B01G408A4M"),
    spade("4.8 mm female push-on, red — Baomain", "4.8 mm", 100, "B01N5APVEE"),
    spade("#4 ring, red — smseace", "#4 ring", 150, "B08B5VS8ZR"),
    spade("6.3 mm female, assorted — three kits decanted", "6.3 mm", 123, "B0B4H54KPS"),
    spade("4.8 mm female, assorted — three kits decanted", "4.8 mm", 123, "B0B9MZJ2ML"),
    spade("2.8 mm male — Baomain 0.11 in", "2.8 mm", 214, "B01MZZGAJP", 4.5, 18.0),
)

#: WAGO's own drawings for the 221 series. A lever nut is a brick and its three figures
#: are all published, which is rare enough here to be worth saying.
LEVERS = (
    heap("WAGO 221-413, 3-conductor", 50, 13.0 * 12.5 * 8.2,
         "WAGO 221-413 datasheet, 13.0 x 12.5 x 8.2 mm", nest=NEST_INTERLOCKS),
    heap("WAGO 221-415, 5-conductor", 25, 13.0 * 12.5 * 13.0,
         "WAGO 221-415 datasheet, 13.0 x 12.5 x 13.0 mm", nest=NEST_INTERLOCKS),
    heap("WAGO 221-420, 10-conductor", 15, 13.0 * 12.5 * 25.6,
         "WAGO 221-420 datasheet, 13.0 x 12.5 x 25.6 mm", nest=NEST_INTERLOCKS),
)


def zip_ties(length_in, strap, thickness, count, asin):
    return heap(
        f'{length_in:g}" zip tie, {strap} mm strap',
        count,
        length_in * inch * strap * thickness,
        f"{length_in:g} in nominal length and {strap} mm strap from {asin}",
        nest=NEST_TANGLES,
    )


TIES = (
    zip_ties(4, 2.5, 1.0, 200, "B0BC1VH4XB"),
    zip_ties(6, 2.5, 1.0, 100, "B0DR8KSVQD"),
    zip_ties(8, 4.8, 1.1, 100, "B08BKSHJ93"),
)


# ============================================================
# JST XH — the connector series' own datasheet
# ============================================================

#: JST XH is a 2.5 mm pitch series. A housing is (poles x 2.5 + 1.9) long, 5.8 wide and
#: 8.0 tall, and a SXH-001T contact is a 1.6 mm strip 8.6 mm long. Every figure here is
#: the connector standard's, so nothing about these depends on a parcel.
XH_PITCH = 2.5


def xh_housing(poles, count):
    return heap(
        f"JST XH {poles}P housing",
        count,
        (poles * XH_PITCH + 1.9) * 5.8 * 8.0,
        f"JST XH series drawing, {poles}P at {XH_PITCH} mm pitch; count from the CQRobot kits",
        nest=0.9,
    )


XH_HOUSINGS = tuple(xh_housing(p, n) for p, n in
                    ((3, 40), (4, 40), (5, 30), (6, 30), (7, 20), (9, 20), (10, 20)))
XH_CONTACTS = heap(
    "JST SXH-001T contacts, loose",
    400,
    1.6 * 2.4 * 8.6,
    "JST SXH-001T-P0.6 drawing; count from the CQRobot kits",
    nest=NEST_TANGLES,
)
XH_LEADS = heap(
    "pre-crimped XH leads",
    100,
    1.6 * 2.4 * 8.6 + cylinder_volume(1.7, 150.0),
    "SXH-001T contact on 1.7 mm OD 22 AWG silicone, coiled",
    nest=NEST_TANGLES,
)


# ============================================================
# UMBILICAL — RJ11 is 6P4C and 6P4C is a standard
# ============================================================

RJ11_JACKS = heap(
    "RiteAV RJ11 6P4C punchdown keystone jacks, black",
    10,
    14.8 * 22.5 * 30.0,
    "the keystone form factor is 14.8 x 22.5 mm; 30 mm over the IDC block",
    nest=NEST_INTERLOCKS,
)
RJ11_PLUGS = heap(
    "EZYUMM RJ11 6P4C 3-prong modular plugs",
    20,
    9.65 * 11.7 * 7.6,
    "FCC 6P4C plug is 9.65 mm across the latch; count from the EZYUMM pack",
    nest=0.9,
)


# ============================================================
# FITTINGS — John Guest's own catalogue drawings, then the rest
# ============================================================

def jg(part, label, length, across, count):
    """A John Guest fitting. JG publishes a dimensioned drawing for every part number."""
    return heap(
        f"John Guest {part} — {label}",
        count,
        length * across * across,
        f"John Guest {part} catalogue drawing, {length} x {across} mm",
        nest=NEST_INTERLOCKS,
    )


def listed(label, length, across, count, asin, nest=NEST_INTERLOCKS):
    """A fitting whose figures are the listing's own, not a drawing's."""
    return heap(
        label,
        count,
        length * across * across,
        f"{asin} listing figures, {length} x {across} mm",
        nest=nest,
    )


UNION_TEES = jg("PP0208E", "union tee", 39.1, 16.3, 30)
UNION_ELBOWS = jg("PP0308E", "union elbow", 28.5, 16.3, 40)
TWO_WAY = jg("PP2308E", "two-way divider", 35.7, 16.3, 20)
BULKHEADS = jg("PP1208E", "bulkhead union", 34.6, 22.9, 10)
BULKHEADS_ACETAL = jg("PI1208S", "acetal bulkhead union", 34.9, 22.2, 2)
MALE_CONNECTORS = jg("PI010822S / PP010822E / PP010821WP", "male connectors", 38.0, 20.0, 30)
FEMALE_ADAPTERS = jg("PP450822E", "female adapter", 32.2, 24.0, 10)
FLARE_ADAPTERS = jg("PI4512F6S / PP061208W", "flare adapter and reducer stem", 38.1, 22.2, 20)
BRASS_FLARE = jg("MI4508F4SLF", "brass flare connector", 45.0, 18.0, 10)

NEOFIT_BULKHEADS = listed("neoFit ABU44-E acetal bulkheads", 40.0, 26.0, 10, "B0DPL88RHC")
PURESEC_ELBOWS = listed("PureSec 90-degree elbow bulkheads", 45.0, 30.0, 5, "B07P8784D2")
BALL_VALVES = listed("NeoFit push-fit ball valves", 50.8, 25.0, 5, "B0DPLBYZB4")
CHECK_VALVES = listed("GASHER and ChillWaves 1/4 NPT check valves", 65.0, 26.0, 8, "B08J2DN6HC")
COUPLINGS = listed("GAGIRA, LTWFITTING and TAISHER couplings and elbows", 40.0, 25.0, 14, "B0BVR3R58V")
BARBS = listed("LTWFITTING and MAACFLOW barb adapters", 50.0, 18.0, 9, "B07PNPHWMG")
PNEUMATIC = listed("MALIDA, TAILONZ and DERPIPE push-fit", 35.0, 20.0, 25, "B07HGTKQ89")
CLAMPS = listed("YDS and WC-316SS-06 hose clamps", 42.0, 25.0, 20, "B0968K4JRN")
STIFFENERS = listed("Siptenk 1/4 in tube stiffeners", 15.0, 7.0, 100, "B0CS662NVK", 0.9)

#: The two big single items on the fittings bench. Both stand on end.
REGULATOR = exact(
    "Interstate Pneumatics WR1110 regulator",
    32.0, 32.0, 90.0,
    "Interstate Pneumatics WR1110 published body",
)
RELIEF_VALVE = exact(
    "Control Devices SV-125 relief valve",
    30.0, 22.0, 65.0,
    "Control Devices SV-125 published body",
)


# ============================================================
# ROUND STOCK — every one of these goes in a cradle, and the cradle
# reads none of these figures for a fit
# ============================================================

WIRE_REEL = parcel(
    "BNTECHGO 22 AWG silicone, 250 ft black",
    99.1, 99.1, 88.9,
    "B06Y2PNW41 package — the listing publishes the wire's 1.7 mm OD and no reel figure",
)
RIBBON_REEL = parcel(
    "BNTECHGO 28 AWG 4-conductor silicone ribbon, 50 ft",
    81.0, 77.0, 68.0,
    "B0DK4V733Q package",
)
SOLDER_ROLL = parcel(
    "Kester 24-6337-0027 0.031 in, 1 lb",
    63.5, 58.4, 58.4,
    "B00068IJNQ package — Kester publishes the alloy and the fill, not the spool",
)
SOLDER_POCKET = parcel(
    "Kester 44 0.020 in, 3/4 oz pocket pack",
    44.5, 44.5, 12.7,
    "B00068IJQI package",
)
BRAID_BOBBIN = parcel(
    "Chemtronics Soder-Wick on its ESD bobbin",
    44.5, 44.5, 6.4,
    "B00425FUW2 package",
)
KAPTON_ROLLS = parcel(
    "ELEGOO polyimide tape, four widths",
    100.0, 100.0, 60.0,
    "B07XD98YYT package, the four rolls stacked",
)
PTFE_TAPE = parcel(
    "Millrose 70894 PTFE thread seal tape",
    53.0, 53.0, 15.0,
    "B07C9ZV4PG package",
)


# ============================================================
# HAND TOOLS — a length is usually published and a cross-section
# almost never is. Every one of these goes in a comb, which reads
# the thinnest figure as an upper bound and nothing else.
# ============================================================

SN2549 = mixed(
    "iCrimp SN-2549 ratcheting crimper, AWG 28-18",
    190.0, 65.0, 27.9,
    "iwiss.com publishes the SN-2549's 190 x 65 x 27.9 mm product envelope",
    (EXACT, EXACT, EXACT),
)
HS9327 = mixed(
    "haisstronica HS-9327 ratchet crimper, AWG 22-10",
    230.1, 59.9, 30.0,
    "B08F3JKDD3 states 230.1 x 59.9 mm; the thickness is the parcel's",
    (EXACT, EXACT, MOST),
)
PRECIVA = mixed(
    "Preciva ferrule crimper, AWG 28-5",
    240.0, 48.0, 32.0,
    "B0DS622GKN states a 240 x 48 mm tool; the thickness is the kit case's",
    (EXACT, EXACT, MOST),
)
KLEIN_11063W = mixed(
    "Klein 11063W Katapult stripper, 8-20 AWG solid",
    167.5, 69.0, 25.0,
    "Klein publishes 6.594 in overall and no other figure; the rest is B00CXKOEQ6",
    (EXACT, MOST, MOST),
)
KLEIN_11057 = mixed(
    "Klein 11057 wire stripper",
    184.0, 70.0, 25.0,
    "Klein publishes the overall length; the rest is the parcel",
    (EXACT, MOST, MOST),
)
KLEIN_VDV427 = exact(
    "Klein VDV427-300 impact punchdown, 66/110 blade",
    152.0, 38.0, 25.0,
    "Klein publishes 6 in x 1.5 in x 1 in overall",
)
KNIPEX_860180 = exact(
    "KNIPEX 86 01 180 Pliers Wrench",
    180.0, 46.0, 15.0,
    "KNIPEX 180 x 46 x 15 mm; joint thickness 12.0 mm, jaw thickness 8.0 mm",
)
VCE_GJ668BL = parcel(
    "VCE GJ668BL modular crimper",
    200.0, 75.0, 30.0,
    "B0BPJ8FJQC package",
)
KATA_CUTTER = mixed(
    "KATA micro flush cutter",
    127.0, 40.0, 17.0,
    "B0BBML9M2V names a 127 mm tool; the rest is the parcel",
    (EXACT, MOST, MOST),
)
MUDDER_CUTTER = parcel(
    "Mudder tubing cutter",
    80.0, 34.0, 24.0,
    "B0968K4JRN package",
)
MASTERCOOL_70025 = parcel(
    "MASTERCOOL 70025 capillary tube cutter",
    120.0, 68.0, 21.0,
    "B00AYJ0B7Y carton — MASTERCOOL publishes no figure for the 70025",
)
RIDGID_150 = mixed(
    "RIDGID 150 constant-swing tubing cutter",
    124.0, 92.0, 41.0,
    "RIDGID publishes 4-7/8 in overall; the rest is B0009W6T8G",
    (EXACT, MOST, MOST),
)
IFIXIT_TWEEZERS = mixed(
    "iFixit precision tweezers — extra-fine, angled, blunt",
    127.0, 12.0, 8.0,
    "iFixit publishes the 127 mm length; the rest is one tweezer out of B079K874CQ",
    (EXACT, MOST, MOST),
)


# ============================================================
# INDEXED STOCK — a bore is cut to a size, so every figure below
# is a standard's and `Env.size` refuses anything else
# ============================================================

T18_TIP = bore(
    "Hakko / VECO-T T18 soldering tip",
    6.5, 44.0,
    "the T18 series barrel is 6.5 mm, the fit to an FX-888D's collar",
)
INSERT_TIP = bore(
    "heat-set insert tip, M2 to M8",
    6.5, 40.0,
    "the seven tips share the T18 6.5 mm barrel of the iron they screw into",
)
COBALT_DRILL = bore(
    'Drill Hulk 9/64" M35 cobalt jobber drill',
    9.0 / 64.0 * inch, 2.875 * inch,
    'ANSI jobber-length 9/64 in; 12 of them from B07XNNNC5Y',
)
PILOT_DRILL = bore(
    "Mollom hole-saw pilot drill",
    0.25 * inch, 95.0,
    'the arbor takes a 1/4 in pilot; length from the set B0BZQ4J5B1',
)
NPT_TAP = bore(
    'HSS 1/4"-18 NPT taper pipe tap',
    0.421 * inch * 2.0 ** 0.5, 2.44 * inch,
    "ANSI B94.9 1/4-18 NPT: 0.421 in square across flats, 2.44 in overall",
)
TAP_GUIDE = bore(
    "Brown & Sharpe 599-792-30 spring tap guide",
    0.5 * inch, 115.0,
    'B&S publishes the 1/2 in hardened shank; the length is generous',
)
#: Five bodies on one 1/4 in shank. They stand head down, so the bore is cut to the head
#: and the shank stands up — and a head is a nominal inch fraction, which is exact.
COUNTERSINKS = tuple(
    bore(
        f'JNB Pro 82-degree countersink, {label} head',
        fraction * inch,
        70.0,
        f"ANSI 82-degree countersink, {label} nominal head; the set is B09C4X5R8F",
    )
    for label, fraction in (
        ("1/4 in", 0.25), ("3/8 in", 0.375), ("1/2 in", 0.5),
        ("5/8 in", 0.625), ("3/4 in", 0.75),
    )
)
DOWEL_PIN = bore(
    "POWERTEC 71476 ground dowel pin",
    0.25 * inch, 2.0 * inch,
    'POWERTEC 71476 is a ground 1/4 x 2 in dowel',
)
#: The saw set lies down rather than standing: the arbor's flange and the spade bit's
#: 1 in paddle are both wider than their shanks, and a bore cut to a shank leaves the
#: wide end to foul its neighbours.
SPADE_BIT = mixed(
    "Bosch DSB1013 spade bit, 1 in x 6 in",
    6.0 * inch, 1.0 * inch, 4.0,
    "B001NGPAA0 names a 1 in x 6 in bit; the paddle thickness is generous",
    (EXACT, EXACT, MOST),
)
HOLE_SAW_ARBOR = parcel(
    "Mollom hole-saw arbor with its pilot fitted",
    115.0, 30.0, 30.0,
    "B0BZQ4J5B1 set — Mollom publishes the saw's cut and no arbor figure",
)


# ============================================================
# THE REST OF THE BENCH — things that stand in a tub
# ============================================================

FLUX_JAR = parcel("MG Chemicals 8341 flux, 49 g jar", 52.0, 52.0, 45.0, "B005KDEIZ0 package")
FLUX_BOTTLE = parcel("BEEYUIHF no-clean flux, 30 mL", 32.0, 32.0, 100.0, "B0BC1VH4XB package")
#: Both of these stand in a bundle rather than lying in a heap, so both are given a
#: shape: four syringes two by two, and the brushes as the column they make standing.
FLUX_SYRINGES = exact(
    "no-clean flux syringes, 10 cc, four",
    34.0, 34.0, 90.0,
    "a 10 cc Luer syringe is 16 mm across the barrel and 90 mm long; four, two by two",
)
FLUX_BRUSHES = exact(
    "acid flux brushes, 36 standing",
    52.0, 52.0, 152.0,
    "a #2 acid brush is 6 in long on an 8 mm ferrule; 36 of them bundle to 52 mm across",
)
HEAT_GUN = parcel("QWORK mini heat gun", 66.0, 66.0, 160.0, "B08VW15TK8 package")

HOTEND_SOCKS = heap(
    "DUROZZLE silicone hotend socks",
    8,
    26.0 * 26.0 * 20.0,
    "B0CZ38MYL1 pack; a H2C sock is about 26 mm square",
    nest=NEST_INTERLOCKS,
)
HOTENDS = heap(
    "H2C hotends, the four a both-printer swap pulls",
    4,
    30.0 * 30.0 * 60.0,
    "the Bambu H2C hotend body, generous, lying down in the swap well",
    nest=NEST_INTERLOCKS,
)

DEPRESSORS = exact(
    'JMU 6" tongue depressors, 100',
    100.0, 48.0, 152.4,
    'a 6 x 3/4 x 1/12 in depressor is a standard size; 100 standing 5 x 20',
)
PIGMENT = parcel("BBDINO black silicone pigment, 150 g", 63.5, 63.5, 88.9, "B0FQPGDD49 package")
MIXING_CUPS = parcel(
    "Pouring Masters 5 oz mixing cups, 50 nested",
    82.0, 82.0, 227.1,
    "B07V6XKZG9 package — the nested column",
)

FLARE_NUTS = heap(
    'Joywayus brass 1/4" SAE 45-degree flare nuts',
    5,
    cylinder_volume(20.0, 20.0),
    'a 1/4 in SAE flare nut on a 7/16-20 thread is 20 mm across corners',
    nest=0.9,
)
SLIP_COUPLINGS = heap(
    '1/4" OD ACR copper slip couplings',
    10,
    cylinder_volume(7.5, 16.0),
    "B0FH549N6D states a 6.3 mm bore, 16 mm long, 0.6 mm wall",
    nest=0.9,
)
FILTER_DRIER = exact(
    "Supco D111 filter-drier",
    38.1, 63.5, 88.9,
    'B00DM8KGXS states 1.5 x 2.5 x 3.5 in in its title',
)
PIERCING_VALVE = exact(
    "Supco BPV31 bullet-piercing valve",
    50.8, 50.8, 44.5,
    "distributor spec tables give 2 x 2 x 1-3/4 in",
)
#: Lying down. A 155 mm tool standing wants a 168 mm bin for a 28 mm handle, and the
#: bin is then mostly air with a tool waving out of the top of it.
NOGA = exact(
    "Noga NG8150 deburr tool, NogaGrip-1 handle",
    155.0, 28.0, 28.0,
    "Noga publishes the NG8150's 125 x 28 mm handle; the blade adds 30 mm",
)
NPT_DIE = exact(
    'Drill America 1-1/2" OD round adjustable NPT die',
    1.5 * inch, 1.5 * inch, 18.0,
    'the die is 1-1/2 in OD by its own designation; 18 mm thick is generous',
)
