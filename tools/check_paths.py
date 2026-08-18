#!/usr/bin/env python3
"""check_paths.py — whether every path this tree names is a path something holds.

    python3 tools/check_paths.py            (0 = every reference lands, 1 = one does not)
    python3 tools/check_paths.py selftest   (the rules below, held against fixtures)

Every other check here guards a NUMBER or a RECORD: `check_pinmap` the pin assignments,
`_bom_totals` the sums, `check_tracked` the sidecar beside each artifact, `check_step_colours`
the material. This one guards the PATH — the other half of what a doc says, and the half that
a rename breaks silently. A figure that drifts is caught by the script that derives it. A link
that rots is caught by nobody, because nothing derives a link.

WHERE A PATH RESOLVES IS THREE PLACES, NOT ONE.

  1. The index. `git ls-files`, the same reading `check_tracked` takes: a file the index does
     not hold is a file a fresh clone does not have.

  2. The solids manifest. `hardware/cad-artifacts.lock.json` names 103 solids that are FETCHED
     AND NOT COMMITTED (`tools/cad-artifacts/pack.py`, `web/scripts/fetch-cad-artifacts.mjs`).
     178 `.step` files sit on this disk and 3 are in the index; resolving against the index
     alone calls the other 175 broken, and `foam-shell.step` — absent from the index, present
     in the lock — is the case that proves it. The lock is as much a record of what the tree
     holds as the index is.

  3. A TAG, WHEN THE REFERENCE NAMES ONE. A path deleted here is not dropped: a tag is cut at
     the commit that still holds it and the reference stays, naming the tag —

         the artifacts are preserved at the `archive-plan-b` git tag   (bom.md)
         its print log and its `.3mf` stand at the `archive-water-test-cup` tag
         archive-blog:posts/2026-05-18-2352.md                         (the gitrevision form)
         --at-b archive-plan-b                                         (as a tool's argument)

     So a path that fails at HEAD is not yet wrong. It is wrong when it fails at HEAD AND at
     every ref named beside it — and it is wrong in the worse way when the tag it names does
     not hold what it promises, because that reference reads as an assurance the thing was
     kept. `archive-water-test-cup` keeps its promise: the cup, its print log and its `.3mf`
     all stand there. Nothing but this checked.

A reference is read in the block that carries it — a markdown paragraph, a run of comment
lines — because that is the span the tag is written in. `--at-b archive-plan-b` sits three
lines under the STEP it pins, and a line-scoped reader would not see it.

WHAT IS NOT A LINK. Four dialects live in this tree and each would drown the answer:

  - `[11](VALVE_COUNT)` is a docgen substitution, not a link — 1,870 of them, against 1,811
    real links. The shape is docgen's own `_LINK_RE`, imported rather than guessed at, and
    the `## Sources` preamble is cut the way `substitute_md` cuts it.
  - `#include "images/anim_00.h"` is relative to the .cpp that writes it, not to the root.
  - `hardware/foo/bar/foo_bar.py`, `path/to/drawing.svg`, `web/.../pcb-pick.js` are ways of
    writing "a path", not paths.
  - `hardware/printed-parts/cap/cap.step` in `pack.py` is BUILT, not referenced: a selftest
    lays a fake tree in a tmpdir and names the files it wrote. A path a selftest constructs
    is a fixture, and the tree it lives in is thrown away.

Filenames here carry spaces — `calibration/sessions/Comments are a code smell.md` is a real
file — so `git ls-files` is read on NEWLINES. Splitting it on whitespace drops every such
file, and a scan that drops files reports clean.
"""

import bisect
import itertools
import json
import re
from functools import lru_cache
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from docgen import _LINK_RE as _DOCGEN_MARKER_RE, _SOURCES_SECTION_RE

ROOT = Path(__file__).resolve().parents[1]

SOURCE_SUFFIXES = (".py", ".cpp", ".c", ".h", ".hpp", ".js", ".mjs", ".ts", ".tsx",
                   ".sh", ".swift", ".kt", ".mmd")

MD_LINK_RE = re.compile(r"(?<!\!)\[([^\]]*)\]\(([^)]+)\)")

# A path a comment names: at least one slash, ending in a file kind we know. No root prefix
# is demanded, because the root a comment writes from is not fixed — see the readings below.
SOURCE_PATH_RE = re.compile(r"(?<![\w./-])(/?[A-Za-z0-9_][A-Za-z0-9_.-]*(?:/[A-Za-z0-9_.-]+)+)")

# A ref named beside a path: `archive-plan-b`, --at-b archive-plan-b, or the gitrevision
# form archive-blog:posts/…. Only the archive/superseded/last-known families — a bare word
# is not a ref, and `main` or a version tag beside a path is not an archive claim.
REF_WORD_RE = re.compile(r"(?<![\w/-])((?:archive|superseded|pattern)[\w./-]*|[\w.-]*-last-known)(?![\w-])")
REVISION_RE = re.compile(r"(?<![\w/:-])([\w.][\w./-]*):([\w][\w./-]*\.[\w]+|[\w][\w./-]*/)(?![\w/-])")

# THE DOMINANT ARCHIVE FORM IN THIS TREE. A path that HEAD no longer has is written as a
# blob URL pinned to the commit that still holds it —
#   https://github.com/<owner>/<repo>/blob/<sha>/hardware/…/scorecard.py#L472
# — and the sha is the whole point of it. A pin at a sha where the path is not actually
# there reads as a working citation and is not one, so the sha is asked.
BLOB_URL_RE = re.compile(
    r"https://github\.com/[\w.-]+/[\w.-]+/blob/([0-9a-f]{7,40})/([^)\s#\"'<>]+)")

# Ways of writing "a path" that are not paths.
SHA_RE = re.compile(r"(?<![\w/])([0-9a-f]{8,40})(?![\w/])")

PLACEHOLDER_SEGMENTS = {"foo", "bar", "baz", "qux", "path", "to", "NAME", "name",
                        "<board>", "<name>", "<dir>", "<n>", "a", "b", "x", "y"}
PLACEHOLDER_MARKS = ("...", "*", "{", "}", "$", "%s", "XX", "NN", "_N.")

# A LEADING SLASH IS NOT ALWAYS THIS REPO. `/tmp/foam-shell.png` is where a render tool
# writes, `/Users/…` is one machine's disk, and `/css/viewer.css` is a route the site
# serves. None of them is a claim about a file in this tree.
SYSTEM_ROOTS = {"tmp", "Users", "home", "opt", "usr", "var", "private", "etc", "dev",
                "mnt", "proc", "root", "srv", "sys", "bin", "sbin", "lib", "Volumes"}

SKIP_TREES = ("node_modules/", "tools/cad-venv/", "tools/pcb-venv/", "tools/video-venv/",
              ".pio/", "bazel-", "calibration/sessions/")

# A SOURCE COMMENT MUST NAME A FILE KIND for its path to be read as a path. `the infill
# pattern/density` and `the marketing/communication` are English, and `_materials.one_body`
# is a module and a function. A markdown link is exempt: `[the ledger](/hardware/ledger/)`
# points at a directory and is still a link a reader clicks.
KNOWN_SUFFIXES = (".md", ".py", ".js", ".mjs", ".ts", ".tsx", ".json", ".cpp", ".c", ".h",
                  ".hpp", ".sh", ".swift", ".kt", ".mmd", ".step", ".stl", ".3mf", ".dxf",
                  ".svg", ".png", ".jpg", ".jpeg", ".glb", ".pdf", ".csv", ".html", ".css",
                  ".yaml", ".yml", ".xml", ".ini", ".toml", ".lock", ".txt", ".bazel", ".tsv")


def _git(*args: str) -> str:
    return subprocess.run(["git", "-C", str(ROOT), *args],
                          capture_output=True, text=True, check=False).stdout


def _tracked() -> tuple[set, set]:
    """The index, and every directory the index implies. Read on NEWLINES (spaces in names)."""
    files = {ln for ln in _git("ls-files").split("\n") if ln}
    dirs = set()
    for f in files:
        p = Path(f).parent
        while str(p) != ".":
            dirs.add(str(p))
            p = p.parent
    return files, dirs


def _lock_solids() -> set:
    """The solids the lock names — fetched at deploy, never committed, and just as held."""
    lock = ROOT / "hardware" / "cad-artifacts.lock.json"
    if not lock.is_file():
        return set()
    try:
        return set(json.loads(lock.read_text()).get("solids", {}))
    except (OSError, ValueError):
        return set()


def _tags() -> set:
    return {ln for ln in _git("tag", "-l").split("\n") if ln}


@lru_cache(maxsize=None)
def _is_commit(ref: str) -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"],
                       capture_output=True, text=True, check=False)
    return r.returncode == 0


@lru_cache(maxsize=None)
def _resolves_at(ref: str, path: str) -> bool:
    r = subprocess.run(["git", "-C", str(ROOT), "cat-file", "-e", f"{ref}:{path}"],
                       capture_output=True, text=True, check=False)
    return r.returncode == 0


def _is_placeholder(path: str) -> bool:
    """Whether this is a way of writing "a path" rather than a path.

    `<board>` IS A WHOLE SEGMENT and stands for one. A stray angle bracket INSIDE a segment
    is a malformed link — `sessions/<Comments are a code smell.md>` has its brackets on the
    wrong side of the directory — and that is a finding, not an exemption.
    """
    if any(m in path for m in PLACEHOLDER_MARKS):
        return True
    segs = path.split("/")
    if any(s.startswith("<") and s.endswith(">") and not s.endswith(KNOWN_SUFFIXES + (">",))
           for s in segs):
        return True
    if any(s.startswith("<") and s.endswith(">") and len(s.split()) == 1
           and not s[1:-1].endswith(KNOWN_SUFFIXES) for s in segs):
        return True
    return any(s in PLACEHOLDER_SEGMENTS for s in segs)


def _line_index(text: str) -> list:
    """Offsets of every newline, so a match's line is a bisect and not a re-count.

    `text[:m.start()].count("\n")` walks the whole prefix for EVERY match, which on an
    80 KB transcript with hundreds of links is the scan's whole cost.
    """
    # accumulate over line lengths, not a step per character: the newline before line n+1
    # sits at (sum of the first n line lengths) + n.
    return list(itertools.accumulate((len(ln) + 1 for ln in text.split("\n")), initial=-1))[1:]


def _line_of(index: list, pos: int) -> int:
    return bisect.bisect_right(index, pos) + 1


def _strip_fences(text: str) -> str:
    """Blank every fenced block, keeping line numbers. A path in a fence is an illustration."""
    out, fenced = [], False
    for line in text.split("\n"):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            out.append("")
            continue
        out.append("" if fenced else line)
    return "\n".join(out)


def _blocks(text: str) -> list[tuple[int, str]]:
    """(start_line, text) for each block — a markdown paragraph or a run of comment lines.

    THE BLOCK IS THE SPAN A TAG IS WRITTEN IN. `--at-b archive-plan-b` sits three lines under
    the STEP it pins, so a reference read one line at a time cannot see what qualifies it.
    """
    out, cur, start = [], [], 1
    for i, line in enumerate(text.split("\n"), 1):
        if line.strip():
            if not cur:
                start = i
            cur.append(line)
        elif cur:
            out.append((start, "\n".join(cur)))
            cur = []
    if cur:
        out.append((start, "\n".join(cur)))
    return out


def _md_targets(text: str) -> list[tuple[int, str]]:
    """(line, target) for every real link in a markdown body.

    Docgen markers are cut two ways, both of them docgen's own: the `## Sources` preamble
    reads `[value](NAME) texts are updated by:` and matches like any link, and a marker's
    target is `_LINK_RE`'s shape. `substitute_md` cuts both for the same reason.
    """
    sources = _SOURCES_SECTION_RE.search(text)
    body = _strip_fences(text[:sources.start()] if sources else text)
    matches = list(MD_LINK_RE.finditer(body))
    if not matches:
        return []
    idx, out = _line_index(body), []
    for m in matches:
        target = m.group(2).strip()
        if target.startswith("<") and target.endswith(">"):
            target = target[1:-1]
        if target.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
            continue
        if _DOCGEN_MARKER_RE.fullmatch(m.group(0)):
            continue
        out.append((_line_of(idx, m.start()), target))
    return out


_SCAN_C = re.compile(r'''"(?:[^"\\\\]|\\\\.)*"?|'(?:[^'\\\\]|\\\\.)*'?|`(?:[^`\\\\]|\\\\.)*`?|//|/\\*''')
_SCAN_HASH = re.compile(r'''"(?:[^"\\\\]|\\\\.)*"?|'(?:[^'\\\\]|\\\\.)*'?|#''')
_SCAN_PCT = re.compile(r'''"(?:[^"\\\\]|\\\\.)*"?|'(?:[^'\\\\]|\\\\.)*'?|%%''')


def _outside_strings(line: str, marks: tuple) -> int:
    """Index of the first `marks` token that is NOT inside a string literal, or -1.

    `"https://…"` carries a `//` and `"/*"` carries a block open; a scanner that finds them
    by `str.find` reads the rest of the file as commentary and every string in it as prose.

    ONE REGEX PASS, NOT ONE PYTHON STEP PER CHARACTER. The alternation eats whole string
    literals first, so any mark it returns is one no string covered — and the walk happens
    in the regex engine rather than in a loop over 58 million `startswith` calls.
    """
    scan = _SCAN_HASH if marks == ("#",) else (_SCAN_PCT if marks == ("%%",) else _SCAN_C)
    for m in scan.finditer(line):
        if m.group(0) in marks:
            return m.start()
    return -1


def _comment_spans(rel: str, text: str) -> str:
    """`text` with everything that is not a comment or a docstring blanked out.

    A PATH IN A STRING LITERAL IS NOT A REFERENCE TO THIS TREE. `"/logs/system.log"` is a
    LittleFS path on the device, `"tools/call"` is a JSON-RPC method, and the `_a_sync.py`
    in `sync_tree.py`'s help text is a name it prints, not a file it names. docgen's
    `substitute_py_comments` refuses string literals for exactly this reason.

    Docstrings ARE read: `beduan_solenoid.py` names the BOM in its module docstring, and a
    docstring is where this tree says what a part is.
    """
    lines = text.split("\n")
    keep = [""] * len(lines)
    if rel.endswith(".py"):
        import ast, io, tokenize
        try:
            for tok in tokenize.generate_tokens(io.StringIO(text).readline):
                if tok.type == tokenize.COMMENT:
                    keep[tok.start[0] - 1] = tok.string
        except (tokenize.TokenError, IndentationError, SyntaxError):
            pass
        try:
            tree = ast.parse(text)
            nodes = [tree] + [n for n in ast.walk(tree)
                              if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))]
            for n in nodes:
                doc = ast.get_docstring(n, clean=False)
                if not doc:
                    continue
                body0 = n.body[0]
                for i, dl in enumerate(doc.split("\n")):
                    idx = body0.lineno - 1 + i
                    if 0 <= idx < len(keep):
                        keep[idx] = dl
        except (SyntaxError, ValueError):
            pass
        return "\n".join(keep)

    if rel.endswith((".sh", ".mmd")):
        mark = "%%" if rel.endswith(".mmd") else "#"
        for i, line in enumerate(lines):
            j = _outside_strings(line, (mark,))
            keep[i] = line[j:] if j >= 0 else ""
        return "\n".join(keep)

    in_block = False
    for i, line in enumerate(lines):
        if in_block:
            end = line.find("*/")
            keep[i] = line if end < 0 else line[:end]
            in_block = end < 0
            continue
        j = _outside_strings(line, ("//", "/*"))
        if j < 0:
            continue
        keep[i] = line[j:]
        if line.startswith("/*", j):
            in_block = "*/" not in line[j:]
    return "\n".join(keep)


def _source_targets(rel: str, text: str, topdirs: set) -> list[tuple[int, str]]:
    """(line, target) for every repo path a source file's COMMENTS name."""
    body = _comment_spans(rel, text)
    matches = list(SOURCE_PATH_RE.finditer(body))
    if not matches:
        return []
    idx, out = _line_index(body), []
    for m in matches:
        # A PATH THAT ENDS A SENTENCE ENDS WITH THE SENTENCE. `see hardware/a.md.` carries
        # a full stop the regex is happy to eat, and the file kind is then `.md.` — which
        # matches nothing, so the reference is dropped instead of read.
        target = m.group(1).rstrip(".,;:)\"'`")
        if target.endswith(KNOWN_SUFFIXES):
            out.append((_line_of(idx, m.start()), target))
    return out


def _clean(target: str) -> str:
    """A link's payload: no fragment, no query, no `:36` line suffix, no trailing punctuation."""
    p = target.split("#")[0].split("?")[0]
    return re.sub(r":\d+(?:-\d+)?$", "", p).rstrip(".,;:)\"'`")


def check(files: set, dirs: set, solids: set, tags: set) -> list[str]:
    """Every reference this tree makes, and the ones that land nowhere."""
    bad = []
    topdirs = {d for d in (p.split("/")[0] for p in files) if "." not in d}
    held = files | dirs | solids

    # THIS FILE IS THE NOTATION, NOT A USE OF IT. Every rule above is written down beside
    # the case that earned it — `images/anim_00.h`, `hardware/a.md`, a tag family's prefix —
    # so a scan of this file reports the examples as though something meant them. Nothing
    # does. `docgen.lint` skips `NAME` for the same reason and says so in the same breath.
    for rel in sorted(f for f in files
                      if f.endswith((".md",) + SOURCE_SUFFIXES)
                      and not f.startswith(SKIP_TREES)
                      and f != "tools/check_paths.py"):
        try:
            text = (ROOT / rel).read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue

        is_md = rel.endswith(".md")
        body = _strip_fences(text)
        targets = _md_targets(text) if is_md else _source_targets(rel, text, topdirs)
        if not targets:
            continue
        blocks = _blocks(body)
        bidx = None

        # A NAMED TAG THAT DOES NOT EXIST is a promise with nothing behind it, and it is
        # wrong whether or not the path beside it happens to land.
        for m in REF_WORD_RE.finditer(body):
            word = m.group(1).rstrip(".,;:")
            # `the infill pattern/density` is English. Only the families that cannot be
            # anything but a tag are reported missing; a `pattern/` ref counts when known.
            if word.startswith(("archive-", "superseded-")) or word.endswith("-last-known"):
                if word not in tags:
                    bidx = _line_index(body) if bidx is None else bidx
                    line = _line_of(bidx, m.start())
                    bad.append(f"{rel}:{line} — `{word}` is named as a tag; no such tag")

        for line, target in targets:
            path = _clean(target)
            if not path or _is_placeholder(path):
                continue

            # A MARKDOWN LINK IS RESOLVED BY A RENDERER, AND A COMMENT IS READ BY A PERSON.
            # So they are asked differently. `[x](web/README.md)` in a doc under
            # calibration/traffic/ is `calibration/traffic/web/README.md` to GitHub and to
            # the site — file-relative, one reading, no second chance, because that is the
            # link a reader actually clicks. A comment naming `hardware/pcb/pcba/pick-data.ts`
            # means the one at the root, and one naming `images/anim_00.h` means the sibling;
            # both are asked, and the root reading is what gets reported.
            if path.startswith("/"):
                cands = [str(Path(path.lstrip("/")))]
            elif is_md:
                cands = [str(Path(rel).parent / path)]
            else:
                # THREE ROOTS A COMMENT CAN BE WRITING FROM, and any of them landing is
                # enough. The repo root (`hardware/pcb/pcba/pick-data.ts` in web/lib).
                # The file's own directory (`images/anim_00.h` in a .cpp). And the file's
                # own TOP-LEVEL directory — `printed-parts/…/foo.step` inside hardware/ is
                # what "STEP paths are relative to hardware/" means, and `scripts/fetch.mjs`
                # inside web/ is the command as run from web/. One rule, both conventions.
                root_rel = str(Path(path))
                sib = str(Path(rel).parent / path)
                top = str(Path(rel.split("/")[0]) / path)
                hw = str(Path("hardware") / path)   # the path space /api/steps serves
                cands = [root_rel, sib, top, hw] if root_rel.split("/")[0] in topdirs \
                    else [top, sib, hw, root_rel]
            if any(c in held or (ROOT / c).exists() for c in cands):
                continue
            # REPORT THE READING THAT GOT CLOSEST. Of the roots a path could be written
            # from, the one whose PARENT directory exists is the one the writer meant;
            # naming any other sends the reader to a tree that was never in question.
            cand = next((c for c in cands if str(Path(c).parent) in held), cands[0])


            # Not at HEAD. Before it is wrong, ask every ref named in its own block.
            block = next((b for st, b in reversed(blocks) if st <= line), "")
            refs = {w.rstrip(".,;:`") for w in REF_WORD_RE.findall(block)} & tags
            refs |= {h for h in SHA_RE.findall(block) if _is_commit(h)}
            if any(_resolves_at(r, c) for r in refs for c in cands):
                continue
            # A tag reaches a tree HEAD does not have, so the reading that got closest is
            # the one whose parent stands AT THE TAG — `hardware/printed-parts/plan-b/` is
            # gone from HEAD and there at `archive-plan-b`.
            for r in sorted(refs):
                near = next((c for c in cands if _resolves_at(r, str(Path(c).parent))), None)
                if near:
                    cand = near
                    break

            # A COMMENT IS ONLY HELD TO A PATH IT PLAINLY MEANT. Comments here write from
            # several roots — the repo, their own directory, their top-level tree, and the
            # hardware/ space /api/steps serves — and `viewer/cards.js` or `css/viewer.css`
            # is a reader's shorthand, not a claim about the root. So a comment is reported
            # on two grounds only: it anchored the path itself (a leading `/`, or a
            # top-level directory it could not have meant relatively), or it named a TAG
            # beside it — and naming a tag is an explicit claim that the path stands there.
            if not is_md:
                head = path.lstrip("/").split("/")[0]
                if head in SYSTEM_ROOTS:
                    continue
                if head not in topdirs and not refs:
                    continue
            if refs:
                named = ", ".join(sorted(refs))
                bad.append(f"{rel}:{line} — {cand} is not at HEAD, and not at {named} either")
            else:
                bad.append(f"{rel}:{line} — {cand} is held nowhere, and no tag is named for it")

        # A blob URL carries its commit in the URL. The sha has to be one this clone has
        # before the path can be asked of it — a pin at a commit nobody fetched is its own
        # kind of dead reference.
        for m in BLOB_URL_RE.finditer(body):
            sha, path = m.group(1), m.group(2)
            line = body[:m.start()].count("\n") + 1
            # A SHA THIS CLONE DOES NOT HAVE IS NOT ANSWERABLE HERE. The history was
            # rewritten (`calibration/traffic/CO2 white.md`, "44/44 tags now inside the new
            # history … restored them from the mirror at their rewritten SHAs"), so every
            # pin taken before that names a commit this repo dropped. Whether GitHub still
            # serves it is a question about the remote, not about this tree, and a check
            # that cannot answer a question does not get to fail it.
            if not _is_commit(sha):
                continue
            if not _resolves_at(sha, path):
                bad.append(f"{rel}:{line} — {path} is not at {sha}, which its blob URL pins it to")

        # The gitrevision form, `archive-blog:posts/…`, carries its own ref.
        for m in REVISION_RE.finditer(body):
            ref, path = m.group(1), m.group(2).rstrip("/")
            if ref not in tags or _is_placeholder(path):
                continue
            if not _resolves_at(ref, path):
                bidx = _line_index(body) if bidx is None else bidx
                line = _line_of(bidx, m.start())
                bad.append(f"{rel}:{line} — {ref}:{path} does not resolve at that tag")
    return bad


def _selftest() -> int:
    """The rules above, each held against the case that made it a rule."""
    fails = []

    def hold(name, got, want):
        if got != want:
            fails.append(f"  {name}\n     got  {got!r}\n     want {want!r}")

    # A docgen marker is not a link, and the Sources preamble is not one either.
    hold("docgen marker is not a link",
         _md_targets("Eleven [11](VALVE_COUNT) valves, see [bom](/hardware/ledger/bom.md)."),
         [(1, "/hardware/ledger/bom.md")])
    hold("a fenced path is an illustration",
         _md_targets("```\n[x](/nope.md)\n```\n[y](/hardware/README.md)"),
         [(4, "/hardware/README.md")])
    hold("angle-bracketed target unwraps",
         _md_targets("[a](</hardware/ledger/bom.md>)"), [(1, "/hardware/ledger/bom.md")])

    # A line suffix is part of the reference, not part of the path.
    hold("line suffix stripped", _clean("/hardware/pcb/pcba/pcba.tsx:210"),
         "/hardware/pcb/pcba/pcba.tsx")
    hold("fragment stripped", _clean("/hardware/README.md#parts"), "/hardware/README.md")

    # A path in a string literal is not a reference to this tree.
    hold("python: comment and docstring read, string literal not",
         sorted(t for _, t in _source_targets(
             "x.py", '"""See hardware/a.md."""\n# and hardware/b.md\nP = "hardware/c.md"\n',
             {"hardware"})),
         ["hardware/a.md", "hardware/b.md"])
    hold("js: `//` inside a string does not open a comment",
         _source_targets("x.js", 'const u = "https://e.com/hardware/no.md"; // hardware/yes.md\n',
                         {"hardware"}),
         [(1, "hardware/yes.md")])
    hold("js: `/*` inside a string does not open a block",
         _source_targets("x.js", 'const g = "/*"; \nfoo("hardware/no.md");\n', {"hardware"}), [])

    # Ways of writing "a path" are not paths.
    for ph in ("hardware/foo/bar/foo_bar.py", "hardware/path/to/x.svg",
               "web/.../pcb-pick.js", "hardware/<board>/x.md"):
        hold(f"placeholder: {ph}", _is_placeholder(ph), True)
    hold("a bracketed FILENAME is a malformed link, not a placeholder",
         _is_placeholder("sessions/<Comments are a code smell.md>"), False)
    hold("a real path is not a placeholder",
         _is_placeholder("hardware/ledger/bom.md"), False)

    # The block is the span a tag is written in.
    hold("a block spans its comment run",
         [st for st, _ in _blocks("a\nb\n\nc")], [1, 4])

    # The archive convention: a tag reaches what HEAD dropped.
    tags = _tags()
    if "archive-water-test-cup" in tags:
        hold("the cup stands at its tag",
             _resolves_at("archive-water-test-cup",
                          "hardware/reference/water-test-cup/water-test-cup.3mf"), True)
        hold("and is gone from HEAD",
             _resolves_at("HEAD", "hardware/reference/water-test-cup/water-test-cup.3mf"), False)

    # A solid is held by the lock, not by the index.
    solids = _lock_solids()
    if solids:
        one = "hardware/printed-parts/cold-core/foam-shell/foam-shell.step"
        if one in solids:
            files, _ = _tracked()
            hold("a fetched solid is not in the index", one in files, False)
            hold("and the lock holds it", one in solids, True)

    # git ls-files is read on NEWLINES: a name with spaces is a name.
    files, _ = _tracked()
    hold("a filename with spaces survives the index reading",
         any(" " in f for f in files), True)

    if fails:
        print("check_paths selftest FAILED")
        print("\n".join(fails))
        return 1
    print("check_paths selftest: every rule holds")
    return 0


def main() -> int:
    files, dirs = _tracked()
    solids, tags = _lock_solids(), _tags()
    bad = check(files, dirs, solids, tags)
    if bad:
        for b in bad:
            print(f"  {b}")
        print(f"\n{len(bad)} reference(s) name a path nothing holds.")
        return 1
    print(f"paths: every reference lands — {len(files)} tracked, "
          f"{len(solids)} fetched solids, {len(tags)} tags")
    return 0


if __name__ == "__main__":
    sys.exit(_selftest() if "selftest" in sys.argv[1:] else main())
