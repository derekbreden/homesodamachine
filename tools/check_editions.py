"""Every anchored path must land on the tree its job lives in.

An edition (web/lib/editions.js) is one machine: its own generators, its own
assemblies, its own outputs. A path that escapes its tree is invisible — the
script runs, the STEP is written, and the number came from outside the job. A
shared path that fails to reach the repo root is the other direction: it names a
directory the content root holds no copy of, and the module never imports.

Nothing enforces either at run time. Python resolves an absolute path without
complaint, and CadQuery loads whichever STEP it is handed. So this walks the
edition's Python, resolves the anchor idioms statically, and reports a path that
lands outside the tree it was written in, or one that stays inside that tree
while naming something only the repo root carries.

Four anchor idioms are in use, and only two of them self-anchor:

    next(p for p in _here.parents if (p / "hardware" / "scripts" / "_cadq_export.py").is_file())
    next(p for p in _here.parents if p.name == "hardware")

both stop at the content root. These do not:

    next(p for p in _here.parents if (p / "tools" / "docgen").is_dir())
    next(p for p in _here.parents if p.name == "homesodamachine")

They reach the repo root, which is right for `tools/` — genuinely shared, one
copy — and wrong for anything under `hardware/`.

A positional anchor — `.parent`, `.parents[N]` — lands on whatever sits N levels
up, the repo root from `hardware/`. One written for `tools/` and used under
`hardware/` finds nothing where it points.

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


def _is_resolved_file(node):
    """`Path(__file__).resolve()` — the file the anchor is written in."""
    if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "resolve" and not node.args):
        return False
    inner = node.func.value
    return (isinstance(inner, ast.Call) and isinstance(inner.func, ast.Name)
            and inner.func.id == "Path" and len(inner.args) == 1
            and isinstance(inner.args[0], ast.Name) and inner.args[0].id == "__file__")


def _dir_expr(node, py_file, anchors):
    """The directory an anchor expression resolves to, or None when it isn't an
    idiom we model.

    Covers a name already bound to an anchor, an inline `next(...)` walk,
    `Path(__file__).resolve()`, and the positional steps `.parent` and
    `.parents[N]` off any of those.
    """
    if isinstance(node, ast.Name):
        return anchors.get(node.id)

    anchored = _anchor_call(node, py_file)
    if anchored is not None:
        return anchored

    if _is_resolved_file(node):
        return py_file.resolve()

    if isinstance(node, ast.Attribute) and node.attr == "parent":
        base = _dir_expr(node.value, py_file, anchors)
        return None if base is None else base.parent

    if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Attribute) \
            and node.value.attr == "parents" and isinstance(node.slice, ast.Constant) \
            and isinstance(node.slice.value, int):
        base = _dir_expr(node.value.value, py_file, anchors)
        if base is None:
            return None
        try:
            return base.parents[node.slice.value]
        except IndexError:
            return None

    return None


def findings_in(py_file, root, shared_dirs):
    """`(kind, lineno, resolved, intended)` per path in `py_file` that misses its job.

    kind is "escape" — resolves outside `root` and outside `shared_dirs`, with no
    `intended` — or "stranded" — rebuilds a shared dir's name where there is
    nothing, with `intended` the repo-root copy it was reaching for.
    """
    try:
        tree = ast.parse(py_file.read_text())
    except (SyntaxError, UnicodeDecodeError):
        return []

    # Anchor variables: `X = next(p for p in _here.parents if TEST)`, or a
    # positional step off one — `X = Path(__file__).resolve().parents[4]`.
    anchors = {}
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or len(node.targets) != 1:
            continue
        if not isinstance(node.targets[0], ast.Name):
            continue
        anchored = _dir_expr(node.value, py_file, anchors)
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
        anchor = _dir_expr(_base(node), py_file, anchors)
        if anchor is None:
            continue
        segments = _segments(node)
        if not segments:
            continue
        # Split a segment that is itself a path ("hardware/printed-parts/x").
        parts = [s for seg in segments for s in seg.split("/") if s]
        resolved = anchor.joinpath(*parts)
        intended = _stranded(resolved, shared_dirs)
        if intended is not None:
            findings.append(("stranded", node.lineno, resolved, intended))
            continue
        if resolved.is_relative_to(root):
            continue
        if any(resolved.is_relative_to(d) for d in shared_dirs):
            continue
        findings.append(("escape", node.lineno, resolved, None))
    return findings


def _stranded(resolved, shared_dirs):
    """The repo-root path `resolved` was reaching for, or None if it isn't stranded.

    A shared dir has one copy. An anchor that stops short of the repo root
    rebuilds its name somewhere there is nothing — `thin/tools` for `tools`.
    Matched on the name, confirmed on what is on disk: nothing where it points,
    something where the repo root holds it.
    """
    for shared in shared_dirs:
        want = shared.relative_to(REPO).parts
        parts = resolved.parts
        for i in range(len(parts) - len(want) + 1):
            if parts[i:i + len(want)] != want:
                continue
            intended = REPO.joinpath(*parts[i:])
            if intended != resolved and intended.exists() and not resolved.exists():
                return intended
    return None


def main():
    eds = editions()
    total = 0
    for root, shared_dirs in eds:
        rel_root = root.relative_to(REPO)
        declared = [d.relative_to(REPO) for d in shared_dirs if d != REPO / "tools"]
        escaped, stranded = [], []
        for py in sorted(root.rglob("*.py")):
            if "__pycache__" in py.parts:
                continue
            for kind, lineno, resolved, intended in findings_in(py, root, shared_dirs):
                row = (py.relative_to(REPO), lineno, resolved.relative_to(REPO),
                       intended.relative_to(REPO) if intended else None)
                (escaped if kind == "escape" else stranded).append(row)
        note = f"shares {', '.join(str(d) for d in declared)}" if declared else "self-contained"
        if escaped or stranded:
            counts = []
            if escaped:
                counts.append(f"{len(escaped)} undeclared path(s) leave the edition")
            if stranded:
                counts.append(f"{len(stranded)} shared path(s) never reach the repo root")
            print(f"FAIL  {rel_root} ({note}): {', '.join(counts)}")
            for rel, lineno, resolved, _ in escaped:
                print(f"        {rel}:{lineno}  ->  {resolved}")
            for rel, lineno, resolved, intended in stranded:
                print(f"        {rel}:{lineno}  ->  {resolved}  (nothing there; {intended} is)")
        else:
            print(f"ok    {rel_root} ({note}): every anchored path lands in its own tree")
        total += len(escaped) + len(stranded)

    print(f"\n{len(eds)} edition(s) checked, {total} misplaced path(s)")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
