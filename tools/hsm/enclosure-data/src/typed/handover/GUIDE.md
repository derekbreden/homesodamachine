# Converting an enclosure-data module to typed Rust

`R` is `/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700`,
`REPO` is `/Users/derekbredensteiner/Developer/homesodamachine`, `PY` is `$REPO/tools/cad-venv/bin/python`,
`T` is `$REPO/tools/hsm/enclosure-data/src/typed`.

## The job

`$REPO/tools/hsm/enclosure-data/src/compiled/<module>.rs` is a mechanical transpile of a Python recipe module
into dynamic code: every name is an `Env` lookup, every value a `Val`, every operation a runtime call
(`binary`, `compare`, `.attr(..)?.call(..)`). Replace it with typed Rust at `$T/<module>.rs`:

- Rust functions with typed parameters and results; structs (and enums) for the records the module builds;
  `f64`, `i64`, `bool`, `String`, arrays, tuples and `Vec`s for its numbers, text and rows; module constants
  held typed in Rust `const`s or in the module's typed `State`.
- The module's own functions call each other directly as Rust functions, never through the namespace
  (except the replaceable names listed below).
- `Val` remains only at the boundary: provider objects (`_rust_part`, `fits`, `port_chip`, fontTools,
  other workers' proxies...), arguments arriving from Python, values returned to Python, namespace entries,
  and recipe documents (`numbers` dicts) that leave for a Rust part program as JSON.

The Python surface (the stub that forwards to Rust) and every other caller must see exactly what they see
today: the same names in the module namespace, in the same order, holding the same values (same Python types:
int vs float, tuple vs list, dict key order, None), and functions that bind the same arguments and return the
same values. Other crates (machine-data, cold-core-data, faucet-data) reach these namespaces too, through
Python. On fixed inputs every file a genrule leaves must stay byte-identical.

The generated Rust is the behavior: it is what runs today. Where the Python reads one way and the generated
code does another, the generated code wins. (Known places: `_enclosure_back_top`'s receiver calls
`crate::nameplate_snap::apply(..)`; `nameplate.numbers()` returns `crate::nameplate_snap::numbers(..)`;
these are hand-written Rust in `src/nameplate_snap.rs` you call directly.)

## What you may change

- Only your own module files `$T/<module>.rs` (each holds a placeholder now: replace it), your workspace
  `$R/aws/<name>/`, and your notes file `$R/notes/<name>.md`.
- Never edit the shared runtime (`$T/mod.rs`, `rt.rs`, `py.rs`, `num.rs`, and any other non-module file in
  `$T`), another module's file, the generated tree (`compiled.rs`, `compiled/`), `main.rs` or the other
  hand-written files in `src/`, any Python file, or anything else in the repository. Other agents are
  converting the other modules in parallel and share those files. If you need a helper the shared files
  lack, write it privately in your own module file. If you think a shared file needs a change, say so in
  your report.
- No git command that changes anything (commit, add, stash, reset, checkout, switch, branch). Reading is fine.
- Don't start agents or sessions.

Write your module file as you go and keep `$R/notes/<name>.md` current (what is done, what is left, what you
found), so you can pick up again after a context compaction.

## Sources

- Readable Python of each module, as transpiled: `$R/py/<module>.py` (the file at `392a60abc`). Repository
  paths are in `$T/mod.rs` (`MODULES`). Its docstrings and comments are the design record: carry the module
  docstring as `//!` and each function's docstring as `///`, and keep the comments.
- Generated Rust: `$REPO/tools/hsm/enclosure-data/src/compiled/<module>.rs`. The module's top level is
  `initialize`; each Python function is an `e.set("<name>", {... bind(&outer, ..) ...})` preceded by a
  `// <name>` comment; class methods are `"Class.method"` entries. The files are large: grep them for the
  function or statement you are converting rather than reading them whole.
- The runtime the generated code calls: `$REPO/tools/hsm/enclosure-data/src/compiled.rs` (`Runtime`, `Env`,
  imports, `source_at`, `context`, `memoize`) and `$REPO/tools/hsm/documents/src/interop.rs` (`Val`,
  `binary`, `unary`, `compare`, `format`, the builtins and `math`).
- The Python stub each module's callers import is the module's own path in the working tree. It forwards
  every attribute to the worker (`action="get"`, `"call"`, `"public-names"`, `"set"`), and declares the
  module's classes, whose methods forward to the `"Class.method"` namespace entries with `self` first. Read
  `hardware/printed-parts/enclosure/enclosure/_enclosure_compiled.py` for how arguments travel: a dict,
  list or set argument from Python arrives as a live reference (`Val::Ref`: every access is a callback);
  tuples and scalars arrive by value; instances of the stub classes arrive as references.
- Observed signatures: `$R/sigs/<module>.sigs.md` (when present) lists, per function, the Python line, the
  argument and return types seen on every traced call, and the steps that ran it. `python3 $R/who.py <module>`
  lists the steps whose traces show the module running.

## The runtime (`$T`)

- `rt.rs` — `Rt` is the module registry, `Ns` a namespace.
  - `ns.set(name, val)`, `ns.get(name)`; `ns.def(rt, name, |rt, args, kwargs| -> Result<Val>)` binds a
    Python-callable function (it pushes the module's frame); `ns.function(rt, f)` makes one without binding
    it (closures, defaults, values handed to other code); `ns.globals()` is `globals()`.
  - Methods of a stub class are bound as `"Class.method"` names, and the class name itself is
    `rt.python_type(<module>, "Class")`, exactly as the generated code does.
  - `rt.import(name)`: another enclosure module's namespace or a provider module (`import x`).
    `rt.member(module, name)`: `from module import name`. Provider imports are cached as Python caches them.
  - `rt.keep(MODULE, State {..})` at install, `rt.state::<State>(MODULE)` in functions: the module's typed
    state (constants, provider handles, caches). Another module's typed API reaches its state the same way.
  - `rt.enclosure_data(json!({"op": .., ..}))`: `_enclosure_data.read(op, **values)` answered in this process
    (the same JSON in and out as the worker round trip: a JSON list comes back where Python would see a list).
  - `rt.print(text)`, `rt.note_read(path)`, `rt.note_write(path)`, `rt.read_input(path)` (`_read_input`),
    `rt.root()` (the checkout root), `rt.substitute(kind, path, values, Some(MODULE))` (docgen's
    `substitute_md` & co. as your module calls them; `rt.import("docgen")` gives the same as a namespace).
  - `rt::site()` (`#[track_caller]`): the construction site a graph node records as `source`.
  - `rt::context(enter, exit)`: a context manager value; `rt::memoize(f, limit)`: `functools.cache` /
    `lru_cache(maxsize=limit)` of a Python-callable function, as the generated code builds them.
- `py.rs` — the Python boundary. `py::bind(args, kwargs, &["a", "b"], &["kw_only"])` then
  `.req/.opt/.some/.f64/.f64_or/.string/.string_or/.bool_or` binds a signature; `py::call`, `py::call_kw`,
  `py::method`, `py::item`; `py::snapshot` copies a provider container by value in one callback;
  `py::plain` converts to serde_json; `f64s`, `v3`, `v2`, `strings`, `path`, `tuple`, `list`, `ftuple`,
  `flist`, `dict`, `s`, `from_json`, `dget`, `at`, `json_loads`, `json_dumps`, `resolve`, `mkdirs`,
  `read_text`, `path_str`, `merged`, `dict_of`, `sys_path_insert`, `sys_path_has`, `unpack`, `splat`.
  The trait `Py` (`to_py(&self) -> Result<Val>`, `from_py(&Val) -> Result<Self>`) converts typed values
  at the boundary: `f64` (accepts an int), `i64`, `bool`, `String`, `()` (None), `Num`, `Val`, `Option<T>`
  (`T` or None), `Vec<T>` (a list), `Tup<T>` (a tuple of any length), Rust tuples and `[T; N]` (tuples);
  `crate::py_args![a, b]` makes positional arguments from typed values.
- `num.rs` — the runtime's arithmetic and text: `fmt(x, spec)` / `fmti` / `fmtv` (an f-string field or
  `format()`), `fstr` (`str()` of a float), `round_to`, `round_int`, `radians`, `degrees`, `hypot`, `hypot2`,
  `hypot3`, `dist`, `isclose`, `floordiv`, `modulo`, `floor`, `ceil`, `max2`, `min2`, `max_of`, `min_of`,
  `argmax`, `argmin`, `sum`, `sum_val`, `order`, `sort_by_key`, `sort_by_keys`, and `Num` (a number that is
  an int or a float, combining as the runtime does).

## The namespace contract

1. Set every name the generated `initialize` sets, in the same order, with the same values: `__name__` and
   `__file__` (the registry sets these two), imports under their aliases (`sys`, `math`, `Path`, `cq`,
   provider modules), constants, functions, classes and their `"Class.method"` entries, and module-level
   loop variables (`for x in ...` at top level leaves `x` bound). There is no `__doc__`. Callers enumerate
   namespaces (`names`, `public-names`, `vars()`), so order and completeness count. Write a check for
   yourself that the name list matches (see "Building and checking").
2. A module-level name rebound later in the file holds its final value; a function reading it at call time
   sees that final value.
3. Bind functions with the Python signature: positional names, defaults, keyword-only parameters, `*args`,
   `**kwargs`. A default is evaluated once, at definition (capture it then). Return exactly the value the
   generated code returns.
4. Names other code replaces while it calls the module must be read from the namespace each time they are
   used, never cached. In this crate that is common: the enclosure source (`enclosure`) is the `shell` that
   the recorders (`_enclosure_panel._record`, `_enclosure_back_top._leaves` / `_frame_leaves`,
   `_rust_enclosure_checks._numeric`, front-top, pump-retainer, the driver) patch with `setattr(shell, ..)`:
   its geometry leaves (`_ybox`, `_xcyl`, `_ycyl`, `_zcyl`, `_teardrop_y`, `_yz_prism`, `_xz_prism`,
   `_xy_prism`, `_round_z`, `_rounded_outer`, `_handhold_cutter`, `_handhold_finish_air`,
   `disposal_letters`, `_unified`, the 29 slots it initialises to `None`, ...), `cq`, and `record_bound`
   (machine-data sets it too). The back-top recipe also patches functions into `funnel_frame`, `flute_skin`,
   `_route_snaps` and `_swept_top` while it runs. Grep the generated code and the Python for `setattr(`,
   `<alias>.<name> =` and `originals` to find every such name your module reads or writes, treat each the
   same way and list them in your report.
5. A module-level container other code reads or mutates (a list, dict or set in the namespace: `BOUNDS`,
   `_z_seam_passes`, `_last_box`, caches) is one object: the namespace and your State hold the same `Val`,
   and you mutate it in place as the generated code does. `BOUNDS` and `_z_seam_passes` are handed to Python
   by reference when read as module members (`rt.rs` `export`), so their identity counts.

## Semantics that decide bytes

- Ints stay ints: an int literal is `Val::Int`; int with int gives an int when the result is integral; `/`
  always gives a float. A number from a provider or JSON may be either: hold it as `Num`, or keep the `Val` if
  it flows back out unchanged. Writing `1.0` where the generated code has `Val::Int(1)` changes output bytes
  (`_ybox(0, depth, ..)` records `0`, not `0.0`, in a recipe document).
- Floats become text only through the runtime: f-string fields via `num::fmt(x, spec)` /
  `interop::format(val, spec)`, `str(x)` via `num::fstr`. Never Rust's `{}` or `{:.3}` on a float.
- Keep Python's operand order and grouping (`a + b + c` is `(a + b) + c`; never reassociate, fold constants,
  replace `x ** 2` by `x * x` (`**` is `powf`), or use `mul_add`).
- `round(x, n)` is `num::round_to` and gives a float even for an int; `round(x)` gives an int (ties to even).
- `sum` adds in order from the int 0; an empty sum is the int 0 (`num::sum_val`).
- `min` / `max` (with or without `key=`): the first of equal values wins. Never `f64::min`/`max`.
- `sorted(.., reverse=True)` and `.sort(reverse=True)`: the runtime sorts ascending (stable) and then reverses
  the whole list, so equal keys come out in reverse order (`num::sort_by_key(s)`). Check the generated code's
  `sorted` call and interop's sort for the key type (numbers, strings, tuples compare as in interop `cmp`).
- `math.*` as interop implements them: `hypot` folds `f64::hypot` from 0, `dist` likewise, `radians` is
  `x * PI / 180`, `degrees` is `x * 180 / PI`, `floor`/`ceil`/`trunc` give ints, `isclose` defaults
  `rel_tol=1e-9`, `abs_tol=0`; `sqrt`, `tan`, `atan2`, ... are the `f64` methods.
- `x ** y` is `num::pow(x, y)` (`Num::pow` for numbers that may be ints), `math.sin`/`math.cos` are
  `num::sin`/`num::cos`: never `powf`, `powi`, `x * x`, or the `f64` `sin`/`cos` methods. The crate's
  release build is optimized, and the optimizer rewrites `powf(2.0)` as `x * x`, `powf` of 2 as `exp2`, and a
  `sin` and a `cos` of one angle as one `__sincos_stret` call; each differs from interop in the last bit for
  some inputs. These builds are unoptimized, so a comparison here does not catch it.
- Comparisons between int and float are numeric. Dicts iterate in insertion order. Follow the generated code
  for sets, string methods, `%` and `.format`.
- `try`/`except`: the generated code catches any error from the `try` body (it does not filter by exception
  class) and runs the handler; mirror its control flow and its error text. A `raise ValueError(msg)` is an
  error whose text is `msg`; callers that catch it and test `str(error)` see that text.
- Keep the order of calls with side effects: part-program runs (`_rust_part.cut`/`check`/`run`), file reads
  and writes, `note_read`, prints, appends to shared lists, `setattr` on another module. Side-effect-free
  provider reads (module constants) may be read once and kept.

## Construction graphs and solids

`_enclosure_panel._Graph` / `_Shape` (and `_rust_enclosure_checks._Questions`, a `_Graph` that measures)
record each solid operation as a node `dict(op=..., inputs=[...], source=dict(path=..., line=...), **numbers)`;
a Rust part program builds the solids from the document. The node's `source` names the line that made it;
it is the one value the conversion changes on purpose (the comparison masks it). Use `rt::site()` for it.
The typed graph API for the modules that build or consume graphs is in `$T/graph.rs` once it exists; until
then, solids your module receives are Python objects (`Val`): call their methods as the generated code does.

## Provider objects and costs

Provider modules are Python objects reached by callback: every attribute read and call is a round trip.
Keep provider objects as `Val`, read a provider constant once and keep it typed, and copy provider data you
compute on with one `py::snapshot` instead of item-by-item access. Values you return are copied back to
Python by value, except functions, namespaces and classes (by reference).

Typed means the computation is Rust: no `Val` in loops over your own data, no namespace lookups for your own
functions, no `interop::binary` on numbers you hold as `f64`/`Num`.

A module calling another enclosure module: `rt.import("<module>")?` gives its namespace (works whether that
module is typed or still generated). Once that module is converted (its file says `TYPED = true`), call its
`pub fn`s directly instead; until then, go through the namespace.

## Building and checking

1. Make your workspace: `$R/ws.sh <name> <module> [<module> ...]`. Your modules (named here, remembered in
   `$R/aws/<name>/.own`) and the shared runtime compile live from the real tree; every other finished module
   (`TYPED = true` in its file) is copied as it stands when you run `ws.sh`, so another agent's unfinished
   edits never break your build; every other module is a placeholder whose generated namespace runs. Re-run
   it when another agent finishes a module you call.
   Set `pub const TYPED: bool = true;` in your module file when it should run typed (a module with
   `TYPED = false` runs its generated code even if your file compiles).
2. Build: `$R/build.sh <name>` (through `tools/run.py`, which may queue behind other builds; the first build
   takes several minutes, later ones are incremental). It prints errors in your files and the binary's time.
   The binary is `$R/aws/<name>/target/release/enclosure-data`.
3. Which genrules run your module: `python3 $R/who.py <module>`. The full list is `$R/rules.txt`.
4. Compare genrules against the saved baseline:
   `python3 $R/compare.py <rule>[,<rule>...] <name>=$R/aws/<name>/target/release/enclosure-data`
   It prints one JSON line per rule; `differ_count` must be 0 and `status` `ok`. The label (`<name>`) names
   the clone directory `$R/work/<rule>.<name>.0`; a rule that differs keeps its clone so you can read the
   differing files (delete it afterwards); `--keep` keeps it anyway. The comparison masks only graph nodes'
   construction sites and the clone's own path. To see what a differing file held before, run the same rule
   with the baseline binary: `--direct` runs it beside yours (label `<name>-base`) and compares the two
   runs; use it when a rule has no manifest yet, and before chasing a difference in a part-program output
   (STEP, STL, mesh, npz), since other sessions edit those programs and the manifest may be stale.
5. Most genrules wait for the CAD lock or the host's run slots: run comparisons in the background
   (`run_in_background`) and check the quick ones first. Don't poll; you are notified when it finishes.
6. The namespace check: `python3 $R/names.py <module> $R/aws/<name>/target/release/enclosure-data` prints
   the module's names in order and the type of each value, typed against generated (exit 1 on a difference).
7. Code no genrule runs still has to be converted faithfully. Note which functions no genrule exercised.

## Report

Your final message: the modules you converted (with `TYPED = true`), each genrule you compared and its result
(files, differ count), the functions no genrule exercised, the names other code replaces that you read through
the namespace, anything you could not match, and any change you think a shared file needs.
