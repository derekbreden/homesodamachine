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
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_HERE.parent))

from inventory import inventory, tracked   # noqa: E402

VENV = "/Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python"
#: The kept work — shapes off BREP, tessellations, optimal boxes — held where every action
#: reaches it. `.bazelignore` holds it out of the workspace and `.bazelrc` mounts it in.
CACHE = "/Users/derekbredensteiner/Developer/homesodamachine/.cache"

#: See the tag it earns in `render`.
NOT_HERMETIC = ("hardware/assembly/scenes/render_scenes.py",)

#: Where `pysrc.py` lays a Python file down with its comments taken out. A step reads its
#: sources from under here, so a comment edit leaves every input it holds byte for byte the
#: same and Bazel runs none of it.
PYSRC = "pysrc"


#: What tells a step that starts node: a script of this repo on node's command line, which
#: the trace sees. The packages beside that script come with it.
_NODE = ("tools/render/", "web/")


def _needs_node(srcs: list) -> bool:
    return any(s.startswith(_NODE) for s in srcs)


def target_name(gen: str) -> str:
    """A Bazel name for a generator. `_wiring_sync.py` is a doc sync like any other, and its
    leading underscore is a Python convention, not part of what it is called here."""
    return Path(gen).stem.strip("_").replace("_", "-")


def comments_come_out(src: str, rewritten: set) -> bool:
    """Whether a step reads `src` with its comments taken out.

    A generator whose own docstring holds figures is handed its file raw: the run rewrites what
    it was given, and `sync_tree` carries that back into the tree. So is anything under a node
    root — `:node-packages` globs those in whole, and a file arriving twice lands the second
    copy on the first, which Bazel leaves read-only."""
    return (src.endswith(".py") and src not in rewritten
            and not src.startswith(_NODE))


def read_from(src: str, rewritten: set) -> str:
    """Where a step reads `src` from — under `pysrc/` once its comments are out of it."""
    return f"{PYSRC}/{src}" if comments_come_out(src, rewritten) else src


def render(gens: tuple, arts: list, srcs: list, docs: list, rewritten: set) -> str:
    name = target_name(gens[0])
    # THE OUTPUT KEEPS THE PATH THE TREE KEEPS IT UNDER, so `sync_tree` strips one prefix and
    # has the file to carry it back to. Twenty generators cut a `README.md`, and a basename is
    # not a name for any of them.
    outs = [f"out/{name}/{a}" for a in (*arts, *docs)]
    lines = [f'genrule(', f'    name = "{name}",', "    srcs = ["]
    lines += [f'        "{read_from(s, rewritten)}",' for s in srcs]
    # NODE RESOLVES ITS OWN IMPORTS, below Python and out of the tracer's sight. A step that
    # hands node a script of this repo reads that script — the trace sees the path on the
    # command line — and the packages beside it come with it.
    if _needs_node(srcs):
        lines.append('        ":node-packages",')
    lines += ["    ],", "    outs = ["]
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
        "  case $$f in */node_modules/*) continue;; esac",
        f"  t=$${{f##*/{PYSRC}/}}",
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
        lines.append(f"HSM_REPO_ROOT=$$PWD HSM_INPUT_DIGEST=$$D {VENV} {g} > /dev/null")
    for i, made in enumerate((*arts, *docs)):
        lines.append(f"cp {made} $$O{i}")
    lines += ['""",', ")"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="emit one target, by generator path")
    args = ap.parse_args()

    files = tracked()
    inv = inventory(files)
    if args.only:
        inv = {k: v for k, v in inv.items() if args.only in k}

    held = set(files)
    if any(f"/{PYSRC}/" in f for f in held):
        raise SystemExit(f"  a tracked path holds /{PYSRC}/, which is where a stripped source"
                         f" lands — the staging loop cannot tell the two apart")

    blocks, comments_out = [], set()
    for gens, made in sorted(inv.items()):
        # A doc is read to be rewritten, so it is on both sides — named as a src under its own
        # path and handed back under the target's own, which `sync_tree` carries into the tree.
        # A solid the run cut is only ever handed back.
        srcs = (set(made["reads"]) | set(made["docs"]) | set(gens)) - set(made["solids"])
        srcs = sorted(s for s in srcs if s in held)
        rewritten = {d for d in made["docs"] if d.endswith(".py")}
        comments_out |= {s for s in srcs if comments_come_out(s, rewritten)}
        blocks.append(render(gens, made["solids"], srcs, made["docs"], rewritten))

    # ONE ACTION FOR THE WHOLE OF IT, so a comment edit is one short run and then a build that
    # finds every input where it left it.
    comments_out = sorted(comments_out)
    blocks.append(
        'genrule(\n    name = "%s",\n    srcs = [\n' % PYSRC
        + "".join(f'        "{s}",\n' for s in comments_out)
        + "    ],\n    outs = [\n"
        + "".join(f'        "{PYSRC}/{s}",\n' for s in comments_out)
        + '    ],\n    tools = ["tools/bazel/pysrc.py"],\n'
        + f'    cmd = "{VENV} $(location tools/bazel/pysrc.py)'
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
    # A RENDERER STANDS THE VIEWER AND PHOTOGRAPHS IT, so what it reads is the whole served
    # tree — `web/lib/templates/viewer-body.html` as much as the `.js` beside it — and the
    # packages node resolves those imports through. Globbed rather than read off the index,
    # because `.gitignore` holds `node_modules`, and named here rather than learned, because
    # node resolves below Python where the trace cannot follow.
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
                  + "".join('        ":%s",\n' % target_name(g[0]) for g in sorted(inv))
                  + "    ],\n)")
    (_ROOT / "BUILD.bazel").write_text(head + "\n" + "\n\n".join(blocks) + "\n")
    print(f"  {len(inv)} step(s) over {sum(len(k) for k in inv)} generators → BUILD.bazel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
