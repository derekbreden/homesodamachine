# b8b — The flat spool line over a crown: nothing folds, the fresh contacts fall out of the ribbon's plane

**A branch of [b8](b8-spool-fed-borrowed-line.md) and a combination** with
terminal-supply's
[a2d, skip-pitch strip over a crowned anvil](../../terminal-supply/ideas/a2d-skip-pitch-crown.md)
(itself a branch of their
[a2, knife-set strip indexer](../../terminal-supply/ideas/a2-strip-indexer.md)).
terminal-supply proposed the pairing.

**What each side brings.**
- **b8** brings the spool as the carrier, with test through its inner end on
  a slip ring; the belt feed whose retraction drives the needle rip, so the
  split root lands on the work clamp's face by geometry; the whole-tip strip
  while the tip is still webbed; the gang push of a housing from a tube; and
  the cut last, so a redo costs spool, not a loom.
- **a2d** brings a strip with every other contact punched out before the
  station; a steel crown block (R 25–30 mm) whose crest land is a knife-set
  anvil, so the next kept contact lies 14.2 mm away and below the plane the
  conductors lie in; tapered pins in the removed contacts' pilot holes; a
  fence set from a picture of each waiting contact; a one-sided drop-shear; a
  level gate view across the station to a fixed backlight; and a bad contact
  sheared off with no wire in it.

**What changes from b8.** The applicator in the shop press goes. Its feed
track holds fresh contacts at strip pitch in the tooling plane, which is why b8
folds every conductor but one back over the clamp face. Over a crown the ribbon
lies flat through the whole cycle: nothing folds, nothing swings 180°, and each
conductor's root is bent once, toward the housing's own fan.

Sketch: [`../sketches/b8b-flat-spool-line.svg`](../sketches/b8b-flat-spool-line.svg)
(plan and a section across the crown, schematic).
Labels used here:
- [calc wave3 §n], [calc wave2 §n]: this explorer's
  [`wave3.out.txt`](../calc/wave3.out.txt) and [`wave2.out.txt`](../calc/wave2.out.txt).
- [TS §n]: terminal-supply's
  [`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt);
  [TS wave2 §n]: their [`wave2.out.txt`](../../terminal-supply/calc/wave2.out.txt).
- [Prime]: a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
  observed 2026-09-28.
- [facts]: [`../../../context/xh-facts.md`](../../../context/xh-facts.md);
  [digest]: [`../../../context/digest-wave1.md`](../../../context/digest-wave1.md).

## Picture it

**Where things start.**
- **The ribbon.** A 4P spool sits on an axle behind the machine. Its inner
  end is in a spare XH housing plugged into a socket on the axle and wired
  through a 6-circuit capsule slip ring ($9.99 [Prime]) to the controller, so
  every conductor of the spool is a test lead. The free end is threaded through
  the **feed head**: a belt feed with an encoder wheel (a 600 P/R encoder,
  $18.99 [Prime]), a guillotine, a needle bar and a work clamp. The head rides a
  small X/Y stage: MGN12 rails ($20.49 [Prime]) and NEMA 17 steppers on Tr8×2
  screws ($27.99 [Prime]).
- **The contacts.** A reel of SXH-001T-P0.6 (Digi-Key 455-1135TR-ND, 1,329,000
  in stock, $0.0235 at 8k [facts §6]) or a clone reel (LCSC CJT A2501-TP,
  $0.0079 [facts §6]) hangs below the bench. The strip rises vertically to the
  crown block. On the rising run a servo punch cuts the tab of every other
  contact against a steel edge under the contact's floor (48–158 N [facts C1],
  a DS3218 servo, $14.99 [Prime], on a 3–4:1 lever); the freed contacts fall into
  a thinning cup.
- **The crown block.** Steel, its top a cylinder of radius 25–30 mm whose axis
  runs along the wire (X). The strip wraps over it along Y. At the crest sits a
  flat land about 3 mm wide, the knife-set anvil, under the barrels. Two
  tapered pins come out of the crown into the pilot holes of the removed
  contacts at ±7.1 mm, their tips flush with the carrier. A fence on a stepper
  sets the strip along the contact's axis. Downstream of the station tab the
  crest is a drop plate.
- **The press.** A 1-ton arbor press, the VEVOR AP-1 ($61.90, 150 mm opening,
  81 mm throat [Prime]), turned so its column stands on the box side of the
  station. A NEMA 17 on a Tr8×2 screw pulls its lever (as in a2). The punch
  holder carries an OTP "XH2.54" knife-set punch and lands on a hard stop on the
  crown block, with disc springs above it for overtravel. The crown block stands
  on a steel pedestal so the strip arrives and leaves on tangents clear of the
  press's 90 mm plate.

**One T4 end** (4P into XHP-4).
1. **Feed out.** The clamp is open. The belts push the square end until its tip
   is S + Ls past the needle bar. S is the split length, 16 mm here (below), and
   Ls the strip length for the reel in use (2.4 mm for genuine JST, 1.85–2.1 mm
   for clone contacts [TS §3]).
2. **Pierce.** The needle bar comes down; each floating needle finds its valley
   and goes through its web, S ahead of the clamp face
   ([b6](b6-pierce-at-the-root-pull-to-the-tip.md)).
3. **Rip.** The belts retract the ribbon by S while the needles stay put. The
   needles travel through the webs toward the tip and stop Ls from it. The
   pierce point, which is the split root, now sits on the clamp face. The clamp
   closes. A 4P's three webs need 9–45 N; two belts on a 20–60 N nip give
   32–180 N [calc wave2 §2, §4].
4. **Strip.** Two flat blades close on the crowns at the strip line, top and
   bottom, to a stop set for **50–60 % of the wall**, or riding a shoe on the
   jacket's top. TPU pads pinch the still-webbed tip and the head backs off
   3 mm. The whole tip leaves as one comb-shaped slug. The pull is 4.7–13 N a
   conductor, or 19–52 N for a 4P, carried by the clamp [calc wave3 §8]. A
   backlit frame checks the four stubs.
5. **Spread.** A comb carried on the head drops in **front of the stripped
   tips** and slides back toward the clamp face.
   - Its tines first pass between the stripped bundles, which are ~1.0 mm
     apart, then wedge between the split jackets, which touch.
   - Its slots fan from 1.7 mm at its rear end to the crimp pitch *p* over a
     4 mm section, then run parallel at *p* for ~2 mm. The outermost 4P
     conductor moves 1.2 mm at a slot angle of ~17° [calc wave3 §7].
   - It stops with its rear end just ahead of the clamp face and stays there
     through the crimps. The conductors leave its front end parallel, at *p*.
6. **Present.** The stage carries the flat, spread end into the crest plane.
   Conductor *k* slides forward over the carrier into the waiting contact's
   open U.
   - The neighbours lie in the same plane at ±*p*, over the crown's flanks,
     0.09–0.16 mm below the crest [TS §5].
   - The next kept contact is 14.2 mm away, rotated 32°, its wing tips 1.2 mm
     below the plane [TS wave2 §2].
   - The stage steers X by the insulation edge in the picture, 0.7 of the
     error per look (a2).
7. **Gate.**
   - **Picture:** a2d's level view at wing height across the station to a
     fixed backlight beyond the ribbon's span: contact present, insulation edge
     in the window, no strand above a wing tip.
   - **Continuity:** from the spool's inner end, through conductor *k*, to the
     grounded crown block. It names the conductor and shows its strands touch
     the contact.
8. **Stroke.** The stepper pulls the lever until the punch holder lands on its
   stop; the force trace is logged. The drop plate sinks 0.3–0.5 mm and shears
   the tab against the crown's own edge. The bend it leaves in the carrier lies
   11–12 mm downstream of the next station tab, in scrap [TS wave2 §9].
9. **Proof pull.** The punch lifts. A thin steel fork drops into the neck
   behind the box: behind the box the crimped conductor barrel is ~1.5 mm wide
   and ≤1.1 mm tall. The stage pulls conductor *k* back 20 N against the fork. It
   bears on the box's rear face, above the floor and clear of the lance [TS
   §11]. A picture follows.
10. **Index.** The stage draws the whole ribbon back behind the contacts' rear
    edge, because a kept contact's wings sweep through the crest plane as it
    rides up the crown. The pins retract, a sprocket advances the strip two
    pitches, the pins return, and the camera measures the new waiting contact
    **alone** and sets the fence. A contact that fails the look is sheared with
    no wire in it and swept into a reject cup. The stage steps *p* in Y.
11. **After four.** The stage carries the crimped row, still at *p*, to a housing
    nest beside the crown.
    - With *p* = 2.5 mm the row is already at housing pitch. Otherwise a
      converging comb takes it to 2.5 mm, moving the outermost 4P contact
      0–0.45 mm [TS §5].
    - An XHP-4 from a tube is pushed onto all four contacts at once through a
      load cell (a bar cell with HX711, $9.99 [Prime]). Each contact is pulled
      back ~5 N.
12. **Test, feed out, cut.** Pogo pins on the housing's mating face; each
    conductor in turn from the spool's inner end: opens, adjacent shorts,
    swaps. The clamp opens, the belts feed out the loom's length down a drop
    tube, and the guillotine cut squares the next end.

**What locates what; the reference for "fixed."** Two references, one for each
supply, and the camera ties them together.

| What | Set by | Reference |
|---|---|---|
| Contact on the anvil | crest land; pins in the removed contacts' holes at ±7.1 mm; fence moved by each contact's own picture | crown block |
| Ribbon | work clamp; the root placed on its face by the needle bar's distance S from it | feed head on the X/Y stage |
| Conductor *k*, lateral | stage Y, into the open U | crown block, through camera fiducials on it |
| Conductor *k*, axial | insulation edge steered into the window in the picture | crown block |
| Crimp height | hard stop between the punch holder and the crown block; optionally on a stepper wedge | crown block |
| Contact fronts at the housing | the strip line was scored while the ribbon was flat, so every contact sits the same along-conductor distance from the root | housing nest |

**Lateral capture depends on the contact.** The open insulation wings give the
insulation ±0.21–0.83 mm per side on clone contacts, ±0.25–0.35 mm on the Würth
analog, and ±0.08–0.18 mm if JST's 1.95 mm catalog envelope is the open width
[TS §4]. With clone reels the stage's Y is enough. With genuine JST, a V-fork on
the punch holder's rear face that closes on the insulation just behind the
carrier line (the V-fork of [b3](b3-gantry-carries-the-crimp-head.md)) puts the
conductor on the crimp axis mechanically, and the picture is needed only for
the axial position. Whether a V fits between the carrier line and the comb is
open.

**What drives the crimp and carries its force.**
- The arbor press is rated 1 t, ~9.8 kN, against a 3 kN design crimp
  [digest].
- The force loop is punch holder → stop → crown block → pedestal. The press
  casting only pushes; the crimp height is the stop's (a2).
- A stepper wedge under the stop, 2–3° and self-locking under 3 kN, moves the
  anvil 35–52 µm per mm of wedge travel [TS wave2 §8]. The machine can sweep
  crimp height on the production die in 0.02 mm steps and then hold it; genuine
  and clone contacts become two stored wedge positions.

**How it knows it worked.**
- Pins home; the waiting contact's picture, taken alone.
- The level gate picture and continuity through the spool, before the stroke.
- The stop switch and the force trace through the stroke.
- The proof pull on the neck fork, and the after-picture.
- The insertion trace and each pull-back; the test through the spool.
- All of it logged against the unit, loom and conductor.

**What the person does.**
- Loads and threads a spool: ~5 min per spool, about one per 5–7 units of T4
  (b8).
- Mounts the contact reel once. At skip-2, all T4 over the program uses 2,400
  strip contacts, 0.30 of an 8,000 reel [TS §5].
- Keeps the housing tube full.
- Empties three cups (thinning, reject, carrier scrap) and the loom bin.
- Labels the looms and makes every far end.

## Steps it covers and what it hands back

- **Covers, for T4 ends:** cut to length (last), split (the needle rip driven
  by the feed), strip (the whole-tip slug), supply contacts (reel and
  thinning), place the contact on the conductor, crimp, verify the crimp,
  insert (gang push), verify insertion and pin order (the test through the
  spool). That is 20 of a unit's 53 crimps and 5 of its 10 housings.
- **Hands back:** far ends; labels; every non-T4 loom. J6 (5P into XHP-5, also
  straight) is the next spool type. The pairs (J1, J2, J4, J7) and the J4/J7
  crossings are not made.
- **The thinning cup feeds a hand station.** Skip-2 over the T4 program drops
  1,200 loose contacts into the cup, 61 % of the other looms' 1,980 crimps, with
  the same contact [TS §5]. A hand station making the rest
  ([b2b](b2b-pedal-less-hand-station.md) stage 1, or terminal-supply's
  [x1 post pen](../../terminal-supply/ideas/x1-post-feeds-the-hand-tool.md))
  then crimps the same contact the line was qualified on.

## The split length and the spreading comb

**Why the comb enters from the tips.** A comb whose slots run from 1.7 mm at
the root to *p* at the strip line cannot be started at the clamp face: its
start position is inside the clamp. Dropped from above in its final place, its
*p*-pitch front lands on conductors that are still at 1.7 mm. Before the strip
the tip is still webbed, so nothing can be threaded from the front. After the
strip the tips are free, 0.72 mm bundles about 1.0 mm apart. A comb brought in
from the front can thread them, and its tines then only have to follow the split
lines already made by the rip.

**Where it sits.** The comb must stay behind the carrier zone. From the strip
line back toward the root lie:
- the rest of the window, 0.3–0.5 mm;
- the insulation barrel, 0.8–1.5 mm;
- the tab, 0.7–1.15 mm;
- the carrier, 2.5–4 mm [estimate, unmeasured];
- clearance to the crown block's rear edge, 1–2 mm [estimate].

That is **5.3–9.2 mm**. With a 4–6 mm comb behind it the split is at least
**9.3–15.2 mm** [calc wave3 §7]. The comb's fins reach below the conductors'
mid-plane, which is why they must be clear of the carrier and the crown.

**S = 16 mm here** [estimate]. It covers the comb and the carrier zone, and it
puts the fronts in the housing close together. Every contact sits the same
along-conductor distance from the root, so in the housing the outermost front
lands short only by the housing fan's own amount [calc wave3 §7]:

| End | 12 mm free | 15 mm | 20 mm |
|---|---:|---:|---:|
| 4P | 0.06 | 0.05 | 0.04 |
| 5P | 0.11 | 0.09 | 0.06 |
| J4 (4P+3P) | 0.24 | 0.19 | 0.14 |
| J1 (5P+4P) | 0.42 | 0.34 | 0.25 |

A gang window is ~±0.3 mm [digest]. J1 needs about 20 mm of free length. How
much split behind the housing is acceptable on a finished loom is Derek's
split-length question.

**The pitch *p*** is set by the knife-set punch.
- If the punch holder clears the conductors, *p* ≥ punch half-width +
  neighbour half-width + 0.3 mm. That gives **2.35–2.80 mm** for a 2.4–3.0 mm
  punch [TS §5, punch width an estimate].
- The crimped neighbours' boxes stand 2.2–2.4 mm tall [facts §1], taller than
  the 1.7 mm conductors. They sit in the same X band as the station contact's
  own box, so a holder that clears its own contact's box clears theirs.
- If the holder does not clear, *p* is 4–6 mm (a2d's rule). The fronts still
  hold by the table above, but the comb moves the outermost 4P conductor
  2.3–5.3 mm and the converging comb has that much to undo.

**The parting pair, an alternative for the crimp only.** Two 0.25 mm blades drop
into the valleys either side of conductor *k* and move apart, each pushing its
whole side out by *p* − 1.7 = 0.65–1.1 mm. Each conductor needs only 50–85 mN
to set at the root [calc wave3 §7]. It leaves the crimped contacts at 1.7–2.0 mm
pitch with boxes 1.85–1.95 mm wide [facts §1], crowded, and the row then needs
spreading before a housing goes on. The comb leaves the row at *p*.

## Variants within the idea

- **One shaft for the contact side** (a pairing terminal-supply proposed, on this explorer's
  [b1c](b1c-one-shaft-applicator-press.md) principle). The thinning punch, the
  pin lever, the two-pitch sprocket advance, the drop plate and the press
  stroke go on cams on one shaft, timed the way an applicator times its feed.
  The ribbon side stays on steppers, because it steers by the picture.
- **The applicator's own body as the guided die holder.** The OTP applicator
  already keeps its crimpers aligned over its anvil. With its feed finger and
  track removed (as in ribbon-as-pallet a2e), a crown built around its anvil
  would remove a2's open problem of guiding a loose knife set. It needs ~15 mm of
  room below the anvil top over ±30 mm for the crown's fall [estimate]. A
  Revopoint scan of the applicator, or the [b1b](b1b-applicator-in-slow-crank-press.md)
  jack test, shows whether the base leaves it.
- **Two spools edge to edge** (procedure-is-the-machine p3b) put J1's nine
  conductors through the same crest, since the crown takes any width flat. At
  *p* = 2.5 mm the outermost of nine moves 3.2 mm, which wants a ~6 mm fan
  section or two comb passes [calc wave3 §7].

## Motorless first build

The crown block, a knife set and the AP-1 pulled by hand make a working
crimper before any spool line exists. The ribbon end is split on b6's hand rip
board, stripped by hand, spread by a hand comb and laid on the crest by hand.
Continuity LEDs on a pogo block at the far end show which conductor touches the
crown. It is a2d at its first stage, and the crown, anvil, stop and wedge carry
straight into the line.

## Contribution

- Nothing folds. Each root is bent once, toward the housing's fan. In b8 each
  conductor goes forward and back over the clamp face about four times, and a
  residual kink of 5–15° shortens a front by 0.05–0.41 mm, differently on each
  conductor [TS §10]. That kink does not arise here.
- The strip line is cut while the ribbon is flat and one piece, so the crimp
  pitch drops out of the fronts at the housing.
- One reel supplies two stations: the line from the strip, a hand station from
  the thinning cup, one contact type.
- Time: ~10.6 min per T4 end, ~53 min for a unit's five, unattended [TS §5,
  estimates].

## Major unresolved problems

- **The die.** A knife set outside its applicator needs a guided holder that
  keeps punch over anvil to a few hundredths of a millimetre: a2's open problem.
  The knife set comes only from eBay or AliExpress; no Prime listing ("OTP XH
  crimper and anvil blade set: no Prime listing found" [Prime]).
- **The pitch *p*** rests on the punch's outer width and how far it stands
  out of its holder. It is read off the knife set when it arrives.
- **The comb.** Whether its tines wedge between split jackets without scuffing
  them. Whether 5.3–9.2 mm is really the carrier zone, which sets how far back
  the comb must sit and so the split.
- **The neck** (repo Open item 5): whether the rip follows it; and the
  whole-tip slug's flank tear from crown scores (as in b6 and b8).
- **The spool's inner end**, or a rewind per spool; feeding floppy silicone
  ribbon out and back with belts (as in b8).
- **The carrier's pitch and temper**, which set the crown radius (a2d).
- **The tab stub** from a one-sided drop on a crown (a2's open question).
- **The press's column** on the box side, and the feed head approaching from
  the root side under an 81 mm throat: whether the stage, comb and V-fork fit.
- **J4 and J7 crossings**, and the pairs (J1, J2, J4, J7).

## What rests on what

- **Derek:** slowness is acceptable; placing, holding and crimping is the step
  he most wants automated; "the whole procedure automated would be ideal".
- **Facts** [facts]: contact dimensions from clone drawings; box 1.85–1.95 mm
  wide and 2.2–2.4 mm tall; tab shear 48–158 N; stock and prices; strip length
  2.4 mm (JST) against 1.6–2.1 mm (clone spec).
- **Calculations:** fronts, comb angles and split zones [calc wave3 §7]; strip
  pulls [calc wave3 §8]; rip and belt traction [calc wave2 §2, §4];
  terminal-supply's crown, pitch, supply, wedge and kink numbers [TS].
- **Estimates:** carrier width 2.5–4 mm; crown-block clearance 1–2 mm; S =
  16 mm; punch width 2.4–3.0 mm; times per end.
- **Assumptions:** the carrier pitch is 7.1 mm (the Würth analog); the OTP
  knife set fits a guided holder; the BNTECHGO spool's inner end is reachable.
