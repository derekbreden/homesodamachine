#!/usr/bin/env python3
"""The targets a working tree's changes reach, for a build that holds only them.

    tools/cad-venv/bin/python tools/bazel/affected.py          # the targets, one per line
    tools/cad-venv/bin/python tools/bazel/affected.py --why    # each target, and what reaches it
    tools/cad-venv/bin/python tools/bazel/affected.py --base HEAD^ --artifacts
    tools/cad-venv/bin/python tools/bazel/affected.py selftest

    bazel build $(tools/cad-venv/bin/python tools/bazel/affected.py)

A NO-OP BUILD OF THIS TREE IS UNDER A SECOND AND A FULL ONE IS FOURTEEN MINUTES, so what an
edit costs is decided by how much of the graph it reaches. `bazel query rdeps` answers that
against the same BUILD.bazel a build reads, and this hands it the files git says have moved.

A CHANGED FILE NO TARGET NAMES IS THE ONE THAT MATTERS, and it is named on stderr rather than
passed over: the target list below it is then a smaller set than the tree owes, and a build of
that list is not a build of what changed. A file bazel does not know is either outside every
target's inputs or newly added to a graph that has not been regenerated.
"""

import argparse
import io
import importlib.util
import json
import os
import re
import subprocess
import sys
from functools import lru_cache
from pathlib import Path, PurePosixPath

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "tools" / "bazel"))

from gen_build import action_plan, dependency_rules, render_build, target_name  # noqa: E402
from inventory import IMPLICIT_SOLIDS, build_inert, inventory, tracked  # noqa: E402

from _bookkeeping import call as _bookkeeping_call
from inventory import _native_config as _inventory_config

def _native(op,**fields):
    return _bookkeeping_call(op,config=_inventory_config(),**fields)

def _inventory_rows():
    return [[list(generators),made] for generators,made in inventory(tracked()).items()]

def _classification_inputs():
    graph,artifacts = _artifact_presentation_context()
    return dict(graph=graph,artifact_gens=artifacts,declared=declared_outputs(),kinds=_read_kinds())



_BUILD = "BUILD.bazel"
_GRAPH = "tools/bazel/graph.json"
_GEN_BUILD = "tools/bazel/gen_build.py"
_CAD_OUTPUTS = (".step", ".stl", ".glb", ".step.mesh")

#: These two programs move or package an already-described cut; neither is an input to a CAD
#: action.  What they name here is REACH, for provenance: the rules whose members an edit to
#: them stands beside, so `pack.py` can record those members as unproven while the edit is
#: uncommitted.  It is not a build scope.  Asking for a cut of these assemblies to "exercise" a
#: packer change re-cuts every solid they reach, and a cut only reproduces across runs of one
#: OCC build — so on the other publisher's wheel the whole bundle re-addresses to an edit that
#: cannot move a single solid.
_PUBLICATION_SENTINELS = {
    "tools/bazel/sync_tree.py": ("//:cold-core-assembly", "//:enclosure-assembly"),
    "tools/cad-artifacts/pack.py": ("//:cold-core-assembly", "//:enclosure-assembly"),
}


def _git(*args) -> list:
    run = subprocess.run(["git", "-C", str(_ROOT), *args],
                         capture_output=True, text=True)
    if run.returncode != 0:
        detail = next((line for line in run.stderr.splitlines() if line.strip()),
                      f"exit {run.returncode}")
        raise SystemExit(f"git {' '.join(args)} did not answer: {detail}")
    return [line for line in run.stdout.splitlines() if line.strip()]


def _git_paths(root,*args):
    result = subprocess.run(['git','--no-optional-locks','-C',str(root),*args],capture_output=True,text=True)
    if result.returncode != 0:
        detail = next((line for line in result.stderr.splitlines() if line.strip()),f'exit {result.returncode}')
        raise SystemExit(f"git {' '.join(args)} did not answer: {detail}")
    return set(_native('affected.split_paths',text=result.stdout))


def changed(root=None):
    root = _ROOT if root is None else root
    return _native('affected.changed',diff=_git_paths(root,'diff','--name-only','--no-renames','-z','HEAD'),untracked=_git_paths(root,'ls-files','--others','--exclude-standard','-z'))


def changed_between(base: str, head: str = "HEAD") -> list:
    """Every old and new path changed between two commits."""
    return _diff_paths(_git("diff", "--name-status", "--find-renames", base, head))


def _diff_paths(lines):
    return _native('affected.diff_paths',lines=lines)


def _normalized_graph(text):
    graph = _native('affected.normalized_graph',text=text)
    return None if graph is None else {name:{key:frozenset(paths) for key,paths in row.items()} for name,row in graph.items()}


def _artifact_projection(graph):
    selected,names = _native('affected.artifact_projection',graph=graph)
    return {name:{key:frozenset(paths) for key,paths in row.items()} for name,row in selected.items()},tuple(names)


def nonartifact_graph_delta(before_text,after_text):
    return _native('affected.graph_delta',before=before_text,after=after_text)


def _build_projection(text,roots):
    return _native('affected.build_projection',text=text,roots=roots)


def nonartifact_build_delta(before_text,after_text,artifact_names):
    return _native('affected.build_delta',before=before_text,after=after_text,roots=artifact_names)


def _artifact_build_roots(graph):
    return tuple(_native('affected.artifact_roots',graph=graph,inventory=_inventory_rows()))


def _git_file(ref: str, path: str):
    run = subprocess.run(["git", "-C", str(_ROOT), "show", f"{ref}:{path}"],
                         capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def _git_tree(ref: str):
    run = subprocess.run(["git", "-C", str(_ROOT), "rev-parse", f"{ref}^{{tree}}"],
                         capture_output=True, text=True)
    return run.stdout.strip() if run.returncode == 0 else None


def _generated_build_matches(text):
    try:
        return _native('affected.equal',a=render_build()[0],b=text)
    except (Exception,SystemExit):
        return False


def _safe_metadata_paths(paths,artifacts_only,graph_safe,build_generated,build_safe=True):
    return set(_native('affected.safe_paths',paths=paths,artifacts_only=artifacts_only,graph_safe=graph_safe,build_generated=build_generated,build_safe=build_safe))


def safely_scoped_metadata(paths,artifacts_only,base=None,head='HEAD'):
    if not _native('affected.metadata_needed',paths=paths,artifacts_only=artifacts_only):
        return set()
    if base:
        before,after = _git_file(base,_GRAPH),_git_file(head,_GRAPH)
        tree = _git_tree(head)
        at_head = tree is not None and _native('affected.equal',a=tree,b=_git_tree('HEAD'))
        build_text = _git_file(head,_BUILD) if at_head else None
        before_build = _git_file(base,_BUILD)
    else:
        before = _git_file('HEAD',_GRAPH)
        after,build_text = _native('affected.read_metadata',root=str(_ROOT))
        before_build = _git_file('HEAD',_BUILD)
    generated = _generated_build_matches(build_text) if build_text is not None else False
    return set(_native('affected.metadata',paths=paths,artifacts_only=artifacts_only,before=before,after=after,before_build=before_build,build_text=build_text,build_generated=generated,inventory=_inventory_rows()))


def known(paths):
    if not paths:
        return [],[]
    result = subprocess.run(['bazel','query','kind("source file", //:*)'],cwd=str(_ROOT),capture_output=True,text=True)
    if result.returncode != 0:
        detail = next((line for line in result.stderr.splitlines() if line.startswith('ERROR')),f'exit {result.returncode}')
        raise SystemExit(f'bazel could not enumerate source inputs: {detail}')
    hit,miss = _native('affected.known',paths=paths,stdout=result.stdout)
    return hit,miss


def targets(paths):
    if not paths:
        return []
    query = f"rdeps(//..., set({' '.join(f'//:{p}' for p in paths)}))"
    result = subprocess.run(['bazel','query',query],cwd=str(_ROOT),capture_output=True,text=True)
    if result.returncode != 0:
        detail = next((line for line in result.stderr.splitlines() if line.startswith('ERROR')),f'exit {result.returncode}')
        raise SystemExit(f'bazel could not compute the affected graph: {detail}')
    return _native('affected.query_targets',stdout=result.stdout)


def manifest_targets(paths):
    actions,_ = action_plan()
    reached,known = _native('affected.manifest',paths=paths,rules=dependency_rules(actions))
    return reached,known


def sentinel_targets(paths):
    return set(_native('affected.sentinels',paths=paths))


def artifact_targets():
    return set(_native('affected.artifact_targets',inventory=_inventory_rows()))


@lru_cache(maxsize=1)
def declared_outputs():
    return frozenset(_native('affected.declared',path=str(_ROOT/'tools/bazel/graph.json')))


@lru_cache(maxsize=1)
def _read_kinds():
    result = _native('affected.kinds',path=str(_ROOT/'tools/bazel/graph.json'))
    return None if result is None else frozenset(result)


def read_kind(path):
    return _native('affected.read_kind',path=path,kinds=_read_kinds())


def artifact_sidecar_output(path):
    return _native('affected.sidecar',path=path,declared=declared_outputs())


def artifact_global(path):
    return _native('affected.global',path=path)


def unscoped_changes(paths,known_paths,artifacts_only,safely_scoped=frozenset()):
    return _native('affected.risky',paths=paths,known=known_paths,artifacts_only=artifacts_only,safe=safely_scoped,**_classification_inputs())


def write_targets(found,stream=None):
    if stream is None:
        stream = sys.stdout
    stream.write(_native('affected.target_text',found=found))


@lru_cache(maxsize=1)
def _artifact_presentation_context():
    graph,artifacts = _native('affected.presentation_context',path=str(_ROOT/'tools/bazel/graph.json'),inventory=_inventory_rows())
    return graph,set(artifacts)


def artifact_presentation_only(path):
    graph,artifacts = _artifact_presentation_context()
    return _native('affected.presentation',path=path,graph=graph,artifact_gens=artifacts)


def artifact_unknown(path,artifacts_only=False):
    return _native('affected.unknown',path=path,artifacts_only=artifacts_only,**_classification_inputs())


def selftest() -> int:
    holds = 0

    def hold(label, ok, got=""):
        nonlocal holds
        holds += ok
        print(f"  {'ok  ' if ok else 'FAIL'} {label}" + ("" if ok else f" — {got}"))

    hold("a diff rename names both sides",
         _diff_paths(["R100\told/a.py\tnew/b.py"]) == ["new/b.py", "old/a.py"])
    hold("every tracked path changed() names really differs from HEAD",
         all(_git("diff", "--name-only", "HEAD", "--", path)
             for path in set(changed())
             - _git_paths(_ROOT, "ls-files", "--others", "--exclude-standard", "-z")))

    def graph_node(reads=(), writes=(), rewritten=()):
        return {"reads": list(reads), "writes": list(writes),
                "rewritten": list(rewritten)}

    quick_before = {
        "hardware/cad/cut.py": graph_node(writes=("hardware/cad/part.step",)),
        "hardware/quickstart/_build.py": graph_node(
            reads=("hardware/quickstart/00-install.html",),
            writes=("hardware/quickstart/quick-start.pdf",)),
        "hardware/quickstart/quickstart_art.py": graph_node(
            writes=("hardware/quickstart/art/mount-drop.png",)),
    }
    quick_after = json.loads(json.dumps(quick_before))
    quick_after["hardware/quickstart/_build.py"]["reads"] += [
        "hardware/quickstart/01-mount.html",
        "hardware/quickstart/art/mount-final-clean.png",
    ]
    quick_after["hardware/quickstart/quickstart_art.py"]["writes"].append(
        "hardware/quickstart/art/mount-final-clean.png")
    quick_delta_safe = nonartifact_graph_delta(
        json.dumps(quick_before), json.dumps(quick_after))
    quick_metadata = _safe_metadata_paths(
        [_BUILD, _GRAPH], True, quick_delta_safe, build_generated=True)
    hold("a Quick Start-only graph delta reaches zero CAD rules",
         quick_delta_safe
         and unscoped_changes([_BUILD, _GRAPH], [_BUILD, _GRAPH], True,
                              quick_metadata) == [])

    build_before = '''load("//:defs.bzl", "genrule")

genrule(
    name = "cad-runtime",
    srcs = ["hardware/cad/tool.py"],
    outs = ["out/cad-runtime/hardware/cad/runtime.json"],
)

genrule(
    name = "cad-source",
    srcs = ["hardware/cad/source.py"],
    outs = ["pysrc/hardware/cad/source.py"],
)

genrule(
    name = "cad-cut",
    srcs = [
        ":out/cad-runtime/hardware/cad/runtime.json",
        "pysrc/hardware/cad/source.py",
    ],
)

genrule(
    name = "quickstart-build",
    srcs = ["hardware/quickstart/old.html"],
)'''
    build_after = build_before.replace(
        'hardware/quickstart/old.html', 'hardware/quickstart/new.html')
    hold("a generated Quick Start BUILD delta leaves the CAD closure byte-identical",
         nonartifact_build_delta(build_before, build_after, ("cad-cut",)))
    hold("a CAD rule or its local runtime cannot use the metadata exemption",
         not nonartifact_build_delta(
             build_before,
             build_after.replace('hardware/cad/tool.py', 'hardware/cad/new-tool.py'),
             ("cad-cut",))
         and not nonartifact_build_delta(
             build_before,
             build_after.replace('hardware/cad/source.py',
                                 'hardware/cad/new-source.py', 1),
             ("cad-cut",))
         and _GEN_BUILD in _safe_metadata_paths(
             [_BUILD, _GRAPH, _GEN_BUILD], True, True, True, True)
         and _GEN_BUILD not in _safe_metadata_paths(
             [_BUILD, _GRAPH, _GEN_BUILD], True, True, True, False))

    cad_after = json.loads(json.dumps(quick_before))
    cad_after["hardware/cad/cut.py"]["reads"].append("hardware/cad/new.dat")
    upstream_before = {
        "hardware/cad/input.py": graph_node(
            reads=("hardware/cad/source-a.dat",),
            writes=("hardware/cad/shape-input.json",)),
        "hardware/cad/cut.py": graph_node(
            reads=("hardware/cad/shape-input.json",),
            writes=("hardware/cad/part.step",)),
    }
    upstream_after = json.loads(json.dumps(upstream_before))
    upstream_after["hardware/cad/input.py"]["reads"] = ["hardware/cad/source-b.dat"]
    collision_after = json.loads(json.dumps(quick_before))
    collision_after["hardware/quickstart/cut.py"] = graph_node(
        writes=("hardware/quickstart/sheet.pdf",))
    hold("CAD, upstream, and artifact-name graph changes stay global",
         not nonartifact_graph_delta(json.dumps(quick_before), json.dumps(cad_after))
         and not nonartifact_graph_delta(json.dumps(upstream_before),
                                         json.dumps(upstream_after))
         and not nonartifact_graph_delta(json.dumps(quick_before),
                                         json.dumps(collision_after)))

    no_build_proof = _safe_metadata_paths(
        [_BUILD, _GRAPH], True, quick_delta_safe, build_generated=False)
    hold("ambiguous graph metadata still widens the CAD slice",
         not nonartifact_graph_delta("{", json.dumps(quick_after))
         and _safe_metadata_paths([_BUILD], True, True, True) == set()
         and unscoped_changes([_BUILD, _GRAPH], [_BUILD, _GRAPH], True,
                              no_build_proof) == [_BUILD])

    hold("firmware outside the graph does not widen the CAD slice",
         not artifact_unknown("firmware/src/main.cpp")
         and artifact_unknown("hardware/new_part.py")
         and not artifact_unknown("hardware/cad-artifacts.json")
         and not artifact_unknown("hardware/quickstart/studies/new/decode_art.py", True)
         and not artifact_unknown("hardware/quickstart/studies/new/.gitignore", True)
         and artifact_unknown(".dockerignore")
         and artifact_unknown("hardware/new-image.png")
         and not artifact_unknown("hardware/new-image.png", artifacts_only=True))
    hold("a kind no generator reads bounds nothing, in either lane",
         not read_kind("hardware/off-the-shelf-parts/C14 - 1.jpeg")
         and not artifact_unknown("hardware/off-the-shelf-parts/C14 - 1.jpeg", True)
         and not artifact_unknown("hardware/off-the-shelf-parts/C14 - 1.jpeg"))
    hold("a kind a generator does read still bounds what bazel cannot name",
         read_kind("hardware/new_part.py")
         and read_kind("hardware/off-the-shelf-parts/new.step")
         and artifact_unknown("hardware/new_part.py", True)
         and artifact_unknown("hardware/off-the-shelf-parts/new.step", True))
    hold("rewritten presentation is outside the artifact slice",
         artifact_presentation_only(
             "hardware/printed-parts/enclosure/display-cover/README.md"))
    hold("a slicer project is inert in both build lanes",
         build_inert("hardware/printed-parts/petgf.3mf")
         and not read_kind("hardware/printed-parts/petgf.3mf")
         and not artifact_unknown("hardware/printed-parts/petgf.3mf")
         and not artifact_unknown("hardware/printed-parts/petgf.3mf", True)
         and artifact_presentation_only("hardware/printed-parts/petgf.3mf"))
    _slicer = ["hardware/printed-parts/zone-c/funnel-mold/print-profile.json",
               "hardware/printed-parts/zone-c/funnel-mold/corner-trial-profile.json",
               "hardware/printed-parts/zone-c/funnel-mold/layer-review.json",
               "hardware/printed-parts/zone-c/funnel-mold/toolpath-review.json",
               "hardware/printed-parts/zone-c/funnel-mold/slice-review.json",
               "hardware/printed-parts/zone-c/funnel-mold/repaired-wall-review.json",
               "hardware/printed-parts/zone-c/funnel-mold/containment-review.json",
               "hardware/printed-parts/zone-c/funnel/wall-review.json",
               "hardware/printed-parts/zone-c/funnel-mold/"
               "funnel-mold-presets.bbscfg"]
    hold("a preset bundle and the verification records are inert with the project",
         all(build_inert(p) and not read_kind(p) and not artifact_unknown(p)
             and not artifact_unknown(p, True) for p in _slicer)
         and unscoped_changes(_slicer, [], True) == []
         and not build_inert(
             "hardware/printed-parts/zone-c/funnel-mold/README.figures.json")
         and artifact_unknown(
             "hardware/printed-parts/zone-c/funnel-mold/mechanical-verification.json", True))
    hold("a data-bearing document stays in the artifact slice",
         not artifact_presentation_only("hardware/ledger/bom.md"))
    hold("only artifact inputs widen the artifact slice",
         unscoped_changes(["BUILD.bazel"], ["BUILD.bazel"], True) == ["BUILD.bazel"]
         and unscoped_changes(["hardware/part.py"], ["hardware/part.py"], True) == []
         and not artifact_unknown("hardware/part.lint-answers", True)
         and unscoped_changes(["tools/bazel/affected.py"],
                              ["tools/bazel/affected.py"], True) == []
         and unscoped_changes([".github/workflows/derive.yml"], [], True)
             == [".github/workflows/derive.yml"])
    hold("publication machinery states its reach and owes no cut",
         not artifact_global("tools/bazel/sync_tree.py")
         and artifact_unknown("tools/cad-artifacts/pack.py", True)
         and sentinel_targets(["tools/cad-artifacts/pack.py"])
             == {"//:cold-core-assembly", "//:enclosure-assembly"}
         and sentinel_targets(["hardware/part.py"]) == set()
         and artifact_sidecar_output(
             "hardware/manifold-layout/enclosure-assembly.scorecard.json"))
    empty = io.StringIO()
    write_targets([], empty)
    hold("zero targets write zero bytes", empty.getvalue() == "", repr(empty.getvalue()))
    # BAZEL IS THE ONE THING THIS CANNOT ASK FOR ITSELF. `known` and `targets` shell out to
    # `bazel query`, and a test bazel is running holds the server lock this workspace shares —
    # a query under it waits for the build that started it. The holds above stand on their own;
    # the three below are taken where a shell can reach bazel.
    if os.environ.get("TEST_SRCDIR"):
        print("  --   bazel query holds skipped: a query under `bazel test` waits on its own "
              "server. Run `affected.py selftest` from a shell for them.")
        print(f"affected selftest {holds}/{holds} (of the holds this run can take)")
        return 0 if holds == 17 else 1

    src = ["hardware/printed-parts/cold-core/foam-cap/foam_cap.rs"]
    hit, miss = known(src)
    hold("a tracked source is a label bazel knows", hit == src, f"{hit!r} {miss!r}")
    t = targets(src)
    hold("a leaf part reaches its own target", "//:foam-cap" in t, str(t))
    hold("and not an unrelated artifact branch", "//:funnel-mold" not in t,
         f"{len(t)} targets")
    hold("a path bazel does not name is reported, not dropped",
         known(["no/such/file.py"]) == ([], ["no/such/file.py"]))
    hold("nothing changed is no targets", targets([]) == [] and changed() is not None)
    hold("artifact rules are a strict build slice",
         "//:display-cover" in artifact_targets() and "//:everything" not in artifact_targets())
    print(f"affected selftest {holds}/23")
    return 0 if holds == 23 else 1


def say_if_unshimmed() -> None:
    """Name it on stderr when this interpreter has no import shim.

    THE COST OF NOT HAVING IT LANDS ON A BUILD AND NOTHING ELSE SAYS SO. Every CAD action
    reaches `tools/cad-venv/bin/python` by absolute path, outside the sandbox, so the
    interpreter is not a declared input to any of them — bazel cannot see the shim, and a
    checkout that never installed it builds the same solids while paying VTK's 12 s and
    145 MB in each of 85 processes. Green, correct, and slow, with nothing to read.

    An advisory and not a gate: the solids are byte-identical either way, so a tree without
    the shim is slow and not wrong, and a red step would be claiming otherwise.

    Only asked when this IS the CAD venv's python — `install.py` answers for whatever
    interpreter imports it, so any other one would be answering about itself.

    BY `sys.prefix` AND NOT BY `sys.executable`. The venv's `bin/python` is a symlink to the
    interpreter it was built from, so resolving it lands in homebrew's cellar and no venv is
    ever recognised — a guard that reads as careful and returns early every time, leaving the
    advisory silent on exactly the tree that needs it. `sys.prefix` is the venv itself."""
    venv = _ROOT / "tools" / "cad-venv"
    try:
        if Path(sys.prefix).resolve() != venv.resolve():
            return
        spec = importlib.util.spec_from_file_location(
            "_hsm_shim_install", venv.parent / "cad-venv-site" / "install.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        gone = mod.missing()
    except Exception:
        return
    if gone:
        print("this interpreter has no import shim — every CAD action will load VTK, which "
              "nothing here draws with, for 12 s and 145 MB apiece:", file=sys.stderr)
        print(f"    {sys.executable} tools/cad-venv-site/install.py", file=sys.stderr)


def main(argv) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cmd", nargs="?", help="selftest")
    ap.add_argument("--why", action="store_true", help="name what reaches each target")
    ap.add_argument("--base", help="read committed changes from BASE instead of the worktree")
    ap.add_argument("--head", default="HEAD", help="range endpoint used with --base")
    ap.add_argument("--artifacts", action="store_true",
                    help="print only rules that publish members of the CAD bundle")
    ap.add_argument("--manifest", action="store_true",
                    help="with --artifacts, read the shared action plan without starting Bazel")
    ap.add_argument("--all-artifacts", action="store_true",
                    help="print every rule that publishes a CAD bundle member")
    args = ap.parse_args(argv)
    if args.manifest and not args.artifacts:
        ap.error("--manifest requires --artifacts")
    if args.cmd == "selftest":
        return selftest()
    if args.all_artifacts:
        write_targets(sorted(artifact_targets()))
        return 0

    if not args.manifest:
        say_if_unshimmed()

    moved = changed_between(args.base, args.head) if args.base else changed()
    moved = _native('affected.filter_moved',paths=moved,artifacts_only=False)
    scoped_metadata = safely_scoped_metadata(moved, args.artifacts, args.base, args.head)
    if args.artifacts:
        moved = _native('affected.filter_moved',paths=moved,artifacts_only=True,**_classification_inputs())
    if not moved:
        print("nothing has moved — a build of this tree holds nothing to do", file=sys.stderr)
        return 0
    if args.manifest:
        found, hit = manifest_targets(moved)
    else:
        hit, miss = known(moved)
    risky = unscoped_changes(moved, hit, args.artifacts, scoped_metadata)
    if risky:
        print(f"{len(risky)} changed CAD path(s) cannot be safely scoped — this slice widens "
              f"to every artifact rule:", file=sys.stderr)
        for p in risky:
            print(f"    {p}", file=sys.stderr)
    if not args.manifest:
        found = targets(hit)
    found = _native('affected.final_targets',found=found,risky=risky,artifacts_only=args.artifacts,artifact_targets=artifact_targets() if args.artifacts else [])
    # A PUBLICATION SENTINEL OWES NO CUT, BECAUSE IT CANNOT MOVE A SOLID. `sync_tree.py` copies
    # bytes a rule already wrote and `pack.py` reads and tars them; neither is an input to a CAD
    # action, which is the same reason `artifact_global` returns False for both. Building their
    # two scorecard producers to "exercise" a change re-cuts the ~95 solids those assemblies
    # reach — and a cut is only reproducible across runs of ONE OCC build, so on a machine whose
    # wheel differs from the one that pointed at the pointer file every one of those members moves. That is
    # the whole bundle re-addressed to the packer's own edit. `sentinel_targets` still states the
    # reach for provenance, where naming what an uncommitted packer touches is exactly right.
    if args.why:
        reach = {path:(manifest_targets([path])[0] if args.manifest else targets([path])) for path in hit}
        print(_native('affected.why',found=found,paths=hit,reach=reach),end='')
    else:
        write_targets(found)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
