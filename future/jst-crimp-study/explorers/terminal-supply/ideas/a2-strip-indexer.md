# a2 — Strip indexer: the carrier strip is the feeder, the locator and the handle

Sketch: [`../sketches/a2-strip-indexer.svg`](../sketches/a2-strip-indexer.svg) (schematic;
strip, pins, hold-down and station; the lifter bar and the vane are described
below).
Numbers: [`../calc/terminal_supply.py`](../calc/terminal_supply.py) [ts §n],
[`../calc/wave2.py`](../calc/wave2.py) [w2 §n], [`../calc/w3.py`](../calc/w3.py)
[w3 §n], each with its output beside it; machine-that-sees-and-learns'
[`on_terminal_supply`](../../machine-that-sees-and-learns/calc/on_terminal_supply.out.txt)
calc [mtsl §n].

**Branches.**
- [a2b](a2b-carrier-as-handle.md) keeps a piece of carrier on each contact as a
  handle after the crimp.
- [a2c](a2c-strip-locator-for-hand-tool.md) feeds the strip into the SN-2549
  Derek already owns.
- [a2d](a2d-skip-pitch-crown.md) removes every other contact and runs the strip
  over a crowned anvil, so the ribbon's other conductors can lie flat and
  nothing needs lifting. [x2](x2-crown-then-sort.md) carries a2d on into a
  housing.

**Related.** The applicator this takes apart is [a1](a1-applicator-slow-ram.md).
The watched-station version is machine-that-sees-and-learns
[v1](../../machine-that-sees-and-learns/ideas/v1-watched-nest.md) with this strip
(its C1 reading of a2).

## Picture it

- **Where things start.** A cut strip of 100 SXH-001T-P0.6 contacts, or a reel,
  lies in a printed track running left to right. A unit's 53 contacts are
  ~0.38 m of strip, so a 100-piece strip covers about two units [ts §1].
  - The contacts point toward the front, barrels open upward.
  - The carrier runs behind them, in the plane of the contact floors, joined to
    each contact at the rear of its insulation barrel by a 0.7–1.15 mm tab
    [xh-facts §1, clone drawings].
  - Upstream, where fresh contacts come from, is the left.
  - The splayed, stripped ribbon waits behind the strip, its web in a clamp on a
    two-axis ribbon carriage.
- **Feeding.** A small stepper turns a printed pin wheel whose pins engage the
  carrier's pilot holes, advancing the strip one pitch, ~7.1 mm (the Würth
  WR-WTB 2.50 mm analog: 7.10 mm pitch, Ø1.50 holes, 3.00 mm carrier [mfr
  analog]). A sprung printed hold-down presses the carrier flat everywhere
  except at the crimp station.
- **Locating.** Two tapered steel pins rise from below into the pilot holes one
  pitch either side of the station and pull the strip to within a few
  hundredths. The station contact rests with its floor on a steel anvil; its tab
  sits over a spring-loaded drop plate on the downstream side. The pin wheel
  only had to come within the taper's capture.
- **Measuring the waiting contact.** While the previous crimp is made, the
  camera looks down on the next contact. It fits the conductor barrel's rear
  edge against two fiducials on the anvil block and reads roll, bent wings and
  the lance from the same picture. A fence on a small stepper moves the strip
  along the contact's axis by the measured error, with the pins down and the
  hold-down lifted. Every contact is measured.
- **Keeping the other conductors off the fresh contacts.** A stationary lifter
  bar behind the carrier holds every conductor of the ribbon about 5 mm above
  the carrier plane, except in one notch at the station's line.
  - As the ribbon carriage steps sideways, the notch's sloped sides lift the
    conductor that leaves and lower the one that arrives. Only conductor k lies
    at carrier height. The bar moves nothing; the ribbon moves past it.
  - Without it, fresh contacts stand every 7.1 mm upstream with open wings up to
    3.0 mm wide and 3.2 mm tall. No 4P or 5P fan pitch keeps every other
    conductor off them, and a 3P is clear only at 1.7–2.3 mm [mtsl §2; w2 §1].
- **Presenting the wire.** The ribbon carriage slides conductor k forward, over
  the carrier, into the open U: insulation into the insulation barrel, 0.72 mm
  strands into the conductor barrel.
  - Its first stop is a taught position, a starting guess.
  - The camera fits the insulation edge and both barrels' edges, and the
    carriage moves by 0.7 of the error, approaching from one side, until the
    insulation edge sits in the window. It converges in 3–8 rounds
    (machine-that-sees-and-learns v1, step 5).
  - The window is 0.5–1.0 mm long. The fan's own shortfall (0.3–1.9 mm) and the
    strip-length scatter of torn silicone both exceed it, so the conductor's
    position comes from its own insulation edge as seen, not from the carriage.
- **The look before the stroke.** From upstream, at wing height, the camera
  looks along the strip across the station. The next fresh contact stands one
  pitch away in that line, so a thin white vane, lit from above, slides into the
  4.1 mm gap between the two contacts' wings as a backlight, and out again
  before the stroke. The gate requires: contact present, insulation edge in the
  window, no strand above the wing tips, no conductor other than k below the
  lifter's height.
- **Crimping.** A punch comes down: the upper crimper of an OTP XH knife set in a
  guided block. The ram of a 1-ton arbor press drives it, and a stepper-driven
  lead screw pulls the press lever. The punch holder lands on a hard stop at the
  set crimp height, and a preloaded disc-spring stack lets the drive overrun.
- **Severing.** While the punch holds the crimp down, a small servo pushes the
  drop plate down 0.3–0.5 mm on the downstream side only. Upstream, a flat
  finger clamps the carrier to the track up to an edge 2–3 mm upstream of the
  station tab. The tab parts against the anvil's rear edge, as an applicator's
  floating shear does [prior-art §3, TE 408-32162]. After the next index the
  bent carrier lies 4–5 mm downstream of the new station tab, in scrap [w2 §9].
  The next contact's own tab is never bent.
- **Leaving.** The ram rises. The carriage lifts conductor k, now carrying its
  free contact, up and back, and shifts to conductor k+1. The pins drop, the
  strip indexes, and the empty carrier with its tab stubs runs on to a take-up
  spool or a snip bin.
- **What the person does.** Threads a strip every ~2 units (100-piece) or ~9
  units (500-piece), or mounts a reel once; empties the scrap bin; splays and
  strips, and inserts, unless other stations do; answers the queue when a
  ribbon end is stopped.

## What locates what

| Direction | What sets it | Tolerance | Note |
|---|---|---|---|
| Along the strip (X) | tapered pins in the neighbours' holes | pin 1.45–1.48 mm in a 1.50 hole: float ≤ 0.035 mm radial, zero when a tapered pin is driven home [ts §2] | Non-accumulating. Counting pitches on a sprocket would drift ±0.15 mm over a unit [ts §2] |
| Along the contact (Y), contact | carrier edge on a stepper fence, set per contact from the waiting contact's picture | an edge fit repeats to 1–7 µm against a ±0.1 mm bellmouth window [mtsl §9] | Tab length varies 0.8 ± 0.2 (HDGC) and 1.00 ± 0.15 (DLL) between brands; within one strip it is unmeasured and does not matter, because each contact is measured |
| Along the contact (Y), conductor | the ribbon carriage, steered by the insulation edge as seen | converges in 3–8 rounds to a fraction of the 0.5–1.0 mm window | The taught position is a starting guess |
| Height (Z) | anvil top, the carrier track level with it | — | The carrier and the barrel floors are one plane |
| Roll | carrier flat on the track and the contact floor on the anvil; tab never bent before its crimp | read from the waiting contact's picture every cycle | A drift in roll over a strip is the first sign of a kink or a worn pin |
| Crimp height | hard stop between punch holder and anvil block | the stop's repeatability, ~0.01 mm [estimate] | The stop is where the tooling was, not what the crimp became: a silhouette height on each crimp and periodic pulls to failure close that loop |

**The reference for "fixed" is the anvil block.** The pin carriage, the fence,
the camera fiducials and the punch guide are all mounted to it. The arbor press
frame only pushes.

**Where precision is needed.** Only as the pins seat and as the punch meets the
wings. Indexing can be sloppy (the pins take out ±0.3 mm); wire entry can be
sloppy (an open U is a funnel, and the picture sets where the insulation edge
lands). The contact must not be tilted when the punch lands: twisting and
rolling in the MKS-L manual trace to "the position of terminal is not right on
crimper anvil" [mfr MKS-L §7-8, §7-9]. Holding the carrier flat up to the tab,
and bending it only downstream of the tab, is what prevents it.

## What drives and carries the crimp force

- **Force.** About 0.8–2.6 kN at the bottom of the stroke; plan on 3 kN
  [xh-facts §4]. The ram pushes the punch holder through the disc-spring stack,
  preloaded above the crimp force. The holder lands on the anvil block's stop
  face, so the loop closes punch holder → stop → anvil block, not through the
  press's cast frame.
- **Drive.** A 1-ton arbor press: the VEVOR AP-1 ($61.90, Prime, 150 mm opening,
  81 mm throat, lever ratio not stated [sourcing/amazon-prime.md]) or Harbor
  Freight 59766 ($79.99, 139.7 mm opening, 20:1 lever [source, via
  force-and-form]). Either is too short for an applicator ([a1](a1-applicator-slow-ram.md))
  and takes a 60–100 mm knife-set die block. At 20:1, ~150 N at the lever end
  gives ~3 kN; a NEMA 17 on a 2 mm-lead screw pulls ~350 N [estimate].
- **The drop-shear.** 50–160 N [xh-facts calc C1] through a lever. A metal-gear
  hobby servo gives ~45 N at a 20–25 mm arm [ts §9], so a 3–4:1 cam or lever
  closes the gap.
- **A settable stop.** The hard stop can sit on a stepper-driven wedge
  (machine-that-sees-and-learns v3). The anvil block then sweeps its own crimp
  height in 0.02 mm steps on this ribbon, and later holds the height it found.

## Why the tab is sheared by moving the carrier down

The wire lies across the tab. Its insulation's underside touches the carrier's
top face: the insulation centre is ~0.85 mm above the floor plane and its radius
is 0.85 mm [calc from xh-facts §7].

- A blade or cutter jaw from above would have to pass between the tab and the
  wire, and there is no gap. The same geometry rules out a flush cutter after
  the crimp for strip contacts.
- Bending the carrier off takes 1–5 cycles [ts §9] and cannot be done at one tab
  of a continuous strip.
- Pushing the carrier down, away from the wire, while the contact is held on the
  anvil, is what applicators do, at any speed.
- Only the downstream side drops. The carrier yields at 0.16 mm of drop
  whatever its width, and a 0.3–0.5 mm drop leaves 0.14–0.34 mm of set, a kink
  of 1.7–4.2° [mtsl §6]. With the upstream carrier clamped to an edge just
  upstream of the station tab, the kink forms in carrier that is scrap after the
  next index [w2 §9].

## How it knows it worked, and backing out

- **Signals:**
  - the pins reached home (a switch on the pin carriage);
  - the waiting contact's picture: axial offset, roll, wings, lance;
  - the pre-stroke gate picture;
  - the ram at its stop (a switch in the spring stack) and a force trace from a
    load cell in the lever link;
  - the after-crimp picture once the carriage lifts the crimp clear: brush,
    window, bend-up, bend-down, twist. Crimp height by silhouette in a booth or
    in line (machine-that-sees-and-learns v5).
- **A contact that fails its look before the wire arrives** (bent wing, rolled,
  lance flattened): the drop plate shears its tab with no wire present, and a
  puff of air or a sweeper arm clears it into a reject cup. Nothing uncut ever
  travels downstream.
- **A crimp that fails its look after the stroke:** a single conductor cannot be
  re-crimped [digest]. The machine stops that ribbon end, spends no more
  contacts on it, queues "cut back and restart J5's end?" with the photo, and
  moves to the next ribbon end.
- **The log** carries the strip or reel lot and the index count into each
  crimp's record.

## Problems and repairs

1. **A pin in the station's own pilot hole** would rise into the wire, because
   the hole lies on the contact's centreline under the wire's path. Repair: pins
   in the holes one pitch either side.
2. **Severing a pitch later** would leave crimped contacts on the strip, and the
   next index would drag the whole ribbon sideways. Repair: sever at the station
   before indexing. [a2b](a2b-carrier-as-handle.md) goes the other way.
3. **Cutting from above** is blocked by the wire. Repair: drop-shear.
4. **A drop-shear between the pins** would kink the carrier next to the upstream
   contact and roll it by up to half its roll window [mtsl §6]. Repair: the
   downstream side drops against a clamped upstream edge. The tab stub's shape
   with a one-sided shear edge stays open.
5. **The ribbon's other conductors land on the fresh contacts** at every 4P and
   5P fan pitch [mtsl §2]. Repair: the notched lifter bar. A conductor lifted
   ~3.5 mm at 10–15 mm from the web keeps ~1.2–2.2 mm of that lift when
   released; at 25–30 mm it keeps a few tenths [w2 §4]. The set does no harm
   during crimping, and whatever combs the conductors to 2.5 mm for insertion
   undoes it. The other repair is [a2d](a2d-skip-pitch-crown.md): take the fresh
   contacts out of the conductors' plane.
6. **One taught conductor position** cannot absorb the tear scatter of silicone
   stripping or a conductor that slipped in its slot. Repair: the insulation
   edge as seen steers the carriage. Cutting and stripping after fanning,
   against one datum line, removes most of the repeatable fan shortfall at its
   source.
7. **The view along the strip meets the next contact.** A camera tilted to see
   over it hides the near wing tip, and a neighbour whose wings stand 0.25 mm
   taller blinds the view [mtsl §1]. Repair: the lit vane in the 4.1 mm gap. Its
   clearance to the punch holder and to the lifted conductors (which must sit
   above the vane) stays open.
8. **Strip ends.** The first contact of a new strip needs the pin wheel ahead of
   it; the last few leave the pin wheel before the station. Repair: a second pin
   wheel downstream, or tape the new strip's head to the old strip's tail, as
   SMT feeders splice tape. Without either, a 100-piece strip loses ~4 contacts.
9. **The wire's axial push** (~0.01–0.1 N [estimate]) against a carrier held by
   two pins is negligible.
10. **The lance and the knife-set anvil.** A flat anvil's front edge must stand
    behind the lance tip and ahead of the conductor barrel; on the clone ranges
    that fits about half the cases [w3 §4]. A knife-set anvil cut for these
    contacts carries its own relief [assumption]; one side look settles it.

## Steps covered, and what it hands back

- **Covers:** placing the contact (index, pins, per-contact fence correction);
  holding it (pins, anvil, punch); placing the conductor in it (carriage steered
  by the picture, lifter for the others); crimping; severing; refilling from
  strip; verifying before and after the stroke; backing out.
- **Hands back:** splaying and stripping (other views; the fanned pose should be
  the one they cut and strip in); insertion. Crimped contacts leave free on their
  conductors, with a short tab stub, in the pose the carriage holds them.

## Printed and bought

| Part | Printed / bought | Evidence / note |
|---|---|---|
| Strip track, fence carriage, sprung hold-down, upstream clamp finger, pin wheel, pin carriage, lifter bar, ribbon carriage, take-up spool | printed (PETG/PET-CF; TPU pads where the carrier rides) | — |
| Pilot pins | 1.448 mm pin gauges from the Accusize 50-piece set (Prime, $45.58, 60–62 HRC [sourcing/amazon-prime.md]), tip ground to a taper | drill blanks near 1.45 mm: no Prime listing found |
| Punch + anvil | OTP "XH2.54" knife set (replacement upper crimpers and lower anvils) | eBay 376757376428, AliExpress 3256803331644772 titles seen in search [source, 2026-09-28]; no Prime listing found |
| Die holder, anvil block, stop face | machined steel or aluminium, or printed PET-CF with a steel insert at the stop | The stop face must be steel |
| Press | VEVOR AP-1 1 t arbor press (Prime, $61.90) or Harbor Freight 59766 ($79.99) | [sourcing/amazon-prime.md]; [source] |
| Lever drive | Iverntech NEMA 17 with integrated Tr8×2 screw (Prime, $27.99, thin listing) | [sourcing/amazon-prime.md] |
| Strip feed and fence | ELEGOO 28BYJ-48 + ULN2003, 5-pack (Prime, $14.99) | [sourcing/amazon-prime.md] |
| Drop-plate, vane and sweeper actuators | MG996R 4-pack (Prime, $18.99); MG90S 4-pack (Prime, $13.88) for the vane | [sourcing/amazon-prime.md] |
| Camera | ELP 16 MP autofocus USB (on hand) | [repo tools.md] |
| Contacts | SXH-001T-P0.6 cut strip: Digi-Key 455-1135-100-ND $4.71/100 (3,100 in stock), -500 and -1000 lots; LCSC C140573 $0.0127 @ 100 (406,500 in stock) | [xh-facts §6]; no Prime listing found for strip |

## Contribution

The applicator's functions separated into slow stations, each observable,
retryable and printable around three bought steel pieces (pins, punch, anvil):
feed by a counted stepper; locate by pins with a home switch and a fence that
corrects each contact; crimp by a ram and a hard stop; sever by a drop-shear
that bends only scrap. The strip is the cheapest locator in the problem, and the
carrier's own geometry answers "what holds the contact before and during the
crimp". Its cost is that the next contact stands beside the station, which the
lifter and the vane pay for here and [a2d](a2d-skip-pitch-crown.md) pays for
differently.

## Major unresolved problems

- **The die outside its applicator.** Whether an OTP knife set keeps
  crimper-to-anvil centring (checked in the MKS-L "with a loupe" [mfr §6-4]) in a
  simple holder, and its crimp height on 60 × 0.08 mm strands in 1.7 mm silicone.
- **Real SXH carrier pitch and pilot-hole geometry.** Not dimensioned in any JST
  document read. One Digi-Key 100-piece strip settles it.
- **Tab stub quality** from a one-sided drop-shear. JST faults both "no cut-off
  length" and "too much" [xh-facts §1].
- **Whether a 0.2 mm carrier stays flat** in a printed track under a sprung
  hold-down, and whether a cut strip arrives kinked from its bag.
- **Crowding within ±7 mm of the station:** vane, upstream clamp finger, lifter
  notch, punch holder and camera line.
- **A J1-style pair of ribbons** at the lifter: crimped as two ribbons, one
  after the other.

## What each conclusion rests on

- **Derek:** the priority on placing, holding and crimping [brief].
- **Facts [mfr, source]:** side-feed carrier geometry and tab (clone drawings,
  xh-facts §1); MKS-L fault causes; stock and prices [xh-facts §6]; Prime
  listings [sourcing/amazon-prime.md].
- **Calculations [calc]:** pin float and pitch drift [ts §2]; carrier set from a
  drop [mtsl §6]; where the kink ends [w2 §9]; neighbour clearances [mtsl §2,
  w2 §1]; lifted-conductor set [w2 §4]; lance window [w3 §4].
- **Estimates:** crimp force [xh-facts C1]; stop repeatability; wire push;
  lever-screw pull; adjacent-hole accuracy of a few hundredths.
- **Assumptions:** pitch ~7.1 mm (Würth analog and HDGC scaling); the OTP knives
  are usable outside their applicator; copper's set model for the lifted
  conductors (elastic-perfectly-plastic strands, 70 MPa yield).
