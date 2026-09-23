# Enclosure fit clearances

The enclosure assembly and its printed accessories use the shared allowances in
[fits.py](/hardware/printed-parts/cadlib/fits.py). This page describes the source geometry and
its verification coverage. It does not certify dimensions measured from a physical print.
The faucet has its own completed fit tests and is outside this adjustment.

| Mating surface | Ordinary clearance | Extra for each supported face |
|---|---:|---:|
| Static assembly | 0.15 mm | 0.25 mm |
| Sliding or moving service fit | 0.25 mm: 0.15 base + 0.10 sliding | 0.25 mm |

A gap with one supported face therefore has 0.40 mm for static assembly or 0.50 mm for
sliding. If both opposing printed faces require support, their two 0.25 mm allowances add
to the same gap. Each supported face is counted once, on that face or its mate.

Ordinary clearance is measured normal to the mating surface. A circular fit adds twice its
radial clearance to the diameter. A 45° sliding lap uses the corresponding axial projection.
The bridge allowance follows the part's print direction: a supported cavity crown retreats
0.25 mm toward print-up without moving its nominal axis or its opposite locating edge.
Surrounding stock grows where that retreat needs backing. Vertical holes, upward-open seats,
bedded faces and support-free slopes do not acquire a bridge allowance merely because they
belong to a supported part.

Screw clamping faces, bearing planes, stroke stops, gasket squeeze and made-up fluid joints
keep their explicit mechanical definitions. Manufacturer heat-set pilot cores
retain their prescribed diameter; supported horizontal pilots receive crown relief only.
Tube routing space, tool access, electrical isolation space and structural thickness are not
ordinary mating clearances.

The [enclosure geometry and support policy](enclosure/README.md#support-removal-strategy)
define the working faces. The [cold-core fit coverage](../cold-core/fit-clearances.md)
records the separate printed cold-core components and their print orientations.

## Coverage in the source

Front-top, front-bottom and back-bottom print with machine +Z as print-up. Back-top and the
pump cap print with machine −Z as print-up. The pump cartridge uses +Z.
The same clearance policy follows these orientations rather than the assembled appearance.

| Interface family | Source coverage |
|---|---|
| Enclosure quadrant seams | Sliding tongues, scarf laps, rail channels and pin passages use 0.25 mm running clearance. Supported catch and passage faces carry the additional bridge allowance. |
| Pump cartridge and cap | Bay, fixed-bulkhead and casing passages use their static or sliding allowances. Supported shoulders, recesses and cap screw-head seats carry bridge relief with backing retained. Pump brackets and floor bearings remain seating datums. |
| Display | The glass cavity is 113.8 × 77.3 mm and the PCB passage is 106.3 × 69.3 mm, providing 0.15 mm per side around their nominal envelopes. The glass seat is 4 mm deep. The deeper cover land has its own 0.15 mm inner-wall clearance. The facet's 45° walls and insert axes are support-free; the PCB opening's start ridge is carried by the solid rib. |
| Rear ports and accessories | C14 flange/shroud and keystone body pockets use 0.15 mm static clearance. Nameplate and bulkhead-ring pockets use the shared static allowance; supported pocket edges receive directional relief. The ASSE pan uses 0.25 mm running clearance in its sleeve; its supported flange underside and supported rebate floor have 0.75 mm total air when the pan is seated on the sleeve floor (1.25 mm at the nominal assembly pose), with both finish allowances assigned to the rebate floor. |
| Hardware supports | Wago pocket roofs and tabs, supported tube/body-seat crowns, anchor tie cavities, ASSE seats and the PRV chase receive their applicable bridge allowance. The surrounding towers, ribs and sleeve stock retain their working sections. |
| Fasteners | M3 through clearance is Ø3.3 mm and nominal Ø5.5 mm heads receive Ø5.8 mm counterbores. Horizontal supported shank/insert crowns and supported head seats receive directional relief; bedded vertical insert openings retain the prescribed pilot. |
| Other enclosure accessories | Display cover, gasket, nameplate, bulkhead rings and collet press retain their stated print orientations. Supported head seats are treated locally; flat bedded plates and support-free tools do not receive blanket offsets. |
| Cold-core printed parts | Foam shell/caps, reservoirs/caps, copper plugs, PRV shroud and reed bridge follow the [component coverage](../cold-core/fit-clearances.md). Copper-plug tabs have 0.50 mm wall clearance and their opposite channel faces have 0.25 mm running clearance. |

## Physical observations

Derek's PET-GF tests show that clean removal of a tree support and its dense interface does
not necessarily remove the loose roof or bridge strands left on the supported model face.
Those strands can remain attached at their edges and reduce a fitted opening. Peeling them
away can bring the measured opening back to the designed size. The geometric allowance is
room for that retained surface finish.

In the overnight numbered test, samples **1, 2, 7, 8, 9, 10, 12 and 16** had the cleanest
support removal while retaining the roof strands. Derek ranked **10, then 16, then 8** as the
cleanest of that group. The retained strands still felt looser than the next model layer.
In the four-sample test, B and C were not visibly distinguishable despite C's removed end
connections; D released some complete strips including their edges, but most remained.
These are removal observations, not a new measurement of the required clearance.

Derek also reports that the enclosure display fits well in the tested print, and that an
RJ11 jack fits in the tested enclosure back-top. Those observations are retained alongside
the nominal hardware envelopes used to size the CAD pockets.

## Verification

Feature checks read supported relief on the actual print-up side, ordinary clearance on the
opposite and lateral faces, retained wall sections, and unchanged seating planes. Enclosure
assembly checks also cover whole-part intersections, cap/cartridge withdrawal, hardware
envelopes, and seam capture. Zero whole-part
overlap alone does not establish a nonzero fit clearance where intentional datums touch.

[check_copper_plug_clearance.py](/hardware/scripts/check_copper_plug_clearance.py) reads the
finished standalone front-top, foam assembly and both copper-plug STEPs. It places the plugs
through the production transforms and writes a focused, hashed reading beside the plugs.
Run it after those outputs have been regenerated:

```sh
tools/cad-venv/bin/python hardware/scripts/check_copper_plug_clearance.py
```

The [focused reading](../cold-core/copper-plugs/clearance-check.json) records its input hashes,
scope and pass/fail result. Use those hashes when interpreting its measurements. The enclosure
and cold-core scorecards carry the results for the geometry they built; neither the source
values on this page nor a retained reading of another build establish the final printed fit.
