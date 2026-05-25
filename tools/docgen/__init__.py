"""
Markdown variable substitution.

Syntax in markdown: [value](VARIABLE_NAME)
- The brackets hold the value — what renders when GitHub formats the link.
- The parens hold the variable name in UPPERCASE_WITH_UNDERSCORES — the
  "href" position. A real markdown link; the broken anchor doesn't matter.
- The variable name is literally in the markdown for any reader (agent or
  human) to see. The value is never authoritative; the script source is.

The substitute_md() function:
- Finds every [value](NAME) where NAME matches [A-Z_]+ in a markdown file.
- For each NAME in `variables`, rewrites the value to the current source
  value (str-cast).
- For each NAME in `expected_counts`, asserts the actual number of
  appearances equals the expected count.
- Leaves [value](NAME) patterns whose NAME isn't in `variables` untouched.
  This lets multiple scripts contribute substitutions to the same markdown —
  each call only manages its own names. The trade-off is that a typo
  `[X](BOGUS_NAME)` won't be caught by any individual call; it just sits
  there. If you need strict catching, the union of every caller's
  `variables` keys needs to cover every NAME in the markdown.

Normal markdown links (parens contain slashes, dots, colons, lowercase, etc.)
never match — only our all-caps-and-underscores variable references do.
"""

import re
from pathlib import Path
from typing import Any


# Matches a markdown link whose href is all-caps-and-underscores.
# Captures: 1 = value (bracket text), 2 = variable name (paren content).
_LINK_RE = re.compile(r"\[([^\]]*)\]\(([A-Z_]+)\)")


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
    if new_text != text:
        md_path.write_text(new_text)
