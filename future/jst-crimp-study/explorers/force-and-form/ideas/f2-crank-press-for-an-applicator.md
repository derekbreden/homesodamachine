# f2 — Build the press, buy the applicator: a crank press turning at ~2 rpm

Explorer: force-and-form. Sketch: [`../sketches/f2-crank-applicator-press.svg`](../sketches/f2-crank-applicator-press.svg).
Numbers: [`../calc/drives.out.txt`](../calc/drives.out.txt) §A,
[`../calc/force_loop.out.txt`](../calc/force_loop.out.txt),
[`../calc/stroke_model.out.txt`](../calc/stroke_model.out.txt),
[`../calc/final_w3.out.txt`](../calc/final_w3.out.txt) §7 [calc final §n].
**[Prime]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28.
Branches: [`f2b-arbor-press-with-a-hard-stop.md`](f2b-arbor-press-with-a-hard-stop.md),
[`f2c-applicator-station-makes-t4-ends.md`](f2c-applicator-station-makes-t4-ends.md).

## Picture it

The industry already packages "place the metal bit on the end of the cable,
hold both in something that crimps, and crimp" into one ~4–6 kg module: the
**side-feed applicator**. It needs only a vertical ram stroke of 30 or 40 mm to
a fixed shut height. This idea buys that module and builds the one thing it
needs, a press. The press runs slowly.

- **Frame.** A steel C-frame of two bolted 12.7 mm plates with a base plate.
  The applicator clamps to the base.
- **Drive.** Above it, a crankshaft in its own two bearings carries an
  eccentric. A link runs from the eccentric to a ram, and the ram's T-slot
  grips the collar on the applicator's shank.
- **Motor.** The NEMA 23 + 30:1 self-locking worm gearbox turns the crankshaft
  at about 2 rpm, and slower near the bottom. It is the kind already driving
  the weld-rotator [repo: tools.md]; the gearbox is a new part.
- **Contacts.** They start on a strip reel beside the applicator. At rest, the
  applicator's pre-feed leaves the lead contact sitting on its anvil, open
  side up, waiting for a wire.
  - The **feed finger** advances the strip one pitch per stroke, off a cam on
    the applicator's own ram.
  - **Guide plates** stop the strip moving front to back.
  - A **pressure plate** stops it sliding back [mfr: JST MKS-L manual
    §6-6…6-9].
  - The **crimpers** form the conductor and insulation barrels in one stroke.
  - A **shear** cuts the tab.
  - Two **dials** set conductor and insulation crimp height. On JST's MKS-L
    the conductor dial moves about 0.05 mm per graduation [mfr: MKS-L §5].
- **Ribbon.** The ribbon, already split and stripped, is clamped in a small
  X/Y/Z carriage in front of the applicator. A printed fork holds conductor i
  just behind its strip. The carriage moves it over the anvil, forward until
  the strip end is where the barrels want it, and down into the open U. It
  comes in from above and behind, the way a person lays a wire into a bench
  press.
- **Stroke.** One crank revolution crimps, cuts off and feeds the next
  contact. The applicator's wire-hold spring and stripper keep the conductor
  in place as the crimpers descend [mfr: MKS-L §6-12].
- **Release.** The carriage lifts the crimped conductor out and indexes to
  the next.
- **How it knows.**
  - A load cell under the applicator's base, or a strain gauge on the frame,
    gives force.
  - A magnetic angle sensor on the crankshaft gives ram height. That yields a
    force–position curve for every crimp.
  - The ELP camera looks at the open barrel before the stroke and at the
    finished crimp after it.
  - The applicator's strip and anvil are grounded. With the ribbon's far end
    in a pogo block (ribbon-as-pallet a6) or on a reel's slip ring
    (procedure-is-the-machine p3/p6), a conductor laid into the pre-fed contact
    reads closed, which names the conductor in the applicator before each
    stroke.
- **What locates what.** Fixed is the applicator's anvil. The applicator's
  feed, guide plates and pressure plate place the contact; the carriage places
  the conductor; the crank's bottom dead centre and the dials set crimp height.
- **The person.** Loads the split, stripped ribbon into the carriage, loads a
  strip reel every thousand-odd crimps, and inserts the crimped contacts.
- **Without the motor.** A handwheel on the worm's input turns the same crank,
  30 turns a stroke: the applicator in its press is usable by hand the week it
  is built, and the NEMA 23 goes on later.

## What drives the crimp and carries the force

- **Force loop.** Frame, crankshaft bearings, link, ram, applicator ram,
  crimp, anvil, applicator base, frame base.
- **Crank torque.** Across the whole modelled force family, the crimp needs
  **1.2–2.5 N·m** at the crank. Adding 150 N of applicator springs and feed
  load over the stroke raises the peak to **~3.3 N·m** (40 mm stroke,
  cut-off included) [calc: drives §A].
  - The torque peaks either a few degrees before bottom dead centre (BDC),
    where force is high but the crank has almost no leverage, or around 77°,
    where the spring load meets the crank's full lever.
  - The NEMA 23 + 30:1 worm is rated 20 N·m at the output [source:
    StepperOnline 23HS30-2804S-RVS30-G30, C$76.69, 200 in stock, ships in
    24 h, 65 % efficiency, ≤1° backlash, 2026-09-28]. That is about 6×
    margin.
- **Why a crank.** Its bottom is geometric. One degree of crank error at
  BDC moves the ram 3–4 µm (30–40 mm stroke) [calc: drives §A]. Step loss,
  worm backlash and motor speed all drop out of crimp height. What is left is
  frame stretch, and a steel frame stretches microns [calc: force_loop §1].
- **Slowness changes nothing bad.**
  - Flow stress is ~5–7 % lower than at production speed [source: CuFe2P
    strain-rate study].
  - There is no ram or flywheel momentum at BDC, so bottom is set by statics
    alone [estimate].
  - JST notes that its applicator's speed in a bench press "is dependent upon
    the skill level of the operator" [mfr: MKS-L §2]. Applicators are indifferent to
    speed.

## References and tolerances

- **Fixed reference.** The applicator's anvil, which carries the contact.
  JST presets the die block and side block that position the anvils, and
  says not to move them [mfr: MKS-L §6-3].
- **Contact to anvil.** Set by the applicator: feed pitch, feed position and
  bellmouth are screw adjustments [mfr: MKS-L §6-8…6-11]. The bellmouth
  reference is one stock thickness, about 0.2 mm.
- **Shut height.** It must match the applicator. The mini-applicator
  standard is 135.78 mm with a 30 or 40 mm stroke (OTP and most makers)
  [source: prior-art §3; <https://www.crimpapplicator.com/product/140.html>: 135.78 mm, 40 mm stroke, 4 kg]. JST's own MKS-L wants 160 mm
  [mfr: MKS-L §2]. JST warns never to adjust crimp height with the press's
  shut height, only with the dials [mfr: MKS-L §5]. So the press needs a
  shut-height adjustment that is set once and locked: a fine thread in the
  ram with a lock nut.
- **Conductor to contact.** Set by the carriage: axial ±0.2–0.3 mm, lateral
  ±0.3 mm into the U [calc: placement_budget].
- **Where precision is needed.**
  - At loading: the carriage laying the conductor.
  - At the first die touch: the applicator's own guides.
  - At the bottom: the crank's geometry and the frame's stiffness.
  - At release: the applicator's stripper.

## Printed and bought

| Part | Printed or bought | Evidence |
|---|---|---|
| OTP side-feed applicator for "XH2.54" | bought | eBay: $160.07 for one, $150.47 each for three. Alibaba: $250 for 1–4, $200 for 5+ [source: web search 2026-09-28]. Prior-art saw ~$155 + $91 shipping on eBay. [Prime: OTP side-feed applicator, no listing found] |
| NEMA 23 + 30:1 worm | bought | StepperOnline 23HS30-2804S-RVS30-G30, see above. [Prime: Heechoo worm-gear NEMA 23, 30:1, $120.00, thin; output torque and self-locking not stated]. [Prime: CNCTOPBAOS NMRV030-40 reducer, 40:1, $38.99, thin; its 11 mm input bore needs a sleeve for a NEMA 23 shaft]. The DM542T driver and 24 V supply are the rotator's kind [repo: tools.md] |
| C-frame plates, base, ram block | bought, cut to a drawing | SendCutSend cuts A36 mild steel up to 0.500 in [source: sendcutsend.com] |
| Crankshaft, two pillow blocks, link bearing, pins | bought | [Prime: XIKE UCP204 pillow blocks, 20 mm, 2 pack, $26.99, 234 ratings; load rating not read] |
| Ram guide | bought | [Prime: 2 × HGR15 400 mm rails with 4 HGH15CA carriages, $48.99; preload class not stated] |
| Button load cell + HX711, or a frame strain gauge | bought | [Prime: 500 kg button load cell, $74.99, thin]; no 1 t button surfaced. 500 kg (4.9 kN) covers the 3 kN design force |
| Magnetic angle sensor on the crankshaft | bought | [Prime: UMLIFE AS5600, 3 boards, $7.99]; 12-bit resolves ~2 µm of ram near BDC [calc: 0.088° × 0.021 mm/° at 0.05 mm above BDC] |
| Contacts on strip | bought | Digi-Key SXH-001T-P0.6 in 1,000-piece strip, $0.0401 each; clone CJT A2501-TP on reel at LCSC, 665,523 in stock at $0.0079 [source: xh-facts §6] |
| Ribbon carriage, fork, strip-reel holder, guards | printed plus printer-class steppers | — |

## What was tried against it, and the repairs

1. **The gearbox cannot carry the crimp.**
   - *Conflict.* A crank on the worm gearbox's output shaft puts the full
     2.5–3 kN crimp reaction on the gearbox's output bearings. An NMRV030 is
     not built for that radial load [assumption: catalogue radial ratings for
     this size are around 1 kN].
   - *Repair.* The crankshaft runs in its own two pillow blocks on the frame.
     The gearbox's hollow output only turns it, held by a torque arm. The
     same applies to the link's big-end bearing: a 6002-size ball bearing's
     static rating (~2.8 kN) is marginal at the peak, so use a 6004 or a
     bronze bushing, which is ideal at 2 rpm [estimate].
2. **Frame stretch.**
   - *Conflict.* A crank sets ram position, so frame stretch at peak force
     lowers compaction.
   - *Repair.* Keep the force loop steel. Scatter from crimp-to-crimp force
     variation is then under a micron for the frame [calc: force_loop §2],
     and the applicator's dial takes up the constant offset.
   - *Unchanged by the repair.* The die blades' own compression, 50–80 µm at
     peak, is the same in any press. The dial calibrates it out.
3. **Will a "XH2.54" OTP applicator fit genuine JST strip?**
   - *Conflict.* The applicator is tooled for one terminal's strip: carrier
     pitch, pilot features, barrel widths. A Chinese "XH2.54" applicator is
     most likely tooled for a clone XH contact [assumption].
   - *Repair A.* Buy the matching clone strip (the CJT or HDGC reels at LCSC
     are cents apiece).
   - *Repair B.* Adjust the feed pitch and position, which are screw
     adjustments, for genuine SXH.
   - *Still open.* The crimp profile and width belong to the applicator and
     are not adjustable. Whether they give JST's crimp on this ribbon is
     unknown.
4. **Laying a floppy conductor into the waiting contact.**
   - *Conflict.* The conductor must drop into a U of 1.3–1.5 mm inner width
     with all 60 strands below wing tips 1.55 mm tall.
   - *Repair.* The fork holds the insulation 3–5 mm behind the insulation
     barrel, and the strands are twisted at stripping. The carriage lowers
     straight down into the U. The camera looks along the U before the
     stroke, and on a miss the carriage lifts and retries.
   - *Still open.* Whether the wire-hold spring on the crimper holds a
     1.7 mm silicone conductor without pulling it out of position as the ram
     comes down.
5. **Other conductors in the way.**
   - *Conflict.* The applicator's front is open, but the crimpers and
     stripper are ~10–20 mm wide [estimate]. Neighbours at ribbon pitch would
     be under them.
   - *Repair.* The fork bends the neighbours up and back. This is the
     JCW-2TE's "wire fork" [source: prior-art Start here].
   - *How the fork gets between them.* A split ribbon's OD equals its pitch
     (1.7 ±0.1 on 1.7), so neighbouring conductors touch: the gap is −0.1 to
     +0.1 mm [change-the-question on f2]. A tine cannot come down between them
     at the root. Either the tines enter at the free tips and slide rootward,
     wedging the conductors apart, or the split has already put alternate
     conductors in two planes 3.4 mm apart (change-the-question c1), and tines
     up to ~1.5 mm wide drop straight into the 1.7 mm gaps. The other plane,
     folded down and back under the clamp nose, lies below the anvil and out of
     the ram's path. borrowed-machines b1's 180° fold-back parking is the same
     answer taken further.
   - *Where the fold happens.* Each fold of a parked plane levers on the web
     at the clamp's face. The clamp face must be exactly the split root
     (ribbon-as-pallet a7's tear stop, or a3's backshell face), or the folds
     peel the web further back.
6. **What the curve can and cannot see.**
   - It sees:
     - a missing conductor, where compaction starts ~0.26 mm later [calc:
       metrology §3];
     - insulation under the conductor barrel;
     - a missing contact;
     - a contact that fed high or rolled.
   - It does not see one missing strand of 60, about 0.8 % of the force
     [calc: metrology §3, from prior-art's industrial figures].
   - Crimp height is measured on samples with a micrometer, or by re-touching
     at low force with an indicator on the applicator ram (f3's method), since
     the crank can stop anywhere.

7. **Setting the two dials.**
   - *Conductor dial.* On JST's MKS-L it moves ~0.05 mm per graduation
     [mfr: MKS-L §5]. The target comes from a genuine JST factory crimp on
     22 AWG (ASXHSXH22K305, $0.90) after correcting for its copper area:
     0.02–0.07 mm, about one graduation [change-the-question calc off §6].
     Compaction goes with crimp width × height, so the target is taken at the
     applicator's own crimp width, measured on a section: 1.20–1.32 mm² ÷ W,
     e.g. 0.80–0.88 mm at 1.50 mm wide, 0.69–0.75 mm at a clone-style 1.75
     [calc final §7]. Sectioning an OTP crimp beside the JST lead also says
     which contact the OTP profile was cut for.
   - *Insulation dial.* Applicators set conductor and insulation heights on
     separate wedges (an OTP-standard applicator states a "CH/IH wedge type
     height adjusting system with the precision of 0.02 mm and the range of
     2.0 mm" [source: crimpapplicator.com KS-EM40R, 2026-09-28]). That is
     what this wire needs: on 1.7 mm silicone the insulation crimp has a
     window about 0.2–0.4 mm tall between cutting the jacket and overfilling
     the cavity, higher than a PVC-wire setting such as the clone spec's
     1.80 mm ([`f6`](f6-two-blades-two-drives.md) [calc: wave2 §5]). The IH
     wedge is where it is set; bend-and-look on sample crimps is how.
8. **The applicator's spare blades are the die source for other ideas.** The
   conductor and insulation crimpers and anvils of an XH applicator are sold as
   "knife sets" [source: terminal-supply, listing titles]. They are the steel
   f3, f4 and f6 need ([`f7`](f7-where-the-steel-comes-from.md)).

## Branch: an output pallet, a real-wafer test and a spool

[`f2c-applicator-station-makes-t4-ends.md`](f2c-applicator-station-makes-t4-ends.md)
adds one pocketed output pallet at housing pitch, filled in cavity order, a
single push, a wafer test and a spool feed (change-the-question c1 and c5). A
single-conductor station can deliver crimped contacts in cavity order rather
than ribbon order, which no gang can do. procedure-is-the-machine's p7 (two
blades across the whole webbed end at the clamp) is the stripper it lacks.

## Contribution

- **The industrial "place the contact" mechanism, for ~$160–250.** It
  already solves feed, location, cut-off and crimp-height adjustment. The
  press it needs is small: under 4 N·m at a crank turning slowly [calc].
- **Crank BDC as a free precision source.** Micron-level bottom from a
  hobby stepper through a backlashy worm.
- **Anyone making the strip-fed step** can reuse the pre-feed idea: at rest,
  the next contact is already waiting on the anvil.
- **Motorless first build:** a handwheel on the worm turns the same crank.

## How it connects to the whole procedure

| Step | Who does it |
|---|---|
| Cut, splay, strip | before; the person, or other explorers' machines |
| Place the contact | **automated** (applicator feed) |
| Present the conductor | **automated** (carriage + fork) |
| Crimp | **automated** |
| Cut-off | **automated** |
| Insert | after; the person, or an insertion station fed with loose crimped conductors |

J2's empty cavity 3 and J7's trimmed conductor are just skipped conductors:
the carriage indexes past them. Per unit: 53 revolutions at ~30 s plus
carriage moves, about an hour unattended once the ribbon ends are loaded
[estimate].

## Major unresolved problems

- **Applicator match to contact.** Which terminal the OTP "XH2.54"
  applicator is tooled for, and whether its crimp suits 22 AWG silicone at
  1.7 mm OD.
- **Frame build.** A steel frame with a crank, bearings and a guided ram is
  real metalwork. It has a few precise interfaces (ram to shank coupling,
  shut-height lock) that Derek would make or buy. The drill press and
  SendCutSend cover most of it [assumption].
- **Wire-hold behaviour** on silicone.
- **The neighbours' folds** at the clamp face, if the ribbon is split into
  planes for the fork.
- **The insulation setting on silicone.** The IH wedge can reach the window;
  where the window is has to be found on this wire (bend-and-look, cavity fit).
- **Force sensing.** Whether a load cell under the base can be arranged
  without the base rocking, or a frame strain gauge is the simpler sensor.
  At a 60 mm-deep plate section the strain is ~65 µε at 2.5 kN, which an
  HX711 reads at ~1 % [estimate].

## Which conclusions rest on assumptions

- **Crank torque** rests on the modelled force family and on the assumed
  150 N of applicator spring and feed load.
- **Gearbox radial rating** is an assumption, not a read catalogue value.
- **That a slow stroke suits the applicator's feed cam and stripper** rests on
  JST's own note that bench speed is set by the operator.
