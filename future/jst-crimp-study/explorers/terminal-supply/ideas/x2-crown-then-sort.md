# x2 — Crown station, then sort and push: one web clamp from reel to latched housing

**A combination**, named by its sources:
- this explorer's [a2d](a2d-skip-pitch-crown.md): a reel of strip thinned to
  every other contact, run over a steel crown so the ribbon lies flat at any
  width, a knife-set crimp with a hard stop, a level gate across the station,
  a bad contact rejected without a wire;
- into-the-housing's [i6](../../into-the-housing/ideas/i6-sort-then-push.md):
  crimped contacts wait in ribbon order in a staging plane; each is lowered into
  its slot of a 2.5 mm target comb, lower layer first, centre outward; a backing
  blade squares the row; the housing is pushed onto it;
- this explorer's [a6](a6-post-is-the-gripper.md): a post head that holds a
  contact by its own socket, roll set by the pin's flats and the box front on a
  holder face, released anywhere by a stripper.

into-the-housing proposed it as T1 in
[its reading of this explorer](../../../exchange/into-the-housing--on--terminal-supply-w3.md).
i6 needs exactly what a2d leaves (a flat, crimped ribbon end in a staging plane)
and has no grip on a crimped contact that controls roll; a6's post head is that
grip.

Sketch: [`../sketches/x2-crown-then-sort.svg`](../sketches/x2-crown-then-sort.svg) (schematic).
Numbers: [`../calc/w3.py`](../calc/w3.py) §1, §5, §6, §9 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X] and [`wave2`](../../into-the-housing/calc/wave2.out.txt) calc
[ith-w2 X]; [`../calc/wave2.py`](../calc/wave2.py) [w2 §n];
[`../calc/terminal_supply.py`](../calc/terminal_supply.py) [ts §n].

**Related.** into-the-housing's [k6](../../into-the-housing/ideas/k6-one-gantry-crimps-in-the-fan-then-sorts.md)
is the same sort after force-and-form's travelling crimp head. The spool-fed
line (K1 in [terminal-supply on borrowed-machines](../../../exchange/terminal-supply--on--borrowed-machines-w3.md))
could feed station A a flat ribbon end without a person loading the web clamp.

## Picture it

- **The bench.** A base about 450 × 250 mm. Along the back, an MGN12 rail carries
  the **ribbon carriage**: an X carriage with a short Y slide, driven through a
  5 kg bar load cell. On it sit the **web clamp** (one under-width channel that
  takes a single ribbon or a pair edge to edge) and, 10–25 mm in front, a printed
  **fan comb** at 3.5 mm pitch.
- **Station A, on the left, is a2d.** A reel of SXH-001T-P0.6 hangs below the
  bench. The strip rises past the thinning punch and wraps a steel crown block of
  R 25–30 mm. A knife-set anvil sits at the crest, with a drop plate downstream
  and radial pins in the removed contacts' holes at ±7.1 mm. A fence stepper sits
  behind the crown. Above is a 1 t arbor press whose lever a NEMA 17 lead screw
  pulls onto a hard stop on the crown block, with disc springs for overtravel.
  The ELP camera looks down, and a level view crosses the station to a backlight
  tile downstream. A slotted steel **pull fork** on a servo drops onto the crown
  land behind the station contact's insulation barrel.
- **Station B, about 200 mm to the right, is i6 with a6's hand.** Two dock pins
  for the carriage; a printed **target comb** of 1.5–1.6 mm U-slots at 2.50 mm,
  6–10 mm below the fan plane; a **housing nest** on a Y slide, driven by a
  NEMA 17 on a T8 screw through a 20 kg bar cell; a slotted stencil-steel
  **backing blade** on a servo; the camera above; and a6's **post head** on a
  small X–Y–Z stage: a 0.64 mm pin standing 1.5–1.8 mm out of a steel holder
  ≤ 2 mm wide, a stripper, a ±0.2 mm float, and a **fork** of two 0.4 mm tines
  that straddles the wire behind the insulation barrel.
- **What the person does.** Lays a split, stripped ribbon end (or a pair) into the
  web clamp and presses its conductors into the fan comb; picks the loom's
  recipe; drops the housing into the nest; later lifts the finished end out and
  labels it (J4 and J7 share a housing). Mounts the reel once: at skip-2, 0.89 of
  one 8,000 reel covers the program [w2 §7]. Empties the thinning, reject and
  scrap cups.
- **At station A, for each conductor in web order** (a2d's cycle):
  1. The ribbon is drawn back and the strip indexes two pitches. The pins go in,
     the camera measures the station contact, and the fence corrects it.
  2. The carriage presents conductor k over the crest, steered by its insulation
     edge as seen, and the level gate looks across the station.
  3. The press closes to its stop, and the drop plate shears the tab.
  4. **Proof pull.** The pull fork drops behind conductor k's insulation barrel.
     The carriage's Y pulls the whole web back at 20 N through its cell, and the
     camera watches k's insulation edge for slip. Only k is blocked by the fork;
     the other conductors' contacts are free and move with the web.
  5. The fork lifts, and the carriage lifts k and draws back.
  6. A contact that fails its look is sheared with no wire, as in a2d. A crimp
     that fails stops the end and queues a cut-back.
- **Carry.** After the last conductor, the carriage runs to station B and docks
  on its pins. The crimped contacts stick out of the fan comb, lance down, at
  3.5 mm pitch: i6's staging plane.
- **At station B, lower layer first, centre outward** [ith-w2 A, C]:
  1. The camera finds contact k's box front.
  2. The head's fork drops behind k's insulation barrel; between neighbours at
     3.5 mm there is 1.8 mm between insulation surfaces, and +1.30 mm left beside
     a tine [w3 §6].
  3. The pin spears the box from the front at 0.2–2 N, reacted by the fork. The
     head's cell shows a rise, then the wall.
  4. The head carries the contact down 6–10 mm and across (at most 8.5 mm, on J4
     [ith-w3 H]) to slot k. The holder face sets the box front on the placement
     line.
  5. Lowering also presses the wire into the U-slot through the fork's crotch.
  6. The stripper releases the box and the head rises.
  7. The upper-layer conductors go last and lie over the placed ones: J4's 3V3
     and GND, J7's GND.
- **Push and check.** The backing blade drops behind every insulation barrel,
  and the nest drives −Y onto the row. The cell trace shows the lance events: at
  the KONNRA clone figure the sum is ≤ 7 × 9.8 N on J4 and 9 × 9.8 N on J1. The
  blade lifts. The carriage pulls the web back at 5 N per conductor while the
  camera watches each wire at the rear face: a contact that moves more than
  0.2 mm has not latched.

## What locates what

| Moment | Reference | Located part |
|---|---|---|
| Contact at the die | crown block: pins in the removed contacts' holes, fence per contact, anvil land, stop | contact [a2d] |
| Conductor at the die | its own insulation edge, as seen | conductor k (carriage X and Y) |
| Proof pull | pull fork on the crown land | insulation barrel's rear edge |
| A to B | two dock pins | the web clamp and fan comb: the whole end |
| Pick at B | the head's holder face and pin, reacted by the fork | box front, and roll by the pin's flats against the leaves |
| Row | target comb (wire), placement line (box fronts), backing blade (rears at the push) | each contact |
| Push | keyed nest on its Y slide | cavities |

**The reference for "fixed" is the crown block at A and the target comb's base at
B**, joined by the carriage's dock pins; the web clamp is the one datum the
ribbon keeps from first crimp to push.

## What drives and carries force

- **The crimp.** 0.8–2.6 kN closes through the crown block and its stop, as in
  a2d; the arbor press frame only pushes.
- **The proof pull.** 20 N from the carriage's Y goes through the fork into the
  crown block: ~42 MPa on the fork's tines, ~56 MPa on the barrel's rear edge
  [w3 §6].
- **The spear.** 0.2–2 N into the head's fork. The conductor alone cannot react
  it: 20–30 mm of free conductor buckles at 0.17–0.39 N [w3 §6; ith-w3 H].
- **The push.** Through the backing blade into the base.

## How it knows it worked

- At A: a2d's five signals (pins home, the waiting contact's picture, the level
  gate, stop and force, the after look) plus the proof-pull trace.
- At B: the spear trace (rise, then wall), the placement photo (order, roll,
  fronts), the push trace and the per-wire pull-back.

## What each part contributes

- **a2d:** supply from a reel; a located contact; a flat ribbon at any width, so
  J1's 5P + 4P goes through as one nine-conductor end; a level line of sight;
  reject without a wire; and a place for the proof pull.
- **a6:** a hand that holds a crimped contact by its own socket, with roll set by
  flats and the front on a face, and no fingers at 2.5 mm pitch.
- **i6:** J4's and J7's crossings; the pairs; J2's empty cavity; the backing
  blade; a gang push that stores no feed; the latch check.
- **Together:** a reel and a ribbon end become a latched, tested housing with one
  datum, the web clamp, from first crimp to push.

## Numbers

- **Fan split at A** [w3 §5]: at 3.5 mm pitch, 3P 11 mm, 4P 13 mm, 5P 16 mm, the
  J4 and J7 pairs ~23 mm, J1 ~26 mm; 1–5.5 mm less at 3.0 mm, and less again at
  the 2.5–2.8 mm the punch holder allows [a2d].
- **Staging height at B.** At 3.0–3.5 mm staging pitch J4 needs ≥ 5.5–6.1 mm and
  J7 ≥ 2.6–3.2 mm; J1 and the straight looms have no crossing [ith-w3 H]. 6–10 mm
  covers the unit.
- **At the target row (2.5 mm), placed neighbours:** the tines clear the
  neighbours' wires by +0.30 mm and the holder their boxes by +0.52 mm [w3 §6].
- **Machine time.** 2.7–3.1 h per unit: a2d's 94 min, plus 60–87 min of sort,
  pull and push, plus the carriage moves [ith-w3 L; w3 §6]. It runs unattended
  between loads.

## Branches

- **Loose contacts at A (x2 with a6's open die).** Station A becomes a6's open
  die with the post head placing kit contacts from a pocket plate; the same head
  then sorts at B. One head, two jobs, no reel. 2.8–3.2 h per unit [w3 §6]. It
  keeps a6's own open problems (pocket plate, lance groove, grip).
- **a2b's tag as the handle at B.** At A the carrier is cut either side of the
  pilot hole instead of at the tab; at B a gripper takes the pin in the hole plus
  a finger on the crimp. Tags 2.3 mm wide cannot enter 1.5–1.6 mm U-slots, so each
  rear stands 3.8–4.2 mm ahead of the comb face and the blade bears on the tag's
  rear edge (0.46 mm², 54 MPa at 25 N). The tags must be bent off after a partial
  push: a2b puts the carrier edge between 0.05 mm inside and 0.9 mm outside the
  rear face at full seat [ts §4], so in the worst case the tag stops the seat.
- **i6b's post bed at B.** Identity is proven before the latch, but the post head
  cannot thread a contact onto a bed post, because both want the box front. This
  branch uses i6's barrel fingers and gives up the post head. The bed push is
  13–14.5 mm [ith-w3 A].

## Problems and repairs

1. **The spear needs the fork** (above). Its tines must be ≤ 0.4 mm and bear on a
   crimped insulation barrel ~1.8–2.0 mm wide.
2. **Capture at the box entry is ±0.1–0.25 mm** (0.60–0.70 mm entry, a
   near-pointed pin tip) [w3 §1]. The staged fronts are found by the camera. A
   roll left by the crimp is squared by the pin's flats, which twist the
   conductor slightly; whether a staged contact's roll exceeds what the entry
   accepts is unknown.
3. **Fronts on a line, rears scattered.** The holder face aligns fronts, so the
   rears differ by the contacts' length spread: ±0.05 mm within a lot [estimate],
   up to ±0.25 mm between brands [xh-facts §1]. During the push each contact
   slides back in its slot (1–11 N of slot grip [ith-w2 D]) onto the blade before
   its lance folds, which staggers the events in the trace. Useful, unmeasured.
4. **Strip-bound at A.** a2d needs strip, genuine or clone reel. The kit contacts
   serve only as hand-repair stock, unless the loose branch is used.
5. **The finished loom's split.** 11–26 mm of split, plus i6's set step of
   6–10 mm and bows up to ~2.9 mm on J4 [ith-w2 B]. Whether that is acceptable
   behind the housing is Derek's question.
6. **Trimmed conductors.** J7's third 3P conductor and J2's cavity-3 conductor are
   cut back at the fan root by the person, or by a snip at A; the carriage skips
   that position.
7. **a2d's own open problems carry over:** real SXH pitch and carrier temper;
   knife-set blade width and protrusion; seating the anvil into the crown; the die
   outside its applicator.

## Steps covered, and what it hands back

- **Covers:** supply from a reel; thinning; placing each contact; holding;
  placing each conductor; crimping; severing; a proof pull; sorting into pin-map
  order with crossings; insertion by a gang push; latch checks.
- **Hands back:** splay and strip; loading the ribbon end and the housing;
  trimming J2's and J7's unused conductors (or a snip does it); labelling; the
  far-end continuity test; emptying cups.

## Printed and bought

| Part | Source |
|---|---|
| Press | VEVOR AP-1 1 t arbor press (Prime, $61.90, 150 mm opening, 81 mm throat) |
| Drives and rails | Iverntech NEMA 17 with integrated Tr8×2 screw (Prime, $27.99, thin listing); MGN12 300 mm rail (Prime, $20.49); MGN9 200 mm rail (Prime, $16.12); MG90S 4-pack (Prime, $13.88) and DS3218 (Prime, $14.99) servos |
| Sensing | ShangHJ 5 kg bar cell with HX711 (Prime, $9.99) for A's 20 N pull; a 20 kg cell for B's push of up to ~90–225 N ([`../sourcing-requests.md`](../sourcing-requests.md) #29) |
| Crown pins | Accusize pin gauges including 1.448 mm (Prime, $45.58) |
| Springs | Hilitchi Belleville assortment (Prime, $14.99, light duty); a heavy series in [`../sourcing-requests.md`](../sourcing-requests.md) #27 |
| Posts | 2.54 mm header strips (Prime, $7.99, pin cross-section not stated), or hardened 0.64 mm square pins (#16) |
| Knife set | no Prime listing; eBay and AliExpress titles only [a2] |
| Contacts | Digi-Key or LCSC reel [xh-facts §6]; no Prime listing |
| Target comb, fan comb, web clamp, nest, head body | printed |
| Backing blade, fork tines | stencil steel (JLCPCB, from $3) or 1095 shim (Prime, $53.39) |

All Prime rows are from [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.

## Major unresolved problems

- **Roll of a staged crimped contact** against what the box entry accepts.
- **The split behind the housing,** and i6's set step.
- **a2d's die, pitch and temper** questions.
- **The fork's tines** bearing on crimped insulation barrels without marking the
  silicone.

## What each conclusion rests on

- **Facts [mfr, source]:** clone contact and entry dimensions [xh-facts §1];
  KONNRA insertion figure; Prime listings.
- **Calculations [calc]:** capture [w3 §1]; split [w3 §5]; tine and holder
  clearances, spear buckling, proof-pull stresses, time [w3 §6]; staging heights,
  bed push, time [ith-w3 A, H, L]; layer rules and slot grip [ith-w2 A–D]; reel
  use [w2 §7]; tag edge at the seat [ts §4].
- **Estimates:** within-lot length spread; machine time; insertion per contact.
- **Assumptions:** a2d's (pitch 7.1 mm, C5191 temper); the pin's flats square the
  roll without marking the box.
