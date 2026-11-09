# Beduan valve in SolidCraft

This model builds the measured Beduan exterior as editable SolidCraft features for printed-part fit and website display.

[Explore the published model](https://homesodamachine.com/3d#step:reference%2Fbeduan-solenoid%2Fsolidcraft%2Fbeduan-valve.step?find=view%3A%20az%3D45%20el%3D25) · [View the mounting surfaces](https://homesodamachine.com/3d#step:reference%2Fbeduan-solenoid%2Fsolidcraft%2Fbeduan-valve.step?find=view%3A%20az%3D45%20el%3D-30%0Abox%3A%20x%3D-17.000%20y%3D-17.000%20z%3D-0.100%20to%20x%3D17.000%20y%3D17.000%20z%3D5.250%20%22Mounting%20surfaces%22)

![Native SolidCraft Beduan valve](beduan-valve.step.png)

Open [beduan-valve.json](beduan-valve.json) in SolidCraft to edit the source. The **Parameters** table's favorites expose the mounting, bearing, port and terminal interfaces. The history folders follow the physical features. [beduan-valve.sc](beduan-valve.sc) is the packed native copy. Both contain the parameters, sketches and feature history.

The [native browser lab](https://homesodamachine.com/labs/solidcraft/beduan) edits and renders this valve in an isolated SolidCraft session. Its local edits, pause and resume controls and update observations are described beside the [lab implementation](../../../../web/public/solidcraft-lab/README.md).

## Construction

The origin is on the mounting-post ends, centered on their rectangular pattern. X crosses the flow axis, Y points toward the outlet and terminals, and Z rises through the coil. The nominal mounting dimensions agree with the [production valve interface](../../../printed-parts/valve-seat/numbers.rs). Printer allowance belongs to the receiving printed part; the purchased-part reference retains the measured nominal surfaces.

| Physical feature | Native construction | What it supplies |
| --- | --- | --- |
| Moulded housing | Circle footprint, associative sketch pattern, extrusion and junction fillets | Main body and rounded corner-boss silhouette |
| Bearing boss | Revolved rounded section and a revolved annular recess | Seating plane and occupied space beneath the body |
| Mounting posts | Patterned circles, post extrusion, lead-in rounds and a hole feature using the post sketch | Post walls, ends, shoulders and bore mouths |
| Cap | Native rounded-rectangle blank and notch, mirrored cut and edge rounds | Moulded flange envelope and access around the ports |
| Port barrels | Revolved stepped section and a mirrored feature | Barrel wall, transition, tube axis and observed entrance depth |
| Release collets | Rounded lip, neck and bore, mirrored base body, and oriented annular arc extrusions | Tube entry, locking collar and the captured release-ear orientation |
| Coil housing | Revolved encapsulation section and extruded profiles for the block, nose, tongue and terminal roots | Black encapsulation, connector approach and exposed gaps |
| Steel yoke | Extruded bent section and a base plate reusing the cap's profile sketches | Constant sheet stock, bend radii and the open space around the coil |
| Terminals | Rounded blade extrusion with latch hole, mirrored as a finished body | Connector width, stock, reach and spacing |
| Fasteners | Rounded screw-head body, repeated on the post pattern | Exposed fastener envelopes |

The port's revolve axis comes from a construction line in its parameter-driven section. Native rounded rectangles own their corner radii and constrained sides. Sketches are fully constrained, and physical interface parameters drive their repetitions. Material bodies retain separate plastic and metal appearances.

The housing's overlapping circles resolve in the sketch. Shared cap and notch profiles locate the plastic cap and steel mounting plate. The coil's concentric rim follows its core radius and round. Uniform sections are extruded; rotational sections are revolved.

## Fidelity boundary

The [capture evidence](../scan-evidence.json) supplies exterior measurements. Cylinders, planes, cones and circular rounds describe the manufactured forms. Scan coating, noisy or missing surface patches, lettering, screw drives and hidden fluid passages are omitted. Unobserved bore closures are model boundaries.

The collet ears have a captured orientation. Access for turning a collet uses the ear's full swept radius, which is exposed as a parameter.

[evaluation.json](evaluation.json) records the native construction, exports, interface measurements, scan agreement and parameter edits. Scan agreement describes the captured sample; it does not establish the scanner's absolute accuracy or qualify a particular printed snap fit.

## Rebuild

From the repository root:

```sh
python3 tools/run.py -- solidcraft-cli run --in hardware/reference/beduan-solenoid/solidcraft/beduan-valve.json --save hardware/reference/beduan-solenoid/solidcraft/beduan-valve.sc --out hardware/reference/beduan-solenoid/solidcraft/beduan-valve.step
```

Save source edits to the native JSON design; SolidCraft keeps that file as plain JSON. Regenerate the packed copy and STEP from it. The STEP supplies CAD interchange and the website's mesh payload. These are manually regenerated reference artifacts; the model adds no recurring build or commit check.

The existing STEP reader groups this component's solids and loses their individual labels and colours. The frozen viewer payload carries the STEP's solid names and the native design's appearances, matched by body bounds. Its geometry buffers retain the STEP tessellation unchanged. The mapping and hashes are recorded in the evaluation; a reusable export adapter remains work for the wider modeling workflow.
