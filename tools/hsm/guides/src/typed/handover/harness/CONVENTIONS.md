# Typed guide modules: how to port one

The guides crate (`tools/hsm/guides`) runs 22 Python modules of the owner and install guides
(`tools/install-guide/*.py`, `hardware/install-guide/**.py`, `tools/faucet-assembly-guide/build.py`,
`tools/assembly-guides/common.py`) as Rust. Today they are *generated* Rust that interprets
Python semantics over a dynamic `Val`/`Env` (`src/compiled/modules/*.rs`). Each is being
replaced by a hand-written *typed* module in `tools/hsm/guides/src/typed/`: concrete structs,
f64/i64/String/arrays, typed function signatures, direct Rust calls between typed modules.
`Val` stays only at the adapter boundary (what Python sees) and for opaque library objects
(ReportLab canvases and flowables, Pillow images, pypdf readers, numpy arrays, CadQuery shapes,
the Python helper modules such as `_rust_part`, `_hsm_render`, `_mesh_payload`).

The bar: every output file every build step writes stays byte-identical (PNG, SVG, PDF, JSON,
STEP payloads), and every module's Python-visible namespace keeps the same names, in the same
order, with the same values.

## Where things are

- Checkout (shared with other sessions; never run git commands that change anything):
  `/Users/derekbredensteiner/Developer/homesodamachine`. RUN below is this directory,
  `/Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-guides-202611041900`.
- Typed modules: `tools/hsm/guides/src/typed/<rust_name>.rs` (rust_name = module name
  without the leading underscore: `_cad_art` → `cad_art.rs`, `_install_art_mesh` →
  `install_art_mesh.rs`). Every module already has a placeholder file and is wired into
  `typed/mod.rs` (`members` and `entrypoint` dispatch). Do not edit `mod.rs`, `py.rs`,
  `table.rs`, `native.rs` or another group's module files.
- Runtime and helpers to read first: `typed/mod.rs` (Runtime, Module trait, Python imports,
  `python_type`, `native`, `shutil`, docgen substitution, PDF export, namespaces) and
  `typed/py.rs` (formatting, numbers, ToVal / FromVal, Obj, Call, Namespace, Dict, OMap, Num,
  paths). `src/native.rs` holds the Rust guide primitives (`_guide_native`, `shutil`).
- Finished typed modules of another crate to imitate (same helper layer):
  `tools/hsm/cold-core-data/src/typed/cold_core_interface.rs`, `above_core_mounts.rs`,
  `reservoir_b_fill.rs`, `core_points.rs`.
- BEHAVIOR SOURCE (what the build runs today, wins on any disagreement):
  `tools/hsm/guides/src/compiled/modules/<module>.rs`, its runtime `src/compiled.rs`.
- Readable Python, comments and all:
  `/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/4eb08324-5815-43ac-91d1-37e7ae6e99d6/scratchpad/py-guides/<module>.py`
  (`faucet_book.py` is `tools/faucet-assembly-guide/build.py`). It is the Python *before* the
  generator ran; the generator's input had small later edits (new helpers such as
  `_plumbing_art_mesh._plain` and `plumbing_scenes._plumbing_data`, changed docstrings,
  changed bodies). Read the Python for intent, then check every function against the
  generated code, which is what you must reproduce.
- The Python stub each module keeps (what Python imports today): the module's repo path
  (`table.rs` `source()`). Classes stay in the stub as Python classes; their methods call the
  compiled functions named `"Class.method"` with `self` first.
- Names probe of today's behavior: `RUN/results/names-before.json`:
  `{module: {"names": [...in namespace order...], "values": {name: description}}}`.
  A description is `{"value": <encoded>}` (`$tuple`, `$dict` as `[[k, v], ...]`, `$set`,
  `$ref` for opaque objects), `{"native": "function"|"namespace"|...}`, `{"module": "<python
  module>"}`, `{"python": "<module>.<qualname>"}` or `{"type": "<qualified type>"}`.

## Module shape

```rust
use super::*;                       // runtime, helpers, Val, Result, bail!, ensure!, args!, kw!, dict!
pub const NAME: &str = "_module";   // the Python module name

pub struct State { /* every module-level binding the module or its callers read, typed */ }
impl Module for State {
    const NAME: &'static str = NAME;
    fn init(rt: &Runtime) -> Result<Self> { /* the top-level statements, in source order */ }
}
pub fn state(rt: &Runtime) -> Result<Rc<State>> { rt.state::<State>() }

pub fn some_function(rt: &Runtime, x: f64, name: &str) -> Result<...> { ... }   // typed API

pub fn members(rt: &Runtime, ns: &mut Namespace) -> Result<()> {
    // every name of the probe, in the probe's order, after __name__/__file__/__doc__ (the
    // runtime sets those three)
}
pub fn main(rt: &Runtime) -> Result<()> { /* the `if __name__ == "__main__":` block; Ok(()) if none */ }
```

- `init` runs the module's top-level statements in order with their side effects:
  `sys.path.insert` (`rt.sys_path_insert(0, &path)`), Python imports (`rt.py("name")`
  imports through the adapter; `from X import a, b` evaluates `rt.pya("X", "a")` in order),
  prints, file reads. Order matters: imports run Python module code, and reads land in the
  build's read trace.
- A module with no state can skip `State`. A typed module reads another typed module through
  its `state(rt)` / pub functions, never through its namespace.
- `members` gives Python exactly what the generated namespace gives: same names, order and
  values. Functions are `ns.func(rt, "name", |rt, c| ...)` binding arguments like the
  generated signature: `c.req::<T>(index, "name")` positional-or-keyword, `c.opt(index,
  "name", default)` with a default, `c.kw("name", default)` keyword-only with default,
  `c.req::<T>(usize::MAX, "name")` keyword-only required, `c.rest(from)` for `*args`.
  Methods are `ns.func(rt, "Class.method", ...)` with `self` (a `Val` reference to the Python
  instance) as argument 0. Values: `ns.value("NAME", x)` (anything ToVal). Python modules /
  members: `ns.module(rt, "json", "json")`, `ns.python(rt, "Path", "pathlib", "Path")`.
  A class the stub keeps: `ns.value("Art", rt.python_type("common", "Art")?)`. A name bound
  by `from docgen import substitute_md`: `ns.value("substitute_md",
  rt.docgen_member("substitute_md", Some(NAME))?)`. Names `_guide_native` / `shutil`:
  `ns.value("x", rt.import_module("_guide_native")?)`.
  Loop variables left at module level are names too: give them their final value.
- Return values to Python with the same shapes: tuple vs list (`[f64; N]`→tuple,
  `Vec<T>`→list, `(a, b)`→tuple, `Val::Tuple`, `Val::list`), dict key order (Dict/OMap keep
  insertion order), int vs float, `Path` vs `str`.
- Arguments the stub passes by reference (`mutable=` in the stub: `insertion_actions.
  moved_payload` argument 1 `entry`, `preflight.Preflight.resource_checks` arguments 4 `fonts`
  and 5 `visited`) arrive as `Val` references to the caller's Python object; mutate them
  through `Val` (`set`, `.m("add", ...)`, `.m("append", ...)`), never on a snapshot.

## Fidelity rules (outputs must stay byte-identical)

- Floating point: same operations in the same order and association as the source
  (`a + b + c` is `(a + b) + c`). `x ** 2` → `x.powf(2.0)`; `math.sqrt` → `.sqrt()`;
  `math.hypot(a, b, ...)` → `hypot(&[a, b, ...])`; `math.dist` → `dist`; `math.radians` /
  `math.degrees` → `radians` / `degrees` (they compute `x*PI/180`, keep them);
  `math.isclose` → `isclose`; `sum` → `fsum` (left fold from 0); `min`/`max` of two →
  `pmin`/`pmax`, of many → `fmin`/`fmax` (both keep the first of equals); `%` → `pymod`;
  `//` → `(a / b).floor()`; `abs`, `sin`, `cos`, `atan2`, `acos` map directly. Check the
  generated code for how each builtin was lowered (`builtin("round")`, `binary("**", ...)`)
  and reproduce that lowering, not CPython's.
- Ints stay ints where Python has ints: literals, `len`, `int(...)`, `round(x)` (→
  `round_int`, ties to even), data read from JSON. When an int-or-float value can reach an
  output (a JSON number, an SVG/PDF number, a printed number, a returned value), keep it as
  `Val` or `Num`. `round(x, n)` → `round_to(x, n)`.
- Text: f-string fields `{x:.3f}` → `ff(x, ".3f")`, `{n:d}` → `fi(n, "d")`, any value →
  `fv(&val, spec)`; plain `{x}` / `str(x)` of a float → `pystr(x)` (Python repr), of a Val →
  `val.str()?`, `repr` → `val.repr()?`. `print(a, b)` → `rt.print(format!("{a} {b}"))`.
  SVG and PDF text is output: format every number exactly as the generated code does.
- Exceptions: this runtime turns `ValueError(msg)` into the text `"ValueError: msg"` (any
  `*Error`, `Exception`, `SystemExit`, `StopIteration`); `raise ValueError(msg)` →
  `bail!("ValueError: {msg}")`. `assert c, m` → `ensure!(c, "{m}")`. A `try/except` around
  something that may fail must keep catching it (see how the generated `attempt`/`outcome`
  closures treat the error: most swallow every error).
- Paths: `Path(__file__).resolve()` → `resolve(&rt.file(NAME))`; `.parent` / `.parents[n]`
  → `parent()` / `parent_n(p, n)`; `str(p)` → `ps(&p)`; `p.read_text()` → `read_text(&p)?`
  and `p.write_text(t)` → `write_text(&p, &t)?` (both record the read/write the build
  traces). Where the generated code calls a Python `Path` method (`mkdir`, `exists`,
  `unlink`, `glob`, `relative_to`, `stat`), keep the observable effect: file system calls in
  the same order, the same paths recorded. `json.loads` / `json.dumps(obj, **kw)` →
  `json_loads` / `json_dumps(&val, kw![...])`. A Path value Python sees is `Val::Path(...)`.
- `_guide_native.<f>` → `rt.native("<f>")?.c(args![...])`; `shutil.copyfile/copy2/which` →
  `rt.shutil("copyfile")?.c(args![...])` (the generated runtime routes `shutil` to these Rust
  primitives, which record the copy for the build trace).
- Documents: `substitute_md(path, variables=v)` → `rt.substitute_md(&path, &vars, caller)`.
  `vars` is `Vec<(String, String)>` holding `str()` of each value. `caller` is the module whose
  code ran the `from docgen import ...`: `Some(NAME)` when that statement sits at module level
  or inside a function of this module, `None` when it sits in the `__main__` block itself.
  `_document_export.export_pdf(draw, target)` → `rt.export_pdf(&target, |tmp| ...)`.
- `with ctx as x:` → `with(&ctx, |x| { ... })` (py.rs): the generated runtime calls
  `__exit__(None, None, None)` after the body even when the body fails, then propagates.
- `from collections import namedtuple` → `rt.namedtuple("Name", "a b c", NAME)`.
- `@lru_cache` / `@functools.cache`: if the generated code drops the decorator, the typed
  module keeps a cache in its state (`RefCell<Option<...>>`, or a small Vec keyed by
  argument) and returns the cached value, as the Python source does.
- Library objects stay Python objects (`Val`), called in the same order with the same
  arguments: `c.m("drawString", args![x, y, text])`, `img.mk("save", args![path],
  kw!["optimize" => true])`, `x.a("attr")`, `f.c(args![...])`. Compute every number in Rust;
  never call Python for arithmetic or string work. Call order of anything with an effect
  (drawing, writing, `_rust_part.run`, `_hsm_render` calls, note_read/note_write) must match.
- Iteration order: Python dicts keep insertion order (use OMap / Vec of pairs, not HashMap);
  sets in the generated runtime keep insertion order; `sorted(...)` sorts with Python's
  ordering (tuples lexicographic, strings by code point). `os.walk`/`glob` results keep the
  order the generated code gets from Python.

## Calls between modules

Call typed pub functions of modules that are already typed in the shared `typed/` dir.
For a module that is still a placeholder, or owned by another group, go through its
namespace (`rt.import_module("_x")?.a("f")?.c(args![...])`, `.a("CONST")?`) and mark the line
`// via namespace: _x` so it can be made a direct call later. Never edit another group's
files.

## Building

Each group has its own build tree: `RUN/agents/<g>/tree/tools/hsm` (its `guides/src/typed/`
holds symlinks to the shared typed files plus real copies of the group's own files) and its
own target dir `RUN/agents/<g>/target`. Edit your files in
`RUN/agents/<g>/tree/tools/hsm/guides/src/typed/`. Type-check with:

```sh
cd RUN/agents/<g>/tree/tools/hsm && PATH=/opt/homebrew/opt/rustup/bin:/opt/homebrew/bin:$PATH \
  CARGO_TARGET_DIR=RUN/agents/<g>/target python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- \
  cargo check --release -j2 -p hsm-guides --features typed --message-format short
```

(run it in the background; the Mac is shared and the wrapper may queue it). Check after a
module is written, not after every edit. When a module type-checks, copy it over its
placeholder in the shared dir (`cp <file> /Users/derekbredensteiner/Developer/homesodamachine/tools/hsm/guides/src/typed/`)
and replace your copy in the build tree with a symlink to the shared file. Warnings about
unused items are fine. Add no dependencies, no build scripts, no tests, no checks.

## Checking your work

When your group's modules are all written and type-check, check them once against today's
behavior (not after every edit):

1. Build your binary and freeze a copy the pins point at:

   ```sh
   cd RUN/agents/<g>/tree/tools/hsm && PATH=/opt/homebrew/opt/rustup/bin:/opt/homebrew/bin:$PATH \
     CARGO_TARGET_DIR=RUN/agents/<g>/target python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- \
     cargo build --release -j2 -p hsm-guides --features typed --bin guides --message-format short \
     && cp -c RUN/agents/<g>/target/release/guides RUN/agents/<g>/guides-typed
   ```

2. Names probe of your modules (`PROBE_MODULES` = your module names, comma-separated):

   ```sh
   cd RUN/work/probe-union && PROBE_MODULES=<m1>,<m2> PYTHONPATH=RUN/pinhook \
     HSM_PINS=RUN/agents/<g>/pins.json HSM_REPO_ROOT=RUN/work/probe-union HSM_INPUT_DIGEST=probe \
     HSM_WORKSPACE=/Users/derekbredensteiner/Developer/homesodamachine \
     python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py --cad -- \
     /Users/derekbredensteiner/Developer/homesodamachine/tools/cad-venv/bin/python RUN/probe_names.py \
     RUN/agents/<g>/pins.json RUN/results/names-<g>.json
   cd RUN && python3 compare_names.py results/names-before.json results/names-<g>.json <m1> <m2>
   ```

   `common`, `faucet_book`, `preflight`, `hold_scene`, `fill_scene`, `ice_scene` are not in
   any build step's inputs: probe those from the checkout root instead
   (`cd /Users/derekbredensteiner/Developer/homesodamachine`, drop `HSM_REPO_ROOT` and
   `HSM_INPUT_DIGEST`). The probe only imports modules and reads names; it writes nothing.

3. Build steps (byte identity of every file a step leaves). Steps and the modules they
   reach: `render-modern-tee`, `plumbing-scenes` (group a); `kit-art`, `opening-scene`
   (groups a and b); `install-guide-build` (group c). A step whose modules are not all typed
   yet fails at a placeholder; run it once they are:

   ```sh
   cd RUN && python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- \
     python3 run.py after-<g> agents/<g>/pins.json <step> [<step> ...]
   cd RUN && python3 compare.py before after-<g> <step> [<step> ...]
   ```

   `results/after-<g>/<step>.json` has each script's stderr on failure. Add `--keep` to keep
   the work dir (`RUN/work/<step>`; runs of one step take turns) for inspecting a differing file; delete it when
   done. Never write into the checkout itself.
