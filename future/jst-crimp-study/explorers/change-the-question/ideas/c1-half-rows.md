# c1 — Half-rows: crimp at ribbon pitch, splay with the contacts on, fill the housing in two pushes

A process change: the order becomes strip, split, place, crimp, splay,
insert. Branches: [c1b](c1b-tack-first.md) (a light gang tack instead of the
crimp) and [c1c](c1c-crimp-in-the-row.md) (narrowed neighbours, crimp in the
row with no lift). into-the-housing's [k8](../../into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md)
gives the half-rows a different ending (sort into one row, push the housing
on). Sketch: [`../sketches/c1-half-rows.svg`](../sketches/c1-half-rows.svg)
(schematic). Numbers: [`../calc/ctq.out.txt`](../calc/ctq.out.txt) [ctq §n],
[`../calc/wave2.out.txt`](../calc/wave2.out.txt) [w2 §n],
[`../calc/on_into_the_housing_w3.out.txt`](../calc/on_into_the_housing_w3.out.txt) [w3 §n],
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) [w3b §n]; J4 and J7 orders in
[`../calc/order_search.out.txt`](../calc/order_search.out.txt).

## Picture it

**Where things start.**
- The ribbon end is cut flush and lies flat in a **web clamp**: one ribbon, or
  a pair laid edge to edge; its first conductor's edge against a side fence;
  its tip against a tip stop. The clamp is the ribbon's reference.
- **One X slide** carries, as one body, the web clamp, two **row pallets** on
  small swing arms, and the **housing nest** in front. Its rail runs behind the
  clamp, under the ribbon's tail, and the body reaches forward from it. The
  slide steps the work; it never carries crimp force.
- **A fixed press** stands at one X position. It is a steel C whose **spine
  stands in front of the housing nest's path**, with arms reaching back
  20–26 mm over and under the working carrier. The upper arm carries a fixed
  **punch** (one nest, any width); the lower arm carries a rising **ram**; the
  hard stop that sets crimp height sits in the die block beside the anvil. The
  slide carries the work through the C's throat in X, so the ribbon's tail and
  the parked pallets stay behind and outside it. A 12 mm-thick arm 15–25 mm
  wide deflects 11–41 µm at 3 kN, and with the stop beside the anvil that is
  travel, not crimp height [htq §7].
- A **push station** at another X position, clear of the C, carries a cam
  plate and a pusher for each pallet.
- **Pallets.** Each is a short track of narrow carriers at **3.4 mm pitch**,
  twice the ribbon's 1.7 mm, so every other conductor. Pallet A holds the
  contacts for the odd cavities (1, 3, 5 …), pallet B those for the even ones.
- **Carriers.** Each takes one open contact by its box, barrels up:
  - a box slot 2.0 mm wide with a **lance groove ~1.1 mm deep running out
    through the open front**; the lance stands 0.6–0.9 mm proud of the floor,
    its tip ~2.4–2.6 mm behind the box front [xh-facts §1];
  - a light spring pushing the carrier forward in its track, and a **rear hard
    stop** at the track's end, so a rearward pull on the wire lands on the
    track, not on the spring;
  - a window under the barrels for the anvil blade, and a slot for the ram's
    steel pilot.
- **Contacts into the pockets.** Dropped in by the person like loading a
  magazine, or by a loader (from strip: terminal-supply's pallet loader; from
  loom-order sticks: [c6](c6-pre-form-the-contact.md)). Loading at 5.0 mm, with
  the pallet parked on its cam plate open, leaves 1.75–2.2 mm between clone
  wing tips instead of 0.15–0.6 mm at 3.4 mm [ctq §3]. The ELP camera confirms
  every pocket full and the right way up, and J2's pocket 3 empty.
- The housing sits in its nest **windows down** if the lance goes toward the
  window face [assumption, xh-facts §3; one kit housing and contact settles
  it].

**What moves, in order.**
1. **Strip, flat.** All conductors are stripped while the web still holds them
   in a line (2.4 mm per JST [mfr S6]; 1.6–2.1 mm per the KONNRA clone spec).
   The stripper is someone else's station. The tip stop sets the strip line.
2. **Split into two planes.** Interlaced toothed jaws close over the last
   12–20 mm [prior-art §1, US 4,179,964]. Odd conductors are cradled upward and
   even ones downward, and the web between them shears. A conductor the loom
   trims is cut back here: J2's conductor 3, J7's spare.
3. **Park the other half-row.** A sweep finger folds plane B down and back
   under the clamp nose, clear of the working zone.
4. **Place a whole half-row at once.** Pallet A swings up under plane A
   against a datum on the clamp frame. In their own plane the conductors are
   already at 3.4 mm, held there by the web root. A printed **presser comb**
   comes down, teeth between the conductors at the insulation, and lays every
   conductor into its contact: strands into the conductor barrel, insulation
   into the insulation barrel. The camera looks straight down: strands in every
   U, none over a wing tip, the insulation edge in the window. A miss means
   lifting the comb and re-laying; nothing has been crimped.
5. **Crimp one at a time, lifted out of the row.** The slide steps carrier *k*
   to the press.
   - A hardened steel pilot on the ram enters the carrier's slot first, so the
     carrier rises on steel, not in its printed track: steel is the master in
     X.
   - The ram's head is an **anvil blade** ≤1.90 mm wide (it passes the 2.0 mm
     pocket), its front edge behind the lance tip, with two rigid shoulders. The
     blade rises through the carrier's window; its top stands 0.1–0.2 mm above
     the pocket floor, so the contact's floor rests on steel alone and the box
     overhangs, as on an applicator's anvil.
   - The shoulders lift carrier, contact and conductor 3.2–4.2 mm above the
     neighbours [ctq §4], past their open wing tips (2.4–3.45 mm tall), to the
     fixed punch. The punch clears the neighbours because they are lower, not
     because it is narrow. The row is crimped from one end, so every lift after
     the first has an open neighbour on one side only.
   - At the top, a **front stop** in the die block has advanced to its seat;
     the carrier's spring presses the box's mating face against it. The stop
     holds until the punch has captured the contact (first force rise), then
     backs off ~0.3 mm, so the conductor barrel's forward growth under coining
     (0.03–0.11 mm) meets nothing [w3 §3]. It is retracted while the slide
     steps, so no box ever meets it sideways.
   - The ram closes to the hard stop, drops, and the slide steps 3.4 mm.
6. **Park row A, do row B.** Pallet A, carrying its crimped row, swings down
   and back under the clamp nose. Plane B swings up into the working plane,
   pallet B comes under it, and steps 4–5 repeat. Both rows are crimped before
   either goes into the housing. As pallet B parks after its row, it draws
   back 7 mm, and its conductors bow downward over the split, 4.6–8.6 mm deep
   [w3 §7]. That bow is the length row B will need for its push; a conductor
   buckles at 0.2–4 N over a 6–26 mm split, so drawing it costs almost nothing
   [w3b §5]. The park fold decides that the bow goes down.
7. **Spread both rows at the push station.** The slide moves the pallets to
   the push station. Each pallet settles onto that station's slotted cam plate,
   fins under the carriers entering its slots; the plate slides, and each
   carrier moves out in proportion to its index, from 3.4 to **5.0 mm**, twice
   the housing pitch. The crimped contacts carry their conductors; nothing grips
   a bare strand. The largest move is J1's outer contact, 3.2 mm over a
   12–18 mm S-bend [ctq §2b]. Because the cam plate lives at the push station,
   nothing but the anvil ever sits under a carrier at the press.
8. **Fill the housing: row A by moving the housing, row B by pushing.**
   - Pallet A swings up to the cavity line, cavity 1 over pocket 1. The housing
     nest slides 7 mm back onto row A; each contact enters its odd cavity
     without moving relative to the web root, so row A stores nothing. A load
     cell on the nest reads the sum. Pallet A drops away; its pockets are open
     at the top, so the wires lift out.
   - The housing shifts 2.5 mm in X. Pallet B comes up between row A's wires
     (1.9 mm gaps for 1.7 mm wires at 5.0 mm pitch) and a pusher comb behind
     the insulation barrels drives row B 7 mm into cavities 2, 4 …, the bow
     straightening as it goes.
   - Pallet B's carriers must meet row A's wires only where those are straight,
     behind the S-bend in which each row converges from 5.0 to 3.4 mm toward
     the web root. That needs a split of ~6–12 mm for rows of two and
     ~15–26 mm for J1's row of five [w2 §6]; box-only carriers (3 mm long) and a
     30° S-bend keep it at the short end.
9. **Test on a real wafer.** The finished housing is pushed onto a board-type
   male XH header wired to a microcontroller: order, opens, adjacent shorts,
   and J2's cavity 3 reads open.

**What locates what.**

| What | Located by | Needed | Reference for fixed |
|---|---|---|---|
| Contact to punch, axial (bellmouth) | box mating face against the front stop until capture; the contact's own box-to-barrel distance | ±0.1 mm [xh-facts §5] | the die block: ±0.05–0.10 mm RSS, steel plus the part [terminal-supply exchange calc §5]; a camera re-teach per lot removes a lot offset |
| Carrier in X at the press | the ram's steel pilot | the lift passes open neighbours with 0.15 mm (worst clone) to 0.60 mm (nominal) between tips | the ram |
| Contact's plane at the crimp | anvil top 0.1–0.2 mm above the pocket floor | the box must not be held above the anvil, or the barrels bend down at the box [MKS-L manual, via terminal-supply] | the anvil |
| Crimp height | hard stop in the die block | ±0.02–0.05 mm [xh-facts §4] | the C |
| Strip line to the barrels | tip stop → clamp frame → pallet datum → front stop | ±0.3 mm keeps the insulation edge in the window [estimate] | the clamp |
| Conductor over its barrel | web root plus presser-comb slot | ±0.5 mm (open barrel 1.8–1.9 mm, strands ~0.72 mm) | the clamp |
| Pocket at 5.0 mm to cavity | cam plate slots, then the housing nest on the same slide | ±0.15 mm at the cavity mouth [estimate] | the slide |

**What drives and carries the crimp force.**
- The ram is the NEMA 23 and DM542T already on the bench, through an SFU1204
  ball screw (Prime-confirmed, $35.99 for 200 mm, end supports not included
  [sourcing/amazon-prime.md]) standing in the C's lower arm, or a sibling's
  drive (a knee, an eccentric).
- ~3 kN at the bottom [xh-facts §4]. The force path is a closed steel C:
  upper arm → punch → contact → anvil blade → ram → screw → lower arm. The
  slide, pallets and printed carriers never carry it.
- The proof pull (below) puts 40–100 N rearward on a row of 2–5 carriers
  [htq §6]. The carriers' rear hard stops take it into the pallet, and a latch
  pin from the slide into the pallet at its working position takes it into the
  slide, not the swing-arm pivot (0.8–4 N·m there [htq §6]).

**How it knows each step worked.**

| Step | Check |
|---|---|
| Loading | camera: every pocket full, right way up, empty where the loom says |
| Placement | camera, before any force |
| Crimp | force against ram position on every stroke, from a load cell under the anvil and the step count to the hard stop. A missing contact, missing strands or insulation in the barrel shows as a wrong curve; one strand in 60 does not [prior-art §6] |
| Crimp, look | camera after crimping: brush, bellmouth, window |
| Hold | optional proof pull: the web clamp backs off with each box held by its pocket's rear shoulder, ~20 N per contact, half of JST's 39.2 N minimum [mfr S6]; the lance groove runs out the front, so the lance carries none of it |
| Insertion | the nest's and the pusher's force traces |
| The whole end | the wafer test |

**What the person does.** Loads the pallets unless a loader does; lays the
ribbon in the clamp and, for J4 and J7, routes the crossing conductors by hand
(below); drops an empty housing in the nest and takes the finished end out.
Roughly a minute of hands-on time per ribbon end [estimate]; the machine takes
several minutes.

**Steps covered:** strip (receives it flat), split, place (a whole half-row in
one motion), crimp (lifted, one at a time), splay (after the crimp, on a cam
plate), insert (two moves), verify. **Hands back:** loading contacts unless a
loader does; the J4 and J7 crossings; housings in and ends out.

## Why the reorder helps where Derek wants help

- **Placing is one motion for up to five contacts.** The conductors are
  located by the web root and a comb at a generous 3.4 mm pitch whose teeth
  are 1.7 mm wide. No fan in front of floppy stripped tips.
- **Nothing open is positioned at 2.5 mm pitch outside the housing.** Open kit
  contacts do not fit side by side at 2.5 mm [ctq §3]:

  | Contact | Open-wing gap at 2.5 mm | at 3.4 mm |
  |---|---|---|
  | Clone, nominal (2.8 mm wings) | −0.30 mm | 0.60 mm |
  | Clone, worst case (3.25 mm) | −0.75 mm | 0.15 mm |
  | JST catalog envelope (1.95 mm), if genuine wings fit inside it | 0.55 mm | 1.45 mm |

- **The splay is done with a rigid handle on every conductor.**
- **The housing is filled by two half-rows that never meet outside it.**

## Loom by loom [ctq §2]

- **The T4 looms** (4P into XHP-4: J3, J5, J9, J11, J13): half-rows of two
  and two, a 0.8 mm spread. The easy case, and half of all housings.
- **J6** (5P into XHP-5): three and two.
- **J1** (5P + 4P into XHP-9): five and four, the largest spread, 3.2 mm. Laid
  edge to edge, the pair is one nine-conductor row.
- **J2** (3P + 3P into XHP-6, cavity 3 empty): row A is conductors 1 and 5,
  with conductor 3 trimmed at step 2 and its pocket left empty, so after the
  spread the empty pocket faces cavity 3; row B is 2, 4 and 6. The guard
  cavity is empty by construction.
- **J7** (5P + 3P into XHP-7, one trimmed). Laid RB1–RB4, GND | X, CLO, CHI
  (X the trimmed conductor), every conductor is on its own parity plane and one
  crossing remains in row A: GND lands in cavity 7 and CLO in cavity 5 [w3 §9].
  The presser comb has one tine that can be held back: stroke 1 lays and snaps
  everything but GND, stroke 2 lays GND over CLO (into-the-housing's "a
  crossing is an order of placement").
- **J4** (4P + 3P into XHP-7) is the awkward one. Its pin order interleaves the
  two ribbons (GND from the 3P lands in cavity 2). The least-crossing layout
  (V5, IO25, 3V3, IO26 | GND, IO27, IO23, or 3V3, IO26, V5, IO25 | …) still
  sends two conductors to the opposite plane and has two crossings [w3 §9]. It
  needs a J4-specific split jaw or a hand step at the split.
- [c7](c7-straight-across.md) removes both crossings by changing the board's
  pin order (J4: swap pins 2 and 5; J7: GND to pin 5), which is Derek's choice.

## Printed and bought

**Printed** (PETG or PET-CF): clamp jaws, side fence, tip stop; pallet tracks,
swing arms; presser comb, sweep finger, pusher comb, housing nest; the split
jaws' cradles; the push station's cam plates. The split jaws' shearing faces
are steel [prior-art §1].

**Carriers.** ~3.0–3.1 mm wide with a 2.0 mm box pocket, so ~0.5 mm walls:
printed with the H2C's 0.2 mm hotend [repo tools.md, via into-the-housing], or
laminated from laser-cut stencil steel either side of a printed core (JLCPCB
stainless stencils from $3, ~24 h [into-the-housing source]).

**Bought:**

| Part | Source |
|---|---|
| NEMA 23 + DM542T | on the bench [repo tools.md] |
| SFU1204 ball screw, 200 mm | Prime-confirmed, $35.99 |
| MGN12 rail with MGN12H carriage, 300 mm (slide) | Prime-confirmed, $20.49, 615 ratings |
| Anvil blade: 3 × 3 mm HSS blank ground to ≤1.90 mm wide | Prime-confirmed, five × 200 mm for $9.99 |
| Front-stop actuator: 12 V push-pull solenoid, 10 mm stroke, 5 N | Prime-confirmed, Heschen HS-0530B, $7.99, 383 ratings (5 N against a 0.1–0.5 N carrier spring) |
| Load cell + HX711 | context sourcing list |
| Punch: an XH nest cut from a spare SN jaw, or an OTP XH knife set | hand-tool-as-press a4; terminal-supply a2. The iCrimp IWS-0723K set is the only Prime route to a loose 2549 die found ($46.59, 9 ratings) |
| Test wafer: B4B/B5B/B6B/B7B/B9B-XH-A | B4B-XH-A Newark 171,802 in stock; B9B-XH-A Digi-Key 44,226 [into-the-housing source] |

All Amazon rows: [sourcing/amazon-prime.md], observed 2026-09-28.

## Problems worked through

1. **"Crimp the odds, then the evens in the gaps: the evens' tooling is back at
   2.5 mm"** (the objection in into-the-housing
   [i3](../../into-the-housing/ideas/i3-converging-shuttles-gang-push.md)).
   Each row is crimped in its own plane, in its own pallet, with only its own
   3.4 mm neighbours; the rows meet only inside the housing.
2. **A stepping ram under a fixed punch does not meet.** The press is fixed,
   ram and punch in one C with the stop inside, and the clamp and pallets step
   under it together, which keeps every conductor-to-contact relation
   (terminal-supply's repair; the same object as its a2 station and
   force-and-form's f2/f2b frame).
3. **Row A's wires lie across row B's working zone** if row A is inserted
   first. So both rows are crimped before either is inserted. Flipping the
   clamp between rows does not help: the housing sits on the flip axis at the
   tip plane, so the flip only mirrors row A's wires in the working plane.
4. **Two sequential pushes need stored length.** With web clamp and housing
   still, each pushed conductor would have to find 7 mm (into-the-housing's
   feed-length rule) [w3 §7]. Moving the housing onto row A stores nothing for
   row A; row B takes its 7 mm as the bow formed when pallet B parks (step 6).
   What stays uncertain is whether the bow stays below row A's wires when
   pallet B rises between them. The ending that stores nothing at all is to
   sort both crimped rows into one 2.5 mm row and push the housing onto it
   (into-the-housing [k8](../../into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md)).
5. **The punch cannot fit beside open neighbours at 3.4 mm.** A conductor punch
   with ~1 mm legs is ~1.75–1.9 mm half-width [estimate]; the room beside an
   open clone neighbour is 1.67–1.90 mm [ctq §3]. The lift (step 5) is the
   answer here: any punch fits. What it leaves is the lifted contact's wing
   tips sliding past its neighbours' with 0.15 mm between them at worst-case
   clone wings. The steel pilot, crimping from one end and loading at 5.0 mm
   reduce the risk; they do not make ±0.07 mm easy. [c1c](c1c-crimp-in-the-row.md)
   narrows the neighbours and removes the lift.
6. **The ram comes from below, through the parked plane-B conductors.** Plane B
   is folded down and back under the clamp nose, not merely lowered, so its
   tips point away from the pallet zone. It is a ~90° fold in silicone ~15 mm
   from the web root, which must not tear the web further back. Untested
   (repo Open item 5).
7. **Spreading drags conductors across each other.** Within a half-row the
   order is preserved except J7's and J4's crossings; the spread moves each
   conductor away from its neighbours.
8. **A C standing behind the clamp puts its spine where the tail goes and its
   lower arm where pallet A parks.** The spine stands in front of the housing
   nest's path instead, arms reaching back; the tail and the parked pallets
   are behind, outside the C.
9. **A cam plate under the pallet and an anvil rising through the carrier want
   the same space.** The cam plate belongs to the push station, at another X;
   at the press, only the anvil is under a carrier.
10. **Carriers sprung against a fixed stop meet it sideways when the slide
    steps, and a fixed stop at the box nose blocks the barrel's growth.** The
    stop retracts for the step and backs off after capture (step 5).
11. **Two pallets, swing arms and a moving housing is a lot of axes:** the
    slide, the ram, two swing arms, two cam plates, the housing's Y and X
    moves, one pusher and the front stop. One pallet used twice is
    incompatible with crimping both rows first.
12. **Why not spread before crimping and crimp at 5.0 mm**, as force-and-form
    and ribbon-as-pallet do? That removes the lift (5.0 mm leaves 3.27–3.93 mm
    beside an open neighbour), at the price of a fan applied to floppy,
    stripped tips before they have handles. force-and-form's
    [f5b](../../force-and-form/ideas/f5b-half-row-cassette.md) develops it. The
    two differ in where the fan sits relative to the crimp.

## Contribution

- A way to place several contacts in one motion without ever holding open
  contacts at 2.5 mm pitch; only the ribbon's own geometry and a coarse comb
  are involved.
- It turns "splay" from positioning floppy wires into moving rigid parts
  sideways.
- Lift-to-crimp: a fixed punch of any width works in a 3.4 mm row, because the
  target rises past its neighbours.

## Major unresolved problems

- **The lift beside worst-case clone wings:** 0.15 mm between tips. c1c
  removes it.
- **The J4 and J7 crossings.** No layout of those two looms is free of them;
  J4 needs a per-loom split jaw or a person's hands at the split. c7 removes
  them by a board change.
- **Silicone web behaviour** under interlaced jaws and a 90° park fold is
  untested (repo Open item 5).
- **Split length:** 12–20 mm for the split jaws, 6–26 mm for row B's push
  (T4 at the short end, J1 at the long) [w2 §6]. Whether Derek accepts that at
  the housing end is unasked.
- **Row B's stored bow** staying below row A's wires, and pallets on swing arms
  carrying crimped rows: plausible on paper, unproven.
- **The carriers' ~0.5 mm walls** holding a box square while sprung against a
  stop, and taking 20 N on the rear shoulder at every proof pull (16 MPa on
  1.27 mm² [htq §6]).
- **Insertion force and the latch click** are unknown [xh-facts Unresolved 4].

## What rests on assumptions

- Contact wing widths: clone drawings [source S19–S22] and JST's envelope
  [mfr S1]; the kit contacts are unmeasured.
- That two ribbons laid edge to edge give a continuous 1.7 mm pitch across the
  join [assumption, from BNTECHGO's 1.7 × N section].
- The 3–25 N insertion force used for the pusher: a sibling's estimate.
- Crimp force and height: the context estimates [xh-facts §4].
- Which housing face the lance goes toward [assumption].
- The growth and bow numbers [estimate, w3 §3, §7].

## Connections

- The stripper feeding step 1 can be any explorer's; flat, before the split,
  is the order this arrangement wants (procedure-is-the-machine's
  [p7](../../procedure-is-the-machine/ideas/p7-strip-before-split.md)).
- The fixed press can be force-and-form's f3 knee, hand-tool-as-press's a4 die
  set, or terminal-supply's a2 knife set in an arbor press.
- Neighbours built from it: force-and-form
  [f5b](../../force-and-form/ideas/f5b-half-row-cassette.md) and
  [f2c](../../force-and-form/ideas/f2c-applicator-station-makes-t4-ends.md);
  into-the-housing [k8](../../into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md).
