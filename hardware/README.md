# Hardware

The home soda machine's physical design — the integrated under-counter appliance that consolidates carbonator, refrigeration, flavor reservoirs, pumps, valves, and electronics into one enclosure.

**Start with [`future.md`](/hardware/future.md)** — the master design narrative. It describes the appliance subsystem by subsystem (carbonation, refrigeration, cold core, flavor, enclosure, power) and links out to every companion doc and part directory below.

## Layout

| Path | What's there |
|---|---|
| [`future.md`](/hardware/future.md) | The design narrative — the entry point and source of architectural intent. |
| [`design-pressures.md`](/hardware/design-pressures.md) | What the appliance is optimised for and what it is not. Placement decisions answer to this: volume and assemblability are optimised, field service and disassembly are not. |
| [`ledger/`](/hardware/ledger/) | Bookkeeping. [`purchases.md`](/hardware/ledger/purchases.md) is the source-of-truth capex ledger; [`bom.md`](/hardware/ledger/bom.md) (per-unit parts), [`tools.md`](/hardware/ledger/tools.md) (active tooling), and [`inventory.md`](/hardware/ledger/inventory.md) (spares / abandoned / donor / diagnostic stock) are views over it. Three more price time rather than parts: [`labor.md`](/hardware/ledger/labor.md) (attended minutes per unit), [`machine-time.md`](/hardware/ledger/machine-time.md) (hours a machine is occupied per unit), and [`build-time.md`](/hardware/ledger/build-time.md) (seconds a generator run takes, which is what a change to this repo costs rather than what an appliance costs). |
| [`assembly/`](/hardware/assembly/) | Production procedures, one doc per subsystem, plus [`handwork.md`](/hardware/assembly/handwork.md) (the skilled-hand task summary). |
| [`service/`](/hardware/service/) | Procedures run on a finished appliance rather than a bench: [`pump-replacement.md`](/hardware/service/pump-replacement.md) and the dry cycle it runs first. |
| [`printed-parts/`](/hardware/printed-parts/) | FDM parts: CadQuery generators (`*.py`) + exported `*.step` + sidecars. Includes `cadlib/` (shared geometry helpers), `cold-core/`, `electronics/`, `enclosure/`, `faucet/`, `refrigeration/`, `valve-seat/`, `zone-c/`. |
| [`cut-parts/`](/hardware/cut-parts/) | Laser-cut sheet parts: `*.dxf` outlines + sidecars (carbonation end-caps, under-counter plate). |
| [`manifold-layout/`](/hardware/manifold-layout/), [`cold-core-layout/`](/hardware/cold-core-layout/), [`faucet-layout/`](/hardware/faucet-layout/) | The assemblies the parts above stand in, each written as one multi-solid STEP: the packed appliance, the core one frame further in, and the above-counter column. `/3d` browses the tree these head — the appliance and the faucet as its two cards, and the appliance stands the core's own bodies, so opening it is already being inside the core. |
| [`off-the-shelf-parts/`](/hardware/off-the-shelf-parts/) | Reference geometry for purchased parts modelled into assemblies. |
| [`reference/`](/hardware/reference/) | Imported / harvested reference STEPs (factory faucet, solenoid, ice-maker, fittings). Not fabricated by this project — no sidecars. |
| [`topology/`](/hardware/topology/) | Fluid + valve topology, including the canonical valve-state truth table. |
| [`wiring/`](/hardware/wiring/) | Wiring schedules, pinouts, and power topology diagrams. |
| [`battery-backup/`](/hardware/battery-backup/) | Mains-outage dispense ride-through subsystem. |
| [`quickstart/`](/hardware/quickstart/) | The two-sheet visual quick start that ships at the top of the carton. |
| [`snapshots/`](/hardware/snapshots/) | Dated, point-in-time records (build-readiness audit, tapping plan, fill-from-funnel plan). **Frozen, not living docs** — re-run produces a fresh dated file rather than editing these. |
| [`scripts/`](/hardware/scripts/) | Project Python tooling. The instruments: [`probe.py`](/hardware/scripts/probe.py) asks the placed machine a geometry question instead of reasoning about it — where a body is, how close two come, what a volume runs into, how far a line runs, where there is room for one, what a pick copied out of the viewer names, and where a piece of a routed line can stand; [`fit.py`](/hardware/scripts/fit.py) asks the same of a body that is not placed yet, carried to a candidate pose; [`lanes.py`](/hardware/scripts/lanes.py) enumerates every corridor a run could take between its two fixed mouths at a stated clearance floor, holding every body still, and reports each one's tube, corners, tightest clearance, lowest z and the sub-assembly its legs lie on without ranking them. Each carries a `selftest`. Then `_cadq_export.py` (the shared atomic STEP/DXF/PDF export helper imported tree-wide) and the doc-sync / totals generators that maintain the `ledger/` docs. |

## Where the solids are

    node web/scripts/fetch-cad-artifacts.mjs              # the solids the lock names, onto this disk

A generated `.step` is on this disk and in no index. [`cad-artifacts.lock.json`](/hardware/cad-artifacts.lock.json) names each one by sha256, the release asset carrying them, and the commit each came from — `source.commit` for the bundle, and a `held` entry for any member whose rule an uncommitted edit reaches, which ships its last publication's bytes and names that commit. [`tools/cad-artifacts/pack.py`](/tools/cad-artifacts/pack.py) builds and pins one, and the deploy runs the fetch above (`render.yaml`). A build cuts them too, so a checkout that runs one needs no fetch. The three harvested solids under [`reference/`](/hardware/reference/) have no builder here and are in the index.

## The design loop

    source → changed solid → local view → pinned artifact → /3d

The local render and the deployed viewer are two stops on one geometry path. [`tools/look.sh`](/tools/look.sh) opens a generated STEP from this disk through the same `/3d` viewer the headless renderers drive. [`pack.py --write`](/tools/cad-artifacts/pack.py) packages the generated solids on this disk; after its lock is committed and pushed, Render fetches that bundle and `/3d` serves it. A push to `main` runs `publish.yml`, builds only the affected artifact rules and their dependencies, carries their ignored outputs, and publishes the lock separately from cards and PDFs. The solid an agent judges locally is the solid that goes in front of Derek.

A repository-wide build is not a viewing boundary. A generator, focused Bazel target, [`probe.py`](/hardware/scripts/probe.py), or [`fit.py`](/hardware/scripts/fit.py) answers the current design question; the next local picture follows it immediately. Broader builds and checks answer broader questions when those questions arise. The iteration speed that matters is the time from an edit to the next informed look — first by the agent, then by Derek.

## What a build costs

    bazelisk build //:everything                          # every generator whose inputs moved
    tools/cad-venv/bin/python tools/bazel/sync_tree.py    # what the tree does not carry yet

For a focused dirty-tree build:

    targets=$(tools/cad-venv/bin/python tools/bazel/affected.py --artifacts)
    bazel build $targets
    tools/cad-venv/bin/python tools/bazel/sync_tree.py --write --solids-only --targets "$targets"

ONE ACTION PER STEP, EACH HOLDING WHAT IT DECLARED AND NOTHING ELSE. What it declared is what
a run of it was watched reading — `tools/bazel/trace_inputs.py` installs an audit hook, runs
the generator once, and keeps every path under this repo it opened, including the ones handed
to a tool it starts. The median step declares nine files; `_cable_assemblies_sync` declares
six, and the assembly syncs that import the machine to reach its constants declare eighty. The
graph is `tools/bazel/graph.json`; `tools/bazel/gen_build.py` writes `BUILD.bazel` from it.

A step is usually one generator. Four are several: `docgen` lets more than one script keep a
doc's `[value](NAME)` figures, each managing its own names, so `faucet_shell.py` and
`under_counter_plate.py` both write `ASSEMBLY.md` and are one action. `bazel` needs
one action per file, and `inventory._together` is what groups them.

`bazel-bin/` is where a build lands. The tree commits its docs and holds ignored solids long
enough for the content-addressed bundle to publish them, because a reader at `/3d` and a shop
printing a part both need the same bytes. `sync_tree.py` carries every declared output over;
a tree it has nothing to say about is a tree holding the artifacts its sources make.

WHAT AN EDIT COSTS IS THE STEPS THAT DECLARED THE FILE, and that is a count, not a guess.
`_boxes.py` is declared by 95 of the 99 steps, so it is the worst case the tree has:

| an edit to `_boxes.py` | steps | wall |
|---|---|---|
| a comment written into it | **1** — `pysrc` alone | **1.8 s** |
| a line of code | 95 | 406 s |

| | wall |
|---|---|
| the whole tree, nothing moved | **0.4 s**, no action run |
| whether anything is owed — `--check_up_to_date` | **0.3 s**, no action run |
| every step rerun, the kept work standing | 88 s, 41 s of critical path |
| every step rerun, the kept work regenerating | 386 s, 219 s of critical path |

The last two are the same 99 actions and differ only in whether `.cache/` already holds the
shapes they cut. A geometry edit pays the second on the bodies it moved and the first on the
rest. All of these were taken on a quiet machine; a reading taken while another build is
running is roughly half speed for want of cores, and is a ceiling rather than a figure.

A BYTE IS WHAT DECIDES A RERUN, and a comment is not a byte a step reads. `tools/bazel/pysrc.py`
lays every Python source down with its comments out of it — a line carrying no code is gone,
and the code lines come through verbatim and in order — and the steps declare that copy rather
than the file. So writing a comment moves one short action, its output lands on the bytes Bazel
already built against, and nothing under it runs. What comes out parses to what went in, and
`pysrc` asserts that per file before it writes: the same reading `_realized.code_digest` takes,
put where Bazel can see it.

The 32 generators whose own docstrings hold `[value](NAME)` figures are handed their file raw,
because the run rewrites what it was given and `sync_tree` carries that back into the tree. A
step that actually starts Node is also handed `:node-packages`, which globs `tools/render/` and
`web/` in whole.

A line number in a sandbox traceback is that copy's, not the tree's. The line it names is in
the tree, found by its text.

AND AN ACTION HOLDS THE KEPT WORK. `.cache/` is the shapes `_realized` keeps, the meshes
`_meshes` tessellates and the optimal boxes `_boxes` measures; `.bazelrc` mounts it into every
action and `_realized.key` mixes in `HSM_INPUT_DIGEST`, a hash over the solids the action was
given. The import walk covers the Python and that digest covers the other half — a solid loaded
off disk is not an import, and `enclosure.py` makes no `import_step` call of its own while its
action declares 28 solids it reaches through what it imports.

A SOLID ONE GENERATOR CUTS AND THE NEXT LOADS IS AN EDGE LIKE ANY OTHER HERE. `foam_assembly`
reads `foam-cap-top.step` from `//:foam-cap` and `enclosure_assembly` reads
`foam-assembly.step` from `//:foam-assembly`; neither can fall back to the older copy fetched
from the artifact lock. OCCT opens these below Python, so `_cadq_export.import_step` records the
paths and `gen_build.py` resolves each one to its producer output.

A picture is the same picture every run. Every renderer in `tools/render/` reads the frame
back off the canvas in the task that drew it (`browser.js` `frameBuffer` carries why), so
nothing here is a race and a redraw of unmoved geometry lands byte-identical — eight runs of
one scene and eight of one part, one hash each.

A view of any STEP, from any angle, is `tools/look.sh` — drawn when someone asks for one, so
there is none of it in the tree to go stale.

WHAT THE ACTIONS RUN WITH IS THE MACHINE'S, not the tree's. `tools/cad-venv` holds the
interpreter and its packages, `node_modules` the renderer's, and `rsvg-convert` and `blender`
come off the brew prefix — `.gitignore` holds the first two and the last two are not in the
repo at all. `.bazelrc` names both roots as mounts and puts them on every action's PATH. A
checkout on another machine builds when those are installed there and not before.

AND `blender` INSTALLED IS NOT THE WHOLE OF WHAT THE LINE ART NEEDS. The Freestyle SVG
exporter is a downloadable extension, not part of Blender, and everything `_blender_scene.py`
and `sieve_scene.py` ask it for is a property it ADDS to the scene when it registers —
`linestyle.use_export_strokes`, and the `scene.svg_export` group. A Blender without it is a
Blender the line art cannot run on:

```
blender --background --online-mode --command extension install -s -e freestyle_svg_exporter
```

`BLENDER_USER_RESOURCES` decides where that lands and where a run looks for it, so `.bazelrc`
passes the variable through to every action rather than stating a path — unset on a machine
whose extensions are already under the default user path. Both scene scripts check the enable
and exit non-zero naming the extension, because `addon_utils.enable` does not raise when the
module is absent: it prints one line and returns None, and the miss surfaces a hundred lines
later as an `AttributeError` with Blender itself exiting 0.

TWO THINGS THE BUILD DOES NOT GUARANTEE, both named where they stand:

- **A `.step.mesh` is not a declared output.** `_cadq_export` tessellates best-effort — a
  payload must never break an export — and a Bazel output is one the action must produce or
  fail. The two are opposite promises. So no action writes one: `sync_tree` carries what a
  target declares, the payload is in nothing's `outs`, and `.bazelrc` sets
  `HSM_SKIP_MESH_PAYLOAD` for every action rather than tessellating a file the sandbox
  discards. The runs that keep the tree's payloads are a hand run and the dev-server watcher.
- **`//:render-scenes` carries `local` and is not sandboxed.** `render-step-posed.js` stands
  the viewer on loopback and photographs it with a headless browser, and that page loads
  `occt-import-js` off a CDN — so drawing a scene reaches the public network for a library this
  tree does not carry. Vendoring it is what would make the action hermetic. It is the one
  action here whose inputs are not all declared.

Inside one run:

| phase | wall |
|---|---|
| derive + audit — `build_enclosure_assembly`, then the card | 8.7 s |
| — of which `_boxes.boxed`, 1372 calls against the disk-kept six | 0.55 s |
| OCCT STEP write, 21 MB | 1.3 s |
| canonicalise — renumber 382,700 entities | 3.7 s |
| tessellate the `.mesh` payload | 1.6 s |
| one thumbnail, drawn off the payload | 3 s |
| one thumbnail, drawn off the STEP with no payload beside it | 16 s |

The export and render rows are timed at `081a1bee`; the two derive rows at `c813264b`.

## Part metadata sidecars

Every fabricated part has a JSON sidecar next to it recording material + thickness + process. The dev viewer reads these to extrude DXF outlines into real 3D plates; tooling and future agents should treat them as the source of truth for material/thickness queries.

### Naming

`<full-filename>.json`, in the same directory as the part:

```
cut-parts/foo/foo.dxf
cut-parts/foo/foo.dxf.json       ← sidecar

printed-parts/bar/bar.step
printed-parts/bar/bar.step.json  ← sidecar
```

The sidecar filename always carries the original extension (`.dxf.json`, `.step.json`), so a directory holding both a `.dxf` and a `.step` of the same basename has no collision.

### Format

```json
{
  "thickness_mm": 1.524,
  "material": "304 stainless steel",
  "process": "laser-cut",
  "notes": "optional free-form context"
}
```

- **`thickness_mm`** (number, required) — for DXF cuts this drives the viewer's `ExtrudeGeometry` so the flat outline becomes a real plate. For STEP prints / shells / tubes it is the wall thickness, kept for documentation and future tooling (the STEP geometry itself already carries full 3D shape).
- **`material`** (string) — free-form, in the spec language you'd put in a quote or order: `"304 stainless steel"`, `"316 stainless steel"`, `"PETG"`, `"PET-CF"`, `"Bambu TPU 90A"`, etc.
- **`process`** (string) — free-form. Common values: `laser-cut`, `3D-print`, `tube-bend`. Add new values as needed.
- **`notes`** (string, optional) — anything else worth knowing: stock size, supplier, why the spec was chosen, tap-engagement counts.

Pull values from the part's generator-script docstring when one exists; otherwise use the spec you ordered or printed against.

### When to update

- **Adding a part:** add the matching `.json` sidecar in the same commit. The viewer treats a DXF without a sidecar as zero-thickness and falls back to wireframe.
- **Changing thickness or material:** update the sidecar in the same commit as the geometry. The dev server's watcher picks up sidecar changes and hot-reloads with the new thickness, no page refresh needed.
- **Renaming or moving a part:** rename/move the sidecar alongside the geometry file.

### Harvested reference parts

[`reference/`](/hardware/reference/) holds imported reference STEPs (the harvested Westbrass, valve internals) this project does not fabricate. These get no sidecars — they're multi-material, externally-spec'd parts kept only for spatial reference.

### Where this is consumed

- The dev viewer (`web/`) extrudes DXF outlines using `thickness_mm`; STEP rendering ignores the sidecar (the STEP is already 3D). See `web/lib/viewer-routes.js` (`/api/dxf` returns each DXF's path alongside its sidecar fields).
- Future tooling (BOM generators, render-dxf, manufacturing quotes) should read the sidecar rather than re-parsing docstrings.
