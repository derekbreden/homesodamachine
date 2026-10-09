# F — The wire path as the spine; the wire and the interlock as instruments

## Picture it

**The wire path, fixed.**
- The feeder stands fixed behind the gun's tail, on a cart module or frame.
- Its conduit lies in a printed trough with one bend of ~50–90°, through a
  roller straightener, into the gun's own wire bracket, which is unchanged.
- A servo finger (or a SwitchBot) presses the feeder's own Feed and Retract
  buttons.
- A 5.5 mm endoscope camera on the shell watches the stick-out.

**Touch sensing, all optical.** The stages of A, E or the cart station move the
work slowly until the wire touches the cap or the wall. The contact is detected
optically, for touch-off and corner finding. Nothing connects to the welder's
circuits.

**Where it fits.** It works best with a still gun. "Fixed" is whatever frame
holds the feeder, the trough and the gun support.

Sketch: [`../sketches/f-wire-path-side.svg`](../sketches/f-wire-path-side.svg).

**Major unresolved:**
- Whether the unit shows gun-to-work conduction with the trigger released
  (check with the key off first).
- Where the interlock contact is actually made during a wire-fed weld.
- The feeder's size, pull force and shortest jog.
- The conduit's minimum bend.
- The real bracket geometry.
- Whether the wire camera survives beside the bracket.

---

Sketch: [`../sketches/f-wire-path-side.svg`](../sketches/f-wire-path-side.svg)
(made by `../calc/sketch_f_wire.py`). Numbers: [`../calc/wire_path.py`](../calc/wire_path.py).

Every other arrangement in this study organises around the gun, the tube, the
structure or the umbilical, and treats the filler wire as a passenger. Here the
wire's path from spool to puddle is the thing the station is built around, and
the wire itself — its tip, its bend, its contact with the work — becomes a
measuring instrument for the learning machine. It is a subsystem with context:
it drops into the cart station (workspace-as-structure), into A (still gun) and
D (seat), and it constrains B and E.

## What is known, what is inferred, and what is not to be touched

**Known [Manual, rendered pages in `/private/tmp/x1-pro-weld-pages/`]:**

- **Interlock (p.19).** "Before turning on the laser, the safety interlock
  must be connected to the laser unit's grounding interface. Prior to laser
  emission, clamp the other end of the interlock (with alligator clip) onto the
  workpiece. Only when a complete circuit is formed between the clip and the
  welding gun can the laser be emitted."
- **Unconducted alarm (p.32).** The unit alarms when conduction between torch
  and workpiece is lacking. The manual's causes are an unclamped clip, poor
  torch-workpiece contact, or an insulated surface. The laser "suddenly stops"
  if contact is lost mid-weld.
- **Key switch (p.31).** A key switch is part of the interlock ("turn the key
  to ON position to eliminate the alarm").
- **Feeder.** It is a separate unit on a 6-pin aviation connector carrying
  power and signal (p.19); the pin table on p.16 is partly legible in the OCR.
  The feeder has two buttons, "Wire Feed: press to advance, release to stop"
  and "Wire Retract: press to reverse" (p.18).
- **Wire settings (p.23).** Wire-feed speed, "pullback length: the length of
  the wire back after releasing the trigger during welding", patch length, and
  delays. The spec test used 5 mm/s wire feed and 10 Hz × 2 mm swing (p.13).
- **Ports (p.16).** RS232 goes to PC supervisory software; DB25 is "used for
  PLC integration by customers". No protocol is given in these pages.
- **[Repo]** The rotator's copper shoe exists for the welder's conductance
  interlock. A stuck wire is snipped, never lasered off, with the head held
  still.

**Inferred (not verified):**

- **What makes the interlock contact during a wire-fed weld.** The nozzle
  stands off (proxy: ~5 mm above the rim), so the contact is probably the
  filler wire: gun → metal wire bracket → wire → work. The vendor page's
  "fires only when the gun touches metal" fits this. If so, the wire tip is an
  electrical contact the welder already monitors.
- **Pullback and a stuck wire.** After the trigger is released, the unit pulls
  the wire back by the pullback length. If the wire is frozen in the bead, that
  pull acts between feeder and bead. The conduit housing is then compressed
  like a Bowden cable, and pushes the gun's wire bracket toward the bead along
  the wire. That is a new load case: up to the feeder's pull force (unknown),
  applied at the bracket, directed toward the joint, at the moment of release.

**Not to be touched — nothing here connects to or alters the welder:**

- the interlock clip, its lead, and the unit's ground terminal;
- any conductor in the gun-to-work path, including the wire's own electrical
  path (no injected voltage, no insulating the wire from the gun, no
  dry-run-only insulated tip that changes the guide);
- the feeder's 6-pin connector and cable;
- the contacts behind the feeder's buttons;
- the RS232 and DB25 ports (undocumented protocol; a command could change
  settings or enable output);
- the key switch.

A low-voltage touch circuit through the wire, as robotic MIG cells use for
"wire touch sensing", is therefore **not proposed**. The wire is part of the
welder's interlock circuit, and a signal injected there is an alteration of the
welder whose consequences nobody here can check. Every instrument below is
optical, mechanical, or a camera reading the welder's own indicators.

## The arrangement

Shown with a still gun, as on workspace-as-structure's cart module or in my A,
where it fits best. Why is at the end.

- **Feeder fixed on the station frame**, its outlet roughly on the extension of
  the wire's final approach. At the opening pose (scene proxy) the wire leaves
  the dot rising 38° above the cap face and running within 20° of the wall's
  plane, 13° from the beam, heading −115° in plan (`wire_path.py` §1). The
  feeder therefore sits behind the gun's tail on the −Y side, where the
  cart station already puts it ("under the gun's tail").
- **One-bend conduit held in a printed trough along its whole length.** A
  fixed ~50–90° bend between the feeder's line and the final approach, instead
  of a hanging conduit.
  - **Why:** feed force through a curved liner grows as exp(μ·θ) with the total
    bend angle θ. At μ 0.15–0.25 that is ×1.2–1.5 for one fixed bend, against
    ×4–11 for a hanging 3 m conduit that accumulates ~1.5 turns
    (`wire_path.py` §2).
  - A short, fixed conduit means low, constant drag, so a constant wire push
    into the puddle, so a constant reaction on the gun. The shape and the
    cast's orientation stop changing between sessions.
- **Straightener.** A roller wire straightener between the feeder and the
  conduit (commodity 20-wheel units for 0.5–2 mm wire exist, search level).
  - **Why:** the cast left in the wire curves the stick-out. The tip offset is
    L²/2R: for a 12 mm stick-out, 0.24 mm at a 300 mm cast radius, 0.07 mm at
    1000 mm (§3). The cast's orientation also rotates as the wire twists, so
    the tip wanders.
  - Whether the straightener helps is itself an experiment for the wire camera
    below.
- **The gun's own wire bracket stays the final guide.** The shell supports the
  conduit up to the bracket and never replaces or insulates it. That keeps
  whatever electrical contact the interlock relies on exactly as XLaserlab
  built it.
- **Button finger on the feeder.** A small servo finger, or an off-the-shelf
  SwitchBot button pusher ($25.99 Prime, "700+ bought in past month"), presses
  the feeder's own Wire Feed and Wire Retract buttons. It presses them the way
  a thumb does: no wiring into the feeder.
- **Wire camera.** A 5.5 mm USB endoscope camera (Teslong 5 MP autofocus,
  $49.99 Prime; fixed-focus 1080p ones from ~$27) clips to the shell beside the
  bracket, 30–40 mm back and a little to the side, looking along the stick-out
  toward the tip.
  - It rides with the gun, so the tip's position in its image is stick-out and
    aim *in the gun's own frame*, independent of pose and stage motion.
  - It also sees the red dot and the corner from close range.
  - It sits behind a sacrificial window (a spare D18 protective lens) and a
    small shield. It is a dry-run instrument; for welds it is capped or
    accepted as consumable.
- **Joint camera and stages** are as in the observation layer: +Y side,
  inboard; X (and later Z) on the work side.

## The instruments

1. **Stick-out gauge.**
   - The wire camera measures the tip's distance from the bracket nozzle to a
     few hundredths of a millimetre (0.05 mm is my estimate).
   - After a snip — the stuck-wire procedure, and the reset the digest flagged
     — the finger jogs Feed or Retract until the camera reads the target.
   - Jog resolution is the feeder's speed times the shortest press (unknown);
     the camera, not the jog, is the reference.
   - Every weld then starts from a measured, logged stick-out.
2. **Aim and cast gauge.**
   - The tip's lateral offset from the bracket's axis, measured for each fresh
     length of wire, gives the distribution of tip aim.
   - Run with and without the straightener, and with the conduit fixed or
     hanging, this is the experiment that shows which part of "the wire feed
     must be as straight as possible" matters.
3. **Optical touch-off.**
   - Approach: with the stick-out set, the station closes the gap between
     wire tip and cap face with a stage — the tube's X/Z in A, or the gun
     carriage elsewhere — at 0.1–0.5 mm/s. The feeder is not used for this.
   - Detection: the wire camera sees the stick-out bend. At L = 12 mm the tip
     is a 5.5 N/mm spring (§4), so 1 px of bend at ~23 µm is about 0.13 N of
     contact. The wire yields at 2.5–4.3 N, 0.44–0.78 mm of tip travel.
   - Overtravel before a 30 fps camera with 60 ms latency reacts is 0.01–0.05 mm
     at stage speeds. At feeder speeds (5–12 mm/s) it would be 0.5–1.1 mm, which
     is why touch-off by jogging the feeder would bend the wire (§5).
   - Result: where the wire meets the cap, in the station's frame, from the same
     wire that will be welding.
4. **Corner finding by touch.**
   - Touch the cap face at two points and the wall at two points by stage
     moves. Fit the two planes; their intersection is the corner.
   - This is the optical, non-electrical cousin of robotic touch sensing. It
     cross-checks the red-beam corner fit from the joint camera: two
     instruments, one reference.
   - Any offset between them is the aim offset between wire and beam.
5. **The welder's own conduction state, read by camera.**
   - If the unit's monitoring screen or the gun's status LED shows gun-to-work
     conduction live while the trigger is released, the station camera can
     read it. That turns the welder's own interlock sensing into an electrical
     touch sensor without a single connection.
   - The clip goes on the work as normal (the copper shoe); the trigger is
     never pressed by software.
   - **Unknown:** whether the unit shows conduction without the trigger, and
     whether it still does with the key off. If it only shows while armed, this
     instrument is not used: a dry run with the laser armed is not worth the
     risk.
6. **Stuck-wire witness.**
   - During a weld the wire camera is washed out near the puddle but can still
     see the stick-out near the bracket with a short exposure and a shade
     filter.
   - Symptoms of a stuck wire: the stick-out bowing while the feeder pushes, or
     the wire failing to withdraw at pullback.
   - The log records the event and the gun's reaction (the joint camera sees
     the gun move).

## How it is used

- **Setup of a recipe:**
  - measure cast and aim over ~20 jog-and-snip cycles;
  - set the target stick-out;
  - touch off on the cap near the dot;
  - cross-check the corner by touch against the red-beam fit;
  - save.
- **Each tube:** after loading, touch off once (it doubles as the per-tube
  height check), reset stick-out, dry lap.
- **Weld:** pedal, Bowden trigger, release, release — as today.
- **Stuck wire:** snip while the head stays put (the procedure), then the
  stick-out reset by finger and camera. Before the next weld the camera confirms
  the tip is clean and at length.
- **Second closure:** identical; the wire path does not know the difference.
- **Second person:** the stick-out, touch-off and corner check are buttons; the
  screen shows the wire tip against its target.

## Loads the wire path puts on the gun (for carry-and-locate's inventory)

- **Wire push into the puddle.** It reacts at the bracket. With a fixed
  one-bend conduit, the feeder force needed is only ×1.2–1.5 the tip force, and
  the conduit's own spring-back on the gun is small and the same every session.
- **Pullback on a stuck wire (new).** At trigger release the feeder pulls the
  wire back. If the wire is frozen in the bead, the conduit housing pushes the
  bracket toward the bead, up to the feeder's pull force (unknown), along the
  wire. A soft carrier moves the nozzle toward the lip; a stiff support takes
  it.
  - Pullback length is a user setting on the unit (p.23). Whether to change it
    is Derek's call as the operator; this study proposes no change to the
    welder.
  - The wire camera and joint camera record the event whenever it happens.

## What it constrains in the other arrangements

- **The wire path is repeatable only if nothing on it moves.** A still gun
  with a fixed feeder (A, D, the cart station with motion under the tube)
  gives a conduit whose shape never changes.
- **With the gun on stages** (B, E's gantry, the hexapods), the conduit's free
  span flexes with every move: drag, cast orientation and the reaction at the
  bracket all change. The wire experiments above are then confounded by pose.
  - For E: keep the feeder on the X carriage? Too heavy (feeders with spools
    are several kg; size unknown). Better to give the conduit a long, gentle
    free loop from a fixed feeder, and to do wire calibration at the recipe's
    pose only.
- **For the learning machine,** this is an argument for putting motion on the
  work side whenever the wire is the thing being learned.

## Parts

See `../../../sourcing/machine-that-learns.md`, wave 4.

- Teslong 5 MP autofocus USB endoscope ($49.99 Prime), or a 1080p fixed-focus
  one (~$27, search level).
- SwitchBot button pusher ($25.99 Prime), or an MG90S servo finger on the
  ESP32.
- A 20-wheel wire straightener (search level, ~$56).
- Printed trough, conduit clamps, camera clip and shield on the shell.
- A spare D18 protective lens as the camera window.

## Contribution

- The first arrangement organised around the filler wire. It makes the wire's
  final approach constant (one fixed bend, a trough, a straightener) and
  measures it (a wire camera in the gun's frame).
- Three dry-run instruments from the wire itself:
  - stick-out;
  - aim and cast;
  - touch-off and corner finding at ~0.1 N, cross-checked against the red-beam
    fit.
- A clear safety boundary: everything is optical or mechanical, and the
  welder's circuits and settings are untouched.
- A new load case: pullback on a stuck wire pushes the gun toward the joint.

## Biggest open problem, and the rest

**Biggest:** whether the welder's own interlock contact, and its indication,
can serve as a touch sensor without arming the laser. If the unit shows
gun-to-work conduction with the trigger released, instrument 5 exists for free,
by camera. If not, touch sensing stays optical (instruments 3 and 4), which is
slower and needs a clear view of the tip. Only Derek's observation of the unit
settles it. With the clip on, the trigger never pressed and the wire touched to
the work, does anything change on the screen or the gun's LEDs?
- Check first with the key off.
- Only if nothing shows is it Derek's call whether the ordinary pre-weld state
  counts. That is key on, trigger released: the state hand welding already
  passes through every time the gun is positioned.

**Also open:**
- where the interlock contact is actually made during a wire-fed weld;
- the feeder's size, pull force and minimum jog;
- the conduit's minimum bend radius;
- the real bracket geometry (needs the scan);
- the cast of Derek's spool;
- whether a 5.5 mm camera survives beside the bracket in dry runs, with its
  light not confusing the red-dot measurement.
