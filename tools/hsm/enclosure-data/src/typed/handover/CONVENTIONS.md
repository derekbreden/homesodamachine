# Typed enclosure-data: translation conventions

Workspace: `$R = /Users/derekbredensteiner/Developer/homesodamachine/.cache/runs/typed-enclosure-202611041700`.
Write code only under `$R/ws/tools/hsm/enclosure-data/src/` (a private copy of the crate).
Never edit the shared checkout `/Users/derekbredensteiner/Developer/homesodamachine` itself.

## What is being replaced

`tools/hsm/enclosure-data/src/compiled/<module>.rs` are generated: Python transpiled onto a
dynamic value runtime (`hsm_documents::interop::Val`, `Env` name lookups, `Val::call`). Each
becomes typed Rust in `src/recipes/<module>.rs` (or a `src/recipes/<module>/` directory):
structs, enums, `f64`/`i64`, typed function signatures, direct calls.

**Behavior source**: the generated file at HEAD. It is the Python at `392a60abc` transpiled,
plus these later edits (read them in the generated file):
- `_enclosure_back_top`: `receiver` calls `crate::nameplate_snap::apply(graph, piece, plan, wing)`
  and the disposal field reads `identification.nameplate_station()` and the plan's `face_y_mm`.
- `nameplate`: `numbers()` returns `crate::nameplate_snap::numbers(<dict>)`.

Read the Python with `git -C /Users/derekbredensteiner/Developer/homesodamachine show 392a60abc:<path>`
(paths in `$R/modules.txt`; copies in `$R/py/`). Its docstrings and comments are the design
record: carry every docstring as a `///` doc comment (module docstring as `//!`) and keep the
comments, edited only to name the Rust items.

Every output must stay byte-identical, so the arithmetic must give the same bits.

## Arithmetic: use `crate::py`

The generated runtime evaluates in `f64`, left to right, as Python does. Keep Python's operand
order and grouping exactly (`a + b + c` is `(a + b) + c`; never reassociate, never fold
constants, never replace `x ** 2` with `x * x`, never use `mul_add`). Differences from plain
Rust that matter:

| Python | Rust |
|---|---|
| `math.radians(x)` | `py::radians(x)` (`x * PI / 180.`) |
| `math.degrees(x)` | `py::degrees(x)` |
| `math.hypot(a, b, ...)` | `py::hypot(&[a, b, ...])` / `py::hypot2(a, b)` |
| `math.dist(a, b)` | `py::dist(&a, &b)` |
| `sum(floats)` | `py::sum(iter)` (left fold from 0) |
| `min(...)`/`max(...)` | `py::min`, `py::max`, `py::min2`, `py::max2`, `py::min_by_key`, `py::max_by_key` (first of the best; never `f64::min`) |
| `sorted(...)` | `py::sorted`, `py::sorted2`, `py::sorted_by_key` (stable) |
| `x // y`, `x % y` (floats) | `py::floordiv`, `py::modulo`; ints `py::ifloordiv`, `py::imodulo` |
| `x ** y` | `py::pow(x, y)` (`powf`; also for integer exponents) |
| `round(x)` | `py::round(x) -> i64` (ties to even) |
| `round(x, d)` | `py::round_to(x, d) -> f64` (always a float) |
| `math.floor/ceil/trunc` | `py::floor/ceil/trunc -> i64` |
| `math.isclose(a, b, rel_tol=r, abs_tol=t)` | `py::isclose(a, b, r, t)` (defaults `1e-9`, `0.0`) |
| `abs(int)` | stays `i64` |
| `str(float)`, `repr(float)`, `f"{x}"` | `py::float_text(x)` |
| `f"{x:.3f}"`, `format(x, spec)` | `py::format(x, ".3f")` |
| `math.sqrt/sin/cos/atan2/...` | the `f64` method |
| `math.pi` | `py::PI` |

Integer arithmetic: `i64`. `int / int` is a float. A mixed int/float operation is a float.

## Types

- A Python float is `f64`. A Python int is `i64` wherever it can reach a document, a printed
  number, a dict key or a comparison that keys on type; otherwise convert where Python would.
  **Integer literals stay integers**: `_ybox(0, depth, ...)` passes the integer `0`, and a
  recipe document writes it as `0`, not `0.0`. A parameter that receives ints from some callers
  and floats from others is `py::Num`.
- A fixed-length tuple is an array `[f64; 6]` or a Rust tuple; a list is `Vec<T>`. When a value
  reaches a document or the Python side, a tuple must arrive as a tuple and a list as a list
  (`py::IntoVal`: arrays and Rust tuples become tuples, `Vec` becomes a list).
- A dict with fixed keys is a struct. A dict used as a map keeps insertion order: `Vec<(K, V)>`
  or a small ordered map; never `HashMap` iteration order.
- `None`-able is `Option<T>`.
- A Python object the recipes only hand on (a third-party value, another worker's proxy) is held
  as `Val` and touched only through a small typed wrapper.
- A function returns `Result<T>` only where it can fail (a callback to Python, an explicit
  raise, a lookup that can miss). Pure arithmetic returns `T`.
- Naming: Python `_band_x` becomes `band_x`; module-level numbers become fields of the module's
  constants struct or `const` items; `CamelCase` classes become structs of the same name.

## Construction graphs

`_enclosure_panel._Graph` / `_Shape` are `crate::graph::{Graph, Shape}` (written; read
`src/graph.rs`). `Shape::cut1`, `fuse1`, `intersect1`, `translate`, `rotate`, `mirror`,
`bounding_box`; `Graph::boxed`, `box6`, `cylinder`, `prism`, `rounded`, `add`, `document`.
Bounds are `[Num; 6]` because a box written from integer literals keeps them.
Builder methods are `#[track_caller]`: a node records the Rust line that asked for it. Leaf
functions that build nodes are `#[track_caller]` too, so the site is the recipe's call.

Vectors, planes and placements: `crate::datums::{Vector, Plane, Location}` (written).

## Calls to Python

Python-side helpers the recipes call (`_rust_part.cut`, `_materials.linear`, `docgen`,
third-party libraries) stay calls into Python through `hsm_documents::interop::callback`.
Wrap each in one typed function in `src/python.rs` (shared) so recipes never build `Val` calls.

## Module-level values and overrides

Module-level numbers that are literals are `const` items. Values read from other modules or
from Python at import are fields of a struct built once per run (`thread_local!` +
`OnceCell`). Where a context swaps a module function for another (`_record`, `_leaves`,
`_replace`, `_dock_recipe`), the swappable function is a slot: a `thread_local!` table of typed
closures with the original as default, set and restored by the context.

## Checking your work

`cd $R/ws/tools/hsm && PATH=/opt/homebrew/opt/rustup/bin:$PATH CARGO_TARGET_DIR=$R/target-check python3 /Users/derekbredensteiner/Developer/homesodamachine/tools/run.py -- cargo check -j2 --offline -p hsm-enclosure-data`
Use `cargo check`, not `cargo build`, while translating. Run nothing else heavy.
