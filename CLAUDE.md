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

That venv is `.gitignore`d and one machine's own, so the import shim it reads at startup is
tracked separately and copied in — the same way the venv is built rather than committed:

```
tools/cad-venv/bin/python tools/cad-venv-site/install.py
```

`--check` says whether this checkout's interpreter has it. Without it every CAD process loads
VTK, which nothing here draws with, and pays 145 MB and two seconds for it; the solids are
byte-identical either way, so a tree that has not run it is slow and not wrong.

See `hardware/printed-parts/faucet/faucet-shell/faucet_shell.py` for patterns to follow, and its companion `faucet_shell.md` for the idioms those patterns embody.

See `hardware/printed-parts/AGENTS.md` before shaping any printed part — what a part is made of, the drawn mesh that reviews it, and where the support policy lives.

## Firmware

The appliance's controller is `firmware/src_appliance/`, on the PCBA's own WROOM. Its front-face display is `firmware/src_front/`, and the two talk over J9. Seven trees, one per board: `firmware/README.md` says which runs where.

## tscircuit forks

The pcba board (`hardware/pcb/pcba`) consumes forked `@tscircuit/*` packages (and `circuit-json-to-gerber`) via git-dependency `overrides` in its `package.json`. The local working trees are at `~/Developer/tscircuit-forks/<pkg>` — branch `homesodamachine/through-hole-vias`, with an `upstream` remote for syncing. See `hardware/pcb/pcba/FORKS.md`.

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

Always commit and push to main. Don't ask. Just do it. The author of everything here is always me (via an instance of you), and you can trust it's worth committing and building on top of. It's all the same work.

## Other sessions

Several sessions work this tree at once, all on main, all committing. A dirty file you did not write is the normal state. It does not matter who commits what, as long as it all gets done.

So: don't go read-only on sight of someone else's edit, don't narrow a commit to dodge their hunks, and don't end a turn offering to wait for the tree to settle. Commit your own work in small pieces as it lands. The collisions here are between running programs and the artifacts they produce, and meeting them live is what surfaces them — a merge would not.

Wait on the inputs your work reads, never on a clean tree: with sessions live `git status` is never empty, so a wait armed on it never fires. `tools/bazel/graph.json` names what each generator reads. A file that parses and has not been written in a minute is one you can read.

`calibration/Traffic.md` is the record — five sessions of this, and what the collisions produced.

## Reconciliation waits for silence

Iterate fast while I'm responding: make the change, show me the result, show me on
homesodamachine.com. Don't reconcile first. When I go quiet, that is when you reconcile — run the
full derive, resync the ledger, the docs and the deck, close whatever is behind. The moment I ask
for anything, stop reconciling and come back. A commit is a checkpoint, not a claim that
everything downstream of it is current.

There is no final release to hold work for. Publish each iteration as it becomes coherent and put
it in front of me; work held back for a ceremonial cut is work nobody has reviewed.

## A check costs the loop

Nothing goes into the build that makes it slower. A gate that turns a five-minute derive into a
twenty-minute one has cost more than it can return: the review here is my eye on the drawn part,
and time added between an edit and that look is taken from the only reviewer that finds these
defects. Prove a change by deriving it and looking at it. Existing gates stay and get faster where
they can; a new one earns its wall time against the loop it slows, and one that cannot is not
written. [`hardware/ledger/build-time.md`](/hardware/ledger/build-time.md) prices what a run
takes, and `_build_time.py --check` names a generator coming in slower than its row.

## Calibration

`calibration/README.md` indexes the working calibration between us. `Principle.md` (a rule is better encoded as an example; explanatory comments are residue), `Fences.md` (a reported limit is usually the edge of the box you searched), `Traffic.md` (this tree, shared), `Discretion.md` (a turn that ends on an offer spends it on the one output with no value).
