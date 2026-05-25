# Touch-Flo TPU O-ring

Printed-TPU **thimble** (closed bottom with a centered hole, open top,
cylindrical wall) that seals the 3/8" OD LLDPE water tube into the
harvested Westbrass R2031-NL valve body's top water port. Sits *in*
the body port. Sealing happens on **two interfaces in series**:

1. **Radial seal** — outer cylindrical face of the thimble compresses
   against the port wall (Ø [10.2 mm](OUTER_D) vs Ø [10 mm](BODY_PORT_D) = [0.1 mm](BODY_SQUEEZE)/side squeeze);
   inner cylindrical face grips the LLDPE OD (Ø [9.45 mm](INNER_D) vs Ø [9.525 mm](LLDPE_OD) =
   [0.0375 mm](LLDPE_INTERFERENCE)/side interference).
2. **Face seal** — the LLDPE tube's square-cut bottom end face
   bottoms out on the thimble's cap and presses against it.
   Pressure-energized: water flowing up from the valve chamber pushes
   the LLDPE end harder onto the cap.

The cap's centered hole (Ø [6.5 mm](CAP_HOLE_D)) is larger than the LLDPE ID
(1/4" = [6.35 mm](LLDPE_ID)) so water flow isn't restricted, but smaller than the
LLDPE OD ([9.525 mm](LLDPE_OD)) so the tube physically bottoms out on the cap
rather than passing through. This also **defines insertion depth** —
the LLDPE pushes in until it stops; no ambiguity, no axial migration.

## Where this lives in the wet path

The Westbrass body acts as the **1/4" → 3/8" diameter adapter** in
the dispense head's wet path:

- **Supply (body's bottom compression port):** 1/4" OD LLDPE comes
  *up* from below with a Siptenk brass stiffener; factory ferrule +
  nut seal the joint. See [`../../../assembly/faucet-and-umbilical.md`](../../../assembly/faucet-and-umbilical.md) step 2.
- **Dispense (body's top water port):** 3/8" OD LLDPE descends from
  the printed [`touch-flo-shell`](../touch-flo-shell/) gooseneck water
  channel and enters the body's Ø [10 mm](BODY_PORT_D) top port. **This is the
  joint this part seals.** Water flows up out of the valve into the
  LLDPE; this TPU bushing prevents leak around the outside of the
  tube where it enters the port.

The factory uses two toroidal rubber o-rings in grooves on a Ø [9.55 mm](FACTORY_TUBE_OD)
metal dispense tube to seal the same port. Replacing the metal
tube with grooveless LLDPE means the seal has to live in the
port-to-tube gap directly — this part fills that gap.

## Geometry

| Dimension | Value | Rationale |
|---|---|---|
| Cylinder ID | **[9.45 mm](INNER_D)** | LLDPE Ø [9.525 mm](LLDPE_OD) with [0.0375 mm](LLDPE_INTERFERENCE) radial interference per side — firm grip on the tube, resists pull-out, contributes to the seal at the inner interface |
| Outer Ø | **[10.2 mm](OUTER_D)** | Body port Ø [10 mm](BODY_PORT_D) with [0.1 mm](BODY_SQUEEZE) radial compression per side — firm seal at the port wall, insertion force manageable by hand |
| Cylinder wall | **[0.375 mm](WALL_T)** | ([10.2 mm](OUTER_D) − [9.45 mm](INNER_D)) / 2. Below 0.4 nozzle's single-line minimum, but the **cap forms the first layer** when printed cap-down (see "Print orientation"), so the thin wall doesn't have to bootstrap from the bed — Arachne thin-wall handling takes over from layer 2 onward |
| Cap hole Ø | **[6.5 mm](CAP_HOLE_D)** | Larger than LLDPE ID (1/4" = [6.35 mm](LLDPE_ID)) so water flow into the LLDPE bore isn't restricted; smaller than LLDPE OD ([9.525 mm](LLDPE_OD)) so the tube bottoms out on the cap and can't pass through. Defines insertion depth |
| Cap thickness | **[1.5 mm](CAP_T)** | Structural under face-seal load (water pressure pushing the LLDPE end onto the cap); also the part's **solid first layer** when printed cap-down |
| Cylinder length | **[13.5 mm](CYL_L)** | Sealing band, generous radial seal contact area |
| Total height | **[15 mm](TOTAL_H)** | [1.5 mm](CAP_T) + [13.5 mm](CYL_L). Port depth ≥ [20 mm](PORT_DEPTH_MIN) per 2026-05-24 measurement — comfortable headroom |
| Chamfers / ribs | None (v1) | Add if v1 insertion is too hard or sealing inadequate |

## Print orientation

**Cap-down on the bed.** First layer becomes the annular cap (Ø [10.2 mm](OUTER_D)
solid disk with a Ø [6.5 mm](CAP_HOLE_D) hole) — maximum bed contact, no
empty-thin-ring slicer rejection. The thin [0.375 mm](WALL_T) cylindrical wall
extrudes upward from layer 2 onward via Arachne thin-wall, which
handles sub-nozzle-width perimeters as long as the geometry below is
already established.

The first attempt at this part (v1, 8 mm open-ended sleeve) hit a
"empty initial layer" error in Bambu Studio because the [0.375 mm](WALL_T)
thin ring couldn't be filled by the 0.5 mm first-layer line width.
The thimble v2 dodges this entirely by starting with a solid cap.

## Material

**Bambu TPU 90A** — same stock and shore hardness as the other
printed gaskets in this project (touch-flo-mounting-gasket,
foam-cap gasket, reservoir face seals). 90A is the
gasket-industry-standard hardness: soft enough to seal under modest
squeeze, firm enough to resist cold-flow over years.

See [`../../cold-core/foam-shell/README.md`](../../cold-core/foam-shell/README.md)
("foam_cap_gasket" section) and
[`../touch-flo-mounting-gasket/generate_step_cadquery.py`](../touch-flo-mounting-gasket/generate_step_cadquery.py)
for the existing TPU-90A treatment.

## Why a single continuous thimble instead of two discrete rings

The factory uses two separate rubber o-rings at axial positions ~10 mm
apart along the metal tube — redundancy plus localized contact
pressure at the seal points. A single continuous thimble is chosen
here because:

- **One part to print, one part to install** instead of two.
- **Continuous full-length sealing band** — [13.5 mm](CYL_L) of axial contact
  area exceeds the combined ~3 mm of contact area the two factory
  o-rings would provide, *plus* the added face seal from the cap is
  a redundancy mode the factory doesn't have.
- **No risk of misaligning a second ring** — discrete rings need a
  positioning system (groove, shoulder, or careful axial measurement
  on install).
- **Easier first iteration.** If this design leaks somehow the
  thimble can't fix, the fallback is to switch to a two-ring layout
  (two short prints, install one at a time).

## Body port geometry, corrected

The body's top water port was originally measured at Ø 9.75 mm on
2026-04-27 (see [`../../../harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md`](../../../harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md)
§3.3). A re-measurement on 2026-05-22, with care taken to land the
caliper tips on the port wall (not the chamfer / lead-in), came back
as **Ø [10 mm](BODY_PORT_D)**. The new value is the design reference going forward,
and it's consistent with the factory o-ring math: uncompressed o-ring
OD [10.15 mm](FACTORY_O_RING_OD) → compressed in [10 mm](BODY_PORT_D) port = [0.075 mm](FACTORY_O_RING_SQUEEZE) radial squeeze,
a normal o-ring compression.

## Assembly

The thimble seats **cap-down** into the body's port first — drop it in
with the closed cap pointing toward the valve chamber below. The
[0.1 mm](BODY_SQUEEZE) radial compression at the outer face holds it in place against
the port wall as it's pushed down; total height [15 mm](TOTAL_H) vs the ≥ [20 mm](PORT_DEPTH_MIN)
port depth means the thimble sits below the plateau face with margin.

Then the LLDPE tube pushes **down through the open top** from above
until its square-cut bottom end **bottoms out on the cap's top face**.
That contact is positive — the LLDPE physically can't push further
because the cap hole (Ø [6.5 mm](CAP_HOLE_D)) is smaller than the LLDPE OD (Ø [9.525 mm](LLDPE_OD)).
Once seated, water flows: valve chamber → cap hole → LLDPE inner bore
→ up through the gooseneck → dispense tip.

For service: pull the LLDPE up and out (the thimble's inner
interference will resist), then pluck the thimble out of the port
with a pick or needle-nose. The thimble is consumable; expect to use
a fresh one on re-assembly.

## Regenerate

```
tools/cad-venv/bin/python generate_step_cadquery.py
```
