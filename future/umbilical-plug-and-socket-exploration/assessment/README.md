# Umbilical connector engineering assessment

Reviewed 2026-10-09. **Recommendation: keep the separate connections for shipping and
assess protection and confined-space use before buying this connector's missing hardware.**
The [tube-protection review](protection.md) gives a bounded geometric candidate: four
integral open fences which pass the counter hole and clear the existing unions. Its
rounded edges leave only 0.519 mm nominal clearance ahead of the tubes against a broad
flat surface; narrow corners can still reach them. It is a prototype candidate, not
established durable protection. The saved [coupling](../tactile-trial/README.md) and
[guided boot](../guided-boot-trial/README.md) prints omit that protection and only assess
their stated plastic-fit and bundle-packing questions.

The operating requirement is shutdown and depressurization before unplugging. This design
uses ordinary open unions; removing the plug leaves their ports open. A shutdown/depressurization
procedure belongs to the eventual customer experience.

## Customer outcome and evidence

The intended benefit is one obvious, correctly oriented connection for four fluid lines and
the display, with comfortable insertion, an unmistakable fully connected state, and intentional
removal. It must retain that state when the umbilical hangs, bends or is handled. The boot must
hold the tube projections, protect the cable and transfer bundle loads without damaging tubes.
The exposed tube ends must remain straight and usable after ordinary confined-space
handling. The complete assembled, protected machine end must pass through the existing
34.93 mm countertop hole; a larger guard attached after passage is outside the accepted
installation requirements. The current guarded candidate needs 126.3 mm of straight
rigid approach room before braid bending or hand clearance.

The main benefit belongs to installation and machine removal. The current
[user operations](../../../hardware/README.md#user-facing-surfaces) do not require unplugging
this bundle to dispense or refill flavor. That makes it reasonable to protect the shipping
design while assessing this improvement independently.

[CPC's Multi-Mount](https://www.cpcworldwide.com/General-Purpose/Products/Multiline/Multi-Mount)
demonstrates a commercial three-to-five-line connection with a keyed interface and a thumb
latch. That establishes the product idea's feasibility. It does not qualify this mechanism,
which reconnects ordinary tube ends to four independent push-fit unions. Commercial connectors
are a useful engineering reference; no purchase or substitution is selected here.

| Design element | Supporting evidence | Present limit |
| --- | --- | --- |
| Fixed plate releases a moving union | [Owned tee observations](../../../hardware/reference/tee-connector/README.md) support holding the collet continuously while withdrawing the tube. | Different fittings, four simultaneous connections and the complete boot have not been tried together. |
| Pogo seat and compression | [Accepted contact coupon](../../../hardware/reference/yyfkgcp-pogo-4p/physical-observations.json) establishes its reported fit and mating. | This plug's alignment, continuity and retention are separate properties. |
| Snap-in frame and receiver | Two leaves, flange bearing and a stepped 6 mm wall coupon are modeled; the native tactile slice emits no supports. | No physical snap result or integrated back-top receiver exists. Supports being disabled alone does not prove a successful roof print. |
| Four-line seating, grip and retention | Their geometry is drawn. | Forces, full seating, tube slip, installed magnetic retention and repeated operation are unestablished. |

Accepted results keep the scopes in the [mechanical evidence register](../../../hardware/mechanical-qualification/README.md).

## The main engineering problem is consistent seating and release

The socket guides the plug before its protruding tube ends reach the release plate. On insertion,
the tubes push each floating union back against the retainer. On removal, each union moves
forward until the plate holds its collet; its body then moves enough to release its tube.
This is a reasonable mechanism to investigate.

The axial stack combines tube projection, fitting insertion depth, collet projection and stroke,
union float, retainer position, plug stop and pogo compression. Every line must seal before
the assembly feels seated. A tube key must preserve all four projections while the unions
resist insertion. The machine-side tubes need enough compliance for the unions' release travel.
Drawing clearance between solids does not establish those behaviors.

The guided boot uses a nominal 26.3 mm quarter-inch projection to reach the modeled
fitting stops. [John Guest's instructions](https://www.johnguest.com/sites/default/files/files/how-to-connect-jg-od-fittings.pdf)
require clean, square tube ends, insertion to the stop, a security check and installed pressure
testing; grip can occur before sealing. A functional revision needs full insertion on every
line across its actual dimensional variation. Nominal projections do not qualify the four-line
tolerance stack. The saved coupling tactile article has different, illustrative projections.

The missing 4 mm union leaves its insertion depth, collet diameter, projection and release stroke
unconfirmed. Those values determine whether its retainer boss locates it properly and whether
the same release plate operates it. The [current neoFit listing](https://www.freshwatersystems.com/products/neofit-acetal-black-union-connector-4mm-5-32-tube-x-4mm-5-32-tube)
does not supply that complete release geometry. Dimensions from John Guest's different 4 mm
part are provisional reference values. The guided scene uses a 1.8 mm-proud drain collar
and a nominal 24.1 mm projection to its assumed stop. It is not an assembly specification.
No additional founder measurement is requested without the part.

The guided boot's key targets 0.15 mm intrusion into each tube after it bears on its guide.
The modeled quarter-inch wall is about 1.02 mm and the drain wall is 0.75 mm. The final
Ø6.65/4.20 mm guides use the accepted organizer L diameters, but its 10 mm physical result
does not establish friction or retention through this boot's longer curved path. Feed force,
tube ovality, scoring, creep and axial slip require handling evidence. The fabric cuff targets
frictional retention; there is no separately qualified jacket or cable strain relief.

Orientation currently relies on a 1/4-inch stub failing to enter the drain's 4.3 mm hole,
plus the intended magnet/pogo orientation. The plastic profiles themselves are symmetric.
For a finished consumer connector, an obvious key that guides orientation early and a clear
fully seated indication are desirable. Their need can be assessed during the tactile trial.

Depressurization does not empty the tubes. Residual liquid and condensation need a managed
path because the fluid ends and exposed display contacts share the mating area. Open ports
also need a practical handling/storage procedure. These are part of the complete connector's UX.

## Magnetic retention needs a corrected fit and an actual load basis

The [SB443-IN drawing](https://www.kjmagnetics.com/resources/pdfs/SB443-IN.pdf) specifies a
0.063 +/- 0.010 inch groove height: nominally 1.600 mm, with a permitted minimum of 1.346 mm.
The modeled rail is 1.500 mm high. It cannot fit every permitted groove even before print
variation. Groove-position tolerances also matter. A functional revision must accommodate the
complete supplier envelope or an explicitly controlled part lot; nominal clearance is insufficient.

[K&J's 3.42 lb rating](https://www.kjmagnetics.com/sb443-in-neodymium-stepped-block-magnet)
is attraction to steel, not an established retention force for this installed pair. Its published
maximum operating temperature is 80 C. Printing over a magnet does not establish its temperature
or retained performance.

The actual load path is bundle to boot/key, tubes and plug, unions/release plate, retainer,
socket and enclosure wall. Magnetic retention must tolerate the relevant pressure and bundle
loads while remaining comfortable to remove after depressurization. The claim that opposing
tube forces automatically keep the floating unions stationary is not an adequate design basis.
Installed force versus separation, tube/bundle routing and pressure state must be considered
together. A nominal steel pull number cannot establish that margin.

## Foam compression belongs in the boot design

The founder [reports that the purchased foam is quite compressible](../../../hardware/reference/cargen-pipe-insulation/physical-observations.json)
and intends the boot to compress it. The [guided boot](../README.md#plug-side) uses a round
Ø34 mm rear body and arranges the entry tubes around the insulated soda line. The two flavors
sit above it; the drain stays to its right and below the flavor tube. No tube crosses another.
The braid surrounds the tubes, foam and ribbon and tucks 15 mm into a tapered cuff.

Inside the boot, a 45 mm quintic transition gradually guides each tube to its final square
formation, with parallel tangents and zero curvature at both ends. The 38 mm straight nose
has guide bores on both sides of the 12 mm tube-key opening. Foam follows the soda tube
through the cuff and halfway through the transition. Its intended insulation wall is 5.025 mm
at entry and 3.475 mm at its end, against a purchased nominal 9.525 mm wall. These require
roughly 47% and 64% radial wall compression. The shaped foam is an intended envelope,
not a clipped solid or a material deformation prediction.

The [native record](../boot-packing.json) binds the geometry and checks the actual solids for
intersections, including the ribbon. Internal minimum centerline bend radii are approximately
168 mm for each flavor, 39 mm for soda and 33 mm for the drain. These nominal paths exceed
[neoFlo's published minima](https://assets.freshwatersystems.com/image/upload/s--N9disqrx--/gjtidjfc0tlprqbhb4ka.pdf)
of 25.4 mm for quarter-inch tubing and 25 mm for 4 mm tubing. The real fed tubes have not
been observed in this boot. The modeled packing transition outside the cuff is illustrative;
the user's actual bundle can take a different shape.

The boot is 98 mm long, with 34 mm inserted in the existing port and 64 mm remaining outside.
A 4 mm chamfered shoulder marks the insertion depth. At the mating-face stop the shoulder
is 0.3 mm clear of the socket mouth, avoiding a competing stop. The maximum rigid Ø34 mm
section leaves 0.465 mm nominal radial clearance through the existing Ø34.93 mm counter hole.
The loose foam/braid envelope still requires compression while passing through that hole.

A tactile boot print should answer whether the 98 mm body is comfortable, each real tube can
be fed without kinking, and the foam and braid can be tucked without damaging the cable.
It must also show whether the straight outlet positions and tube projections survive the
bundle being bent and handled. The visible shoulder should align with full mating-face seating.
The owned quarter-inch tubes, foam, braid and cable are sufficient for that limited trial;
missing drain tubing, magnets and the exact union limit its coverage. The saved coupling
trial omits this guided boot and cannot answer its compression or feed questions.

Foam recovery, heat gain through the exposed final soda run, braid pull-out force and long-term
tube grip remain unqualified. Those limits do not require a purchase or founder measurement
before handling a prototype. An acceptable tactile result would justify a functional revision
with exact hardware; it would not establish sealing, magnetic retention or lifetime.

## Machine placement of the 81 mm inward reach

The socket and retainer reach 81.36 mm inward from the rear wall's inner face. The
[native placement record](geometry-review.json) intersects their actual solids with the
current exported machine, excluding enclosure geometry to be redesigned and connections
this connector would replace.

| Provisional wall center, machine X/Z | Result |
| --- | --- |
| -59.39 / 302.62 mm, centered on the existing connection field | Intersects the drain vent tube and 1.42 mm3 of the neighboring water-port ring. No other retained body intersects in this placement. Rerouting the drain and resolving the ring overlap appear feasible. |
| -59.39 / 326.50 mm, higher in the same lane | Intersects the backflow assembly, water bulkhead, flow sensor, water-port ring and carbonated-water tubing. It is unsuitable with those parts in their current positions. |

This makes the depth a manageable integration question rather than an unexplored obstacle.
It is not an exhaustive location search. Internal tube routes, wire routes, assembly sequence
and structural enclosure stock still require design. The coupon's support-free receiver intent
and snap geometry do not qualify the complete back-top. Production enclosure geometry is
unchanged by this exploration.

## Simplest geometry

The [protection review](protection.md) rules out a fixed closed shell around the current
unions within the counter hole. Its open-cage candidate uses one annulus, four fitting
keepouts and rounded contact wings, with no extra separate part, motion mechanism or
wet joint. The keepouts earn their shape from mating clearance; the rounding removes
fragile mathematical points. This is a simple nearby candidate, not a proof of globally
minimum geometry or complete protection. Its socket is 2.4 mm wider and needs matching
receiver geometry; production back-top remains unchanged.

The round rear boot has one outer perimeter edge per cross section. Its nose and socket
profile earn their shape from the counter hole, mating guidance and sloped receiver roofs.
The flange, two snap leaves, union-retaining plate and tube key have named jobs.
These are a sensible starting structure, with no decorative geometry needed.

The retainer prints on its face and does not need the socket's sloped roof profile. A plain
round perimeter can reduce its outer outline from eight edges to one. Preserving all existing
blank stock takes about 44.68 mm diameter, increasing width about 3.68 mm and height 1.08 mm.
That is a modest simplification candidate, not a solution to the connector's functional risks.
The tactile plate retains the current retainer so it tests the drawn assembly.

The larger simplification opportunity is a reliable, toleranced seating/release mechanism and
a single clear bundle load path. Extra detail added to compensate for uncertain fitting geometry
would make this harder to manufacture and use. The current design cannot yet be called complete
or the fewest-edge design that meets every requirement.

## Decision after handling it

The guarded candidate is CAD only. Its printed contact envelope and stiffness need
assessment before the connector can claim protected handling. The saved unguarded
boot can answer packing questions but cannot qualify tube-end protection. The
[bounded next-evidence procedure](protection.md#useful-next-evidence) defines what a
guarded handling screen would decide using owned materials and three quarter-inch unions.

The [coupling trial](../tactile-trial/README.md) and [guided boot trial](../guided-boot-trial/README.md)
can answer whether the grip, cup guidance, snap frame and real bundle transition are worth
pursuing with no missing-hardware purchase.
It intentionally does not reproduce magnetic retention or qualify complete four-line operation.

If the size or transition is awkward, keeping the separate connectors is a justified product
choice. If the experience is attractive, the next bounded development step is an exact-hardware
functional prototype: correct the magnet fit, establish full seating and release across actual
fitting variation, provide jacket/cable strain relief and resolve the provisional machine location.
Subsequent operating evidence must cover the machine's actual pressure/temperature range,
handling and repeated connections, including leaks, tube movement and electrical continuity.
The acceptance target is consistent complete engagement and intentional release without
individual-line adjustment. A lifetime or retention-load claim needs application-specific
evidence; no arbitrary cycle count or force threshold is assigned here.

These future checks are conditional development work. Nothing in this assessment adds a
machine-build check, hook or recurring verification requirement.

## Reproduce this review

Run only when revisiting the questions answered here:

```sh
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/assessment/geometry_review.py
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/assessment/review_guided_boot.py
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/assessment/prepare_tactile_trial.py
tools/cad-venv/bin/python future/umbilical-plug-and-socket-exploration/assessment/prepare_guided_boot_trial.py
```

The placement record binds the current native machine and source hashes. The tactile print
record binds its source meshes, editable project and freshly emitted archive. No job is submitted.
