# Touch-Flo TPU O-ring

Printed-TPU sealing bushing that seals the 3/8" OD LLDPE water tube
into the harvested Westbrass R2031-NL valve body's top water port.
Sits *in* the body port, sandwiched between the LLDPE tube's outer
wall and the body's port bore. Radial compression on both faces
(inner against the tube, outer against the port wall) is the seal.

## Where this lives in the wet path

The Westbrass body acts as the **1/4" → 3/8" diameter adapter** in
the dispense head's wet path:

- **Supply (body's bottom compression port):** 1/4" OD LLDPE comes
  *up* from below with a Siptenk brass stiffener; factory ferrule +
  nut seal the joint. See [`../../../assembly/faucet-and-umbilical.md`](../../../assembly/faucet-and-umbilical.md) step 2.
- **Dispense (body's top water port):** 3/8" OD LLDPE descends from
  the printed [`touch-flo-shell`](../touch-flo-shell/) gooseneck water
  channel and enters the body's Ø 10 mm top port. **This is the
  joint this part seals.** Water flows up out of the valve into the
  LLDPE; this TPU bushing prevents leak around the outside of the
  tube where it enters the port.

The factory uses two toroidal rubber o-rings in grooves on a Ø 9.55
mm metal dispense tube to seal the same port. Replacing the metal
tube with grooveless LLDPE means the seal has to live in the
port-to-tube gap directly — this part fills that gap.

## Geometry

| Dimension | Value | Rationale |
|---|---|---|
| Inner Ø | **9.45 mm** | LLDPE Ø 9.525 mm with 0.0375 mm radial interference per side — firm grip on the tube, resists pull-out, contributes to the seal at the inner interface |
| Outer Ø | **10.2 mm** | Body port Ø 10.0 mm with 0.1 mm radial compression per side — firm seal at the port wall, insertion force manageable by hand |
| Wall | **0.375 mm** | (10.2 − 9.45) / 2. At the edge of FDM minimum wall but printable in TPU with Bambu Studio's Arachne thin-wall handling on a 0.4 mm nozzle |
| Height (axial) | **8 mm** | Substantial sealing band — equivalent contact area to the two factory rubber o-rings combined |
| Cross-section | Plain rectangular ring (concentric cylinder shell) | Easiest to print, full-length contact for sealing |
| Chamfers / ribs | None (v1) | Add if v1 insertion is too hard or sealing is inadequate |

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

## Why a single 8 mm bushing instead of two discrete rings

The factory uses two separate rubber o-rings at axial positions ~10 mm
apart along the metal tube — redundancy plus localized contact
pressure at the seal points. A single continuous TPU bushing is the
v1 choice because:

- **One part to print, one part to install** instead of two.
- **Continuous full-length sealing band** — the 8 mm of axial contact
  area exceeds the combined ~3 mm of contact area the two factory
  o-rings would provide.
- **No risk of misaligning a second ring** — discrete rings need a
  positioning system (groove, shoulder, or careful axial measurement
  on install).
- **Easier first iteration.** If v1 leaks somehow that single-bushing
  geometry can't fix, the fallback is to switch to a two-ring layout
  (two short prints, install one at a time).

## Body port geometry, corrected

The body's top water port was originally measured at Ø 9.75 mm on
2026-04-27 (see [`../../../harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md`](../../../harvested/touch-flo-faucet/valve-body-reference/valve-body-geometry.md)
§3.3). A re-measurement on 2026-05-22, with care taken to land the
caliper tips on the port wall (not the chamfer / lead-in), came back
as **Ø 10.0 mm**. The 10.0 number is the design value going forward,
and it's consistent with the factory o-ring math: uncompressed o-ring
OD 10.15 mm → compressed in 10.0 mm port = 0.075 mm radial squeeze,
a normal o-ring compression.

## Assembly

The bushing seats *into the port* first (slide it down into the body's
top port until its bottom face is at the port floor or 8 mm below the
plateau, whichever comes first), then the LLDPE tube pushes *down
through the bushing* from above. The 0.1 mm radial compression at the
outer face holds the bushing in place against the port wall; the
0.0375 mm radial interference at the inner face means the LLDPE is a
firm push-fit through the bushing's ID.

For service: pull the LLDPE up and out (the bushing's inner interference
will resist), then pluck the bushing out of the port with a pick or
needle-nose. The bushing is consumable; expect to use a fresh one on
re-assembly.

## Regenerate

```
tools/cad-venv/bin/python generate_step_cadquery.py
```
