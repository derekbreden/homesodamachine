"""The runs the stock cannot bend, worst first — and the bodies each one stands on.

`need.py` reports what a run connects before what it rides. `room.py` reports what a band
holds before anything is put in it. This ranks the RUNS, the way the scorecard does, and
against each one names its two end bodies and how much else those bodies carry.

    python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
    python3 .../ugly.py fluid-20          # one run: every corner, and the leverage on it
    python3 .../ugly.py --bodies          # the same debt summed onto bodies
    python3 .../ugly.py --held            # whose mount joint does not hold
    python3 .../ugly.py selftest

Worst ratio first.

Rows are runs. A body appears only as one end of a run, with the `[debt]` beside it counting
the other runs the same move would pay off.

THIS IS NOT A SEARCH. It ranks no candidate poses, finds no optimum and moves nothing. It
reads the committed sidecar `enclosure-assembly.scorecard.json` — the same figures the card
carries — so it costs a file read and reports the last build. The footer says when that build
ran, and says STALE when placement or routing source has been written since.

`binding` is the corner holding the run down, and its kind is what the corner needs:

- `reach` — the corner sits at the ceiling its own shorter leg imposes, `min(leg)/tan(turn/2)`.
  `of` gives the leg one stock arc wants there, `cap * tan(turn/2)`. That length is NECESSARY
  and not sufficient: a leg reaching it clears this corner's own bound and still answers to
  whatever it shares the leg with.
- `share` — the corner sits BELOW that ceiling, so a turning neighbour is taking part of the
  leg. Lengthening the leg alone does not hand this corner the difference.
- `REVERSAL` — the run turns back on itself. No leg length seats any radius through 180°, so
  there is no `of` to report, and the length of the legs either side of it is not the figure
  in play.

`debt` is what a body owes: for each run standing on it that the stock cannot bend, how far
under 1.0 that run's `ratio` sits, summed. A run counts on BOTH its ends.

What this does not answer: whether a body may move, what it would cost to move it, or where
it would go — `room.py` reports the bands, `scorecard.pose` says whose pose is an input, and
`pack-closes` / `lines-clear` / `bend-radius` are the oracle. Every figure here is a number
off the sidecar; what a run looks like in the machine is `tools/look.sh`.
"""

import json
import math
import os
import sys

SIDECAR = "enclosure-assembly.scorecard.json"
BAD = ("F", "D")
SECTIONS = ("runs", "bodies", "held")
# A turn this severe reverses the run. `tan(turn/2)` runs away here, so the leg a stock arc
# would want stops being a length and the ceiling stops being a bound worth printing.
REVERSAL_TURN = 179.0


def _pl(rows, one, many) -> str:
    """Singular when one row, plural otherwise."""
    return one if len(rows) == 1 else many


def _card(path=None) -> dict:
    """The committed sidecar, read from beside this file unless pointed elsewhere."""
    p = path or os.path.join(os.path.dirname(os.path.abspath(__file__)), SIDECAR)
    with open(p) as f:
        return json.load(f)


def _written_since(card, here=None) -> str:
    """Placement or routing source written after the sidecar was built, as a names string.
    The sidecar's own `source.commit` is the commit the build RAN ON, one behind the commit
    that carries it, so freshness is read off the files rather than off that hash."""
    here = here or os.path.dirname(os.path.abspath(__file__))
    sidecar = os.path.join(here, SIDECAR)
    if not os.path.exists(sidecar):
        return ""
    built = os.path.getmtime(sidecar)
    late = [n for n in ("_contents.py", "_lines.py", "_placing.py", "_routing.py")
            if os.path.exists(os.path.join(here, n))
            and os.path.getmtime(os.path.join(here, n)) > built]
    return ", ".join(late)


def legs(run) -> list:
    """The run's leg lengths, port to port. Corner `i` stands between legs `i` and `i+1`."""
    cs = run["corners"]
    if not cs:
        return []
    return [cs[0]["legs"][0]] + [c["legs"][1] for c in cs]


def ceiling(corner, leg_a, leg_b) -> float:
    """The largest radius this corner's own two legs can seat, whatever it shares them with."""
    t = math.tan(math.radians(corner["turn"]) / 2)
    return float("inf") if t < 1e-9 else min(leg_a, leg_b) / t


def binding(run) -> dict | None:
    """The corner holding the run down: lowest radius, its kind, the leg it stands on, and
    the leg one stock arc would want there. `kind` is `reversal` through 180°, `reach` when
    the corner sits at the ceiling its own shorter leg imposes, and `share` when it sits
    below that ceiling with a turning neighbour taking part of the leg."""
    cs = run["corners"]
    if not cs:
        return None
    i, c = min(enumerate(cs), key=lambda ic: ic[1]["radius"])
    L = legs(run)
    a, b = L[i], L[i + 1]
    t = math.tan(math.radians(c["turn"]) / 2)
    cap = ceiling(c, a, b)
    # The sidecar rounds legs to 2 dp, so the bound carries that much slack.
    at_ceiling = c["radius"] >= cap - 0.02
    reversal = c["turn"] >= REVERSAL_TURN
    return {
        "at": c["at"],
        "turn": c["turn"],
        "radius": c["radius"],
        "grade": c["grade"],
        "kind": "reversal" if reversal else ("reach" if at_ceiling else "share"),
        "leg": round(min(a, b), 2),
        "ceiling": None if reversal else round(cap, 2),
        "wants": None if reversal else round(run["minBend"] * t, 2),
        "at_ceiling": at_ceiling,
    }


def bodies(bends) -> list:
    """Every component a sub-stock run stands on, worst debt first."""
    seen = {}
    for r in bends:
        if r["grade"] is None:
            continue
        for end in (r["frm"], r["to"]):
            name = end.split(".")[0]
            rec = seen.setdefault(name, {"body": name, "runs": [], "bad": []})
            rec["runs"].append(r)
            if r["grade"] in BAD:
                rec["bad"].append(r)
    out = []
    for rec in seen.values():
        if not rec["bad"]:
            continue
        rec["debt"] = round(sum(1.0 - min(1.0, r["ratio"]) for r in rec["bad"]), 2)
        rec["ids"] = sorted(r["id"] for r in rec["bad"])
        out.append(rec)
    out.sort(key=lambda rec: (-rec["debt"], rec["body"]))
    return out


def unmounted(card) -> list:
    """Components whose joint does not hold, biggest box first. `joint` is the scorecard's
    own state: `adrift` names a carrier whose measurement fails or was never taken, and a
    blank names no carrier at all. A row that holds is off the board."""
    pose = {p["name"]: p["pose"] for p in card["poses"]}
    shape = {s["component"]: s for s in card["shapes"]}
    out = []
    for m in card["mounts"]:
        if m.get("joint") == "holds":
            continue
        s = shape.get(m["component"], {})
        vol = sum(abs((b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2]))
                  for b in s.get("boxes", []))
        miss = [c["label"] for c in m.get("checks", []) if not c["ok"]]
        out.append({"component": m["component"], "kind": m["kind"],
                    "pose": pose.get(m["component"], "—"),
                    "joint": m.get("joint") or "none",
                    "by": m.get("by"), "miss": miss,
                    "cm3": round(vol / 1000.0, 1), "fill": s.get("fill")})
    out.sort(key=lambda r: -r["cm3"])
    return out


def standing(card) -> dict:
    """The whole machine as the few numbers an iteration is judged on: gates passing, corners
    at their stock's minimum, runs the stock cannot bend, and the summed debt."""
    gates = [c for c in card["checks"] if c["kind"] == "gate" and c.get("active")]
    ok = tot = 0
    for r in card["bends"]:
        a, b = at_spec(r)
        ok, tot = ok + a, tot + b
    return {
        "gates": sum(1 for g in gates if g["status"] == "pass"),
        "of_gates": len(gates),
        "spec": ok,
        "of_corners": tot,
        "unbendable": sum(1 for r in card["bends"] if r["grade"] in BAD),
        "debt": round(sum(1.0 - min(1.0, r["ratio"])
                          for r in card["bends"] if r["grade"] in BAD), 2),
    }


def verdict(before: dict, after: dict) -> tuple:
    """Whether an iteration may stand, as (ok, reason). A gate that was passing and now is
    not ends it outright. Otherwise the machine has to be further along than it was: more
    corners at spec, or the same corners and less debt."""
    if after["gates"] < before["gates"]:
        return False, (f"REGRESSED — gates {before['gates']}/{before['of_gates']} → "
                       f"{after['gates']}/{after['of_gates']}")
    if after["spec"] > before["spec"]:
        return True, f"gained {after['spec'] - before['spec']} corners at spec"
    if after["spec"] < before["spec"]:
        return False, f"REGRESSED — lost {before['spec'] - after['spec']} corners at spec"
    if after["debt"] < before["debt"] - 0.005:
        return True, f"debt {before['debt']} → {after['debt']}"
    if after["debt"] > before["debt"] + 0.005:
        return False, f"REGRESSED — debt {before['debt']} → {after['debt']}"
    return False, "NO CHANGE — nothing moved"


def _card_at(ref: str, here=None) -> dict | None:
    """The sidecar as it stood at a git ref, or None when it cannot be read there."""
    import subprocess
    here = here or os.path.dirname(os.path.abspath(__file__))
    top = subprocess.run(["git", "-C", here, "rev-parse", "--show-toplevel"],
                         capture_output=True, text=True)
    if top.returncode:
        return None
    rel = os.path.relpath(os.path.join(here, SIDECAR), top.stdout.strip())
    got = subprocess.run(["git", "-C", here, "show", f"{ref}:{rel}"],
                         capture_output=True, text=True)
    if got.returncode:
        return None
    try:
        return json.loads(got.stdout)
    except json.JSONDecodeError:
        return None


def at_spec(run) -> tuple:
    """Corners at or above the stock's minimum, over the run's corner count."""
    cs = run["corners"]
    return sum(1 for c in cs if c["radius"] >= run["minBend"] - 1e-6), len(cs)


def _end(name: str, debt: dict) -> str:
    """A run's end body, carrying its debt when it has any."""
    d = debt.get(name)
    return f"{name}[{d:.1f}]" if d else name


def table(card, only=(), show=("runs", "held")) -> str:
    """The board."""
    src = card.get("source", {})
    bends = card["bends"]
    debt = {b["body"]: b["debt"] for b in bodies(bends)}
    # Naming a run asks which bodies could move for it, so it selects its own two ends in
    # every section below the run rows.
    kin = set(only) | {e.split(".")[0] for r in bends if r["id"] in only
                       for e in (r["frm"], r["to"])}
    out = []

    if "runs" in show:
        rows = [r for r in bends if r["grade"] in BAD
                and (not only or r["id"] in only
                     or any(e.split(".")[0] in only for e in (r["frm"], r["to"])))]
        rows.sort(key=lambda r: (r["ratio"], r["id"]))
        out.append(f"{'ratio':>6} {'R':>7} {'of':>6} {'spec':>6} {'det':>6}  "
                   f"{'binding':<26} run")
        for r in rows:
            n, bd = r["need"], binding(r)
            ok, tot = at_spec(r)
            det = "  —  " if n["detour"] is None else f"{n['detour']:4.2f}×"
            if not bd:
                b = "—"
            elif bd["kind"] == "reversal":
                b = f"c{bd['at']} REVERSAL {bd['turn']:.0f}°"
            else:
                b = (f"c{bd['at']} {bd['kind']} {bd['turn']:.0f}° "
                     f"{bd['leg']:.1f} of {bd['wants']:.1f}")
            out.append(f"{r['ratio']:6.2f} {r['radius']:7.2f} {r['minBend']:6.1f} "
                       f"{f'{ok}/{tot}':>6} {det:>6}  {b:<26} {r['id']:<10} "
                       f"{_end(r['frm'].split('.')[0], debt)} → "
                       f"{_end(r['to'].split('.')[0], debt)}")
        out.append(f"{len(rows)} {_pl(rows, 'run', 'runs')} the stock cannot bend, worst first. "
                   f"`binding` is the corner holding each one down and what it needs — `reach` "
                   f"is short of leg, `share` is a neighbour taking the leg, `REVERSAL` turns "
                   f"back on itself. `[n]` on an end body is what else that body carries.")

    if "bodies" in show:
        rows = [b for b in bodies(bends) if not kin or b["body"] in kin]
        if out:
            out.append("")
        out.append(f"{'debt':>6} {'bad':>7}  body")
        for b in rows:
            out.append(f"{b['debt']:6.2f} {len(b['bad']):3d}/{len(b['runs']):<3d}  "
                       f"{b['body']:<26} {' '.join(b['ids'])}")
        out.append(f"{len(rows)} {_pl(rows, 'body', 'bodies')} standing at the end of a "
                   f"sub-stock run, each run counted on both its ends. This is the same debt "
                   f"the run rows carry, summed — a run is what gets worked, and this says "
                   f"which move would land on more than one of them.")

    if "held" in show:
        rows = [u for u in unmounted(card) if not kin or u["component"] in kin]
        if out:
            out.append("")
        out.append(f"{'cm³':>8} {'fill':>5} {'joint':>7} {'pose':>12}  component")
        for u in rows:
            fill = "  —  " if u["fill"] is None else f"{u['fill']:5.2f}"
            tail = (f"  → {u['by']}: {'; '.join(u['miss'])}" if u["by"] else "")
            out.append(f"{u['cm3']:8.1f} {fill} {u['joint']:>7} {u['pose']:>12}  "
                       f"{u['component']}{tail}"
                       + ("  (placeholder)" if u["kind"] != "real" else ""))
        out.append(f"{len(rows)} {_pl(rows, 'component', 'components')} whose joint does not "
                   f"hold, biggest box first. `adrift` names a carrier and fails or never "
                   f"took the measurement; `none` names no carrier at all. A box is larger "
                   f"than its part — `fill` says how much of it is material.")

    out.append("")
    out.append(f"sidecar built {src.get('generated', '?')} on {str(src.get('commit'))[:8]}"
               + (f" — STALE, {stale} written since; rebuild before you read this"
                  if (stale := _written_since(card)) else ""))
    return "\n".join(out)


def selftest() -> int:
    failures = 0

    def check(label, ok, detail=""):
        nonlocal failures
        mark = "✓" if ok else "✗"
        if not ok:
            failures += 1
        print(f"  {mark} {label}" + (f" — {detail}" if detail else ""))

    def run(rid, ratio, grade, corners, frm="A.p", to="B.p", cap=25.4):
        return {"id": rid, "kind": "fluid", "frm": frm, "to": to, "radius": ratio * cap,
                "cap": cap, "minBend": cap, "ratio": ratio, "grade": grade,
                "need": {"span": 1.0, "path": 1.0, "detour": 1.0}, "corners": corners}

    def corner(at, turn, radius, la, lb):
        return {"at": at, "turn": turn, "radius": radius, "ratio": radius / 25.4,
                "grade": "F", "legs": [la, lb]}

    print("ugly (leg ceiling, body debt, held census)")

    # A square corner's ceiling is its own shorter leg: tan(45°) = 1.
    square = corner(1, 90.0, 11.03, 11.03, 53.16)
    check("a 90° corner's ceiling is its shorter leg",
          abs(ceiling(square, 11.03, 53.16) - 11.03) < 1e-6,
          f"{ceiling(square, 11.03, 53.16):.2f}")

    # A shallower turn seats more radius on the same leg.
    shallow = corner(1, 38.0, 5.0, 11.03, 53.16)
    check("a shallower turn seats more radius on the same leg",
          ceiling(shallow, 11.03, 53.16) > 30.0,
          f"38° on an 11.03 leg reaches {ceiling(shallow, 11.03, 53.16):.2f}")

    # Legs chain: corner i stands between legs i and i+1, so an interior leg is shared.
    chained = run("t", 0.22, "F", [corner(1, 90.0, 11.03, 11.03, 53.16),
                                   corner(2, 90.0, 25.4, 53.16, 32.07),
                                   corner(3, 90.0, 5.52, 32.07, 11.03)])
    check("legs chain port to port", legs(chained) == [11.03, 53.16, 32.07, 11.03],
          f"{legs(chained)}")

    b = binding(chained)
    check("the binding corner is the lowest radius", b["at"] == 3 and b["radius"] == 5.52,
          f"corner {b['at']} at R{b['radius']}")
    check("a corner below its own ceiling reads as sharing",
          not b["at_ceiling"] and b["ceiling"] == 11.03,
          f"R{b['radius']} under a ceiling of {b['ceiling']}")
    check("a corner at its own ceiling reads as leg-bound",
          binding(run("t", 0.43, "F", [corner(1, 90.0, 11.03, 11.03, 53.16)]))["at_ceiling"])
    check("`wants` is the leg one stock arc needs at that corner", b["wants"] == 25.4,
          f"{b['wants']} for a 90° at cap 25.4")
    check("a corner short of its own leg reads reach",
          binding(run("t", 0.43, "F", [corner(1, 90.0, 11.03, 11.03, 53.16)]))["kind"] == "reach")
    check("a corner under its ceiling reads share", b["kind"] == "share", b["kind"])

    # A 180° turn seats no radius at any leg length, so the leg figures stop being the story.
    rev = binding(run("t", 0.0, "F", [corner(1, 180.0, 0.0, 4.0, 53.16),
                                      corner(2, 90.0, 16.2, 53.16, 32.07)]))
    check("a reversal reads reversal", rev["kind"] == "reversal" and rev["at"] == 1)
    check("a reversal reports no leg a stock arc wants",
          rev["wants"] is None and rev["ceiling"] is None,
          f"wants {rev['wants']}, ceiling {rev['ceiling']}")

    spec = run("t", 0.5, "F", [corner(1, 90.0, 25.4, 30.0, 30.0),
                               corner(2, 90.0, 5.0, 30.0, 5.0)])
    check("corners at spec counts against the run's cap", at_spec(spec) == (1, 2),
          f"{at_spec(spec)}")
    check("an end body carries its debt inline",
          _end("tee-y-f", {"tee-y-f": 2.31}) == "tee-y-f[2.3]"
          and _end("clean", {}) == "clean")

    # The ratchet an unattended iteration is judged on.
    def state(gates, spec, debt):
        return {"gates": gates, "of_gates": 11, "spec": spec, "of_corners": 100,
                "unbendable": 0, "debt": debt}

    base = state(10, 45, 12.0)
    check("a lost gate ends it whatever else improved",
          verdict(base, state(9, 60, 1.0))[0] is False,
          verdict(base, state(9, 60, 1.0))[1])
    check("more corners at spec stands", verdict(base, state(10, 46, 12.0))[0] is True)
    check("fewer corners at spec is backed out",
          verdict(base, state(10, 44, 0.1))[0] is False)
    check("same corners and less debt stands",
          verdict(base, state(10, 45, 11.5))[0] is True)
    check("same corners and more debt is backed out",
          verdict(base, state(10, 45, 12.5))[0] is False)
    check("no change is not progress", verdict(base, state(10, 45, 12.0))[0] is False,
          verdict(base, state(10, 45, 12.0))[1])
    check("a gained gate alone is not enough without geometry moving",
          verdict(base, state(11, 45, 12.0))[0] is False)

    # Debt sums a run onto both its ends, and a body with no bad run is off the board.
    bs = bodies([run("r1", 0.2, "F", [], "tee.a", "tray.b"),
                 run("r2", 0.3, "F", [], "tee.c", "pump.d"),
                 run("r3", 1.0, "B", [], "tee.e", "clean.f")])
    got = {b["body"]: b["debt"] for b in bs}
    check("a run's debt lands on both its ends",
          got["tray"] == 0.8 and got["pump"] == 0.7, f"{got}")
    check("debt sums over a body's bad runs", got["tee"] == 1.5, f"tee {got['tee']}")
    check("a body with no bad run is off the board", "clean" not in got, f"{sorted(got)}")
    check("worst debt first", [b["body"] for b in bs][0] == "tee")

    # A straight (no corners, grade None) is not a run the stock cannot bend.
    check("a graded straight is not debt",
          not bodies([run("s", 1.0, None, [], "a.p", "b.p")]))

    held = unmounted({"mounts": [{"component": "big", "held": "none", "kind": "real",
                                  "joint": "adrift", "by": "shell",
                                  "checks": [{"label": "no joint measured", "ok": False}]},
                                 {"component": "small", "held": "none", "kind": "real"},
                                 {"component": "done", "held": "rails", "kind": "real",
                                  "joint": "holds"}],
                   "poses": [{"name": "big", "pose": "provisional"}],
                   "shapes": [{"component": "big", "boxes": [[0, 0, 0, 100, 100, 100]],
                               "fill": 0.5},
                              {"component": "small", "boxes": [[0, 0, 0, 10, 10, 10]],
                               "fill": 1.0}]})
    check("a joint that holds is off the census", [u["component"] for u in held] == ["big", "small"],
          f"{[u['component'] for u in held]}")
    check("a declared carrier whose measurement fails reads adrift",
          held[0]["joint"] == "adrift" and held[0]["miss"] == ["no joint measured"])
    check("no carrier at all reads none", held[1]["joint"] == "none" and held[1]["by"] is None)
    check("biggest box first", held[0]["cm3"] == 1000.0 and held[1]["cm3"] == 1.0,
          f"{held[0]['cm3']} then {held[1]['cm3']}")
    check("pose provenance rides each row", held[0]["pose"] == "provisional"
          and held[1]["pose"] == "—")

    # The bound is the property the board rests on: no corner in the live pack exceeds its
    # own legs' ceiling. The sidecar rounds legs to 2 dp, hence the tolerance.
    try:
        card = _card()
    except FileNotFoundError:
        print("  · sidecar absent — bound check skipped")
    else:
        over = [(r["id"], c["at"]) for r in card["bends"]
                for i, c in enumerate(r["corners"])
                if c["radius"] > ceiling(c, legs(r)[i], legs(r)[i + 1]) + 0.02]
        n = sum(len(r["corners"]) for r in card["bends"])
        check(f"no corner in the pack exceeds its own legs' ceiling ({n} corners)",
              not over, f"{over[:4]}")

    print("PASS" if failures == 0 else f"FAIL — {failures}")
    return 0 if failures == 0 else 1


def main(argv) -> int:
    if argv and argv[0] == "selftest":
        return selftest()

    # --since <ref>: judge the tree against where it stood. Exit 0 when the iteration may
    # stand, 1 when it may not — an unattended loop reads the status, not the text.
    if "--since" in argv:
        i = argv.index("--since")
        ref = argv[i + 1]
        was = _card_at(ref)
        if was is None:
            print(f"no sidecar at {ref} — nothing to judge against")
            return 1
        before, after = standing(was), standing(_card())
        ok, why = verdict(before, after)
        for label, s in (("was", before), ("now", after)):
            print(f"{label}  gates {s['gates']}/{s['of_gates']}  "
                  f"corners at spec {s['spec']}/{s['of_corners']}  "
                  f"unbendable {s['unbendable']}  debt {s['debt']}")
        print(f"{'STANDS' if ok else 'BACK IT OUT'} — {why}")
        return 0 if ok else 1

    show = [f[2:] for f in argv if f.startswith("--")]
    # An unrecognised flag prints an empty board and says nothing is wrong, which reads as a
    # pass to anything running this without a person watching.
    if bad := [f for f in show if f not in SECTIONS]:
        print(f"unknown flag: {' '.join('--' + f for f in bad)}\n"
              f"known: {' '.join('--' + s for s in SECTIONS)} --since <ref>")
        return 2
    only = {a for a in argv if not a.startswith("--")}
    # Named a run or a body: show the runs, the bodies carrying them, and the mount rows.
    print(table(_card(), only=only,
                show=show or (["runs", "bodies", "held"] if only else ["runs", "held"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
