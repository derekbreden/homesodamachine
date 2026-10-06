# PGFUN two-axis positioner assembly

Build one swivel and one horizontal pivot, each with an inline NEMA 17 motor
and PGFUN TYXC-0062_17_50 reducer. The gun sits in two lined housing bands
supported from below. The existing rotator provides tube rotation.

The [design](../printed-parts/fixtures/pgfun-positioner/design.json),
[assembly STEP](../printed-parts/fixtures/pgfun-positioner/assembly.step) and
[print pack](../printed-parts/fixtures/pgfun-positioner/print-pack.zip) govern
dimensions. All dimensions here are millimetres. The
[purchase and fastener allocation](purchases.md) covers one complete fixture,
controller and one camera stand.

## Print and prepare

Print the fit coupons first in the same PET-CF17 profile and orientation as
the journals and housings. Use a hardened 0.6 mm nozzle, 0.20 mm first layer,
0.24 mm normal layers, six walls and 100% infill for the structural PET-CF17
pieces. Start from the printer's established Fiberon PET-CF17 profile within
Polymaker's 270-300 C nozzle and 70-80 C bed ranges; fan off. Dry wet stock at
100 C for 10 hours and feed from the dryer. These parts use the as-printed
material; annealing is not specified. Manufacturer annealed strength numbers
do not establish these parts' strength.

The STL files already have their print orientation and bed Z=0. Do not use
automatic reorientation. Use accessible supports on every part marked in the
manifest: fork, cheeks, motor pedestal, yaw bearing cartridge, both journals,
cradle/retainers, bench toes, all four switch holders, controller case,
cable post sections/saddle and camera risers/upright. Support the elevated
plates, flange/key projections, band cavities, front cradle shoulders,
switch-clip roofs and controller cable-window roofs. Support the toes'
12 mm nut-loading lanes from their open sides. Keep support contacts out of
bearing bores, screw tunnels and the short internal nut-seat shoulders;
these bridge. The camera-post bores have 14 mm closing bridges; the lens
bolt wells have 2.6 mm radial shoulders. Inspect those bridge toolpaths in
the slicer and their printed seats before installing hardware. Use manual
support painting and blockers to keep removal paths open. The cable-post
service bores open at both ends for inspection and cleanup. Remove all support
material without rounding seats or changing housing contact profiles.
PETG camera/control pieces use the established PETG profile, four walls and
25% infill; the thin walls remain solid. TPU liners use three walls and 100%
infill. The 0.2 mm lens pad is one first layer.

Check the 40 mm bearing inner-ring fit on coupons 39.98, 40.04 and 40.06;
the nominal journal is 40.04. Check outer-ring fits on 52.00, 52.03 and 52.08;
the nominal housing is 52.03. Select a journal that enters with firm hand
pressure and cannot turn in the inner ring under hand torque. Select a
housing that accepts the outer ring squarely by hand and does not rock.
Change those two dimensions in `design.json` and regenerate before printing
full-size bearing parts if the nominal coupons fail. Do not force a bearing
through its balls, sand a loose seat larger, or glue over a rocking fit.

The nominal spacers are 7 mm for the paired 6808 bearings. Print inner and
outer spacers together and compare their heights with the owned caliper;
keep their difference within 0.02 mm. After assembly both races must turn
smoothly without axial rattle. Trim a high spacer squarely or regenerate a
matched pair; do not tighten caps until a binding stack frees up.

Load all captive nuts, including the M6 follower nuts, before closing a joint. Nut loading windows open to
the outside on the bearing cartridges, opposite bearing cap, cradle rails,
frame tie and cable post. The output journal flange nuts load from its
underside before the journal enters its bearing stack.

Cut two purchased M8x80 anchors to **45 +/-0.5 mm** under-head length. Cut
owned M5x50 screws into eight 20 mm, four 25 mm and four 30 mm screws. Four
owned M3x60 screws supply 30 mm fan bolts; two more supply 40 mm pitch
switch-holder bolts. Thread a backing nut onto each
screw before cutting; deburr, back the nut over the cut and confirm another
nut runs freely. For the M3 cuts, clamp a sacrificial steel nut around the
cut location in the metal saw's vise and cut the nut and screw together:
the nut supplies the section for the owned 24 TPI blade. Support the work
in the vise; do not hold a small bare screw at the blade. Measure every
finished length. Use ordinary hex nuts as the captive fasteners.

## 1. Attach to the stationary rotator base

Parts: `bridge`, two `bench-toe` feet, two M8x45 anchors with washers/nuts,
four M5x30 toe bolts, four M5x25 pedestal bolts and `motor-pedestal`.

1. With the tube removed, put the bridge over the two near-side stationary
   base holes, X=-102 and X=162, Y=-107. The 9.7 mm locating collars enter
   the existing 10 mm holes. The bridge seats on the 12 mm base.
2. The two toes support the bridge's outboard edge on the bench. Install
   their M5 nuts through the side windows and join each toe with two M5x30
   bolts. The feet bottom at the same bench plane as the rotator's feet.
3. Insert the M8 anchors through bridge and base. Their shortened ends clear
   the bench. Snug washers and nuts until the bridge cannot rock; do not
   bow the existing base. Preserve the rotator's existing bench attachment.
4. Load four M5 nuts into the bridge underside, then attach the pedestal
   with four M5x25 bolts through its recessed head seats. Their ends must
   stay clear of the bench and moving rotator.

Ready check: every foot bears on the bench, the bridge has no rocking
motion, and turning the empty rotator causes no contact. A rocking bridge
requires flat mating surfaces and corrected foot height before fastening.

## 2. Assemble the two motor/reducer units

Follow PGFUN's **"Harmonic Reducer Assemble Instruction (Nema 17)"** video on
the [selected Prime listing](https://www.amazon.com/dp/B0GF87W2KK). Its input
flange is removable to expose the motor mounting screws. Preserve its seal
and supplied case screws; the outer four 5.5 mm mounting holes do not retain
the motor. The video also covers the input-shaft side set screws.

Remove that flange, attach it to the motor's 31x31 mm threaded pattern from
inside using four M3x8 screws per motor, retain the seal, seat the 22 mm pilot
and 5 mm motor shaft, reinstall the flange and secure the input coupling as
the supplier demonstrates. Confirm that the actual flange leaves **3-4 mm
of M3 thread engagement**, the screws do not bottom in the motor, and the
shaft is clamped on its flat. Use the supplied motor screws if their length
is specified differently. Turn the motor shaft by hand before installing
the units; the output should move smoothly through reduction.

The model uses the supplier's 60 mm square input flange, 70 mm outer bolt
circle, 63.1 mm overall length and six M4 output holes on a 30 mm circle.
Verify those interface dimensions against the received units before
fastening printed parts. An incoming dimensional discrepancy requires a
corrected adapter; it is not addressed by enlarging the bearing seats.

## 3. Install the vertical swivel

Parts: yaw motor/reducer, `yaw-output-adapter`, `yaw-journal`, two 6808
bearings, inner/outer spacers, `yaw-bearing-cartridge`, `yaw-bearing-cap`.

1. Fasten the reducer's square input flange to the pedestal with four
   M5x20 bolts, washers and nuts. Leave them finger snug. The motor hangs
   below the reducer, with its cable exiting through the pedestal opening.
2. Load six M3 nuts into the output adapter. Attach it to the output with
   six M4x10 bolts and flat washers in the deep head wells. Effective M4
   engagement is about 5.2 mm in the vendor's 10 mm deep holes. Confirm
   neither screw tips nor heads bottom; keep washers within the 9.4 mm wells.
3. Load the six M5 flange nuts into the journal underside. Join journal to
   adapter with six M3x12 bolts and owned 7 mm OD x 0.5 mm washers. The six
   keys enter their matching pockets; they carry torque. Seat the faces
   squarely without crushing the keys. The key sides have 0.05 mm nominal
   interference, which the assembly clearance receipt identifies explicitly.
4. Fit the bearing cartridge around the journal. Stack: first 6808, 7 mm
   inner and outer spacers, second 6808. Seat outer rings on the cartridge
   shoulder and inner rings on the adapter. Support the ring being pressed.
5. Attach the cap with four M4x16 screws through its outer loading-window
   nuts. Snug evenly; it captures the outer races with 0.1 mm nominal
   axial clearance. Journal and output flange must turn without rubbing it.
6. Fasten cartridge legs to the pedestal with four M5x20 bolts. Turn the
   assembly by hand with the motor unpowered, centre the floating reducer
   mounting holes, then tighten its case bolts evenly. The external bearings
   carry the gun frame; the reducer delivers torque through the adapter.

Ready check: no axial rattle, no tight spot and no cartridge movement.
Binding calls for coaxial alignment or matched spacer/seat dimensions.

## 4. Build the horizontal pivot and frame

Parts: `fork`, pitch motor/reducer and supported journal stack, left/right
cheeks, `bottom-frame-tie`, two 6001 bearings, 12x100 mm axle, five axle
spacers, opposite bearing cap and keeper.

1. Assemble the cheeks and bottom frame tie first. Four M4x20 bolts run
   through the cheek recesses into the tie's side-loaded nuts. These bolts
   become inaccessible behind the output flange after installation.
2. Assemble the pitch reducer, adapter and paired 6808 journal stack by the
   same sequence as the yaw stack. The output points toward the left cheek.
   Its case mounts to the fork with four M5x20 bolts and nuts. Leave the
   case bolts loose for coaxial alignment.
3. Attach the left cheek to its journal flange with six M5x16 bolts. Insert
   the axle from the right through the split collet in the right cheek;
   its inboard end is at pivot-local X=30.
4. The axle stack, proceeding outward, is: 8 mm collet spacer, first 6001
   (8 mm), 8 mm inner spacer, second 6001 (8 mm), 21 mm front stop spacer,
   12 mm middle spacer, 18 mm end spacer, 3 mm keeper. The 6001 outer rings
   sit in the fork at X=55 and X=71. The keeper starts at X=130.
5. Load four M3 nuts through the opposite cartridge's radial windows and
   install its cap with four M3x12 bolts. The cap captures outer races.
   Secure the keeper with the shaft supplier's matching M6 end screw;
   confirm engagement and that it does not bottom in the tapped end.
6. Clamp the right cheek collet with one M4x20 bolt. Tighten only enough to prevent shaft slip. The spacing stack must
   seat without forcing the bearing rings sideways or pinching them.
7. Centre the pitch reducer on the external bearing axis, then tighten
   its case bolts. Fasten the fork to the yaw journal's six flange nuts
   with six M5x16 bolts and washers.

Ready check: the assembled frame turns smoothly at both axes, the shaft
cannot slide outward and the two cheeks stay parallel. Rotate only through
the stop-defined range after installing stops. The gearmotor is not used
as a press or as a means of forcing a crooked bearing stack straight.

## 5. Fit the gun from below

Parts: `lower-cradle`, two gun retainers, four TPU band liners and eight
M4x20 bolts/nuts. Keep the welder powered off during fitting.

Attach the lower cradle to the four integral cheek pads with four M4x20
bolts into its rail nuts. Put the lower TPU liners in the two bands, lay
the measured scan housing into them, and put the upper liners and retainers
over the housing. Each retainer uses two M4x20 screws into the lower band's
captive nuts. Tighten alternately to compress the liners slightly and
prevent housing slip; the nominal 0.6 mm split permits compression. Do not
bottom the split or crush the housing. The front shoulder wings provide
an axial stop while clearing the wire-feed guide. The grip, mode button,
factory trigger and boot remain accessible.

The supplied print pose is 60 degrees below horizontal and 16 mm from
nozzle tip to nominal joint. Those are editable mounting parameters, not a
recorded welding recipe. Establish the actual focus and working attitude
on a sacrificial joint using the X1 Pro focus procedure. If the printed
pose misses that setting, change the cradle/cheek parameters and regenerate
the parts before a welding run; motor trim is reserved for the small
in-process correction range.

## 6. Install stops, parking pins and limit switches

Attach each fixed stop sector with two M4x16 bolts. Put an M6x25 follower
through the moving fork and an M6x35 follower through the left cheek's
integral stop arm, at the 70 mm radius. The pitch sector mounts on the
left-side fork ear. Its thread crosses
the sector slot. The nominal hard stop is +/-1.5 degrees; soft travel is
+/-1 degree. Confirm actual assembled hard-stop travel is at most 1.7
degrees and nothing else touches first.

The two M3x25 parking screws pass through the matching 3.05 mm datum holes
at radius 77.5. Insert with motor power off. Bias each axis consistently
toward the same side of its pin clearance, then remove both screws before
referencing the controller. They establish a repeatable assembly datum;
the camera qualification establishes how repeatable that datum actually is.

Four KW12 roller switches sit in the printed holders. Use M3x12 for yaw holder
mounting. Mount the pitch holders through their two 30 mm standoffs with
owned M3x60 screws shortened to 40 mm. Use M3x8 side screws to grip each switch's body, clear of its lever.
Slide the body and holder until the moving cam opens the normally closed
contact at 1.15-1.35 degrees in each direction. Show that the NC contact
opens before the follower reaches its hard stop. Adjust one switch at a
time with power off, then electrically check all four. Wire the two NC
contacts per axis in series, as in [control.md](control.md).

## 7. Support the umbilical and mount the controller

Join the two printed cable post sections with two M5x30 bolts; mount the
saddle with two M5x20 bolts. Use the four owned 25 mm fender washers at
these accessible top joints. Clamp the post foot to the bench using two
owned C-clamps. Route the existing loose cable curve over the broad saddle
and tie only its jacket. Preserve its natural bend and slack; do not force
a tighter fiber bend or let a tie flatten the cable. The gun-side residual
cable force must satisfy the commissioning load limit.

Mount the SKR Pico on four M3x10 screws and 7x0.5 mm washers, with captive
nuts loaded from the case bottom. Install the 22 mm NC stop button in the
lid. Attach the 40x40x20 mm 24 V fan and printed guard using four M3x30
screws, washers and nuts. Fit the lid with four M3x12 screws. Cable exits
keep the USB, motor, stop and 24 V harnesses clear; secure their strain
relief with owned ties. Keep the controller away from the weld plume.

## 8. Assemble the one-camera stand

Join `camera-riser-base` and `camera-riser-top` with four M5x20 screws.
The tray is horizontal, as required by the camera manufacturer. Its PTZ
head and the separate macro cassette look down at 29 degrees, within the
head's 30-degree downward limit. The nominal sight line clears the 6.35 mm
recessed rim by about 1.6 mm. Secure the camera base through both pairs of
tray tie slots using the owned 8-inch ties chained into long straps. Grip
the camera base, clear of moving PTZ housing, connectors and ventilation.

Fasten the lens upright to the tray with two M5x20 bolts/nuts. Install
the Raynox DCR-250 in the cassette: rear 43 mm neck enters the shoulder,
outer front rim contacts the 0.2 mm TPU pad, then the retainer holds the
rim with four owned M3x25 screws. Keep the optical aperture and glass clear;
the clamp bears only on the metal body. The optional 0.4 mm TPU shim takes
up received axial clearance if needed. Do not use the universal snap-on
adapter inside this cassette.

Attach the cassette behind the upright's two long slots with four M5x30
screws and nuts. Insert screws from the cassette's rear head wells; the
carrier lies on its front face, outside the optical aperture. Align its centre to the camera's actual optical axis, set the
camera's lens to face through it, and slide the whole stand to focus near
Raynox's approximately 109 mm working distance. The published camera body
envelope governs tray clearance; the optical-centre illustration is not a
measured camera mounting datum. Slots provide +/-49 mm adjustment along the tilted lens plane. Set the
head and cassette coaxially using those slots and stand position.

Before any camera power-up or reboot, remove the lens upright and cassette
as a unit using its two foot bolts. The camera's automatic pan/zoom self-test
needs that space. Reattach only after self-test, with the head set to its
recorded pose. Never turn its motorized head by hand.

Lock focus, exposure and PTZ/tracking for the dry measurements. Keep the
actual wire endpoint and aiming dot in the same sharp view. Withdraw this
entire stand before emission: this build uses learned trajectory replay
and supplies no qualified welding-light protection for the camera.

## Fastening and release check

Use flat washers under bolt heads against prints. M3 wells take the owned
7x0.5 mm washers; M4/M5 wells take the kit's matching flat washers. Use one
owned M5 hex nut in addition to the kit's 45 nuts. Start printed joints at
M3 0.15, M4 0.3 and M5 0.5 N m, then use the lowest preload that passes
retention and movement checks. These are assembly starting points, not
qualified joint capacities. Do not apply these values to the reducer's
factory screws: use its installation instructions. Use Loctite 243 only
on compatible metal-to-metal threads and allow its stated cure; keep it
off plastic and bearings. Add witness marks to motor couplings, journal
adapters, shaft clamps and base anchors.

Complete [commissioning](commissioning.md) before running with the tube
present. Its procedures address loaded retention, stop travel, heat drift,
camera noise and independent dry laps. Record received fit and real results
beside the hardware; numerical clearance is not a load or lifetime result.
