# i3b — Branch of i3: stagger the row so one push seats the contacts one after another, each one reported

- **Branch of:** [i3](i3-converging-shuttles-gang-push.md).
- **Numbers:** force-and-form's reading [f&f §6], [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §6], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) section E [calc w3 E].
- **Related:** [i6](i6-sort-then-push.md) and [i6b](i6b-post-bed-through-the-housing.md),
  where the same trick becomes constant-force tines on the backing blade.

**What it changes from i3.**
- i3 pushes the housing onto a row whose fronts are all on one line, and checks
  each contact afterwards with a pull-back.
- i3b sets the shuttles' clamps at **staggered Y positions**, each 0.3–1 mm
  behind the one before. Each clamp rides on its own **constant-force spring**,
  preloaded above the largest single insertion force.
- As the housing advances, the contacts reach their cavities in a known order.
  Each folds its lance, snaps and bottoms at a different housing position, then
  rides its clamp back at the spring's constant force while the housing goes on
  to seat the rest.

## Picture it

- The push is one slow move of the housing nest.
- The load cell trace shows N separate events, each where the stagger says it
  should be: a small rise, a snap, then a step up by one preload as that contact
  starts riding its clamp back.
- Counting the steps counts the seated contacts. A missing or early step names
  the cavity.
- **Per-contact confirmation without a load cell.** A flag on each clamp passes
  a sensor when it rides back. At 2.5 mm pitch the flags stagger into two rows,
  or the ELP camera watches a row of printed flags.
- The springs are flat coiled constant-force springs, or hanging weights, which
  a slow machine can use.

## At a glance

| | |
|---|---|
| **What locates each contact** | Its shuttle clamp, set to its staggered Y; then the cavity |
| **Reference for "fixed"** | The shuttle base; each clamp's rest position against its stop |
| **Crimp force** | None here: an insertion module on i3's row. The push is carried by the nest drive and, per contact, by its clamp's spring at the preload |
| **How it knows** | N steps in the push trace, each at its expected housing position; a flag per clamp seen by the camera or a switch |
| **Steps it covers** | Gang insert with a per-contact seating report |
| **What it hands back** | As i3 |

## Numbers [f&f §6]

- **Why constant force.**
  - The force path runs from the housing's front wall through box, contact,
    crimps and wire to a clamp 2–4 mm back.
  - With ordinary springs and a 1 mm stagger on J1's nine contacts, the first
    clamp rides back up to 8 mm and ends at 36–70 N. That is 92–179 % of JST's
    39.2 N pull-out minimum, pushing the brush toward the box. At 60–70 N the
    4 mm of wire between clamp and crimp also buckles (K = 0.5 limit
    2.9–3.5 mm).
  - A 0.3 mm stagger still peaks at ~25–42 N.
  - A constant-force spring holds the load at its preload however far the
    clamp rides.
- **Preload = 1.25 × the largest single insertion force:**

  | Single insertion force | Preload | Share of pull-out minimum |
  |---:|---:|---:|
  | 8 N | 10 N | 26 % |
  | 9.8 N (KONNRA clone spec max [source]) | 12 N | 31 % |
  | 12 N | 15 N | 38 % |
  | 15 N | 19 N | 48 % |
  | 25 N | 31 N | 80 % |

- A 0.3 mm stagger puts events 0.3 mm apart: at 0.2 mm/s and 80 SPS, ~120
  samples between them [calc geometry §6].
- The same springs also absorb a contact length spread: the longest contact
  bottoms first and rides back [calc w3 E].

## What it costs

- **The stagger reintroduces stored feed.** Each clamp that rides back pulls its
  conductor with it, so each needs slack equal to its ride-back (up to the whole
  stagger span) between clamp and web. It is the feed-length rule with small
  numbers: 0.1–0.5 mm of ride-back is a 0.9–2.4 mm bow over a 20–30 mm split
  [calc w3 E].
- **Sustained load on the first contacts.** The preload presses the box on the
  PA6 front wall around the post opening until the push ends.
- **Spring packaging.** Flat constant-force coils are wider than the 2.5 mm pitch
  [assumption]. They stagger in 3–4 rows or act through push-wires, or hanging
  weights on threads do the job.

## Contribution

It turns a gang push, blind to single contacts, into a sequence that reports
each contact in one motion. The stepped-preload trick applies to any gang
insertion; in [i6](i6-sort-then-push.md) it is the alternative to a finishing
tine.

## Major unresolved problems

- Stored feed at the clamps.
- Where flags or sensors go at 2.5 mm pitch, and where the springs go.
- Whether single insertion is ≤ ~12–15 N. Derek's scale under one housing
  decides whether i3b stands.

## What rests on assumptions

- Single insertion 8–25 N, bracketed; the KONNRA clone spec says ≤ 9.8 N.
- Constant-force spring width [assumption].
