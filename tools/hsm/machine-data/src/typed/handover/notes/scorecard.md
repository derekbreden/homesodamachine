# scorecard — `_scorecard` typed conversion notes

Module file: tools/hsm/machine-data/src/typed/_scorecard.rs (TYPED = true).
Workspace: $R/ws/scorecard (deleted at wind-down). Python source: scratchpad/py/_scorecard.py (git show a78cf15ba^:hardware/manifold-layout/_scorecard.py).

## Probes (ws/scorecard deleted at wind-down)
- Differential probes ran Python scripts through harness.py in an APFS clone of
  steps/enclosure-assembly, calling the module's functions on fixtures and printing each value or
  "RAISED Type: first line" with captured stdout/stderr, once per binary.
- Probe 1 (~110 calls: selftest, main, mounts family, made_of for every ml.SEGMENTS how,
  load_connections, need_of/need_clause, bend_radii, _bend_radius, _routed, _clearance_floor,
  _size_line, to_dict, gates_pass, seat_misses/seat_tol, _located, _room_holds, _placed,
  anchored_pairs, _DeferredModule, _PlacedShapes, the error paths of every function that needs a
  full assembly, module values).
- Probes 2 (populated fake assembly; fine world with _assembly_model/meshcad.write patched) and 3
  (fine_world on a fake reading and casing npz; argument-binding errors; namespace paths) were
  written but never ran: the host scheduler held them past the wind-down.

## Comparing
- Parent's note: workers missing from $R/bin come from the live checkout. Use
  `BINDIR=$R/bin-all $PY $R/compare.py $R/steps <target> base=$R/bin/machine-data scorecard=<bin>`
  (base first in the same call), or `BINDIR=$R/bin-all AGAINST=$R/base-trees-pinned` once that
  tree exists for the target.
- The workspace build is opt-level 0; opt 0 and opt 3 differ by 1 ulp where LLVM merges a sin/cos
  pair (layout-data arc sampling). Against `base0=$R/bin-base0/machine-data` for targets that route.
  _scorecard.rs calls no sin or cos (only num::degrees), so it needs no num::sin/num::cos change.

## Findings (the generated namespace, mirrored)
- Comprehension loop vars are not bound at module level; only `_p` leaks.
- @cache is not applied (pack_bodies, _selected_mounts, derived_mounts recompute each call).
- `ml.placed_leaves` and `ml.clashes` do not exist in manifold_layout: `_split_placed` and every
  non-fine path through pack_clashes / part_clearances / size_rows / lane_notes raise.
- `__import__` is not a name the generated namespace resolves: `_selected_mate_regions` and
  `_bed_fit`'s non-fine branch raise "_scorecard: unknown name __import__".
- `isinstance(x, Exception)` never matches a stored error (errors are strings): the 'mates' family's
  failure is stored as text, `unpack(text, 3)` then raises, so `_fine_pack_readings` always raises
  and pack_clashes, _pack_closes, _build, build, report and write can never succeed.
- raise Kind(m) -> bail!("Kind: m"); `except Exception as e` binds the error text.
- The runtime's `<=` reads numbers only: `selected_clearance_joints`' last line (`pair <= present`)
  raises "expected number, got frozenset({'tee-fold', 'vk-solenoid'})" on every call, so it and
  every caller (run/fine clearance pairs, part_clearances, _fine_pack_readings) always raise; and
  selftest raises "expected number, got {'mate', 'drawn'}" at `{MADE_BY_MATE, MADE_BY_TUBE} <=
  set(MADE_AS)`, after the made checks print. Typed calls interop::compare("le") on the same values.
- Argument binding: a private `bind` with the generated runtime's order and texts ("missing
  argument X" in signature order, "too many positional arguments", "unexpected keyword
  arguments"); a name ending in `?` has a default (marked from compiled/_scorecard.rs params).
  Every function's positional/keyword-only lists match the generated params (scratchpad sig/sigs.py).
- Deferred modules: instances made at install through the Python type (shim -> typed __init__);
  TOUCHING_OK reads the four gas adapters through `_gas_chain.__getattr__`; functions import the
  provider modules directly (`_boxes`, `_clearing`, `_overlap`, `_routing` are providers).
- Genrules staging _scorecard.py: bom-masses, enclosure, enclosure-assembly, enclosure-box,
  enclosure-dimensions, enclosure-mechanical-sync, fluid-topology-sync, internal-plumbing-sync.
  Only fluid-topology-sync touches the module's names at run time (MADE_AS, MADE_UP,
  _DeferredModule.__init__/__getattr__); other crate modules read CLEARANCE_FLOOR and
  REFRIGERANT_SEGMENTS.

## Results (typed binary vs generated, same call, BINDIR=$R/bin-all, opt 3 base)
- fluid-topology-sync: 678 files, 0 differ, no errors
- internal-plumbing-sync: 671 files, 0 differ, no errors
- enclosure-mechanical-sync: 671 files, 0 differ, no errors
- enclosure-dimensions: 665 files, 0 differ, no errors
- not compared (stopped at wind-down): enclosure-box, bom-masses, enclosure, enclosure-assembly

## Status (wind-down, 21:45)
- Complete: every function, class method, value and the main block of `_scorecard` is typed;
  TYPED = true.
- Verified: the four genrules above byte-identical; the namespace dump has the same 137 names in
  the same order with the same values, except that the generated dump printed the five paths and
  five `_DeferredModule` instances by type name only (their typed values were read, not diffed);
  probe 1 identical except the two `<=` cases (selftest, selected_clearance_joints), which the
  21:16 build mirrors.
- Not verified: the 21:16 build itself (the `<=` mirrors and the private `bind`) compiled clean and
  was never run; it changes only error paths and argument-binding error text, but the release-build
  check is its first run. enclosure-box, bom-masses, enclosure and enclosure-assembly were not
  compared with this module typed.
- Shared files: none need a change. interop compare("le") reading numbers only is mirrored, not fixed.
