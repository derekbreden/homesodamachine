# a2 Two pallets meet: the carrier strip is the contact pallet

## Picture it

The ribbon is a precision part that holds its conductors in order, and the
carrier strip is a precision part that holds its contacts in order. Fan the
ribbon to the strip's pitch and set one on the other: every contact is placed
on its conductor in one passive motion. Crimping becomes a separate job that can
take as long as it likes. Sketch:
[`../sketches/a2-two-pallets-meet.svg`](../sketches/a2-two-pallets-meet.svg)
(schematic).

**Where things start.**
- **Contacts.** A segment of **N + 2 contacts on their carrier** (N for the
  ribbon, one spare at each end) lies on a **strip pallet**, a flat steel bar or
  printed PET-CF with steel inserts.
  - Slot pins in the carrier's rectangular slots between contacts locate the
    strip. The clone drawings show a Ø1.5 round pilot hole on each contact's
    centreline and a rectangular slot between holes [source S19]; the round
    holes lie under the wire's path, so the pins go in the slots.
  - A comb clamp bar presses the carrier down between the conductor paths.
  - The contacts stand open side up and cantilever forward on their 0.8 mm tabs
    onto a printed support comb, which swings away later. **The support comb and
    the rail below carry a groove along X under the lance line**, 2.2–2.7 mm
    behind each contact's front and at least 1.1 mm deep. On a flat face the
    retention lance, 0.6–0.9 mm proud of the floor, props every contact
    7.6–15.9° about its tab, against the tab's ~2.3° of elastic bend
    [w3 §5].
- **Ribbon.** A ribbon pallet like [a1](a1-pallet-tour.md)'s, prepared at its
  stations: parted to the split root at the lid's face ([a7](a7-zip-station.md));
  **fanned to the strip pitch**, ~7.1 mm, in the plane where the conductors
  will lie in the barrels; flush-cut and ring-stripped at the fan block's face
  ([a8](a8-rolling-ring-scorer.md)), because at 7.1 mm a 5P's outer conductors
  recede 2.77 mm against the centre one [calc W2 §3].

**What moves.**
1. **Dock.** The ribbon pallet comes down onto the strip pallet, by hand or on
   one vertical axis. Three steel balls underneath settle on three hardened
   seats (ball pairs or case-hardened rod; unhardened stainless dowels dent at
   1,100–1,700 MPa [calc F §1]), and magnets pull it home. All N conductors go
   into all N open contacts at once: strands between the conductor-barrel
   wings, jacket between the insulation-barrel wings, insulation edge in the
   gap between the barrels.
2. **Press in, if needed.** Whether the conductors drop in or must be pressed
   depends on the open-wing width, which nobody has measured (below). If they
   must be pressed, a comb of fingers on the ribbon pallet lands on each jacket
   1–2 mm behind its insulation barrel and pushes it past the wing tips at
   ~0.5–2 N [calc F §4]. The push goes into the support comb and rail, never
   into the tabs.
3. **Check.** Every contact is common through the carrier. With the far-end
   pogo port ([a6](a6-housing-as-last-comb.md)), each conductor reads continuous
   to the grounded carrier once its strands touch the barrel. A camera frame of
   the docked row shows none sitting on a wing tip.
4. **The walking head.** A crimp head on an X carriage runs along the front
   edge and crimps each contact in turn.
   - It is a small steel C-frame (borrowed-machines'
     [b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md)),
     turned so the C opens toward the carrier with its back beyond the box ends.
     Its arms are no more than 10 mm wide in X, which clears neighbours at
     7 mm [calc §3b].
   - Its dies are a harvested OTP applicator's crimper and anvil. A NEMA 17 with
     a 10:1 gearbox turns a 3 mm crank inside the C, ~3.8 kN at 0.1 mm above
     bottom dead centre. The head weighs about 1 kg, and a 10–40 kN/mm C gives
     ±30 to ±8 µm of crimp-height scatter [borrowed-machines calc presses §5].
   - Its lower arm rides a **hardened rail on the strip pallet flush with the
     contacts' floor**, so the head floats in Z and the lower die arrives at
     floor height without lifting the contact.
   - It approaches from the box end. The lance hangs across that path: the
     lower die passes under it and rises behind its tip only if the neck between
     box and conductor barrel, t, is at least 0.34–0.74 mm [w3 §5]. Otherwise
     the lower die drops, passes, and rises, as force-and-form's
     [f4](../../force-and-form/ideas/f4-crimp-head-goes-to-the-wire.md) anvil
     does.
5. **Proof pull.** With every contact crimped and the carrier clamped, the
   shear comb's pad comes down on the crimped barrels and a hook pulls each
   conductor in turn to ~20 N at the fan block's face. Without the pad the tab
   is the only reaction, and the wire's axis stands 0.95 mm above the tab's
   mid-plane, so every contact pitches about its tab at 2.5–4.6 N [w3 §4]. With
   the pad (3.8–6.3 N) the tab carries the pull in compression, 125 MPa, far
   from buckling [calc F §3], into slot pins at every slot.
6. **Shear.** The **shear comb** cuts every tab: a hardened lower bar with one
   notch per contact, its edge at the contacts' rear; the pad on the crimped
   barrels; a lever that drives the carrier down past the edge. Tab length is
   the bar edge's position against the slot pins.
7. **Lift.** The ribbon pallet lifts away with its crimped contacts, all with
   the same roll, swaps its fan block for a 2.5 mm closing block and goes to
   insertion ([a6](a6-housing-as-last-comb.md)).

**What locates what, and the reference for fixed.** **"Fixed" is the strip
pallet's slot pins.**
- **Contacts:** the carrier on the slot pins; contact-to-slot position is the
  stamping's, ±0.05 mm [assumption].
- **Ribbon pallet:** its seats are on the same plate, so it locates to the pins
  within ~0.01–0.02 mm [estimate].
- **Conductors:** the fan block, ~±0.1 mm at its face.
- **Capture at the barrels.** Read as inside widths, the clone drawings' open
  widths give +0.54 mm a side for the strands and +0.51 mm for the jacket;
  read as outside widths at the low tolerance, +0.14 and +0.01 mm; if JST's
  1.95 mm end-view envelope includes the open insulation wings, a 1.7 mm jacket
  meets 0.08 mm of interference a side [P3 §2]. Placement error stacks to
  ~0.16 mm RSS, 0.32 mm worst [P3 §2, estimate]. Which reading is right decides
  between step 1 alone and step 2.
- **Axial:** the strip line at the fan block face, against the slot pins,
  sets where the insulation lands (±0.2 mm stacked [estimate]).
- **Crimp:** the head's anvil cradle centres the contact in X as the crimper
  closes, as an applicator's does. No pin enters the round pilot hole, which lies
  under the jacket. Z comes from the rail.

**What drives the crimp and carries its force.** The force is closed inside the
head's C: crank → crimper → contact → anvil → C. 0.8–2.6 kN per contact, design
to 3 kN [xh-facts §4]. The pallets and the carriage carry none of it.

**How it knows it worked.**
- **Before any force:** conductor-to-carrier continuity for every conductor,
  and a camera frame of the docked row.
- **During:** a force curve from a strain gauge on the C, with stop-before-bottom.
- **After:** a camera frame per contact, the 20 N pull per conductor, and a
  micrometer on the session's first crimps.

**What the person does.**
- Snips a strip segment, lays it on the slot pins, flips the clamp bar and
  support comb into place (about 20 s).
- Loads the ribbon pallet, starts the cycle, takes out the finished loom.
- Makes the far end.

## Steps it covers and what it hands back

- **Machine:** placement of every contact (docking), placement check, crimp
  (walking head), proof pull, tab cut; with [a7](a7-zip-station.md),
  [a8](a8-rolling-ring-scorer.md) and [a6](a6-housing-as-last-comb.md), also
  split, strip and insert.
- **Person:** cutting to length, laying strip segments, loading the ribbon
  pallet, moving it between stations, far ends.
- **Contacts:** 81 a unit at N + 2 with trimmed positions snipped out; an
  8,000 reel is ~99 units, $1.90 a unit at $0.0235 [calc F §7].

## Mechanism notes

### Strip pitch and the fan

- **The pitch is not public.** JST's carrier dimensions are licence-gated
  [xh-facts §1]. Würth's public drawing of an analogous 2.50 mm contact gives
  **7.10 mm** [mfr, via change-the-question and terminal-supply]. Clone
  drawings, not to scale, give 6.8–9.5 mm [calc §2; xh-facts §1]. One Digi-Key
  100-piece strip (455-1135-100-ND, $4.71) settles it.
- **Parted length.** Fanning each ribbon alone to ~7 mm needs 21 mm (3P), 25 mm
  (4P) and 30 mm (5P) [calc §2]. A pair goes through as two cassettes and meets
  at insertion.
- **The length the fan leaves in the loom.** Cut after the fan (order A in
  [a5](a5-part-fan-strip-in-the-pallet.md)), the outer conductors stay longer:
  closed to 2.5 mm and latched at one depth, a 4P's outer pair carries 1.85 mm
  and a 5P's 2.46 mm of excess, a 4–5 mm arc over a 20–30 mm split
  [calc F §5]. Stripping before the split and fanning with equal paths (order B,
  [a9](a9-reel-end-docks.md)) leaves none, at the cost of humps in the fan
  block's inner grooves.
- **Every other contact** (14.2 mm) would halve the fan's lateral move but waste
  half the strip. Its only use is a strip pitch that turns out small.

### Why contacts stay on the carrier through the crimp

- The carrier locates each contact better than a printed nest could.
- Nothing has to hold a 0.043 g part [source S27b] on its own.
- The carrier and slot pins react the proof pull, with the pad down.
- All tabs are cut in one stroke of the shear comb.
- [a10](a10-dock-tack-then-nest.md) ends the carrier's job earlier: it tacks
  every insulation barrel on the strip, cuts the tabs, and crimps each contact
  alone in a steel nest.

### The contacts' tabs

Each contact cantilevers on a tab about 0.8–1.0 × 0.20 mm. It yields at
0.5–0.9 N applied at the box, or 1.0–1.7 N at the barrels, after only
0.10–0.14 mm of elastic lift [calc X §5]. A lower die arriving 0.1 mm high
lifts the contact and bends its tab for good, which is why the head's Z comes
from the rail on the strip pallet.

### The shear comb

A tab shears at 50–160 N, so 250–800 N for five [calc X §5]. Without a die edge
under each contact's rear, the crimped contacts would bend down with the carrier
and the tabs would tear long and ragged; JST lists "too much cut-off length" as
a fault [mfr S5]. So the lower bar is notched at strip pitch, its edge at the
contacts' rear, with the pad holding each crimped barrel down on it.

### The proof pull, conductor by conductor

The fanned outer conductors reach their contacts through S-bends. A single pull
on the whole pallet would load the straightest conductors first and straighten
the others' S-bends, which yield at 0.31–0.61 N·mm [P3 C11], before any crimp
took load. So each conductor is gripped at the fan block's face with 20–40 N of
normal force [calc §4] and pulled on its own.

## Printed and bought parts

| Part | Source | Evidence and note |
|---|---|---|
| Ribbon pallet, fan blocks, support comb, clamp bar, finger comb | printed | |
| Strip pallet with the head's rail and the lance groove | steel flat with pressed pins and a ground rail | nothing loads it hard except the head's Z float |
| Balls, seats, magnets | bought | 6 mm 52100 G25 balls, 100 for $6.65; N52 10 × 3 mm discs, 60 for $23.99 [Prime]; 8 mm case-hardened rod, two 100 mm for $6.99 [Prime: ground shaft, 8 mm] |
| X carriage for the head | bought | MGN12 rail $20.49; NEMA 17 Tr8×2 $27.99 [Prime] |
| C-frame head | laser-cut steel plates (SendCutSend, 2–4 days), NEMA 17 with 10:1, 3 mm crank, harvested OTP crimper and anvil | borrowed-machines b3; OTP knife set: no Prime listing |
| Shear comb | laser-cut or ground tool-steel bar, printed lever | notch spacing from the measured strip |
| SXH-001T-P0.6 strip | bought | Digi-Key 100 / 500 / 1,000 at $0.047–0.040; reel $0.0235 [xh-facts §6] |

## Problems, repairs and branches

1. **Contacts on 0.8 mm tabs sag when a conductor lies in them.** The support
   comb takes docking loads. After it swings away a conductor's residual push of
   ~0.1 N at 6 mm is well under the tab's yield at the box, and the head's lower
   die re-supports each contact from the rail before the upper die arrives.
2. **The lance props the contacts on a flat face.** The groove along X.
3. **The head lifts the contact before it crimps.** The rail flush with the
   floor.
4. **A pilot pin would poke the conductor.** No pin; the anvil centres the
   contact and the slot pins hold it to ±0.05 mm.
5. **A hand-tool head cannot walk a row.** A ratchet crimper's jaw lies along
   the row toward its pivot; at 7.1 mm pitch 1–4 neighbours lie within its
   10–30 mm nest-to-pivot extent [calc X §6]. So the head is a C-frame with
   applicator dies. JST's YRS-110 ("parallel action, ratchet style handtool...
   designed to crimp the applicable contact in strip form", $1,565.93, Digi-Key
   [xh-facts §2]) is the one bought hand tool made for strip.
6. **The gang shear bends the crimped contacts.** The notched shear comb. A
   variant cuts each tab in the head with the applicator's punch and floating
   blade, and gives up the pull against the carrier.
7. **The fan leaves the outer conductors short.** Flush cut and strip at the fan
   block face after the fan; or order B ([a9](a9-reel-end-docks.md)).
8. **Why a head at all?** [a2e](a2e-docked-strip-through-a-feedless-applicator.md)
   runs the docked row through a bought applicator with its feed removed;
   [a2b](a2b-gang-press-stop-die.md) crimps the whole row in one stroke;
   [a10](a10-dock-tack-then-nest.md) tacks the row and crimps each contact in
   a nest; [a2d](a2d-by-hand.md) and [a10b](a10b-tacked-row-into-the-hand-tool.md)
   do it by hand.

## What it contributes

- **Placement becomes a docking.** "Place the metal bit on the end of the
  cable" is one gravity-and-magnet motion for every conductor of a ribbon at
  once, before any force is applied, and checked electrically.
- **Crimping becomes a separate step** with no feeding, locating or placing:
  closing a die on something already assembled. Any force source works.
- **The carrier becomes a fixture** for continuity, pull and one shear.

## Major unresolved problems

- **The strip pitch, and the open-wing width**: one $4.71 strip under the
  caliper and camera settles both.
- **The head:** harvested applicator dies aligned to ~0.02 mm in a ~1 kg
  C-frame, approaching from the box end past the lance (t).
- **Whether docked conductors stay in their barrels** while the support comb
  swings away and the head approaches.
- **The shear comb's tab length** against JST's criteria.
- **21–30 mm of split behind the housing**, with a 4–5 mm arc in the outer
  conductors: Derek's call.

## Related ideas

- Branches: [a2b](a2b-gang-press-stop-die.md), [a2c](a2c-loose-contact-cassette.md),
  [a2d](a2d-by-hand.md), [a2e](a2e-docked-strip-through-a-feedless-applicator.md),
  [a10](a10-dock-tack-then-nest.md) and its [a10b](a10b-tacked-row-into-the-hand-tool.md).
- The docking at a reel clamp: [a9](a9-reel-end-docks.md).
- Other explorers: borrowed-machines
  [b3](../../borrowed-machines/ideas/b3-gantry-carries-the-crimp-head.md);
  terminal-supply's carrier-as-fixture ideas
  ([a2b](../../terminal-supply/ideas/a2b-carrier-as-handle.md)).

## What rests on assumptions

- Strip pitch ~7.1 mm; contact-to-slot stamping tolerance ±0.05 mm.
- Kinematic seat repeatability [estimate].
- That JST's strip has the clone drawings' layout: tab at the insulation-barrel
  end, round holes on the contact centreline, slots between. JST's catalog shows
  round holes and slots on side-feed chain terminals [xh-facts §1].
- Press-in forces [estimate, calc F §4].

## Labels

As [a1](a1-pallet-tour.md#labels); [w3 §n]:
[`../calc/exchange_on_force_and_form_w3.out.txt`](../calc/exchange_on_force_and_form_w3.out.txt).
