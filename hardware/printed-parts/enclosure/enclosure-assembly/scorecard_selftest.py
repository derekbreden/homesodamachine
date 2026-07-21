"""Prove the scorecard's geometry gates actually fire.

A guard that never triggers is worthless — it manufactures false confidence. The
board learned this the hard way: for a while an agent could route a trace under
the WROOM antenna and the build stayed green, because the keepout check did not
exist yet. When it was finally written, the first thing done was to *prove it
fires* — inject the defect, watch it flag, and add a control just outside that
must stay silent (`hardware/pcb/pcba` commit eac5ada5).

This is that discipline for the enclosure's geometry gates. Each gate's audit
function is fed hand-built defect geometry (`cq.Solid` boxes at chosen positions)
and a passing control, and we assert the audit flags the defect and stays silent
on the control. `build_scorecard` is exercised end-to-end too, so a refactor that
quietly stops a gate from failing is caught here rather than on a real board.

Run: `tools/cad-venv/bin/python scorecard_selftest.py` (exit 0 = every gate fires
as designed; exit 1 = a gate has gone blind). Wired into the enclosure pre-commit
and runnable in CI.
"""

from __future__ import annotations

import sys

import cadquery as cq

import scorecard as sc


def box(x, y, z, dx=10.0, dy=10.0, dz=10.0):
    """An axis-aligned solid with its low corner at (x, y, z)."""
    return cq.Solid.makeBox(dx, dy, dz, cq.Vector(x, y, z))


# Each case returns (ok, message). `check(name, ok, msg)` records and prints it.
_failures = 0


def check(label: str, ok: bool, detail: str = "") -> None:
    global _failures
    mark = "\033[32m✓\033[0m" if (ok and sys.stdout.isatty()) else ("✓" if ok else "✗")
    if not ok:
        mark = "\033[31m✗\033[0m" if sys.stdout.isatty() else "✗"
        _failures += 1
    print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))


# ── pack-closes: two solids overlapping = a clash; apart = clean ─────────────
def test_pack_closes() -> None:
    print("pack-closes (no two solids overlap)")
    # Defect: two content solids sharing a 5×5×5 = 125 mm³ region (> CLASH_TOL).
    clash = sc.pack_clashes({"a": box(0, 0, 0), "b": box(5, 5, 5)}, {})
    check("fires on overlapping content pair", len(clash) == 1,
          f"got {len(clash)} clash(es)")
    # Defect on the content-vs-piece path (a part fouling a wall/lip).
    clash_piece = sc.pack_clashes({"c": box(5, 5, 5)}, {"piece": box(0, 0, 0)})
    check("fires on content fouling a piece", len(clash_piece) == 1,
          f"got {len(clash_piece)} clash(es)")
    # Control: well separated — must stay silent.
    clear = sc.pack_clashes({"a": box(0, 0, 0), "b": box(50, 50, 50)}, {})
    check("silent on a separated pair", len(clear) == 0, f"got {len(clear)} clash(es)")


# ── lines-clear: a tube driving through another tube or a non-terminal part = a clash ─────────
def test_lines_clear() -> None:
    print("lines-clear (no routed tube intersects a part or another tube)")
    # Defect: two crossing tube-solids sharing a 4×4×4 = 64 mm³ region (> CLASH_TOL). Neither
    # terminates on the other, so it is a real interpenetration.
    tt = sc.line_clashes({"t1": box(0, 0, 0, 40, 4, 4), "t2": box(18, 0, 0, 4, 40, 4)},
                         {}, {"t1": {"A", "B"}, "t2": {"C", "D"}})
    check("fires on two interpenetrating tubes", len(tt) == 1, f"got {len(tt)} clash(es)")
    # Defect: a tube driving through a part it does NOT terminate on.
    tp = sc.line_clashes({"t1": box(0, 0, 0)}, {"pump-x": box(5, 5, 5)}, {"t1": {"A", "B"}})
    check("fires on a tube through a non-terminal part", len(tp) == 1, f"got {len(tp)} clash(es)")
    # Control: the SAME overlap, but the part is one this tube terminates on — a tube seats into
    # its end fitting's collet by design, so it must stay silent.
    seat = sc.line_clashes({"t1": box(0, 0, 0)}, {"pump-x": box(5, 5, 5)}, {"t1": {"A", "pump-x"}})
    check("silent on a tube seating into its own end fitting", len(seat) == 0, f"got {len(seat)} clash(es)")
    # Control: a tube well clear of every tube and part.
    wide = sc.line_clashes({"t1": box(0, 0, 0), "t2": box(50, 50, 50)},
                           {"part": box(200, 0, 0)}, {"t1": {"A"}, "t2": {"B"}})
    check("silent on tubes clear of everything", len(wide) == 0, f"got {len(wide)} clash(es)")
    # Wiring: lines_clear_check turns a clash into a red 'lines-clear' gate, and none into green.
    orig = sc.line_clashes
    try:
        sc.line_clashes = lambda *a, **k: [("fluid-x", "fluid-y", 50.0)]
        red = sc.lines_clear_check({})
        check("lines_clear_check emits a red gate on a clash",
              red.id == "lines-clear" and red.kind == "gate" and red.status == "fail",
              f"id={red.id} status={red.status}")
        sc.line_clashes = lambda *a, **k: []
        green = sc.lines_clear_check({})
        check("lines_clear_check passes when no tube clashes", green.status == "pass",
              f"status={green.status}")
    finally:
        sc.line_clashes = orig


# ── clearance-floor: sub-floor gap = violation; declared contact = allowed ───
def test_clearance_floor() -> None:
    print(f"clearance-floor (part↔part gap ≥ {sc.CLEARANCE_FLOOR} mm)")
    # Defect: two undeclared parts 0.5 mm apart (below the 1.0 mm floor).
    tight = sc.part_clearances({"mq6-sensor": box(0, 0, 0),
                                "dc-dist": box(0, 0, 10.5)})
    viol = [(a, b, g) for a, b, g, ok in tight if not ok and g < sc.CLEARANCE_FLOOR]
    check("fires on a sub-floor gap between undeclared parts", len(viol) == 1,
          f"tightest {viol[0][2]:.2f} mm" if viol else "no violation seen")
    # Control: the same 0.5 mm gap, but a declared intentional contact → allowed.
    contact = sc.part_clearances({"foam-assembly": box(0, 0, 0),
                                  "power-tray": box(0, 0, 10.5)})
    cviol = [r for r in contact if not r[3] and r[2] < sc.CLEARANCE_FLOOR]
    check("silent on a declared TOUCHING_OK contact at the same gap", len(cviol) == 0,
          f"{len(cviol)} spurious violation(s)")
    # Control: undeclared parts comfortably clear.
    wide = sc.part_clearances({"mq6-sensor": box(0, 0, 0), "dc-dist": box(0, 0, 12.0)})
    wviol = [r for r in wide if not r[3] and r[2] < sc.CLEARANCE_FLOOR]
    check("silent on undeclared parts above the floor", len(wviol) == 0,
          f"{len(wviol)} spurious violation(s)")


# ── pieces-fit-bed: a piece over the H2C envelope can't print ────────────────
def test_fit_bed() -> None:
    bed = (325.0, 320.0, 320.0)
    print(f"pieces-fit-bed (each piece ≤ {bed[0]:g}×{bed[1]:g}×{bed[2]:g})")
    over = sc.fit_bed({"huge": box(0, 0, 0, 400, 100, 100)}, bed)
    check("fires on a piece overflowing the bed", not over[0][4],
          f"{over[0][1]:.0f} mm on X")
    fits = sc.fit_bed({"ok": box(0, 0, 0, 300, 100, 100)}, bed)
    check("silent on a piece within the bed", fits[0][4])


# ── seams-mate: piece∩piece over the slip tolerance = interference ───────────
def test_seams_mate() -> None:
    print(f"seams-mate (piece∩piece < {sc.SLIP_TOL} mm³ slide fit)")
    interf = sc.seam_mates({"p1": box(0, 0, 0), "p2": box(5, 5, 5)})  # 125 mm³
    check("fires on interfering pieces", not interf[0][3], f"{interf[0][2]:.0f} mm³")
    mate = sc.seam_mates({"p1": box(0, 0, 0), "p2": box(50, 0, 0)})   # disjoint
    check("silent on a clean slide-fit seam", mate[0][3])


# ── placed: rules that hold = placed; drifted = a visible fail ───────────────
def test_placement() -> None:
    print("placed (face-to-datum rules hold)")
    inner = (0.0, 100.0, 0.0, 100.0, 0.0, 100.0)  # ix0 ix1 iy0 iy1 iz0 iz1
    # foam-assembly rules: y+≤1, x-≤1, x+≤1, z-≤10. A slab hugging back/sides/floor.
    held = sc.placement_audit({"foam-assembly": box(0, 0, 0, 100, 100, 50)}, inner)
    row = next((r for r in held if r[0] == "foam-assembly"), None)
    check("a component meeting its rules reads as placed", bool(row) and row[1])
    # Drift it 5 mm off the left wall — x- rule (≤1 mm) now fails.
    drift = sc.placement_audit({"foam-assembly": box(5, 0, 0, 95, 100, 50)}, inner)
    drow = next((r for r in drift if r[0] == "foam-assembly"), None)
    check("a drifted component reads as NOT placed", bool(drow) and not drow[1],
          "x- rule should break")

    # The part-to-part `near` form: source-select-assembly is pressed to the foam
    # (`near foam-assembly` ≤ 1.0 mm). A 0.5 mm gap = placed; drifted = flagged;
    # an absent neighbor = flagged.
    print("placed (part-to-part `near` rules hold)")
    near_ok = sc.placement_audit({"source-select-assembly": box(0, 0, 0),
                                  "foam-assembly": box(0, 0, 10.5)}, inner)
    nrow = next((r for r in near_ok if r[0] == "source-select-assembly"), None)
    check("a component within its near gap reads as placed", bool(nrow) and nrow[1])
    near_far = sc.placement_audit({"source-select-assembly": box(0, 0, 0),
                                   "foam-assembly": box(0, 0, 15.0)}, inner)
    frow = next((r for r in near_far if r[0] == "source-select-assembly"), None)
    check("a component drifted off its neighbor reads as NOT placed", bool(frow) and not frow[1],
          "near foam-assembly rule should break")
    near_missing = sc.placement_audit({"source-select-assembly": box(0, 0, 0)}, inner)
    mrow = next((r for r in near_missing if r[0] == "source-select-assembly"), None)
    check("a near rule against an absent neighbor reads as NOT placed", bool(mrow) and not mrow[1],
          "missing foam-assembly must not pass")

    # The part-to-part `clear` (keep-out) form — proven through an injected probe rule,
    # independent of the pack rules that lean on it (the bag-circuit assembly's floor-stratum
    # keep-outs), so the proof never rides the current pack's numbers.
    print("placed (part-to-part `clear` keep-out fires)")
    sc.PLACEMENT_RULES["clear-probe"] = [("clear", "display", 7.0)]
    try:
        held_clear = sc.placement_audit({"clear-probe": box(0, 0, 0),
                                         "display": box(0, 0, 18.0)}, inner)
        hrow = next((r for r in held_clear if r[0] == "clear-probe"), None)
        check("a component honoring its keep-out reads as placed", bool(hrow) and hrow[1])
        crowd = sc.placement_audit({"clear-probe": box(0, 0, 0),
                                    "display": box(0, 0, 13.0)}, inner)
        crow = next((r for r in crowd if r[0] == "clear-probe"), None)
        check("a component crowding its keep-out reads as NOT placed", bool(crow) and not crow[1],
              "clear display rule should break")
        clear_missing = sc.placement_audit({"clear-probe": box(0, 0, 0)}, inner)
        xrow = next((r for r in clear_missing if r[0] == "clear-probe"), None)
        check("a clear rule against an absent neighbor reads as NOT placed", bool(xrow) and not xrow[1],
              "missing display must not vacuously pass the keep-out")
    finally:
        del sc.PLACEMENT_RULES["clear-probe"]


# ── end-to-end: build_scorecard wires a defect through to a red gate ─────────
def test_scorecard_end_to_end() -> None:
    print("build_scorecard end-to-end (a defect reaches the gate status)")
    bed = (325.0, 320.0, 320.0)
    inner = (0.0, 100.0, 0.0, 100.0, 0.0, 100.0)
    # A minimal overlapping pack. Registry coverage will fail (these aren't real
    # components) — we assert specifically on the pack-closes gate here.
    solids = {"a": box(0, 0, 0), "b": box(5, 5, 5)}
    pieces = {"piece": box(200, 0, 0)}
    card = sc.build_scorecard(solids, pieces, bed, inner)
    pack = next(c for c in card.checks if c.id == "pack-closes")
    check("pack-closes gate goes red on an overlapping pack", pack.status == "fail",
          f"status={pack.status}")
    # Clean pack → the pack-closes gate passes.
    ok = sc.build_scorecard({"a": box(0, 0, 0), "b": box(50, 50, 50)}, pieces, bed, inner)
    packok = next(c for c in ok.checks if c.id == "pack-closes")
    check("pack-closes gate passes on a clean pack", packok.status == "pass",
          f"status={packok.status}")


# ── routing guards: a path that cannot be made raises ────────────────────────
def test_routing_guards() -> None:
    import _routing as R

    print("routing guards (bend radius, ambiguous close, folded close)")

    # Two ports facing each other down a corridor, offset along x: exit stub → across → close.
    # Hand-built fixture geometry, like the defect boxes above.
    span, depth = 200.0, 130.0
    bend = R.BEND_RATIO * 6.35

    def fixture():
        R._frames.clear()
        R.frame("A", box(0, 0, 0), {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
        R.frame("B", box(0, 0, 0), {"p": ((span, depth, 0.0), "y-", 6.35)})

    # `across` turns perpendicular to the exit stub, so the stub is its own leg; a constraint
    # continuing the stub's direction straightens into it.
    across = {"x": span}

    # The control first: a stub of one full bend radius seats its turn, and the run is clean.
    fixture()
    try:
        run = R.route("t", "A.p", across, "B.p")
        check("silent on legs that clear the bend radius", len(run.bends) >= 2, f"{len(run.bends)} bends")
    except ValueError as e:
        check("silent on legs that clear the bend radius", False, str(e)[:70])

    # A stub shorter than the bend radius cannot seat the turn off the port.
    fixture()
    try:
        R.route("t", "A.p", across, "B.p", stub=bend / 3.0)
        check("fires on a leg too short for its bend radius", False, "no raise")
    except ValueError as e:
        check("fires on a leg too short for its bend radius", "tangent" in str(e), str(e)[:58])

    # Two coordinates still differing at the close = an ambiguous corner order.
    fixture()
    try:
        R.route("t", "A.p", "B.p")
        check("fires when the close is ambiguous (2 coords differ)", False, "no raise")
    except ValueError as e:
        check("fires when the close is ambiguous (2 coords differ)",
              "needs another constraint" in str(e), str(e)[:58])

    # A path nearer the port than its own approach stub would back out and come straight back.
    fixture()
    try:
        R.route("t", "A.p", {"y": depth - bend / 2.0}, across, "B.p", stub=(bend, bend * 2.0))
        check("fires when the close folds back on itself", False, "no raise")
    except ValueError as e:
        check("fires when the close folds back on itself", "folds" in str(e), str(e)[:58])
    R._frames.clear()


def main() -> None:
    print("── enclosure scorecard self-test " + "─" * 20)
    if not sc._HAVE_EXACT:
        print("  note: exact solid-distance kernel unavailable; clearance uses bbox estimate")
    for t in (test_pack_closes, test_lines_clear, test_clearance_floor, test_fit_bed,
              test_seams_mate, test_placement, test_scorecard_end_to_end,
              test_routing_guards):
        t()
    print("─" * 53)
    if _failures:
        raise SystemExit(f"{_failures} gate(s) did not fire as designed — the scorecard has a blind spot")
    print("every gate fires on a real defect and stays silent on its control")


if __name__ == "__main__":
    main()
