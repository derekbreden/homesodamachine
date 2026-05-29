# PureSec 1/4" RO Push-to-Connect 90° Elbow Bulkhead (Amazon B0968K4JRN) — Photo/Estimate-Derived Geometry

## Purpose of This Document

Describes the physical geometry of the PureSec 1/4" reverse-osmosis push-to-connect **90° elbow bulkhead** ([B0968K4JRN](https://www.amazon.com/dp/B0968K4JRN) — white polypropylene, water/RO/beverage-rated, $10.99 / 5-pack) in enough detail that the next CAD agent can re-cut the reservoir's bulkhead port from the old John Guest PP1208E straight-union geometry to this part without holding it.

This part **replaces the John Guest PP1208E** that `reservoir.py` currently models. The two are NOT interchangeable in geometry: the PureSec uses a **smaller ⌀16 mm mounting hole** (vs JG ⌀17), a **single hex locknut on a male-threaded barrel** (vs JG's symmetric twin-flange union), **ships with NO panel o-ring** (a reviewer explicitly confirms "These should come with a seal or rubber washer… they will never make a watertight seal without them"), and has an **integral 90° elbow** so the dry line turns laterally with no separate union elbow.

All values here are **best-estimate**, derived from the Amazon listing text, the single listing photo (`raw-images/01-…jpg`, 1445×1500 px showing 5 bodies + 5 hex nuts), the shared 1/4" push-to-connect collet family (inherited from `../jg-bulkhead-union/extracted-results/geometry-description.md`), and the widely-cloned generic RO-bulkhead spec family (this exact body is sold under PureSec / ZAOJIAO / Malida / DIGITEN and others from one OEM design). Confidence is annotated per row. **Per the project's standing preference, these estimates are intended to drive the CAD now — do NOT wait for the physical part.** The listing photo is a cluttered marketing shot (every body overlaps a neighbour, the bodies are tilted), so absolute pixel calibration is weak; the part's **topology and proportions read clearly**, and the hard anchors below carry the absolute scale.

### Hard anchors (what the absolute scale rests on)
- **⌀16 mm mounting hole** — listing states verbatim: *"Requires 16mm(about 9/16 inch) mounting hole."* HIGH.
- **Thread major OD ≈ 15 mm, threaded length ≈ 10 mm** — generic RO-bulkhead clone-family spec (multiple supplier listings give "thread length ≈ 10mm, thread diameter ≈ 15mm, hole 15–20mm"); consistent with a 16 mm hole (≈0.5 mm/side clearance). MEDIUM-HIGH.
- **1/4" tube = ⌀6.35; PTC release ring = ⌀9.57** — inherited from the JG 1/4" collet family (same push-to-connect collet design). HIGH.
- **White polypropylene, 1/4"×1/4", NSF-class food/water material, ships without o-ring** — listing + review. HIGH.

## Measured (2026-05-29) — part in hand

Caliper measurements of the physical part now supersede the photo estimates below for these dimensions, and resolve the orientation question:

| feature | measured | drove (in `reservoir.py`) |
|---|---|---|
| thread OD (max extent of threads) | **15.5 mm** | `bulkhead_seal_id` = 16.0 (barrel + 0.5); panel hole lower bound |
| flange OD, dry/elbow side | **18.7 mm** | dry-side gasket seat; upper bound on the panel hole |
| flange OD, wet/nut side | **21.9 mm** | wet-side gasket seat (nut clamping face) |
| flange-top (elbow side) → elbow bottom | **19.6 mm** | below-floor elbow clearance |

**Orientation RESOLVED — elbow-DOWN.** The part mounts with the threaded barrel pointing UP through the floor: the ⌀18.7 elbow-side flange + the integral 90° elbow hang BELOW the floor in the bag-pocket space, and the hex nut threads on from ABOVE in the cavity. This is the OPPOSITE of the "elbow above the flange" reading the photo-only note below proposed. The reservoir CAD (`reservoir.py`, `_cold_core_interface.py`) has been re-cut to match: ⌀16 panel hole, a TPU face-seal counterbore on BOTH floor faces (one common ⌀17.5 washer — wet washer under the ⌀21.9 nut face, dry washer under the ⌀18.7 flange), and `bulkhead_below_floor_stack` raised to 24.0 so the reservoir's lowest point sits 22.6 mm above the bag-pocket floor (2.0 mm gasket + 19.6 mm elbow + boss/clearance terms).

Still photo-estimated (not yet calipered): flange thickness, nut across-flats/height, thread length + engagement margin, elbow lateral offset + body envelope, and the up/lateral PTC port details. The table and prose below remain as the photo-derived baseline for those.

## CAD-Ready Constants Table

Maps each PureSec dimension onto the `reservoir.py` constant it should drive (and a couple in `_cold_core_interface.py`). Confidence + source per row.

| reservoir.py constant | Current (JG) | New (PureSec) | Conf | Source / basis |
|---|---|---|---|---|
| `bulkhead_panel_hole_diameter` | 17.5 | **16.5** | HIGH | Listing ⌀16 mounting hole + 0.5 mm print/clearance allowance (same +0.5 logic the JG value used over its ⌀17 spec). |
| `bulkhead_nut_hex_flat_to_flat` | 19.8 | **20.0** | MEDIUM | Hex locknut across-flats; photo ratio to the ⌀15 threaded bore (wall ≈2–2.5 mm/side → AF ≈20). Nearly unchanged from JG. |
| `bulkhead_nut_hex_corner_to_corner` | (derived) | **≈23.1** | MEDIUM | = AF / cos30°; drives the hex register pocket. |
| `bulkhead_nut_hex_pocket_depth` | 1.5 | **1.5 (keep)** | HIGH | Shallow anti-rotation register only; nut hangs in open bag-pocket space. Unchanged. |
| `bulkhead_seal_id` | 16.5 | **15.5** | MEDIUM | TPU washer ID = threaded barrel OD (⌀15) + ~0.5 mm so the washer slips over the barrel; barrel passes through the seal. |
| `bulkhead_seal_od` | 21.3 | **21.3 (keep)** | MEDIUM | Stays under the ⌀22 flange so the flange seats on PETG outside the seal. ~unchanged. |
| `bulkhead_seal_thickness` | 2.0 | **2.0 (keep)** | HIGH | Project TPU face-seal convention; 30% compression. Unchanged. |
| `bulkhead_seal_counterbore_diameter` | 21.5 | **21.5 (keep)** | MEDIUM | 0.3 mm/side PETG seating ring under the ⌀22 flange (was sized for JG ⌀22.9; ⌀22 flange still seats on the rim). ~unchanged. |
| `bulkhead_seal_counterbore_depth` | 1.4 | **1.4 (keep)** | HIGH | 30% compression of the 2 mm seal. Unchanged. |
| `floor_trough_half_width_y` | 14.0 | **14.0 (keep)** | HIGH | Still hosts the ⌀21.5 counterbore + flange seat with margin; the lateral elbow runs in X, not Y, so it doesn't widen the trough. Unchanged. |
| `_cold_core_interface.py: bulkhead_nut_cavity_diameter` | 23.0 | **23.5** | MEDIUM | Foam-shell clearance cavity for the nut; must clear the hex across-corners (≈23.1) + a hair. Bump 23.0→23.5. |

### Part dimensions not yet bound to a named constant (the next agent adds these)

| Feature | Value (mm) | Conf | Source / basis |
|---|---|---|---|
| Threaded barrel OD (thread major) | **15.0** | MEDIUM-HIGH | Clone-family spec; fits ⌀16 hole. |
| Thread designation / pitch | **~M16×1.0, straight (non-tapered)** | LOW | Metric-ish straight thread that fits a 16 mm hole; pitch ≈1 mm read from ~6–7 turns over ~10 mm in the photo. Threads are NOT modelled (the panel hole is a plain ⌀16.5 bore) — designation matters only for picking the locknut pocket / barrel OD. |
| Threaded barrel length | **10.0** | MEDIUM | Clone-family spec; photo-consistent. |
| Locknut height (axial) | **9.0** | LOW-MED | Photo ratio ≈0.45 × across-flats. Hangs in open bag-pocket space; only ~1.5 mm registers in the floor pocket, so the model is insensitive to this. |
| Locknut bore (threaded ID) | **15.0** | MEDIUM | = thread major; runs on the barrel. |
| Flange disc OD (wet-side shoulder) | **22.0** | MEDIUM | Photo; the flange is a thin round disc ≈ hex across-corners, clearly **smaller** than the JG ⌀22.9 hex flange. This is the panel-seating face (seats on the wet/top trough rim through the TPU washer). |
| Flange disc thickness | **2.5** | LOW | Photo; thin disc. |
| Barrel-axis → flange face offset | flange sits at the **top** of the threads, directly under the elbow neck | MEDIUM | Photo: order down the vertical leg is elbow → short neck → flange disc → threads → barrel-end PTC port. The wet face of the flange is the panel seat. |
| Wet/up PTC port: release-ring OD | **9.57** | HIGH | Shared JG 1/4" collet family. |
| Wet/up PTC port: tube bore | **6.35** | HIGH | 1/4" tube OD. |
| PTC port body OD (collet barrel) | **12.5** | MEDIUM | Photo column-scan of the lateral port body. |
| PTC port socket depth (tube insertion) | **~14** | MEDIUM | Typical 1/4" PTC collet socket depth (JG-family). |
| **90° elbow** lateral offset: barrel axis → lateral-PTC centerline | **15** | LOW-MED | Photo ratio ≈1 × thread OD. This is the key elbow clearance number below the floor. |
| Elbow body bounding box below the flange (X-lateral × Y × Z) | **≈28 × 16 × 16** | LOW | Photo bounding-box estimate of the cast 90° body + the lateral collet barrel. Use as the lateral-clearance keep-out volume below the floor. |
| Overall height, wet-port mouth (above floor) → barrel-end PTC tip (below floor) | **≈45** | LOW | Sum of leg lengths from the photo; lower confidence, not load-bearing for the cut. |

## Overall Form & Topology (this is the part that changed most vs the JG)

The part is an **L (90°) body**, NOT a symmetric in-line union. One leg is the **male-threaded bulkhead barrel** that carries the **hex locknut**; the other leg is a **plain push-to-connect port**; an integral cast 90° elbow joins them. Both ends accept 1/4" tube ("push connects on both ends"), so down the threaded leg the sequence is:

```
            ┌── lateral PTC port ──┐   (release ring ⌀9.57 / port body ⌀12.5 / tube ⌀6.35)
            │   90° elbow body     │
        ════╪══════════════════════╛
            │  short neck
        ┌───┴───┐  FLANGE DISC  ⌀22 × ~2.5    ← wet-side panel-seating face
        │█████████│ THREADS  ⌀15 major × ~10 long  ← locknut runs here
        │█████████│
         ╲ PTC ╱   barrel-end PTC port (release ring ⌀9.57 / tube ⌀6.35)
          ╲___╱
```

Separate loose piece: **hex locknut** — across-flats ≈20, across-corners ≈23, height ≈9, threaded bore ≈15, white PP, rounded hex corners (photo shows the internal threads through a large bore with a ~2–2.5 mm wall).

### How it sits in the reservoir (from `../../printed-parts/cold-core/reservoir/floor-and-bulkhead.md`)
The **threaded barrel passes vertically down through the flat trough floor**; the **flange disc seats on the wet (top) trough face through the printed TPU washer**; the **hex locknut threads on from below** in the open bag-pocket cavity, registered against rotation by the shallow floor-underside hex pocket. The **integral 90° elbow turns the line laterally (in X, toward the bag-pocket pass-through) below/at the floor** so no separate union elbow is needed. The barrel-end PTC port (the "up"/wet collet) sits on the barrel axis; the elbow's lateral PTC is the dry route.

> **Orientation note — RESOLVED on the physical part (see "Measured" above):** the part mounts **elbow-DOWN**. The threaded barrel points UP through the floor; the ⌀18.7 elbow-side flange + the integral 90° elbow hang BELOW the floor in the bag-pocket space; the hex nut threads on from ABOVE in the cavity. The lateral PTC on the elbow turns the dry line in +Y toward the bag-pocket pass-through, below the floor. This is the OPPOSITE of the photo-only "elbow above the flange" guess that was originally written here. The reservoir CAD now models it as elbow-down with a TPU washer on each floor face.

## Dimensional Profile — vertical leg, top → bottom

1. **Lateral PTC port** (elbow leg): release ring ⌀9.57 (HIGH), tube bore ⌀6.35 (HIGH), port body ⌀12.5 (MEDIUM), socket depth ~14 (MEDIUM). Offset ≈15 mm laterally (+X) from the barrel axis (LOW-MED).
2. **90° elbow body**: cast right-angle, bounding box ≈28 × 16 × 16 mm (LOW). Keep-out volume below/around the floor.
3. **Flange disc**: ⌀22 × ~2.5 mm (MEDIUM / LOW). Wet-side panel-seating face — seats on the trough-floor PETG rim outside the seal counterbore.
4. **Threaded barrel**: ⌀15 major × ~10 mm long (MEDIUM-HIGH / MEDIUM). Passes through the ⌀16.5 panel hole; locknut runs on it from below.
5. **Barrel-end PTC port**: release ring ⌀9.57, tube ⌀6.35 (HIGH). The "wet/up" collet in the install.

## Locknut (separate piece, shipped loose)

- **Across-flats ≈20 mm** (MEDIUM) · **across-corners ≈23.1 mm** (MEDIUM, = AF/cos30°) · **height ≈9 mm** (LOW-MED) · **threaded bore ≈15 mm** (MEDIUM) · white PP, rounded hex corners.
- Only ~1.5 mm registers in the floor-underside hex pocket; the rest hangs in open bag-pocket space, so the model is insensitive to the height estimate.

## Max Panel Thickness It Clamps

Threaded barrel ≈10 mm long. The locknut needs ~4–5 mm of thread engagement, so the **clampable panel stack ≈ 5–6 mm** (MEDIUM). The reservoir floor is 4 mm PETG; adding the ~1.4 mm-compressed TPU washer puts the clamped stack at ≈5.4 mm — **right at the limit**. The flange seats on the wet face, the nut on the dry face, the 4 mm floor between them. This is workable but has little margin; if a print test shows the nut bottoming out before clamping, thin the seal-counterbore rim or accept slightly less thread engagement. **Flag: confirm on the physical part.**

## The TPU Face Seal We Supply (printed washer + its counterbore)

The PureSec ships with **no o-ring**, so the printed TPU 85A washer is the only fluid seal at the barrel-to-floor joint.

| Washer / counterbore feature | Value (mm) | drives | Conf |
|---|---|---|---|
| Washer ID | 15.5 | `bulkhead_seal_id` | MEDIUM — barrel ⌀15 + 0.5 slip |
| Washer OD | 21.3 | `bulkhead_seal_od` | MEDIUM — under ⌀22 flange |
| Washer thickness | 2.0 | `bulkhead_seal_thickness` | HIGH — project convention |
| Counterbore ⌀ | 21.5 | `bulkhead_seal_counterbore_diameter` | MEDIUM — 0.3/side seating ring |
| Counterbore depth | 1.4 | `bulkhead_seal_counterbore_depth` | HIGH — 30% compression |

Net: the seal seat barely changes from the JG model — the JG already used a ~⌀21.5 counterbore under its ⌀22.9 flange, and the PureSec's ⌀22 flange seats on the same rim. The only seal change is **ID 16.5 → 15.5** (the PureSec threaded barrel ⌀15 is narrower than the JG body at the seal plane, so the washer hugs it more tightly).

## Adjustments for the Next CAD Agent

Work in `reservoir.py`, the `Outlet bulkhead port + V floor` block (≈ lines 245–321) and the bulkhead-port cuts inside `build_reservoir_body` (≈ lines 726–768). Plus one value in `_cold_core_interface.py`.

**Change these constants (JG → PureSec):**
1. `bulkhead_panel_hole_diameter`: **17.5 → 16.5** (⌀16 listing hole + 0.5 mm). Update the inline comment + the `BULKHEAD_PANEL_HOLE_D` docgen tag (used in a few comments) to 16.5. The straight-down `panel_hole` cut already does the right thing at the new ⌀.
2. `bulkhead_nut_hex_flat_to_flat`: **19.8 → 20.0** (across-corners auto-updates to ≈23.1 via the existing `/cos30°` line; the `nut_hex_profile` regenerates automatically).
3. `bulkhead_seal_id`: **16.5 → 15.5** (washer hugs the ⌀15 barrel). Update its inline comment (it references the JG body OD at the seal location).
4. `_cold_core_interface.py` `bulkhead_nut_cavity_diameter`: **23.0 → 23.5** (clear the PureSec hex across-corners ≈23.1).

**Add for the integral 90° elbow (new — the JG had none):**
5. Add a **lateral keep-out / clearance volume below-and-around the trough floor** for the elbow body + lateral collet: a box roughly **28 (X) × 16 (Y) × 16 (Z)** centred on the barrel axis and extending ~15 mm in the lateral (+X, toward the bag-pocket pass-through) direction, plus the lateral PTC port stub (⌀12.5 body, ⌀9.57 ring) reaching to the pass-through. This replaces the JG note that "a separate PP0308E 90° elbow (not modelled) turns the line." Verify the bag-pocket +Y pass-through (`reservoir_bulkhead_port_y` in `_cold_core_interface.py`) lines up with where the elbow's lateral port points; the elbow turns in **X** in this part, so check the pass-through axis vs the elbow axis and rotate the modelled part about Z if needed so its lateral port aims at the pass-through.
6. Define explicit elbow/port constants alongside the existing ones, e.g. `bulkhead_elbow_lateral_offset = 15.0`, `bulkhead_elbow_envelope_x/y/z`, `bulkhead_ptc_port_body_diameter = 12.5`, `bulkhead_ptc_release_ring_diameter = 9.57`, `bulkhead_ptc_tube_diameter = 6.35` — mirroring how the JG doc fed the chamber/port dims. Mark them MEDIUM/LOW in comments.

**Keep unchanged (verified still correct for PureSec):**
- `bulkhead_nut_hex_pocket_depth` (1.5), `bulkhead_seal_od` (21.3), `bulkhead_seal_thickness` (2.0), `bulkhead_seal_counterbore_diameter` (21.5), `bulkhead_seal_counterbore_depth` (1.4), `floor_trough_half_width_y` (14.0), `floor_slope_rise` (6.0).
- The V-floor sweep, the trough, the wet-side counterbore cut, the nut-hex-pocket cut mechanism, the seal washer geometry — all stay; only the diameters above shift.
- The vertical-through-floor mounting scheme itself (barrel down, flange on wet face, nut from below) is unchanged.

**Also update the prose comment** at the top of the bulkhead block (≈ lines 245–272) that currently names the *John Guest PP1208E* (Amazon B00JYFU8MM, NSF 51/61) and a *separate JG PP0308E 90° elbow*: replace with the PureSec B0968K4JRN, ⌀16 hole, integral 90° elbow, ⌀22 flange, ⌀15 thread, ships-without-o-ring.

## Sources

- **PureSec B0968K4JRN Amazon listing** (read live via Chrome MCP, 2026-05-28): title *"PureSec 1/4 Bulkhead Fitting 90 degree Elbow…"*, material Polypropylene, color White, 5-pack $10.99; *"Requires 16mm (about 9/16 inch) mounting hole"*; description *"basically a bolt and nut, with a hole thru the bolt… push connects on both ends"*; review *"No seals… they will never make a watertight seal without them"*. — HIGH for hole/material/no-seal/topology.
- **Listing photo** `raw-images/01-amazon-B0968K4JRN-5pack-bodies-and-nuts.jpg` (1500 px hi-res, the only product image). Crops `02-single-body-…png` (barrel/flange/elbow/port proportions) and `03-hex-locknut-thru-bore.png` (nut across-flats : bore ratio, wall thickness). — MEDIUM for proportions; weak for absolute scale (cluttered, overlapping, tilted bodies).
- **Generic RO-bulkhead clone-family spec** (multiple supplier listings for the same OEM body — PureSec / ZAOJIAO / Malida / DIGITEN / Bulk Reef Supply 1/4" push-connect bulkhead): "thread length ≈10 mm, thread diameter ≈15 mm, hole 15–20 mm"; BRS confirms "comes with a plastic nut… does not have a gasket… designed for above-water applications." — MEDIUM-HIGH for thread OD/length, no-gasket.
- **Shared 1/4" PTC collet family** — `../jg-bulkhead-union/extracted-results/geometry-description.md`: release ring ⌀9.57 (caliper-measured on PP0408W), tube ⌀6.35. — HIGH (inherited).

## Confirmed vs Best-Estimate (explicit call-out)

**Confirmed (HIGH):** ⌀16 mounting hole; white PP / water-food material; ships with NO o-ring; both ends 1/4" push-to-connect; integral 90° elbow; release ring ⌀9.57; tube ⌀6.35.

**Best-estimate, drive-the-CAD-now (MEDIUM):** thread OD ⌀15; threaded length 10; locknut across-flats 20 / across-corners 23.1; flange OD 22; PTC port body OD 12.5; nut-cavity bump to 23.5; seal ID 15.5.

**Best-estimate, lower-confidence (LOW / LOW-MED) — flag in CAD comments:** flange thickness 2.5; locknut height 9; thread pitch / designation (M16×1.0 assumed); elbow lateral offset 15; elbow bounding box 28×16×16; overall part height ~45; max clampable panel 5–6 mm.

## Remaining Unknowns / TODO

- [x] **Thread OD, both flange ODs, elbow standoff, up-vs-lateral orientation** — caliper-measured 2026-05-29 (see "Measured" above). Orientation resolved to elbow-DOWN.
- [ ] **Verify nut thread engagement (now tighter, and load-bearing for the clamp).** Elbow-down sandwiches the floor between the below flange and the wet-side nut, so the nut clamps a ~5.4 mm seal-boss stack (wet counterbore 1.4 + mid-rim 2.6 + dry counterbore 1.4). With ~10 mm of estimated thread that leaves ~4.6 mm of nut engagement above the trough — **measure the thread length on the part and confirm the nut bites before bottoming out**, since this clamp is the seal force on both gaskets.
- [ ] **Confirm the dry-side seal land.** The ⌀18.7 elbow flange seats on only ~0.5 mm/side of PETG rim outside the ⌀17.7 counterbore, and the common ⌀17.5 washer is a narrow ~0.75 mm-wide ring. If the dry seal weeps, widen the wet-side washer separately (the wet ⌀21.9 face has 2.1 mm/side of rim to spare) and treat the wet seal as primary.
- [ ] **Still photo-estimated:** flange thickness, nut across-flats/height, thread pitch/designation, elbow lateral offset + body envelope. None block the panel-hole / seal cuts.
- [ ] **Elbow-to-pass-through alignment**: confirm `reservoir_bulkhead_port_y`/pass-through geometry receives the elbow's lateral (+Y) port.
- [ ] If a dimensioned drawing surfaces, drop images into `raw-images/` and re-derive the remaining MEDIUM/LOW rows at HIGH confidence.
