# Foam shell

3D-printed PETG enclosure for the soda machine's "cold core" — the
back-of-enclosure subsystem that holds the carbonator pressure vessel, the
copper evaporator coil wrapped around it, and two flavor reservoirs in
pockets on opposite sides. Pour-in-place polyurethane foam fills the
cavities around the wetted/cold parts for thermal insulation.

## Coordinate convention

The CadQuery script uses an explicit XZ plane with +Y normal
(`xz_plane_y_up`), so geometry grows upward in +Y.

- **Y** is vertical. The floor sits at y=0; everything stacks upward from
  there.
- **X** is the bag axis. Two bag pockets sit on opposite sides along X.
- **Z** is perpendicular to the bag axis.

## Physical inputs

- **Pressure vessel** — 5.000" OD × 0.065" wall × 6.000" cut length 316 SS
  welded tube (OnlineMetals #12498). Two 1/4"-thick 316 SS endcap plates
  laser-welded internally, recessed flush with the tube ends. Hand-tapped
  1/4" NPT, four ports total — two top plate (water inlet, PRV), two
  bottom plate (CO2 inlet, water outlet). Vessel assembled height = tube
  length = **152.4 mm**. Outer radius = **63.5 mm**.
- **Bag** — Platypus-style soft-walled bladder, 1 L max but used at
  ≤ 750 mL. Single port at the cap end with a 90° turn. Filled envelope,
  posed cap-down: **125 mm wide (along Z) × 35 mm deep (along X, radially
  outward) × 225 mm tall**. Two bags per cold core. (Production now uses
  a rigid PETG reservoir matching this envelope; "bag pocket" is still
  the geometric name in the code.)
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper,
  hand-wound helically around the vessel exterior, bonded with 3M 425
  aluminum foil tape. ~6.35 mm radial occupancy plus tolerance — budgeted
  at 7 mm (`copper_coil_buffer_radius`).
- **Tank-port fittings** — 1/4" NPT 90° elbows on every port, turning the
  line laterally. ~30 mm vertical envelope per elbow above and below the
  tank. An additional **John Guest PP0308E 1/4" PTC 90° elbow** seats in
  the Ø16 CO2 inlet bore at x = 0, z = −70.5, where the cap-top CO2 line
  transitions 90° into a horizontal run that connects to the vessel-port
  TAISHER elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter.

## Shells

The geometry is built up from open-topped sub-shells that union into
one foam-shell solid. **All structural walls and floors use 2 mm
thickness** (`wall_and_floor_thickness`).

### reservoir_pocket_walls

Two reservoir pockets, one on each ±X side of the cold-core, mirrored
across the YZ plane. Each pocket is a four-walled enclosure (open at
+Y; the outer_shell's floor closes the bottom; the foam_cap closes
the top during foam pour):

- **Far ±X wall** — outboard face at x = ±107.5, cavity face at
  x = ±105.5.
- **+Z wall** — outboard face at z = +72.5, cavity face at z = +70.5.
- **−Z wall** — outboard face at z = −72.5, cavity face at z = −70.5.
- **Centerward wall** — the only curved wall. Its cavity-side face
  rides on a cylinder of radius **72.5 mm**
  (`pocket_centerward_arc_outer_radius`, centered on the cold-core
  Y axis); its tank-side face is concentric one wall-thickness
  inboard at R = 70.5. The 7 mm of radial clearance between the
  tank's outer face (R = 63.5) and the wall's tank-side face fits
  the 1/4" ACR copper coil + thermal tape + slack.

The centerward wall is one continuous curved wall built from three
arc segments along its length:

1. A **middle segment** — the cylindrical arc that wraps the tank+coil
   envelope, running from z = −60 to z = +60 (the handoff Z is
   `pocket_centerward_arc_transition_z`).
2. Two **transition segments**, one at each ±Z end — short 8 mm-radius
   arcs that swing the wall out from the middle arc to the pocket's
   ±Z wall. Each transition arc is tangent to the middle arc and to
   the ±Z outboard face; its tank-side face has radius 8 mm and its
   cavity-side face is concentric with the same center but a slightly
   smaller radius derived from geometry.

The two **far-side corners** (where the far +X wall meets the ±Z
walls) are filleted: **6.5 mm inner radius, 8.5 mm outer radius** (so
the wall thickness stays uniform through the bend). The 6.5 mm inner
radius matches the rigid PETG reservoir's 6 mm outer fillet plus the
0.5 mm `reservoir_clearance`, so the reservoir slides into a snugly-
mated pocket with uniform clearance around the corner.

The pocket is **open along its centerward face into the foam zone
inside the centerward arc envelope** — there's no wall at radius
R < 70.5. During operation, that interior region holds the tank +
copper coil, and the foam pour fills the gap between the coil and
the wall's tank-side face.

The four walls of each pocket are traced as a single connected
outer-perimeter polyline (with the matching cavity-perimeter polyline
cut out of it), so the four walls union into one solid by
construction. The +X pocket is traced explicitly; the −X pocket is
its mirror across YZ. Total assembly height = 213.4 mm
(`foam_shell_outer_height`).

### tank_support_ring

Annular ring sitting inside the lower portion of the assembly,
holding the tank up by its outer rim. The ring's outer face is
coincident with the centerward wall's tank-side face (at R = 70.5
at the current 2 mm wall thickness); its inner face sits 9 mm
inboard at R = 61.5. The top face is a flat annular plateau where
the tank's outer rim rests, 30 mm tall above the floor (y = 2 to
y = 32).

Inboard of the ring's inner face (R < 61.5) is open volume — so the
tank's bottom-plate fittings have unobstructed downward space, and
pour foam fills around them.

Four 30°-wide angular slots are cut through the ring at azimuths
45°/135°/225°/315°, leaving four 60° support segments aligned with
the cardinal axes. The slots let pour foam reach the under-tank
floor regardless of which cavity it enters from.

### outer_shell

Outer rectangular cup framing the whole foam-shell: floor + four
perimeter walls + six 8 × 8 mm bosses. Total height matches the
foam-shell outer height (213.4 mm = `foam_shell_outer_height`).
Outer footprint
(`outer_shell_x_length` × `outer_shell_z_length` = 283 × 181 mm)
sized to leave `outer_shell_foam_gap` (= 16 mm) of foam-pour zone
between the outer_shell's inner face and the outermost reservoir-
pocket walls on each side.

The six bosses are positioned at the four corners + two mid-long-side
positions (offset in X by ±15 mm with opposite signs at +Z vs −Z, to
preserve 180° rotational symmetry around the Y axis). Each boss
carries a heat-set insert pocket at the top (drilled down from the
top face) and at the bottom (drilled up from the bottom face) —
twelve inserts total, six per face, for fastening the foam_cap above
and below.

The outer +Z wall carries the shared copper/water-inlet slot, the
two ⌀6.5 reservoir-line holes, the two reed-cable holes, and the
water-outlet hole. See Penetrations. (The CO2 inlet bore is internal
to the assembly — it cuts down through the support ring at −Z, not
through any outer wall.)

### foam_cap and foam_cap_lid

The `foam_cap` is a 16 mm-tall cup matching the outer shell's
footprint, printed twice — one sits on top of the assembly (flipped,
open side mating with the outer shell's top edge) and one on the
bottom (in normal orientation, open side mating with the outer
shell's bottom edge). The cap interior receives the foam pour
through pour and vent holes in the lid above.

The `foam_cap_lid` is a flat 2 mm plate matching the same outer
footprint, sitting on top of a cap during its foam pour. It has the
pour hole (Ø 10 mm) and two vent holes (Ø 6 mm).

Both the cap and the lid have **six 8 × 8 mm boss / clearance-hole
positions** — four at the corners (inherited from the earlier dowel-
pin layout) and two at the mid-points of the long edges (one near
the +Z wall and one near the −Z wall, offset in X by ±15 mm with
opposite signs at +Z vs −Z for 180° rotational symmetry). Each
position passes a clearance hole for an M3 cap screw all the way
through the part. See "Cap-to-outer-shell joinery" below.

### foam_cap_gasket

A TPU 90A gasket, printed twice — one between each cap and its
mating face on the outer_shell. 251 × 181 mm outer envelope, 2 mm
thick (flat 2D shape throughout — no 3D features). The shape is a
**5 mm-wide perimeter ring + an 8 × 8 mm pad at each of the six
screw positions**, matching the boss footprints on the cap and
shell above and below. Each screw hole sits at the center of its
pad with 4 mm of TPU material on all sides, so the screw clamp
force compresses the full 8 × 8 boss footprint uniformly. A
uniform-width ring without these pads would leave the corner-boss
screw holes asymmetrically supported (1 mm of TPU on the cavity-
facing side, 4 mm on the outer-facing side), compressing unevenly
and sealing poorly. The 1 mm of the perimeter-ring width that's
aligned with the cap and shell wall edges is the part that seals
along the wall sections (away from the bosses); the remaining 4 mm
extends inward over the cavity opening for print stability and
material continuity. Replaces the friction-fit pin joinery's
complete absence of any seal between cap and outer shell.

## Cap-to-outer-shell joinery

Each cap (top and bottom) is fastened to the outer_shell with **six
M3 × 25 mm DIN 912 socket head cap screws, 12.9 alloy steel, black
oxide finish** ([BNUOK B0DJQGF665](https://www.amazon.com/dp/B0DJQGF665),
60-pc bag $8.57 delivered = $0.14/screw, head Ø 5.5 × 3.0 mm tall,
2.5 mm hex) threading into **six ruthex M3 short heat-set inserts**
([B09ZHSGHXD](https://www.amazon.com/dp/B09ZHSGHXD) — same insert
spec as in `touch-flo-shell`; the 100-pc bag already on order for
that part covers ~7 builds at the combined 14-inserts-per-unit
total) pressed into the corresponding face of the outer_shell.
**Twelve inserts and twelve screws total per outer_shell:** six on
the top face accepting the top-cap screws threading down from above,
six on the bottom face accepting the bottom-cap screws threading up
from below.

Stack-up under each screw head, top cap (mm):
- Lid (1) + cap floor (1) + cap boss / interior void (14) + cap
  mating edge (1) + gasket (2) = 19 mm above the outer_shell mating
  face
- 4 mm engagement into the insert
- M3 × 25 mm screw under-head length = 25 mm, with 2 mm slack into
  the pocket relief below the insert

Insert pocket: Ø 4.0 mm × 8 mm deep (4 mm for the insert + 4 mm
relief so the M3 × 25 screw tip has clearance and doesn't bottom
out). Pockets are drilled inward from each face — top face pockets
go down, bottom face pockets go up.

Standard SHCS chosen instead of the ultra-low-profile heads used in
`touch-flo-mounting-plate`: there's no under-counter flush-mount
constraint here (the heads protrude on the appliance top and bottom
faces; under-counter install hides both), and the standard DIN 912
SHCS is roughly an order of magnitude cheaper Prime-shippable than
McMaster ULH. Black finish is preferred over bright stainless for
appearance; black oxide on alloy steel is adequate corrosion
protection for this dry foam-filled enclosed interior.

Six attachment positions per cap (vs the earlier four pin corners)
halve the longest unsupported gasket span between adjacent screws
from ~251 mm corner-to-corner along the long axis to ~125 mm, which
matters for a TPU gasket compressed only at discrete points. The
two mid-long-side screws are offset in X by ±15 mm (opposite signs
at +Z vs −Z) rather than centered at x = 0, both to clear the
shared +Z slot that runs up the centerline and to preserve 180°
rotational symmetry so the caps can be flipped end-for-end.

## Penetrations

Eight pass-throughs total, all carrying **1/4" OD tubing (6.35 mm)** through
holes sized at ⌀6.5 mm for a tight tube fit. Four pass-throughs each get
their own dedicated round hole; the remaining four share a single
Y-elongated slot at the +Z outer wall.

| # | Pass-through | Opening | Carries |
|---|---|---|---|
| 1 | Reservoir line (+X) | own ⌀6.5 hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 2 | Reservoir line (−X) | own ⌀6.5 hole | 1/4" OD soft tubing — reservoir to peristaltic pump |
| 3 | CO2 inlet | own ⌀16 doorway | 1/4" OD line from the regulator (90° push-to-connect elbow seats in the doorway) |
| 4 | Water outlet | own ⌀6.5 hole | 1/4" OD line to the dispense faucet |
| 5 | Copper evaporator inlet (low) | shared +Z slot | 1/4" OD ACR copper to compressor |
| 6 | Copper evaporator outlet (high) | shared +Z slot | 1/4" OD ACR copper to compressor |
| 7 | Water inlet | shared +Z slot | 1/4" OD line from the diaphragm pump |
| 8 | PRV vent | shared +Z slot | 1/4" OD LLDPE from the prv-shroud cap into the appliance interior (unpressurized; carries relief-event discharge only — see [`../prv-shroud/`](../prv-shroud/)) |

**Build decision:** for the water inlet and CO2 inlet, the supply-side
tubing reduces to 1/4" OD *before* reaching the shell wall — i.e., the
transition fittings (3/8" barb-to-NPT adapter, 5/16" push-to-connect,
1/4" NPT check valves, etc.) all live on the warm side of the shell.
Inside the shell, every penetration is the same 1/4" OD. This keeps
holes small, uniform, and simple to seal during foam pour, at the cost
of the transition fittings being a few cm further from the tank.

### Shared +Z slot and copper plug stack

The +Z outer_shell wall carries four pass-throughs along a single
**Y-elongated slot** at x = 0: the two copper evaporator lines (low
and high), the water inlet, and the PRV vent. The slot is ⌀6.5 mm
wide in X (rounded ends along Y), runs from y = 42 up to
y = `foam_shell_outer_height + 10` (10 mm of open extension past
the wall top), and is cut by `cut_slot_for_copper_and_water_inlet`
in `_port_cuts.py`. The 10 mm top extension means no sliver
of wall material remains above the slot — the four plugs can
slide down into the slot from above during assembly. With the
centerward wall extending only to z = ±72.5 (where it meets the
±Z walls via the transition arcs), the slot at x = 0, z = 52.5
pierces only this one outer +Z wall.

Pass-through Y heights (centers, measured from the **top of the
floor** — i.e. from the interior cavity's lower bound, not from y = 0):

| Pass-through | Y center above floor (mm) |
|---|---|
| Lowest copper (evaporator inlet) | 45.0 |
| Highest copper (evaporator outlet) | 164.4 |
| Water inlet | 196.4 |
| PRV vent | 204.4 |

(Absolute Y in the CadQuery model is +`wall_and_floor_thickness`
above these — i.e. 47.0 / 166.4 / 198.4 / 206.4 at the current
2 mm wall — since the floor occupies y = 0 to
y = `wall_and_floor_thickness`.)

(The highest copper drifted by −1 mm relative to the floor top when
`wall_and_floor_thickness` was bumped from 1 mm to 2 mm in commit
`8a9ffc0`; the formula
`foam_shell_outer_height − hole_shift_from_edge − wall_and_floor_thickness − above_tank_elbows_height`
has a `−wall_and_floor_thickness` term that the `+wall_thickness_compensation`
inside `foam_shell_outer_height` only half-cancels once you reframe
against the floor top. The drift was accepted.)

Four printed PETG **copper plugs** slide down into the slot from
above to seal the gaps between (and above) the four pass-throughs:

| Plug | Y span (mm) | Y end arches |
|---|---|---|
| `copper-plug-lower` | 50.75 → 162.65 | both ends |
| `copper-plug-middle` | 170.15 → 194.65 | both ends |
| `copper-plug-upper` | 202.15 → 202.65 | both ends |
| `copper-plug-top` | 210.15 → 211.40 | bottom end only (top flat) |

Each plug has a **binder-clip cross-section** that grips the wall
edge instead of floating loosely in the slot. Viewed end-on, it's an
I-beam: a 6.5 mm × 2 mm plate-body web fits the slot's wall Z range
exactly, 4 mm-tall "wings" at the outer X edges of the slot span the
full plug Z envelope, and 1 mm × 1 mm rail prongs branch out past
the wings at +Z (above the wall outer face) and −Z (below the wall
inner face). The 2 mm air gap between the top and bottom prongs at
the rail edges is where the wall material slides in — that's how
the plug grips the wall like a binder clip. The wings act as the
I-beam flange linking web to prongs along a continuous 2D face
(rather than a 1D corner edge); see the docstring at the top of
`copper-plugs/generate_step_cadquery.py` for the full cross-section
diagram.

Each plug end that abuts a tube has a **⌀6.5 mm half-circle arch
cutout** centered at x = 0, so the plug seats around the tube
without crushing it. `lower`, `middle`, and `upper` all arch at
both Y ends; `top` arches at the bottom Y end only (its top is
flush with the wall top and stays flat).

After the four plugs are installed, the slot still has ~4.25 mm of
total unfilled length within the wall along Y: 1.75 mm at the
bottom of the slot, 2 mm at the top, plus eight 0.5 mm clearance
bands (one above and one below each of the four tubes). All of
that gets filled by the body foam pour.

## Assembly and foam pour

Production-procedure framing at [`../../../assembly/cold-core.md`](../../../assembly/cold-core.md). The geometry detail below is the source-of-truth for the shells and the pour paths; the assembly doc is the production-cadence wrapper that places this pour in the appliance build sequence.

The cold core is foam-filled in **three independent pour operations**:
the top cap, the bottom cap, and the body. Each is a self-contained
pour; nothing chains across the three.

### Top cap and bottom cap (independent, before final assembly)

Each cap is a 16 mm-tall foam-filled cup. Liquid pour-in-place foam
goes in through the `foam_cap_lid`'s Ø10 mm pour hole, air escapes
through the lid's two Ø6 mm vents, foam expands to fill the cap's
interior, cures to a self-contained foam puck. Done before the cap
is mated to the body.

### Body pour (after all body-side assembly)

Every internal component is installed first:

- Pressure vessel lowered into the centerward arc envelope, seated
  on the `tank_support_ring`.
- Copper evaporator coil hand-wound around the vessel exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two reservoir pockets.
- Copper evaporator inlet (low), copper evaporator outlet (high),
  water inlet, and PRV vent LLDPE (from the prv-shroud cap) routed
  through the shared +Z slot at their four Y heights. The water
  inlet and PRV vent both come from above the tank and take slight
  bends in their LLDPE runs to land in vertical alignment in the
  slot.
- Four copper plugs slid down into the slot from above (through
  the 10 mm open extension past the wall top) to seal between the
  pass-throughs.
- PRV shroud (`../prv-shroud/`) slipped over the SV-125 valve,
  seated on the TAISHER elbow's smooth ⌀18.8 cylinder, and hot-
  glued at the elbow joint for foam-pour-tightness.
- Reservoir LLDPE lines routed through holes #1 and #2 in the
  reservoir-pocket far ±X walls.
- Water outlet through hole #4 in the outer_shell +Z wall.
- CO2 inlet enters from above through the foam-cap-top boss +
  foam-cap-lid-top hole at (x=0, z=−68.75); the line drops to
  y=17 inside the cavity and bends 90° at a PP0308E push-to-connect
  elbow seated in the Ø16 CO2 inlet bore at x = 0, z = −70.5.

With everything in place, liquid foam is poured **directly into the
body's open +Y top** all at once — no cap on, no down-channels.
Foam falls into the body and reaches the two air volumes in
parallel:

- the **two reservoir-pocket cavities** (each open at +Y, fully
  enclosed below and on its four sides);
- the **surrounding foam zone** — a single connected volume wrapping
  around the pockets between the outer_shell and the pockets'
  outboard walls. This zone reaches the centerward space around the
  tank+coil through the gap at x ∈ [−39.7, +39.7] where the pockets'
  ±Z walls end (z = ±72.5) and the centerward walls' transition arcs
  swing in to join them.

The longest required slot traverse for the foam is the ~0.5 mm
radial gap between the coil and the centerward wall's tank-side
face at the ±X azimuths — ~110 mm of arc to reach around the back
of the coil from the ±Z entry. Shorter than the old top-down
~200 mm vertical traverse the diagonal pour-channels were originally
added to help with.

Foam expansion may push a small amount of material out through the
0.5 mm clearance bands around tubes in the +Z slot and through the
tight-fit tube exits at the other penetrations. This is expected;
trim flush after cure.

### Final assembly (after all three foam pours have cured)

TPU gasket onto the body's top edge, top cap screwed down with six
M3 × 25 SHCS. Bottom cap screwed onto the body's underside (no
gasket — the body floor handles the air seal). See the screw /
insert spec under "Cap-to-outer-shell joinery" above.

## Coincident-wall principle

Wherever two structural surfaces touch in the assembly, their walls
are positioned so they **overlap exactly in 3D space** — same outer
face, same inner face — rather than sitting side-by-side. After
union, that boundary is one wall's worth of material (2 mm), not
two (4 mm).

This drives several dimension choices:

- Each **reservoir pocket's ±Z outboard face** sits at
  z = ±`pocket_centerward_arc_outer_radius` (= ±72.5), tangent to the
  cylinder the centerward arc rides on. The ±Z walls meet the
  centerward wall's transition arcs along that tangent.
- The **tank_support_ring**'s outer face sits at
  `pocket_centerward_arc_outer_radius − wall_and_floor_thickness`
  (= 70.5), coincident with each pocket's centerward wall on its
  tank-side face.
- Each **reservoir pocket's four walls** are traced as a single
  connected outer-perimeter polyline (with one cavity-perimeter
  polyline cut from it), so the four walls union into one solid by
  construction rather than by OCCT face-merging.
- The **outer_shell**'s inner face sits `outer_shell_foam_gap`
  (= 16 mm) outboard of the outermost reservoir-pocket walls — a
  deliberate gap, not a coincidence: this is the outer foam-pour zone.

## Print settings

Current slicer save: [`foam-shell.3mf`](foam-shell.3mf) (Bambu
Studio 02.06.01.55). Plate contains four objects sliced together:
`foam-shell` + `copper-plug-lower` + `copper-plug-middle` +
`copper-plug-upper`. The `foam-cap` and `foam-cap-lid` are printed
on a separate plate.

### Chamber exhaust fan

PETG on the H2C heat-soaks during long prints, which causes outer-wall
warping. The fix is to vent the chamber with the chamber exhaust fan
(`M106 P2 S153` — `P2` selects the chamber exhaust, `P0` is part-
cooling, `P1` is aux; `S153` is ~60 % of 255).

Background: a previous H2C running this part on PETG produced
warp-free prints (first 2 mm walls, then 1 mm walls) once
`M106 P2 S153` was added unconditionally to the filament Start
G-code (commit `24605cb`). That earlier printer's nozzle size is
not recorded in the repo. That setup was retired and the work
moved to a **brand-new H2C** — the 0.8 mm nozzle transferred over
physically, but plate, chamber, gaskets, and everything else are
clean-slate.

On the new H2C, the same unconditional setup pulled too much heat
too early and the first layer curled off the bed. Delaying the fan
to layer 16 (in Layer Change G-code) let the print get past the
first-layer-adhesion phase but the corners still lifted within one
or two layers of the fan turning on. No fan-off attempt has been
run to completion yet.

Conditional placement: the M106 line **must** live in **Printer
Settings → Machine G-code → Layer Change G-code** (appended to the
existing layer-progress lines), not in filament Start G-code.
`layer_change_gcode` is re-emitted each layer with `layer_num`
rebound; filament Start G-code is evaluated once at `t=0` where
`layer_num` is 0, so the conditional would never fire from there.

Current `foam-shell.3mf` Layer Change G-code carries:

```gcode
{if layer_num == 29}M106 P2 S77{endif}
```

`layer_num` is 0-indexed, so this targets the 30th layer (~12 mm up
at 0.4 mm layer height) at ~30 % fan speed (S77 / 255).

### Printer / profile

- **Printer:** Bambu Lab H2C, **0.8 mm nozzle**
- **Print profile:** `0.40mm Standard @BBL H2C 0.8 nozzle`
- **Layer height:** 0.4 mm (initial layer 0.4 mm)
- **Line width:** 0.82 mm (inner / outer / top all 0.82)
- **Wall loops:** 2
- **Top / bottom shells:** 4 / 3
- **Sparse infill:** 15 % grid
- **Speeds (mm/s):** outer 200, inner 300, infill 350, top 200,
  travel 1000, initial layer 50
- **Supports:** off (threshold 30°)
- **Brim:** auto, 5 mm width, 0.1 mm object gap, 0.15 mm elephant-foot
  compensation
- **Wrapping detection:** off

### Filament

- **Material:** Bambu PETG Basic @BBL H2C
- **Nozzle temp:** 250 °C (initial layer 245 °C)
- **Bed:** Textured PEI Plate at 70 °C
- **Chamber:** passive (`chamber_temperatures: 0`); chamber exhaust
  fan delayed via conditional, see above
- **Flow ratio:** 0.97
- **Max volumetric speed:** 21 mm³/s (28 on the second nozzle slot)
- **Part-cooling fan:** max 40 %, min 20 %, overhang 90 % at ≥ 10 %
  overhang, closed first 3 layers
- **Auxiliary fan (P1):** on

### Attempts (0.8 nozzle / 0.40 mm layer)

| # | Date | Outcome | Change for next attempt |
|---|------|---------|-------------------------|
| 1 | 2026-05-11 | Nozzle clumping at layer 1 | Called a fluke (no slicer change); restarted |
| 2 | 2026-05-11 | First-layer curling off the bed; not noticed in time | Suspect chamber exhaust fan pulling heat before brim grip. Moved `M106 P2 S153` from unconditional to `{if layer_num == 15}M106 P2 S153{endif}` inside filament Start G-code |
| 3 | 2026-05-11 | Cancelled mid-print after realizing the conditional in filament Start G-code wouldn't fire (`layer_num == 0` at slice time → empty expansion → fan off the whole print) | Move the conditional from filament Start G-code into printer-level Layer Change G-code, where `layer_num` is rebound per layer |
| 4 | 2026-05-11 | Conditional fired correctly at layer 16, but corners lifted within ~1 layer of fan turn-on | Suspected the chamber fan itself, on this brand-new H2C, is the failure cause regardless of trigger layer. Two candidate next attempts discussed: skip the chamber fan entirely (single-variable test) or reduce both fan speed and trigger layer (layer 30 / 30 %) |
| 5 | 2026-05-11 | In progress — Layer Change G-code now reads `{if layer_num == 29}M106 P2 S77{endif}` (~30 % fan at the 30th layer, ~12 mm up). Both axes moved in the safer direction: trigger layer 16 → 30, fan speed 60 % → 30 % | — |

## Regression baseline

Source-level refactors of `_foam_shell.build_full_shell()`
should preserve the geometry of `foam-shell.step` exactly.  These four
scalars are the canonical regression sieve — any change to them
(beyond OCCT numerical noise at the ~1e-6 mm³ level) is a geometry
shift that needs a deliberate explanation:

| metric | value |
|---|---|
| volume   | **996325.726298 mm³** |
| bbox x   | [−134.500, +134.500] mm |
| bbox y   | [0.000, 213.400] mm |
| bbox z   | [−90.500, +90.500] mm |
| centroid | (0.000005, 90.742949, −0.616723) mm |

Captured at commit `ff24ef7` after a comment-removal pass on
`_foam_shell_geometry.py` (geometry preserved at vol Δ = 0 across
that pass).

Volume at commit 68b8d3f (the bug — slot extended to y=0, cutting
through the floor at y=0..2 in x∈[−8,8], z∈[−70.5,−30.5]) was
981102.086096 mm³. Restoring that floor strip adds +1280.07 mm³ of
PETG back: 288 mm³ from the arch's own y=0..2 floor at x∈[−8,8],
plus the bag-pocket bridging-wall and outer-shell floor material
the slot was wrongly clearing in the same y=0..2 strip over the
full +Z extrusion. The centroid shifts slightly in Y and Z because
the recovered material is concentrated near y=1 and z=−50.5.

Geometry-change history immediately prior: `bag_pocket_depth` was
bumped from 37 mm to 46 mm (+9 mm interior X depth per reservoir,
+18 mm total outer-shell X width), sizing each reservoir's cavity
to hold ≥ 1 L of usable fluid (1003.75 mL per reservoir at this
geometry, 2.01 L total between the two reservoirs).  Volume at the
start of that bump was 948199.817081 mm³ (bag_pocket_depth = 37 mm,
bbox x = ±125.5 mm); the +36957.6 mm³ delta to 985157.417081 mm³
was the new +X strip on each of the two bag pockets (~85.4 cm²
cross-section × 195.4 mm extrusion × 2 sides = ~33.4 mL × 2 ≈
66.7 mL of foam-shell material added).  Future refactors that
introduce a deliberate geometry change should update this section
in the same commit.

Quick reproduction:

```python
import cadquery as cq
s = cq.importers.importStep("foam-shell.step").val()
bb = s.BoundingBox()
com = s.Center()
print(s.Volume(), (bb.xmin, bb.xmax, bb.ymin, bb.ymax, bb.zmin, bb.zmax), (com.x, com.y, com.z))
```

## Reference

- [`../../flavor/pump-case/generate_step_cadquery.py`](../../flavor/pump-case/generate_step_cadquery.py)
  — gold standard for the PETG-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).
