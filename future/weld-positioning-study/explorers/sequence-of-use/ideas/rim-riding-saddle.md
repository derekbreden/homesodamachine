# C. Rim-riding saddle — precision only while the contacts are loaded

Sketch: `../sketches/rim-saddle.svg` (plan to scale; section schematic).

> **Pose note (wave 3).** Numbers in the wave-1 text below were computed at scene hole **dial 65** (my proxy passed the dial straight into `posePoint`; the scene subtracts 35). Derek's opening pose is dial 30. The corrected numbers and the repaired branches are in the *Wave 3* sections at the end; dial-65 values are kept where they describe that reachable orientation.

## Picture it (as it now stands: mirrored for counter-clockwise, true opening pose)

The gun's shell sits, through a recipe stage, on a printed saddle that rides the
tube itself. The saddle carries five rolling contacts on the arriving side, which
is −Y at the true pose, where the wire comes from:

- two stainless bearings on the rim top (height);
- two on the outside wall just below the rim (radius and yaw);
- one lower on the outside wall (tilt).

These contacts are cold metal that the puddle has not reached. The saddle body
stays below ~35 mm above the rim, to pass under the wire (which crosses the outside
wall near −54° about 49 mm up) and under the barrel.

- **What carries.** A spring balancer hooked at the gun's centre of mass. That
  point is outboard of the contacts at (−30, −108) mm.
- **Preload.** A small separate preload between the rim rollers keeps all five
  contacts loaded.
- **What locates.** The tube, and only while the contacts are loaded.
- **The frame.** A tether to the frame takes only the rolling drag. The frame
  supplies weight and tangential restraint; nothing it does locates.
- **Branches.**
  - C-h: the same saddle held by hand.
  - C-p: height taken from the plate face by a tripod of ball transfers instead of
    the rim.

Sketch: `../sketches/rim-saddle.svg` (true pose, counter-clockwise, CG marked).

## Major unresolved problems

1. **Real CG and cable forces** against the preload.
2. **Residuals the contacts cannot see:** plate tilt vs rim (C5; C-p repairs it),
   and wall thickness.
3. **Space under the wire** on −Y.
4. **Heat** at the arriving contacts during the 20° overlap.
5. **Whether following is needed at all.** The process window is unknown.

## The physical idea

Precision is needed during two phases (dot dry run, weld) and then only relative
to *this tube's* joint. So take the reference from the tube itself at those
moments: the gun shell carries a printed saddle with rolling contacts that ride the
tube's rim and outer wall **on the arriving side** of the dot, where the metal is
still cold and unwelded. The frame only carries weight and stops the saddle from
being carried round; it does not locate anything.

- Five contacts (rolling, stainless 608 bearings or plastic tyres on them):
  R1, R2 on the rim top at ~22° and ~52° ahead of the dot (height; tilt about the
  radius); O1, O2 on the OD just below the rim at the same angles (radius; yaw);
  O3 lower on the OD at ~37° (tilt about the tangent).
- Sixth freedom — sliding round the circumference — is taken by a light tether
  (a rod with ball ends) to the frame. It carries the rolling drag only.
- Preload: net weight downward (a spring balancer carries most of the gun) and a
  radial inward pull (spring from the frame). Contacts only push; the preload
  keeps all five in compression.
- The fine stage between saddle and shell holds the recipe (pose about the dot) as
  in A and B. Per-tube variation (tube length, seating, runout, face runout) is
  taken up by the contacts automatically, because the plate hanger set the plate's
  depth relative to the same rim.

## Operating it

| Phase | Saddle |
|---|---|
| Load … shoe | Lifted off and swung aside on the balancer / arm |
| Tacks | Lowered onto the rim; plate held by the stationary hanger H2 (kit K1) or tacks by hand before lowering |
| Aim | Lower onto the rim at the station; contacts seat; no per-tube dial |
| Dry run | Pedal one revolution; the saddle follows the rim; the dot's track shows what is left over (plate vs rim, wall thickness) |
| Weld | Riding; trigger via kit K2 (or by hand in the hand branch below) |
| Stuck wire | Stays on the rim; snip; then lift |

The saddle is direction-specific: contacts on the arriving side. A ccw recipe needs
the mirror-image saddle (a second print).

## What it does to the unknowns

- Tube length, reseating and runout drop out of the per-tube setup.
- Umbilical and trigger forces no longer need to be *resisted* by a stiff frame;
  they need to be *smaller than the preload margin*. As long as no contact unloads,
  the pose is set by the contacts, not by the force.
- It measures itself: if a contact lifts, the dot jumps visibly in the dry-run
  video. A contact switch or a strain point on the tether could log it.

## Trying to break it

**C1 — heat and the lip.** Contacts near a weld on an unbacked 6.35 mm lip.
*Repair:* all contacts on the arriving side, 24–57 mm of arc ahead of the dot; that
metal is cold until the puddle arrives. Nothing touches the departing (hot) side.
Contact loads of a few tens of newtons: the lip as a 6.35 mm cantilever of 1.65 mm
wall is roughly 8 kN/mm per 10 mm of width (plain beam estimate), so preload does
not deflect it measurably. *Leaves:* heat conducted ahead of the puddle over a
48 s lap; plastic tyres may soften near R1 — use bare stainless bearings at R1/O1.

**C2 — the gun's weight tips the saddle the wrong way.** The gun's centre of mass
sits over the tube centre (proxy: 6 mm from the axis, 185 mm above the rim), inboard
of the rim contacts. On its own it rotates the saddle inward about R1–R2, which
swings the part below the rim outward and **lifts O3 off the OD**. *Repair:* hang the
gun from a spring balancer at (or just outboard of) its CG so the residual weight
acts outboard of the rim contacts, or add a counterweight on the saddle outside the
tube. Then the net moment loads O3. *Leaves:* the balance depends on the real CG
(unknown) and changes if the umbilical pulls.

**C3 — contamination.** Carbon-steel rollers on 316L leave free iron. *Repair:*
440C stainless bearings (Prime, $9.99/10) or plastic tyres; the contacts run on the
OD stripe near the rim, which is scuffed/cleaned like the copper shoe stripe.

**C4 — the tether and the lap.** The tube turns 380°; the saddle stays. Drag is
rolling friction plus bearing seals — small, but the tether direction must be
tangential so it does not add radial or vertical load. A tether that also pulls
inward would change the preload during the lap. *Repair:* long tether (≥ 200 mm)
with ball ends, tangential at the saddle.

**C5 — what the contacts do not see.** They follow the rim and the OD, not the
plate face or the ID corner. Plate tilt relative to the rim (face TIR up to 0.30 mm
accepted) and wall-thickness variation pass straight through to the dot. These are
exactly the residuals a dry run then shows. *Leaves:* whether ±0.15 mm matters in
the (unknown) process window.

**C6 — landing it.** Lowering a saddle onto a rim by hand can bang a roller onto the
lip. *Repair:* a guide on the balancer arm that brings the saddle down vertically
over the station; the last 10 mm under a light spring.

**C7 — stuck wire and lifting.** With the wire stuck to the bead, lifting the saddle
bends the wire and guide. *Repair:* snip before lift, always (same rule in all
arrangements).

## Branch C-h: hand saddle (cheapest test of the idea)

Same saddle, no balancer, no tether: Derek holds the shell by its grip as now and
presses the saddle onto the rim; the pedal turns the table; his trigger finger
stays on the trigger. His hand *is* the preload and the tether. The contacts do the
positioning; the hand only has to keep them loaded, which is a much easier skill to
hand to another person than holding a pose in the air.

Break: over a 48 s lap the hand's force direction wanders; if it leaves the contact
"cone", a roller lifts. The trigger force now goes through the saddle — acceptable
here, because it adds to preload if the trigger pull points toward the contacts
(it depends on the grip direction relative to the saddle; unknown).
Value: one printed part plus a few bearings tests the central claim (the rim can
locate the dot) with the camera recording the dot, before any frame is built. If
the claim fails, the result still says how much the rim and plate differ.

## Parts (representative)

- S608-2RS 440C stainless bearings (KABOBEARING, Prime, $9.99/10).
- QWORK spring balancer 1.1–3.3 lb, 2-pack (Prime, $16.97, 50+ bought/month) — for
  the gun's weight; its range fits a ~1 kg gun (assumed mass).
- Printed saddle and tether; M8 shoulder bolts or 8 mm pins as axles.

## Contribution, open problems, assumptions

Contribution: removes per-tube setup and turns cable/trigger forces into a preload
margin question; offers a very cheap first experiment (C-h). Open: CG balance (C2),
residuals the contacts cannot see (C5), mirror saddles per direction. Assumptions:
proxy pose, contact angles chosen by eye, gun CG at the proxy housing centre.

---

## Wave 3 — true opening pose (hole dial 30), mirrored saddle, and branch C-p

**Which side arrives.** At dial 30 the scene's wire runs from the tip toward −Y
(plan angle −115°, rising at 38°). With the wire on the arriving side, as the
current per-weld sequence says, the arriving (cold) side is −Y and the table turns
**counter-clockwise** from above. who-moves-what pointed this out. The sketch is
redrawn for ccw with the contacts on −Y. The wave-1 cw / +Y layout is kept, labelled,
for a recipe with the gun on the +Y side.

**Space on −Y.** The wire crosses over the OD near −54° at ~rim + 49 mm, and the
barrel near −81° at ~rim + 76 mm. The saddle body must stay below ~rim + 35 mm
across −10°…−90°.

**C2, recomputed.** At dial 65 the CG sat over the tube centre, inboard of the rim
contacts, and lifted O3. At dial 30 it sits at (−30, −108), 375 mm above the bench:
outboard of the wall and beyond R2 in angle (≈ −105°).

- It no longer lifts O3.
- It lies outside the contact polygon, so on its own it would tip the saddle about
  R2 and lift R1.

*Repair:* hang the gun from a balancer at its CG (the bail of idea E; the same
arrangement as borrowed-ecosystems' A1), and apply a small separate preload (5–10 N)
between R1 and R2. The contacts then carry only that preload.

**Branch C-p — height from the plate face (who-moves-what).** Replace R1/R2 with a
tripod of ball transfers on the plate face inside the recess (r ≈ 30–47 mm,
upstream); keep the OD rollers. This removes C5: plate tilt relative to the rim no
longer passes straight to the dot.

- *Sequence and space constraint:* on the −Y side the wire descends into the corner.
  At ~30 mm along its path it is only ~23 mm above the plate (r ≈ 56, −23°), which is
  too tight for a 5/8 in transfer unit (~20 mm tall).
- Put the tripod at −40° to −70°, where the wire is ≥ 35 mm up.
- The tripod rides clean, cold plate face ahead of the puddle. It never crosses the
  tacks, which sit in the corner.

C-h, the hand saddle, is still the cheapest first experiment. who-moves-what
suggests running it on the same tube as their mapped dry lap (3b): C-h shows whether
contacts can locate the dot, and 3b shows whether following is needed at all.
