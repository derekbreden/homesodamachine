# Working method for explorers

Every explorer reads this file, [`brief.md`](brief.md),
[`shared-context.md`](shared-context.md) and [`xh-facts.md`](xh-facts.md).
Each wave's own instructions arrive in the explorer's prompt. This file holds
what stays the same across waves.

## The job

This is exploration. Develop possibilities Derek can understand and think with:
- challenge them;
- repair them;
- combine them;
- bring them back more useful for that work.

There is no competition, no winning design and no complete implementation plan.
A polished proposal gets no preference over a rough one, and a rough one gets
none for being unusual. A huge unresolved problem does not stop an idea from
being worth bringing back.

**Slowness is the premise.** The machine may take minutes per crimp, one
conductor at a time, running unattended while the printers run.
- Industrial wire processing is a source of physics and mechanisms, not a price
  anchor.
- "Commercial machines cost tens of thousands" is never a reason to stop.
- Ask what becomes simple, cheap or easy when speed does not matter:
  - dwell, re-grip and re-measure;
  - look, retry and back out;
  - do one thing per station;
  - let gravity, springs and friction do the placing;
  - use a light, slow actuator through a large mechanical advantage;
  - accept a 30-second cycle for a single step.

**Your framing is a way of seeing the whole procedure**, not only a subsystem:
splay, strip, place the contact, crimp, insert, verify. Weight goes to the step
Derek most wants automated: place the contact on the conductor, hold both in
something that crimps, and crimp. Every arrangement connects your viewpoint to
the actual things:
- the 22 AWG silicone ribbon at 1.7 mm pitch;
- the XH contact, loose or on its carrier strip;
- the XHP housing at 2.5 mm pitch;
- the 53 crimps per unit;
- the person at the bench.

Say which steps an arrangement automates and exactly what it hands back to the
person. A machine that only does one step, or needs a person to load it, is a
legitimate contribution.

Take a small number of ideas beyond their first attractive sketch. Depth can be
unequal where the ideas demand it.
- A list of mechanism names with pros and cons has not done the job.
- A drawing package or a complete parts list is not the goal either.

## Take it further, break it, fix it

"It will misalign" or "the wire is floppy" is a starting observation. Continue
into:
- which motion is free and which force causes displacement;
- what happens at each contact;
- what locates the contact relative to the die, and the conductor relative to
  the contact. Name the reference for "fixed".
- whether precision is needed continuously or only at certain moments:
  - loading;
  - the first die touch;
  - the bottom of the stroke;
  - the release.

Point to a specific conflict in a specific variant, and say what a repair
changes and what it leaves uncertain. If you cannot repair it, keep the idea and
the issue visible side by side. Your failure to find a solution does not prove a
whole family impossible. Do not hide a serious problem to keep an idea alive, and
do not drop an idea because a serious problem exists.

Preserve an original idea alongside the variants that change it. A replacement
is a branch, not what the originator "must have meant".

## Facts, estimates and assumptions

Label what you rely on:
- **[Derek]**
- **[repo]** with the file named
- **[mfr]**: a manufacturer document, with the link
- **[source]**: another published source, with the link
- **[calc]**: your calculation, kept in `calc/`
- **[estimate]**
- **[assumption]**

Old agent-written numbers in the repo are not requirements. When an unknown
matters, such as crimp force, contact springback or web tear strength, work
through the plausible range and say which conclusions depend on it. List the
measurements Derek could take that would settle it, but do not stop exploring
for want of them.

## Files

Everything lives under `future/jst-crimp-study/`. Your own directory is
`explorers/<your-name>/`:

| Path | What it holds |
|---|---|
| `summary.md` | Your account of every arrangement you hold. For each, a short paragraph and links to its idea file. Also transferable mechanisms and open questions for Derek |
| `ideas/<id>-<slug>.md` | One developed idea per file, `<id>` a short letter-number like `a1`. Branches get their own file, `a1b-...`, and say what they change |
| `sketches/*.svg` | Schematic sketches, labelled "schematic" unless the geometry comes from cited dimensions |
| `calc/` | Python or notes for any number you compute, with the output kept beside it |
| `notebook.md` | Running log, rejected directions (why, and what would revive them), questions |

Every idea file opens with a **"Picture it"** section: enough plain description
to see the arrangement operate. It covers:
- where the ribbon and contact start;
- what moves;
- what locates what;
- what drives the crimp and carries its force;
- how the machine knows the crimp worked;
- what the person does.

After that, cover what matters for that idea:
- the mechanism;
- its references and tolerances;
- printed parts and bought parts, with sourcing evidence;
- what was tried against it and the repairs or branches;
- its contribution;
- its **major unresolved problems**, kept beside it rather than in an appendix;
- which conclusions rest on assumptions.

Describe ideas as they stand. Problems, repairs and branches sit beside the idea
as its current state and are not written as a story.

Write for Derek: plain, specific and physical. Use no rankings, scores,
"recommended", "best" or "winner". Do not refer to Derek's family or relatives.

## Sourcing

- **Where to look.** Find representative purchasable parts when price,
  availability or physical capability shapes an idea. Use WebSearch and
  WebFetch for:
  - manufacturer documents (JST, Molex, TE, Bambu, and others);
  - distributors (Digi-Key, Mouser, LCSC, McMaster-Carr);
  - makers' write-ups (Hackaday, GitHub, forums, YouTube descriptions);
  - vendor sites.
- **Amazon.** Only Prime listings count, and non-Prime listings are never read
  or mentioned. Explorers **do not fetch amazon.com pages and do not use the
  Chrome tools.** When an idea wants an Amazon part:
  - record it in `sourcing-requests.md` in your directory: the item, the idea it
    serves, what capability matters, and search terms;
  - the coordinator's sourcing pass confirms Prime listings in Derek's
    signed-in Chrome;
  - in idea files, call such parts "Amazon, Prime to be confirmed" until then.
- **What to record.** For every sourced item, record:
  - source link;
  - date observed (2026-09-28 unless otherwise);
  - price;
  - stock or lead-time signal;
  - whatever supports volume or interchangeability.

  A listing's existence or a familiar brand is not evidence of volume.
- **Depth.** One or two representative sources establish that a route exists.
  No procurement audit and no every-bolt BOM.

## Boundaries

Stay inside `future/jst-crimp-study/`:
- Change nothing else in the repository.
- Do not commit.
- Order nothing and contact no vendor.
- Operate no equipment.
- Do not use the printers.

Questions that need Derek's observations or measurements go in your summary
under "Questions for Derek". They never block other work.
