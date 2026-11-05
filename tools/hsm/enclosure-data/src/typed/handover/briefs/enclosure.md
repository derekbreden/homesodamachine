# enclosure: the enclosure source, in five parts

`enclosure` (`$R/py/enclosure.py`, 8,543 lines; generated `compiled/enclosure.rs`, 31,539 lines) is the
`shell` every enclosure recipe reads. Five agents convert it in parallel, each one part:

| part | agent | Python lines | what |
|---|---|---|---|
| root | `e1` | the whole top level | `$T/enclosure.rs`: `State`, `Cx`, install (hybrid and final), the namespace order |
| p1 | `e1` | 118–2116 | `$T/enclosure/p1.rs` |
| p2 | `e2` | 2117–3500 | `$T/enclosure/p2.rs` |
| p3 | `e3` | 3501–4993 | `$T/enclosure/p3.rs` |
| p4 | `e4` | 4994–6595 | `$T/enclosure/p4.rs` |
| p5 | `e5` | 6596–8543 | `$T/enclosure/p5.rs` |

Your part is the module-level functions (`def`s) whose first line is in your range, with everything nested
in them. Every top-level statement that is not a `def` (imports, constants, namedtuples, the 29 slots) is
the root's, wherever it stands. `$R/enclosure-functions.json` maps every function: its part, Python and
generated line ranges, parameters and defaults, the module functions it calls (and their parts), the
constants it reads, the slots it calls and the other modules' attributes it reads.

## How the parts run before the whole module is typed

`$T/enclosure.rs` is the root. In the hybrid build its install first runs the generated module
(`rt.generated_base("enclosure")`) and adopts that namespace as the module's, so every generated function
is there; then it builds the module's `Cx` and replaces, in that same namespace, every function a part
lists in its `CONVERTED` with that part's typed wrapper. A generated caller looks the name up at call time
and reaches the converted function; a converted function reaches an unconverted one through its fallback.
In the final build (no `hybrid` feature) there is no generated module: the root runs the
whole top level typed, in source order, and every function must be converted.

```rust
pub struct Cx {
    pub rt: Rt,    // the registry
    pub ns: Ns,    // the module namespace: replaceable names are read here at every use
    pub s: State,  // every module constant, typed, one field per Python name
}
```

A function of the module is `pub fn <python_name>(cx: &Cx, <typed parameters>) -> Result<<typed result>>`
(keep the Python name, leading underscore and all; `#[allow(non_snake_case)]` where needed). Call any
module function, in any part, directly by that signature: `super::p3::_z_rail_heads(cx, ..)`. Read a
constant as `cx.s.<name>`.

Each part file has:

```rust
/// The functions of this part that run typed: the hybrid build replaces exactly these.
pub const CONVERTED: &[&str] = &[..];
/// A function of this part as a Python-callable value: its wrapper binds the Python signature
/// (positional names, defaults evaluated once, keyword-only parameters, *args, **kwargs), converts the
/// arguments, calls the typed function and converts its result.
pub fn function(cx: &Rc<Cx>, name: &str) -> Option<Result<Val>>
```

`$T/py.rs` has the trait `Py` (`to_py` / `from_py`) for the boundary conversions: `f64`, `i64`, `bool`,
`String`, `()`, `Num`, `Val`, `Option<T>`, `Vec<T>` (a list), `Tup<T>` (a tuple of any length), Rust
tuples and `[T; N]` (tuples); `py_args![a, b, ..]` builds positional arguments. Implement `Py` for the
types you add (a namedtuple's struct, a record).

## Work in two phases

**Phase 1, signatures (first).** For every function in your part, write its final typed signature
with a fallback body that calls the generated function:

```rust
/// <the Python docstring>
pub fn _lip_band(cx: &Cx, y_side: &str, z_side: &str, x0: f64, x1: f64) -> Result<Solid> {
    cx.generated("_lip_band", py_args![y_side.to_owned(), z_side.to_owned(), x0, x1], vec![])
}
```

`cx.generated(name, args, kwargs)` (hybrid only) calls the namespace's generated function and converts
its result with `Py::from_py`. `$R/enclosure-sigs-draft.md` drafts every function's signature from the
observed types, with the parts and modules that call it and the steps that ran it; settle each against
the Python: `f64` for a float, `Num` where an int or a
float may arrive and reach output, `&str`/`String`, tuples or arrays for fixed tuples, `Vec` for lists,
the solid type for solids (below), a struct for a record that has fields (the module's namedtuples
`Box`, `Pack`, `Bound`, `PortField`, `BoxReadings`, `_ReadingBounds` are the root's: `e1` defines their
structs first), `Val` only for a provider object or a value whose shape the Python leaves open. A
function that takes a callable takes `&dyn Fn(..) -> Result<..>` (or `&Val` when Python code hands it in).

Build, then write `## Signatures` at the top of `$R/notes/<name>.md`: done, with any signature that needed
a decision. Other parts call your signatures as soon as you publish them: if you change one, fix every
caller in every part and list the change in your notes and report.

**Phase 2, bodies.** Replace each fallback with the typed body and add the function to `CONVERTED` and
`function`. Call other parts' functions directly by their signatures (a part not yet through phase 1:
read its notes, or call through `cx.generated` until it is). Re-run `ws.sh` to take the other parts'
latest files.

## The root (`e1`) goes first

`$T/enclosure.rs` exists with `Cx`, `State` (one field per module constant, typed as the value the
generated top level holds; read from the generated namespace in the hybrid build: `State::from_ns`), the
hybrid install and the registration loop. `e1`'s first job, before phase 1 of `p1`:

1. The namedtuple structs (`Box`, `Pack`, `Bound`, `PortField`, `BoxReadings`, `_ReadingBounds`) with `Py`
   (the namespace keeps the namedtuple classes the generated code makes; a struct's `to_py` makes an
   instance of that class, `from_py` reads one), and any `State` field type the others will need to change
   from `Val`. Publish (`## Root` in `$R/notes/e1.md`) as soon as it builds.
2. The typed top level: compute every constant in Rust, in source order, from the same inputs. In the
   hybrid build, `State::compute` runs after the generated top level and every field must equal the
   generated namespace's value (check it in your own testing; nothing permanent).
3. The final install (`#[cfg(not(feature = "hybrid"))]`): every top-level statement in source order,
   setting each name as the generated `initialize` does (imports under their aliases, constants,
   functions through each part's `function`, the namedtuple classes, the 29 slots as `None`), with no
   generated module. It cannot run until every part is converted; write it so it compiles.

## Solids, slots and the replaceable names

The graph agent (`_enclosure_panel`, `_rust_enclosure_checks`) is designing the solid type and the leaf
calls now; its API goes into `$R/notes/graph.md` under `API` (and the top of `$T/_enclosure_panel.rs`).
Until that section exists, do the functions that hold no solids (about two thirds of them: the draft
marks the rest `Solid`), then take the solid ones from the API.

The 29 slots (`_ybox`, `_xcyl`, ... `disposal_letters`), `_teardrop_y`, `record_bound` and `cq` are
replaced by the recorders and by machine-data while they call this module: read them from `cx.ns` at
every use, through the graph API's leaf call, never cached.

## Checking

Your part compiles only once the root runs typed: before your first build, check that `$T/enclosure.rs`
says `pub const TYPED: bool = true;` (the orchestrator sets it once the root matches the generated
module); until then, read and write code.

`$R/ws.sh <name> enclosure/p<k>` (e1 also `enclosure`). Build as GUIDE.md says. Compare
`enclosure-dimensions` first (fast), then `enclosure-box`, `enclosure-assembly` and `enclosure`
(15 minutes of wall time; run them in the background and keep converting). `python3 $R/names.py enclosure
<binary>` checks the namespace (it must stay identical in both builds).
