# Typed cold-core modules: how to port one

The cold-core-data crate runs 51 Python modules (hardware/printed-parts/cold-core and
hardware/cold-core-layout) as Rust. Today they are *generated* Rust that interprets Python
semantics over a dynamic `Val`/`Env` (src/compiled/*.rs). Each is being replaced by a
hand-written *typed* module in `tools/hsm/cold-core-data/src/typed/`: concrete structs,
f64/i64/String/arrays, typed function signatures, direct Rust calls between typed modules.
`Val` stays only at the adapter boundary (what Python sees) and for opaque library/provider
objects (CadQuery shapes, ezdxf documents, ReportLab canvases, Python providers).

The bar: every output file every build step writes stays byte-identical, and every module's
Python-visible namespace keeps the same names, in the same order, with the same values.

## Where things are

- Checkout (shared with other sessions; never run git commands that change anything):
  `/Users/derekbredensteiner/Developer/homesodamachine`
- Typed modules: `tools/hsm/cold-core-data/src/typed/<rust_name>.rs` (rust_name = module
  name without the leading underscore; `_foam_cap` → `foam_cap_parts.rs`, `_foam_shell` →
  `foam_shell_parts.rs`). Every module already has a placeholder file and is wired into
  `typed/mod.rs` (`members` and `entrypoint` dispatch). Do not edit `mod.rs`, `py.rs`,
  `cad.rs`, `above_core.rs`, `table.rs` or another group's module files.
- Runtime and helpers to read first: `typed/mod.rs` (Runtime, Module trait, docgen
  substitution, PDF/DXF export, namespaces), `typed/py.rs` (formatting, numbers, ToVal /
  FromVal, Obj, Call, Namespace, Dict, OMap, Num, paths), `typed/cad.rs` (CadQuery calls),
  `typed/above_core.rs` (the above-core placement provider).
- Finished examples to imitate: `typed/cold_core_interface.rs`, `typed/above_core_mounts.rs`,
  `typed/reservoir_b_fill.rs`, `typed/core_points.rs`, `typed/show_skin.rs`,
  `typed/water_inlet_jet.rs`.
- BEHAVIOR SOURCE (what the build runs today, wins on any disagreement):
  `tools/hsm/cold-core-data/src/compiled/<module>.rs`. Note `_core_presentation.rs` carries
  hand-written native helpers after its `entrypoint`; carry them over.
- Readable Python of the same modules (comments and all):
  `/private/tmp/claude-501/-Users-derekbredensteiner-Developer-homesodamachine/4eb08324-5815-43ac-91d1-37e7ae6e99d6/scratchpad/py/<repo path>`
  (or `git show a78cf15ba^:<repo path>`). Module → path: `RUN/deps.json` ("paths"; RUN is
  this directory). `python3 <scratchpad>/tools/bare.py <file> [start] [end]` prints the code
  without comments/docstrings, numbered.
- Names probe of today's behavior: `RUN/results/names-before.json`:
  `{module: {"names": [...in namespace order...], "values": {name: description}}}`.
  A description is `{"value": <encoded>}` (`$tuple`, `$dict` as `[[k, v], ...]`, `$set`,
  `$ref` for opaque objects), `{"native": "callable"|"namespace"}`, `{"module": "<python
  module>"}`, `{"python": "<module>.<qualname>"}` or `{"type": "<qualified type>"}`.
  `_reservoir_a_c2` is missing from it. Sets list in an arbitrary order there.

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
pub fn main(rt: &Runtime) -> Result<()> { /* the `if __name__ == "__main__":` block */ }
```

- `init` runs the module's top-level statements in order with their side effects:
  `sys.path.insert` (`rt.sys_path_insert(0, &path)`), Python imports (`rt.py("name")`
  imports through the adapter; a `from X import a, b` evaluates `rt.pya("X", "a")` in order),
  calls into `_stated_bounds` (`state(...)`, `bound(...)`, calling a bound), prints, file
  reads. Order matters: those calls register rows in scorecards and the read-trace.
- A module with no state can skip `State`. A typed module reads another typed module through
  its `state(rt)` / pub functions, never through its namespace. A module that the build
  reaches in a cycle (A's init calls B whose init reads A) needs care: see `rt.put` and
  `cold_core_interface::base` for how one module publishes a part of its state early.
- Lazy imports inside Python functions (`importlib.import_module("_cold_core_interface")`)
  become direct typed calls at call time.
- `members` gives Python exactly what the generated namespace gives: same names, order and
  values. Functions are `ns.func(rt, "name", |rt, c| ...)` binding arguments like the
  Python signature: `c.req::<T>(index, "name")` positional-or-keyword, `c.opt(index, "name",
  default)` with a default, `c.kw("name", default)` keyword-only with default,
  `c.req::<T>(usize::MAX, "name")` keyword-only required, `c.rest(from)` for `*args`.
  Values: `ns.value("NAME", x)` (anything ToVal). Python modules/members:
  `ns.module(rt, "math", "math")`, `ns.python(rt, "lru_cache", "functools", "lru_cache")`
  (the generated `rt.member(...)` form → probe says `{"python": ...}`), types/callables from
  Python providers as `Val`. A Python module `__getattr__` becomes a `"__getattr__"` func.
  Loop variables left at module level (`_name`, `_row`, `_a`) are names too: give them their
  final value.
- Return values to Python with the same shapes: tuple vs list (`[f64; N]`→tuple,
  `Vec<T>`→list, `(a, b)`→tuple, `Val::Tuple`, `Val::list`), dict key order (Dict/OMap keep
  insertion order), int vs float.

## Fidelity rules (outputs must stay byte-identical)

- Floating point: same operations in the same order and association as the source
  (`a + b + c` is `(a + b) + c`). `x ** 2` → `x.powf(2.0)`; `math.sqrt` → `.sqrt()`;
  `math.hypot(a, b, ...)` → `hypot(&[a, b, ...])`; `math.dist` → `dist`; `math.radians` /
  `math.degrees` → `radians` / `degrees` (they compute `x*PI/180`, keep them);
  `math.isclose` → `isclose`; `sum` → `fsum` (left fold from 0); `min`/`max` of two →
  `pmin`/`pmax`, of many → `fmin`/`fmax` (both keep the first of equals); `%` → `pymod`;
  `//` → `(a / b).floor()`; `abs`, `sin`, `cos`, `atan2`, `acos` map directly.
- Ints stay ints where Python has ints: literals (`2`, `(0, 0, 0)`), `len`, `int(...)`,
  `round(x)` (→ `round_int`, ties to even) and data read from JSON / providers that may hold
  ints (above-core.json rotations, translations). When an int-or-float value can reach an
  output (a JSON number, a printed number, a returned value), keep it as `Val` or `Num`.
  `round(x, n)` → `round_to(x, n)`.
- Text: f-string fields `{x:.3f}` → `ff(x, ".3f")`, `{n:d}` → `fi(n, "d")`, any value →
  `fv(&val, spec)`; plain `{x}` / `str(x)` of a float → `pystr(x)` (Python repr), of a Val →
  `val.str()?`, `repr` → `val.repr()?`. Lists of strings printed via `str(list)` →
  `repr_strs`. `print(a, b)` → `rt.print(format!("{a} {b}"))` (Python joins with spaces).
- Exceptions: `raise ValueError(msg)` → `bail!("{msg}")` with the same text; `assert c, m` →
  `ensure!(c, "{m}")`. `try/except` around something that may fail must keep catching it.
- Paths: `Path(__file__).resolve()` → `resolve(&rt.file(NAME))`; `.parent` / `.parents[n]`
  → `parent()` / `parent_n(p, n)`; `next(p for p in X.parents if p.name == "hardware")` →
  `ancestor(&X, "hardware")?`, other predicates → `ancestor_where`; `str(p)` → `ps(&p)`;
  `p.read_text()` → `read_text(&p)?` and `p.write_text(t)` → `write_text(&p, &t)?` (both
  record the read/write the build traces; never use std::fs directly for those).
  `json.loads` / `json.dumps(obj, **kw)` → `json_loads` / `json_dumps(&val, kw![...])`.
  A Path value Python sees is `Val::Path(...)`.
- Documents: `from docgen import substitute_md` then `substitute_md(path, variables=v)` →
  `rt.substitute_md(&path, &vars, caller)`; same for `substitute_py_comments`. `vars` is
  `Vec<(String, String)>` holding `str()` of each value. `caller` is the module whose code
  ran the `from docgen import ...`: `Some(NAME)` when that statement sits in a module-level
  statement or inside a function of this module, `None` when it sits in the `__main__`
  block itself. `_document_export.export_pdf(draw, target)` → `rt.export_pdf(&target,
  |tmp| ...)`; `export_dxf(doc, target)` → `rt.export_dxf(&doc, &target)`.
- `from collections import namedtuple`: the generated runtime passes `module=<the importing
  module>`; use `rt.namedtuple("Name", "a b c", NAME)` (a Python type, a Val). Instances:
  `ty.c(args![...])`.
- `@lru_cache` / `@functools.cache`: the generated code drops these; the typed module keeps a
  cache in its state (`RefCell<Option<...>>`, or a small Vec keyed by argument) and returns
  the cached value, as the Python source does.
- CadQuery / OCP / ezdxf / reportlab / numpy etc. stay Python objects (`Val`), called in the
  same order with the same arguments: `cq.m("Workplane")`, `shape.m("cut", args![tool])`,
  `x.mk("method", args![...], kw!["k" => v])`, `x.a("attr")`, `f.c(args![...])`. Int
  literals the source passes (`(0, 0, 0)`, `-90`) can stay ints. Compute every number in
  Rust; never call Python for arithmetic.
- Values read from Python providers (fits, valve_seat, above_core.specification(), stock
  modules) are read once in `init` (snapshot containers with `own(&val)?`), typed where the
  module computes with them, kept as `Val` where they pass through to outputs.
- Iteration order: Python dicts keep insertion order (use OMap / Vec of pairs, not HashMap);
  Python sets in the generated runtime also keep insertion order (`Val::set_values`);
  `sorted(...)` sorts with Python's ordering (tuples lexicographic, strings by code point).

## Calls between modules

Call typed pub functions of modules that are already typed in the shared `typed/` dir.
For a module that is still a placeholder, or owned by another group, go through its
namespace (`rt.import_module("_x")?.a("f")?.c(args![...])`, `.a("CONST")?`) and mark the line
`// via namespace: _x` so it can be made a direct call later. Never edit another group's
files.

## Building

Each group has its own build tree: `RUN/agents/<g>/tree/tools/hsm` (its `typed/` holds
symlinks to the shared typed files plus real copies of the group's own files) and its own
target dir `RUN/agents/<g>/target`. Edit your files in `RUN/agents/<g>/tree/tools/hsm/cold-core-data/src/typed/`.
Type-check with:

```sh
cd RUN/agents/<g>/tree/tools/hsm && PATH=/opt/homebrew/opt/rustup/bin:/opt/homebrew/bin:$PATH \
  CARGO_TARGET_DIR=RUN/agents/<g>/target python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- \
  cargo check --release -j2 -p hsm-cold-core-data --features typed --message-format short
```

(run it in the background; the Mac is shared and the wrapper may queue it). Check after a
module is written, not after every edit. When a module type-checks, copy it over its
placeholder in the shared dir (`cp <file> /Users/derekbredensteiner/Developer/homesodamachine/tools/hsm/cold-core-data/src/typed/`)
and replace your copy in the build tree with a symlink to the shared file. Warnings about
unused items are fine. Add no dependencies, no build scripts, no tests, no checks.
