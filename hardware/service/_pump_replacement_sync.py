"""Doc-sync driver for hardware/service/pump-replacement.md.

Run: tools/cad-venv/bin/python hardware/service/_pump_replacement_sync.py

The joint table in that doc is DERIVED, not typed. Which bodies ride `enclosure-front-top` comes
off `_scorecard`'s own fastening rows, and which connections part comes off `manifold_layout`'s
segment and mouth tables read against them. A valve re-seated onto the cold core's lid, a panel
that loses a station, a tee that reroutes onto a different butt — each moves the set, and `main`
raises rather than writing a doc that sends a service bench to the wrong eight collets.
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
_hw = next(p for p in _here.parents if p.name == "hardware")
_root = _hw.parent

sys.path.insert(0, str(_hw / "scripts"))
sys.path.insert(0, str(_root / "tools"))
sys.path.insert(0, str(_hw / "printed-parts" / "cadlib"))
sys.path.insert(0, str(_hw / "printed-parts" / "cold-core"))
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "pump-tray"))
sys.path.insert(0, str(_hw / "manifold-layout"))

import _facts                                          # noqa: E402  — the placed pack, off the last build
import _routing as R                                   # noqa: E402  — the stock every run is drawn on
import _scorecard as _sc                               # noqa: E402  — what fastens each body
import manifold_layout as _ml                          # noqa: E402  — the segment and mouth tables
import pump_tray as _tray                              # noqa: E402  — the bore the boss lifts out of
from _cold_core_interface import cap_cradles           # noqa: E402  — the valves the core's lid holds

from docgen import substitute_md                       # noqa: E402

#: The piece a pump swap takes off. Everything it fastens rides up with it.
LIFTS = "enclosure-front-top"

#: 1/4" OD LLDPE's INSIDE diameter is stated nowhere in this tree — `_routing.STOCKS` carries the
#: outside diameter and the bend floor, which is what a routed run needs. This is the nominal bore
#: for the reel the BOM buys, and every millilitre below is arithmetic on it rather than a reading.
#: Measure a reel and this becomes a figure like any other.
NOMINAL_BORE = 0.170 * 25.4

#: The eight the procedure breaks. Derived below and checked against this, so the doc's own table
#: and the machine cannot drift apart in silence.
EXPECTED = ("fluid-3", "fluid-5", "fluid-14", "fluid-16",
            "fluid-18", "fluid-24", "fluid-26", "fluid-28")


def holder(name: str):
    """The enclosure piece that fastens one body, through whatever it rides.

    A tee is fastened by nothing of its own: its collets make up onto a valve's, face to face on
    one stub, so what holds it is the seat under the valve it butts (`_scorecard.TEE_BUTTS`)."""
    by = _sc.fastened_by(name)
    if by is not None:
        return by
    if name in _sc.TEE_BUTTS:
        return holder(_sc.TEE_BUTTS[name])
    return None


def lifts(tag: str) -> bool:
    """Whether the body one `SEGMENTS` endpoint stands on rides the quadrant.

    A pump barb is not a body — the head under it is, and the tray in the quadrant's ceiling is
    what that head hangs in."""
    name = f"pump-{tag[-1].lower()}-head" if tag.startswith("P-") else _ml.body_name(tag)
    return holder(name) == LIFTS


def parting() -> tuple:
    """Every connection with one end on a body that rides and one on a body that stays.

    Two tables answer it together. `SEGMENTS` carries what the pack joins to itself, and a
    connection in it parts when its two endpoints land on different sides of the seam.
    `MOUTHS` carries what leaves the pack, and one of those parts when its pack end rides — the
    body at the far end is a bulkhead, a cap conduit or a lid-cradled valve, none of which move."""
    out = []
    for cid, frm, to, _how in _ml.SEGMENTS:
        a, b = frm.rsplit("-", 1)[0], to.rsplit("-", 1)[0]
        if lifts(a) != lifts(b):
            out.append(f"fluid-{cid}")
    out += [cid for cid, p, _what, _pos, _axis in _ml.MOUTHS
            if lifts(p.rsplit("-", 1)[0])]
    return tuple(sorted(out))


def main():
    f = _facts.read()
    runs = {r.id: r for r in f.runs}
    od = R.stock_of("fluid", 6.35).od

    found = parting()
    if found != tuple(sorted(EXPECTED)):
        raise ValueError(
            f"the joints a quadrant lift parts are {found}, and pump-replacement.md is written "
            f"for {tuple(sorted(EXPECTED))}. A valve, tee or pump has changed which side of the "
            f"seam holds it — `_scorecard.MOUNTS` / `cap_cradles` / `TEE_BUTTS` say which. The "
            f"doc's joint table and its step 3 both name these by hand and have to move with it.")

    # The two source connections are the pack's own quarter turn plus the step that carries the
    # valve toward the core's crown — `manifold_layout` sweeps them rather than `_lines`, so
    # neither is a run and the length is the two arcs added up.
    src_len = {cid: _ml.QUARTER_LEN + _ml.source_step(v)[2] for cid, v in _ml.SBENDS.items()}

    def crest(body: str) -> float:
        """The top of a run's centreline, off the swept solid's own box. A tube's box stands one
        radius over its centreline where the path is level, which is what a crest is."""
        return f.bodies[body][5] - od / 2.0

    def mL(length: float) -> float:
        return 3.141592653589793 * NOMINAL_BORE ** 2 / 4.0 * length / 1000.0

    lengths = {"LEN_3": src_len[3], "LEN_5": src_len[5],
               **{f"LEN_{n}": runs[f"fluid-{n}"].length for n in (14, 16, 18, 24, 26, 28)}}

    draw_crest, core_crown = crest("tube-fluid-16"), f.bodies["foam-assembly"][5]
    valves = [n for n in f.manifold_bodies if n.startswith("valve-v-")]

    variables = {
        # What the ceiling carries away and what the core's lid keeps. Both counts come off the
        # same fastening rows the card reads, so a valve that moves seat moves one and the other.
        "LIFT_VALVES": f"{sum(1 for n in valves if holder(n) == LIFTS)}",
        "CAP_VALVES":  f"{len(cap_cradles)}",
        "LIFT_TEES":   f"{sum(1 for n in _sc.TEE_BUTTS if holder(n) == LIFTS)}",
        # The doc names this count in seven places — the heading, the lift, step 3, the reassembly,
        # the output condition and the bore note — and `docgen` keys a text by its own name, so a
        # count standing more than once stands under a suffix per standing.
        **{f"JOINT_COUNT{s}": f"{len(found)}"
           for s in ("", "_2", "_3", "_4", "_5", "_6", "_7")},
        # Each broken joint's own tube, at the precision the runs were drawn at.
        **{k: f"{v:.1f}" for k, v in lengths.items()},
        # The two crests that decide what a broken joint lets go of. `fluid-3`'s is between its
        # own two ends, so the run drains both ways off it; the draw lines' stands over the whole
        # cold core, so no level inside one reaches it.
        "SOURCE_CREST":   f"{crest('step-fluid-3'):.1f}",
        "DRAW_CREST":     f"{draw_crest:.1f}",
        "CORE_CROWN":     f"{core_crown:.1f}",
        "SIPHON_MARGIN":  f"{draw_crest - core_crown:.1f}",
        # The stock, and the arithmetic the nominal bore allows on it.
        "TUBE_OD":     f"{od:.4g} mm",
        "JOINT_ML":    f"{mL(sum(lengths.values())):.0f}",
        "WET_ML":      f"{mL(lengths['LEN_3']):.1f}",
        # The socket the boss lifts out of, off the module that draws the tray. `internal-plumbing`
        # quotes the same figure for putting a pump in.
        "PUMP_SOCKET": f"{2 * _tray.boss_half:.4g} mm",
    }

    substitute_md(_here / "pump-replacement.md", variables=variables)
    print("-> pump-replacement.md")
    print(f"   {len(found)} joints part: {', '.join(found)}")
    print(f"   {variables['LIFT_VALVES']} valves + {variables['LIFT_TEES']} tees ride "
          f"{LIFTS}; {variables['CAP_VALVES']} valves stay on the core's lid")


if __name__ == "__main__":
    main()
