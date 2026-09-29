# a2d — Skip-pitch strip over a crowned anvil: the fresh contacts fall out of the ribbon's plane

Branch of [`a2-strip-indexer.md`](a2-strip-indexer.md). **What it changes:** a2
keeps every contact on the strip, and pays for it with a lifter bar that holds
the ribbon's other conductors above the fresh contacts and a vane that gives the
camera a backlight between two contacts 7.1 mm apart. a2d removes every other
contact from the strip before the station and runs the strip over a crowned
steel block. The next fresh contact then lies 14.2 mm away and below the plane
the conductors lie in. The whole ribbon lies flat at any fan pitch the punch
allows, the camera looks level across the station, and nothing lifts or swings.

Sketch: [`../sketches/a2d-skip-pitch-crown.svg`](../sketches/a2d-skip-pitch-crown.svg)
(to scale within the view: R 25 mm, pitch 7.1 mm, clone wing height).
Numbers: [`../calc/wave2.py`](../calc/wave2.py) §1, §2, §3, §7, §9, §11 [w2 §n];
[`../calc/w3.py`](../calc/w3.py) §5, §6 [w3 §n]; into-the-housing's
[`exchange_terminal_supply_w3`](../../into-the-housing/calc/exchange_terminal_supply_w3.out.txt)
calc [ith-w3 X]; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
calc [mtsl §n].

**Related.**
- [x2](x2-crown-then-sort.md) carries a2d's flat, crimped ribbon end straight
  into into-the-housing's sort-then-push
  ([i6](../../into-the-housing/ideas/i6-sort-then-push.md)), with
  [a6](a6-post-is-the-gripper.md)'s post head as the sorting hand.
- The spool-fed line (borrowed-machines
  [b8](../../borrowed-machines/ideas/b8-spool-fed-borrowed-line.md),
  procedure-is-the-machine [p3](../../procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md),
  ribbon-as-pallet [a4](../../ribbon-as-pallet/ideas/a4-spool-as-magazine.md))
  supplies exactly the flat end a2d takes; K1 in
  [terminal-supply on borrowed-machines](../../../exchange/terminal-supply--on--borrowed-machines-w3.md)
  puts the two together.
- The same crown is a strip feed for into-the-housing's
  [i2](../../into-the-housing/ideas/i2-crimp-in-the-cavity.md) strip branch (below).

## Picture it

- **Where things start.** A reel of SXH-001T-P0.6 (or a clone reel, or a
  Digi-Key cut strip) hangs below the bench. The strip rises toward a steel
  crown block, contacts pointing toward the front, barrels open away from the
  block.
- **Thinning.** On the rising run, a small servo punch cuts the tab of every
  other contact. The freed contact drops into a cup. The pilot holes stay,
  because they are in the carrier, not the contacts. The strip now carries a
  contact every 14.2 mm and a pilot hole every 7.1 mm [pitch from the Würth
  analog; unmeasured for SXH].
- **The crown.** The block's top is a cylinder of radius ~25 mm whose axis runs
  along the contacts. At its crest sits a flat land ~3 mm wide: the knife-set
  anvil, under the barrels. Downstream of the anvil, under the carrier, part of
  the crest is a drop plate. The strip wraps over the crown and leaves downward
  on the far side to a sprocket and a take-up spool. A light drag upstream keeps
  ~2 N of tension, and the wrap presses the carrier onto the crown: the tension
  is the hold-down.
- **What the crown does.** The contact at the crest sits flat on the anvil. The
  kept contact one step upstream, 14.2 mm of arc away, is rotated 32° and its
  open wing tips sit 1.2 mm below the crest plane [w2 §2]. Every contact further
  away is lower still. Downstream there are only tab stubs.
- **Locating.** Two tapered pins come radially out of the crown into the pilot
  holes at ±7.1 mm, the holes of removed contacts. Their tips stop flush with
  the carrier, 1.0 mm below the crest plane [w2 §2], so no conductor lying over
  them is touched. A fence on a small stepper behind the crown sets the strip's
  position along the contact's axis.
- **Measuring the waiting contact.** After each index, with the ribbon drawn
  back, the camera looks down on the station contact: conductor barrel's rear
  edge against two fiducials on the anvil, roll, wings, lance. The fence moves
  the strip by the axial error. A contact that fails is sheared with no wire
  present and swept into a reject cup.
- **Presenting the wire.** The splayed, stripped ribbon lies flat in the crest
  plane, fanned at the pitch the punch holder needs (2.5–2.8 mm for a
  2.5–3.0 mm blade, more if the holder is wide [w3 §5]), its web in a clamp on
  an X-Y carriage. The carriage slides conductor k forward over the carrier into
  the open U. Every other conductor lies in the same plane over the falling
  flanks of the crown, where no fresh contact reaches. The carriage steers by the
  insulation edge as seen, moving 0.7 of the error each round (as a2).
- **The look before the stroke.** The camera looks along the strip at wing
  height, level, across the station, to a lit backlight tile beyond the ribbon's
  span downstream, where the crown has fallen away 7–8 mm. Nothing stands in
  that line except the station contact: fresh contacts are below it, and the
  ribbon's conductors and crimped contacts lie at 0–2.4 mm, under the 2.7–3.6 mm
  band where a strand above a wing tip would show. The gate is a2's.
- **Crimping.** An OTP XH knife-set punch in a guided holder, driven by a 1-ton
  arbor press whose lever a stepper-driven lead screw pulls, lands on a hard stop
  on the crown block, with disc springs for overtravel. The crown block is the
  anvil block.
- **Severing.** While the punch holds the crimp, the drop plate sinks 0.3–0.5 mm
  on the downstream side. The crown just upstream of the plate's edge is the
  fixed shear edge, and the drop pulls the carrier toward the crown, so no clamp
  finger is needed. After the next 14.2 mm index the bend lies 11–12 mm
  downstream of the new station tab, in scrap [w2 §9].
- **Proof pull.** A slotted steel pull fork on a servo drops onto the crown land
  behind conductor k's crimped insulation barrel, straddling the wire. The
  carriage's Y pulls the whole web back at 20 N through its load cell while the
  camera watches k's insulation edge for slip. Only k is blocked by the fork;
  the other conductors' contacts are free and move with the web. 20 N on two
  0.4 mm tines is ~42 MPa on the fork and ~56 MPa on the barrel's rear edge
  [w3 §6]. This puts the proof pull before insertion, below the 39.2 N pull-out
  and above the 14.7–19.6 N retention range [w3 §9].
- **Leaving and indexing.** The fork lifts. The carriage lifts conductor k with
  its crimp and draws the whole ribbon back behind the contacts' rear edge. The
  pins retract, the sprocket advances two pitches, the pins return. A contact
  riding up the crown sweeps its wings through the crest plane, which is why the
  ribbon is drawn back during the index.
- **What the person does.** Mounts a reel (one 8,000-piece reel covers the whole
  program even with every other contact removed: 0.89 of it [w2 §7]); empties
  the thinning cup (loose contacts, kept as stock), the reject cup and the
  scrap; splays and strips, and inserts, unless other stations do.

## What locates what

| Direction | What sets it | Note |
|---|---|---|
| Along the strip | tapered radial pins in the removed contacts' holes at ±7.1 mm | flush tips, 1.0 mm below the crest plane |
| Along the contact | strip edge against a stepper fence behind the crown, set per contact from the picture | as a2 |
| Height | the anvil land at the crest | the carrier beside it follows the crown |
| Roll | the contact floor flat on the land; the carrier held to the crown by wrap tension | the tab is never bent before its crimp; the drop bends only scrap |
| The conductor | carriage steered by the insulation edge as seen | as a2 |
| Crimp height | hard stop between punch holder and crown block | as a2; the stop can ride a stepper wedge for a sweep |

**The reference for "fixed" is the crown block.** Pins, fence, camera
fiducials, anvil, stop and pull fork all mount to it.

## What drives and carries the crimp force

As a2: 0.8–2.6 kN [xh-facts §4] closes punch holder → stop → crown block; the
arbor press frame only pushes. The press is a 1 t arbor press: the VEVOR AP-1
(Prime, $61.90, 150 mm opening, 81 mm throat [sourcing/amazon-prime.md]) or
Harbor Freight 59766 ($79.99, 139.7 mm, 20:1 lever [source]). The 81 mm throat
bounds how far the crest may sit from the press column; the strip path and the
reel hang on the side away from the column. The proof pull (20 N) goes through
the pull fork into the crown block. The drop-shear (50–160 N) goes through the
drop plate's lever into the crown block.

## How it knows it worked

- Pins home.
- The waiting contact's picture (axial offset, roll, wings, lance).
- The level gate across the station.
- The stop switch and the force trace.
- The proof-pull trace: force rises to 20 N with the insulation edge still.
- The after-crimp picture.

## Why removing contacts is cheap here

- **Contacts are the cheapest thing in the machine.** At LCSC's $0.0100 each, the
  program's ~3,556 crimps from strip (3,233 plus 10 % spares) cost $36 with every
  contact used and $71 with every other one removed [w2 §7; prices xh-facts §6].
  At Digi-Key's reel price it is $84 against $167.
- **Nothing is wasted.** The removed contacts drop into a cup as loose contacts,
  about 3,500 over the program: hand repair, the loose routes
  ([a6](a6-post-is-the-gripper.md), [a4](a4-post-held-contacts.md),
  [x3](x3-stage-crimp-one-push.md)), or spares.
- **The pilot holes stay.** They belong to the carrier, so the pins still have a
  hole every 7.1 mm, and the holes beside the station are the removed contacts'.

## Why the crown, and when a flat strip is enough

With fresh contacts every 14.2 mm, a flat strip already lets a 5P lie flat at fan
pitches up to 2.9 mm and a 4P up to 3.9 mm with every other conductor on the
upstream side [w2 §1]. The punch holder needs 2.5–2.8 mm for a 2.5–3.0 mm blade
[w3 §5], so **a flat skip-2 strip without a crown already works for 4P and 5P
ends with a narrow blade**. The crown adds three things: a level view across the
station with a fixed backlight, the wrap tension as hold-down, and any width
(J1's 5P + 4P as one nine-conductor ribbon, where the outermost conductor is
28 mm out at 3.5 mm pitch and the crown has fallen far below the plane).

| Crown radius | Carrier strain | 7.1 mm neighbour's wing tips vs crest | 14.2 mm neighbour's wing tips vs crest |
|---:|---:|---:|---:|
| 8 mm | 1.25 % (plastic) | −0.9 mm | far below |
| 20 mm | 0.50 % (at yield) | +1.8 mm | −2.4 mm |
| 25 mm | 0.40 % (elastic) | +2.1 mm | −1.2 mm |
| 30 mm | 0.33 % (elastic) | +2.3 mm | −0.5 mm |

[w2 §2; C5191 yield strain 0.41–0.59 % from 450–650 MPa, estimate]

- **Every contact kept** would need a crown of ~8 mm radius, bending the carrier
  plastically at every contact that passes: the kink that rolls the next
  contact.
- **Every other contact kept** clears with an elastic crown of 25–30 mm.
- **Two of three removed** (21.3 mm) clears by 4.8–6.4 mm at the same radii, at
  1.33 reels for the program.

## The neighbours and the punch

The crown settles the fresh contacts. It does not settle the punch holder.
Conductors already crimped keep their contacts at the station's Y, at ±p. The
widest part there is the crimped box, 1.85–1.95 mm wide and 2.2–2.4 mm tall.

- **Width** [w3 §5]: p ≥ blade half-width + 0.98 + 0.3 mm. A 2.5–3.0 mm blade
  gives p ≥ 2.5–2.8 mm; against a waiting (uncrimped) conductor alone it would be
  0.13 mm less. A holder that does not clear needs p of 4–6 mm, as in
  borrowed-machines' punch-zone estimate.
- **Height** [w3 §5]: at the bottom of the stroke the holder must stay above the
  neighbours' box tops, so the conductor crimper stands ≥ 1.8–1.9 mm out of its
  holder and the insulation crimper ≥ 0.7–0.9 mm.
- **Both are read off the knife set** when it arrives, and the fan pitch follows.

## The fan stays in the loom

Crimping flat at fan pitch p leaves the conductors split back to where the fan
starts. At a 20° fan plus ~6 mm straight [w3 §5, ith-w3 H]:

| End | p 2.8 | p 3.0 | p 3.5 |
|---|---:|---:|---:|
| 3P | 9.0 mm | 9.6 mm | 10.9 mm |
| 4P | 10.5 mm | 11.4 mm | 13.4 mm |
| 5P | 12.0 mm | 13.1 mm | 15.9 mm |
| J4/J7 pair | 16.6 mm | 18.5 mm | 23.3 mm |
| J1, nine | 18.1 mm | 20.3 mm | 25.8 mm |

Insertion re-closes the fan to 2.5 mm at the housing (as x2 does), and the split
remains behind the housing. Whether 9–26 mm of split behind a housing is
acceptable on a finished loom is Derek's question.

## The line of sight

- **Along the station, at wing height, level.** A grazing view along a flat
  strip needs a 0.2–2.2° tilt over a neighbour one pitch away, which hides the
  near wing tip by up to 72 µm [mtsl §1]. On the crown the neighbour is 1.2 mm
  below the line, and the ribbon's own conductors are below the band looked at.
- **The backlight** sits beyond the ribbon's span downstream, where the crown's
  surface is 7–8 mm below the plane. It is fixed.
- **From above** the station contact is clear once the ribbon is drawn back,
  which is when the per-contact measurement is made.

## The crown as a strip feed at a housing

into-the-housing's i2 strip branch crimps a strip contact whose box is already in
a housing cavity, so the kept neighbour must pass under the housing. With every
contact kept, the 7.1 mm neighbour's box top clears the housing only on a
plastic crown (R ≤ 8–10 mm). With every other contact removed, R 25–30 mm puts
the kept neighbour's box top 1.2–2.0 mm below the housing's underside, with a
floor drop of 3.3–3.9 mm [ith-w3 I]. The same elastic crown serves there, and
under force-and-form's [f8](../../force-and-form/ideas/f8-narrow-press-at-the-housing-mouth.md),
whose strip drops 3.6–4 mm over a plastic crown of 6–12.5 mm.

## Problems and repairs

1. **A thinning cut missed** leaves a contact at 7.1 mm on the flank, 2.1 mm above
   the crest plane. Repair: the look after each index shows the flank; the
   machine indexes one pitch instead of two, the extra contact comes to the
   station, is sheared without a wire and swept off, and the next one-pitch index
   brings the next kept contact. Untested.
2. **The arriving contact's wings sweep through the crest plane** as it rides up.
   Repair: the ribbon is drawn back during every index.
3. **Carrier temper.** If the carrier is softer than C5191 spring temper, a 25 mm
   crown yields it slightly at every pass. Repair within the idea: a 30 mm crown
   (0.5 mm clearance) or two-of-three removal (≥ 4.8 mm). A strip bent round a
   50 mm bar and released shows which.
4. **The tab stub from a one-sided drop on a crown.** The shear edge is the
   crown's surface beside the drop plate. Same open question as a2.
5. **The thinning cup mixes stub lengths** among the removed contacts. That
   matters only to a loose route that references the rear end; the post routes
   ([a6](a6-post-is-the-gripper.md), [x3](x3-stage-crimp-one-push.md)) reference
   the box front.
6. **No proof pull at a flat crimp station.** Repair: the pull fork on the crown
   land, above.

## Steps covered, and what it hands back

- **Covers:** refilling from a reel, thinning, placing the contact (index, pins,
  per-contact fence), holding, placing the conductor (carriage steered by the
  picture, the rest of the ribbon lying flat), crimping, severing, a proof pull,
  verifying before and after the stroke, rejecting a bad contact without a wire.
- **Hands back:** splay and strip; insertion ([x2](x2-crown-then-sort.md) takes
  it on); emptying cups.
- **Machine time** ~106 s per crimp, ~94 min per unit [w2 §11].

## Printed and bought

| Part | Printed / bought | Note |
|---|---|---|
| Crown block | steel: a 50–60 mm round bar section, or plate milled to a 25 mm radius, with a pocket at the crest for the knife-set anvil and a slot for the drop plate | Low wear: the carrier slides over it at walking pace. Printed PET-CF flanks around a steel centre also serve; the anvil and the stop must be steel. Round bar is in [`../sourcing-requests.md`](../sourcing-requests.md) #21 |
| Knife-set punch and anvil | OTP "XH2.54" knife set | as a2; no Prime listing found |
| Thinning punch | a small hardened blade on a servo lever against a steel die edge, 48–158 N [xh-facts C1] | MG996R (Prime, $18.99 4-pack) on a 3–4:1 lever |
| Radial pins | 1.448 mm pin gauges ground to a taper, on a small lever inside the crown | Accusize set (Prime, $45.58) |
| Pull fork | two 0.4 mm tines of 1095 shim on an MG90S servo | Precision Brand shim (Prime, $53.39); Miuzei MG90S (Prime, $13.88) |
| Sprocket, take-up, drag, fence carriage, ribbon carriage, backlight holder | printed | — |
| Carriage load cell | ShangHJ 5 kg bar cell with HX711 (Prime, $9.99) | [sourcing/amazon-prime.md] |
| Press and drive | as a2 | — |
| Contacts | SXH-001T-P0.6 reel (Digi-Key 455-1135TR-ND, 1,329,000 in stock, $0.0235 @ 8k) or LCSC | [xh-facts §6] |

## Contribution

Two cheap moves from the supply side remove the strip's worst geometric cost:
take out half the contacts, which are the cheapest thing in the machine, and
bend the strip away from the station elastically. The ribbon then lies flat, the
camera looks straight across the station, the carrier's tension is the
hold-down, and the next contact is never bent before its turn.

## Major unresolved problems

- **The real SXH carrier pitch and temper.** At a pitch of 8.5 mm (the DLL
  drawing's scale) skip-2 gives 17 mm and more clearance. One strip settles both.
- **The knife set's blade width and protrusion,** which set the fan pitch.
- **Seating a knife-set anvil into a crown** with its top as the crest land.
- **Everything a2 leaves open about the die** outside its applicator.
- **The split left behind the housing** (9–26 mm) and whether it is acceptable.
- **The thinning punch's stub on the kept carrier** (irrelevant to the crimp; it
  must not snag the sprocket).

## What each conclusion rests on

- **Facts [mfr, source]:** side-feed strip geometry from clone drawings; stock
  and prices [xh-facts §6]; press openings and Prime listings.
- **Calculations [calc]:** neighbour clearances on a flat strip [w2 §1]; crown
  geometry and strain [w2 §2]; supply and cost [w2 §7]; kink position [w2 §9];
  punch-holder rule, blade protrusion and split [w3 §5]; proof-pull stresses
  [w3 §6]; crown under a housing [ith-w3 I]; grazing view [mtsl §1].
- **Estimates:** C5191 yield 450–650 MPa, E 110 GPa; punch-holder clearance of
  0.3 mm; time per crimp.
- **Assumptions:** pitch 7.1 mm (Würth analog); clone open-wing height 3.2 mm
  maximum (genuine wings, if smaller, only add clearance).
