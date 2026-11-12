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

## Numbers in Prose

Don't write numbers into code comments or documents. They go stale when the code moves, and a
stale number does more harm than good. There are plenty of other ways to get a number when you
need it: the constant that owns it, the program that prints it, `hsm` for the geometry. What the
site shows is the exception: the ledger behind the costs page keeps its figures.

## Questions

Don't ask Derek what the repo already answers. What he owns and has on hand is in [`hardware/ledger/`](hardware/ledger/): every purchase in `purchases.md`, sorted by role into `bom.md`, `tools.md` and `inventory.md`.

For geometry questions about the machine, [`hsm`](tools/hsm/README.md) measures the mesh
payloads in the checkout. Claude Code and Codex sessions have its tools: `hsm_where`,
`hsm_gap`, `hsm_overlap`, `hsm_move`, `hsm_section` and `hsm_ray`. In a shell they are
`hsm where <name>`, `hsm gap <a> <b>`, `hsm overlap <a> <b>`, `hsm move <name> --by <x> <y> <z>`,
`hsm section` and `hsm ray`. A query starts no CAD build. Each reply names the payload it
measured, so a source edit shows once its producer exports a new payload. `root` (`--root`)
picks another worktree and `scene` (`--scene`) another assembly.

An already-open MCP connection retains its reader build. If it reports an old-reader or
whole-scene cache error, use the installed `hsm` CLI, which adopts the installed reader.

For remembered descriptions, brands or part numbers, `node tools/find-part.mjs "water regulator"`
uses the same material search as `/3d`. It returns candidates, source producers, build targets
and published model links. Suggestions retain their uncertainty; use the returned identity
when a description could mean more than one part.

For a named construction feature, add `--context` to its exact key in `find-part.mjs`.
It reads the current source, dimensions, compiler-recorded references and other exported
features authored in that file. References are leads to inspect, not inferred fit constraints.
Use `tools/inspect-part.mjs` for a focused view or `--measure-only` for a clearance, interference or passage
question. Reuse its saved inspection to retain the subject, camera, neighbours and rays while
reading the next export. These commands run only when the current question needs them.

## Mechanical Layout

Finish the mechanical layout before placing Wagos or routing wires. Position
Wagos and route wires around the finished mechanics. Their existing positions
and routes do not constrain mechanical changes.

## Sourcing

Two things decide where a part comes from: lead time and volume. It ships from stock and arrives in days, and it is the high-volume part for its job, the one most people buy for that job today.

Amazon Prime is the default because a Prime listing usually has both. Any other store that has both is a source I'll like: a manufacturer's or distributor's own shop that ships the part from stock, such as FWS, Digi-Key, Mouser or the maker itself. On Amazon, a listing without the Prime logo doesn't count. Do not read it. Do not mention it.

Your MCP reaches my Chrome on this Mac, which is signed in to my Amazon. The Windows laptop is my work laptop. Never use its Chrome.

## History

Git keeps history. Code and docs in this repo describe current state. Don't write "was X, now Y" or decision narratives in current files. Don't defend the current choice against alternatives the reader hasn't asked about. The repo describes only what is.

When Derek identifies a class of obsolete work, trace why the example persisted and
investigate the other instances of that class. Removing a design includes its unused
catalog identities, relationships, publication entries and agent-facing commands.
When Derek shares a print result, save his photos and observations with the
print they document. Hand off the result by its file path or archived Git link.
Archive completed and retired trials in Git, including their physical evidence, and
remove their working-tree copies. Current instructions that use a past observation
link to the archived file at its Git SHA.

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

## Fitted

When Derek tries a made part in hand and says anything affirmative about it, add a row to
[`hardware/ledger/fitted.json`](hardware/ledger/fitted.json): the part's material number, the
date, his words exactly, what he tried, and where the fuller record is. The bar is "good
enough": anything he says along those lines once he has tried the print counts, with whatever
flaw he names beside it. A remark about a model or a picture is not a try. When a later try of
that part fails in his hands, take the part's rows out; Git keeps them.

The site reads the record and measures nothing. A printed part shows as fitted or not fitted
yet, and the list behind the machine's mark names its printed parts that are not fitted yet.

## Missing Tools

A script you write because nothing in the repo answers your question is a tool the repo lacks. [`calibration/principle/Positions.md`](calibration/principle/Positions.md) shows one: a ten-minute search for a part's move, beside the same move read off the scene in a second. Derek decides what joins the repo.

## Enclosure Changes

Every change to the enclosure's geometry has an entry in [`changes/`](changes/README.md), shown at [homesodamachine.com/changes](https://homesodamachine.com/changes): a before and an after picture of what changed, from one camera, with a short lede. The before is the snapshot taken ahead of the rebuild, `node tools/changes/change.mjs snapshot`; nothing else keeps it. [`changes/README.md`](changes/README.md) has the rest. Recording follows the change and never holds it up.

## Showing the Machine

To show me a part or a spot in the machine, link the published model on the site. A link that
closes on `?find=` lights and labels what it points at and turns the camera to it;
[`hsm-pick link`](tools/hsm/inspection/README.md) writes one. No agent publishes a
3D scene of its own to show something.

## What Counts

Two things count: what I see on the website and what I print. Everything else is a means to
those two. An output, check or report that feeds neither can go, and so can an expensive detail
of the website that isn't needed, such as a check in the `/3d` checks modal.

Every part has a manufacturing process, and its process names its build:

- The **print build** makes what the H2C and Mark2 print here. It is the normal build, because
  printing is what we iterate on.
- The **cut build** makes the DXFs and drawings SendCutSend cuts parts from.
- The **PCB build** makes the Gerbers, parts list and placement file JLCPCB makes the boards from.

The cut and PCB builds feed neither the website nor a print here, and they are still needed: they
stay generatable, outside the normal build, and run when an order needs them. Bought parts have
no build. The website's 3D model shows every part, whatever its process.

A change keeps the machine the same when the website shows the same things and the same solids
print, within the kernel's rule. Nothing else has to match: intermediate files, report wording,
error text and float rounding can all change.

## Purpose

Every piece of machinery says in one line what it is for, where it is defined: a build step, a
check, a report, a cache, a lock, a program. The line is in the present tense, as in "`tools/run`
keeps heavy runs from running this Mac out of memory." When the line stops being true, the
machinery goes. Something with no line gets one before anything is built on it.

## Speed

Every agent's builds run on this one Mac. The goal is the time from Derek's request to the
first relevant source-authored change visible on the website. Discovery, tool recovery,
agent review iterations and machine waits all contribute. Publish completed parts while
other parts and focused review continue, and say what remains under review. First view,
checked geometry and print readiness are separate milestones.

Use the existing part search, source attribution, physical fit records and targeted geometry
queries to answer the next design question. Read the instructions that apply to the task;
keep detailed constraints beside the geometry or physical record that owns them.
[`tools/iteration/`](tools/iteration/README.md) records request and view milestones when
someone asks for a timing measurement. It adds nothing to ordinary edits or builds.

The build runs in Rust on the `hsm` kernel, and its speed work is closed:
[`tools/hsm/conversion.md`](tools/hsm/conversion.md) records it. Speed work opens again from a
measured request in which the build is the long part.

A concept, a throwaway part or a study starts in Rust too: [`tools/hsm/sandbox`](tools/hsm/sandbox/README.md)
is a file to copy and a command to rerun, with nothing to set up.

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

## Shared Checkout

All agents on this Mac work in `/Users/derekbredensteiner/Developer/homesodamachine`
on `main`. Use this shared working directory so every agent sees the others'
source edits immediately. Do not create branches, worktrees or separate repository
copies. Keep `main` current with `origin/main`, preserving other sessions' work,
and commit and push directly to `main` using the path-scoped commit rule above.

## Temporary Build Files

Reuse the artifacts already held by `hsm`. Do not copy whole build
trees into `.cache` for comparisons, handoffs or publication. When a snapshot is
needed, save only the required files in `.cache/runs/<purpose>-<run-id>`.
Keep private benchmark caches inside the same run directory.

Remove a run's temporary files when its comparison, publication or handoff is
finished. Keep concise results, source revisions, artifact hashes and measured
numbers. Keep current deliverables and active print records at their recorded
destinations outside `.cache`. Completed experiments, including their print records,
are archived in Git and referenced by SHA; a scratch copy is not an archive.

The existing six-hour cleanup removes individual run directories after three
days without a write. A new run does not extend an older run's lifetime. Keep the
shared geometry memo caches (`realized`, `meshes`, `boxes`) and installed runtimes.

## Heavy Runs

The normal print build is `tools/run -- hsm-print-build --`.
Additional producer names select smaller builds. Each completed producer reaches the
website while the remaining producers continue.

Use `tools/run -- <command>` for Cargo, slicing and rendering.
Add `--cad` for a native CadQuery/OCP command and `--timing` for a timing run
that needs the machine to itself. Kernel part generators use the installed
`hsm` engine. Ordinary runs need no coordinator grant.

The shared host scheduler admits at most four logical runs, spaces concurrent
starts by 30 seconds, and waits before a new run while macOS memory pressure is
critical or used swap exceeds 10 GiB. Running jobs continue. Set the live count
with `tools/run --count 1` or `--count 4`.

Children share their parent's verified lease. Native work also takes the CAD
lock; `HSM_NO_BUILD_LOCK=1` alone bypasses neither admission nor that lock. Keep
Cargo at two jobs and run it through the wrapper so its compiler lock is shared
with the native engine. Producer runs inherit their parent's verified lease.

The protocol and entry points are in
[`tools/hsm/run-slots/README.md`](tools/hsm/run-slots/README.md).

## Publishing

Complete requested repository changes by committing and pushing to `main` without asking for separate confirmation.
