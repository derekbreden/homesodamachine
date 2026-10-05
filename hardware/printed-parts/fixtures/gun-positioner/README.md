# Gun positioner fabrication kit

This kit defines one permanent metal bench frame, three supported-rail linear stages and three screw-driven angular stages. The gun uses adjustable insulated jaws on a retained release cradle. Two independently mounted camera stages observe the actual gun and seam; the independently anchored fiber boom uses swiveling saddles and preserves the active fiber's minimum 350 mm bend radius.

The assets support fabrication and guarded commissioning. No print, loaded motion, holding, accuracy or lifetime result has been accepted. The physical gates in [requirements.json](requirements.json) and the [commissioning procedure](../../../gun-positioner/commissioning.md) govern use.

## Ready files

| File or directory | Purpose |
|---|---|
| [Illustrated assembly guide](../../../gun-positioner-guide/gun-positioner-guide.pdf) | Build order, parts added at each operation, fixtures and qualification |
| [Purchase list](../../../gun-positioner/purchases.md) | Shared Amazon Prime purchases, including camera and calibration hardware |
| [Assembly STEP](gun-positioner-assembly.step) | Complete neutral assembly with separate named bodies |
| [STEP solids](step/) | Printed parts, plates, tube spacers, formed angles and square-bar parts |
| [STL solids](stl/) | Same fabrication geometry; print only rows whose `kind` is `print` |
| [Actual-size templates](templates/) | Plate SVG/DXF and kerf-aware stock sheet layouts |
| [Fabricated part manifest](parts.json) | Quantity, material, blank, hole/slot coordinates, print orientation and asset filenames |
| [Assembly instances](assembly.json) | Named components, groups and world transforms |
| [Service fixture instances](fixture-assemblies.json) | Powered force fixture, nozzle fork, torque lever/redirect, installed Z load fixture and hub/capture proof fixtures |
| [Fastener schedule](fasteners.json) | Each joint's exact bolt quantity, length, washers, nuts and checked grip |
| [Hardware totals](hardware-counts.json) | Consumption totals and separate large-washer requirements |
| [Joint allocations](joint-allocations.json) | Named angle/corner allocations rather than unassigned bulk hardware |
| [Shared flat stock nest](stock-nest.json) | Mechanism and camera blanks on the same purchase sheets; eight extrusion-stick layouts |
| [Flat blank inventory](metal-blanks.json) | Unique part labels and finished blank sizes |
| [Other metal stock](stock-profiles.json) | Tube, angle, square bar, screw and shaft cut lengths with quantities |
| [Fabrication source check](fabrication-source-check.json) | Solid validity, drill-circle and named head clearances; explicit scope |
| [Geometry arithmetic](geometry-check.json) | Travel, lead geometry, command scale and assumed-load calculations |
| [Finite proxy clearance](working-subset-clearance.json) | Numeric gun/vessel screen and its explicit scope |
| [Export receipt](export-receipt.json) | Source/helper and actual assembly STEP hashes, export status and counts |
| [Asset hash index](asset-hashes.json) | SHA256 of every fabrication asset and complete assembly STEP |

All CAD and DXF coordinates are millimetres. SVG templates print at 100% with scaling disabled. Confirm the 50 mm ruler within 0.25 mm before drilling. Blank tolerance is ±0.5 mm; registered hole centers are ±0.25 mm. Transfer-drill the actual supplied rail feet, bearing bases and switch bodies. Catalog drawings describe the selected interface; they do not accept a delivered fit or whole-machine load rating.

Plate templates apply only to `template_type: plate`. Formed angles, annular spacers and square bars retain their purchased profiles. Their STEP/STL geometry and stock-cut table must not be interpreted as flat aluminum substitutes. The separate purchased steel-washer template drills two 3.4 mm guide holes, 30 mm apart, in a 37 OD / 13 ID / 3 mm steel washer.

## Metal preparation and joints

Use the shared nest before cutting. Three 450 × 199 mm beds require the long sheets. Camera blanks share the remaining sheets. The selected stock uses 3 mm cutting kerf and a 1 mm sheet-edge reserve. Wide sheet needs the listed nonferrous jigsaw blade; it does not fit the bench band saw throat. Deburr every cut and check the actual blank before transferring its template.

The SBR12 block deck is 40 mm above the rail mounting surface. Its four M5 holes are 26 mm along the rail and 28 mm across. A 6.35 mm carriage plus a 1 mm washer uses M5×16, leaving 8.65 mm engagement in the catalog 10 mm thread depth. The rail foot uses M3×20 through-bolts. Confirm actual depth and prevent bottoming.

Each axis has one moving TR8×2 nut and two fixed retention nuts, 18 total. One end has metal races on both sides of the metal thrust bulkhead. Five 2 mm M10 clearance washers form each 10 mm spacer around the brass body. The housing race rests on the 10.5–16 mm annulus of the bulkhead; its inner 8.2–10.5 mm band is unsupported. Center the race without imposing radial force and qualify the assembled reaction. There is no counterbore operation. Degrease the fixed threads, apply the specified medium-strength retainer, cure 24 hours and mark witness lines after adjusting the measured stack.

XYZ screws retain their 400 mm length. Angular screws are 300 mm. Cut one spare purchased screw to 200 mm for the powered test fixture. Never saw the four hardened 8 × 100 mm crash guide rods. The 12 mm shaft cuts are 175/165 mm from one 356 mm stick and 130/85 mm from the other, with 3 mm kerf.

The seven hubs clamp 12 mm 304 shafts with no transverse holes. Center-drill and tap both ends M5×0.8: 4.2 mm pilot 16 mm deep and at least 10 mm usable full thread. Each M5×12 end bolt uses the exact 20 OD / 6 ID / 2 mm 304 keeper and one 0.8 mm M5 flat washer, giving nominal 9.2 mm engagement. Verify at least 8 mm engagement and 0.8 mm bottom clearance before tightening. The eight keepers are uxcell B0DYK1PVYB. The end bores overlap some terminal hub seats and are included in the conservative section screen and actual-seat proof; they do not extend into the free interhub spans.

Ream each hub bore, saw the 1.5 mm slit and drill its two clamp bores along X at local Y16, Z6/19. Each uses two grade 12.9 M4×50 bolts. Use the specified LEXIVON cam-over tool with H3 bit clockwise at the head while holding the locking nut: alternate 10, 20 and 25 in-lb stages. The final 25 in-lb setting is 2.8246 N·m nominal and 2.9376 N·m at the stated +4% upper error, below the absolute 3.0 N·m ceiling. Prevailing nut torque is included. Never increase the setting to rescue failed grip.

Every hub is the ungripped specimen on its own marked completed shaft seat in the supported 140 mm proof fixture. The companion hub has a visible 1 mm face gap, the vise grips only its bolted metal reaction plate, and end keepers/tubes cannot touch or bypass the specimen during torque proof. Accept the entire measured torque interval in both signs: 30–32.5 N·m for the pitch drive-lever hub and negative-side pitch output hub; 25.2–27.5 N·m for the other five hubs. Repeat after 50 supervised reversals at the qualified settled temperature. Any witness slip, residual twist or resolved straightness change rejects the joint or shaft.

Fourteen 20 OD / 12 ID capture tubes, finished to 12.5 mm bore, positively bound shafts and hubs against their actual bearing inner-race faces and end keepers. The cut table gives each nominal length; finish the delivered stack for at most 1 mm captured movement with no outer-race/seal loading or rotational rubbing. The keeper radius is 10 mm; the nearest M5 mounting washer envelope leaves 1.40 mm radial clearance. Bearing setscrews and hub friction alone do not qualify axial capture.

Use the symmetric axial capture fixture before carrying a gun. A 100×60 mm interface clears the keeper through its 22 mm aperture; four 75 mm tubes and borrowed M3×100 ties place the closed bridge beyond every actual keeper/head. One captured M6×16 bolt, a 1 mm washer and the bought B0DHGXW6G9 20 mm M6×1 coupling nut join the gauge load shaft directly. Measure at least 6 mm engagement at each end without bottoming. The slotted 70×160 backing and manual jack provide both signs: quill moves the body toward the bridge for compression; with quill withdrawn, jack moves it away for tension. Accept the full 450–500 N force interval for ten seconds in each sign, with hub clamps and bearing setscrews free, no friction bypass, no catch contact and no permanent change. The source-bound fixture and per-hub near-face table in requirements govern placement and hardware reuse. Independent joined catch plates retain the interface with nominal 0.75 mm gaps and clear the shaft.

All 8 OD tubes use the sourced 6 mm bore. They carry metal clamp loads between plates, including the single-nut frame, force cages, crash ties, guard/keeper spacers and roll feet. M6 base/gauge spacers and KP08 risers use 10 OD / 8 ID tube. Hinge, swivel and redirect inner-race contact tubes are drilled to 8.5 mm ID. Use the actual purchased 22 mm smooth shank to finish the nominal 9.65 mm hinge thread-start spacer. A washer must cover its tube bore; the separate M4 riser washers have at least 10 mm OD.

The complete joint schedule governs hardware, including the 149 small angle slices and 40 mechanical corner brackets (two are temporary test-column braces). Matched purchased 40-series corner brackets use their included M8×16/slot8 hardware. Plate and fixture connections retain their specified M6 hardware. Keep at least two full threads beyond lock nuts, with no bearing riding on screw threads and no clamp load through an empty gap.

The small angles include 137 ordinary pieces and six each of the two guard-thrust variants. Fit each right-side upper thrust angle to its shared M6 post, then transfer the registered 3.4 mm guard passage through its foot. Bulkhead holes are at (±5,13); printed guard holes are at local (±5,−7). The 7 mm metal spacers and M3×25 bolts include the angle foot in their grip. The M3 and M6 washer envelopes stay clear.

Fit the capture fixture to the unplugged press by relative height. Its canonical cap is 455.7 mm above the column-base datum. Positively anchor the column below the press work surface as needed to align the coupling and leave at least 10 mm downward quill travel at mid-stroke. Use matched brackets and the independent anchored catch. Loose blocks and hand support do not provide the fixture's reaction.

## Print treatment

Print rigid rows in PET-GF and the registered insulating gun pads in TPU. Use an abrasive-resistant 0.4 mm nozzle, 0.20 mm first layer, 0.24 mm normal layers, six walls and six top/bottom layers. Use 40% gyroid; bodies no thicker than 4 mm are solid. The manifest gives the orientation. Dry and process the actual material according to its manufacturer's instructions.

Use accessible supports under functional bearing-pocket ceilings and saddle undersides as required by the native slice. Remove them through the open pockets and inspect contact surfaces. Before accepting a print, inspect first/second-layer bead overlap and accessible support contacts; saved layer heights alone do not accept those surfaces.

The printed parts locate and protect purchased metal. Main guides, screw/nut load paths, thrust reaction, gimbal shafts, clevises, overload shoulders and gun jaws are metal. The 80-tooth pulley is a printed transmission part: grade the tooth coupon with the actual GT2 belt, then qualify loaded response and warm operation. A nominal tooth profile and saved print recipe do not establish drive margin, wear or lifetime.

The two swivel saddles and redirect wheel have open bearing pockets and separate outer-race caps. Fixed M8 axles clamp metal tubes and the 608 inner races; rotating prints carry the outer races. Check free rotation and clearances cold and warm. The fiber remains in a loose padded sling. No saddle clamps the optical cable or establishes its routing acceptance by itself.

## Travel and load gates

| Axis | Soft range | Switch | Metal bound |
|---|---:|---:|---:|
| X / Y / Z | −85…+85 mm | ±89 mm | ±94 mm |
| Yaw / roll | −20…+20° | ±21° | ±22° |
| Pitch | −20…+10° | −21…+11° | −22…+12° |

All angular screw geometry uses a 150 mm lever and 180 mm neutral actuator length. The drive produces 6,400 nominal command pulses/mm at the fixed microstep setting. Its 2.5 µm full step is a command scale, not measured gun accuracy. Positive Z shortens the top-supported screw; ordinary gravity places that screw in tension.

| Force-link direction | Seat preload | Accepted static trip | Powered peak ceiling |
|---|---:|---:|---:|
| Yaw / roll, either sign | 100 N | 100–140 N | 140 N |
| Pitch, either sign | 130 N | 148–165 N | 165 N |
| X / Y and upward Z | 250 N | 250–350 N | 350 N |
| Downward Z | 400 N | 440–500 N | 500 N |

These are measured force gates including uncertainty. The nominal springs have 20 mm free length and 43 N/mm rate, with electrical trip at 0.30 mm angular or 0.75 mm XYZ and metal capture at ±1.0 mm. Grade each directional spring pair and finish its four matching metal spacers; leave the 8.35 mm center capture spacers unchanged. Maximum nominal compression at capture is 2.163 mm yaw/roll, 2.512 mm pitch, 3.907 mm X/Y/upward Z and 5.651 mm downward Z. Every actual spring must remain below the catalog 8 mm compression and at least 1 mm short of its measured solid height.

Static trip acceptance and powered force ceilings are different gates. A low-current stall below preload establishes only a measured ceiling. Observe it, stop and abort; do not increase current to force a trip. Separately opening the hardware loop must inhibit and latch all six axes. Any capture impact, yielding, bow, unsupported load, repeated powered retry or unexplained response fails commissioning.

Independent dry friction retainers use the unoccupied fixed-nut flange on Z, pitch and roll. Accept complete measured torque intervals inside 0.20–0.23 N·m Z, 0.06–0.08 N·m pitch and 0.02–0.04 N·m roll, including the characterized redirect and mass/radius/alignment uncertainty. The measured minimum also exceeds twice the actual ideal backdrive bound. In particular, the 100 N pitch screen requires at least 0.063662 N·m before additional uncertainty; the lower 0.06 band edge alone does not accept that load.

Measure actual carried load with the supplied fixtures. The installed Z gauge uses an independently braced 500 mm test column, metal platen and M6 feed jack. Its guide screws retain laterally while permitting smooth feed, at most 1/12 turn (0.0833 mm), with an independent catch within 1 mm. The separate balanced angular-load-lever replaces only the drive-lever hub plate; the carried-mass output hub and actual gun/cable stay installed. Actuator clevises disconnect only after gauge/cord and independent support restrain the rotor. Both signed onset thresholds include gravity, cable free couple and bearing resistance. Restore all joints and a fresh observed datum after testing.

The sizing envelopes are 300 N normal Z force, 100 N normal pitch actuator force and a 15 N·m pitch shaft/hub screen. Upward obstruction compression is bounded by 350 N. These are engineering assumptions subject to measured load and retention gates. No catalog holding torque, Euler calculation or CAD mass total accepts the machine.

The gun release combines two seated axial pods and three steel ball/dowel magnetic contacts. Grade added nozzle release force in both axial signs and transverse directions with the real cable and gravity baseline. Accept the complete force interval within 20–30 N using qualified weighed cups and the characterized redirect. The 500 N gauge cannot by itself accept this narrow low-force band. Four independent contacts open the hard and sense channels on axial trip or missing/separated plate. Independent short tethers and a padded metal catch retain the released gun. Release removes positioner power; the operator stops the independent pedal rotator during dry tests.

## Clearance and acceptance scope

The finite proxy/vessel screen checks 360 correlated poses: yaw and roll −5/0/+5°, pitch −10/−5/0/+5/+10°, and all endpoint offset corners at ±0.25 mm. Its sampled minimum gun/vessel separation is 5.555 mm; subtracting the measured mesh edge and tessellation allowance gives a conservative sampled-surface lower bound of 4.462 mm. The consumable wire's intended seam contact and the gun's own clamped-pad contacts are excluded explicitly.

That screen clears only the unscanned gun body/nozzle/handle proxy against the complete vessel-cylinder envelope at those samples. It does not clear the full assembly, release tray, clamps, cameras, lenses, cables, an actual gun or the continuous path between samples. The full independent travel envelope includes vessel collisions. Remove the vessel for unrestricted dry commissioning. A physically accepted correlated subset, actual two-view tool datum, cable routing and retained-load test govern any seam path.

Power-cut holding is screened for ten minutes at actual accepted loads and worst poses, with no observed jump, catch contact or growth resolved by the owned 12.7 µm indicator. This is coarse holding evidence and cannot establish 5 or 10 µm accuracy. Repeat retention, response and datum checks after wear, adjustment, cleaning, releases and thermal settling. The temperature reading plus uncertainty stays at or below 50 °C, with no growing trend beyond documented measurement uncertainty across three consecutive five-minute intervals.

Physical observations and acceptance records belong beside these assets and are indexed from the repository's mechanical qualification records. Empty or absent records mean the corresponding claim remains unaccepted.
