# procedure-is-the-machine on ribbon-as-pallet (wave 3)

Wave 3 exchange. The view doing the reading: *the sequence and the division of
labor are the design*. The view being read: *the ribbon is a precision part*
([`../explorers/ribbon-as-pallet/summary.md`](../explorers/ribbon-as-pallet/summary.md)).

Read for this file: every idea in
[`../explorers/ribbon-as-pallet/ideas/`](../explorers/ribbon-as-pallet/ideas/),
with the most weight on what wave 2 added or changed (a1's tongue, a1c, a2e,
a5's order, a7, a7b, a8, a8b), their calcs, their notebook's wave-2 rejected
directions, and borrowed-machines' wave-2 critique
([`borrowed-machines--on--ribbon-as-pallet.md`](borrowed-machines--on--ribbon-as-pallet.md)).
That critique's breaks (a1-1 to a1-4, a2-1 to a2-4, the applicator's upstream
envelope, the crank pause, the SN jaw along the row) are not repeated here.

Citations:
- **[calc P3 §n]**: this exchange's numbers,
  [`../explorers/procedure-is-the-machine/calc/exchange_ribbon_w3.py`](../explorers/procedure-is-the-machine/calc/exchange_ribbon_w3.py)
  with its output [`.out.txt`](../explorers/procedure-is-the-machine/calc/exchange_ribbon_w3.out.txt).
- **[calc wave2 §n]**: my wave-2
  [`wave2.out.txt`](../explorers/procedure-is-the-machine/calc/wave2.out.txt).
- **[calc W2 §n]** and **[calc R §n]**: ribbon-as-pallet's
  [`stations_wave2.out.txt`](../explorers/ribbon-as-pallet/calc/stations_wave2.out.txt)
  and [`pallet_geometry.out.txt`](../explorers/ribbon-as-pallet/calc/pallet_geometry.out.txt).
- **[calc X §n]**: borrowed-machines'
  [`exchange_ribbon_as_pallet.out.txt`](../explorers/borrowed-machines/calc/exchange_ribbon_as_pallet.out.txt).
- **[Prime: row name]**: a Prime-confirmed row in
  [`../sourcing/amazon-prime.md`](../sourcing/amazon-prime.md), observed
  2026-09-28.

---

## 1. Combinations

### X1 The reel end docks: p6 + p7 × a2e + a7 + an equal-path fan (developed)

**Sources.**
- Mine:
  - [p6](../explorers/procedure-is-the-machine/ideas/p6-spool-end-bench-that-grows.md):
    a reel rewound onto an 80 mm hub radius, a hub socket, the clamp face as
    the cut line, draw to length and cut last;
  - [p7](../explorers/procedure-is-the-machine/ideas/p7-strip-before-split.md):
    the whole webbed end stripped in one stroke;
  - [p3](../explorers/procedure-is-the-machine/ideas/p3-terminate-at-the-spool-cut-last.md)'s
    puller and partner nest.
- Theirs:
  - [a2e](../explorers/ribbon-as-pallet/ideas/a2e-docked-strip-through-a-feedless-applicator.md):
    docking onto a strip, a feedless applicator, continuity to the carrier;
  - [a7](../explorers/ribbon-as-pallet/ideas/a7-zip-station.md): a tear
    stopped at the clamp face;
  - [a6](../explorers/ribbon-as-pallet/ideas/a6-housing-as-last-comb.md):
    closing block, insertion clamp, slide-along jaws, real-wafer nest;
  - the **equal-path fan**, their wave-2 rejected direction 5, revived here
    (below).
- Transfers T1–T3 of section 4: a short eccentric, a pilot in the carrier
  slot, and a pull through the box.

**Why they meet.** Their notebook rejected staggered-length fan grooves:
"Revive if some station needs the tips on a line before fanning." p7 is that
station:
- it cuts and strips the whole end while the web still holds the pitch;
- a fan made afterwards pulls a 5P's outer tips back 2.77 mm at 7.1 mm [calc
  W2 §3];
- docking cannot absorb that.

Equal-length grooves make the two compatible. In exchange, docking gives p6
what its tip-down SN module cannot: every contact crimped floor-down on one
anvil (section 4, R1).

#### Picture it: the 4P reel run making J11

**Where things start.**
- **Behind the bench.** Three printed reels (3P, 4P, 5P) stand on axles. Each
  BNTECHGO spool is rewound once, through a printed roller straightener, onto
  an 80 mm hub radius:
  - the reel adds no new set [calc wave2 §2];
  - the inner end comes out through the hub;
  - the inner end is hand-crimped into an XH housing plugged into a small board
    in the hub (p6's hub socket).
- **The hub lead.** A flying lead from the controller plugs into the running
  reel's hub socket. The reel stands still while an end is terminated, so the
  lead never twists.
- **Feed and clamp.** The 4P ribbon runs through a belt feed with an encoder
  wheel (a4's feed) into a channel clamp, 0.2 mm under the ribbon's width (AMP
  US 4,230,008, their registration):
  - the clamp rides an **X carriage**: an MGN12 300 mm rail [Prime: MGN12 rail
    with MGN12H carriage] and a NEMA 17 on a Tr8×2 screw [Prime: NEMA 17 with
    integrated T8×2 lead screw];
  - **the clamp face is the cut line and the split root**;
  - a hinged **fan block** for the 4P rides on the clamp. It is one per
    ribbon type, because a reel's ribbon type never changes during its run.
- **The contacts.** SXH-001T-P0.6 on the reel come in along a fixed steel
  track from +X. The track is flush with the applicator's own track and runs
  continuous through the anvil and ~45 mm past it. An SMT-style sprocket feeder
  (borrowed-machines' b2) advances the strip on its own slots.
- **The press.** A side-feed OTP XH applicator stands on the VEVOR 12-ton
  press's bed, with its feed finger, pressure plate and shear punch removed
  (a2e):
  - it is driven by a **3–4 mm eccentric** (T1), not b1b's 15–20 mm crank:
    a NEMA 17 through a 26.85:1 planetary [Prime: NEMA 17 planetary geared
    stepper, 3 N·m permissible];
  - a **bullet-nosed pilot** sits in the removed shear punch's pocket (T2);
  - a strain gauge on the eccentric rod and an AS5600 on the shaft [Prime:
    AS5600 magnetic angle sensor] log force against angle.
- **The insertion nest** is a real B4B-XH-A wafer on a test board, on a load
  cell, fed from a small XHP-4 magazine. The **puller** is a belt carriage on a
  rail along +Y.

**What moves, for one end.**
1. **Feed-out and touch-off.** The last loom's cut left the 4P end flush at the
   clamp face. The clamp opens and the belt feed pushes the webbed end out
   along a covered floor until its copper faces touch a grounded tip stop,
   ~29 mm out for a 4P.
   - Every conductor reads continuous through the hub socket as it touches
     (their touch-off, read through the reel).
   - A conductor that never touches, or a spread over ~0.1 mm, stops the end.
   - The clamp closes.
2. **Strip, webbed (p7).** Two single-edge razors, above and below, close
   across the whole width 2.4 mm behind the stop [Prime: single-edge razor
   blades, 0.009 in]:
   - they stop on steel stops at strand radius + 0.2–0.3 mm from the centre
     plane;
   - the stop drops away, and the blades slide 3–4 mm toward the tip, pushing
     the whole slug (four jackets and three webs) off as one sleeve;
   - a 4P end takes ~40–60 N [calc wave2 §7];
   - the blades are isolated, so a blade touching copper names the conductor
     through the hub;
   - one backlit ELP frame reads all four bare lengths and insulation edges on
     one line.
3. **Zip from the slug's gap (a7).** The tine comb comes back along −Y from
   beyond the tips:
   - its noses enter the ~0.98 mm gaps between bare bundles, so no nicker is
     needed;
   - each nose meets its web at the strip line, which p7's tear has already
     opened;
   - it drives the tears back to 1 mm short of the clamp face, where they stop.
4. **Fan, equal-path.** The fan block swings down and takes the conductors
   from 1.7 mm at the clamp face to 7.1 mm at its front face.
   - **Each inner groove carries a vertical hump** that makes its path as long
     as the outer groove's.
   - For a 4P at 7.1 mm the inner pair's hump is 3.3 mm over the fan's
     16.7 mm, bent at R ~4.3 mm. For a 5P's centre conductor it is 5.1 mm over
     21.4 mm at R ~4.5 [calc P3 §1].
   - Every tip then recedes by the same 2.05 mm (4P) or 2.77 mm (5P), so the
     tip line and the strip line stay straight. The 29 mm feed-out already
     allowed for it.
5. **Dock.** X brings the clamp over the dock position of the track, where the
   sprocket feeder has put four open contacts.
   - A cam drops the clamp and fan block ~3 mm onto three balls in V-grooves
     on the carriage [Prime: chrome steel balls, 6 mm; dowel pins], and every
     conductor settles into every contact at once.
   - Grip pins drop into the carrier's slots just beyond contacts 1 and 4,
     and a small carrier guillotine cuts the strip behind the segment. The end
     uses N contacts, with no spares [calc P3 §11].
   - The hub socket reads each conductor to the grounded carrier: placement is
     confirmed before any force.
6. **Crimp, one per revolution.** The carriage indexes the docked row −X
   through the anvil one strip pitch per eccentric turn (~10 s).
   - The pilot enters the slot beside the anvil contact before the crimpers
     touch, drawing the floating row to the strip's own X (T2).
   - The rod gauge draws ~40–47 HX711 samples through the last 0.2 mm [calc P3
     §5].
   - A curve out of band stops the shaft short of bottom and backs it off.
7. **Back to the dock position: pull and shear.**
   - A comb drops a thin blade behind every box, stopping ~1.2 mm above the
     floor so it clears the brush.
   - A hook pulls each conductor in turn at the fan block's face to 20 N. The
     load goes conductor → crimp → barrel → box → blade, and never through the
     carrier (T3).
   - a2's notched shear comb then cuts all four tabs.
   - The carrier scrap and grips go to a chute.
8. **Insert (a6).** X moves to the insertion lane.
   - The fan block lifts, and a 2.5 mm closing block and the insertion clamp
     take the row.
   - The closing block's grooves are plain, not equal-path, so the fronts come
     free as a **V staircase**: for a 4P closed from 7.1 mm, the outer pair
     ~1.85 mm ahead of the inner pair [calc P3 §10].
   - The nest's Y slide pushes the XHP-4 on. The load cell sees the outer
     pair's lances snap, then the inner pair's. The clamp follows home by
     slide-along jaws.
   - A spring-limited pull-back and the camera check the latch.
9. **Test.** The controller drives each wafer post and reads the hub socket:
   pin order, opens, adjacent shorts, and J2's cavity 3 open when the 3P reel
   runs J2.
10. **Draw and cut.**
    - The puller clips the ribbon just behind the housing, and a fold around a
      bar gives the grip (a3's IDC fold, section 4 R3).
    - The clamp opens, and the puller draws J11's ~600 mm off the reel,
      measured on its encoder. The clamp closes.
    - A razor guillotine cuts at the clamp face. J11 drops into the bin with
      its far end square.
    - The 4P end is flush at the clamp face, which is step 1's start. The next
      recipe in the list is J3.

**What locates what.**

| Moment | Located | Against | Held to |
|---|---|---|---|
| Cut | tip line | guillotine running on the clamp face | ±0.05 mm [estimate] |
| Feed-out | every tip | grounded stop, touch-off through the hub | ±0.01–0.05 [calc W2 §6] |
| Strip | strip line; depth | blades 2.4 mm from the stop (one steel part); steel stops to the channel floor | ±0.05 axial; ligament 0.2–0.3 ±0.08–0.12 RSS [calc wave2 §7] |
| Split root | tear end | clamp face | ~±1 mm (a7) |
| Fan | lateral 7.1 mm pitch; tip line | grooves; equal paths | ±0.1 lateral; tip line ±0.05–0.1 [estimate, groove path accuracy] |
| Dock | conductor into contact | kinematic seat on the carriage; carrier on the fixed track | capture: section 3, C2 |
| Crimp, X | contact on the anvil | pilot in the carrier's own slot | ±0.02–0.05 [assumption, stamping] |
| Crimp, Y | insulation edge in the window | strip line and carrier edge, both referenced to the carriage and track | ~±0.15 RSS [estimate] |
| Crimp height | barrels | applicator dials; eccentric BDC set once to shut height | ±8–23 µm frame scatter, read as ΔF/k [calc X §9] |
| Length | loom | puller encoder from the clamp face | ±1–2 mm [calc wave2 §6] |

**What drives the crimp and carries its force.** The load path is:
- NEMA 17 → planetary → eccentric shaft in pillow blocks on the VEVOR frame's
  crosshead;
- rod → applicator ram → crimpers → contact → anvil;
- applicator base → press bed.

The carriage, pallets, grips and track carry positioning loads only. The
eccentric needs ~1.0–1.7 N·m against ~2.2–6 N·m for a 15–20 mm crank [calc P3
§5]. That keeps the bench's NEMA 23 and DM542T in the cap-weld tube rotator,
where the shared context puts them.

**How it knows.** Every check below runs through one wire per conductor, the
hub socket, from the tip stop to the wafer test:
- touch-off at the tip stop (all N present, tips on one line);
- blade and tine touch on copper;
- one backlit frame of every bare length;
- continuity to the carrier at docking;
- a force curve and ΔF/k crimp height per contact;
- a camera frame per crimp;
- a 20 N pull through the box;
- lance snaps and pull-back;
- pin map and shorts through the real wafer;
- the loom's length.

Each end is logged with the reel's ID and the metre mark it came from.

**What the person does.**
- Once per spool: the rewind, straightening and hub-socket crimp, ~6 min (about
  3 spools per 5 units).
- Per reel run:
  - mount the reel and plug the hub lead;
  - load the run's recipe list;
  - keep the contact reel and the run's housing magazine;
  - empty the bin and scrap cup.
- Per unit, four pair events at the partner nest, when called:
  - **J1 and J2:** put the half-housed housing into the nest. The machine
    inserts the second ribbon through a straight closing block.
  - **J4 and J7:** the machine inserts the first ribbon through a gapped
    closing block: J4's 4P to cavities 1 and 3–5, J7's 5P to 1–4 and 7
    [assumption: cavity numbers read from calc unit_inventory §1's one-line
    maps]. The person inserts the other ribbon's 5 crossing contacts by hand
    (J4's 3P, J7's two used 3P conductors), because both crossings run between
    the two ribbons (section 2, B8).
- Also per unit: label 10 housings, and make every far end, as today.
- About **12 attended minutes a unit**, against ~46 by hand on the same task
  library [calc P3 §7, estimate].
- The machine's longest stretch alone is one 4P reel run: 5.4 units' worth of
  4P ends (35 ends) at ~5.5 min each, ~3.5 h. The pair calls interrupt it
  unless the half-housed housings wait in a magazine by the nest.

**What the pairing does that neither side does alone.**

| | a2e alone | p6 alone | X1 |
|---|---|---|---|
| Ribbon pallet | one per ribbon end, loaded by hand from a cut length | the reel clamp | the reel clamp; one fan block per ribbon type |
| Far-end port | a pogo block pressed onto each loom's cut far end | hub socket | hub socket |
| Crimp orientation | floor-down on the anvil | rolled 90° by a tip-down SN module (R1) | floor-down on the anvil |
| Crimp height | applicator dials | the SN-2549's fixed dies | applicator dials |
| Contact supply | snipped N+4 segments laid by hand | a post revolver loaded in key order by hand | strip reel and sprocket, N per end |
| Flush cut and strip | a separate guillotine and rolling scorer after the fan | V-jaws per conductor, or p7 | the loom-freeing cut plus one p7 stroke, before the split |
| A bad crimp costs | the loom's length (cut first) | ~6 mm of reel | ~35 mm of reel: the whole split is cut off at the clamp face, ~37 mm per unit at a 2 % crimp failure rate [calc P3 §12]; no loom |
| Person, per end | ~40–220 s | stage-dependent | ~0 for single-ribbon ends |

**Stage 0, no motors.** The same reel clamp sits on a hand-slid X plate with
ball detents at strip pitch:
- p7 as a lever with two razors on shim stops, and a7's hand comb on a rail;
- the equal-path fan block closed by a lever;
- a strip segment laid on the shelf by hand, docked by a lever, and
  continuity read on LEDs through the hub socket;
- one stroke per contact by pumping the VEVOR jack against a hard-stop collar
  over the applicator (b1b's zero-build test);
- a luggage-scale pull against a neck-blade comb, and the shear comb on a
  lever;
- a hand insertion jig;
- draw to a peg and cut at the clamp face.

Docking, p7's slug and the equal-path fan can be tried the week they are
printed, with no crimp tool at all (a2d's steps 1–3: dock, photograph, read
continuity). The crimp waits on the OTP applicator, the long-lead item, which
had no Prime listing [Prime: "OTP side-feed applicator for XH chain contacts:
no Prime listing found"]. eBay and Alibaba list it at $150–250 plus shipping
[force-and-form key findings].

**Major unresolved problems, beside it.**
- **p7's flank tear.** Two straight scores leave 144–200° of each jacket to
  tear from full wall [calc W2 §5]. A ragged edge worsens the silicone bulge
  their W2 §9 found the insulation barrel pushes into the window.
- **Starting the zip from a slug gap** rests on the web's neck thickness t_n
  (repo Open item 5).
- **Closing the equal-path fan block.** Whether it catches each tine-fanned
  conductor into its groove, humps included, without the conductor riding up.
  The humps leave vertical set that the closing block and insertion clamp have
  to straighten.
- **Parted length.** The split is 22–33 mm (3P–5P) at 7.1 mm pitch
  including the 1.3–2.8 mm recession allowance, against a4's 20–23 mm at 5 mm. This is
  Derek's split-length question.
- **The applicator scan.** It sets which parts unbolt, whether the shear
  punch's pocket takes a pilot, and the downstream room: ~32–35 mm with grips
  in the carrier's end slots, ~43 mm with grips on spare contacts (section 2,
  B2).
- **The eccentric's frame.** Pillow blocks on the VEVOR crosshead set to shut
  height, with a stiffness still to be found (b1b's 13–39 kN/mm is an
  estimate).
- **The reel itself.** Whether a BNTECHGO spool's inner end is reachable
  without a rewind, and whether the straightener marks silicone.
- **Batching.** Per-reel runs of 5–11 units hold finished looms and half-housed
  pairs ahead of units. That is Derek's call.
- **J4 and J7:** 5 crossing contacts a unit stay with the person (B8), and the
  gapped closing blocks are per-loom parts.

---

### Other combinations, briefly

- **X2: a2e × p4b's rhythm, with prep and insertion split between person and
  machine.**
  - With a2e and hand prep at a1b's seats, the person's overlappable work per
    end is ~178 s (cut, load, prep the next end, insert the previous one)
    against the machine's ~108 s [calc P3 §7]. The person sets the pace and a
    second docking shelf buys nothing.
  - Only when prep moves onto a1's stage (person ~147 s per end) or into the
    reel clamp (X1) does the machine's cycle start to matter.
  - Section 2, B7, has the table.
- **X3: a3's backshell as p3/p6's puller grip.**
  - The puller that draws a loom off the reel needs a hold of a few newtons on
    silicone, which I left untested (p3).
  - a3's fold around a bar turns a 3 N clip into 14–69 N at μ 0.5–1 [calc X
    §8].
  - If the backshell is folded on at the reel clamp before the zip, its front
    face is the split root and the tear stop, and it ships on the loom as
    label and strain relief.
  - Its height above the board, 36–52 mm for 14–30 mm splits [calc X §7], is
    a3's open problem, unchanged.
- **X4: a2c's keyed nest bar with the recession printed into the pockets ×
  p7.**
  - With loose kit contacts at a free pitch, each pocket's Y can be set back by
    that conductor's fan recession (5P at 5 mm: 0, 0.77, 1.65 mm from centre
    out [calc P3 §1]). p7's strip-before-split then docks without an
    equal-path fan.
  - It is the only route here that uses the CQRobot contacts on hand.
  - The recession depends on the groove's exact shape (C1), so the pockets
    must be printed from the same geometry as the fan block.
- **X5: p1's cassette loft × a2 for J4 as one pallet.**
  - J4's crossing (3P GND to pin 2) runs between its two ribbons [calc
    unit_inventory §1], so two pallets cannot make it before crimping.
  - Clamped as one 7-conductor pallet, the person lays the GND conductor into
    a raised crossover groove at loading (my loft), where the fan is at 7.1 mm
    and the room is generous.
  - The cost is a ~39 mm split at 7 mm pitch fanned as one [calc R §2], plus
    the crossover's length. J7's 44 mm, or the wiring choice in the digest
    that makes J7 straight, is the same trade.
- **X6: p1c's lift-once as a8b's clearance** (section 2, B4). k is raised
  ~9 mm into the spindle, clear of 5 mm neighbours, and laid back. Its residual
  rise (0.3–5.6 mm at 20–25 mm free for an 8 mm lift [calc wave2 §1(b)], more
  at 9) is then pressed level by a1c's flat sole.

---

## 2. What still breaks in their revised and new ideas

### B1 a2e: the proof pull bends a carrier held only by its end grips

**Conflict.**
- a2e step 7 pulls each conductor to 20 N at the fan block face "against the
  carrier".
- The pull runs −Y, toward the carrier side, because the conductor enters the
  contact over its tab. So contact k's tab pushes on the carrier's edge: an
  in-plane point load.
- In a2e "the carrier between the grips lies free on the shelf". The grips are
  pins in the outermost spares' pilot holes, (N+3) strip pitches apart: 42.6,
  49.7 and 56.8 mm for 3P, 4P and 5P.

**Physical consequence** [calc P3 §3; carrier width unmeasured, 2.5–4 mm
assumed; 0.20 mm thick; C5191 yield 450–650 MPa]:
- For a 5P's middle contact on a 3 mm carrier, the carrier bows 0.39–1.54 mm
  in-plane at 473–947 MPa (ends fixed or pinned).
- On a 2.5 mm carrier: 0.67–2.67 mm at 682–1363 MPa.
- The pilot hole under contact k cuts the section further.
- So the carrier yields, the contact moves 0.4–2.7 mm with its conductor, and
  "a crimp that slips shows as a conductor that moved" can no longer be read.
- a2's strip pallet does not have this. Its slot pins at ±3.55 mm
  give 1 µm and 59–85 MPa.

**Repairs.**
- a2's slot pins at every slot, at the pull position.
- Or a blade behind every box that takes the pull (T3). The carrier then sees
  none of it.

**What stays uncertain.**
- The carrier's width and temper. The $4.71 strip settles the width.
- Whether a blade fits behind a box still on its carrier above the brush.

### B2 a2e: the downstream room is ~43 mm, not 28

- a2e reads the downstream need as "up to four strip pitches (28 mm for a 5P)".
- When the last real contact is on the anvil, the row reaches further:
  - four crimped contacts at 7.1–28.4 mm;
  - the two leading spare contacts at 35.5 and 42.6 mm;
  - the end grip on the outer one.

  That is 42.6 mm for a 5P, 35.5 for a 4P and 28.4 for a 3P [calc P3 §4].
- Everything there passes the scrap-chute side of the anvil that the applicator
  never designed for.
- **Repair: grip pins in the carrier's end slots** instead of in spare
  contacts' pilot holes.
  - The overhang falls to about half a pitch beyond the leading crimped
    contact: ~32–35 mm for a 5P.
  - Contacts per unit fall from 111 to ~55. At N+4 a unit's 111 contacts are
    1.11 of the 100-piece strips a2e counts as "about one unit" [calc P3
    §11].
- **What stays uncertain.** The scan, as a2e says, and whether a pin in a slot
  holds the carrier's Y as well as a pin in a round hole. A fixed track rail
  against the carrier's edge would take Y.

### B3 a2e's crank is the applicator's standard stroke, and the feed that needed it is gone

- a2e keeps b1b's crank, 15–20 mm throw on a NEMA 23 and DM542T "on hand".
- The shared context places that motor and driver in the cap-weld tube
  rotator, so it is not free [repo tools.md via shared-context].
- A pre-feed applicator's 30–40 mm stroke drives its feed cam and lets a hand
  lay a wire in [assumption]. With the feed removed and nothing fed by hand,
  the ram only needs to lift its crimper legs clear of the next open contact's
  wings (2.75–3.2 mm) plus margin: a 6–8 mm stroke [estimate].
- Numbers [calc P3 §5]:

  | Drive | Peak torque | Samples in the last 0.2 mm |
  |---|---|---|
  | 3–4 mm eccentric | 1.0–1.7 N·m | 40–47 |
  | 15–20 mm crank | 2.2–6.0 N·m, mostly the ram's return spring | 18–21 |

- The repair is transfer T1. What stays uncertain: the eccentric's bearing
  blocks set to the applicator's shut height (135.78 mm for the CDS standard
  [mfr S11]; the OTP unit's own figure unknown), and whether the OTP ram has a
  return spring at all.

### B4 a8b at 5 mm crimp pitch collides with the neighbours' tips in a1, a1c and a4

- a8b says it "suits a1, a1c, a4" and lists the 15 mm bearing OD as a problem
  only "at housing pitch".
- At 5 mm, a1's held-up fan and a1c/a4's flat downstream fan put the
  neighbours' jacket edges 4.15 mm from k's axis. The stage feeds k 2.4 mm plus
  touch-off into the funnel, and the neighbours' flush-cut tips advance the
  same distance toward the head's front face.
- a4 is the case that matters: a8b's touch-off there is what replaces the
  second flush cut.
- **Physical consequence.** The neighbours' tips butt the spindle face, or are
  pushed back into their grooves before k reaches its stop. Touch-off then
  reads k against the stop and a bent neighbour against the face.
- **Repairs** [calc P3 §8]:
  - A snout at most 7.8 mm across, reaching at least ~6 mm ahead of the 15 mm
    bearing section. It has to hold the 4 mm funnel, both flexure-mounted
    sliver tips and the closing cone.
  - Or lift k ~9 mm into a full-size head (X6). At 8 mm of lift k is left
    0.3–5.6 mm high at 20–25 mm free [calc wave2 §1(b)], more at 9. a1c's flat
    sole presses that level.
- **What stays uncertain.** The cone-and-flexure closing mechanism at under
  8 mm OD; a8b already calls 10 mm "small work for a printed part".

### B5 a4, and every pallet cut from near a spool's hub: curl lifts the protrusion out of the zip's plane

- a7 wants 35–50 mm of end standing past the clamp, and a4 answers the curl
  with "the channel squeezes it straight near the clamp". The channel holds only
  what is under the lid.
- Off a 25 mm hub radius, ribbon wound there keeps a residual curl radius of
  55–242 mm [calc wave2 §2]:
  - a 35 mm protrusion's tip stands 2.5–12.6 mm out of plane;
  - a 50 mm protrusion's 5.2–32 mm;
  - off a 35 mm hub, 0.1–5.3 and 0.2–11 mm [calc P3 §9].
- The hub size is unrecorded. Between 11 % and 66 % of a spool's length can be
  wound below first yield on a 25 mm hub [calc wave2 §2].
- **Consequence.** a7's nicker V-noses sit just above and below a 1.7 mm-thick
  ribbon, so a tip 2.5 mm high passes over them, and the tine noses then meet
  unnicked jacket.
- **Repairs:**
  - a covered floor continuing from the clamp to the nicker (X1 step 1 has
    one), lifted only for the tines;
  - a roller straightener at the feed;
  - p6's rewind onto an 80 mm hub radius, which adds no set.
- **What stays uncertain.** Whether a straightener removes curl from silicone
  ribbon without marking it or twisting the web. That is p6's open item too.

### B6 a6 after strip pitch: "a slight bow" is 2–4.5 mm

- a6 says that closing a fan to 2.5 mm brings the outer contacts forward, and
  that "the difference goes into a slight bow" behind a clamp that sets every
  front.
- On their own recession numbers [calc W2 §3], closing a 5P from 7.1 mm leaves
  the outer conductors 2.47 mm long and the next pair 1.22 mm long [calc P3
  §10].
- Forced onto one front line, 2.47 mm bows 2.2 mm over a 5 mm free span,
  3.2 mm over 10 and 4.5 mm over 20. The gap between jackets at 2.5 mm pitch
  is 0.8 mm.
- **Consequence.** An in-plane bow crosses a neighbour; an out-of-plane bow
  stands 2–4.5 mm proud behind the housing, with set in it.
- **Repairs.**
  - Leave the fronts free. The same excess is a V staircase, outer contacts
    ~2.5 mm ahead, the next ~1.2 mm, centre last. That is a6's own staircase
    with the steps made by the fan, and it needs no stepped clamp face (X1
    step 8).
  - Or give the closing block equal-path grooves, which brings all fronts in
    together, at up to 49 N for a 5P straight in [calc R §8].
- **What stays uncertain.** Whether the load cell separates two lances that
  snap together (the symmetric pairs of a V), where a6's staircase snaps one
  at a time.

### B7 Division of labor: in every pallet row the crimp is a small share of the person's time

On one task library, the wave-2 one plus pallet tasks; every figure is an
estimate, so compare rows, not minutes [calc P3 §7]:

| Arrangement | Person min/unit | Machine alone per call | Calls/unit |
|---|---:|---|---:|
| today, by hand | 46 | – | 0 |
| a1b hand shuttle, applicator on the jack | 65 | – | – |
| a2e, prep at a1b's seats, hand insertion | 60 | ~1.8 min | 14 |
| a2e, prep on a1's stage, hand insertion | 43 | ~1.8 min | 28 |
| a1 pallet tour (their ~156 min machine time) | 20 | ~11 min | 14 |
| X1, the reel end docks | 12 | ~3.5 h per 4P run | ~7 |

- **a1b and a2e with hand prep cost more attended time than today's hand
  procedure.** The reason is the person's per-end work: cut, load, zip, fan,
  flush-cut, strip, seat, lift, then insert, 178–220 s per end against today's
  60 s per end plus 31 s per conductor.
- What they buy is not minutes:
  - contacts that arrive by themselves;
  - dies at a dialled height;
  - a force curve;
  - positions that come from seats and stops.
- a2e calls every ~1.8 min, which is p4's pattern: the person is present for
  the whole run.
- Minutes fall only when nobody cuts and loads a pallet per end: a1's stage,
  or the reel clamp in X1.
- None of their files claims otherwise. The table shows where the person's
  time sits once the priority step is solved.

### B8 J4 and J7: the crossings run between the two ribbons of a pair

- a6 hands J4/J7 to the person, "laying the crossing conductors into the 2.5 mm
  clamp by hand".
- On the repo's pin maps [calc unit_inventory §1]:
  - J4's crossing is the **3P's GND to pin 2**;
  - J7's is the **5P's GND to pin 7, past CLO/CHI**.
- Both cross from one ribbon into the other's cavities. With pairs processed as
  two pallets bolted together only at insertion (a2, a2e, a6), no fan-block
  groove on either pallet can make the crossing before crimping.
- The crossing conductor's contact must pass over the other ribbon's crimped
  row at 2.5 mm pitch.
- **Repairs and branches:**
  - a gapped closing block lets the machine insert each pair's first ribbon
    (J4's 4P to 1 and 3–5, J7's 5P to 1–4 and 7). The second ribbon's 5
    crossing contacts are inserted by hand, which is X1's division;
  - X5: J4 as one pallet with a loft, at a ~39 mm split;
  - for J7, the digest's wiring choice.
- **What stays uncertain.** Whether a crossover groove at 7.1 mm leaves the
  crossing conductor's contact square for docking.

---

## 3. Consistency

- **C1 Fan recession: their 0.31 mm and my 0.09–0.16 mm for a 5P closed to
  2.5 mm are both right, for different shapes.**
  - Their [calc W2 §3] is the compact R 5 / 30° S, 5.5 mm long, followed by a
    straight. Mine (exchange_borrowed §7) is a straight diagonal over the
    whole split.
  - A gentle cosine S spread over 15 mm gives 0.10 mm; over 8 mm, 0.19 mm
    [calc P3 §1].
  - So the recession is set by the groove's shape, and the fan block designer
    chooses it. For a parallel exit their numbers apply unless the S is
    stretched over the split.
  - Consequence for my p7: its "single ribbons stay inside ±0.3 mm" holds for
    a stretched fan and not for their compact one (5P 0.31 mm).
  - At 7.1 mm no shape helps much: 2.0–3.1 mm over 21–30 mm.
- **C2 a2's "±0.5 mm of lateral capture, five times the placement error"** reads
  the clone drawings' open widths as inside dimensions, at nominal.
  - The drawings do not say inside or outside, and carry ±0.25 [xh-facts §1].
  - Read as outside widths at the low tolerance with a 1.8 mm jacket, the
    insulation barrel's half-gap is +0.01 mm, and the conductor barrel's +0.14
    [calc P3 §2].
  - JST's own 1.95 mm end-view envelope, if it includes open wings, leaves a
    1.7 mm jacket 0.08 mm of interference per side.
  - Placement error stacks to ~0.16 mm RSS, 0.32 mm worst [estimate].
  - Which reading is right decides whether docking drops conductors in or has
    to press them. The $4.71 strip under a caliper settles it.
- **C3 a2e's "a 100-piece strip is about one unit"**: at N+4, a unit is 111
  contacts, or 1.11 strips. An 8,000 reel is ~72 units at N+4, ~96 at N+2 and
  ~145 at N+0 [calc P3 §11]. The digest's and borrowed-machines' "~150 units
  per reel" assume no spares. Both figures are right for their arrangements.
- **C4 a2e's downstream room, 28 mm**, omits the leading spares and grip:
  42.6 mm for a 5P (B2).
- **C5 a6's "slight bow"** is 2.2–4.5 mm for a 5P closed from strip pitch (B6).
- **C6 a1, a1c and a2e call the NEMA 23 and DM542T "on hand".** They are on
  hand, but installed in the cap-weld tube rotator [shared-context]. A second
  set, or T1's NEMA 17, lets the press exist beside the weld station.
- **C7 a8b's "suits a1, a1c, a4"** against its own 15 mm head at their 5 mm
  pitch (B4).
- **C8 Rolled crimps in my own files.** into-the-housing found that a tip-down
  SN module closing across a flat row crimps every contact rolled 90°
  ([`into-the-housing--on--hand-tool-as-press.md`](into-the-housing--on--hand-tool-as-press.md),
  its calc §8), and hand-tool-as-press a3 took the on-edge repair.
  - My p1c, p5b, p6 stages 1–4 and C1 still describe a flat cassette or clamp
    under that same module, "jaws closing across the row".
  - Their a6's rule, every contact crimped floor-down on one anvil with the
    ribbon never turned over, is the correct statement.
  - My files are wrong on this (section 4, R1).
- **C9 Pogo pins.** a6 cites Adafruit's P75-H2 crown head. The Prime row is a
  P75-E2 conical head, 1.3 mm cone, 1.02 mm tube, $6.49 for 100 [Prime: P75
  pogo pins, 100 pack]. The crown-head P75 had no Prime listing. On a cut face
  whose strand bundle is ~0.72 mm across, a cone centres itself in the bundle,
  so either head serves [assumption].
- **C10 Slip ring.** a4 cites Adafruit 736 ($14.95). A 6-circuit capsule ring is
  $9.99 on Prime [Prime: capsule slip ring, 6 circuits], and a pair needs two.
  With the reel still during termination, p6's hub socket and flying lead need
  no ring at all until a draw-off is powered [calc wave2 §6].
- **C11 Minor.**
  - Their strand-yield radius (~67 mm) and plastic moment (0.36 N·mm) take
    70 MPa. My 60–120 MPa gives 39–78 mm and 0.31–0.61 N·mm.
  - a7's "crack stays within ~1 mm of the nose" scales with that moment. It is
    not decisive.
  - a2e's per-unit 20–28 min matches its per-end figures, which average ~25
    min over a unit's 4 × 3P, 7 × 4P and 3 × 5P ends.

---

## 4. Transfers

### From this view into theirs

- **T1 The eccentric (p5) under a2e.**
  - Once the feed is gone, the stroke only has to clear open wings, so a
    3–4 mm eccentric replaces the 15–20 mm crank (B3).
  - Torque falls to ~1.0–1.7 N·m, inside a NEMA 17 + 26.85:1 planetary's
    3 N·m [Prime: NEMA 17 planetary geared stepper].
  - Samples through compaction roughly double, and the weld station keeps its
    motor.
  - It does not serve a1 or a1c, whose feed finger is driven through the
    ram's full travel [assumption, MKS-L's cam roller].
- **T2 A pilot in the carrier's own slot, in the removed shear punch's pocket.**
  - This answers a2e's "X location between end grips". The rectangular slot
    between contacts lies between conductor paths, 3.55 mm from the anvil
    contact, where a 1.2 mm pilot clears both neighbouring conductors by
    2.1 mm [calc P3 §6].
  - It is an applicator's own principle, "the part's own feature as the
    reference at the moment of force", done at the slot, because borrowed-
    machines' Break a2-2 found the round hole under the insulation.
  - The docked assembly floats ±0.5 mm in X on a light spring. The
    correction costs ~1 N on a 0.2 mm slot edge, ~13–23 MPa.
  - On p5's single shaft, the pilot's entry (before crimper touch) and the
    index (after withdrawal) are two lobes of one timing diagram, so a
    carriage move with the ram down cannot happen.
- **T3 The proof pull through the box, dies open (p1c, p4).** A thin blade
  drops behind each box and reacts the 20 N, so the carrier is never loaded
  (B1). The blade stops ~1.2 mm above the floor: it bears on the 2.2–2.4 mm
  box's rear face above the brush.
- **T4 Strip before split (p7) with an equal-path fan.** This revives their
  rejected direction 5.
  - The loom-freeing cut or the pallet's load cut becomes the flush cut.
  - One stroke strips the whole webbed end, and one frame measures it.
  - The slug's gap starts the zip, so a7's nicker is not needed.
  - The post-fan guillotine station and its offcut go away.
  - Hump heights [calc P3 §1]:

    | Pitch | Hump |
    |---|---|
    | 2.5 mm | under 1 mm |
    | 5.0 mm | 1.7–3.2 mm, smallest bend R 2.1–4.3 mm |
    | 7.1 mm | 2.6–5.1 mm, smallest bend R 2.8–6.2 mm |

  - The trade against a8's rolled full ring is p7's flank tear (X1's first
    open problem).
- **T5 The reel (p6).**
  - An 80 mm-hub rewind keeps the zip's protrusion in plane (B5).
  - The hub socket is a4's far-end port with no ring.
  - The puller draws the loom off with the housing never the handle, in place
    of a4's 0.6–0.7 m drop tube.
- **T6 The loft (p1).** Crossings made by the person at loading, in the one
  pallet where they are cheap (X5, B8).
- **T7 Lift once (p1c) as a8b's clearance** at 5 mm and 2.5 mm pitch (X6,
  B4).
- **T8 Count the calls, not the crimps.** B7's table: the machine calls every
  ~1.8 min in a2e with hand prep, and every ~11 min in a1. With per-reel runs
  in X1, the calls are ~7 a unit and the machine runs 3.5 h alone.

### From their view into mine

- **R1 Floor-down on one anvil (a6), and my rolled crimps (C8).** My tip-down
  SN module over a flat cassette (p1c, p5b, p6 stages 1–4, p3's C1) makes
  every contact with its lance along the row. No XHP can be pushed onto that
  row, and twisting each conductor back 90° over 20–35 mm strains the strands
  2.3–4× past torsional yield (into-the-housing, calc §8). Three routes stand:
  - **The on-edge cassette** (hand-tool-as-press a3's repair). The ribbon's
    plane is vertical, the jaws close normal to it, and k is pulled out
    sideways by the jaw half's depth + 2 mm. That brings back a side pull of
    8–14 mm on a 25–35 mm split, with the set it leaves.
  - **Docking replaces the module** (X1). Every crimp is floor-down, at dialled
    height, from bought dies. My p6's stages keep their order (terminate
    first, cut last, hub socket, peg then puller), and the crimp step becomes
    a2e's.
  - **p4 and p4b escape it** if the funnel's slot holds the ribbon's plane
    normal to the jaw closing. With one conductor presented at a time, the
    funnel, not a row, sets the roll.
- **R2 The fan recession sets my p7's reach (C1).** p7 feeds docking only with
  an equal-path fan (T4) or a staggered nest (X4). It feeds my one-at-a-time
  stations unchanged, because each conductor's own edge is measured.
- **R3 a3's fold as my puller's grip** (X3). p3's and p6's open item, "the
  puller's clip on silicone at a few newtons", becomes a capstan wrap of 4.8–23×
  [calc X §8].
- **R4 A staircase for my bench C.** p1's open problem, "gang insertion
  needs all fronts on one line ±0.3 mm", turns around with a6's staircase:
  - bench C's front plate is stepped ~1 mm per key, so contacts latch one at a
    time and the nest's load cell counts snaps, instead of every front being
    set on one line;
  - where crimps are made at a wider pitch and then closed (X1), the fan makes
    the steps itself (B6).
- **R5 Docking and continuity to the carrier as p6's stage-1 crimp.** p6's
  stage 1 is a knob-turned SN squeezer, and its crimps are rolled per R1.
  p6 stage 0 × a2d (X1's stage 0) is a crimp step with no motor that keeps the
  orientation right.
- **R6 A tear stop at the clamp face** (a7) already sits in my p7 and p6 stage 5.
  Their tangent-circle neck ratio, t_n over the 0.49 mm wall, is the deciding
  number for starting a zip from p7's gap: X1 step 3 needs t_n well
  under ~0.6 of the wall.

---

## Measurements that settle most of this

1. **The $4.71 SXH strip** (455-1135-100-ND) under the caliper and ELP camera.
   It settles:
   - carrier width and pitch (B1, B2, X1);
   - slot size and position for the pilot (T2);
   - open wing widths, inside against outside (C2);
   - whether a blade fits behind a box on the strip (T3).
2. **The OTP applicator, when one arrives,** scanned with the Revopoint and
   hand-cycled. It settles:
   - the shear punch's pocket for the pilot;
   - the room ~32–43 mm downstream of the anvil;
   - whether the ram has a return spring and how strong (T1);
   - shut height for the eccentric's bearing blocks.
3. **A 5P end squeezed between two razor blades on shims and pushed off** (p7).
   Then a tine, or a flat feeler, driven into the gap it leaves. It shows
   whether the slug comes off whole and whether the web tears from its front
   edge (X1 steps 2–3).
4. **The BNTECHGO spool's hub radius,** and a 40 mm free end from near the hub
   photographed from the side (B5).
5. **One printed equal-path fan block for a 4P at 7.1 mm,** closed over a
   stripped, split end. Are the tips still on one line within ~0.1 mm (T4)?
