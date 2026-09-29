# hand-tool-as-press on procedure-is-the-machine

Wave 2 exchange.
- **The view doing the reading:** *the crimp tool is already the machine*
  ([`../explorers/hand-tool-as-press/summary.md`](../explorers/hand-tool-as-press/summary.md)).
- **The view being read:** *the sequence and the division of labor are the
  design* ([`../explorers/procedure-is-the-machine/summary.md`](../explorers/procedure-is-the-machine/summary.md)).
  All seven idea files, the notebook and every calc output were read.

What I bring to their ideas:
- **A crimp head that exists.** The bench's SN-2549 ($17.99–20.99, a validated
  XH nest) closes its own force loop. It can be squeezed by a pusher (a1),
  carried tip-down on a light gantry (a3), or have its dies moved into a die set
  with a stop and a disc-spring stack (a4).
- **A thin blade in the contact's neck** (a1). It locates the box's rear
  shoulder, stops the strand tips, senses touch, and carries a proof pull.
- **The loom's far end as an electrode array** (a1, a2).
- **Loose-contact supply that keeps hands off the contact at each crimp:** the
  revolver (a2b) and the post column (a3).

Citations:
- **[calc H §n]**: this exchange's numbers,
  [`../explorers/hand-tool-as-press/calc/exchange_procedure.py`](../explorers/hand-tool-as-press/calc/exchange_procedure.py)
  with output [`exchange_procedure.out.txt`](../explorers/hand-tool-as-press/calc/exchange_procedure.out.txt).
- **[calc H1 §n]**: my wave-1
  [`hand_tool_press.out.txt`](../explorers/hand-tool-as-press/calc/hand_tool_press.out.txt).
- **[calc P name §n]**: procedure-is-the-machine's calcs in
  [`../explorers/procedure-is-the-machine/calc/`](../explorers/procedure-is-the-machine/calc/).
  This includes their own wave-2 `exchange_borrowed.out.txt`, which reached
  one of the breaks below first.
- **[MKS-L]**: JST's side-feed applicator manual, as read in
  [`borrowed-machines--on--ribbon-as-pallet.md`](borrowed-machines--on--ribbon-as-pallet.md)
  ("A fact base used throughout").

---

## p1 Cassette and benches

### Break p1-1: the slotted presser drops neighbours into the strip's own hardware

**Their own finding, carried further.** Their
[calc P exchange_borrowed §1](../explorers/procedure-is-the-machine/calc/exchange_borrowed.out.txt)
already says the presser "does not work over an attached strip". Here is the
conflict part by part.
- **Where the carrier runs.** The side-feed carrier joins at the rear of the
  insulation barrel, in the contact's floor plane, and runs across the row (X).
  Every neighbour, on its way from the comb to its tip, crosses the carrier
  line.
- **What sits on each side of the anvil.**
  - Upstream: the feed plate, guide plates and pressure plate, at strip height,
    for several centimetres.
  - Under the tab line on the wire-entry side: the shear blade supporter and
    the scrap chute. The floating shear (158) is driven down there by its punch
    (157).

  [MKS-L]
- **What happens to each neighbour.**
  - A neighbour at k±1 pressed 7 mm down is pushed into the shear supporter and
    the scrap chute.
  - Neighbours at k−2 and k−3 are pressed onto the feed and pressure plates.
  - Where the presser cannot push them down, they lie on the waiting contacts'
    open wings, 7.1 mm apart, in the punch's path.
- **The punch width.** "The punch above can be as wide as it likes" does not
  hold with a strip attached. Tooling half-width at the wings is limited to
  ≤5.4–5.7 mm by the next waiting contact
  ([borrowed-machines exchange calc](../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt)).

**Physical consequence.** The OTP applicator route that p1, p2, p3, p4 and p5
all name for their tooling ([p1](../explorers/procedure-is-the-machine/ideas/p1-cassette-and-benches.md)
"Anvil and punch") cannot sit under a dropped row. Any design that keeps the
presser has to be custom thin tooling.

**Repairs and branches.** Each changes a different thing.

**R1: lift k, and make the crimp head something that fits above the row.**
Invert the presser into a stationary *lifter* at the station line: a finger
under the cassette that raises whichever key is indexed over it. Every other
conductor stays in the row, untouched.
- **The head.** My a3 module hung tip-down: the SN-2549 with its pusher bolted
  to its own lower handle, the flap blade in the neck, and jaws closing across
  the row (X). The neighbours pass under the jaw tip.
- **The lift.** By their own formula, the lift must be at least the jaw's reach
  past the conductor axis plus 1.85 mm
  ([calc P selector_and_bow §1](../explorers/procedure-is-the-machine/calc/selector_and_bow.out.txt)).
  For a tip-down SN jaw that reach is the distance from the usable nest to the
  jaw tip, **t**, still unmeasured (my a3's first open problem). For t = 2–6 mm
  the lift is 3.9–7.9 mm.
- **The contact** arrives in the tool, not on the anvil. It comes from a post
  column (a3) or a revolver (a2b). Bench B's pawl-fed strip goes away.
- **What it changes.** Bench B is:
  - the cassette slide (X);
  - one lifter servo;
  - a Y–Z stage carrying a ~0.8 kg module that closes its own force loop.

  It needs no ram, no steel C-frame and no applicator.
- **What it leaves uncertain.**
  - t, and the jaw's shape near the tip.
  - The lifted conductor's set (Break p1-2).
  - Crimp height becomes whatever the SN-2549's dies give. JST calls hand-tool
    heights fixed [xh-facts §2]. a5's two-squeeze plier is the branch where
    height is a setting.

**R2: cut the contact free before it reaches the anvil, and keep the narrow
anvil.** A 1.6–1.9 mm hardened fin standing ≥7–9 mm above its base is an
applicator anvil plate without the applicator around it.
- **Buckling.** Fixed at the base and free at the top, a 1.6 × 4 × 10 mm steel
  fin buckles near 6.7 kN. With its top guided by the punch it is far higher.
  Both are above the 3 kN design force [estimate, Euler on the fin].
- **Holding the contact without its carrier.** It needs the blade behind the
  box shoulder (a1) or the pilot-hole stub (a2).
- **Making the fin.** Cut down from an SN jaw piece (a4's "narrowing a hardened
  jaw piece" risk), or the anvil plate out of an OTP applicator.
- **What it leaves uncertain.**
  - Whether either can be cut to that height and width without cracking.
  - Where the contact supply sits so it does not block the dropped neighbours.
    Stub, post or revolver must come in from above or from the front.

**R3: keep the strip and build the tooling thin.** All strip hardware (guides,
pressure plate, feed finger, shear and chute) has to live between the floor
plane and ~3–4 mm below it in every neighbour's column. The anvil fin rises from
a base below −9 mm.
- **What it leaves uncertain.** It amounts to designing an applicator. It is
  kept visible because it is the only branch that keeps pilot-hole location and
  in-stroke tab shear together with the presser.

### Break p1-2: every earlier conductor carries the presser's bend when its turn comes

**Conflict.** The strands yield below a ~40–77 mm bend radius for strand
yield of 120–60 MPa. The digest's ~67 mm sits in that range.
- **When each conductor is pressed.** At bench A (strip) and at bench B
  (crimp), conductor k is pressed ~7 mm down during every other key's cycle
  before its own. That is eight times for J1's ninth key.
- **Where the bend happens.** p1 says neighbours bend "over ~20 mm". The
  presser has to act near the tips, within the 10–20 mm stick-out past the
  comb.

**Numbers** [calc H §1]. Cantilever from the comb face, tip pressed 7 mm and
released. The model is elastic-plastic strands with an elastic silicone tube, in
small-deflection theory, so the figures are rough at short lengths.

| Free length | Residual drop | Tip pull-back |
|---|---|---|
| 10 mm | 4.3–5.7 mm (61–81 % kept) | 1.0–1.8 mm |
| 15 mm | 2.7–4.7 mm | 0.25–0.8 mm |
| 20 mm | 1.0–3.4 mm | 0.02–0.3 mm |
| 30 mm | 0–0.7 mm | ~0 |

Repeating the same press adds little set. The first press does it [estimate].

**Physical consequence.**
- **Capture height.** Key 1 arrives level. Keys 2…N arrive 1–5 mm low at their
  tips.
  - The fork closes sideways at level height.
  - The V-jaws close sideways.
  - The lay-in finger assumes a start ~1.5 mm above the barrels.

  A conductor 3 mm low meets the anvil fin's side or passes under the contact's
  floor.
- **Axial.** The tip is short by up to ~1.8 mm at short free lengths. The pull-
  back differs between key 1 and the rest, against a ±0.3 mm window
  ([calc P transfer_capture §3](../explorers/procedure-is-the-machine/calc/transfer_capture.out.txt)).
- **Insertion.** At bench C the fronts are not on one line or in one plane,
  which gang insertion needs to ±0.3 mm.

**Repairs.**
- **Capture from below.** A V-fork rises to a fixed height under key k, lifting
  it to level before the jaws or finger act. This changes the fork from a
  sideways close to a vertical capture. What stays uncertain is the axial pull-
  back, which the V does not undo.
- **Bend each conductor once (R1's order).** Lift k, then trim, strip and crimp
  it in that pose. Their own selector_and_bow §1 already says "Trimming each
  tip in the lifted pose, at the crimp station, removes it". k's set then does
  not matter to its own crimp.
- **Square the fronts before insertion.** A comb squares the fronts before
  bench C, pushing each crimped contact back to level plus the springback.
  Copper that yields also re-yields. This is "undone deliberately", as the
  digest says.
- **A longer split** (≥30 mm free) makes a 7 mm press nearly elastic. The cost
  is split length behind the housing, which is Derek's question.

What rests on assumptions: strand yield (60–120 MPa) and silicone modulus
(2–6 MPa). into-the-housing reached the same kind of set for my own lifter and
fork ([calc](../explorers/into-the-housing/calc/exchange_hand_tool_as_press.out.txt)
§6).

**One bench-top test settles it.** Press a split conductor 7 mm down at 15 mm
free length, release it, and photograph it with the ELP camera.

### Break p1-3 (also p5): the fork sits on the tab-and-shear line through the stroke

**Conflict** [calc H §2]. From the clone drawings, measured behind the strip
line:
- the insulation barrel ends 1.05–1.9 mm back;
- the tab runs to 1.75–3.05 mm;
- the carrier edge, which is the shear line, is at 1.75–3.05 mm.

The fork "closes on conductor k 3 mm behind the strip line", which is on the
tab or the carrier edge. The applicator's shear punch and floating shear act on
that line [MKS-L]. In p5's timing table the fork closes at 30–70° and opens at
330–360°, so it stays in place through the punch stroke at 170–240°.

**Consequence.**
- The steel punch stack and shear come down on a printed fork.
- In p5 the eccentric is a displacement source, so the fork is crushed or the
  punch is held off bottom dead centre. That is p5's over-travel hazard,
  triggered on every stroke.

**Repairs.**
- **Release the fork during the stroke.** Open it after lay-in, around
  150–170° in p5, and hold the wire through the stroke with a ram-mounted
  spring leaf. JST's MKS-L has exactly this as a factory accessory, the wire
  hold spring [MKS-L]. By the time it opens, the open wings and the lay-in
  finger already confine the conductor laterally.
- **Move the fork back 5–6 mm**, behind the carrier. The free length to the tip
  grows from 5.4 to 7.4–8.4 mm. A light 0.02 N brush then moves the tip 0.15–
  0.28 mm, inside the ±0.33 mm lateral window [calc H §2].
- **Uncertain:** the carrier's width, which is unmeasured and sets how far back
  "behind the carrier" is.

With a hand-tool head (R1) there is no carrier or shear at the rear. The rear
face is free for a printed funnel.

### Break p1-4: the axial chain leaves out the contact's own reference

**Conflict.** p1's axial chain lists:
- trim blade;
- cassette;
- strip length;
- lift scatter.

It does not list where the contact sits along its axis on the anvil
([calc P transfer_capture §3](../explorers/procedure-is-the-machine/calc/transfer_capture.out.txt)).
With strip, the pilot hole holds the contact to ±0.075 mm. p1's loose-kit
branch has no such reference.

**Numbers** [calc H §6]. Without lift scatter (k is never lifted in p1), the
chain is ±0.21 mm RSS. Adding the contact's reference:

| Contact located by | Chain RSS | With camera-measured bare length and Y correction |
|---|---|---|
| Pilot hole (strip) | ±0.23 | ±0.11 |
| Box rear shoulder on a blade (a1) | ±0.23 | ±0.11 |
| Box front on a stop (loose kit contact) | ±0.33 | ±0.26 |

The box front carries the clone drawings' ±0.25 on overall length. Where that
tolerance sits is not drawn [calc H1 §7].

**Consequence.** Loose kit contacts on p1's anvil, stopped by the box front,
use the whole ±0.3 mm window by themselves.

**Repairs.**
- **Transfer the a1 blade.** A 0.3 mm spring-steel blade drops into the neck
  between the conductor barrel and the box, and bears on the box's rear
  shoulder.
- **Transfer the camera-and-carriage row of my calc H1 §7.** At bench B the ELP
  camera measures the bare length, and the slide moves the cassette in Y so
  the insulation edge lands mid-window. This removes the ±0.20 mm strip term,
  which is the largest.
- **What stays uncertain.**
  - Whether the neck is long enough for the blade. p1's proof-tug hook behind
    the box needs the same neck, so one measurement under the ELP camera serves
    both.
  - Whether the camera can see the insulation edge on black silicone. A
    backlight makes the bare copper a silhouette.

### Transfers and combinations for p1

- **Combination: the cassette + a1, a first powered bench B (stage 1.5).** Each
  side contributes this.

  | From p1 | From a1 |
  |---|---|
  | The cassette, with its keys, blanks and loft | The SN-2549 squeezer lying on its side |
  | p5's printed rack at 2.5 mm, as a hand-lever escapement in X | The flap blade |
  | A lifter lever for key k | The pusher and load cell |
  | | The far-end continuity light |

  - **The cassette rides a Y slide.** The person indexes (lever), lifts (lever)
    and puts a contact on the locator. The squeezer closes to hold. The person
    slides the cassette toward the tool until the light shows that the strands
    touch the blade. Then the pedal.
  - **The machine** does hold, crimp, the force curve, and the identity check.
  - It works with loose kit contacts on day one. The cassette's keys, not the
    person's fingers, hold the conductor.
  - **Uncertain:** the SN's first ratchet tooth relative to "held, wire still
    enters" (a1's open problem).
- **Transfer: the far end rides on the cassette.** A small block on the
  cassette's tail tray takes the loom's far end. Two ways to touch it:
  - needle pins pierce each conductor within the length that will later be
    stripped or trimmed away for its Faston, ferrule or IDC;
  - or pogo pins touch the cut face, as in ribbon-as-pallet a6.

  Pogo contacts under the cassette connect it to each bench's dowel plate.

  Then, at bench B, the grounded anvil or blade touching conductor k's strands
  reads which far-end conductor it is, **before the crimp**.
  - A J4/J7 crossing laid into the wrong key in the loft is caught at the first
    crimp, not at the unit's final test. The loft crossing is the person's most
    error-prone act in p1.
  - Bench C's header test becomes pin-to-pin, not only adjacent shorts.
  - p1b's "cassette-ID misread runs the wrong program" gets a second, physical
    check.
  - **Uncertain.** How the pierce pins' contact behaves on tinned strands through
    0.49 mm of silicone [assumption]. Touch-off only needs "open" against "under
    ~100 Ω", so it is a low bar.

## p1b Carousel joins the benches

Everything in p1-1 to p1-4 carries over. Two points are specific to p1b:
- **Bench B reaching in.** "Bench B … can sit outside the ring, reaching in
  only with its slide, presser and anvil." With a steel ram frame and a strip
  reel, what reaches in is the bulky part.
  - With R1, what reaches in is a two-axis stage and a ~0.8 kg module whose
    force closes inside itself. The lift pins that put the cassette on the
    station's reference carry only positioning loads.
- **The redo lap.** Station A splits the extra 6 mm, and the conductors that
  were pressed on the first lap keep that set (Break p1-2). The second lap's
  fork and jaws need the capture-from-below repair even more.

## p2 Still ribbon, tools come to it

### Break p2-1: the crimped contact has no way out of a strip-fed C-frame head

**Conflict.**
- **How the conductor went in.** The conductor entered the head axially,
  through a V lead-in behind the insulation barrel, over the carrier and tab
  [calc H §2].
- **Which ways out are blocked.** After the crimp and shear:
  - withdrawing the head along +x slides the anvil forward under the contact,
    so the crimped box (1.95 × 2.4 mm) is dragged backward through the head's
    own rear lead-in and over the strip track;
  - the head cannot drop, because its lower body is already within ~6 mm of
    the unlifted row (Break p2-2);
  - it cannot go up, because the crimp sits in the anvil's cradle under the
    rising punch.

  This is my a2's "unloading rearward" problem, in p2.
- **Consequence.** The crimp jams in the lead-in, or the pull strains a fresh
  crimp through the lead-in's throat.

**Repairs.**
- **Lift the wire out.** The selector hook rises a further ~3 mm after the
  punch rises, lifting the crimp out of the anvil. That is an applicator's
  normal exit: the operator lifts the wire out. The cost is ~11 mm total lift
  and more set in k (Break p1-2 numbers). The p2 bow calc already runs at
  8–11 mm.
- **Open the lead-in.** Split the V lead-in into two halves on a servo, so the
  crimp can leave rearward.
- **Transfer (a3): a head whose jaws open across the row.**
  - The SN module hangs tip-down. Opening the jaws frees the crimp sideways.
  - The module rises +Z, and the crimp leaves through the mouth with no further
    lift of k.
  - The contact is held by the flap blade at the neck until then, so the proof
    pull happens in the same place.
- **Uncertain:** the nest-to-tip distance t, as in R1.

### Break p2-2: the head's anvil body against the 8 mm selector lift

**Conflict.** With k lifted 8 mm, everything of the head below k's axis must
stay above the neighbours: ≤ 8 − 0.85 − 0.85 − 1 ≈ 5.3 mm [calc P selector_and_bow
§1, inverted]. That includes the anvil, its base, the strip track and the
pawl.
- **Consequence.** An anvil and track taken from an applicator do not fit.
  p2's own text cites the OTP route through p1 for the anvil set. The head has
  to be built thin below the strip plane (as R3), or the lift grows.
- **Repair.** A tip-down hand-tool jaw needs only t below the axis. If t is
  ≤3.5 mm, an 8 mm lift already clears it.

### Transfer and combination for p2

- **Combination: p2's order and turret, with an a3 module as the crimp head.**

  | p2 keeps | a3 contributes |
  |---|---|
  | The never-re-gripped clamp | A self-closing tip-down module of ~0.8 kg (p2 estimates its C-frame head at 1–2 kg) |
  | The per-conductor order strip k → crimp k → look → insert k | A post-column or revolver station on the drum in place of a strip reel on the head |
  | Crossings by program | Electrical touch-off and identity through the far end at every conductor |
  | The drop stage | The flap blade for the proof pull |

  - **Uncertain.** How the turret brings the module to the post column and
    back. That is one more tool position on the drum, or a fixed post column
    the x slide reaches.

## p3 Terminate at the spool, cut last

### Transfer p3-T1: the slip ring is a far-end electrode during the crimp, not only after it

p3 tests through the spool after gang insertion: opens, shorts and identity
through ~0.1–0.9 Ω of spool
([calc P spool_test §1](../explorers/procedure-is-the-machine/calc/spool_test.out.txt)).
The same circuit is live while each conductor is being crimped. With the
anvil, contact or blade grounded, three things come from it:
- **Touch-off.** Strands meeting the contact or a blade read "closed" on
  exactly one conductor. That is an axial event in the machine's own frame,
  where p3 today uses a light beam once per end.
- **Identity before the crimp.** The conductor about to be crimped is checked
  against the loom's pin map. J2's trimmed conductor and J7's trimmed 3P
  conductor are confirmed absent.
- **A coarse after-crimp check** in series with the spool. It sees an open, not
  milliohms (their own calc).

This costs nothing p3 does not already buy (Adafruit 736, $14.95).

### Break p3-1: step 4 inherits p1's bench B

p3's step 4 uses "p1's presser, fork and lay-in finger" with contacts from a
strip reel. Breaks p1-1, p1-2 and p1-3 apply unchanged. The ribbon at p3's work
clamp is exactly "a ribbon that never moves", so R1 fits it without change.

### Combination C1: p3's spool and clamp, a3's travelling tool

- **p3 contributes:**
  - the spool as carrier;
  - the belt feed and the clamp-face beam;
  - recovery that costs 6 mm of spool, never a loom;
  - the order (XH end before any far-end work);
  - batching by spool;
  - gang insertion from a housing tube;
  - the slip ring.
- **a3 contributes:**
  - the tip-down SN module on a laser-engraver-class gantry above the clamp;
  - a lifter under each fan-comb slot;
  - the post column (loose kit contacts plugged on in a batch, or a strip
    pushed on and gang-cut);
  - electrical touch-off and identity through the slip ring;
  - the flap-blade proof pull;
  - the tool rack (Klein stripper, KATA cutter, housing holder) on the same
    kinematic mount.
- **What becomes possible.**
  - A spool run of 35 ends and 140 crimps with no applicator, no ram and no
    steel frame.
  - Every crimp is checked for identity before it is made.
  - The far-end terminal block in my a1–a3 is no longer needed. That block
    needed the far end stripped first, against p3's order.
- **What stays open.**
  - t.
  - The lifted conductor's set, for the fronts before gang insertion.
  - Web splitting and stripping at the clamp, as p3 already lists.
  - Whether a 0.8 kg module and its cable bundle sit well over a clamp that
    also has a belt feed and a guillotine in line.

### Far ends: a step p3 hands back that my view can take

p3's notebook sets aside "terminate both ends on the machine" because the far
ends are Fastons, ferrules, IDC and screw terminals on branching legs. Those are
hand-tool crimps on the bench today:
- Haisstronica for insulated terminals;
- the Preciva ferrule crimper;
- the Klein VDV427 punchdown.

Each one sits in an a1 squeezer saddle as a person-paced station. The person
presents, and the machine squeezes, logs the curve and photographs the result.

By p4's own accounting this saves no minutes. What it buys is the same thing
p4 buys: the same squeeze every time and a record. For ferrules into Wago lever
nuts, a pull and a photo are the whole check.

## p3b Ribbon AMS

C1 applies unchanged at p3b's wide clamp. A pair enters as one wide ribbon, and
both spools' slip rings give identity across all nine conductors of J1 at every
crimp. Whether the lifter under the fan comb can reach a conductor at the seam
between the two ribbons without disturbing the other ribbon's edge conductor is
a new clearance to check.

## p4 The person presents, the machine takes

### Break p4-1: the proof pull is taken through the dies

**Conflict.** "The punch stays at bottom dead centre, holding the contact,
while the clamp pulls back against a spring set to 15–20 N." The punch at bottom
dead centre is not holding the contact by its box. It is clamping both barrels
with whatever die force the held position leaves in the loop.

**Numbers** [calc H §3]. Friction on clamped barrels at μ 0.15–0.5:

| Held die force | Friction on the barrels |
|---|---|
| 200 N | 30–100 N |
| 800 N | 120–400 N |

Holding at the hard stop leaves most of the 0.8–2.6 kN crimp force in the loop.

**Consequence.** A crimp with no grip of its own passes the 20 N pull. The
check tests the clamp's grip on the silicone, not the crimp.

**Repair.**
- **Pull through the box, with the dies open.** The punch rises, and a blade
  drops into the neck behind the box's rear shoulder (a1). Or a hook, as p1 and
  p5 already use. Then the clamp pulls.
- **Where the load goes then:** box → barrels → crimp → wire. Only the crimp
  carries it.
- **Uncertain:** the neck length (as p1-4).

### Break p4-2: the V lead-in and the anvil shuttle sit on the carrier

**Conflict.**
- **The lead-in.** The stripped end runs axially into a pre-fed strip contact
  "through a V lead-in". The lead-in has to sit behind the insulation barrel.
  That is where the tab and carrier lie, 1.05–3.05 mm behind the strip line
  [calc H §2], so its lower half is the carrier itself.
- **The shuttle.** The "anvil shuttle" that "brings the pre-fed contact from
  the strip under the work line" carries a contact that is still on its strip.
  Either the strip moves with the shuttle, or the contact is cut free first.
  p4 does not say which.

**Repair (transfer: this is a1 almost literally).** Cut the contact free (stub,
revolver or post) and hold it in a hand-tool nest. The flap blade sits in the
neck and the front stop at the box.
- The conductor then feeds axially from the rear face, as the WC-110 procedure
  p4 cites describes. The rear face is free for a printed V funnel, because no
  carrier is there.
- The "anvil shuttle" becomes nothing. The tool stays put while the strip jaws
  swing clear, and p4's clamp carries the conductor forward.
- **Uncertain.**
  - Whether strands splay on the barrel's rear edge. p4 lists this; a1 adds that
    touch-off stops the feed at first contact, before any buckling force
    builds.
  - The first ratchet tooth.

### Combination C2: p4's division of labor with a1's squeezer and a2b's revolver

| p4 contributes | a1 and a2b contribute |
|---|---|
| The funnel and the beam at a hard stop | The SN-2549 squeezer as the whole crimp head, $17.99–20.99 plus one NEMA 17 Tr8×2 pusher (Amazon, Prime to be confirmed) and a load cell |
| The soft clamp that takes the conductor | The flap blade: axial reference on the box's rear shoulder, strand stop, proof pull through the box |
| The strip by clamp-and-pull | The revolver, filled with loose kit contacts away from any wire, dropping one per cycle through the open nest |
| The lit conductor and lit cavity | The far end clamped in a push-in block, so a wrong conductor presented is refused before stripping |
| The person inserting k−1 while the machine works on k | |

The revolver keeps p4's "the machine … never holds the contact" true with the
kit contacts on hand. p4's loose-kit mode gives that up.

The far-end block turns p4's lights from a suggestion into a check. J4's
crossing, "the person's hands make the crossing without thinking about it",
gets an electrical confirmation.

**Minutes** [calc H §7, estimates]. p4's own figures are 5 s to present and
8 s to insert.

| Heads | Machine cycle | Conductor every | Person waits | 53 conductors |
|---|---|---|---|---|
| One squeezer | ~26 s (fast approach, slow last 8 mm of grip travel) | 26 s | ~13 s each | ~23 min |
| Two squeezers, alternating | ~26 s each | ~13 s | ~0 s | ~11 min |

With two heads the person's own pace sets the rhythm. A second head costs one
more $18–21 tool and one more pusher. That is cheap only because the crimp head
is a hand tool. It answers p4's open problem ("whether a slow machine can reach
~15 s") with two slow machines, not a fast one.
- **Uncertain.**
  - The 26 s cycle is an estimate.
  - The approach at 15 mm/s on a Tr8×2 lead screw is 450 rpm, where a NEMA 17
    has little torque. That is fine, because the approach needs little force.
  - Whether two funnels confuse which conductor goes where. The lights and the
    far-end check guard that.

## p5 Camshaft: one revolution per conductor

### Break p5-1: fork closed through the punch stroke

See p1-3. In p5's timing, fixing it means moving "fork opens" from 330–360° to
~150–170°. A wire-hold leaf on the punch stack takes over from 170° to 240°.

### Break p5-2, with a repair from a4: crimp height by a stop, force capped by a stack

**Conflict.** p5 sets crimp height by the eccentric at bottom dead centre. So
height = BDC position − loop deflection at the crimp force. That is why it asks
for a loop of ≥15–30 kN/mm, and why it has "no stop-at-force"
([calc P cam_drive §3](../explorers/procedure-is-the-machine/calc/cam_drive.out.txt)).

**Transfer (a4).**
- **The stop.** Steel stop blocks beside the punch meet at crimp height. The
  loop through the punch holder and anvil holder is ~30 mm of steel, ~670 kN/mm.
- **The stack.** A disc-spring stack in the rod is preloaded above the crimp
  force, which caps any over-travel.

**Numbers** [calc H §4].
- **Crimp height scatter.** Without the stop, ±300–600 N of force scatter
  moves height by ±20–40 µm at 15 kN/mm. With the stop it moves it by
  ~±1 µm.
- **What the frame still has to do.** It must deliver the dies to the stop,
  which needs torque, because a softer frame moves the crimp force away from
  BDC (e = 2.5 mm, 2.6 kN at closure):

| Frame stiffness | Die contact before BDC | Shaft torque needed |
|---|---|---|
| 40 kN/mm | 21° | 2.3 N·m |
| 20 kN/mm | 25° | 2.7 N·m |
| 10 kN/mm | 31° | 3.4 N·m |
| 5 kN/mm | 41° | 4.3 N·m |
| 2 kN/mm | 64° | 5.8 N·m |

**What it changes.**
- Crimp height becomes a property of the stop, which is set by shims, not of
  frame, bearings or force scatter.
- With the stop, the stiffness figure is only about torque:
  - a NEMA 17 through 30:1 (3.1 N·m) needs a frame of ~20 kN/mm;
  - through 50:1 (4.5 N·m), ~5–10 kN/mm;
  - the bench's NEMA 23 through 30:1 (12.6 N·m) turns even a 2 kN/mm frame.
- The same stack caps an obstruction. Their exchange calc §3 already shows it
  at 2–5 kN for a doubled contact, which removes p5's shear-pin question.
- **Where the stop shows in the force curve.** Stop contact is a sharp rise in
  stiffness. A crimp that reaches the stack's preload before that rise is
  "high", from a doubled contact or a folded conductor, and it is flagged.

**Uncertain.**
- Whether a die set with a hard stop gives a good XH crimp. Hand tools bottom
  their jaws, which is the same principle (IWISS "touch each other everywhere").
  Applicators do not, and set height on dials [xh-facts §2].
- A soft or printed frame under 3–4 kN cyclic load for ~3,200 strokes: creep
  and fatigue [assumption].

### Combination C3: the camshaft squeezes a hand tool (p5 × a1)

- **p5 contributes.**
  - One NEMA 17 through the 30:1 self-locking worm.
  - One revolution per conductor.
  - The cassette's rack as escapement and program, with skip and end bumps.
  - Printed face cams for the light motions.
- **a1 contributes.**
  - The SN-2549 in place of the eccentric, steel C-frame and applicator
    tooling.
  - A squeeze lobe on the camshaft pushes the upper handle through a roller
    and a spring link.
  - Crimp height is the tool's.
  - The force loop closes inside the tool, so the frame carries only the
    handle reaction (≤220 N).

**Numbers** [calc H §5].

| Lobe | Travel | Load | Shaft torque |
|---|---|---|---|
| Approach | 45 mm over 120° | ~20 N | 0.4 N·m |
| Squeeze | last 8 mm of grip over 40° | 220 N | 2.5 N·m |
| Squeeze, spring link preloaded to 275 N | same | 275 N | 3.2 N·m |

- **The spring link** caps die force at ~1.25× the handle need if the tool
  jams. It is the b2 spring link in their exchange calc §4.
- **The cam.** A ~170 mm plate cam, or a 4:1 lever on a smaller one.
- **The follower.** A 16 mm roller, 8 mm wide, puts ~83 MPa on PET-CF. That is
  near its compressive limit. A 16 mm wide roller gives ~58 MPa. A steel
  insert on the squeeze lobe also works.
- **The ratchet** is compatible with one revolution. It completes its cycle
  within the lobe and releases on the return.

**What the other cams must do with a hand-tool head** (instead of a presser and
lay-in):
- a lift cam raises key k (R1);
- a Y cam slides the tip-down tool onto k, or brings k forward into a side-
  lying tool;
- a pawl on the shaft indexes the a2b revolver, one contact per turn;
- a flap cam drops the blade.

Touch-off is optional here. The cassette trim line and the blade on the box
shoulder fix the axial chain as in p1-4. The far-end block can still stop the
shaft through p5's switch cam when identity is wrong.

**Uncertain.**
- Whether the revolver and a gravity drop through the open nest work (a2b's
  open problems).
- Tool orientation on the camshaft frame.
- The lifted conductor's set.

## What their view has not yet seen

- **A crimp head that exists.** Every p-idea routes its crimp to OTP applicator
  tooling (eBay, ~$155 plus ~$91 shipping), a steel ram or eccentric frame, or
  a custom anvil. The SN-2549 already makes XH crimps on this bench, closes its
  own loop, and costs $17.99–20.99 as a machine copy.
  - The price of that head is fixed height.
  - a5's two-squeeze plier gives a settable height if that matters.
- **The tool's "hold" click is a locator.** Closing to the first tooth sets the
  contact's lateral position and roll in the nest without a strip. The digest's
  roll window is 5–11°. That is how loose contacts get located without a
  carrier.
- **Loose kit contacts without a hand per crimp.**
  - The a2b revolver.
  - The a3 post column, which also turns a strip into oriented loose contacts
    with one push and one gang cut.

  p1's loose-contact branch lists a bowl, a scoop, a magazine, or the person
  per crimp.
- **Identity at the moment of crimping.** The far end (a terminal block, pierce
  pins, cut-face pogo pins, or p3's slip ring) tells the machine which
  conductor it is about to crimp. The order they carry in cassettes, lights
  and bumps gets a physical check at every conductor.
- **A proof pull has to go through the box** (p4-1).
- **Selecting a conductor bends it for good** (p1-2). Presser and lifter both
  leave set. Which conductors carry it, and when, depends on the order. That
  makes it an order question, squarely in their view.
- **Bench hand tools as stations for other steps they hand to the person.**
  - Squeezers can hold the Knipex or KATA cutters (p1's cut-square step, p2's
    trim tool), the Klein 11063W (bench A's strip, as a2c), and the far-end
    crimpers (p3's handback).
  - Each is one printed saddle and one pusher.

## Where their work changes my own ideas (for my revision)

1. **Order.** My a1–a3 are cut-first, and my far-end terminal block needs the
   far end stripped before the XH end is made. That goes against their
   recovery numbers:
   - a whole-end redo cuts back 4.5–6.7 mm;
   - a cut-first order at a 10 % bad-crimp rate with a 12 mm reserve scraps ~35
     looms over the program;
   - the XH end should come before far-end hand work.

   Revision: a3 moves to p3's work clamp (C1), with the slip ring as the
   electrode array. Where a loom is cut first, the far end is pierced within
   its future strip zone rather than stripped.
2. **Person minutes.**
   - a1 is a p4-class person-paced station. It buys consistency and a log, not
     minutes.
   - a2 and a3 need a person to clamp each of 14 ribbon ends per unit, which
     is p2's "ten calls a unit".
   - Revision: feed a2/a3 from a magazine of p1 cassettes or from the spool,
     and use C2's two heads where a person-paced station stays.
3. **J4 and J7.** a3 says "pin order is physical" because each conductor lives
   in its cavity's comb slot. That is untrue for J4 and J7 as the looms are
   wired. a3's fixture needs p1's loft (crossing made at loading), or a2c's
   per-conductor insertion order, which is p2's route.
4. **Axial reference.** My touch-off finds the strand tip, so strip-length
   scatter goes straight into where the insulation edge lands. That is the
   largest term in their chain. Revision:
   - strip k in the same pose at the same station (their "trim in the lifted
     pose");
   - measure the bare length with the camera and correct in Y (calc H §6,
     ±0.11 mm);
   - or take the insulation edge from a score line, as their borrowed-machines
     exchange found (±0.10).
5. **Lift once, do everything to k in that pose.** a3 lifts k only for the
   crimp. Stripping elsewhere, in a different pose, brings back the split-point
   scatter of 0.06–1.02 mm
   ([calc P selector_and_bow §1](../explorers/procedure-is-the-machine/calc/selector_and_bow.out.txt)).
6. **a1b can have a mechanical guarantee again.** a1b made the controller's
   judgement the whole guarantee against a partial crimp. p5's camshaft with
   C3's spring link restores a mechanical one:
   - the lobe always completes;
   - the spring caps force;
   - the ratchet (kept, or removed) no longer has to be the guarantee.
7. **The contact supply for a hand-tool head is cut free first.** Their calc P
   exchange_borrowed §1 (no space below an attached strip) confirms stubs,
   posts and the revolver.
   - My a2 variant, "strip off the jaw tip", keeps a strip attached behind the
     rear face. The working conductor's approach then crosses the carrier, and
     the next contact's open wings stand one pitch along. The fork's path has
     to stay above the carrier plane.
   - The stub occupies the rear face, which rules out a funnel there. Their tip-
     wander table puts a 5–8 mm unsupported conductor at 0.12–0.61 mm under a
     0.05 N brush, against a ±0.38–0.65 mm insulation-barrel mouth. That argues
     for post or revolver contacts, so the rear face can carry a funnel.
8. **Set in my own selection.** a2's fork offset and a3's lifter both leave k
   bent when laid back. The finished row needs a squaring comb before any gang
   insertion (calc H §1; into-the-housing's calc §6 says the same).

## Measurements this exchange adds or sharpens

- **The neck between conductor barrel and box on a kit contact and on a strip
  contact**, under the ELP camera. It serves my flap blade, p1/p5's proof-tug
  hook, and p4-1's repair.
- **One conductor pressed 7 mm down at 15 mm free length and released**,
  photographed from the side. This measures the residual set and pull-back that
  p1-2 and my a2/a3 depend on. The strand yield and silicone modulus behind
  calc H §1 are both assumptions.
- **The SN-2549's nest-to-tip distance t**, for R1, C1, C3 and p2-2.
- **How deep an OTP XH applicator's anvil and strip track sit** below the
  conductor axis, if one is bought. This settles R3 and p2-2 for that route.
- **The carrier's width on a Digi-Key 100-piece strip**, for where a fork can
  sit behind it (p1-3).
