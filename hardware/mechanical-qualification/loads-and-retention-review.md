# Loads and retention review

Each case: the load, its path, the feature that governs it, a hand-calculation margin and a
verdict, for the enclosure at `fbc3e5dd3` and its regenerated quadrants; the pump-tube and
cartridge-seat cases read the current tree's dock. Physical evidence is in the
[register](README.md). The pump dock's tee caps, tee anchors and collet plate are outside this
review.

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
| Y seam under a lift | 23.5 N·m from the front column | Top laps in compression; the lower M5 rods in bearing on the knuckles: 46 N per side | Ligament shear-out of one knuckle is 8.8 kN | Adequate |
| Y-seam head seat | Screw preload | Head on its printed floor, compression across layers | 31 MPa at a 1 N·m seat against an assumed 50 MPa; see [head recesses](#y-seam-head-recesses) | Adequate at a snug seat |
| Compressor posts, lateral shock (side or edge drop) | 4.5 kg × deceleration, shared by four posts | Ø12/Ø6.4 post bending at its root on the slab, across layers, lever about 10 mm | 2.1 at 10 g, 1.06 at 20 g, 0.71 at 30 g | Needs a physical observation; see below |
| Compressor posts, vertical rebound | 4.5 kg × deceleration | Grommet top flange → washer → M5 screw → RX-M5x9.5 pull-out | 276 N per insert at 25 g, 552 N at 50 g | Adequate to about 50 g on an assumed 1 kN insert pull-out; drop acceptance is the evidence |
| M3 wall-mount inserts (supply, relay, C14, boards) | C14 cord insertion, about 50 N; the 0.33 kg supply at 50 g, 162 N over its screws | Screw → ruthex M3 → boss; C14 insertion loads its two inserts in pull-out because the flange lands from inside | Under 100 N per insert against an assumed 300 N | Adequate |
| M1.4 connector inserts | Connector magnets plus four 0.44 N springs | Ear plate → two M1.4×8 → M1.4×4 inserts per half | Under 10 N per half | Adequate; installation access is the open item ([mounting audit](../reference/yyfkgcp-pogo-4p/mounting-audit.md)) |
| Pump tubes under blocked-fill pressure | Blocked-fill pressure over each pump tube's sealed section | Tube → its tee's branch collet; the tube's far end in the pump head's housing clamp. The tube carries the separating load between collet and clamp, and the magnets carry none of it | Not calculated: the collet's grip is the fitting's own and the clamp's hold is unmeasured | Open; see [cartridge seat](#cartridge-seat) |
| Cartridge seat | The four upper tubes' spring at connected, pushing the cartridge forward through the bottomed pump tubes, and the hairpins' spring across the tees' travel | Pump tubes → pump heads → cartridge → four SB443-IN pairs, one column of two on each pump's own line, printed in on rails, bare poles meeting across the frame gap | 60.9 N for all four pairs at the catalogue steel rating, 30.4 N per pump's column, against an unmeasured spring | Open; no margin until the spring is known |
| Pogo contact current | Pump start and jam current, held at the trip | DRV8870 current regulation through the 0.2 Ω sense resistor on each ISEN (R28, R29) | 1.54–1.81 A against 2 A: 1.10 at the ceiling; 1.65 A nominal, about twice the 0.8 A running current | Adequate in the board source; the start under the trip needs a physical observation; see below |

## Y-seam head recesses

The four M5 seam screws seat in Ø9 openings, their head floors at Z40.8 and Z347: the lower
heads' faces stand 6.55 mm above the handhold ceiling, the upper 3 mm inside the roof. The upper
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

**Bearing.** The head bears 32.1 mm² on its floor, compression across layers. A hand-snug seat
of 0.5–1 N·m gives 500–1,000 N and 16–31 MPa, inside the assumed 50 MPa. At 2 N·m it reaches
62 MPa and the head sinks into its floor. The joint carries its loads with the screws in
bearing and has no designed preload; the heads seat snug.

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

## Pogo contact current

Each contact is rated 2 A and carries one pump's whole motor current. In the
[PCB source](../pcb/pcba/pcba.tsx), each DRV8870's ISEN returns through its own 0.2 Ω ±1 %
sense resistor (R28 on U11, R29 on U12) and VREF is 3V3. The
[DRV8870 data sheet](https://www.ti.com/lit/ds/symlink/drv8870.pdf) trips at
I_TRIP = VREF / (A_V × R_ISEN): 1.65 A nominal, 1.54–1.81 A across its 9.4–10.4 ISEN gain, the
3V3 rail's ±2 % and the resistor's ±1 %. At the trip the bridge brakes for 25 µs and drives
again, so a start or a jam is held there, and the contacts carry the trip current through the
brake. The resistor dissipates 0.65 W at the 1.81 A ceiling, on a 1 W part. Boards from the first
two JLCPCB batches ground ISEN and are bounded only by the driver's 3.7–6.4 A overcurrent
protection.

A primed head starts against the trip current. The observation that confirms the setting is a
pump start under it: a primed pump at the coldest expected cabinet temperature reaches full speed
within 1 s of its command
([current protection](../reference/yyfkgcp-pogo-4p/mounting-audit.md#current-protection)).

## Cartridge seat

The tees' branch collets grip the pump tubes and carry the pressure
([pump dock](../printed-parts/enclosure/pump-dock/README.md)). Under a blocked fill each tube
holds its separating load between its collet and the pump head's housing clamp, so the load
does not reach the cartridge's seat. The clamp's hold under that load is unmeasured.

The four SB443-IN pairs seat the cartridge, one column of two on each pump's own line, their
bare poles setting its flat back 0.25 mm off the collet plate. K&J rates one block at 3.42 lbf
to thick steel, 15.21 N, so the four pairs give 60.9 N and each pump's column 30.4 N; that
catalogue figure is not an installed rating. At connected each upper tube stands 0.75 mm off
straight and pulls its tee forward, and through the bottomed pump tubes that spring pushes the
cartridge against the magnets. That spring and the hairpins' spring across the tees' travel
are unmeasured, so no seat margin is stated. Straight removal parts all four pairs, presses four
collets home against the plate, drags four tubes through their O-rings and adds the upper tubes'
spring at release; that total is unmeasured.

## Evidence limits

Hand calculations on the assumptions above. They establish no load capacity, impact
performance or lifetime.
