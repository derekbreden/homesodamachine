# b1b — The OTP applicator in a slow crank press built around it

**Branch of [b1](b1-press-and-applicator-with-shuttle.md).**

**What stays from b1:**
- the bought OTP side-feed XH applicator, which does all of "place the contact,
  hold it, crimp both barrels, cut the tab";
- the printer-axis shuttle, the cassette with its flat band, and the
  valley-tine fork.

**What changes:**
- the 50 kg Chinese press is not bought;
- the applicator's ram is driven by a slow crank that Derek builds, in the idle
  VEVOR 12-ton shop press already in the shop (or a laser-cut steel O-frame, or
  a 3-ton arbor press);
- the drive is Derek's own NEMA 23 and DM542T through a gearbox;
- because the crank can **stop at any angle**, the applicator runs in pre-feed:
  the camera sees the contact alone on the anvil, then the conductor laid into
  it, before anything irreversible happens.

**Related:** [b1c](b1c-one-shaft-applicator-press.md) puts every motion on this
crankshaft; [b8](b8-spool-fed-borrowed-line.md) runs this press at the spool;
terminal-supply's [a1](../../terminal-supply/ideas/a1-applicator-slow-ram.md)
drives the same applicator with a screw ram, and its supply-side gate (look
first, reject turn, wedge) is part of this idea as it stands.

Sketch: [`../sketches/b1b-crank-press.svg`](../sketches/b1b-crank-press.svg).

Labels: [calc presses §n], [calc wave3 §n] are this explorer's
[`presses.out.txt`](../calc/presses.out.txt) and [`wave3.out.txt`](../calc/wave3.out.txt);
[procedure calc §n] is procedure-is-the-machine's
[`exchange_borrowed.out.txt`](../../procedure-is-the-machine/calc/exchange_borrowed.out.txt);
[TS §n] is terminal-supply's
[`w3_on_borrowed.out.txt`](../../terminal-supply/calc/w3_on_borrowed.out.txt) and
[TS wave2 §n] their [`wave2.out.txt`](../../terminal-supply/calc/wave2.out.txt);
[Prime] is a row in [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md)
(observed 2026-09-28); [facts] is [`../../../context/xh-facts.md`](../../../context/xh-facts.md).

## Picture it

**Where things start.** An XH reel threads through the applicator, its cam in
the **pre-feed** ("manual") position [mfr: WERI manual §7], so a contact waits
open on the anvil at rest. The ribbon end sits in b1's cassette on the shuttle
in front of it, split, stripped and folded back as one flat band.

**The press.**
- **Frame.** The applicator's base is clamped to the bed of the VEVOR 12-ton
  H-frame shop press [repo tools.md]. Its bottle jack is set aside.
- **Crank unit**, bolted under the press's top crossmember:
  - a 20 mm crankshaft in two UCP204 pillow blocks ($26.99 a pair [Prime]);
  - a steel crank disc whose throw is half the applicator's stroke: 15 mm for
    the 30 mm stroke of OTP units made for the Chinese presses, 20 mm for a
    40 mm-stroke applicator such as JST's CMKS-L [facts §2];
  - a flat steel connecting rod ~100 mm long with a bearing at each end and a
    **preloaded disc-spring stack** in its length (below);
  - a short ram in a bronze bushing, its lower end a laser-cut T-slot block that
    captures the applicator's ram head.
- **Drive.** The NEMA 23 turns the crankshaft through a 10:1 planetary
  (StepperOnline, $48, 10 N·m permissible, 20 N·m momentary [Prime]), one turn
  in about 10 s when it is not stopped. The DM542T's current is set so the
  gearbox never sees more than its 10 N·m.
- **Home and angle.** A slotted flag and an optical switch mark top dead
  centre; step count gives angle.
- **Gauges.** Two BF350 foil gauges ($6.99 [Prime]) on the connecting rod's
  flats feed an HX711 (SparkFun, $11.50 [Prime]). A microswitch watches the
  disc-spring stack.

**One conductor.**
1. **Look at the contact alone.** The crank is at top dead centre and a contact
   waits open on the anvil. Before the fork moves, the camera checks it:
   present, lance, roll, wings, bellmouth line against fiducials on the anvil.
   A bad contact gets a **reject turn** (below) and no conductor ever meets it.
2. **Lay in.** The shuttle and fork lay conductor *i* into the waiting contact.
   A servo presser foot (or the applicator's own wire hold spring, held down by
   a small cam on the crank unit) seats it in both barrels.
3. **Gate.** The camera sees the strands inside the conductor barrel and the
   insulation edge in the window between barrels. Far-end channel *i* to the
   grounded applicator reads continuous: the strands touch the contact, and it
   is the right conductor. Only then does the crank turn.
4. **Crimp.** The crank turns slowly through bottom dead centre. Its mechanical
   advantage is highest there, where the crimp needs the most force. The HX711
   records ~19 samples through compaction at a 10 s turn, ~39 at 20 s [calc
   wave3 §3].
5. **Dwell.** The crank stops between 40° and ~85–105° after bottom dead
   centre (220° to 265–285° from top). At 220° the crimpers have risen ~4 mm and
   cleared the box; the feed finger starts only at ~15–20 mm up [calc wave3 §1;
   the feed height is an assumption until the jack test]. While the crank waits:
   - the foot lifts and the fork opens its hold;
   - the shuttle withdraws the crimped contact ≥7 mm along its axis;
   - a thin fork drops into the neck behind the box and the shuttle pulls 20 N
     against it, above the floor and clear of the lance [TS §11];
   - the camera photographs the finished crimp, punch clear, contact in view.
6. The crank finishes its turn. The feed runs on an empty anvil and leaves the
   next contact waiting. The fork parks the crimped conductor in the band.

**The reject turn.** When step 1 or step 3 blames the contact, the fork lifts
the conductor away (it is a servo, not bound to the shaft) and the shuttle moves
the band aside. The crank then turns once with nothing to crimp: the crimpers
close the bad contact empty and the shear cuts its tab. In the dwell, between
the crimpers clearing (220°) and the feed moving (~266°), a puff from a 1 mm
nozzle through a 24 V 5/2 valve (TAILONZ, $16.99 [Prime]; compressor on hand)
blows the crushed contact off the anvil into a reject cup. That window is 1.3 s
at a 10 s turn, or as long as wanted with the shaft stopped [calc wave3 §5]. The
feed then brings the next contact, which is looked at alone again. Without the
blow-off, the next pre-feed would push a fresh contact into the crushed one.

**What locates what; the reference for "fixed."**

| What | Set by | Reference |
|---|---|---|
| Contact on the anvil | strip track, terminal stop, feed finger, hold-down | applicator |
| Conductor in the barrels | fork tines and foot, both on brackets bolted to the applicator base | applicator |
| Ram bottom | crank throw plus rod length, set once with a threaded rod end to the applicator's shut height (135.8 mm for the mini-applicator standard [prior-art §3], 135.78 mm for JST's CDS/CMKS-L [facts §2], 160 mm for JST's MKS-L), measured on the unit that arrives | crank geometry and frame |
| Dwell angle | after the crimpers clear the box, before the feed finger moves | home flag and step count; the window measured in the jack test |
| Crimp height | the applicator's dials; optionally a stepper wedge under its base (below) | applicator |

**What drives the crimp and carries its force.**
- **Needed at the crank:** 3.8 N·m to push a 3 kN design crimp through bottom
  dead centre, and up to 5.4 N·m at mid-stroke if the applicator's springs
  total 300 N [calc presses §1, spring load an estimate].
- **Available:** the 10:1 gearbox held to its 10 N·m permissible rating gives
  ~4.6 kN of ram force at 0.1 mm above bottom and ~3.3 kN at 0.2 mm [calc wave3
  §4].
- **The force loop:** crank, rod, disc stack, ram, applicator, bed, press
  columns, top beam, pillow blocks. The 12-ton frame (118 kN) barely notices
  3 kN [estimate: deflection in proportion to its rating, tens of µm].

**How it knows it worked.**
- **Before anything irreversible:** the contact alone (step 1), then contact
  and conductor together with continuity (step 3). These are the gates a fast
  press cannot have.
- **Force curve.** A band taught from good crimps catches no wire, no contact,
  insulation under the conductor barrel and a doubled contact.
- **Stop before bottom.** The stepper can stop at 0.3 mm above bottom when the
  curve is already out of band, and back out.
- **Stop at force.** The disc-stack microswitch trips if the rod carries more
  than its preload.
- **After:** the dwell picture, the 20 N proof pull, continuity.
- **Crimp height** by micrometer on sample crimps, or by a wedge sweep (below).

**What the person does.** The same as b1: loads cassettes, closes the fold lid,
inserts, changes reels, measures crimp height by sample, empties the reject
cup. At the start, they set shut height once with the rod-end thread and a
gauge block.

## Steps it covers and what it hands back

- **Covers:** supply contacts (reel), place the contact on the conductor
  (pre-feed, fork, foot), crimp, verify the crimp (two gates, force curve,
  stop-before-bottom, stack switch, dwell picture, proof pull, continuity).
- **Hands back:** as b1: cutting and loading cassettes, the fold lid,
  splitting and stripping unless a prep station is built, insertion, reels,
  sample crimp height, the reject cup.

## The dwell is what the slow crank buys

On a bought fast press the window between "punch clear of the box" and "feed
finger moves" is 50–90 ms. On this crank it is ~46–65° of shaft: **1.3–1.8 s at
10 s per turn, and as long as wanted if the stepper stops there** [calc wave3
§1, §5]. That lets b1b keep pre-feed, with the contact waiting in the die for
the conductor, which is also what a person at a hand-fed press has. Everything
that must be off the conductor before the feed (foot, fork, crimped contact)
leaves during the dwell, in any order, at any speed.

## The over-travel stack in the connecting rod

Near bottom dead centre a crank is a displacement source: ds/dθ → 0, so the
stepper does not stall on a short, stiff obstruction; it pushes it through with
whatever force the loop stiffness demands.
- With the drive held to 10 N·m, a 4 kN obstruction met above ~0.13 mm over
  bottom stalls the drive; one met below that is pushed through [calc wave3 §4].
  In a 40–100 kN/mm loop an obstruction 0.1–0.2 mm high reaches 8–10 kN
  [procedure calc §3].
- That is a doubled contact (+0.2–0.4 mm of stock), a folded strand bundle or a
  carrier scrap, met in the last 0.1–0.2 mm where compaction happens anyway, so
  the force curve cannot flag it early enough to stop.

**The stack.** Two DIN 2093 A35.5 disc springs in series in the rod, preloaded
to ~4 kN, give ~0.30 mm of travel to ~5.2 kN (~4 kN/mm) [TS §7]. Smaller series
A discs (A25, A28, A31.5) cannot reach a 4 kN preload.
- Below 4 kN the stack does not move, so crimp height is untouched.
- Above it, the rod force stays under ~5.4 kN in every case computed
  [procedure calc §3]; ~0.13–0.15 mm of stack travel covers the obstructions a
  10 N·m drive would push through [calc wave3 §4].
- The stack's travel trips a microswitch: a real "stopped at force" signal.
- Discs of this size come from industrial suppliers. Prime shows only a light
  stainless M3–M12 Belleville assortment ($14.99 [Prime]), which cannot make
  this stack.
- Uncertain: whether the OTP crimpers survive ~5 kN on a doubled contact. They
  are made for 15–20 kN presses [assumption].

## Crimp height on the production die: the stepper wedge

A 2–3° steel wedge under the applicator's base, pushed by a small stepper on a
Tr8×2 screw, raises the anvil 35–52 µm per mm of wedge travel and self-locks
under 3 kN [TS wave2 §8] (terminal-supply's transfer from its a1 and a5). The
crank still fixes bottom dead centre; the wedge moves the anvil to meet it.
- The machine sweeps crimp height in 0.02 mm steps on the production die and
  sections or pulls the results, finer than the applicator's ~0.05 mm dial
  graduations [mfr MKS-L].
- Genuine and clone contacts become two stored wedge positions.

## Stage 0: the jack test

With the bottle jack left in, the shop press is already a slow manual press:
- the applicator sits on the bed;
- a T-slot adapter goes on the jack's ram;
- pumping by hand strokes the applicator, and releasing the valve returns it;
- a hard-stop collar on the adapter, landing on the applicator frame, sets
  bottom [estimate].

Every stroke feeds and crimps. One applicator, a reel and a printed adapter
make a working crimper in the first week, laid in by hand, and a measuring bench
for every applicator arrangement in this study:
- **Crimp** real contacts on the real ribbon; section and pull-test them.
- **Two supplies through one die** (terminal-supply's proposal). Thread the vendor's
  reel, crimp, section and pull; then thread one Digi-Key 100-piece genuine
  SXH strip (455-1135-100-ND, $4.71 [facts §6]) through the same feed and do the
  same. That shows which contact the OTP die is cut for, whether genuine carrier
  pitch fits the feed's pitch screw, and whether genuine wings clear b1's ram
  finger V.
- **Timing.** Note the ram height where the feed finger starts to move on the
  way up, and where it retracts on the way down. That sets the dwell window
  here, b1's post-feed timing and b1c's cam phasing.
- **Envelope.** Watch where the feed finger stands when the feed ends, with a
  conductor held at 4.6 mm (b1's envelope question), and photograph across the
  anvil at wing height (line of sight to the waiting contact).
- **Geometry.** Scan the tooling face with the Revopoint for its half-width and
  tip-to-face depth, which set the split length, and for the room below the
  anvil top ([b8b](b8b-flat-spool-line-over-a-crown.md)'s applicator-as-die-holder
  variant).

The crank replaces the jack later; the shuttle, cassette and cams come after.

## Drives, as borrowed

| Drive | Usable torque at the crank | Stroke time | Ram force at 0.1 mm above bottom | Notes |
|---|---:|---:|---:|---|
| Derek's NEMA 23 + DM542T [repo] + 10:1 planetary held to 10 N·m | 10 N·m | 10 s, or stopped | ~4.6 kN [calc wave3 §4] | programmable dwell, stop-before-bottom, speed; gearbox $48 [Prime], thin listing (4 ratings) |
| same + 20:1 planetary | ~20 N·m if its rating allows (not read) | 20 s | ~9 kN | 39 HX711 samples in the last 0.2 mm; same $48 listing [Prime] |
| NEMA 23 + 30:1 self-locking worm (StepperOnline NMRVS30, C$76.69, 20 N·m, 24 h ship [force-and-form, source]) | ~13–20 N·m | 30 s | ~6–9 kN | holds the dwell unpowered; Prime alternatives: Heechoo 30:1 worm-gear NEMA 23, $120, output torque not stated; CNCTOPBAOS NMRV030 40:1, $38.99, 11 mm bore needs a sleeve [Prime] |
| 12 V car wiper motor with its park switch | stall ~12 N·m (search summary), ~6 used | ~1.2 s | ~2.8 kN | the park switch is a single-revolution stop; **no dwell**: one uninterruptible turn gives a 0.12–0.22 s window [procedure calc §2], so it needs b1's post-feed and ram finger. The Prime wiper-type gearmotor (BEMONOC, 6 N·m rated) has no park switch [Prime]; this route means a salvaged car motor |
| industrial wiper gearmotor (AM Equipment 240) | stall 40 N·m, ~20 used | 1–3 s | ~9 kN | $172.65, two-week lead time [source](https://www.amequipment.com/shop/240-series-dc-gear-motor/); no dwell unless braked |

With any gearmotor the crankshaft sits in its own pillow blocks and is driven
through a coupling; a gearbox housing is not meant to carry 3 kN of radial load
[assumption].

## Other rams, same "position from geometry, force from something bigger"

- **Ball screw with an over-travel spring.** Thrust 1.4 kN from a direct SFU1605
  on the NEMA 23; 3.8 kN via 3:1; 8 kN via 5:1 on a 4 mm lead [calc presses §3].
  The nut drives the ram through a disc stack preloaded above 3 kN and the ram
  lands on a stop at shut height. It dwells anywhere, like the crank. (An
  SFU1605 kit with supports is $41.59 [Prime].)
- **Air cylinder with a hard stop.** A 63 mm bore at 7 bar is 2.2 kN; through a
  3:1 lever, 6.5 kN [calc presses §3]. BAOMAIN SC63×50, $33.49; flow controls,
  $14.99 [Prime]. It gives no curve without a load cell, and a mid-stroke dwell
  needs a 5/3 closed-centre valve.
- **Toggle clamp.** A GH-305-class push-pull clamp (POWERTEC 305CM pair, 500 lb
  hold, $18.25 [Prime]) passes over centre to a fixed end position. Its hold
  rating sits inside the crimp range, so it suits hand-tool dies
  ([b2](b2-hand-crimper-in-a-frame.md)) better than a 30 mm-stroke applicator.

## Frame, if not the shop press

- **A 3-ton arbor press.** The VEVOR AP-3 ($255.90, 310 mm opening, 130 mm
  throat [Prime]) is the first Prime frame found that opens past an OTP
  applicator plus its stroke (166–176 mm [force-and-form f2b]). The crank unit
  replaces its rack drive, or a motor turns its pinion with a stop at shut
  height (force-and-form f2b). The AP-1 1-ton (150 mm) takes a knife-set block
  only.
- **A laser-cut O-frame.** Two steel plates and four 16–20 mm rods; SendCutSend
  cuts mild steel to 12.7 mm in 2–4 production days
  ([SendCutSend](https://sendcutsend.com/materials/mild-steel/)). The rods must
  clear the applicator (a WERI mini-applicator is 155 × 150 × 110 mm
  [prior-art §3]), so one span is ~170 mm. There a single 12.7 mm plate gives
  ~13 kN/mm: 0.24 mm stretch at 3 kN and ±0.024 mm scatter from a ±15 % force
  spread. Two plates acting as one give ~39 kN/mm and ±0.008 mm [calc presses
  §2]. The mean stretch is dialled out on the applicator; J.S.T. UK's tolerance
  is ±0.05 mm [facts §1].
- **A printed frame** is not viable: 0.12–0.23 mm at 3 kN, and it creeps [calc
  presses §2].

## References and tolerances

| Quantity | Needed | Provided by |
|---|---|---|
| Ram bottom (shut height) | repeat to ~±0.01–0.02 mm so crimp height holds ±0.05 [estimate] | crank geometry (fixed) plus frame stiffness; the disc stack is solid below its preload |
| Shut height, absolute | the applicator's value, unpublished for OTP | rod-end thread, set once against a gauge block |
| Ram alignment | T-slot captures the applicator ram head; rod angle ≤ asin(15/100) = 8.6°, ~45 N of side load mid-stroke at 300 N of springs [estimate] | bronze bushing |
| Dwell angle | after the crimpers clear, before the feed moves | home flag and step count, from the jack test |

## Printed and bought

- **Printed:** flag disc, sensor bracket, gauge-wire strain relief, air-nozzle
  holder, guard panels. The shuttle parts are as in b1.
- **Bought:** applicator and reel (eBay or Made-in-China, not Prime);
  laser-cut crank disc, connecting rod and T-slot block (SendCutSend); two DIN
  2093 A35.5 discs and a microswitch (industrial supplier); bronze bushing;
  UCP204 pillow blocks and 20 mm shaft, the 10:1 planetary or a worm, BF350
  gauges, HX711, opto switch, 5/2 valve [Prime rows above].
- **On hand:** NEMA 23 + DM542T + 24 V, the VEVOR 12-ton press, the compressor
  [repo tools.md].

## Problems and their repairs, as they stand

- **"A slow crank can't make 3 kN."** Near bottom the crank's ds/dθ falls to
  1.3–2.6 mm/rad, so 3.8 N·m at the shaft is enough for the crimp [calc presses
  §1]. The applicator's springs over the open stroke may need more torque than
  the crimp; that is a measurement on the applicator.
- **"The applicator's cam feed needs a fast stroke."** The cam-and-pawl
  mechanism is kinematic [prior-art §3]; stock drag holds the strip between
  strokes [assumption: no inertia-assisted feed in the cheap OTP units].
- **The stepper does not stall safely at bottom** on a short stiff obstruction;
  the disc stack in the rod caps the force and signals it.
- **A bad waiting contact has no exit by stroking alone:** a stroke with no wire
  leaves a crushed contact that the next pre-feed pushes into. The look at the
  contact alone and the reject turn with its blow-off are the repair.
- **The shop press's frame and the shuttle.** The H-frame's columns stand
  ~500 mm apart [estimate]; the shuttle sits on the bed in front of the
  applicator and the frame's height leaves the camera room. Whether the bed is
  flat and rigid enough to clamp the applicator is open; it is usually two
  channel sections on pins [estimate].
- **The drive's rating.** The Prime 10:1 planetary is rated 10 N·m permissible
  and 20 N·m momentary, so the DM542T's current is set to hold 10 N·m at the
  crank. That still covers the crimp (3.8 N·m) and 300 N of applicator springs
  (5.4 N·m) [calc wave3 §4].

## Contribution

- A slow machine keeps the contact waiting in the die and still gets every
  holding part out of the way before the next feed, by stopping the shaft.
- It looks at the contact alone, then at contact and conductor together, before
  anything irreversible; a bad contact leaves by an empty crimp and a puff of
  air.
- A real crimp force signature from the cheapest ADC.
- Crimp force is a torque problem only at mid-stroke; at the crimp, crank
  geometry does the work.
- The idle 12-ton press and its jack are a zero-cost way to learn the applicator
  before building anything.

## Major unresolved problems

- **The applicator interface.** Shut height, stroke (30 or 40 mm), ram-head
  shape, spring loads and feed-finger timing are unpublished for OTP units; they
  come with the part, and the jack test measures them.
- **The crank disc.** Made without a lathe: a laser-cut disc keyed to the shaft.
  How well a laser-cut bore and keyway hold on a 20 mm shaft is untested.
- **The shop press bed.** Its flatness and rigidity, and how the applicator
  clamps to it.
- **Strain-gauge calibration** to read newtons; comparing curve shapes works
  without it.
- **The crimpers at ~5 kN** on a doubled contact, with the stack capping it.
- **The reject turn's blow-off.** Whether a crushed empty contact leaves the
  anvil on a puff, or stays wedged in the nest or under the stripper plate
  [assumption]; the after-picture shows which.
- **Guarding.** A slow pinch point, and a stroke that could start with the fork
  still near the tooling if the controller is wrong; an interlock on the fork's
  parked position belongs in the drive's enable.

## What rests on what

- **Derek:** slowness is acceptable; the bench's idle 12-ton press and NEMA 23
  with DM542T [repo] are his.
- **Facts:** crimp force range and design value [facts §4]; applicator shut
  heights and strokes [facts §2, prior-art §3]; J.S.T. UK's ±0.05 mm
  tolerance; contact dimensions; the Digi-Key strip.
- **Calculations:** crank torque, force and samples [calc presses §1, calc
  wave3 §1, §3, §4]; frame stiffness [calc presses §2]; the reject-turn window
  [calc wave3 §5]; the push-through at bottom [procedure calc §3]; the disc stack
  and wedge [TS §7, TS wave2 §8].
- **Estimates:** applicator spring load 100–300 N; frame deflection; ram side
  load.
- **Assumptions:** the OTP applicator tolerates any stroke speed; its feed
  finger starts 15–20 mm up the upstroke; a feed lever that follows ram height; a
  gearmotor housing does not carry radial load.
