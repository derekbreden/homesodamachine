#!/usr/bin/env python3
"""Carry what the build cut into the tree that commits it.

    tools/cad-venv/bin/python tools/bazel/sync_tree.py            # what differs
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write    # and copy it in
    tools/cad-venv/bin/python tools/bazel/sync_tree.py selftest   # the carry, on fixtures

Bazel cuts into `bazel-bin/`, and this repo commits its solids and its docs, because a reader
at `/3d` and a shop printing a part both take them off the tree rather than off a build. So the
two live side by side: the build is what decides the bytes, and this is what hands them over.

WHAT DIFFERS IS THE READING. A tree that comes back with nothing to copy is a tree holding the
artifacts its sources make — asked here for the cost of a comparison, because the build ran.

AN OUTPUT IS SOMETIMES ALSO AN INPUT. Fifty-two `.md`, two `.mmd` charts, thirty-four
generators' own `.py` and the assembly cards are rewritten in place, so the copy a build hands
back carries whatever text that build was handed. THE BUILD DECIDES THE FIGURES IN SUCH A FILE
AND NOT ONE WORD AROUND THEM, so that is the whole of what this carries into one: its figures,
written into the text the tree holds now. A build that ran before an edit hands back nothing
that can reach the sentence — or the line of code — that edit wrote, and a tree whose figures
are the build's reads clean whether or not that build was handed its prose.
"""

import argparse
import filecmp
import io
import re
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

_HERE = Path(__file__).resolve()
_ROOT = _HERE.parents[2]


#: An output is `…/bin/out/<target>/<the path the tree keeps it under>`. The query answers with
#: every file of every target, and `//:node-packages` alone globs eleven thousand that are
#: inputs; this is what tells a declared output from one of those.
_DECLARED = re.compile(r"/bin/out/[^/]+/(.+)$")

#: THE FILES WHOSE TEXT IS THEIR OWN. `inventory.REWRITTEN_SUFFIXES` names every file a run
#: reads and writes back over; of those a `.figures.json` is cut whole and these four are not.
#: A word in one of them was typed by whoever typed it, and only its figures are the build's.
_AUTHORED = (".md", ".mmd", ".py", ".html")

#: `docgen`'s own marker, and the section `substitute_md` maintains at the end of every markdown
#: file it touches. Between them they are the whole of what a build writes into an authored
#: file, so between them they are the whole of what this hands over.
_LINK = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")
_SOURCES = re.compile(r"## Sources\n\[value\]\(NAME\) texts are updated by:\n"
                      r"(?:- `[^`\n]+`\n)+")


def _targets() -> dict:
    """`{bazel output path: tracked path}` — read off the BUILD file's own outs."""
    q = subprocess.run(["bazel", "cquery", "//...", "--output=files"],
                       cwd=str(_ROOT), capture_output=True, text=True)
    # A GRAPH THAT DOES NOT LOAD IS NOT A TREE THAT IS STALE. An unanswerable query and a
    # tree nobody has built for come back the same way — no outputs — and reporting the
    # second sends a reader to look at geometry when what failed was `BUILD.bazel`.
    if q.returncode != 0:
        first = next((ln for ln in q.stderr.splitlines() if ln.startswith("ERROR")), "")
        raise SystemExit(f"  the build graph does not load, so nothing here can be read\n"
                         f"  {first}")
    tracked = set(subprocess.run(["git", "-C", str(_ROOT), "ls-files"],
                                 capture_output=True, text=True, check=True).stdout.split())
    out, claimed = {}, {}
    for line in q.stdout.split():
        m = _DECLARED.search(line)
        if not m or m.group(1) not in tracked:
            continue
        hit = m.group(1)
        # TWO ACTIONS CUTTING ONE FILE is a graph that cannot be carried into a tree, because
        # the second copy decides and the first is lost. Named here rather than resolved.
        if hit in claimed:
            raise SystemExit(f"  {hit} is cut by two targets: {claimed[hit]} and {line}")
        claimed[hit] = line
        out[str(_ROOT / line)] = hit
    return out


def _managed(text: str, suffix: str, names=None) -> list:
    """The `(start, end)` slices of `text` a substituter rewrites markers inside.

    The three scopes `docgen` writes through, and no wider: a markdown file whole; a mermaid
    chart's `%%` comment lines alone, because a marker in a node or edge label would DRAW and
    `substitute_mmd` leaves it standing; a Python file's `#` comments plus any string that
    already carries one of `names`, which is how `substitute_py_comments` reaches a docstring
    without ever touching functional string data. `names=None` asks for every string instead,
    which is what reading a file's figures out of it wants — see `_figures`.

    A `.py` the tree holds mid-edit does not tokenize, and nothing is carried into a file this
    cannot read — the generator that owns it fails on the same text, and says so.
    """
    if suffix == ".md":
        return [(0, len(text))]

    starts, run = [], 0
    for line in text.splitlines(keepends=True):
        starts.append(run)
        run += len(line)

    if suffix == ".mmd":
        return [(at, at + len(line))
                for at, line in zip(starts, text.splitlines(keepends=True))
                if line.lstrip().startswith("%%")]

    spans = []
    try:
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.COMMENT or (
                    tok.type == tokenize.STRING
                    and (names is None
                         or any(m.group(2) in names for m in _LINK.finditer(tok.string)))):
                spans.append((starts[tok.start[0] - 1] + tok.start[1],
                              starts[tok.end[0] - 1] + tok.end[1]))
    except (tokenize.TokenError, SyntaxError, IndentationError, IndexError):
        return []
    return spans


def _figures(text: str, suffix: str) -> dict:
    """`{NAME: value}` for every marker standing in a scope a substituter writes.

    READ WHERE THE WRITE REACHES AND NO FURTHER. `[^\\]]*` crosses newlines, so a bare `[`
    typed in prose — `reservoir.py` opens a docstring with a literal `` `[` `` — runs on until
    some later `](NAME)` closes it, and swallows every line between as that name's value. One
    comment line and one string literal are each read alone, which is the length such a match
    can reach in a file `docgen` rewrites through comments and strings.
    """
    out = {}
    for start, end in _managed(text, suffix):
        for m in _LINK.finditer(text[start:end]):
            out[m.group(2)] = m.group(1)
    return out


_CARDGEN = None


def _cardgen():
    """`_cardgen`, whose `markers()` answers a card's `(name, value, start, end)`."""
    global _CARDGEN
    if _CARDGEN is None:
        sys.path.append(str(_ROOT / "hardware" / "assembly" / "cards"))
        import _cardgen as module
        _CARDGEN = module
    return _CARDGEN


def carried(built: str, tracked: str, suffix: str) -> str:
    """`tracked` holding the figures `built` decided, and nothing else that `built` holds.

    A NAME the build does not carry stays where it stands: a marker somebody has just typed is
    filled by the build that next reads the file, and by nothing before it.
    """
    # A CARD'S MARKER IS AN ELEMENT: `<td data-gen="BOX_SIZE">215 × 464 × 358 mm</td>`, whose
    # text is the figure. Every other word on the card is the card's, the way every sentence
    # around a `[value](NAME)` is the doc's.
    if suffix == ".html":
        cards = _cardgen()
        figures = {name: value for name, value, _s, _e in cards.markers(built)}
        out = tracked
        for name, value, start, end in sorted(cards.markers(tracked),
                                              key=lambda m: m[2], reverse=True):
            if name in figures and figures[name] != value:
                out = out[:start] + figures[name] + out[end:]
        return out

    figures = _figures(built, suffix)

    def fill(match: re.Match) -> str:
        name = match.group(2)
        return f"[{figures[name]}]({name})" if name in figures else match.group(0)

    # Highest offset down, so an earlier slice can never shift a span not yet rewritten.
    out = tracked
    for start, end in sorted(set(_managed(tracked, suffix, figures)), reverse=True):
        out = out[:start] + _LINK.sub(fill, out[start:end]) + out[end:]

    # THE SOURCES SECTION IS THE BUILD'S TOO. It lists one bullet per script that keeps the
    # file's markers, and `inventory._together` puts every such script in the one step that
    # cuts the file — so the built section is the whole list, and carrying it whole is
    # carrying what ran.
    if suffix == ".md":
        theirs, ours = _SOURCES.search(built), _SOURCES.search(out)
        if theirs and ours:
            out = out[:ours.start()] + theirs.group(0) + out[ours.end():]
        elif theirs:
            out = out.rstrip() + "\n\n" + theirs.group(0)
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="copy what differs into the tree")
    args = ap.parse_args()

    pairs = _targets()
    if not pairs:
        print("  nothing built — run `bazel build //...` first")
        return 1

    differs, missing = [], []
    for built, tracked in sorted(pairs.items()):
        b, t = Path(built), _ROOT / tracked
        if not b.is_file():
            missing.append(tracked)
        # WHAT DIFFERS IS WHAT A WRITE WOULD CHANGE — every byte of a solid, and of an authored
        # file its figures alone. One reading for both, so a tree that reports clean is a tree
        # `--write` would leave where it is.
        elif t.suffix in _AUTHORED and t.is_file():
            text = t.read_text()
            want = carried(b.read_text(), text, t.suffix)
            if want != text:
                differs.append((b, t, tracked, want))
        elif not t.is_file() or not filecmp.cmp(b, t, shallow=False):
            differs.append((b, t, tracked, None))

    for _b, _t, rel, _want in differs[:20]:
        print(f"  {rel}")
    if len(differs) > 20:
        print(f"  …and {len(differs) - 20} more")

    if args.write:
        for b, t, _rel, want in differs:
            if want is None:
                # THE BYTES AND NOT THE MODE. Bazel leaves an output read-only and executable,
                # and a copy that carries that over hands the tree a file its own generator
                # cannot rewrite and git a mode change nobody made. `copyfile` keeps the mode
                # the tree already has.
                shutil.copyfile(b, t)
            else:
                t.write_text(want)
        print(f"{len(differs)} carried into the tree")
    else:
        print(f"{len(pairs) - len(differs) - len(missing)}/{len(pairs)} artifacts in the tree "
              f"are the ones the build cut"
              + (f", {len(missing)} not built" if missing else ""))
    return 0 if not differs else 1


def selftest() -> int:
    """The carry, on a build that was handed older text than the tree holds."""
    def holds(got, want, what):
        if got != want:
            raise ValueError(f"{what}\n  carried: {got!r}\n  wanted:  {want!r}")

    sources = ("## Sources\n[value](NAME) texts are updated by:\n"
               "- `/hardware/assembly/_a_sync.py`\n")

    # A MARKDOWN DOC. The build was handed the old sentence; the tree holds the new one and the
    # old figure. What comes back is the new sentence at the build's figure.
    built = f"The wall stands off the pack.\n\nDepth is [473](APPLIANCE_D) mm.\n\n{sources}"
    tree = f"The wall is struck off the can.\n\nDepth is [464](APPLIANCE_D) mm.\n\n{sources}"
    holds(carried(built, tree, ".md"),
          f"The wall is struck off the can.\n\nDepth is [473](APPLIANCE_D) mm.\n\n{sources}",
          "a sentence the build was not handed reached the tree")

    # A SOURCES SECTION IS CARRIED WHOLE, so a script that has just started keeping a doc's
    # markers gets its bullet without anybody typing one.
    two = sources + "- `/hardware/assembly/_b_sync.py`\n"
    holds(carried(f"x\n\n{two}", f"x\n\n{sources}", ".md"), f"x\n\n{two}",
          "a new Sources bullet did not reach the tree")

    # AND APPENDED WHERE THE TREE HAS NONE.
    holds(carried(f"x\n\n{sources}", "x\n", ".md"), f"x\n\n{sources}",
          "a first Sources section did not reach the tree")

    # A NAME THE BUILD DOES NOT CARRY. Somebody typed the marker after the build ran; it waits
    # for the build that reads it rather than being filled with a value nothing decided.
    holds(carried("a\n", "a [?](NEW_ONE) b\n", ".md"), "a [?](NEW_ONE) b\n",
          "a marker the build never saw was written over")

    # A MERMAID CHART. The `%%` line is the build's; the node label draws literally, so a marker
    # standing in one is the chart's own and is left where it is.
    built = "%% span [10](SPAN) mm\nflowchart LR\n  A(( [10](SPAN) mm )) --> B\n"
    tree = "%% span [99](SPAN) mm\nflowchart LR\n  A(( [99](SPAN) mm )) --> B\n"
    holds(carried(built, tree, ".mmd"),
          "%% span [10](SPAN) mm\nflowchart LR\n  A(( [99](SPAN) mm )) --> B\n",
          "a mermaid label the renderer draws was rewritten")

    # A GENERATOR'S OWN .py. Its comment and its docstring carry figures; the line of code
    # beside them is the file's, and a build handed the old code hands back nothing that
    # reaches the new.
    built = ('"""Rib at [30](RIB_Z) mm."""\nWALL = 3.0  # [30](RIB_Z) over the floor\n'
             'LABEL = "rib [30](RIB_Z)"\nKEY = "RIB_Z"\n')
    tree = ('"""Rib at [99](RIB_Z) mm."""\nWALL = 2.4  # [99](RIB_Z) over the floor\n'
            'LABEL = "rib [99](RIB_Z)"\nKEY = "RIB_Z"\n')
    holds(carried(built, tree, ".py"),
          '"""Rib at [30](RIB_Z) mm."""\nWALL = 2.4  # [30](RIB_Z) over the floor\n'
          'LABEL = "rib [30](RIB_Z)"\nKEY = "RIB_Z"\n',
          "a .py the build was not handed came back over the tree's own")

    # A BARE `[` TYPED IN PROSE. `reservoir.py` opens a docstring with a literal `` `[` ``, and
    # `[^\]]*` crosses newlines — read any wider than one comment and one literal and that
    # bracket runs on to the next `](NAME)` and takes every line between as its value.
    built = '"""A `[`-shaped body."""\nWALL = 3.0  # rib at [30](RIB_Z)\n'
    tree = '"""A `[`-shaped body."""\nWALL = 2.4  # rib at [99](RIB_Z)\n'
    holds(carried(built, tree, ".py"),
          '"""A `[`-shaped body."""\nWALL = 2.4  # rib at [30](RIB_Z)\n',
          "a bare `[` in prose swallowed the lines down to the next marker")

    # A .py MID-EDIT does not tokenize, and nothing is carried into a file this cannot read.
    broken = 'WALL = (  # [99](RIB_Z)\n'
    holds(carried(built, broken, ".py"), broken, "a file that does not parse was written into")

    # A CARD. The figure sits in the element's text; the sentence beside it is the card's, and
    # an element the build does not carry keeps the text it has.
    built = ('<p>Stage the four pieces.</p>\n'
             '<td class="v" data-gen="BOX_SIZE">215 &#215; 464 &#215; 358 mm</td>\n'
             '<span class="dim" data-gen="LATER">7</span>\n')
    tree = ('<p>Stage the four pieces on the bench, gasket up.</p>\n'
            '<td class="v" data-gen="BOX_SIZE">215 &#215; 462 &#215; 358 mm</td>\n'
            '<span class="dim" data-gen="NEW_ONE">?</span>\n')
    holds(carried(built, tree, ".html"),
          '<p>Stage the four pieces on the bench, gasket up.</p>\n'
          '<td class="v" data-gen="BOX_SIZE">215 &#215; 464 &#215; 358 mm</td>\n'
          '<span class="dim" data-gen="NEW_ONE">?</span>\n',
          "a card's own sentence or an uncarried figure moved")

    # IDEMPOTENT, so what `--write` changes is what the reading without it named.
    once = carried(built, tree, ".py")
    holds(carried(built, once, ".py"), once, "a second carry moved the file again")

    print("  sync_tree selftest: 10 holds, the build's figures and the tree's own text")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(main())
