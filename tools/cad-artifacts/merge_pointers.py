#!/usr/bin/env python3
"""Two publishes of the pointer file, merged the way a rebase needs them: main's pointers, plus yours.

    python3 tools/cad-artifacts/merge_pointers.py %O %A %B     # git merge driver: the result lands in %A
    python3 tools/cad-artifacts/merge_pointers.py selftest

`.gitattributes` names this driver for `hardware/cad-artifacts.json`, and `tools/push.py`
puts its command in a clone's config the first time it runs there (`merge.cadpointers.driver`), which
is how a fresh clone, cloud or laptop, comes to have it. git calls it whenever both sides of a
merge, rebase or cherry-pick moved the pointer file — which two publishes always do. Without it
every concurrent publish stops on the pointer file; with it the merge has one right answer, and
this is it.

THE MEMBERS ARE THE POINTERS. `solids` and `sidecars` merge by key. A member one side left alone
takes the other side's hash, so a publish adds its members to main's without dropping main's. A
member both sides moved to different hashes takes the incoming side's — the publish being
brought in is the newer act — and its `made` line is marked unproven, so the next publish proves
it against the merged tree or leaves it to the reconciler. A member one side retired and the
other left alone is gone.

Each line's time (`moved`) and its `made` line travel with the hash the merged line carries, so a
publish on any machine can still tell its own newer cut from main's older bytes, and what made
each member. Where both sides carry that hash, the later time stands, and the `made` line that
proves the member over one that does not.

`release.objects` stands only when both sides had it, since it promises every member is on the
release by its own hash. The bundle is the one from the side that cut a new one, main's when
both did, and it is marked behind whenever the merged members are not the ones it holds. A key
`pack.py` does not write stands where both sides hold it alike.

The result is the bytes `pack.py` writes: its key order, its indentation, its escaping. Merging a
pointer file with itself gives the file back unchanged.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'bazel'))
from _bookkeeping import call as _bookkeeping_call

def _merge_native(name,*args):
    result = _bookkeeping_call('merge.'+name,args_json=[json.dumps(value) for value in args])
    if name=='render':
        return result
    result = json.loads(result)
    return tuple(result) if name in {'merge_members','merge','merge_texts'} else result


POINTERS_REL = "hardware/cad-artifacts.json"

#: The order pack.py seats the keys in.
KEYS = ("_", "release", "store", "bundle", "solids", "sidecars", "moved", "made")


def merge_members(base,ours,theirs):
    return _merge_native('merge_members',base,ours,theirs)


def _proves(line):
    return _merge_native('_proves',line)


def merge_made(ours,theirs,lines,both):
    return _merge_native('merge_made',ours,theirs,lines,both)


def _seat(out,ours,theirs):
    return _merge_native('_seat',out,ours,theirs)


def merge(base,ours,theirs):
    return _merge_native('merge',base,ours,theirs)


def render(pointers):
    return _merge_native('render',pointers)


def merge_texts(base,ours,theirs):
    return _merge_native('merge_texts',base,ours,theirs)


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

    def pointers(solids, digest="d0", behind=False, objects=True, made=None, sidecars=None):
        out = {
            "_": "Written by tools/cad-artifacts/pack.py.",
            "release": {"tag": "cad-artifacts", "asset": f"cad-{digest}.tar.gz",
                        "url": f"https://example/{digest}"},
            "bundle": {"sha256": digest, "bytes": 1, "solids": len(solids)},
            "solids": dict(solids),
            "sidecars": dict(sidecars or {}),
        }
        if objects:
            out["release"]["objects"] = "s-"
        if behind:
            out["bundle"]["behind"] = True
        if made:
            out["made"] = made
        return {k: out[k] for k in KEYS if k in out}

    def line(inputs, commit, unproven=False):
        return {"inputs": inputs, "commit": commit, **({"unproven": True} if unproven else {})}

    base = pointers({"m": "h0", "n": "h0"})

    # Disjoint publishes: each side adds a member; both members stand, and the held bundle is
    # behind the union.
    ours = pointers({"m": "h0", "n": "h0", "a": "ha"}, behind=True)
    theirs = pointers({"m": "h0", "n": "h0", "b": "hb"}, behind=True)
    got, notes = merge(base, ours, theirs)
    hold("disjoint members union", got["solids"], {"a": "ha", "b": "hb", "m": "h0", "n": "h0"})
    hold("main's bundle fields stand, behind the union",
         got["bundle"], {"sha256": "d0", "bytes": 1, "solids": 3, "behind": True})
    hold("objects stands when both had it", got["release"].get("objects"), "s-")
    hold("no note for a clean union", notes, [])
    hold("key order is pack.py's", list(got), ["_", "release", "bundle", "solids", "sidecars"])

    # The same member moved on both sides: the incoming hash stands, its line unproven.
    ours = pointers({"m": "hA", "n": "h0"}, made={"m": line("tA", "cA")})
    theirs = pointers({"m": "hB", "n": "h0"}, made={"m": line("tB", "cB")})
    got, notes = merge(base, ours, theirs)
    hold("both moved: incoming hash stands", got["solids"]["m"], "hB")
    hold("both moved: the incoming `made` line, unproven", got["made"],
         {"m": line("tB", "cB", unproven=True)})
    hold("both moved: named in a note", len(notes), 1)

    # One side moved a member and the other left it: the moved hash stands either way.
    got, _ = merge(base, pointers({"m": "hA", "n": "h0"}), pointers({"m": "h0", "n": "h0"}))
    hold("main moved, incoming untouched: main's hash", got["solids"]["m"], "hA")
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}), pointers({"m": "hB", "n": "h0"}))
    hold("incoming moved, main untouched: incoming hash", got["solids"]["m"], "hB")

    # A retired member goes when the other side left it alone; stays when the other moved it.
    got, _ = merge(base, pointers({"n": "h0"}), pointers({"m": "h0", "n": "h0"}))
    hold("pruned on main, untouched incoming: gone", "m" in got["solids"], False)
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}), pointers({"n": "h0"}))
    hold("pruned incoming, untouched on main: gone", "m" in got["solids"], False)
    got, notes = merge(base, pointers({"n": "h0"}),
                       pointers({"m": "hB", "n": "h0"}, made={"m": line("tB", "cB")}))
    hold("pruned on main, moved incoming: incoming stands", got["solids"].get("m"), "hB")
    hold("…and its `made` line is unproven", got["made"]["m"], line("tB", "cB", unproven=True))

    # objects is a promise about every member; one side without it takes it off.
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}, objects=False),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}))
    hold("objects absent when one side lacks it", "objects" in got["release"], False)

    # The bundle comes from the side that cut one, and is behind unless it holds the union.
    got, _ = merge(base, pointers({"m": "h0", "n": "h0"}, digest="d0", behind=True),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}, digest="dB"))
    hold("incoming cut a bundle, main held: incoming asset", got["release"]["asset"],
         "cad-dB.tar.gz")
    hold("…and it holds the union, so not behind", got["bundle"].get("behind"), None)
    got, _ = merge(base, pointers({"m": "h0", "n": "h0", "a": "ha"}, digest="dA"),
                   pointers({"m": "h0", "n": "h0", "b": "hb"}, digest="dB"))
    hold("both cut: main's asset", got["release"]["asset"], "cad-dA.tar.gz")
    hold("…behind the union", got["bundle"].get("behind"), True)

    # A `made` line travels with the hash the merged line carries.
    o = pointers({"m": "hA", "n": "h0"},
                 made={"m": line("tA", "cA"), "n": {"commit": "cA", "unproven": True}})
    th = pointers({"m": "h0", "n": "h0", "b": "hb"},
                  made={"m": line("t0", "c0"), "n": line("t0", "c0"), "b": line("tb", "cB")})
    got, _ = merge(base, o, th)
    hold("a `made` line travels with the hash its member's line carries",
         got["made"]["m"], line("tA", "cA"))
    hold("where both sides carry the hash, the line that proves the member stands",
         got["made"]["n"], line("t0", "c0"))
    hold("a member one side made keeps that side's line", got["made"]["b"], line("tb", "cB"))
    hold("`made` is the last key", list(got)[-1], "made")

    # A key pack.py does not write stands where both sides hold it alike, and goes where not.
    old = {"_": "note", "release": {"asset": "cad-d0.tar.gz"}, "source": {"commit": "c0"},
           "unproven": {"members": ["m"]}, "bundle": {"sha256": "d0"}, "solids": {"m": "h0"},
           "sidecars": {"s": "x0"}}
    got, _ = merge(old, old, old)
    hold("a key pack.py does not write stands in its place where both sides hold it alike",
         list(got), list(old))
    got, _ = merge(old, old, {k: v for k, v in old.items() if k != "source"})
    hold("…and goes where they differ", ("source" in got, "unproven" in got), (False, True))

    got, _ = merge(base, {}, pointers({"m": "h0", "n": "h0"}))
    hold("an empty side gives the other side back", got, pointers({"m": "h0", "n": "h0"}))
    got, _ = merge({}, pointers({"m": "h0"}), pointers({"n": "h1"}))
    hold("both sides created the pointer file from nothing: union", got["solids"], {"m": "h0", "n": "h1"})

    # A line's time travels with its hash; the later time stands where the hashes agree.
    o = pointers({"m": "hA", "n": "h0"}); o["moved"] = {"m": 20, "n": 5}
    th = pointers({"m": "h0", "n": "h0", "b": "hb"}); th["moved"] = {"m": 1, "n": 7, "b": 9}
    got, _ = merge(base, o, th)
    hold("line times follow the hash taken", got["moved"], {"b": 9, "m": 20, "n": 7})
    got, _ = merge(base, pointers({"m": "h0"}), pointers({"m": "h0"}))
    hold("no times on either side, none written", "moved" in got, False)

    # Sidecars merge like solids.
    got, _ = merge(pointers({}, sidecars={"s": "x0"}), pointers({}, sidecars={"s": "x0", "t": "y"}),
                   pointers({}, sidecars={"s": "x1"}))
    hold("sidecars merge by key", got["sidecars"], {"s": "x1", "t": "y"})

    # A pointer file merged with itself is the file, byte for byte.
    text = render(pointers({"m": "h0", "n": "h0"}, made={"m": line("t0", "c0")}))
    hold("a pointer file merged with itself is itself", merge_texts(text, text, text), (text, []))
    real = Path(__file__).resolve().parents[2] / POINTERS_REL
    if real.is_file():
        text = real.read_text()
        merged, notes = merge_texts(text, text, text)
        hold("…and the real one says what it says, in its key order",
             (json.loads(merged), list(json.loads(merged)), notes),
             (json.loads(text), list(json.loads(text)), []))

    # The driver itself, on files, through the command line.
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        o, a, b = (Path(tmp) / n for n in ("O", "A", "B"))
        o.write_text(render(base))
        a.write_text(render(pointers({"m": "hA", "n": "h0", "a": "ha"})))
        b.write_text(render(pointers({"m": "hB", "n": "h0"})))
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
