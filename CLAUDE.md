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

`hardware/scripts/probe.py` queries the placed world — the enclosure pack, the panel bodies, the display, the funnel and the routed tubes, as one flat `{name: shape}`. It answers where a body sits, how close two come, what a candidate volume runs into, how far a line travels before it hits something, and how any of those move across a continuous parameter. Import it the way `pick_text` is imported, or run it:

```
tools/cad-venv/bin/python hardware/scripts/probe.py boxes --sort ymin
tools/cad-venv/bin/python hardware/scripts/probe.py gap foam-assembly compressor-shroud
tools/cad-venv/bin/python hardware/scripts/probe.py at bag-circuit-assembly.Y-H-2
tools/cad-venv/bin/python hardware/scripts/probe.py cast 110.1,155.9,253.3 0,0,-1 --dia 6.35
tools/cad-venv/bin/python hardware/scripts/probe.py hits --x 100,120 --y 160,200 --z 30,275
```

The thin edition's copy (`thin/hardware/scripts/probe.py`) also holds the four printed enclosure pieces, tagged `piece`, so its world is body for body what `scorecard.pack_clashes` measures: `w.parts` are the gate's `solids`, `w.pieces` are its `pieces`, and every query sees both. The walls, seam lips, cross-pin pods and boss chains are what bounds a placement in a full machine, and a world without them answers CLEAR exactly where the gate that blocks the build answers clash. `HSM_SKIP_PIECES=1` takes them out for a tree whose `enclosure-*.step` are not exported; every scan then says so in its header. The kitchen copy holds the interior pack alone, so a pose it calls clear may still stand in a wall.

Every query raises rather than degrading: a body that will not normalize, a boolean that fails, a distance that cannot be taken exactly. A cast that reaches its limit reports that it made no contact, because its length is a property of the probe and not a clearance. `probe.py selftest` runs known-answer controls — a known hit, a known miss, a known distance, a known refusal, a volume buried in a printed wall that every interior body clears — and then normalizes every body in the real world. Run it when a number looks wrong, before trusting the number.

A claim about where something sits, what it clears, or which poses are available is a claim this tool can settle. Settle it before stating it, and quote the query.

## Trying a part somewhere it isn't yet

`hardware/scripts/fit.py` is the other half: `probe` asks about the world as it stands, `fit` asks about a body that is not in it. It discovers a reference part's builder and ports from `hardware/reference/<name>/`, carries it to a pose, and measures it against the placed world — so in the thin edition a pose it calls CLEAR is a pose the enclosure's pack-closes gate agrees is clear, walls included.

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

`slab` maps a Z band instead of testing one part: the largest rectangles a footprint could stand in, inside the enclosure's own cavity. Obstacles count by their bounding box unless named in `--exact` — a part that is mostly air, like the pump, hides real space behind its box, and the two answers differ enough to reverse a conclusion. A printed piece is always exact and can never be boxed: its box is the whole machine, and a scan that took one by box would report a full cavity.

Both scans state their bounds before their answer, and what they measured them against. `search` prints the box it ranged over — every range, every axis pinned to one value, the anchor, the bodies held out, the world the poses were measured in — and names the ends the best pose sits on; `slab` prints its field, where the field came from, which bodies it took by box against which it took exactly, which pieces reach into the band, and whether its largest rectangle runs to the edge of a field you supplied. An end of a scan is a property of the grid and not of the geometry, so quote the box with the number: a "there is no room" that arrives without one is a claim about a search, and `calibration/Fences.md` is what it costs.

`fit.py selftest` checks the instrument: that a port stays on its body at arbitrary angles, that the fast reject and the full check never disagree, that clearance only removes, that a pose clear of every interior body but standing in a printed piece comes back CLASH, that a scan reports its own box and the ends its answer sits on, and that every reference part still builds.

## Looking at it

`probe`, `fit` and `arrange` answer in numbers. `tools/render/render-view.js` answers in a picture — the placed world through the same /3d viewer, at a camera and a visibility set you name, with the bodies called out in the margins, a millimetre grid ticked with the coordinate each line holds, a scale bar measured through the projection, and section clips.

```
node tools/render/render-view.js printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step --list --edition thin
node tools/render/render-view.js printed-parts/enclosure/enclosure-assembly/enclosure-assembly.step \
  /tmp/look.png --edition thin --view front --ortho --span 92 --target 53,55,240 \
  --clip y:0,112 --only pump-b,tee-y-e --xray pump-a
```

A body is solid, x-ray, ghost or hidden. `--only` names the solid set and gives each one its own tint, carried on its label chip; anything unnamed ghosts to feature edges alone. `--xray` holds faces at low opacity, for a body another one stands in front of. `--hide` removes, and the legend names every body it removed. `--view` takes the six elevations and `iso`; `--ortho --span` sets the half-height in millimetres, so a millimetre is the same length everywhere in the frame.

The legend goes on the frame and on stdout: the camera, the projection, the target, the span, the clip bands, the mm/px, the world rectangle the frame covers, and the count in each mode. A pattern that matches no body comes back with the names that are present. A view is a bounded scan like the other three — `calibration/Fences.md`.

Coordinates read off the grid agree with `probe boxes` to a few tenths, and `--list` prints the names `--only` accepts.

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