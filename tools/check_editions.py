"""Every edition's tree must aim at itself.

An edition (web/lib/editions.js) is one machine: its own generators, its own
assemblies, its own outputs. The trees are copies of each other, so nearly every
module name exists in all of them, and a path that escapes its own tree is
invisible — the script runs, the STEP is written, and the number came from the
wrong machine.

Nothing enforces that at run time. Python resolves an absolute path without
complaint, and CadQuery loads whichever STEP it is handed. So this walks each
edition's Python, resolves the repo-anchor idiom statically, and reports any
path that lands outside the tree it was written in.

Four anchor idioms are in use, and only two of them self-anchor:

    next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
    next(p for p in _here.parents if p.name == "hardware")

both stop at the nearest copy, so a file under thin/hardware/ resolves to
thin/. These do not:

    next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
    next(p for p in _here.parents if p.name == "homesodamachine")

They reach the real repo root, which is right for `tools/` — genuinely shared,
one copy, every edition uses it — and wrong for anything under `hardware/`.

Run: tools/cad-venv/bin/python tools/check_editions.py
"""

import ast
import re
import sys
from pathlib import Path

_here = Path(__file__).resolve()
REPO = _here.parents[1]

# Directories every edition legitimately shares, relative to the repo root. A
# path that escapes an edition into one of these is not a finding: there is one
# copy on purpose.
SHARED = ("tools",)


def editions():
    """(root, shared_dirs) per edition web/lib/editions.js declares, in order.

    `shared_dirs` is what that edition is allowed to reach outside its own root:
    its declared `shares`, plus the globally shared SHARED dirs.
    """
    src = (REPO / "web" / "lib" / "editions.js").read_text()
    # Each entry runs `dir: [...]` then `shares: [...]`; pair them in order.
    pairs = re.findall(r"dir:\s*\[([^\]]*)\].*?shares:\s*\[([^\]]*)\]", src, re.S)
    out = []
    for dir_src, shares_src in pairs:
        root = REPO.joinpath(*re.findall(r'"([^"]+)"', dir_src))
        if not root.is_dir():
            continue
        shared = [REPO / s for s in SHARED]
        shared += [REPO.joinpath(*s.split("/")) for s in re.findall(r'"([^"]+)"', shares_src)]
        out.append((root, shared))
    if not out:
        raise SystemExit("no editions found in web/lib/editions.js")
    return out


def _anchor_of(test, py_file):
    """Resolve one `next(p for p in _here.parents if TEST)` against a real file.

    Returns the directory the walk stops at, or None when the test isn't an
    idiom we model (in which case we can't judge the paths built from it).
    """
    parents = py_file.resolve().parents

    # (p / "a" / "b").is_file() / .is_dir()
    if isinstance(test, ast.Call) and isinstance(test.func, ast.Attribute) \
            and test.func.attr in ("is_file", "is_dir"):
        segments = _segments(test.func.value)
        if segments is None:
            return None
        for p in parents:
            target = p.joinpath(*segments)
            if target.is_file() if test.func.attr == "is_file" else target.is_dir():
                return p
        return None

    # p.name == "x"
    if isinstance(test, ast.Compare) and len(test.ops) == 1 and isinstance(test.ops[0], ast.Eq) \
            and isinstance(test.left, ast.Attribute) and test.left.attr == "name" \
            and isinstance(test.comparators[0], ast.Constant):
        want = test.comparators[0].value
        for p in parents:
            if p.name == want:
                return p
        return None

    return None


def _segments(node):
    """Constant path segments of a `base / "a" / "b"` chain, or None."""
    out = []
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        if not isinstance(node.right, ast.Constant) or not isinstance(node.right.value, str):
            return None
        out.append(node.right.value)
        node = node.left
    out.reverse()
    return out


def _base(node):
    """The expression a `x / "a" / "b"` chain is rooted at."""
    while isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        node = node.left
    return node


def _anchor_call(node, py_file):
    """Resolve `next(p for p in _here.parents if TEST)` written inline, or None.

    A chain can be rooted at the call itself rather than at a variable bound to
    it — `next(...) / "hardware" / "topology"` — and that reads as one
    expression, so it has to resolve the same way a named anchor does.
    """
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
            and node.func.id == "next" and node.args
            and isinstance(node.args[0], ast.GeneratorExp)):
        return None
    gen = node.args[0]
    if not gen.generators or len(gen.generators[0].ifs) != 1:
        return None
    return _anchor_of(gen.generators[0].ifs[0], py_file)


def escapes_in(py_file, root, shared_dirs):
    """Paths in `py_file` that resolve outside `root` and outside `shared_dirs`."""
    try:
        tree = ast.parse(py_file.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return []

    # Anchor variables: `X = next(p for p in _here.parents if TEST)`.
    anchors = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if not isinstance(node.targets[0], ast.Name):
            continue
        anchored = _anchor_call(node.value, py_file)
        if anchored is not None:
            anchors[node.targets[0].id] = anchored

    # Every `anchor / "a" / "b"` chain built from one of them. Only the whole
    # chain is a path anyone uses: `_repo / "hardware"` inside
    # `_repo / "hardware" / "scripts"` is a node in the tree, not a second
    # finding, so the inner links are skipped.
    inner = {id(n.left) for n in ast.walk(tree)
             if isinstance(n, ast.BinOp) and isinstance(n.op, ast.Div)}
    findings = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div)):
            continue
        if id(node) in inner:
            continue
        base = _base(node)
        if isinstance(base, ast.Name):
            anchor = anchors.get(base.id)
        else:
            anchor = _anchor_call(base, py_file)
        if anchor is None:
            continue
        segments = _segments(node)
        if not segments:
            continue
        # Split a segment that is itself a path ("hardware/printed-parts/x").
        parts = [s for seg in segments for s in seg.split("/") if s]
        resolved = anchor.joinpath(*parts)
        if resolved.is_relative_to(root):
            continue
        if any(resolved.is_relative_to(d) for d in shared_dirs):
            continue
        findings.append((node.lineno, anchor, resolved))
    return findings


def main():
    eds = editions()
    total = 0
    for root, shared_dirs in eds:
        rel_root = root.relative_to(REPO)
        declared = [d.relative_to(REPO) for d in shared_dirs if d != REPO / "tools"]
        bad = []
        for py in sorted(root.rglob("*.py")):
            if "__pycache__" in py.parts:
                continue
            for lineno, anchor, resolved in escapes_in(py, root, shared_dirs):
                bad.append((py.relative_to(REPO), lineno, resolved.relative_to(REPO)))
        note = f"shares {', '.join(str(d) for d in declared)}" if declared else "self-contained"
        if bad:
            print(f"FAIL  {rel_root} ({note}): {len(bad)} undeclared path(s) leave the edition")
            for rel, lineno, resolved in bad:
                print(f"        {rel}:{lineno}  ->  {resolved}")
        else:
            print(f"ok    {rel_root} ({note}): no undeclared path leaves the edition")
        total += len(bad)

    print(f"\n{len(eds)} edition(s) checked, {total} undeclared escape(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
