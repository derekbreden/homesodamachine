# A1 — The squeezer: the bench's SN-2549 in a printed cradle, closed by a slow actuator

## Picture it

**Where things start.**
- The iCrimp SN-2549 lies on its side in a printed cradle on the bench, jaw
  plane vertical, so every nest's axis points horizontally at the person.
- Its lower handle sits in a printed saddle and is strapped down. A printed
  opening limiter stops the upper handle opening wider than loading needs.
- The ribbon is in the person's hand, split and stripped. The strip length is
  set from one measured contact of the lot in use (below). The ribbon's far
  end is in a push-in terminal block wired to an ESP32.
- The contacts are loose from the CQRobot kit, in a dish, or SXH stubs.

**What moves.** Only the upper handle.
- A NEMA 17 with a Tr8×2 external lead screw, mounted on the cradle, drives a
  nut carriage with a roller foot onto the upper handle's grip end, through a
  bar load cell.
- A branch reels a Dyneema cord from the upper handle's grip with a worm
  gearmotor. That is the same cord and pulley that
  [a6](a6-foot-closed-jig-bench.md)'s foot treadle pulls, so a6's bench
  becomes a1 by swapping the treadle for the winch.

**What locates what.** "Fixed" is the lower jaw.
- **The locator plate.** A printed plate bolts to the lower jaw through the
  stock M4 jaw screw, lengthened to 20 mm. That is the attachment the published
  SN-2549 positioners use [source: Chief Delphi / Printables, Ryan Reed].
- **The contact.**
  - The box rests against a front stop on the plate.
  - A thin insulated steel blade on a sprung flap drops into the contact's
    neck, the short floor strip between the box's rear face and the conductor
    barrel. Its insulated front face bears on the box's rear walls. Its bare
    rear face is the stop and the electrode for the strand tips.
  - With strip stubs, a sprung pin in the pilot hole does the axial locating
    instead (terminal-supply's
    [a2c](../../terminal-supply/ideas/a2c-strip-locator-for-hand-tool.md)).
- **Sideways and in rotation,** the nest locates the barrels once the jaws
  close to "hold".
- **The conductor** is guided by a printed funnel on the jaw's rear face.

**What drives and carries the crimp force.**
- The actuator supplies at most a hand's force at the grip, 90–220 N
  [calc §1].
- The tool's linkage multiplies it to the 0.8–2.6 kN the crimp takes
  [xh-facts §4], and that force stays inside the head, jaw to jaw.
- The cradle carries only the actuator's reaction, grip to grip.

**How it knows it worked.**
- **The stroke.** Logged as force against lead-screw position, and compared
  with curves taught from good crimps and with two references: the empty tool,
  and a contact with no wire. The station ESP32 runs the whole squeeze and
  checks every load-cell sample; the Mac commands squeezes and reads traces
  (below).
- **The ratchet.** Its teeth show as a sawtooth, and its release as the force
  collapsing at the end of the stroke.
- **Continuity through the far-end block.** Two separate events:
  - **amber:** conductor *k*'s strands touch the contact or tool;
  - **green:** they touch the blade's rear face.

  Only conductor *k* may read.
- **Two camera frames.** One looks across the neck at hold, one at the side of
  the crimp once the jaws open, including the window between the barrels.
  Both are judged against what the housing needs.

**What the person does.**
1. Presses a contact onto the locator, box against the front stop; the flap
   drops. The machine closes to "hold".
2. Pushes the stripped conductor in until green.
3. Presses the pedal, or lets the machine fire after a dwell once green holds.
4. When the jaws open, lifts the crimp off the anvil (a printed ramp does it as
   the wire is drawn), then draws it back.

Everything upstream (cut, split, strip) and downstream (housing insertion,
test, label) is as today, or a6's jigs.

Sketch: [`../sketches/a1-squeezer-cradle.svg`](../sketches/a1-squeezer-cradle.svg);
the neck at hold in [`../sketches/a6-jig-bench.svg`](../sketches/a6-jig-bench.svg).

## Steps it covers and what it hands back

**Covers:**
- holding the contact (the first ratchet tooth);
- the full crimp stroke;
- entry, depth and identity by continuity;
- logging and judging the force curve;
- the neck and side frames.

**Hands back:**
- cut, split and strip;
- putting the contact on the locator and the conductor into the contact;
- lifting and drawing the crimp out;
- the proof pull and fit check, at a6's jigs if wanted;
- housing insertion;
- the label.

The person does the fine placing against stops instead of by eye, and never
carries crimp force.

## How it relates

This is the base the other arrangements build on:
- [a6](a6-foot-closed-jig-bench.md) is this station without the motor;
- [a1b](a1b-pawl-out.md) takes the ratchet pawl out;
- [a2](a2-ribbon-to-fixed-tool.md) adds a carriage that loads it;
- [a3](a3-tool-travels-to-ribbon.md) moves the squeezer to the wire;
- [a4](a4-dies-in-a-die-set.md) takes the dies out of this frame;
- [a5](a5-two-squeeze-plier.md) puts a different tool in it;
- [a6b](a6b-flags-by-hand-foot-crimp.md) and [a6c](a6c-flags-by-machine-foot-crimp.md)
  feed it contacts already on their wires, which removes the blade and the
  first-tooth question.

## Major unresolved problems

- **The neck.** Its length on a kit contact is unmeasured. The 0.2–0.5 mm used
  here is a reading of how the parts look [estimate, ith ex §1]; summing the
  clone drawings' lengths does not constrain it (−0.7 to +2.0 mm
  [ribbon-as-pallet calc P §3]), and genuine and clone necks may differ. A
  blade plus a brush fits only if the box-to-barrel transition is at least
  ~0.3 mm [calc w2 §1]. Below that the contact is located by a pin (strip) or
  a front stop checked by camera.
- **The first tooth.** Where the ratchet's first tooth falls relative to
  "contact held, wire still enters". Past the first tooth the tool cannot
  reopen until it has crimped, unless the release lug is lifted.
- **The nest.** Which of the SN-2549's four nests (0.08–0.5, 0.25, 0.5,
  1.0 mm²) makes a good crimp on this 22 AWG silicone, and whether its closed
  insulation barrel fits the cavity. The crimp height it makes is unmeasured.
- **Whether the SN-2549's dies bottom face to face.** If they do, crimp height
  is die geometry; if not, it is where the ratchet releases.

## The tool as the machine

- **The tool.** The SN-2549 is listed at 8 × 3 × 1 in and 10 oz. It crimps
  both barrels in one squeeze and has a tension wheel on the side [source:
  TH3D listing, $17.99]. iCrimp describes a "parallel crimping" ratchet
  mechanism with wire-EDM-cut jaws [source: icrimptools.com]. A second one is
  on Prime at $22.29, 532 ratings, 100+ bought in the past month [prime:
  B01N4L8QMW].
- **The family.** The SN tools (SN-28B, SN-48B, SN-58B, SN-2549 and others)
  share one frame. Their jaws are replaceable at $4.99–9.99 a set [source:
  icrimptools.com]. Each jaw is held by screws, which are loosened, the dies
  crimped closed to seat them, and the screws tightened [source: IWISS
  instructions as quoted in search results].
- **On the bench.** Derek owns the SN-2549 and an SN-28B [repo:
  `hardware/ledger/tools.md`], so the bench already holds two copies of the
  frame.

What the machine borrows from the tool:
- **Die geometry that already makes XH crimps.** Derek crimps XH with it by
  hand [repo].
- **A linkage whose gain rises toward closure.** Pressmaster's C-frame tools
  went from 23:1 to 50:1 gain [source: Assembly Magazine 95079]. A cheap
  stamped tool is assumed at 15–40 [assumption], which puts the grip force at
  16–173 N across the die-force range [calc §1].
- **A frame that bottoms the dies.** IWISS's IWS-3220M jaws "touch each other
  everywhere" when closed [source: hackaday.io 176110]. If the SN-2549's do
  too (Derek can see it by holding the closed tool to a light), crimp height
  is set by the dies, not by how hard or fast the tool is squeezed.

## The hand is the existence proof for force

Derek closes this tool on XH contacts by hand [Derek, via repo]. People apply
20–50 lbf (89–222 N) at a crimper's handle [source: Assembly Magazine 95079].
So the grip force needed is at most ~220 N, whatever the gain.

| Drive | Force at the grip [calc §2] |
|---|---:|
| NEMA 17 (48 mm stack) + Tr8×2 external nut, run slow | ~280 N |
| NEMA 17 + Tr8×8 | ~110 N |
| NEMA 23 on hand + Tr8×2 | ~940 N |
| 5840-31ZY worm gearmotor, cord drum r = 6 / 8 / 12 mm | ~380 / 290 / 190 N |
| Air cylinder 25 mm bore at 6 bar | ~300 N |
| 35 kg·cm hobby servo, 25 mm horn | ~70 N |
| A foot on a 2:1 treadle (a6) | ~100–220 N for 55–122 N at the toe [calc w2 §5] |

Grip travel is ~50–56 mm at full opening. At 2 mm/s the full squeeze takes
~27 s [calc §3]. The opening limiter cuts the travel to ~25–35 mm [estimate],
the least that lets the contact in with its lance clear (below).

## Who owns the squeeze: the station MCU

The pusher does not crawl near closure, but the die does. At 2 mm/s at the
grip and a gain of 15–40 the die moves 0.05–0.13 mm/s, which is a crawl
through compaction with no crawl phase to program [sl w3 §2]. What the handle
does not slow is the controller's reaction:
- one HX711 sample (12.5 ms) past a force limit is 25 µm of grip and 3–21 N
  extra at the dies;
- a 30 ms USB round trip is 6–51 N;
- a 0.5 s stall on the Mac is 108–857 N [sl w3 §2, estimates of handle and
  die-loop stiffness].

So the station ESP32 runs each squeeze whole and checks every sample: the
force envelope, the ratchet-release collapse, and a heartbeat hold. The Mac
commands squeezes and reads the traces. This is machine-that-sees-and-learns'
rule for any press ([v7](../../machine-that-sees-and-learns/ideas/v7-the-run.md)),
and a1 is one of v7's stations unchanged.

## What the ratchet does for and against a machine

**For:**
- It forces a full cycle, so an interrupted stroke leaves the tool locked on
  the contact. The wire cannot come out half-crimped.
- It gives a "hold" position at the first tooth.
- The tension wheel moves where the ratchet releases, a coarse crimp
  adjustment [source: icrimptools blog; the mechanism is an assumption].
- Its clicks mark positions in the force trace.

**Against:**
- **No back-out past the first tooth.** If continuity never comes (the wire
  missed the barrel), the machine can only crimp the empty contact or lift
  the release lug.
  - The SN family has a release lug on the pawl between the grips [source:
    cabling forum; IWISS video "SN series how to release the crimper"].
  - A small servo finger on the lug restores back-out.
- **Stalls.** An actuator that stalls short leaves the tool locked. A NEMA 17
  pusher at ~280 N, against a need of ≤ 220 N, stalls only on a jam.
- **The sawtooth.** The pawl adds a sawtooth to the force curve, which the
  teach-in has to absorb.

[a1b](a1b-pawl-out.md) takes the pawl out.

## The handle as a gauge

Near closure, the grip moves 15–40 times as far as the die [assumption on
gain]. Strand compaction happens in the last 0.10–0.20 mm of punch travel
[xh-facts §4], which is 1.5–8 mm at the grip [calc §4]. The pusher resolves far
finer than the compliance of handles, pins and pusher mount. That compliance is
measured, not modelled:
- close the empty tool;
- close on a contact with no wire;
- close on a good crimp.

The difference between those curves is what the wire and the crimp did. This is
crimp force monitoring by teach-in and band [prior-art §6]. It catches:
- no contact;
- no wire;
- insulation under the conductor barrel;
- the wrong nest;
- a doubled-back conductor.

It does not catch one strand of 60, which is 1.7 % of the force [digest].

## The locator in the neck, with the lance underneath it

The WC-110's own sequence places the contact against a flap locator, closes
lightly until it is held, then feeds the conductor to a stop [mfr: WC-110
instruction manual, RS-hosted PDF]. The SN-2549's one-piece stepped die leaves
nothing reachable between the barrels. So the stop sits in the one gap outside
the die that bounds both the contact and the strands: the neck.

**What shares the neck** [ith ex §1; calc w2 §1]:
- **The box's rear face,** at 2.0 mm from the nose.
- **The conductor barrel's front edge,** 0.2–0.5 mm further back
  [estimate].
- **The brush,** 0.1–0.2 mm past that edge, and never into the box [mfr S5].
- **The lance tip,** 2.24–2.64 mm from the nose and 0.6–0.9 mm below the
  floor. It lies in front of the anvil's front face, or over a relief, since
  hand crimps from this tool latch.

**The blade.**
- **Thickness.** 0.10 mm spring steel (a feeler leaf), plus polyimide tape or
  lacquer on the front face and slot edges; 0.13–0.15 mm in all. It leaves
  +0.05 to +0.38 mm for the brush at transitions of 0.2–0.5 mm. A 0.3 mm
  blade would leave −0.10 to +0.20 [calc w2 §1].
- **The slot** straddles the floor strip within ~0.05 mm a side, so no
  0.08 mm strand slips past toward the box.
- **The tines** stop at the strip's lower face. The lance, narrower than the
  strip, hangs below and between them.
- **The front face** bears on the box's rear walls, sides and top.
- **The rear face** is bare steel: the strand stop, and an electrode insulated
  from the contact.
- **The ramp.** A contact loaded from the rear lifts the flap on a ramp, and
  the blade drops behind the box: a latch.
- **The front stop** is a printed face for the box nose. It keeps the blade
  from having to find the contact.

**Why the insulation matters.** A bare blade touching the box is electrically
the contact. The contact sits on the steel anvil, so strands touching any part
of the contact, or the die's rear face on a miss, read the same as strands at
the blade, and one continuity signal cannot tell depth from entry. Insulated,
there are two events:
- **Amber, the strands meet metal of the contact or tool.** It comes at the
  insulation barrel's mouth. If it comes at the wrong hand or carriage
  position, the tip has hit the die's rear face.
- **Green, the strands meet the blade.** That is depth.

**When the neck is too short.** At a transition of ~0.2 mm there is no room
for any blade with a brush. Then:
- **Strip stubs.** A 1.45 mm pin in the pilot hole and a fence on the carrier
  edge [terminal-supply a2c], ±0.035 mm plus the hole-to-barrel tolerance
  [calc §7].
- **Loose contacts.** The box front against the stop, checked by the neck
  frame. The stop is set per contact lot from the lot's own measured
  box-to-barrel spread, not the clone drawings' ±0.25 mm.
- **Depth** comes from the neck frame (a line on the image at the wanted
  brush) with a person feeding, or from feed distance with a machine feeding
  ([a2](a2-ribbon-to-fixed-tool.md)).
- **Or no locator at all:** the contact arrives already on its wire
  ([a6b](a6b-flags-by-hand-foot-crimp.md), [a6c](a6c-flags-by-machine-foot-crimp.md)).

**Tolerances.**
- The conductor die wants the barrel's rear edge 0.1–0.2 mm proud of it, a
  bellmouth window of about ±0.1 mm [estimate].
- **Blade on the box's rear walls:** ±0.08 mm, if box length holds ±0.05
  [assumption].
- **Box front on a stop:** fits only if the clone drawings' ±0.25 mm on
  length lies outside box-to-barrel [calc §7]. A caliper on twenty kit
  contacts says.

## The strip length belongs to the contact

JST's 2.4 mm [mfr S6] fits a genuine conductor barrel of ~1.8–2.05 mm. The
clone drawings' barrel (1.25–1.5 mm) and window (0.5–0.8 mm) give 1.60–2.10 mm
by JST's own rule S = E + A/2 + brush, which is exactly the KONNRA clone spec
[calc w3 §7; sl w3 §4]. A 2.4 mm strip on a clone-shaped contact puts bare
strands 0.2–0.5 mm into the insulation barrel; a 1.6 mm strip on a genuine one
puts jacket under the conductor barrel. Both are named defects [mfr S5]. So:
- the strip stop is set from one contact of the lot in use, E and A measured
  under the ELP;
- the side frame looks at the window between the barrels, where either error
  shows.

## Taking the crimp out: lift before drawing back

Drawn straight back while it lies low in the anvil's cradle, a crimp's lance
tip meets the anvil's front face head-on. It either stalls or folds flat, and
a folded lance does not latch in the housing [into-the-housing's
[exchange](../../../exchange/into-the-housing--on--hand-tool-as-press.md)].
- **Lift first:** the crimp is raised 1.0–1.7 mm off the anvil, then drawn
  back [ith ex §2]. The opening limiter leaves that room.
- **The ramp:** a printed ramp on the locator plate's rear edge lifts the
  insulation barrel as the wire is drawn, so a person's pull or a carriage's
  −Y does it without thinking.
- **Optional lance check.** With the tool open and the crimp low, a 2–3 N
  nudge rearward must meet a wall within the expected travel: lance present
  and sprung, checked against steel before the housing. Then lift.

## The proof pull does not go through the tool

- **Not the blade.** 20 N on 0.10–0.20 mm tines cantilevered 2–4 mm reaches
  1,200–16,000 MPa [calc w2 §2].
- **Not the anvil.** A pull with the lance against the anvil face puts
  1.3–1.6× the analog lance retention minimum on it [ith ex §4].
- **Not the dies re-closed.** A grip-side "few newtons" is 30–200 N at the dies
  through the end-of-stroke gain, and die friction adds 4–100 N of grip to a
  20 N test [sl w3 §1]. A crimp with no grip of its own passes.
- **Where it goes:** a6's pull jig, a backed plate on the box's rear walls
  above the floor (16 MPa at 20 N [calc w2 §2]). Whether that plate fits a kit
  contact depends on the same neck photo as the blade; a stepped plate that
  bears outside the crimped barrel's width relaxes it
  ([a6](a6-foot-closed-jig-bench.md), [calc w3 §3]).

## Two frames, judged against the housing

- **The neck frame, at hold.** It looks across the neck and shows three
  things:
  - the blade on the box;
  - the brush length;
  - the lance tip in front of the anvil face.

  The SN head hides the floor side from most angles. a4's open die set sees
  it best.
- **The side frame, after opening.** It checks what insertion needs
  [into-the-housing `handover.md`]:
  - nose bend under ~5° (0.2 mm at the nose);
  - roll within ±10–15° of barrels-up;
  - the closed insulation barrel inside the cavity's end view, wing tips
    tucked;
  - a tab stub ≤ ~0.3 mm on strip contacts;
  - no strand outside a barrel, the brush short of the box, and the insulation
    edge in the window.

  A failed check is a reason to cut the conductor back ~6 mm now, before the
  contact is buried in a housing.

## How the far end helps

Every loom's far end is free while its board end is crimped, and it is
stripped for its Faston, ferrule or IDC [repo: `cable-assemblies.md`]. The
far-end block (Wago 221-415, $28.00 for 25, 6,963 ratings [prime:
B0107SYYGU], or a push-in strip) lets the ESP32 drive and read each conductor:
- **Entry and depth,** the amber and green events above.
- **Identity.** Only the conductor in the tool may read, so a wrong-conductor
  crimp shows before the squeeze. This is the J2 cavity-3 and J4/J7
  discipline, done electrically.
- **After the crimp,** a coarse two-wire resistance through conductor, crimp
  and tool. It cannot grade a crimp (loom 6–34 mΩ against a crimp's
  1–2 mΩ [ribbon-as-pallet]), but its trend over a loom is visible.
- **At insertion,** the same block pairs conductor with cavity at
  into-the-housing's i5 nest (a6).

## Parts

**Printed:**
- cradle, saddle and opening limiter;
- pusher mount, nut carriage and roller foot;
- locator plate, flap arm, ramp and funnel;
- camera arms and a small diffuser hood.

**Bought or on hand:**
- the SN-2549 [repo], or a second one kept for the machine ($22.29 [prime:
  B01N4L8QMW]);
- a 20 mm M4 screw and thumb nut;
- 0.10 mm feeler leaf (Hotop 17-blade set, $8.99 [prime: B08GLN7K1R]) and
  polyimide tape (Amazon, Prime to be confirmed);
- NEMA 17 Tr8×2 external linear stepper (MybotOnline, $27.78, thin, nut not
  anti-backlash [prime: B07TB7FPPP]);
- a TMC2209-class driver;
- a load cell past ~250 N with an HX711 (the Prime S-type row is a 100 kg
  variant at $37.71 [prime: B077YHNNCP]; the 5 kg bar pair at $9.99 is below
  range);
- a pedal (the rotator's deadman pedal is the class [repo]);
- the ESP32 (the bench's DevKitC stack [repo]).

**Worm-winch branch:** the Greartisan 12 V 10 rpm 40 kg·cm self-locking worm
gearmotor, $26.99 [prime: B07YBXB4N7], or the 5840-31ZY at $18.50 [source:
nfpshop.com], plus Dyneema cord ($17.95 [prime: B07BKQLFRB]). It shares a6's
pulley and cord line, and an S-type cell in the cord.

## Which tool goes in the cradle

The cradle holds a handle and pushes a handle. Any ratchet crimper with a
similar handle fits with a different saddle.
- **JST WC-110.** Has the flap locator and wire stop this idea prints, and a
  dedicated 22 AWG cavity. Digi-Key had 147 at $536.51; a replacement WC-110P
  flap is $51.23 [xh-facts §2]. No Prime listing.
- **SN-28B.** Already on the bench [repo]. The same frame takes SN-2549 jaws
  [source: icrimptools.com].
- **The Preciva ferrule crimper and the Haisstronica** are two-handle ratchet
  tools too. A saddle per tool turns the same squeezer into a ferrule or
  Faston station for the looms' far ends [repo: `tools.md`].

## Tried against it

- **"The cradle flexes and the crimp changes."** If the dies bottom, crimp
  height is die geometry. The cradle's compliance changes the force curve, not
  the crimp. If they do not, the crimp depends on where the ratchet releases,
  as in the hand, and the machine squeezes the same way every time.
- **"The actuator pushes at a different spot than a hand."** The roller foot
  sits at the grip's centre. The force table has room for a 1.3× shift
  [calc §2].
- **"Strands splay on the blade."** Green comes at first touch, before any
  buckling force builds.
- **"The contact is dragged forward by the wire."** The blade behind the box
  carries that. A front stop alone lets the contact slide until the box hits
  it.
- **"The lance meets the blade or the anvil."** The tines stop at the floor
  strip's lower face, and the lance hangs below them. The anvil face is met
  only by drawing the crimp back low, which the ramp prevents.

## Rests on

- **[Derek]** He crimps XH by hand with this tool today.
- **[assumption]** The SN-2549's dies bottom at ratchet release.
- **[estimate]** The neck's transition is ≥ ~0.3 mm for the blade case.
- **[assumption]** The box's rear walls are square enough to bear on a blade.
- **[assumption]** The first ratchet tooth falls at or after "contact held". If
  it falls before, "hold" is the actuator holding position, which a lead screw
  does unpowered.
- **[calc]** Grip force is at most a hand's force. This follows from Derek
  doing it by hand, not from a measurement.

Measurements that bear on it:
- a luggage scale on the grip through a real XH crimp;
- a caliper on the grip span open and closed;
- the jaw gap at the opening the limiter will allow;
- the SN-2549 closed against a light;
- the neck, the lance and the barrel lengths on a kit contact under the ELP
  camera;
- the first-tooth position, felt by closing slowly on a contact.

---

Citation keys: **[calc §n]** is [`../calc/hand_tool_press.out.txt`](../calc/hand_tool_press.out.txt);
**[calc w2 §n]** is [`../calc/wave2.out.txt`](../calc/wave2.out.txt);
**[calc w3 §n]** is [`../calc/wave3.out.txt`](../calc/wave3.out.txt);
**[sl w3 §n]** is machine-that-sees-and-learns'
[`w3_on_hand_tool_as_press.out.txt`](../../machine-that-sees-and-learns/calc/w3_on_hand_tool_as_press.out.txt);
**[ith ex §n]** is into-the-housing's
[`exchange_hand_tool_as_press.out.txt`](../../into-the-housing/calc/exchange_hand_tool_as_press.out.txt);
**[prime: ASIN]** is a row of [`../../../sourcing/amazon-prime.md`](../../../sourcing/amazon-prime.md),
observed 2026-09-28 in Derek's signed-in Chrome.
