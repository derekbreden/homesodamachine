"""Derive the joint and prepared-pump figures in pump-replacement.md.

Run: tools/cad-venv/bin/python hardware/service/_pump_replacement_sync.py

The separating joints come from the manifold topology and the bodies the cartridge
carries. Tee count, prepared-tube lengths and seating geometry come from the same
declared dock that builds the enclosure; this driver does not build another appliance.
"""

import sys
from functools import cache
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
import _scorecard as _sc                               # noqa: E402  — what fastens each body
import manifold_layout as _ml                          # noqa: E402  — the segment and mouth tables
import enclosure as _enc                               # noqa: E402  — the cradle, top clamp and screws
from _cold_core_interface import cap_cradles           # noqa: E402  — the valves the core's lid holds

from docgen import substitute_md                       # noqa: E402

#: The piece a pump swap draws out of the front bay. Everything standing on its deck rides out.
RIDES_OUT = "enclosure-pump-cartridge"

#: The bay wall and its two valve trays keep the stationary flavor manifold.
BAY = "enclosure-front-top"

#: The four joints the collet plate releases: each prepared pump tube in its pump tee.
EXPECTED = ("fluid-11", "fluid-12", "fluid-21", "fluid-22")


@cache
def _fastening_by_body():
    return {name: by for name, by, _joint in _sc.mounts()}


def holder(name: str, decked: frozenset):
    """The enclosure piece holding a body, including its fixed host.

    Pump heads ride the cartridge. Each pump tee stands in its bore through front-top's
    tee wall; each source tee inherits the valve in `TEE_LANDS`.
    """
    if name in decked:
        return RIDES_OUT
    by = _fastening_by_body()[_sc.RIDES.get(name, name)]
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


def collet_joints() -> tuple:
    """Pump branches served by the four pump tees' branch collets."""
    return tuple(sorted(f"fluid-{cid}" for cid, _f, _t, how in _ml.SEGMENTS
                        if how in _ml.BARB_OF))


def main():
    f = _facts.read()
    decked = frozenset(f.pump_trays)
    found = parting(decked)
    if found != tuple(sorted(EXPECTED)) or found != collet_joints():
        raise ValueError(
            f"cartridge joints {found}, tee collets {collet_joints()}, and the service "
            f"table {tuple(sorted(EXPECTED))} must identify the same connections")

    plate = f.box["collet_plate"]
    valves = [n for n in f.manifold_bodies if n.startswith("valve-v-")]
    variables = {
        "JOINT_COUNT": f"{len(found)}",
        "CART_PUMPS": f"{len(decked)}",
        # One pump tee in the tee wall behind each collet-plate hole.
        "PUMP_TEES": f"{len(plate['holes'])}",
        # Each mating part carries its own half of the magnet pairs.
        "CART_MAGNETS": f"{_enc._retention.MAGNETS_PER_HALF}",
        "TRAY_VALVES": f"{sum(1 for n in valves if holder(n, decked) == BAY)}",
        "CAP_VALVES": f"{len(cap_cradles)}",
        "BOX_TEES": f"{sum(holder(_ml.body_name(n), decked) != RIDES_OUT for n in _ml.PURCHASED_TEES)}",
        "TUBE_OD": f"{_ml.TUBE_D:.4g} mm",
        "TEE_STROKE": f"{_enc._dock.tee.BRANCH_COLLET_TRAVEL:.3g} mm",
        "TUBE_CUT": f"{_ml.PUMP_TUBE_CUT:.3g} mm",
        "TUBE_HELD": f"{_ml.PUMP_TUBE_HELD:.5g} mm",
        "TUBE_PROJECTION": f"{_ml.PUMP_TUBE_PROJECTION:.6g} mm",
        "TIP_Y": f"{plate['seated_tube_bottom_y']:.6g} mm",
        "TIP_FROM_CARTRIDGE": f"{plate['seated_tube_bottom_y'] - _enc.pump_cartridge_aft_y(f.box['pump_trays'], plate):.6g} mm",
        "DOCK_BODY_GAP": f"{_enc.bay_back_y(plate) - _enc.pump_cartridge_aft_y(f.box['pump_trays'], plate):.4g} mm",
        "CAP_SCREWS": f"{len(_enc.cap_screw_ys(f.box['inner'], plate))}",
        "CAP_SCREW_LEN": f"{_enc.cap_screw_len:.4g}",
    }
    substitute_md(_here / "pump-replacement.md", variables=variables)
    print("-> pump-replacement.md")
    print(f"   {len(found)} collet joints: {', '.join(found)}")
    print(f"   {variables['CART_PUMPS']} prepared pumps leave with {variables['TUBE_CUT']} tubes; "
          f"{variables['PUMP_TEES']} pump tees in the tee wall "
          f"({variables['BOX_TEES']} tees in all) stay")


if __name__ == "__main__":
    main()
