# top: the enclosure's piece recipes

Modules, in this order: `_enclosure_back_top`, `_enclosure_front_top` (imports back-top's `_leaves`,
`_replace`, `_rounded`, `_placed`, `_funnel_containment`), `_enclosure_front_bottom` (imports
front-top's `_front_half`, `_leaves` and back-top's `_replace`).

Each builds its pieces as a construction graph (`_enclosure_panel._Graph`, `_record`). The typed graph API
is the module documentation at the top of `$T/_enclosure_panel.rs` (`Graph`, `AnyGraph`, `Solid`, `Bounds`,
`Recording`, `record`, `leaf`, `call_leaf`); `$R/notes/graph.md` has the graph agent's notes once it writes them. Their context managers
(`_leaves`, `_frame_leaves`, front-top's own) replace names with `setattr` while they run, and restore
them afterwards in the same order:

- in `enclosure` (`shell`): its geometry slots and helpers (read `briefs/enclosure.md`, "Solids, slots
  and the replaceable names"; install them as the graph API says, so generated and typed callers alike
  reach them);
- in `funnel_frame`, `flute_skin` (provider modules: `setattr` on the provider object, as now), and in
  `_route_snaps` and `_swept_top` (this crate's modules: set the name in their namespace).

`_enclosure_back_top`'s receiver calls `crate::nameplate_snap::apply(..)` in the generated code: call that
hand-written Rust directly.

They read about 35, 53 and 22 names of `enclosure` (`shell.<name>`). `enclosure` is being converted at the
same time, in five parts (`briefs/enclosure.md`): call its functions through its namespace
(`rt.import("enclosure")`, then `.attr(name)?.call(..)`) until its parts publish their typed signatures
(`## Signatures` in `$R/notes/e1.md` … `e5.md`), then call the typed functions directly
(`super::enclosure::p3::_z_rail_heads(&cx, ..)`, with the `Cx` from
`rt.state::<super::enclosure::Cx>("enclosure")`) wherever no recorder replaces the name.

Steps: `python3 $R/who.py <module>`; mainly `enclosure`, `enclosure-box`, `enclosure-assembly`.
