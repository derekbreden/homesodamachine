#!/usr/bin/env python3
"""Two publishes of the pointer file, merged the way a rebase needs them: main's pointers, plus yours.

    python3 tools/cad-artifacts/merge_pointers.py %O %A %B     # git merge driver: the result lands in %A
    python3 tools/cad-artifacts/merge_pointers.py selftest

`.gitattributes` names this driver for `hardware/cad-artifacts.json`, and `tools/push.py`
puts its command in a clone's config the first time it runs there (`merge.cadpointers.driver`), which
is how a fresh clone, cloud or laptop, comes to have it. git calls it whenever both sides of a
merge, rebase or cherry-pick moved the pointer file — which two publishes always do, because
`source.commit` and the bundle move on every one. Without it every concurrent publish stops on
the pointer file; with it the merge has one right answer, and this is it.

THE MEMBERS ARE THE POINTERS. `solids` and `sidecars` merge by key. A member one side left alone
takes the other side's hash, so a publish adds its members to main's without dropping main's. A
member both sides moved to different hashes takes the incoming side's — the publish being
brought in is the newer act — and is recorded under `unproven`, so the reconciler cuts it once
more from the merged source and the pointer file stops guessing. A member one side retired and the
other left alone is gone.

Each line's time (`moved`) travels with the hash the merged line carries, so a publish on any
machine can still tell its own newer cut from main's older bytes.

`source.commit` becomes the merge-base of the two sources: the debt it implies then covers what
either side built against, and over-reporting a cut is a rebuild nobody waits on where
under-reporting is a stale solid nobody is told about. `unproven` is the union of both records.
`release.objects` stands only when both sides had it, since it promises every member is on the
release by its own hash. The bundle is the one from the side that cut a new one, main's when
both did, and it is marked behind whenever the merged members are not the ones it holds.

The result is the bytes `pack.py` writes: its key order, its indentation, its escaping. Merging a
pointer file with itself gives the file back unchanged.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

POINTERS_REL = "hardware/cad-artifacts.json"

#: pack.py's own note, repeated so the merged record reads like one it wrote. The selftest holds
#: the two strings together.
UNPROVEN_NOTE = ("source.commit does not describe these members: an uncommitted path below reaches"
                 " the rule that cuts one, its rule would not cut, or an interactive publication"
                 " explicitly deferred that rule.")

#: The order pack.py seats the keys in; `unproven` sits after the commit it qualifies.
KEY_ORDER = ("_", "release", "source", "unproven", "bundle", "solids", "sidecars", "moved")


def merge_members(base: dict, ours: dict, theirs: dict) -> tuple[dict, list, list]:
    """`(merged, moved on both sides, notes)` for one path→hash map.

    Per key: equal on both sides stands; a side that left the key at its base value defers to
    the other; both moved to different values takes theirs and names the key."""
    base, ours, theirs = base or {}, ours or {}, theirs or {}
    out, both, notes = {}, [], []
    for key in sorted(set(base) | set(ours) | set(theirs)):
        vb, vo, vt = base.get(key), ours.get(key), theirs.get(key)
        if vo == vt:
            if vo is not None:
                out[key] = vo
        elif vt == vb:
            if vo is not None:
                out[key] = vo
        elif vo == vb:
            if vt is not None:
                out[key] = vt
        elif vt is None:
            out[key] = vo
            both.append(key)
            notes.append(f"{key}: retired on the incoming side and moved on main; main's stands")
        elif vo is None:
            out[key] = vt
            both.append(key)
            notes.append(f"{key}: retired on main and moved on the incoming side; the incoming "
                         "hash stands")
        else:
            out[key] = vt
            both.append(key)
            notes.append(f"{key}: moved on both sides; the incoming hash stands and the member "
                         "is recorded unproven")
    return out, both, notes


def merge_unproven(base: dict, ours: dict, theirs: dict, extra_members=()) -> dict | None:
    """The union of both records, plus the members the merge itself could not vouch for."""
    records = [ours.get("unproven") or {}, theirs.get("unproven") or {}]
    paths = sorted({p for r in records for p in r.get("paths", ())})
    members = sorted({m for r in records for m in r.get("members", ())} | set(extra_members))
    targets = sorted({t for r in records for t in r.get("targets", ())})
    if not members and not targets:
        return None
    out = {"_": UNPROVEN_NOTE, "paths": paths, "members": members}
    if targets:
        out["targets"] = targets
    return out


def git_merge_base(a: str, b: str) -> str | None:
    """The merge-base of two commits, else the older of the two, else nothing.

    Runs in the checkout git invoked the driver from; a shallow clone that cannot see one of the
    commits falls through each step."""
    def run(*args):
        got = subprocess.run(["git", *args], capture_output=True, text=True)
        return got.stdout.strip() if got.returncode == 0 else None
    mb = run("merge-base", a, b)
    if mb:
        return mb
    ta, tb = run("log", "-1", "--format=%ct", a), run("log", "-1", "--format=%ct", b)
    if ta and tb:
        return a if int(ta) <= int(tb) else b
    return None


def resolve_source(ours: dict, theirs: dict, merge_base=git_merge_base) -> str | None:
    so = (ours.get("source") or {}).get("commit")
    st = (theirs.get("source") or {}).get("commit")
    if so and st and so != st:
        return merge_base(so, st) or so
    return so or st


def merge(base: dict, ours: dict, theirs: dict, merge_base=git_merge_base) -> tuple[dict, list]:
    """`(merged pointer file, notes)`. `ours` is the side being merged onto (main, in a rebase or a
    cherry-pick); `theirs` is the side being brought in."""
    base, ours, theirs = base or {}, ours or {}, theirs or {}
    # A side with no manifest at all — an emptied file, a side where the pointer file did not exist —
    # contributes nothing, rather than reading as a side that retired every member.
    if not ours:
        return {k: theirs[k] for k in KEY_ORDER if k in theirs}, []
    if not theirs:
        return {k: ours[k] for k in KEY_ORDER if k in ours}, []
    notes = []
    solids, both_s, n = merge_members(base.get("solids"), ours.get("solids"), theirs.get("solids"))
    notes += n
    sidecars, both_c, n = merge_members(base.get("sidecars"), ours.get("sidecars"),
                                        theirs.get("sidecars"))
    notes += n

    # THE BUNDLE COMES FROM THE SIDE THAT CUT ONE. A held publish keeps the bundle it found and
    # marks it behind; a runner's plain publish cuts a new one. Whichever side's digest moved
    # from the base is the side with the newer asset; main's when both moved.
    base_digest = (base.get("bundle") or {}).get("sha256")
    ours_new = (ours.get("bundle") or {}).get("sha256") != base_digest
    theirs_new = (theirs.get("bundle") or {}).get("sha256") != base_digest
    side = theirs if theirs_new and not ours_new else ours
    if not side.get("bundle"):
        side = theirs if theirs.get("bundle") else ours

    release = {}
    for key in ("tag", "asset", "url"):
        if key in (side.get("release") or {}):
            release[key] = side["release"][key]
    objects_o = (ours.get("release") or {}).get("objects")
    objects_t = (theirs.get("release") or {}).get("objects")
    if objects_o and objects_t:
        release["objects"] = objects_o

    bundle = dict(side.get("bundle") or {})
    behind = bool(bundle.pop("behind", False)) or solids != (side.get("solids") or {})
    if behind and bundle:
        bundle["behind"] = True

    # A LINE'S TIME TRAVELS WITH ITS HASH: the side whose hash the merged line carries is the
    # side whose time it carries, and where both sides carry the same hash the later time stands.
    moved = {}
    for rel, digest in solids.items():
        candidates = [side.get("moved", {}).get(rel) for side in (ours, theirs)
                      if (side.get("solids") or {}).get(rel) == digest and rel in (side.get("moved") or {})]
        if candidates:
            moved[rel] = max(candidates)
    out = {
        "_": ours.get("_") or theirs.get("_") or base.get("_"),
        "release": release,
        "source": None,
        "unproven": merge_unproven(base, ours, theirs, both_s + both_c),
        "bundle": bundle,
        "solids": solids,
        "sidecars": sidecars,
        "moved": moved or None,
    }
    source = resolve_source(ours, theirs, merge_base)
    out["source"] = {"commit": source} if source else None
    return {k: out[k] for k in KEY_ORDER if out.get(k) is not None}, notes


def render(pointers: dict) -> str:
    """The bytes pack.py writes for this dict."""
    return json.dumps(pointers, indent=2, sort_keys=False) + "\n"


def merge_texts(base: str, ours: str, theirs: str,
                merge_base=git_merge_base) -> tuple[str, list]:
    """The three files as text; an empty side is a pointer file that did not exist there yet."""
    def load(text):
        return json.loads(text) if text.strip() else {}
    merged, notes = merge(load(base), load(ours), load(theirs), merge_base)
    return render(merged), notes


def main(argv: list) -> int:
    if argv[:1] == ["selftest"]:
        return selftest()
    if len(argv) < 3:
        print(__doc__.split("\n\n")[0], file=sys.stderr)
        print("usage: merge_pointers.py %O %A %B   (a git merge driver)", file=sys.stderr)
        return 2
    base, ours, theirs = (Path(p) for p in argv[:3])
    try:
        text, notes = merge_texts(base.read_text(), ours.read_text(), theirs.read_text())
    except (OSError, ValueError) as exc:
        # A side that is not a pointer file — conflict markers already in it, or a half-written file —
        # is left to git to mark as a conflict rather than guessed at.
        print(f"merge_pointers: cannot merge {POINTERS_REL}: {exc}", file=sys.stderr)
        return 1
    ours.write_text(text)
    for note in notes:
        print(f"merge_pointers: {note}", file=sys.stderr)
    return 0


# --------------------------------------------------------------------------------------------
def selftest() -> int:
    holds = 0

    def hold(name, got, want):
        nonlocal holds
        if got != want:
            raise AssertionError(f"{name}:\n  got  {got!r}\n  want {want!r}")
        holds += 1
        print(f"  \N{CHECK MARK} {name}")

    def pointers(solids, source="c0", digest="d0", behind=False, objects=True, unproven=None,
             sidecars=None):
        out = {
            "_": "Written by tools/cad-artifacts/pack.py.",
            "release": {"tag": "cad-artifacts", "asset": f"cad-{digest}.tar.gz",
                        "url": f"https://example/{digest}"},
            "source": {"commit": source},
            "bundle": {"sha256": digest, "bytes": 1, "solids": len(solids)},
            "solids": dict(solids),
            "sidecars": dict(sidecars or {}),
        }
        if objects:
            out["release"]["objects"] = "s-"
        if behind:
            out["bundle"]["behind"] = True
        if unproven:
            out["unproven"] = unproven
        return {k: out[k] for k in KEY_ORDER if k in out}

    mb = lambda a, b: f"mb({a},{b})"  # noqa: E731 — the driver's git call, stubbed
    base = pointers({"m": "h0", "n": "h0"})

    # Disjoint publishes: each side adds a member and moves its source; both members stand,
    # the source is their merge-base, the held bundle is behind the union.
    ours = pointers({"m": "h0", "n": "h0", "a": "ha"}, source="cA", behind=True)
    theirs = pointers({"m": "h0", "n": "h0", "b": "hb"}, source="cB", behind=True)
    got, notes = merge(base, ours, theirs, mb)
    hold("disjoint members union", got["solids"], {"a": "ha", "b": "hb", "m": "h0", "n": "h0"})
    hold("source is the merge-base of the two sources", got["source"], {"commit": "mb(cA,cB)"})
    hold("main's bundle fields stand, behind the union",
         got["bundle"], {"sha256": "d0", "bytes": 1, "solids": 3, "behind": True})
    hold("objects stands when both had it", got["release"].get("objects"), "s-")
    hold("no note for a clean union", notes, [])
    hold("no unproven record where neither side had one", "unproven" in got, False)
    hold("key order is pack.py's", list(got), ["_", "release", "source", "bundle", "solids",
                                                "sidecars"])

    # The same member moved on both sides: the incoming hash stands, recorded unproven.
    ours = pointers({"m": "hA", "n": "h0"}, source="cA")
    theirs = pointers({"m": "hB", "n": "h0"}, source="cB")
    got, notes = merge(base, ours, theirs, mb)
    hold("both moved: incoming hash stands", got["solids"]["m"], "hB")
    hold("both moved: recorded unproven", got["unproven"],
         {"_": UNPROVEN_NOTE, "paths": [], "members": ["m"]})
    hold("both moved: named in a note", len(notes), 1)
    hold("unproven sits after source", list(got)[:4], ["_", "release", "source", "unproven"])

    # One side moved a member and the other left it: the moved hash stands either way.
    got, _ = merge(base, pointers({"m": "hA", "n": "h0"}), pointers({"m": "h0", "n": "h0"}), mb)
    hold("main moved, incoming untouched: main's hash", got["solids"]["m"], "hA")
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}), pointers({"m": "hB", "n": "h0"}), mb)
    hold("incoming moved, main untouched: incoming hash", got["solids"]["m"], "hB")

    # A retired member goes when the other side left it alone; stays when the other moved it.
    got, _ = merge(base, pointers({"n": "h0"}), pointers({"m": "h0", "n": "h0"}), mb)
    hold("pruned on main, untouched incoming: gone", "m" in got["solids"], False)
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}), pointers({"n": "h0"}), mb)
    hold("pruned incoming, untouched on main: gone", "m" in got["solids"], False)
    got, notes = merge(base, pointers({"n": "h0"}), pointers({"m": "hB", "n": "h0"}), mb)
    hold("pruned on main, moved incoming: incoming stands", got["solids"].get("m"), "hB")
    hold("…and is recorded unproven", got["unproven"]["members"], ["m"])

    # objects is a promise about every member; one side without it takes it off.
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}, objects=False),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}), mb)
    hold("objects absent when one side lacks it", "objects" in got["release"], False)

    # The bundle comes from the side that cut one, and is behind unless it holds the union.
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}, digest="d0", behind=True),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}, digest="dB"), mb)
    hold("incoming cut a bundle, main held: incoming asset", got["release"]["asset"],
         "cad-dB.tar.gz")
    hold("…and it holds the union, so not behind", got["bundle"].get("behind"), None)
    got, _ = merge(base, pointers({"m": "h0", "n": "h0", "a": "ha"}, digest="dA"),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}, digest="dB"), mb)
    hold("both cut: main's asset", got["release"]["asset"], "cad-dA.tar.gz")
    hold("…behind the union", got["bundle"].get("behind"), True)

    # unproven is the union of both records; a side without one contributes nothing.
    ua = {"_": UNPROVEN_NOTE, "paths": ["p1"], "members": ["m"], "targets": ["//:t1"]}
    ub = {"_": UNPROVEN_NOTE, "paths": ["p2"], "members": ["n"]}
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}, unproven=ua),
                   pointers({"m": "h0", "n": "h0"}, unproven=ub), mb)
    hold("unproven records union", got["unproven"],
         {"_": UNPROVEN_NOTE, "paths": ["p1", "p2"], "members": ["m", "n"], "targets": ["//:t1"]})

    # Sources: equal stands, one missing takes the other, both missing is absent.
    hold("equal sources stand", resolve_source(pointers({}, source="c"), pointers({}, source="c"), mb), "c")
    hold("one source missing takes the other",
         resolve_source({"source": {}}, pointers({}, source="c"), mb), "c")
    hold("no source on either side", resolve_source({}, {}, mb), None)
    got, _ = merge(base, {}, pointers({"m": "h0", "n": "h0"}), mb)
    hold("an empty side gives the other side back", got, pointers({"m": "h0", "n": "h0"}))
    got, _ = merge({}, pointers({"m": "h0"}, source="cA"), pointers({"n": "h1"}, source="cB"), mb)
    hold("both sides created the pointer file from nothing: union", got["solids"], {"m": "h0", "n": "h1"})
    hold("…with the merge-base source", got["source"], {"commit": "mb(cA,cB)"})

    # A line's time travels with its hash; the later time stands where the hashes agree.
    o = pointers({"m": "hA", "n": "h0"}); o["moved"] = {"m": 20, "n": 5}
    th = pointers({"m": "h0", "n": "h0", "b": "hb"}); th["moved"] = {"m": 1, "n": 7, "b": 9}
    got, _ = merge(base, o, th, mb)
    hold("line times follow the hash taken", got["moved"], {"b": 9, "m": 20, "n": 7})
    got, _ = merge(base, pointers({"m": "h0"}), pointers({"m": "h0"}), mb)
    hold("no times on either side, none written", "moved" in got, False)

    # Sidecars merge like solids.
    got, _ = merge(pointers({}, sidecars={"s": "x0"}), pointers({}, sidecars={"s": "x0", "t": "y"}),
                   pointers({}, sidecars={"s": "x1"}), mb)
    hold("sidecars merge by key", got["sidecars"], {"s": "x1", "t": "y"})

    # A pointer file merged with itself is the file, byte for byte — the real one, when it is there.
    real = Path(__file__).resolve().parents[2] / POINTERS_REL
    if real.is_file():
        text = real.read_text()
        merged, notes = merge_texts(text, text, text, mb)
        hold("the real pointer file merged with itself is itself", merged == text and notes == [], True)
        try:
            sys.path.insert(0, str(Path(__file__).resolve().parent))
            import pack  # noqa: E402
            hold("the unproven note is pack.py's own",
                 pack.unproven(["p"], ["m"])["_"], UNPROVEN_NOTE)
        except ImportError:
            print("  (pack.py not importable here; note comparison skipped)")

    # The driver itself, on files, through the command line.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        o, a, b = (Path(tmp) / n for n in ("O", "A", "B"))
        o.write_text(render(base))
        a.write_text(render(pointers({"m": "hA", "n": "h0", "a": "ha"}, source="cA")))
        b.write_text(render(pointers({"m": "hB", "n": "h0"}, source="cB")))
        run = subprocess.run([sys.executable, __file__, str(o), str(a), str(b)],
                             capture_output=True, text=True)
        hold("driver exits 0", run.returncode, 0)
        result = json.loads(a.read_text())
        hold("driver wrote the merge into %A", result["solids"],
             {"a": "ha", "m": "hB", "n": "h0"})
        hold("driver names the collision on stderr", "m: moved on both sides" in run.stderr, True)
        a.write_text("<<<<<<< not json")
        run = subprocess.run([sys.executable, __file__, str(o), str(a), str(b)],
                             capture_output=True, text=True)
        hold("a side that is not a pointer file is left to git", run.returncode, 1)

    print(f"merge_pointers selftest {holds}/{holds}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
