"""What is contorted, worst first — and which BODY carries it.

`need.py` reports what a run connects before what it rides. `room.py` reports what a band
holds before anything is put in it. This reports what is ugly against BODIES: every run the
stock cannot bend, summed onto the two components its ends stand on.

    python3 hardware/printed-parts/enclosure/enclosure-assembly/ugly.py
    python3 .../ugly.py --runs            # the runs behind the debt, worst first
    python3 .../ugly.py --held            # what still has no holder
    python3 .../ugly.py tee-y-f           # one body's rows
    python3 .../ugly.py selftest

Worst debt first.

THIS IS NOT A SEARCH. It ranks no candidate poses, finds no optimum and moves nothing. It
reads the committed sidecar `enclosure-assembly.scorecard.json` — the same figures the card
carries — so it costs a file read and reports the last build. The footer says when that build
ran, and says STALE when placement or routing source has been written since.

`debt` is what a body owes: for each run standing on it that the stock cannot bend, how far
under 1.0 that run's `ratio` sits, summed. A run counts on BOTH its ends. `3/3` beside a body
says every run it touches is sub-stock; `3/8` says most of its traffic is fine.

`ceiling` is the largest radius a corner's own two legs can seat — `min(leg) / tan(turn/2)`.
It is a bound, not a prediction: a corner sharing a leg with a turning neighbour gets less
than this, and the router allocates that share. A corner AT its ceiling is one whose own leg
is the whole of its limit. A corner BELOW its ceiling is competing with a neighbour, and what
binds it is the run's shape rather than any single leg.

`wants` is the leg one stock arc needs at that corner — `cap * tan(turn/2)` — against the leg
there now. It is a NECESSARY length and not a sufficient one: a leg reaching it clears this
corner's own bound and still answers to whatever it shares the leg with.

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
    """The corner holding the run down: lowest ratio, with the leg it stands on and the leg
    one stock arc would want there. `at_ceiling` is whether that leg is the whole of its
    limit — below it, a neighbour is taking the share."""
    cs = run["corners"]
    if not cs:
        return None
    i, c = min(enumerate(cs), key=lambda ic: ic[1]["radius"])
    L = legs(run)
    a, b = L[i], L[i + 1]
    t = math.tan(math.radians(c["turn"]) / 2)
    return {
        "at": c["at"],
        "turn": c["turn"],
        "radius": c["radius"],
        "grade": c["grade"],
        "leg": round(min(a, b), 2),
        "ceiling": round(ceiling(c, a, b), 2),
        "wants": round(run["minBend"] * t, 2),
        # The sidecar rounds legs to 2 dp, so the bound carries that much slack.
        "at_ceiling": c["radius"] >= ceiling(c, a, b) - 0.02,
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


def unheld(card) -> list:
    """Components with no holder, biggest box first — `mounted` as a census."""
    pose = {p["name"]: p["pose"] for p in card["poses"]}
    shape = {s["component"]: s for s in card["shapes"]}
    out = []
    for m in card["mounts"]:
        if m["held"] != "none":
            continue
        s = shape.get(m["component"], {})
        vol = sum(abs((b[3] - b[0]) * (b[4] - b[1]) * (b[5] - b[2]))
                  for b in s.get("boxes", []))
        out.append({"component": m["component"], "kind": m["kind"],
                    "pose": pose.get(m["component"], "—"),
                    "cm3": round(vol / 1000.0, 1), "fill": s.get("fill")})
    out.sort(key=lambda r: -r["cm3"])
    return out


def table(card, only=(), show=("bodies", "held")) -> str:
    """The board."""
    src = card.get("source", {})
    bends = card["bends"]
    out = []

    if "bodies" in show:
        rows = [b for b in bodies(bends) if not only or b["body"] in only]
        out.append(f"{'debt':>6} {'bad':>7}  body")
        for b in rows:
            out.append(f"{b['debt']:6.2f} {len(b['bad']):3d}/{len(b['runs']):<3d}  "
                       f"{b['body']:<26} {' '.join(b['ids'])}")
        out.append(f"{len(rows)} {_pl(rows, 'body', 'bodies')} carrying sub-stock runs. Each run "
                   f"is counted on both its ends — either end moving can be the fix.")

    if "runs" in show:
        rows = [r for r in bends if r["grade"] in BAD
                and (not only or any(e.split(".")[0] in only for e in (r["frm"], r["to"])))]
        rows.sort(key=lambda r: r["ratio"])
        if out:
            out.append("")
        out.append(f"{'ratio':>6} {'R':>7} {'cap':>6} {'det':>6} {'c':>3}  "
                   f"{'corner':>6} {'leg':>7} {'wants':>7}  run")
        for r in rows:
            n = r["need"]
            bd = binding(r)
            det = "  —  " if n["detour"] is None else f"{n['detour']:4.2f}×"
            if bd:
                mark = "=" if bd["at_ceiling"] else "<"
                corner = f"{bd['at']:>2}{mark}{bd['turn']:.0f}°"
                leg, wants = f"{bd['leg']:7.2f}", f"{bd['wants']:7.2f}"
            else:
                corner, leg, wants = "     —", "      —", "      —"
            out.append(f"{r['ratio']:6.2f} {r['radius']:7.2f} {r['minBend']:6.1f} {det:>6} "
                       f"{len(r['corners']):3d}  {corner:>6} {leg} {wants}  "
                       f"{r['id']:<10} {r['frm']} → {r['to']}")
        out.append(f"{len(rows)} {_pl(rows, 'run', 'runs')} the stock cannot bend. `corner` is the binding one: "
                   f"`=` its own leg is the whole of its limit, `<` a neighbour takes part of "
                   f"the share. `leg` is what it stands on, `wants` what one stock arc needs "
                   f"there — necessary, not sufficient.")

    if "held" in show:
        rows = [u for u in unheld(card) if not only or u["component"] in only]
        if out:
            out.append("")
        out.append(f"{'cm³':>8} {'fill':>5} {'pose':>12}  component")
        for u in rows:
            fill = "  —  " if u["fill"] is None else f"{u['fill']:5.2f}"
            out.append(f"{u['cm3']:8.1f} {fill} {u['pose']:>12}  {u['component']}"
                       + ("  (placeholder)" if u["kind"] != "real" else ""))
        out.append(f"{len(rows)} {_pl(rows, 'component', 'components')} with no holder, biggest "
                   f"box first. A box is larger "
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

    held = unheld({"mounts": [{"component": "big", "held": "none", "kind": "real"},
                              {"component": "small", "held": "none", "kind": "real"},
                              {"component": "done", "held": "rails", "kind": "real"}],
                   "poses": [{"name": "big", "pose": "provisional"}],
                   "shapes": [{"component": "big", "boxes": [[0, 0, 0, 100, 100, 100]],
                               "fill": 0.5},
                              {"component": "small", "boxes": [[0, 0, 0, 10, 10, 10]],
                               "fill": 1.0}]})
    check("a held component is off the census", [u["component"] for u in held] == ["big", "small"],
          f"{[u['component'] for u in held]}")
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
    show = [f[2:] for f in argv if f.startswith("--")]
    only = {a for a in argv if not a.startswith("--")}
    print(table(_card(), only=only, show=show or (["bodies", "runs", "held"] if only
                                                  else ["bodies", "held"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
