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

from _cold_core_interface import cap_conduits, cap_conduit_bore_radius  # noqa: E402

import _lines  # noqa: E402  — the stock every water run is drawn on
import front_half as _fh  # noqa: E402  — the placed pack, and the runs cut to it
import manifold_layout as _ml  # noqa: E402  — the manifold's own census
import seaflo_discharge_chain as _dis  # noqa: E402  — on the path once `_lines` is imported

from docgen import substitute_md  # noqa: E402


def main():
    # The two pump-port stubs are cut to the runs the placed pack draws, so the length
    # a bench cuts is read off the run and not rounded beside it. `_cards_ip` states the
    # same two lengths on IP-02 off the same runs at the same precision — one cut under
    # one figure, so card and procedure cannot send a bench to two different lengths.
    _runs = {r.id: r for r in _fh.build_pack().runs}
    for _rid in ("water-6", "water-7"):
        if _runs[_rid].bend != _lines.HOSE_BEND:
            raise ValueError(
                f"`{_rid}` is drawn on a {_runs[_rid].bend} mm bend and the procedure quotes "
                f"the 3/8\" reinforced PVC's {_lines.HOSE_BEND} mm for both pump-port stubs — "
                f"either they go back on one stock or the doc reads them out apiece.")

    variables = {
        # Every warm-side fluid termination this procedure lands on is a conduit
        # in the cold core's top cap — a bore up one of the cup's own columns,
        # opening on the lid's outer face. `cap_conduits` is the table; a conduit
        # added or dropped there moves this count, and the procedure's own list
        # of what it closes has to move with it.
        "CAP_CONDUITS": f"{len(cap_conduits)}",
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
    }

    substitute_md(
        _here / "internal-plumbing.md",
        variables=variables,
        expected_counts={
            "CAP_CONDUITS": 2,
            "CAP_CONDUIT_D": 1,
            "SUCTION_STUB_LEN": 1,
            "DISCHARGE_STUB_LEN": 1,
            "PVC_BEND_R": 2,
            "DISCHARGE_CHAIN_LEN": 1,
            "MANIFOLD_VALVES": 2,
            "MANIFOLD_TEES": 2,
        },
    )
    print("-> internal-plumbing.md")


if __name__ == "__main__":
    main()
