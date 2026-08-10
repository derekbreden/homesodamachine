"""What a physics world does with the pack, read back in the layout's own frame.

    tools/cad-venv/bin/python hardware/scripts/_settled.py settled.json

`settle.gd` starts every named body where its rule put it, with nothing pulling on it, and lets
contact push apart whatever is inside something else. A body that comes back unmoved is one the
engine agrees is clear. A body that moves has been pushed somewhere, and how far says which
direction and roughly how much — not the smallest move that would have opened the pack, because
nothing minimises and nothing restores.

EVERY READING CARRIES THE BOX IT WAS TAKEN IN, printed above the answer. Four of its numbers
decide what moves: the mover set, the decomposition's hull cap and resolution, and how long
stillness has to hold before it counts. A reading is about the machine only where those were not
the binding constraint.

FREE A SET THAT CROSSES NOTHING. This machine interpenetrates by design — a bulkhead union
through a wall, a tube through a cap bore, a display in its cutout — and the card knows those
are legal where the engine does not. Freed all together they cascade, and what comes back is
about the cascade. `wago-*` alone reads 0.00 mm on all ten; the same ten inside a whole-pack
run read 6.24-6.35.

`_clearing.gap` on a pair is the exact answer. This is what to ask about several bodies at once,
which is the question with no exact form here.
"""

import json
import statistics
import sys

# The gap the pack is graded on, from `_scorecard`. A body the engine wants to move by less than
# this is inside the band the layout already calls clear.
FLOOR = 1.0


def read(path):
    """The rows `settle.gd` wrote, each carrying where a rule put a body and where contact left
    it, as 4×4s in the layout's millimetres."""
    with open(path) as f:
        report = json.load(f)
    return report["bodies"], report


def families(rows):
    """Rows gathered by the name a body's siblings share, trailing digits dropped."""
    out = {}
    for row in rows:
        stem = row["name"].rstrip("0123456789").rstrip("-_") or row["name"]
        out.setdefault(stem, []).append(row)
    return out


def box(whole):
    """The bounds the run was taken under, before the answer it produced."""
    b = whole.get("box")
    if not b:
        return ["  box  not stated — an older run, and its bounds are not recoverable"]
    return [
        f"  box  free {b['free']!r}: {b['movers']} moved, {b['held']} held "
        f"({b['held_as'].split(' — ')[0]})",
        f"       gravity {b['gravity']:g}, started from {b['started_from']}",
        f"       hulls ≤{b['max_convex_hulls']} at resolution {b['resolution']}, "
        f"concavity {b['max_concavity']:.3g}",
        f"       still under {b['still_under'][0]:g} mm and {b['still_under'][1]:g}° a step, "
        f"held for {b['quiet_steps_wanted']} steps",
        f"       {b['note']}",
    ]


def report(path):
    rows, whole = read(path)
    moved = sorted((r["moved"] for r in rows), reverse=True)
    over = [r for r in rows if r["moved"] > FLOOR]
    print(f"{len(rows)} bodies, {whole['steps']} steps, "
          f"{'settled' if whole['settled'] else 'STILL MOVING at the step cap — raise --steps'}")
    for line in box(whole):
        print(line)
    print(f"  median {statistics.median(moved):.3f} mm   "
          f"{len(rows) - len(over)} of {len(rows)} inside the {FLOOR:g} mm floor")
    if not over:
        print("  every body came back where its rule put it")
        return 0

    print(f"\n  {'family':22s} {'bodies':>6s} {'over':>5s} {'worst':>9s} {'median':>9s}")
    for stem, group in sorted(families(over).items(),
                              key=lambda kv: -max(r["moved"] for r in kv[1])):
        kin = [r["moved"] for r in group]
        print(f"  {stem:22s} {len(families(rows).get(stem, group)):6d} {len(group):5d} "
              f"{max(kin):8.2f} mm {statistics.median(kin):8.2f} mm")
    return 0


def selftest():
    """The reading is in the layout's frame and the two poses are told apart."""
    import tempfile
    import pathlib

    ident = [1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1, 0, 0, 0, 0, 1]
    stood = list(ident[:12]) + [3.0, 4.0, 0.0, 1.0]
    rows = [{"name": "held-1", "from": ident, "to": ident, "moved": 0.0, "turned": 0.0},
            {"name": "held-2", "from": ident, "to": ident, "moved": 0.02, "turned": 0.0},
            {"name": "shoved-1", "from": ident, "to": stood, "moved": 5.0, "turned": 0.0}]
    with tempfile.TemporaryDirectory() as d:
        path = pathlib.Path(d) / "settled.json"
        path.write_text(json.dumps({"steps": 60, "settled": True, "bodies": rows}))
        got, whole = read(path)

    if len(got) != len(rows):
        raise AssertionError(f"{len(rows)} rows written, {len(got)} read")
    yield f"{len(got)} rows read back"

    moved = [r for r in got if r["moved"] > FLOOR]
    if [r["name"] for r in moved] != ["shoved-1"]:
        raise AssertionError(f"the {FLOOR:g} mm floor let through {[r['name'] for r in moved]} — "
                             f"a body inside the band the pack is graded on is being reported")
    yield f"only a body past the {FLOOR:g} mm floor is reported"

    kin = families(got)
    if sorted(kin) != ["held", "shoved"]:
        raise AssertionError(f"names gathered as {sorted(kin)} — siblings are not meeting")
    yield "siblings gather under the name they share"

    # The distance is the one the engine measured, not one re-derived from the matrices, so a
    # row that disagrees with its own poses is a row to distrust.
    row = got[2]
    apart = sum((row["to"][12 + i] - row["from"][12 + i]) ** 2 for i in range(3)) ** 0.5
    if abs(apart - row["moved"]) > 1e-6:
        raise AssertionError(f"a row states it moved {row['moved']:.3f} mm and its poses stand "
                             f"{apart:.3f} mm apart")
    yield f"a row's stated move is the distance between its two poses ({apart:.1f} mm)"


if __name__ == "__main__":
    if sys.argv[1:2] == ["selftest"]:
        for line in selftest():
            print(" ", line)
        print("_settled selftest OK")
    elif len(sys.argv) == 2:
        raise SystemExit(report(sys.argv[1]))
    else:
        print(__doc__)
        print("usage: _settled.py selftest | _settled.py <settled.json>")
