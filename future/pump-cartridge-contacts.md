# Automatic pump-cartridge contacts

Proposed interface: four broad rigid pads on the pump cap's rear face, contacted
by four independently sprung, screw-mounted metal leaves recessed into the
stationary PET-GF enclosure.
Short wires and female Faston receptacles connect the pads to the motor spades.
Two magnetic retention stations flank the contacts. The cartridge guides establish
alignment and a mechanical stop establishes insertion depth.

This is a design study, not an implemented or electrically qualified connection.

## Geometry and electrical load

The inspected assembly payload is
`hardware/manifold-layout/enclosure-assembly.step.mesh`, source
`15f01e61bedfc2de411bf6ab0be5e3a8ec481cae3708d02c0109b99939921d33`.
It matches the selected face and source identifier. Its `enclosure-pump-cap`
rear plane is Y = 79.269 mm, with X = -87.225 to +87.225 mm and
Z = 216.925 to 284.174 mm: a 174.450 × 67.249 mm face. The selected point is
(-2.033, 79.269, 273.926) mm.

An XZ-projected triangle intersection through that point meets the stationary
`enclosure-front-top` at Y = 79.515 and 99.440 mm. The existing separation is
approximately 0.246 mm, and the fixed material along that line is approximately
19.925 mm deep. Thus the proposed spring travel needs a recess in the stationary
part. The existing gap does not provide that travel by itself. At X = ±27,
Z = 270 mm, the fixed material extends to Y = 98.056 mm; at X = ±9,
Z = 270 mm and X = ±55, Z = 264 mm, it extends to Y = 99.440 mm. These are
local mesh readings, not a clearance audit of a finished contact assembly.

The [pump reference generator](../hardware/reference/kamoer-kphm400/kamoer_kphm400.py)
contains a head, boss and plain motor can. It does not model the electrical
terminals. The two [native pump scans](../hardware/reference/kamoer-kphm400/scan-evidence.json)
do contain the spades. Both original cloud hashes were verified for this review,
and their recorded rigid transforms were used without rescaling.

In the registered scan frame, the exposed blades lie in opposite XY quadrants,
approximately around (-12, +12) and (+12, -11) mm. Their tips reach
Z ≈ 68.5–68.6 mm. Both scans show the blades splaying outward. A selection above
Z = 64 mm gives a transverse 1st–99th percentile span of approximately
3.6–3.8 mm. This is an observed, sprayed surface envelope of the exposed portion,
not a certified tab width, thickness or mating specification. The scans are two
views of one sample; they do not establish variation between pumps.

The motor spades are bendable, including toward an inward-facing orientation.
Their scanned inclination is therefore an assembly variable. A direct-contact
design can specify a formed position and a simple forming gauge; the scan alone
does not establish the acceptable bend radius or number of forming operations.

The [wiring schedule](../hardware/wiring/ac-wiring-schedule.md) specifies two
DRV8870 differential motor outputs and four separate conductors: AM1, AM2, BM1,
BM2. The published pump figure recorded there is approximately 0.8 A per motor
at 12 V. Four isolated contacts are required; neither motor conductor is a shared
ground. Actual starting current and the driver's configured current limit remain
inputs to contact qualification.

## Contact arrangement

A useful starting layout has four pads approximately 18 × 20 mm on 22 mm
horizontal pitch, centred around Z = 270 mm. That occupies an 84 × 20 mm band
on the rear face. These dimensions are proposed, not production dimensions.
Each pad has a dedicated insulated wire to one motor terminal.

Use a rigid pad on the cartridge and a spring on the stationary side. Give the
spring a rounded nose or formed bump and a swept lead-in so insertion and removal
do not catch its free edge. The nose should move slightly along the pad while
compressing. The broad pad supplies positional tolerance; the rounded contact
region supplies local pressure. Full-area flat-to-flat contact is unnecessary.

For example, a 5 mm wide leaf landing centrally on an 18 mm wide pad has 6.5 mm
of geometric margin on either side before its width reaches the pad edge. This
is an overlap allowance, not the complete connector's tolerance rating: tilt,
vertical overlap, wiping motion, neighbouring conductors and the cartridge guides
still bound the usable movement. Plastic separators keep each leaf in its own lane.

The cartridge's mechanical seat sets spring deflection; the magnets pull it onto
that seat. A stop behind each leaf limits overtravel.

### Screw mounting in PET-GF

Use a leaf with a flat mounting tail and a separate free spring section. The
mounting stack, from the screw head toward the printed boss, is:

1. Machine screw and flat washer.
2. Crimped ring-terminal tongue.
3. Flat metal tail of the spring contact.
4. Exposed face of a brass threaded insert retained in the PET-GF boss.

The ring tongue touches the leaf directly. The intended electrical path is wire
to ring terminal to leaf; it does not depend on the screw threads. The insert face
supports the metal tail directly, with no plastic layer inside the compression
stack. A metal spacer can establish that bearing surface if the insert is recessed.
The mating hole must be smaller than the supporting insert face. This follows
[SPIROL's guidance on metal bearing surfaces and joint integrity in plastic](https://www.spirol.com/resources/white-papers/how-to-ensure-bolted-joint-integrity-when-using-a-compression-limiter-in-a-plastic-assembly/).

A shaped pocket captures the flat tail against rotation; the screw provides
clamping force. Leave the spring bend and its swept volume clear of the washer,
ring barrel and printed walls. Size the root pocket for the ring terminal as well
as the leaf: a 5 mm leaf does not imply a 5 mm wide complete mounting assembly.
Route and strain-relieve the wire behind the fixed root.

The enclosure already uses M3 heat-set inserts, and the wiring BOM includes M3
ring terminals. Use that hardware only if the selected leaf's measured hole and
tail dimensions accept it. The uxcell B07N27RSPS listing does not specify its hole
diameter; its photograph is not a fit specification for M3.

Keystone 209's snap-on mounting could be accommodated with a purpose-designed
printed rib of the specified thickness. The proposed mount uses a screw and
anti-rotation pocket, giving the wire and spring root a common clamped joint.

### Direct contact with formed motor spades

Direct engagement with the motor tabs is plausible using long leaves with rounded
lead-ins. Inward-formed tabs can present a more convenient contact face and avoid
an outward-pointing edge catching a leaf. Establish tab position during cartridge
assembly, with support at the terminal root while forming; cartridge servicing
should flex the stationary spring, not repeatedly bend the motor terminal.

Check the insertion sweep, motor-can clearance and spring reaction at the terminal
root. Where feasible, an insulating backing feature can support the mating blade
against contact pressure. The direct arrangement removes the four short cartridge
wires and separate pads. The cap-pad arrangement provides independently located,
broad targets and keeps contact reaction out of the motor terminals. It remains
the preferred service interface for this study. Its ordinary Faston connections
remain attached during cartridge insertion and withdrawal.

## Spring material and force scale

For a custom leaf, use specified spring-temper phosphor bronze, with a suitable
contact finish. Copper alloy and temper matter: generic soft copper sheet does
not supply the same resistance to permanent set and stress relaxation.
[Copper Development Association's connector guide](https://www.copper.org/applications/industrial/DesignGuide/selection/phbronze02.html)
describes phosphor-bronze strip as a contact-spring material.
[Keystone's battery-contact catalog](https://www.keyelco.com/pdfs/p10.pdf)
specifies 0.012 inch (0.305 mm) nickel-plated phosphor bronze for its 5209 leaf.
Nickel-plated spring steel is also an established battery-contact construction;
Keystone specifies it for the 209.

An illustrative straight cantilever with 25 mm free length, 10 mm width and
0.35–0.40 mm thickness produces approximately 1.13–1.69 N at 1.5 mm tip
deflection using E = 110 GPa. Four such leaves oppose insertion with approximately
4.5–6.8 N. These figures use F = E b t³ δ / (4 L³); the associated ideal root
stress is approximately 139–158 MPa. The modulus is consistent with
[C51000's published 16,000 ksi](https://alloys.copper.org/alloy/C51000).
The calculation establishes a plausible scale. It does not rate a formed
commercial contact or account for bends, mounting compliance, stress concentration,
fatigue or surface films. Final working travel and force come from the selected
part or a measured coupon.

## Magnetic retention

The [inventory](../hardware/ledger/inventory.md) records 30 K&J RC62 rings in hand.
[K&J specifies](https://www.kjmagnetics.com/rc62-neodymium-ring-magnet)
19.05 mm OD, 9.52 mm ID and 3.17 mm thickness, axial magnetization and N42 grade.
Its listed Case 1 pull is 8.51 lbf, approximately 37.9 N, against a thick steel
plate in the specified test arrangement.

One retention station on each side of the contact group is a reasonable coupon
layout. A ring can pull against a retained steel target, with its axial field
aligned to cartridge insertion. Retain the magnet mechanically, and tune the
actual face separation for the desired release force. Magnets supply retention;
guides take weight and lateral loads; the mechanical stop sets contact compression.

Catalogue pull is not installed holding force. Plastic cover thickness, the
existing clearance, target size and target thickness all affect it.
[K&J's pull-test description](https://www.kjmagnetics.com/blog/testing-magnet-strength)
and [steel-thickness discussion](https://www.kjmagnetics.com/blog/steel-thickness-and-magnetic-fields)
explain these dependencies. Retention must exceed the contact spring reaction
plus any outward plumbing/carrier force and normal handling loads, while leaving
cartridge removal comfortable. Check the complete force through the final approach,
not only at the seated position.

## Prime bench candidates

Observed in the signed-in Amazon session on 2026-09-29, with Prime shown on each
product's selected offer:

| Candidate | Observed offer | What is established |
|---|---|---|
| [uxcell B07N27RSPS](https://www.amazon.com/dp/B07N27RSPS) | $13.79 / 20; Prime; September 30 delivery | Flat holed mounting tail, offset spring face and turned end; listing gives 13 × 5 × 10 mm overall size. Suitable mounting form for the proposed screw-and-ring-terminal coupon. Hole diameter, spring temper and force/travel are unspecified. |
| [Keystone 209, B06VTPWM6M](https://www.amazon.com/dp/B06VTPWM6M) | $12.49 / 20; Prime; October 2 delivery | Formed, rounded leaf; snap-on case mounting; nickel-plated spring steel, also confirmed by [Keystone](https://www.keyelco.com/product.cfm/17-19-mm-Dia-Cell-Contacts/209/product_id/875). |
| [uxcell B07N2F5W2D](https://www.amazon.com/dp/B07N2F5W2D) | $9.99 / 10; Prime | Long folded battery leaf with a rounded nose and attachment hole; listing gives 24.4 × 5 × 8 mm overall size. The listing identifies the substrate only as metal. |

The inspected listings do not supply sufficient force/travel or motor-current
qualification to claim an approved connector. B07N27RSPS is the first mounting
coupon candidate; its listing identifies the substrate only as metal. Measure its
mounting hole, usable travel and force before fixing the printed pocket, screw
size or stop position. Its 10 mm overall height is not a 10 mm travel rating.

## First physical check

A small printed coupon with one spring, one broad pad and an adjustable stop can
establish working deflection, wiping action and misalignment allowance. Use the
actual pump and driver to measure voltage drop at steady running and startup,
then repeat insertion and withdrawal and check for permanent set or interruptions.
The four-contact coupon adds the magnetic stations and measures seating and
removal force with the real plumbing/carrier assembly. Service insertion and
withdrawal keep the motors disabled; live disconnection of an inductive load
requires separate provision.
