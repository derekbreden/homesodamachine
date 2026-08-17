#!/usr/bin/env python3
"""Run each generator once and write down every file it read and every file it wrote.

    tools/cad-venv/bin/python tools/bazel/trace_inputs.py            # every generator
    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py>   # one

An audit hook watches the run, which happens the way the generator's own `__main__` runs. Every
path under this repo it opens is kept, on the side its mode names — reads on one, writes on the
other, and an atomic write on the rename that lands it. The answer is `graph.json`, which
`inventory.py` and `gen_build.py` both read.

OCCT READS A STEP BELOW PYTHON, where no audit hook reaches. `_cadq_export.import_step` is the
one loader and keeps the list; this takes it at the end of the run, so a generator that cuts no
solid of its own still names the ones it stood the machine off.

A WRITE THAT LANDS ON THE BYTES ALREADY THERE PERFORMS NO WRITE. `_cadq_export._atomic_write`
skips the rename and `docgen` skips the `write_text`, and both keep the target they were
handed in `_WRITE_TARGETS`, which this takes the same way.

A generator that raises is traced to where it stopped. What it read is what it read; what it
had not yet written is absent from its outputs, and the copy at the end of its action finds
nothing there.
"""

import argparse
import json
import os
import re
import runpy
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
GRAPH = _HERE.parent / "graph.json"

sys.path.insert(0, str(_HERE.parent))
from inventory import tracked as _inventory_tracked   # noqa: E402

RUNNER = r'''
import json, os, sys, runpy
ROOT = %r
GEN = %r
OUT = %r
ARGV = %r
read, wrote, scanned = set(), set(), set()

def _under(path):
    try:
        p = os.path.abspath(os.fspath(path))
    except (TypeError, ValueError):
        return None
    return os.path.relpath(p, ROOT) if p.startswith(ROOT + os.sep) else None

def _keep(into, path):
    rel = _under(path)
    if rel is not None:
        into.add(rel)

# THE WRITE MACHINERY LOOKS AT ITS OWN DESTINATION, and neither look is a build input.
# `_cadq_export._sweep_orphan_temps` globs the target's directory to unlink the temps a
# SIGKILLed build left behind, and `_matches_existing_target` compares the target's bytes to
# decide whether the rename is a no-op. A glob scans and a compare opens, so untold apart they
# both arrive as reading — and the scan is the expensive half, because a scanned directory is
# taken below as an input area whole. A generator would read the solid it writes, its own
# thumbnail, the README beside it, and the sibling assembly shelved in the same folder.
WRITE_MACHINERY = ("_sweep_orphan_temps", "_matches_existing_target")

def _by_write_machinery():
    """Whether `_cadq_export`'s write bookkeeping is what reached the disk here.

    Both calls land under `glob` or `filecmp`, so the frame that raised the event never names
    the one that meant it — the stack is walked to find it. Bounded, because both sit within a
    few frames of the call they make, and entered only for a path inside this tree.
    """
    try:
        f = sys._getframe(1)
    except ValueError:
        return False
    for _ in range(8):
        if f is None:
            return False
        code = f.f_code
        if code.co_name in WRITE_MACHINERY and code.co_filename.endswith("_cadq_export.py"):
            return True
        f = f.f_back
    return False

def _hook(event, args):
    # `open` is most of it, and its mode says which side of the edge it is. `import` is the
    # rest of the reading: a module loaded by path through importlib — `_bom_sync` takes a
    # dozen generators that way — is read by the loader, not by open().
    if event == "open" and args and isinstance(args[0], (str, bytes, os.PathLike)):
        mode = args[1] if len(args) > 1 and isinstance(args[1], str) else "r"
        if set(mode) & set("wxa+"):
            _keep(wrote, args[0])
        elif _under(args[0]) is not None and not _by_write_machinery():
            _keep(read, args[0])
    # AN ATOMIC WRITE LANDS AS A RENAME. `_cadq_export._atomic_write` writes a sibling temp
    # and moves it over the target, so the name the tree carries is never opened for writing.
    elif event in ("os.rename", "os.replace") and len(args) > 1:
        _keep(wrote, args[1])
    # A TOOL THIS RUN HANDS A PATH TO opens it out of Python's sight. `render-step-posed.js`
    # is named on node's command line and `_blender_scene.py` on blender's; both are read.
    elif event == "subprocess.Popen" and len(args) > 1:
        for a in (args[1] or ()):
            try:
                if os.path.isfile(os.fspath(a)):
                    _keep(read, a)
            except (TypeError, ValueError):
                pass
    # A DIRECTORY THIS RUN GLOBS names its files without opening one. `_build.py` asks its
    # own directory for `*.html` to know which cards there are; `Path.glob` scans and nothing
    # is read until node opens them, out of sight.
    #
    # A DIRECTORY THE IMPORT MACHINERY SCANS IS NOT ONE THIS RUN GLOBBED. Python lists every
    # `sys.path` entry to find the module it is about to load, and a scan is read below as an
    # input area whole — so the entries a generator inserts arrived as every tracked file
    # beneath them: `tools/` for `docgen`, 61 files into 77 of the hundred targets, the CAD
    # venv and sixteen animation frames among them; `hardware/scripts/` for the shared machinery,
    # 29 into 103; and the run's own directory, which for a doc sync is `hardware/assembly/`
    # entire, 401 files. What an import reads is the module, which the `import` event below
    # names outright, and `exec` names the ones loaded by path.
    #
    # TWO PARTS OF THAT MACHINERY WALK `sys.path` AND THEY DO NOT LOOK ALIKE FROM HERE. The
    # finder runs frozen, so its frame is `<frozen importlib._bootstrap_external>`; the
    # `importlib.metadata` a package's version lookup reaches runs from a real file. Both are
    # the import system looking along the path, and a `Path.glob` of a content directory is
    # neither — its frame is `glob.py`.
    elif event in ("os.scandir", "os.listdir") and args and args[0]:
        try:
            by = sys._getframe(1).f_code.co_filename
        except ValueError:
            by = ""
        if not (by.startswith("<frozen importlib") or "/importlib/" in by) \
                and not _by_write_machinery():
            _keep(scanned, args[0])
    elif event == "import" and len(args) > 1 and args[1]:
        _keep(read, args[1])
    elif event == "exec" and args:
        code = getattr(args[0], "co_filename", None)
        if code:
            _keep(read, code)

sys.addaudithook(_hook)
sys.argv = [GEN, *ARGV]
sys.path.insert(0, os.path.dirname(os.path.join(ROOT, GEN)))
raised = None
try:
    runpy.run_path(os.path.join(ROOT, GEN), run_name="__main__")
except BaseException as exc:
    raised = type(exc).__name__
    print(f"  (raised {raised}; keeping what it read)", file=sys.stderr)
finally:
    # THE SOLIDS OCCT OPENED BELOW PYTHON. `import_step` is the one loader and keeps the list;
    # a generator that cuts nothing of its own has no stamp to carry it, so it is taken here.
    mod = sys.modules.get("_cadq_export")
    read |= set(getattr(mod, "_STEP_READS", ())) | set(getattr(mod, "_READ_TARGETS", ()))
    # A FILE IS CUT WHOLE OR REWRITTEN IN PLACE, and the module that wrote it is the one that
    # knows which. `_cadq_export` draws a solid from nothing; `docgen` and `_cardgen` read a
    # doc or a card, replace the values they manage, and write the rest of it back. A file of
    # the second kind belongs on both sides of its own action, and no suffix says so —
    # `.figures.json` carries no marker and is rewritten; a `.step` is read to be compared
    # against and is not.
    back = set()
    for mod in ("docgen", "_cardgen"):
        back |= set(getattr(sys.modules.get(mod), "_WRITE_TARGETS", ()))
    wrote |= back | set(getattr(sys.modules.get("_cadq_export"), "_WRITE_TARGETS", ()))
    with open(OUT, "w") as fh:
        json.dump({"reads": sorted(read), "writes": sorted(wrote),
                   "rewritten": sorted(back), "scanned": sorted(scanned),
                   "raised": raised}, fh)
'''


def _tracked() -> set:
    """Every file this tree stands behind — `inventory.tracked`, which is git's index plus the
    solids `hardware/cad-artifacts.lock.json` names.

    A GENERATED SOLID IS IN NO INDEX AND A GENERATOR STILL OPENS IT. `_pump_replacement_sync`
    loads `kamoer-kphm400.step` through `manifold_layout.build_pump`. A trace filtered by
    `git ls-files` drops that read, the graph stops naming it, and the action built from the
    graph holds no such file and dies on `STEP File could not be loaded` — a generator that
    runs by hand and cannot run in the sandbox. `gen_build.py` reads the same function, so the
    set a trace is filtered against and the set an action is filled from are one reading."""
    return set(_inventory_tracked())


def trace(gen: str, files: set, argv=()) -> dict:
    """Every tracked file `gen` read and every one it wrote, plus the solids OCCT loaded."""
    out = Path(os.environ.get("TMPDIR", "/tmp")) / f"hsm-trace-{Path(gen).stem}.json"
    # ONE GENERATOR AT A TIME IS WHAT THIS ALREADY DOES, so each run takes the global lock
    # the way a hand run does. Two traces on one machine are two pileups otherwise, and the
    # lock is what everything outside `bazel` shares.
    #
    # AND NEVER FOLLOWS SOMEBODY ELSE'S. `_run_lock` attaches a second run of the same script
    # to the one already going and hands back ITS exit status, so the generator's own `main`
    # never runs and the trace watches a process that opened nothing. A reading needs the run
    # to happen, so this one asks for the lock and refuses the shortcut.
    #
    # A TRACE WATCHES THE RUN A BUILD MAKES. What it hands the generator is what the generator
    # would have had anyway, bar the two the lock reads above — a flag that turned work off
    # here would be a reading of a shorter run than the one an action performs, and the graph
    # would name less than the sandbox has to hold.
    env = dict(os.environ, HSM_BUILD_SOURCE="trace", HSM_NO_BUILD_ATTACH="1")
    subprocess.run([sys.executable, "-c",
                    RUNNER % (str(_ROOT), gen, str(out), tuple(argv))],
                   cwd=str(_ROOT), env=env, capture_output=True, text=True, timeout=1800)
    try:
        seen = json.loads(out.read_text())
    except (OSError, ValueError):
        # The runner left no reading: killed, or stopped before its own `finally`.
        return {"reads": [], "writes": [], "raised": "no reading"}
    out = {side: {p for p in seen.get(side, ()) if p in files}
           for side in ("reads", "writes", "rewritten")}
    # A SCANNED DIRECTORY IS AN INPUT AREA, and what it holds below the top counts. `_build.py`
    # globs its own directory for `*.html` and hands each card to a browser, which resolves
    # `tools.css` and `img/tool/*.png` against it — reads no scan and no `open` here sees.
    here = tuple(d + "/" for d in seen.get("scanned", ()))
    if here:
        out["reads"] |= {f for f in files if f.startswith(here)}
    answer = {k: sorted(v) for k, v in out.items()}
    if seen.get("raised"):
        answer["raised"] = seen["raised"]
    return answer


#: WHAT THE BOARD READS IS NOT IN THIS REPO. `hardware/pcb/pcba/package.json` pins seven
#: `@tscircuit/*` packages to commits of `github:derekbreden/*`, resolved at install from
#: outside the tree, and `board-3d.py` runs `tsci` through them. An action cannot hold what
#: it reads, so the board is built by `bun render-board.ts` and its GLB carried by the hook.
#: Vendoring the forks is what would let it join the graph.
ELSEWHERE = ("tools/", "hardware/pcb/pcba/")


def _generators(files: set) -> list:
    """Every `.py` with a `__main__` this tree builds through — see `ELSEWHERE`."""
    out = []
    for f in sorted(files):
        if not f.endswith(".py") or f.startswith(ELSEWHERE):
            continue
        try:
            if '__name__ == "__main__"' in (_ROOT / f).read_text():
                out.append(f)
        except OSError:
            continue
    return out


SELFTESTS = _HERE.parent / "selftests.json"


def _selftests(files: set) -> list:
    """Every module that answers to `selftest` on its own command line.

    NOT `_generators`, and not `ELSEWHERE` either. That reading answers which modules BUILD
    this tree, and `tools/` is left out of it because the machinery that writes the graph is
    not a step in the graph it writes. What a test reads is a different question with a
    different answer, and three modules under `tools/` are where the two differ: `sync_tree.py`
    holds ten, one of them that a card's authored text survives a build handed stale figures,
    `check_declared_imports.py` holds nine on the sources a step owes a declaration for, and
    this module holds seven on `gave_up`, which reads two entries and no run at all.
    """
    out = []
    for f in sorted(files):
        if not f.endswith(".py"):
            continue
        try:
            text = (_ROOT / f).read_text()
        except OSError:
            continue
        # A DEFINITION AND NOT A MENTION. `gen_build.py` names the word in the code that
        # looks for it, and matching on the mention gave it a test that its own argument
        # parser refuses.
        if re.search(r"^def selftest\(", text, re.M):
            out.append(f)
    return out


def gave_up(prior: dict, seen: dict) -> bool:
    """Whether a reading hands back fewer files than the one it replaces, on EITHER side.

    Each side on its own, because a run can open MORE and write LESS — the inputs load, then it
    dies before the exports land — and that reading has its reads intact, which is the one that
    looks healthy. Asking it as an ordered pair against `(0, 0)` answers on the reads and never
    reaches the writes: `(-1, 1)` is a run that gained four reads and lost two writes, and it
    compares less-than on the first element and passes."""
    return any(len(prior[side]) > len(seen[side]) for side in ("reads", "writes"))


def selftest() -> int:
    """Every shape the reading can take, against the answer. Two agents got this comparison
    wrong before it was named — the trace is no part of it, so neither is a run."""
    holds = 0

    def hold(label, prior, seen, want):
        nonlocal holds
        got = gave_up({"reads": [0] * prior[0], "writes": [0] * prior[1]},
                      {"reads": [0] * seen[0], "writes": [0] * seen[1]})
        holds += got == want
        print(f"  {'✓' if got == want else '✗'} {label}"
              + ("" if got == want else f" — {got} != {want}"))

    hold("both sides shrank", (9, 3), (5, 1), True)
    hold("the reads shrank and the writes stood", (9, 3), (5, 3), True)
    hold("the writes shrank and the reads stood", (9, 3), (9, 1), True)
    hold("the reads shrank and the writes grew", (9, 1), (5, 3), True)
    # THE ONE AN ORDERED PAIR WAVES THROUGH, and the one a part-way run most looks like.
    hold("the reads GREW and the writes shrank", (5, 3), (9, 1), True)
    hold("both sides grew", (5, 1), (9, 3), False)
    hold("neither side moved", (9, 3), (9, 3), False)

    print(f"trace_inputs selftest {holds}/7")
    return 0 if holds == 7 else 1


def main() -> int:
    # `selftest` holds the reading above; `--selftests` watches every OTHER module's. The two
    # words are one letter apart and answer different questions.
    if sys.argv[1:] == ["selftest"]:
        return selftest()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("gen", nargs="*", help="generator paths; default every one")
    ap.add_argument("--selftests", action="store_true",
                    help="watch each module's `selftest` instead, into selftests.json")
    args = ap.parse_args()

    files = _tracked()
    if args.selftests:
        held = json.loads(SELFTESTS.read_text()) if SELFTESTS.is_file() else {}
        gens = args.gen or _selftests(files)
        for i, gen in enumerate(gens, 1):
            seen = trace(gen, files, argv=("selftest",))
            held[gen] = sorted(set(seen["reads"]) | {gen})
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} {len(held[gen]):3d} read")
            SELFTESTS.write_text(json.dumps(held, indent=2, sort_keys=True) + "\n")
        print(f"{len(held)} selftest(s) watched")
        return 0

    gens = args.gen or _generators(files)

    graph = json.loads(GRAPH.read_text()) if GRAPH.is_file() else {}
    shrank = []
    for i, gen in enumerate(gens, 1):
        seen = trace(gen, files)
        # `probe.py`, `fit.py` and `lanes.py` are instruments: they answer and write nothing,
        # and a generator this has never watched write is not a step of the build.
        #
        # A RUN THAT DID NOT HAPPEN IS NOT A GENERATOR THAT MAKES NOTHING. Attached, superseded,
        # killed, timed out — each comes back the way an instrument does, with no writes, and
        # dropping the entry on that reading takes the generator out of `graph.json`, out of
        # `inventory`, out of `BUILD.bazel`, and its solids stop being cut against a green
        # build. So an entry already standing is left standing, and the line below says the
        # reading failed rather than writing a verdict over it.
        # A GENERATOR THAT RAISED WROTE NOTHING TOO, and the RUNNER is where the two part: it
        # names the exception. One that raised keeps the entry it had, and one with no entry
        # is named on its own line, because a build cannot cut what a red generator makes.
        # AND A RUN THAT DID PART OF ITS WORK WROTE SOMETHING. The branch below reads any write
        # as a whole run, so a generator that stopped halfway replaces its entry with the part
        # it reached — `render_scenes` came back 38 read / 22 written where it stands at
        # 210 / 76, and the reading that catches it is the entry already in hand. A shrink is
        # not wrong on its own: a tracer that stops recording what a run never opened shrinks
        # every entry it touches, on purpose. So this takes the reading and NAMES it, at the
        # tail as well, where a sweep of a hundred generators cannot scroll it away.
        raised = seen.pop("raised", None)
        if seen["writes"]:
            prior = graph.get(gen)
            if prior and gave_up(prior, seen):
                shrank.append((gen, len(prior["reads"]), len(seen["reads"]),
                               len(prior["writes"]), len(seen["writes"])))
            graph[gen] = seen
        elif raised and gen in graph:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} raised {raised} — keeping what it had")
            continue
        elif raised:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} raised {raised} — NOT IN THE GRAPH, so "
                  f"nothing it makes is cut")
            continue
        elif gen in graph:
            print(f"  [{i:3d}/{len(gens)}] {gen:60s} wrote nothing — keeping what it had")
            continue
        else:
            graph.pop(gen, None)
        print(f"  [{i:3d}/{len(gens)}] {gen:60s} "
              f"{len(seen['reads']):3d} read {len(seen['writes']):3d} written")
        GRAPH.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n")
    print(f"{len(graph)} generator(s) in the graph")
    if shrank:
        # Either side alone is the reading, so the line cannot say the entry came back smaller:
        # a run can open more and still write less, which is the shape that gets past a guard
        # comparing the pair in order.
        print(f"\n{len(shrank)} entr(y/ies) gave up reads or writes they had:")
        for gen, r0, r1, w0, w1 in shrank:
            print(f"    {gen}\n      {r0:3d} -> {r1:3d} read   {w0:3d} -> {w1:3d} written")
        print("  A run that stopped part way writes down the part it reached. Re-trace the one")
        print("  generator and read it again; the second reading is the one to keep.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
