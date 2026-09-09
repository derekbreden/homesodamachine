"""What is printed: one holder per row, and the build that cuts and checks them all.

Run from the repository root:

    tools/cad-venv/bin/python hardware/printed-parts/shop-storage/holders.py

Every holder is one Gridfinity module. It stands anywhere a baseplate reaches, it prints
on its own feet without support, and it is the unit of being wrong: a figure that turns
out badly costs one module and not a column of them.

The build cuts each holder, runs its shape's own checks against everything the holder is
said to take, writes one coloured STEP per holder, and rewrites this directory's README.
A holder whose contents do not fit does not export — the check raises and the build stops
with the holder, the content and the two figures that disagree.
"""

import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import cadquery as cq  # noqa: E402

import _holder as H  # noqa: E402
import _kit  # noqa: E402
import catalog as C  # noqa: E402
from _bound import EXACT, Heap  # noqa: E402


here = Path(__file__).resolve().parent
out_dir = here / "holders"


@dataclass
class Holder:
    """One printed module.

    `takes` is what goes in it, in reading order — compartment by compartment for a tub,
    slot by slot for a comb, row by row for an index. `note` is the one line the README
    carries about why it is this shape.
    """

    name: str
    shape: str
    x_u: int
    y_u: int
    height_u: int
    takes: tuple = ()
    note: str = ""
    opts: dict = field(default_factory=dict)

    def __post_init__(self):
        if self.shape == "index" and not self.takes:
            self.takes = tuple(
                dict.fromkeys(env for row in self.opts["rows"] for env, _count in row)
            )

    @property
    def cells(self):
        return (self.opts.get("length_div", 0) + 1) * (self.opts.get("width_div", 0) + 1)


# ============================================================
# THE DOCK
# ============================================================

DOCKS = [
    Holder("dock-3x3", "dock", 3, 3, 0,
           note="The bench plate. Print as many as the bench has room for; any "
                "baseplate docks any holder."),
]


# ============================================================
# CRADLES — round stock, and not one figure read for a fit
# ============================================================

CRADLES = [
    Holder("reel-cradle", "cradle", 3, 3, 6,
           takes=(C.WIRE_REEL, C.RIBBON_REEL, C.KAPTON_ROLLS),
           note="A 90-degree V. A reel rests on two lines and centres itself between "
                "them at any radius, and turns as the wire is pulled. Nothing here is "
                "cut to a reel's diameter or to its width."),
    Holder("roll-cradle", "cradle", 2, 2, 5,
           takes=(C.SOLDER_ROLL, C.SOLDER_POCKET, C.BRAID_BOBBIN, C.PTFE_TAPE),
           note="The same V at bench-roll size: solder off the reel, braid off the "
                "bobbin, tape off the roll."),
    Holder("reel-spacer", "spacer", 3, 3, 6,
           note="Drops into the reel cradle's trough beside a narrow reel and takes up "
                "its run. Print as many as the slack wants.",
           opts={"width": 20.0}),
    Holder("roll-spacer", "spacer", 2, 2, 5,
           note="The roll cradle's spacer.",
           opts={"width": 12.0}),
]


# ============================================================
# COMBS — tools that stand, held by a throat and a taper
# ============================================================

COMBS = [
    Holder("crimp-comb", "comb", 3, 2, 9,
           takes=(C.SN2549, C.HS9327, C.PRECIVA),
           note="The three ratcheting crimpers, head down. Each slot is cut to its own "
                "tool, so the SN-2549 does not rattle in a mouth sized for the Preciva."),
    Holder("strip-comb", "comb", 3, 3, 8,
           takes=(C.KLEIN_11063W, C.KLEIN_11057, C.VCE_GJ668BL),
           note="The two strippers and the modular crimper."),
    Holder("punch-comb", "comb", 2, 2, 8,
           takes=(C.KLEIN_VDV427, C.MASTERCOOL_70025),
           note="The punchdown and the capillary cutter — two tools whose makers publish "
                "between them one usable figure."),
    Holder("cut-comb", "comb", 2, 2, 7,
           takes=(C.KATA_CUTTER, C.KATA_CUTTER, C.MUDDER_CUTTER),
           note="Both flush cutters and the tube cutter."),
    Holder("fine-comb", "comb", 2, 1, 8,
           takes=(C.IFIXIT_TWEEZERS, C.IFIXIT_TWEEZERS, C.IFIXIT_TWEEZERS),
           note="The three iFixit tweezers, points down to the root of the taper.",
           opts={"root": 3.0, "taper": 10.0}),
    Holder("tube-comb", "comb", 3, 3, 9,
           takes=(C.KNIPEX_860180, C.RIDGID_150),
           note="The pliers wrench and the tubing cutter. KNIPEX publishes 180 x 46 x "
                "15 mm and RIDGID publishes a length, so one slot is cut to a drawing "
                "and the other to a parcel, 26 mm wider.")
]


# ============================================================
# INDEXES — a bore is cut to a size, so every figure is a standard's
# ============================================================

INDEXES = [
    Holder("tip-index", "index", 3, 2, 5,
           note="Twenty T18 soldering tips and the seven heat-set insert tips that "
                "share their barrel. One bore for all twenty-seven: the README's table "
                "is what tells them apart.",
           opts={"rows": [
               [(C.T18_TIP, 10)],
               [(C.T18_TIP, 10)],
               [(C.INSERT_TIP, 7)],
           ]}),
    Holder("drill-index", "index", 3, 3, 5,
           note="The drill-press station. Countersinks stand head down — a head is a "
                "nominal inch fraction — and everything else shank down.",
           opts={"rows": [
               [(C.COBALT_DRILL, 12)],
               [(C.PILOT_DRILL, 2), (C.TAP_GUIDE, 1)],
               [(C.NPT_TAP, 3)],
               [(cs, 1) for cs in C.COUNTERSINKS],
           ]}),
    Holder("dowel-index", "index", 2, 1, 5,
           note="Ten ground dowel pins, points up.",
           opts={"rows": [[(C.DOWEL_PIN, 5)], [(C.DOWEL_PIN, 5)]]}),
]


# ============================================================
# TUBS — everything loose, and everything that just stands
# ============================================================

TUBS = [
    Holder("m3-tub", "tub", 3, 2, None,
           takes=(C.M3X25, C.M3X12SS, C.M3X12, C.M3X10, C.M3X8),
           note="The five M3 lengths. The two M3 x 12 troughs are adjacent and their "
                "contents are not interchangeable: 304 SS closes the wet reservoir "
                "caps, black oxide bolts the dry above-counter plate.",
           opts={"length_div": 4}),
    Holder("m5-tub", "tub", 3, 2, None,
           takes=(C.M5X10, C.M5WASHER, C.RUTHEX_M5),
           note="The compressor floor stack.",
           opts={"length_div": 2}),
    Holder("insert-tub", "tub", 3, 1, None,
           takes=(C.RUTHEX_M3, C.RUTHEX_M3S, C.RUTHEX_M2),
           note="LABEL THIS ONE FIRST. The long and short M3 share a knurl and a hole "
                "and differ only in body length; pressed into the wrong station the "
                "short one is a weaker joint that looks identical.",
           opts={"length_div": 2}),
    Holder("small-tub", "tub", 3, 2, None,
           takes=(C.M2X6, C.ULPM3X6, C.ULPM3X8, C.MAGNETS, C.MEMBRANES),
           note="M2, the two ultra-low-profile M3 lengths, and the two that are not "
                "screws. The sixth compartment stands empty for whatever is in play.",
           opts={"length_div": 2, "width_div": 1}),

    Holder("ferrule-tub", "tub", 3, 3, None,
           takes=C.FERRULES,
           note="Six DIN 46228-4 cross-sections. The machine's largest conductor is "
                "16 AWG, so the kit's 4 mm2 and up stay in the kit's own case.",
           opts={"length_div": 2, "width_div": 1}),
    Holder("shrink-tub", "tub", 3, 3, None,
           takes=C.SHRINK,
           note="Eleven sizes of 2:1 sleeving decanted into six bands; a band's "
                "compartment is sized on the widest sleeve in it.",
           opts={"length_div": 2, "width_div": 1}),
    Holder("terminal-tub", "tub", 3, 3, None,
           takes=C.TERMINALS,
           note="Push-ons and rings, the single-gauge packs and the mixed kits decanted "
                "beside them.",
           opts={"length_div": 2, "width_div": 1}),
    Holder("lever-tub", "tub", 3, 1, None,
           takes=C.LEVERS,
           note="WAGO 221 in three widths.",
           opts={"length_div": 2}),
    Holder("tie-tub", "tub", 3, 2, None,
           takes=C.TIES,
           note="Zip ties in three lengths; the 6 in and 8 in lie doubled back.",
           opts={"length_div": 2}),

    Holder("xh-tub", "tub", 3, 3, None,
           takes=(C.XH_CONTACTS, C.XH_LEADS) + C.XH_HOUSINGS,
           note="The JST XH station: contacts, pre-crimped leads, and the seven pole "
                "counts. Every figure here is the XH series drawing's.",
           opts={"length_div": 2, "width_div": 2}),
    Holder("keystone-tub", "tub", 2, 2, None,
           takes=(C.RJ11_JACKS, C.RJ11_PLUGS),
           note="RJ11 6P4C jacks and plugs. 6P4C is a standard and the keystone form "
                "factor is a standard, so neither figure is a parcel's.",
           opts={"length_div": 1}),

    Holder("junction-tub", "tub", 3, 3, None,
           takes=(C.UNION_TEES, C.UNION_ELBOWS),
           note="Thirty union tees and forty union elbows, on John Guest's own drawings.",
           opts={"length_div": 1}),
    Holder("bulkhead-tub", "tub", 3, 3, None,
           takes=(C.BULKHEADS, C.NEOFIT_BULKHEADS, C.PURESEC_ELBOWS, C.BALL_VALVES),
           note="Everything that passes a wall, and the valves that sit in line with it.",
           opts={"length_div": 1, "width_div": 1}),
    Holder("adapter-tub", "tub", 3, 3, None,
           takes=(C.MALE_CONNECTORS, C.FEMALE_ADAPTERS, C.FLARE_ADAPTERS, C.PNEUMATIC),
           note="Thread to tube, in both directions.",
           opts={"length_div": 1, "width_div": 1}),
    Holder("npt-tub", "tub", 3, 3, None,
           takes=(C.CHECK_VALVES, C.COUPLINGS, C.BARBS, C.BRASS_FLARE),
           note="The NPT stock. The regulator and the relief valve stand in the "
                "pressure-tub beside it.",
           opts={"length_div": 1, "width_div": 1}),
    Holder("pressure-tub", "tub", 2, 2, None,
           takes=(C.REGULATOR, C.RELIEF_VALVE),
           note="The two bodies that stand on end.",
           opts={"length_div": 1}),
    Holder("stock-tub", "tub", 3, 3, None,
           takes=(C.TWO_WAY, C.CLAMPS, C.STIFFENERS),
           note="Dividers, clamps and stiffeners — the bulk of the tube bench.",
           opts={"length_div": 2}),
    Holder("copper-tub", "tub", 3, 1, None,
           takes=(C.FLARE_NUTS, C.SLIP_COUPLINGS),
           note="The flare nuts and slip couplings the copper bench works through.",
           opts={"length_div": 1}),
    Holder("service-tub", "tub", 3, 2, None,
           takes=(C.FILTER_DRIER, C.PIERCING_VALVE),
           note="The loop-service spare and one piercing valve per appliance, both "
                "standing.",
           opts={"length_div": 1}),

    Holder("flux-tub", "tub", 3, 3, None,
           takes=(C.FLUX_JAR, C.FLUX_BOTTLE, C.FLUX_SYRINGES),
           note="The wet end of the solder bench: the jar, the bottle and the four "
                "syringes, all standing. The fourth compartment takes whatever is open.",
           opts={"length_div": 1, "width_div": 1}),
    Holder("brush-quiver", "tub", 2, 2, None,
           takes=(C.FLUX_BRUSHES,),
           note="Thirty-six acid brushes standing. They come out of the flux tub "
                "because a 152 mm brush would put a 45 mm jar at the bottom of a "
                "158 mm well.",
           ),
    Holder("heat-gun-tub", "tub", 2, 2, None,
           takes=(C.HEAT_GUN,),
           note="The mini heat gun, nozzle down.",
           ),
    Holder("deburr-tub", "tub", 4, 1, None,
           takes=(C.NOGA,),
           note="The Noga NG8150, lying down.",
           ),
    Holder("saw-tub", "tub", 4, 2, None,
           takes=(C.HOLE_SAW_ARBOR, C.SPADE_BIT),
           note="The saw set lies down: the arbor's flange and the spade bit's paddle "
                "are both wider than their shanks, and a bore cut to a shank leaves the "
                "wide end to foul its neighbours. The bit is 6 in long, which is what "
                "makes this the one four-unit tub.",
           opts={"width_div": 1}),
    Holder("die-tub", "tub", 2, 2, None,
           takes=(C.NPT_DIE,),
           note="The 1-1/2 in round adjustable NPT die, lying flat.",
           ),

    Holder("hotend-tub", "tub", 3, 2, None,
           takes=(C.HOTEND_SOCKS, C.HOTENDS),
           note="The silicone socks, and the swap well a both-printer change pulls into.",
           opts={"length_div": 1}),
    Holder("depressor-quiver", "tub", 3, 2, None,
           takes=(C.DEPRESSORS,),
           note="A hundred 6 in depressors standing. A depressor is a standard size and "
                "the quiver is cut to the bundle.",
           ),
    Holder("pigment-tub", "tub", 2, 2, None,
           takes=(C.PIGMENT,),
           note="The silicone pigment. The two-part kits, the aerosols and the 32 oz "
                "cups all stand wider than a footprint and stay at the pour bench.",
           ),
]


HOLDERS = DOCKS + CRADLES + COMBS + INDEXES + TUBS


# ============================================================
# BUILD
# ============================================================

def build(holder):
    """Cut one holder and check it against everything it is said to take."""
    tall = holder.height_u if holder.height_u is not None else "?"
    print(f"\n{holder.name}  [{holder.shape}]  {holder.x_u}x{holder.y_u}x{tall}")
    opts = dict(holder.opts)

    if holder.shape == "dock":
        shape = H.dock(holder.x_u, holder.y_u)

    elif holder.shape == "tub":
        length_div = opts.get("length_div", 0)
        width_div = opts.get("width_div", 0)
        if holder.height_u is None:
            holder.height_u = H.tub_height_for(
                holder.x_u, holder.y_u, holder.takes, length_div, width_div
            )
            print(f"   {holder.name}: {holder.height_u} units deep, from its contents")
        shape = H.tub(holder.x_u, holder.y_u, holder.height_u, **opts)
        cells = (length_div + 1) * (width_div + 1)
        if len(holder.takes) > cells:
            raise ValueError(
                f"{holder.name}: {len(holder.takes)} things into {cells} compartments"
            )
        for env in holder.takes:
            check = H.assert_heap_fits if isinstance(env, Heap) else H.assert_tub_takes
            check(holder.name, env, holder.x_u, holder.y_u, holder.height_u,
                  length_div, width_div)

    elif holder.shape == "cradle":
        shape = H.cradle(holder.x_u, holder.y_u, holder.height_u)
        for env in holder.takes:
            H.assert_cradle_takes(holder.name, env, holder.x_u, holder.y_u, holder.height_u)

    elif holder.shape == "spacer":
        width = opts.pop("width")
        shape = H.spacer(width, holder.x_u, holder.y_u, holder.height_u)

    elif holder.shape == "comb":
        mouths = [H.slot_mouth_for(env) for env in holder.takes]
        shape, centers = H.comb(holder.x_u, holder.y_u, holder.height_u, mouths, **opts)
        for index, (env, mouth) in enumerate(zip(holder.takes, mouths)):
            gaps = [abs(centers[index] - other) for other in centers if other != centers[index]]
            neighbour = min(gaps) if gaps else H.comb_slot(
                holder.y_u, holder.height_u, mouth)[3]
            H.assert_comb_takes(holder.name, env, holder.y_u, holder.height_u,
                                mouth, neighbour, **opts)

    elif holder.shape == "index":
        shape, placed = H.index(holder.x_u, holder.y_u, holder.height_u, opts["rows"])
        seen = []
        for env, _x, _y, _d in placed:
            if env not in seen:
                seen.append(env)
        for env in seen:
            H.assert_index_holds(holder.name, env, holder.height_u)

    else:
        raise ValueError(f"{holder.name}: {holder.shape} is not a holder shape")

    H.assert_printable(holder.name, shape)
    if holder.shape not in ("spacer", "dock"):
        H.assert_docks(holder.name, H.dock(holder.x_u, holder.y_u), shape)
    return shape


def sizes():
    """Every tub's derived depth, without cutting a body: the fast loop while a pack
    count or a footprint is being settled."""
    for holder in HOLDERS:
        if holder.shape != "tub":
            continue
        opts = holder.opts
        height_u = holder.height_u or H.tub_height_for(
            holder.x_u, holder.y_u, holder.takes,
            opts.get("length_div", 0), opts.get("width_div", 0),
        )
        clear = H.tub_holds(holder.x_u, holder.y_u, height_u,
                            opts.get("length_div", 0), opts.get("width_div", 0))
        print(f"{holder.name:20s} {holder.x_u}x{holder.y_u}x{height_u:<3d} "
              f"{height_u * 7:5.0f} mm tall   cell "
              f"{clear[0]:5.1f} x {clear[1]:5.1f} x {clear[2]:5.1f}   "
              f"{len(holder.takes)} of {(opts.get('length_div', 0) + 1) * (opts.get('width_div', 0) + 1)}")


def cradle_witness(holder, shape, diameters):
    """The cradle with reels of several diameters lying in it, as one assembly.

    The claim a cradle makes is that it holds a reel at any radius without being told the
    radius. A picture of one reel does not show that; a picture of three does. The reels
    are witnesses and are not printed — each is placed by the geometry of a cylinder
    resting in a V, which is the same arithmetic the trough is cut by.
    """
    mouth, depth, run = H.cradle_trough(holder.x_u, holder.y_u, holder.height_u)
    top_z = _kit.top_reference_z(holder.height_u)

    assembly = cq.Assembly(name=f"{holder.name}-witness")
    assembly.add(shape, name=holder.name, color=_kit.kit_color)
    width = run / (len(diameters) + 1)
    for index, diameter in enumerate(diameters):
        radius = diameter / 2.0
        center_z = top_z + H.cradle_seat(mouth, depth, diameter)
        x = -run / 2.0 + width * (index + 1)
        reel = (
            cq.Workplane("YZ")
            .circle(radius)
            .extrude(width * 0.35, both=True)
            .translate((x, 0.0, center_z))
        )
        assembly.add(reel, name=f"reel-{diameter:.0f}",
                     color=cq.Color(0.80, 0.81, 0.83))
    return assembly


def figures():
    """The figures this directory's README carries, keyed by its `[value](NAME)` names."""
    marks = {
        "HOLDER_COUNT": str(len(HOLDERS)),
        "GRID": f"{_kit.grid_unit:.0f} mm x {_kit.grid_unit:.0f} mm x {_kit.height_unit:.0f} mm",
        "H2C_ENVELOPE": f"{_kit.h2c_build_x:.0f} x {_kit.h2c_build_y:.0f} x {_kit.h2c_build_z:.0f} mm",
        "TROUGH": "{:.0f} mm x {:.0f} mm".format(*H.cradle_trough(3, 3, 6)[:2]),
        "ROLL_TROUGH": "{:.0f} mm x {:.0f} mm".format(*H.cradle_trough(2, 2, 5)[:2]),
        "SLOT_ROOT": f"{H.slot_root:.0f} mm",
        "SLOT_TAPER": f"{H.slot_taper:.0f} mm",
        "SLOT_CLEAR": "2 mm",
        "BORE_SLIP": f"{H.slip:.1f} mm",
        "WALL": f"{H.wall:.0f} mm",
        "LABEL_TAPE": f"{_kit.label_tape_width:.0f} mm",
    }
    for holder in HOLDERS:
        key = holder.name.upper().replace("-", "_")
        marks[f"{key}_SIZE"] = (
            f"{holder.x_u} x {holder.y_u}"
            if holder.shape in ("dock", "spacer")
            else f"{holder.x_u} x {holder.y_u} x {holder.height_u}"
        )
    return marks


def parcels():
    """Every slot whose width rests on a parcel, and what a caliper would buy.

    A comb sizes each slot to the thinnest side of its tool's parcel, which is honest —
    the tool is certainly no thicker than that — and loose by however much the box was
    oversized. A loose tool leans; `assert_comb_takes` holds the lean inside the slot's
    own share of the block, so nothing here is unsafe. It is just slack, and one measured
    figure per line closes it.
    """
    print("Slots cut to a parcel. One caliper reading each closes the slack:\n")
    print(f"{'holder':<13}{'tool':<46}{'mouth':>6}{'known':>9}   source")
    for holder in COMBS:
        for env in dict.fromkeys(holder.takes):
            thin = "xyz"[min(range(3), key=lambda i: (env.x, env.y, env.z)[i])]
            if env.reading(thin) == EXACT:
                continue
            print(f"{holder.name:<13}{env.name[:44]:<46}{H.slot_mouth_for(env):5.1f} "
                  f"{env.thinnest:8.1f}-   {env.source}")


def main():
    out_dir.mkdir(exist_ok=True)
    shapes = {}
    for holder in HOLDERS:
        shapes[holder.name] = build(holder)
    print()
    _kit.export_parts(out_dir, shapes)
    reel = next(h for h in HOLDERS if h.name == "reel-cradle")
    _kit.export_assembly_step(
        out_dir,
        "reel-cradle-witness",
        cradle_witness(reel, shapes[reel.name], (40.0, 72.0, 110.0)),
    )
    _kit.substitute_md(here / "README.md", variables=figures())
    print(f"\n{len(shapes)} holders")


if __name__ == "__main__":
    if "--sizes" in sys.argv:
        sizes()
    elif "--parcels" in sys.argv:
        parcels()
    else:
        main()
