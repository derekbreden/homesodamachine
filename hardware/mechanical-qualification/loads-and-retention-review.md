# Loads and retention review

Each case: the load, its path, the feature that governs it, a hand-calculation margin and a
verdict. The Y-seam cases use the current four M5×100 pin stacks and their
[native review](../printed-parts/enclosure/enclosure/y-seam-100-review.json).
The other enclosure calculations bind `fbc3e5dd3` and its regenerated quadrants;
the pump-mount and tube-joint cases describe the current integral mount and dock below. Physical evidence is in the
[register](README.md). The tee wall that holds the pump tees is outside this review.

## Basis and assumptions

| Quantity | Value used | Basis and limit |
| --- | --- | --- |
| Installed mass, filled | 20 kg | The BOM's printed parts are 7.44 kg ([BOM §7](../ledger/bom.md)). The compressor, carbonator, condenser, valves, pumps, supply and boards add an estimated 8–10 kg, and the fluids 2.5 kg ([finish, pack and ship](../assembly/finish-pack-ship.md)). This bounds the 10–15 kg dry working estimate from above. |
| Front column mass and centre | 10 kg, 120 mm ahead of the grip axis (Y214) | The compressor and condenser stand at the front of the floor. The machine's centre of mass is not stated; this is a bound. |
| Compressor mass | 4.5 kg | Not recorded for the donor; typical of a small hermetic R-600a compressor. The limit is 3.5–6 kg. |
| Printed PET-GF15 strength | 40 MPa in-layer tension, 15 MPa across layers, 20 MPa in-layer shear, 50 MPa compression | Assumed design values for printed parts. The [PET-GF15 data sheet](https://fiberon.polymaker.com/wp-content/uploads/TDS_FIBERON-PET-GF15_V1.0_EN.pdf) tests annealed 100%-infill specimens; the register treats those as no production allowable. Margins below scale directly with these values. |
| Printed section | Two perimeters plus solid skins, about 1 mm each face | The shared profile prints sparse 15% infill inside thick sections ([infill and deposited structure](README.md#infill-and-deposited-structure)). Skin-only section moduli are used where a section is thick and not in a 100% region. |
| Lifting dynamic factor | 2.0 | A jerked lift doubles the static weight. |
| Drop | 4–6 in, 1.41–1.73 m/s at contact | From [short-drop retention](README.md#short-drop-retention). Peak deceleration is not measured; drop cases state the deceleration at which each feature reaches its assumed allowable. |

## Results

| Case | Load | Path and governing feature | Margin | Verdict |
| --- | --- | --- | --- | --- |
| Two-hand lift by the handholds | 196 N per side with the dynamic factor | Fingers → 12 mm lifting ceiling → end walls and the lower knuckle stack standing on the ceiling at mid-span | One-hand case below governs | Adequate |
| One-hand lift or tilt over the face-frame lip | 392 N on one ceiling | Ceiling bending over its 25.6 mm span from end wall to knuckle face, skin-only section 151 mm³: 16.6 MPa | 2.4 against in-layer tension | Adequate; the ceiling prints flat and bends along its layers |
| Tops hanging on the Z rails during a lift | Tops' weight × 2 | Hooked arms on each flank's straight run, 4.5 mm arm and 5 mm lap over 150 mm or more | Under 0.2 N per mm of rail | Adequate |
| Y seam under a lift | 23.5 N·m from the assumed front-column load | Printed knuckles bear on four steel pins; their head/insert end pairs capture the opposite half's middle blocks. Running gaps and printed deflection determine first contact. The floor tongue has no tensile interlock and the top lap is not a qualified compression flange | Native geometry supplies no measured bearing, ligament-shear or assembled bending capacity | Unqualified for current geometry |
| Y-seam head seat | Head seating; no designed middle-block clamp preload | Head on a printed floor; insert and head belong to the same half | 32.1 mm² nominal head-bearing area; no qualified torque-to-tension or printed compression allowable | Seat only; see [head recesses](#y-seam-head-recesses) |
| Compressor posts, lateral shock (side or edge drop) | 4.5 kg × deceleration, shared by four posts | Ø12/Ø6.4 post bending at its root on the slab, across layers, lever about 10 mm | 2.1 at 10 g, 1.06 at 20 g, 0.71 at 30 g | Needs a physical observation; see below |
| Compressor posts, vertical rebound | 4.5 kg × deceleration | Grommet top flange → washer → M5 screw → RX-M5x9.5 pull-out | 276 N per insert at 25 g, 552 N at 50 g | Adequate to about 50 g on an assumed 1 kN insert pull-out; drop acceptance is the evidence |
| M3 wall-mount inserts (supply, relay, C14, boards) | C14 cord insertion, about 50 N; the 0.33 kg supply at 50 g, 162 N over its screws | Screw → ruthex M3 → boss; C14 insertion loads its two inserts in pull-out because the flange lands from inside | Under 100 N per insert against an assumed 300 N | Adequate |
| Pump tubes under blocked-fill pressure | Blocked-fill pressure over each pump tube's sealed section | Tube → its tee's gripping branch collet; the tube's far end is held by the pump head's housing clamp. The fixed upper pockets and lower retainer carry the pump body | Not calculated: the collet's grip is the fitting's own and the housing clamp's hold is unmeasured | Open; see [pump mount and tube joints](#pump-mount-and-tube-joints) |
| Pump skirt capture | Pump weight, motor reaction and installation/handling loads; magnitudes not assessed here | Molded skirt → lower retainer → full-depth snap-wing roots and lower hooks → receiver floors → front-top; fitted upper lands capture the skirt above | The snap geometry is recorded; fit, holding capacity, insertion/release forces and lifetime are unqualified | See [pump mount and tube joints](#pump-mount-and-tube-joints) |
| Individual tee installation | One prepared tee/upper-tube/fore-valve group approaches a secured pump tube from aft | Tee branch → tube and pump-head clamp → the secured pump mount; the fore valve seats on its tray posts | Complete 11.65 mm native approaches are clear; actual insertion force and fluid-joint retention are unmeasured | See [pump-mount reading](../printed-parts/enclosure/enclosure/pump-mount-review/README.md) |

## Y-seam head recesses

The four fully threaded M5×0.8×100 seam screws seat in Ø9 openings, their head floors
at Z60.8 and Z347. The lower heads' faces stand 26.55 mm above the handhold ceiling;
the upper heads stand 3 mm inside the roof. The upper
axes stand at |X|97.7, 9.8 mm in from the exterior, and their M5 insert envelope stays 0.4 mm
inside front-top's 13 mm knuckle face. The lower axes stand at |X|98.25, where the head passes the handhold's 3 mm inner
wall, which stands 0.25 mm off the cold core.

Each recess stands inside an R6 roll whose additive print chamfer, 0.5 mm outward per mm of
rise, meets the ceiling and roof planes at |X|105.21: the roof's side shoulder over the upper
recesses, the handhold's lifting edge under the lower ones. The upper outboard rim is 3.0 mm at
the roof plane. The lower one is 2.46 mm at the ceiling plane and reaches 3 mm about 1.2 mm
above it; 3 mm at the plane needs the handhold roll at R4.5, and Derek asked on 2026-09-19 that
the bottom grips match the top's rounding, so the roll stays R6 and the rim's lint row is
answered with R4.5 as the alternative.

**Bearing and clamping.** A nominal Ø8.5 head over the Ø5.2 passage has 35.5 mm²
of projected bearing area. Each head floor and insert block belong to the same
quadrant: back-bottom at the lower stations and front-top at the upper stations.
The screw retains the opposite quadrant's middle block as a pin through a clearance
passage. Tightening seats the head; it does not directly squeeze that middle block
between the end blocks. The Ø5.2 passages use the
[selected physical M5 fit](../print-tests/m5-seam-bearing/physical-result.json);
the nominal diametral air around an M5 thread envelope is 0.2 mm. The 0.25 mm
running fits remain between the printed blocks. Printed variation, contact, wear and deflection
set assembled movement. No installation torque or retained preload is qualified;
stop when the head meets its floor. The nominal bearing area and solid host geometry
do not establish printed load capacity or long-term rigidity.

## Compressor posts in a side drop

Each post is the donor grommet bore less 1 mm on the radius: Ø12 around the Ø6.4 insert bore,
rooted on the 6 mm slab. A lateral shock reaches the post through the rubber, after its 1 mm
radial slip closes. The root bends across layers, the weakest direction. The calculation reaches
the assumed interlayer allowable at about 20 g.

Two things bound it in practice and are unmeasured. The rubber stores the slip, which lowers the
peak; and the compressor shell's clearance to its neighbours decides whether it lands on the
condenser or the flank before the posts take the whole load. The decision this changes is whether
the posts need a lateral stop independent of them, such as a printed curb round the base plate
standing clear of the grommets. In the first assembled machine, before the compressor is
charged, push the compressor's shell sideways at mid-height by hand in each of the four
directions until its plate meets the post or the shell meets a neighbour. Record which it meets first and the travel to contact, read with a feeler
gauge. If the shell meets a neighbour or the condenser cradle first with the posts unloaded, the
posts are adequate for lateral shock. If the plate meets a post first, a curb is added before
shipment.

## Pump mount and tube joints

Front-top contains the fitted upper pump pockets. The broad lower retainer carries
the lower skirt lands. Its two full-depth integral snap wings transfer the retainer’s load
through their upper roots and lower hooks to front-top’s receiver floors. The two fitted
halves capture the molded pump skirts. The [pump-snap review](../printed-parts/enclosure/enclosure/pump-snap-review/README.md)
records nominal geometry and spring displacement; it does not establish printed fit,
operating retention, load capacity, insertion/release forces or lifetime. The
[three-screw mount receipts](../printed-parts/enclosure/enclosure/pump-mount-review/README.md)
retain their own identified input and motion scope.

With both pumps secured in loose front-top, each prepared tee, upper tube and fore valve
approaches individually from aft. The [pump dock](../printed-parts/enclosure/pump-dock/README.md)
defines the sequence and tube-tip marks. Each tee's extended branch collet grips its pump
tube. Under a blocked fill the separating load acts over the tube's 31.7 mm² section;
the collet and the pump head's housing clamp hold its ends. Their joint holding force is
unmeasured. The fixed mount supplies the pump body's structural retention.

Each tee stops aft on its lower return, anchored in its rear valve, and its fixed branch
barrel lands on the bore face if pushed fore. Native path clearance does not establish
the actual tee insertion force or the returns' resistance to that load.

## Evidence limits

Hand calculations on the assumptions above. They establish no load capacity, impact
performance or lifetime.
