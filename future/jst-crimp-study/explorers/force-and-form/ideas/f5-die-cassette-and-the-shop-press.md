# f5 — Die cassette: load and look at leisure, then one push per ribbon end

Explorer: force-and-form. Sketch: [`../sketches/f5-cassette-gang.svg`](../sketches/f5-cassette-gang.svg) (schematic).
Numbers: [`../calc/gang.out.txt`](../calc/gang.out.txt),
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt) §3,
[`../calc/metrology.out.txt`](../calc/metrology.out.txt),
[`../calc/exchange_procedure_w3.out.txt`](../calc/exchange_procedure_w3.out.txt) §7 [calc FP §n].
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Branches: [`f5b-half-row-cassette.md`](f5b-half-row-cassette.md); the every-k-th
and strip-pitch variants below. Related: [`f9b-tack-on-the-strip.md`](f9b-tack-on-the-strip.md)
(a strip docked at its own pitch, then crimped one at a time),
[`f7-where-the-steel-comes-from.md`](f7-where-the-steel-comes-from.md) (a
cassette of one is f7's cartridge).

## Picture it

Force is the one thing this bench has in surplus. The **VEVOR 12-ton shop
press** is idle [repo: tools.md], about 118 kN [calc C1]. This idea puts all
the precision into a small steel **cassette** and lets anything that pushes
close it: the shop press, an arbor press, or a motorised screw.

- **The cassette.** A lower shoe carries N anvils in a row, one per
  conductor of the ribbon end, 3 to 5. An upper shoe carries N crimpers. Two
  guide posts align the shoes, springs hold them open, and two steel **stop
  blocks** set how far they can close. The stops, not the press, decide the
  crimp height.
- **The strip is the pallet.** A segment of N contacts, still on their
  carrier, lies on steel pilot pins in the lower shoe. The strip already holds
  the contacts at its own pitch, so the cassette's stations sit at the
  strip's pitch and the strip locates every contact at once.
- **Loading.** At a loading station on the bench, under the ELP camera:
  1. The person lays a strip segment on the pins.
  2. The splayed ribbon end goes into a printed comb behind the anvils, each
     conductor into its slot. Fanned to the station pitch, the outer
     conductors recede against the inner ones (2.8 mm for a 5P at 7.1 mm), so
     the end is flush-cut and stripped **after** the fan, at the comb's face,
     which puts every insulation edge on one line (ribbon-as-pallet a8 rolls a
     whole row under two razors at any pitch; procedure-is-the-machine p7
     strips the webbed end in one stroke, and then the fan's pull-back,
     ~0.6 d²/L, is the stated cost [calc FP §7]).
  3. A hinged printed presser comb pushes each insulated conductor down
     behind its insulation barrel, so the strands lie in the open U's.
  4. The camera looks straight down at N open barrels: strands in every U,
     none over a wing tip, insulation edge in the window.
  4a. **Identity per station.** Each anvil is insulated from the shoe and
      wired. With the ribbon's far end in a pogo port (ribbon-as-pallet a6) or
      on a reel (procedure-is-the-machine p3/p6), every station reads which
      conductor lies in it before any force: a conductor in the wrong station
      is caught, which the summed force cannot name.
  5. A miss means lifting a conductor and relaying it, all before any force
     exists.
- **Crimp.** The cassette slides on a rail under the shop press ram. The
  person pumps until the shoes meet the stop blocks, which shows as a sudden
  rise on the press gauge or on a load cell under the cassette. N crimps
  happen in one stroke.
- **Cut-off.** In the same stroke, a spring-loaded shear plate under the
  carrier is pressed down by the upper shoe and cuts every tab, as an
  applicator's floating shear does [mfr: MKS-L §6-3, §6-5; prior-art §3]. Or a
  second, separate stroke does it.
- **Release.** Springs lift the upper shoe, and the ribbon end comes out
  with N crimped contacts.
- **Proof pull.** Each conductor is gripped at the comb face and pulled on
  its own, ~20 N, against a pad on its crimped barrels (a pull across the whole
  ribbon would first straighten the fanned S-bends, whose copper yields at
  ~0.36 N·mm, and load the straightest conductors first; ribbon-as-pallet
  a2).
- **What locates what.** Fixed is the lower shoe: its pilot pins locate the
  strip and the strip the contacts; the guide posts locate the crimpers; the
  stop blocks set crimp height; the comb and presser place the conductors.
- **The person** does the loading, the pumping and the insertion. Per unit
  that is 14 ribbon ends, so 14 loadings and 14 strokes. The shop press is
  hand-pumped, so this is usable with no motor at all.

## What drives the crimp and carries the force

- **Stroke force.** For a whole ribbon end it is N × one crimp: **5–12 kN**
  for 3–5 stations across the modelled family [calc: gang §2].
- **What can push it.**
  - The shop press covers any ribbon end with an order of magnitude to spare.
  - A 1 t arbor press covers 3 stations at the high estimate and 5 at the
    central one [calc: gang §2] ([Prime: VEVOR AP-1, $61.90, 150 mm opening,
    281 ratings]; Harbor Freight #59766, $79.99 [source]).
  - A motorised screw covers it: a NEMA 23 with a 5:1 belt on a 1605 ball
    screw gives ~6 kN [calc: drives §C]. That makes this an automated
    stroke.
- **Force loop inside the cassette.** Shoes, anvils, crimpers, stop blocks
  and posts. The outer press's springiness and ram play cost only travel:
  about 1 mm of extra stroke even for a soft frame [calc: force_loop §3].
- **Unbalanced strokes.** One station carrying half its force puts a moment
  on the shoes. Two posts 60 mm apart take it as ~100–365 N of side load, and
  10 µm of post clearance tilts the outermost station by 2.5–9 µm [calc: gang
  §3].
- **"Gang of one."** The same cassette with one station, pushed by hand in
  the arbor press, is the cheapest thing in this explorer's set. It is a
  portable, self-stopping die that goes in any press on the bench.

## References and tolerances

- **Fixed reference.** The lower shoe. Its pilot pins locate the strip, and
  the strip locates the contacts (±0.03–0.06 mm [calc: placement_budget]).
- **Station to station.** The anvils are ground as one block, or each is
  shimmed to about 0.01 mm. Otherwise the stations' crimp heights differ
  [calc: gang §3].
- **Crimp height.** Set by the stop blocks' height relative to anvils and
  crimpers, and adjusted by shimming the stops.
- **Conductors.** The comb holds each to ±0.1 mm at its slot; the U walls
  take ±0.3 mm. Axial position is the stop bar's, about ±0.2 mm.
- **Where precision is needed.**
  - At loading: pins, comb, stop bar.
  - At the first die touch: the guide posts.
  - At the bottom: the stop blocks.
  - At release: springs and a stripper plate.

## Station pitch: the one number this idea hangs on

- **2.5 mm is impossible.** An insulation crimper's channel plus two
  tool-steel walls is 3.5–4.4 mm wide, and the open insulation wings are
  2.5–3.0 mm wide [calc: gang §1; source S19–S22]. The minimum pitch is
  3.8–4.7 mm.
- **Two ways to set the pitch.**
  - *Stations at the strip's pitch.* Unmeasured; 7–9.5 mm scaled from clone
    drawings [xh-facts §1]. The contacts stay on their carrier, which makes
    loading trivial. A 5P ribbon then fans to 30–38 mm: its outer
    conductors move 12–15 mm from their place in the ribbon [calc: gang §1].
    That needs a longer split behind the housing.
  - *Stations at 5.0 mm, every other housing cavity.* The fan is modest (5P
    outer conductors move 6.6 mm), but the contacts have to come off the
    strip and go into shaped pockets as loose pieces. That brings back
    placement by hand or feeder, and vibration seating in pockets needs a
    camera check.
- **This is a question for Derek.** How long a split can each loom carry
  behind its housing?
- **A third way: keep the strip, crimp every k-th conductor.** Four
  conductors span 4 × 1.7 = 6.8 mm, 0.3 mm from Würth's 7.10 mm carrier pitch;
  for any pitch from 7.1 to 9.5 mm some k of 4, 5 or 6 sits within 0.7 mm
  [change-the-question calc off §5]. A strip segment on its pins takes
  conductors {1, 5, 9…}, then {2, 6…}, and so on, each moving 0.7 mm or less
  instead of 12–15 mm.
  - *The price.* k strokes per ribbon end with small gangs (3P 1+1+1;
    5P 2+1+1+1; J1 laid as nine, 3+2+2+2), and the conductors not in the row
    lifted 3–4 mm off the anvil plane, 11–19° over a 12–20 mm split. A
    3.5 mm lift leaves 0.5–2.2 mm of residual rise at 15 mm free and 0–0.8 mm at
    20 mm (procedure-is-the-machine's set model [calc FP §1]), so a squaring pass
    follows.
  - *What decides it.* The $4.71 strip decides k.
- **A fourth: half-rows at 5.0 mm** with loose contacts in steel pockets, both
  half-rows then merged at 2.5 mm and inserted with one housing move:
  [`f5b-half-row-cassette.md`](f5b-half-row-cassette.md).
- **A fifth: the strip docked at its own pitch, tacked, cut, and crimped one
  contact at a time** in a keyed nest, which gives up the gang but keeps the
  strip's placement: [`f9b-tack-on-the-strip.md`](f9b-tack-on-the-strip.md).

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| Shoes, stop blocks, pilot pins, guide posts and bushings, springs | steel, bought or cut | SendCutSend A36 plate [source]; [Prime: 10 mm case-hardened rods, $17.99; uxcell 10 mm bronze flange bushings, $11.99; Glarks 8 mm light die springs, $16.95]. No two-post die set surfaced on Prime |
| N crimper and anvil pairs | steel dies, EDM or shop-made | f3 routes b and c; [`f7`](f7-where-the-steel-comes-from.md). One EDM program cuts N matched profiles in one plate. Harvested SN jaws do not gang: one jaw pair has one XH nest. N OTP knife sets could, each in its own slot, at a pitch no smaller than a knife set's width |
| Floating shear plate and blades | steel | — |
| Comb, presser comb, stop bar, loading tray, rail | printed | — |
| Force reading | a 5 t load cell under the cassette, or the press's own gauge | [Prime: bellows compression load cell 0–5 t with indicator and peak hold, $129.00, thin; raw mV/V access for an HX711 not stated]. Whether the VEVOR shop press has a gauge is a question for Derek |
| Pusher | shop press (owned); a 1 t arbor press; or a NEMA 23 ball-screw pusher | [repo: tools.md]; [Prime: VEVOR AP-1, $61.90] |

## What was tried against it, and the repairs

1. **Overpumping.**
   - *Conflict.* The shop press can put 118 kN through a cassette built for
     ~12 kN. Stop blocks of 2 × 18 × 18 mm see ~180 MPa at full press force,
     which steel survives [calc, hand]. A 5 t load cell in the stack would
     not.
   - *Repair.* Watch the gauge, or leave the load cell out and read force
     from the jack's pressure. Or use the arbor press or a screw pusher, whose
     force is inherently limited.
2. **The summed force cannot say which station failed.**
   - *Conflict.* A missing conductor drops the sum 8–20 % for 3–5 stations,
     if an empty barrel keeps 40–60 % of its force [assumption; calc: gang
     §4]. Industrial monitors work in a ~±4 % band. So the sum probably sees
     a missing conductor, but it cannot say which, and sees nothing finer.
   - *Repair.* The camera, before the stroke, is the per-station check.
     Afterwards, a caliper or micrometer check of crimp height samples one
     station per stroke.
3. **Die height matching.**
   - *Conflict.* N stations with independent heights give N crimp heights.
   - *Repair.* Grind the anvils as one block, or shim each, and check each
     station with test crimps.
4. **The tab lies under the conductor.**
   - *Conflict.* A shear from above cannot reach the tab without meeting the
     wire.
   - *Repair.* The applicator's answer: the shear sits under the carrier and
     is pushed down, so the carrier drops away from the contact.
5. **Loading a splayed ribbon into N slots at once.** It is fiddly for a
   person, but it is done calmly, with a camera and no time pressure. A
   comb with entry chamfers helps.
6. **The loom map belongs in the force check.** J2's and J7's 3P ends each
   carry a trimmed conductor. In a strip cassette that station either crimps
   a contact with no wire or runs with a gap in the strip, and the sum falls by
   the same 8–20 % [calc: gang §4] that reads as "missing conductor"
   [change-the-question on f5]. The expected occupancy of each ribbon end sets
   the band.
7. **The lance under the anvils.** Each anvil stops short of its contact's
   lance or carries a relief under it: the lance hangs 0.6–0.9 mm below the
   floor under the front of the conductor barrel
   ([`../calc/on_into_the_housing.out.txt`](../calc/on_into_the_housing.out.txt) §1).

## Contribution

- **Inspection before force, for a whole ribbon end.** Every conductor's
  placement is seen and fixed while nothing is committed.
- **The strip is a precision pallet.** Its pilot holes locate N contacts
  with no feeder.
- **The idle press does all the force work.** There is no motion system
  to build at all for a first version.
- **Stop blocks in a self-contained cassette.** Any press, however sloppy,
  becomes a precision crimp press. f2b and f3 use the same principle.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Splay | the person, into the comb (the comb is the splay jig) |
| Strip | after the fan, at the comb face (a8), or the whole webbed end at once before the fan (p7) with its pull-back |
| Place the contacts | the strip, on pins |
| Place the conductors | the person, checked by camera |
| Crimp and cut | one push |
| Insert | after; the conductors come out at the station pitch and converge to 2.5 mm at the housing. For the 4P family the cassette's comb can be into-the-housing i3's shuttle row: a fan plate closes it to 2.5 mm and the housing is pushed onto the whole row (K3 in [force-and-form's reading of into-the-housing](../../../exchange/force-and-form--on--into-the-housing.md)). The row keeps the copper set of its fan |

## Major unresolved problems

- **Carrier-strip pitch.** It decides between contacts on the strip with a
  wide fan, and loose contacts at 5 mm with a modest fan. It is unmeasured.
- **Split length the looms can carry.**
- **N die pairs**, and matching their heights.
- **The proof pull per conductor** at the comb face, which needs a gripper
  per conductor or one that walks.
- **Identity wiring:** insulating N anvils from the shoe, and the far-end port
  on every ribbon end.
- **Loading comfort.** Whether laying 3–5 floppy conductors into a comb, then
  pressing them into U's, is quicker than today's hand crimping. If it is
  not, this idea buys quality and inspection, not labour.

## Which conclusions rest on assumptions

- **Stroke forces** rest on the modelled family.
- **Headroom.** The force an empty barrel keeps is assumed to be 40–60 %.
- **Post spacing, clearance and engagement** are assumed.
- **Strip pitch** is estimated from drawings not to scale.
