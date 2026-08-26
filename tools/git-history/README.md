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

**The transcripts were not edited.** A SHA sitting in prose — often in something the author
typed — is the record of what was said, and rewriting it would be changing that record to
keep a lookup working. Keeping the table is the cheaper half of the trade and it costs the
record nothing. Blob URLs are the exception and were repinned: a URL's SHA is an address
rather than a word, and a dead one is a link that 404s instead of a fact a reader can chase.

[`check_paths.py`](/tools/check_paths.py) holds that: a blob URL pinned to a commit this
repo does not have is reported, and this file is what answers it.

This table cannot be regenerated. The mirrors both runs came from were throwaways.
