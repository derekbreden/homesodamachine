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
  the Ø16 doorway of the −Z support arch, where the cap-top CO2 line
  transitions 90° into a horizontal run that connects to the vessel-port
  TAISHER elbow via a PP010822E 1/4" PTC × 1/4" NPT M adapter.

## Shells

The geometry is built up from open-topped shells, each printed as a
separate solid and unioned together. **All shells use 2 mm wall and floor
thickness** (`wall_and_floor_thickness`).

### tank_copper_shell

Round cup that contains the pressure vessel and the copper coil zone
wrapped around it. Outer radius **72.5 mm** (tank radius 63.5 + coil-zone
buffer 8 + 1 mm wall-thickness compensation). Total height **213.4 mm**
(tank height 152.4 + 30 mm above + 30 mm below for the 90° elbow space
+ 1 mm wall-thickness compensation).

The cylindrical wall is **cut at z = ±60** (`tank_copper_shell_open_z`),
so the ±Z apex bands of the wall are removed entirely. The cylinder is
open at +Z and at −Z over its full Y height, leaving the coil zone
directly accessible from those two sides.

Four **curved bridging walls** close each of the four open arc ends of
the cylinder, connecting them to the inner faces of the
`bag_pocket_support_shell`'s ±Z walls. Each bridging wall is convex
toward the tank/coil cavity (origin side) and concave toward the
adjacent bag pocket; its tank-facing face is an arc of radius **8 mm**
(at 2 mm wall, scaled from a 6.5 mm base by wall-thickness
compensation), and its reservoir-facing face is a concentric arc one
wall-thickness inboard. The bridging walls' chord-end X range matches
the cylinder's wall band exactly at z = ±60, so OCCT's boolean union
merges cylinder and bridging walls into one continuous solid.

Pour-foam access to the coil zone now travels **laterally** through the
±Z apex openings rather than top-down through the now-removed diagonal
channels: foam falls into the cylinder's open +Y top, into the corner
pockets at ±Z, and bleeds into the coil zone through the full-height
±Z openings.

### tank_support_ring

Annular ring sitting inside the lower portion of the tank-copper-shell,
holding the tank up by its outer rim. The ring's outer face is
coincident with the tank-copper-shell's inner wall (at R = 70.5 at the
current 2 mm wall thickness); its inner face sits 9 mm inboard at
R = 61.5. The top face is a flat annular plateau where the tank's
outer rim rests, 30 mm tall above the floor (y = 2 to y = 32).

Inboard of the ring's inner face (R < 61.5) is open volume — so the
tank's bottom-plate fittings have unobstructed downward space, and pour
foam fills around them.

Four 30°-wide angular slots are cut through the ring at azimuths
45°/135°/225°/315°, leaving four 60° support segments aligned with the
cardinal axes. The slots let pour foam reach the under-tank floor
regardless of which cavity it enters from — they're not tied to the
old diagonal pour-channels (now removed), they just keep the
under-tank-floor zone connected to the rest of the cavity.

### bag_pocket_support_shell

Channel-section structure framing the tank-copper-shell at +Z and −Z:
**floor + +Z wall + −Z wall**, sized 145 × 145 mm in plan-view at the
outer envelope so its wall centerlines are tangent to the
tank-copper-shell's wall centerline at the four cardinal axis points.
Same total height as the tank-copper-shell. The four corners of the
floor extend beyond the round cup's footprint; everywhere the two
floors overlap (inside the inscribed circle), they coincide and the
union produces no change.

**No +X / −X walls** — those would be coincident with the bag pockets'
tank-facing walls (also not built) and would have air on both sides
(bag cavity inside, corner-pocket air outside). The +Z and −Z walls
*do* earn their keep: they separate corner-pocket air (between this
shell's interior and the round cup's outside) from outer-pour foam
(outside this shell at +Z and −Z).

The ±Z walls each have a **central gap at x = 0**, wide enough for the
tank_copper_shell's ±Z apex opening to pass through directly into the
outer foam-gap volume. Without this gap, the corner pockets would be
sealed off from the outer foam pour and would never receive foam. At
each of the four corners of that central gap, a **curved blend cut**
trims the wall's inner edge to follow the same arc as the adjacent
curved bridging wall in `tank_copper_shell` — so the support-shell
wall doesn't terminate in a sharp right angle against the bridging
wall's curve, but blends smoothly into it.

The support-shell ±Z walls and the bag-pocket-shell walls share a
single 2-D cross-section in the code; both are produced by
`build_tank_and_bag_pocket_walls` (along with the tank cylinder and
the bridging walls), so the wall transitions at z = ±70.5 are exact
by construction rather than by OCCT face-merging. The support
shell's floor is omitted entirely — it would be 100% buried inside
the outer_shell's floor, which already spans the full assembly
footprint.

### bag_pocket_shell (one of two)

Three-walled cup attached at one ±X face of the support shell:
**floor + far (away from center) wall + +Z wall + −Z wall**. Outer
envelope **37 mm deep (along X) × 145 mm wide (along Z) × 213.4 mm
tall** so the +Z / −Z walls coincide with the support shell's +Z /
−Z walls and merge into one continuous wall after union.

**No centerward (toward-tank) wall** — same reason as the support
shell's missing ±X walls. The bag cavity is therefore open along
its centerward face into the support shell's interior (corner-pocket
region around the round cup); during operation, the bag and the
corner-pocket region are one continuous air volume bounded by the
round cup on the inside, the bag pocket's far/+Z/−Z walls and the
support shell's +Z/−Z walls on the outside, and the unioned floor
beneath.

The two far-side corners (where the far wall meets the ±Z walls) are
**filleted with a 6.5 mm inner radius** (and an 8.5 mm outer radius,
maintaining uniform wall thickness through the bend). The 6.5 mm
inner radius matches the rigid PETG reservoir's 6 mm outer fillet
plus the 0.5 mm `reservoir_clearance`, so the reservoir slides into
a snugly-mated pocket with uniform clearance around the corner.

The −X bag pocket is built as a mirror of the +X side from the same
2-D cross-section in `build_tank_and_bag_pocket_walls`.

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

Seven pass-throughs total, all carrying **1/4" OD tubing (6.35 mm)** through
holes sized at ⌀6.5 mm for a tight tube fit. Four pass-throughs each get
their own dedicated round hole; the remaining three share a single
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

**Build decision:** for the water inlet and CO2 inlet, the supply-side
tubing reduces to 1/4" OD *before* reaching the shell wall — i.e., the
transition fittings (3/8" barb-to-NPT adapter, 5/16" push-to-connect,
1/4" NPT check valves, etc.) all live on the warm side of the shell.
Inside the shell, every penetration is the same 1/4" OD. This keeps
holes small, uniform, and simple to seal during foam pour, at the cost
of the transition fittings being a few cm further from the tank.

### Shared +Z slot and copper plug stack

The +Z outer_shell wall carries three pass-throughs along a single
**Y-elongated slot** at x = 0: the two copper evaporator lines (low
and high) and the water inlet. The slot is ⌀6.5 mm wide in X
(rounded ends along Y), runs from y = 42 up to
y = `tank_copper_shell_height + 10` (10 mm of open extension past
the wall top), and is cut by `cut_slot_for_copper_and_water_inlet`
in `_foam_shell_geometry.py`. The 10 mm top extension means no sliver
of wall material remains above the slot — the three copper plugs
can slide down into the slot from above during assembly. With the
cylinder wall now open at ±Z and the support-shell ±Z walls gapped
at x = 0, the slot pierces only this one outer wall.

Pass-through Y heights (centers, measured from the **top of the
floor** — i.e. from the interior cavity's lower bound, not from y = 0):

| Pass-through | Y center above floor (mm) |
|---|---|
| Lowest copper (evaporator inlet) | 45.0 |
| Highest copper (evaporator outlet) | 164.4 |
| Water inlet | 196.4 |

(Absolute Y in the CadQuery model is +`wall_and_floor_thickness`
above these — i.e. 47.0 / 166.4 / 198.4 at the current 2 mm wall
— since the floor occupies y = 0 to y = `wall_and_floor_thickness`.)

(The highest copper drifted by −1 mm relative to the floor top when
`wall_and_floor_thickness` was bumped from 1 mm to 2 mm in commit
`8a9ffc0`; the formula
`tank_copper_shell_height − hole_shift_from_edge − wall_and_floor_thickness − above_tank_elbows_height`
has a `−wall_and_floor_thickness` term that the `+wall_thickness_compensation`
inside `tank_copper_shell_height` only half-cancels once you reframe
against the floor top. The drift was accepted.)

Three printed PETG **copper plugs** slide down into the slot from
above to seal the gaps between (and above) the three pass-throughs:

| Plug | Y span (mm) | Y end arches |
|---|---|---|
| `copper-plug-lower` | 50.75 → 162.65 | both ends |
| `copper-plug-middle` | 170.15 → 194.65 | both ends |
| `copper-plug-upper` | 202.15 → 211.40 | bottom end only (top flat) |

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
without crushing it. `lower` arches at both Y ends, `middle` arches
at both Y ends, `upper` arches at the bottom Y end only (its top is
flush with the wall top and stays flat).

After the three plugs are installed, the slot still has ~3.75 mm of
total unfilled length within the wall along Y: 1.75 mm at the
bottom of the slot, 2 mm at the top, plus six 0.5 mm clearance bands
(one above and one below each of the three tubes). All of that gets
filled by the body foam pour.

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

- Pressure vessel lowered into the cylinder, seated on the
  `tank_support_ring`.
- Copper evaporator coil hand-wound around the vessel exterior and
  bonded with 3M 425 aluminum foil tape.
- Reservoirs installed into the two bag pockets.
- Copper evaporator inlet (low), copper evaporator outlet (high),
  and water inlet routed through the shared +Z slot at their three
  Y heights.
- Three copper plugs slid down into the slot from above (through
  the 10 mm open extension past the wall top) to seal between the
  pass-throughs.
- Reservoir LLDPE lines routed through holes #1 and #2 in the
  bag_pocket_shell ±X far walls.
- Water outlet through hole #4 in the outer_shell +Z wall.
- CO2 inlet enters from above through the foam-cap-top boss +
  foam-cap-lid-top hole at (x=0, z=−68.75); the line drops to
  y=17 inside the cavity and bends 90° at a PP0308E push-to-connect
  elbow seated in the −Z support arch's Ø16 doorway.

With everything in place, liquid foam is poured **directly into the
body's open +Y top** all at once — no cap on, no down-channels.
Foam falls into the body and reaches every cavity in parallel:

- the outer foam gap (between outer_shell and bag_pocket_support_shell);
- the bag pockets (open at +Y, also open inward through the missing
  centerward wall);
- the corner pockets at ±Z (open at +Y, also connected to the outer
  foam gap via the central gap at x = 0 in each support_shell ±Z wall);
- the tank cavity inside the cylinder (open at +Y at the cylinder top,
  also accessible laterally via the ±Z apex openings over the full
  Y height).

The longest required slot traverse for the foam is the ~0.5 mm
radial gap between the coil and the cylinder's inner wall at the
±X azimuths — ~110 mm of arc to reach from the ±Z apex openings
around to the back of the coil. Shorter than the old top-down
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

Wherever two shells share a boundary, their walls are positioned so they
**overlap exactly in 3D space** — same outer face, same inner face —
rather than sitting side-by-side. After union, that boundary is one
wall's worth of material (2 mm), not two (4 mm).

This drives several dimension choices:

- The **bag_pocket_support_shell** has its half-side equal to the
  tank_copper_shell's outer radius, so the square's wall centerline meets
  the circle's wall centerline at the four cardinal points (their walls
  coincide there).
- The **bag_pocket_shell** is offset by
  `tank_copper_shell_radius + depth/2 - wall_thickness`, so its inner
  wall coincides with the bag_pocket_support_shell's +X wall.
- The **tank_support_ring**'s outer face coincides with the
  tank_copper_shell's inner wall.
- The **tank_copper_shell's curved bridging walls** meet each
  bag_pocket_support_shell ±Z wall along a 2D face (chord-end X
  range matches the cylinder's wall band exactly at z = ±60), so
  the union is a single continuous solid rather than two pieces
  sharing a 1D edge.

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

Source-level refactors of `_foam_shell_geometry.build_full_shell()`
should preserve the geometry of `foam-shell.step` exactly.  These four
scalars are the canonical regression sieve — any change to them
(beyond OCCT numerical noise at the ~1e-6 mm³ level) is a geometry
shift that needs a deliberate explanation:

| metric | value |
|---|---|
| volume   | **982382.157916 mm³** |
| bbox x   | [−134.500, +134.500] mm |
| bbox y   | [0.000, 213.400] mm |
| bbox z   | [−90.500, +90.500] mm |
| centroid | (0.000005, 90.542167, -0.044238) mm |

Captured after the CO2-inlet doorway slot was clamped to the support
arch's bottom face (fix for commit 68b8d3f, which had `slot_y_bottom
= 0` and so cut through the y=0..2 foam-shell floor below the arch).
The doorway now has its bottom flush with the floor's top face at
y=wall_and_floor_thickness, leaving the floor intact under the cut.
Composite shape on the arch's −Z outer face: upper half of the Ø16
circle at y=17..25 as a rounded pocket, plus a 16 × 15 mm rectangular
slot from y=2 (arch bottom face) up to y=17 (the bore's Y center).
Both halves still extrude +Z by 40 mm. The doorway exists because the
John Guest PP0308E 90° push-to-connect elbow (~⌀15 mm body, ~20 mm
legs) cannot be inserted along the bore axis — its perpendicular legs
snag at the bore opening, and the z<−70.5 back wall is solid. The
slot provides angled-insertion clearance from above: the elbow is
lowered through the open +Y top of the foam shell with one leg tilted
into the slot opening on the arch's bottom face, then rotated into
the round pocket.

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
