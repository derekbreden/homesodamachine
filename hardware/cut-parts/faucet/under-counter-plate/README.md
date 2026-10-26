# Under-counter mounting plate

One laser-cut 0.060-inch (1.524 mm) 316 stainless plate per faucet, shared by
Sculpted and Industrial. The retained donor washer and nut clamp it against
the underside of the countertop. Its two rounded channels open toward world
+X so the plate slides sideways over the shank and complete rear bundle.

[under-counter-plate.dxf](under-counter-plate.dxf) is the production ordering
file: one closed outline, native lines/arcs, millimetres (`$INSUNITS=4`).
[under_counter_plate.py](under_counter_plate.py) derives the rear opening
from the same interface used by the faucet, rigid plate and TPU gasket.

[Finished plate engineering drawing](under-counter-plate-drawing.pdf)
(FCT-PLT-01, Rev A) defines the production profile in the DXF coordinate frame,
channel widths and cap centers, thickness and finished edge requirements.
Linear dimensions are ±0.13 mm unless specified; stock thickness is
1.52 ±0.13 mm. The finished plate has a 0.10 mm maximum edge break and a
0.25 mm maximum free-state gap on a flat inspection surface.
[under_counter_plate_drawing.py](under_counter_plate_drawing.py) generates
the sheet from the production outline and shared interface dimensions.

| Feature | Dimension |
|---|---|
| Circular bearing outline | Ø54.55 mm, world center (0, 3.275) |
| Shank pocket and open channel | Ø12.6 mm / 12.6 mm wide |
| Rear terminal pocket | 18.15 × 7.25 mm, world center (0, 18.925) |
| Rear open channel | 7.25 mm along world Y |
| Four channel-mouth rounds | R1.5 mm |
| Sheet | 0.060-inch (1.524 mm) 316 stainless |

The lower faucet, rigid above-counter plate and gasket place the flavors at
X=±5.45, Y=18.925 mm; the drain at X=0, Y=18.525 mm; and the flat ribbon at
X=0, Y=21.4875 mm. The soda connection is on the shank axis, X=Y=0.
The organizer shares that left/right centerline, with wider flavor spacing
and small forward offsets to retain at least 1.5 mm of material everywhere.

The [manual mounting review](centered-layout-check.json) bounds the complete
60 mm plate slide at every intermediate position through the modeled 19–38 mm
countertop routing range. The minimum nominal cut-to-flavor gap is 0.45 mm;
the measured ribbon envelope has at least 0.4725 mm clearance. SendCutSend
[publishes ±0.005-inch (0.127 mm) cut tolerance](https://sendcutsend.com/materials/stainless-steel-316/).
These are geometric clearances. Cut-edge finish, printed threading fit,
installation force, clamp capacity and maximum clampable deck thickness are
unqualified for this centered set.

Finish both faces of every cut edge and remove any laser tabs before kit
assembly, including the closed rear cap and channel-mouth rounds. The supplier
quote does not offer deburring at this part size; edge cleanup is done at
Derek's bench. Keep the rear channel open for the complete bundle.
The [purchased-stock record](stock-profile.json) and
[S4177511-purchased.dxf](S4177511-purchased.dxf) identify the received plates.
Use the production ordering file above for this centered faucet set.
