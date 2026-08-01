# Home Soda Machine

## What This Is

A home soda machine — a kitchen appliance that dispenses flavored carbonated water from a faucet. In the prototype, refrigerated carbonated water is provided by an external carbonator (Lillium, Brio). When flow is detected, peristaltic pumps inject flavoring through a parallel line. Two flavors, each primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before.

The prototype under the counter dispenses from a Lillium-class external carbonator. The integrated appliance under development consolidates the carbonator into the same enclosure.

See `thin/hardware/future.md` for details.

## Why This Exists

Pepsi and Coke will not sell bag-in-box syrup to home consumers without a business license. Pepsi does sell their own brand formulations as SodaStream-compatible syrup (1:20 ratio, sucralose, no sugar) to home consumers. Diet Mountain Dew syrup made by Pepsi is Diet Mountain Dew — not an off-brand approximation.

Dispensed through chilled carbonated water, the result is indistinguishable from the canned product, with equal or better carbonation and temperature. It is the same product, colder and fizzier than a can, on tap.

There is no machine on the market that gives a home user this experience — turn the handle, soda comes out. The alternatives are hauling cans from the store every week, or home carbonation products that carbonate warm water into bottles that go flat within hours. Despite enormous initial sales, very few people stick with home carbonation because warm water cannot hold carbonation — it is flat before it reaches your glass.

See `marketing/target-market.md` for details.

## CadQuery

Run scripts with the project's CadQuery venv: `tools/cad-venv/bin/python`.

See `thin/hardware/printed-parts/faucet/touch-flo-shell/touch_flo_shell.py` for patterns to follow, and its companion `touch_flo_shell.md` for the idioms those patterns embody.

## Firmware

Flash with `tools/flash.sh`.

## tscircuit forks

The pcba board (`thin/hardware/pcb/pcba`) consumes forked `@tscircuit/*` packages (and `circuit-json-to-gerber`) via git-dependency `overrides` in its `package.json`. The local working trees are at `~/Developer/tscircuit-forks/<pkg>` — branch `homesodamachine/through-hole-vias`, with an `upstream` remote for syncing. See `thin/hardware/pcb/pcba/FORKS.md`.

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

Always commit and push to main. Don't ask. Just do it. The author of any change you see is always me (via an instance of you), and you can trust my changes are worth committing and building on top of.

## Red Lands

A failing check does not block a commit. The generators have no failure exit — the `.step` and the scorecard sidecar are written whatever the gates say, and a pack that does not close carries its real overlapping geometry — and `.githooks/pre-commit` reports the enclosure's verdict without gating on it. The board's fab-ready gates are the exception; they block.

Commit broken work, push it, and say what to look at in the 3D viewer. Don't hold a change back because it scores red, don't revert to green before committing, and don't spend a session reaching a clean card before anything lands. The one thing that must not land is a build whose artifacts came from different source than the commit carries.

## The Long View

The thin enclosure assembly is the PCBA job with a third axis: not packing, composition. Done is a machine that reads as meant — every line swept on purpose, every part fastened to something printed, nothing anywhere just because there was room. The full statement of the standard is `thin/hardware/printed-parts/enclosure/enclosure-assembly/requirements.md`. The card's focus is `bend-radius` and `mounted`; every other axis waits gray behind them.

The envelope is fixed — never reach for the box. Inside it, everything moves: the layout is a draft, a pose derived from a neighbour is a line of code and not a law, and "X can't move" is the name of the next thing to move. Render before any claim about room — `tools/look.sh <body>[,<body>]` takes the three orthographic views of it (`calibration/Fences.md`; the whole-machine elevations sit beside the STEP). Prefer a move made to an instrument built — the tools to look already exist. The last tenth is noticing: unexplained variance — a crossing an assignment swap would uncross, mixed pitches, twins that don't read as twins — costs no room to fix, only attention. Fix the free ones; bring me the ties.