# The commit map

`commit-map` is the old → new SHA table two `git filter-repo` runs left behind, composed
into one: the first expunged 98 generated solids on 2026-08-17, the second the rest of the
generated tree — every `.step`, `.stl`, `.glb` and `.step.mesh` but the three harvested
reference solids, the board renders, the card pictures and decks, the Quick Start artwork —
on 2026-08-26. 9,282 pairs, one per line, oldest first, under an `old new` header.

**A SHA written down before 2026-08-26 names a commit this repo does not have.** Both
rewrites gave every commit they touched a new identity and `gc --prune=now` dropped the
originals, so `git show <old sha>` fails and the transcripts under
[`calibration/`](/calibration/) are full of them, in prose a reader is meant to be able to
follow. This file is how they are followed:

```
grep -i ^<old sha> tools/git-history/commit-map
```

The second rewrite's pairs are composed onto the first's, so an address from either era
resolves in one lookup. The messages and author dates survived both untouched, so the commit
the new SHA names is the same commit in every respect a reader cares about.

**427 pairs end in forty zeroes.** Those commits carried nothing but the paths that were
expunged, so the rewrite left them empty and dropped them — 214 in the second run. The zero
is the answer: there is no successor, and the work is in the commit that follows.

**Every SHA in this tree that has a successor now names it.** A SHA in prose is an address a
reader is meant to chase, not a word — the transcripts under [`calibration/`](/calibration/)
carry them because a file moved or was deleted and the commit is where the thing still stands,
which is the same reason source and print logs carry them. An address that resolves for nobody
is worth less than the record it was thought to preserve, so the tree is repinned and this
table is what a SHA written down somewhere ELSE — an old note, a message, a branch nobody
kept — is followed with.

**Twenty-six do not resolve, and none of them can.** Seventeen name commits the rewrite left
empty and dropped, so there is no successor to point at; the work is in the commit that
follows. Nine were never commits here — SHAs in the `rectdiff` and `circuit-json-to-gerber`
forks, and payload content hashes, which are hex of a different kind and belong to whatever
produced them.

[`check_paths.py`](/tools/check_paths.py) reports a blob URL pinned to a commit this repo does
not have, and this file is what answers it. It guards the PATH half of a reference; a bare SHA
in prose is not a path, so nothing derives it and nothing catches it when a rewrite orphans
it. That is why the sweep is a sweep and not a check.

This table cannot be regenerated. The mirrors both runs came from were throwaways.
