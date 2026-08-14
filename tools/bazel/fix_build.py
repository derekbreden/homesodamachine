#!/usr/bin/env python3
"""Read the build's own failures back into the graph, to a fixpoint.

    tools/cad-venv/bin/python tools/bazel/fix_build.py

An action that named too little does not read a stale file — it fails to find one. That
failure names the file, so it is the reading that settles what an action's inputs are, and
nothing here has to guess. Each pass builds everything, takes what the failures name, writes
it to `tools/bazel/extra_srcs.json`, regenerates, and goes again. A pass that adds nothing is
where it stops; a pass that adds the same thing twice is an action whose failure is not a
missing input, and it is printed rather than looped on.
"""

import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]
EXTRA = _HERE.parent / "extra_srcs.json"
MAX_PASSES = 12

_TARGET = re.compile(r"Executing genrule //:([\w.-]+) failed")
_MISSING_FILE = re.compile(r"No such file or directory: '[^']*/work/([^']+)'")
_MISSING_MOD = re.compile(r"No module named '([^']+)'")


def _tracked() -> set:
    return set(subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                              capture_output=True, text=True, check=True).stdout.split())


def _module_paths(mod: str, files: set) -> list:
    """Every tracked file a bare module name could be — the sandbox will keep whichever it
    imports, and naming a sibling that is never read costs a rebuild it did not need."""
    leaf = mod.split(".")[-1]
    return [f for f in files if Path(f).name == f"{leaf}.py"]


def main() -> int:
    files = _tracked()
    extra = json.loads(EXTRA.read_text()) if EXTRA.is_file() else {}
    seen_adds = set()

    for pass_no in range(1, MAX_PASSES + 1):
        subprocess.run([sys.executable, str(_HERE.parent / "gen_build.py")],
                       cwd=str(_ROOT), capture_output=True, text=True)
        p = subprocess.run(["bazel", "build", "//...", "--keep_going"],
                           cwd=str(_ROOT), capture_output=True, text=True)
        out = p.stdout + p.stderr
        if p.returncode == 0:
            print(f"pass {pass_no}: green — every action holds what it names")
            return 0

        # Attribute each missing name to the target whose action reported it.
        adds, target = {}, None
        for line in out.splitlines():
            m = _TARGET.search(line)
            if m:
                target = m.group(1)
            f = _MISSING_FILE.search(line)
            if f and target and f.group(1) in files:
                adds.setdefault(target, set()).add(f.group(1))
            mo = _MISSING_MOD.search(line)
            if mo and target:
                adds.setdefault(target, set()).update(_module_paths(mo.group(1), files))

        fresh = 0
        for t, names in adds.items():
            for n in sorted(names):
                key = f"{t}:{n}"
                if key in seen_adds:
                    continue
                seen_adds.add(key)
                extra.setdefault(t, [])
                if n not in extra[t]:
                    extra[t].append(n)
                    fresh += 1
        EXTRA.write_text(json.dumps({k: sorted(v) for k, v in extra.items()},
                                    indent=2, sort_keys=True) + "\n")
        failed = sorted({m.group(1) for m in _TARGET.finditer(out)})
        print(f"pass {pass_no}: {len(failed)} failing, {fresh} input(s) named")
        if not fresh:
            print("  no failure names a missing input; what is left is not a graph problem:")
            for t in failed[:10]:
                print(f"    //:{t}")
            return 1
    print(f"still failing after {MAX_PASSES} passes")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
