# Home Soda Machine

## What This Is

A home soda machine — a kitchen appliance that dispenses flavored carbonated water from a faucet. In the prototype, refrigerated carbonated water is provided by an external carbonator (Lillium, Brio). When flow is detected, peristaltic pumps inject flavoring through a parallel line. Two flavors, each primed and valve-locked for instant dispensing. The mixing happens in the user's glass, not before.

The prototype under the counter dispenses from a Lillium-class external carbonator. The integrated soda machine under development consolidates the carbonator into the same enclosure.

See `future/README.md` for where this is going and what done looks like, `hardware/README.md` for the machine as it stands, subsystem by subsystem, and `hardware/concerns.md` for the concerns already answered.

## Why This Exists

Pepsi and Coke will not sell bag-in-box syrup to home consumers without a business license. Pepsi does sell their own brand formulations as SodaStream-compatible syrup (1:20 ratio, sucralose, no sugar) to home consumers. Diet Mountain Dew syrup made by Pepsi is Diet Mountain Dew — not an off-brand approximation.

Dispensed through chilled carbonated water, the result is indistinguishable from the canned product, with equal or better carbonation and temperature. It is the same product, colder and fizzier than a can, on tap.

There is no machine on the market that gives a home user this experience — turn the handle, soda comes out. The alternatives are hauling cans from the store every week, or home carbonation products that carbonate warm water into bottles that go flat within hours. Despite enormous initial sales, very few people stick with home carbonation because warm water cannot hold carbonation — it is flat before it reaches your glass.

See `marketing/target-market.md` for details.

## Questions

Don't ask Derek what the repo already answers. What he owns and has on hand is in [`hardware/ledger/`](hardware/ledger/): every purchase in `purchases.md`, sorted by role into `bom.md`, `tools.md` and `inventory.md`.

## Amazon Prime

You have access to my Chrome which is signed in to my amazon through your MCP. I only care about Amazon Prime listings. Non-Prime listings are non-existent as far as I am concerned. Do not read them. Do not mention them. They do not exist.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

A commit takes the paths your session changed — `git commit -- <paths>`, with `git add <path>` first for a new file — and every other change stays in the tree as it is. The message ends in one trailer block:

```text
Session: <session title>
Derek: "<his words, exactly as typed>"
Derek: "<another passage, with ... marking a cut; a long one wraps onto
 lines that start with a space>"
Co-Authored-By: <the harness's line, when it adds one>
```

`python3 ~/Developer/claude-code-setup/jsonl2md/jsonl2md.py whoami` prints the session title, marked `(auto-generated)` when Derek hasn't named the session; in a cloud session, the `Claude-Session:` link names it. Each `Derek:` line is a passage of his that the commit answers, quoted exactly — never paraphrased. A commit nothing of his asked for has no `Derek:` line. `git log --format='%(trailers:key=Derek)'` reads them back.

## Concerns

[`hardware/concerns.md`](hardware/concerns.md) holds concerns that are already answered, so no agent raises them again. Agents are bad at telling a legitimate concern from one that isn't, so an agent never writes its own concern there. Tell Derek the concern. If he convinces you it isn't one, record his answer there. If he doesn't, it is work to do, not a row. If he doesn't respond, you haven't told him yet.

## Enclosure Changes

Every change to the enclosure's geometry has an entry in [`changes/`](changes/README.md), shown at [homesodamachine.com/changes](https://homesodamachine.com/changes): a before and an after picture of what changed, from one camera, with a short lede. The before is the snapshot taken ahead of the rebuild, `node tools/changes/change.mjs snapshot`; nothing else keeps it. [`changes/README.md`](changes/README.md) has the rest. Recording follows the change and never holds it up.

## Placement Sequence

The machine is placed in this order:

1. Envelope: the outer box and footprint, front face and faucet, seams between printed pieces, service openings.
2. Modules: cold core and compressor, PSU, pump cartridge, flavor manifold.
3. Hardware: valves, fittings, flow meter, regulator, check valves, PCB, display.
4. Hardware mounts: printed sockets, pedestals, saddles, walls.
5. Tubes: soda, flavor, gas and drain routes between ports.
6. Cables
7. WAGOs
8. Tube mounts: tube snaps, tie and strap passages.
9. Cable mounts: cable clips.

When you move something, only what comes earlier in the sequence can be in its way. Nothing later blocks the move: remove or ignore whatever later item is in the way, make the move, then rebuild what you displaced, in sequence order, before you finish.

## What Runs Every Time

"Correctness" is far too broad a goal to enforce on every commit. Everyone can defend a check once it is in; no one defends keeping one out. I will. Whatever runs on every commit, every build or every edit costs time on each run, and you don't predict well how often it will run when it doesn't need to.

- Nothing joins that path unless I asked for that specific thing: no hook, gate, scorecard row, build-stopping assertion or verification step added because it seems safer.
- A check runs when someone asks the question it answers, not because a file changed.
- In your own loop, check what the change touched, once. Don't re-run the machine's checks after every small edit.
- Taking something off that path needs no defense beyond its cost.

## Inline Visualizations

When creating or editing an inline HTML visualization, apply the
[mobile compatibility skill](tools/viz/inline-mobile/SKILL.md) alongside the
host's visualization instructions. Reuse its shared theme helper for text,
native controls, legends and canvas/WebGL colors. Save inline fragments in the
current chat's visualization directory. This adds no automatic build or commit check.

## Engineering Drawings

For requested dimensioned mechanical part drawings, use the
[engineering drawing workflow](tools/engineering-drawings/SKILL.md). It covers
finished-part requirements, generation, and separate annotation and layout
reviews within that drawing task.

## Publishing

Complete requested repository changes by committing and pushing to `main` without asking for separate confirmation.
