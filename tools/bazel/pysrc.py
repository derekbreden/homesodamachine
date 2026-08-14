#!/usr/bin/env python3
"""A Python file with its comments taken out and its lines where they were.

    tools/cad-venv/bin/python tools/bazel/pysrc.py <out-root> <file.py> …

A comment is invisible to Python: a file whose comments moved draws the same walls, writes the
same figures and takes the same picture. Bazel names an input by its bytes. So the build steps
read what comes out of here instead of the file, and a comment edit moves this not at all —
Bazel finds an input it has already built against, and nothing downstream runs. A code edit
moves it, and everything that reads it runs. `_realized.code_digest` names a file by its parsed
form; this is that reading, put where Bazel can see it.

WHAT COMES OUT PARSES TO WHAT WENT IN, attributes and all, asserted per file. No line is ever
removed, only emptied, so a traceback points at the line the reader has open.

A DOCSTRING IS NOT A COMMENT. It is a value the code carries, and a doc that prints one moves
when it moves, so it stays. `gen_build` hands the generators whose docstrings hold figures
their file raw.
"""

import ast
import io
import sys
import tokenize
from pathlib import Path


def stripped(raw: bytes) -> bytes:
    """`raw` with every comment gone, every line still where it was.

    A comment is cut back to the code before it on its line, and a line that was only a comment
    is left empty. Two files that differ in their comments come out byte for byte the same."""
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(raw).readline)
    except SyntaxError:
        return raw
    if encoding != "utf-8":
        return raw

    cut: dict = {}
    for tok in tokenize.tokenize(io.BytesIO(raw).readline):
        if tok.type == tokenize.COMMENT:
            row, col = tok.start
            cut[row] = min(cut.get(row, col), col)

    lines = raw.decode("utf-8").splitlines(keepends=True)
    for row, col in cut.items():
        line = lines[row - 1]
        end = "\n" if line.endswith("\n") else ""
        lines[row - 1] = line[:col].rstrip() + end
    return "".join(lines).encode("utf-8")


def same_code(before: bytes, after: bytes) -> bool:
    """Whether the two parse to the same tree, standing in the same places."""
    def dump(b):
        return ast.dump(ast.parse(b), include_attributes=True)
    try:
        return dump(before) == dump(after)
    except SyntaxError:
        return before == after


def main(argv: list) -> int:
    root, files = Path(argv[0]), argv[1:]
    for rel in files:
        raw = Path(rel).read_bytes()
        try:
            ast.parse(raw)
            out = stripped(raw)
        except SyntaxError:
            out = raw                            # a file that will not parse keeps its bytes
        if not same_code(raw, out):
            print(f"  {rel}: stripping its comments moved what it computes", file=sys.stderr)
            return 1
        dest = root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
