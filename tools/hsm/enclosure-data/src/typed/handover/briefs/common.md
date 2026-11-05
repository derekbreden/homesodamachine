# Working as one of the enclosure-data conversion agents

You are one of several agents converting the `enclosure-data` crate's generated Rust modules to typed
Rust, in parallel, in Derek Bredensteiner's home-soda-machine repository
(`/Users/derekbredensteiner/Developer/homesodamachine`, a shared checkout that other sessions edit too).

`$R/GUIDE.md` (`R=/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700`)
is the contract: what to produce, what you may touch (only your own module files under
`tools/hsm/enclosure-data/src/typed/`, your workspace `$R/aws/<name>/` and your notes `$R/notes/<name>.md`),
the runtime API, the namespace contract, the arithmetic that decides bytes, and how to build and compare.
Read it first and follow it exactly.

How to work:
1. `$R/ws.sh <name> <your modules>` once (re-run it after another agent finishes a module you call).
2. Per module: read `$R/py/<module>.py`, the generated `tools/hsm/enclosure-data/src/compiled/<module>.rs`,
   the stub at the module's repository path, and `$R/sigs/<module>.sigs.md` if present. Write
   `tools/hsm/enclosure-data/src/typed/<module>.rs` with `pub const TYPED: bool = true;`.
3. Build with `$R/build.sh <name>`; check the namespace with
   `python3 $R/names.py <module> $R/aws/<name>/target/release/enclosure-data`; compare the steps
   `python3 $R/who.py <module>` lists with `python3 $R/compare.py <rules> <name>=$R/aws/<name>/target/release/enclosure-data`.
   Every rule has its baseline manifest in `$R/base/`; `--direct` (a baseline run beside yours, twice the
   cost) is for chasing a difference in a part-program output. The step `enclosure` (about 2.5 CPU-minutes, the most thorough) exercises
   nearly every module; `enclosure-box` and `enclosure-assembly` the machine-level flows. HEAD's
   enclosure-checks part program lacks the `nameplate-stock`/`nameplate-cuts` operations; the harness
   empties those nodes in what the checks are asked, for every binary alike, so don't chase that.
4. Fix every difference, then the next module. Keep `$R/notes/<name>.md` current as you go.

The machine is an 8 GB Mac shared with other agents and sessions: builds and step runs go through
`tools/run.py` and may queue for minutes. Run builds and comparisons with `run_in_background` and keep
working (on the next function or module) while they run; never poll an output file or sleep: wait for the
completion notification. The shell is zsh: `status` is a read-only variable, there is no `timeout`, and
`git grep` is the fast way to search the repository.

Your final message is your report (GUIDE.md, "Report"), concise.
