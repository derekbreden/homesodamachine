# The Rust conversion

[AGENTS.md](../../AGENTS.md#speed) states the goal: this Mac's CPU and memory stop limiting how
much the agents get done. This is the build's plan for it.

## Done

No step of the normal build loads CadQuery, OpenCASCADE (OCP) or meshcad. Each generator keeps
its numbers in Python and has a Rust program cut its geometry on the kernel, as the
[parts the kernel cuts](README.md#parts-the-kernel-cuts) do, and the checks and exports that
read the geometry run in Rust or on `hsm`. The conversion converts what the build has: the same
parts, checks and outputs.

## How the work runs

- **The bet is on Rust.** A piece moves as soon as its Rust program makes the outputs it
  replaces. One that is slower on its first try lands anyway and is made faster in Rust
  afterwards. One that stays slower after that goes to Derek to re-examine, and holds up nothing
  else.
- **Pieces run in parallel.** The integration lead splits what is left into pieces with separate
  files, and one agent takes each piece, as many at once as the thread limit allows.
- **A piece is converted whole** before anything in it is verified.
- **A piece is verified once, at its end, on fixed inputs:** its outputs against the ones they
  replace, from the same inputs. The same solids within the kernel's rule; the same names,
  placements and colours; the same check answers. No full normal build, whole-build memory
  sample or old-against-new timing gates a single change. A normal build runs when a batch
  merges to main.
- **Memory is cut in the Rust programs** and verified the same way. The Python side of a program
  being converted gets no tuning.
- **Mechanical changes keep landing.** One that reaches main while its piece is being converted
  is carried into the Rust version before that piece merges. Once a piece is in Rust on main,
  its mechanical edits are made there.

## What is left

A piece comes off this list when it lands on main. The box and the machine are most of the
build's critical path: a change to the box runs both steps, one after the other, and a change to
any part in the machine runs the machine's.

1. **Standing the machine.** `machine()` in
   [`enclosure_assembly.py`](../../hardware/manifold-layout/enclosure_assembly.py) places every
   body on meshcad, and `_dims` in
   [`enclosure.py`](../../hardware/printed-parts/enclosure/enclosure/enclosure.py) sizes the box
   around them. [`enclosure_box.py`](../../hardware/manifold-layout/enclosure_box.py) runs both
   to write the Box the enclosure's step reads, and the machine's step stands the machine again
   around the cut pieces. `machine-assembly-model` (`tools/hsm/machine`) builds the fine
   measurement model from the placements Python hands it.
2. **The box.** `enclosure.py` reads the Box and cuts its printable pieces with the
   `tools/hsm/enclosure-shell` programs. The rest of its step runs on meshcad: the bounds and
   reports (`_report_*`, `vent_readings`, the handhold, silhouette and ceiling bounds), the
   assembled `enclosure.step` and the pump dock.
3. **The machine's checks**, called inline from `enclosure_assembly.py` on the stood machine.
4. **The machine's exports**: its STEP, payload, scene GLBs, scorecard and facts.
5. **The install guide's plumbing scenes**,
   [`plumbing_scenes.py`](../../hardware/install-guide/plumbing/plumbing_scenes.py) and
   [`render_modern_tee.py`](../../hardware/install-guide/plumbing/modern/render_modern_tee.py),
   on CadQuery.
6. **Any other step that loads CadQuery, OCP or meshcad at run time.** A generator that calls
   `_rust_part.start()` defers CadQuery, and still loads it on any path that reads a CadQuery
   name.
7. **The CadQuery path itself.** Once the rest lands, meshcad, the Python builders nothing on the
   build calls, and CadQuery leave the normal build.
