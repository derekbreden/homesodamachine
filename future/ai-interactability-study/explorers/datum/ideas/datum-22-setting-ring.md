# datum-22-setting-ring: the surface that sets the plate is the surface the gun rides

Scene: `scenes/datum-22-setting-ring/index.html`. Depth: **deep** (seven rounds below). Origin: combination of `datum-03-rim-crown` and `travel-14-exact-crown` (the soft-then-lock seat), with `travel-14b-crown-cartridge` answered per closure. Region: shells, seats and interfaces formed by the work (wave 3). Numbers: `calc/plate_seat.js` (`plate_seat.out`).

## Picture it

A teal ring sits on the tube's rim and stays on for the whole closure. For the tacks an amber plug drops into it: a hub over the plate, three thin arms out to the ring's ledge, a set-screw foot under each arm reaching the plate face, two pins hanging from the hub down through the plate's two ports. The plate hangs from the plug by those pins, pulled up against the three feet, so its depth below the ledge is the feet's length and its face is parallel to the ledge. The gun tacks eight times (the tube indexes to multiples of 45 degrees; the arms stand at 22.5, 157.5 and 292.5 degrees, never at a tack). The plug lifts out. The upper ring, on balls, goes on the ledge the plug just sat on, with the boom and the gun. The plane that placed the plate is the plane the gun rides.

## The proposal

Seat depth and plate tilt are the two links left standing under a rim reference (`datum-01`), and until now every idea here measured them: a plunger, an eddy coil, a touch, a camera. The scene's finding for the plate is that they are not properties of the tube: the plate is an ID-fit plug with 0.127 mm of radial slip, and its diagonal (123.607 mm) is shorter than the bore (123.698 mm), so it can lie at any tilt without touching the wall on both sides. Nothing squares it except what holds it. The repo says so from the other side: a rolled-over burr holds it off its seated depth, the recess is set with a spacer or depth-stop on the rim, and the rig's own face acceptance (0.30 mm TIR at the weld circle, a tilt of 0.139 degrees) is a check that the plate seat was corrected by hand.

So make it, not measure it. The ring is what the crown already needs (a rim seat, three rim pads, soft-to-lock rockers on the outside). What it adds is a ledge that is at once the seat of a temporary plug and the race the upper ring's balls run on. The plug replaces the spacer or depth-stop on the rim; it holds the plate by its own ports while the tacks cool, so the plate cannot be lifted, tilted or jammed high without a switch noticing.

## What carries the loads, what establishes position, what is free or restrained

- **Loads:** the rim carries the ring (three pads); the ring's ledge carries the plug (three ledge pads) and later the upper ring; the plug carries the plate's weight (0.6 kg) on two pins with T-heads; nothing but the slip fit touches the wall. The tack pull is reacted by the feet (as a ceiling) and the pins.
- **Position:** ring to tube: rim (height and two tilts) and outside (two translations, rockers settled then locked; or bore fingers for seating, `datum-21`). Plug to ring: ledge pads (three), a spring ball at each of three inner-edge points (two translations); the turn about the axis is free until pinned. Plug to plate: pin 1, a cone collar in one port's 82 degree countersink (two translations); pin 2 in a slot (the turn about the axis); three feet on the face (height and two tilts). That is exactly six, and the plate's remaining freedom is the pin fit.
- **Free / restrained / driven:** nothing is driven by software. The plug's rotation in the ring is free until the top plate's register has met the rod (closure 2), then pinned by hand.

## What software could command, observe, and what stays manual

- **Command:** the rotator (index to each tack angle, then the bead), existing.
- **Observe** (all proposed, all switch-class): three foot switches (the plate is against all three feet); a flange switch (the plug is down on the ledge, so the plate is at its recess and the rod is not holding it proud); optionally a contact on one rim pad (ring seated). Blind: the tack pull, the plate after the plug lifts, the dot.
- **Manual:** seating the ring and locking its rockers; hanging the plate and hand-tightening the pins; the eight tacks; lifting the plug; setting the upper ring and gun; in closure 2 clocking the register to the rod.

## What was tried to break it

Numbers are from `calc/plate_seat.js` and the scene; every spread is illustrative unless tagged.

1. **Round 1: does the slip fit square the plate?** *Conflict:* the crown's vertical case assumes the plate follows the rim. *Assumption:* a plug in a bore stands square. *What the numbers say:* diagonal 123.607 mm against a bore of 123.698 mm: it can lie at any tilt. A tilt of 0.139 degrees is 0.30 mm face TIR at the weld circle, the rig's acceptance; 0.25 degrees is 0.54 mm; one degree is 2.16 mm. *Change:* the plate is placed by a part that shares the gun's plane. *Uncertain:* how the plates sit today (nobody has measured).
2. **Round 2: threads.** *Conflict:* a post screwed into the ports. *Assumption:* the tapped 1/4 NPT ports are a good handle. *What breaks:* stainless taper threads gall and the same ports take the elbows later. *Change:* pins in the drilled 11.13 mm pilot with a cone collar seating in the countersink the repo cuts on both faces (step 1 of the vessel procedure), one pin in a slot, and a quarter-turn T-head under the plate; the thread is never engaged. *Uncertain:* the port centres against the plate edge (laser-cut position) and how well a cone centres in a countersink; the T-heads must clear the float rod and float in the second closure (drawn).
3. **Round 3: arms and the nozzle.** *Conflict:* the plug's arms turn with the tube and pass the station. *What the scene shows:* arms at 22.5, 157.5 and 292.5 degrees are 22.5 degrees (24 mm of arc) from every tack angle, so no arm is at the station while a tack is made; an arm 22.5 degrees ahead on the wire's side stands about 5 mm below the kit proxy's wire there (a tight place: the wire's real path decides). Spacing 135, 135, 90 keeps the feet triangle round the plate's centre (the worst case for one foot long and two short at r = 52 mm and +-0.02 mm is 0.032 mm of tilt amplitude). *Uncertain:* clearance to the real wire and nozzle.
4. **Round 4: the tacks.** *Conflict:* eight tacks move the plate. *What the numbers say:* each locks the plate edge at its own height; the eight leave a constant (the mean lift) and a first harmonic about half the spread between tacks (`plate_seat.js` D: mean 0.05 and spread 0.02 give 0.014 mm rms of first harmonic). A steady lift is a depth shift of one number per tube, trimmed like seat depth; only the spread tilts. *Change:* feet and pins clamp the plate while the tacks cool: the tack pull is locked in as stress and part comes back when the plug lifts (0.3 in the scene). *Uncertain:* the size of the tack lift and the recovery; **an indicator on the plate face at three azimuths before and after the eight tacks, on a plate Derek welds today, settles it in ten minutes.**
5. **Round 5: a burr.** *Conflict:* a plate caught part-way down. *What the scene shows:* the flange stands proud of the ledge and a foot stays open; today nothing detects it (`room` finding 6). *Change:* push the plug until the flange seats, then look at the bits. *Uncertain:* the force a jammed plate takes.
6. **Round 6: the flip.** *Conflict:* use's finding that a crown or presetter that stays on its tube serves one closure. *Change:* the ring is per closure by design (its job is to set that closure's plate): it goes on the other rim, its rockers settle and lock again, and the same plug hangs plate 2. The float rod stands up from plate 1 and stops 1 mm short of plate 2's register [repo]; the plug is the depth stop, so the rod cannot hold the plate proud. Plate 1's ports are reachable through the 90 mm service bore but are not used. *Cost:* the ring's seat is a fresh draw at each end. *Uncertain:* the top plate's register must meet the rod; the plug turns freely until it does, and nothing here helps. `travel-14b`'s cartridge (a crown that stays on its tube, the gun docking on trunnion pins) would serve one closure at a time in exactly the same way; not drawn.
7. **Round 7: what it does not fix.** *Left standing:* radial position. The ring centres on the outside, so the wall eccentricity (`datum-21`) and the seat's own leak are still there. The plug centres the plate on the ring, so the slip gap round the plate is even (0.127 mm all round) only if the ring is centred on the bore; a bore-finger seat (`datum-21`) would do that and is the arrangement's natural next step. Also unresolved: heat near the ring at the corner (steel feet and set screws; a printed plug at 10 mm from a tack is not credible), ball retention and the gap in the upper ring (as `datum-03`), and whether a printed race carries the plug's and the upper ring's loads.

## Branches and combinations

- Parent: `datum-03-rim-crown`. Combines `travel-14-exact-crown` (the seat) and answers `travel-14b-crown-cartridge` (the flip).
- With `datum-23-wall-clip`: the clip supplies the radial reading the ring cannot, the ring supplies the plate the clip cannot know.
- With `datum-21-mates-on-the-tube`: the plug is the "plate face plus ports" mate; the ring is the "rim plus outside" mate; the fingers are the bore's.
- With `datum-01`: the datum chain's *How the plate was seated* control sets seat depth and tilt to 0.50 and 0.10 (by hand) or 0.06 and 0.03 (ring).

## Unresolved problems and questions for Derek

- **How is the plate held at its recess today, before it is tacked?** The rig doc names a spacer or depth-stop on the rim; what keeps the plate there is not recorded.
- The tack term (the indicator test above); plate depth and tilt as found (ten plates, a depth gauge from the rim).
- Whether the port pilot's countersink is concentric enough with the hole to centre a cone (a drill-press countersink on a laser-cut hole).
- Whether a ring may sit on the rim of a plate-carrying tube while it is tacked (it must; the crown already assumes so).

## Assumptions

- Geometry from the repo (see the scene). Plate as found (0.30 mm deeper, 0.12 degrees), foot tolerance +-0.02 mm, tack lift mean 0.05 and spread 0.02, recovery 0.3, the seat spreads for the datum chain: illustrative. The tack term and the recovery are **[unknown]**.

## Sourcing pointers

`sourcing/datum.md`: M3 to M8 stainless set screws (Prime, 100+ bought a month), 5/16 in quick-release pins (nearest ordinary part; not a T-head), micro limit switches and A3144 hall sensors.

## Scene id

`datum-22-setting-ring`.
