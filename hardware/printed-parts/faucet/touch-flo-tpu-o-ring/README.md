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

The cap's centered hole (Ø [6.5 mm](CAP_HOLE_D)) sits between LLDPE
ID (1/4" = [6.35 mm](LLDPE_ID)) and LLDPE OD ([9.525 mm](LLDPE_OD)).
The LLDPE bottoms out on the cap.

## Where this lives in the wet path

The Westbrass body acts as the **1/4" → 3/8" diameter adapter** in
the dispense head's wet path:

- **Supply (body's bottom compression port):** 1/4" OD LLDPE comes
  *up* from below with a Siptenk brass stiffener; factory ferrule +
  nut seal the joint. See [`../../../assembly/faucet-and-umbilical.md`](../../../assembly/faucet-and-umbilical.md) step 2.
- **Dispense (body's top water port):** 3/8" OD LLDPE descends from
  the printed [`touch-flo-shell`](../touch-flo-shell/) gooseneck water
  channel and enters the body's Ø [10 mm](BODY_PORT_D) top port. Water
  flows up out of the valve into the LLDPE; this TPU bushing seals
  around the outside of the tube where it enters the port.

## Geometry

| Dimension | Value |
|---|---|
| Cylinder ID | **[9.45 mm](INNER_D)** |
| Outer Ø | **[10.2 mm](OUTER_D)** |
| Cylinder wall | **[0.375 mm](WALL_T)** |
| Cap hole Ø | **[6.5 mm](CAP_HOLE_D)** |
| Cap thickness | **[1.5 mm](CAP_T)** |
| Cylinder length | **[13.5 mm](CYL_L)** |
| Total height | **[15 mm](TOTAL_H)** |

## Print orientation

Cap-down on the bed. First layer is the annular cap (Ø [10.2 mm](OUTER_D)
solid disk with a Ø [6.5 mm](CAP_HOLE_D) hole); the [0.375 mm](WALL_T)
cylindrical wall extrudes upward via Arachne thin-wall.

## Material

**Bambu TPU 90A**

## Assembly

The thimble seats **cap-down** into the body's port first — drop it in
with the closed cap pointing toward the valve chamber below. The
[0.1 mm](BODY_SQUEEZE) radial compression at the outer face engages
the port wall as it's pushed down. Total height [15 mm](TOTAL_H);
port depth ≥ [20 mm](PORT_DEPTH_MIN).

Then the LLDPE tube pushes **down through the open top** from above
until its square-cut bottom end **bottoms out on the cap's top face**.
Once seated, water flows: valve chamber → cap hole → LLDPE inner bore
→ up through the gooseneck → dispense tip.

For service: pull the LLDPE up and out, then pluck the thimble out
of the port with a pick or needle-nose. The thimble is consumable;
replace on re-assembly.

## Regenerate

```
tools/cad-venv/bin/python touch_flo_tpu_o_ring.py
```

## Sources
[value](NAME) texts are updated by:
- `/hardware/printed-parts/faucet/touch-flo-tpu-o-ring/touch_flo_tpu_o_ring.py`
