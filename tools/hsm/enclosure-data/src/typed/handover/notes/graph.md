# graph: the construction-graph core

Modules: `_enclosure_panel` (the API lives here), `_rust_enclosure_checks`, `_enclosure_pump_retainer`,
`_enclosure_rust_driver`. Workspace `$R/aws/graph`. The doc comments at the top of
`$T/_enclosure_panel.rs` and `$T/_rust_enclosure_checks.rs` say the same as this section.

## API

`P` = `super::_enclosure_panel`, `C` = `super::_rust_enclosure_checks`.

### Values

- `P::Graph`: a native `_Graph` (`Graph::new()`) or `_Questions` (`Graph::questions(answers)`, `answers`
  `Val::None` while collecting). Cheap to clone (one `Rc`).
  - `g.add(op, &[usize], Option<Bounds>, vec![("name", val), ..]) -> Shape`: one node,
    `dict(op, inputs, source, **numbers)` in that order; `#[track_caller]`, so `source` is your line.
    A questions graph records `empty` with `(0.0,)*6` and gives reading shapes.
  - `g.add_val(op: Val, inputs: &Val, bounds: &Val, numbers: Kwargs) -> Result<Shape>`: the same with the
    Python values as given (`inputs` any sequence, `bounds` a tuple/list or `None`).
  - `g.box_(Vec<Val>) -> Result<Shape>` (`graph.box(*bounds)`), `g.box6([Num; 6]) -> Shape`,
    `g.cylinder(axis: i64, radius, a, b, lo, hi: Num) -> Result<Shape>`,
    `g.prism(axis: i64, lo: Num, hi: Num, section: &Val) -> Result<Shape>`,
    `g.rounded(&Solid, radius: Num) -> Result<Solid>`.
  - `g.document(&result, &[(key, Solid)]) -> Result<Val>` (`graph.document(result, extras)`; empty
    slice = no extras).
  - `g.nodes()` (the one shared list), `g.node(i)` (the node dict itself: mutate it in place, as
    `graph.nodes[i].update(..)` / `graph.nodes[i]['offset'] = ..` do), `g.op(i)`, `g.len()`.
  - `g.attr(name)` / `g.set_attr(name, val)`: every other attribute (`extras`, `answers`, `queries`,
    and what generated code sets, e.g. `graph.extras = {}` is `g.set_attr("extras", Val::dict(vec![]))`).
  - Questions only: `g.model(&Val) -> Result<Solid>`, `g.identity(i) -> Result<String>` (cached),
    `g.reading(&Solid, kind: &str, components: bool, valid: bool) -> Result<Val>`,
    `g.questions_document()`, `g.answers()`, `g.queries()`, `g.extras()`.
- `P::Shape`: a native node. `index()`, `graph()`, `is_reading()`, `bounds() -> Result<Option<Bounds>>`,
  `bounds_val()` (as Python holds it), `set_bounds(Option<Bounds>)` (`shape.bounds = ..`), `same(&Shape)`
  (`is`), `fuse/cut/intersect(&[Solid]) -> Result<Shape>`, `boolean(op, &[Solid])`, `translate(&Val)`,
  `rotate(&origin, &end, &angle)`, `mirror(&plane)`, `bounding_box() -> Result<Val>`.
- `P::Solid` = `Native(Shape) | Py(Val)`: what typed code holds for any solid (a native shape, a Python
  `_Shape`/`_ReadingShape` another worker made, `None`). `Solid::from_val(&v)` never fails; `s.to_val()`.
  Methods behave the same for both variants: `cut/fuse/intersect(&[Solid]) -> Result<Solid>`,
  `translate(&Val)`, `rotate(&Val, &Val, &Val)`, `mirror(&Val)`, `clean()`, `val()`,
  `solids() -> Result<Vec<Solid>>`, `bounding_box() -> Result<Val>`, `bounds()`, `bounds_val()`,
  `index()`, `index_val()`, `volume()`, `faces() -> Result<Vec<Val>>`, `is_valid() -> Result<Val>`,
  `same(&Solid)`, `is_none()`, `native()`, `method(name, args, kwargs)` (anything else).
  `From<Shape> for Solid`.
- `P::AnyGraph` = `Native(Graph) | Py(Val)`: a graph argument that may be a Python object
  (machine-data's `_Questions()`, a generated module's `_Graph()`). `from_val`, `to_val`, `attr`,
  `set_attr`, `node(i)`, `add(op, Vec<Val>, bounds: Val, numbers)`, `box_(Vec<Val>)`,
  `cylinder(axis, &r, &a, &b, &lo, &hi)`, `prism(axis, &lo, &hi, &section)`, `rounded(&Solid, &Val)`,
  `document(&Solid, &[(Val, Solid)])`; `C::model(&AnyGraph, &Val)`, `C::reading(&AnyGraph, &Solid,
  vec![("components", ..)])` for the questions methods.
- `P::Bounds { v: [Num; 6], list: bool }`: `(xmin, xmax, ymin, ymax, zmin, zmax)`, ints and floats as
  Python holds them, tuple or list. `Bounds::from_val(&Val) -> Result<Option<Bounds>>`, `to_val()`,
  `lo(axis)`, `hi(axis)`, `f()`, `overlaps(&other)`.
- `py::Py` is implemented for `Solid` (`from_py` never fails), `Shape` and `Graph` (`from_py` fails for a
  value that is not native), `AnyGraph`, `Bounds` (`from_py` fails on `None`). So a typed signature
  `fn f(rt, .., body: Solid) -> Result<Solid>` crosses both ways, and
  `cx.generated::<Solid>(name, py_args![solid, graph, ..], kwargs)` hands generated code the namespace it
  expects and gives the native value back.

### Leaves and recorders

- `P::call_leaf(&cx.ns.0, "_ybox", args, kwargs) -> Result<Solid>`: `shell._ybox(*args, **kwargs)` read
  from the namespace at the call. A leaf a recorder installed with `P::leaf` runs typed (no namespace
  made, its native shape returned as is); any other value is called and its result wrapped.
- `P::leaf(|args, kwargs| -> Result<Solid> {..}) -> Leaf`: `leaf.value` is the Python-callable to
  `setattr`; keep the `Leaf` alive while it is installed (dropping it only unregisters the fast path).
  `P::Memo` is `functools.cache` for such a leaf.
- `P::Recording::enter(rt, shell, &AnyGraph, structure: Solid)` / `recording.exit()` is
  `_record(shell, graph, structure)`: the 14 leaves of `P::RECORDED`, installed and restored in that
  order. `P::with_recording(rt, shell, &graph, structure, || body)` is the `with` block (exit always
  runs, its failure wins); `P::record(rt, shell, &graph, &structure) -> Val` is the context manager for
  generated callers.
- `C::Numeric::enter(rt, shell, &AnyGraph, box: Option<&Val>)` / `.exit()`, `C::with_numeric(..)`,
  `C::numeric(rt, shell, graph, box) -> Val`: `_numeric` (`shell.cq` = `SimpleNamespace(Vector=_Vector)`,
  `_record(shell, graph, None)`, then `_enclosure_back_top._leaves(shell, graph, box)` when a box is
  given).
- `C::measure(rt, &AnyGraph) -> Result<Val>` is `_measure`; `C::check_pieces`, `C::box_readings`,
  `C::piece_reports`, `C::check_rows` are the module functions, Python values in and out.
- Readings stay Python objects as generated code receives them: `C::bounds_namespace(rt, lower, upper)`
  (`_bounds`), `C::vector(rt, coords)` (`_Vector`), `_ScalarFace` / `_ScalarComponent` lists from
  `Solid::faces` / `Solid::solids` of a reading shape.

### Crossing to generated code

- `shape.to_val()` makes the shape's namespace the first time it crosses: one 5-entry `Val::Namespace`
  (`graph`, `index`, `bounds`, a hand-back function, `__getattr__`), two closures. Later crossings clone
  an `Rc`. A graph's namespace exists from creation (it holds `extras`/`answers`/`queries` itself).
- Back to typed code: `Solid::from_val` scans the namespace (5 entries) for the hand-back function,
  calls it, takes the native value from a thread-local. A value that is not one of ours is `Py`.
- Generated code calling a face method: one `__getattr__` call that makes a bound function, then the
  native operation; the result is a namespace again. Attributes `graph`, `index`, `bounds` are plain
  entries (a generated `shape.bounds = ..` writes the entry, which the native shape then reads).
- `==` and `in` never match two namespaces (interop's `eq`), `is` does; nothing in these modules'
  callers compares shapes by `==`.

### Python `self`

Every `"_Shape.*"`, `"_Graph.*"`, `"_ReadingShape.*"`, `"_Questions.*"`, `"_Vector.*"`, `"_Scalar*"` entry
takes a Python instance (machine-data's `_Questions()`, the other modules' `_Graph()` until they are
typed) and a native namespace alike. Python graphs keep their nodes in the Python list; their shapes
are Python `_Shape` / `_ReadingShape` objects.

## Status (wound down 2026-11-04, nothing compiled)

- `_enclosure_panel`, `_rust_enclosure_checks`: written in full (TYPED = true). The one build was
  stopped at the wind-down before it reported, so neither has been compiled, run through names.py or
  compared. `math.sin`/`math.cos` in rotate and the teardrop leaf use `num::sin`/`num::cos`.
- `_enclosure_pump_retainer`: written in full (TYPED = true), never compiled.
- `_enclosure_rust_driver`: still the placeholder (TYPED = false). The generated code was read up to
  `cut_tube_setting_jig`.

## Findings

- Generated `cutter is shell._port_cuts` (panel `numbers`) never holds between two functions in the
  generated runtime, so the west-port branch always runs for both pairs; the typed code evaluates the
  same `is`.
