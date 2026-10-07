# Sculpted faucet assembly

[Faucet styles](../README.md) names the Sculpted and Industrial pieces.

The PET-GF shell encloses the harvested Westbrass, the
[printed lever](../lever-replica/README.md), four LLDPE tubes, two vent seals and Waveshare display. Factory assembly supplies a complete
faucet and umbilical. Customer installation uses the captive donor nut and the
existing stainless under-counter plate.

## Printed pieces and seams

The shell base carries the oval foot, lever opening and lower gooseneck. The
shell tip carries the upper gooseneck and display pocket. Their internal joint datum is at [50°](SPLIT_JUNCTION_ROT) around the arc.
The base has the 18 mm male plug; the tip has the 20 mm female socket.
The visible outer seam is about 34° around the arch, at the socket entrance. The separate display cover has a perimeter
seam around the display pocket. The above-counter plate meets the shell at
its foot; the matching TPU gasket sits under that plate.

Rigid structural walls, display supports, screw seats and insert backing
are at least [2 mm](WALL_MIN) at the checked sections. The gooseneck lap has a
[2 mm](SPLIT_SOCKET_WALL) socket wall and a [2 mm](SPLIT_PLUG_WALL) plug wall, separated by
[0.3 mm](SPLIT_SLIP) diametral clearance. The display cover's side walls flex
around the rigid neck; the nominal skin is 1.30 mm thick, with a 1 mm
minimum for the cover's thin sections. Its broad retaining lips are 3 mm high.
The compressible above-counter gasket remains 2 mm TPU.

The round stem, bend and dispense tip share a Ø[27.000 mm](NECK_DIAMETER)
section. The display is placed inside its cover before the pair seats on the tip.

## Base joint

The [58 mm](FOOT_WIDTH) × [59 mm](FOOT_DEPTH) oval plate is [4 mm](PLATE_T) thick, with three [2.2 mm](PEDESTAL_H) raised screw-seat pedestals. Three M3 × [8 mm](BASE_SCREW_L) socket-head screws
enter from its underside, through 3 mm bearing seats, into ruthex
RX-M3Sx4.0 inserts heat-set at the ceilings of the shell's pedestal sockets. The three
chamfered pedestals register the plate. The gasket covers all three screw
heads on the completed faucet.

1. Clear the donor cavity, pedestal sockets, tube passages and insert pilots
   of supports and stringing. Dry-fit the printed pieces before heat setting.
2. Heat-set the three short M3 inserts into the shell's bottom-facing Ø4 mm
   pilots, with their mouths at Z = [3.2 mm](BASE_INSERT_Z). Let them cool without disturbing their alignment.
3. With the donor's own lever removed and set aside, soda tube removed and
   base plate separate, seat the donor from below with its lever interface facing the front opening.
   Keep the shell tip separate for access to the soda tube's top-port entry.
4. Position the printed lever, in the faucet's finish, aft of its working position, lower it onto
   the valve, then slide it forward so it wraps and lightly snaps around the
   valve's metal cylinder. Keep the soda tube out throughout this motion.
5. Fit the fresh TPU thimble cap-down into the donor's top water port. Feed
   the soda tube through the lower neck and push it into the thimble until
   it bottoms on the cap. The installed tube retains the lever's working
   position by blocking its aft disengagement motion.
6. Assemble the four-tube bundle and continuous insulated signal conductors
   through the two vent bungs using [vent seal assembly](../asse-vent-seals/README.md).
   Pre-thread the upstream bung, then the distal bung, onto the free ends of
   S, F1, F2 and the four unterminated display wires. Keep D out of the tip
   while seating the distal bung with the curved perimeter pusher. Feed D
   through the preloaded upstream bung, then seat that bung. The drain ends square inside
   the round chamber. Set its cut 8.0 mm beyond the bung's flange front before
   insertion; keep that position marked while seating. The drink tubes continue
   through both bungs and the three final face passages. Confirm the soda tube
   remains seated in its donor port, then close the curved lap.
7. Thread the tube tails and ribbon through the plate's matching openings and
   pass the shank through its centre hole. The three pedestals enter their
   sockets; the donor and shell foot seat on the plate.
8. Install the three M3 × [8 mm](BASE_SCREW_L) screws from below with a 2.5 mm hex key. Seat
   progressively so the plate closes evenly. Verify the lever through
   its full travel and confirm the flavor tubes stay in position and pass flow
   before adding the gasket.

The lever's light snap resists shaking loose while the soda tube is absent,
but the lever remains easy to remove. Pressing it without the tube can slide
it aft off the metal cylinder. Remove the soda tube before removing the lever;
the tube blocks that disengagement path while installed.

The assembly model's fixed-axis rotation and straight insertion corridor are
nominal clearance approximations. They do not establish a pin hinge or verify
the actual aft/down/forward seating path. Check that path on the physical
donor and shell before closing the base. The measured assembled pose and
operating contact motion are not yet established in CAD.

The central lever opening is open above the handle up to the rounded front
of the neck cap. The arched clearance farther aft leaves room for the rear
arm to rise when the front is pressed. Confirm this motion with the printed lever before
closing the faucet base.

The screw stations are (X,Y)=(±[20](BASE_X),[10](BASE_Y)) and (0,[-22.3](BASE_FRONT_Y)) mm. The head recesses
are Ø[6.15 mm](BASE_CBORE_D) × [3.2 mm](BASE_CBORE_DEPTH) deep. Each [4 mm](BASE_INSERT_L) insert receives the screw's full thread
engagement; the blind pilot provides tip relief.

## Gooseneck closure

The tubes and close-fit curved lap retain the neck. Rotate the tip's curved
socket over the base plug about the arc centre until the seam seats. The
socket has [20 mm](SPLIT_OVERLAP) of engagement length and accepts the
18 mm plug, with [0.3 mm](SPLIT_SLIP) diametral fit allowance. The smooth
neck has no screw opening or external bridge.

The female socket presents the full 23 mm opening for factory seal insertion.
The wet chamber and both retained bungs are wholly in the tip; the lap is dry.
The upstream bundle is S with D centered above it and F1/F2 beside D. It spreads
locally at the bungs to leave 0.8 mm nominal elastomer webs, then the flavor
paths converge gently to the unchanged symmetric drink face.

The separate bottom-center opening spans the wet chamber across the crown.
Water flows around the drink tubes into that opening. D ends with a square cut
across its natural path, above the separate bottom opening; no internal divider is fitted.
The two single-piece 85A bungs seal each tube and each of the four continuously
insulated conductors. They have captured flanges and rigid backstops.
Peel the cable web from its unterminated display end before threading; no wet-zone
solder joints, adhesive or slit through the bungs are used.

Route all tubes and conductors through both pieces before closing the lap. Confirm the seam is fully seated and the outlets remain in position
through normal lever operation and handling.

## Display

Use the exact Waveshare ESP32-S3-Touch-LCD-1.47 housing and PCB envelope.
The lever is the [printed replica](../lever-replica/README.md), rebuilt from a scan of the
donor's own and printed in the faucet's finish. The assembly model's lever is a
dimensioned clearance stand-in.

1. Route SIG-6 from the neck into the open space below the PCB, toward its
   southwest corner as viewed from the glass. The cable lies freely between
   the components and supports.
2. Spread the cover's plastic wings and place the display inside it from
   the open underside. Keep the PCB clear of the retaining lips; spread the
   plastic by hand rather than using the board as a wedge.
3. Hold the display and cover together [8.5 mm](DISPLAY_INSTALL_LIFT) above
   their final seat, measured normal to the glass. Slide the pair along the
   tip from the outlet end until the four metal feet align with their
   printed supports. Feed the ribbon through the neck as the pair moves.
4. Lower the pair normal to the display. Its side walls spread outward
   around the rigid cylinder until both broad lips seat in the side grooves,
   under their retaining shoulders. The lips contact the groove roots, and
   the inward-preformed wings remain spread after assembly. The lips' flat
   lower lands seat on the groove floors before the bezel reaches
   the glass. No display screw or insert is fitted.
5. Check that all four feet sit on their supports and the underside
   components clear the three tubes and ribbon. The central space above the
   tubes is open. Check that the seam closes, the glass clears the bezel,
   and the display remains seated when its touch surface is pressed. The
   enclosure's lower edge and the three tube outlets end at the same plane.

The nominal tube-to-USB clearance is 0.30 mm. The flavor passages permit
some tube movement, so the seated real bundle is part of the complete faucet's
fit reading. The [display print project](../faucet-display-petgf.3mf) contains
the complete tip and two complete covers in their stated print orientations.
Its [print record](../faucet-display-petgf.md) identifies the geometry and settings.

The dispense face has [2 mm](DISPENSE_FACE_T) axial stock. The display pocket and USB clearance
share one flat plane behind it.

The [display cover instructions](../faucet-display-cover/README.md) give the
mating dimensions and print orientation.

## Tubes and countertop mounting

Route the separate soda faucet tube from the TPU thimble in the Westbrass's
top port to the printed tip. The two flavor tubes pass through the plate's
pill opening and continue to the same tip. The prints carry and protect the
tubes; they do not form the pressurized fluid path.

The signal ribbon follows a dedicated lane beside the flavor tubes. Its lower
exit passes through the existing stainless plate's open flavor channel and
the countertop hole. The ribbon is routed before either connector is fitted.

Follow [faucet and umbilical assembly](/hardware/assembly/faucet-and-umbilical.md)
for the derived tube cuts, gasket, captive washer/nut, blue tube connection
and cable. Square-cut the three beverage outlets flush with the printed tip. The white
4 mm drain ends inside the chamber and its exterior opening remains bare.

For the nominal 1-3/8-inch mounting hole, its center must be no more than
50.8 mm (2 inches) behind the bowl edge. Aim the faucet directly into the bowl,
within 10° of the modeled forward direction, and check that the complete separate
bottom opening is above the bowl. This fixture is fixed when its nut is tightened;
installation orientation applies to both beverage and fault discharge.

At the modeled 30 mm countertop, 12.476 mm of the 50 mm donor shank remains
below the stainless plate. Confirm the actual retained washer, nut and
thread engagement on the bench, including the intended countertop thickness.
The donor washer and nut have not been dimensionally verified in CAD.

## Verification

`hardware/scripts/check_faucet_geometry.py` records validity, interference,
assembly motion and measured sections in `centered-vent-check.json`.
[Vent qualification](../vent-qualification/README.md) separates the native
port/seat evidence from conditional hydraulic calculations and device qualification. These checks
cover nominal geometry. The fit print must establish actual slip, insert
seating, full lever travel, tube routing, display/cable fit, support removal
and resistance to handling loads.

## Sources
[value](NAME) texts are updated by:
- `/hardware/cut-parts/faucet/under-counter-plate/under_counter_plate.py`
- `/hardware/printed-parts/faucet/faucet-shell/faucet_shell.py`
