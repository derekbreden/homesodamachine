#!/usr/bin/env python3
"""Write BUILD.bazel from what the tree already records about its own generators.

    tools/cad-venv/bin/python tools/bazel/gen_build.py

A generator is the one `.py` in a directory that holds committed artifacts; what it cuts is
those artifacts; what it reads is the Python its imports reach, the solids it loaded, and the
docs it rewrites in place. The first two the tree records — `.cache/stamps/parts/` per solid,
`_realized.source_files` for the rest. The third is the one a walk cannot find, so this seeds
it from the directory and lets the sandbox correct the seed: an action that names too little
does not read a stale file, it fails to find one at all, and `--fix` reads that failure back
into the list.

WHAT THIS EMITS IS A SEED, NOT AN ANSWER. The build is the authority on its own graph.
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
OUT_SUFFIXES = (".step", ".dxf", ".stl", ".step.png", ".dxf.png")
#: What a generator rewrites in place — an input to the run and an output of it, so it is
#: named on both sides under two names, and `sync` is what carries the second back.
DOC_SUFFIXES = (".md", ".figures.json")

_MISSING_FILE = re.compile(r"No such file or directory: '[^']*?/work/([^']+)'")
_MISSING_MOD = re.compile(r"No module named '([^']+)'")


EXTRA = _HERE.parent / "extra_srcs.json"


def _extra() -> dict:
    """What the sandbox has already told us an action reads — see `fix_build.py`."""
    try:
        return json.loads(EXTRA.read_text())
    except (OSError, ValueError):
        return {}


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
    # and whatever the sandbox has since said this action actually reads
    srcs.update(_extra().get(target_name(gen), []))
    return sorted(s for s in srcs if s in set(files))


def target_name(gen: str) -> str:
    return Path(gen).stem.replace("_", "-")


def render(gen: str, arts: list, srcs: list, docs: list) -> str:
    name = target_name(gen)
    outs = [f"out/{name}/{Path(a).name}" for a in arts]
    outs += [f"out/{name}/doc/{Path(d).name}" for d in docs]
    lines = [f'genrule(', f'    name = "{name}",', "    srcs = ["]
    lines += [f'        "{s}",' for s in srcs]
    lines += ["    ],", "    outs = ["]
    lines += [f'        "{o}",' for o in outs]
    lines += ["    ],", '    cmd = """', "set -e"]
    for a, o in zip(arts, outs[:len(arts)]):
        lines.append(f"O_{Path(a).name.replace('.','_').replace('-','_')}=$$PWD/$(location {o})")
    for d, o in zip(docs, outs[len(arts):]):
        lines.append(f"D_{Path(d).name.replace('.','_').replace('-','_')}=$$PWD/$(location {o})")
    lines += [
        "for f in $(SRCS); do mkdir -p work/$$(dirname $$f); cp -L $$f work/$$f; done",
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
    (_ROOT / "BUILD.bazel").write_text(head + "\n" + "\n\n".join(blocks) + "\n")
    print(f"  {len(inv)} generator(s) → BUILD.bazel")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
