# Shared context — weld positioning exploration

Assembled by the coordinator on 2026-09-28 from Derek's statements, the repo's
fabrication sources, the XLaserlab X1 Pro manual, and earlier conversations.
Every explorer receives this file. Each item is labelled by where it comes from:

- **[Derek]** — Derek's own statement (quoted where the wording matters).
- **[Repo]** — a value or relationship in the repo's current fabrication sources.
- **[Manual]** — XLaserlab / Xphotonics X1 Pro user manual.
- **[Agent]** — an estimate, proxy or proposal made by an earlier agent. None of
  these is a requirement.
- **[Unknown]** — not measured; work through plausible alternatives and label them.

## Derek's goals, in his words

> I do need agents to consider low lead times and low prices and high sales volume, as this dramatically impacts the feasibility of any option, and is something agents training corpus has made them woefully inept on, because "real" manufacturers, real engineers, are so often working in places where "quotes and 6 to 8 week lead times" are SOP, and so we have this unique aspect of our situation that must be considered. And there are others, like that I like building things, and I like printing things. And this is fun for me, and I'd like to build something. But I also like making things that work, that really function, and function very well.

> No, no budget for any of this please. That's a much later reason to cut an idea, not a reason to stop it early.

What the equipment is for **[Derek]**: learning to reliably weld the carbonator.
Repeatability makes each physical experiment informative: reproduce a baseline,
deliberately change a parameter, and interpret the result. The knowledge should
accumulate in equipment and a reproducible process, so success can eventually
be transferred to someone besides Derek. From an earlier conversation:

> If I learn the skill on my own, how to hold the gun, how to release, then I become the bottleneck. If I document the parameters and build a rig that allows those parameters to be flawlessly executed, then we've solved the problem in a way where there is no bottleneck. But that's not the only benefit of repeatability. Repeatability also changes the shape of the learning curve. The only way we can really form a hypothesis and test it is if we can do the same thing over and over again in the same way, or at least as much in the same way as possible.

Positioning and aiming the X1 Pro gun relative to the tube and recessed endcap
are central. Measurement, support, cable handling, workpiece positioning, and
how an arrangement is used can change that problem substantially **[Derek]**.

Derek has also described motorized positioning and software-controlled
observation, with an AI able to conduct repeated laser-dot dry-run experiments
across tubes. Manual setup and partial arrangements remain useful contributions
to that broader goal **[Derek]**.

Scanning a gun and printing a shell that fits it are established capabilities
here **[Derek]**. He has described the gun as "gripped along its length" by a
custom printed shell that encloses most of the gun except the tip **[Derek]**.

## The joint and workpiece

- Tube: 5.000 in (127.0 mm) OD × 0.065 in (1.65 mm) wall welded 316L, 152.4 mm
  long; bore at the weld Ø123.70 mm **[Repo]**.
- End plate: 1/4 in (6.35 mm) 316L disc, Ø4.860 in (123.44 mm), an ID slip-fit
  plug with about 0.005 in radial slip. It sits **recessed 6.35 mm below the
  tube rim**, so a 6.35 mm lip of tube wall stands proud above it. Two 7/16 in
  (11.13 mm) port holes lie on one diameter, 0.75 in (19.05 mm) either side of
  centre **[Repo]**.
- The weld is an **inside-corner fillet** between the plate's upward face and
  the tube bore: a flat circle Ø123.70 mm, 388.61 mm around, on the tube's own
  axis. The beam is directed into the thick plate and washes onto the tube
  wall. The unbacked 6.35 mm lip above it distorts if heat dwells **[Repo]**.
- The gun reaches the recessed corner **through the open interior of the
  tube**, from above; it cannot reach around the outer wall to the inside
  corner **[Derek]**.
- Both closures are welded downhand with the tube vertical; the carbonator is
  inverted for the second closure. Rotating mass 1.40 kg for the first
  closure and 2.01 kg for the second **[Repo]**. The float rod and captive
  float are inside by the second closure **[Repo]**.

## The existing rotator

**[Repo]**, from `hardware/assembly/weld-rotation-rig.md` and
`hardware/printed-parts/fixtures/weld-rotator/README.md`:

- It stands the tube vertically and turns it under a gun it does not carry.
  PET-GF base 300 × 250 × 12 mm on four 24 mm feet, four Ø10 mm bench-clamp
  holes, a 36-ball race on a 165 mm circle, NEMA 23 belt drive at 4.5:1 on a
  motor tower to one side, and a ground tower whose copper shoe wipes the tube
  OD as the welder's work contact (the arm's top is 91 mm above the base
  bottom). A Ø90 mm passage through the centre gives purge access to the lower
  plate's ports.
- The tube's working rim is 214.4 mm above the base bottom and **238.4 mm above
  the bench** on the current feet, so the joint is about 232 mm above the bench.
- The tube is located by a nest: an ID pilot, an OD guide and three M3
  adjusters. The procedure accepts ≤ 0.25 mm radial TIR and ≤ 0.30 mm face TIR
  at the weld end. Those are acceptance limits in a procedure, not measured
  behaviour.
- Control: a foot pedal is the whole control. Held, the table turns at the
  stored speed; released, it stops. Bead travel 5–15 mm/s (default 8 mm/s =
  1.235 rpm, 48.6 s per revolution). Direction cw/ccw is stored. The console
  reports degrees turned; nothing counts laps. 14,400 pulses per table
  revolution (0.025°, 0.027 mm at the bead). The belt train is backdrivable and
  the driver releases 10 s after a stop.
- Current per-weld sequence: wire placed on the arriving side of the puddle for
  the verified direction; hold the head at angle and standoff; press the pedal;
  hold the laser trigger once rotation is steady; carry about 20° past the first
  tack; release trigger, then pedal. A wire that sticks is snipped between the
  wire nozzle and the bead while the head stays put.
- Recorded hand practice (not qualified): 60 % power, wobble 80 Hz × 2 mm, wire
  12 mm/s, argon 2 s pre/post, ER316L 0.030 in filler, 8-tack pattern.

The study changes none of this; explore freely around it, including moving,
remounting, tilting or rebuilding a rotator as part of an arrangement.

## The X1 Pro gun and its cables

**[Manual]** (section 3.4 drawing and specification table; rendered pages at
`/private/tmp/x1-pro-weld-pages/page-17.png` and `page-12.png`,
cable rules on `page-20.txt`):

- Pistol form, **253 mm** from nozzle tip to the back of the body, **143 mm**
  tall, **34 mm** wide. Along the barrel: copper nozzle → graduated tube (sets
  nozzle extension/focus) → protective-lens drawer → focusing lens → body with
  the **motor** (the wobble; "the laser head contains a vibration motor; handle
  it gently"). Status and process LEDs on the body. The grip rakes back and
  holds the collimator; the **QBH fiber exits the grip butt**. Light switch
  (trigger) and process switch on the grip front. **Wire-feeding bracket**
  under the barrel just ahead of the body.
- Fiber cable 5 m. Minimum bend radius **35 cm while emitting**, 24 cm stored.
  "Twisting is strictly forbidden."
- Reference (aiming) beam 630–670 nm, 0.3 mW — the laser dot used for dry runs.
- 1080 nm, 700 W peak; shielding gas through a 6 mm OD tube.
- Gun weight is not given.
- Earlier agents read the manual as describing an RS232 port and a DB25 port
  "for PLC integration" on the laser unit **[Agent; not re-verified]**.

**[Derek]**: the external wire feed is separate from the gun's umbilical; they
run together near the grip base. The single wire feeder is a separate box on the
welding cart with its own conduit to the gun's wire bracket **[Repo/Agent]**.

## Orientation: the three rotations about the dot

The [3D orientation scene](https://homesodamachine.com/weld-position),
documented in `hardware/assembly/weld-position.md` (source
`web/public/js/weld-position/pose.js`), holds the relationships Derek worked out
in conversation. Its coordinates: +Z up, tube axis vertical, the weld station on
the +X side; the laser dot sits at the inside corner on the +X radius, so the
tangent there runs along ±Y.

- **Tangent [Derek]**: at zero grip-axis and vertical-axis rotation, the gun's
  length and the wire's final approach follow the tangent in plan view. "The
  reason the base of the gun must stay tangent, is because it controls the bend
  of the wire feed. The umbilical does not actually contain the wirefeed, but
  the umbilical does come out the base of the gun, and it is easiest if we keep
  the wirefeed and umbilical together. And the wire feed must be as straight as
  possible in terms of causing the tip of the wirefeed to point precisely where
  we want, tangent and pointing at our laser dot."
- **Grip axis [Derek]**: the line through the precise laser dot and the cable
  exit at the bottom of the grip. Rolling about it keeps both points fixed and
  tips the laser between endcap and tube wall. Its purpose is the wall/cap
  split of the wobble pattern: "If we leave it precisely as I described, we
  either get 100% of tube wall or 100% of endcap, depending on the XY
  position. We roll it to point at both wall and cap."
- **Hole axis [Derek]**: through the laser dot and both endcap hole centres —
  the horizontal radial line at the cap's outer face. Rotating about it tilts
  the entire gun (and grip axis); increasing it raises the grip.
- **Vertical axis [Derek]**: parallel to the tube axis through the dot; turns
  the whole gun in plan away from the tangent, carrying the other two axes.
- Opening pose in the scene: grip 45°, hole 30°, vertical −15° — close to the
  orientation Derek has been using by hand **[Derek]**.
- The gun proxy's housing sections, 60° initial pitch, 16 mm nozzle clearance,
  wire-guide brace and 2 mm straight sweep are **illustrative [Agent]**. The
  scene does not compute wall/cap energy split.

All three axes pass through the dot, which sits inside the tube 6.35 mm below the
rim, against the wall. The mechanism does not have to reproduce these controls
as literal physical joints. Equally, software coordinates do not remove physical
constraints imposed by a support.

Lever arms, for intuition (plain geometry; the 279 mm is the scene proxy's
dot-to-grip-base distance, not a measurement):

| Distance from the dot | 1° about the dot moves it | 0.1 mm there turns the gun |
|---:|---:|---:|
| 50 mm | 0.87 mm | 0.115° |
| 150 mm | 2.62 mm | 0.038° |
| 279 mm | 4.87 mm | 0.021° |
| 400 mm | 6.98 mm | 0.014° |

## How to think about support, motion and travel

- A printed shell can support the gun along its length and contain attachments
  wherever useful. An actuator attachment, weight-bearing support, effective
  pivot, and cable support can all occupy different locations. Do not collapse
  them into one assumed "grip point." **[Derek]**
- Manual setup can establish a working neighbourhood before fine adjustment.
  Small angular changes can still produce substantial travel at distant points.
  The useful travel depends on the arrangement; it has not been specified.
  Movement can be divided between gun, workpiece, supports and setup
  adjustments. The positioning problem does not require a conventional
  six-motor arm. **[Derek]**
- Setup and weld are different phases; so are the first and second closure,
  a tube change, and a stuck wire.

## Unknowns that matter

Work through plausible alternatives; label which you assume.

- Gun mass and centre of mass; mass and stiffness of the umbilical (fiber, gas,
  signal) and of the wire conduit; how much they pull or spring back as the gun
  moves. **[Unknown]**
- Trigger force and whether the trigger must be pressed by hand. **[Unknown]**
- Which way the wobble sweeps relative to the gun's axes, and the true optical
  geometry (focus standoff, beam vs. reference-beam coincidence). **[Unknown]**
- How precisely the dot, angles and standoff must be held for a good bead —
  the process window is not established. **[Unknown]**
- The useful travel for each motion. **[Unknown]**
- How the tube's actual runout, ovality and reseating compare with the
  procedure limits. **[Unknown]**

Numbers that circulated in earlier conversations, each an agent's proposal and
**none a requirement**: dot held within 0.1 mm and standoff within 0.3 mm during a
weld; 0.02–0.05 mm adjustment resolution; 0.25° angle resolution; a 40–75° angle
range; a ~1 kg gun; the scene's 60° pitch and 16 mm clearance.

## Shop and equipment on hand

**[Repo]** ledger, **[Agent]** where marked:

- Two Bambu Lab H2C printers (PET-GF, PETG, TPU and more; large build volume),
  AMS units, heat-set inserts, M3/M5 hardware.
- Revopoint MINI 2 structured-light scanner (0.02 mm stated), scanning spray.
- ELP 16 MP autofocus USB camera.
- Neoteck 0.0005 in dial test indicator with a magnetic base; calipers.
- WEN 4208T drill press, WEN BA4555 metal band saw, taps and dies.
- The X1 Pro itself, which can weld steel and stainless structure.
- Strong Hand magnetic V-pads; Knipex cutters; argon at the welding cart.
- VEVOR adjustable-height workbenches with wooden tops: two 48 in on casters
  with pegboard, two 72 in heavy-duty. Height range 28–39.5 in **[Agent]**.
  The rotator was clamped to one of them **[Agent, as of 2026-09-25]**.
- Weldpro 3-tier welding cart carrying the welder and argon cylinder.

## Sourcing

**[Derek]**: a part may come from any vendor when it is currently available,
has a short lead time, and sells in enough volume or standardisation that it is
likely to be available again in 6 months or a year:

> If there are parts needed elsewhere even, I would like that agent to be able to proceed with a plan if they do find something in stock with low lead time and dealt in large enough volume to be likely to be available again in 6 months or a year.

On Amazon only Prime listings count; non-Prime listings do not exist for Derek —
do not read or mention them. Search ordinary retail and widely used component
ecosystems, including products sold for unrelated purposes. Printed adapters
can connect those components into something specific to this gun.

Capture, for each representative part that matters to an idea: source link,
observed date, price, stock/delivery signal, and the evidence for volume or
interchangeability. Distinguish direct observations from estimates. A familiar
brand or a listing's existence does not by itself establish volume, delivery or
future stock. One or a few representative sources can establish that an idea
has a practical route; no complete parts lists.

## Boundaries

Do not change the current hardware design or welding procedure, operate
equipment, order anything, or contact vendors. Questions that need Derek's
observations go into your notes for the result; they are not a reason to stop.
