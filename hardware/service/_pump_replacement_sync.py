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
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "tee-carrier"))
sys.path.insert(0, str(_hw / "printed-parts" / "enclosure" / "enclosure"))
sys.path.insert(0, str(_hw / "manifold-layout"))

import _facts                                          # noqa: E402  — the placed pack, off the last build
import _routing as R                                   # noqa: E402  — the stock every run is drawn on
import _scorecard as _sc                               # noqa: E402  — what fastens each body
import manifold_layout as _ml                          # noqa: E402  — the segment and mouth tables
import pump_tray as _tray                              # noqa: E402  — the clamp collar the boss lifts out of
import tee_carrier as _carrier                         # noqa: E402  — the moving tees, tabs and locks
import enclosure as _enc                               # noqa: E402  — the cradle, top clamp and screws
from _cold_core_interface import cap_cradles           # noqa: E402  — the valves the core's lid holds

from docgen import substitute_md                       # noqa: E402

#: The piece a pump swap draws out of the front bay. Everything standing on its deck rides out.
RIDES_OUT = "enclosure-pump-cartridge"

#: The piece the bay is cut in, and the one that keeps the manifold: its two valve panels seat
#: eight of the ten valves and its integral collet plate releases the cartridge.
BAY = "enclosure-front-top"

#: The four the plate opens. Derived below twice — once off what holds each body and once off
#: what the printed collet plate is bored for — and checked against this, so the doc's own table and the
#: machine cannot drift apart in silence.
EXPECTED = ("fluid-11", "fluid-12", "fluid-21", "fluid-22")


def holder(name: str, decked: frozenset):
    """The enclosure piece that holds one body, through whatever it rides.

    A pump's bracket bears in the cartridge's lower cradle, and `_facts.pump_trays` records the
    conformal clamp collar found on each boss — so a head in that table is held by the piece
    that rides out and by nothing the box screws down. A tee without a direct carrier row
    inherits the fixed valve and construction named by `_scorecard.TEE_LANDS`: the inner pair
    still butt, while the four pump-barb tees land through bowed flex stubs."""
    if name in decked:
        return RIDES_OUT
    by = _sc.fastened_by(name)
    if by is not None:
        return by
    if name in _sc.TEE_LANDS:
        return holder(_sc.TEE_LANDS[name][0], decked)
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
    """The same question asked of the collet passages rather than of the pieces.

    `enclosure_assembly.collet_plate_spec` strikes one hole per `manifold_layout.BARB_OF` tee,
    so the connections `SEGMENTS` draws on a barb ARE the ones the plate is bored to release."""
    return tuple(sorted(f"fluid-{cid}" for cid, _f, _t, how in _ml.SEGMENTS
                        if how in _ml.BARB_OF))


def state_text(value: float) -> str:
    """One carrier offset as the service prose prints it: signed except at the zero datum."""
    if abs(value) < 1e-9:
        return "0"
    return f"{value:+g}".replace("-", "−")


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
            f"`TEE_LANDS` say which. The doc's joint table and its step 2 both name these by "
            f"hand and have to move with it.")
    if found != bored():
        raise ValueError(
            f"the cartridge takes {found} across the bay's mouth and the collet plate is bored "
            f"for {bored()} — `manifold_layout.BARB_OF` and the pieces that hold the pack no "
            f"longer name one joint set. A tube with no hole in front of it is one the pull "
            f"tears out, and a hole with no tube in it is a joint nothing releases.")

    # The release feature's planes belong to the Box; it is not a separate assembly body.
    plate = f.box.collet_plate
    rest_gap = plate["rest_gap"]

    valves = [n for n in f.manifold_bodies if n.startswith("valve-v-")]
    # Each released tube's own exposed length, barb plane to branch collet face. That gap is
    # `manifold_layout.BARB_STANDOFF` is its fore/aft projection.
    berth = {cid: _ml.dist(*_ml.RUNS[how]) for cid, _f, _t, how in _ml.SEGMENTS
             if how in _ml.BARB_OF}

    # THE MECHANISM THAT STAYS IN FRONT-TOP. Keep the service card tied to the same connector
    # measurements, carrier mounts and printed-part inventory as the enclosure. The generated
    # enclosure facts can lag a source edit until the next full CAD publish, so this small sync
    # reads those source interfaces directly and refuses to bless a half-integrated carrier.
    states = _ml.tee.CARRIER_STATES
    if tuple(states) != ("release", "squeeze", "connected", "park"):
        raise ValueError(f"tee-carrier states are not in service order: {tuple(states)}")
    carrier_tees = tuple(sorted(_ml.CARRIER_TEES))
    mounted_carrier_tees = tuple(sorted(
        name[len("tee-"):].upper()
        for name, by, joint in _sc.MOUNTS
        if by == "enclosure-tee-carrier" and joint == "tie-capture"
    ))
    if mounted_carrier_tees != carrier_tees:
        raise ValueError(
            f"manifold_layout carries {carrier_tees}, but the carrier's tie-capture mounts are "
            f"{mounted_carrier_tees}")
    carrier_interface = _carrier.interface()
    printed = carrier_interface["printed_parts"]
    tabs = tuple(name for name in printed if "-tab-" in name and "-tab-lock-" not in name)
    locks = tuple(name for name in printed if "-tab-lock-" in name)
    springs = tuple(name for name, _by, _joint in _sc.MOUNTS
                    if name.startswith("tee-carrier-spring-"))
    tie_sites = carrier_interface["tie_sites"]
    if len(tie_sites) % len(carrier_tees):
        raise ValueError(
            f"the carrier has {len(tie_sites)} tie sites for {len(carrier_tees)} tees")
    bowed = tuple(cid for cid, frm, to, how in _ml.SEGMENTS
                  if how.startswith("fore-y-")
                  and {frm.rsplit("-", 1)[0], to.rsplit("-", 1)[0]} & set(carrier_tees))
    hairpins = tuple(cid for cid, frm, to, how in _ml.SEGMENTS
                    if how == "spine"
                    and {frm.rsplit("-", 1)[0], to.rsplit("-", 1)[0]} & set(carrier_tees))
    if not (len(carrier_tees) == len(bowed) == len(hairpins) == len(found)):
        raise ValueError(
            "the cartridge joints, carried tees, bowed stubs and moving hairpin ends no "
            f"longer form four matching paths: joints={found}, tees={carrier_tees}, "
            f"bows={bowed}, hairpins={hairpins}")

    variables = {
        # What rides out of the bay and what the box keeps. All four counts come off the same
        # fastening rows the card reads, so a body that moves seat moves one and the rest.
        "CART_PUMPS":   f"{len(decked)}",
        "TRAY_VALVES": f"{sum(1 for n in valves if holder(n, decked) == BAY)}",
        "CAP_VALVES":   f"{len(cap_cradles)}",
        "BOX_TEES":     f"{sum(1 for n in _sc.TEE_LANDS if holder(n, decked) != RIDES_OUT)}",
        "CARRIER_TEES": f"{len(carrier_tees)}",
        "BOWED_STUBS":  f"{len(bowed)}",
        "MOVING_HAIRPINS": f"{len(hairpins)}",
        "TIES_PER_TEE": f"{len(tie_sites) // len(carrier_tees)}",
        "SPRING_COUNT": f"{len(springs)}",
        "TAB_COUNT":    f"{len(tabs)}",
        "TAB_LOCK_COUNT": f"{len(locks)}",
        # The doc names this count in four places — the opening, the heading, the pull and the
        # output condition — and `docgen` keys a text by its own name, so a count standing more
        # than once stands under a suffix per standing.
        **{f"JOINT_COUNT{s}": f"{len(found)}" for s in ("", "_2", "_3", "_4")},
        # Each released joint's own exposed tube, at the precision the pack was drawn at.
        **{f"LEN_{cid}": f"{v:.1f}" for cid, v in berth.items()},
        # The integral release face's dimensions and nose air.
        "PLATE_SPAN": f"{plate['x1'] - plate['x0']:.4g}",
        "PLATE_T":    f"{plate['aft_y'] - plate['fore_y']:.4g}",
        "REST_GAP":   f"{rest_gap:.4g}",
        # The tee's release stroke and what stands between its body and the wall at rest, off
        # the same plate figures and the tee reference's own calipered sleeve travel.
        "STROKE":     f"{plate['stroke']:.4g}",
        "SLEEVE_TRAVEL": f"{(plate['stroke'] - rest_gap):.4g}",
        "BODY_AIR":   f"{(plate['aft_y'] + rest_gap + _ml.tee.BRANCH_REACH - _ml.tee.HALF_W
                          - plate['stroke'] - plate['wall_aft_y']):.4g}",
        "TUBE_OD":    f"{od:.4g} mm",
        # Four service states: offsets are enclosure +Y (aft) from the squeeze datum. Tube
        # depth is the measured connector coordinate; squeeze bottoms at 10 mm, connected
        # floats at the 8.5 mm first-grip depth, and empty park is beyond the 7 mm first
        # resistance station.
        **{f"{name.upper()}_OFFSET": state_text(offset)
           for name, (offset, _depth) in states.items()},
        "SQUEEZE_DEPTH": f"{states['squeeze'][1]:g}",
        "CONNECTED_DEPTH": f"{states['connected'][1]:g}",
        "PARK_DEPTH": f"{states['park'][1]:g}",
        "CONNECTED_RELEASE_TRAVEL":
            f"{states['connected'][0] - states['release'][0]:g}",
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
