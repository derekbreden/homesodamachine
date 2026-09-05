"""Doc-sync driver for hardware/service/pump-replacement.md.

Run: tools/cad-venv/bin/python hardware/service/_pump_replacement_sync.py

The joint table in that doc is DERIVED, not typed. What leaves the box on the pump cartridge
comes off `_facts`' own tray seats read against `_scorecard`'s fastening rows, and which
connections part comes off `manifold_layout`'s segment and mouth tables read against both. A
pump that changes seat, a tee that reroutes onto another barb, a mouth that lands on a body the
deck carries — each moves the set, and `main` raises rather than writing a doc that sends a
service bench to the wrong collets.
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
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_hw / "manifold-layout"))

import _facts                                          # noqa: E402  — the placed pack, off the last build
import _routing as R                                   # noqa: E402  — the stock every run is drawn on
import _scorecard as _sc                               # noqa: E402  — what fastens each body
import manifold_layout as _ml                          # noqa: E402  — the segment and mouth tables
import pump_tray as _tray                              # noqa: E402  — the clamp collar the boss lifts out of
import enclosure as _enc                               # noqa: E402  — the cradle, top clamp and screws
from _cold_core_interface import cap_cradles           # noqa: E402  — the valves the core's lid holds

from docgen import substitute_md                       # noqa: E402

#: The piece a pump swap draws out of the front bay. Everything standing on its deck rides out.
RIDES_OUT = "enclosure-pump-cartridge"

#: The piece the bay is cut in, and the one that keeps the manifold: its two valve panels seat
#: eight of the ten valves and its side walls pocket the printed release face the cartridge releases against.
BAY = "enclosure-front-top"

#: The four the plate opens. Derived below twice — once off what holds each body and once off
#: what the printed release face is bored for — and checked against this, so the doc's own table and the
#: machine cannot drift apart in silence.
EXPECTED = ("fluid-11", "fluid-12", "fluid-21", "fluid-22")


def holder(name: str, decked: frozenset):
    """The enclosure piece that holds one body, through whatever it rides.

    A pump's bracket bears in the cartridge's lower cradle, and `_facts.pump_trays` records the
    conformal clamp collar found on each boss — so a head in that table is held by the piece
    that rides out and by nothing the box screws down. A tee is fastened by nothing of
    its own: its collets make up onto a valve's, face to face on one stub, so what holds it is
    the seat under the valve it butts (`_scorecard.TEE_BUTTS`)."""
    if name in decked:
        return RIDES_OUT
    by = _sc.fastened_by(name)
    if by is not None:
        return by
    if name in _sc.TEE_BUTTS:
        return holder(_sc.TEE_BUTTS[name], decked)
    return None


def rides(tag: str, decked: frozenset) -> bool:
    """Whether the body one `SEGMENTS` endpoint stands on leaves the box on the cartridge.

    A pump barb is not a body — the head under it is, and its bracket bears in the cartridge's
    lower cradle."""
    name = f"pump-{tag[-1].lower()}-head" if tag.startswith("P-") else _ml.body_name(tag)
    return holder(name, decked) == RIDES_OUT


def parting(decked: frozenset) -> tuple:
    """Every connection with one end on a body that rides out and one on a body the box keeps.

    Two tables answer it together. `SEGMENTS` carries what the pack joins to itself, and a
    connection in it parts when its two endpoints land on different sides of the bay's mouth.
    `MOUTHS` carries what leaves the pack, and one of those parts when its pack end rides — the
    body at the far end is a bulkhead, a cap conduit or a lid-cradled valve, none of which move."""
    out = []
    for cid, frm, to, _how in _ml.SEGMENTS:
        a, b = frm.rsplit("-", 1)[0], to.rsplit("-", 1)[0]
        if rides(a, decked) != rides(b, decked):
            out.append(f"fluid-{cid}")
    out += [cid for cid, p, _what, _pos, _axis in _ml.MOUTHS
            if rides(p.rsplit("-", 1)[0], decked)]
    return tuple(sorted(out))


def bored() -> tuple:
    """The same question asked of the printed release face rather than of the pieces.

    `enclosure_assembly.collet_plate_spec` strikes one hole per `manifold_layout.BARB_OF` tee,
    so the connections `SEGMENTS` draws on a barb ARE the ones the plate is bored to release."""
    return tuple(sorted(f"fluid-{cid}" for cid, _f, _t, how in _ml.SEGMENTS
                        if how in _ml.BARB_OF))


def main():
    f = _facts.read()
    od = R.stock_of("fluid", 6.35).od
    # THE BODIES THE CRADLE CARRIES, off the last build rather than named here.
    # `_facts.pump_trays` is `enclosure_assembly.pump_tray_plans` written down — one row per
    # head the machine found in a conformal clamp collar.
    decked = frozenset(f.pump_trays)

    found = parting(decked)
    if found != tuple(sorted(EXPECTED)):
        raise ValueError(
            f"the joints a cartridge pull parts are {found}, and pump-replacement.md is "
            f"written for {tuple(sorted(EXPECTED))}. A pump, valve or tee has changed which "
            f"side of the bay's mouth holds it — `_facts.pump_trays`, `_scorecard.MOUNTS` and "
            f"`TEE_BUTTS` say which. The doc's joint table and its step 2 both name these by "
            f"hand and have to move with it.")
    if found != bored():
        raise ValueError(
            f"the cartridge takes {found} across the bay's mouth and the collet plate is bored "
            f"for {bored()} — `manifold_layout.BARB_OF` and the pieces that hold the pack no "
            f"longer name one joint set. A tube with no hole in front of it is one the pull "
            f"tears out, and a hole with no tube in it is a joint nothing releases.")

    # HOW THE BERTH IS SPENT, off the placed bodies rather than off the constants that drew
    # them. The plate presses one plane — `enclosure_assembly.collet_plate_spec` raises unless
    # all four branch collets stand on it — so Y is the printed release face's own axis and each released
    # tube's exposed run lies along it, from the barb plane at one end to the branch collet
    # face at the other. What is left either side of the plate is the air off the barbs and the
    # nose air the tee closes before it lands, and a joint the printed release face does not stand in reads one
    # of them negative.
    spec = f.box.collet_plate
    plate = (spec["x0"], spec["fore_y"], spec["z0"],
             spec["x1"], spec["aft_y"], spec["z1"])
    airs = set()
    for rid in found:
        lo, hi = f.bodies[f"tube-{rid}"][1], f.bodies[f"tube-{rid}"][4]
        airs.add((round(plate[1] - lo, 6), round(hi - plate[4], 6)))
    if len(airs) != 1 or min(min(a) for a in airs) <= 0.0:
        raise ValueError(
            f"the four released tubes stand off the printed release face by {sorted(airs)} (barb air, nose "
            f"air) — one plate presses one plane, and a joint whose tube the plate is not in "
            f"the berth of drags its tee against nothing when the cartridge is pulled.")
    barb_air, rest_gap = airs.pop()

    valves = [n for n in f.manifold_bodies if n.startswith("valve-v-")]
    # Each released tube's own exposed length, barb plane to branch collet face. That gap is
    # `manifold_layout.BARB_STANDOFF`, opened for the printed release face and spent on it.
    berth = {cid: _ml.dist(*_ml.RUNS[how]) for cid, _f, _t, how in _ml.SEGMENTS
             if how in _ml.BARB_OF}

    variables = {
        # What rides out of the bay and what the box keeps. All four counts come off the same
        # fastening rows the card reads, so a body that moves seat moves one and the rest.
        "CART_PUMPS":   f"{len(decked)}",
        "TRAY_VALVES": f"{sum(1 for n in valves if holder(n, decked) == BAY)}",
        "CAP_VALVES":   f"{len(cap_cradles)}",
        "BOX_TEES":     f"{sum(1 for n in _sc.TEE_BUTTS if holder(n, decked) != RIDES_OUT)}",
        # The doc names this count in four places — the opening, the heading, the pull and the
        # output condition — and `docgen` keys a text by its own name, so a count standing more
        # than once stands under a suffix per standing.
        **{f"JOINT_COUNT{s}": f"{len(found)}" for s in ("", "_2", "_3", "_4")},
        # Each released joint's own exposed tube, at the precision the pack was drawn at.
        **{f"LEN_{cid}": f"{v:.1f}" for cid, v in berth.items()},
        # THE PRINTED RELEASE FACE, and the three ways the berth around it is spent: the air that
        # keeps it off the barbs, its own section, and the nose air the tees close before they
        # land. All three off the plate's placed box and the tubes it passes.
        "PLATE_SPAN": f"{plate[3] - plate[0]:.4g}",
        "COLLET_PLATE_T":    f"{plate[4] - plate[1]:.4g} mm",
        "BARB_AIR":   f"{barb_air:.4g}",
        "REST_GAP":   f"{rest_gap:.4g}",
        "TUBE_OD":    f"{od:.4g} mm",
        # The collar the boss lifts out of, off the module that draws the clamp. `internal-plumbing`
        # quotes the same figure for putting a pump in.
        "PUMP_SOCKET": f"{2 * _tray.boss_half:.4g} mm",
        # THE TOP CLAMP AND THE SCREWS THAT HOLD IT, the joint a swap opens before a pump is
        # reachable at all. Counted off the module that cuts both the clearance bores and the
        # heat-set seats, so a screw added there is a screw this procedure names.
        "CAP_SCREWS": f"{len(_enc.cap_screw_ys(f.box.inner, f.box.collet_plate))}",
        "CAP_SCREW_LEN": f"{_enc.screw_len:.4g}",
    }

    substitute_md(_here / "pump-replacement.md", variables=variables)
    print("-> pump-replacement.md")
    print(f"   {len(found)} joints part: {', '.join(found)}")
    print(f"   {variables['CART_PUMPS']} pumps ride {RIDES_OUT}; "
          f"{variables['TRAY_VALVES']} valves + {variables['BOX_TEES']} tees stay on {BAY}, "
          f"{variables['CAP_VALVES']} valves on the core's lid")


if __name__ == "__main__":
    main()
