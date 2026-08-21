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

The appliance's controller is `firmware/src_appliance/`, on the PCBA's own WROOM. Its front-face display is `firmware/src_front/`, and the two talk over J9. Seven trees, one per board: `firmware/README.md` says which runs where.

## tscircuit forks

The pcba board (`hardware/pcb/pcba`) consumes forked `@tscircuit/*` packages (and `circuit-json-to-gerber`) via git-dependency `overrides` in its `package.json`. The local working trees are at `~/Developer/tscircuit-forks/<pkg>` — branch `homesodamachine/through-hole-vias`, with an `upstream` remote for syncing. See `hardware/pcb/pcba/FORKS.md`.

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

Always commit and push to main. Don't ask. Just do it. The author of everything here is always me (via an instance of you), and you can trust it's worth committing and building on top of. It's all the same work.

## Calibration — read this before you decide to stop

`calibration/` is the worked-out record of where agents in this repo go wrong. It is not
background reading. Two of its documents describe failures every fresh agent repeats:

- [`calibration/Discretion.md`](calibration/Discretion.md) — I soften instructions because the
  flat register costs me nothing. *"Perhaps you can"*, *"if you can"*, *"whenever you want it"*
  are instructions. Ending your turn on an offer — *say the word*, *want me to?* — puts it in
  the one position on the page I never read, and produces the one output with no value: prose
  about a state that does not exist. **When the directive force of a sentence is ambiguous, the
  tie goes to acting.**
- [`calibration/Traffic.md`](calibration/Traffic.md) — agents go read-only, narrow a commit, or
  hold a step because they believe another session is live in the tree. Those boundaries do not
  exist. A dirty file is just a dirty file, usually mine, often a slicer. Never say another
  session is doing something, never defer anything to "whoever picks it up next" — nobody picks
  it up — and never leave a gate red on that reasoning.

[`calibration/Fences.md`](calibration/Fences.md) is the same for limits you are about to report,
and [`calibration/Principle.md`](calibration/Principle.md) for why these are examples and not
rules. Read the two above before your first commit, not after I point you at them.

## Landing your work

Finish the cycle. Don't stop partway and hand me the rest.

1. Build and verify:

   ```
   bazel build $(tools/cad-venv/bin/python tools/bazel/affected.py)
   ```

   `affected.py` reads git's own list of what moved and names the targets it reaches. **The
   half to read is stderr**: a changed path no target holds means the list under it is smaller
   than the tree owes, and `//:everything` is what answers that one.

   **A WARM TREE IS ALREADY CHEAP, so read a build's action count and not its wall clock.**
   Bazel runs the actions an edit reaches and no others, whether the command names one target
   or `//:everything`. On this tree: a no-op is 0.2 s, and one part's geometry moving is 13 s
   and **one** sandboxed action. Fourteen minutes is a different operation — a cold checkout,
   a `sync_tree --write` carry, or a module the whole graph imports — and that one is 97–159
   actions and swaps 6.5 GB on an 8 GB box. Three numbers have been quoted for "the build"
   here as though they were one; the action count is what tells them apart.
2. Sync the docs and the ledger for whatever you moved.
3. Commit **by pathspec** — `git commit -F - -- <paths>` — never `git add -A`. One checkout, one
   `main`; the pathspec form takes files straight from the tree without touching the shared index.
   It only takes files git already tracks, so a NEW file needs `git add <its path>` first — name
   the paths, never `-A`, and commit straight after so nothing of yours sits in the index.
4. `git push`.
5. **If geometry moved, repin the artifact lock**, then commit the lock and push:

   ```
   tools/cad-venv/bin/python tools/cad-artifacts/pack.py --write
   ```

   The pre-commit hook already names this as the follow-up your commit owes and prints the
   command. **It is not a publish and it is not my call.** It uploads a content-addressed bundle
   to a `gh release` on this same repo — where your push just went — and never rewrites one. Run
   it. Never leave it owed, and never ask me first.

A pathspec commit takes the **worktree**, not just your edits. If a path you name holds changes
you didn't make, you commit those too — so before pushing, `git show HEAD:<other-file> | grep`
whatever the swept code newly references. A change split across two files leaves HEAD broken on a
clean checkout. If a dirty file isn't yours, leave it out and say so — without inventing whose it is.
