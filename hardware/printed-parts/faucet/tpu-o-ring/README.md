# Faucet tube sealing thimble · HSM-000090

Printed TPU 85A **sealing thimble** (closed bottom with a centered hole, open top,
cylindrical wall) that seals the 3/8" OD LLDPE soda faucet tube into the
harvested Westbrass R2031-NL's top water port. Sits *in*
that port. Sealing happens on **two interfaces in series**:

1. **Radial seal** — outer cylindrical face of the thimble compresses
   against the port wall (Ø [10.44 mm](ORING_OUTER_D) vs Ø [10 mm](WESTBRASS_PORT_D) = [0.22 mm](WESTBRASS_SQUEEZE)/side squeeze);
   inner cylindrical face grips the LLDPE OD (Ø [9.2 mm](ORING_INNER_D) vs Ø [9.525 mm](LLDPE_OD) =
   [0.1625 mm](LLDPE_INTERFERENCE)/side interference).
2. **Face seal** — the LLDPE tube's square-cut bottom end face
   bottoms out on the thimble's cap and presses against it.
   Pressure-energized: water flowing up from the valve chamber pushes
   the LLDPE end harder onto the cap.

The cap's centered hole (Ø [6.5 mm](CAP_HOLE_D)) sits between LLDPE
ID (1/4" = [6.35 mm](LLDPE_ID)) and LLDPE OD ([9.525 mm](LLDPE_OD)).
The LLDPE bottoms out on the cap.

## Where this lives in the wet path

The Westbrass acts as the **1/4" → 3/8" diameter adapter** in
the faucet's wet path:

- **Supply (the Westbrass's bottom compression port):** 1/4" OD LLDPE comes
  *up* from below with a Siptenk brass stiffener; factory ferrule +
  nut seal the joint. See [`/hardware/assembly/faucet-and-umbilical.md`](/hardware/assembly/faucet-and-umbilical.md) step 2.
- **Dispense (the Westbrass's top water port):** 3/8" OD LLDPE descends from
  the printed [`faucet-shell`](/hardware/printed-parts/faucet/faucet-shell/) gooseneck water
  channel and enters the Ø [10 mm](WESTBRASS_PORT_D) top port. Water
  flows up out of the valve into the LLDPE; this thimble seals
  around the outside of the tube where it enters the port.

## Geometry

| Dimension | Value |
|---|---|
| Cylinder ID | **[9.2 mm](ORING_INNER_D)** |
| Outer Ø | **[10.44 mm](ORING_OUTER_D)** |
| Cylinder wall | **[0.62 mm](ORING_WALL_T)** |
| Cap hole Ø | **[6.5 mm](CAP_HOLE_D)** |
| Cap thickness | **[2.1 mm](ORING_CAP_T)** |
| Cylinder length | **[13.5 mm](CYL_L)** |
| Total height | **[15.6 mm](TOTAL_H)** |

## Print orientation

Cap-down on the bed. First layer is the annular cap (Ø [10.44 mm](ORING_OUTER_D)
solid disk with a Ø [6.5 mm](CAP_HOLE_D) hole); the [0.62 mm](ORING_WALL_T)
cylindrical wall extrudes upward using the saved single-wall recipe.

The saved spiral recipe commands three solid cap layers totaling **0.66 mm**
(0.30 + 0.18 + 0.18 mm), then one continuous spiral wall. The **2.1 mm** cap
dimension above describes the CAD region, not this recipe's solid cap thickness.

## Material

**Bambu TPU 85A**, using the
[accepted Touch-Flo / LLDPE fit project](tpu-o-ring-85A-6mm.3mf).
The [2026-05-30 physical fit record](print-log.md#v3--85a-seats-successfully-2026-05-30-settings-per-tpu-o-ring-85a-6mm3mf)
establishes successful tube-plus-sleeve seating in the metal donor. It supplies
no quantified sealing-pressure, insertion-force or lifetime result.

The [Mark1 print project and launch record](prints/2026-10-13-tpu85a-right06-mark1/README.md)
retain that project's mesh and process, with the filament mapped to the right
0.6 mm nozzle, Mark1's +0.18 mm trim, and one cap-down sleeve centered on the bed.

The [Mark2 sleeve print](prints/2026-10-23-black-tpu85a-right06-mark2/README.md)
uses black Bambu TPU 85A on the right 0.6 mm nozzle, the glued Engineering Plate
and zero added user Z trim. Its processed archive prints through turns in the
three cap layers, with straight material-contained transfers, and preserves
the native continuous spiral wall. Timelapse is off. Derek reports that the print
“came out pretty well”; specific stringing, assembled fit and sealing results
are unreported. Use the processed archive directly to retain the cap routing.

## Assembly

Fit the thimble to the **tube first, outside the donor**. Stretch and slide
its open mouth evenly around the square-cut 3/8-inch LLDPE tube end until
the end **bottoms on the cap's top face**. Work around the circumference so
the wall stays straight, without a rolled edge or a scrunched section. The
[tube insertion tool](../../fixtures/tube-insertion/README.md) can hold the
tube while fitting the sleeve.

Attach the printed lever to the bare Touch-Flo before inserting the sleeved
tube. Keep the lever **down at rest, not pressed**. Align the tube and sleeve
with the empty metal top port and push them in together, **cap first**.
The [0.22 mm](WESTBRASS_SQUEEZE) nominal radial compression at the outer
face engages the port wall. Total sleeve height is [15.6 mm](TOTAL_H);
nominal port depth is ≥ [20 mm](PORT_DEPTH_MIN).

[Derek's observation](../lever-replica/assembly-observations.json)
establishes that TPU slides against metal far more easily than against LLDPE.
An empty sleeve placed in the donor first scrunches beneath the entering
tube. Keep it on the tube throughout port insertion. Once seated, water
flows: valve chamber → cap hole → LLDPE inner bore → dispense tip.

Complete the donor-to-shell motion in
[shell assembly](../faucet-shell/ASSEMBLY.md): flip the attached lever up,
insert the donor, then let the shell-guided lever snap down to unpressed rest.

For service, remove the tube and thimble from the donor. Recover any sleeve
left in the port without scratching the metal bore. The thimble is consumable;
replace on re-assembly and fit its replacement to the tube outside the donor.

## Regenerate

```
tools/cad-venv/bin/python tpu_o_ring.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/tpu-o-ring/tpu_o_ring.py`
