# graph: the construction-graph core

Modules: `_enclosure_panel`, `_rust_enclosure_checks`, `_enclosure_pump_retainer`, `_enclosure_rust_driver`
(in that order).

What they are: `_enclosure_panel._Graph` / `_Shape` record solid operations as nodes of a document that a
Rust part program builds; `_rust_enclosure_checks._Questions` is a `_Graph` that asks the Rust
`enclosure-checks` program questions about its shapes (`_ReadingShape`, `_ScalarFace`, `_ScalarComponent`,
`_Vector` read the answers). `_enclosure_panel._record` and `_rust_enclosure_checks._numeric` are context
managers that replace the enclosure source's geometry leaves (`setattr(shell, '_ybox', ...)`, ...) with
graph-recording functions and restore them afterwards; `shell` is the `enclosure` module namespace. The
pump retainer builds its pieces through them; the driver runs the enclosure step (`enclosure.py`'s main
calls it) and the checks.

Other agents convert `_enclosure_back_top`, `_enclosure_front_top`, `_enclosure_front_bottom` and
`enclosure` (8.5k lines of Python) after you, on top of your API. Design it for them:

1. Native graphs. A graph this crate's typed code creates is a Rust struct. Nodes are recorded exactly as
   `_Graph.add` records them: `dict(op=..., inputs=list(...), source=dict(path=..., line=...), **numbers)`
   in that key order, each number the exact Python value the generated code records (an int stays an int,
   a tuple a tuple, a list a list). Shapes are Rust values with the same bounds arithmetic as
   `_Shape._boolean`, `translate`, `rotate`, `mirror` and `BoundingBox`; `document()` returns the same dict.
   A node's `source` is `rt::site()` at the typed line that recorded it (the comparison masks sources).
2. One solid type for typed callers (for example `pub enum Solid { Native(Shape), Py(Val) }`) with the
   methods the recipes call (`cut`, `fuse`, `intersect`, `translate`, `rotate`, `mirror`, `clean`, `val`,
   `Solids`, `BoundingBox`, `bounds`, and what `_ReadingShape` offers: `Volume`, `Faces`, `isValid`, ...),
   behaving the same whichever variant it holds. `Py` holds a Python object another worker made:
   machine-data creates `_rust_enclosure_checks._Questions()` itself and calls `.model(..)`,
   `_numeric(shell, graph)`, `_measure(graph)` and enclosure functions with those shapes (see
   `git show a78cf15ba^:hardware/scripts/_machine_checks.py`, around line 140; the step
   `enclosure-assembly` runs it).
3. The stub classes' `"Class.method"` entries keep working on Python instances (`self` a Python object)
   for those external callers.
4. Until the modules above are converted, generated code receives your solids and graphs as `Val`, calls
   their methods and reads `graph`, `index`, `bounds` and `graph.nodes`. A native shape or graph handed to
   generated code must behave as the Python object would: for example a `Val::Namespace` whose fields are
   those attributes and whose functions act on the native value, and which converts back to the native
   value when it comes back to typed code (a field holding a closure that hands the value back through a
   thread-local is one way; `Val` has no opaque variant). Keep the nodes list one shared list if generated
   code reads it while you append. When every consumer is typed, no wrapper is made.
5. The recorders install their leaves into the enclosure namespace exactly as now (the same names, values
   callable from generated and typed code alike, the same restore order), because `enclosure` reads them
   through its namespace at every call. Give typed callers a way to call an installed leaf with typed
   arguments and get a `Solid` back.

Write the API's usage at the top of `_enclosure_panel.rs` (and `_rust_enclosure_checks.rs`) as a doc
comment for the next agents, and as soon as the panel's API is settled, describe it in
`$R/notes/graph.md` under a heading `API` (the next agents start from that note while you finish the other
modules). In your report, give the API and what a native-to-generated crossing costs.

Steps: `python3 $R/who.py <module>`; mainly `enclosure`, `enclosure-box`, `enclosure-assembly`.
