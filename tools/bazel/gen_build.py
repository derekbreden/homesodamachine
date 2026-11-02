#!/usr/bin/env python3
"""Write BUILD.bazel from what a run of each generator was watched doing.

    tools/cad-venv/bin/python tools/bazel/gen_build.py

`--project-graph GENERATOR INPUT OUTPUT` writes a reader's stable graph input for
the support action. Assembly and tube actions stage that input at the existing
`tools/bazel/graph.json` path; the full graph is only the support rule's input.

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
import os
import re
import shlex
import sys
from pathlib import Path


def project_graph(graph: dict, generator: str) -> dict:
    """One reader's input set and the writer classifications of those inputs.

    `_facts` asks which assembly reads any generator writes or rewrites; `_machine`
    and the tube exporter ask for the assembly's reads. Writer identities and all
    unrelated fields are absent, so changing another graph row changes no staged byte.
    This is a reader projection, not an inventory of generators.
    """
    if generator not in graph:
        return {}
    reads = set(graph[generator].get("reads", ()))
    written = set().union(*(set(row.get("writes", ())) for row in graph.values()))
    rewritten = set().union(*(set(row.get("rewritten", ())) for row in graph.values()))
    return {
        generator: {"reads": sorted(reads), "writes": [], "rewritten": []},
        "@derived-input-classification": {
            "reads": [], "writes": sorted(reads & written),
            "rewritten": sorted(reads & rewritten),
        },
    }


def write_graph_projection(generator: str, source: str, output: str) -> None:
    """Cheap support transformation, usable without importing the build inventory."""
    text = json.dumps(project_graph(json.loads(Path(source).read_text()), generator),
                      indent=1, sort_keys=True) + "\n"
    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.is_file() or path.read_text() != text:
        path.write_text(text)


# The support action runs from the execroot with only its two declared files.
# Dispatch before imports that locate this checkout's build inventory or runtime.
if __name__ == "__main__" and sys.argv[1:2] == ["--project-graph"]:
    parser = argparse.ArgumentParser(description="Project the graph for one reader")
    parser.add_argument("generator")
    parser.add_argument("source")
    parser.add_argument("output")
    options = parser.parse_args(sys.argv[2:])
    write_graph_projection(options.generator, options.source, options.output)
    raise SystemExit(0)

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_HERE.parent))
sys.path.insert(0, str(_ROOT / 'hardware/scripts'))

from inventory import inventory, tracked, RUNTIME_READS   # noqa: E402
import _run_slots                         # noqa: E402

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

# A clone shares file data while retaining ordinary copy modes and fresh timestamps.
# Existing regular files keep their modes through atomic replacement; other platforms use cp.
_COPY_FILES = (
    'case "$$(uname -s)" in',
    '  Darwin)',
    '    copy_mask=$$((8#$$(umask)))',
    '    copy_bits=("" x w wx r rx rw rwx)',
    '    copy_mode="u-$${copy_bits[$$((copy_mask >> 6 & 7))]},'
    'g-$${copy_bits[$$((copy_mask >> 3 & 7))]},o-$${copy_bits[$$((copy_mask & 7))]}"',
    '    copy_file() {',
    '      local copy_dest="$${!#}" copy_target copy_permissions="$$copy_mode"',
    '      if [ -e "$$copy_dest" ] || [ -L "$$copy_dest" ]; then',
    '        if [ ! -f "$$copy_dest" ] || [ -L "$$copy_dest" ]; then cp "$$@"; return; fi',
    '        copy_permissions=$$(stat -f %Lp "$$copy_dest")',
    '        copy_target=$$(mktemp "$$copy_dest.hsm-copy.XXXXXX")',
    '      else copy_target="$$copy_dest"; fi',
    '      if cp -c "$${@:1:$$(( $$# - 1 ))}" "$$copy_target" 2>/dev/null; then',
    '        chmod "$$copy_permissions" "$$copy_target"',
    '        touch "$$copy_target"',
    '        if [ "$$copy_target" != "$$copy_dest" ]; then mv -f "$$copy_target" "$$copy_dest"; fi',
    '      else rm -f "$$copy_target"; cp "$$@"; fi',
    '    };;',
    '  *) copy_file() { cp "$$@"; };;',
    'esac',
)

#: The two lines that are this checkout's and no other's. `.bazelrc` takes it with `try-import`,
#: which is the one place bazel expands `%workspace%`; `.gitignore` holds it out of the tree.
RC_PATHS = _ROOT / ".bazelrc.paths"

#: See the tag it earns in `render`.
NOT_HERMETIC = ()

#: Where `pysrc.py` lays a Python file down with its comments taken out. A step reads its
#: sources from under here, so a comment edit leaves every input it holds byte for byte the
#: same and Bazel runs none of it.
PYSRC = "pysrc"

# Both consumers use the assembly read row; the facts reader also needs the relevant
# writer classifications. A support output stays outside out/, which sync_tree carries.
GRAPH_SUPPORT = {
    "support/enclosure-assembly-graph.json": (
        "hardware/manifold-layout/enclosure_assembly.py",
        frozenset(("enclosure-assembly", "tube-routes")),
    ),
}

#: What tells a step that starts node: a script of this repo on node's command line, which
#: the trace sees. Node resolves that entrypoint's local imports and packages below Python's
#: audit hook, so the matching runtime group supplies exactly that unseen portion. Unknown
#: entrypoints retain the broad group and fail closed rather than losing an input edge.
_NODE = ("tools/render/", "web/")
_NODE_RUNTIME_CONSUMERS = {}
_NODE_RUNTIME_SUPPORT = {
    ":render-card-runtime": {
        "tools/render/browser.js",
        "tools/render/render-card.js",
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
    return any(s.startswith(_NODE) and s.endswith((".js", ".mjs", ".cjs")) for s in srcs)


#: What tells a step that runs a part the Rust kernel cuts: a Cargo manifest among what it read
#: (`hardware/scripts/_rust_part.py`). Cargo compiles into the checkout's own target directory,
#: which no sandbox may write, so the step runs unsandboxed — and in a work directory of its own,
#: because unsandboxed steps share one execroot.
def _needs_cargo(srcs: list) -> bool:
    return any(s.endswith("Cargo.toml") for s in srcs)


#: A relative import in a JS module — `from "./browser.js"`, `import("./x.js")`, `require`.
_JS_LOCAL = re.compile(r"""(?:from|import|require)\s*\(?\s*["'](\.[^"']*)["']""")


def _js_closure(srcs: set) -> set:
    """Every local module the `.js` in `srcs` import, to a fixpoint.

    Node resolves these below the interpreter the tracer watches. The relative specifiers are
    resolved against each importer's directory, so every imported local file is declared even
    when a trace did not reach the node call."""
    seen, stack = set(), [s for s in srcs if s.endswith((".js", ".mjs", ".cjs"))]
    while stack:
        current = stack.pop()
        try:
            text = (_ROOT / current).read_text()
        except OSError:
            continue
        for spec in _JS_LOCAL.findall(text):
            found = os.path.normpath(os.path.join(os.path.dirname(current), spec))
            if found not in seen and (_ROOT / found).is_file():
                seen.add(found)
                stack.append(found)
    return seen - set(srcs)


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

    Build entrypoints take their parent directory as a prefix. Other stems shared
    by two generators do the same, so each target has its own stable name.
    """
    if gen == "hardware/install-guide/installation_art.py":
        return "cad-art"
    stem = Path(gen).stem.strip("_").replace("_", "-")
    if stem == "build":
        return f"{Path(gen).parent.name}-{stem}"
    if taken is not None and stem in taken:
        return f"{Path(gen).parent.name}-{stem}"
    return stem


def comments_come_out(src: str, rewritten: set, consumer: str = None) -> bool:
    """Whether a step reads `src` with its comments taken out.

    A generator whose own docstring holds figures is handed its file raw: the run rewrites what
    it was given, and `sync_tree` carries that back into the tree. So is anything under a node
    root — its runtime group carries those bytes raw, and a file arriving twice lands the
    second copy on the first, which Bazel leaves read-only.

    The tube-route export fingerprints source bytes for a web server that holds the git
    checkout. That consumer receives those same bytes, including Python comments."""
    return (src.endswith(".py") and src not in rewritten
            and not src.startswith(_NODE) and consumer != "tube-routes")


def read_from(src: str, rewritten: set, producers: dict = None,
              consumer: str = None, support: dict = None) -> str:
    """The label a step reads for `src`.

    A generated artifact comes from its producer's output, not from the copy restored into the
    source tree by the artifact pointer file. That edge makes a clean build topological: an assembly
    cannot read yesterday's STEP while the target that cuts today's STEP runs beside it.
    Rewritten docs stay source inputs; their generated figures are carried back separately and
    some of those documents intentionally read one another.
    """
    if src in (support or {}):
        return ":" + support[src]
    producer = (producers or {}).get(src)
    if producer and producer != consumer:
        return f":out/{producer}/{src}"
    return f"{PYSRC}/{src}" if comments_come_out(src, rewritten, consumer) else src


def generator_argv(gens: tuple) -> list:
    """Each normal-build entrypoint, in order, in its own Python interpreter."""
    return [[generator] for generator in gens]


def render(gens: tuple, arts: list, srcs: list, optional: list, docs: list, rewritten: set,
           name: str, declaration: dict, support: dict = None) -> str:
    # THE OUTPUT KEEPS THE PATH THE TREE KEEPS IT UNDER, so `sync_tree` strips one prefix and
    # has the file to carry it back to. Twenty generators cut a `README.md`, and a basename is
    # not a name for any of them.
    outs = declaration["outs"]
    cargo = _needs_cargo(srcs)
    work = f"work-{name}" if cargo else "work"
    lines = [f'genrule(', f'    name = "{name}",', "    srcs = ["]
    lines += [f'        "{source}",' for source in declaration["srcs"]]
    # NODE RESOLVES ITS OWN IMPORTS, below Python and out of the tracer's sight. The trace sees
    # the entrypoint on the command line; its runtime group carries the packages and served
    # resources that entrypoint reaches. An unknown entrypoint gets the broad fallback.
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
        lines.append('    tags = ["local", "requires-network"],')
    elif cargo:
        lines.append('    tags = ["no-sandbox"],')
    elif _needs_node(srcs):
        lines.append('    tags = ["requires-network"],')
    lines += ['    cmd = """', "set -e", *_COPY_FILES]
    for i, o in enumerate(outs):
        lines.append(f"O{i}=$$PWD/$(location {o})")
    if cargo:
        lines.append(f"rm -rf {work}")
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
        *(f"    */bin/{output}) t={shlex.quote(source)};;"
          for source, output in sorted((support or {}).items())),
        # A producer output arrives as bazel-out/<cfg>/bin/out/<producer>/<repo path>.
        # Strip both generated prefixes so the consumer sees the same path a direct run sees.
        "    */bin/out/*/*) t=$${f#*/bin/out/}; t=$${t#*/};;",
        f"    */{PYSRC}/*) t=$${{f##*/{PYSRC}/}};;",
        "    *) t=$$f;;",
        "  esac",
        f'  mkdir -p "{work}/$$(dirname "$$t")"; copy_file -L "$$f" "{work}/$$t"',
        "done",
        "for d in tools/render/node_modules web/node_modules "
        "hardware/pcb/pcba/node_modules; do",
        f"  if [ -d $$d ]; then mkdir -p {work}/$$(dirname $$d); "
        f"ln -sfn $$PWD/$$d {work}/$$d; fi",
        "done",
        f"cd {work}",
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
    for argv in generator_argv(gens):
        # The normal build skips payloads because they are not outputs. An action that declares
        # one must make it; `env -u` overrides the global action environment for that action.
        payload_env = "env -u HSM_SKIP_MESH_PAYLOAD " if any(
            a.endswith(".step.mesh") for a in arts) else ""
        lines.append(f"HSM_REPO_ROOT=$$PWD HSM_INPUT_DIGEST=$$D {payload_env}"
                     f"{VENV} tools/run.py -- {VENV} {shlex.join(argv)} > /dev/null")
    for i, made in enumerate((*arts, *docs)):
        lines.append(f'copy_file {shlex.quote(made)} "$$O{i}"')
    if cargo:
        lines.append(f"cd .. && rm -rf {work}")
    lines += ['""",', ")"]
    return "\n".join(lines)


def action_plan(only: str = None) -> tuple:
    """Declared generator actions and their inventory, shared by BUILD and the part engine."""
    _check_node_runtime_map()
    files = tracked()
    all_inv = inventory(files)
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

    held =set(files) | {
        path for made in all_inv.values() for kind in ("solids", "docs")
        for path in made[kind]
    } | {gen for gens in all_inv for gen in gens}
    if any(f"/{PYSRC}/" in f for f in held):
        raise SystemExit(f"  a tracked path holds /{PYSRC}/, which is where a stripped source"
                         f" lands — the staging loop cannot tell the two apart")

    actions, wants = {}, {}
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
        # AND WHAT A NODE ENTRYPOINT IMPORTS COMES WITH IT. Node resolves its own specifiers,
        # so whether the graph holds them is a reading of how far the traced run got rather
        # than of what the action needs.
        srcs |= _js_closure(srcs)
        # Admission is runtime behavior every heavy action explicitly shares.
        srcs |= RUNTIME_READS
        srcs = sorted(s for s in srcs if s in held)
        optional = sorted(d for d in made["docs"] if d.endswith((".png", ".json")))
        rewritten = {d for d in made["docs"] if d.endswith(".py")}
        wants[names[gens]] = {producers[s] for s in srcs
                              if producers.get(s) and producers[s] != names[gens]}
        actions[names[gens]] = {
            "generators": list(gens), "entrypoints": generator_argv(gens),
            "solids": made["solids"], "docs": made["docs"],
            "reads": srcs, "optional": optional, "rewritten_python": sorted(rewritten),
            "stripped": [s for s in srcs if comments_come_out(s, rewritten, names[gens])],
            "producers": {s: producers[s] for s in srcs if s in producers},
            "dependencies": sorted(wants[names[gens]]),
            "node_runtimes": list(_node_runtimes(gens, srcs)),
            "support_inputs": {"tools/bazel/graph.json": output
                for output, (_reader, consumers) in GRAPH_SUPPORT.items()
                if names[gens] in consumers and "tools/bazel/graph.json" in srcs},
        }

    _no_cycles(wants)
    return actions, inv


def dependency_rules(actions: dict) -> dict:
    """The declared inputs and outputs of actions and their build support rules.

    BUILD rendering and affected discovery use these same labels. Producer outputs,
    stripped Python, optional files and runtime globs retain their declared edges.
    """
    rules, comments_out, used_support = {}, set(), set()
    for name, action in actions.items():
        rewritten = set(action["rewritten_python"])
        rules[name] = {
            "kind": "action",
            "srcs": [read_from(source, rewritten, action["producers"], name,
                               action["support_inputs"]) for source in action["reads"]]
                    + action["node_runtimes"],
            "outs": [f"out/{name}/{path}" for path in (*action["solids"], *action["docs"])],
            "globs": [(action["optional"], [])] if action["optional"] else [],
        }
        comments_out.update(action["stripped"])
        used_support.update(action["support_inputs"].values())

    for output in sorted(used_support):
        generator, _consumers = GRAPH_SUPPORT[output]
        rules[f"support-{Path(output).stem}"] = {
            "kind": "graph", "generator": generator,
            "srcs": ["tools/bazel/graph.json"], "outs": [output],
            "tools": ["tools/bazel/gen_build.py"],
        }

    # ONE STRIPPED SOURCE PER ACTION. A single multi-output action made every Python edit an
    # input to every consumer of any stripped source, so `rdeps(display_cover.py)` became almost
    # the whole graph. Each tiny action keeps the exact edge and lets an affected build stay a
    # slice. The output path remains stable; only the rule that produces it is split.
    for source in sorted(comments_out):
        digest = hashlib.sha256(source.encode()).hexdigest()[:12]
        rules[f"{PYSRC}-{digest}"] = {
            "kind": "pysrc", "srcs": [source], "outs": [f"{PYSRC}/{source}"],
            "tools": ["tools/bazel/pysrc.py"],
        }

    # Runtime groups include changed paths directly, including a newly added member.
    rules["render-card-runtime"] = {
        "kind": "runtime", "globs": [(["tools/render/node_modules/**"], [])],
    }
    rules["node-packages"] = {
        "kind": "runtime", "globs": [(["tools/render/**", "web/**"], [])],
    }
    rules["everything"] = {"kind": "aggregate", "srcs": [":" + name for name in actions]}
    return rules


def render_build(only: str = None) -> tuple:
    """The whole of BUILD.bazel as text, and the steps it was rendered from."""
    actions, inv = action_plan(only)
    rules = dependency_rules(actions)
    blocks = []
    for name, action in actions.items():
        blocks.append(render(tuple(action["generators"]), action["solids"], action["reads"],
                             action["optional"], action["docs"], set(action["rewritten_python"]),
                             name, rules[name], action["support_inputs"]))
    for name, rule in rules.items():
        if rule["kind"] == "graph":
            source, = rule["srcs"]
            output, = rule["outs"]
            tool, = rule["tools"]
            blocks.append(
                f'genrule(\n    name = "{name}",\n'
                f'    srcs = ["{source}"],\n'
                f'    outs = ["{output}"],\n'
                f'    tools = ["{tool}"],\n'
                f'    cmd = "{VENV} $(location {tool}) --project-graph '
                f'{rule["generator"]} $(location {source}) $@",\n)')
        elif rule["kind"] == "pysrc":
            source, = rule["srcs"]
            output, = rule["outs"]
            tool, = rule["tools"]
            blocks.append(
                f'genrule(\n    name = "{name}",\n'
                + f'    srcs = ["{source}"],\n'
                + f'    outs = ["{output}"],\n'
                + f'    tools = ["{tool}"],\n'
                + f'    cmd = "{VENV} $(location {tool})'
                + f' $(RULEDIR)/{PYSRC} $(SRCS)",\n)')

    head = (
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
        f'        {json.dumps(rules["render-card-runtime"]["globs"][0][0])},\n'
        '        allow_empty = True,\n    ),\n)')

    # A renderer not yet classified above keeps the old whole-runtime boundary. A new tool can
    # be slow, but never silently underdeclared; once measured, give it its own group.
    blocks.append(
        'filegroup(\n    name = "node-packages",\n    srcs = glob(\n'
        '        [\n'
        + "".join(f'            "{pattern}",\n'
                  for pattern in rules["node-packages"]["globs"][0][0])
        + '        ],\n'
        '        allow_empty = True,\n    ),\n)')

    # ONE NAME FOR THE WHOLE TREE, so what a commit owes is `bazel build //:everything` and
    # what it carries is `sync_tree --write`.
    blocks.append("filegroup(\n    name = \"everything\",\n    srcs = [\n"
                  + "".join('        "%s",\n' % source for source in rules["everything"]["srcs"])
                  + "    ],\n)")
    return head + "\n" + "\n\n".join(blocks) + "\n", inv


def render_rc_paths() -> str:
    """The flags that name this checkout, for `.bazelrc` to take with `try-import`."""
    return ("# Written by tools/bazel/gen_build.py — this checkout's own paths, and no other\n"
            "# checkout's. `.gitignore` holds it out of the tree.\n"
            f"build --action_env=HSM_WORKSPACE={_ROOT}\n"
            f"build --sandbox_add_mount_pair={_ROOT}/.cache\n"
            f"build --action_env=HSM_RUN_BROKER={shlex.quote(_run_slots.broker_config(_ROOT))}\n"
            f"build --sandbox_add_mount_pair={_run_slots.directory()}\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="print one target, by generator path")
    ap.add_argument("--check", action="store_true",
                    help="say whether BUILD.bazel is what this would write")
    ap.add_argument("--cycles", action="store_true",
                    help="say only whether the graph's rules wait on each other")
    args = ap.parse_args()

    # THE ONE FAULT THAT COSTS EVERY TARGET, ASKED WITHOUT ASKING ANYTHING ELSE. `--check` also
    # holds BUILD.bazel to the graph, which several sessions share and one of them is always
    # part-way through moving — so a gate that runs `--check` stops a commit over a file its
    # author never touched. This renders and throws the text away: the cycle walk in
    # `_no_cycles` is the whole of the answer.
    if args.cycles:
        render_build()
        print("gen_build: no rule waits on another")
        return 0

    if args.check:
        text, inv = render_build()
        red = False

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
