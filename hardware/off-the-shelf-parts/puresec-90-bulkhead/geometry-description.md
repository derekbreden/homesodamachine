# PureSec 1/4" RO Push-to-Connect 90° Elbow Bulkhead (Amazon B0968K4JRN)

PureSec 1/4" reverse-osmosis push-to-connect **90° elbow bulkhead**, white polypropylene, water/RO/beverage-rated, sold as a 5-pack ([B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN)). It mounts the dry flavor line through the reservoir trough floor and turns the line laterally below the floor. Ships with no panel o-ring; a purchased silicone washer (wet/top face) and a printed TPU washer (dry/under face) are the only fluid seal at the barrel-to-floor joint.

The part is an **L (90°) body**: one leg is a male-threaded bulkhead barrel carrying a hex locknut; the other leg is a plain push-to-connect port; an integral cast 90° elbow joins them. Both ends accept 1/4" tube. It mounts to a ⌀[16 mm](BULKHEAD_PANEL_HOLE_D) hole.

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
| Thread major OD (max extent of threads) | 15.5 | `bulkhead_seal_id` = [16 mm](BULKHEAD_SEAL_ID) (barrel + 0.5); panel hole lower bound |
| Threaded barrel length | 10.0 | |
| Thread designation | M16×1.0, straight (non-tapered), ~6–7 turns over the barrel | |
| Flange OD, dry/elbow side | [18.7 mm](BULKHEAD_DRY_FLANGE_OD) | dry-side gasket seat; panel hole upper bound |
| Flange OD, wet/nut side | [21.9 mm](BULKHEAD_WET_NUT_OD) | wet-side gasket seat (nut clamping face) |
| Flange disc thickness | 2.5 | |
| Flange-top (elbow side) → elbow bottom | 19.6 | below-floor elbow clearance |
| Panel mounting hole | [16 mm](BULKHEAD_PANEL_HOLE_D) (about 9/16 inch) | `bulkhead_panel_hole_diameter`; barrel + 0.5 slip |
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

The part mounts **elbow-DOWN**. The threaded barrel points up through the flat trough floor; the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) elbow-side flange and the integral 90° elbow hang below the floor in the bag-pocket space; the hex locknut threads on from above in the cavity, registered against rotation by the shallow floor-underside hex pocket. The integral 90° elbow turns the dry line laterally (in +Y, toward the bag-pocket pass-through) below the floor, so no separate union elbow is needed. The barrel-end PTC port sits on the barrel axis; the elbow's lateral PTC is the dry route.

A face seal sits on each floor face, each sized to its clamping face: a **purchased silicone wet ⌀[24 mm](BULKHEAD_SEAL_WET_OD)** washer under the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut face, and a printed-TPU **dry ⌀[18.5 mm](BULKHEAD_SEAL_DRY_OD)** washer under the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) flange (`reservoir-bulkhead-seal-dry.step`). The below-floor stack (elbow + clearance) is detailed in `../../printed-parts/cold-core/reservoir/floor-and-bulkhead.md`.

## Face Seals (purchased silicone wet + printed TPU dry, in counterbores)

The bulkhead ships with no o-ring; the face washers are the only fluid seal at the barrel-to-floor joint — a purchased silicone washer (uxcell B07D23JJMR) on the wet (top) face, a printed TPU 85A washer on the dry (under) face. The threaded barrel passes through each seal; the washer ID slips over the barrel.

| washer / counterbore feature | value (mm) | reservoir.py constant |
|---|---|---|
| Washer ID | [16 mm](BULKHEAD_SEAL_ID) | `bulkhead_seal_id` |
| Washer OD (wet) | [24 mm](BULKHEAD_SEAL_WET_OD) | `bulkhead_seal_wet_od` |
| Washer OD (dry) | [18.5 mm](BULKHEAD_SEAL_DRY_OD) | `bulkhead_seal_dry_od` |
| Washer thickness — dry/printed ([30%](BULKHEAD_SEAL_COMPRESSION) squeeze; the purchased wet washer is 3 mm) | [2 mm](BULKHEAD_SEAL_THICKNESS) | `bulkhead_seal_thickness` |
| Counterbore ⌀ (wet) | [24.3 mm](BULKHEAD_SEAL_WET_CB_D) | `bulkhead_seal_wet_counterbore_diameter` |
| Counterbore ⌀ (dry) | [18.5 mm](BULKHEAD_SEAL_DRY_CB_D) | `bulkhead_seal_dry_counterbore_diameter` |
| Counterbore depth | [1.4 mm](BULKHEAD_SEAL_CB_DEPTH) | `bulkhead_seal_counterbore_depth` |

The wet seal is the primary: a purchased silicone ⌀[24 mm](BULKHEAD_SEAL_WET_OD) × 3 mm washer under the ⌀[21.9 mm](BULKHEAD_WET_NUT_OD) nut face — its OD is wider than the nut, so the nut compresses it inside the counterbore. The dry seal is a printed TPU 85A washer, flange-limited: the ⌀[18.7 mm](BULKHEAD_DRY_FLANGE_OD) elbow flange caps it at a ⌀[18.5 mm](BULKHEAD_SEAL_DRY_OD) ring on a narrow PETG rim.

## Panel Clamp

The threaded barrel is ~10 mm long. The locknut needs ~4–5 mm of thread engagement, giving a clampable panel stack of ~5–6 mm. The reservoir floor is [3 mm](RESERVOIR_WALL_T) PETG; the clamped stack is that floor plus the seal washer recessed in its [1.4 mm](BULKHEAD_SEAL_CB_DEPTH)-deep counterbore. The nut compresses the wet (silicone) washer, the flange the dry (TPU) washer, the [3 mm](RESERVOIR_WALL_T) floor between them.

## Foam-Shell Cavity

`_cold_core_interface.py: bulkhead_nut_cavity_diameter` = 23.5 — clearance cavity for the locknut, clearing the hex across-corners (≈23.1).

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/cold-core/reservoir/reservoir.py`
