# c1c — Half-rows crimped where they lie: narrowed neighbours, a fixed press, both rows crimped before either is inserted

**A combination** of:
- change-the-question [c1](c1-half-rows.md): split the ribbon end into two
  planes, lay a whole half-row into a pallet at 3.4 mm in one motion, fill the
  housing from the two crimped rows, test on a real wafer;
- change-the-question [c6](c6-pre-form-the-contact.md) (pre-formed contacts
  the conductor snaps into) **or** [c1b](c1b-tack-first.md) (a light tack that
  closes the insulation barrels on the wire). Either narrows every open contact
  to ~2.0–2.2 mm;
- terminal-supply's reading of c1
  ([`../../../exchange/terminal-supply--on--change-the-question.md`](../../../exchange/terminal-supply--on--change-the-question.md)):
  a fixed press with the work stepping under it, both rows crimped before
  either is inserted, the box's own face as the axial stop, the lance groove,
  the anvil-defined plane, and a strip-fed pallet loader (its C1);
- a press from another explorer: force-and-form [f3](../../force-and-form/ideas/f3-knee-micropress.md)'s
  knee with one nest; hand-tool-as-press [a4d](../../hand-tool-as-press/ideas/a4d-tongue-under-a-windowed-pallet.md),
  one SN-2549 nest cut to a tongue on an eccentric; or terminal-supply
  [a2](../../terminal-supply/ideas/a2-strip-indexer.md)'s OTP knife set in an
  arbor press;
- into-the-housing's rules for any press that holds a contact by its box (the
  lance condition, growth-safe stops, steel as master in X), and its sort
  ending, which it develops with this idea as
  [k8](../../into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md).

Sketch: [`../sketches/c1c-crimp-in-the-row.svg`](../sketches/c1c-crimp-in-the-row.svg)
(schematic). Numbers: [`../calc/wave2.out.txt`](../calc/wave2.out.txt) [w2 §n],
[`../calc/ctq.out.txt`](../calc/ctq.out.txt) [ctq §n],
[`../calc/on_into_the_housing_w3.out.txt`](../calc/on_into_the_housing_w3.out.txt) [w3 §n],
[`../calc/wave3.out.txt`](../calc/wave3.out.txt) [w3b §n], and
hand-tool-as-press's [`exchange_ctq_w3.out.txt`](../../hand-tool-as-press/calc/exchange_ctq_w3.out.txt) [htq §n].

## Picture it

**The machine.** A baseplate with two things on it.
- **One X slide** on an MGN12 rail (Prime-confirmed, $20.49 for 300 mm with an
  MGN12H carriage [sourcing/amazon-prime.md]) and a NEMA 17 lead screw. The
  rail runs behind the clamp; the slide's body reaches forward from it and
  carries, as one body:
  - the **web clamp** with its side fence and tip stop, the ribbon's
    reference;
  - **pallet A** and **pallet B**, each a row of carriers at 3.4 mm, each on a
    small swing arm that can park it down and back under the clamp nose;
  - the **housing nest** in front, which can shift 2.5 mm in X and 7 mm in Y.

  Stepping the slide 3.4 mm brings the next carrier to the press without
  changing any contact's relation to its conductor, because clamp and pallets
  move together.
- **A fixed steel C at one X position.** Its **spine stands in front of the
  housing nest's path**; its arms reach back 20–26 mm over and under the
  working carrier, so the ribbon's tail and the parked pallets lie behind it,
  outside. A 12 mm-thick arm 15–25 mm wide deflects 11–41 µm at 3 kN; the hard
  stop sits in the die block beside the anvil, so that deflection is travel,
  not crimp height [htq §7].
  - **Upper arm: one punch, one nest.** An ordinary single-nest XH punch
    (half-width 1.75–2.0 mm [estimate]), or one SN-2549 nest cut to a tongue
    **≤4.45 mm wide**, kept that narrow up to 2.1–2.3 mm above the anvil beside
    keyhole neighbours, or 2.6–3.3 mm beside the taller pre-forms [htq §5]. A
    punch "narrowed to 6–8 mm" is 1.5–3.5 mm too wide here.
  - **Lower arm: an anvil blade ≤1.90 mm wide**, so it passes the carrier's
    2.0 mm pocket (a 3 × 3 mm HSS blank must lose ≥1.1 mm of width
    [htq §5]). Its front edge stands behind the lance tip, so the box and lance
    overhang it. It is fixed in its block; the pallet's swing arm lifts the
    pallet 1–2 mm to step past it and settles it back with each pocket floor
    0.1–0.2 mm under the anvil top, so the anvil alone sets the contact's plane
    (a4d's arrangement). A ram-carried anvil rising through the window, as in
    c1, also works.
  - **A retracting front stop** in the die block, on a 12 V push-pull solenoid
    (Heschen HS-0530B, 10 mm stroke, 5 N, Prime-confirmed, $7.99, 383 ratings
    [sourcing/amazon-prime.md]). It advances to a hard seat before a crimp,
    holds the box until the punch has captured the contact, then backs off
    ~0.3 mm; it is retracted whenever the slide steps.
  - **Electrodes.** The anvil block and the punch are insulated and wired. The
    ribbon's far end sits in a far-end block (Wago 221-415s, Prime-confirmed,
    $28 for 25, 6,963 ratings), or is the rest of the spool on
    [c5](c5-ends-as-stock.md)'s slip ring (6-circuit, Prime-confirmed, $9.99).
- **A second station at another X**, clear of the C, where the crimped rows
  go into the housing (two endings, below).

**A carrier.** One per contact, ~3.0 mm wide:
- a box slot 2.0 mm wide with a **lance groove running out through the open
  front**, so no pull or push ever bears on the lance;
- a pocket floor 0.1–0.2 mm **below** the anvil's top;
- a light spring (0.1–0.5 N) pushing it forward in its track against the front
  stop, and a **rear hard stop** at the track's end;
- a window under the barrels, and an open top.

The pallet **floats in X** on a small flexure (±0.2 mm). The slide's step only
has to bring each contact inside the punch's flare; the flare and the anvil
then centre it. Steel is the master in X, not the printed pocket (±0.1 mm)
against the screw (±0.02 mm).

**Loading the pallets.** At a load position beside the press:
- **Pre-formed contacts** come in loom-order sticks. An escapement finger
  singles the lead contact out of the stick onto a short channel and a pusher
  moves it into the pocket; the slide steps 3.4 mm; the next goes in. The stick
  never feeds a pocket directly, because nose to tail the next box sits against
  the lead contact's barrel. J2's blank spacer leaves pocket 3 empty, so the
  loaded pallet is the build list.
- **Or strip** (terminal-supply C1): pins in the pilot holes, a blade shears the
  tab 0.2–0.3 mm behind the contact, a pusher drives the freed contact down a
  contact-shaped window into the pocket.
- **Or kit contacts, open**, when the narrowing is c1b's tack.

**One ribbon end.**
1. **Clamp, strip flat, split** (c1 steps 1–3): all conductors stripped while
   webbed; interlaced jaws put odd conductors in plane A and even in plane B;
   plane B folded down and back. J2's conductor 3 and J7's spare are trimmed
   at the split.
2. **Lay and fix row A.** Pallet A swings up under plane A. A presser comb
   comes down, a rear tine on each jacket over its insulation barrel and a
   front tine on each strand bundle.
   - With **pre-formed contacts**: every jacket snaps in (~0.3–30 N each, a few
     newtons central [w2 §4]) and every strand bundle goes into its U.
   - With **open contacts**: the comb lays them; then a steel tack comb closes
     the insulation barrels in two passes at 6.8 mm, 66–660 N per row [ctq §5].
   - One tine can be held back, so a crossing is laid in a second stroke (J7).
   - The camera looks down at every U before any crimp force exists.
3. **Crimp row A where it lies, from one end.** The slide steps carrier 1 to the
   press; the pallet settles; the conductor now resting on the anvil answers
   through the far end, and must be the one the pin map puts there. The stop
   advances, the punch closes to the hard stop, the stop backs off at capture.
   The slide steps 3.4 mm to the next. Beside a keyhole neighbour the
   insulation punch has 0.23–0.42 mm and the conductor punch 0.33–0.65 mm to
   spare [w2 §2].
4. **Park row A, do row B.** Pallet A, now a row of crimped contacts on their
   carriers, swings down and back under the clamp nose. Plane B swings up,
   pallet B comes under it, and steps 2–3 repeat.
5. **Proof pull, row by row.** The web clamp backs off ~20 N per contact with
   each box on its pocket's rear shoulder; the carriers' rear hard stops take
   the row's 40–100 N into the pallet, and a latch pin from the slide into the
   pallet takes it into the slide, not the swing-arm pivot [htq §6].
6. **Into the housing, one of two endings, at the second station.**
   - **Ending A, two moves (c1's).** Each pallet settles on the station's cam
     plate and spreads from 3.4 to 5.0 mm. The housing nest moves 7 mm back onto
     row A (row A stores nothing); pallet A drops away. The housing shifts
     2.5 mm; pallet B, whose conductors took a 4.6–8.6 mm downward bow when it
     parked [w3 §7; w3b §5], rises between row A's wires (1.9 mm gaps) and
     pushes row B 7 mm into the even cavities, straightening the bow. The split
     must hold the S-bend plus a carrier: ~6–12 mm for T4's rows of two,
     ~15–26 mm for J1's row of five [w2 §6].
   - **Ending B, sort into one row** (into-the-housing
     [k8](../../into-the-housing/ideas/k8-half-rows-crimped-then-sorted.md), from
     its [i6](../../into-the-housing/ideas/i6-sort-then-push.md)). A pad pair
     takes each crimped contact from its open-topped pocket, the upper pad on
     the crimp's lobes and the lower pad up through the anvil window, and sets
     it into a 2.5 mm target comb in housing order: pallet B first, then A,
     upper-layer conductors last. A backing blade on constant-force tines
     squares the row and the housing is pushed onto it. No cam plate, no stored
     length, and J4's and J7's crossings become an order of placement.
7. **Test** on a board-type male XH header read by a microcontroller: order,
   opens, adjacent shorts, J2's empty cavity.

**What locates what.**

| Pair | Located by | Reference for fixed |
|---|---|---|
| Conductor to its contact, axially | tip stop → clamp → pallet; then the snap (or tack) holds it | the web clamp |
| Contact to punch, axially | box face on the front stop until capture | the die block |
| Contact to punch, in X | punch flare and anvil, the pallet floating | the C |
| Contact's plane | anvil top 0.1–0.2 mm above the pocket floor | the anvil |
| Crimp height | hard stop beside the anvil | the C |
| Contact to cavity | cam plate then housing nest (A), or target comb (B) | the slide (A), the second station (B) |

**What drives and carries the crimp force.** Only the press. One of:
- force-and-form's knee: 60–160 N at the knee for 0.8–2.6 kN at the dies
  [digest];
- a4d's 2–2.5 mm eccentric on the bench NEMA 23 through a 10:1 planetary, or
  the self-locking 12 V worm gearmotor (Prime-confirmed, $26.99), with a
  disc-spring stack capping the peak and a 500 kg button cell under the anvil
  (Prime-confirmed, $74.99, no ratings);
- an OTP knife set in an arbor press (terminal-supply a2).

The loop is the C. The slide, pallets and printed carriers never see crimp
force; the proof pull's 40–100 N goes into the slide through the latch pin.

**How it knows.**
- **Before force:** the camera at the lay (strands in the U, none over a wing
  tip, insulation edge in the window) and at the load position (every pocket
  full, J2's pocket 3 empty); the anvil electrode names the conductor on each
  carrier before its crimp, which catches a mis-laid J7 GND.
- **During:** force against ram position on every stroke.
- **After:** crimp height by a ~10 N re-touch read on a 0.001 mm indicator
  across ram holder and anvil block (Clockwise DITR-0105, RS232, Prime-confirmed
  $52.99; its DTCR-01 cable is not on Prime); the proof pull; the insertion
  trace; the wafer test.

**What the person does.** Keeps sticks (or strip) and housings in their
feeds; lays each ribbon end in the clamp; for J4 and J7, either makes the
crossings at the lay (ending A) or nothing (ending B, or [c7](c7-straight-across.md)'s
pin map); takes each finished end off the wafer. One call per ribbon end, 14
per unit, a few minutes of machine time each; one call per run when fed from
c5's spool.

**Steps covered:** strip (received flat), split, supply into pockets (sticks
or strip), place (snap or lay-and-tack, a whole half-row), crimp (in the row,
no lift), splay (cam spread or sort), insert, verify. **Hands back:** laying
each ribbon end; the J4/J7 crossings in ending A; the feeds; the stripper.

## Two ways to narrow the neighbours, side by side

| | Pre-formed (c6) | Tacked (c1b) |
|---|---|---|
| Where the insulation barrel is formed | in bulk before any wire: a keyhole, a tall keyhole, or the crimper's own stroke stopped early | on the wire, in the machine, one half-row per stroke |
| Force over the ribbon | a few newtons per conductor (the snap) | 66–660 N per half-row, over a steel anvil strip |
| Extra tooling in the machine | a presser comb | a tack comb (two passes at 3.4 mm with clone wings) and its drive |
| Extra tooling outside | the pre-former (or none, if the crimp tool makes the pre-form) | none |
| Punch height beside the neighbour | narrow to 2.1–2.3 mm (keyhole) or 2.6–3.3 mm (tall shapes) above the anvil | ~2.0–2.3 mm [estimate] |
| What the final crimp does | keyhole: pinches the sides to an O with a narrowed gap; tall shapes: a B [c6] | a single-stroke die passes through a loose tack anyway [c1b] |

Either runs in this machine; the pallet, press and slide are the same.

## J4 and J7

- **Ending A:** the crossings are made at the lay. J7 laid RB1–RB4, GND | X,
  CLO, CHI has one crossing in row A (GND over CLO), made by the held-back tine.
  J4 needs two conductors sent to the opposite plane (a J4 jaw insert) and a
  crossing in each row [w3 §9].
- **Ending B:** the crossings are an order of placement in the sort; with J4
  laid V5, IO25, 3V3, IO26 | GND, IO27, IO23 and J7 as above, every
  upper-layer conductor sits in pallet A, so "B first, then A, upper layer
  last" satisfies i6's rule.
- **[c7](c7-straight-across.md):** a board pin order with no crossings at all.

## Problems worked through

1. **The anvil and a cam plate under the pallet want the same place.** Ending
   A spreads at the second station, so at the press only the anvil is under a
   carrier; ending B has no cam plate.
2. **Carriers sprung against a fixed stop meet it sideways when the slide
   steps, and nothing holds them against a rearward proof pull.** The stop
   retracts for every step; the carriers have rear hard stops and the pallet a
   latch pin into the slide.
3. **A C standing behind the clamp puts its spine in the tail's path and its
   lower arm where pallet A parks.** The spine stands in front of the housing
   nest's path, arms reaching back.
4. **A rigid stop at the box nose blocks the conductor barrel's growth**
   (0.03–0.11 mm, pushed with up to 80–520 N; the transition would bow
   0.07–0.19 mm [w3 §3]). The stop holds only until capture.
5. **The lance and the anvil.** The anvil's front edge stands behind the lance
   tip; the lance groove clears the lance in the carrier, the blade's position
   clears it at the press.
6. **Two locators in X.** The printed pocket (±0.1 mm) and the screw step
   (±0.02 mm) would fight; the pallet floats and the steel centres.
7. **The feed-length rule.** Two sequential row pushes with web and housing
   still would need 7 mm stored per pushed conductor [w3 §7]. Ending A moves
   the housing onto row A and bows row B at its park; ending B stores nothing.
8. **An SN nest cut to a tongue loses the SN's lower cradle.** Over a flat
   ≤1.90 mm HSS anvil, the crimp's underside differs from the hand tool's
   [assumption: the SN's lower XH die shape is unrecorded], so hand crimps are
   references for the upper profile only. The tongue itself is a hardened jaw
   cut to ≤4.45 mm without cracking [hand-tool-as-press a4b's problem].

## Contribution

- Derek's priority step, whole: place a half-row of contacts on their
  conductors in one motion, hold both in a pocket that stays put through the
  crimp, crimp each one where it lies. The contact never leaves its pocket
  between placement and crimp.
- No lift and no bend in the conductor.
- The force loop is one fixed steel C with its stop inside; everything that
  moves is light.
- The conductor is named at the anvil before any force.

## Major unresolved problems

- **The final crimp over a pre-formed or tacked insulation barrel:** an O over
  a keyhole, a B over the taller shapes, re-registration unmeasured.
  Sectioning and pull tests.
- **Split length** behind the housing: 6–12 mm for T4, 15–26 mm for J1 in
  ending A [w2 §6]; ~25–30 mm on J4 and J7 for ending B's sort (into-the-housing i6, via k8).
  Derek's question.
- **Ending A:** row B's bow staying below row A's wires as pallet B rises
  between them; pallets on swing arms carrying crimped rows. **Ending B:** the
  lower pad through a window sized for an anvil; two pallets and a sort stage
  on one slide.
- **Carrier walls ~0.5 mm** (fine-nozzle print or laminated stencil steel)
  holding a box square and taking 20 N on the rear shoulder at each pull.
- **Insertion force and the latch click** are not public.
- **J4** in ending A.

## What rests on assumptions

- Punch half-widths (1.75–1.9 conductor, 1.9–2.0 insulation) [estimate].
- Tacked insulation width 2.0–2.2 mm [estimate]; pre-formed widths [w2 §2,
  w3b §2].
- The growth, bow and C-arm numbers [estimate: w3 §3, §7; htq §7].
- Everything c6 and c1b rest on.
