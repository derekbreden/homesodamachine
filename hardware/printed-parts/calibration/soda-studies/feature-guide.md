# The Pour — Service Section

This is an appliance-shaped print reference. Its four shell sections enclose a working drawer, tee-release column, plumbing seats and service openings. A complete faucet stands on its own counter plate and gasket. The native joints hold the parts; the drawer crossmembers, faucet neck bands and captive rear dust shutters provide the deliberate comparisons.

The [full feature map](fullfeature-map.json) maps all 83 inventory entries to source builders, native roles, mates, print orientation and current part hashes. Some entries describe the same geometry, its material or a process condition. They are not 83 separate mechanisms. The assembly is unprinted; the source physical records below apply only to their identified articles and properties.

## Print identity and coordinates

Use the prepared native projects and their material assignments. All individual manufacturing meshes use millimetres, XY as the bed and +Z as the build direction; their source rotations are already baked in. The assembled viewer is a reading pose. `back-top` prints with world −Z upward, whereas the other three shell sections print with world +Z upward. The complete faucet body `FB` uses source X −15°, tip `FT` −105° and relaxed cover `FC` −50°. Keep registered colour volumes together in their shared frame.

World −Y is forward, +Y rearward and +Z upward. “Per side” or “per face” means the air at one named face; a diametral allowance applies across the entire diameter. A nominal CAD gap, a commanded native deposit gap and a physical gap are separate quantities.

The rigid parts use their PET-GF object recipes. The full `FB` neck uses Arachne, aligned seams and a 15% regular gap. The selected tee surface and `R30`/`R45`/`R60` source roofs use Classic. The cabinet `front-top` uses 0.08 mm layers throughout its 60 mm body after the 0.20 mm first layer. Other inward/top rounds and expanding downward rounds have distinct local layer/wall treatments; retain those regions when changing material.

The three compliant parts are separate print cohorts:

| Part | Geometry and source recipe |
| --- | --- |
| `FG` | Full 2 mm counter gasket; TPU 85A, 0.6 mm nozzle, 0.30 mm first / 0.18 mm body, nonspiral Arachne, two walls and 100% infill. |
| `FS` | Full donor-port thimble; TPU 85A, 0.6 mm nozzle, 0.30 mm first / 0.18 mm body, Classic spiral, one wall, 0% infill, zero top and three bottom layers. |
| `display_gasket_90A` | Separate 1 mm ring; the prepared white TPU 90A source profile uses a nominal right 0.6 mm nozzle, 0.30 mm first / 0.18 mm body, Arachne, two walls, 100% zigzag infill, three top/bottom layers and supports off. Its compression is unmeasured. |

The nameplate uses the current face-up flat-wing geometry, with a 0.20 mm first layer, 0.28 mm second layer and 0.24 mm remaining layers in its registered project. Its 0.48 mm raised artwork retains the full wordmark, faucet-drop mark and QR quiet border. DATA and the port chips retain their own registered volumes and closing schedules. On Mark2, the right nozzle's source correction is X −0.50 / Y +0.70 mm. CO2 uses white on the left and red on the right; preserve the correction on the red body. `TC` has flush SODA lettering: its source preview is blue, while the reviewed native project uses black/white.

## Open, inspect and reassemble

Keep the shell supported while working on one joint. Release its native fasteners before sliding a shell section, and detach tubes/leads that cross a service boundary before moving that assembly. The [assembly review](assembly-review.json) binds these sampled rigid motions to the current parts; physical release force and repeated handling remain unmeasured.

1. Withdraw `front-top` forward along world −Y through 72 mm to disengage the complete source rail, then lift along +Z and set the display/facet section aside. The nominal lift is clear through the sampled 60 mm. This exposes the full drawer pull and forward cartridge opening.
2. Withdraw `pump_drawer`, its fitted `pump_cap` and all three bolted roof crossmembers together along world −Y, through 175 mm. The nameplate stays on the forward fascia. Keep the two native M3 × 60 clamp screws fitted during whole-drawer withdrawal.
3. With the drawer outside the cabinet, remove those two clamp screws to lift `pump_cap` along world +Z. To inspect a support underside, unbolt the corresponding `R30`, `R45` or `R60`. Each roof uses two M3 × 8 screws and inserts in the moving floor pads. Remove its supports with the roof loose, through either open Y end of the complete lifting profile.
4. After `front-top` is removed, raise `vertical_window_cover` 22.5 mm along world +Z to clear its native tongue/post, then move it inward toward −X. The tee column's native release moves 2 mm toward −Y. For extraction, remove the window cover, disconnect the tee's actual tubes, move the column 10.896 mm toward +Y to staging, then 40 mm outward toward +X. Record spring return separately from the accepted low-force slide.
5. To remove `removable_plumbing_lid`, first remove `front-top` and withdraw the drawer. Release the handhold grip and lower/middle Y-joint fasteners, then slide `front-bottom` 130 mm forward along world −Y and set it aside. The complete lid can then slide 37 mm toward its local −Y before lifting 30 mm along +Z. Keep the full hook, catch, stop, front-right cabinet rail and R20/R27 bearing quadrant intact.
6. With `front-top` set aside and the upper seam screws released, slide `back-top` toward world +Y. Its surviving source Z rail disengages at 82.2 mm; continue to 112.25 mm so the lower plumbing ceiling clears the rear wall, then lift along +Z. The nominal lift is clear through the sampled 80 mm. Its faucet/counter stack, registered DATA/port faces and captive flags belong to this service section. Retain the faucet fasteners, support the complete section and detach crossing plumbing/leads before moving it. `FO`, `TC` and both tied neck controls remain on the disconnected lower bundle; they do not move through the counter passages.
7. The complete `handhold_grip` bows at its centre to engage or release one end wing, then the other. Preserve the full 84.5 mm span. Use each nameplate, DATA and display plate's own entry bevel, retaining lip and push-out or support-exit access. Clear supports before seating the plate.

Reassemble in the reverse service order, with the source floor scarf and telescoping Y lips fully seated before fitting the joint fasteners. The source curved `FB`/`FT` lap retains its complete socket and plug. Print `FC` in its relaxed manufacturing shape; the viewer's seated elastic cover model is a separate source representation. Read its broad-wall snap and residual bow on the complete cover.

## Read a feature and act on it

Use the same light and viewing angle when comparing surfaces, then touch the relevant face or operate its actual mate. Record the filament, drying and prepared recipe with the object ID. A useful result ends in a local setting to try or a decision to retain that feature's present setting.

| Object or location | Read | Setting or assembly action | Record |
| --- | --- | --- | --- |
| Shell skin, corners and vents | Groove crests, smooth fades, corner phase and complete open vent cells. | Retain the native 4 mm groove, 1.2 mm depth and 5 mm fade. The compact field closes with 181 grooves at 5.123747 mm pitch. Compare wall paths and the actual local layer schedule before changing the skin. | Surface, orientation, light, blocked slot or ragged edge. |
| Facet, roof and rolled shoulders | Stair stepping on the 30° facet, inward/top R6/R12/R18 curves and expanding lower rounds. | Apply fine layers to the actual inward/top span. Preserve the expanding underside's additive profile, normal local layers and six-wall region. | Exact face and finish preference. |
| Shell Y lip, floor scarf, Z hook and M3 cross pins | Seating, seam, catch and running play. | Clear debris and follow the source direction first. Change the relevant static/running/supported-face allowance only at the identified bind. Enclosure M3 heads are Ø5.8 × 3.5 mm; faucet mount heads have their own Ø6.15 datum. | Bind location, seating and remaining play. |
| `handhold_grip` and its receiver | Support cleanup, bow, wing capture and touch edges. | Retain the selected full strip/receiver dimensions and the actual supported ceiling recipe. | Insertion and residual bow; keep lifting load separate. |
| `R30` / `R45` / `R60` | Release effort, underside scar and sag on the same complete 80 mm opening / 35.25 mm ceiling / 12 mm roof. | Compare the requested 0.30 / 0.45 / 0.60 mm top distances with XY/interface settings held fixed. Select the useful cleanup/finish compromise for the material. | Requested rung, current commanded air and actual underside result. |
| `FB`, `NR00`, `NR05` | Layer texture and the ridge or groove at the seam. | Use the identified band or regular-gap control below. Keep the source wall generator and recorded layer height visible in the comparison. | Band/control code, touch, appearance and preferred setting. |
| `Q24` / `Q48` / `Q72` | Whether the solid-skin captive foot releases and completes its 26 mm X travel. | Read it off the bed first, then gently try the intended raised flag. Choose a useful Z rung with the lateral gap fixed; keep support-interface results separate. | Free off bed, gently freed at the handle, or fused; then travel/bind location. |
| Nameplate, DATA, TAP, CO2, OVER and TC | Full strokes, body/ink registration, raised edge or flush word. | Keep source material slots, closing layers and nozzle correction. For a QR scan, inspect quiet border and deposition as well as the artwork. | Exact volume/edge, scan conditions and decoded URL if actually scanned. |
| Display bezel, 90A ring and nominal backer | Flush seating, bow, both wing catches and dry stack capture. | Use the complete native support exits and display-specific 0.60 mm wing air. Keep the 90A recipe distinct. | Seating, bow, cleanup and compression. |
| Pump well, cap, M3 hosts and full side pull | Actual pump location and clamp access through the full service opening. | Use both source clamp screws and intended inserts; withdraw the drawer before lifting the cap. | Pump movement with fasteners seated and service access. |
| Pogo pair and sealed RC62 pockets | Connector ear/lead fit, compression, magnet insertion and docking. | Retain M1.4 datums, native pause planes and C3 pockets. Actual continuity and magnetic retention require their own observations. | Fit, compression, continuity, rattle and seating as separate results. |
| Tee shoulder, journals, trough and spring tunnels | Tube release/relock, low-force slide, tilt and return. | Preserve the selected 1.00 mm roof / 0.25 mm floor air and whole tee/tie route. | Slide, return and actual collet operation separately. |
| Valve posts, loom clip, tube anchor and hardware seats | Real valve, braid, tube/fitting, Wago, RJ11 and C14 seating and access. | Use each stated hardware family and full native seat; V69 is the selected valve socket, with V70 only when the actual valve does not fit V69. | Part identity, seating, tie/lead path and latch access. |
| Flow/ASSE roof, PRV chase, MQ6 chute, cold-core and condenser seats | Paired collar/body seating, common tie exits, card route and native contact lands. | Keep the matched roof rooms open and the full active seats rooted. Use actual hardware before making an operating claim. | Housing/contact seating, exit openness and cleanup access. |
| `FB` / `FT` / `FC` | Real bend flanks, supported shoulder recovery, curved lap, snap and thin bezel. | Retain source orientation and complete flexing spans. Compare support scar and layer recovery on the actual source face. | Face, supported region, seating and residual bow. |
| `FO` and `TC` | Individual beverage/drain bores, flat signal slot and horizontal tube grip. | Use the separately selected Ø6.65 / Ø4.40 organizer bores. Tune the 5.4 × 1.8 mm signal slot from its own fit; record TC's PET-GF tube fit directly. | Each line's seating and the actual slot/collar fit. |
| `FPD`, `FG`, `FS`, `FL` and counter passages | Plate/gasket seating, native shank/pill/ribbon routing, thimble elasticity and lever snap/swing. | Retain the 4 mm plate, 2 mm 85A gasket, all three M3 axes and separate passages. Use the thimble's saved spiral recipe and the full side-down lever. | Compression, passage, snap and travel; sealing and valve function separately. |

The three supported roofs are bolted to the moving fore-floor at world Y 20, 48 and 76 mm. Their underside is world Z 47.50 mm, or nominal manufacturing Z 35.25 mm above the foot plane. The end bolts and 13 mm feet remain outside the full active opening. The moving pads provide 6.25 mm of total insert stock, with Ø4 mm pilots 5.7 mm deep and a 0.55 mm blind floor. These new fastened crossmembers are unprinted.

## Neck comparison key

Read `FB` bands in manufacturing print Z, measured from its baked STL bed plane. The visible assembled neck is rotated relative to those layers. Read the interiors at least 0.48 mm from a band boundary; layer transitions themselves answer a different question.

| Band | Manufacturing print Z, mm | Comparison |
| --- | --- | --- |
| LH080 | 76.04–84.20 | 0.08 mm layers, aligned regular gap 15%, no scarf. |
| LH120 | 84.20–92.36 | 0.12 mm layers, otherwise the same height comparison. |
| LH240 | 92.36–100.52 | 0.24 mm layers, otherwise the same height comparison. |
| REG15 | 100.52–112.04 | 0.24 mm layers, regular gap 15%, no scarf. |
| SCF00 | 112.04–123.56 | 0.24 mm layers, external scarf gap 0%, regular gap 15%. |
| SCF10 | 123.56–135.08 | 0.24 mm layers, external scarf gap 10%, regular gap 15%. |
| SCF20 | 135.08–146.60 | 0.24 mm layers, external scarf gap 20%, regular gap 15%. |

All these bands use Arachne and aligned seams. The external scarf bands use a 10% start height, 10 mm minimum length and ten steps; inner walls retain their normal seam. The native paths contain the requested scarf Z ramps. The two source shoulder bands at print Z 13.4–29.0 and 55.16–68.12 use 0.12 mm layers independently of the straight-neck comparison.

`NR00` and `NR05` are unchanged short source necks, with Arachne, aligned seams and no scarf. Only their regular gap changes, to 0% or 5%; their fine comparison span is print Z 4.04–16.04 at 0.12 mm. Mark the code on the cut face or adjacent native anchor after printing. Their below-counter reference bundle uses the source neck sizes: water OD 9.525 mm, two flavour lines OD 6.35 mm, drain OD 4 mm and ribbon 4.6 × 1.18 mm. The passage is one smooth shared hull. Source-convention nylon straps, 1.0 mm thick and 4.8 mm wide, loop around the four round tubes and complete ribbon lane at both ends of each neck. The nominal loop is larger than the shared opening and does not overlap the cable. Actual strap size, tightening, axial grip and tube/cable compression remain unmeasured. A short section's cooling and print time differ from the complete neck.

The two water tube sizes belong to different line sections. In the [native faucet routing](../../../assembly/faucet-and-umbilical.md), the upstream blue umbilical is OD 6.35 mm and enters the donor's lower compression port. A separate OD 9.525 mm soda tube leaves the donor's top through `FS` and runs through the gooseneck. `FO` has three Ø6.65 mm beverage bores for the 6.35 mm upstream tails; `TC`'s Ø6.68 mm SODA bore identifies that upstream tail. The below-counter `NR` bundle is a dry reference of the larger neck section, kept separate from the `FO`/`TC` supply tail. The 9.525 mm tube does not pass through either smaller gauge.

The lower `FB` mounting form carries Industrial geometry on source X < 0 and the complete Sculpted loft/skin on X > 0 below source Z 67.5 mm, with their common mounting cavity and full upper neck. Both halves use one object-wide recipe. The identified accepted Industrial print establishes its recorded appearance; it does not physically qualify this hybrid.

## Release and support readings

`R30`, `R45` and `R60` name requested slicer top support distances. The current full-roof native slice gives the following commanded air after layer quantization:

| Roof | Requested top distance, mm | First roof nozzle Z, mm | Nominal roof underside, mm | Highest support nozzle Z, mm | Commanded nominal air, mm |
| --- | --- | --- | --- | --- | --- |
| `R30` | 0.30 | 35.48 | 35.24 | 35.00 | 0.24 |
| `R45` | 0.45 | 35.48 | 35.24 | 34.76 | 0.48 |
| `R60` | 0.60 | 35.48 | 35.24 | 34.52 | 0.72 |

All Z values here are manufacturing coordinates. The actual model step is 0.24 mm; the Bridge strand-flow HEIGHT is 0.239998 mm. The named central probe lies within the source 544 mm² flat face, whose support contact edge has the native 0.8 mm inset. Read that flat underside separately from the small rounded perimeter. Physical sag and support removal remain unmeasured.

`Q24`, `Q48` and `Q72` name nominal manufacturing-Z top release gaps of 0.24, 0.48 and 0.72 mm. Their lower release air is 1.44 mm, running lateral Y air is 0.35 mm per face, and X travel is 26 mm. Print all three with `back-top` in the prepared common frame; each flag begins on the same bed. The new captive shutters are reference additions. Solid model skin can sag or contact differently from sparse support-interface deposits.

The current native reading puts each moving foot's top at manufacturing Z 50.12 mm. With the 0.24 mm model step, the fixed cap readings are:

| Shutter | First fixed cap nozzle Z, mm | Nominal cap underside, mm | Commanded top air, mm |
| --- | --- | --- | --- |
| `Q24` | 50.60 | 50.36 | 0.24 |
| `Q48` | 50.84 | 50.60 | 0.48 |
| `Q72` | 51.08 | 50.84 | 0.72 |

The fixed lower ledge ends at nozzle Z 45.32 mm; the moving foot begins at nozzle Z 47.00 mm, giving a nominal underside of 46.76 mm and 1.44 mm lower air. The six named vertical gap windows contain no model or support deposits. The bridge flow HEIGHT values are approximately 0.24 mm and remain separate from these slab readings. Lateral commanded bead air varies with the sampled face and height: the +Y running foot reads 0.335 mm at its first contact layer and 0.350 mm above it. The opposite curved faces have their own readings; a uniform emitted 0.35 mm on both sides is not claimed.

For native gap readings, subtract the actual model layer step from the first model roof nozzle Z to locate its nominal underside, then subtract the last underlying model or support nozzle Z. Name both contributing surfaces: a support roof reads against support deposits, while a captive release reads against the opposing solid part. Keep Bridge flow-height and width metadata separate from the nominal model slab. These are commanded footprints and planes; physical sag, release, fit and legibility require the printed result.

## Source evidence and local notes

The accepted source records are deliberately scoped. [Grip](../../enclosure/grip-cover/physical-acceptance.json), [nameplate](../../enclosure/nameplate/horizontal-wing-trial/physical-acceptance.json) and [display](../../enclosure/display-cover/face-up-trial/physical-acceptance.json) records concern identified fit/finish coupons; the display retains its recorded residual bow. [Tee surface](../../enclosure/tee-carrier/physical-acceptance.json) and [tee slide](../../enclosure/tee-carrier/low-force-trial/physical-acceptance.json) evidence separates underside appearance from the selected slide. [Pump](../../../reference/kamoer-kphm400/physical-fit.json), [pogo](../../../reference/yyfkgcp-pogo-4p/physical-observations.json) and [magnet](../../enclosure/enclosure/magnet-retention/fit-coupons/physical-fit-selection.json) records do not establish this complete drawer's force, electrical performance or life.

The [Industrial faucet](../../faucet/industrial/physical-acceptance.json), [full cover](../../faucet/faucet-display-cover/physical-acceptance.json), [lever](../../faucet/lever-replica/physical-acceptance.json) and [organizer bores](../../faucet/umbilical-organizer/physical-acceptance.json) retain their named physical scopes. The current hybrid, comparison bands, shared control mounts, relocated source joints and assembled service section have no physical acceptance result.

The printed `nominal_*_flange/nut` pairs reproduce source fitting datums and clamp the port chips with M3 hardware. The 1 mm `display_nominal_backer` occupies the glass space. The rooted `FPD` donor provides the thimble and lever datums. These dry dimensional parts do not establish threads, pressure sealing, glass behaviour, electronic operation or dispensing.

Use the [blank reference card](reference-card.csv) for local observations. Fill in sample ID, date, printer/nozzle, filament/batch/drying, recipe/archive and source STL hash before recording a result. Keep the initial result separate from cleanup or freeing, add the next setting you actually intend to try, and link a photo or manual record. Every observation field starts blank. The [mechanical evidence index](../../../mechanical-qualification/README.md) identifies the production records when a real accepted result is available.
