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
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "tools" / "bazel"))

from gen_build import render_build, target_name  # noqa: E402
from inventory import IMPLICIT_SOLIDS, inventory, tracked  # noqa: E402


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


def _git_paths(root, *args) -> set:
    """The paths one git command names, read NUL-separated so a space in a name is a name.

    `--no-optional-locks` keeps a read off `.git/index.lock`. With several sessions live, a
    refresh that has to take that lock is a refresh that loses a race, and asking what the tree
    holds has no business writing the index to find out."""
    run = subprocess.run(["git", "--no-optional-locks", "-C", str(root), *args],
                         capture_output=True, text=True)
    if run.returncode != 0:
        detail = next((line for line in run.stderr.splitlines() if line.strip()),
                      f"exit {run.returncode}")
        raise SystemExit(f"git {' '.join(args)} did not answer: {detail}")
    return {path for path in run.stdout.split("\0") if path}


def changed(root=None) -> list:
    """Every path this worktree holds that HEAD does not — staged, unstaged and untracked alike.

    A build reads the worktree, so what is staged and what is merely saved reach it the same.

    ASKED AGAINST HEAD, NOT AGAINST THE INDEX. `status` compares the worktree to the index and
    answers that half from stat data, so a file whose bytes are already HEAD's reads as modified
    on a stale stat cache, and reads as modified again when a staged edit and an unstaged one
    cancel. Neither is a change a build has to see, `update-index --refresh` clears only the
    first, and it writes the index to do it. `diff HEAD` hashes whatever stat cannot settle, so
    it never names a path whose content is already HEAD's, and `--no-renames` names both sides
    of a rename, which is the reach an edit actually has.

    `ls-files --others` names untracked files one by one. `status` collapses an untracked
    DIRECTORY to `dir/` unless asked otherwise, and a trailing slash is not a path a build
    scopes on, so files under a newly added directory reached nothing here."""
    root = _ROOT if root is None else root
    out = _git_paths(root, "diff", "--name-only", "--no-renames", "-z", "HEAD")
    out |= _git_paths(root, "ls-files", "--others", "--exclude-standard", "-z")
    return sorted(path for path in out if path)


def changed_between(base: str, head: str = "HEAD") -> list:
    """Every old and new path changed between two commits."""
    return _diff_paths(_git("diff", "--name-status", "--find-renames", base, head))


def _diff_paths(lines: list[str]) -> list:
    """Parse `git diff --name-status`, retaining both sides of a rename or copy."""
    out = set()
    for line in lines:
        fields = line.split("\t")
        if not fields:
            continue
        if fields[0].startswith(("R", "C")) and len(fields) >= 3:
            out.update(fields[1:3])
        elif len(fields) >= 2:
            out.add(fields[1])
    return sorted(p for p in out if p and not p.endswith("/"))


def _normalized_graph(text: str):
    """The graph's action-affecting fields, or ``None`` when its meaning is ambiguous."""
    try:
        raw = json.loads(text)
    except (TypeError, ValueError):
        return None
    fields = {"reads", "writes", "rewritten"}
    if not isinstance(raw, dict):
        return None
    out = {}
    for gen, seen in raw.items():
        if (not isinstance(gen, str) or not isinstance(seen, dict)
                or set(seen) != fields):
            return None
        node = {}
        for field in fields:
            paths = seen[field]
            if not isinstance(paths, list) or not all(isinstance(p, str) for p in paths):
                return None
            node[field] = frozenset(paths)
        out[gen] = node
    return out


def _artifact_projection(graph: dict) -> tuple:
    """The declarations which can feed or join a CAD action, plus its generated names."""
    artifacts = {
        gen for gen, seen in graph.items()
        if gen in IMPLICIT_SOLIDS
        or any(path.endswith(_CAD_OUTPUTS) for path in seen["writes"])
    }
    held = set(artifacts)
    while True:
        inputs = set().union(*(
            graph[gen]["reads"] | graph[gen]["rewritten"] | graph[gen]["writes"]
            for gen in held
        )) if held else set()
        more = {gen for gen, seen in graph.items() if seen["writes"] & inputs} - held
        if not more:
            break
        held |= more

    # An unrelated generator with the same stem changes an artifact rule's generated label.
    stems = [Path(gen).stem.strip("_").replace("_", "-") for gen in graph]
    shared = {stem for stem in stems if stems.count(stem) > 1}
    names = tuple(sorted(target_name(gen, shared) for gen in artifacts))
    return {gen: graph[gen] for gen in held}, names


def nonartifact_graph_delta(before_text: str, after_text: str) -> bool:
    """Whether a graph edit provably leaves every CAD-producing action unchanged.

    This is deliberately semantic rather than path-based. A Quick Start producer may gain an
    HTML input and PNG outputs without recutting sixty-two solids. A changed CAD node, a helper
    feeding one, a co-writer grouped with one, a target-name collision, or a graph this reader
    does not understand all fail closed.
    """
    before = _normalized_graph(before_text)
    after = _normalized_graph(after_text)
    if before is None or after is None:
        return False
    return _artifact_projection(before) == _artifact_projection(after)


def _build_projection(text: str, roots: tuple) -> dict | None:
    """Generated BUILD blocks that can change one of ``roots``, including local deps."""
    blocks = {}
    outputs = {}
    global_chunks = []
    for block in text.split("\n\n"):
        match = re.search(r'^\s*name = "([^"]+)",\s*$', block, re.MULTILINE)
        if match:
            name = match.group(1)
            blocks[name] = block
            outs = re.search(r'\bouts\s*=\s*\[(.*?)\]\s*,', block, re.DOTALL)
            if outs:
                for path in re.findall(r'"([^"]+)"', outs.group(1)):
                    outputs[path] = name
        else:
            global_chunks.append(block)
    held = {"__global__": "\n\n".join(global_chunks)}
    pending = list(roots)
    while pending:
        name = pending.pop()
        if name in held:
            continue
        block = blocks.get(name)
        if block is None:
            return None
        held[name] = block
        for label in re.findall(r'"([^"]+)"', block):
            dep = label.removeprefix(":")
            provider = dep if dep in blocks else outputs.get(dep)
            if provider and provider not in held:
                pending.append(provider)
    return held


def nonartifact_build_delta(before_text: str, after_text: str,
                            artifact_names: tuple) -> bool:
    """Whether every generated BUILD block in the CAD target closure is byte-identical."""
    before = _build_projection(before_text, artifact_names)
    after = _build_projection(after_text, artifact_names)
    return before is not None and after is not None and before == after


def _artifact_build_roots(graph: dict) -> tuple:
    """Actual generated target names for every action in the CAD producer closure."""
    held = set(_artifact_projection(graph)[0])
    inv = inventory(tracked())
    seen, shared = set(), set()
    for gens in inv:
        for gen in gens:
            stem = Path(gen).stem.strip("_").replace("_", "-")
            (shared if stem in seen else seen).add(stem)
    names = set()
    for gens in inv:
        if held.intersection(gens):
            names.add(target_name(gens[0], shared))
    return tuple(sorted(names))


def _git_file(ref: str, path: str):
    run = subprocess.run(["git", "-C", str(_ROOT), "show", f"{ref}:{path}"],
                         capture_output=True, text=True)
    return run.stdout if run.returncode == 0 else None


def _git_tree(ref: str):
    run = subprocess.run(["git", "-C", str(_ROOT), "rev-parse", f"{ref}^{{tree}}"],
                         capture_output=True, text=True)
    return run.stdout.strip() if run.returncode == 0 else None


def _generated_build_matches(text: str) -> bool:
    try:
        return render_build()[0] == text
    except (Exception, SystemExit):
        return False


def _safe_metadata_paths(paths: list, artifacts_only: bool, graph_safe: bool,
                         build_generated: bool, build_safe: bool = True) -> set:
    """Metadata paths a CAD-only slice may ignore after their semantics were proved."""
    paths = set(paths)
    if not artifacts_only or _GRAPH not in paths or not graph_safe:
        return set()
    safe = {_GRAPH}
    if _BUILD in paths and build_generated and build_safe:
        safe.add(_BUILD)
    if _GEN_BUILD in paths and build_generated and build_safe:
        safe.add(_GEN_BUILD)
    return safe


def safely_scoped_metadata(paths: list, artifacts_only: bool, base: str = None,
                           head: str = "HEAD") -> set:
    """Prove a graph/BUILD edit changes no CAD action; otherwise return no exemptions."""
    if not artifacts_only or _GRAPH not in paths:
        return set()
    if base:
        before = _git_file(base, _GRAPH)
        after = _git_file(head, _GRAPH)
        # `render_build` reads this checkout. It can prove a committed head only when that head
        # is the checkout; race checks against a fetched future tip remain deliberately global.
        at_head = _git_tree(head) is not None and _git_tree(head) == _git_tree("HEAD")
        build_text = _git_file(head, _BUILD) if at_head else None
        before_build = _git_file(base, _BUILD)
    else:
        before = _git_file("HEAD", _GRAPH)
        try:
            after = (_ROOT / _GRAPH).read_text()
            build_text = (_ROOT / _BUILD).read_text()
        except OSError:
            after = build_text = None
        before_build = _git_file("HEAD", _BUILD)
    graph_safe = (before is not None and after is not None
                  and nonartifact_graph_delta(before, after))
    build_generated = (build_text is not None and _generated_build_matches(build_text))
    normalized = _normalized_graph(after)
    artifact_names = _artifact_build_roots(normalized) if normalized is not None else ()
    build_safe = (
        before_build is not None
        and build_text is not None
        and bool(artifact_names)
        and nonartifact_build_delta(before_build, build_text, artifact_names)
    )
    return _safe_metadata_paths(
        paths, artifacts_only, graph_safe, build_generated, build_safe
    )


def known(paths: list) -> tuple:
    """The paths bazel names as source labels, and the ones it does not."""
    if not paths:
        return [], []
    labels = [f"//:{p}" for p in paths]
    # Asking for the package's source-file universe keeps a genuinely unknown path from
    # turning the query itself red. Every generated rule lives in this root package.
    q = subprocess.run(["bazel", "query", 'kind("source file", //:*)'],
                       cwd=str(_ROOT), capture_output=True, text=True)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith("ERROR")),
                      f"exit {q.returncode}")
        raise SystemExit(f"bazel could not enumerate source inputs: {detail}")
    seen = {l.strip() for l in q.stdout.splitlines() if l.startswith("//:")}
    hit = [p for p, l in zip(paths, labels) if l in seen]
    return hit, [p for p in paths if p not in set(hit)]


def targets(paths: list) -> list:
    """Every target `paths` reach, source labels dropped."""
    if not paths:
        return []
    q = subprocess.run(
        ["bazel", "query", f"rdeps(//..., set({' '.join(f'//:{p}' for p in paths)}))"],
        cwd=str(_ROOT), capture_output=True, text=True)
    if q.returncode != 0:
        detail = next((line for line in q.stderr.splitlines() if line.startswith("ERROR")),
                      f"exit {q.returncode}")
        raise SystemExit(f"bazel could not compute the affected graph: {detail}")
    out = []
    for line in q.stdout.splitlines():
        line = line.strip()
        # A source file is its own rdep. What a build takes is the rules.
        if line.startswith("//:") and not any(line.endswith(s) for s in
                                              (".py", ".js", ".json", ".md", ".step", ".mmd",
                                               ".html", ".css", ".svg", ".png", ".dxf", ".glb",
                                               ".pdf", ".3mf", ".stl", ".ts", ".tsx", ".sh")):
            out.append(line)
    return sorted(set(out))


def sentinel_targets(paths) -> set:
    """The artifact rules a publication sentinel in `paths` names for itself.

    `_PUBLICATION_SENTINELS` states reach `targets` cannot see. These files carry a solid that
    is already cut rather than being read while one is being cut, so no rule lists them as a
    source and an rdeps walk over source labels finds nothing.

    FOR PROVENANCE, NOT FOR A BUILD. `pack.py` asks this to name the members an uncommitted
    packer stands beside; nothing adds the answer to a set of targets to cut."""
    moved = set(paths)
    return {target for path, targets_for_path in _PUBLICATION_SENTINELS.items()
            if path in moved for target in targets_for_path}


def artifact_targets() -> set:
    """Generator rules that publish at least one member of the CAD bundle."""
    inv = inventory(tracked())
    seen, shared = set(), set()
    for gens in inv:
        for gen in gens:
            stem = Path(gen).stem.strip("_").replace("_", "-")
            (shared if stem in seen else seen).add(stem)
    return {
        f"//:{target_name(gens[0], shared)}"
        for gens, made in inv.items()
        if any(p.endswith(_CAD_OUTPUTS) for p in made["solids"])
    }


def declared_outputs() -> set:
    try:
        graph = json.loads((_ROOT / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return set()
    return {path for node in graph.values() for path in node.get("writes", ())}


def artifact_sidecar_output(path: str) -> bool:
    """Whether `path` is generated viewer evidence, not an authored action input.

    Sidecars are committed atomically with the lock, so every later source range crosses the
    preceding publication commit. Treating that generated output as fresh input debt rebuilds
    its producer after every unrelated source push. The source that makes it remains a normal
    graph input and selects the producer; a sidecar-only race is handled at the lock boundary.
    """
    return path.endswith(".scorecard.json") and path in declared_outputs()


def artifact_global(path: str) -> bool:
    """Whether an edit changes how every artifact action is described or executed."""
    if path in {".bazelrc", ".bazelversion", ".dockerignore", "BUILD.bazel", "MODULE.bazel",
                "MODULE.bazel.lock", "tools/cad-requirements.txt"}:
        return True
    # This publisher selects and carries already-described actions; it cannot move geometry.
    # Other workflows are not assumed inert: image, derive and runner changes can change the
    # machine or route an artifact action runs under, so an accumulated edit to one stays global.
    if path.startswith(".github/workflows/"):
        return path != ".github/workflows/publish.yml"
    # Selection code decides WHICH already-described actions run; it is not an input to any
    # artifact action.  Making its own edits global forces the very full-tree build a scoping
    # correction is meant to remove.  The selftest inventory likewise describes test runners,
    # not published solids.
    if path in {"tools/bazel/affected.py", "tools/bazel/selftests.json"}:
        return False
    if path in _PUBLICATION_SENTINELS:
        return False
    return path.startswith(("tools/bazel/", "tools/cad-artifacts/",
                            "tools/cad-venv-site/", "tools/ci-image/"))


def unscoped_changes(paths: list, known_paths: list, artifacts_only: bool,
                     safely_scoped: set = frozenset()) -> list:
    """Changes whose effect cannot be bounded by Bazel reverse dependencies."""
    known_set = set(known_paths)
    return sorted(
        path for path in paths
        if path not in safely_scoped and (
            artifact_global(path)
            or (path not in known_set and artifact_unknown(path, artifacts_only))
        )
    )


def write_targets(found: list, stream=None) -> None:
    """Write labels one per line, and exactly zero bytes for an empty slice."""
    if stream is None:
        stream = sys.stdout
    if found:
        stream.write("\n".join(found) + "\n")


@lru_cache(maxsize=1)
def _artifact_presentation_context() -> tuple:
    try:
        graph = json.loads((_ROOT / "tools" / "bazel" / "graph.json").read_text())
    except (OSError, ValueError):
        return {}, set()
    inv = inventory(tracked())
    artifact_gens = {
        gen for gens, made in inv.items()
        if any(p.endswith((".step", ".stl", ".glb", ".step.mesh"))
               for p in made["solids"])
        for gen in gens
    }
    return graph, artifact_gens


def artifact_presentation_only(path: str) -> bool:
    """Whether `path` can change presentation but not a published solid.

    Rewritten docs and media are source inputs to their combined generator action only so the
    action can preserve authored text while updating figures. Their bytes do not define its
    geometry. A path stops being presentation-only if another artifact generator reads it as a
    normal input; that keeps real data-bearing documents such as the BOM and fluid topology in
    the CAD slice while letting ordinary README/card edits advance the deployment lock without
    recutting solids.
    """
    if not path.startswith("hardware/"):
        return False
    if not (path.endswith((".md", ".mmd", ".html", ".png", ".svg", ".pdf", ".css",
                           ".figures.json", ".scene.json"))):
        return False
    graph, artifact_gens = _artifact_presentation_context()
    if not graph:
        return False

    writers = {gen for gen, seen in graph.items()
               if path in seen.get("rewritten", ())}
    readers = {gen for gen, seen in graph.items()
               if gen in artifact_gens and path in seen.get("reads", ())}
    return readers <= writers


def artifact_unknown(path: str, artifacts_only: bool = False) -> bool:
    """Whether an unlabelled path could define or feed a new CAD action."""
    if path == "hardware/cad-artifacts.lock.json":
        return False
    # A study is deliberately outside the product graph.  If one of its files is promoted into
    # a generator, that generator's changed, declared importer scopes the build; while it remains
    # unlabelled, rebuilding every solid cannot answer anything about it.  Ignore files likewise
    # change checkout bookkeeping rather than geometry.
    if path.startswith("hardware/quickstart/studies/") or path.endswith("/.gitignore"):
        return False
    if path in declared_outputs():
        return False
    if path.startswith("hardware/"):
        # Presentation outputs cannot alter a STEP/STL/GLB action. They still widen the full
        # derive lane, where cards and docs are outputs in their own right.
        if artifacts_only and artifact_presentation_only(path):
            return False
        return True
    if artifact_global(path):
        return True
    return path.startswith(("tools/bazel/", "tools/cad-artifacts/",
                            "tools/cad-venv-site/", "tools/ci-image/",
                            "tools/docgen/", "tools/render/", "web/"))


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
         and not artifact_unknown("hardware/cad-artifacts.lock.json")
         and not artifact_unknown("hardware/quickstart/studies/new/decode_art.py", True)
         and not artifact_unknown("hardware/quickstart/studies/new/.gitignore", True)
         and artifact_unknown(".dockerignore")
         and artifact_unknown("hardware/new-image.png")
         and not artifact_unknown("hardware/new-image.png", artifacts_only=True))
    hold("rewritten presentation is outside the artifact slice",
         artifact_presentation_only(
             "hardware/printed-parts/enclosure/ceiling-panel/README.md"))
    hold("a data-bearing document stays in the artifact slice",
         not artifact_presentation_only("hardware/ledger/bom.md"))
    hold("only artifact inputs widen the artifact slice",
         unscoped_changes(["BUILD.bazel"], ["BUILD.bazel"], True) == ["BUILD.bazel"]
         and unscoped_changes(["hardware/part.py"], ["hardware/part.py"], True) == []
         and unscoped_changes(["tools/bazel/affected.py"],
                              ["tools/bazel/affected.py"], True) == []
         and unscoped_changes([".github/workflows/publish.yml"], [], True) == []
         and unscoped_changes([".github/workflows/publish.yml",
                               "tools/bazel/affected.py"],
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
        return 0 if holds == 15 else 1

    src = ["hardware/printed-parts/cold-core/foam-cap/foam_cap.py"]
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
         "//:ceiling-panel" in artifact_targets() and "//:everything" not in artifact_targets())
    print(f"affected selftest {holds}/21")
    return 0 if holds == 21 else 1


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
    ap.add_argument("--all-artifacts", action="store_true",
                    help="print every rule that publishes a CAD bundle member")
    args = ap.parse_args(argv)
    if args.cmd == "selftest":
        return selftest()
    if args.all_artifacts:
        write_targets(sorted(artifact_targets()))
        return 0

    say_if_unshimmed()

    moved = changed_between(args.base, args.head) if args.base else changed()
    scoped_metadata = safely_scoped_metadata(moved, args.artifacts, args.base, args.head)
    if args.artifacts:
        moved = [path for path in moved
                 if not artifact_presentation_only(path)
                 and not artifact_sidecar_output(path)]
    if not moved:
        print("nothing has moved — a build of this tree holds nothing to do", file=sys.stderr)
        return 0
    hit, miss = known(moved)
    risky = unscoped_changes(moved, hit, args.artifacts, scoped_metadata)
    if risky:
        print(f"{len(risky)} changed CAD path(s) cannot be safely scoped — this slice widens "
              f"to every artifact rule:", file=sys.stderr)
        for p in risky:
            print(f"    {p}", file=sys.stderr)
    found = targets(hit)
    if risky:
        # Unknown changes cannot be scoped honestly. The artifact lane can still stay narrower
        # than the docs/tests graph; an ordinary affected build takes the aggregate target.
        found = sorted(artifact_targets()) if args.artifacts else ["//:everything"]
    elif args.artifacts:
        found = sorted(set(found) & artifact_targets())
    # A PUBLICATION SENTINEL OWES NO CUT, BECAUSE IT CANNOT MOVE A SOLID. `sync_tree.py` copies
    # bytes a rule already wrote and `pack.py` reads and tars them; neither is an input to a CAD
    # action, which is the same reason `artifact_global` returns False for both. Building their
    # two scorecard producers to "exercise" a change re-cuts the ~95 solids those assemblies
    # reach — and a cut is only reproducible across runs of ONE OCC build, so on a machine whose
    # wheel differs from the one that pinned the lock every one of those members moves. That is
    # the whole bundle re-addressed to the packer's own edit. `sentinel_targets` still states the
    # reach for provenance, where naming what an uncommitted packer touches is exactly right.
    if args.why:
        for t in found:
            reach = [p for p in hit if t in targets([p])]
            print(f"{t}\n    " + "\n    ".join(reach))
    else:
        write_targets(found)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
