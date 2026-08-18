# The commit map

`commit-map` is the old → new SHA table `git filter-repo` wrote when the 98 generated
solids were expunged from this history. 5,543 commits, one pair per line, oldest first,
under a `old new` header.

**Every SHA written down before 2026-08-17 names a commit this repo does not have.** The
rewrite gave all 5,532 of them new identities and `gc --prune=now` dropped the originals,
so `git show <old sha>` fails and the transcripts under [`calibration/`](/calibration/) are
full of them — 167 distinct, in prose a reader is meant to be able to follow. This file is
how they are followed:

```
grep -i ^<old sha> tools/git-history/commit-map
```

The messages and author dates survived the rewrite untouched, so the commit the new SHA
names is the same commit in every respect a reader cares about.

**The transcripts were not edited.** A SHA sitting in prose — often in something the author
typed — is the record of what was said, and rewriting it would be changing that record to
keep a lookup working. Keeping the table is the cheaper half of the trade and it costs the
record nothing. Blob URLs are the exception and were repinned: a URL's SHA is an address
rather than a word, and a dead one is a link that 404s instead of a fact a reader can chase.

[`check_paths.py`](/tools/check_paths.py) holds that: a blob URL pinned to a commit this
repo does not have is reported, and this file is what answers it.

This table cannot be regenerated. The mirror it came from was a throwaway.
