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

## Reference

- [`../pump-case/generate_step_cadquery.py`](../pump-case/generate_step_cadquery.py)
  — gold standard for the PETG-enclosure pattern in this repo.

The cadquery venv lives at `tools/cad-venv/bin/python` (cadquery is not
on system Python).
