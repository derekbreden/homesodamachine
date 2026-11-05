# machine-data typed conversion — run directory

- `bin/`: worker binaries copied from tools/hsm/target/release at 16:56; `bin/machine-data` is
  the HEAD (78404375d) generated build.
- `steps/<genrule>`: pristine work directories staged at 78404375d by `stage.py`, with
  `<genrule>.stage.json` naming scripts and outputs.
- `compare.py steps <target> label=program ...`: one fresh clone per variant, all files hashed.
- `sweep.sh out.jsonl label=program ...`: every genrule in `genrules.txt` (or `TARGETS=`), with
  per-target coverage logs under `cover-logs/` when `COVER=1`.
- `harness.py`: worker binaries from `bin/`, machine-data from the named program;
  `CALLBACK_STATS=<path>` appends provider-callback counts.
- `cover/`: instrumented crate copy (`instrument.py`), private target directory.
- Readable source of each generated module: `git show a78cf15ba^:<python path>`.
- Conversion agents (Agent tool, background): rear afb3ae60460f7d94a (rear_snaps, rear_plumbing),
  lines af0908ebec5afd6ee, manifold a47a67df5aae96154, machine aadf9d27ddb13b4ac (_machine*,
  _assembly_questions), misc a313653b1d62a219c (_facts, check_asse_drain, _tube_export, above_core_parts,
  above_core_wiring), assembly ab44721c206ca9a22, scorecard affc6dcfc73a4180a. Guide: GUIDE.md;
  workspaces ws/<name> (ws.sh), build.sh, who.sh, notes/<name>.md.
- base-trees/: hashes saved by the cover sweep; the first four targets were saved before compare.py
  normalized the clone path and need re-saving.
- bin-all/: every worker in tools/hsm/target/release at 19:58, bin/ overlaid (bin-all.sha256);
  compare.py takes BINDIR=<dir>, harness logs workers still taken from the checkout to UNPINNED_LOG.
  bin/enclosure-data and bin/cold-core-data are opt-level 0 builds (16:44, 16:33).
- Opt-level: a build at opt ≥1 merges a sin and a cos of one angle in one block into
  __sincos_stret (last-bit differences for 89,265 of 20M angles). layout-data's arc sampling has
  such a pair, so opt-0 builds differ from bin/machine-data at a few route samples on
  enclosure-assembly. bin-base0/machine-data (d985a9c49622b8dc) is the generated crate at opt 0,
  the base for opt-0 workspaces. typed code calls num::sin / num::cos (#[inline(never)]).
- compare.py writes Library/Caches/hsm/parts/tmp/<pid>-<n> as <ENGINE-TMP> (the equipment and
  route scratch JSON name the requesting pid). base-trees-pinned/enclosure-assembly.json: base
  with bin-all, re-hashed with that rule.
- switch.py: graph.json / BUILD.bazel source-list switch (45 entries, 42 lists, 27 typed files).
