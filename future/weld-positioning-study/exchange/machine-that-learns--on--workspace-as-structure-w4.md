# machine-that-learns on workspace-as-structure — wave 4

Their newest idea, still rough: `explorers/workspace-as-structure/ideas/cart-station.md`.

What it is:
- The weld station is built on the Weldpro cart, around the cable system.
- A module plate on the upper tray carries the rotator and a still gun support
  (paddle, sled or fixed bridge).
- The X1 unit sits on the bottom tray.
- A rear mast saddle gives the umbilical one fixed bend, and the spare fiber is
  stored in an S of two opposite turns.
- The joint is at ~985 mm, counter height.
- Their open problems are the cart's tipping limit and the unit's heat below the
  module.

My view: the station as something software moves and observes. Their view: the
room's structure is the first positioning stage. I worked on two difficulties:
- **the unit's heat under the module** (their break 1);
- **what the constant cable shape needs in order to stay constant once motors
  are added**.

For the second I sketch where motors, cameras and the controller go on the
cart. The wire path on their cart is taken further in my new idea
(`explorers/machine-that-learns/ideas/f-wire-and-interlock-instruments.md`).

---

## 1. The unit's heat under the module

**Variant:**
- The X1 unit (470 × 205 × 335 mm, 21 kg) sits on the bottom tray, ~270 mm
  under a module plate carrying a PET-GF rotator.
- The manual lists "power dissipation 2500 W", air-cooled.
- The exhaust direction is unknown.

**Assumption behind their repairs:** thermal drift has to be *prevented by
layout*. Their options are to aim the exhaust sideways, add a baffle, or take
the unit off the cart.

**First, a reading of the 2500 W.** The manual lists it under *electrical*
parameters, next to "conversion efficiency 35 %". I read it as the maximum
electrical draw, not heat released beside the module. This is an inference,
not stated.
- At 700 W peak optical and 35 % efficiency, full power draws ~2.0 kW, of
  which ~1.3 kW becomes heat in the unit. The rest leaves as light, into the
  tube.
- At the rig's recorded 60 % power, roughly 0.8 kW of heat while firing.
- One closure fires for about a minute (48.6 s per revolution plus ~20°
  overlap).
- So a session's average heat is set mostly by the unit's idle draw (fans and
  electronics, **unknown**, plausibly 100–300 W), with short peaks during welds.

That is not negligible, but it is slow and periodic. So:

**Repair H1 — make the loop's growth common-mode, then measure the rest.**

- **Common-mode layout.** Their loop is gun support → module plate → rotator →
  tube. Growth that moves the gun support and the tube together does nothing to
  the dot. Two cheap rules follow.
  - Build the gun support's height from the same material as the rotator's
    height (both PET-GF, or both on aluminium spacers). A 214 mm PET-GF rotator
    beside a 214 mm aluminium post differs by ~(35 − 23) µm/m·K × 214 mm ≈
    2.6 µm/K in height (PET-GF expansion assumed ~35 µm/m·K).
  - Keep the horizontal distance from the rotator axis to the gun support
    short, on one plate. Aluminium over ~200 mm is ~4.6 µm/K.
  - At 5 K of module warming the residual is tens of microns, not tenths of a
    millimetre (estimate).
- **Measure the rest.** The Klipper board I use for the stages (BTT Octopus
  Pro) has thermistor inputs meant for hotends and beds. Four 100 k NTC
  thermistors (printer-standard) go on:
  - the module plate beside the rotator;
  - the plate beside the gun support;
  - the rotator base;
  - the air gap between the unit and the module.

  The joint camera measures dot against corner at the start of every tube, and
  on idle laps between tubes. Over a few sessions the station fits the dot
  offset against those temperatures. Then it either compensates with the X
  stage (below), or tells the operator "re-trim; the module is 4 K warmer than
  at setup".
- **Keep their physical repairs.** A steel baffle under the upper tray with an
  air gap, and the exhaust aimed out of the side or rear, reduce the drift the
  model has to explain.

**What it leaves:** the unit's real air path and idle draw (Derek can feel and
read them); PET-GF's actual expansion; whether heat reaches the fiber's stored
S on the side panel (fiber heating is a question for XLaserlab, not a precision
one).

---

## 2. A constant cable shape stays constant only if the gun does not move

**Variant:** their cable argument. "The cable then has the same shape for every
tube, every session and every person, so its force on the gun is a constant."
It rests on the gun support being still: paddle, sled, fixed bridge.

**The difficulty from my side.** The automated vision needs motors. Put them on
the gun side (my B, the table station's gantry) and the cable's free span changes
with every commanded move, so its force on the gun changes too. The cart's best
property would be spent by the first motor. Their break 3 adds a second
constraint: the 531 × 330 mm upper tray has no room for a gantry.

**Assumption:** the cart station stays manual, or its motion goes wherever the
gun support is.

**Repair / branch M — "A on the cart": the work moves, the gun and every cable
and conduit stay still.** This merges their cart with my still-gun idea
(`ideas/a-still-gun-moving-tube.md`).

- **Motion under the tube only.**
  - A double-rail SFU1605 X stage (ZBX150 class: 150 mm wide, 120 kg
    horizontal) goes on the module plate under the rotator, radial to the dot.
    - Swept footprint: 350 × 250 mm on a ~520 × 300 module.
    - Travel: ±0.13 mm runout follow; corner scans of a few mm; the ~50–60 mm
      radial retract that puts the whole gun proxy outside the tube's plan
      footprint for loading.
  - The retract replaces their gun "park" rotation for tube changes. The cable
    exit does not move at all.
  - Z stays at first a manual trim on the gun support. Height per tube is
    measured by the joint camera on the first dry lap; a motorised Z is a later
    step.
- **Height.** The stage adds ~75 mm, so the dot moves from ~985 to ~1060 mm,
  still a standing counter height.
- **What stays constant.** The umbilical (saddle on their mast, clamp on the
  module), the wire conduit (feeder on the module), the gun and the joint camera
  never move during a session. Everything the AI changes moves a 6–7 kg stack a
  few millimetres on a ball screw, and the cable force on the gun is the
  constant they designed for.
- **Where the rest goes.**
  - **Joint camera:** on the module, on the free +Y side of the dot, inboard,
    ~85 mm up and ~120 mm away (the observation layer's placement). It is the
    metrology camera.
  - **PTZ:** on a short mast at the cart's front corner, on the +Y side (away
    from the gun's tail), 250–400 mm above the module, looking down into the
    recess at 20° or more.
  - **Station camera:** on their rear mast, beside the saddle, looking over the
    whole module: gun, cables, hands, the gun's status LEDs.
  - **Fiducials:** printed tags on the module plate register every PTZ frame.
    Because the cameras and tags ride the module, rolling the cart moves the
    whole measuring frame with it.
  - **Controller:** Octopus Pro + host, the rotator's ESP32/DM542T and supplies,
    in a box on the cart side panel opposite the fiber S. One power lead for the
    station's electronics, separate from the unit's own 20 A-class outlet.
  - **Bump log:** a small IMU on the module (BNO085 class). The Weldpro's
    casters have no brakes, so a bump or lean is recorded as an event in the
    same log as the weld.
- **Tipping.** Moving 6–7 kg by 50 mm shifts the load by ~0.3 N·m against their
  ~180 N·m sideways restoring moment. The motors do not change their tipping
  problem. A person leaning still does: their outriggers or bench dock remain
  the repair.

**What it leaves:**
- The heavy work lead and purge hose ride the X stage (hang the work lead from
  the mast).
- Their paddle compass references the plate itself; it would move with the
  tube on the X stage, which suits it: the paddle's P3 foot then needs a plane
  that moves with the stage, or it gives up X-follow.
- A module this full needs a real layout check against the rotator's motor and
  ground towers.

---

## What their idea does that mine lack

- **The cable system as a structure.** My arrangements carried the umbilical
  with a saddle "somewhere". Theirs gives it one shape, measured once, for every
  tube and person. For a learning machine that removes a hidden variable: two
  experiments a week apart see the same cable force, so a difference in the
  result is not the cable.
- **A station that moves as one piece** with its calibration inside it.
- **"Organise motion around the cable exit"**: park about an axis through the
  exit, perpendicular to the cable's plane. That is the rule for the head in my
  table station (`ideas/e-table-opening-station.md`). Its roll/tilt head should
  put the tilt axis's cable-side effect in the cable's own plane, and loading
  should never use the grip-axis roll.
- **A short, fixed wire conduit** from a feeder on the module. My new idea F
  builds on exactly that.

## What transfers from mine to theirs

- **Motion under the tube** keeps their constant cable shape constant.
- **The thermistor + camera drift model** turns their open heat question into a
  measured variable.
- **The joint camera's placement** on the free +Y side, and fiducials on the
  module, so observation travels with the cart.
- **The stylus.** Their cart has no table opening, so the tube's OD at the
  dot's angle is in open air on the module. The D-s stylus mounts on the module
  beside the tube with no gap to reach through.
