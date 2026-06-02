# PureSec 1/4" RO Push-to-Connect 90° Elbow Bulkhead (Amazon B0968K4JRN)

PureSec 1/4" reverse-osmosis push-to-connect **90° elbow bulkhead**, white polypropylene, water/RO/beverage-rated, sold as a 5-pack ([B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN)). It mounts the dry flavor line through the reservoir trough floor and turns the line laterally below the floor. Ships with no panel o-ring; the printed TPU face seals are the only fluid seal at the barrel-to-floor joint.

The part is an **L (90°) body**: one leg is a male-threaded bulkhead barrel carrying a hex locknut; the other leg is a plain push-to-connect port; an integral cast 90° elbow joins them. Both ends accept 1/4" tube. It mounts to a ⌀16 mm hole.

## Overall Form & Topology

```
            ┌── lateral PTC port ──┐   (release ring ⌀9.57 / port body ⌀12.5 / tube ⌀6.35)
            │   90° elbow body     │
        ════╪══════════════════════╛
            │  short neck
        ┌───┴───┐  FLANGE DISC  ⌀18.7 (elbow side) / ⌀21.9 (nut side)
        │█████████│ THREADS  ⌀15.5 major × ~10 long  ← locknut runs here
        │█████████│
         ╲ PTC ╱   barrel-end PTC port (release ring ⌀9.57 / tube ⌀6.35)
          ╲___╱
```

Down the threaded leg the sequence is: lateral PTC port → 90° elbow body → short neck → flange disc → threaded barrel → barrel-end PTC port. The flange disc seats against the panel face.

Separate loose piece: **hex locknut** — white PP, rounded hex corners, with internal threads through a large bore on a ~2–2.5 mm wall.

## Dimensions

| feature | value (mm) | reservoir.py constant |
|---|---|---|
| Thread major OD (max extent of threads) | 15.5 | `bulkhead_seal_id` = 16.0 (barrel + 0.5); panel hole lower bound |
| Threaded barrel length | 10.0 | |
| Thread designation | M16×1.0, straight (non-tapered), ~6–7 turns over the barrel | |
| Flange OD, dry/elbow side | 18.7 | dry-side gasket seat; panel hole upper bound |
| Flange OD, wet/nut side | 21.9 | wet-side gasket seat (nut clamping face) |
| Flange disc thickness | 2.5 | |
| Flange-top (elbow side) → elbow bottom | 19.6 | below-floor elbow clearance |
| Panel mounting hole | 16 (about 9/16 inch) | `bulkhead_panel_hole_diameter` = 16.5 (hole + 0.5) |
| Elbow lateral offset: barrel axis → lateral-PTC centerline | 15 | |
| Elbow body bounding box below the flange (X-lateral × Y × Z) | ≈28 × 16 × 16 | lateral-clearance keep-out below the floor |
| Overall height, wet-port mouth → barrel-end PTC tip | ≈45 | |

### Locknut (separate piece, shipped loose)

| feature | value (mm) | reservoir.py constant |
|---|---|---|
| Across-flats | 20.0 | `bulkhead_nut_hex_flat_to_flat` |
| Across-corners (= AF / cos30°) | ≈23.1 | `bulkhead_nut_hex_corner_to_corner`; drives the hex register pocket |
| Height (axial) | 9.0 | |
| Threaded bore (ID, = thread major) | 15.5 | |

The locknut registers against rotation by ~1.5 mm in the floor-underside hex pocket (`bulkhead_nut_hex_pocket_depth` = 1.5); the rest hangs in open bag-pocket space.

### PTC ports (both ends, shared 1/4" collet family)

| feature | value (mm) |
|---|---|
| Release ring OD | 9.57 |
| Tube bore (1/4" tube OD) | 6.35 |
| Port body OD (collet barrel) | 12.5 |
| Socket depth (tube insertion) | ~14 |

## How It Sits in the Reservoir

The part mounts **elbow-DOWN**. The threaded barrel points up through the flat trough floor; the ⌀18.7 elbow-side flange and the integral 90° elbow hang below the floor in the bag-pocket space; the hex locknut threads on from above in the cavity, registered against rotation by the shallow floor-underside hex pocket. The integral 90° elbow turns the dry line laterally (in +Y, toward the bag-pocket pass-through) below the floor, so no separate union elbow is needed. The barrel-end PTC port sits on the barrel axis; the elbow's lateral PTC is the dry route.

A TPU face seal sits on each floor face, each sized to its flange: a **wet ⌀21.0** washer under the ⌀21.9 nut face (`reservoir-bulkhead-seal-wet.step`) and a narrow **dry ⌀17.5** washer under the ⌀18.7 flange (`reservoir-bulkhead-seal-dry.step`). `bulkhead_below_floor_stack` is 24.0, so the reservoir's lowest point sits 22.6 mm above the bag-pocket floor (2.0 mm gasket + 19.6 mm elbow + boss/clearance terms). See `../../printed-parts/cold-core/reservoir/floor-and-bulkhead.md`.

## TPU Face Seals (printed washers + counterbore)

The bulkhead ships with no o-ring; the printed TPU 85A washers are the only fluid seal at the barrel-to-floor joint. The threaded barrel passes through the seal; the washer ID slips over the barrel.

| washer / counterbore feature | value (mm) | reservoir.py constant |
|---|---|---|
| Washer ID | 15.5 | `bulkhead_seal_id` |
| Washer OD | 21.3 | `bulkhead_seal_od` |
| Washer thickness (30% compression) | 2.0 | `bulkhead_seal_thickness` |
| Counterbore ⌀ | 21.5 | `bulkhead_seal_counterbore_diameter` |
| Counterbore depth | 1.4 | `bulkhead_seal_counterbore_depth` |

The wet seal is the primary: ⌀21.0 washer, ~2.5 mm-wide ring, under the ⌀21.9 nut face. The dry seal is flange-limited: the ⌀18.7 elbow flange caps it at a ⌀17.5 washer (~0.75 mm ring) on ~0.5 mm/side of PETG rim.

## Panel Clamp

The threaded barrel is ~10 mm long. The locknut needs ~4–5 mm of thread engagement, giving a clampable panel stack of ~5–6 mm. The reservoir floor is 4 mm PETG; with the ~1.4 mm-compressed TPU washer the clamped stack is ≈5.4 mm. The flange seats on the wet face, the nut on the dry face, the 4 mm floor between them.

## Foam-Shell Cavity

`_cold_core_interface.py: bulkhead_nut_cavity_diameter` = 23.5 — clearance cavity for the locknut, clearing the hex across-corners (≈23.1).
