# Notebook — force-and-form

A running log across the waves: what was worked, what was set aside and why, and
what would revive it.

## Log

- **Read the context.** Read `brief.md`, `shared-context.md`,
  `working-method.md`, `xh-facts.md` and `prior-art.md`. Took the facts
  pass's force bounds as the starting point: 0.75–2.3 kN conductor, peak at
  bottom dead centre (BDC), compaction in the last 0.1–0.2 mm, ~0.3–0.4 J.
  Did not re-derive them.
- **Built a force family.** Five force–position shapes (low, central, high,
  high + cut-off, steep) so drive conclusions could be tested against shape,
  not only magnitude ([`calc/stroke_model.py`](calc/stroke_model.py)).
  - Work per crimp in the family is 0.13–0.48 J, which brackets C1's
    0.3–0.4 J.
  - About 40 % of the work goes in the last 0.2 mm.
- **Checked what slowness changes.** From a published copper-alloy
  strain-rate test, flow stress rises ~5–7.7 % from quasi-static to 5.65/s
  (<https://pmc.ncbi.nlm.nih.gov/articles/PMC11242886/>). A slow press
  therefore needs a few percent less force for the same shape. Beyond that:
  - there is no inertia at BDC;
  - adiabatic heating is ≤16–26 K even at production speed, and nil when
    slow;
  - springback changes by about a micron.

  Nothing found says slowness hurts a crimp. JST's MKS-L manual says a bench
  applicator's speed "is dependent upon the skill level of the operator".
- **Sized drives against the family** ([`calc/drives.py`](calc/drives.py)):
  - A crank needs <3.3 N·m, applicator springs included, and 1° of crank
    error at BDC is 3–4 µm.
  - A knee needs 60–160 N at its pin, and 0.2 mm short of straight is ~1 µm.
  - A direct screw needs the whole force and has no geometric bottom.
  - A 20:1 arbor press needs 150 N at the handle for 3 kN, and has no bottom
    either.
  - A ratchet hand tool needs 40–250 N at the grip if its ratio is 10–40:1.
- **Stiffness** ([`calc/force_loop.py`](calc/force_loop.py)). The first cut
  of the scatter calculation forgot that the crimp's own steep curve is a
  spring in parallel. Redone:
  - Scatter from ±25 % force variation stays inside ±0.05 mm even for a
    printed frame.
  - A printed frame's **offset**, 0.2–0.85 mm open at peak, drifts with creep
    and temperature, and that is what disqualifies it as the crimp's force
    loop.
  - The die blades themselves compress 50–80 µm at peak, constant from crimp
    to crimp.
- **Metrology** ([`calc/metrology.py`](calc/metrology.py)).
  - Re-touch at 10 N reads crimp height to about a micron of blade
    compression.
  - The model's steep curve says one missing strand drops peak force 5–12 %.
    Industrial crimp-force-monitoring experience says ~0.8 % for 1 of 60.
    The industrial figure is used, and the model is marked as an upper bound.
- **Placement** ([`calc/placement_budget.py`](calc/placement_budget.py)).
  - The contact needs ±0.1 mm axially and ±0.15–0.3 mm laterally at first
    touch, and not before.
  - The conductor needs ±0.2–0.3 mm.
  - The dangerous direction for the conductor is vertical: strands above a
    wing tip. Capture-then-thread removes it.
- **Gang** ([`calc/gang.py`](calc/gang.py)).
  - Minimum station pitch is 3.8–4.7 mm; 2.5 mm is impossible.
  - Summed force sees one missing conductor in 3–5 stations only
    marginally.
- **Sourcing** (web, 2026-09-28): the OTP applicator (eBay $150–160,
  Alibaba $200–250), iCrimp SN-2549 ($20.99), SN-2549 jaws ($9.99), the
  StepperOnline NEMA 23 + 30:1 worm (C$76.69), the Harbor Freight 1 t arbor
  press ($79.99, 5-1/2 in maximum height), JST MKS-L manual facts, JLCCNC wire
  EDM at ±0.05 mm, Mitutoyo SPC indicators ($451–668), and TouchDRO
  ESP32 scale reading. The session's web-search budget ran out before a
  desktop CNC gantry price was found.
- **Wrote the ideas.** f1, f1b, f2, f2b, f3, f3b, f4 and f5, the summary,
  sketches and sourcing requests.

## Findings that changed an idea while writing

- **Continuity as a wire stop fails.** The strands touch the metal barrel
  on the way in, long before the tip reaches depth. f1's depth reference
  became carriage Z, zeroed by the camera on the bare tip.
- **The carrier strip is a floor, not a wall.** The tab continues the barrel
  floor at the rear, so a conductor can be threaded axially over it. That
  lets f3 capture first and thread second while still on the strip.
- **A crank on a worm gearbox's output** puts the crimp reaction on the
  gearbox's bearings. The crankshaft gets its own bearings, and the gearbox
  becomes a torque source on a torque arm (f2).
- **The Harbor Freight 1 t arbor press is too short** for a mini-applicator:
  139.7 mm maximum against 166–176 mm needed (f2b).
- **The tab lies under the conductor in a gang cassette.** The shear has to
  come from below, as an applicator's floating shear does (f5).

## Rejected or parked directions

| Direction | Why set aside | What would revive it |
|---|---|---|
| **Printed die faces** for the conductor crimp | A wing tip on a printed face reaches thousands of MPa against ~50–100 MPa [calc: force_loop §4] | Nothing for the conductor barrel. An insulation-only station with a steel insert on a printed body is conceivable |
| **A printed frame as the crimp's force loop** | Its 0.2–0.85 mm offset at peak drifts with creep and temperature | Per-crimp re-touch closing the loop on crimp height, or a hard stop in a steel local loop (both in f3 and f5) |
| **Direct lead screw to crimp height** (no linkage, no stop) | BDC follows lost steps and frame stretch one to one | A gauge across the dies closing the loop; it then becomes f3 with a screw for a knee |
| **Drill press as the crimp press** | The WEN's quill bearings and cast table were not designed for 2–3 kN axial loads [assumption; the WEN manual was not read for a thrust rating]. It could push a self-stopping cassette, but its bearings would carry the peak | Evidence that its quill bearings tolerate ~3 kN static. It stays usable for light stations (f3b's station A) |
| **Hydraulic "syringe" press** (a stepper pushing a small master piston into a slave cylinder; pressure = force) | More parts than a knee for the same result | If a force sensor under the anvil proves hard to seat, a pressure transducer is a clean force signal |
| **Incremental narrow-band coining** | Metal escapes sideways from a narrow band; the crimp form is non-standard | Sectioned crimps showing compaction equal to a full-width die (noted in f3b) |
| **Stripping in the same press** (JST lists a strip-crimp applicator) | Silicone's tear behaviour under blades is untested (Open item 5 in the repo) and belongs to the stripping explorers | A blade-strip result on this ribbon from another explorer |
| **Ultrasonic in-die crimp verification** (NASA Langley) | Transducers in dies are a research build | If a quality question arises that force and height cannot answer |
| **Magnetic pulse crimping** | The opposite of slow; not relevant | — |

## Questions for Derek

These were written for `summary.md`, but the session's harness refused that
file, so they went back to the coordinator in the structured return. The same
questions:

1. **SN-2549 handle force and travel.** Squeeze the SN-2549 through one XH
   crimp with a luggage or bathroom scale at the handle ends, and note the
   handle travel from first jaw contact to release. This sizes f1's actuator.
2. **SN-2549 release and jaws.** Does it have a ratchet-release lever? Which
   jaw carries the XH crimper, and which the anvil?
3. **Crimp height today.** Crimp five contacts on the ribbon with the SN-2549
   and caliper the crimp height at the barrel centre. It calibrates every
   idea here, and is the facts pass's Unresolved 1.
4. **Carrier strip.** Is any SXH or clone contact strip on hand? Its pitch,
   pilot hole and tab length decide f3, f4 and f5. Digi-Key's 100-piece strip
   is $4.71.
5. **Split length.** How long a split, meaning individual conductor length
   behind the housing, can each loom carry? f5 at strip pitch wants
   25–40 mm; f4's comb wants ~5 mm pitch.
6. **Shop press.** Does the VEVOR 12-ton have a pressure gauge, and are its
   bed plates flat enough to seat a cassette?
7. **Applicator.** Is an OTP applicator ($150–250) plus strip contacts
   within what you would buy? And would genuine JST strip or matching clone
   strip be the contact supply?
8. **Steel.** Is ordering laser-cut steel plate and drilling or reaming on
   the WEN something you would do?
9. **Crimp standard.** Is today's SN-2549 crimp the standard a machine should
   reproduce, or should a machine aim for JST's own profile (WC-110,
   applicator or EDM dies)?

## Wave 2 exchange: on into-the-housing

- **Written.**
  - The exchange file:
    [`../../exchange/force-and-form--on--into-the-housing.md`](../../exchange/force-and-form--on--into-the-housing.md).
  - Its numbers:
    [`calc/on_into_the_housing.py`](calc/on_into_the_housing.py), output
    [`calc/on_into_the_housing.out.txt`](calc/on_into_the_housing.out.txt).
- **For revision of this explorer's own ideas.**
  - **Lance relief.** Every anvil here (f3, f4, f5, and harvested SN jaws
    closed straight) needs one. The lance hangs 0.6–0.9 mm below the floor,
    2.44 ±0.20 mm behind the contact front, under the front of the conductor
    barrel.
  - **Feed-length rule.** f4 and f5 crimp off the seated position. f5 leads
    into into-the-housing's i3 fan plate and gang push (exchange K3).
  - **f1's locator.** It becomes a non-latching XHP stub (exchange K5).
  - **A new branch to develop.** f3/f4 as the narrow in-row press for i2
    (exchange K1): a 3.1 mm conductor step with ~0.8 mm walls, dies that bottom
    on the anvil block's shoulders below the floor, and a side-entry C.
  - **Order of checks.** The crimp proof pull (~20 N) must come before
    insertion; after latching, only a latch tug of 5 N or less.

## Wave 2: revise and a new direction

- **Read.** change-the-question's critique
  ([`../../exchange/change-the-question--on--force-and-form.md`](../../exchange/change-the-question--on--force-and-form.md)),
  the digest, and the other eight summaries. New numbers are in
  [`calc/wave2.py`](calc/wave2.py) with output
  [`calc/wave2.out.txt`](calc/wave2.out.txt); sketches for the new files come
  from [`sketches/make_sketches_w2.py`](sketches/make_sketches_w2.py).
- **Repaired in place.**
  - f1: swinging flap loaded outside the jaws; neck blade as wire stop, touch
    sensor and proof-pull reaction; contact supply and call rate set out
    (67 / 15 / 14 / 34 calls per unit).
  - f1b: locator and profile taken apart; the reference crimp judges the
    profile before $536 is spent; the stop accepted only inside a position
    window.
  - f2 and f2b: how a fork gets between touching conductors; both dials,
    the insulation wedge set into this wire's window.
  - f3: flush pilot pin from below; order pilot, capture, thread with the
    carrier in tension, crimp, re-touch, cut, pull on the box's rear face;
    lance relief; chase-the-height variant; knife sets as die route d.
  - f3b: one station, three finishes; gang station A needs a steel stop.
  - f4: head leaves toward the box, anvil drops for the lance, no funnel.
  - f5: loom map in the force band, lance relief, every-k-th variant.
- **Where I disagree with the critique, and why.** Break 3 on f1 put the
  captured insulation barrel's clear width at the pinched tips (1.4–1.6 mm)
  against a 1.7 mm conductor. The tips stand 0.7–1.0 mm above the conductor's
  top; the conductor meets the wings at its equator, where a wing hinged at its
  root is still near the floor width. Least clearance is −0.17 to +0.17 mm
  across floor widths of 1.6–2.0 mm [calc: wave2 §1], and a contact rated for
  1.9 mm insulation argues for a floor of 1.8–2.0 mm. The repairs are kept
  anyway.
- **Findings that changed ideas.**
  - SN jaws closed straight instead of on the tool's arc: at 10–35 mm from the
    pivot, one wing leads by 0.05–0.17 mm at first touch in the tool and the
    roll at compaction is under 1.2°. Straight closure is the more symmetric
    one. This retires wave 1's main worry about die route a [calc: wave2 §2].
  - On this silicone the insulation crimp is not a pull-out grip (strands slip
    inside the jacket at 0.4–9 N), and the jacket is invisible in the stroke's
    force (1–13 N against 30–130 N of wing forming). It must be set by
    position, and its window has a floor (cut) and a ceiling (cavity), roughly
    2.0–2.2 mm tall at 1.8–1.9 mm wide, above the clone spec's 1.80 mm
    [calc: wave2 §5]. That became f6.
  - Continuity cannot see a cut at the insulation barrel: the wing tips touch
    the same conductor. Bend-and-look can [calc: wave2 §7].
  - The neck blade needs no far-end wiring when the contact sits on grounded
    steel [calc: wave2 §11].
  - In a one-piece EDM crimper plate at 5.0 mm, webs between channels are
    3.0–3.5 mm, not the 0.6–1.5 mm of separate crimpers side by side. That
    makes f5b's gang steel easy.
  - Reloading a crimp in the same direction retraces elastically to the
    previous peak, so a crimp can be approached in hits and measured between
    them.
- **New files.** f6 (new direction: insulation crimp on silicone, two blades,
  two drives), f7 (new direction: die sources as cartridges), and combinations
  f5b (f5 × c1), f8 (i2 × f3/f4), f9 (c1b × f3-t), f2c (f2 × c1 × c5).
- **Sourcing this wave.** Web search was used up. SendCutSend's materials pages
  fetched (laser-cut ±0.005 in; 1095 annealed, MagnaCut, AR500; no heat
  treatment service). crimpapplicator.com's KS-EM40R page fetched (135.78 mm
  shut height, 40 mm stroke, 4 kg, CH/IH wedge adjustment at 0.02 mm over
  2 mm, 19 mm tooling width). eBay refused (403); PCBWay's wire-EDM page 404.
  Knife-set and EDM prices remain estimates.

### Rejected or parked in wave 2

| Direction | Why set aside | What would revive it |
|---|---|---|
| **A sprung, force-limited insulation crimper** | Silicone pushes back 1–13 N against 30–130 N of wing forming; a spring preload set by the metal cannot feel the jacket | A jacket much stiffer than silicone |
| **A round anvil from a needle roller or gauge pin** | A convex anvil of 1.5–4 mm diameter lets the barrel floor bend around it and pushes the wing roots into the gap beside it | A roller with a ground flat, which is no longer a bought part |
| **A B-roof crimper from two pins side by side** | Two pins make convex bumps with a notch between, the inverse of a B roof's concave arches and centre cusp | — |
| **Laser-cut steel laminations as die faces** | ±0.127 mm laser cutting against ±0.01 mm for a channel, and a laser's heat-affected zone sits exactly on the working edge of hardened sheet | Photo-etched hardened sheet (no heat, ±0.01–0.02 mm on thin stock), if a quick-turn source appears |
| **A lengthwise lance slot in f4's anvil** | Leaves the conductor barrel's floor unsupported at its centre during compaction | — (the anvil drops instead) |

### Questions added for Derek

1. Five of today's SN-2549 crimps: caliper the insulation crimp's height and
   width, then bend each 60–90° three times over a 2 mm pin and look at the
   jacket at the barrel under the ELP camera. Is any jacket cut?
2. One kit contact end-on under the ELP camera: the insulation barrel floor's
   inner width (f1's bore at capture), and side-on: the transition from box
   to conductor barrel (f8's decisive unknown) and the neck's length.
3. The SN-2549's jaws: how far is the XH nest from the moving jaw's pivot?
4. Would you buy an OTP XH knife set (price unobserved, China post) to make
   the second die cartridge, and would you send a crimper profile out for
   wire EDM once a traced drawing exists?

## Wave 3: the exchange on procedure-is-the-machine, then the final pass

- **Written first (exchange).**
  [`../../exchange/force-and-form--on--procedure-is-the-machine-w3.md`](../../exchange/force-and-form--on--procedure-is-the-machine-w3.md),
  numbers in [`calc/exchange_procedure_w3.py`](calc/exchange_procedure_w3.py).
  It proposed FP1 (lift once, fin from below), FP2 (camshaft turns a knee),
  FP3 (p7 strips for f2c), FP4 (one strip line for a gang) and FP5 (the reel as
  the qualification rig), and its "from procedure-is-the-machine into
  force-and-form" list: camera bare length as the axial reference, identity
  through the far end, lift once so f4 needs no planes.
- **Read for the final pass.** ribbon-as-pallet's reading of force-and-form
  ([`../../exchange/ribbon-as-pallet--on--force-and-form-w3.md`](../../exchange/ribbon-as-pallet--on--force-and-form-w3.md))
  and its calc; the Prime-confirmed table; my own exchange above.
- **New calc:** [`calc/final_w3.py`](calc/final_w3.py), output beside it:
  bend strain by pin diameter; the tab shear under a tack comb; the neck blade
  used only for the pull; the fork's set in f1; 0.7 mm walls in f8; both
  half-rows in one shoe; target height against channel width; one pallet at
  housing pitch in f2c; latch retention; camera against touch-off.
- **Corrected in my own calc.** `wave2.py` §7 labelled its pins by radius and
  the idea files read them as diameters. The labels now say radius; f6 uses
  final_w3 §1's diameters: a 2 mm pin gives strain 0.46, and a cut gapes
  0.23–0.56 mm, not 0.15–0.37.
- **New idea files.** [f9b](ideas/f9b-tack-on-the-strip.md) (ribbon-as-pallet's
  K1: dock on strip, tack, shear, crimp in a keyed nest) and
  [f10](ideas/f10-lift-once-fin-from-below.md) (FP1, with FP2 as a branch).
- **Changed in place.** f1 (hold short of the first tooth; camera depth; neck
  blade only for the pull; the fork's set); f1b (target height at each crimp's
  width); f2 and f2b (Prime rows; which presses open far enough; handwheel);
  f2c (one pallet at housing pitch, p7 stripping, p6 puller); f3 (camera depth,
  capture height from the floor width, channel ±0.05 with a measured width,
  latch 14.7–19.6 N); f4 (tip probe; both planes crimped before any housing
  move; f10 as the no-planes form); f5 (strip after the fan, per-station
  identity, per-conductor pull); f5b (merged row and one housing move; grooved
  fan block; strip after the spread; the one-shoe branch); f6 (bend down; drop
  section of track; bend nest; row bend; K5); f7 (width measured, height set
  for it; laminated shim anvil; Prime rows); f8 (0.7 mm walls, floating nest
  required, comb behind the rear face); f9 (the other plane at C, the pallet as
  datum, the tack's loads settled on paper).
- **Sketches.** [`sketches/make_sketches_w3.py`](sketches/make_sketches_w3.py)
  redraws f1, f3, f4 (top view), f5b and draws f9b and f2c; `make_sketches.py`
  now writes only f2 and f5, `make_sketches_w2.py` f4b, f6, f7 and f8 (labels
  updated). The FP1 sketch is f10's.

### Where I agreed, and where the physics says something different

- **B1 (the later half-row has no feed).** Agreed. It is the feed-length rule
  applied to two groups from one web; f5b, f2c and f4 now insert both planes
  together.
- **B2 (strip before spread, V-tooth comb).** Agreed; my S-bend model gives a
  slightly larger pull-back (0.6 d²/L against d²/2L), which only strengthens
  it.
- **B3 (bend-and-look closes the cut).** Agreed, and the pin-radius error was
  mine.
- **B4 (the other plane at C).** Agreed; f9b removes planes, f9 keeps them with
  the clamp face at the split root.
- **B5 (f1's set).** Agreed and extended: bending the neighbours in one arc
  above the 67 mm set radius shortens a 30 mm conductor only 0.25 mm, so no
  version of f1 avoids the set; the fork can only choose its direction.
- **B6 (f8 rubs the neighbours).** Agreed; 0.7 mm walls.
- **K1's proof pull through a 3–5 mm throat jaw.** The strands slip inside a
  squeezed jacket at 1.4–6.3 N per mm of grip at 30 % squeeze, so a 3–5 mm jaw
  reaches 20 N only at the stiffer end. f9b reacts the pull at the ribbon
  pallet's web clamp instead, with the neck blade holding the box.
- **K1's +Y push to the front stop.** It loads the tack along the jacket, where
  a loose tack may hold 0.1–0.4 N. f9b cuts the slot 0.05 mm over the box so the
  vertical entry seats it and nothing pushes along the wire.
- **K1's tab shear under the comb.** Worked through (final_w3 §2): the contact
  sees at most the tab's plastic moment, 3.6–6 N·mm, held by the comb at its
  stop with 2–8 N. The tack carries none of the shear.
- **C2 (channel ±0.01).** Agreed that ±0.05 is usable for a single die whose
  width is measured and whose height is set for it; a gang plate with one stop
  still needs its stations matched.

### Rejected or parked in wave 3

| Direction | Why set aside | What would revive it |
|---|---|---|
| **Two half-rows pushed into a housing in turn** (f5b, f2c, f4 as they were) | Every conductor has the same length from the web; the second push needs 6–9 mm of stored feed per conductor | Humps of 4.7–7.7 mm over 10–20 mm chords that fit the split, or planes cut to different lengths if a 6–9 mm bow in the loom is acceptable |
| **The neck blade as the depth stop** (f1, f3) | It sets the brush exactly and leaves the strip's ±0.2 mm on the window, and a screw pushing tips into it can fold strands back | Strip length held to ±0.05 mm (a stripper with a hard wire stop), when the two references agree |
| **Capture at the first ratchet tooth before threading** (f1) | Pinches the insulation bore: 0.03–0.17 mm interference for floors of 1.6–1.7 mm | A measured kit-contact floor of 1.9 mm or more |
| **A fixed rear fork in f9b's nest** instead of the servo neck blade | It must straddle the transition and lance and bear on the box below the floor; whether the transition is narrower than the box floor is unknown | One side-on and one top-down photograph of a kit contact showing a narrow transition strap |
| **Both half-rows in one shoe at 2.5 mm** (f5b's branch) with open plane-B wings beside crimped plane A | The insulation flare's plate edge falls to 0.10 mm at 2.7 mm wings and to nothing at 3.0; 3.0 mm wings touch a 2.05 mm crimp | JST-sized wings (~2.46 mm open) measured on the contacts in use, or plane B tacked first (c1c) |
| **A 3–5 mm throat jaw for the proof pull** | Too short a grip on silicone to carry 20 N into the copper at low squeeze | A jaw that squeezes 30 % over ≥5 mm without marking the jacket |

### Questions added for Derek

1. **One kit contact, three photographs under the ELP camera**: side-on (the
   transition *t*, the lance root and tip), end-on (the insulation barrel
   floor's inner width), and top-down (the transition strap's width against the
   box floor). They decide f8, f9b's nest and neck blade, f10's fin, f1's hold
   and f3's capture height.
2. **The tack by hand** (c1b, f9, f9b): lay three contacts of a strip segment
   under three split, stripped conductors; close each insulation barrel loosely
   with smooth pliers; cut the tabs; pull and twist each contact on its
   conductor with the bench scale.
3. **Five SN-2549 crimps bent down**: bend each 90° over a 2 mm pin just behind
   the insulation barrel with the wire's tail going away from the wing tips, and
   look from above.
4. **Is a 21–30 mm split behind the housing acceptable** (f9b, ribbon-as-pallet
   a2), or 12–20 mm (f5b, f4, f9), or none (f10)?
5. **A crimped conductor in a TPU clamp pulled at 20 N**: does the copper creep
   back inside the jacket?
