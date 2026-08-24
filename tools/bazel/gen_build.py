#!/usr/bin/env python3
"""Write BUILD.bazel from what a run of each generator was watched doing.

    tools/cad-venv/bin/python tools/bazel/gen_build.py

`inventory.py` reads `graph.json` and says, per build step, the solids it cuts, the docs it
rewrites and the files it reads. One `genrule` per step carries all three. A step is usually
one generator and sometimes several — see `inventory._together`.

An action that names too little does not read a stale file: it fails to find one at all. So a
target here can be wrong in exactly one direction, and the build says which.
"""

import argparse
import difflib
import hashlib
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_HERE.parent))

from inventory import inventory, tracked   # noqa: E402
from trace_inputs import _selftests        # noqa: E402

#: WHERE THIS CHECKOUT IS, NAMED ONCE, BY THE CHECKOUT. An action runs in the execroot and the
#: interpreter is not in the workspace, so the only way to it is an absolute path — and an
#: absolute path written into a tracked file is one machine's. `RC_PATHS` below carries it, out
#: of the tree, and every cmd reads it from the environment. `$$` is the genrule escape: what
#: the shell in the action sees is `$HSM_WORKSPACE`.
_WS = "$$HSM_WORKSPACE"
VENV = f"{_WS}/tools/cad-venv/bin/python"
#: The kept work — shapes off BREP, tessellations, optimal boxes — held where every action
#: reaches it. `.bazelignore` holds it out of the workspace and `.bazelrc` mounts it in.
CACHE = f"{_WS}/.cache"

#: The two lines that are this checkout's and no other's. `.bazelrc` takes it with `try-import`,
#: which is the one place bazel expands `%workspace%`; `.gitignore` holds it out of the tree.
RC_PATHS = _ROOT / ".bazelrc.paths"

#: See the tag it earns in `render`.
NOT_HERMETIC = ("hardware/assembly/scenes/render_scenes.py",
                "hardware/assembly/scenes/render_scene_cards.py")

#: Where `pysrc.py` lays a Python file down with its comments taken out. A step reads its
#: sources from under here, so a comment edit leaves every input it holds byte for byte the
#: same and Bazel runs none of it.
PYSRC = "pysrc"

#: What each module's `selftest` was watched reading — `trace_inputs.py --selftests` writes it.
SELFTESTS = _HERE.parent / "selftests.json"

#: What tells a step that starts node: a script of this repo on node's command line, which
#: the trace sees. Node resolves that entrypoint's local imports and packages below Python's
#: audit hook, so the matching runtime group supplies exactly that unseen portion. Unknown
#: entrypoints retain the broad group and fail closed rather than losing an input edge.
_NODE = ("tools/render/", "web/")
_NODE_RUNTIME_CONSUMERS = {
    "hardware/assembly/cards/_build.py": ":render-card-runtime",
    "hardware/assembly/cards/tools/_build.py": ":render-card-runtime",
    "hardware/quickstart/_build.py": ":render-card-runtime",
    "hardware/quickstart/quickstart_art.py": ":render-step-posed-runtime",
}
_NODE_RUNTIME_SUPPORT = {
    ":render-card-runtime": {
        "tools/render/browser.js",
        "tools/render/render-card.js",
    },
    ":render-step-posed-runtime": {
        "tools/render/browser.js",
        "tools/render/render-step-posed.js",
        "web/server.js",
    },
}

# A read a generator records that no Bazel action can act on. Nothing is skipped today: making
# a tool an action cannot run a source of every solid rule ties an ordinary edit of it to nearly
# the entire CAD graph, so anything of that shape belongs here rather than in a rule's srcs.
BAZEL_SKIPPED_READS = set()


def _no_cycles(wants: dict) -> None:
    """Refuse to write a BUILD.bazel whose rules wait on each other.

    A step's srcs name another step's outputs, and bazel will not analyze a graph where that
    relation comes back around: the whole build stops at the loading phase, so every target
    fails and none of the messages is about the pair at fault. The relation is in hand here,
    a rule and the rules it reads, and the loop is a walk over it.

    THIS IS A TRACE THAT CAME BACK WRONG, EVERY TIME. Nobody writes an edge by hand — a run is
    watched, and a generator that opened a sibling's output while doing something else is
    recorded as needing it. So the report names the pair and leaves the reading to a person:
    the cure is either a filter above, where the read is incidental, or a producer split, where
    it is real."""
    seen, stack = set(), []

    def walk(rule):
        if rule in stack:
            loop = stack[stack.index(rule):] + [rule]
            raise SystemExit("gen_build: these rules wait on each other and bazel will not\n"
                             "  load the graph at all — one of these reads is incidental:\n    "
                             + "\n    ".join(f"{a} reads {b}" for a, b in zip(loop, loop[1:])))
        if rule in seen:
            return
        stack.append(rule)
        for nxt in sorted(wants.get(rule, ())):
            walk(nxt)
        stack.pop()
        seen.add(rule)

    for rule in sorted(wants):
        walk(rule)


def _needs_node(srcs: list) -> bool:
    return any(s.startswith(_NODE) for s in srcs)


def _node_runtimes(gens: tuple, srcs: list) -> tuple[str, ...]:
    labels = {_NODE_RUNTIME_CONSUMERS[gen] for gen in gens
              if gen in _NODE_RUNTIME_CONSUMERS}
    covered = set().union(*(_NODE_RUNTIME_SUPPORT[label] for label in labels)) \
        if labels else set()
    node_js = {path for path in srcs
               if path.startswith(_NODE) and path.endswith((".js", ".mjs", ".cjs"))}
    if (not labels and _needs_node(srcs)) or node_js - covered:
        labels.add(":node-packages")
    return tuple(sorted(labels))


def _check_node_runtime_map() -> None:
    cases = (
        (("hardware/quickstart/_build.py",),
         ["tools/render/browser.js", "tools/render/render-card.js"],
         (":render-card-runtime",)),
        (("hardware/quickstart/_build.py",),
         ["tools/render/browser.js", "tools/render/render-card.js",
          "tools/render/future-entrypoint.cjs"],
         (":node-packages", ":render-card-runtime")),
        (("hardware/unknown.py",), ["tools/render/future-entrypoint.js"],
         (":node-packages",)),
    )
    for gens, srcs, expected in cases:
        got = _node_runtimes(gens, srcs)
        if got != expected:
            raise SystemExit(
                f"node runtime classification for {gens} is {got}, expected {expected}"
            )


def target_name(gen: str, taken=None) -> str:
    """A Bazel name for a generator. `_wiring_sync.py` is a doc sync like any other, and its
    leading underscore is a Python convention, not part of what it is called here.

    A STEM IS NOT A NAME WHEN TWO FILES SHARE IT. `assembly/cards/_build.py` draws the unit
    cards and `assembly/cards/tools/_build.py` the tool deck, and one target cannot be both —
    so where a stem is taken, the directory the file sits in goes in front of it.
    """
    stem = Path(gen).stem.strip("_").replace("_", "-")
    if taken is not None and stem in taken:
        return f"{Path(gen).parent.name}-{stem}"
    return stem


def comments_come_out(src: str, rewritten: set) -> bool:
    """Whether a step reads `src` with its comments taken out.

    A generator whose own docstring holds figures is handed its file raw: the run rewrites what
    it was given, and `sync_tree` carries that back into the tree. So is anything under a node
    root — its runtime group carries those bytes raw, and a file arriving twice lands the
    second copy on the first, which Bazel leaves read-only."""
    return (src.endswith(".py") and src not in rewritten
            and not src.startswith(_NODE))


def read_from(src: str, rewritten: set, producers: dict = None,
              consumer: str = None) -> str:
    """The label a step reads for `src`.

    A generated artifact comes from its producer's output, not from the copy restored into the
    source tree by the artifact lock. That edge makes a clean build topological: an assembly
    cannot read yesterday's STEP while the target that cuts today's STEP runs beside it.
    Rewritten docs stay source inputs; their generated figures are carried back separately and
    some of those documents intentionally read one another.
    """
    producer = (producers or {}).get(src)
    if producer and producer != consumer:
        return f":out/{producer}/{src}"
    return f"{PYSRC}/{src}" if comments_come_out(src, rewritten) else src


def render(gens: tuple, arts: list, srcs: list, optional: list, docs: list, rewritten: set,
           name: str, producers: dict) -> str:
    # THE OUTPUT KEEPS THE PATH THE TREE KEEPS IT UNDER, so `sync_tree` strips one prefix and
    # has the file to carry it back to. Twenty generators cut a `README.md`, and a basename is
    # not a name for any of them.
    outs = [f"out/{name}/{a}" for a in (*arts, *docs)]
    lines = [f'genrule(', f'    name = "{name}",', "    srcs = ["]
    lines += [f'        "{read_from(s, rewritten, producers, name)}",' for s in srcs]
    # NODE RESOLVES ITS OWN IMPORTS, below Python and out of the tracer's sight. The trace sees
    # the entrypoint on the command line; its runtime group carries the packages and served
    # resources that entrypoint reaches. An unknown entrypoint gets the broad fallback.
    lines += [f'        "{runtime}",' for runtime in _node_runtimes(gens, srcs)]
    if optional:
        lines += ["    ] + glob(", "        ["]
        lines += [f'            "{s}",' for s in optional]
        lines += ["        ],", "        allow_empty = True,", "    ),"]
    else:
        lines += ["    ],"]
    lines += ["    outs = ["]
    lines += [f'        "{o}",' for o in outs]
    lines += ["    ],"]
    # A THUMBNAIL IS A PHOTOGRAPH OF A PAGE. The renderer stands a server on loopback and
    # points a headless browser at it, so an action that draws one needs a socket; the rest
    # of the tree is built with the network off.
    if any(g in NOT_HERMETIC for g in gens):
        # A SCENE IS A PHOTOGRAPH OF A LIVE PAGE. `render-step-posed` stands the viewer on
        # loopback and points a headless browser at it, and that page loads occt-import-js
        # off a CDN — so drawing one reaches the network for a library this tree does not
        # carry. Vendoring it is what would make this action hermetic; until then it runs
        # outside the sandbox and is the one target here whose inputs are not all declared.
        lines.append('    tags = ["local", "requires-network"],')
    elif _needs_node(srcs):
        lines.append('    tags = ["requires-network"],')
    lines += ['    cmd = """', "set -e"]
    for i, o in enumerate(outs):
        lines.append(f"O{i}=$$PWD/$(location {o})")
    lines += [
        # THE COPY IS FOR THE FILES `Path(__file__).resolve()` WALKS OUT OF, which is this
        # repo's own Python. A package tree is read by node, which is content with a symlink,
        # and copying eleven thousand files into every action took the critical path from
        # 89 s to 281 s.
        # A SOURCE LANDS ON THE PATH THE TREE KEEPS IT UNDER, comments taken out or not, so
        # `import` finds it and a traceback names it.
        "for f in $(SRCS); do",
        "  case $$f in",
        "    */node_modules/*) continue;;",
        # A producer output arrives as bazel-out/<cfg>/bin/out/<producer>/<repo path>.
        # Strip both generated prefixes so the consumer sees the same path a direct run sees.
        "    */bin/out/*/*) t=$${f#*/bin/out/}; t=$${t#*/};;",
        f"    */{PYSRC}/*) t=$${{f##*/{PYSRC}/}};;",
        "    *) t=$$f;;",
        "  esac",
        "  mkdir -p work/$$(dirname $$t); cp -L $$f work/$$t",
        "done",
        "for d in tools/render/node_modules web/node_modules "
        "hardware/pcb/pcba/node_modules; do",
        "  if [ -d $$d ]; then mkdir -p work/$$(dirname $$d); "
        "ln -sfn $$PWD/$$d work/$$d; fi",
        "done",
        "cd work",
        # TWO THINGS DECIDE A SHAPE and the key must hold both. `_realized.key` walks the
        # drawing module's imports, which covers the Python; this is the other half — the
        # solids the action was given, which no import statement reaches. A doc moving is
        # neither of them, so it leaves the kept work standing.
        #
        # `_boxes` and `_meshes` need no such name: each keys an entry by the serialized
        # shape it was taken from, which is already only what it was given.
        f"ln -sfn {CACHE} .cache",
        "D=$$(find . -type f -name '*.step' -o -type f -name '*.dxf'"
        " -o -type f -name '*.stl' | sort | xargs cat 2>/dev/null"
        " | shasum -a 256 | cut -c1-32)",
    ]
    # THE ROOT IS THIS DIRECTORY. `docgen` finds it by walking for `.git`, which an action
    # holding only what it declared does not have — without this the doc's figures are
    # rewritten and its `.figures.json` is not.
    for g in gens:
        # The normal build skips payloads because they are not outputs. An action that declares
        # one must make it; `env -u` overrides the global action environment for that action.
        payload_env = "env -u HSM_SKIP_MESH_PAYLOAD " if any(
            a.endswith(".step.mesh") for a in arts) else ""
        lines.append(f"HSM_REPO_ROOT=$$PWD HSM_INPUT_DIGEST=$$D {payload_env}{VENV} {g} > /dev/null")
    for i, made in enumerate((*arts, *docs)):
        lines.append(f"cp {made} $$O{i}")
    lines += ['""",', ")"]
    return "\n".join(lines)


def render_build(only: str = None) -> tuple:
    """The whole of BUILD.bazel as text, and the steps it was rendered from."""
    _check_node_runtime_map()
    files = tracked()
    all_inv = inventory(files)
    try:
        selftests = json.loads(SELFTESTS.read_text())
    except (OSError, ValueError):
        selftests = {}
    # WHICH STEMS ARE SHARED, before a name is handed to anything.
    seen, shared = set(), set()
    for gens in all_inv:
        for g in gens:
            stem = Path(g).stem.strip("_").replace("_", "-")
            (shared if stem in seen else seen).add(stem)

    names = {gens: target_name(gens[0], shared) for gens in all_inv}
    # Whole generated artifacts become producer edges. Rewritten authored files remain inputs
    # to their own writer and are spliced back into the current tree by sync_tree; PNGs and
    # JSON are composed whole, so a consumer must wait for this build's writer instead of
    # racing it while reading the restored/committed prior copy.
    producers = {artifact: names[gens]
                 for gens, made in all_inv.items()
                 for artifact in (*made["solids"],
                                  *(d for d in made["docs"]
                                    if d.endswith((".png", ".json"))))}

    inv = ({k: v for k, v in all_inv.items() if only in k} if only else all_inv)

    # What each generator reads, by its own path, for widening a selftest's data below.
    inv_by_gen = {g: set(made["reads"]) for gens, made in all_inv.items() for g in gens}

    held = set(files) | {
        path for made in all_inv.values() for kind in ("solids", "docs")
        for path in made[kind]
    } | {gen for gens in all_inv for gen in gens}
    if any(f"/{PYSRC}/" in f for f in held):
        raise SystemExit(f"  a tracked path holds /{PYSRC}/, which is where a stripped source"
                         f" lands — the staging loop cannot tell the two apart")

    blocks, comments_out, wants = [], set(), {}
    for gens, made in sorted(inv.items()):
        # A doc is read to be rewritten, so it is on both sides — named as a src under its own
        # path and handed back under the target's own, which `sync_tree` carries into the tree.
        # A solid the run cuts is only ever handed back. Atomic writers often open an old copy
        # solely to avoid replacing equal bytes; that optional comparison must not make a new
        # output into a required source. Whole rewritten PNG/JSON outputs are the same case.
        #
        # A PAYLOAD BESIDE A SOLID THIS STEP CUTS IS THAT SAME COMPARISON. `_write_payload_beside`
        # stats `<solid>.step.mesh` to decide whether the bytes it holds were made from the STEP
        # about to be written, so every exporter reads the payload of everything it exports —
        # including payloads a sibling step writes. Read as an edge, that points a producer at
        # its own consumer. The payload is derived from the STEP and from nothing else, so a
        # step that cuts the STEP owes the payload no dependency; one that does not cut it is
        # reading somebody's output and keeps the edge.
        probes = {r for r in made["reads"]
                  if r.endswith(".step.mesh") and r[:-len(".mesh")] in set(made["solids"])}
        srcs = ((set(made["reads"]) | set(made["docs"]) | set(gens))
                - set(made["solids"])
                - probes
                - {d for d in made["docs"] if d.endswith((".png", ".json"))}
                - BAZEL_SKIPPED_READS)
        srcs = sorted(s for s in srcs if s in held)
        optional = sorted(d for d in made["docs"] if d.endswith((".png", ".json")))
        rewritten = {d for d in made["docs"] if d.endswith(".py")}
        comments_out |= {s for s in srcs if comments_come_out(s, rewritten)}
        wants[names[gens]] = {producers[s] for s in srcs
                              if producers.get(s) and producers[s] != names[gens]}
        blocks.append(render(gens, made["solids"], srcs, optional, made["docs"], rewritten,
                             names[gens], producers))

    _no_cycles(wants)

    # ONE STRIPPED SOURCE PER ACTION. A single multi-output action made every Python edit an
    # input to every consumer of any stripped source, so `rdeps(ceiling_panel.py)` became almost
    # the whole graph. Each tiny action keeps the exact edge and lets an affected build stay a
    # slice. The output path remains stable; only the rule that produces it is split.
    comments_out = sorted(comments_out)
    for source in comments_out:
        digest = hashlib.sha256(source.encode()).hexdigest()[:12]
        blocks.append(
            f'genrule(\n    name = "{PYSRC}-{digest}",\n'
            + f'    srcs = ["{source}"],\n'
            + f'    outs = ["{PYSRC}/{source}"],\n'
            + '    tools = ["tools/bazel/pysrc.py"],\n'
            + f'    cmd = "{VENV} $(location tools/bazel/pysrc.py)'
            + f' $(RULEDIR)/{PYSRC} $(SRCS)",\n)')

    # A MODULE THAT CARRIES A `selftest` IS ONE NOBODY RUNS. Twenty-five of them state their own
    # holds and every one is verified only when a person types the word — `sync_tree`'s ten
    # include the hold that a card's authored text survives a build handed stale figures, whose
    # failure is silent destruction. A test target is what runs it, and running one costs
    # nothing the second time: `bazel test` skips a test whose data has not moved.
    #
    # `large` is a fifteen-minute ceiling. The slowest of these stands the machine and comes
    # back in four minutes; `enormous` gave every one of them an hour, which is not headroom
    # but the time a hung test would burn before anyone was told.
    #
    # WHAT A TEST READS IS NOT WHAT ITS MODULE BUILDS. `graph.json` answers the second and has
    # no entry at all for `sync_tree.py`, because the machinery that writes the graph is not a
    # step in the graph it writes. So a selftest is watched the same way a generator is —
    # `trace_inputs.py --selftests`, which runs the module on the word and keeps what it opened.
    for gen, data in sorted(selftests.items()):
        if gen not in held:
            continue
        # WHAT A TEST REACHES IS NOT WHAT ONE RUN OF IT TOOK. A watch records the path that
        # run went down, and `lanes.py` reaches `manifold_layout`, which imports `_lines`
        # inside a function the traced run never called — so an edit to the routing constants
        # this test exists to check would not rerun it. A build action that names too little
        # fails to find a file; a test that names too little caches a pass.
        #
        # So a module in the data brings what it reads, to a fixpoint. The build graph already
        # holds that for every generator, and the ones this reaches are generators.
        want = set(data)
        while True:
            more = {r for m in want if m in inv_by_gen for r in inv_by_gen[m]} - want
            if not more:
                break
            want |= more
        blocks.append(
            f'sh_test(\n    name = "{target_name(gen)}-selftest",\n'
            + '    srcs = ["tools/bazel/selftest.sh"],\n    data = [\n'
            + "".join(f'        "{s}",\n' for s in sorted(want & held))
            + f'    ],\n    args = ["{gen}"],\n'
            + '    size = "large",\n    tags = ["local"],\n)')

    head = (
        'load("@rules_shell//shell:sh_test.bzl", "sh_test")\n\n'
        "# The appliance's geometry, docs and pictures — one action per generator. Written by\n"
        "# tools/bazel/gen_build.py off tools/bazel/inventory.py; the sandbox corrects it.\n"
        "#\n"
        "# WHAT AN ACTION HOLDS IS WHAT IT NAMED. A generator reads the Python its imports\n"
        "# reach, the solids it loads and the docs it rewrites; all three are `srcs`, and\n"
        "# nothing else is in the directory the run happens in. A solid one generator cuts and\n"
        "# the next loads is an edge like any other: unnamed, the reader does not find the file.\n"
    )
    # `render-card` reads local HTML and never starts the product viewer. Give it Puppeteer's
    # packages without tying every sheet to every viewer/server source. The tracked entrypoint,
    # browser helper and package manifests remain ordinary action inputs above.
    blocks.append(
        'filegroup(\n    name = "render-card-runtime",\n    srcs = glob(\n'
        '        ["tools/render/node_modules/**"],\n'
        '        allow_empty = True,\n    ),\n)')

    # `render-step-posed` does stand the viewer and photograph it. Its server can reach the
    # whole web tree, so retain that safe boundary while excluding the three tracked files each
    # consumer names directly. This separates card-renderer edits without lying about shared
    # browser or viewer inputs.
    blocks.append(
        'filegroup(\n    name = "render-step-posed-runtime",\n    srcs = glob(\n'
        '        [\n'
        '            "tools/render/node_modules/**",\n'
        '            "web/**",\n'
        '        ],\n'
        '        exclude = [\n'
        '            "web/package-lock.json",\n'
        '            "web/package.json",\n'
        '            "web/server.js",\n'
        '        ],\n'
        '        allow_empty = True,\n    ),\n)')

    # A renderer not yet classified above keeps the old whole-runtime boundary. A new tool can
    # be slow, but never silently underdeclared; once measured, give it its own group.
    blocks.append(
        'filegroup(\n    name = "node-packages",\n    srcs = glob(\n'
        '        [\n'
        '            "tools/render/**",\n'
        '            "web/**",\n'
        '        ],\n'
        '        allow_empty = True,\n    ),\n)')

    # ONE NAME FOR THE WHOLE TREE, so what a commit owes is `bazel build //:everything` and
    # what it carries is `sync_tree --write`.
    blocks.append("filegroup(\n    name = \"everything\",\n    srcs = [\n"
                  + "".join('        ":%s",\n' % target_name(g[0], shared) for g in sorted(inv))
                  + "    ],\n)")
    return head + "\n" + "\n\n".join(blocks) + "\n", inv


def render_rc_paths() -> str:
    """The flags that name this checkout, for `.bazelrc` to take with `try-import`."""
    return ("# Written by tools/bazel/gen_build.py — this checkout's own paths, and no other\n"
            "# checkout's. `.gitignore` holds it out of the tree.\n"
            f"build --action_env=HSM_WORKSPACE={_ROOT}\n"
            f"build --sandbox_add_mount_pair={_ROOT}/.cache\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="print one target, by generator path")
    ap.add_argument("--check", action="store_true",
                    help="say whether BUILD.bazel is what this would write")
    args = ap.parse_args()

    if args.check:
        text, inv = render_build()
        red = False

        # A TARGET IS RENDERED FROM THE REGISTRY, so a module that answers to `selftest` and is
        # not a key writes no target and states its holds to nobody. `_selftests` is the reading
        # `trace_inputs` writes the registry by; the tree is asked with it here.
        registry = json.loads(SELFTESTS.read_text()) if SELFTESTS.is_file() else {}
        holds = set(_selftests(tracked()))
        for f in sorted(holds - set(registry)):
            print(f"  {f} answers to selftest and selftests.json does not name it"
                  f"\n    tools/cad-venv/bin/python tools/bazel/trace_inputs.py --selftests {f}")
            red = True
        for f in sorted(set(registry) - holds):
            print(f"  selftests.json names {f}, which answers to no selftest")
            red = True

        # NO ACTION FINDS THE INTERPRETER WITHOUT THIS. Every cmd reads `$HSM_WORKSPACE`, and
        # `.bazelrc` takes the file that sets it from this directory, so a checkout that has
        # not written one builds nothing.
        want_rc = render_rc_paths()
        if not RC_PATHS.is_file() or RC_PATHS.read_text() != want_rc:
            print(f"  {RC_PATHS.name} does not name this checkout"
                  f"\n    tools/cad-venv/bin/python tools/bazel/gen_build.py")
            red = True

        have = (_ROOT / "BUILD.bazel").read_text()
        if text != have:
            print("\n".join(difflib.unified_diff(
                have.splitlines(), text.splitlines(),
                "BUILD.bazel", "what gen_build.py writes now", lineterm="")))
            print("\n  BUILD.bazel is not what gen_build.py writes."
                  "\n    tools/cad-venv/bin/python tools/bazel/trace_inputs.py <gen.py>  # re-read one"
                  "\n    tools/cad-venv/bin/python tools/bazel/gen_build.py              # write this")
            return 1
        if red:
            return 1
        print(f"  BUILD.bazel is what {len(inv)} step(s) write")
        return 0

    if args.only:
        print(render_build(args.only)[0])
        return 0

    text, inv = render_build()
    (_ROOT / "BUILD.bazel").write_text(text)
    RC_PATHS.write_text(render_rc_paths())
    print(f"  {len(inv)} step(s) over {sum(len(k) for k in inv)} generators → BUILD.bazel")
    print(f"  this checkout's paths → {RC_PATHS.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
