#!/usr/bin/env python3
"""Write BUILD.bazel from what the tree already records about its own generators.

    tools/cad-venv/bin/python tools/bazel/gen_build.py

`inventory.py` says which generators there are and what each one makes. What each one READS is
every path a run of it was watched opening — `trace_inputs.py` — plus the Python its imports
reach and the solids its stamps record, which cover a run that stopped early.

An action that names too little does not read a stale file: it fails to find one at all. So a
target here can be wrong in exactly one direction, and the build says which.
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
sys.path.insert(0, str(_ROOT / "hardware" / "scripts"))
sys.path.insert(0, str(_HERE.parent))

import _realized                                        # noqa: E402
from inventory import inventory, tracked   # noqa: E402

VENV = "/Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python"

#: What a generator cuts. A `.mesh` rides beside a solid for the viewer and is not committed.
#:
#: A `.step.png` IS NOT AMONG THEM. `_cadq_export` draws a thumbnail best-effort — "a thumbnail
#: must never break export" — by standing a server on loopback and photographing a page. An
#: output declared here is one the action must produce or fail, which is the opposite promise,
#: so the two cannot be the same thing. The thumbnails are still drawn by the run; they are
#: not what the build is asked to guarantee.
OUT_SUFFIXES = (".step", ".dxf", ".stl")
#: What a generator rewrites in place — an input to the run and an output of it, so it is
#: named on both sides under two names, and `sync` is what carries the second back.
DOC_SUFFIXES = (".md", ".figures.json")

#: See the tag it earns in `render`.
NOT_HERMETIC = ("hardware/assembly/scenes/render_scenes.py",)

_MISSING_FILE = re.compile(r"No such file or directory: '[^']*?/work/([^']+)'")
_MISSING_MOD = re.compile(r"No module named '([^']+)'")


EXTRA = _HERE.parent / "extra_srcs.json"


def _extra() -> dict:
    """Every file a run of each generator was watched opening — see `trace_inputs.py`.

    Keyed the way `target_name` keys a target, and a key written before it stopped leading
    with the generator's own underscore is read here under either spelling."""
    try:
        held = json.loads(EXTRA.read_text())
    except (OSError, ValueError):
        return {}
    return {k.lstrip("-"): v for k, v in held.items()}


def seed_srcs(gen: str, arts: list, files) -> list:
    """Every file this generator is known or likely to read."""
    srcs = set()
    # the Python its imports reach, walked from outside — short, and the sandbox says so
    try:
        for p in _realized.source_files(_ROOT / gen):
            srcs.add(Path(p).relative_to(_ROOT).as_posix())
    except (ValueError, OSError):
        srcs.add(gen)
    # the solids it loaded, as the stamps recorded them
    for art in arts:
        held = _realized.stamp_read("parts", _ROOT / art)
        srcs.update(held.get("sources") or {})
    # the docs beside it, which docgen rewrites in place
    d = str(Path(gen).parent)
    srcs.update(f for f in files
                if str(Path(f).parent) == d and f.endswith(DOC_SUFFIXES))
    # and every file a run of it was watched opening
    srcs.update(_extra().get(target_name(gen), []))
    # WHAT IT OPENED TO WRITE IS NOT WHAT IT READ. A trace sees a solid being cut the same way
    # it sees one being loaded, and a generator that takes its own output as an input rebuilds
    # whenever the copy in the tree moves — which is the copy this action exists to replace.
    return sorted(s for s in srcs - set(arts) if s in set(files))


def target_name(gen: str) -> str:
    """A Bazel name for a generator. `_wiring_sync.py` is a doc sync like any other, and its
    leading underscore is a Python convention, not part of what it is called here."""
    return Path(gen).stem.strip("_").replace("_", "-")


def render(gen: str, arts: list, srcs: list, docs: list) -> str:
    name = target_name(gen)
    outs = [f"out/{name}/{Path(a).name}" for a in arts]
    outs += [f"out/{name}/doc/{Path(d).name}" for d in docs]
    lines = [f'genrule(', f'    name = "{name}",', "    srcs = ["]
    lines += [f'        "{s}",' for s in srcs]
    # A THUMBNAIL IS DRAWN BY NODE, which resolves its own imports below Python and out of the
    # tracer's sight. A target that cuts one names the renderer's packages or it draws nothing
    # and the copy of its own declared output fails.
    if any(a.endswith(".png") for a in arts):
        lines.append('        ":node-packages",')
    lines += ["    ],", "    outs = ["]
    lines += [f'        "{o}",' for o in outs]
    lines += ["    ],"]
    # A THUMBNAIL IS A PHOTOGRAPH OF A PAGE. The renderer stands a server on loopback and
    # points a headless browser at it, so an action that draws one needs a socket; the rest
    # of the tree is built with the network off.
    if gen in NOT_HERMETIC:
        # A SCENE IS A PHOTOGRAPH OF A LIVE PAGE. `render-step-posed` stands the viewer on
        # loopback and points a headless browser at it, and that page loads occt-import-js
        # off a CDN — so drawing one reaches the network for a library this tree does not
        # carry. Vendoring it is what would make this action hermetic; until then it runs
        # outside the sandbox and is the one target here whose inputs are not all declared.
        lines.append('    tags = ["local", "requires-network"],')
    elif any(a.endswith(".png") for a in arts):
        lines.append('    tags = ["requires-network"],')
    lines += ['    cmd = """', "set -e"]
    for a, o in zip(arts, outs[:len(arts)]):
        lines.append(f"O_{Path(a).name.replace('.','_').replace('-','_')}=$$PWD/$(location {o})")
    for d, o in zip(docs, outs[len(arts):]):
        lines.append(f"D_{Path(d).name.replace('.','_').replace('-','_')}=$$PWD/$(location {o})")
    lines += [
        # THE COPY IS FOR THE FILES `Path(__file__).resolve()` WALKS OUT OF, which is this
        # repo's own Python. A package tree is read by node, which is content with a symlink,
        # and copying eleven thousand files into every action took the critical path from
        # 89 s to 281 s.
        "for f in $(SRCS); do",
        "  case $$f in */node_modules/*) continue;; esac",
        "  mkdir -p work/$$(dirname $$f); cp -L $$f work/$$f",
        "done",
        "for d in tools/render/node_modules web/node_modules; do",
        "  if [ -d $$d ]; then mkdir -p work/$$(dirname $$d); "
        "ln -sfn $$PWD/$$d work/$$d; fi",
        "done",
        "cd work",
        f"{VENV} {gen} > /dev/null",
    ]
    for a, o in zip(arts, outs[:len(arts)]):
        lines.append(f"cp {a} $$O_{Path(a).name.replace('.','_').replace('-','_')}")
    for d, o in zip(docs, outs[len(arts):]):
        lines.append(f"cp {d} $$D_{Path(d).name.replace('.','_').replace('-','_')}")
    lines += ['""",', ")"]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--only", help="emit one target, by generator path")
    args = ap.parse_args()

    files = tracked()
    inv = inventory(files)
    if args.only:
        inv = {k: v for k, v in inv.items() if k == args.only}

    blocks = []
    for gen, made in sorted(inv.items()):
        srcs = seed_srcs(gen, made["solids"], files)
        # A doc is read to be rewritten, so it is on both sides — named as a src under its own
        # path and handed back under the target's own, which `sync_tree` carries into the tree.
        srcs = sorted(set(srcs) | set(made["docs"]))
        blocks.append(render(gen, made["solids"], srcs, made["docs"]))

    head = (
        "# The appliance's geometry, docs and pictures — one action per generator. Written by\n"
        "# tools/bazel/gen_build.py off tools/bazel/inventory.py; the sandbox corrects it.\n"
        "#\n"
        "# WHAT AN ACTION HOLDS IS WHAT IT NAMED. A generator reads the Python its imports\n"
        "# reach, the solids it loads and the docs it rewrites; all three are `srcs`, and\n"
        "# nothing else is in the directory the run happens in. A solid one generator cuts and\n"
        "# the next loads is an edge like any other: unnamed, the reader does not find the file.\n"
    )
    # NODE RESOLVES ITS OWN IMPORTS, below Python and out of the tracer's sight, so the
    # packages a renderer needs are named here rather than learned. `.gitignore` holds them,
    # so they are globbed rather than read off the index.
    blocks.append(
        'filegroup(\n    name = "node-packages",\n    srcs = glob(\n'
        '        [\n'
        '            "tools/render/*.js",\n'
        '            "tools/render/node_modules/**",\n'
        '            "web/**/*.js",\n'
        '            "web/node_modules/**",\n'
        '        ],\n'
        '        allow_empty = True,\n    ),\n)')

    # ONE NAME FOR THE WHOLE TREE, so what a commit owes is `bazel build //:everything` and
    # what it carries is `sync_tree --write`.
    blocks.append("filegroup(\n    name = \"everything\",\n    srcs = [\n"
                  + "".join('        ":%s",\n' % target_name(g) for g in sorted(inv))
                  + "    ],\n)")
    (_ROOT / "BUILD.bazel").write_text(head + "\n" + "\n\n".join(blocks) + "\n")
    print(f"  {len(inv)} generator(s) → BUILD.bazel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
