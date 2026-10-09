# Cart station: build the station on the welding cart, around the cable system

## Picture it (as it now stands)

- **The frame:** the Weldpro welding cart.
- **Upper tray:** a module plate on three hard feet, carrying the rotator
  (bolted through its four Ø10 holes), the gun support (paddle, sled or fixed
  bridge) and the wire feeder under the gun's tail.
- **Bottom tray:** the X1 Pro unit, with the middle tray removed.
- **Rear rack:** the argon cylinder, with a tee to gun gas and a purge line
  that rises through a tray hole into the rotator's Ø90 passage.
- **Rear mast:** a printed saddle gives the umbilical one fixed R 375 bend,
  from the grip butt to a vertical drop. The spare fiber lies as an S of two
  opposite turns on the side panel.
- **Where the loop lives:** entirely on the module plate. The cart's trays and
  casters carry but never locate.
- **The joint:** ~985 mm above the floor.
- **"Fixed" is fixed to:** the module plate.
- **Branch M (machine-that-learns):** a ball-screw X stage under the rotator
  moves the work, and the gun and cables stay still. The joint rises to
  ~1060 mm.
- **Branch H1 (theirs):** common-mode thermal layout plus thermistors and a
  drift model fitted by the camera.

**Sketch:** `../sketches/cart-station.svg`.

**Major unresolved problems:**

- Tray heights and the X1 unit's air path and idle draw.
- Sideways tipping under a lean (~180 N·m restoring).
- Where the umbilical leaves the unit, and storing ~3 m of spare fiber without
  twist.
- Module space: 531 × 330 mm.
- In M, the retract needs the nozzle raised first.


Sketch: `../sketches/cart-station.svg` (made by `../sketches/make_wave2_sketches.py`).
Cable numbers: `../cable_path.py`. Wave 3; new direction.

## The physical idea

The biggest, least negotiable structure in this problem isn't a table. It's
the cable system:

- a 5 m fiber umbilical that must bend no tighter than 350 mm radius while
  emitting and must never twist [Manual];
- the gas hose and signal cable inside it;
- a separate wire conduit from a separate feeder box;
- the argon cylinder that feeds both the gun and the purge.

All of it starts at one place, the Weldpro cart. Today the gun works on a bench
and the umbilical spans whatever gap there is between cart and bench, in a
shape that changes whenever either is moved. A changing cable shape is a
changing force on the gun, and the gun's support has to absorb it.

So build the weld station **on the cart**:

- **Weld module on the upper tray:** a module plate carrying the rotator and
  whichever gun support is chosen (paddle, sled, collar centre).
- **Machine on the bottom tray.**
- **Feeder on the module, under the gun's tail.**
- **One mast at the cart's rear** carrying a saddle that gives the umbilical a
  single fixed shape from the machine to the gun.

The cable then has the same shape for every tube, every session and every
person, so its force on the gun is a constant. It can be measured once, and
the support sees the same load each time. The cart stops being a separate
object the station has to reach across to; it is the station's frame.

## What's on the cart (facts, then assumptions)

**Observed [listing, 2026-09-28]:** Weldpro 3-tier cart:

- overall 40.5 × 18.2 × 30.7 in (1029 × 462 × 780 mm);
- upper and middle trays 20.9 × 13 in (531 × 330 mm);
- bottom tray 33.1 × 13.8 in;
- 400 lb total static load;
- cylinder rack with two chains, for cylinders up to 125 CF;
- two fixed rear wheels and two swivel front wheels;
- assembled with basic tools in 15–20 min, so the trays are bolted.

**X1 Pro unit [xlaserlab.com]:** 470 × 205 × 335 mm, 21 kg.
**Manual:** power dissipation up to 2500 W, air-cooled.

**Assumed (Derek to confirm):**

- tray heights: upper ~740 mm, bottom ~130 mm;
- the unit currently sits on the upper tray;
- the feeder's size and conduit length;
- the cylinder size;
- where the umbilical and the unit's cooling air leave the unit.

Layout (sketch):

| Place | What | Why |
|---|---|---|
| Upper tray | **Weld module**: a laser-cut plate (MIC-6 or steel, ~520 × 300) on three hard feet, with the rotator bolted through its four Ø10 holes and the gun support on the same plate | The whole positioning loop lives on this plate; the tray only carries it |
| Middle tray | Removed (bolted) | The 335 mm-tall unit fits between bottom and upper trays |
| Bottom tray | X1 Pro unit, exhaust aimed sideways or to the rear | Heat and fans below, at ~270 mm below the module |
| Rear rack | Argon cylinder, regulator with a tee: gun gas + purge line | Short fixed hoses |
| Rear mast | 1–1.5 in steel square tube clamped or welded to the cart frame (Derek's X1 Pro welds steel), with a printed saddle | Fixes the umbilical's one bend |
| Cart side panel | The excess umbilical (~3 m) laid as an S of two opposite R ≥ 350 turns in printed half-round saddles | Stores the length with no net twist |

## Geometry

At the true opening pose (grip 45°, hole dial 30°, vertical −15°), with the
rotator on the module on the upper tray (`cable_path.py`):

- **Heights:** dot ~985 mm above the floor, rim ~990. The mouth is at a
  kitchen-counter height, like the table opening, without cutting a bench.
- **Where the cable goes:** it leaves the grip butt 30° up, heading −105° in
  plan (15° off the tangent toward the operator's side). Plan:
  - an 80 mm straight lead to a clamp on the module;
  - one bend at R 375 over a printed saddle on the mast;
  - down.
- **Size of the loop:** the apex is ~230 mm above the dot (~1.21 m above the
  floor), and the vertical drop is 840–910 mm from the dot in plan (R 350–400).
  At hole dial 10° the apex is only ~70 mm above the dot; at 50° it is
  ~400–420 mm. The saddle's height is a per-pose-family setting on the mast.
- **Fit on the cart:** tube axis ~150 mm from the front end on the cart's
  centreline; dot across the width, away from the operator (+X); gun tail
  toward the rear. The drop lands at the rear end (~960–1030 mm from the
  front), ~160 mm toward the operator side. Just on the cart.
- **Umbilical budget:** grip to unit uses ~1.9 m; ~3.1 m is stored. One 180°
  turn at R 350 uses 1.1 m and spans 700 mm, so two opposite turns on the side
  panel store it.

## Structural loop and what "fixed" is fixed to

- **Position:** gun → shell → gun support → module plate → rotator base → race
  → nest → tube. Everything is on the module plate, which stands on three hard
  feet on the upper tray.
  - The cart's sheet-steel trays, bolted frame and casters are outside the
    loop.
  - Leaning on the cart or rolling it moves the module as one body.
  - "Fixed" means fixed to the module plate.
- **Cable shape:** fixed by two bodies, the mast saddle (on the cart) and the
  clamp on the module 80 mm behind the grip.
  - If the cart frame flexes a millimetre relative to the module, the free
    span between saddle and clamp takes it.
  - The gun sees only the short fixed lead from clamp to grip.
- **Gas and wire:**
  - Gun gas and purge come from the cart's own cylinder through fixed hoses.
  - The wire conduit runs from a feeder on the module along the saddle to the
    gun's bracket: short, in a fixed curve.
  - A shorter, fixed conduit means consistent drag and wire cast, and so a
    more repeatable wire tip — the other half of Derek's "the wire feed must be
    as straight as possible".

## How it is used

- **Loading (top, as today).** The gun parks and the tube lifts out of the
  nest. The park motion is chosen for the cable (next section). Indicate or
  seat as the gun support requires, for example work-as-datum's collar centre
  hung from a small +Y bridge on the module.
- **Purge, both closures.** The module plate and upper tray have a hole under
  the rotator's Ø90 passage; the purge line comes straight up from under the
  tray. For the second closure, reach under the tray to push the fitting into
  the lower port after the vessel is seated.
- **Weld.** The pedal and trigger are unchanged. The rotator's controller and
  adapters ride on the cart.
- **Stuck wire.** The head stays put (it's on the module), and the snip goes
  in from above.
- **After the session.** Roll the cart to the window fan or into a laser-safe
  corner or booth. The station moves as one piece and needs no re-setup,
  because nothing inside the loop depends on the floor or a bench.
- **Second person / another place.** The whole station is transferable, cable
  shape included. The only tether is power: the manual wants the unit on its
  own 20 A-class outlet, not a power strip.

## Parking the gun without disturbing the cable

The umbilical tolerates bending in its own plane at R ≥ 350. It must never
twist. So the gun's parking motion should be a rotation about an axis that:

- passes through the cable exit at the grip butt;
- is perpendicular to the cable's bending plane: horizontal, and perpendicular
  to the grip axis in plan.

The cable exit then doesn't move, and the cable only bends a little more in
its own plane, which the free span to the saddle (≥ 400 mm) absorbs.

- **How far to rotate.** The nozzle is ~260 mm from that axis. Rotating nose-up
  by 60° lifts the nozzle to ~270 mm above the dot and back over the lip, so a
  tube can be lifted ~150 mm out of the nest and slid out sideways. At 90° the
  nozzle leaves the tube's footprint entirely.
- **The hinge in the working pose.** Pins sit in open slots, so the gun
  support's own locating contacts (paddle rollers, sled feet) are what locate
  in the working pose. The same pattern as sequence-of-use's lid carrier,
  here with the hinge line put through the cable exit.
- **Rolling about the grip axis** (the scene's roll) is the one motion that
  twists the cable at the exit. On the cart it's set once per pose family and
  never used for loading.

## Breaking it

1. **Heat from below.** The unit can dissipate up to 2.5 kW
   [Manual, power dissipation], air-cooled. On the bottom tray it is ~270 mm
   under the module. Warm air rising onto a PET-GF rotator and an aluminium
   module plate during a session means slow thermal drift.
   *Repair:* aim its exhaust sideways or out of the cart's rear. Put a sheet
   baffle under the upper tray. Or leave the unit off the cart on the floor
   beside it; the cable shape then starts at the saddle and is still fixed.
   Its air path and the heat when welding at 60% are **unknown**.
2. **Tipping.** Total ~80 kg (unit 21, cylinder ~30 [assumed], module ~25,
   feeder ~5). The cart is 462 mm wide, so the restoring moment is ~180 N·m. A
   200 N sideways lean on the module ~1 m up is enough to tip it.
   *Repair:* two fold-down outrigger feet on the operator's side, or dock the
   cart against the bench (branch below). The cylinder low at the rear helps
   fore-aft, not sideways.
3. **Space.** The upper tray is 531 × 330 mm.
   - The rotator base (300 × 250), the gun's tail (to ~390 mm from the front),
     the paddle's P3 foot (~400 mm) and the feeder all fit on a ~520 × 300
     module.
   - A gantry doesn't fit.
   - This is a paddle, sled, or fixed-bridge station.
4. **Height is fixed by the tray** (~1 m dot). That suits standing work. For
   seated work the module would go on the bottom tray with the unit elsewhere.
5. **Storing the excess umbilical.** Coiling in loops twists a cable whose ends
   are held, and the manual forbids twisting. Two opposite 180° turns (an S)
   cancel. Whether the stored length also has to respect 350 mm while emitting:
   yes, the whole fiber carries the beam. The side panel is ~1 m × 0.65 m;
   an S of two R 350 turns needs ~0.7 m of height per turn, so it is tight. The
   drop behind the mast gives the extra height. Worth checking against the real
   exit position on the unit.
6. **Cable force is constant, not zero.** The gun support must still carry it.
   But a constant force can be measured once (luggage scale at the clamp) and
   built into the support's preload. For the paddle compass, that means P3 and
   the hub spring are sized for it.
7. **Cart casters.** The Weldpro's wheels have no listed brakes. A bump rolls
   the whole cart. That's harmless to the pose (the loop is on the module), but
   the power and extraction lines must tolerate it.
8. **Cylinder height.** A tall cylinder in the rear rack stands where the cable
   drops. The mast and saddle sit beside it, and the drop passes on the
   operator's side of the cylinder (the drop is ~160 mm toward that side
   anyway).

## Branch: the cart docks to a bench station

Keep a bench arrangement (table opening, collar, sled) and give the cart one
parking place at the bench's −Y end: a V-bracket on a bench leg that the cart's
frame is pushed into and strapped to.

- The mast saddle on the cart delivers the umbilical to the bench gun in the
  same shape every session, because the dock repeats the cart's position to a
  millimetre or two, which is plenty for a cable.
- The bench keeps the positioning; the cart keeps the cable system.
- This is the minimal change to the table-opening station: its "≥ 350 mm bend
  off the bench end to the cart" becomes a fixed structure instead of a hanging
  loop.

## Branch: the cart mast as a travelling overhead anchor

Several explorers hang the gun's weight from overhead (balancers,
float-and-dock, suspension rings). A balancer hung from the cart's mast at the
right height gives that overhead anchor wherever the cart goes. It moves with
the station, so the float geometry is the same everywhere. It carries only;
position still comes from the module.

## Other shop structure considered

- **WEN 4208T drill press** [4208T manual]: 8 in swing (101.6 mm from spindle
  axis to column face), 2 in spindle stroke, depth stop, JT33 taper,
  1.75 in column, 6.5 × 6.5 in table, 11 × 7 in base, 23.1 in tall, 34.2 lb.
  - *As a whole machine:* the column (Ø44) would stand ~124 mm from the tube
    axis, spanning 102–146 mm. That is inside the rotator's 300 × 250 base
    footprint (120–180 mm from the axis in every direction), so it can't
    straddle the existing rotator.
  - *Transplanted:* its head on a column stub from a collar or module, quill
    down the tube axis, is a ready-made spring-return quill with a depth stop
    and scale. That is exactly work-as-datum's collar centre (W1) or its rigid
    variant (W1b). But the head would have to sit ≥ 210 mm above the dot to
    clear the gun, so the centre needs a ~200 mm extension (Ø20 or stiffer to
    keep tip deflection under ~0.03 mm at 20 N).
  - It is also a production tool for plate tapping. A dedicated LM12 plunger
    (work-as-datum W1) does the job without borrowing it.
- **Bench pegboard:** 1/4 in hardboard on the 48 in benches. Good for storing
  pose blocks, pucks and saddles, and for cable hooks during setup. Not a
  locating structure.
- **Ceiling and overhead rails:** developed by carry-and-locate and
  sequence-of-use (balancer trolleys on a rail). The cart mast is the portable
  version of that anchor.

## Contribution

- The cable system becomes a fixed structure. Its force on the gun is a
  constant that can be measured, rather than a disturbance that varies with
  where the cart was parked.
- A short, fixed wire conduit.
- Gas and purge from a cylinder a hand's reach away.
- A self-contained, mobile, transferable station at counter height, with no
  bench cut.
- Two principles that apply everywhere:
  - organise motion around the cable exit (park about an axis through the
    exit, perpendicular to the cable's plane; never roll about the grip axis
    to load);
  - dock the cart if the station stays on a bench.

## Unresolved / rests on

- Tray heights and whether the middle tray comes out.
- The unit's cooling-air path and how much of its 2.5 kW rises into the module.
- The umbilical's exit position on the unit.
- The feeder's size and conduit length.
- The cylinder size.
- The umbilical's stiffness and weight, which set the constant cable force.
- Tipping margin with the real masses; whether outriggers or a dock are
  needed.

---

## Wave 5: machine-that-learns' critique, and branches H1 and M

Source: `../../../exchange/machine-that-learns--on--workspace-as-structure-w4.md`.
The station above is left as written. This section records what changes.

### The 2500 W (accepted, with the reading labelled)

The manual lists "Power Dissipation 2500 W" under **electrical** parameters,
beside "Conversion Efficiency 35 %" [Manual p.12]. machine-that-learns reads
it as the unit's maximum electrical draw, not the heat released next to the
module. I agree; it is an inference, not stated.

- At 700 W peak optical and 35 % efficiency, full power draws ~2.0 kW, of
  which ~1.3 kW is heat in the unit. At the recorded 60 %, that is ~0.8 kW
  while firing.
- A closure fires for about a minute (48.6 s per revolution plus overlap).
- A session's average heat is therefore set mostly by the unit's idle draw
  (fans and electronics, **unknown**, plausibly 100–300 W), with short peaks
  during welds.

Break 1 above ("up to 2.5 kW … rising onto the rotator") overstated the
steady load. The direction of the concern stands, at a smaller size.

### Branch H1 (theirs, adopted): common-mode layout, then measure the rest

**Common-mode layout.** Build the gun support's height from the same material
as the rotator's height, and keep the rotator axis and the gun support on one
plate a short distance apart.

- A 214 mm PET-GF rotator beside a 214 mm aluminium post differs by ~2.6 µm/K
  (PET-GF expansion assumed ~35 µm/m·K).
- Aluminium over ~200 mm is ~4.6 µm/K.
- At 5 K of module warming the residual is tens of microns (their estimate).

**Measure the rest.** Four printer-standard 100 k NTC thermistors, on:

- the module plate by the rotator;
- the plate by the gun support;
- the rotator base;
- the gap above the unit.

They read on the controller's thermistor inputs. The joint camera measures
dot vs corner at the start of each tube and on idle laps, and over a few
sessions the station fits the offset against those temperatures. It then
either compensates or says "re-trim".

**Keep the physical repairs:** a steel baffle with an air gap under the upper
tray, and the exhaust aimed out of the side or rear.

**What stays uncertain:** the unit's real air path and idle draw (Derek can
feel and read both); PET-GF's actual expansion; whether warm air matters to the
stored fiber on the side panel.

### Branch M (theirs): the work moves on the cart, and gun, cables and conduit stay still

**What it is.** A double-rail SFU1605 X stage (ZBX150 class) sits on the
module under the rotator, radial to the dot.

- ±0.13 mm runout follow, corner scans, and a ~50–60 mm radial retract for
  loading.
- The dot rises from ~985 to ~1060 mm.
- Cameras, tags and an IMU bump log ride the module, so the measuring frame
  travels with the cart.
- The controller box goes on the side panel opposite the fiber S.

**What it keeps:** the station's reason to exist. Everything the software
changes moves a 6–7 kg stack a few millimetres; the gun and its cables don't
move. Agreed.

**Three notes from this side:**

1. **The retract needs the nozzle above the rim first.** At the proxy pose the
   nozzle tip is ~5 mm above the rim, and the digest notes that at 5 mm
   standoff it would be below. A radial retract then drags the lip under or
   into the nozzle. M's Z is a manual trim on the gun support, and lifting the
   gun moves its cables.
   *Repair:* use this station's cable-exit park before the retract. A ~5°
   nose-up rotation about the hinge through the cable exit lifts the nozzle
   ~22 mm (≈ 260 mm × sin 5°) and leaves the exit point where it was. Then X
   retracts. Order: park 5°, retract X, lift the tube out.
2. **M and a work-riding gun support are alternatives on the cart.** The
   paddle and split mount ride the plate. On M's X stage they would be dragged
   by the 50 mm retract, and their room foot (P3) would need a plane that moves
   with the stage.
   - **M** pairs with a fixed bridge or a sled: gun room-referenced, runout by
     X-follow, height per tube by the camera.
   - **The split mount** pairs with a fixed rotator: gun work-referenced,
     motors only for experiments.
   - Both fit a 520 × 300 module; not both at once.
3. **Partial disagreement: gun-side motion needn't spend the constant cable
   shape.** Their difficulty says the cart's best property "would be spent by
   the first motor" on the gun side.
   - **What the cart removes:** a cable force that depends on uncontrolled
     things — where the cart was parked, how the cable lay, who moved it.
   - **What a gun-side motion leaves:** a cable force that is a repeatable
     function of the commanded pose, which a learning station can map like any
     other stage error.
   - **So it survives small gun-side motions** (the split mount's tilt of a few
     degrees, micro-slides of a few mm) with a fixed saddle and a loose ring at
     the butt.
   - **What would spend it:** hysteresis, meaning the cable sticking on its
     saddle and settling differently depending on the direction of approach.
   - **The test:** approach one pose from both sides and compare the dot on the
     camera.
   - **Where they are right:** for large gun-side motion (a gantry), the cable
     force varies with the free span as well. M avoids that entirely.

**What stays uncertain in M:**

- the module layout with the rotator's motor and ground towers;
- where the work lead and purge hose hang (from the mast);
- the X stage's backlash under the one-sided load of the cables on the rotator.
