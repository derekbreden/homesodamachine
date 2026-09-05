# Hardware

The home soda machine's physical design — the integrated under-counter appliance that consolidates carbonator, refrigeration, flavor reservoirs, pumps, valves, and electronics into one enclosure.

This page is the design narrative and the map. The narrative describes the appliance subsystem by subsystem and points at the companion docs and part directories that specify each one; it carries no specifics itself. Where the machine is going, and what done looks like, is [`/future/README.md`](/future/README.md). Who it is for is [`/marketing/target-market.md`](/marketing/target-market.md).

## The appliance

The appliance is an integrated under-counter machine. It packs the carbonator, its refrigeration loop, both flavor reservoirs, the pumps and valves, and the electronics into one enclosure behind a single 120 VAC cord, with the tap-water inlet at the rear and the CO2 cylinder standing beside the appliance on a short tether. The prototype under the counter has proven the dispense path — two flavors of Pepsi-made concentrate injected into cold carbonated water, press the lever and soda comes out. What this build adds is the cold carbonated water itself: the machine carbonates and refrigerates its own. What stays above the counter is a faucet and a small display; the rest is under the sink.

This is the **thin** machine: tall and narrow, built around one bound. The cold core is turned a quarter turn so its short axis runs across the cabinet, and nothing else in the appliance is as wide, so nothing else sets the width. What the turn buys is a column of height above and ahead of the core. The space it is built for is in [`/marketing/install-envelope.md`](/marketing/install-envelope.md).

Read the machine from its cold center outward and from the back of the box forward. A **cold core** fills the back-bottom of the enclosure — a stainless carbonator, an evaporator coil wound around it, and the two flavor reservoirs nested in foam around it, where they pre-chill. Forward of the core are the compressor and the pumps and valves; above it, the electronics and the water deck; over them the flavor funnel. The carbonated-water line runs straight up through the countertop to the faucet. The sections below take the cold core **inside out** and the enclosure **back to front**.

### Carbonation

The carbonator is a custom 316L stainless pressure vessel standing vertically, with four NPT ports. CO2 enters through an internal sparge stone and dissolves as the bubbles rise; filtered tap water is pumped in against the CO2 back-pressure; carbonated water leaves from the bottom; a pressure-relief valve guards the top. Carbonation is set by the CO2 supply pressure. The water level inside is read without piercing it — a magnet rides on an internal rod and external reed switches see it through the wall.

Carbonator fabrication, the hydro-test, the passivation, and the working pressure are in [`/hardware/assembly/pressure-vessel.md`](/hardware/assembly/pressure-vessel.md), with the end-cap cut parts in [`/hardware/cut-parts/carbonation/`](/hardware/cut-parts/carbonation/) and the bench fixture that turns the tube under the welder in [`/hardware/assembly/weld-rotation-rig.md`](/hardware/assembly/weld-rotation-rig.md). The full water and CO2 plumbing — every fitting, the check valves, the beverage backflow preventer, the two-stage CO2 regulation and its setpoint — is in [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md) and the valve-and-fluid topology in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md). The parts themselves, and their order status, are in [`/hardware/ledger/`](/hardware/ledger/).

### Refrigeration

The cold comes from a refrigeration loop harvested from a countertop ice maker — its compressor, condenser, fan, capillary tube, and drier kept in service, with a copper coil wound around the carbonator doing the evaporator's work. Firmware cycles the compressor against temperatures read at the carbonator wall and the coil, with a freeze cutout. The refrigerant is a natural hydrocarbon, vented and recharged through a permanent service valve.

The teardown, the recharge and its charge mass, and the brazing safety are in [`/hardware/assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md); the donor units and the keep-or-discard plan in [`/hardware/reference/ice-maker/README.md`](/hardware/reference/ice-maker/README.md); the coil winding in [`/hardware/printed-parts/cold-core/coil-mandrel/`](/hardware/printed-parts/cold-core/coil-mandrel/). The refrigerant's regulatory standing is in [`/business/regulatory.md`](/business/regulatory.md).

### Cold core (inside out)

Read it inside out: the carbonator; the evaporator coil bonded to its outside; the foam shell's inner wall foamed against the coil; the two flavor reservoirs nested in that foam, where they pre-chill in the gradient between the near-freezing core and the cabinet air; the foam shell's outer wall, foamed again. The reservoirs are vented printed parts, not pressure vessels — sized for a refill of concentrate, and level-sensed the same way the carbonator is.

The layered build is in [`/hardware/assembly/cold-core.md`](/hardware/assembly/cold-core.md). The shells and the pour-in-place foam are in [`/hardware/printed-parts/cold-core/foam-shell/`](/hardware/printed-parts/cold-core/foam-shell/), with [`foam-cap/`](/hardware/printed-parts/cold-core/foam-cap/) and [`foam-assembly/`](/hardware/printed-parts/cold-core/foam-assembly/). The reservoirs — their floor and bulkhead, their filtered vent, their reed-and-float level column, their watertight printing — are in [`/hardware/printed-parts/cold-core/reservoir/`](/hardware/printed-parts/cold-core/reservoir/). The relief-valve shroud is in [`prv-shroud/`](/hardware/printed-parts/cold-core/prv-shroud/).

### Flavor

Two peristaltic pumps draw flavor from the chilled reservoirs and inject it at the gooseneck alongside the carbonated water; each flavor is primed and valve-locked between pours. The pumps run forward only, and a valve manifold selects the fill, dispense, and clean-in-place paths. Four pump-side tees are tied two places each to one Y-guided carrier. Two compression springs push it aft; four bowed tee-to-valve stubs and four tee-side hairpin ends flex as it travels while their other ends remain on the fixed valve rows. Each reservoir fills from the funnel on top, which the concentrate is poured into. The clean cycle runs in software.

The canonical valve-state truth table, with the manifold and tray diagrams beside it, is in [`/hardware/topology/fluid-topology.md`](/hardware/topology/fluid-topology.md). How a valve is held on a printed face is in [`/hardware/printed-parts/valve-seat/`](/hardware/printed-parts/valve-seat/); the carrier, its separately installed rigid service-tab arms and their tab locks in [`/hardware/printed-parts/enclosure/tee-carrier/`](/hardware/printed-parts/enclosure/tee-carrier/); the pumps in [`/hardware/printed-parts/enclosure/pump-tray/`](/hardware/printed-parts/enclosure/pump-tray/) and the pump cartridge they ride out on in [`enclosure/`](/hardware/printed-parts/enclosure/enclosure/); the funnel in [`/hardware/printed-parts/zone-c/`](/hardware/printed-parts/zone-c/). The four 12 mm bowed dimensions are exposed developed paths across 10 mm sleeve-face chords, not tube-blank cut lengths. Those blanks and the spring-driven mechanism remain bench gates: the complete assembly must be force-measured, release and reconnect all four tubes together, return empty without racking, and survive cycling without leaks or tube damage. The reservoir level-sensing pattern is in [`/hardware/printed-parts/cold-core/reservoir/level-sensing.md`](/hardware/printed-parts/cold-core/reservoir/level-sensing.md). One pump serving N flavors on a single line, switching by reverse-purge and re-prime, is a desire captured in [`/future/pie-in-the-sky/single-pump-flavor-switching.md`](/future/pie-in-the-sky/single-pump-flavor-switching.md).

### Enclosure (back to front)

The enclosure stands in the cabinet beneath the sink, in the slot beside the disposal that [`/marketing/install-envelope.md`](/marketing/install-envelope.md) describes. Read it back to front. The cold core is yawed a quarter turn and seated in the back-bottom corner, flat on the floor and flush at the side walls; the diaphragm pump runs front to back over its lid and is what the rear wall stands off. The band above the core is the service bay: the diaphragm pump down the middle, the electronics bay against the +X wall, the water deck in the −X lane. The compressor stands upright on the floor at the front, bolted to the slab, with the condenser beside it and the **machine corridor** behind — the band the refrigerant loop turns in on its way to the core, and the one the manifold's cross-machine lines run along. The condenser's airflow crosses the cabinet: in through the grille on one side face, out the other. A flat 45° facet chamfers the top-front arris, wall to wall, carrying the enclosure display; the funnel takes the top wall's full width behind it. The cabinet prints as four telescoping quadrants that cross-pin with screws from the side faces. The pump cartridge and its top clamp ride in the front bay; behind them a fixed release plate fronts four tee journals and a spring-loaded carrier. The carrier has four named positions: release at −3.15 mm and park at +3 mm are the physical stops, squeeze at 0 is held by two recessed rigid tabs, and connected at +1.5 mm floats under the two aft-pushing springs. Pulling the cartridge brings the tied tees to release; when the four tubes leave, the empty carrier parks beyond connection reach. Insertion is squeeze, bottom all four tubes, release. No face is a panel of its own. The **+Y wall of back-top** lands every connection the appliance makes to the world — the water inlet, the CO2 inlet, the AC cord, the signal jack and the umbilical — one row above the deck. The front wall's one opening is the bay, and the pump cartridge's own face closes it.

The silhouette, the zoning, and what each face carries are in [`/hardware/printed-parts/enclosure/README.md`](/hardware/printed-parts/enclosure/README.md). The split-printable box and its joint are in [`enclosure/`](/hardware/printed-parts/enclosure/enclosure/), the packed assembly in [`manifold-layout/enclosure_assembly.py`](/hardware/manifold-layout/enclosure_assembly.py). The +Y wall of back-top's connection inventory is in [`y-wall-of-back-top/`](/hardware/printed-parts/enclosure/y-wall-of-back-top/), the serialized nameplate in [`nameplate/`](/hardware/printed-parts/enclosure/nameplate/). The mechanical assembly of the whole is in [`/hardware/assembly/enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md). What placement answers to is [`design-pressures.md`](/hardware/design-pressures.md).

### Electronics and power

A single 120 VAC cord enters the +Y wall of back-top. A 12 V supply makes the low-voltage bus that runs the diaphragm pump, the peristaltic pumps, the solenoid valves, the condenser fan, the displays, and the sensors; the logic rails are made on-board. The compressor switches on the AC side; the fan and the 12 V loads switch low-side, firmware-gated. The whole electronics bay — the PSU, the relays, the AC distribution and ground bus, the main board, and the DC distribution — stands down the +X wall in the band above the cold core, feet on the foam cap's lid, each module turned so its own mounting plane faces the wall and bolted to printed bosses reaching in off it, with the water deck in the lane beside them. There is no tray under any of it.

The run-by-run AC schedule is in [`/hardware/wiring/ac-wiring-schedule.md`](/hardware/wiring/ac-wiring-schedule.md), and the power, pinout, and valve-control topology in [`/hardware/wiring/`](/hardware/wiring/). The bench build of the electronics, and the wiring procedure that follows it, are in [`/hardware/assembly/power-column.md`](/hardware/assembly/power-column.md) and [`/hardware/assembly/wiring.md`](/hardware/assembly/wiring.md). The main board — one JLCPCB-assembled PCBA, no plug-in modules — is in [`/hardware/pcb/`](/hardware/pcb/); its bench mount, which does not ship, is in [`/hardware/printed-parts/electronics/`](/hardware/printed-parts/electronics/).

### Safety

Three hazards are designed around independently. The compressor's terminal block and clip-on PTC start relay remain under the R-600a donor's own moulded cover; the hydrocarbon refrigerant is watched by a gas sensor low in the cabinet that gates the remotely mounted compressor relay, and backstopped by a thermal fuse in the compressor's own AC primary. The carbonic-acid backflow path is held by a beverage backflow preventer whose vent weeps to the sensed ASSE drip pan as the mechanical telltale. The plumbed appliance's mains and ground-fault posture, the refrigerant charge limits, and the unit markings are consolidated in one place.

The whole safety and regulatory posture is in [`/business/regulatory.md`](/business/regulatory.md), which carries the qualification still owed on the retained donor terminal cover; the refrigerant-handling and brazing safety in [`/hardware/assembly/refrigerant-loop.md`](/hardware/assembly/refrigerant-loop.md) under "Safety". An integrated ground-fault (GFCI) module is a deferred desire, captured in [`/future/pie-in-the-sky/gfci.md`](/future/pie-in-the-sky/gfci.md).

### User-facing surfaces

Above the counter, the faucet lever pours, and the faucet display at the end of the gooseneck shows the selected flavor and switches it by touch. On the appliance's 45° top-front facet, angled up toward the standing user, the enclosure display is the configuration surface, over the flat face that is the pump cartridge's own. Flavor is refilled from the top: lift the silicone funnel out and pour. The pumps are reached from the front instead — pull the pump cartridge and both are in your hand. Once the cartridge is clear, its cord unplugs from the pump jack, an RJ11 keystone centred behind the display; the plug's clip faces down into the empty bay, and the fixed lead returns to J13 through the cable clip near that ridge wall's +X edge. Returning it is a deliberate two-hand fluid connection: click the plug into the pump jack, squeeze the two recessed side tabs, bottom the four pump tubes, then release the tabs and confirm they settle evenly at connected.

The faucet's printed parts — the faucet shell, the above-counter plate, the above-counter gasket, the o-ring — are in [`/hardware/printed-parts/faucet/`](/hardware/printed-parts/faucet/), over the cut [`under-counter plate`](/hardware/cut-parts/faucet/). The displays' reference geometry is in [`/hardware/reference/waveshare-43b-display/`](/hardware/reference/waveshare-43b-display/) and [`/hardware/reference/touch-flo-faucet/`](/hardware/reference/touch-flo-faucet/); the facet the enclosure display is let into, and the pump cartridge under it, in [`/hardware/printed-parts/enclosure/enclosure/README.md`](/hardware/printed-parts/enclosure/enclosure/README.md); the funnel in [`/hardware/printed-parts/zone-c/README.md`](/hardware/printed-parts/zone-c/README.md). What the customer does on install day is drawn in [`/hardware/quickstart/`](/hardware/quickstart/). The behavior these surfaces drive is firmware — [`/firmware/`](/firmware/).

### Build order

The sequence the whole appliance is built in is the dependency chain of the procedure docs in [`/hardware/assembly/`](/hardware/assembly/), with the skilled-hand tasks summarized in [`handwork.md`](/hardware/assembly/handwork.md): carbonator, cold core, refrigerant loop, then three benches that run in parallel with that chain and feed the chassis — cable assemblies, power column, faucet and umbilical — then the loose-front-top manifold mechanism, enclosure closure, the remaining internal plumbing, wiring, commissioning, burn-in, pack and ship.

[`internal-plumbing.md`](/hardware/assembly/internal-plumbing.md) §3 begins before enclosure closure because `enclosure-front-top` is the assembly fixture. Its order is aft valves; two springs and the empty carrier lowered into the guides, followed by the two separately installed rigid tab arms and tab locks; four tees inserted individually; two ties per tee; fore valves and four bowed flex stubs; then cartridge connection after the box closes by squeeze, bottom and release. The rest of internal plumbing follows [`enclosure-mechanical.md`](/hardware/assembly/enclosure-mechanical.md), and [`wiring.md`](/hardware/assembly/wiring.md) takes a chassis that already carries its plumbing. The card deck in [`/hardware/assembly/cards/`](/hardware/assembly/cards/) prints in this order.

## Layout

| Path | What's there |
|---|---|
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

A generated `.step` is on this disk and in no index. [`cad-artifacts.lock.json`](/hardware/cad-artifacts.lock.json) names each one by sha256, the release asset carrying them, and the commit each came from — `source.commit` for the bundle, and an `unproven` entry naming the uncommitted paths a pack was cut beside and the members they reach, since a solid mid-edit still ships. [`tools/cad-artifacts/pack.py`](/tools/cad-artifacts/pack.py) builds and pins one, and the deploy runs the fetch above (`render.yaml`). A build cuts them too, so a checkout that runs one needs no fetch. The three harvested solids under [`reference/`](/hardware/reference/) have no builder here and are in the index.

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

The export and render rows are timed at `189e46a0`; the two derive rows at `7101d08c`.

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
- **`material`** (string) — free-form, in the spec language you'd put in a quote or order: `"304 stainless steel"`, `"316 stainless steel"`, `"PETG"`, `"PET-GF"`, `"Bambu TPU 90A"`, etc.
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
