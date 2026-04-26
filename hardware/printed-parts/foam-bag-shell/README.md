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

Square cup encompassing the tank-copper-shell. **141 × 141 mm** in
plan-view, sized so that the square's wall centerlines are tangent to the
tank-copper-shell's wall centerline at the four cardinal axis points.
Same total height as the tank-copper-shell. The four corners of the
square's floor extend beyond the round cup's footprint; everywhere the
two floors overlap (inside the inscribed circle), they coincide and the
union produces no change.

### bag_pocket_shell (one of two)

Rectangular cup attached to one side of the bag_pocket_support_shell.
**35 mm deep (along X) × 125 mm wide (along Z) × 212.4 mm tall**. The
pocket's tank-facing wall is coincident with the bag_pocket_support_shell's
+X wall.

A second `bag_pocket_shell` mirrored on the −X side is planned but not
yet in the code.

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
