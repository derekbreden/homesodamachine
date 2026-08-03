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
        red = sc.lines_clear_check({}, {})
        check("lines_clear_check emits a red gate on a clash",
              red.id == "lines-clear" and red.kind == "gate" and red.status == "fail",
              f"id={red.id} status={red.status}")
        sc.line_clashes = lambda *a, **k: []
        green = sc.lines_clear_check({}, {})
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
    # Control: the same 0.5 mm gap, but a declared intentional contact → allowed. The
    # pair is injected rather than taken from the pack, so this tests the exemption
    # mechanism whether or not the pack currently declares any contact of its own —
    # a set that happens to be empty must not quietly retire the check that reads it.
    pair = frozenset(("mq6-sensor", "dc-dist"))
    sc.TOUCHING_OK.add(pair)
    try:
        contact = sc.part_clearances({"mq6-sensor": box(0, 0, 0),
                                      "dc-dist": box(0, 0, 10.5)})
    finally:
        sc.TOUCHING_OK.discard(pair)
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
    # A slab seated on every datum foam-assembly is measured against, so every
    # rule reads zero and holds whatever the tolerances are. In Z that datum is
    # the floor slab itself — the core stands on it.
    held = sc.placement_audit({"foam-assembly": box(0, 0, 0, 100, 100, 45)}, inner)
    row = next((r for r in held if r[0] == "foam-assembly"), None)
    check("a component meeting its rules reads as placed", bool(row) and row[1])
    # Drift it off the left wall by more than that rule's OWN tolerance, read from
    # the rule itself — a fixed drift goes quietly blind the day a tolerance grows.
    # Everything else stays seated, so `x-` is the only rule that can break.
    x_tol = next(t for f, t in sc.PLACEMENT_RULES["foam-assembly"] if f == "x-")
    dx = x_tol + 5.0
    drift = sc.placement_audit({"foam-assembly": box(dx, 0, 0,
                                                     100 - dx, 100, 45)}, inner)
    drow = next((r for r in drift if r[0] == "foam-assembly"), None)
    check("a drifted component reads as NOT placed", bool(drow) and not drow[1],
          "x- rule should break")

    # The part-to-part `near` form, proven through an injected probe rule for the same
    # reason the `clear` form below is — the proof never rides the pack's current numbers,
    # so a component changing which form holds it cannot blind this gate. A 0.5 mm gap =
    # placed; drifted = flagged; an absent neighbor = flagged.
    print("placed (part-to-part `near` rules hold)")
    sc.PLACEMENT_RULES["near-probe"] = [("near", "display", 1.0)]
    try:
        near_ok = sc.placement_audit({"near-probe": box(0, 0, 0),
                                      "display": box(0, 0, 10.5)}, inner)
        nrow = next((r for r in near_ok if r[0] == "near-probe"), None)
        check("a component within its near gap reads as placed", bool(nrow) and nrow[1])
        near_far = sc.placement_audit({"near-probe": box(0, 0, 0),
                                       "display": box(0, 0, 15.0)}, inner)
        frow = next((r for r in near_far if r[0] == "near-probe"), None)
        check("a component drifted off its neighbor reads as NOT placed", bool(frow) and not frow[1],
              "near display rule should break")
        near_missing = sc.placement_audit({"near-probe": box(0, 0, 0)}, inner)
        mrow = next((r for r in near_missing if r[0] == "near-probe"), None)
        check("a near rule against an absent neighbor reads as NOT placed", bool(mrow) and not mrow[1],
              "missing display must not pass")
    finally:
        del sc.PLACEMENT_RULES["near-probe"]

    # The part-to-part `clear` (keep-out) form — proven through an injected probe rule,
    # independent of the pack rules that lean on it (the pack's own floor-stratum
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


# ── port-leads: a body parked in front of a collet = no room to leave ────────
def test_port_leads() -> None:
    print(f"port-leads (a tube port has {sc.PORT_LEAD_BENDS:g} bend radii of straight)")
    import _lines
    reach = sc.PORT_LEAD_BENDS * _lines.WBEND

    # The instrument first, on hand-built geometry. A collet at the origin looking +Y.
    near = {"wall": box(-5, 3.0, -5, 20, 20, 20)}        # a body 3 mm off the port face
    who, free = sc._lead_first((0, 0, 0), (0, 1, 0), 6.35, reach, near)
    check("fires on a body parked in front of a port", who == "wall" and free < reach,
          f"{free:.2f} mm to {who}")
    far = {"wall": box(-5, reach + 5.0, -5, 20, 20, 20)}
    who2, free2 = sc._lead_first((0, 0, 0), (0, 1, 0), 6.35, reach, far)
    check("silent on a port with its lead clear", who2 is None and free2 == reach,
          f"reached {free2:.2f} mm")
    # The same near body, held out because the port's own run terminates on it — a divider's
    # outlet stands one leg-lead off the collet it feeds, and that is the mate, not a blockage.
    who3, free3 = sc._lead_first((0, 0, 0), (0, 1, 0), 6.35, reach, near, skip=("wall",))
    check("silent when the body in front is the port's own mate", who3 is None,
          f"{free3:.2f} mm, hit {who3}")

    # And through `port_leads`, so the wiring from a Port row to a verdict is proven too.
    probe = sc._p("probe", "tee-y-c", "fluid", (0.0, 0.0, 0.0), "y+", 6.35, "a test fixture")
    sc.PORTS.append(probe)
    try:
        blocked = sc.port_leads({"tee-y-c": box(-5, -20, -5, 20, 20, 20), **near}, mates={})
        row = next(r for r in blocked if r[1] == "probe")
        check("port_leads reports a blocked collet", not row[5] and row[6], f"met {row[2]}")
        clear = sc.port_leads({"tee-y-c": box(-5, -20, -5, 20, 20, 20), **far}, mates={})
        crow = next(r for r in clear if r[1] == "probe")
        check("port_leads passes a clear collet", crow[5], f"met {crow[2]}")
        # The gate itself: a blocked collet must turn build_scorecard's verdict red.
        card = sc.build_scorecard({"tee-y-c": box(-5, -20, -5, 20, 20, 20), **near},
                                  {"piece": box(400, 0, 0)}, (325.0, 320.0, 320.0),
                                  (0.0, 100.0, 0.0, 100.0, 0.0, 100.0))
        pl = next(c for c in card.checks if c.id == "port-leads")
        check("port-leads gate goes red on a blocked collet",
              pl.kind == "gate" and pl.status == "fail", f"status={pl.status}")
    finally:
        sc.PORTS.remove(probe)


# ── located: a fluid port is the open mouth of its own bore, exactly where it says ────
def test_located_faces() -> None:
    print("located (a fluid port names the collet face that is there)")
    # A bored collet end, hand-built: a Ø12 barrel to y = 0 with a Ø6.35 bore recessed
    # 4 deep — the bulkhead union's own end. Its open face is the y = 0 plane.
    bored = (cq.Solid.makeCylinder(6.0, 20.0, cq.Vector(0, -20, 0), cq.Vector(0, 1, 0))
             .cut(cq.Solid.makeCylinder(6.35 / 2.0, 4.0, cq.Vector(0, -4, 0), cq.Vector(0, 1, 0))))
    # A solid collet tip (a valve's own): same barrel, no bore. A small float over it sits
    # inside the rim allowance the whole way, which is what the seat read is for.
    solid_tip = cq.Solid.makeCylinder(6.0, 20.0, cq.Vector(0, -20, 0), cq.Vector(0, 1, 0))

    def status(y, body):
        probe = sc._p("probe", "tee-y-c", "fluid", (0.0, y, 0.0), "y+", 6.35, "a test fixture")
        sc.PORTS.append(probe)
        try:
            comp, ok, rows = next(r for r in sc.ports_audit({"tee-y-c": body}) if r[0] == "tee-y-c")
            return next(s for pt, s in rows if pt.name == "probe")
        finally:
            sc.PORTS.remove(probe)

    s_ok = status(0.0, bored)
    check("passes a mouth exactly on its face", s_ok == "ok", s_ok)
    s_adrift = status(3.0, bored)   # the bulkhead defect: declared 3 mm past the face
    check("fires on a face declared past the fitting (tube stops in air)",
          s_adrift.startswith("adrift"), s_adrift)
    s_buried = status(-3.0, bored)  # the mirror: declared inside the fitting
    check("fires on a face declared inside the fitting (tube drawn into it)",
          s_buried.startswith("buried"), s_buried)
    s_solid_ok = status(0.0, solid_tip)
    check("passes a mouth on a solid tip's face", s_solid_ok == "ok", s_solid_ok)
    s_float = status(1.5, solid_tip)  # a float the rim allowance alone never sees
    check("fires on a small float over a solid face (the seat read)",
          s_float.startswith("adrift") and "behind" in s_float, s_float)


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


# ── routing guards: a path short of what it needs is drawn and recorded ──────
def test_routing_guards() -> None:
    """A run that cannot hold its collet discipline is drawn at what it has and its shortfall
    written to `_routing.BLOCKED`. These are the controls on that record — that a clean run
    leaves it empty, and that each shortfall lands in it with the run still swept, so the tangle
    a moved body makes can be looked at instead of ending the build."""
    import _routing as R

    print("routing guards (bend radius, ambiguous close, folded close)")

    # Two ports facing each other down a corridor, offset along x: exit stub → across → close.
    # Hand-built fixture geometry, like the defect boxes above.
    span, depth = 200.0, 130.0
    bend = R.BEND_RATIO * 6.35

    def fixture():
        R._frames.clear()
        R.BLOCKED.clear()
        R.frame("A", box(0, 0, 0), {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
        R.frame("B", box(0, 0, 0), {"p": ((span, depth, 0.0), "y-", 6.35)})

    # `across` turns perpendicular to the exit stub, so the stub is its own leg; a constraint
    # continuing the stub's direction straightens into it.
    across = {"x": span}

    # The control first: a stub of one full bend radius seats its turn, and the run is clean.
    fixture()
    try:
        run = R.route("t", "A.p", across, "B.p")
        check("silent on legs that clear the bend radius",
              len(run.bends) >= 2 and not R.BLOCKED, f"{len(run.bends)} bends")
    except ValueError as e:
        check("silent on legs that clear the bend radius", False, str(e)[:70])

    # A stub shorter than the bend radius cannot seat the whole turn off the port — so the corner
    # takes what the stub holds and the gate reads the tighter radius, rather than the build dying
    # on a leg the pack is entitled to shorten.
    fixture()
    short = R.route("t", "A.p", across, "B.p", stub=bend / 3.0)
    check("a leg too short for the cap seats a tighter corner, not a raise",
          short.tightest <= bend / 3.0 + 1e-6 and short.tightest > 0,
          f"stub R{bend / 3.0:.2f} → corner R{short.tightest:.2f} under a cap of R{short.bend:.2f}")

    # Two coordinates still differing at the close = an ambiguous corner order. The run is drawn
    # as one leg across all of them and the ambiguity recorded against it.
    fixture()
    amb = R.route("t", "A.p", "B.p")
    check("records the ambiguous close, and still draws the run",
          "needs another constraint" in R.BLOCKED.get("t", "")
          and amb.pts[-1] == (span, depth, 0.0),
          R.BLOCKED.get("t", "no record")[:58])

    # A path nearer the port than its own approach stub would back out and come straight back, so
    # the stub is drawn at the room the path leaves it and the shortfall says how much that was.
    fixture()
    fold = R.route("t", "A.p", {"y": depth - bend / 2.0}, across, "B.p", stub=(bend, bend * 2.0))
    check("records the folded close, and closes on the port anyway",
          "folds" in R.BLOCKED.get("t", "") and fold.pts[-1] == (span, depth, 0.0),
          R.BLOCKED.get("t", "no record")[:58])

    # A corner whose legs are wholly spent on its neighbours seats nothing; it is drawn square
    # and the run recorded, so `bend-radius` grades the kink instead of the build ending on it.
    fixture()
    kink = R.route("t", "A.p", across, "B.p", stub=(1e-7, bend), bend=bend)
    check("records a corner that seats no radius, and draws it square",
          "seats no radius" in R.BLOCKED.get("t", "") and min(kink.radii.values()) == 0.0,
          R.BLOCKED.get("t", "no record")[:58])
    R._frames.clear()
    R.BLOCKED.clear()


# ── bend-radius: the grade reads the same inequality the guard raises on ─────
def test_bend_radius() -> None:
    """`leg_caps` claims the largest radius a centreline seats, and the gate grades against it.
    That claim is only worth anything if it is the SAME bound `_bends` raises on — a second
    implementation of the arithmetic would drift from the guard and the card would grade a run
    buildable that the build refuses. So the control is a round trip: measure the cap, then
    author the run at it and just past it, and require the guard to agree at both."""
    import _routing as R

    print("bend radius (the cap, its classification, the grades)")
    span, depth, stub = 200.0, 130.0, 40.0

    def fixture():
        R._frames.clear()
        R.frame("A", box(0, 0, 0), {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
        R.frame("B", box(0, 0, 0), {"p": ((span, depth, 0.0), "y-", 6.35)})

    # An explicit stub, so the two lead legs are fixed lengths and the centreline does not move
    # when the radius does — otherwise the default stub (one bend radius) rescales the run.
    def at(r):
        fixture()
        return R.route("t", "A.p", {"x": span}, "B.p", stub=stub, bend=r)

    run = at(6.0)
    caps = R.leg_caps(run)
    seat = min(c[0] for c in caps)
    where = {c[1]: c[4] for c in caps}
    check("the two end legs are leads, the rest interior",
          where.get(0) == "lead" and where.get(len(run.pts) - 2) == "lead"
          and all(v == "interior" for k, v in where.items() if k not in (0, len(run.pts) - 2)),
          " ".join(f"{k}:{v}" for k, v in sorted(where.items())))

    got = at(seat)
    check("every corner reaches the cap leg_caps measured",
          all(v >= seat - 1e-6 for v in got.radii.values()),
          f"R{seat:.2f} → {sorted(round(v, 2) for v in got.radii.values())}")
    # Past what the legs seat, a corner takes less — it does not raise. A cap is a ceiling, and
    # the floor under it is the geometry, so a part that moves re-seats rather than failing the
    # build and `bend-radius` is what says the corner got too tight.
    past = at(seat * 2.0)
    check("past the cap the corners seat less rather than raising",
          past.tightest <= seat + 1e-6 and past.pts == got.pts,
          f"cap R{seat * 2:.2f} → tightest R{past.tightest:.2f}, centreline unmoved")
    # A cap BELOW what the legs seat is honoured — that is how a turn is authored deliberately
    # tighter than its room.
    tight = at(seat / 2.0)
    check("a cap under what the legs seat holds every corner to it",
          all(abs(v - seat / 2.0) < 1e-6 for v in tight.radii.values()),
          f"cap R{seat / 2:.2f} → {sorted(round(v, 2) for v in tight.radii.values())}")

    # The whole point of per-corner: a corner held down by its OWN cap leaves the rest of the leg
    # it shares to the neighbour, which then rises past what an equal share would have given it.
    corners = sorted(got.radii)
    a, b = corners[0], corners[1]
    held = at({a: 1.0})
    check("a corner held by its cap leaves its leg to the neighbour",
          held.radii[a] <= 1.0 + 1e-6 and held.radii[b] > got.radii[b] + 1e-6,
          f"corner {a} capped R1.0 → corner {b} rises R{got.radii[b]:.2f} → R{held.radii[b]:.2f}")

    # A cap naming something that is not a corner is an author's mistake, not a silent no-op.
    try:
        at({max(corners) + 99: 5.0})
        check("a cap on a waypoint that is not a corner raises", False, "no raise")
    except ValueError as e:
        check("a cap on a waypoint that is not a corner raises", "not a corner" in str(e), str(e)[:58])

    # The grade bands, on the stock the fixture's Ø6.35 refrigerant runs are drawn in.
    copper = sc.stock_of("refrigerant", 6.35)
    check("a run at its stock's minimum grades B (buildable, no more)",
          sc.grade_of(copper.min_bend / copper.min_bend) == "B", f"R{copper.min_bend:g}")
    check("half the minimum grades F", sc.grade_of(0.5 - 1e-9) == "F")
    try:
        sc.stock_of("fluid", 3.0)
        check("an undeclared stock raises rather than being graded", False, "no raise")
    except KeyError as e:
        check("an undeclared stock raises rather than being graded", "no stock declared" in str(e))

    # A run with no corner has no bend to grade, and must not be counted as a failing one.
    # Two collets facing each other down one line: the whole run is a single straight length.
    R._frames.clear()
    R.frame("A", box(0, 0, 0), {"p": ((0.0, 0.0, 0.0), "y+", 6.35)})
    R.frame("B", box(0, 0, 0), {"p": ((0.0, depth, 0.0), "y-", 6.35)})
    straight = R.route("s", "A.p", "B.p", stub=0.0, bend=6.0)
    rows = sc.bend_radii([straight, at(6.0)])
    check("a straight run is ungraded, a bent one is graded",
          len(rows) == 2 and [d["grade"] is None for d in rows].count(True) == 1
          and next(d["grade"] for d in rows if d["id"] == "s") is None,
          f"{straight.id}: {len(straight.bends)} bends")
    bent = next(d for d in rows if d["grade"])
    check("reach is measured without the leads seat counts",
          bent["reach"] is not None and bent["seat"] is not None and bent["reach"] >= bent["seat"],
          f"seat R{bent['seat']:.2f} ≤ reach R{bent['reach']:.2f}")
    # The need record rides every row: what the run CONNECTS, beside what pins it. A straight
    # spends its path on its span exactly; the bent fixture's span is its endpoint distance
    # split by axis, and its drawn path exceeds it.
    sn = next(d for d in rows if d["id"] == "s")["need"]
    check("need: a straight run's path is its span",
          abs(sn["detour"] - 1.0) < 1e-9, f"detour {sn['detour']}")
    n = bent["need"]
    check("need: span is the endpoint distance, split by axis",
          abs(n["span"] - (span * span + depth * depth) ** 0.5) < 0.01
          and n["axis"] == {"x": span, "y": depth, "z": 0.0} and n["detour"] > 1.0,
          f"span {n['span']}, path {n['path']} = {n['detour']}× over Δ({span:g}, {depth:g}, 0)")
    R._frames.clear()


def test_divider_reach() -> None:
    """`divider_reach` is the only thing standing between `DIVIDER_LEAN` and the front of the
    machine, and the lean is a number a future session will want to push. What stops it is
    each leg's two corners: an R`WBEND` arc eats `WBEND · tan(lean/2)` off every straight it
    meets, from both ends of the leaning run at once. These are the controls on that bound —
    that it is silent where the tube still runs straight, and records on each of the two ends
    it can run out at, so nobody has to read the reach as a number somebody picked."""
    import _contents as c

    print("divider reach (the lean's own bound)")
    lean, lead = c.DIVIDER_LEAN, c.DIVIDER_LEG_LEAD
    keep = dict(c.SHORT)
    try:
        c.SHORT.clear()
        check("silent at the lean the machine is built to",
              c.divider_reach() > 2 * lead and not c.SHORT,
              f"lean {lean}° → reach {c.divider_reach():.2f} mm")

        # The leaning run: steepen far enough and the two arcs meet in the middle of it.
        c.SHORT.clear()
        c.DIVIDER_LEAN = 85.0
        c.divider_reach()
        check("records the leaning run that cannot seat both arcs",
              any("the leaning run" in v for v in c.SHORT.values()),
              "; ".join(c.SHORT)[:58] or "no record")

        # The collet stub: the same arc eats into the 6 mm straight off the valve's own port.
        c.SHORT.clear()
        c.DIVIDER_LEAN, c.DIVIDER_LEG_LEAD = 60.0, 3.5
        c.divider_reach()
        check("records the collet stub that cannot seat its arc",
              any("each collet stub" in v for v in c.SHORT.values()),
              "; ".join(c.SHORT)[:58] or "no record")
    finally:
        c.DIVIDER_LEAN, c.DIVIDER_LEG_LEAD = lean, lead
        c.SHORT.clear()
        c.SHORT.update(keep)


# ── room-holds: a derivation short of its own stated band = a red gate ───────
def test_room_holds() -> None:
    """`room-holds` carries what a pose could not get. The derivations fill `_contents.SHORT` as
    the pack is built and this gate reads it, so the control is the round trip: an empty record
    passes, one entry turns the gate red and its measurement reaches the card's detail."""
    import _contents as c

    print("room-holds (a derived pose has the band it states)")
    bed, inner = (325.0, 320.0, 320.0), (0.0, 100.0, 0.0, 100.0, 0.0, 100.0)
    solids, pieces = {"a": box(0, 0, 0)}, {"piece": box(200, 0, 0)}
    keep = dict(c.SHORT)
    try:
        c.SHORT.clear()
        clean = next(k for k in sc.build_scorecard(solids, pieces, bed, inner).checks
                     if k.id == "room-holds")
        check("passes when every derived pose got its band", clean.status == "pass",
              f"status={clean.status}, {clean.value}")

        c.SHORT["a-band"] = "the band is 2.50 mm and what stands in it wants 7.35"
        red = next(k for k in sc.build_scorecard(solids, pieces, bed, inner).checks
                   if k.id == "room-holds")
        check("goes red on a pose short of its own band, with the measurement",
              red.status == "fail" and any("7.35" in d for d in red.detail),
              f"status={red.status}, {red.value}")
    finally:
        c.SHORT.clear()
        c.SHORT.update(keep)


def main() -> None:
    print("── enclosure scorecard self-test " + "─" * 20)
    if not sc._HAVE_EXACT:
        print("  note: exact solid-distance kernel unavailable; clearance uses bbox estimate")
    for t in (test_pack_closes, test_lines_clear, test_clearance_floor, test_fit_bed,
              test_seams_mate, test_placement, test_port_leads, test_located_faces,
              test_scorecard_end_to_end, test_routing_guards, test_bend_radius,
              test_divider_reach, test_room_holds):
        t()
    print("─" * 53)
    if _failures:
        raise SystemExit(f"{_failures} gate(s) did not fire as designed — the scorecard has a blind spot")
    print("every gate fires on a real defect and stays silent on its control")


if __name__ == "__main__":
    main()
