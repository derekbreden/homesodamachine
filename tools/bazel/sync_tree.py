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

AN OUTPUT IS SOMETIMES ALSO AN INPUT. Two hundred and five files are read and written back
over, and `graph.json` names them because the writers do — so the copy a build hands one of
them back carries whatever text that build was handed. THE BUILD DECIDES THE FIGURES IN SUCH A
FILE AND NOT ONE WORD AROUND THEM, so that is the whole of what this carries into one: its
figures, written into the text the tree holds now. A build that ran before an edit hands back
nothing that can reach the sentence — or the line of code — that edit wrote, and a tree whose
figures are the build's reads clean whether or not that build was handed its prose.
"""

import argparse
import filecmp
import io
import json
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

#: HOW A REWRITTEN MEDIUM IS CARRIED. `_SPLICE` names the four whose text is partly their own,
#: each with a scope a substituter writes in and everything outside it authored; `_WHOLE` names
#: the two a writer composes every byte of — a `.figures.json` holds figures and nothing a
#: person typed, and a card's `.png` is a photograph of a page, drawn whole by the run that
#: names it on both sides of its step so a picture that has not moved is not redrawn.
#:
#: WHICH FILES ARE REWRITTEN IS `graph.json`'s `rewritten` and not these. A suffix answers how
#: to carry a medium — the mechanisms differ per medium and no writer reports one — and cannot
#: answer whether a file was rewritten at all. That second question is the one whose wrong
#: answer destroys: a medium missing from a list, copied whole, lands a stale build's text over
#: a sentence somebody wrote. A rewritten medium in neither list is named and left alone.
_SPLICE = (".md", ".mmd", ".py", ".html")
_WHOLE = (".json", ".png")

#: `docgen`'s own marker, and the section `substitute_md` maintains at the end of every markdown
#: file it touches. Between them they are the whole of what a build writes into an authored
#: file, so between them they are the whole of what this hands over.
_LINK = re.compile(r"\[([^\]]*)\]\(([A-Z_][A-Z0-9_]*)\)")
_SOURCES = re.compile(r"## Sources\n\[value\]\(NAME\) texts are updated by:\n"
                      r"(?:- `[^`\n]+`\n)+")


def _rewritten() -> set:
    """Every file a run read and wrote back over, as the writers recorded it.

    `docgen` and `_cardgen` note each target they maintain; `trace_inputs` keeps that beside
    the writes, and `inventory` sorts the docs from the solids by it. A reading taken without
    it cannot tell a doc from a STEP — 102 solids stand in both the reads and the writes of
    their own run, because `_atomic_write` opens the target to compare before it renames.
    """
    try:
        graph = json.loads((_HERE.parent / "graph.json").read_text())
    except (OSError, ValueError) as exc:
        raise SystemExit(f"  no build graph to read, so which files are rewritten in place is\n"
                         f"  unknown, and copying one whole lands a build's text over an\n"
                         f"  author's: {exc}")
    return {f for seen in graph.values() for f in seen.get("rewritten", ())}


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
    ap.add_argument("--failed", default="", metavar="TARGET[,TARGET…]",
                    help="targets that failed this run; their outputs are not carried")
    args = ap.parse_args()
    failed = {t.strip().lstrip("/").lstrip(":") for t in args.failed.split(",") if t.strip()}

    # A BUILD THAT DID NOT FINISH LEAVES THE LAST ONE'S OUTPUTS STANDING. Bazel keeps what a
    # target cut the last time it succeeded, so a failed build's `bazel-bin` is a mix of what
    # this run made and what some earlier run made — and carrying that into the tree writes
    # stale bytes over files somebody just got right. Which is not a wrong reading to fix
    # later: it is the one move here that cannot be taken back.
    #
    # `--check_up_to_date` answers whether every output is the one its declared inputs make,
    # runs no action, and costs a graph read. Only `--write` is held: reporting what differs
    # against a half-built tree is still worth reading, and it changes nothing.
    if args.write:
        q = subprocess.run(["bazel", "build", "--check_up_to_date", "//:everything"],
                           cwd=str(_ROOT), capture_output=True, text=True)
        owed = [ln for ln in q.stderr.splitlines() if "not up-to-date" in ln]
        # THE WORKSPACE STATUS ACTION IS NEVER UP TO DATE AND NEVER CAN BE. Bazel re-runs
        # `BazelWorkspaceStatusAction` on every invocation because it is what captures the
        # volatile facts a build could stamp, so `--check_up_to_date` names it whether or not
        # anything else moved. It writes `stable-status.txt` and nothing in `graph.json`
        # declares it, so it is not a file this carries and its staleness says nothing about
        # the outputs that are. Held out by name, and everything else still refuses.
        stale = [ln for ln in owed if "BazelWorkspaceStatusAction" not in ln]
        # AND A NON-ZERO EXIT THAT NAMED NOTHING IS STILL A REFUSAL. `--check_up_to_date` runs
        # no action, so a failure carrying no `not up-to-date` line is bazel unable to answer —
        # a broken graph, a missing input — which is not permission to carry.
        if q.returncode != 0 and (stale or not owed):
            print("  the build is not up to date, so what is in bazel-bin is not what these\n"
                  "  sources make — carrying it into the tree would write stale bytes over\n"
                  "  whatever is there. Run `bazel build //:everything` first.")
            for ln in (stale or owed)[:5]:
                print(f"  {ln.strip()}")
            if len(stale or owed) > 5:
                print(f"  …and {len(stale or owed) - 5} more")
            return 1

    pairs = _targets()
    if not pairs:
        print("  nothing built — run `bazel build //...` first")
        return 1

    # A TARGET THAT FAILED THIS RUN STILL HAS THE OUTPUTS OF THE LAST RUN THAT DID NOT. Bazel
    # keeps those, and `--check_up_to_date` answers about inputs rather than about whether an
    # action ran, so it calls them current — a red build reads up to date and its stale bytes
    # are carryable. The path names the target it came from (`/bin/out/<target>/…`), so what
    # is held back is those outputs and nothing else: every green target still owes its own.
    if failed:
        held = {b: t for b, t in pairs.items()
                if (m := re.search(r"/bin/out/([^/]+)/", b)) and m.group(1) in failed}
        pairs = {b: t for b, t in pairs.items() if b not in held}
        print(f"  {len(held)} output(s) held back, cut by {len(failed)} target(s) that failed "
              f"this run: {', '.join(sorted(failed))}")

    back = _rewritten()
    differs, missing, unknown = [], [], []
    for built, tracked in sorted(pairs.items()):
        b, t = Path(built), _ROOT / tracked
        spliceable = tracked in back and t.suffix in _SPLICE
        if not b.is_file():
            missing.append(tracked)
        # A MEDIUM READ BACK OVER THAT NOTHING HERE CAN SPLICE is left where it stands. The
        # copy that would replace it holds the text the build was handed, and handing that to
        # the tree is the one move this cannot take back.
        elif tracked in back and not spliceable and t.suffix not in _WHOLE:
            unknown.append(tracked)
        # WHAT DIFFERS IS WHAT A WRITE WOULD CHANGE — every byte of a solid, and of a spliceable
        # file its figures alone. One reading for both, so a tree that reports clean is a tree
        # `--write` would leave where it is.
        elif spliceable and t.is_file():
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
    for rel in unknown:
        print(f"  {rel} is read back over and {Path(rel).suffix} has no splice here — left "
              f"alone rather than carried whole")

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
        # AND CARRYING IS NOT A FAULT. `differs` is the work this mode exists to do, so by the
        # line above it is the work DONE. Sharing `--check`'s exit with it meant `--write`
        # could only ever report success on a run with nothing to carry: derive 32480943980
        # moved 53 files and came back 1, and `derive.yml` reads that as
        # `sync_tree carried nothing` and warns that every step below it read the fetch.
        # What is left undone is `unknown` — read back over, no splice for its suffix, still
        # standing where the tree had it — and that is the only thing here a caller cannot see
        # from the count.
        return 0 if not unknown else 1
    print(f"{len(pairs) - len(differs) - len(missing) - len(unknown)}/{len(pairs)} artifacts "
          f"in the tree are the ones the build cut"
          + (f", {len(missing)} not built" if missing else "")
          + (f", {len(unknown)} with no splice" if unknown else ""))
    # A CARRY THAT HAPPENED IS NOT A DIFFERENCE THAT REMAINS. `differs` is what the tree was
    # missing when the comparison ran; under `--write` those files have just been written into
    # it, so the tree now holds what the build cut. What is still owed either way is `unknown`
    # — a rewritten medium with no carry in the table, which nothing here can hand over.
    return 0 if not unknown and (args.write or not differs) else 1


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

    # EVERY MEDIUM THE WRITERS READ BACK OVER HAS A CARRY HERE. A `.rst` in `rewritten` and in
    # neither list is a file `--write` would copy whole, over text nobody generated.
    from collections import Counter
    kinds = Counter(Path(f).suffix for f in _rewritten())
    astray = sorted(k for k in kinds if k not in _SPLICE and k not in _WHOLE)
    if astray:
        raise ValueError(f"read back over and carried by nothing here: "
                         f"{', '.join(f'{k} ({kinds[k]})' for k in astray)}")

    print(f"  sync_tree selftest: 11 holds, the build's figures and the tree's own text; "
          f"{sum(kinds.values())} files read back over, every medium carried")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        raise SystemExit(selftest())
    raise SystemExit(main())
