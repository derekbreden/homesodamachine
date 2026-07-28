# Home Soda Machine

## What This Is

A home soda machine — a kitchen appliance that dispenses flavored carbonated water from a faucet. In the prototype, refrigerated carbonated water is provided by an external carbonator (Lillium, Brio). When flow is detected, peristaltic pumps inject flavoring through a parallel line. Two flavors, each primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before.

The prototype under the counter dispenses from a Lillium-class external carbonator. The integrated appliance under development consolidates the carbonator into the same enclosure.

See `hardware/future.md` for details.

## Why This Exists

Pepsi and Coke will not sell bag-in-box syrup to home consumers without a business license. Pepsi does sell their own brand formulations as SodaStream-compatible syrup (1:20 ratio, sucralose, no sugar) to home consumers. Diet Mountain Dew syrup made by Pepsi is Diet Mountain Dew — not an off-brand approximation.

Dispensed through chilled carbonated water, the result is indistinguishable from the canned product, with equal or better carbonation and temperature. It is the same product, colder and fizzier than a can, on tap.

There is no machine on the market that gives a home user this experience — turn the handle, soda comes out. The alternatives are hauling cans from the store every week, or home carbonation products that carbonate warm water into bottles that go flat within hours. Despite enormous initial sales, very few people stick with home carbonation because warm water cannot hold carbonation — it is flat before it reaches your glass.

See `marketing/target-market.md` for details.

## Editions

There is more than one machine in this repo, and each gets a whole tree of its own — its own generators, assemblies, tools and outputs. `web/lib/editions.js` is the list:

- **kitchen** — `hardware/`, the counter appliance.
- **thin** — `thin/hardware/`, the tall, narrow machine.

They are duplicates, not variants: no flag selects between them and no module is shared to keep them in step. Cut one however the work demands without asking what it does to the others.

The viewer serves one edition per request (Settings → Edition, dev mode only), and the dev-server watches, rebuilds and broadcasts for every root. Adding a third is one entry plus the directory.

The trees mirror each other's filenames, so a path that leaves its own tree is invisible — the script runs, the STEP is written, and the number came from another machine. A shared path that fails to leave is the same mistake pointed the other way: it names a `tools/` the edition has no copy of, and the import dies. Two things hold both off:

- Anchors have two jobs and say which. Content resolves to the *nearest* `hardware/`; shared machinery (`tools/`) resolves to the repo root that holds `tools/docgen`. A positional anchor — `.parent`, `.parents[N]` — says neither, and lands on whatever sits that far up. In a single tree all three land in the same place, which is why it goes unnoticed until there are two.
- `tools/check_editions.py` resolves every anchored path in every edition's Python and fails on one that lands on the wrong tree: content that leaves the edition without being declared in that edition's `shares`, or shared machinery that stops inside the edition where there is nothing. Both declare nothing.

```
tools/cad-venv/bin/python tools/check_editions.py
```

## CadQuery

Run scripts with the project's CadQuery venv: `tools/cad-venv/bin/python`.

See `hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py` for patterns to follow, and its companion `touch_flo_shell.md` for the idioms those patterns embody.

A generator that writes a STEP also renders its `.step.png` thumbnail at exit, by driving the real /3d viewer in a headless browser — so the committed thumbnail is the detail view's own x-ray render. It hands the browser the tessellation it already has (`hardware/scripts/_mesh_payload.py`) rather than making it read the STEP back through occt in wasm, which puts a large assembly at a couple of seconds, nearly all of it browser boot. `HSM_SKIP_THUMBNAILS=1` skips the render entirely; the dev-server watcher sets it and rebuilds thumbnails off its own critical path.

`_mesh_payload.py selftest` checks that what is handed over is what the viewer would otherwise have read — the tessellation against occt-import-js itself, and the colors against a STEP round trip. Run it if thumbnails start looking wrong.

`HSM_SKIP_CLEARANCES=1` drops the enclosure scorecard's per-run "nearest N mm to X" report — an exact solid-distance query from every routed tube to every body, and the largest single cost of a route-only rebuild. Set it while iterating on where a line runs; `lines-clear` still gates on a tube driving through a part. The build you commit runs without it, so the committed scorecard carries its clearances measured.

## Asking the geometry

`hardware/scripts/probe.py` queries the placed world — the enclosure pack, the panel bodies, the funnel and the routed tubes, as one flat `{name: shape}`. It answers where a body sits, how close two come, what a candidate volume runs into, how far a line travels before it hits something, and how any of those move across a continuous parameter. Import it the way `pick_text` is imported, or run it:

```
tools/cad-venv/bin/python hardware/scripts/probe.py boxes --sort ymin
tools/cad-venv/bin/python hardware/scripts/probe.py gap foam-assembly compressor-shroud
tools/cad-venv/bin/python hardware/scripts/probe.py at bag-circuit-assembly.Y-H-2
tools/cad-venv/bin/python hardware/scripts/probe.py cast 110.1,155.9,253.3 0,0,-1 --dia 6.35
tools/cad-venv/bin/python hardware/scripts/probe.py hits --x 100,120 --y 160,200 --z 30,275
```

Every query raises rather than degrading: a body that will not normalize, a boolean that fails, a distance that cannot be taken exactly. A cast that reaches its limit reports that it made no contact, because its length is a property of the probe and not a clearance. `probe.py selftest` runs known-answer controls — a known hit, a known miss, a known distance, a known refusal — and then normalizes every body in the real world. Run it when a number looks wrong, before trusting the number.

A claim about where something sits, what it clears, or which poses are available is a claim this tool can settle. Settle it before stating it, and quote the query.

## Trying a part somewhere it isn't yet

`hardware/scripts/fit.py` is the other half: `probe` asks about the world as it stands, `fit` asks about a body that is not in it. It discovers a reference part's builder and ports from `hardware/reference/<name>/`, carries it to a pose, and measures it against the placed world.

```
tools/cad-venv/bin/python hardware/scripts/fit.py parts
tools/cad-venv/bin/python hardware/scripts/fit.py ports beduan-solenoid
tools/cad-venv/bin/python hardware/scripts/fit.py try meanwell-irm90 --bbmin=0,180,267.5 --yaw 90
tools/cad-venv/bin/python hardware/scripts/fit.py mate gasher-check-valve --port inlet --onto seaflo-pump.discharge
tools/cad-venv/bin/python hardware/scripts/fit.py search meanwell-irm90 --x=-14,60,6 --y=176,200,6 --z=267.5 --yaw=90 --anchor bbmin --clearance 1
tools/cad-venv/bin/python hardware/scripts/fit.py slab --z 267,331 --size 52,109 --exact seaflo-pump
```

The body and its ports move under one `cq.Location`, so a port always sits on the face it names — a pose rotated by hand alongside a port rotated by hand is two implementations of one transform. `pose.port(name)` returns the world position and axis. `anchor` picks what lands on the coordinate you give: `at` is the part's own origin, `bbmin` is its rotated bounding box's low corner, which is how `_contents._at` seats a body in the pack.

`mate` is the pose a fitting takes when it is put on the thing it connects to: give a port the position and normal of the mouth it joins and the body follows, so the answer to "where does the far end land, and what is already there" is one query rather than a rotation worked out by hand. A port's axis points out of its part, so mating seats the two mouths facing each other; `--along` points it the other way.

Clearance is a threshold on an exact measured distance, never an inflation of the obstacles, so raising it can only ever remove poses. `search` reports the free poses ranked by the room they leave; the body being re-placed must be named in `--skip`, or it clashes with itself.

`slab` maps a Z band instead of testing one part: the largest rectangles a footprint could stand in, inside the enclosure's own cavity. Obstacles count by their bounding box unless named in `--exact` — a part that is mostly air, like the pump, hides real space behind its box, and the two answers differ enough to reverse a conclusion.

Both scans state their bounds before their answer. `search` prints the box it ranged over — every range, every axis pinned to one value, the anchor, the bodies held out — and names the ends the best pose sits on; `slab` prints its field, where the field came from, which bodies it measured exactly, and whether its largest rectangle runs to the edge of a field you supplied. An end of a scan is a property of the grid and not of the geometry, so quote the box with the number: a "there is no room" that arrives without one is a claim about a search, and `calibration/Fences.md` is what it costs.

`fit.py selftest` checks the instrument: that a port stays on its body at arbitrary angles, that the fast reject and the full check never disagree, that clearance only removes, that a scan reports its own box and the ends its answer sits on, and that every reference part still builds.

## Firmware

Flash with `tools/flash.sh`.

## tscircuit forks

The pcba board (`hardware/pcb/pcba`) consumes forked `@tscircuit/*` packages (and `circuit-json-to-gerber`) via git-dependency `overrides` in its `package.json`. The local working trees are at `~/Developer/tscircuit-forks/<pkg>` — branch `homesodamachine/through-hole-vias`, with an `upstream` remote for syncing. See `hardware/pcb/pcba/FORKS.md`.

The pcba board is **100% hand-routed** — every signal connection is an explicit `pcbPath`; the capacity autorouter owns no copper. To author or move traces, see `hardware/pcb/pcba/hand-routing.md` (the `route`/`routeBottom`/`routeInner` frame idiom and the render→floor verify loop).

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

Always commit and push to main. Don't ask. Just do it. The author of any change you see is always me (via an instance of you), and you can trust my changes are worth committing and building on top of.