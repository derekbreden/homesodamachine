# Foam-bag shell

3D-printed PETG enclosure for the soda machine's "cold core" — the
back-of-enclosure subsystem that holds the carbonator pressure vessel, the
copper evaporator coil wrapped around it, and two flavor bladders in
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
  outward) × 225 mm tall**. Two bags per cold core.
- **Evaporator coil** — 1/4" OD × 0.187" ID × 0.031" wall ACR copper,
  hand-wound helically around the vessel exterior, bonded with 3M 425
  aluminum foil tape. ~6.35 mm radial occupancy plus tolerance — budgeted
  at 7 mm (`copper_coil_buffer_radius`).
- **Tank-port fittings** — 1/4" NPT 90° elbows on every port, turning the
  line laterally. ~30 mm vertical envelope per elbow above and below the
  tank.

## Shells

The geometry is built up from open-topped shells, each printed as a
separate solid and unioned together. **All shells use 1 mm wall and floor
thickness** (`wall_and_floor_thickness`).

### tank_copper_shell

Round cup that contains the pressure vessel and the copper coil zone
wrapped around it. Outer radius **70.5 mm** (tank radius 63.5 + coil-zone
buffer 7). Total height **212.4 mm** (tank height 152.4 + 30 mm above +
30 mm below for the 90° elbow space).

Four **foam-pour down-channels** are unioned to the outside of the cup
at azimuths 45°/135°/225°/315°, running the full cavity height. Each
channel is an 8 mm radial × 10 mm tangential rectangular slot whose
center sits on the shell's OD, so half the slot overlaps the wall
(becomes a rectangular flute on the inside after shelling) and half
protrudes outward into the corner pocket between this shell and
`bag_pocket_support_shell`. On the inside, the channels locally widen
the radial foam gap from the design 7 mm to ~11 mm at the four
diagonal lines.

A cylindrical-lobe variant lives in the project's history; the
rectangular variant trades smooth merge curves and sharp-internal-
corner-free walls for uniform circumferential width along the channel's
full depth (vs. the lobe's tapered throat → max → throat profile).
Both reach R = 75.5 mm at the diagonal and add ~4 mm of effective
cavity depth at the channel azimuth.

The channels exist because the helically-wrapped 1/4" ACR copper
evaporator coil leaves only ~0.5 mm of radial slot on each flank —
borderline for liquid pour-in-place foam to traverse top-to-bottom
inside the foam's ~45 s cream window, and lot-variation-sensitive
(FSi/Fibre Glast Side B viscosity is specced 400–2000 cP, a 5×
range). The channels give the liquid foam a clear path to the cavity
floor; the coil-side slots then fill from below by the foam's
4–6 psi closed-rise expansion pressure.

The channel azimuths coincide with the `tank_support_wedge`'s four
30°-wide slots (also at 45° + 90·i), so foam falls down a channel
and continues straight through a wedge slot to the under-tank floor
with no wedge change.

### tank_support_wedge

Annular wedge ring sitting inside the lower portion of the
tank-copper-shell, holding the tank up by its outer rim. The wedge's
outer face is coincident with the tank-copper-shell's inner wall (at
R = 69.5).

The top face of the wedge is a flat annular plateau, **15 mm wide**
(R = 54.5 to R = 69.5), where the tank's outer rim rests. The inside of
the wedge has a 45° slope from (R = 69.5, y = 1) up and inward to
(R = 54.5, y = 16), then continues straight up as a vertical inner face
to the plateau at y = 31.

Inboard of R = 54.5 (and below the plateau) is open volume — so the
tank's bottom-plate fittings have unobstructed downward space, and pour
foam fills around them.

### bag_pocket_support_shell

Channel-section structure framing the tank-copper-shell at +Z and −Z:
**floor + +Z wall + −Z wall**, sized 143 × 143 mm in plan-view at the
outer envelope so its wall centerlines are tangent to the tank-copper-
shell's wall centerline at the four cardinal axis points. Same total
height as the tank-copper-shell. The four corners of the floor extend
beyond the round cup's footprint; everywhere the two floors overlap
(inside the inscribed circle), they coincide and the union produces
no change.

**No +X / −X walls** — those would be coincident with the bag pockets'
tank-facing walls (also not built) and would have air on both sides
(bag cavity inside, corner-pocket air outside). The +Z and −Z walls
*do* earn their keep: they separate corner-pocket air (between this
shell's interior and the round cup's outside) from outer-pour foam
(outside this shell at +Z and −Z). The function `build_bag_pocket_
support_shell` constructs floor and the two walls explicitly rather
than building a closed cup and cutting the unneeded faces back off.

### bag_pocket_shell (one of two)

Three-walled cup attached at one ±X face of the support shell:
**floor + far (away from center) wall + +Z wall + −Z wall**. Outer
envelope **35 mm deep (along X) × 143 mm wide (along Z) × 212.4 mm
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

A second `bag_pocket_shell` mirrored on the −X side is built the same
way (`build_a_bag_pocket_shell(side=-1)`) and unioned alongside the
first.

### foam_cap and foam_cap_lid

The `foam_cap` is a 16 mm-tall cup matching the outer shell's
footprint, printed twice — one sits on top of the assembly (flipped,
open side mating with the outer shell's top edge) and one on the
bottom (in normal orientation, open side mating with the outer
shell's bottom edge). The cap interior receives the outer-pour foam
through pour and vent holes in the lid above.

The `foam_cap_lid` is a flat 1 mm plate matching the same outer
footprint, sitting on top of the top cap during the foam pour. It
has the pour hole (Ø 10 mm) and two vent holes (Ø 6 mm).

Both the cap and the lid have **six 8 × 8 mm boss / clearance-hole
positions** — four at the corners (inherited from the earlier dowel-
pin layout) and two at the mid-points of the long edges (along
+Z and −Z, at x = 0). Each position passes a clearance hole for an
M3 cap screw all the way through the part. See "Cap-to-outer-shell
joinery" below.

### foam_cap_gasket

A TPU 90A gasket, printed twice — one between each cap and its
mating face on the outer_shell. 245 × 177 mm outer envelope, 2 mm
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
from ~245 mm corner-to-corner along the long axis to ~120 mm, which
matters for a TPU gasket compressed only at discrete points.

## Penetrations

Seven holes total, all sized for **1/4" OD tubing (6.35 mm)** plus a small
clearance for fit and seal:

| # | Hole | Carries |
|---|---|---|
| 1, 2 | Bag-pocket flavor line (×2) | 1/4" OD soft tubing from each bag's cap to its peristaltic pump |
| 3, 4 | Evaporator coil suction & liquid (×2) | 1/4" OD copper refrigerant lines to/from the compressor |
| 5 | Water inlet | 1/4" OD line from the diaphragm pump |
| 6 | CO2 inlet | 1/4" OD line from the regulator |
| 7 | Carbonated water outlet | 1/4" OD line to the dispense faucet |

**Build decision:** for the water inlet and CO2 inlet, the supply-side
tubing reduces to 1/4" OD *before* reaching the shell wall — i.e., the
transition fittings (3/8" barb-to-NPT adapter, 5/16" push-to-connect,
1/4" NPT check valves, etc.) all live on the warm side of the shell.
Inside the shell, every penetration is the same 1/4" OD. This keeps
holes small, uniform, and simple to seal during foam pour, at the cost
of the transition fittings being a few cm further from the tank.

## Coincident-wall principle

Wherever two shells share a boundary, their walls are positioned so they
**overlap exactly in 3D space** — same outer face, same inner face —
rather than sitting side-by-side. After union, that boundary is one
wall's worth of material (1 mm), not two (2 mm).

This drives several dimension choices:

- The **bag_pocket_support_shell** has its half-side equal to the
  tank_copper_shell's outer radius, so the square's wall centerline meets
  the circle's wall centerline at the four cardinal points (their walls
  coincide there).
- The **bag_pocket_shell** is offset by
  `tank_copper_shell_radius + depth/2 - wall_thickness`, so its inner
  wall coincides with the bag_pocket_support_shell's +X wall.
- The **tank_support_wedge**'s outer face coincides with the
  tank_copper_shell's inner wall.

## Print settings

Current slicer save: [`foam-bag-shell.3mf`](foam-bag-shell.3mf) (Bambu
Studio 02.06.01.55). Plate contains three objects sliced together:
`foam-bag-shell` + `copper-inlet-plug` + `copper-outlet-plug`. The
`foam-cap` and `foam-cap-lid` are printed on a separate plate.

### Chamber exhaust fan (the key fix)

Large thin-walled PETG parts on the Bambu H2C warp when the chamber
heat-soaks. The fix is to run the **chamber exhaust fan** during the
print — added to the **filament start g-code** in Bambu Studio:

```gcode
M106 P2 S153
```

`P2` selects the chamber exhaust fan (P0 = part-cooling, P1 = aux);
`S153` is ~60 % of 255. Validated on the 2 mm-wall print after 1 mm
full-size attempts failed from heat soak; with the fan on, the
1 mm walls succeed (see commit `24605cb`).

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
- **Chamber:** passive (`chamber_temperatures: 0` — fan-cooled by the
  M106 P2 S153 above)
- **Flow ratio:** 0.97
- **Max volumetric speed:** 21 mm³/s (28 on the second nozzle slot)
- **Part-cooling fan:** max 40 %, min 20 %, overhang 90 % at ≥ 10 %
  overhang, closed first 3 layers
- **Auxiliary fan (P1):** on

## Reference

- [`../../flavor/pump-case/generate_step_cadquery.py`](../../flavor/pump-case/generate_step_cadquery.py)
  — gold standard for the PETG-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).
