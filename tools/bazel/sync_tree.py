#!/usr/bin/env python3
"""Carry what the build cut into the tree that commits it.

    tools/cad-venv/bin/python tools/bazel/sync_tree.py            # what differs
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write    # and copy it in
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write \
        --targets //:display-cover                                # one built slice
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write --derived-only
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --derived-only --stage
    tools/cad-venv/bin/python tools/bazel/sync_tree.py selftest   # the carry, on fixtures

Bazel cuts into `bazel-bin/`, while the artifact packer and derived-doc tools read the tree.
The build is what decides the bytes, and this carries the declared outputs from their producers — tracked
docs as well as ignored solids that leave the checkout through the content-addressed bundle.

WHAT DIFFERS IS THE READING. A tree that comes back with nothing to copy is a tree holding the
artifacts its sources make — asked here for the cost of a comparison, because the build ran.

AN OUTPUT IS SOMETIMES ALSO AN INPUT. Two hundred and five files are read and written back
over, and `graph.json` names them because the writers do — so the copy a build hands one of
them back carries whatever text that build was handed. THE BUILD DECIDES THE FIGURES IN SUCH A
FILE AND NOT ONE WORD AROUND THEM, so that is the whole of what this carries into one: its
figures, written into the text the tree holds now. A build that ran before an edit hands back
nothing that can reach the sentence — or the line of code — that edit wrote, and a tree whose
figures are the build's reads clean whether or not that build was handed its prose.
"""

import argparse
import filecmp
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_HERE.parent))
from inventory import ACTION_INTERMEDIATE, build_inert    # noqa: E402

from _bookkeeping import call as _bookkeeping_call
from inventory import _native_config as _inventory_config

def _native(op,**fields):
    return _bookkeeping_call(op,config=_inventory_config(),**fields)



#: An output is `…/bin/out/<target>/<the path the tree keeps it under>`. The query answers with
#: every file of every target, and `//:node-packages` alone globs eleven thousand that are
#: inputs; this is what tells a declared output from one of those.
_DECLARED = re.compile(r"/bin/out/[^/]+/(.+)$")

#: `--solids-only` carries only bytes the deployed viewer consumes. Geometry leaves through
#: the artifact bundle; scorecards remain tracked beside it because the viewer reads them directly.
#: Everything else stays in bazel-bin so a scoped CAD publish never grows into a docs,
#: ledger, facts, or thumbnail regeneration lane.
_SOLID_OUTPUTS = (".step", ".stl", ".glb", ".step.mesh")
_PUBLIC_EVIDENCE = (".scorecard.json",)


def _runtime_output(path):
    return _native('sync.runtime',path=path)


#: The publisher carries model bytes and the metadata belonging to that cut. The cloud
#: derive carries documents, figures and media while leaving this cohort in the tree.
_MODEL_METADATA = frozenset({
    "hardware/cad-artifacts.json",
    "web/public/tube-routes.json",
})


def _publisher_owned(path):
    return _native('sync.publisher',path=path)


def stage_derived():
    status = subprocess.run(['git','-c','status.renames=false','status','--porcelain=v1','-z','--untracked-files=all'],cwd=_ROOT,capture_output=True,check=True)
    selected = _native('sync.stage',status_bytes=list(status.stdout))
    def change(command,kind):
        paths = [bytes(path) for path in selected[kind]]
        if paths:
            subprocess.run(['git','--literal-pathspecs',*command,'--pathspec-from-file=-','--pathspec-file-nul'],cwd=_ROOT,input=b'\0'.join(paths)+b'\0',check=True)
    change(['restore','--staged'],'staged')
    change(['add','-A'],'paths')
    change(['restore','--worktree','--source=HEAD'],'tracked')
    print(f"{len(selected['paths'])} derived path(s) staged; {len(selected['held'])} publisher-owned path(s) left out")
    return 0

#: HOW A REWRITTEN MEDIUM IS CARRIED. `_SPLICE` names the three whose text is partly their own,
#: each with a scope a substituter writes in and everything outside it authored; `_WHOLE` names
#: the two a writer composes every byte of — a `.figures.json` holds figures and nothing a
#: person typed, and a card's `.png` is a photograph of a page, drawn whole by the run that
#: names it on both sides of its step so a picture that has not moved is not redrawn.
#:
#: WHICH FILES ARE REWRITTEN IS `graph.json`'s `rewritten` and not these. A suffix answers how
#: to carry a medium — the mechanisms differ per medium and no writer reports one — and cannot
#: answer whether a file was rewritten at all. That second question is the one whose wrong
#: answer destroys: a medium missing from a list, copied whole, lands a stale build's text over
#: a sentence somebody wrote. A rewritten medium in neither list is named and left alone.
#:
#: `_WHOLE_FILES` names individual outputs generated whole in an otherwise authored medium.
#: The purchases program derives every byte of the purchase export from the ledger and its
#: evidence; other rewritten CSVs still have no whole-file carry here.
_SPLICE = (".md", ".mmd", ".py")
_WHOLE = (".json", ".png")
_WHOLE_FILES = {"hardware/ledger/purchases.export.csv"}


def _whole_rewritten(path):
    return _native('sync.whole',path=path)

#: `docgen`'s own marker, and the section `substitute_md` maintains at the end of every markdown
#: file it touches. Between them they are the whole of what a build writes into an authored
#: file, so between them they are the whole of what this hands over.
_LINK = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")
_SOURCES = re.compile(r"## Sources\n\[value\]\(NAME\) texts are updated by:\n"
                      r"(?:- `[^`\n]+`\n)+")


def _rewritten():
    from _bookkeeping import read
    try:
        return set(read('sync.rewritten',_HERE.parent/'graph.json'))
    except ValueError as exc:
        raise SystemExit(str(exc)) from None


def _labels(raw):
    return _native('sync.labels',raw=raw)


def _targets(labels=()):
    query = f"set({' '.join(labels)})" if labels else 'deps(//:everything)'
    q = subprocess.run(['bazel','cquery',query,'--output=files'],cwd=str(_ROOT),capture_output=True,text=True)
    if q.returncode != 0:
        first = next((line for line in q.stderr.splitlines() if line.startswith('ERROR')),'')
        raise SystemExit(f"  the build graph does not load, so nothing here can be read\n  {first}")
    result = _native('sync.targets',root=str(_ROOT),stdout=q.stdout,intermediate=ACTION_INTERMEDIATE)
    print(result['output'],end='')
    return result['pairs']




def _managed(text,suffix,names=None):
    return [tuple(span) for span in _native('sync.managed',text=text,suffix=suffix,names=names)]


def _figures(text,suffix):
    return _native('sync.figures',text=text,suffix=suffix)


def carried(built,tracked,suffix):
    return _native('sync.carried',built=built,tracked=tracked,suffix=suffix)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--write',action='store_true',help='copy what differs into the tree')
    ap.add_argument('--failed',default='',metavar='TARGET[,TARGET…]',help='targets that failed this run; their outputs are not carried')
    ap.add_argument('--targets',default='',metavar='TARGET[,TARGET…]',help='carry these explicitly built producers; default: //:everything')
    scope = ap.add_mutually_exclusive_group()
    scope.add_argument('--solids-only','--runtime-only',dest='runtime_only',action='store_true',help='carry publishable viewer outputs, leaving derived work in bazel-bin')
    scope.add_argument('--derived-only',action='store_true',help='carry docs and media, retaining publisher-owned models and metadata')
    ap.add_argument('--stage',action='store_true',help='stage derived changes and retain the committed model cohort; requires --derived-only')
    args = ap.parse_args()
    if args.stage:
        if not args.derived_only or args.write or args.failed or args.targets:
            ap.error('--stage is used only with --derived-only')
        return stage_derived()
    failed = _native('sync.failed_labels',raw=args.failed)
    labels = _labels(args.targets)
    if args.write:
        q = subprocess.run(['bazel','build','--check_up_to_date',*(labels or ['//:everything'])],cwd=str(_ROOT),capture_output=True,text=True)
        proof = _native('sync.freshness',failed=failed,status=q.returncode,stderr=q.stderr)
        if proof['refused']:
            print(proof['output'],end='')
            return 1
    scoped = _native('sync.carry',root=str(_ROOT),pairs=_targets(labels),runtime_only=args.runtime_only,derived_only=args.derived_only,scope_only=True)
    print(scoped['output'],end='')
    if scoped['status'] is not None:
        return scoped['status']
    result = _native('sync.carry',root=str(_ROOT),pairs=scoped['pairs'],rewritten=_rewritten(),failed=failed,write=args.write)
    print(result['output'],end='')
    return result['status']


def selftest() -> int:
    """The carry, on a build that was handed older text than the tree holds."""
    def holds(got, want, what):
        if got != want:
            raise ValueError(f"{what}\n  carried: {got!r}\n  wanted:  {want!r}")

    sources = ("## Sources\n[value](NAME) texts are updated by:\n"
               "- `/hardware/assembly/_a_sync.py`\n")

    holds(_labels("display-cover, //:enclosure"),
          ["//:display-cover", "//:enclosure"],
          "a scoped target list was not canonicalized")
    sample = "/tmp/bazel-out/darwin/bin/out/display-cover/hardware/panel.step"
    match = _DECLARED.search(sample)
    holds(match.group(1) if match else None, "hardware/panel.step",
          "an ignored declared STEP was not mapped back into the tree")
    holds([_runtime_output(path) for path in (
              "hardware/panel.step",
              "hardware/panel.step.mesh",
              "hardware/panel.scorecard.json",
              "hardware/panel.facts.json",
              "hardware/panel.png",
              "hardware/README.md",
          )],
          [True, True, True, False, False, False],
          "the runtime carry either lost public evidence or admitted presentation work")

    # A MARKDOWN DOC. The build was handed the old sentence; the tree holds the new one and the
    # old figure. What comes back is the new sentence at the build's figure.
    built = f"The wall stands off the pack.\n\nDepth is [473](APPLIANCE_D) mm.\n\n{sources}"
    tree = f"The wall is struck off the can.\n\nDepth is [464](APPLIANCE_D) mm.\n\n{sources}"
    holds(carried(built, tree, ".md"),
          f"The wall is struck off the can.\n\nDepth is [473](APPLIANCE_D) mm.\n\n{sources}",
          "a sentence the build was not handed reached the tree")

    # A SOURCES SECTION IS CARRIED WHOLE, so a script that has just started keeping a doc's
    # markers gets its bullet without anybody typing one.
    two = sources + "- `/hardware/assembly/_b_sync.py`\n"
    holds(carried(f"x\n\n{two}", f"x\n\n{sources}", ".md"), f"x\n\n{two}",
          "a new Sources bullet did not reach the tree")

    # AND APPENDED WHERE THE TREE HAS NONE.
    holds(carried(f"x\n\n{sources}", "x\n", ".md"), f"x\n\n{sources}",
          "a first Sources section did not reach the tree")

    # A NAME THE BUILD DOES NOT CARRY. Somebody typed the marker after the build ran; it waits
    # for the build that reads it rather than being filled with a value nothing decided.
    holds(carried("a\n", "a [?](NEW_ONE) b\n", ".md"), "a [?](NEW_ONE) b\n",
          "a marker the build never saw was written over")

    # A MERMAID CHART. The `%%` line is the build's; the node label draws literally, so a marker
    # standing in one is the chart's own and is left where it is.
    built = "%% span [10](SPAN) mm\nflowchart LR\n  A(( [10](SPAN) mm )) --> B\n"
    tree = "%% span [99](SPAN) mm\nflowchart LR\n  A(( [99](SPAN) mm )) --> B\n"
    holds(carried(built, tree, ".mmd"),
          "%% span [10](SPAN) mm\nflowchart LR\n  A(( [99](SPAN) mm )) --> B\n",
          "a mermaid label the renderer draws was rewritten")

    # A GENERATOR'S OWN .py. Its comment and its docstring carry figures; the line of code
    # beside them is the file's, and a build handed the old code hands back nothing that
    # reaches the new.
    built = ('"""Rib at [30](RIB_Z) mm."""\nWALL = 3.0  # [30](RIB_Z) over the floor\n'
             'LABEL = "rib [30](RIB_Z)"\nKEY = "RIB_Z"\n')
    tree = ('"""Rib at [99](RIB_Z) mm."""\nWALL = 2.4  # [99](RIB_Z) over the floor\n'
            'LABEL = "rib [99](RIB_Z)"\nKEY = "RIB_Z"\n')
    holds(carried(built, tree, ".py"),
          '"""Rib at [30](RIB_Z) mm."""\nWALL = 2.4  # [30](RIB_Z) over the floor\n'
          'LABEL = "rib [30](RIB_Z)"\nKEY = "RIB_Z"\n',
          "a .py the build was not handed came back over the tree's own")

    # A BARE `[` TYPED IN PROSE. `reservoir.py` opens a docstring with a literal `` `[` ``, and
    # `[^\]]*` crosses newlines — read any wider than one comment and one literal and that
    # bracket runs on to the next `](NAME)` and takes every line between as its value.
    built = '"""A `[`-shaped body."""\nWALL = 3.0  # rib at [30](RIB_Z)\n'
    tree = '"""A `[`-shaped body."""\nWALL = 2.4  # rib at [99](RIB_Z)\n'
    holds(carried(built, tree, ".py"),
          '"""A `[`-shaped body."""\nWALL = 2.4  # rib at [30](RIB_Z)\n',
          "a bare `[` in prose swallowed the lines down to the next marker")

    # A .py MID-EDIT does not tokenize, and nothing is carried into a file this cannot read.
    broken = 'WALL = (  # [99](RIB_Z)\n'
    holds(carried(built, broken, ".py"), broken, "a file that does not parse was written into")

    # IDEMPOTENT, so what `--write` changes is what the reading without it named.
    once = carried(built, tree, ".py")
    holds(carried(built, once, ".py"), once, "a second carry moved the file again")

    # THE PURCHASE EXPORT IS GENERATED WHOLE. Exercise the actual comparison and write path
    # with a fresh build, including a tree that does not hold the output yet.
    from contextlib import redirect_stdout
    from tempfile import TemporaryDirectory
    from unittest.mock import patch

    module = sys.modules[__name__]
    pairs, rewritten = {}, set()
    fresh = subprocess.CompletedProcess([], 0, stdout="", stderr="")
    with TemporaryDirectory(prefix="hsm-sync-tree-") as tmp, \
            patch.object(module, "_ROOT", Path(tmp)), \
            patch.object(module, "_targets", return_value=pairs), \
            patch.object(module, "_rewritten", return_value=rewritten), \
            patch.object(subprocess, "run", return_value=fresh):
        def run(*args):
            output = io.StringIO()
            with patch.object(sys, "argv", ["sync_tree.py", *args]), redirect_stdout(output):
                return main(), output.getvalue()

        export = "hardware/ledger/purchases.export.csv"
        built_export = Path(tmp) / "bazel-out/bin/out/ledger-totals" / export
        built_export.parent.mkdir(parents=True)
        built_export.write_bytes(b'purchase_id,total_minor\n"purchase,one",1234\n')
        tree_export = Path(tmp) / export
        pairs[str(built_export)] = export
        rewritten.add(export)
        code, output = run("--write")
        holds(code, 0, f"the generated purchase CSV was not carried: {output}")
        holds(tree_export.read_bytes(), built_export.read_bytes(),
              "the new purchase CSV did not carry the exact generated bytes")
        holds(run()[0], 0, "a carried purchase CSV still reported a difference")

        built_export.write_bytes(b'purchase_id,total_minor\n"purchase,one",5678\n')
        before = tree_export.read_bytes()
        holds(run()[0], 1, "a changed purchase CSV did not report a difference")
        holds(tree_export.read_bytes(), before, "a comparison wrote the purchase CSV")
        holds(run("--write")[0], 0, "an updated purchase CSV made the carry incomplete")
        holds(tree_export.read_bytes(), built_export.read_bytes(),
              "the existing purchase CSV did not carry the exact generated bytes")
        holds(run("--write")[0], 0, "an unchanged purchase CSV made the carry incomplete")

        # A CSV SUFFIX OR THE SAME BASENAME ELSEWHERE IS NOT THE EXPORT. Authored CSVs and
        # unknown rewritten media stay in the tree, and their refusal keeps the carry red.
        protected = ("hardware/ledger/notes.csv", "elsewhere/purchases.export.csv",
                     "hardware/ledger/notes.txt")
        for rel in protected:
            built_file = Path(tmp) / "bazel-out/bin/out/ledger-totals" / rel
            tree_file = Path(tmp) / rel
            built_file.parent.mkdir(parents=True, exist_ok=True)
            tree_file.parent.mkdir(parents=True, exist_ok=True)
            built_file.write_bytes(b"stale build text\n")
            tree_file.write_bytes(b"authored tree text\n")
            pairs[str(built_file)] = rel
            rewritten.add(rel)
        built_export.write_bytes(b'purchase_id,total_minor\n"purchase,one",9012\n')
        code, output = run("--write")
        holds(code, 1, "unknown rewritten files did not keep the carry incomplete")
        holds(tree_export.read_bytes(), built_export.read_bytes(),
              "the purchase CSV was not carried beside an unknown rewritten file")
        holds([(Path(tmp) / rel).read_bytes() for rel in protected],
              [b"authored tree text\n"] * len(protected),
              "an authored CSV or unknown rewritten file was overwritten")
        holds(all(f"{rel} is read back over" in output for rel in protected), True,
              "an unknown rewritten file was not reported")
        holds(f"{export} is read back over" in output, False,
              "the generated purchase CSV was refused beside an unknown file")

    # EVERY MEDIUM THE WRITERS READ BACK OVER HAS A CARRY HERE. A `.rst` in `rewritten` and in
    # neither list is a file `--write` would copy whole, over text nobody generated.
    from collections import Counter
    rewritten = _rewritten()
    kinds = Counter(Path(f).suffix for f in rewritten)
    astray = sorted(f for f in rewritten
                    if Path(f).suffix not in _SPLICE and not _whole_rewritten(f))
    if astray:
        raise ValueError(f"read back over and carried by nothing here: {', '.join(astray)}")

    print(f"  sync_tree selftest: 26 holds, the build's figures and the tree's own text; "
          f"{sum(kinds.values())} files read back over, every medium carried")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(main())
