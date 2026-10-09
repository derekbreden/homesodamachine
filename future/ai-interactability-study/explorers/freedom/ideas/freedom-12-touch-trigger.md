# freedom-12: touch trigger (a stylus on three contacts that says which way it was pushed, and what it is standing on)

Scene: `scenes/freedom-12-touch-trigger`. Origin: branch of `eyes-05-touch-off-interlock` (sketch, no scene), combined with `freedom-07-floating-on-work` (mine) and `datum-07-touch-off`; drawn in wave 2 from the exchange `exchange/freedom--on--eyes-w2.md` (section 2). Depth: developed (statics in the scene; five break-and-repair entries). Numbers **illustrative** except the trigger criterion, which is statics.

## Picture it

A thin stylus with a 1 mm ball tip stands on the shell beside the nozzle. Its upper end rests on three small contacts, three balls on three seats, held down by a light spring; each contact is a switch. A stage drives the stylus at the tube, fast to find it, back off, slow to read. On contact the tip is pushed and one contact opens (or two, or all three), and software has three bits and the stage position. The top view of the seat shows which contacts opened for a wall push (sideways), a plate or rim push (along the axis) or a push in the corner.

## The proposal

Make the touch probe of eyes-05 a **kinematic trigger**: three contacts under a spring, each a separate switch. Push the tip sideways and the contact nearest the push unloads first; push along the axis and all three unload together. So the contact pattern is the direction, to 60° (six patterns plus axial), and one signal tells wall from plate from rim without the tube's conductivity or the laser's interlock. From statics with three contacts on a circle of radius a, a stylus of length L and a preload P: contact *i* opens when F<sub>lat</sub> cos(θ − α<sub>i</sub>) ≥ a (P − F<sub>axial</sub>) / 2L. Sideways trigger P·a/2L to P·a/L (lobes, factor two), axial trigger P: 0.18 to 0.36 N sideways and 1.5 N axial for a = 6 mm, L = 25 mm, P = 1.5 N.

The same stylus **leans**: at the trigger force the tip stays in contact while the tube turns. A sliding ball at μ 0.3 drags 0.054 N; a gun on the 350 mm pendulum of freedom-07 drifts 1.6 mm along the tangent and the seam is 0.02 mm nearer, against 18 mm for freedom-07's 2 N skid. The three switches are then the watchdog for the unilateral contact: the "is it still there" bit that freedom-07 lacked. datum-04's ball feeler rides the same contact in the corner.

## What carries loads, what establishes position, what is free or restrained

- **Load:** the spring presses the stylus body on the contacts; the tube pushes the tip; the contacts carry the difference. The touch force is a fraction of a newton; the stage and whatever holds the gun carry the reaction.
- **Position:** the tube's wall, plate and rim at the moment a contact opens. The stage's own position at that instant is the reading.
- **Free:** the tangent (when leaning, by rolling or sliding at trigger force); the stylus's tilt after the trigger (overtravel).
- **Restrained:** the stylus on its contacts until pushed past the trigger force.
- **Driven:** the approach stage; back-off; the order of touches.

## What software could command, observe, and what stays manual

- **Command:** approach speed (fast, then slow), back-off, the order of touches.
- **Observe:** three contact bits (a resistor ladder can put them on one wire), the stage position at the first change.
- **Manual:** fitting and cleaning the stylus and seat; coarse aim to within the search distance.

## What was tried to break it

**Entry 1. One bit cannot say wall from plate (eyes-05's own).**
- Conflict: wall and plate are one conductor.
- Change: the contact pattern is direction. With the stylus vertical a wall touch is sideways (one contact), a plate or rim touch is axial (all three). A stylus tilted 32° (in place of the nozzle, as datum-07) mixes them: the pattern changes and the trigger force does not fall to the lateral value; the scene's tilt slider shows it.
- Leaves uncertain: whether the stylus fits beside the nozzle in a canyon 8 mm wide; rim and plate both read "axial": the stage height separates them.

**Entry 2. The touch measures the support, not the tube, on a soft axis.**
- Conflict: the reading is the stage position when the contact opens; everything between the stage's encoder and the tip gives way by trigger force over stiffness. A 0.2 N wall touch reads 1.3 mm short on a 0.15 N/mm bungee axis, 1.0 mm on a friction arm (0.2 N/mm), 0.1 mm on a rigid-grip arm, 15 µm on six taut lines, 3 µm on the nose stage of the seat, 1 µm on a lead-screw vernier. A plate touch at 1.5 N is eight times worse (75 mm on a constant-force balancer, 7.5 mm on the friction arm, 0.2 mm on a 200 N/mm wire or stage).
- Assumption: the approach axis is a stage and the stylus is rigid.
- Change: the driven axis is the stiffest element on the touched axis (freedom-01c); a soft element belongs to weight. Lower P for a lighter plate touch.
- Leaves uncertain: the real stiffnesses are the scenes' illustrative ones.

**Entry 3. Latency and overrun.**
- Conflict: datum-07's numbers: 0.1 mm/s × 10 ms = 1 µm; 1 mm/s × 100 ms = 0.1 mm.
- Change: fast-then-slow, and overtravel: after the trigger the tip tilts away against the spring alone (about 0.5 N/mm assumed), so an overrun costs the spring's stiffness, not the stage's: 1 µm of overrun adds 0.5 mN.
- Leaves uncertain: the stylus's real overtravel range and stop.

**Entry 4. Trigger force is a design trade.**
- Conflict: low P is sensitive and false-triggers on the head's vibration (a 5 g stylus at 1 g is 0.05 N); high P bends the wall and pushes the gun on a soft axis.
- Change: P is one slider; 0.5 N gives 0.06 to 0.12 N sideways and 0.5 N axial.
- Leaves uncertain: the vibration level at the shell.

**Entry 5. The stylus registers its tip.**
- Conflict: the dot is 16 mm along the beam from the nozzle; the tip is wherever it is mounted.
- Change: none here; tip-to-dot is the calibration every other idea needs (eyes-07's phantom answers it).

## Branches and combinations

- **freedom-07:** the leaning shoe and the probe are one mechanism at two preloads; continuity watches the unilateral contact.
- **datum-07** (touch-off) and **trials-14** (contact sense): datum-07's speeds and latency and the CR Touch sourcing; this idea adds the direction and the path-stiffness term, and works without the laser's circuit.
- **eyes-04 (pads):** a contact at a known geometry zeroes a pad's offset (exchange section 5).

## Unresolved problems, and questions that need Derek's observation

- Does a steel ball at a fraction of a newton mark the bore of a 316L tube?
- Can the copper nozzle's neighbour space (between the nozzle, the wire guide and the wall) take a 3 mm seat?
- (eyes-05's) does the laser's ready lamp change when the nozzle touches with the laser off? (Independent of this idea: the stylus does not need it.)

## Assumptions

- a 6 mm, L 25 mm, P 1.5 N, tip radius 1 mm, seat repeatability 0.005 mm (steel) or 0.03 mm (printed), overtravel spring 0.5 N/mm, μ 0.3, path stiffnesses 0.15 / 0.02 / 0.2 / 2.1 / 15 / 67 / 200 N/mm: **illustrative**. Friction ignored in the trigger statics; seat rigid.

## Sourcing pointers

`sourcing/freedom.md` wave 2: 3 mm chrome steel balls (Prime, several listings from $3.99), the EISCO Newton force meter ($9.99, Prime). The CR Touch in `sourcing/datum.md` is the ready-made single-axis touch probe.

## Scene

`freedom-12-touch-trigger`.

**Wave 3 note (from borrowed's exchange).** The stylus, the shoe (freedom-07) and borrowed's tonearm are one contact at different preloads. A phono cartridge tracks at about 10 to 20 mN (general knowledge, unchecked): ten to twenty times lighter than the 0.18 to 0.36 N trigger here, which says what a light enough follower can be; not verified for a steel corner. See freedom-07 entry 5.
