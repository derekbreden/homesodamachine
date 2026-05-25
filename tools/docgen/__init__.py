"""
Variable substitution for documentation that lives next to its source.

Syntax: [value](VARIABLE_NAME)
- The brackets hold the value — what renders when the host format displays it.
- The parens hold the variable name in UPPERCASE_WITH_UNDERSCORES (digits
  allowed after the first character — e.g. ZONE1_Z_TOP, CO2_INLET, BEND2_R) —
  the "href" position. A real markdown link; the broken anchor doesn't matter.
- The variable name is literally in the source for any reader (agent or
  human) to see. The value is never authoritative; the script's variable is.

Two substituters with the same signature and semantics:

- substitute_md(md_path, ...) — rewrites inside a markdown file.
- substitute_py_comments(py_path, ...) — rewrites inside `#` line comments
  of a Python file. The script modifies its own comments — safe because
  only comment text is touched (never code, never strings/docstrings),
  the file is only written when content changes, and the rewritten comment
  text is never read back into any calculation.

Both:
- Find every [value](NAME) where NAME matches [A-Z_][A-Z0-9_]* in their scope.
- For each NAME in `variables`, rewrite the value to the current source
  value (str-cast).
- For each NAME in `expected_counts`, assert the actual count matches.
- Leave [value](NAME) patterns whose NAME isn't in `variables` untouched.
  This lets multiple scripts contribute substitutions to the same file —
  each call only manages its own names. The trade-off is that a typo
  `[X](BOGUS_NAME)` won't be caught by any individual call; it just sits
  there. If you need strict catching, the union of every caller's
  `variables` keys needs to cover every NAME in the file.

Normal markdown links (parens contain slashes, dots, colons, lowercase, etc.)
never match — only our all-caps-and-underscores variable references do. The
first-character restriction (no leading digit) keeps numeric literals like
`[0.5](2)` from being interpreted as substitution targets.

Sources section
---------------

substitute_md also maintains a `## Sources` block at the end of every
markdown file it touches, listing the repo-relative path(s) of the
script(s) that own its [value](NAME) markers. The caller's path is
auto-detected via the call stack — no extra argument needed. Multiple
callers per file accumulate as separate bullets (deduped, sorted).
A caller's bullet stays in place even if the script later stops
calling substitute_md on the file; pruning is manual.

Cross-file collision linter
---------------------------

The per-file substituters cannot detect when the same NAME resolves to
different values in different files (e.g., `PILL_L` rendered as
`13.4 mm` in one part's docs and `13.2 mm` in a sibling's). The
`docgen.lint` submodule walks a directory tree, extracts every
[value](NAME) marker from .md files and from .py `#` comments, and
reports any NAME with more than one distinct value across files.

Invoke as:

    tools/cad-venv/bin/python -m docgen.lint              # scan cwd
    tools/cad-venv/bin/python -m docgen.lint <directory>  # scan a root

Exit code is 0 if no collisions are found, 1 otherwise.
"""

import inspect
import io
import re
import tokenize
from pathlib import Path
from typing import Any


# Matches a markdown link whose href is an all-caps-and-underscores NAME
# (digits allowed after the first character, but not as the first character).
# Captures: 1 = value (bracket text), 2 = variable name (paren content).
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")


# Sources section — appended/updated by substitute_md at the end of every
# .md it touches, so a reader can see which Python file(s) keep this
# markdown's [value](NAME) markers honest.
_SOURCES_HEADER = "## Sources"
_SOURCES_PREAMBLE = "[value](NAME) texts are updated by:"
# Matches an existing Sources section: header line, preamble line, then one
# or more `- `…`` bullets. Caller normalizes text to end with \n first.
_SOURCES_SECTION_RE = re.compile(
    re.escape(_SOURCES_HEADER) + r"\n"
    + re.escape(_SOURCES_PREAMBLE) + r"\n"
    + r"((?:- `[^`\n]+`\n)+)"
)


def _find_repo_root(path: Path) -> Path | None:
    """Walk up from `path` looking for a `.git` directory."""
    for p in [path, *path.parents]:
        if (p / ".git").exists():
            return p
    return None


def _caller_repo_path(stack_depth: int = 2) -> str | None:
    """Repo-root-relative path of the script that called substitute_md.

    `stack_depth` = how far up the call stack to look. Default 2:
    0 is this helper, 1 is substitute_md, 2 is the caller.

    Returns a string like `/hardware/foo/bar/foo_bar.py`,
    or None if the caller's file is outside the repo or unidentifiable.
    """
    try:
        caller_file = Path(inspect.stack()[stack_depth].filename).resolve()
    except (IndexError, OSError):
        return None
    repo = _find_repo_root(caller_file)
    if repo is None:
        return None
    try:
        rel = caller_file.relative_to(repo)
    except ValueError:
        return None
    return f"/{rel.as_posix()}"


def _render_sources_section(bullets: list[str]) -> str:
    """Build the Sources section text. Each bullet line ends with \\n."""
    bullet_lines = "\n".join(f"- `{b}`" for b in bullets)
    return f"{_SOURCES_HEADER}\n{_SOURCES_PREAMBLE}\n{bullet_lines}\n"


def _update_sources_section(text: str, caller_path: str) -> str:
    """Ensure the Sources section in `text` lists `caller_path`. If the
    section exists, add `caller_path` to its bullet list (deduped, sorted)
    leaving any other callers' bullets alone. If absent, append the
    section after the existing content with a blank-line separator."""
    # Normalize trailing newline so the regex can match the last bullet.
    if text and not text.endswith("\n"):
        text = text + "\n"

    match = _SOURCES_SECTION_RE.search(text)
    if match:
        paths: set[str] = set()
        for line in match.group(1).split("\n"):
            line = line.strip()
            if line.startswith("- `") and line.endswith("`"):
                paths.add(line[3:-1])
        paths.add(caller_path)
        new_section = _render_sources_section(sorted(paths))
        return text[:match.start()] + new_section + text[match.end():]

    new_section = _render_sources_section([caller_path])
    # Empty/whitespace-only file: section becomes the whole file.
    if not text.strip():
        return new_section
    return text.rstrip() + "\n\n" + new_section


def substitute_md(
    md_path: Path | str,
    variables: dict[str, Any],
    expected_counts: dict[str, int],
) -> None:
    """Rewrite [value](NAME) → [current_value](NAME) in `md_path` for each
    NAME in `variables`, validating counts and unknown-name references.

    Args:
        md_path: Path to the markdown file (updated in place).
        variables: name → current value. Each value is str-cast for insertion.
        expected_counts: name → expected number of [value](NAME) occurrences.
            Every name here must also appear in `variables`.

    Raises:
        ValueError: if expected_counts has names with no variable value, or
            if the markdown references any unknown NAME, or if any
            expected count doesn't match the actual count.
    """
    md_path = Path(md_path)

    missing_vars = sorted(set(expected_counts) - set(variables))
    if missing_vars:
        raise ValueError(
            f"{md_path}: expected_counts has names with no variable value: "
            f"{missing_vars}"
        )

    text = md_path.read_text()

    # Count occurrences of every NAME the caller knows about. Names that
    # appear in the markdown but aren't in `variables` are left alone —
    # they belong to some other script that contributes to this markdown.
    name_counts: dict[str, int] = {}
    for match in _LINK_RE.finditer(text):
        name = match.group(2)
        if name in variables:
            name_counts[name] = name_counts.get(name, 0) + 1

    count_errors: list[str] = []
    for name, expected in expected_counts.items():
        actual = name_counts.get(name, 0)
        if actual != expected:
            count_errors.append(f"  {name}: expected {expected}, found {actual}")
    if count_errors:
        raise ValueError(
            f"{md_path}: variable reference count mismatch:\n"
            + "\n".join(count_errors)
        )

    def repl(match: re.Match) -> str:
        name = match.group(2)
        if name in variables:
            return f"[{variables[name]}]({name})"
        return match.group(0)  # unknown — leave alone

    new_text = _LINK_RE.sub(repl, text)

    # Maintain the Sources section at end of file. Auto-detects the
    # caller's repo path via the call stack; silently skips if the
    # caller isn't inside a .git checkout.
    caller_path = _caller_repo_path()
    if caller_path:
        new_text = _update_sources_section(new_text, caller_path)

    if new_text != text:
        md_path.write_text(new_text)


def substitute_py_comments(
    py_path: Path | str,
    variables: dict[str, Any],
    expected_counts: dict[str, int],
) -> None:
    """Rewrite [value](NAME) → [current_value](NAME) inside Python `#`
    comments in `py_path` for each NAME in `variables`.

    Operates only on `#` line comments. Code, string literals, docstrings,
    and every other token in the file are left untouched. Same
    skip-unknown-names semantics as substitute_md so multiple scripts can
    contribute substitutions to the same .py file. Idempotent: rerunning
    with the same variable values produces no write.

    Args:
        py_path: Path to the Python file (updated in place when any value
            actually changes).
        variables: name → current value. Each value is str-cast for
            insertion (same as substitute_md).
        expected_counts: name → expected number of [value](NAME)
            occurrences inside #-comments. Every name here must also
            appear in `variables`.

    Raises:
        ValueError: if expected_counts has names with no variable value,
            or if any expected count doesn't match the actual count.
    """
    py_path = Path(py_path)

    missing_vars = sorted(set(expected_counts) - set(variables))
    if missing_vars:
        raise ValueError(
            f"{py_path}: expected_counts has names with no variable value: "
            f"{missing_vars}"
        )

    text = py_path.read_text()

    # Find every # comment token. tokenize correctly skips # characters
    # that appear inside strings, f-strings, etc. — those are STRING tokens,
    # not COMMENT tokens, and stay invisible to the substitution.
    comment_tokens = [
        tok
        for tok in tokenize.generate_tokens(io.StringIO(text).readline)
        if tok.type == tokenize.COMMENT
    ]

    # Count occurrences of every NAME the caller knows about, ignoring
    # unknowns (let other scripts' substitutions alone).
    name_counts: dict[str, int] = {}
    for tok in comment_tokens:
        for match in _LINK_RE.finditer(tok.string):
            name = match.group(2)
            if name in variables:
                name_counts[name] = name_counts.get(name, 0) + 1

    count_errors: list[str] = []
    for name, expected in expected_counts.items():
        actual = name_counts.get(name, 0)
        if actual != expected:
            count_errors.append(f"  {name}: expected {expected}, found {actual}")
    if count_errors:
        raise ValueError(
            f"{py_path}: variable reference count mismatch:\n"
            + "\n".join(count_errors)
        )

    def repl(match: re.Match) -> str:
        name = match.group(2)
        if name in variables:
            return f"[{variables[name]}]({name})"
        return match.group(0)  # unknown — leave alone

    # Rewrite each comment in place. Python's # comments always run from
    # `#` to end-of-line, so at most one comment per line — token positions
    # from the original text stay valid even after earlier comments are
    # rewritten (the rewrites only change content within a single line).
    lines = text.splitlines(keepends=True)
    for tok in comment_tokens:
        line_idx = tok.start[0] - 1            # 1-indexed → 0-indexed
        start_col = tok.start[1]
        end_col = tok.end[1]
        line = lines[line_idx]
        new_comment = _LINK_RE.sub(repl, tok.string)
        if new_comment != tok.string:
            lines[line_idx] = line[:start_col] + new_comment + line[end_col:]

    new_text = "".join(lines)
    if new_text != text:
        py_path.write_text(new_text)
