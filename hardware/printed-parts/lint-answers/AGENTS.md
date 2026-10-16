# Lint answers

Each file here holds the answers for one printed piece, at that piece's own path below
`printed-parts/`. An answer explains a lint finding instead of fixing it. Fixing is the default:
change the source so the flagged face is gone. A step, land, skin, fin or facet left where two
features meet is fixed by reconciling those two features.

> There are legitimate reasons to give an answer instead of fixing a lint finding (e.g.
> unavoidable without adding 20 GB  of meshes to the geometry) (e.g. the linter is wrong and
> that's not actually what's happening and we haven't fixed the linter yet but we really should)
> (e.g. it was out of my scope but i noticed it so I'm documenting it *and* telling the user
> about what I found), it's just that those legitimate reasons do *not* include "eh its not
> hurting nobody". It is hurting somebody. It hurts me. It hurts my sensibilities.
>
> — Derek, 2026-10-15

An answer says which of those reasons it is. When the lint is wrong, or the finding is outside
the task, the same reply tells Derek. "Carries no load", "not a freestanding wall", "backed by
complete stock" and "prints fine" are all "eh its not hurting nobody".

An entry is a `[class] reason` line, an `alternatives:` line and one `click:` per instance;
`hardware/scripts/geometry_lint.py` reads them and says what an answer does and does not do.
