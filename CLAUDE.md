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

## CadQuery

Run scripts with the project's CadQuery venv: `tools/cad-venv/bin/python`.

See `hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py` for patterns to follow, and its companion `touch_flo_shell.md` for the idioms those patterns embody.

A generator that writes a STEP also renders its `.step.png` thumbnail at exit via a headless browser — tens of seconds on a large assembly. `HSM_SKIP_THUMBNAILS=1` skips that render for fast iteration; the dev-server watcher already sets it and rebuilds thumbnails off its own critical path.

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