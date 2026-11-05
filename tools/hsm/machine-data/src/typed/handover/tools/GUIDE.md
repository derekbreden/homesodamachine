# Converting a machine-data module to typed Rust

`R` below is `/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/machine-typed-202611041700`,
`REPO` is `/Users/derekbredensteiner/Developer/homesodamachine`, and `PY` is `$REPO/tools/cad-venv/bin/python`.

## The job

`tools/hsm/machine-data/src/compiled/<module>.rs` is a mechanical transpile of a Python recipe module into
dynamic code: every name is an `Env` lookup, every value a `Val`, every operation a runtime call. Replace it
with typed Rust at `tools/hsm/machine-data/src/typed/<module>.rs`:

- Rust functions with typed parameters and results; structs (and enums) for the records the module builds;
  `f64`, `i64`, `bool`, `String`, arrays and `Vec`s for its numbers, text and rows; module constants held
  typed in Rust consts or in the module's typed `State`.
- The module's own functions call each other directly as Rust functions, never through the namespace
  (except the replaceable names listed below).
- `Val` remains only at the boundary: provider objects (CadQuery, reference parts, `_routing`, `above_core`,
  `fits`, numpy arrays...), arguments arriving from Python, values returned to Python, and namespace entries.

The Python surface (the stub that forwards to Rust) and every other caller must see exactly what they see
today: the same names in the module namespace, in the same order, holding the same values (same Python types:
int vs float, tuple vs list, dict key order, None), and functions that bind the same arguments and return the
same values. On fixed inputs every file a genrule writes must stay byte-identical.

The generated Rust is the behavior: it is what runs today. Where the Python reads one way and the generated
code does another, the generated code wins.

## What you may change

- Only your own module files `tools/hsm/machine-data/src/typed/<module>.rs` (each holds a placeholder now:
  replace it), your workspace `$R/ws/<name>/`, and your notes file `$R/notes/<name>.md`.
- Never edit the shared runtime (`typed/mod.rs`, `rt.rs`, `py.rs`, `num.rs`, `docs.rs`), another module's
  file, the generated tree (`compiled.rs`, `compiled/`), `native_profiles.rs`, any Python file, or anything else
  in the repository. Other agents are converting the other modules in parallel and share those files. If you
  need a helper the shared files lack, write it privately in your own module file. If you think a shared file
  needs a change, say so in your report.
- No git command that changes anything (commit, add, stash, reset, checkout, switch, branch). Reading is fine.
- Don't start agents or sessions.

Write your module file as you go and keep `$R/notes/<name>.md` current (what is done, what is left, what you
found), so you can pick up again after a context compaction.

## Sources

- Readable Python of each module: `git show a78cf15ba^:<path>`, also copied to
  `/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/d7001403-7740-4475-8098-abce61ab6b5f/scratchpad/py/<module>.py`.
  Paths: `hardware/manifold-layout/{enclosure_assembly,manifold_layout,_scorecard,_lines,rear_snaps,above_core_wiring,above_core_parts,above_core_bom,_machine_reporting,_gas_chain,rear_plumbing}.py`,
  `hardware/scripts/{_machine_checks,_machine_layout,_machine_equipment,_facts,_machine,_stated_bounds,_tube_export,check_asse_drain,_machine_export,_machine_routes}.py`.
  `_assembly_questions` is the subset of `enclosure_assembly.py`'s statements that
  `hardware/scripts/_machine_checks.py` (`_source_statements`) selects; its generated module shows exactly which.
- Generated Rust: `tools/hsm/machine-data/src/compiled/<module>.rs`. The module's top level is `initialize`;
  each Python function starts at a `// <file>.py:<line> <name>` comment. The files are large: grep them for
  the function or statement you are converting rather than reading them whole.
- The runtime the generated code calls: `tools/hsm/machine-data/src/compiled.rs` (`Runtime`, `Env`, imports)
  and `tools/hsm/documents/src/interop.rs` (`Val`, `binary`, `unary`, `format`, the builtins and `math`).
- The Python stub each module's callers import (same path as the Python above, in the working tree) lists
  `_rust_functions` and `_rust_exports`: the names Python reaches.
- `tools/hsm/machine-data/src/native_profiles.rs` installs native functions into some namespaces after the
  module's own top level runs:
  - `rear_snaps`: `clearance_profile`, `asse_cap_room`, `asse_adapter_capture`, `pisco_cap_fit` (it reads
    `ASSE_BODY_SEATING_DEPTH`, `ASSE_HEX_SEATING_DEPTH`, `WALL`, `PISCO_CAP_FIT` from the namespace as it
    installs, so they must be set by then);
  - `rear_plumbing`: `regulator_datums`;
  - `check_asse_drain`: `centerline_radii`, `_names`, `_torus_records`;
  - `_machine`: `sources`, `stamps`.
  The generated code looks globals up at call time, so the module's own callers of these names reach the
  native versions. Yours must too: call them through the namespace (`ns.get(name)?.call(..)`; keep the `Ns`
  in your State) — or convert them into the same typed computation only if you can show it is identical.

Finished modules to copy patterns from: `typed/_stated_bounds.rs` (instances of a class the Python stub
declares, a module-level list shared by reference), `typed/_gas_chain.rs` (provider constants as `Num`,
CadQuery calls), `typed/_machine_export.rs`, `typed/_machine_routes.rs`, `typed/above_core_bom.rs`
(`_layout_data` answered in process). Their `pub fn`s are typed APIs you may call directly.

## The runtime (`typed/`)

- `rt.rs` — `Rt` is the module registry, `Ns` a namespace.
  - `ns.set(name, val)`, `ns.get(name)`; `ns.def(rt, name, |rt, args, kwargs| -> Result<Val>)` binds a
    Python-callable function (it pushes the module's frame). Methods of a class the stub declares are bound
    as `"Class.method"` names, as `_stated_bounds.rs` does; get the class with `rt.python_type(module, name)`.
  - `rt.import(name)`: another machine module's namespace or a provider module (`import x`).
    `rt.member(module, name)`: `from module import name`. Imports are cached as Python caches them.
  - `rt.keep(MODULE, State {..})` at install, `rt.state::<State>(MODULE)` in functions: the module's typed
    state (constants, provider handles, caches).
  - `rt.layout_data(json!({"op": .., ..}))`: `_layout_data.data(op, **values)` answered in process (same
    result as the worker round trip: plain JSON in and out).
  - `rt.print(text)`: `print(text)`. `rt.note_read(path)`. `rt.root()`: the checkout root.
- `py.rs` — the Python boundary. `py::bind(args, kwargs, &["a", "b"], &["kw_only"])` then
  `.req/.opt/.some/.f64/.f64_or/.string/.string_or/.bool_or` binds a signature; `py::call`, `py::call_kw`,
  `py::method`, `py::item`; `py::snapshot` copies a provider container by value in one callback;
  `py::plain` converts to serde_json; `f64s`, `v3`, `v2`, `strings`, `path`, `tuple`, `list`, `ftuple`,
  `flist`, `dict`, `s`, `doc`, `from_json`, `dget`, `at`, `json_loads`, `json_dumps`, `resolve`, `mkdirs`,
  `read_text`, `path_str`, `merged`, `dict_of`, `sys_path_insert`, `sys_path_has`, `unpack`, `splat`.
- `num.rs` — the runtime's arithmetic and text: `fmt(x, spec)` / `fmti` / `fmtv` (an f-string field or
  `format()`), `fstr` (`str()` of a float), `round_to`, `round_int`, `radians`, `degrees`, `hypot`, `hypot2`,
  `hypot3`, `dist`, `isclose`, `floordiv`, `modulo`, `floor`, `ceil`, `max2`, `min2`, `max_of`, `min_of`,
  `argmax`, `argmin`, `sum`, `sum_val`, `order`, `sort_by_key`, `sort_by_keys`, and `Num` (a number that is
  an int or a float, combining as the runtime does).
- `docs.rs` — each module's `__doc__` (`docs::MODULE_NAME`, `py::doc(..)`).

## The namespace contract

1. Set every name the generated `initialize` sets, in the same order, with the same values: `__doc__`,
   imports under their aliases (`sys`, `Path`, `cq`, `_hw`, provider modules), constants, functions, classes,
   and module-level loop variables (`for x in ...` at top level leaves `x` bound; the stub's `_rust_exports`
   lists them). Callers enumerate namespaces (`vars()`, the `names` action), so order and completeness count.
2. A module-level name rebound later in the file holds its final value; a function reading it at call time
   sees that final value.
3. Bind functions with the Python signature: positional names, defaults, keyword-only parameters. A default is
   evaluated once, at definition (capture it then). Return exactly the value the generated code returns.
4. Names other code replaces while it calls the module must be read from the namespace each time they are
   used, never cached:
   - `rear_snaps`: `box`, `prism_x`, `section_solid` (enclosure-data's back-top recipe swaps them while it
     calls rear_snaps functions);
   - `above_core_wiring`: `shell_features`, and `layout`, `_box`, `cq`, `SIZES`, `WALL`, `FIT`, `IDENTITY`,
     `PORTS_WEST`, `PORTS_FORE`, `UPRIGHT_PORTS_FORE`, `WALL_BACK_FORE`, `WALL_BACK_AFT`, `EAST_FLANK`, `carry`
     (`hardware/wiring/installed/_fine_contacts.py` sets them while it calls `placements`, `_well`,
     `driver_columns`);
   - the native_profiles names above.
   If you find another caller that assigns into your module (grep the repo for `<alias>.<name> =` and
   `setattr(`), treat that name the same way and say so in your report.
5. A module-level container other code reads or mutates (a list, dict or set in the namespace) is one object:
   the namespace and your State hold the same `Val`, and you mutate it in place as the generated code does.

## Semantics that decide bytes

- Ints stay ints: an int literal is `Val::Int`; int with int gives an int when the result is integral; `/`
  always gives a float. A number from a provider or JSON may be either: hold it as `Num`, or keep the `Val` if
  it flows back out unchanged. Writing `1.0` where the generated code has `Val::Int(1)` changes output bytes.
- Floats become text only through the runtime: f-string fields via `num::fmt(x, spec)` /
  `interop::format(val, spec)`, `str(x)` via `num::fstr`. Never Rust's `{}` or `{:.3}` on a float.
- `round(x, n)` is `num::round_to` and gives a float even for an int; `round(x)` gives an int (ties to even).
- `sum` adds in order from the int 0; an empty sum is the int 0 (`num::sum_val`).
- `min` / `max` (with or without `key=`): the first of equal values wins.
- `sorted(.., reverse=True)` and `.sort(reverse=True)`: the runtime sorts ascending (stable) and then reverses
  the whole list, so equal keys come out in reverse order (`num::sort_by_key(s)`). Check the generated code's
  `sorted` call and interop's sort for the key type (numbers, strings, tuples compare as in interop `cmp`).
- `math.*` as interop implements them: `hypot` folds `f64::hypot` from 0, `dist` likewise, `radians` is
  `x * PI / 180`, `degrees` is `x * 180 / PI`, `floor`/`ceil`/`trunc` give ints, `isclose` defaults
  `rel_tol=1e-9`, `abs_tol=0`.
- Comparisons between int and float are numeric. Dicts iterate in insertion order. Follow the generated code for
  sets, string methods, `%` and `.format`.
- `try`/`except`: the generated code catches any error from the `try` body (it does not filter by exception
  class) and runs the handler; mirror its control flow and its error text.
- Keep the order of calls with side effects: CadQuery constructions, file reads and writes, `note_read`,
  prints, appends to shared lists. Side-effect-free provider reads (module constants) may be read once and
  kept.

## Provider objects and costs

Provider modules are Python objects reached by callback: every attribute read and call is a round trip.
Keep provider objects as `Val`, read a provider constant once and keep it typed, and copy provider data you
compute on with one `py::snapshot` instead of item-by-item access. Python dicts, lists and sets passed in as
arguments arrive as live references (`Val::Ref`: every access is a callback); tuples and scalars arrive by
value. Values you return are copied back to Python by value.

Typed means the computation is Rust: no `Val` in loops over your own data, no namespace lookups for your own
functions, no `interop::binary` on numbers you hold as `f64`/`Num`.

## Building and checking

1. Your workspace is `$R/ws/<name>`: your modules, the finished modules and the shared runtime compile from
   the real tree; every other module is a placeholder whose generated namespace runs. Set
   `pub const TYPED: bool = true;` in your module file when it should run typed (a module with
   `TYPED = false` runs its generated code even if your file compiles).
2. Build: `$R/build.sh <name>` (through `tools/run.py`, which may queue behind other builds; the first build
   takes about 3 minutes, later ones are incremental). It prints errors in your files and the binary's time.
   The binary is `$R/ws/<name>/target/release/machine-data`.
3. Which genrules run your module: `$R/who.sh <module>` (from `$R/cover-logs/`; a coverage sweep over all 42
   genrules is still filling them in, `$R/cover.jsonl` lists the genrules it has finished, in the order of
   `$R/genrules.txt`). Each genrule's scripts are listed in `$R/steps/<genrule>.stage.json`.
4. Compare one genrule against the saved baseline:
   `cd $R && AGAINST=$R/base-trees $PY compare.py steps <genrule> <name>=$R/ws/<name>/target/release/machine-data`
   It prints one JSON line; `differ_count:<name>` must be 0 and `runs.<name>.errors` empty. Use your agent
   name as the label (it names the clone directory, so labels must not collide). `KEEP=1` keeps the clone at
   `$R/steps/<genrule>.<name>` so you can inspect a differing file (delete it afterwards). To rule out a
   stale baseline, compare against the generated build directly:
   `$PY compare.py steps <genrule> base=$R/bin/machine-data <name>=<your binary>` (labels `base`/`<name>`
   name the clones; pick `base-<name>` if `base` might collide with another agent).
   A diff whose only content is the clone's own path means a baseline saved before paths were normalized:
   use the direct comparison.
5. Some genrules wait minutes for the CAD lock other sessions hold: run them in the background
   (`run_in_background`), and check the quick ones first.
6. Code no genrule runs still has to be converted faithfully. Note which functions no genrule exercised.

## Report

Your final message: the modules you converted (with `TYPED = true`), each genrule you compared and its result
(files, differ count), the functions no genrule exercised, anything you could not match, and any change you
think a shared file needs.
