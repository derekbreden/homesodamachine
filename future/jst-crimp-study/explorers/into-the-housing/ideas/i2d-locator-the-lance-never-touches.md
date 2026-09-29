# i2d — Branch of i2c: a locator the lance never touches (a housing stub cut short, or a steel pocket on a post), first on the SN-2549 by hand

- **Branch of:** [i2c](i2c-cut-down-housing-locator.md). Its source is
  force-and-form's i2c′ and i2c″, their proposals for i2c.
- **Sketch:** [`../sketches/i2d-stub-locator.svg`](../sketches/i2d-stub-locator.svg) (schematic).
- **Numbers:**
  - [`../calc/wave2.out.txt`](../calc/wave2.out.txt) sections G and H [calc w2 X];
  - [`../calc/wave3.out.txt`](../calc/wave3.out.txt) sections C and D [calc w3 X];
  - change-the-question's [`on_into_the_housing_w3.out.txt`](../../change-the-question/calc/on_into_the_housing_w3.out.txt) [ctq w3 §n].
- **Coordinates** as in [`../handover.md`](../handover.md).
- **Related:**
  - combination K5 with force-and-form [f1](../../force-and-form/ideas/f1-motorised-ratchet-crimper.md)
    and hand-tool-as-press [a1](../../hand-tool-as-press/ideas/a1-squeezer-cradle.md)
    (below);
  - the flag route with change-the-question [c6b](../../change-the-question/ideas/c6b-by-hand-this-week.md)
    (below);
  - the stub as [k7](k7-pre-formed-contacts-crimped-in-the-cavity.md)'s
    pre-former nest;
  - [i5](i5-person-inserts-on-a-sensing-nest.md)'s bench downstream.

**What it changes from i2c.**
- i2c latches the contact into a cut-down housing by its lance, then lifts the
  lance to release it: three lance folds before the product housing.
- i2d keeps only the **front wall and the first ~1–1.5 mm of cavity** of a
  housing. The box nose stops on the front wall, the short cavity holds X, Z and
  roll, and the lance root never enters. The contact leaves with a plain pull.
- The axial reference becomes the box nose on the front wall, which is the
  product housing's own +Y stop.

## Picture it

**By hand, on today's tool (the first build).**
- **The stub.**
  - A kit XHP-2 is cut across, parallel to its mating face, keeping the front
    wall and 1.0–1.5 mm of cavity behind it.
  - A printed sanding jig with a depth stop sets the cut to ±0.05 mm
    [estimate]. Several are cut at 0.2 mm steps, and the right one is found by
    trial.
  - A strip of stencil foil on the stub's floor takes up all but 0.05–0.10 mm of
    the box's height clearance.
- **The carrier.**
  - The stub is pressed into a small printed carrier.
  - The carrier rides a printed **parallelogram flexure**, free ±0.2 mm in X and
    Z and stiff in roll.
  - In Y, a small spring holds the carrier back against the tip of a fine
    **adjusting screw** with a **10–30 N preload**.
  - The flexure is on a clip on the SN-2549's lower jaw, through the stock M4
    jaw screw lengthened to 20 mm. That is the mount the published SN-2549
    positioners use [source: Chief Delphi / Printables, Ryan Reed, via
    hand-tool-as-press].
- **Where it sits.**
  - The stub is in front of the jaws, its open (cut) face toward the XH nest,
    1.0–1.7 mm ahead of the anvil's front edge [calc w2 H].
  - The adjusting screw sets that distance once, with a contact in place under
    the camera.
- **One crimp.**
  1. With the tool open, Derek lays a loose kit contact lance-down in the XH
     nest and slides it forward until its box nose stops on the stub's front
     wall.
     - The box is now 1.0–1.5 mm into the stub, and the lance hangs free in the
       gap between the stub and the anvil.
     - His push, a newton or two, never lifts the carrier off the screw.
  2. He closes the ratchet one click. The contact is captive, square and at the
     right depth.
  3. He feeds the stripped conductor into the barrels until the insulation edge
     sits in the window, and completes the squeeze. As the conductor barrel
     coins, its front grows toward the box. The carrier lifts off the screw at
     its preload and moves forward the few hundredths the growth needs.
  4. He opens the tool and draws the crimped contact back out of the stub. No
     lance was folded, and the carrier springs back onto the screw.
- **What changes from today.** The contact is placed by a stop and a molded
  cavity, not by eye. Axial position, roll and box height are the same every
  time.

**In a cradle (combination K5).**
- The same stub, or its steel twin below, is the seat of force-and-form's
  swinging flap (f1) or hand-tool-as-press's squeezer (a1): the SN-2549 in a
  cradle, closed by a lead-screw actuator with a load cell.
- A keyed stick magazine or the person drops a contact into the flap, and the
  flap carries it to the nest.
- The box goes into the stub, and the actuator closes to the first click.
- A carriage threads the conductor, and the actuator completes the stroke.

**With snapped flags (change-the-question's c6b).**
- In c6b the contact is pre-formed and snapped onto its conductor in a printed
  block before it reaches the tool: a "flag".
- The stub is the box-keyed clip c6b wants on the SN-2549. It is molded at
  product tolerance, costs cents, and never touches the lance.
- The flag goes box-first into the open nest and forward until its nose meets
  the stub; then one squeeze. There is no one-click captive juggling.
- The stub squares the flag's roll, which the snap's friction alone does not
  (below).
- **The conflict.** With the stub in front, the flag cannot come in from the
  front with its conductor threaded back, which is c6b's fallback. So the
  SN-2549's open XH nest must pass box plus lance, 2.8–3.25 mm, by a lay-in
  from above between the open jaws or a slide in from behind. That decides this
  route, and it is unmeasured.

**The steel twin (i2d″).**
- A pocket laminated from laser-cut stainless stencil foil: the box's end-view
  shape plus clearance, with a **0.64 mm square post** standing in its front
  wall where the header post would be.
- The contact is pushed box-first onto the post, as it will be onto the board's
  wafer, until its nose touches the front wall.
  - The box's own spring grips the post (0.2–1.6 N [terminal-supply calc, Molex
    KK analog, secondhand]), so the contact stays put when released.
  - The pocket rides the same preloaded Y stop as the stub. A rigid steel wall
    at the nose would make the transition take the growth instead, as a bow of
    ~0.07–0.19 mm, which is JST's bend-up/down fault [ctq w3 §3].
- **The post is wired to an ESP32 input.** With the loom's far end in a terminal
  block (hand-tool-as-press's electrode array), the circuit closes when the
  conductor lies in the barrel. That shows **the conductor is in the contact,
  and it is the right conductor**, before the crimp.
- Steel does not wear where the box slides; PA6 does.
- After the crimp, a 0.2–1.6 N pull on the wire slides the contact off the post.
  A contact that stays on the post has not been crimped to its wire.

## At a glance

| | |
|---|---|
| **What locates the contact** | Y: the box nose on the stub's front wall, held by the 10–30 N preload against the adjusting screw. X, Z and roll: the stub's walls and floor shim until the jaws capture; then the SN-2549's steel nest, with the flexure letting the stub follow |
| **What locates the conductor** | Derek's hand and eye (by hand); a carriage (in a cradle) |
| **Reference for "fixed"** | The SN-2549's lower jaw; the adjusting screw's tip on the clip is the axial reference |
| **What drives the crimp** | Derek's hand on the SN-2549, or the cradle's lead-screw actuator |
| **What carries the crimp force** | The SN-2549's own frame and jaws. The stub carries at most its preload, 10–30 N |
| **How it knows** | By hand: the eye, and the proof-pull fork and crimp-height pocket of [i5](i5-person-inserts-on-a-sensing-nest.md). In a cradle: the actuator's force trace. With the post: continuity before the crimp and the pull-off after |
| **Steps it covers** | Place the contact on a locator (loose kit contacts), hold, crimp (by hand or cradle); with the post, conductor-in-contact and identity |
| **What it hands back** | By hand, everything the person does today except aiming the contact: placing each contact against the stop, feeding the conductor, squeezing. In a cradle, dropping contacts into the flap or a stick and presenting the ribbon |

## Why this arrangement exists

- Every cheap XH crimper lacks a locator [repo: `cable-assemblies.md`]. JST's
  WC-110 flap costs $537 with the tool [source S26].
- The other locators in the study each need something the kit contacts may not
  have:
  - hand-tool-as-press a1's 0.3 mm blade needs a neck between barrel and box
    long enough for it, unmeasured;
  - terminal-supply a2c's pilot pin needs strip contacts;
  - force-and-form f1's keyed flap is printed, and printed parts should guide,
    not set [digest].
- A housing stub is molded to the box at the product's own tolerance, costs a
  few cents, and uses the loose contacts on hand. It holds the box by its
  outside and its nose, the way the product does, and needs nothing from the
  neck.

## Mechanism, references and tolerances

**Axial (Y).**
- The box nose on the stub's front wall carries the barrels' position through
  the contact's own nose-to-barrel length, which is tight within one lot
  [assumption].
- The stub's Y relative to the anvil is set once by the screw, to the ±0.1 mm
  bellmouth window [digest].

**Growth at the bottom of the stroke** [calc w3 C; ctq w3 §3].
- Coining after the barrel fills lengthens the conductor barrel. Its front
  moves ~0.03–0.11 mm toward the box, and die friction can push with ~80–520 N
  [estimates].
- A rigid stop at the nose makes something give:
  - a fixed PA6 face dents (54–173 MPa on ~1.7 mm², around PA6's yield), and
    the reference walks forward with use;
  - a fixed steel face bows the transition.
- **The preloaded stop.** The carrier stays on the screw under the person's push
  and lifts off at 10–30 N.
  - The nose then bears 6–18 MPa on the PA6 face, a third or less of its yield.
  - The transition carries at most 30 N, against its ~90–310 N yield.
  - The spring is a small steel compression spring, not a printed flexure,
    so the preload does not creep away.
- A compliant stop with no preload also works if its stiffness is
  100–250 N/mm: the push moves the reference 0.004–0.02 mm, and growth raises
  the force only to 3–28 N.

**Which axial reference.** There are two versions:
- **Nose on the front wall** (above): no neck needed. The reference is farther
  from the barrels.
  - Clone drawings give ±0.25 mm on overall length. If most of that lies
    between nose and barrels, the nose is too far from the barrels to set the
    ±0.1 mm bellmouth window.
- **Stub for X, Z and roll only, with a 0.3 mm blade on the box's rear shoulder
  for Y.** hand-tool-as-press's neck blade holds ±0.08 mm [hand-tool-as-press
  calc §7].
  - The box nose then stops ~0.2 mm short of the front wall.
  - The blade needs a neck long enough for it and for the growth. The gap
    between blade and conductor-barrel front is t − 0.3 = 0.04–0.44 mm for
    t = 0.34–0.74 mm, which is marginal at the short end against 0.03–0.11 mm
    of growth.
- One side photo of a kit contact decides which version.

**Roll** [calc w3 D; ctq w3 §4].
- Roll is the smaller of (C − W)/H and (D − H)/W for a W × H box in a C × D
  channel.
- Clone boxes are 1.85–1.90 × 2.2–2.35 mm [source S19–S22]. In a 2.00–2.10 mm
  cavity, limited by width alone, they roll ±2.4–6.5°. The top of that range is
  above the 5° low end of the digest's 5–11° window.
- The floor shim leaves 0.05–0.10 mm of height clearance, which limits roll to
  ±1.5–3.1° whatever the width clearance. It touches only the box, ahead of the
  lance.
- Picking stubs from the tighter housings by trial also helps.

**The lance.** The stub may be deep only until the lance root would enter it.
- With the lance tip 2.24–2.64 mm behind the contact's front and a lance
  0.8–1.4 mm long [assumption], the box may enter 0.74–1.74 mm [calc w2 H].
- The anvil's front edge must sit behind the lance tip and ahead of the
  conductor barrel's front. That needs transition t ≥ 0.34–0.74 mm: the same
  condition as i2, and as the SN-2549 itself [calc w2 G].
- Holding the box in a stub changes nothing about it. If today's SN-2549 anvil
  is a plain block, the tool already proves the condition for these contacts.

**Height.** The stub floor (with its shim) must match the anvil top to
~±0.05–0.1 mm before the jaws close, or the contact is tilted when captured. The
flexure's Z freedom takes up the rest when the nest closes on the barrels.

**What the stub does not do.**
- It is not a wire stop: its face is 1–1.7 mm ahead of the barrel front, so the
  brush is set by the camera or the eye.
- It does not react a proof pull: the box nose stops +Y only. That is the neck
  blade's and the fork's job.

## Printed and bought parts

| Part | Source |
|---|---|
| Stub | A kit XHP-2 (CQRobot kit, Prime-confirmed [sourcing/amazon-prime.md]), or an XHP-2 from Digi-Key/LCSC (XHP-n from $0.025–0.12 [source S26–S28]) |
| Floor shim | A leaf from the Hotop 0.02–1.00 mm feeler set, $8.99, Prime-confirmed [sourcing/amazon-prime.md], or stencil foil |
| Preload spring | Dianrui 300-piece compression spring kit, $6.99, Prime-confirmed [sourcing/amazon-prime.md] |
| Sanding jig, stub carrier, parallelogram flexure, jaw clip | Printed PETG on the 0.2 mm nozzle [repo: `tools.md`] |
| M4 × 20 mm screw and nut, fine adjusting screw | Hardware |
| Steel pocket (i2d″) | Laser-cut stainless stencil foil, stacked ([JLCPCB stencil](https://jlcpcb.com/pcb-stencil), from $3 [source]) |
| 0.64 mm post (i2d″) | A pin pulled from a male header (the Prime-confirmed header listings do not state the pin section [sourcing/amazon-prime.md]), or loose square pins (sourcing request, Wave 3) |
| Far-end terminal block (i2d″) | Wago 221-415 lever nuts, Prime-confirmed [sourcing/amazon-prime.md] |

## Problems met, and how it answers them

1. **The stub fights the nest in X.** The parallelogram flexure lets the stub
   translate; it holds only Y and roll.
2. **The SN-2549's upper jaw hits the stub.** The stub sits wholly ahead of the
   jaws' front faces, 1.0–1.7 mm clear of the anvil. Whether the SN-2549's
   jaw faces are flush with the anvil's front edge is unmeasured. Holding the
   closed tool against a light shows it.
3. **PA6 wears where the box slides in.** 53 contacts a unit, ~3,200 over the
   program [shared context]. A stub is replaced when the camera sees the box
   sitting deeper; the steel pocket removes wear.
4. **Clone housings against clone contacts.** The stub is cut from the same kit
   as the contacts, so the fit is the product's fit.
5. **The contact backs out before the jaws close.** By hand, the finger holds it
   forward for the second the first click takes. In the steel twin, the post
   grip holds it. In a cradle, the flap's slot holds it until capture.
6. **Growth against the nose.** The preloaded stop (above).
7. **Loose roll with small clone boxes.** The floor shim (above).

## Contribution

- A locator for loose contacts made from the product's own housing, on the tool
  Derek already uses. It is a first step that works the week it is made, with
  no motor.
- The contact's first lance fold happens in the product housing, not before.
- The steel twin adds a conductor-in-contact and conductor-identity check before
  the crimp, and a crimp-held check after.
- It names the condition every flat anvil shares with it (calc w2 G), so one
  look at the SN-2549's anvil answers a question for i2, i2d and the machine
  cradles at once.
- The preloaded stop is a rule any front stop can use, including
  change-the-question's c1c front stop and c6b's clip: hold until capture, then
  give way to growth.

## Major unresolved problems

- **The stub depth.** Lance length and root position are unmeasured; the right
  cut is found by trial with stubs at 0.2 mm steps.
- **Whether the SN-2549's jaws and nest leave room** for a stub 1.0–1.7 mm ahead
  of the anvil, and whether its open nest passes a flag's box and lance
  (2.8–3.25 mm).
- **Height match** between the stub floor and the anvil top before capture.
- **Growth.** Whether it is 0.03 mm or 0.1 mm, and how it divides front and
  back.
- **Post grip** of the kit contacts (i2d″) is unmeasured.
- **Nose or shoulder** as the axial reference, which turns on where the kit
  contact's length tolerance sits.

## What rests on assumptions

- Lance length 0.8–1.4 mm and tip 2.24–2.64 mm behind the front [source S22 for
  the tip; length assumed].
- Cavity width 2.00–2.10 mm [estimate].
- Growth 0.03–0.11 mm and its force [ctq w3 §3, estimates].
- Contact length within a lot tight enough for the box nose to carry the
  barrels' position [assumption].

**Measurements that settle it.**
- Growth: five SN-2549 crimps with the box nose touching a steel feeler leaf
  held across the front of the nest, and five with the nose free, then
  side-on photos under the ELP camera. Does the transition bow?
- Stubs at 0.2 mm steps, each tried with a contact under the camera.
- The SN-2549 closed against a light: jaw faces against the anvil's front edge,
  and the full-open gap at the XH nest.
