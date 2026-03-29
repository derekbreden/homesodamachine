# Release Plate — Decomposition

## Decision: Pass Through

This part is a single geometric paradigm. No decomposition needed.

The release plate is a flat prismatic plate with cylindrical bores and holes — entirely an extrude-and-cut problem. Every feature is either a through-bore, a stepped bore (modeled as a revolved profile cut), or a simple cylindrical hole. There are no sweeps, no lofts, no rotational features, and no features from a different geometric paradigm. A single CadQuery agent handles this cleanly using `box` + revolved-profile cuts + cylindrical cuts.

## Features (all belonging to the single part)

1. **Plate body** — rectangular flat plate, the base solid. Extrude a box.
2. **4x stepped collet-actuating bores** — each bore has multiple diameter steps sized to push the JG fitting collet when the plate translates rearward. Modeled as revolved profiles cut from the plate. Positions match the 2x2 JG fitting grid on the rear wall plate.
3. **2x guide pin holes** — clearance holes (sliding fit on 3mm dowel pins pressed into the rear wall plate). The plate slides on these pins. Simple cylindrical through-cuts.
4. **2x link rod attachment points** — blind holes or through holes where the 3mm steel link rods press-fit into the plate. Simple cylindrical cuts.
5. **Spring seat features** — counterbores or flat faces around the guide pin holes where compression springs bear against the plate. May be integral to the stepped guide pin holes (a counterbore step) or simply the flat plate face itself.
6. **Elephant's foot chamfers** — 0.3mm x 45-degree chamfers on bottom edges per manufacturing constraints.

## Geometric Paradigm

Extrude-and-cut. The base body is a rectangular box. Every feature is a cylindrical removal (straight bore, stepped bore via revolved profile, or counterbore). No additive features protrude beyond the plate envelope. No sweeps, no lofts, no helical geometry.

## Print Orientation

Flat on the build plate. Stepped bores and guide pin holes print as vertical cylinders, giving best roundness accuracy. This matches the orientation noted in the concept document.

## Downstream Pipeline

Since no decomposition is needed, the pipeline runs as a single unit:

```
4s (spatial resolution) -> 4b (parts.md) -> 5 (drawing) -> 6g (CadQuery generation)
```

No composition step (6c) required.
