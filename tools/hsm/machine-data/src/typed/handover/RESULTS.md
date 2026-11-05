# machine-data typed modules: results (2026-11-04)

Not committed. The typed sources are untracked in `tools/hsm/machine-data/src/typed/`, 27 files.
The hand-over, the module status and the run's scripts are in
`~/Library/Application Support/Claude/side-session-notes/local_133364ed-38b1-444b-9fc7-c60c2251535d/machine-data-typed/`.

## Revisions and binaries

- Stage revision: `78404375d`. Crate sources: `a78cf15ba`.
- `bin/machine-data`, generated, opt 3, `debug = 1`:
  `9fe15e7d5d39516ae4abb8b272a40fe3a37608d8fb8ec6fea8f86751c7dbc2a7`
- `bin-base0`, generated, opt 0:
  `d985a9c49622b8dcd5d435fb0b2819f87aab8ef4726f35731ee4557ec13c54e7`
- Hybrid with five typed modules, opt 0:
  `840d2b052a14e02902d2df79e012dcc626510e64ed1245604e2ddc5b1fb63b23`
- Pinned workers: 90 binaries; the list's digest is
  `7a92dc570d5a51ef2c81f7df9fb542cac5978bfe00c6ef5072bd839cd9f7b1fb`.

## Numbers

- The generated sweep covered all 42 genrules in 442.8 CPU s, on the instrumented opt-1 build.
- Every genrule finished except `enclosure`, which stops at `nameplate-stock` in enclosure-checks
  with the generated build as well.
- Typed against generated, at opt 0 (files that differ / files compared):

  | Genrule | Result |
  | --- | --- |
  | cold-core-assembly | 0/405 |
  | bom-masses | 0/832 |
  | fluid-topology-sync | 0/678 |
  | internal-plumbing-sync | 0/671 |
  | enclosure-mechanical-sync | 0/671 |
  | enclosure-dimensions | 0/665 |
  | foam-cap | 0/386 |
  | rear-equipment-caps | 0/278 |
  | enclosure-assembly | 23/940 |

- On enclosure-assembly, every one of the 23 differing files follows from two arc samples that
  differ by 1 ulp. The cause is layout-data built at opt 0, which keeps `sin` and `cos` separate
  where opt 3 merges them into one `__sincos_stret` call.
- No release-build check was run, and no CPU or recompile measurement was taken.
