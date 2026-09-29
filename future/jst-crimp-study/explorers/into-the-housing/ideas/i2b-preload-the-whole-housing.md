# i2b — Branch of i2: load every cavity first, crimp each in place, push them all home together

- **Branch of:** [i2](i2-crimp-in-the-cavity.md) (K1).
- **Related:**
  - [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md), whose two-pass branch
    is this idea run on pre-formed contacts;
  - terminal-supply's [x3](../../terminal-supply/ideas/x3-stage-crimp-one-push.md),
    which stages every other cavity with a post through its front opening,
    crimps each where it stands, stages and crimps the rest, and pushes once;
    its insulation mouth in the second pass meets the same limit as here.
- **Numbers:** [`../calc/insertion_geometry.out.txt`](../calc/insertion_geometry.out.txt)
  [calc geometry §n], [`../calc/wave3.out.txt`](../calc/wave3.out.txt) [calc w3 X],
  force-and-form's [`on_into_the_housing.out.txt`](../../force-and-form/calc/on_into_the_housing.out.txt) [f&f §n].
- **Sketch:** the end views in [`../sketches/insulation-mouth.svg`](../sketches/insulation-mouth.svg) (schematic).

**What it changes from i2.**
- i2 places, crimps and seats one contact per cycle.
- i2b loads the housing with contacts at the shallow depth first, crimps them
  one after another, then seats them all in one push.
- Placement becomes a separate batch job that the person or a loader does ahead
  of time. The housing arrives at the press loaded like a magazine.

Everything i2 carries applies here: the lance condition, the floating nest, the
3.1 mm stepped crimper bottoming on anvil shoulders inside a steel C with a
knee, and the proof pull before the push.

## Picture it

1. **First pass.** The person, or a loader, sets a contact box-first into
   cavities 1, 3, 5… (the odd ones), about 1.4–2 mm deep, lance down. For J2,
   cavity 3 stays empty.
2. The housing goes into the press's floating nest. The web clamp and saddle
   comb bring the conductors over the barrels.
3. For each loaded cavity, the carriage steps it onto the die axis, the presser
   lays conductor n in, and the crimper crimps. Its neighbours are empty
   cavities.
4. **Second pass.** The person or loader sets contacts into the even cavities.
   Each is then crimped between two crimped neighbours.
5. **Push.** When all are crimped, the anvil drops 1.5 mm.
   - A **comb pusher** comes down behind the whole row: one slot per cavity
     straddling the wires, and teeth that follow up to ~2 mm into the cavities.
   - It pushes every contact at once until the first one bottoms, read by a
     bar cell.
   - A single finishing tine (i2's blade) then visits each cavity and pushes
     that contact to its own wall, logging its fold, snap and wall.
6. **Check.** A per-cavity pull-back: one pad pair stepped along the row.

## At a glance

| | |
|---|---|
| **What locates the contact** | The product's cavity walls (X, Z, roll), placed by hand or loader to the first stop; a slotted backstop comb on each tab stub (−Y); the steel dies at first touch |
| **What locates the conductor** | Saddle comb (X), web clamp and hump presser (Y), presser foot and hold-down pad (Z) |
| **Reference for "fixed"** | The C-frame's anvil block for the crimp; the web clamp along the wire |
| **What drives and carries the crimp** | i2's knee in a steel C; the housing and nest carry none |
| **How it knows** | i2's force against die gap, crimp height and proof pull per cavity; the push trace to the first wall; each contact's finishing trace; a camera frame of the rear face; the pull-back |
| **Steps it covers** | Place the conductor into the contact, crimp, crimp height, proof pull, insert (gang, then per-cavity finish), latch check |
| **What it hands back** | Pre-loading contacts to the first stop in two passes (odds, then evens); splitting, stripping and laying over the saddles (crossings by hand); loading and unloading the housing between passes |

## What it gains

- The per-cycle mechanism has no contact feed at all.
- Loading a housing by hand is a task anyone does now, made easier: each contact
  goes in only ~2 mm and does not latch.
- One push brings the whole row home. The conductors each still store ~5 mm of
  feed in their saddles, and all straighten together.

## Mechanism and the problems it meets

**Open wings side by side at 2.5 mm.** Clone insulation barrels open
2.46–3.25 mm [source S19–S22], wider than the pitch, so open neighbours clash.
Hence the two passes.
- **Loading the evens between crimped odds** leaves a gap of
  2.5 − s/2 − 1.0 mm to each crimped neighbour [calc w3 J]:

  | Contact | Gap |
  |---|---:|
  | pre-formed keyhole, 1.96–2.14 mm | +0.43 to +0.52 mm |
  | clone open, 2.46 mm | +0.27 mm |
  | clone open, 2.80 mm | +0.10 mm |
  | clone open, 3.00 mm | 0.00 mm |
  | clone open, 3.25 mm | −0.12 mm |

  So open clone contacts load in pass 2 only up to ~2.8 mm wings.
- **Crimping the evens.** The insulation step's outer face passes crimped
  insulation barrels ~2.0 mm wide, leaving a half-width of 1.50 mm
  [calc w3 A].
  - Clone spreads fail from 2.46 mm up with generous margins (−0.08 to
    −0.48 mm), and from ~2.7 mm up with tight ones.
  - Nothing can be pushed aside: the neighbours are bronze barrels in
    cavities. This differs from i2, where a seated neighbour's jacket can give
    way.
  - Pre-formed keyholes fit with +0.08 to +0.37 mm.
- **So i2b on open kit contacts works only if their wings are narrower than
  ~2.2–2.5 mm.** With wider wings, it runs on pre-formed contacts: the two-pass
  branch of [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md).
- **Alternate depths** (2 mm and 1.4 mm) stagger the insulation barrels 0.6 mm
  in Y. Insulation barrels are ~0.8–1.5 mm long [estimate, xh-facts §1], so
  they still overlap by 0.2–0.9 mm. The depth window (1.4–2.4 mm with
  t ≥ 0.8 mm) allows at most ~1.0 mm of stagger. The shallower contacts are
  held by 1.4 mm of wall.

**Room for the conductor step** [f&f on i2b].
- In pass 2, at the conductor crimper's Y, the neighbours are crimped conductor
  barrels (~1.5 mm wide, edge 1.75 mm from the axis). The 3.1 mm conductor
  step clears them by ~0.2 mm a side.
- In pass 1 the neighbours are empty: all the room there is.
- A single-pass preload does not crimp. Beside an open conductor-barrel
  neighbour, the conductor step's 1.55 mm half-width has 1.32–1.50 mm of room
  [ctq w2 §2].

**Anvil drop to step.** A 1.0 mm drop leaves 0.1 mm under the tallest clone
lance of a neighbour; 1.5 mm leaves 0.6–0.9 mm [f&f §11].

**X registration.** With every cavity loaded, the floating nest moves every
preloaded contact with the housing, and the die centres each one in turn.

**Gang force.**
- 9 × 3–25 N = 27–225 N on J1 [calc geometry §5]; at the KONNRA clone spec's
  ≤ 9.8 N per contact [source, via ribbon-as-pallet] it is ≤ 88 N.
- The comb stops at the first wall, because contact lengths differ: clone
  drawings run 5.8–6.73 mm, each ±0.25 [source S19–S22], and the spread within
  a lot is unknown. The finishing tine brings each contact home with its own
  trace, so a stalled contact does not hide in the sum [calc w3 E].

**Proof pull per cavity.** Each contact needs a backstop behind it during its
proof pull: a slotted comb (the comb pusher turned around), bearing on each tab
stub from below the wires.

**Comb pusher teeth.**
- Teeth that enter 2.0 mm cavities at 2.5 mm pitch with a slot for a 1.7 mm
  wire are tines ~0.25 mm wide [calc geometry §2].
- They are a laminated stack of laser-cut stainless stencil foil
  ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil)) [source], one layer per
  0.1–0.2 mm of tooth depth [assumption on foil thickness].
- They reach up to ~2 mm into the cavity, because a seated rear lies 0–1.8 mm
  inside the rear face [calc w3 H].

**J4 and J7.** The saddle comb carries the crossings as raised grooves, laid by
the person, or conductors come from a raised loft (i2's picker). The housing's
own order is fixed once the contacts are loaded, so the pin map is decided at
loading.

## Printed and bought parts

As [i2](i2-crimp-in-the-cavity.md), plus the comb pusher and backstop comb in
stacked stencil foil, and a housing-loading jig (printed) that holds an XHP
rear-face up with a depth stop for the first pass.

## Contribution

It separates three jobs:
- **placing**, a batch job with no aiming;
- **crimping**, a repeated simple cycle;
- **seating**, one push with a per-cavity finish.

The person's share becomes filling a housing to the first stop, perhaps the
easiest hand task in the procedure.

## Major unresolved problems

- It inherits i2's lance condition and die making in full.
- **The insulation mouth in pass 2** fails for most open clone wings, with no
  neighbour to push aside. Either the kit wings are narrow, or the contacts are
  pre-formed (k7).
- Two loading passes, and a housing out of the press between them.
- The comb pusher is fine metalwork.

## What rests on assumptions

- Clone contact dimensions [source S19–S22]; the kit contacts are unmeasured.
- Insulation barrel length 0.8–1.5 mm [estimate].
- Insertion force per contact 3–25 N, bracketed (KONNRA clone spec ≤ 9.8 N).
