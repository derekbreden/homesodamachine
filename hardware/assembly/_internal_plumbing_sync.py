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
import hlghlg_check_valve as _dis  # noqa: E402  — on the path once `_lines` is imported
import diaphragm_pump_sleeve as _pump_elbow  # noqa: E402  — likewise, the elbow on each barb
import wr1110_regulator as _wr1110  # noqa: E402  — the barrel the box bores a rib for
import digiten_flow_sensor as _digiten  # noqa: E402  — the arm its two anchors bore for
import pump_tray as _tray  # noqa: E402  — the plate each Kamoer's head lies on

from docgen import substitute_md  # noqa: E402


def main():
    # The two tubes at the pump's elbows are cut to the runs the placed pack draws, so the
    # length a bench cuts is read off the run and not rounded beside it.
    _f = _facts.read()
    _runs = {r.id: r for r in _f.runs}

    # The loops a tie is picked by on this path, off the hull `enclosure` states for its own ribs
    # and the seats the pack actually bored: each anchored BODY answers with its own.
    # A BODY'S SEAT IS ITS OWN REFERENCE MODULE'S SECTION, taken by name off the table
    # `check_body_seated` grades the built pieces against — the same route `_bom_sync` takes, so
    # this page and the ledger's rows cannot read one barrel two ways. What the pack bored is held
    # against it rather than searched: a section that moved without its rib has nothing behind it.
    _body_seats = {name: section()[1] + _ea.BODY_ANCHOR_SLIP
                   for name, section, _root, _piece in _ea.BODY_ANCHOR_SITES}
    _bored = {round(station[3], 6) for station in _f.pack["body_anchors"]}
    _missing = sorted(n for n, r in _body_seats.items() if round(r, 6) not in _bored)
    if _missing:
        raise ValueError(
            f"{_missing} name a section this procedure quotes a loop for and the last build bored "
            f"no rib at that radius. The seat is the body's own, so a body whose section moved "
            f"without its rib leaves a figure with nothing behind it.")

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
        # The two tubes at the pump's elbows: what each run leaves exposed, the depth each
        # elbow's tube socket swallows, and the clocking the discharge elbow takes on its barb.
        "SUCTION_TUBE_LEN": f"{_runs['water-7'].length:.0f} mm",
        "DISCHARGE_TUBE_LEN": f"{_runs['water-6'].length:.0f} mm",
        "ELBOW_TUBE_DEPTH": f"{_pump_elbow.TUBE_DEPTH:g} mm",
        "ELBOW_DIP": f"{_ea.DISCHARGE_ELBOW_DIP:g}°",
        # The discharge chain's made-up length, off the module that draws it: every NPT
        # joint in it is modeled at its engagement, so `LENGTH` is inlet mouth to outlet
        # mouth on the stack the bench actually screws together.
        "DISCHARGE_CHAIN_LEN": f"{_dis.LENGTH:.4g} mm",
        # The valve and purchased-tee census comes from the placed layout.
        "MANIFOLD_VALVES": f"{sum(1 for n in _ml.P if n.startswith('V-'))}",
        "MANIFOLD_TEES": f"{len(_ml.PURCHASED_TEES)}",
        "DOCK_FORE_LINK": f"{_ml.FORE_STUB_EXPOSED:.6g} mm",
        "DOCK_UPPER_TAIL": f"{_ml.FORE_STUB_EXPOSED + _ml._returns.RUN_INSERTION + _ml._returns.VALVE_INSERTION_NOMINAL:.6g} mm",
        "POGO_INSERT_HOST_DEPTH": f"{_enc._pogo.ear_back() + _enc.pogo_heatset_setback + _enc.pump_contact_face_recess:.4g} mm",
        "POGO_INSERT_SETBACK": f"{_enc.pogo_heatset_setback:.4g} mm",
        "DOCK_BODY_GAP": f"{_enc.bay_back_y(_f.box['collet_plate']) - _enc.pump_cartridge_aft_y(_f.box['pump_trays'], _f.box['collet_plate']):.4g} mm",
        "FLAVOR_A_CORNERS": f"{_runs['fluid-18'].corners}",
        "FLAVOR_B_CORNERS": f"{_runs['fluid-28'].corners}",
        "FLAVOR_B_RETURN_RISE": f"{_lines.GATE_B_DRAIN_RETURN_RISE:.4g} mm",
        "FLAVOR_B_RETURN_WEST": f"{_lines.GATE_B_RETURN_WEST:.4g} mm",
        # What each of the flow meter's anchors leave alone at the outer end of its barrel —
        # the push-fit ring, off the layout that strikes the anchor's own band on it.
        "DIGITEN_COLLET_FREE": f"{_ea.DIGITEN_COLLET_FREE:.4g} mm",
        # How far west of the carb union's column the meter lies, off the constant that sets it.
        "DIGITEN_WEST_SET": f"{_ea.DIGITEN_WEST_SET:.4g} mm",
        "WR1110_LOOP": f"{_enc.tube_anchor_tie_loop(_body_seats['wr1110']):.3g} mm",
        "SPLIT_LOOP": f"{_enc.tube_anchor_tie_loop(_body_seats['water-split']):.3g} mm",
        "FLOWREG_LOOP": f"{_ea._water_regulator.tie_loop():.3g} mm",
        # And the meter's, on the seat `enclosure_assembly.digiten_anchors` strikes: the
        # fixed collar's own radius and the slip its bore stands off it by. A flow-meter anchor
        # reaches `flow_meter_anchor_wall` off that axis where a rib reaches `wall`, and
        # both are the box's three millimetres, so one hull answers for both families.
        "DIGITEN_LOOP": f"{_enc.tube_anchor_tie_loop(_digiten.port_dia / 2.0 + _ea.DIGITEN_SEAT_SLIP):.3g} mm",
        # The cap and what closes it, off the module that cuts both the clearance bores and
        # the heat-set seats — so a screw added there is a screw the bench is told to drive.
        "CAP_SCREWS": f"{len(_enc.cap_screw_ys(_f.box.inner, _f.box.collet_plate))}",
        "CAP_SCREW_LEN": f"{_enc.cap_screw_len:.4g}",
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
