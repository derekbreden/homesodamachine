# Compressor Shroud

Sheet-metal shroud over the compressor terminal block area, providing a non-combustible enclosure around the only ignition-risk parts of the AC system in the R-600a refrigerant compartment. SendCutSend laser-cut + bent.

## Why this part exists

The appliance uses R-600a (isobutane), a flammable hydrocarbon refrigerant. The shroud exists for one reason: making the appliance genuinely safe in the kitchens of friends, family, and customers (the first 30+ units go to people the founder knows directly — see `marketing/target-market.md` "rings of trust"). UL 60335-2-89 (hydrocarbon appliance safety) is the engineering standard that codifies what safe handling of this refrigerant class actually requires, and the design follows it because the standard is right about safety — not as a compliance posture (per [`../../../business/regulatory.md`](../../../business/regulatory.md), no third-party listing is being pursued).

The standard requires a fire-rated enclosure around the ignition sources in the refrigerant compartment. The compressor's hermetic can already encloses the motor windings and oil sump. The remaining ignition-risk surfaces — exposed outside the can — are:

- The **terminal block** on top of the compressor (where the AC leads attach to the motor pins)
- The clip-on **PTC start relay + overload protector** module that bolts directly to those terminals (operates at ~140–150 °C in normal use, far hotter than anything else in the system)

These two items are intrinsically co-located and cannot move; they must be enclosed where they sit. The Teyleten relay #1 that switches the compressor's AC is **not** inside the shroud — it's an arc source that does NOT have to be in the protected zone, so it lives on the electronics shelf instead. See [`../../wiring/power.mmd`](../../wiring/power.mmd) for the placement rationale.

The condenser fan motor also runs on AC but sits on the side wall of the enclosure (on the side-to-side intake → condenser → exhaust airflow path, away from the cold core), is a low-ignition-risk small induction motor, and would be defeated by being inside the shroud (it needs to move air across the condenser). It is **not** enclosed.

## What's inside vs outside the shroud

**Inside:**
- Compressor body
- Compressor terminal block + clip-on PTC start relay/overload module
- The wire stub from the terminals to the AC pass-through grommet (a few cm of 18 AWG)
- Refrigerant line stubs (suction, discharge, process tube) where they exit the compressor body — these pass through the shroud floor / bottom edge as needed; the shroud is open-bottom so the stubs aren't penetrations, just clearance

**Outside:**
- Teyleten relay #1 (electronics shelf)
- Condenser fan motor (side of enclosure, on the side-to-side airflow path)
- AC distribution block (electronics shelf)
- Everything else

## Shape concept

A **5-sided open-bottom box** that drops over the compressor from above. Top panel + 4 side walls. Open bottom because the compressor sits on its M5 mounting feet on the printed enclosure floor (no separate metal floor pan — see [`../../future.md`](../../future.md) "Other metal candidates considered, decided against"), and the refrigerant tubes need to exit downward / sideways anyway.

Construction approach: a single SendCutSend part, bent on 4 sides. Alternative is a 2-piece U-channel + back-wall design with 2-3 bends and screw assembly — TBD when the first build's compressor measurements are in hand.

## Dimensions

**Status: TBD.** The donor compressor (HD48Y11 from the generic ice-maker unit, or the equivalent in the Frigidaire EFIC117-SS) needs to be measured before final dimensions are committed. Per [`../../harvested/ice-maker/README.md`](../../harvested/ice-maker/README.md) "Open items": *Physical dimensions of compressor + condenser pair, for enclosure layout* is still pending.

Working assumptions (revise after measurement):

- Compressor body: ~95 mm OD × ~110 mm tall (rough estimate for a 100 W-class hermetic)
- Terminal block + PTC module envelope: ~50 mm wide × ~40 mm tall × ~30 mm radial standoff above the terminal pins
- Internal clearance to terminal block: ≥10 mm on all sides for service access and to keep the PTC's ~150 °C surface off the metal wall

Working envelope:

- Outer dimensions: ~130 mm (X, depth into appliance) × ~130 mm (Y, width across appliance) × ~100 mm (Z, vertical height above floor)
- Wall thickness: 0.059" (1.50 mm) — see "Material" below
- Internal headroom over compressor: ≥20 mm
- Side wall flange height: 90–100 mm (well within SendCutSend's "max 4-sided box flange height with hardware = 3″" ≈ 76 mm — *if we use a 4-sided box, this will need to be split into a U-channel + separate back wall, or shortened*)

The flange-height constraint (3″ for 4-sided box bends) is the design driver for whether this is one part or two. Decide after measurement.

## Material

**0.059" G90 hot-dipped galvanized steel.**

Rationale:

- **Non-combustible.** Trivially satisfies UL 60335-2-89's fire-enclosure requirement around the terminal block. No flame-rating documentation to source, no testing to commission.
- **Appliance-standard.** G90 is the universal sheet metal in countertop ice makers, dishwashers, microwaves, fridge bodies. The galvanized coating handles humid-kitchen ambient over the 10-year design life without a separate finish.
- **0.059" thickness** is the SendCutSend offering closest to typical OEM appliance-shroud gauge (16-gauge nominal). Thinner (0.030″/.036″/.048″) would work mechanically but is more prone to vibration noise and feels light. Thicker (0.074″) adds cost and weight with no benefit at this duty.
- **Cost:** ~$5–10/part at qty 5–10 from SendCutSend. Trivially small line item.

Alternatives considered and rejected:

- **5052 H32 aluminum** — lighter, available in same thickness range, but the conductive thermal mass of galvanized steel is helpful (absorbs heat from the PTC) and aluminum costs more. No structural reason to pick it here.
- **304 stainless steel** — overkill on corrosion resistance for an internal hidden part. ~3× the cost of galvanized for no benefit a kitchen-cabinet interior cares about.

## Penetrations

| # | Hole | Purpose |
|---|---|---|
| 1 | Ø ~12 mm grommet hole, one side wall | AC cable pass-through (3-conductor: switched H + N + chassis G, 18 AWG bundle) from Teyleten relay #1 on the electronics shelf to the compressor terminal block. Rubber grommet (Heyco SB-625-8 class) protects the cable from the cut edge. |
| 2 | 2× M3 mounting tab through-holes at base flange | Anchor to the compressor's existing M5 mounting feet using M5→M3 step-down adapter washers. (No floor pan in this design — see [`../../future.md`](../../future.md) "Other metal candidates considered, decided against".) |
| 3 | Ø ~6 mm chassis ground stud hole | PEM stud or threaded insert for the chassis bonding wire (run AC-6 in [`../../wiring/ac-wiring-schedule.md`](../../wiring/ac-wiring-schedule.md)) — bonds the shroud to building earth. |

No top-side ventilation holes by design — the goal is to *contain* a flame event in this compartment, not vent it. The compressor's heat dissipation is through its body OD (the foot-mounting shell), which is open to the appliance interior and not affected by this shroud.

## SendCutSend specs (working envelope)

For 0.059" G90 galvanized steel, from the SendCutSend material catalog (sendcutsend.com/materials/g90-steel/, .059" tab):

**Laser cutting:**
- Cut tolerance: ±0.005"
- Min hole diameter: 0.022" (0.56 mm) — much smaller than anything we need
- Min hole-to-edge: 0.020" (0.51 mm)
- Min part size: 0.25" × 0.375"

**Bending:**
- Min bend part size: 0.375" × 1.5"
- Max bend length: 44"
- Min flange length (after bend, 90°): 0.311" (7.9 mm)
- Effective bend radius @ 90°: 0.063" (1.6 mm)
- Bend deduction @ 90°: 0.112"
- K factor: 0.36
- Bend angle tolerance: ±1° (bend length ≤24")
- **Max 4-sided box flange height with hardware: 3.00" (76 mm)** — design driver if we go 5-sided box

**Hole-to-bend distance** (rule of thumb, not from SendCutSend's published table): keep holes ≥1.5×T + R from the bend line = 1.5 × 0.059 + 0.063 ≈ 0.15" (3.8 mm). Closer than this risks deformation around the hole during bending. The grommet hole and chassis-ground stud hole both want to sit well inboard of any bend lines anyway.

**Hardware insertion** (PEM nuts, studs, standoffs): SendCutSend offers this on parts ≥1" × 1.5" — the shroud easily clears that. The chassis-ground stud will be a press-in PEM stud inserted by SendCutSend.

**Tapping**: M3 × 0.5 supported on this thickness. If the mounting tabs are tapped instead of clearance-holed, M3 hardware is the path.

## File workflow

SendCutSend accepts both:
1. **2D DXF + bend annotation** at order time (specify bend angles in the quoting UI)
2. **3D STEP file** with bends already modeled

The repo's existing cut-parts (`endcaps-circular`, `touch-flo-under-counter-plate`) use **2D DXF generation via ezdxf** in Python. For a bent part, the DXF carries the *flat pattern* (after applying bend deduction) plus bend lines as a separate layer or as dashed/centered lines. SendCutSend's quoting UI then asks for the bend angle of each line.

Either approach works. Once the python generator is written, decide which file SendCutSend gets at order time:

- **DXF route**: Python generates the flat-pattern DXF using the SendCutSend bend deduction (0.112" for this material at 90°). Bend lines drawn on a separate layer or with a distinct line type. At checkout, specify each bend line's angle.
- **STEP route**: CadQuery-generated 3D model with bends modeled. SendCutSend computes the flat pattern automatically. Higher upfront CAD effort, simpler ordering.

The DXF route matches the pattern already used in this repo. The STEP route is preferable if and when the geometry becomes complex enough that a flat-pattern DXF gets error-prone.

## Files (planned)

- `generate_dxf.py` — parametric flat-pattern DXF generator (ezdxf), once compressor measurements are in hand
- `compressor-shroud-flat.dxf` — generated flat pattern with bend lines marked
- `compressor-shroud-drawing.pdf` — annotated drawing showing bend angles + bend lines + grommet location, generated from CadQuery `.section()` projections

Run with `tools/cad-venv/bin/python generate_dxf.py` per the project's CadQuery / ezdxf convention.

## Open items

1. **Measure the donor compressor** — terminal block envelope, PTC module standoff, mounting foot pattern (M5 thread spacing + bolt circle), body OD/height. Without this the shroud dimensions are placeholders.
2. **Decide one-piece 5-sided box vs. two-piece U-channel + back-wall.** Driven by the 3" max box-flange height constraint and by build / install ergonomics.
3. **Decide the AC pass-through grommet location.** Best path is the side facing the electronics shelf (back-side of shroud, since the shelf is at top-back) — minimizes wire run length.
4. **Write `generate_dxf.py`** once items 1–3 are settled.

The floor pan question (earlier item 4) was resolved against a floor pan; the shroud's mounting tabs go directly to the compressor's M5 mounting feet. See [`../../future.md`](../../future.md) "Other metal candidates considered, decided against".
