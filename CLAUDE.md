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