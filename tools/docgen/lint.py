"""Cross-file NAME-collision linter for docgen markers.

The substituters (`substitute_md`, `substitute_py_comments`) are scoped
to a single file each, so they cannot detect when the same NAME
resolves to different values in different files. This module walks a
directory tree, extracts every [value](NAME) marker (from .md files
and from .py # comments), groups by NAME, and reports any NAME that
has more than one distinct value across the tree.

Run as:

    tools/cad-venv/bin/python -m docgen.lint              # cwd
    tools/cad-venv/bin/python -m docgen.lint <directory>  # specific root

Exit code is 0 if every NAME resolves consistently across the scanned
tree, 1 if any collision was found.

Normalization: values are stripped of surrounding whitespace before
comparison. Numeric formatting differences ("32 mm" vs "32.0 mm") are
NOT normalized — those are intentionally treated as distinct values
because they often hide a real drift.
"""

import io
import sys
import tokenize
from pathlib import Path

from . import _LINK_RE


# Directory names that should never be descended into during a lint scan.
SKIP_DIRS = {"cad-venv", "__pycache__", ".git", "node_modules"}


def _extract_from_text(text: str) -> list[tuple[str, str]]:
    """Return [(name, raw_value), ...] for every [value](NAME) in `text`."""
    return [(m.group(2), m.group(1)) for m in _LINK_RE.finditer(text)]


def _extract_from_md(md_path: Path) -> list[tuple[str, str]]:
    """Extract every [value](NAME) from a markdown file."""
    try:
        text = md_path.read_text()
    except (OSError, UnicodeDecodeError):
        return []
    return _extract_from_text(text)


def _extract_from_py(py_path: Path) -> list[tuple[str, str]]:
    """Extract every [value](NAME) from `#` comments in a Python file.

    Uses `tokenize` so we only see actual COMMENT tokens — `#` inside
    string literals, f-strings, etc. is invisible (mirroring
    `substitute_py_comments`).
    """
    try:
        text = py_path.read_text()
    except (OSError, UnicodeDecodeError):
        return []
    try:
        tokens = list(
            tokenize.generate_tokens(io.StringIO(text).readline)
        )
    except tokenize.TokenizeError:
        return []
    out: list[tuple[str, str]] = []
    for tok in tokens:
        if tok.type == tokenize.COMMENT:
            out.extend(_extract_from_text(tok.string))
    return out


def _iter_files(root: Path):
    """Yield every .md and .py file under `root`, skipping SKIP_DIRS."""
    for path in root.rglob("*"):
        # Skip anything inside an excluded directory.
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix == ".md" or path.suffix == ".py":
            yield path


def _normalize(value: str) -> str:
    """Minimal normalization: strip surrounding whitespace only."""
    return value.strip()


def scan(root: Path) -> dict[str, dict[str, list[Path]]]:
    """Walk `root` and return {NAME: {normalized_value: [paths, ...]}}.

    A NAME with multiple distinct keys in its inner dict is a collision.
    """
    occurrences: dict[str, dict[str, list[Path]]] = {}
    for path in _iter_files(root):
        if path.suffix == ".md":
            pairs = _extract_from_md(path)
        else:
            pairs = _extract_from_py(path)
        for name, value in pairs:
            norm = _normalize(value)
            by_value = occurrences.setdefault(name, {})
            paths = by_value.setdefault(norm, [])
            # Don't list the same file twice for the same (name, value).
            if not paths or paths[-1] != path:
                if path not in paths:
                    paths.append(path)
    return occurrences


def find_collisions(
    occurrences: dict[str, dict[str, list[Path]]],
) -> dict[str, dict[str, list[Path]]]:
    """Filter `occurrences` to NAMEs with more than one distinct value."""
    return {
        name: by_value
        for name, by_value in occurrences.items()
        if len(by_value) > 1
    }


def format_collision(
    name: str,
    by_value: dict[str, list[Path]],
    root: Path,
) -> str:
    """Format one NAME's collision as a multi-line string.

    Paths are printed relative to `root` if possible; otherwise absolute.
    """
    distinct_value_count = len(by_value)
    total_file_count = sum(len(paths) for paths in by_value.values())
    lines = [
        f"NAME `{name}` has {distinct_value_count} distinct values "
        f"across {total_file_count} files:"
    ]
    # Sort values for stable output.
    for value in sorted(by_value):
        lines.append(f'  "{value}" in:')
        for path in sorted(by_value[value]):
            try:
                rel = path.relative_to(root)
                shown = str(rel)
            except ValueError:
                shown = str(path)
            lines.append(f"    - {shown}")
    return "\n".join(lines)


def lint(root: Path | str = ".") -> int:
    """Scan `root` and print collisions. Returns 0 if none, 1 otherwise."""
    root_path = Path(root).resolve()
    occurrences = scan(root_path)
    collisions = find_collisions(occurrences)
    if not collisions:
        return 0
    # Sort collisions by name for stable output.
    blocks = [
        format_collision(name, collisions[name], root_path)
        for name in sorted(collisions)
    ]
    print("\n\n".join(blocks))
    print(
        f"\n{len(collisions)} NAME(s) with cross-file value collisions.",
        file=sys.stderr,
    )
    return 1


def main(argv: list[str] | None = None) -> int:
    """CLI entrypoint. Default root is cwd; one optional positional arg."""
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) == 0:
        roots = [Path.cwd()]
    else:
        roots = [Path(a) for a in args]

    # Scan each root and merge — lets `python -m docgen.lint hardware/ tools/`
    # behave like one combined scan.
    occurrences: dict[str, dict[str, list[Path]]] = {}
    for r in roots:
        rp = r.resolve()
        for name, by_value in scan(rp).items():
            merged = occurrences.setdefault(name, {})
            for value, paths in by_value.items():
                merged_paths = merged.setdefault(value, [])
                for p in paths:
                    if p not in merged_paths:
                        merged_paths.append(p)

    collisions = find_collisions(occurrences)
    if not collisions:
        return 0

    # Use the first root as the display anchor for relative paths.
    display_root = roots[0].resolve()
    blocks = [
        format_collision(name, collisions[name], display_root)
        for name in sorted(collisions)
    ]
    print("\n\n".join(blocks))
    print(
        f"\n{len(collisions)} NAME(s) with cross-file value collisions.",
        file=sys.stderr,
    )
    return 1


# --------------------------------------------------------------------------
# Self-test — run via `tools/cad-venv/bin/python -m docgen.lint --test`.
# Synthesizes a tiny on-disk tree, asserts the linter reports the right
# collisions, then cleans up.

def test_lint() -> None:
    """Minimal self-test for collision detection. Raises on failure."""
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "sub").mkdir()
        (root / "cad-venv").mkdir()       # should be skipped
        (root / "__pycache__").mkdir()    # should be skipped

        # Scenario 1: collision across two .md files.
        (root / "a.md").write_text(
            "Pill is [13.4 mm](PILL_L) wide.\n"
            "Width is [7.05 mm](PILL_W).\n"
        )
        (root / "sub" / "b.md").write_text(
            "Different pill: [13.2 mm](PILL_L) here.\n"
            "Width: [7.05 mm](PILL_W).\n"  # consistent
        )

        # Scenario 2: collision between a .md and a .py # comment.
        (root / "c.py").write_text(
            '# Diameter is [32 mm](DIA) per side.\n'
            'BORE = "[32 mm](DIA)"  # inside a string literal — IGNORED\n'
        )
        (root / "d.md").write_text("Bore [33 mm](DIA) per side.\n")

        # Scenario 3: whitespace differences should NOT collide.
        (root / "e.md").write_text("Height: [10 mm  ](HEIGHT)\n")
        (root / "f.md").write_text("Height: [10 mm](HEIGHT)\n")

        # Scenario 4: a NAME that appears only once — no collision.
        (root / "g.md").write_text("[42 mm](ONLY_ONCE)\n")

        # Scenario 5: skip dirs must be ignored even with marker content.
        (root / "cad-venv" / "ignored.md").write_text("[99 mm](DIA)\n")
        (root / "__pycache__" / "ignored.py").write_text(
            "# [88 mm](DIA)\n"
        )

        occurrences = scan(root)
        collisions = find_collisions(occurrences)
        names = set(collisions)

        # Expectations.
        assert "PILL_L" in names, f"PILL_L should collide; got {names}"
        assert "DIA" in names, f"DIA should collide; got {names}"
        assert "PILL_W" not in names, "PILL_W is consistent — no collision"
        assert "HEIGHT" not in names, (
            "HEIGHT differs only by trailing whitespace — must be normalized"
        )
        assert "ONLY_ONCE" not in names, "ONLY_ONCE appears once — no collision"

        # DIA collision must include c.py and d.md, but NOT pull values
        # from the string literal in c.py or from the skipped dirs.
        dia_values = set(collisions["DIA"])
        assert dia_values == {"32 mm", "33 mm"}, (
            f"DIA values from comments + md only, got {dia_values}"
        )

        # Exit code behavior.
        assert lint(root) == 1, "lint() must return 1 when collisions exist"
        (root / "a.md").unlink()
        (root / "sub" / "b.md").unlink()
        (root / "c.py").unlink()
        (root / "d.md").unlink()
        (root / "e.md").unlink()
        (root / "f.md").unlink()
        (root / "g.md").unlink()
        assert lint(root) == 0, "lint() must return 0 when no collisions"

    print("test_lint: OK")


if __name__ == "__main__":
    if "--test" in sys.argv:
        test_lint()
        sys.exit(0)
    sys.exit(main())
