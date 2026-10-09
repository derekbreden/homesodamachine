# Umbilical tube organizer candidate

One floating round puck is intended to keep the soda, two flavor and drain tubes
in formation below the faucet mounting workspace. The target is deliberate
pushing or pulling of each tube while the other hand holds the puck. Hanging,
bending and ordinary handling should leave those relative positions unchanged.
This is a proposed part, with an unqualified physical sliding fit.

## Geometry and material

The part is Ø32 × 20 mm in **Bambu TPU 90A**, the material specified for the
[faucet thimble](../../hardware/printed-parts/faucet/tpu-o-ring/README.md).
Four smooth straight bores provide 19.2 mm of contact after the 0.4 mm entrance
chamfers. Three are Ø6.20 mm for nominal 6.35 mm tubing and one is Ø3.85 mm for
the nominal 4 mm drain. The 0.15 mm nominal diametral interference is a starting
value for a fit trial. It does not establish a hand force. Tube size, printed
bore size, wall compliance, surface texture and contact length all affect grip.

A separate Ø5 mm round passage clears the 4.1 × 1.3 mm maximum stated signal
ribbon envelope. It provides spacing without intentional axial grip. The outer
rim has 0.6 mm chamfers to ease threading the braid. The body has no fasteners,
teeth, separate liners or opening seam. Its closed passages thread over free
tube and cable ends during bench assembly.

The flexible body is intended to yield around the tube instead of making a rigid
undersized socket. The manufacturer's [TPU 90A material information](https://us.store.bambulab.com/products/tpu-85a-tpu-90a/)
supports that material choice; it does not qualify this part's friction or life.
An increase in contact length can increase sliding resistance if contact
pressure is retained. Length cannot make an oversized straight bore grip an
otherwise straight tube. The existing
[identification collars](../../hardware/printed-parts/faucet/tube-collar/README.md)
use clearance and tubing curvature; their PETG estimate is not a TPU friction
calibration.

## Proposed installation

The shown station begins at faucet Z = −88 mm and ends at −108 mm. With the
native 30 mm slab, its upper face is **50.476 mm below the steel plate** and
38 mm below the shank end. With the 38 mm routing-envelope slab the corresponding
plate gap is 42.476 mm. These are geometric gaps; the retained washer, nut and
soda compression fitting are absent from the native reference, so the model does
not prove hand or wrench access.

The white faucet's staggered flavor unions sit below the organizer: the upper
union starts 7 mm below it and the lower union follows end to end. Both flavor
tubes keep the native R30 return to the existing union axes. The drain makes its
R25 return to the bypass axis before the organizer. All four axes are parallel
through the bores. The downstream gathers retain the native radii, and the
insulation starts below both unions. This placement requires the proposed lower
routing and union positions shown in the context; it is not a drop-in overlay
on the production assembly. The black faucet can pass continuous flavor tubing
through the same bores.

In the shown white-faucet context the foam begins at Z = −241.062 mm, leaving
191.062 mm of bare blue tubing below the shank end. That is part of this candidate's
thermal layout; the organizer's grip trial does not qualify outlet temperature.

The signal cable's lower continuation is modeled only beside the puck. Its
complete approach around the unions and its slack need bench routing. The
braid covers the organizer; at the existing nominal 1 mm braid wall it is
Ø34 mm, giving 0.465 mm radial clearance in the Ø34.93 mm counter hole at this
station. That envelope excludes extra braid folds and is not a passage result.
The foam remains compressible as recorded in the
[reference observations](../../hardware/reference/cargen-pipe-insulation/physical-observations.json).
This organizer grips bare tubing, with foam downstream. It does not depend on
foam compression for tube retention.

The puck floats with the bundle rather than fastening to the cabinet. Gripping
at one station does not eliminate the different path lengths tubes need around
a bend. The tubes between gripping stations still need room to flex and settle.

## Fit trial decision

The first trial selects a bore and contact length that preserve formation while
remaining deliberately adjustable by two hands. It uses the actual quarter-inch
and 4 mm tubing, this material, and the intended upright print orientation.
No unions or magnets from the plug exploration are needed for the puck trial.

Thread the puck on loose ends. With one hand holding it and the other holding
each tube, push and pull the tube through. Accept a fit that moves without a tool,
without bracing against a counter and without visibly flattening, kinking or
scoring the tube. If the bore grips too firmly, enlarge it before adding length
or requesting a force measurement. If it slides freely, reduce the bore or
increase effective contact length while retaining that hand adjustment.

Then mark each tube at the puck, hang the actual sleeved bundle, and handle the
under-counter plate, washer and nut through the installation sequence. Bend and
reposition the lower bundle as that sequence requires. Accept only if the marks
stay at the puck and the tubes remain clear of the mounting working area. The
retained nut, washer and compression fitting must also allow the intended hand
and tool approach. A clamp, bracket or force gauge is unnecessary for this first
decision. These observations would select the fit; they would not establish
long-term creep, wear or lifetime.

## Files

- `organizer.py`: parameterized candidate and proposed installation context.
- `organizer.step`: analytic part, generated locally.
- `organizer.stl`: upright source mesh, generated locally.
- `geometry.json`: dimensions, positions, topology and evidence limits.

Regenerate with `tools/cad-venv/bin/python future/umbilical-organizer-exploration/organizer.py`.
This is a manual exploration command, with no production build or print launch.

The generated part is one valid native solid with 20 faces and 42 edges. The
STL is closed with consistent winding. Its four specified bore volumes are open
through the complete length. The minimum straight-bore outer wall is 2.350 mm
and the minimum web between passages is 1.613 mm; the entrance and rim chamfers
reduce those values locally. These are geometry checks, not retention evidence.
The intended print orientation stands all five passages vertically. A sliced
printer job has not been prepared for this candidate.
