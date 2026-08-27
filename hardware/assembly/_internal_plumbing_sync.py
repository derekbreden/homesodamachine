"""Doc-sync driver for hardware/assembly/internal-plumbing.md.

Run: tools/cad-venv/bin/python hardware/assembly/_internal_plumbing_sync.py
"""

import sys
from pathlib import Path

_here = Path(__file__).resolve().parent
sys.path.insert(0, str(next(p for p in _here.parents if p.name == "hardware") / "scripts"))
sys.path.insert(
    0,
    str(next(p for p in _here.parents if (p / "tools" / "docgen").is_dir()) / "tools"),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cadlib"
    ),
)
sys.path.insert(
    0,
    str(
        next(p for p in _here.parents if p.name == "hardware")
        / "printed-parts"
        / "cold-core"
    ),
)

sys.path.insert(
    0,
    str(next(p for p in _here.parents if p.name == "hardware") / "manifold-layout"),
)

from _cold_core_interface import cap_fluid_conduits, cap_conduit_bore_radius  # noqa: E402

import _lines  # noqa: E402  — the stock every water run is drawn on
import enclosure as _enc  # noqa: E402  — the box, and the hull its own zip tie cavities state
import _facts  # noqa: E402  — the placed pack and its runs, off the last build
import enclosure_assembly as _ea  # noqa: E402,F401  — holds the closure this doc watches
import manifold_layout as _ml  # noqa: E402  — the manifold's own census
import seaflo_discharge_chain as _dis  # noqa: E402  — on the path once `_lines` is imported
import wr1110_regulator as _wr1110  # noqa: E402  — the barrel the box bores a rib for
import digiten_flow_sensor as _digiten  # noqa: E402  — the arm its two anchors bore for
import pump_tray as _tray  # noqa: E402  — the plate each Kamoer's head lies on

from docgen import substitute_md  # noqa: E402


def main():
    # The two pump-port stubs are cut to the runs the placed pack draws, so the length
    # a bench cuts is read off the run and not rounded beside it. `_cards_ip` states the
    # same two lengths on IP-02 off the same runs at the same precision — one cut under
    # one figure, so card and procedure cannot send a bench to two different lengths.
    _f = _facts.read()
    _runs = {r.id: r for r in _f.runs}
    for _rid in ("water-6", "water-7"):
        if _runs[_rid].bend != _lines.HOSE_BEND:
            raise ValueError(
                f"`{_rid}` is drawn on a {_runs[_rid].bend} mm bend and the procedure quotes "
                f"the 3/8\" reinforced PVC's {_lines.HOSE_BEND} mm for both pump-port stubs — "
                f"either they go back on one stock or the doc reads them out apiece.")

    # The two loops a tie is picked by on this path, off the hull `enclosure` states for its own
    # ribs and the seats the pack actually bored. Every rib holding a RUN is bored for the one
    # stock, so the runs answer with one figure and the regulator's barrel with its own.
    _run_seats = {round(r, 6) for *_s, r in _f.pack["tube_anchors"]}
    if len(_run_seats) != 1:
        raise ValueError(
            f"the box's run anchors are bored at {sorted(_run_seats)}. This procedure quotes one "
            f"loop for all of them, so either they go back on one stock or it reads them apiece.")
    _barrel = _f.carried_points["wr1110.barrel"]["pos"]
    _barrel_seat = next(r for mid, _u, _n, r in _f.pack["body_anchors"]
                        if mid == _barrel)

    variables = {
        # Every warm-side fluid termination this procedure lands on is a conduit
        # in the cold core's top cap — a bore up one of the cup's own columns,
        # opening on the lid's outer face. `cap_fluid_conduits` is the table; a
        # conduit added or dropped there moves this count, and the procedure's own
        # list of what it closes has to move with it. The cap's other two carry a
        # reed cable apiece, which is a lid this procedure never opens.
        #
        # `CAP_CONDUITS` is the whole cap's count and is nine; this is the fluid
        # subset, which `_enclosure_mechanical_sync` and the cards already call
        # `CAP_FLUID_LINES`.
        "CAP_FLUID_LINES": f"{len(cap_fluid_conduits)}",
        "CAP_CONDUIT_D": f"{2 * cap_conduit_bore_radius:.4g} mm",
        # The two pump-port stubs, and the corner the stock they are cut from holds.
        # The bend radius is the reinforced PVC's own floor as `_lines` reads it off
        # the stock table — the figure every water run on that hose is drawn to — so
        # the parts table and the bench step quote what the runs were actually drawn
        # with rather than a spec copied alongside them.
        "SUCTION_STUB_LEN": f"{_runs['water-7'].length:.0f} mm",
        "DISCHARGE_STUB_LEN": f"{_runs['water-6'].length:.0f} mm",
        "PVC_BEND_R": f"{_lines.HOSE_BEND:.4g} mm",
        # The discharge chain's made-up length, off the module that draws it: every NPT
        # joint in it is modeled at its engagement, so `LENGTH` is barb tip to collet
        # mouth on the stack the bench actually screws together.
        "DISCHARGE_CHAIN_LEN": f"{_dis.LENGTH:.4g} mm",
        # The manifold's census, off the layout that stands the bodies. The procedure
        # lays out one valve and one tee per station, so these are the same two counts
        # `_cards_ip` puts on IP-03 — a station added to the topology moves both.
        "MANIFOLD_VALVES": f"{sum(1 for n in _ml.P if n.startswith('V-'))}",
        "MANIFOLD_TEES": f"{sum(1 for n in _ml.P if n.startswith('Y-'))}",
        # What each of the flow meter's anchors leave alone at the outer end of its barrel —
        # the push-fit ring, off the layout that strikes the anchor's own band on it.
        "DIGITEN_COLLET_FREE": f"{_ea.DIGITEN_COLLET_FREE:.4g} mm",
        "WR1110_LOOP": f"{_enc.tube_anchor_tie_loop(_barrel_seat):.3g} mm",
        "CARB_1_LOOP": f"{_enc.tube_anchor_tie_loop(next(iter(_run_seats))):.3g} mm",
        # And the meter's, on the seat `enclosure_assembly.digiten_anchors` strikes: the
        # barrel's own radius and the slip the V stands off it by. A flow-meter anchor
        # reaches `flow_meter_anchor_wall` off that axis where a rib reaches `wall`, and
        # both are the box's three millimetres, so one hull answers for both families.
        "DIGITEN_LOOP": f"{_enc.tube_anchor_tie_loop(_digiten.port_dia / 2.0 + _ea.DIGITEN_SEAT_SLIP):.3g} mm",
        # And the loop each of a pump's two zip ties closes — the tray's plate and the bracket the
        # part carries under it, off the module that draws the tray, with the bore and the can's
        # own hole that tray takes the pump on.
        "PUMP_BRACKET": f"{_tray.bracket_half * 2:.4g} mm",
        # The cap and what closes it, off the module that cuts both the clearance bores and
        # the heat-set seats — so a screw added there is a screw the bench is told to drive.
        "CAP_SCREWS": f"{len(_enc.cap_screw_ys(_f.box.inner, _f.box.collet_plate))}",
        "CAP_SCREW_LEN": f"{_enc.screw_len:.4g}",
        "PUMP_SOCKET": f"{2 * _tray.boss_half:.4g} mm",
        "PUMP_SOCKET_D": f"{_tray.boss_depth:.4g} mm",
        "PUMP_CAN_BORE": f"{2 * _tray.can_half:.4g} mm",
    }

    substitute_md(
        _here / "internal-plumbing.md",
        variables=variables,
    )
    print("-> internal-plumbing.md")


if __name__ == "__main__":
    main()
